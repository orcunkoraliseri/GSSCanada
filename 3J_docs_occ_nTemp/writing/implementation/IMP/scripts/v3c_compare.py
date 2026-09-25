#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3c -- F (Default_NECB with dwelling-unit/apartment+hotel occupancy) vs U (Default_NECB,
frozen, NECB-A office occupancy on those same PEOPLE objects) comparison.

Reuses p3_code_schedule_comparison.py's functions (circ, resultant, load, wd_profile) rather
than reimplementing the peak-hour / coincidence-factor / EUI math. Task doc: V3c_fair_control.md
section 6. READ-ONLY on Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable (U). Writes only
under writing/implementation/IMP/data/V3c/.

U aggregate: frozen `agg_deliverable` (never re-aggregated here), filtered to cell_tag starting
"Default_NECB__" (== scenario Default_NECB, per agg_meta.csv).
F aggregate: `IMP/data/V3c/agg_V3c_F` (built locally from the 4 Speed-run V3c cells by the
Step-8E aggregator, same CLI U itself was built with; not re-derived by hand here).

Usage:
  PYTHONIOENCODING=utf-8 py -3 v3c_compare.py [--agg-f DIR] [--agg-u DIR] [--outdir DIR] [--tag TAG]

--agg-f / --agg-u let the self-test (step 5, "gates must be seen failing") point both arms at
the same directory (U vs U -> expect zero diff) or at a deliberately altered copy of F (expect
a nonzero diff), without touching the real run.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IMP = os.path.dirname(HERE)                                   # writing/implementation/IMP
J3 = os.path.abspath(os.path.join(IMP, "..", "..", ".."))     # 3J_docs_occ_nTemp
AGG_U_DEFAULT = os.path.join(J3, "Leg3_4-split", "Step8_docs", "outputs_step8", "agg_deliverable")
AGG_F_DEFAULT = os.path.join(IMP, "data", "V3c", "agg_V3c_F")
OUT_DEFAULT = os.path.join(IMP, "data", "V3c")

# ---- import p3_code_schedule_comparison.py as a module, reuse its functions verbatim ----
_P3_PATH = os.path.join(HERE, "p3_code_schedule_comparison.py")
_spec = importlib.util.spec_from_file_location("p3_code_schedule_comparison", _P3_PATH)
_p3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p3)   # module-level code only defines constants/functions (main() is
                                 # guarded by __name__ == "__main__"), safe to exec on import

circ = _p3.circ
resultant = _p3.resultant
load = _p3.load
wd_profile = _p3.wd_profile

TENANT = ["office", "retail", "hotel", "residential"]
BLD_CITY = [("SuperTall", "MTL"), ("SuperTall", "CLG"), ("Tall", "MTL"), ("Tall", "CLG")]
DAY_H = list(range(8, 18))
NIGHT_H = [h for h in range(24) if h not in DAY_H]


def load_arm(agg_dir, cell_prefix="Default_NECB__"):
    """Load one arm's agg_{peak,diurnal,meta,annual_by_channel}.csv, filtered to the
    Default_NECB cells (4 building x city combinations)."""
    A = load(agg_dir)
    peak, diur, meta, eui = A["peak"], A["diurnal"], A["meta"], A["annual_by_channel"]
    cells = [f"{cell_prefix}{b}__{c}" for b, c in BLD_CITY]
    peak = peak[peak["cell_tag"].isin(cells)].copy()
    diur = diur[diur["cell_tag"].isin(cells)].copy()
    meta = meta[meta["cell_tag"].isin(cells)].copy()
    eui = eui[eui["cell_tag"].isin(cells)].copy()
    return dict(peak=peak, diur=diur, meta=meta, eui=eui, cells=cells)


def presence_by_hour(arm_data, arm_label):
    """Weekday presence (people metric) by hour, per channel, per cell."""
    diur = arm_data["diur"]
    rows = []
    for b, c in BLD_CITY:
        cell = f"Default_NECB__{b}__{c}"
        for ch in TENANT:
            p = wd_profile(diur, cell, ch, metric="people", daytype="WD")
            for h in range(24):
                rows.append(dict(arm=arm_label, cell_tag=cell, building=b, city=c,
                                  channel=ch, hour=h, wd_people=float(p[h]) if len(p) == 24 else np.nan))
    return pd.DataFrame(rows)


def per_cell_metrics(arm_data, arm_label):
    """Per-channel + whole-building peak hour, coincidence factor, EUI -- one row per
    (cell, channel), matching the shape of P3_comparison_summary.csv (arm column added)."""
    peak, diur, eui = arm_data["peak"], arm_data["diur"], arm_data["eui"]
    rows = []
    for b, c in BLD_CITY:
        cell = f"Default_NECB__{b}__{c}"
        brow = peak[(peak.cell_tag == cell) & (peak.channel == "_BUILDING")
                    & (peak.daytype == "all") & (peak.metric == "energy_W")]
        if len(brow) != 1:
            raise SystemExit(f"expected exactly 1 _BUILDING/all/energy_W row for {cell}, got {len(brow)}")
        brow = brow.iloc[0]
        rows.append(dict(arm=arm_label, cell_tag=cell, building=b, city=c, channel="_BUILDING",
                          peak_hour_circular=brow.peak_hour_circular,
                          coincidence_factor=brow.coincidence_factor,
                          eui_CFA_kWh_m2=np.nan))
        for ch in TENANT:
            p_e = wd_profile(diur, cell, ch, metric="energy_W", daytype="WD")
            p_p = wd_profile(diur, cell, ch, metric="people", daytype="WD")
            e = eui[(eui.cell_tag == cell) & (eui.channel == ch)]
            e_val = float(e["eui_CFA_kWh_m2"].iloc[0]) if len(e) == 1 else np.nan
            rows.append(dict(arm=arm_label, cell_tag=cell, building=b, city=c, channel=ch,
                              wd_peak_hour_circular_energy=circ(p_e) if len(p_e) == 24 else np.nan,
                              occ_wd_peak_hour_circular=circ(p_p) if len(p_p) == 24 else np.nan,
                              wd_night_people=(np.concatenate([p_p[0:5], p_p[22:24]]).mean()
                                               if len(p_p) == 24 else np.nan),
                              wd_midday_people=(p_p[11:15].mean() if len(p_p) == 24 else np.nan),
                              eui_CFA_kWh_m2=e_val))
    return pd.DataFrame(rows)


def build_summary(f_metrics, u_metrics):
    """arm column (U/F) + diff, table shaped like P3_comparison_summary.csv."""
    both = pd.concat([u_metrics, f_metrics], ignore_index=True)
    num_cols = [c for c in both.columns if c not in ("arm", "cell_tag", "building", "city", "channel")]
    summ = both.groupby(["channel", "arm"])[num_cols].median().reset_index()
    # diff F - U per channel (median over 4 cells)
    piv_u = summ[summ.arm == "U"].set_index("channel")
    piv_f = summ[summ.arm == "F"].set_index("channel")
    diff_rows = []
    for ch in piv_u.index:
        if ch not in piv_f.index:
            continue
        row = dict(channel=ch)
        for col in num_cols:
            u_val, f_val = piv_u.loc[ch, col], piv_f.loc[ch, col]
            if pd.isna(u_val) or pd.isna(f_val):
                continue
            if "hour" in col:
                d = (f_val - u_val + 12) % 24 - 12
            else:
                d = f_val - u_val
            row[f"diff_F_minus_U__{col}"] = d
        diff_rows.append(row)
    diff = pd.DataFrame(diff_rows)
    return summ, diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg-f", default=AGG_F_DEFAULT)
    ap.add_argument("--agg-u", default=AGG_U_DEFAULT)
    ap.add_argument("--outdir", default=OUT_DEFAULT)
    ap.add_argument("--tag", default="")   # suffix for output filenames, used by the self-test
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    U = load_arm(args.agg_u)
    F = load_arm(args.agg_f)

    pres_u = presence_by_hour(U, "U")
    pres_f = presence_by_hour(F, "F")
    presence = pd.concat([pres_u, pres_f], ignore_index=True)

    met_u = per_cell_metrics(U, "U")
    met_f = per_cell_metrics(F, "F")
    metrics = pd.concat([met_u, met_f], ignore_index=True)

    summ, diff = build_summary(met_f, met_u)

    suf = f"_{args.tag}" if args.tag else ""
    presence_path = os.path.join(args.outdir, f"v3c_presence_by_hour{suf}.csv")
    metrics_path = os.path.join(args.outdir, f"v3c_per_cell_metrics{suf}.csv")
    summary_path = os.path.join(args.outdir, f"v3c_comparison_summary{suf}.csv")
    diff_path = os.path.join(args.outdir, f"v3c_comparison_diff{suf}.csv")
    presence.to_csv(presence_path, index=False)
    metrics.to_csv(metrics_path, index=False)
    summ.to_csv(summary_path, index=False)
    diff.to_csv(diff_path, index=False)

    # console summary
    pd.set_option("display.width", 250, "display.max_columns", 40)
    print("=== per-channel/arm medians (4 cells) ===")
    show_cols = ["channel", "arm", "peak_hour_circular", "coincidence_factor",
                 "wd_peak_hour_circular_energy", "occ_wd_peak_hour_circular",
                 "wd_night_people", "wd_midday_people", "eui_CFA_kWh_m2"]
    show_cols = [c for c in show_cols if c in summ.columns]
    print(summ[show_cols].round(4).to_string())
    print("\n=== diff (F - U), signed circular for hour columns ===")
    print(diff.round(4).to_string())

    # whole-building coincidence factor + peak hour, one line, easy to eyeball
    bld = metrics[metrics.channel == "_BUILDING"]
    for arm in ("U", "F"):
        sub = bld[bld.arm == arm]
        print(f"\n{arm}: building CF median={sub.coincidence_factor.median():.4f} "
              f"peak_hour median={sub.peak_hour_circular.median():.3f}")

    max_abs_diff = float(np.nanmax(np.abs(diff.select_dtypes(include=[float, int]).to_numpy()))) \
        if len(diff) and diff.select_dtypes(include=[float, int]).shape[1] else 0.0
    print(f"\nMAX_ABS_DIFF_ACROSS_ALL_NUMERIC_COLUMNS = {max_abs_diff:.6f}")
    print(f"wrote: {presence_path}\n       {metrics_path}\n       {summary_path}\n       {diff_path}")


if __name__ == "__main__":
    main()
