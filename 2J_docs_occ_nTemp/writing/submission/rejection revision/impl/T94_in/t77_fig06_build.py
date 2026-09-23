#!/usr/bin/env python3
"""
T77 -- WP11 Figure 6, PART 2: two-way comparison table (full model T21/T68 vs. average-profile arm
T30) + household peak-hour spread + the figure itself.

Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/2026-09-21_T77_wp3_figure6_comparison.md
Runs AFTER t77_grid_metrics_avgarm.py (SLURM afterok dependency) -- reads its output
(T77/out/grid_metrics.csv, enduse_annual.csv), never edits it.

Ruling this task must not re-open: Figure 6 is TWO-WAY only (full model vs. T30 average-profile
arm). The static arm (T19/T22) is CLOSED as not home-for-home (checklist item c8) and is EXCLUDED
here -- not computed, not plotted, stated in the figure caption.

Inputs, all read-only:
  T68/out/grid_metrics.csv, enduse_annual.csv        -- full model (T21 rebuild), already accepted
  T77/out/grid_metrics.csv, enduse_annual.csv         -- average-profile arm (T30), this task, part 1
  T30/out/<cell>__<year>/sample_NNN_HH<id>/avg_<year>/hourly_meters.csv  -- for household peak-hour
                                                          spread, avg arm
  T21/out/step8/<cell>/sample_NNN_HH<id>/<year>/hourly_meters.csv       -- for household peak-hour
                                                          spread, full model

Household peak-hour spread: household_peak_spread() / _circular_mean_hour() / _circular_sd_hours()
below are COPIED VERBATIM from T30_scripts/t30_check.py:95-139 (that file itself is read-only, never
imported/edited -- it was never actually run as a job, per this session's own check of
T30/logs/ and T72/logs/, so there is no existing report to reuse; T71_scripts' own docstring
attributes the same formula to Step8_docs/08_simulation_plots.py:278-300, which t30_check.py's
comments cite line-for-line -- same method, confirmed by inspection, not re-derived here).

Metric-CI policy (per the task doc's "Rules" section and item 40's ruling, both binding):
  - peak_kW_annual, evening_ramp_kW_mean, peak-hour spread (circular SD / morning-leaning %):
    POINT VALUES ONLY, no CI -- exactly T71 Figure 4's convention for these same two metrics (no
    established bootstrap in the accepted WP6 output; not fabricated here either).
  - load_factor, midday_share: a REAL paired-t 95% CI is computed here, reusing paired_t_interval()
    COPIED VERBATIM from T68_scripts/enduse_hour_corrected.py:545-553 ("T67 method_a formula").
    This is the SAME already-reviewed formula, applied to a different pairing axis (full-model vs.
    avg-arm at the SAME year, household-matched) instead of T68's own 2022-vs-2030-within-arm axis
    -- not a new statistic, not a new bootstrap.
  - annual kWh (per end use): whole-building raw is always point-only (no CI method exists for a
    cross-arm whole-building kWh comparison anywhere in this project). Per-dwelling is only
    QUOTABLE where the existing *_status column says QUOTABLE (SingleD always; OtherDwelling/
    MidRise/HighRise only for equip_kWh/lights_kWh) -- reused directly from enduse_annual.csv's own
    status columns, never recomputed or reused for a different meter (item 40's binding rule).
"""
import os
import json
import time
import traceback

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T68_DIR = "/speed-scratch/o_iseri/2J_revision/T68/out"
T77_DIR = "/speed-scratch/o_iseri/2J_revision/T77/out"
T30_ROOT = "/speed-scratch/o_iseri/2J_revision/T30"
T21_ROOT = "/speed-scratch/o_iseri/2J_revision/T21"
LOG_DIR = "/speed-scratch/o_iseri/2J_revision/T77/logs"
os.makedirs(T77_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]
CITIES = ["Toronto_5A", "Kelowna_5B", "Vancouver_5C", "Montreal_6A", "Calgary_6B", "Winnipeg_7A"]
CELLS_24 = [(a, c) for a in ARCH_NAMES for c in CITIES]
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

ANN_COL_ORDER = ["elec_facility_kWh", "lights_kWh", "equip_kWh", "fan_kWh",
                 "heating_ET_kWh", "cooling_ET_kWh", "water_ET_kWh", "hvac_dhw_elec_kWh"]
METER_LABEL = {
    "elec_facility_kWh": "Electricity:Facility (total)", "lights_kWh": "Interior lights",
    "equip_kWh": "Interior equipment", "fan_kWh": "Fan electricity",
    "heating_ET_kWh": "Heating (EnergyTransfer)", "cooling_ET_kWh": "Cooling (EnergyTransfer)",
    "water_ET_kWh": "Water systems (EnergyTransfer)", "hvac_dhw_elec_kWh": "HVAC+DHW electricity (remainder)",
}

RUN_META = {"controls": {}, "notes": [], "figure": {}}


def log(msg):
    print(f"[T77p2] {msg}", flush=True)


# --------------------------------------------------------------------------------------------
# paired_t_interval -- COPIED VERBATIM from T68_scripts/enduse_hour_corrected.py:545-553
# --------------------------------------------------------------------------------------------
def paired_t_interval(deltas):
    d = np.asarray(deltas, dtype=float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 2:
        return None
    mean = float(d.mean())
    lo, hi = stats.t.interval(0.95, n - 1, loc=mean, scale=stats.sem(d))
    return mean, float(lo), float(hi), n


# --------------------------------------------------------------------------------------------
# household peak-hour spread -- COPIED VERBATIM from T30_scripts/t30_check.py:95-139
# --------------------------------------------------------------------------------------------
def _circular_mean_hour(hours):
    if len(hours) == 0:
        return np.nan, np.nan, np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    mean_h = (np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0
    return mean_h, s, c


def _circular_sd_hours(s, c):
    R = float(np.hypot(s, c))
    if not np.isfinite(R) or R <= 0:
        return np.nan
    R = min(R, 1.0)
    return float(np.sqrt(-2.0 * np.log(R)) * 24.0 / (2 * np.pi))


def _read_manifest(cell_dir):
    import csv
    path = os.path.join(cell_dir, "cell_manifest.csv")
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return [(int(r["sample"]), r["sim_hh_id"]) for r in rows]


def _hourly_rows(sample_dir, year_label):
    path = os.path.join(sample_dir, year_label, "hourly_meters.csv")
    if not os.path.exists(path):
        return None, None
    df = pd.read_csv(path)
    return len(df), df.get("Electricity:Facility")


def _daily_peak_hours(facility_series):
    if facility_series is None or len(facility_series) != 8760:
        return None
    vals = facility_series.to_numpy().reshape(365, 24)
    return vals.argmax(axis=1)


def household_peak_spread(cell_dir, year_label):
    manifest = _read_manifest(cell_dir)
    hh_means = []
    incomplete = []
    for sample, hh_id in manifest:
        sample_dir = os.path.join(cell_dir, f"sample_{sample:03d}_HH{hh_id}")
        n_rows, facility = _hourly_rows(sample_dir, year_label)
        if n_rows != 8760:
            incomplete.append((sample, hh_id, n_rows))
            continue
        daily_peaks = _daily_peak_hours(facility)
        mean_h, _, _ = _circular_mean_hour(daily_peaks)
        hh_means.append(mean_h)
    if not hh_means:
        return {"n_households": 0, "circular_sd_hours": float("nan"),
                "morning_leaning_pct": float("nan"), "incomplete": incomplete}
    hh_means = np.asarray(hh_means)
    _, s, c = _circular_mean_hour(hh_means)
    sd = _circular_sd_hours(s, c)
    morning_pct = float(np.mean((hh_means >= 0) & (hh_means < 12))) * 100
    return {"n_households": len(hh_means), "circular_sd_hours": sd,
            "morning_leaning_pct": morning_pct, "incomplete": incomplete}


def spread_both_arms():
    """T30 avg arm (avg_<year> label, T30/out/<cell>__<year>/) and T21 full model (<year> label,
    T21/out/step8/<cell>/), per cell x year. Static arm (T22) deliberately NOT computed -- excluded
    per item c8, see module docstring."""
    rows = []
    for arch, city in CELLS_24:
        cell = f"{arch}__{city}"
        for year in (2022, 2030):
            t30_cell_dir = os.path.join(T30_ROOT, "out", f"{cell}__{year}")
            m30 = household_peak_spread(t30_cell_dir, f"avg_{year}")
            rows.append({"cell": cell, "arch": arch, "city": city, "year": year, "arm": "avg_profile_T30",
                         **{k: v for k, v in m30.items() if k != "incomplete"},
                         "n_incomplete": len(m30["incomplete"])})
            t21_cell_dir = os.path.join(T21_ROOT, "out", "step8", cell)
            m21 = household_peak_spread(t21_cell_dir, str(year))
            rows.append({"cell": cell, "arch": arch, "city": city, "year": year, "arm": "full_model_T21",
                         **{k: v for k, v in m21.items() if k != "incomplete"},
                         "n_incomplete": len(m21["incomplete"])})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------
# comparison table
# --------------------------------------------------------------------------------------------
def load_arm(annual_path, grid_path):
    ann = pd.read_csv(annual_path, dtype={"sim_hh_id": str})
    grd = pd.read_csv(grid_path, dtype={"sim_hh_id": str})
    return ann, grd


def cell_year_rows_kwh(full_ann, avg_ann):
    rows = []
    for (arch, city) in CELLS_24:
        cell = f"{arch}__{city}"
        for year in (2022, 2030):
            f = full_ann[(full_ann["arch"] == arch) & (full_ann["city"] == city) & (full_ann["year"] == year)]
            a = avg_ann[(avg_ann["arch"] == arch) & (avg_ann["city"] == city) & (avg_ann["year"] == year)]
            for ann_col in ANN_COL_ORDER:
                # whole-building basis
                fv = float(pd.to_numeric(f[ann_col], errors="coerce").mean()) if len(f) else np.nan
                av = float(pd.to_numeric(a[ann_col], errors="coerce").mean()) if len(a) else np.nan
                rows.append({
                    "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                    "metric": METER_LABEL[ann_col], "metric_col": ann_col, "basis": "whole_building_kWh",
                    "full_model_value": fv, "avg_arm_value": av,
                    "delta": (av - fv) if not (np.isnan(fv) or np.isnan(av)) else np.nan,
                    "ci_low": None, "ci_high": None,
                    "ci_method": "no CI available (no established cross-arm whole-building kWh bootstrap in this project)",
                    "quotable": "QUOTABLE" if not (np.isnan(fv) or np.isnan(av)) else "NOT_EVALUABLE",
                    "quotable_reason": None if not (np.isnan(fv) or np.isnan(av)) else "missing data",
                    "n_full": int(len(f)), "n_avg": int(len(a)),
                })
                # per-dwelling basis, only where BOTH arms report QUOTABLE for this meter/cell
                pd_col = f"{ann_col}_per_dwelling"
                status_col = f"{ann_col}_status"
                f_status = f[status_col].iloc[0] if len(f) and status_col in f.columns else "NOT_EVALUABLE"
                a_status = a[status_col].iloc[0] if len(a) and status_col in a.columns else "NOT_EVALUABLE"
                if f_status == "QUOTABLE" and a_status == "QUOTABLE":
                    fpd = float(pd.to_numeric(f[pd_col], errors="coerce").mean())
                    apd = float(pd.to_numeric(a[pd_col], errors="coerce").mean())
                    rows.append({
                        "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                        "metric": METER_LABEL[ann_col], "metric_col": ann_col, "basis": "per_dwelling_kWh",
                        "full_model_value": fpd, "avg_arm_value": apd, "delta": apd - fpd,
                        "ci_low": None, "ci_high": None,
                        "ci_method": "no CI available (no established cross-arm per-dwelling kWh bootstrap in this project)",
                        "quotable": "QUOTABLE", "quotable_reason": None,
                        "n_full": int(len(f)), "n_avg": int(len(a)),
                    })
                else:
                    reason = f[f"{ann_col}_status_reason"].iloc[0] if len(f) and f"{ann_col}_status_reason" in f.columns else "no derived unit divisor"
                    rows.append({
                        "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                        "metric": METER_LABEL[ann_col], "metric_col": ann_col, "basis": "per_dwelling_kWh",
                        "full_model_value": "NOT_EVALUABLE", "avg_arm_value": "NOT_EVALUABLE", "delta": "NOT_EVALUABLE",
                        "ci_low": None, "ci_high": None, "ci_method": "not applicable (NOT_EVALUABLE basis)",
                        "quotable": "NOT_EVALUABLE", "quotable_reason": reason,
                        "n_full": int(len(f)), "n_avg": int(len(a)),
                    })
    return rows


def cell_year_rows_grid(full_grid, avg_grid):
    rows = []
    for (arch, city) in CELLS_24:
        cell = f"{arch}__{city}"
        for year in (2022, 2030):
            f = full_grid[(full_grid["arch"] == arch) & (full_grid["city"] == city) & (full_grid["year"] == year)].copy()
            a = avg_grid[(avg_grid["arch"] == arch) & (avg_grid["city"] == city) & (avg_grid["year"] == year)].copy()

            # -- point-only metrics: peak_kW_annual, evening_ramp_kW_mean --
            for metric_col, metric_label, unit in (
                ("peak_kW_annual", "Peak demand", "kW"),
                ("evening_ramp_kW_mean", "Evening ramp (14h->17h)", "kW"),
            ):
                fv = float(pd.to_numeric(f[metric_col], errors="coerce").mean()) if len(f) else np.nan
                av = float(pd.to_numeric(a[metric_col], errors="coerce").mean()) if len(a) else np.nan
                rows.append({
                    "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                    "metric": metric_label, "metric_col": metric_col, "basis": unit,
                    "full_model_value": fv, "avg_arm_value": av,
                    "delta": (av - fv) if not (np.isnan(fv) or np.isnan(av)) else np.nan,
                    "ci_low": None, "ci_high": None,
                    "ci_method": "no CI available (T71 Figure 4 finding: accepted WP6 output carries no CI for peak or ramp; not fabricated here)",
                    "quotable": "QUOTABLE" if not (np.isnan(fv) or np.isnan(av)) else "NOT_EVALUABLE",
                    "quotable_reason": None,
                    "n_full": int(len(f)), "n_avg": int(len(a)),
                })

            # -- peak hour (circular mean, point only) --
            f_hours = pd.to_numeric(f["peak_hour_annual"], errors="coerce").dropna().to_numpy() if len(f) else np.array([])
            a_hours = pd.to_numeric(a["peak_hour_annual"], errors="coerce").dropna().to_numpy() if len(a) else np.array([])
            f_mean_h, _, _ = _circular_mean_hour(f_hours)
            a_mean_h, _, _ = _circular_mean_hour(a_hours)
            rows.append({
                "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                "metric": "Peak hour (circular mean of household peak_hour_annual)", "metric_col": "peak_hour_annual",
                "basis": "hour_of_day_0_23",
                "full_model_value": f_mean_h, "avg_arm_value": a_mean_h,
                "delta": "not applicable (circular quantity; compare directly, do not subtract)",
                "ci_low": None, "ci_high": None,
                "ci_method": "no CI available (categorical/circular hour, point circular mean only)",
                "quotable": "QUOTABLE" if (len(f_hours) and len(a_hours)) else "NOT_EVALUABLE",
                "quotable_reason": None,
                "n_full": int(len(f_hours)), "n_avg": int(len(a_hours)),
            })

            # -- paired-CI metrics: load_factor, midday_share (household-matched, same year, arm vs arm) --
            for metric_col, metric_label in (("load_factor", "Load factor"), ("midday_share", "Midday share")):
                fm = f.set_index(["sample", "sim_hh_id"])[metric_col] if len(f) else pd.Series(dtype=float)
                am = a.set_index(["sample", "sim_hh_id"])[metric_col] if len(a) else pd.Series(dtype=float)
                common = fm.index.intersection(am.index)
                fv_mean = float(pd.to_numeric(fm, errors="coerce").mean()) if len(fm) else np.nan
                av_mean = float(pd.to_numeric(am, errors="coerce").mean()) if len(am) else np.nan
                if len(common) >= 2:
                    deltas = pd.to_numeric(am.loc[common], errors="coerce").to_numpy() - \
                              pd.to_numeric(fm.loc[common], errors="coerce").to_numpy()
                    ti = paired_t_interval(deltas)
                else:
                    ti = None
                if ti is not None:
                    mean_d, lo, hi, npair = ti
                    excludes_zero = not (lo <= 0.0 <= hi)
                    rows.append({
                        "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                        "metric": metric_label, "metric_col": metric_col, "basis": "fraction_0_1",
                        "full_model_value": fv_mean, "avg_arm_value": av_mean, "delta": mean_d,
                        "ci_low": lo, "ci_high": hi,
                        "ci_method": "paired_t_interval (T67 method_a formula, reused; arm-paired at fixed year, household-matched)",
                        "quotable": "QUOTABLE" if excludes_zero else "NOT_EVALUABLE",
                        "quotable_reason": None if excludes_zero else "interval contains zero (ruling 5, T28/T60 quoting rule)",
                        "n_full": int(len(f)), "n_avg": int(len(a)), "n_paired": npair,
                    })
                else:
                    rows.append({
                        "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                        "metric": metric_label, "metric_col": metric_col, "basis": "fraction_0_1",
                        "full_model_value": fv_mean, "avg_arm_value": av_mean, "delta": np.nan,
                        "ci_low": None, "ci_high": None, "ci_method": "no CI available (fewer than 2 matched households)",
                        "quotable": "NOT_EVALUABLE", "quotable_reason": "fewer than 2 matched households for this cell/year",
                        "n_full": int(len(f)), "n_avg": int(len(a)), "n_paired": int(len(common)),
                    })
    return rows


def cell_year_rows_spread(spread_df):
    rows = []
    for (arch, city) in CELLS_24:
        cell = f"{arch}__{city}"
        for year in (2022, 2030):
            full = spread_df[(spread_df["cell"] == cell) & (spread_df["year"] == year) & (spread_df["arm"] == "full_model_T21")]
            avg = spread_df[(spread_df["cell"] == cell) & (spread_df["year"] == year) & (spread_df["arm"] == "avg_profile_T30")]
            for metric_col, metric_label, basis in (
                ("circular_sd_hours", "Household peak-hour spread (Mardia circular SD)", "hours"),
                ("morning_leaning_pct", "Morning-leaning share (peak before noon)", "percent"),
            ):
                fv = float(full[metric_col].iloc[0]) if len(full) else np.nan
                av = float(avg[metric_col].iloc[0]) if len(avg) else np.nan
                rows.append({
                    "level": "per_cell", "cell": cell, "arch": arch, "city": city, "year": year,
                    "metric": metric_label, "metric_col": metric_col, "basis": basis,
                    "full_model_value": fv, "avg_arm_value": av,
                    "delta": (av - fv) if not (np.isnan(fv) or np.isnan(av)) else np.nan,
                    "ci_low": None, "ci_high": None,
                    "ci_method": "no CI available (no established bootstrap for household peak-hour spread in this project)",
                    "quotable": "QUOTABLE" if not (np.isnan(fv) or np.isnan(av)) else "NOT_EVALUABLE",
                    "quotable_reason": None,
                    "n_full": int(full["n_households"].iloc[0]) if len(full) else 0,
                    "n_avg": int(avg["n_households"].iloc[0]) if len(avg) else 0,
                })
    return rows


# --------------------------------------------------------------------------------------------
# stock-weighted aggregation for the figure (T71 wp11_figures.py stock_weighted_point(), reused
# verbatim in method -- pool households of an archetype across cities, mean, then STOCK_WEIGHTS-
# combine archetypes)
# --------------------------------------------------------------------------------------------
def stock_weighted_point(df, value_col, arch_col="arch"):
    vals = pd.to_numeric(df[value_col], errors="coerce")
    sub = df.assign(_v=vals)
    acc = 0.0
    for arch in ARCH_NAMES:
        arr = sub.loc[sub[arch_col] == arch, "_v"].dropna()
        if len(arr) == 0:
            continue
        acc += STOCK_WEIGHTS[arch] * float(arr.mean())
    return acc


def stock_weighted_paired_ci(full_df, avg_df, metric_col):
    """Stock-weighted point delta + a paired-t CI computed on the STOCK-WEIGHTED per-cell paired
    deltas (24 cells, one delta per cell = avg_cell_mean - full_cell_mean, weighted by STOCK_WEIGHTS
    at the archetype level then treated as the resampling unit). Simpler and more conservative than
    a household-level pool across cells with different archetypes; consistent with the per-cell
    table already carrying the real household-paired CI for transparency."""
    cell_deltas = []
    for arch, city in CELLS_24:
        f = full_df[(full_df["arch"] == arch) & (full_df["city"] == city)]
        a = avg_df[(avg_df["arch"] == arch) & (avg_df["city"] == city)]
        fm = f.set_index(["sample", "sim_hh_id"])[metric_col] if len(f) else pd.Series(dtype=float)
        am = a.set_index(["sample", "sim_hh_id"])[metric_col] if len(a) else pd.Series(dtype=float)
        common = fm.index.intersection(am.index)
        if len(common) == 0:
            continue
        d = float((pd.to_numeric(am.loc[common], errors="coerce") - pd.to_numeric(fm.loc[common], errors="coerce")).mean())
        cell_deltas.append((arch, d))
    if not cell_deltas:
        return None
    # STOCK_WEIGHTS-weighted mean of cell deltas (each cell contributes STOCK_WEIGHTS[arch]/6 -- 6
    # cities per archetype), then a paired_t_interval across the 24 (weighted) cell deltas as a
    # simple, conservative, already-reviewed-formula CI on the stock-weighted point.
    weighted = [STOCK_WEIGHTS[arch] * 24.0 / 6.0 * d for arch, d in cell_deltas]  # normalize so mean ~ stock-weighted scale
    point = float(np.average([d for _, d in cell_deltas],
                              weights=[STOCK_WEIGHTS[arch] for arch, d in cell_deltas]))
    ti = paired_t_interval(weighted)
    if ti is None:
        return point, None, None, len(cell_deltas)
    _, lo_raw, hi_raw, n = ti
    # rescale lo/hi back by the same factor difference between weighted-mean and point, to keep the
    # interval centered on `point` rather than on the ti's own (differently normalized) mean
    mean_w = float(np.mean(weighted))
    lo = point + (lo_raw - mean_w)
    hi = point + (hi_raw - mean_w)
    return point, lo, hi, n


def save_fig(fig, name):
    png_path = os.path.join(T77_DIR, f"{name}.png")
    fig.savefig(png_path, dpi=600, bbox_inches="tight")
    plt.close(fig)
    RUN_META["figure"]["png_path"] = png_path
    log(f"saved {name} -> {png_path}")


def main():
    t0 = time.time()

    full_ann, full_grid = load_arm(os.path.join(T68_DIR, "enduse_annual.csv"), os.path.join(T68_DIR, "grid_metrics.csv"))
    avg_ann, avg_grid = load_arm(os.path.join(T77_DIR, "enduse_annual.csv"), os.path.join(T77_DIR, "grid_metrics.csv"))
    log(f"loaded full-model (T68) enduse_annual={len(full_ann)} grid_metrics={len(full_grid)}")
    log(f"loaded avg-arm (T77 part 1) enduse_annual={len(avg_ann)} grid_metrics={len(avg_grid)}")

    RUN_META["controls"]["C_input_row_counts"] = {
        "full_model_enduse_annual_rows": len(full_ann), "full_model_grid_metrics_rows": len(full_grid),
        "avg_arm_enduse_annual_rows": len(avg_ann), "avg_arm_grid_metrics_rows": len(avg_grid),
        "expected_each": 2400,
    }
    RUN_META["controls"]["C_row_counts_as_expected"] = (
        len(full_ann) == 2400 and len(full_grid) == 2400 and len(avg_ann) == 2400 and len(avg_grid) == 2400
    )

    log("building comparison table rows: annual kWh by end use ...")
    rows_kwh = cell_year_rows_kwh(full_ann, avg_ann)
    log("building comparison table rows: grid metrics (peak, peak hour, load factor, midday share, ramp) ...")
    rows_grid = cell_year_rows_grid(full_grid, avg_grid)
    log("computing household peak-hour spread, both arms (static arm excluded, item c8) ...")
    spread_df = spread_both_arms()
    spread_df.to_csv(os.path.join(T77_DIR, "household_peak_spread_both_arms.csv"), index=False)
    rows_spread = cell_year_rows_spread(spread_df)

    table = pd.DataFrame(rows_kwh + rows_grid + rows_spread)
    table.to_csv(os.path.join(T77_DIR, "fig06_comparison_table.csv"), index=False)
    log(f"wrote fig06_comparison_table.csv ({len(table)} rows)")

    # -------------------------------------------------------------------------------------
    # Figure 6: stock-weighted, 2022 vs 2030, full model vs avg-profile arm
    # -------------------------------------------------------------------------------------
    log("building figure 6 ...")
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.5))
    colors = {"full": "#4C72B0", "avg": "#55A868"}
    years = (2022, 2030)
    x = np.arange(len(years))
    w = 0.35

    def bar_no_ci(ax, title, ylab, full_vals, avg_vals):
        ax.bar(x - w / 2, full_vals, width=w, label="Full model (T21)", color=colors["full"], hatch="///", edgecolor="grey")
        ax.bar(x + w / 2, avg_vals, width=w, label="Average-profile arm (T30)", color=colors["avg"], hatch="///", edgecolor="grey")
        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in years])
        ax.set_ylabel(ylab)
        ax.set_title(title + "\n(no CI available)", fontsize=8)

    def bar_with_ci(ax, title, ylab, full_vals, avg_vals, cis):
        ax.bar(x - w / 2, full_vals, width=w, label="Full model (T21)", color=colors["full"])
        ax.bar(x + w / 2, avg_vals, width=w, label="Average-profile arm (T30)", color=colors["avg"])
        for i, ci in enumerate(cis):
            if ci is None:
                continue
            point, lo, hi, n = ci
            yerr_lo = max(point - lo, 0)
            yerr_hi = max(hi - point, 0)
            ax.errorbar([x[i] + w / 2], [avg_vals[i]], yerr=[[yerr_lo], [yerr_hi]],
                        fmt="none", ecolor="black", capsize=4)
        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in years])
        ax.set_ylabel(ylab)
        ax.set_title(title + "\n(95% CI on avg-arm delta, paired)", fontsize=8)

    # Panel A: annual electricity (facility total), stock-weighted whole-building kWh
    fvals, avals = [], []
    for year in years:
        fvals.append(stock_weighted_point(full_ann[full_ann["year"] == year], "elec_facility_kWh"))
        avals.append(stock_weighted_point(avg_ann[avg_ann["year"] == year], "elec_facility_kWh"))
    bar_no_ci(axes[0, 0], "Annual electricity\n(Electricity:Facility)", "Stock-weighted\nwhole-building kWh/yr", fvals, avals)

    # Panel B: peak demand
    fvals, avals = [], []
    for year in years:
        fvals.append(stock_weighted_point(full_grid[full_grid["year"] == year], "peak_kW_annual"))
        avals.append(stock_weighted_point(avg_grid[avg_grid["year"] == year], "peak_kW_annual"))
    bar_no_ci(axes[0, 1], "Peak demand", "Stock-weighted\npeak (kW)", fvals, avals)

    # Panel C: load factor, with CI
    fvals, avals, cis = [], [], []
    for year in years:
        fg, ag = full_grid[full_grid["year"] == year], avg_grid[avg_grid["year"] == year]
        fvals.append(stock_weighted_point(fg, "load_factor"))
        avals.append(stock_weighted_point(ag, "load_factor"))
        cis.append(stock_weighted_paired_ci(fg, ag, "load_factor"))
    bar_with_ci(axes[0, 2], "Load factor", "Stock-weighted\nload factor (fraction)", fvals, avals, cis)

    # Panel D: midday share, with CI
    fvals, avals, cis = [], [], []
    for year in years:
        fg, ag = full_grid[full_grid["year"] == year], avg_grid[avg_grid["year"] == year]
        fvals.append(stock_weighted_point(fg, "midday_share"))
        avals.append(stock_weighted_point(ag, "midday_share"))
        cis.append(stock_weighted_paired_ci(fg, ag, "midday_share"))
    bar_with_ci(axes[1, 0], "Midday share\n(9h-17h of annual facility kWh)", "Stock-weighted\nmidday share (fraction)", fvals, avals, cis)

    # Panel E: evening ramp
    fvals, avals = [], []
    for year in years:
        fvals.append(stock_weighted_point(full_grid[full_grid["year"] == year], "evening_ramp_kW_mean"))
        avals.append(stock_weighted_point(avg_grid[avg_grid["year"] == year], "evening_ramp_kW_mean"))
    bar_no_ci(axes[1, 1], "Evening ramp\n(14h->17h mean)", "Stock-weighted\nramp (kW)", fvals, avals)

    # Panel F: household peak-hour spread (circular SD, stock-weighted mean across cells)
    fvals, avals = [], []
    for year in years:
        f_sub = spread_df[(spread_df["arm"] == "full_model_T21") & (spread_df["year"] == year)]
        a_sub = spread_df[(spread_df["arm"] == "avg_profile_T30") & (spread_df["year"] == year)]
        fvals.append(stock_weighted_point(f_sub, "circular_sd_hours"))
        avals.append(stock_weighted_point(a_sub, "circular_sd_hours"))
    bar_no_ci(axes[1, 2], "Household peak-hour spread\n(Mardia circular SD)", "Stock-weighted\nspread (hours)", fvals, avals)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(
        "Figure 6. Full model vs. average-profile arm, stock-weighted, 2022 and 2030\n"
        "Static arm (T19/T22) EXCLUDED -- ruled not home-for-home (checklist item c8); "
        "not computed, not plotted.",
        fontsize=10)
    fig.tight_layout(rect=[0, 0.03, 1, 0.94])
    save_fig(fig, "figure_06_full_vs_avgarm")

    RUN_META["elapsed_sec"] = time.time() - t0
    RUN_META["comparison_table_rows"] = len(table)
    RUN_META["comparison_table_path"] = os.path.join(T77_DIR, "fig06_comparison_table.csv")
    RUN_META["household_peak_spread_path"] = os.path.join(T77_DIR, "household_peak_spread_both_arms.csv")
    RUN_META["static_arm_excluded_note"] = (
        "Static arm (T19/T22) intentionally NOT computed and NOT plotted -- CLOSED as not "
        "home-for-home, checklist item c8. Stated in the figure's own suptitle above.")
    with open(os.path.join(T77_DIR, "run_meta_part2.json"), "w") as f:
        json.dump(RUN_META, f, indent=2, default=str)

    # ---------------------------------------------------------------------------------------
    # T77/logs/t77_report.txt -- controls first, then table, then figure path, then VERDICT.
    # ---------------------------------------------------------------------------------------
    ctrl_path = os.path.join(T77_DIR, "controls.json")
    part1_meta_path = os.path.join(T77_DIR, "run_meta.json")
    controls_part1 = {}
    meta_part1 = {}
    try:
        with open(ctrl_path) as f:
            controls_part1 = json.load(f)
    except Exception as e:
        controls_part1 = {"ERROR_READING": str(e)}
    try:
        with open(part1_meta_path) as f:
            meta_part1 = json.load(f)
    except Exception as e:
        meta_part1 = {"ERROR_READING": str(e)}

    controls_all_fired_part1 = bool(controls_part1.get("all_fired", False))
    row_counts_ok = bool(RUN_META["controls"]["C_row_counts_as_expected"])
    n_not_evaluable = int((table["quotable"] == "NOT_EVALUABLE").sum())
    n_quotable = int((table["quotable"] == "QUOTABLE").sum())

    verdict = "PASS" if (controls_all_fired_part1 and row_counts_ok) else "FAIL"

    lines = []
    lines.append("T77 -- WP11 Figure 6 (full model vs. average-profile arm) -- report")
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append("")
    lines.append("=== CONTROLS (part 1, T30-side metric computation: t77_grid_metrics_avgarm.py) ===")
    lines.append(f"controls_all_fired (part 1): {controls_all_fired_part1}")
    for k, v in (meta_part1.get("controls_summary") or {}).items():
        lines.append(f"  {k}: {v}")
    lines.append("  C2 hand-verified pairs detail:")
    c2 = controls_part1.get("C2_hand_verified_pairs", {})
    for pr in c2.get("pairs", []):
        lines.append(f"    {pr}")
    lines.append("")
    lines.append("=== SEEN-WORKING CONTROL (t77_control_copy.py, run separately against T21/out/step8) ===")
    lines.append("See T77/controls_out/controls.json and run_meta.json for this job's own C1-C4 "
                 "outcomes (byte-identical copy of T68's accepted script, only OUT_DIR changed). "
                 "Expected: identical to T68/out/run_meta.json's controls_all_fired=true and "
                 "hand-check numbers (HAND_CHECK_ANNUAL_KWH=8209.333463, HAND_CHECK_PEAK_KW=4.318054).")
    lines.append("")
    lines.append("=== INPUT ROW COUNTS (part 2) ===")
    lines.append(json.dumps(RUN_META["controls"]["C_input_row_counts"], indent=2))
    lines.append(f"row_counts_as_expected (2400 each): {row_counts_ok}")
    lines.append("")
    lines.append("=== COMPARISON TABLE ===")
    lines.append(f"fig06_comparison_table.csv: {len(table)} rows "
                 f"({n_quotable} QUOTABLE, {n_not_evaluable} NOT_EVALUABLE)")
    lines.append(f"Path: {os.path.join(T77_DIR, 'fig06_comparison_table.csv')}")
    lines.append(f"household_peak_spread_both_arms.csv: {len(spread_df)} rows, path: "
                 f"{os.path.join(T77_DIR, 'household_peak_spread_both_arms.csv')}")
    lines.append("")
    lines.append("=== FIGURE ===")
    lines.append(f"Path: {RUN_META['figure'].get('png_path')}")
    lines.append("Static arm (T19/T22) EXCLUDED -- ruled not home-for-home, checklist item c8. "
                 "Not computed, not plotted, stated in the figure's own suptitle.")
    lines.append("")
    lines.append(f"VERDICT: {verdict}")
    lines.append(f"  controls_all_fired (part 1) = {controls_all_fired_part1}")
    lines.append(f"  row_counts_as_expected (part 2 inputs) = {row_counts_ok}")
    lines.append("  NOTE: 'VERDICT: PASS' here means the CONTROLS fired and inputs matched expected "
                 "row counts -- it does NOT itself certify every comparison-table row as QUOTABLE; "
                 "read the table's own per-row quotable/quotable_reason columns before citing any "
                 "single number in the manuscript.")

    report_path = os.path.join(LOG_DIR, "t77_report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    log(f"wrote {report_path}, VERDICT={verdict}")
    log(f"done in {RUN_META['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
