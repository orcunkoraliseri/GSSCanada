# -*- coding: utf-8 -*-
"""
3rdJ_04E_inference_2split.py — Step 4E (Leg-2): Two-Channel Inference & CSV.

Ports 2J_docs_occ_nTemp/04E_inference.py (AR generation + CSV writer) and adds
the second AT_WORK channel end-to-end.

For each respondent x DDAY_STRATA:
  - DDAY_STRATA == observed -> copy observed act/home/work/cop (IS_SYNTHETIC=0).
  - else -> model AR generation (IS_SYNTHETIC=1):
        activity via temperature sampling (default 0.8);
        home/work/cop via sigmoid threshold 0.5.

Post-hoc consistency (per generated diary):
  - Work activity (raw cat 1 = tensor 0) at a slot -> wrk30=1, hom30=0.
  - Sleep (tensor 4) at night -> hom30=1, wrk30=0.
  - Enforce NOT(hom30==1 AND wrk30==1): if both, keep the higher sigmoid prob.
  - Colleagues channel NaN/zero for 2005/2010.

Output: outputs_step4/augmented_diaries.csv  (N*3 rows)
  occID, CYCLE_YEAR, DDAY_STRATA, IS_SYNTHETIC, + merged demographics,
  act30_001..048 (raw 1..14), hom30_001..048 (0/1), wrk30_001..048 (0/1) [NEW],
  and 9x {Channel}30_001..048 (float [0,1], 4 dp).
  Channel order: Alone,Spouse,Children,parents,otherInFAMs,otherHHs,friends,others,colleagues.

Usage:
    py -3 -X utf8 3rdJ_04E_inference_2split.py --sample
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import sys

import numpy as np
import pandas as pd
import torch

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
model_mod = importlib.import_module("3rdJ_04B_model_2split")
JSeriesHybrid2Split = model_mod.JSeriesHybrid2Split

# ── Platform-detection path block ─────────────────────────────────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )
OUTPUT_DIR = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")

N_SLOTS = 48
N_COP = 9
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
COLLEAGUES_IDX = 8
NIGHT_SLOTS = list(range(0, 7)) + list(range(37, 48))
SLEEP_CAT = 4   # 0-indexed tensor value (raw category 5 = Sleep & Naps & Resting)
WORK_CAT = 0    # 0-indexed tensor value (raw category 1 = Work & Related)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default=None)
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--output", default=None)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--home_threshold", type=float, default=0.5)
    p.add_argument("--work_threshold", type=float, default=0.5)
    p.add_argument("--sample", action="store_true")
    return p.parse_args()


def load_all_data(data_dir: str):
    splits = {}
    for split in ["train", "val", "test"]:
        splits[split] = torch.load(
            os.path.join(data_dir, f"step4_{split}.pt"), map_location="cpu", weights_only=False
        )
    keys = list(splits["train"].keys())
    return {k: torch.cat([splits[s][k] for s in ["train", "val", "test"]], dim=0) for k in keys}


def apply_posthoc_consistency(act_seq, home_seq, work_seq, home_prob, work_prob):
    """
    Enforce logical home/work consistency on one generated diary.
    Returns (home, work) updated arrays.
    """
    home = home_seq.astype(np.float32).copy()
    work = work_seq.astype(np.float32).copy()

    for slot in range(N_SLOTS):
        act = act_seq[slot]
        if act == WORK_CAT:                       # paid work -> at work, not home
            work[slot] = 1.0
            home[slot] = 0.0
        if act == SLEEP_CAT and slot in NIGHT_SLOTS:   # sleep at night -> home, not work
            home[slot] = 1.0
            work[slot] = 0.0

    # Enforce mutual exclusion: NOT(home==1 AND work==1).
    both = (home == 1.0) & (work == 1.0)
    if both.any():
        prefer_work = work_prob >= home_prob
        for slot in np.where(both)[0]:
            if prefer_work[slot]:
                home[slot] = 0.0
            else:
                work[slot] = 0.0

    return home, work


def run_inference(model, data, device, temperature, home_threshold, work_threshold,
                  batch_size=256):
    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()
    cycle_year_all = data["cycle_year"].numpy()
    occ_ids_all = data["occ_ids"].numpy()

    rows = []
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        chunk = list(range(start, end))

        syn_idx, syn_strata = [], []
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i); syn_strata.append(s_tgt)

        syn_results = {}
        if syn_idx:
            act_t  = data["act_seq"][syn_idx].to(device)
            aux_t  = data["aux_seq"][syn_idx].to(device)
            cond_t = data["cond_vec"][syn_idx].to(device)
            cidx_t = data["cycle_idx"][syn_idx].to(device)
            strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

            with torch.no_grad():
                g_act, g_home, g_work, _, g_cop_probs = model.generate(
                    act_t, aux_t, cond_t, cidx_t, strat,
                    temperature=temperature,
                    home_threshold=home_threshold,
                    work_threshold=work_threshold,
                    apply_safety=True,
                )
            g_act = g_act.cpu().numpy()
            g_home = g_home.cpu().numpy()
            g_work = g_work.cpu().numpy()
            g_cop_probs = g_cop_probs.cpu().numpy()

            for k, (i, s_tgt) in enumerate(zip(syn_idx, syn_strata)):
                cy = int(cycle_year_all[i])
                # work/home raw probs for tie-breaking are approximated by the
                # binary decisions; use binary as proxy probability ordering.
                home_k, work_k = apply_posthoc_consistency(
                    g_act[k], g_home[k], g_work[k], g_home[k], g_work[k]
                )
                cop_k = g_cop_probs[k].copy()
                if cy in (2005, 2010):
                    cop_k[:, COLLEAGUES_IDX] = 0.0
                syn_results[(i, s_tgt)] = (g_act[k], home_k, work_k, cop_k)

        for i in chunk:
            occ_id = int(occ_ids_all[i])
            cy = int(cycle_year_all[i])
            s_obs = int(obs_strata_all[i])

            obs_act  = data["act_seq"][i].numpy()
            obs_aux  = data["aux_seq"][i].numpy()
            obs_home = obs_aux[:, 0]
            obs_work = obs_aux[:, 1]
            obs_cop  = obs_aux[:, 2:]

            for s_tgt in [1, 2, 3]:
                row = {
                    "occID": occ_id, "CYCLE_YEAR": cy, "DDAY_STRATA": s_tgt,
                    "IS_SYNTHETIC": 0 if s_tgt == s_obs else 1,
                }
                if s_tgt == s_obs:
                    act_out = obs_act.copy(); home_out = obs_home.copy()
                    work_out = obs_work.copy(); cop_out = obs_cop.copy()
                else:
                    act_out, home_out, work_out, cop_out = syn_results[(i, s_tgt)]

                act_out_raw = act_out + 1  # 0-indexed -> raw 1..14
                for s in range(N_SLOTS):
                    ss = f"{s+1:03d}"
                    row[f"act30_{ss}"] = int(act_out_raw[s])
                    row[f"hom30_{ss}"] = int(home_out[s])
                    row[f"wrk30_{ss}"] = int(work_out[s])  # [Leg-2 NEW]

                for ci, cn in enumerate(COP_COLS):
                    for s in range(N_SLOTS):
                        ss = f"{s+1:03d}"
                        val = cop_out[s, ci]
                        if cn == "colleagues" and cy in (2005, 2010) and s_tgt == s_obs:
                            row[f"{cn}30_{ss}"] = np.nan
                        else:
                            row[f"{cn}30_{ss}"] = round(float(val), 4)
                rows.append(row)

        print(f"  Processed {end}/{n} respondents ({100.0*end/n:.1f}%)", flush=True)

    return rows


def main():
    args = parse_args()
    if args.data_dir is None:
        args.data_dir = OUTPUT_DIR
    if args.checkpoint is None:
        args.checkpoint = os.path.join(OUTPUT_DIR, "checkpoints", "best_model.pt")
    if args.output is None:
        suffix = "_SAMPLE" if args.sample else ""
        args.output = os.path.join(OUTPUT_DIR, f"augmented_diaries{suffix}.csv")

    print("=" * 60)
    print(f"Step 4E (Leg-2) — Inference  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)
    print(f"  data_dir:   {args.data_dir}")
    print(f"  checkpoint: {args.checkpoint}")
    print(f"  output:     {args.output}")
    print(f"  temperature={args.temperature} home_thr={args.home_threshold} work_thr={args.work_threshold}")

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  Device: {device}")

    print("\n[1/4] Loading tensor datasets...")
    data = load_all_data(args.data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    meta = pd.read_csv(os.path.join(args.data_dir, "step4_all_meta.csv"), low_memory=False)
    print(f"  Metadata: {meta.shape}")

    with open(os.path.join(args.data_dir, "step4_feature_config.json")) as f:
        json.load(f)  # validated to exist

    print("\n[2/4] Loading model checkpoint...")
    if not os.path.isfile(args.checkpoint):
        raise FileNotFoundError(
            f"Checkpoint not found: {os.path.abspath(args.checkpoint)}\n"
            f"  Run 3rdJ_04D_train_2split.py first."
        )
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = JSeriesHybrid2Split(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded epoch {ckpt.get('epoch','?')}  val_JS={ckpt.get('val_js','?')} "
          f"work_gap={ckpt.get('work_gap','?')}")

    print("\n[3/4] Generating synthetic diaries...")
    rows = run_inference(model, data, device, args.temperature,
                         args.home_threshold, args.work_threshold)

    print("\n[4/4] Assembling augmented_diaries.csv...")
    aug_df = pd.DataFrame(rows)
    meta_merge = meta.drop(columns=["DDAY_STRATA"], errors="ignore")
    aug_df = aug_df.merge(meta_merge, on=["occID", "CYCLE_YEAR"], how="left")

    # ── G3 operating-point fix: per-channel rank-to-marginal binarization ──────
    # Pool ALL synthetic rows per channel (unweighted) so that synthetic
    # co-presence prevalence matches observed prevalence under the EXACT same
    # definition the G3 validator uses:
    #   obs:  np.nanmean(obs_block == 1)  (equality to 1, NaN-aware, unweighted)
    #   syn:  np.nanmean(syn_block >= 0.5)  (after binarization, unweighted)
    # Observed rows (IS_SYNTHETIC==0) are NOT modified — they stay 0/1/NaN.
    print("\n[4b/4] Applying per-channel rank-to-marginal binarization (G3 fix)...")
    syn_mask = aug_df["IS_SYNTHETIC"] == 1
    obs_mask = aug_df["IS_SYNTHETIC"] == 0
    thresholds = {}
    for cn in COP_COLS:
        cols = [f"{cn}30_{s:03d}" for s in range(1, N_SLOTS + 1)
                if f"{cn}30_{s:03d}" in aug_df.columns]
        if not cols:
            continue
        obs_vals = aug_df.loc[obs_mask, cols].to_numpy(dtype=float)
        p_obs = np.nanmean(obs_vals == 1)           # fraction in [0,1], matches validator
        syn_block = aug_df.loc[syn_mask, cols].to_numpy(dtype=float)
        flat = syn_block[~np.isnan(syn_block)]
        if flat.size == 0 or np.isnan(p_obs):
            continue
        # rank-to-marginal: choose threshold so synthetic prevalence == observed
        q = min(max(1.0 - p_obs, 0.0), 1.0)
        t = float(np.quantile(flat, q))
        binarized = (syn_block >= t).astype(float)  # NaN >= t -> False -> 0.0
        aug_df.loc[syn_mask, cols] = binarized
        thresholds[cn] = {
            "obs_prev_pct":      round(float(p_obs * 100), 4),
            "threshold":         round(t, 6),
            "syn_prev_pct_after": round(float(np.nanmean(binarized >= 0.5) * 100), 4),
        }

    # Write provenance JSON
    out_thresh = os.path.join(os.path.dirname(args.output), "g3_copresence_thresholds.json")
    with open(out_thresh, "w") as _f:
        json.dump(thresholds, _f, indent=2)

    if thresholds:
        max_gap = max(
            abs(v["obs_prev_pct"] - v["syn_prev_pct_after"]) for v in thresholds.values()
        )
        print(f"  Thresholded {len(thresholds)} channels; "
              f"max |obs−syn| after binarization = {max_gap:.4f} pp  →  {out_thresh}")
    else:
        print("  Warning: no channels thresholded (check COP_COLS / column names).")
    # ── end G3 fix ─────────────────────────────────────────────────────────────

    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    wrk_cols = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    cop_cols_f = []
    for cn in COP_COLS:
        cop_cols_f.extend([f"{cn}30_{s:03d}" for s in range(1, N_SLOTS + 1)])
    seq_cols = set(act_cols + hom_cols + wrk_cols + cop_cols_f) | {"IS_SYNTHETIC"}
    meta_cols = [c for c in aug_df.columns if c not in seq_cols]

    final_cols = meta_cols + act_cols + hom_cols + wrk_cols + cop_cols_f + ["IS_SYNTHETIC"]
    final_cols = [c for c in final_cols if c in aug_df.columns]
    aug_df = aug_df[final_cols]
    aug_df.to_csv(args.output, index=False)

    print(f"\n  === AUGMENTED OUTPUT ===")
    print(f"  Shape: {aug_df.shape}")
    print(f"  IS_SYNTHETIC=0: {(aug_df['IS_SYNTHETIC']==0).sum()}  "
          f"=1: {(aug_df['IS_SYNTHETIC']==1).sum()}")
    print(f"  Unique occIDs: {aug_df['occID'].nunique()}")
    print(f"  wrk30 columns present: {sum(c in aug_df.columns for c in wrk_cols)}/48")
    # Mutual-exclusion spot check
    bad = 0
    for s in range(1, N_SLOTS + 1):
        h = aug_df[f"hom30_{s:03d}"]; w = aug_df[f"wrk30_{s:03d}"]
        bad += int(((h == 1) & (w == 1)).sum())
    print(f"  hom==1 AND wrk==1 violations: {bad} (expect 0)")
    print(f"\nOK 04E (Leg-2) complete. Saved {args.output}")
    print(f"  Total rows: {len(aug_df)} (expect {n * 3})")


if __name__ == "__main__":
    main()
