#!/usr/bin/env python3
"""
3rdJ Step 4 — G3 Co-Presence Diagnostic (Leg-2, analysis-only, NO retraining)
================================================================================
The augmented diaries store SYNTHETIC co-presence as raw sigmoid *probabilities*
(float [0,1]) and OBSERVED co-presence as binary 0/1. This script analyses the
stored probabilities for one variant to answer: how much of the residual G3 gap
is just the arbitrary 0.5 binarisation cutoff (an operating-point issue, fixable
for free by a per-channel threshold / rank-to-marginal assignment) vs a genuine
shortfall in what the co-presence head learned (a calibration deficit)?

For each of the 9 channels it reports, weighted by WGHT_PER when present:
  obs_prev      observed prevalence (binary, %)
  syn_mean_prob head's mean predicted probability (%)  <- calibration anchor
  syn_prev@0.5  synthetic prevalence at the current 0.5 cutoff (%)
  gap@0.5       |obs_prev - syn_prev@0.5|  (what the validator's G3 currently sees)
  calib_gap     |obs_prev - syn_mean_prob| (mean-prob vs reality)
  t_match       per-channel threshold that makes syn prevalence == obs_prev
  gap@t_match   residual gap after rank-to-marginal (≈0 if achievable)

Decision rule:
  calib_gap small  -> head calibrated; gap@0.5 is an operating-point artifact;
                      a per-channel threshold (t_match) closes it for free.
  calib_gap large  -> genuine learned deficit on that channel -> model-side lever.

Read-only. Writes a small TXT + CSV to --step4_dir. No checkpoints touched.
Run on the cluster via sbatch (reads the ~500 MB diaries CSV).
"""
import argparse
import os
import numpy as np
import pandas as pd

N_SLOTS = 48
COP_COLS = ["Alone", "Spouse", "Children", "parents", "otherInFAMs",
            "otherHHs", "friends", "others", "colleagues"]


def slot_cols(channel):
    return [f"{channel}30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def weighted_mean(mask_2d, w):
    """Mean of a (rows, slots) boolean/float array, weighting each row by w,
    NaN-aware (NaN cells dropped per-row). Returns percent."""
    vals = mask_2d.astype(float)
    # per-row mean over valid slots, then weight across rows
    with np.errstate(invalid="ignore"):
        row_mean = np.nanmean(vals, axis=1)
    ok = ~np.isnan(row_mean)
    if ok.sum() == 0:
        return float("nan")
    return float(np.average(row_mean[ok], weights=w[ok]) * 100.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step4_dir", required=True,
                    help="dir containing augmented_diaries.csv (variant subdir for sweeps)")
    ap.add_argument("--csv", default=None, help="override CSV path")
    args = ap.parse_args()

    csv_path = args.csv or os.path.join(args.step4_dir, "augmented_diaries.csv")
    print(f"[diag] reading {csv_path}", flush=True)

    # only the columns we need (keeps a ~500 MB file manageable)
    cop_cols_all = [c for cn in COP_COLS for c in slot_cols(cn)]
    meta = ["IS_SYNTHETIC", "CYCLE_YEAR", "DDAY_STRATA"]
    head = pd.read_csv(csv_path, nrows=0)
    wcol = "WGHT_PER" if "WGHT_PER" in head.columns else None
    usecols = meta + ([wcol] if wcol else []) + [c for c in cop_cols_all if c in head.columns]
    df = pd.read_csv(csv_path, usecols=usecols)
    print(f"[diag] loaded {len(df):,} rows x {len(usecols)} cols "
          f"(weight col: {wcol or 'NONE -> uniform'})", flush=True)

    syn = df[df["IS_SYNTHETIC"] == 1]
    obs = df[df["IS_SYNTHETIC"] == 0]
    w_syn = syn[wcol].to_numpy(float) if wcol else np.ones(len(syn))
    w_obs = obs[wcol].to_numpy(float) if wcol else np.ones(len(obs))

    rows = []
    for cn in COP_COLS:
        cols = [c for c in slot_cols(cn) if c in df.columns]
        if not cols:
            continue
        ov = obs[cols].to_numpy(float)
        sv = syn[cols].to_numpy(float)

        obs_prev = weighted_mean(ov == 1, w_obs)
        syn_mean_prob = weighted_mean(sv, w_syn)
        syn_prev_05 = weighted_mean(sv >= 0.5, w_syn)
        gap_05 = abs(obs_prev - syn_prev_05)
        calib_gap = abs(obs_prev - syn_mean_prob)

        # rank-to-marginal: threshold so synthetic prevalence == obs_prev
        flat = sv[~np.isnan(sv)]
        if flat.size and not np.isnan(obs_prev):
            t_match = float(np.quantile(flat, max(0.0, 1.0 - obs_prev / 100.0)))
            syn_prev_t = weighted_mean(sv >= t_match, w_syn)
            gap_t = abs(obs_prev - syn_prev_t)
        else:
            t_match, gap_t = float("nan"), float("nan")

        verdict = ("OPERATING-POINT" if calib_gap <= 3.0 else "LEARNED-DEFICIT")
        rows.append(dict(channel=cn, obs_prev=obs_prev, syn_mean_prob=syn_mean_prob,
                         syn_prev_05=syn_prev_05, gap_05=gap_05, calib_gap=calib_gap,
                         t_match=t_match, gap_t_match=gap_t, verdict=verdict))

    res = pd.DataFrame(rows)
    out_csv = os.path.join(args.step4_dir, "g3_copresence_diagnostic.csv")
    out_txt = os.path.join(args.step4_dir, "g3_copresence_diagnostic.txt")
    res.to_csv(out_csv, index=False)

    def fmt(x):
        return "  nan" if (isinstance(x, float) and np.isnan(x)) else f"{x:5.2f}"

    lines = []
    lines.append("G3 Co-Presence Diagnostic (operating-point vs learned-deficit)")
    lines.append(f"CSV: {csv_path}")
    lines.append(f"syn rows: {len(syn):,}   obs rows: {len(obs):,}   "
                 f"weight: {wcol or 'uniform'}")
    lines.append("=" * 96)
    hdr = (f"{'channel':<12} {'obs%':>6} {'meanP%':>7} {'prev@.5%':>9} "
           f"{'gap@.5':>7} {'calibGap':>8} {'t_match':>7} {'gap@t':>6}  verdict")
    lines.append(hdr)
    lines.append("-" * 96)
    for r in rows:
        lines.append(f"{r['channel']:<12} {fmt(r['obs_prev']):>6} "
                     f"{fmt(r['syn_mean_prob']):>7} {fmt(r['syn_prev_05']):>9} "
                     f"{fmt(r['gap_05']):>7} {fmt(r['calib_gap']):>8} "
                     f"{r['t_match']:>7.3f} {fmt(r['gap_t_match']):>6}  {r['verdict']}")
    lines.append("=" * 96)
    n_op = sum(1 for r in rows if r["verdict"] == "OPERATING-POINT")
    lines.append(f"OPERATING-POINT channels: {n_op}/{len(rows)}  "
                 f"(calib_gap<=3pp => threshold fix closes G3 for free)")
    lines.append(f"LEARNED-DEFICIT channels: {len(rows) - n_op}/{len(rows)}  "
                 f"(need a model-side lever)")
    report = "\n".join(lines)
    with open(out_txt, "w") as f:
        f.write(report + "\n")
    print("\n" + report, flush=True)
    print(f"\n[diag] wrote {out_txt}\n[diag] wrote {out_csv}", flush=True)


if __name__ == "__main__":
    main()
