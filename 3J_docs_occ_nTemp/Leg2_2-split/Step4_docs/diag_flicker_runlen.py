# -*- coding: utf-8 -*-
"""
diag_flicker_runlen.py
Diagnostic: Gate-B transition-flicker (hom30) -- real over-segmentation vs blip artifact.

Runs on the Speed cluster via sbatch (CPU-only, ~980k rows).

Loads:
  - syn rows (IS_SYNTHETIC==1) from R10_fast_floataware_raked/augmented_diaries.csv
  - obs rows (IS_SYNTHETIC==0) from the SAME file (same source as validator)

Computes per person-day:
  transitions = sum_{i=1}^{47} |hom30[i+1] - hom30[i]|   (identical to Gate-B logic)

Reports:
  1. Syn vs obs transition distribution: median, mean, p10/25/50/75/90, histogram 0-8+
  2. Syn HOME run-length distribution (fraction of length-1 runs)
  3. Syn AWAY run-length distribution (fraction of length-1 runs)
  4. Interpretation cue: would min-dwell=2 post-process bring median toward obs?
"""

import sys
import os
import numpy as np
import pandas as pd

BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
CSV_PATH = os.path.join(BASE, "outputs_step4/sweep/R10_fast_floataware_raked/augmented_diaries.csv")

HOM_COLS = [f"hom30_{i:03d}" for i in range(1, 49)]

print("=" * 70)
print("diag_flicker_runlen.py -- Gate-B transition flicker diagnostic")
print(f"CSV: {CSV_PATH}")
print("=" * 70)

print("\nLoading CSV ...", flush=True)
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"  Total rows: {len(df):,}")

# Split obs / syn exactly as validator does
if "IS_SYNTHETIC" in df.columns:
    syn = df[df["IS_SYNTHETIC"] == 1].copy()
    obs = df[df["IS_SYNTHETIC"] == 0].copy()
else:
    print("  WARNING: IS_SYNTHETIC column missing -- treating all as syn")
    syn = df.copy()
    obs = df.iloc[0:0].copy()

print(f"  Observed rows: {len(obs):,}  |  Synthetic rows: {len(syn):,}")

# Restrict to hom30 columns present in the file
present_hom = [c for c in HOM_COLS if c in df.columns]
if len(present_hom) != 48:
    print(f"  WARNING: found {len(present_hom)}/48 hom30 columns")

# ── helper: per-row transition count ──────────────────────────────────────────
def transitions_per_row(df_sub, cols):
    """Returns 1-D array of per-row hom30 transition counts (same as Gate-B)."""
    if len(df_sub) == 0 or not cols:
        return np.array([], dtype=float)
    arr = df_sub[cols].to_numpy(dtype=float)
    diff = np.abs(np.diff(arr, axis=1))       # (N, 47)
    return np.nansum(diff, axis=1)             # (N,)

# ── helper: distribution summary ──────────────────────────────────────────────
def dist_summary(name, vals):
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        print(f"\n{name}: NO DATA")
        return
    pcts = np.percentile(vals, [10, 25, 50, 75, 90])
    print(f"\n{'─'*60}")
    print(f"  {name}  (N={len(vals):,})")
    print(f"    median={pcts[2]:.2f}  mean={vals.mean():.2f}")
    print(f"    p10={pcts[0]:.1f}  p25={pcts[1]:.1f}  p50={pcts[2]:.1f}  p75={pcts[3]:.1f}  p90={pcts[4]:.1f}")
    # histogram 0..7, 8+
    bins = {k: 0 for k in list(range(9))}
    for v in vals:
        iv = int(v)
        key = min(iv, 8)
        bins[key] = bins.get(key, 0) + 1
    total = sum(bins.values())
    labels = [str(k) if k < 8 else "8+" for k in range(9)]
    row_k = "  count:"
    row_p = "  %    :"
    for k in range(9):
        cnt = bins[k]
        pct_v = 100.0 * cnt / total if total else 0.0
        lbl = labels[k]
        row_k += f"  {lbl}={cnt:6d}"
        row_p += f"  {lbl}={pct_v:5.1f}%"
    print(row_k)
    print(row_p)

# ── 1. Transition distributions ───────────────────────────────────────────────
print("\n\n[1] TRANSITION COUNTS PER PERSON-DAY (hom30)")
obs_trans = transitions_per_row(obs, [c for c in present_hom if c in obs.columns])
syn_trans = transitions_per_row(syn, [c for c in present_hom if c in syn.columns])

dist_summary("OBSERVED  transitions/day", obs_trans)
dist_summary("SYNTHETIC transitions/day", syn_trans)

if len(obs_trans) > 0 and len(syn_trans) > 0:
    obs_med = np.nanmedian(obs_trans)
    syn_med = np.nanmedian(syn_trans)
    ratio = syn_med / max(obs_med, 1e-6)
    print(f"\n  RATIO syn_median / obs_median = {ratio:.3f}x  "
          f"(obs {obs_med:.2f}  syn {syn_med:.2f})")

# ── 2. Run-length analysis (syn only) ────────────────────────────────────────
print("\n\n[2] SYN HOME/AWAY RUN-LENGTH DISTRIBUTION")

def run_lengths(df_sub, cols, target_state):
    """
    Collect run-lengths of consecutive identical slots equal to target_state.
    Returns array of run-lengths (integers).
    """
    if len(df_sub) == 0 or not cols:
        return np.array([], dtype=int)
    arr = df_sub[cols].to_numpy(dtype=float)
    all_lens = []
    for row in arr:
        # treat NaN as the opposite state (won't happen but safe)
        mask = (~np.isnan(row)) & (row == target_state)
        in_run = False
        run_len = 0
        for v in mask:
            if v:
                in_run = True
                run_len += 1
            else:
                if in_run and run_len > 0:
                    all_lens.append(run_len)
                in_run = False
                run_len = 0
        if in_run and run_len > 0:
            all_lens.append(run_len)
    return np.array(all_lens, dtype=int)

syn_hom_cols = [c for c in present_hom if c in syn.columns]

print("  Computing HOME run-lengths (hom30==1) ...", flush=True)
home_runs = run_lengths(syn, syn_hom_cols, 1.0)
print("  Computing AWAY run-lengths (hom30==0) ...", flush=True)
away_runs = run_lengths(syn, syn_hom_cols, 0.0)

def rl_summary(name, runs):
    if len(runs) == 0:
        print(f"\n  {name}: NO RUNS FOUND")
        return
    total = len(runs)
    len1 = int((runs == 1).sum())
    len2 = int((runs == 2).sum())
    len3plus = int((runs >= 3).sum())
    pcts = np.percentile(runs, [10, 25, 50, 75, 90])
    print(f"\n  {name}  (N runs={total:,})")
    print(f"    median={pcts[2]:.1f}  mean={runs.mean():.2f}  max={runs.max()}")
    print(f"    p10={pcts[0]:.0f}  p25={pcts[1]:.0f}  p50={pcts[2]:.0f}  p75={pcts[3]:.0f}  p90={pcts[4]:.0f}")
    print(f"    len=1 (30min blips): {len1:,}  ({100.*len1/total:.1f}%)")
    print(f"    len=2 (60min runs):  {len2:,}  ({100.*len2/total:.1f}%)")
    print(f"    len>=3 (90min+):     {len3plus:,}  ({100.*len3plus/total:.1f}%)")

rl_summary("SYN HOME runs (hom30==1)", home_runs)
rl_summary("SYN AWAY runs (hom30==0)", away_runs)

# ── 3. Simulate min-dwell=2 post-processing ───────────────────────────────────
print("\n\n[3] SIMULATED MIN-DWELL=2 POST-PROCESS (syn only)")
print("  Merging 1-slot runs: any isolated slot (different on both sides) is flipped to neighbor ...")

def apply_min_dwell2(arr_in):
    """
    Remove 1-slot blips: if arr[i] differs from arr[i-1] AND arr[i+1], replace arr[i] = arr[i-1].
    Pass over once left-to-right (approximation; good enough for diagnostic).
    Binary (0/1) values assumed.
    """
    arr = arr_in.copy()
    N, S = arr.shape
    for i in range(1, S - 1):
        # mask: differs from left and from right
        blip = (~np.isnan(arr[:, i-1])) & (~np.isnan(arr[:, i])) & (~np.isnan(arr[:, i+1])) & \
               (arr[:, i] != arr[:, i-1]) & (arr[:, i] != arr[:, i+1])
        arr[blip, i] = arr[blip, i-1]
    return arr

chunk_size = 50000
syn_arr_raw = syn[syn_hom_cols].to_numpy(dtype=float)
n_rows = len(syn_arr_raw)
print(f"  Processing {n_rows:,} rows in chunks of {chunk_size:,} ...", flush=True)

fixed_trans = []
for start in range(0, n_rows, chunk_size):
    chunk = syn_arr_raw[start:start+chunk_size]
    fixed = apply_min_dwell2(chunk)
    diff = np.abs(np.diff(fixed, axis=1))
    fixed_trans.append(np.nansum(diff, axis=1))
    if start % 200000 == 0:
        print(f"    ... {start:,}/{n_rows:,}", flush=True)

syn_trans_fixed = np.concatenate(fixed_trans)
dist_summary("SYNTHETIC (min-dwell=2 applied) transitions/day", syn_trans_fixed)

if len(syn_trans) > 0:
    syn_med_orig  = np.nanmedian(syn_trans)
    syn_med_fixed = np.nanmedian(syn_trans_fixed)
    print(f"\n  Median before min-dwell: {syn_med_orig:.2f}")
    print(f"  Median after  min-dwell: {syn_med_fixed:.2f}")
    reduction_pct = 100.0 * (syn_med_orig - syn_med_fixed) / max(syn_med_orig, 1e-6)
    print(f"  Reduction: {reduction_pct:.1f}%")
    if len(obs_trans) > 0:
        obs_med = np.nanmedian(obs_trans)
        print(f"  Obs median target:       {obs_med:.2f}")
        gap_before = syn_med_orig - obs_med
        gap_after  = syn_med_fixed - obs_med
        print(f"  Gap before: {gap_before:+.2f}  |  Gap after: {gap_after:+.2f}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
