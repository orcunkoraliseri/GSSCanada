#!/usr/bin/env python3
"""
T09 -- WP5 step 3: simulated Toronto 2022 vs measured IESO profiles (T02).
Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/
          2026-09-15_T09_wp5_sim_vs_measured_toronto.md

Numbers only. No pass/fail bands, no interpretation beyond stating mismatches.

------------------------------------------------------------------------------
RUN SELECTION -- restricted to Toronto_5A, year=2022, the "new_2022_2030 wins"
gate ported verbatim from Step8_docs/08_simulation_plots.py:154-234
(load_cell_manifest + discover_runs), the same logic already reused read-only
in T06_scripts/enduse_hour_2022_v2.py:146-210 (discover_2022_runs) -- T06's
input tree is read here too (INPUT_ROOT below), nothing under T06/ is written.

METRICS -- compute_slice_outputs() and circular_mean_hour_idx() below are
copied UNCHANGED from T02_scripts/ieso_wp5_build_v2.py:271-338, so simulated
and measured use exactly one metric definition. Do not edit these two
functions; if a bug is found, fix it in T02's script first and re-port.

CLOCK / CALENDAR MAPPING -- established locally (grep, not on the cluster)
from BEM_Setup/SimResults_Step8/campaign_N50/SingleD__Toronto_5A/
sample_001_HH33188/2022/Scenario_2022.idf, RunPeriod object, lines 115-129:
    Day of Week for Start Day = Sunday
    Use Weather File Holidays and Special Days = Yes
    Use Weather File Daylight Saving Period = Yes
Real 2022-01-01 = Saturday (python datetime.date(2022,1,1).weekday(), checked
locally), NOT Sunday -- EnergyPlus's internal simulated weekday sequence for
this RunPeriod does not line up with the real 2022 civil calendar.
Row `hour` (0..8759) -> day_idx = hour // 24 (0..364), hour_of_day = hour % 24
(0..23). Calendar date = 2022-01-01 + day_idx days: day_idx is used purely as
a day-of-year OFFSET, so the resulting dates are the real 2022 calendar dates
regardless of which weekday EnergyPlus itself thinks day 1 is. IESO HOUR
(hour-ending, 1-24, EST, no DST) = hour_of_day + 1 -- the same array-index
convention already established and verified in T02_scripts/ieso_wp5_build_v2.py
module docstring (lines 10-14) and reused unchanged inside
compute_slice_outputs() below.

Two day-type calendars are built and reported separately (task step 3):
  - "real2022": weekday/weekend from the actual 2022 civil calendar
    (python date.weekday() < 5); holiday from T02's HOLIDAY_SET (T02_scripts/
    ieso_wp5_build_v2.py:87-99, 2022 subset copied verbatim below). This is
    the SAME calendar T02 used for the measured IESO side, so period x
    daytype slices line up exactly -- this is the calendar used for the
    sim-vs-measured join file.
  - "eplus": weekday/weekend from EnergyPlus's own simulated day-of-week,
    i.e. the "Jan 1 = Sunday" convention already coded as is_weekend() in
    Step8_docs/08_simulation_plots.py:128-131 (ported verbatim below as
    is_weekend_eplus, doy = day_idx + 1) -- the calendar the occupancy
    schedule (and hence the simulated load) actually ran against.
    DECISION (not specified by the task doc): holiday membership is NOT
    recomputed for this calendar -- a holiday is the same calendar date
    either way; only the weekday/weekend split changes.
DST mismatch (task step 7, stated not fixed): RunPeriod uses "Use Weather
File Daylight Saving Period = Yes", so EnergyPlus's own hour labelling may
follow the EPW's DST period; IESO's HOUR field is fixed EST, no DST, all
year. No shift is applied for this here.

SERIES (task step 4):
  (a) "facility" = Electricity:Facility (all electricity, incl. electric
      heating/cooling/water heating).
  (b) "nonhvac"  = InteriorLights:Electricity + InteriorEquipment:Electricity
      + Fan Electricity Energy (non-HVAC subset).
  Units: hourly_meters.csv is joules per hour (confirmed locally on a
  Toronto SingleD sample; same header T06 already verified for the full
  set). kWh = J / 3,600,000.

ARCHETYPE MIX: STOCK_WEIGHTS copied verbatim from
Step8_docs/08_simulation_plots.py:74-77 (Toronto only, no six-city split,
per task step 4). "StockWeighted" combines the 4 archetypes' per-run series
with weight = STOCK_WEIGHTS[arch] / n_runs_of_arch applied to BOTH the
TOTAL_CONSUMPTION and PREMISE_COUNT columns fed into compute_slice_outputs
(so PREMISE_COUNT sums to 1.0 across the combined table when every archetype
has full 8760-hour coverage) -- this reproduces a weight-average of the
per-archetype per-dwelling kWh, algebraically, without changing
compute_slice_outputs itself. DECISION: "mean_premises" in the StockWeighted
output rows is therefore a WEIGHT SUM (~1.0), not a real premise count --
flagged, not fixed.
"""
import os
import re
import glob
import json
import time
import datetime as dt

import numpy as np
import pandas as pd

INPUT_ROOT = "/speed-scratch/o_iseri/2J_revision/T06/input"   # T06's output -- READ ONLY
T02_METRICS_PATH = "/speed-scratch/o_iseri/2J_revision/T02/out/ieso_metrics.csv"  # READ ONLY
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T09/out"

CITY = "Toronto_5A"
ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]

# ---- Step8_docs/08_simulation_plots.py:74-77, verbatim ----
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

FACILITY = "Electricity:Facility"
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP = "InteriorEquipment:Electricity"
M_FAN = "Fan Electricity Energy"
SERIES_COLS = {"facility": "kwh_facility", "nonhvac": "kwh_nonhvac"}

# ---- T02_scripts/ieso_wp5_build_v2.py:87-99, 2022 subset only, verbatim ----
HOLIDAYS_2022 = ["2022-01-01", "2022-02-21", "2022-04-15", "2022-05-23", "2022-07-01",
                 "2022-09-05", "2022-10-10", "2022-12-25", "2022-12-26"]
HOLIDAY_SET = set(HOLIDAYS_2022)

# ---- T02_scripts/ieso_wp5_build_v2.py:106-110, verbatim ----
PERIOD_MONTHS = {"winter": {12, 1, 2}, "shoulder": {4, 5, 9, 10}, "summer": {6, 7, 8}}
MIDDAY_HOURS_1TO24 = {10, 11, 12, 13, 14, 15, 16, 17}  # ieso_wp5_build_v2.py:112


# ---- Step8_docs/08_simulation_plots.py:128-131, verbatim ----
def is_weekend_eplus(doy):
    """Jan 1 = Sunday (EnergyPlus default in this pipeline). Verbatim from reporting.py:302-310."""
    wd = (doy - 1) % 7
    return wd == 0 or wd == 6


# ---- T02_scripts/ieso_wp5_build_v2.py:271-278, UNCHANGED ----
def circular_mean_hour_idx(hour_idx_array):
    """hour_idx_array: 0-23 values. Returns circular mean (0-23, wraps at 24)."""
    if len(hour_idx_array) == 0:
        return np.nan
    ang = 2 * np.pi * np.asarray(hour_idx_array, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    return float((np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0)


# ---- T02_scripts/ieso_wp5_build_v2.py:280-337, UNCHANGED ----
def compute_slice_outputs(scope, year, period, daytype, sub):
    """sub: rows already filtered to this scope/year/period/daytype, columns DATE, HOUR,
    TOTAL_CONSUMPTION, PREMISE_COUNT. Returns (profile_rows, metric_row)."""
    if sub.empty:
        return [], None

    per_dh = sub.groupby(["DATE", "HOUR"], observed=True).agg(
        tot_cons=("TOTAL_CONSUMPTION", "sum"),
        tot_prem=("PREMISE_COUNT", "sum"),
    ).reset_index()
    per_dh = per_dh[per_dh["tot_prem"] > 0]
    if per_dh.empty:
        return [], None
    per_dh["kwh_per_premise"] = per_dh["tot_cons"] / per_dh["tot_prem"]

    n_days = per_dh["DATE"].nunique()
    mean_premises = float(per_dh.groupby("DATE")["tot_prem"].sum().mean())

    prof = per_dh.groupby("HOUR")["kwh_per_premise"].mean().reindex(range(1, 25))
    prof_sum = prof.sum()
    share = prof / prof_sum if prof_sum else prof * np.nan

    profile_rows = []
    for h in range(1, 25):
        profile_rows.append({
            "scope": scope, "year": year, "period": period, "daytype": daytype,
            "hour_ending": h,
            "kwh_per_premise": float(prof.loc[h]) if pd.notna(prof.loc[h]) else np.nan,
            "share": float(share.loc[h]) if pd.notna(share.loc[h]) else np.nan,
            "n_days": int(n_days), "mean_premises": mean_premises,
        })

    vals = per_dh["kwh_per_premise"].to_numpy()
    mean_all = float(vals.mean())
    max_all = float(vals.max())
    load_factor = mean_all / max_all if max_all else np.nan
    peak_to_avg = max_all / mean_all if mean_all else np.nan
    midday_mask = per_dh["HOUR"].isin(MIDDAY_HOURS_1TO24)
    midday_sum = float(per_dh.loc[midday_mask, "kwh_per_premise"].sum())
    total_sum = float(per_dh["kwh_per_premise"].sum())
    midday_share = midday_sum / total_sum if total_sum else np.nan

    daily_peak_hour_idx = per_dh.loc[per_dh.groupby("DATE")["kwh_per_premise"].idxmax(), ["DATE", "HOUR"]]
    hour_idx0 = (daily_peak_hour_idx["HOUR"].to_numpy() - 1)
    mean_peak_hour = circular_mean_hour_idx(hour_idx0)

    metric_row = {
        "scope": scope, "year": year, "period": period, "daytype": daytype,
        "n_days": int(n_days), "mean_premises": mean_premises,
        "mean_kwh_per_premise": mean_all, "max_kwh_per_premise": max_all,
        "load_factor": load_factor, "peak_to_avg": peak_to_avg,
        "midday_share": midday_share, "mean_peak_hour": mean_peak_hour,
    }
    return profile_rows, metric_row


# ---- Step8_docs/08_simulation_plots.py:154-186, verbatim (manifest merge) ----
_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)


def load_cell_manifest(cell_dir):
    out = {}
    path = os.path.join(cell_dir, "cell_manifest.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str)
            for _, r in df.iterrows():
                out[(int(r["sample"]), str(r.get("sim_hh_id", "")))] = {
                    "hhsize": r.get("hhsize", ""), "dtype": r.get("dtype", ""),
                    "pr": r.get("pr", ""), "source": "orig",
                }
        except Exception:
            pass
    for new_path in sorted(glob.glob(os.path.join(cell_dir, "cell_manifest.csv.new_2022_2030_*"))):
        try:
            df = pd.read_csv(new_path, dtype=str)
            for _, r in df.iterrows():
                out[(int(r["sample"]), str(r.get("sim_hh_id", "")))] = {
                    "hhsize": r.get("hhsize", ""), "dtype": r.get("dtype", ""),
                    "pr": r.get("pr", ""), "source": "new_2022_2030",
                }
        except Exception:
            pass
    return out


def discover_toronto_2022_runs(results_dir):
    """Restricted to CITY / year=2022, same 'new_2022_2030 wins' gate as
    Step8_docs/08_simulation_plots.py:189-234 (discover_runs) -- read-only reference pattern
    already used in T06_scripts/enduse_hour_2022_v2.py:175-210 (discover_2022_runs)."""
    runs = []
    for arch in ARCH_NAMES:
        cell_name = f"{arch}__{CITY}"
        cell_dir = os.path.join(results_dir, cell_name)
        if not os.path.isdir(cell_dir):
            continue
        manifest = load_cell_manifest(cell_dir)
        for samp_name in sorted(os.listdir(cell_dir)):
            m = _RUN_RE.match(samp_name)
            if not m:
                continue
            samp_dir = os.path.join(cell_dir, samp_name)
            if not os.path.isdir(samp_dir):
                continue
            sample_from_dir = int(m.group(1))
            hh_from_dir = m.group(2)
            meta = manifest.get((sample_from_dir, str(hh_from_dir)), {})
            is_new_sample = meta.get("source") == "new_2022_2030"
            if not is_new_sample:
                continue
            ydir = os.path.join(samp_dir, "2022")
            csvp = os.path.join(ydir, "hourly_meters.csv")
            if not os.path.exists(csvp):
                continue
            runs.append({"arch": arch, "sample": sample_from_dir,
                         "sim_hh_id": str(hh_from_dir), "csv_path": csvp})
    return runs


# ---- clock/calendar mapping (see module docstring) ----
_BASE_DATE = dt.date(2022, 1, 1)


def build_calendar_frame():
    """One row per hour 0..8759: DATE, HOUR (1-24), month, daytype_real2022, daytype_eplus.
    Identical for every run (the mapping does not depend on the household), computed once."""
    hours = np.arange(8760)
    day_idx = hours // 24
    hod = hours % 24
    dates = np.array([(_BASE_DATE + dt.timedelta(days=int(d))).isoformat() for d in day_idx])
    hourend = (hod + 1).astype(int)
    months = np.array([int(d_str[5:7]) for d_str in dates])
    doy = day_idx + 1  # 1-based day-of-year, same offset basis as the dates above

    is_holiday = np.isin(dates, list(HOLIDAY_SET))
    dow_real = pd.to_datetime(dates).dayofweek.to_numpy()  # 0=Mon..6=Sun
    weekend_real = dow_real >= 5
    daytype_real = np.where(is_holiday, "holiday", np.where(weekend_real, "weekend", "weekday"))

    weekend_eplus = np.array([is_weekend_eplus(int(d)) for d in doy])
    daytype_eplus = np.where(is_holiday, "holiday", np.where(weekend_eplus, "weekend", "weekday"))

    return pd.DataFrame({"DATE": dates, "HOUR": hourend, "month": months,
                          "daytype_real2022": daytype_real, "daytype_eplus": daytype_eplus})


def period_month_map():
    periods = {"full_year": set(range(1, 13))}
    for m in range(1, 13):
        periods[f"month_{m:02d}"] = {m}
    for pname, months in PERIOD_MONTHS.items():
        periods[pname] = months
    return periods


def full_sub_table(frame_weight_list, value_col, daytype_col):
    """Concatenate every (per-run frame, weight) pair into one table with columns
    DATE, HOUR, month, TOTAL_CONSUMPTION (= value*weight), PREMISE_COUNT (= weight),
    daytype -- ready to be month/daytype-filtered and fed to compute_slice_outputs."""
    parts = []
    for f, w in frame_weight_list:
        parts.append(pd.DataFrame({
            "DATE": f["DATE"].to_numpy(), "HOUR": f["HOUR"].to_numpy(),
            "month": f["month"].to_numpy(),
            "TOTAL_CONSUMPTION": f[value_col].to_numpy() * w,
            "PREMISE_COUNT": np.full(len(f), w, dtype=float),
            "daytype": f[daytype_col].to_numpy(),
        }))
    if not parts:
        return pd.DataFrame(columns=["DATE", "HOUR", "month", "TOTAL_CONSUMPTION",
                                      "PREMISE_COUNT", "daytype"])
    return pd.concat(parts, ignore_index=True)


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"[T09] discovering Toronto 2022 runs under {INPUT_ROOT} ...", flush=True)
    runs = discover_toronto_2022_runs(INPUT_ROOT)
    n_by_arch = {a: sum(1 for r in runs if r["arch"] == a) for a in ARCH_NAMES}
    print(f"[T09] n runs per archetype: {n_by_arch} (total {len(runs)}, expect 50 each)", flush=True)

    calendar = build_calendar_frame()

    per_arch_frames = {a: [] for a in ARCH_NAMES}
    skipped = []
    for r in runs:
        try:
            df = pd.read_csv(r["csv_path"])
        except Exception as e:
            skipped.append({**r, "reason": f"read_error: {e}"})
            continue
        if len(df) < 8760:
            skipped.append({**r, "reason": f"short: n_hours={len(df)}"})
            continue
        missing = [c for c in (FACILITY, M_LIGHTS, M_EQUIP, M_FAN) if c not in df.columns]
        if missing:
            skipped.append({**r, "reason": f"missing_columns: {missing}"})
            continue
        kwh_fac = pd.to_numeric(df[FACILITY], errors="coerce").to_numpy()[:8760] / 3.6e6
        kwh_nonhvac = (pd.to_numeric(df[M_LIGHTS], errors="coerce").to_numpy()[:8760]
                       + pd.to_numeric(df[M_EQUIP], errors="coerce").to_numpy()[:8760]
                       + pd.to_numeric(df[M_FAN], errors="coerce").to_numpy()[:8760]) / 3.6e6
        run_df = calendar.copy()
        run_df["kwh_facility"] = kwh_fac
        run_df["kwh_nonhvac"] = kwh_nonhvac
        per_arch_frames[r["arch"]].append(run_df)

    n_loaded = sum(len(v) for v in per_arch_frames.values())
    print(f"[T09] loaded {n_loaded} runs ok, {len(skipped)} skipped", flush=True)

    entities = {}
    for a in ARCH_NAMES:
        entities[a] = [(f, 1.0) for f in per_arch_frames[a]]
    stock_list = []
    for a in ARCH_NAMES:
        n = len(per_arch_frames[a])
        if n == 0:
            continue
        w = STOCK_WEIGHTS[a] / n
        stock_list.extend([(f, w) for f in per_arch_frames[a]])
    entities["StockWeighted"] = stock_list

    periods = period_month_map()
    all_metric_rows = []
    all_profile_rows = []

    for entity, frame_weight_list in entities.items():
        for series, value_col in SERIES_COLS.items():
            for calendar_name, daytype_col in (("real2022", "daytype_real2022"),
                                                ("eplus", "daytype_eplus")):
                full_tbl = full_sub_table(frame_weight_list, value_col, daytype_col)
                for period_name, months in periods.items():
                    period_tbl = full_tbl[full_tbl["month"].isin(months)]
                    if period_tbl.empty:
                        continue
                    for daytype in ("weekday", "weekend", "holiday"):
                        sub = period_tbl[period_tbl["daytype"] == daytype][
                            ["DATE", "HOUR", "TOTAL_CONSUMPTION", "PREMISE_COUNT"]]
                        profile_rows, metric_row = compute_slice_outputs(
                            "Toronto", 2022, period_name, daytype, sub)
                        if metric_row is not None:
                            metric_row.update({"series": series, "archetype": entity,
                                                "calendar": calendar_name})
                            all_metric_rows.append(metric_row)
                        for pr in profile_rows:
                            pr.update({"series": series, "archetype": entity,
                                       "calendar": calendar_name})
                        all_profile_rows.extend(profile_rows)
        print(f"[T09] entity {entity} done, t={time.time()-t0:.0f}s", flush=True)

    metrics_df = pd.DataFrame(all_metric_rows)
    metrics_path = os.path.join(OUT_DIR, "sim_toronto_2022_metrics.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"[out] wrote {metrics_path} ({len(metrics_df)} rows)", flush=True)

    profiles_df = pd.DataFrame(all_profile_rows)
    profiles_path = os.path.join(OUT_DIR, "sim_toronto_2022_profiles_long.csv")
    profiles_df.to_csv(profiles_path, index=False)
    print(f"[out] wrote {profiles_path} ({len(profiles_df)} rows)", flush=True)

    # ---- sim_vs_measured_toronto_2022.csv ----
    # Join on period x daytype for the WEIGHTED STOCK entity, calendar="real2022" (the same
    # calendar T02 used for the measured side, so period/daytype slices line up exactly),
    # series (a) and (b), against measured Toronto 2022 and Ontario 2022 from T02's own
    # ieso_metrics.csv (read-only, /speed-scratch/o_iseri/2J_revision/T02/out/). DECISION: only
    # the 6 substantive metric columns are compared (mean_kwh_per_premise, max_kwh_per_premise,
    # load_factor, peak_to_avg, midday_share, mean_peak_hour) -- n_days and mean_premises are
    # NOT compared as "metrics" here (mean_premises means different things on each side: real
    # premise counts for measured, a stock-weight sum close to 1.0 for simulated -- see module
    # docstring). "Shoulder months first" -> period sort order below puts period=="shoulder"
    # first.
    metric_cols = ["mean_kwh_per_premise", "max_kwh_per_premise", "load_factor",
                   "peak_to_avg", "midday_share", "mean_peak_hour"]

    sim_stock = metrics_df[(metrics_df["archetype"] == "StockWeighted")
                            & (metrics_df["calendar"] == "real2022")].copy()

    measured = pd.read_csv(T02_METRICS_PATH)
    measured = measured[measured["year"].astype(str) == "2022"].copy()

    join_rows = []
    period_order = (["shoulder", "winter", "summer", "full_year"]
                     + [f"month_{m:02d}" for m in range(1, 13)])
    daytype_order = ["weekday", "weekend", "holiday"]

    for series in SERIES_COLS:
        sim_series = sim_stock[sim_stock["series"] == series]
        for period in period_order:
            for daytype in daytype_order:
                sim_row = sim_series[(sim_series["period"] == period)
                                      & (sim_series["daytype"] == daytype)]
                if sim_row.empty:
                    continue
                sim_row = sim_row.iloc[0]
                for measured_scope in ("Toronto", "Ontario"):
                    meas_row = measured[(measured["scope"] == measured_scope)
                                         & (measured["period"] == period)
                                         & (measured["daytype"] == daytype)]
                    if meas_row.empty:
                        continue
                    meas_row = meas_row.iloc[0]
                    for metric in metric_cols:
                        sim_v = float(sim_row[metric]) if pd.notna(sim_row[metric]) else np.nan
                        meas_v = float(meas_row[metric]) if pd.notna(meas_row[metric]) else np.nan
                        join_rows.append({
                            "period": period, "daytype": daytype, "series": series,
                            "measured_scope": measured_scope, "metric": metric,
                            "sim": sim_v, "measured": meas_v,
                            "sim_minus_measured": (sim_v - meas_v)
                                if (pd.notna(sim_v) and pd.notna(meas_v)) else np.nan,
                        })

    join_df = pd.DataFrame(join_rows)
    join_path = os.path.join(OUT_DIR, "sim_vs_measured_toronto_2022.csv")
    join_df.to_csv(join_path, index=False)
    print(f"[out] wrote {join_path} ({len(join_df)} rows)", flush=True)

    meta = {
        "job_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "elapsed_sec": time.time() - t0,
        "input_root": INPUT_ROOT,
        "n_runs_per_archetype": n_by_arch,
        "n_runs_loaded_ok": n_loaded,
        "n_runs_skipped": len(skipped),
        "skipped": skipped,
        "row_counts": {
            "sim_toronto_2022_metrics.csv": len(metrics_df),
            "sim_toronto_2022_profiles_long.csv": len(profiles_df),
            "sim_vs_measured_toronto_2022.csv": len(join_df),
        },
    }
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print(f"[T09] done in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
