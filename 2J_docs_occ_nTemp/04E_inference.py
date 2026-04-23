"""
04E_inference.py — Step 4E: Inference & Synthetic Diary Generation

Loads the best checkpoint and generates synthetic diaries for all 64,061
respondents.  For each respondent × DDAY_STRATA:
  - If DDAY_STRATA matches the observed diary → copy observed (IS_SYNTHETIC=0)
  - Else → autoregressive generation with temperature τ (IS_SYNTHETIC=1)

Post-hoc consistency rules:
  - Sleep (tensor value 4, 0-indexed; raw category 5 = Sleep & Naps & Resting)
    at night slots → AT_HOME=1
  - Work & Related (tensor value 0, 0-indexed; raw category 1) → AT_HOME=0
  - Colleagues zeroed for 2005/2010 respondents

Output: augmented_diaries.csv (~192,183 rows × ~552 columns)

Usage (HPC):
    python 04E_inference.py \\
        --data_dir outputs_step4 \\
        --checkpoint outputs_step4/checkpoints/best_model.pt \\
        --output outputs_step4/augmented_diaries.csv \\
        --temperature 0.8

Usage (local sample):
    python 04E_inference.py --sample
"""

import argparse
import importlib
import json
import os
import sys

import numpy as np
import pandas as pd
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("04B_model")
ConditionalTransformer = model_mod.ConditionalTransformer

N_SLOTS = 48
N_COP   = 9
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
# Night slots (4:00–7:30 AM = slots 1–7, 0-indexed 0–6;
#              and 22:30 AM–3:30 AM = slots 37–47, 0-indexed)
# Diaries start at 4:00 AM: slot 0 = 4:00–4:29, slot 47 = 3:30–3:59 (next day)
NIGHT_SLOTS = list(range(0, 7)) + list(range(37, 48))  # 4:00–7:30 and 22:30–4:00
SLEEP_CAT   = 4   # 0-indexed tensor value (raw category 5 = Sleep & Naps & Resting)
WORK_CAT    = 0   # 0-indexed tensor value (raw category 1 = Work & Related)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",   default=None)
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--output",     default=None)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--home_threshold", type=float, default=0.5,
                   help="Sigmoid cutoff for AT_HOME head (default 0.5). "
                        "Raise to reduce AT_HOME=1 predictions.")
    p.add_argument("--sample", action="store_true")
    return p.parse_args()


def load_all_data(data_dir: str):
    """Load and concatenate train/val/test tensor datasets."""
    splits = {}
    for split in ["train", "val", "test"]:
        path = os.path.join(data_dir, f"step4_{split}.pt")
        splits[split] = torch.load(path, map_location="cpu", weights_only=False)

    # Concatenate all tensors along dim 0
    all_keys = list(splits["train"].keys())
    combined = {}
    for k in all_keys:
        combined[k] = torch.cat([splits[sp][k] for sp in ["train", "val", "test"]], dim=0)
    return combined


def apply_posthoc_consistency(
    act_seq: np.ndarray,  # (48,) 0-indexed
    home_seq: np.ndarray, # (48,)
) -> np.ndarray:
    """
    Enforce logical AT_HOME consistency on a single generated diary.
    Returns updated home_seq.
    """
    home = home_seq.copy()

    for slot in range(N_SLOTS):
        act = act_seq[slot]
        # Sleep at night → must be home
        if act == SLEEP_CAT and slot in NIGHT_SLOTS:
            home[slot] = 1.0
        # Paid work → not home (no WFH flag available in this dataset)
        if act == WORK_CAT:
            home[slot] = 0.0

    return home


def run_inference(model, data: dict, device, temperature: float,
                  home_threshold: float = 0.5,
                  batch_size: int = 256) -> list:
    """
    Generate synthetic diaries for all respondents (batched generation).

    Collects all synthetic (respondent, target_stratum) pairs per chunk and
    calls model.generate() once per chunk — ~50-100x faster than B=1 per call.
    Returns list of dicts (one per output row).
    """
    model.eval()

    # Reproducibility: torch.multinomial with temperature>0 is non-deterministic;
    # seeding here makes a given checkpoint + temperature reproduce the same CSV.
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()
    cycle_year_all = data["cycle_year"].numpy()
    occ_ids_all    = data["occ_ids"].numpy()

    rows = []

    for start in range(0, n, batch_size):
        end   = min(start + batch_size, n)
        chunk = list(range(start, end))

        # ── Collect all (respondent, target_stratum) pairs needing generation ──
        syn_idx    = []   # respondent index in data
        syn_strata = []   # target DDAY_STRATA
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i)
                    syn_strata.append(s_tgt)

        # ── Batch generate all synthetic pairs in one model.generate() call ───
        syn_results = {}   # (i, s_tgt) → (act_0idx ndarray, home ndarray, cop ndarray)

        if syn_idx:
            act_t  = data["act_seq"][syn_idx].to(device)
            aux_t  = data["aux_seq"][syn_idx].to(device)
            cond_t = data["cond_vec"][syn_idx].to(device)
            cidx_t = data["cycle_idx"][syn_idx].to(device)
            strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

            with torch.no_grad():
                gen_act, gen_home, gen_cop, gen_cop_probs = model.generate(
                    act_t, aux_t, cond_t, cidx_t, strat,
                    temperature=temperature,
                    home_threshold=home_threshold,
                )

            gen_act       = gen_act.cpu().numpy()        # (K, 48) 0-indexed
            gen_home      = gen_home.cpu().numpy()       # (K, 48)
            gen_cop_probs = gen_cop_probs.cpu().numpy()  # (K, 48, 9) raw σ — used for output

            for k, (i, s_tgt) in enumerate(zip(syn_idx, syn_strata)):
                cy     = int(cycle_year_all[i])
                home_k = apply_posthoc_consistency(gen_act[k], gen_home[k])
                cop_k  = gen_cop_probs[k].copy()
                if cy in (2005, 2010):
                    cop_k[:, 8] = 0.0
                syn_results[(i, s_tgt)] = (gen_act[k], home_k, cop_k)

        # ── Build output rows ──────────────────────────────────────────────────
        for i in chunk:
            occ_id = int(occ_ids_all[i])
            cy     = int(cycle_year_all[i])
            s_obs  = int(obs_strata_all[i])

            obs_act  = data["act_seq"][i].numpy()   # (48,) 0-indexed
            obs_aux  = data["aux_seq"][i].numpy()   # (48, 10)
            obs_home = obs_aux[:, 0]                 # (48,) AT_HOME
            obs_cop  = obs_aux[:, 1:]                # (48, 9) co-pres

            for s_tgt in [1, 2, 3]:
                row = {
                    "occID":       occ_id,
                    "CYCLE_YEAR":  cy,
                    "DDAY_STRATA": s_tgt,
                    "IS_SYNTHETIC": 0 if s_tgt == s_obs else 1,
                }

                if s_tgt == s_obs:
                    act_out  = obs_act.copy()
                    home_out = obs_home.copy()
                    cop_out  = obs_cop.copy()
                else:
                    act_out, home_out, cop_out = syn_results[(i, s_tgt)]

                # Convert activity from 0-indexed to raw 1-indexed for output CSV
                act_out_raw = act_out + 1

                for s in range(N_SLOTS):
                    slot_str = f"{s+1:03d}"
                    row[f"act30_{slot_str}"]  = int(act_out_raw[s])
                    row[f"hom30_{slot_str}"]  = int(home_out[s])

                for ci, cn in enumerate(COP_COLS):
                    for s in range(N_SLOTS):
                        slot_str = f"{s+1:03d}"
                        val = cop_out[s, ci]
                        # Colleagues NaN for 2005/2010 observed rows
                        if cn == "colleagues" and cy in (2005, 2010) and s_tgt == s_obs:
                            row[f"{cn}30_{slot_str}"] = np.nan
                        else:
                            row[f"{cn}30_{slot_str}"] = round(float(val), 4)

                rows.append(row)

        pct = 100.0 * end / n
        print(f"  Processed {end}/{n} respondents ({pct:.1f}%)", flush=True)

    return rows


def main():
    args = parse_args()

    # Resolve paths
    base_dir = os.path.join(
        SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
    )
    if args.data_dir is None:
        args.data_dir = base_dir
    if args.checkpoint is None:
        args.checkpoint = os.path.join(base_dir, "checkpoints", "best_model.pt")
    if args.output is None:
        suffix = "_SAMPLE" if args.sample else ""
        args.output = os.path.join(base_dir, f"augmented_diaries{suffix}.csv")

    print("=" * 60)
    print(f"Step 4E — Inference  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir:   {args.data_dir}")
    print(f"  checkpoint: {args.checkpoint}")
    print(f"  output:     {args.output}")
    print(f"  temperature:    {args.temperature}")
    print(f"  home_threshold: {args.home_threshold}")

    # Device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}")

    # Load data
    print("\n[1/4] Loading tensor datasets...")
    data = load_all_data(args.data_dir)
    n    = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    # Load metadata (for additional columns in output CSV)
    meta_path = os.path.join(args.data_dir, "step4_all_meta.csv")
    meta = pd.read_csv(meta_path, low_memory=False)
    print(f"  Metadata: {meta.shape}")

    # Load feature config and checkpoint
    cfg_path = os.path.join(args.data_dir, "step4_feature_config.json")
    with open(cfg_path) as f:
        feat_cfg = json.load(f)

    print("\n[2/4] Loading model checkpoint...")
    if not os.path.isfile(args.checkpoint):
        raise FileNotFoundError(
            f"Checkpoint not found: {os.path.abspath(args.checkpoint)}\n"
            f"  Run 04D_train.py first, or pass --checkpoint <path>."
        )
    print(f"  checkpoint (absolute): {os.path.abspath(args.checkpoint)} "
          f"({os.path.getsize(args.checkpoint) / 1e6:.1f} MB)")
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model_config = ckpt["model_config"]
    model_config["d_cond"] = feat_cfg["d_cond"]
    model = ConditionalTransformer(model_config).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded from epoch {ckpt.get('epoch', '?')}  "
          f"val_JS={ckpt.get('val_js', '?')}")

    # Run inference
    print("\n[3/4] Generating synthetic diaries...")
    rows = run_inference(model, data, device, args.temperature,
                         home_threshold=args.home_threshold)

    # Build output DataFrame
    print("\n[4/4] Assembling augmented_diaries.csv...")
    aug_df = pd.DataFrame(rows)

    # Merge in metadata (demographics, weights) from meta CSV.
    # Must join on (occID, CYCLE_YEAR) — occID is not unique across GSS cycles.
    meta_merge = meta.drop(columns=["DDAY_STRATA"], errors="ignore")
    aug_df = aug_df.merge(meta_merge, on=["occID", "CYCLE_YEAR"], how="left")

    # Column order: metadata | act30 | hom30 | cop30 | IS_SYNTHETIC
    meta_cols  = [c for c in aug_df.columns
                  if c not in [f"act30_{s:03d}" for s in range(1, 49)]
                  and c not in [f"hom30_{s:03d}" for s in range(1, 49)]
                  and not any(c.startswith(f"{cn}30_") for cn in COP_COLS)
                  and c != "IS_SYNTHETIC"]
    act_cols   = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    hom_cols   = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    cop_cols_f = []
    for cn in COP_COLS:
        cop_cols_f.extend([f"{cn}30_{s:03d}" for s in range(1, N_SLOTS + 1)])

    final_cols = meta_cols + act_cols + hom_cols + cop_cols_f + ["IS_SYNTHETIC"]
    final_cols = [c for c in final_cols if c in aug_df.columns]
    aug_df = aug_df[final_cols]

    aug_df.to_csv(args.output, index=False)

    # Test 5 inspection prints
    print(f"\n  === AUGMENTED OUTPUT ===")
    print(f"  Shape: {aug_df.shape}")
    print(f"  IS_SYNTHETIC=0 (observed): {(aug_df['IS_SYNTHETIC']==0).sum()}")
    print(f"  IS_SYNTHETIC=1 (synthetic): {(aug_df['IS_SYNTHETIC']==1).sum()}")
    print(f"  Unique occIDs: {aug_df['occID'].nunique()}")
    rows_per_id = aug_df.groupby("occID").size().unique()
    print(f"  Rows per occID: {sorted(rows_per_id)}")

    # Show one respondent's 3 diary rows
    ex_id = aug_df["occID"].iloc[0]
    ex    = aug_df[aug_df["occID"] == ex_id]
    cy    = ex["CYCLE_YEAR"].iloc[0]
    print(f"\n  === EXAMPLE RESPONDENT (occID={ex_id}, CYCLE_YEAR={cy}) ===")
    obs_s = data["obs_strata"][0].item()
    print(f"  Observed DDAY_STRATA: {obs_s}")
    for _, r in ex.iterrows():
        acts = [r[f"act30_{s:03d}"] for s in range(1, 49)]
        home = [r[f"hom30_{s:03d}"] for s in range(1, 49)]
        print(f"  DDAY_STRATA={r['DDAY_STRATA']} IS_SYNTHETIC={r['IS_SYNTHETIC']}  "
              f"acts={acts[:10]}...  home={home[:10]}...")

    # Check: colleagues = 0/NaN for 2005/2010
    old_syn = aug_df[(aug_df["CYCLE_YEAR"].isin([2005, 2010])) &
                     (aug_df["IS_SYNTHETIC"] == 1)]
    if len(old_syn) > 0:
        col_cols = [f"colleagues30_{s:03d}" for s in range(1, 49)]
        col_cols = [c for c in col_cols if c in old_syn.columns]
        if col_cols:
            max_val = old_syn[col_cols].fillna(0).max().max()
            assert max_val == 0, f"BUG: colleagues non-zero for 2005/2010 synthetic rows"
            print("  ✓ colleagues = 0 for all 2005/2010 synthetic rows")

    print(f"\n✓ 04E complete. Saved {args.output}")
    print(f"  Total rows: {len(aug_df)} (expect {n * 3})")


if __name__ == "__main__":
    main()
