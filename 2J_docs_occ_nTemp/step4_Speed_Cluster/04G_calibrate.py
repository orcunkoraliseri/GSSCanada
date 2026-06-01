"""
04G_calibrate.py — Step 4G: Decision-boundary calibration sweep

Purpose
-------
The 04F validation run flagged two inference-side failures:
  §3  AT_HOME bias 12–25 pp (synthetic > observed, all 12 cycle × stratum cells)
  §4.2 Transition-rate ratio ~2.5 (synthetic thrashes 2.5× more than observed)

Both are governed by generation-time decisions, not by weights:
  - §3   ← sigmoid > 0.5 cutoff in the AT_HOME head (04B_model.py)
  - §4.2 ← multinomial temperature on the activity head (default 0.8)

This script sweeps (temperature × home_threshold) on a stratified subsample of
respondents, regenerates synthetic diaries under each combo, and reports the
two 04F metrics using the **exact same definitions** as 04F_validation.py:

  §3   | obs[hom_cols].mean()*100 - syn[hom_cols].mean()*100 |  per (cy, s)
  §4.2 | syn_transitions.mean() / obs_transitions.mean() - 1 | * 100

Outputs
-------
  outputs_step4/calibration/sweep_results.csv — one row per (T, θ) combo
  outputs_step4/calibration/sweep_summary.txt — top-5 sorted table

Usage (HPC)
-----------
  python 04G_calibrate.py \\
      --data_dir outputs_step4 \\
      --checkpoint outputs_step4/checkpoints/best_model.pt \\
      --out_dir outputs_step4/calibration \\
      --per_bucket 150
"""

import argparse
import importlib
import itertools
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("04B_model")
ConditionalTransformer = model_mod.ConditionalTransformer

# Re-use 04E post-hoc helpers to mirror production inference exactly.
infer_mod = importlib.import_module("04E_inference")
apply_posthoc_consistency = infer_mod.apply_posthoc_consistency

N_SLOTS     = 48
SLEEP_CAT   = 4    # 0-indexed (raw 5 = Sleep & Naps & Resting)
STRATA      = [1, 2, 3]

# Default sweep grid — small enough to finish in ~1 hr CPU / minutes GPU.
DEFAULT_TEMPS      = [0.5, 0.6, 0.7, 0.8]
DEFAULT_THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",   default=None)
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--out_dir",    default=None)
    p.add_argument("--per_bucket", type=int, default=150,
                   help="Respondents per (cycle × obs_strata) bucket. "
                        "12 buckets × per_bucket = subsample size.")
    p.add_argument("--temperatures", type=float, nargs="+",
                   default=DEFAULT_TEMPS)
    p.add_argument("--thresholds",   type=float, nargs="+",
                   default=DEFAULT_THRESHOLDS)
    p.add_argument("--batch_size",   type=int, default=256)
    p.add_argument("--seed",         type=int, default=42)
    return p.parse_args()


# ── Data loading (mirrors 04E) ──────────────────────────────────────────────

def load_all_data(data_dir: str) -> dict:
    splits = {}
    for split in ["train", "val", "test"]:
        path = os.path.join(data_dir, f"step4_{split}.pt")
        splits[split] = torch.load(path, map_location="cpu", weights_only=False)
    combined = {}
    for k in splits["train"].keys():
        combined[k] = torch.cat([splits[sp][k] for sp in ["train", "val", "test"]], dim=0)
    return combined


def stratified_subsample(data: dict, per_bucket: int, seed: int) -> np.ndarray:
    """Return respondent indices, ~per_bucket per (CYCLE_YEAR × obs_strata)."""
    rng       = np.random.default_rng(seed)
    cy_all    = data["cycle_year"].numpy()
    strata_all = data["obs_strata"].numpy()
    picked = []
    for cy in sorted(np.unique(cy_all)):
        for s in STRATA:
            idx = np.where((cy_all == cy) & (strata_all == s))[0]
            if len(idx) == 0:
                continue
            k = min(per_bucket, len(idx))
            picked.extend(rng.choice(idx, size=k, replace=False).tolist())
    return np.array(sorted(picked), dtype=np.int64)


# ── Observed-reference metrics (computed once) ──────────────────────────────

def observed_reference(data: dict) -> dict:
    """
    Build the reference distributions 04F compares against:
      - obs_home_rate[(cy, s)] : mean AT_HOME % over all observed diaries
      - obs_trans_mean         : mean per-diary transition count
    Uses the FULL observed population (not the subsample) for stability —
    this matches how 04F computes these from augmented_diaries.csv.
    """
    cy_all     = data["cycle_year"].numpy()
    strata_all = data["obs_strata"].numpy()
    aux_all    = data["aux_seq"].numpy()   # (N, 48, 10) — [AT_HOME | 9 cop]
    act_all    = data["act_seq"].numpy()   # (N, 48) 0-indexed

    obs_home_rate = {}
    for cy in sorted(np.unique(cy_all)):
        for s in STRATA:
            mask = (cy_all == cy) & (strata_all == s)
            if mask.sum() == 0:
                continue
            obs_home_rate[(int(cy), int(s))] = float(aux_all[mask, :, 0].mean() * 100.0)

    # Transitions: count position-to-position changes in the 48-slot act sequence.
    # Matches 04F: sum(row_acts[i] != row_acts[i+1] for i in range(47)).
    diffs = (act_all[:, 1:] != act_all[:, :-1]).sum(axis=1)
    obs_trans_mean = float(diffs.mean())

    return {
        "obs_home_rate":  obs_home_rate,
        "obs_trans_mean": obs_trans_mean,
    }


# ── Sweep core ──────────────────────────────────────────────────────────────

def generate_syn_for_subsample(
    model, data, device, sub_idx, temperature, home_threshold, batch_size
):
    """
    For every respondent in sub_idx, generate the 2 non-observed synthetic
    diaries. Returns arrays aligned with syn pairs:
      syn_act  (K, 48) 0-indexed
      syn_home (K, 48) 0/1 (post-hoc consistency applied, matches 04E)
      syn_cy   (K,) int
      syn_s    (K,) int  target stratum
    """
    obs_strata_all = data["obs_strata"].numpy()
    cy_all         = data["cycle_year"].numpy()

    pair_i      = []
    pair_s_tgt  = []
    for i in sub_idx:
        s_obs = int(obs_strata_all[i])
        for s_tgt in STRATA:
            if s_tgt != s_obs:
                pair_i.append(int(i))
                pair_s_tgt.append(int(s_tgt))

    pair_i     = np.array(pair_i,     dtype=np.int64)
    pair_s_tgt = np.array(pair_s_tgt, dtype=np.int64)
    K = len(pair_i)

    syn_act  = np.zeros((K, N_SLOTS), dtype=np.int64)
    syn_home = np.zeros((K, N_SLOTS), dtype=np.float32)

    torch.manual_seed(42)  # reproducibility within a combo
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    for start in range(0, K, batch_size):
        end = min(start + batch_size, K)
        idx_b = pair_i[start:end]
        s_b   = pair_s_tgt[start:end]

        act_t  = data["act_seq"][idx_b].to(device)
        aux_t  = data["aux_seq"][idx_b].to(device)
        cond_t = data["cond_vec"][idx_b].to(device)
        cidx_t = data["cycle_idx"][idx_b].to(device)
        strat  = torch.tensor(s_b, dtype=torch.long, device=device)

        with torch.no_grad():
            gen_act, gen_home, _gen_cop, _gen_cop_probs = model.generate(
                act_t, aux_t, cond_t, cidx_t, strat,
                temperature=temperature,
                home_threshold=home_threshold,
            )

        gen_act  = gen_act.cpu().numpy()
        gen_home = gen_home.cpu().numpy()

        # Apply the exact same post-hoc rules as 04E (Sleep@night → 1, Work → 0)
        for k in range(end - start):
            syn_home[start + k] = apply_posthoc_consistency(gen_act[k], gen_home[k])
        syn_act[start:end] = gen_act

    syn_cy = cy_all[pair_i].astype(np.int64)
    syn_s  = pair_s_tgt
    return syn_act, syn_home, syn_cy, syn_s


def score_combo(syn_act, syn_home, syn_cy, syn_s, ref) -> dict:
    """Compute §3 and §4.2 metrics for one (T, θ) combo."""
    # §3 — per-bucket |ΔAT_HOME| in pp
    deltas = []
    per_bucket = {}
    for cy in sorted(set(syn_cy.tolist())):
        for s in STRATA:
            mask = (syn_cy == cy) & (syn_s == s)
            if mask.sum() == 0:
                continue
            syn_rate = float(syn_home[mask].mean() * 100.0)
            obs_rate = ref["obs_home_rate"].get((int(cy), int(s)))
            if obs_rate is None:
                continue
            d = abs(obs_rate - syn_rate)
            deltas.append(d)
            per_bucket[f"{cy}_{s}"] = round(d, 2)

    max_pp  = max(deltas) if deltas else float("nan")
    mean_pp = float(np.mean(deltas)) if deltas else float("nan")

    # §4.2 — transition-rate ratio
    syn_trans     = (syn_act[:, 1:] != syn_act[:, :-1]).sum(axis=1).astype(np.float64)
    syn_trans_m   = float(syn_trans.mean())
    ratio         = syn_trans_m / max(ref["obs_trans_mean"], 1e-6)
    trans_pct_dev = abs(ratio - 1.0) * 100.0

    return {
        "at_home_max_pp":  round(max_pp, 2),
        "at_home_mean_pp": round(mean_pp, 2),
        "transition_ratio": round(ratio, 3),
        "transition_pct_dev": round(trans_pct_dev, 1),
        "syn_trans_mean": round(syn_trans_m, 2),
        "per_bucket_pp": per_bucket,
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    base_dir = os.path.join(SCRIPT_DIR, "outputs_step4")
    if args.data_dir   is None: args.data_dir   = base_dir
    if args.checkpoint is None: args.checkpoint = os.path.join(base_dir, "checkpoints", "best_model.pt")
    if args.out_dir    is None: args.out_dir    = os.path.join(base_dir, "calibration")
    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 60)
    print("Step 4G — Inference calibration sweep")
    print("=" * 60)
    print(f"  data_dir:    {args.data_dir}")
    print(f"  checkpoint:  {args.checkpoint}")
    print(f"  out_dir:     {args.out_dir}")
    print(f"  per_bucket:  {args.per_bucket}")
    print(f"  temps:       {args.temperatures}")
    print(f"  thresholds:  {args.thresholds}")

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}")

    # Load data and model once
    print("\n[1/4] Loading tensor datasets...")
    data = load_all_data(args.data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    cfg_path = os.path.join(args.data_dir, "step4_feature_config.json")
    with open(cfg_path) as f:
        feat_cfg = json.load(f)

    print("\n[2/4] Loading checkpoint...")
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model_config = ckpt["model_config"]
    model_config["d_cond"] = feat_cfg["d_cond"]
    model = ConditionalTransformer(model_config).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded from epoch {ckpt.get('epoch', '?')}  val_JS={ckpt.get('val_js', '?')}")

    # Build stratified subsample and observed reference
    print("\n[3/4] Building subsample and observed-reference metrics...")
    sub_idx = stratified_subsample(data, args.per_bucket, args.seed)
    ref     = observed_reference(data)
    print(f"  Subsample respondents: {len(sub_idx)}  (target {args.per_bucket} × 12 buckets)")
    print(f"  Observed mean transitions / diary: {ref['obs_trans_mean']:.2f}")
    print(f"  Observed AT_HOME rate buckets: {len(ref['obs_home_rate'])}")

    # Sweep
    grid = list(itertools.product(args.temperatures, args.thresholds))
    print(f"\n[4/4] Sweeping {len(grid)} combos...")
    results = []
    t0_all = time.time()
    for ci, (T, th) in enumerate(grid, 1):
        t0 = time.time()
        syn_act, syn_home, syn_cy, syn_s = generate_syn_for_subsample(
            model, data, device, sub_idx, T, th, args.batch_size,
        )
        m = score_combo(syn_act, syn_home, syn_cy, syn_s, ref)
        dt = time.time() - t0
        row = {"temperature": T, "home_threshold": th, "runtime_s": round(dt, 1), **m}
        results.append(row)
        print(f"  [{ci:>2}/{len(grid)}] T={T:.2f} θ={th:.2f}  "
              f"AT_HOME max={m['at_home_max_pp']:>5.2f}pp mean={m['at_home_mean_pp']:>5.2f}pp  "
              f"trans_ratio={m['transition_ratio']:.3f} (|dev|={m['transition_pct_dev']:>5.1f}%)  "
              f"[{dt:.1f}s]", flush=True)

    print(f"\n  Sweep wall time: {time.time() - t0_all:.1f} s")

    # ── Save results ─────────────────────────────────────────────────────────
    df = pd.DataFrame([{k: v for k, v in r.items() if k != "per_bucket_pp"}
                       for r in results])
    # Combined score: favor low AT_HOME bias, penalise |transition dev|
    df["combined_score"] = df["at_home_max_pp"] + 0.5 * df["transition_pct_dev"]
    df = df.sort_values("combined_score").reset_index(drop=True)

    csv_path = os.path.join(args.out_dir, "sweep_results.csv")
    df.to_csv(csv_path, index=False)

    # Summary with top-5 and per-bucket breakdown for the winner
    lines = []
    lines.append("=" * 72)
    lines.append("04G sweep summary — sorted by combined_score (lower = better)")
    lines.append("=" * 72)
    lines.append("")
    lines.append(df.head(10).to_string(index=False))
    lines.append("")
    best_row = df.iloc[0]
    best_raw = next(r for r in results
                    if r["temperature"] == best_row["temperature"]
                    and r["home_threshold"] == best_row["home_threshold"])
    lines.append(f"Winner: T={best_row['temperature']}  θ={best_row['home_threshold']}")
    lines.append(f"  AT_HOME |Δ| per (cycle_strata): {best_raw['per_bucket_pp']}")
    lines.append(f"  Thresholds for PASS (04F non-sample): AT_HOME ≤ 2.0 pp, |trans dev| ≤ 20%")
    lines.append("")
    lines.append("Next step:")
    lines.append(f"  Re-run 04E full inference with --temperature {best_row['temperature']} "
                 f"--home_threshold {best_row['home_threshold']}, then 04F.")

    summary_path = os.path.join(args.out_dir, "sweep_summary.txt")
    with open(summary_path, "w") as f:
        f.write("\n".join(lines))

    print("\n" + "\n".join(lines))
    print(f"\n✓ Wrote {csv_path}")
    print(f"✓ Wrote {summary_path}")


if __name__ == "__main__":
    main()
