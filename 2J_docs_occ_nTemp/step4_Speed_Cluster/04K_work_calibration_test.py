"""
04K_work_calibration_test.py — Step 4K: Work-calibration diagnostic (CPU-only)

For 4 candidate models (J3, J5_X1, J6_HC, MDLM_G1):
  (a) Baseline: Work marginal excess, AT_HOME per-slot gaps, co-presence max gap,
      HHSIZE=1 weekday HH below AT_HOME floor (0.30).
  (b) Accounting: midday correlation + mean ratio of Work-excess vs AT_HOME-deficit.
  (c) Calibration: cap synthetic Work at observed rate (convert excess to AT_HOME=1);
      recompute AT_HOME gaps and HH<0.30 count. Co-presence unchanged.

Writes diag_workcal_compare.json and prints a ranked summary table.
Reuses cell/column definitions from 04H and 04I.

Usage (cluster):
    python 04K_work_calibration_test.py
    python 04K_work_calibration_test.py --base_dir /speed-scratch/o_iseri/occModeling
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

N_SLOTS  = 48
CYCLES   = [2005, 2010, 2015, 2022]
STRATA   = [1, 2, 3]

ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WORK_CODE     = 1     # raw 1-indexed; Work & Related (act30_* == 1)
AT_HOME_GATE  = 3.0   # pp gate for per-slot AT_HOME max |gap|
AT_HOME_FLOOR = 0.30  # HHSIZE=1 weekday mean AT_HOME threshold

# Midday: 0-indexed positions 14–27 (11:00 AM–5:59 PM, diaries start 4 AM)
MIDDAY_START = 14
MIDDAY_END   = 28

# 9 co-presence channels (from 04E COP_COLS)
COP_CHANNELS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
OLD_CYCLES = {2005, 2010}   # colleagues column = NaN for observed rows in these cycles

MODELS_REL = {
    "J3":      "outputs_step4_J3/augmented_diaries.csv",
    "J5_X1":   "outputs_step4_J5_X1/augmented_diaries.csv",
    "J6_HC":   "outputs_step4_J6_HC/augmented_diaries.csv",
    "MDLM_G1": "outputs_step4_full/MDLM_G1/augmented_diaries.csv",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base_dir",    default=None,
                   help="Base dir containing outputs_step4_* dirs.")
    p.add_argument("--step3_dir",   default=None,
                   help="Step-3 outputs dir (hetus_30min.csv).")
    p.add_argument("--output_json", default=None,
                   help="JSON destination.")
    return p.parse_args()


def _resolve_paths(args):
    base_dir  = args.base_dir  or "/speed-scratch/o_iseri/occModeling"
    step3_dir = args.step3_dir or os.path.join(base_dir, "outputs_step3")
    out_json  = args.output_json or os.path.join(base_dir, "diag_workcal_compare.json")
    return base_dir, step3_dir, out_json


# ── Co-presence helpers ─────────────────────────────────────────────────────

def _cop_max_gap_per_cell(syn_c, obs_src_c, cy):
    """Max |gap| pp across 9 channels for one (cycle × stratum) cell."""
    max_gap = 0.0
    for ch in COP_CHANNELS:
        cols = [f"{ch}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
        cols_s = [c for c in cols if c in syn_c.columns]
        cols_o = [c for c in cols if c in obs_src_c.columns]
        if not cols_s or not cols_o:
            continue
        use_nan = ch == "colleagues" and cy in OLD_CYCLES
        fn = np.nanmean if use_nan else np.mean
        s_prev = float(fn(syn_c[cols_s].values.astype(float)))
        o_prev = float(fn(obs_src_c[cols_o].values.astype(float)))
        gap = abs(s_prev - o_prev) * 100.0
        if gap > max_gap:
            max_gap = gap
    return max_gap


# ── Main model analysis ─────────────────────────────────────────────────────

def analyse_model(model_name, csv_path, obs_df):
    print(f"\n[{model_name}]  {csv_path}", flush=True)
    if not os.path.exists(csv_path):
        print(f"  ERROR: file not found — skipping", flush=True)
        return None

    aug     = pd.read_csv(csv_path, low_memory=False)
    syn     = aug[aug["IS_SYNTHETIC"] == 1].copy()
    obs_src = aug[aug["IS_SYNTHETIC"] == 0].copy()
    print(f"  rows: aug={len(aug)}  syn={len(syn)}  obs_src={len(obs_src)}", flush=True)

    has_hhsize = "HHSIZE" in syn.columns
    if not has_hhsize:
        print("  WARN: HHSIZE column missing; HH<0.30 counts will be 0", flush=True)

    # HHSIZE=1, weekday (DDAY_STRATA=1), synthetic — for floor count
    if has_hhsize:
        syn_wd_h1 = syn[(syn["DDAY_STRATA"] == 1) & (syn["HHSIZE"] == 1)].copy()
    else:
        syn_wd_h1 = pd.DataFrame()

    # Weekday calibration params (strata=1) keyed by cycle year
    excess_by_cy   = {}   # cy -> np.array(48,) excess fractions (max(0, syn_work - obs_work))
    syn_work_by_cy = {}   # cy -> np.array(48,) syn work fractions

    per_cell = {}
    # Collect midday (work excess, AT_HOME deficit) across all cells for accounting
    all_work_ex_mid  = []
    all_at_home_def_mid = []

    for cy in CYCLES:
        for s in STRATA:
            obs_c     = obs_df[(obs_df["CYCLE_YEAR"] == cy) & (obs_df["DDAY_STRATA"] == s)]
            syn_c     = syn[(syn["CYCLE_YEAR"] == cy) & (syn["DDAY_STRATA"] == s)]
            obs_src_c = obs_src[(obs_src["CYCLE_YEAR"] == cy) & (obs_src["DDAY_STRATA"] == s)]
            if len(obs_c) == 0 or len(syn_c) == 0:
                continue

            obs_act = obs_c[ACT_COLS].values   # (n_obs, 48)
            syn_act = syn_c[ACT_COLS].values   # (n_syn, 48)

            obs_work_ps = (obs_act == WORK_CODE).mean(axis=0)   # (48,) fraction
            syn_work_ps = (syn_act == WORK_CODE).mean(axis=0)
            work_excess_ps = syn_work_ps - obs_work_ps           # signed fractions

            obs_hom_ps = obs_c[HOM_COLS].values.astype(float).mean(axis=0)  # (48,)
            syn_hom_ps = syn_c[HOM_COLS].values.astype(float).mean(axis=0)
            at_home_gap = (syn_hom_ps - obs_hom_ps) * 100.0    # pp, signed

            # (a) Baseline
            base_max_gap = float(np.abs(at_home_gap).max())
            base_fail    = int((np.abs(at_home_gap) > AT_HOME_GATE).sum())
            work_excess_mean_pp = float(work_excess_ps.mean() * 100)

            # Verify Work→AT_HOME=0 (post-hoc rule in 04E guarantees this)
            work_any = (syn_act == WORK_CODE).any()
            if work_any:
                work_hom_mat = syn_c[HOM_COLS].values.astype(float)
                work_mask_2d = (syn_act == WORK_CODE)  # (n_syn, 48)
                work_at_home_mean = float(work_hom_mat[work_mask_2d].mean()) if work_mask_2d.any() else None
            else:
                work_at_home_mean = None

            # (b) Accounting: midday slots
            mid = slice(MIDDAY_START, MIDDAY_END)
            mid_work_ex    = work_excess_ps[mid] * 100              # (14,) pp
            mid_at_home_def = -at_home_gap[mid]                     # (14,) pp (positive=deficit)
            all_work_ex_mid.extend(mid_work_ex.tolist())
            all_at_home_def_mid.extend(mid_at_home_def.tolist())

            # Failing midday slots (|AT_HOME gap| > 3 pp)
            failing_mid = [
                MIDDAY_START + i
                for i, g in enumerate(at_home_gap[mid])
                if abs(g) > AT_HOME_GATE
            ]

            # (c) Calibration: cap Work at observed rate
            excess = np.maximum(0.0, work_excess_ps)    # (48,) fractions ≥ 0
            cal_hom_pp = syn_hom_ps * 100 + excess * 100
            cal_hom_pp = np.minimum(cal_hom_pp, 100.0)
            cal_gap     = cal_hom_pp - obs_hom_ps * 100
            cal_max_gap = float(np.abs(cal_gap).max())
            cal_fail    = int((np.abs(cal_gap) > AT_HOME_GATE).sum())

            # COP baseline for this cell
            cop_cell = _cop_max_gap_per_cell(syn_c, obs_src_c, cy)

            if s == 1:
                excess_by_cy[cy]   = excess
                syn_work_by_cy[cy] = syn_work_ps

            per_cell[f"{cy}_{s}"] = {
                "n_obs": int(len(obs_c)),
                "n_syn": int(len(syn_c)),
                "work_excess_mean_pp":   round(work_excess_mean_pp, 3),
                "base_max_gap_pp":       round(base_max_gap, 3),
                "base_fail_slots":       base_fail,
                "failing_midday_slots":  failing_mid,
                "cal_max_gap_pp":        round(cal_max_gap, 3),
                "cal_fail_slots":        cal_fail,
                "cop_max_gap_pp":        round(cop_cell, 3),
                "work_at_home_mean":     round(work_at_home_mean, 4) if work_at_home_mean is not None else None,
            }

    # Overall accounting stats (pooled across all cells × midday slots)
    if len(all_work_ex_mid) > 2:
        acct_corr = float(np.corrcoef(all_work_ex_mid, all_at_home_def_mid)[0, 1])
        wex  = np.array(all_work_ex_mid)
        adef = np.array(all_at_home_def_mid)
        pos_mask = wex > 0.0
        mean_ratio = float(np.mean(adef[pos_mask] / (wex[pos_mask] + 1e-12))) if pos_mask.any() else None
    else:
        acct_corr = mean_ratio = None

    # Overall rollup across cells
    if per_cell:
        base_max_overall  = max(v["base_max_gap_pp"]  for v in per_cell.values())
        base_fail_total   = sum(v["base_fail_slots"]   for v in per_cell.values())
        cal_max_overall   = max(v["cal_max_gap_pp"]   for v in per_cell.values())
        cal_fail_total    = sum(v["cal_fail_slots"]    for v in per_cell.values())
        cop_max_overall   = max(v["cop_max_gap_pp"]   for v in per_cell.values())
        work_excess_overall = float(np.mean([v["work_excess_mean_pp"] for v in per_cell.values()]))
    else:
        base_max_overall = cal_max_overall = cop_max_overall = 0.0
        base_fail_total = cal_fail_total = 0
        work_excess_overall = 0.0

    # HH<0.30 baseline
    if len(syn_wd_h1) > 0:
        hom_bl = syn_wd_h1[HOM_COLS].values.astype(float)
        n_hh_base = int((hom_bl.mean(axis=1) < AT_HOME_FLOOR).sum())
    else:
        n_hh_base = 0

    # HH<0.30 post-calibration (expected value approach)
    # For each Work slot in a HHSIZE=1 weekday row: if that cell has excess Work,
    # the slot is reassigned to AT_HOME=1 with probability p = excess/syn_work_frac.
    # Expected post-cal AT_HOME mean is computed per-row without modifying the DataFrame.
    if len(syn_wd_h1) > 0 and excess_by_cy:
        hom_cal  = syn_wd_h1[HOM_COLS].values.astype(float).copy()
        act_wd   = syn_wd_h1[ACT_COLS].values
        cy_vals  = syn_wd_h1["CYCLE_YEAR"].values
        for cy in CYCLES:
            row_mask = cy_vals == cy
            if not row_mask.any() or cy not in excess_by_cy:
                continue
            exc = excess_by_cy[cy]       # (48,) fractions
            swk = syn_work_by_cy[cy]     # (48,)
            act_sub = act_wd[row_mask, :]
            hom_sub = hom_cal[row_mask, :].copy()
            for t in range(N_SLOTS):
                if exc[t] > 0.0 and swk[t] > 1e-9:
                    p_reasn = min(1.0, exc[t] / swk[t])
                    wk_rows = act_sub[:, t] == WORK_CODE
                    hom_sub[wk_rows, t] = p_reasn   # expected AT_HOME after reassignment
            hom_cal[row_mask, :] = hom_sub
        n_hh_cal = int((hom_cal.mean(axis=1) < AT_HOME_FLOOR).sum())
    else:
        n_hh_cal = n_hh_base

    result = {
        "n_syn": int(len(syn)),
        "n_hhsize1_weekday_syn": int(len(syn_wd_h1)),
        "work_excess_mean_pp":      round(work_excess_overall, 3),
        "accounting_corr":          round(acct_corr, 4) if acct_corr is not None else None,
        "accounting_mean_ratio":    round(mean_ratio, 4) if mean_ratio is not None else None,
        "base_at_home_max_gap_pp":  round(base_max_overall, 3),
        "base_fail_slots_total":    base_fail_total,
        "base_hh_below_floor":      n_hh_base,
        "cop_max_gap_pp":           round(cop_max_overall, 3),
        "cal_at_home_max_gap_pp":   round(cal_max_overall, 3),
        "cal_fail_slots_total":     cal_fail_total,
        "cal_hh_below_floor":       n_hh_cal,
        "per_cell": per_cell,
    }

    # Console summary
    print(f"  BASELINE  : AT_HOME max={base_max_overall:.2f}pp  fail_slots={base_fail_total}  "
          f"HH<0.30={n_hh_base}", flush=True)
    print(f"  POST-CAL  : AT_HOME max={cal_max_overall:.2f}pp  fail_slots={cal_fail_total}  "
          f"HH<0.30={n_hh_cal}", flush=True)
    print(f"  COP max   : {cop_max_overall:.2f}pp", flush=True)
    corr_str  = f"{acct_corr:.3f}"  if acct_corr  is not None else "n/a"
    ratio_str = f"{mean_ratio:.2f}" if mean_ratio is not None else "n/a"
    print(f"  Work excess (mean): {work_excess_overall:.2f}pp  "
          f"acct_corr={corr_str}  ratio={ratio_str}", flush=True)

    return result


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    base_dir, step3_dir, out_json = _resolve_paths(args)

    print("=" * 68)
    print("04K — Work-Calibration Diagnostic")
    print("=" * 68)
    print(f"  base_dir  : {base_dir}")
    print(f"  step3_dir : {step3_dir}")
    print(f"  out_json  : {out_json}")

    # Load observed reference
    hetus_path = os.path.join(step3_dir, "hetus_30min.csv")
    if not os.path.exists(hetus_path):
        print(f"ERROR: {hetus_path} not found — aborting")
        sys.exit(1)
    print(f"\nLoading observed reference: {hetus_path} ...", flush=True)
    obs_df = pd.read_csv(hetus_path, low_memory=False)
    print(f"  {len(obs_df)} observed rows")

    # Confirm Work code in observed data
    act_sample = obs_df[ACT_COLS].values.ravel()
    work_frac = (act_sample == WORK_CODE).mean()
    print(f"  Observed Work (act=={WORK_CODE}) fraction: {work_frac*100:.2f}%")

    # Run per model
    results = {}
    for model_name, rel_path in MODELS_REL.items():
        csv_path = os.path.join(base_dir, rel_path)
        results[model_name] = analyse_model(model_name, csv_path, obs_df)

    # Write JSON
    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
    payload = {
        "run_timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "base_dir": base_dir,
        "step3_dir": step3_dir,
        "gates": {
            "at_home_gate_pp": AT_HOME_GATE,
            "at_home_floor": AT_HOME_FLOOR,
            "midday_slots_0idx": [MIDDAY_START, MIDDAY_END - 1],
        },
        "models": {k: v for k, v in results.items() if v is not None},
    }
    with open(out_json, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n  Wrote: {out_json}")

    # ── Summary table ──────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("SUMMARY TABLE — 4-model Work-Calibration Comparison")
    print("=" * 68)
    hdr = (f"{'Model':<10} {'WkEx':>5} {'Pre-Max':>8} {'Pre-Fail':>9} {'Pre-HH':>7} "
           f"{'Post-Max':>9} {'Post-Fail':>10} {'Post-HH':>8} {'COP-Max':>8} {'AcctCorr':>9}")
    print(hdr)
    print("-" * 68)

    valid = {k: v for k, v in results.items() if v is not None}
    # Sort by post-cal AT_HOME max gap (ascending)
    ranked = sorted(valid.items(), key=lambda kv: kv[1]["cal_at_home_max_gap_pp"])

    for rank, (name, r) in enumerate(ranked, 1):
        wex  = r["work_excess_mean_pp"]
        bmax = r["base_at_home_max_gap_pp"]
        bfai = r["base_fail_slots_total"]
        bhh  = r["base_hh_below_floor"]
        cmax = r["cal_at_home_max_gap_pp"]
        cfai = r["cal_fail_slots_total"]
        chh  = r["cal_hh_below_floor"]
        cop  = r["cop_max_gap_pp"]
        corr = r["accounting_corr"]
        gate_str = " ✓" if cmax <= AT_HOME_GATE else "  "
        corr_fmt = f"{corr:.3f}" if corr is not None else "n/a"
        print(f"  {rank}. {name:<8} {wex:>5.2f} {bmax:>8.2f} {bfai:>9} {bhh:>7} "
              f"{cmax:>9.2f}{gate_str} {cfai:>10} {chh:>8} {cop:>8.2f} "
              f"{corr_fmt:>9}")
    print("-" * 68)
    print(f"  Gates: AT_HOME max ≤ {AT_HOME_GATE:.0f} pp per slot  |  "
          f"HH floor = {AT_HOME_FLOOR:.2f}")

    # ── Verdicts ───────────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("VERDICTS")
    print("=" * 68)

    j3 = valid.get("J3")
    if j3:
        v1_pass = j3["cal_at_home_max_gap_pp"] <= AT_HOME_GATE
        print(f"  Verdict 1 — J3 post-calibration AT_HOME max gap "
              f"({j3['cal_at_home_max_gap_pp']:.2f} pp) "
              f"{'<= 3 pp  GATE PASS' if v1_pass else '> 3 pp  GATE FAIL'}")
    else:
        print("  Verdict 1 — J3 not available")

    passing  = [(n, r) for n, r in ranked if r["cal_at_home_max_gap_pp"] <= AT_HOME_GATE]
    best_overall = None
    if passing:
        # Among gate-passing models, pick lowest COP max gap
        best_overall = min(passing, key=lambda kv: kv[1]["cop_max_gap_pp"])
        print(f"  Verdict 2 — Best post-cal profile: {best_overall[0]}  "
              f"(AT_HOME max={best_overall[1]['cal_at_home_max_gap_pp']:.2f} pp, "
              f"COP max={best_overall[1]['cop_max_gap_pp']:.2f} pp)")
    else:
        # No model passes the gate; pick best available (lowest cal max gap, then cop)
        best_fallback = min(ranked, key=lambda kv: (kv[1]["cal_at_home_max_gap_pp"],
                                                     kv[1]["cop_max_gap_pp"]))
        print(f"  Verdict 2 — No model passes AT_HOME gate post-calibration. "
              f"Best available: {best_fallback[0]}  "
              f"(AT_HOME max={best_fallback[1]['cal_at_home_max_gap_pp']:.2f} pp, "
              f"COP max={best_fallback[1]['cop_max_gap_pp']:.2f} pp)")

    print("=" * 68)
    print(f"\nDone. Results in: {out_json}")


if __name__ == "__main__":
    main()
