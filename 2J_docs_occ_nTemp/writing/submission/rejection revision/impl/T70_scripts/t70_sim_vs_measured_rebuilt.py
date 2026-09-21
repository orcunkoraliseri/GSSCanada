#!/usr/bin/env python3
"""
T70 -- WP5: redo the measured-vs-simulated 2022 profile comparison on the REBUILT runs.
Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/
          2026-09-21_T70_wp5_measured_vs_rebuilt.md
Parent:   2026-09-15_T15_wp5_sim_vs_measured_fix.md (script this is copied from:
          T15_scripts/t15_sim_vs_measured.py -- copied verbatim, see WHAT CHANGED below)

Numbers only. No pass/fail bands, no interpretation.

------------------------------------------------------------------------------
WHAT CHANGED FROM T15 (discovery + input tree only; everything else copied
verbatim -- compute_slice_outputs, circular_mean_hour_idx, build_calendar_frame,
period_month_map, full_sub_table, STOCK_WEIGHTS, HOLIDAYS_2022, DWELLING_COUNT,
the normalization step, and the eplus/real2022 two-calendar join loop are all
byte-identical to T15):

1. INPUT TREE. INPUT_ROOT repointed from the OLD retired T06/input tree to the
   REBUILT T21/out/step8 tree (T21 = "2022-diaries-only" rebuild). This is the
   whole point of this task -- T15's numbers are stale now that the rebuild
   exists (task doc section 0).

2. DISCOVERY / MANIFEST GATE. T15's discover_toronto_2022_runs() required
   `meta.get("source") == "new_2022_2030"` from an OVERLAY manifest file
   (`cell_manifest.csv.new_2022_2030_*`) that existed only in the OLD tree to
   pick between an original and a replacement run. The T21 rebuilt tree has
   ONLY a plain `cell_manifest.csv` (columns sample,sim_hh_id,hhsize,dtype,pr)
   and NO overlay file anywhere under T21/out/step8 -- reinstating the
   is_new_sample gate here would silently zero every single run (nothing in
   this tree has `source == "new_2022_2030"`, because the concept of "new
   vs old" replacement samples does not exist post-rebuild; T21 IS the single
   authoritative build). Fix: discovery reads the plain manifest only, no
   overlay merge, no is_new_sample gate -- this is the IDENTICAL adaptation
   T68 (`T68_scripts/enduse_hour_corrected.py:204-219,222-258`) already made
   for reading this exact same T21 tree, confirmed correct there
   (`T68_out`/collector notes, 2,400/2,400 household-years read ok). Restricted
   here to Toronto_5A / year=2022 only (T70's Toronto-only scope, task Ruling 1),
   whereas T68's version covers all 6 cities and both years -- narrower re-use
   of the same pattern, not a new invention.

3. NEW CONTROL C5 (rebuild-vs-old sanity bound). Before trusting the real
   result, the raw (non-normalized) whole-building annual Facility kWh mean per
   archetype (already computed by T15's own "item 3" logic, unchanged here) is
   compared against T15's OLD per-archetype meter means (hardcoded below from
   `impl/T15_out/run_meta.json`'s `annual_facility_kwh_meter_mean_per_archetype`,
   read once, not re-derived on the cluster -- old tree is retired and no
   longer readable). Guard only: ratio (new/old) must sit in [0.5, 2.0] for
   every archetype; this does NOT fail the job (task doc section 2, "report
   both sides' numbers plainly; do not fail the job on this, just flag").

4. OUTPUT NAMING / data_vintage COLUMN. Output filenames carry `_rebuilt`
   (`sim_toronto_2022_shape_metrics_rebuilt.csv`,
   `sim_vs_measured_toronto_2022_shape_rebuilt.csv`) per the task doc's
   Deliverables section, and the join file gets an extra
   `data_vintage="rebuilt_2022"` column so it is never confused with T15's old
   file if both are ever read side by side (task doc explicit instruction).

5. DWELLING COUNTS UNCHANGED (task doc Ruling 2). DWELLING_COUNT /
   DWELLING_COUNT_EVIDENCE are copied byte-identical from T15 -- the rebuild
   changes occupancy schedules (2022-diaries only), not building geometry / IDF
   zone structure, so the IDF-derived dwelling-unit counts from T15 (grepped
   from Scenario_2022.idf zone objects) still apply to the rebuilt runs, which
   share the same Toronto_5A archetype IDF templates. Stated explicitly here
   per the task doc's instruction not to silently assume this.

METRICS -- compute_slice_outputs() and circular_mean_hour_idx() below are
copied UNCHANGED from T15_scripts/t15_sim_vs_measured.py (itself copied
unchanged from T02_scripts/ieso_wp5_build_v2.py:271-338; do not edit).

RUN SELECTION -- Toronto/2022 only (task Ruling 1); T21 plain-manifest
discovery pattern reused from T68 (see item 2 above), not T15's overlay-gated
pattern (which would zero every run on this tree).

SERIES -- unchanged from T15/T09: (a) "facility" = Electricity:Facility,
(b) "nonhvac" = InteriorLights:Electricity + InteriorEquipment:Electricity +
Fan Electricity Energy. Units: hourly_meters.csv is J/hour; kWh = J / 3,600,000
(unchanged). Header of the rebuilt tree's hourly_meters.csv was confirmed
identical column names to what this script expects before writing this file
(see task doc's Ledger note in the IMPL doc) -- no column-name adaptation
needed.
"""
import os
import re
import glob
import json
import time
import datetime as dt

import numpy as np
import pandas as pd

INPUT_ROOT = "/speed-scratch/o_iseri/2J_revision/T21/out/step8"   # T21 rebuild -- READ ONLY
T02_METRICS_PATH = "/speed-scratch/o_iseri/2J_revision/T02/out/ieso_metrics.csv"  # READ ONLY
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T70/out"

CITY = "Toronto_5A"
ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]

# ---- Step8_docs/08_simulation_plots.py:74-77, verbatim (unchanged from T15/T09) ----
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

FACILITY = "Electricity:Facility"
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP = "InteriorEquipment:Electricity"
M_FAN = "Fan Electricity Energy"
SERIES_COLS = {"facility": "kwh_facility", "nonhvac": "kwh_nonhvac"}

# ---- T15 task step 3: explicit dwelling-unit counts (byte-identical to T15;
# task Ruling 2 -- geometry unchanged by the rebuild, only occupancy schedules
# changed). NOT re-derived here, NOT inferred from floor area. ----
DWELLING_COUNT = {
    "SingleD": 1,
    "OtherDwelling": 7,
    "MidRise": 31,   # 7 ground (SE corner absent) + 8*2 middle (ZoneGroup mult=2) + 8 top
    "HighRise": 79,  # 7 ground (SE corner absent) + 8*8 middle (ZoneGroup mult=8) + 8 top
}
DWELLING_COUNT_EVIDENCE = {
    "SingleD": ("SingleD__Toronto_5A/sample_001_HH33188/2022/Scenario_2022.idf:4392-4425 "
                "(one Zone living_unit1/attic_unit1/unheatedbsmt_unit1 triple, no ZoneGroup) "
                "[T15 evidence, geometry unchanged by rebuild per task Ruling 2]"),
    "OtherDwelling": ("OtherDwelling__Toronto_5A/sample_001_HH22934/2022/Scenario_2022.idf:4392-4613 "
                       "(seven Zone living_unitN/attic_unitN/unheatedbsmt_unitN triples, N=1..7, "
                       "no ZoneGroup multiplier -- a 7-unit row-house block, NOT a single dwelling) "
                       "[T15 evidence, geometry unchanged by rebuild per task Ruling 2]"),
    "MidRise": ("MidRise__Toronto_5A/sample_001_HH126139/2022/Scenario_2022.idf:5448-5511 "
                "(7 ground-floor Apartment zones, SE corner absent) + :5690-5705 (ZoneList "
                "'Mid Floor List', 8 Apartment zones + M Corridor; ZoneGroup Zone List "
                "Multiplier=2) + :5592-5655 (8 top-floor Apartment zones) = 7 + 8*2 + 8 = 31 "
                "[T15 evidence, geometry unchanged by rebuild per task Ruling 2]"),
    "HighRise": ("HighRise__Toronto_5A/sample_001_HH49514/2022/Scenario_2022.idf:5527-5632 "
                 "(7 ground-floor Apartment zones, SE corner absent) + :5931-5946 (ZoneList "
                 "'Mid Floor List', 8 Apartment zones + M Corridor; ZoneGroup Zone List "
                 "Multiplier=8) + :5797-5902 (8 top-floor Apartment zones) = 7 + 8*8 + 8 = 79; "
                 "same ZoneGroup lines/multiplier independently re-checked on "
                 "sample_002_HH129161, identical geometry "
                 "[T15 evidence, geometry unchanged by rebuild per task Ruling 2]"),
}

# ---- C5 sanity bound: T15's OLD per-archetype raw meter means, read ONCE from
# impl/T15_out/run_meta.json ("annual_facility_kwh_meter_mean_per_archetype"),
# hardcoded here since the old T06/input tree is retired and no longer
# readable on the cluster. Guard only, does not fail the job. ----
T15_OLD_ANNUAL_FACILITY_KWH_MEAN = {
    "SingleD": 8164.714032723402,
    "OtherDwelling": 47444.01943999619,
    "MidRise": 272595.0552057583,
    "HighRise": 393032.78629638226,
}

# ---- T02_scripts/ieso_wp5_build_v2.py:87-99, 2022 subset only, verbatim (unchanged) ----
HOLIDAYS_2022 = ["2022-01-01", "2022-02-21", "2022-04-15", "2022-05-23", "2022-07-01",
                 "2022-09-05", "2022-10-10", "2022-12-25", "2022-12-26"]
HOLIDAY_SET = set(HOLIDAYS_2022)

# ---- T02_scripts/ieso_wp5_build_v2.py:106-110, verbatim (unchanged) ----
PERIOD_MONTHS = {"winter": {12, 1, 2}, "shoulder": {4, 5, 9, 10}, "summer": {6, 7, 8}}
MIDDAY_HOURS_1TO24 = {10, 11, 12, 13, 14, 15, 16, 17}  # ieso_wp5_build_v2.py:112


# ---- Step8_docs/08_simulation_plots.py:128-131, verbatim (unchanged) ----
def is_weekend_eplus(doy):
    """Jan 1 = Sunday (EnergyPlus default in this pipeline). Verbatim from reporting.py:302-310."""
    wd = (doy - 1) % 7
    return wd == 0 or wd == 6


# ---- T02_scripts/ieso_wp5_build_v2.py:271-278, UNCHANGED (do not edit; fix upstream first) ----
def circular_mean_hour_idx(hour_idx_array):
    """hour_idx_array: 0-23 values. Returns circular mean (0-23, wraps at 24)."""
    if len(hour_idx_array) == 0:
        return np.nan
    ang = 2 * np.pi * np.asarray(hour_idx_array, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    return float((np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0)


# ---- T02_scripts/ieso_wp5_build_v2.py:280-337, UNCHANGED (do not edit; fix upstream first) ----
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


# ---- T21 plain-manifest discovery (item 2 above) -- adapted from
# T68_scripts/enduse_hour_corrected.py:204-219 load_cell_manifest, narrowed
# here to Toronto/2022 only, matching T15's discover_toronto_2022_runs()
# signature/behaviour otherwise. NO overlay merge, NO is_new_sample gate. ----
_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)


def load_cell_manifest(cell_dir):
    """T21 PLAIN manifest only, columns sample,sim_hh_id,hhsize,dtype,pr. No overlay file
    exists anywhere under T21/out/step8 -- reinstating T15's is_new_sample gate here would
    silently zero every run (see module docstring item 2)."""
    out = {}
    path = os.path.join(cell_dir, "cell_manifest.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str)
            for _, r in df.iterrows():
                out[(int(r["sample"]), str(r.get("sim_hh_id", "")))] = {
                    "hhsize": r.get("hhsize", ""), "dtype": r.get("dtype", ""),
                    "pr": r.get("pr", ""),
                }
        except Exception:
            pass
    return out


def discover_toronto_2022_runs(results_dir):
    """Restricted to CITY / year=2022 (task Ruling 1: Toronto only). T21 plain-manifest
    discovery -- see module docstring item 2 for why T15's is_new_sample gate is dropped."""
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
            _meta = manifest.get((sample_from_dir, str(hh_from_dir)), {})
            ydir = os.path.join(samp_dir, "2022")
            csvp = os.path.join(ydir, "hourly_meters.csv")
            if not os.path.exists(csvp):
                continue
            runs.append({"arch": arch, "sample": sample_from_dir,
                         "sim_hh_id": str(hh_from_dir), "csv_path": csvp})
    return runs


# ---- clock/calendar mapping, unchanged from T15/T09 (no hour shift) ----
_BASE_DATE = dt.date(2022, 1, 1)


def build_calendar_frame():
    """One row per hour 0..8759: DATE, HOUR (1-24), month, daytype_real2022, daytype_eplus.
    Identical for every run (the mapping does not depend on the household), computed once.
    Holiday membership is anchored to the REAL calendar date in BOTH daytype columns --
    only the weekday/weekend split differs between real2022 and eplus (unchanged from T15)."""
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
    daytype -- ready to be month/daytype-filtered and fed to compute_slice_outputs.
    Unchanged from T15; `value_col` holds each run's SCALE-FREE normalized series."""
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

    print(f"[T70] discovering Toronto 2022 runs under {INPUT_ROOT} (T21 rebuilt tree) ...", flush=True)
    runs = discover_toronto_2022_runs(INPUT_ROOT)
    n_by_arch = {a: sum(1 for r in runs if r["arch"] == a) for a in ARCH_NAMES}
    print(f"[T70] n runs per archetype: {n_by_arch} (total {len(runs)}, expect 50 each)", flush=True)

    calendar = build_calendar_frame()

    per_arch_frames = {a: [] for a in ARCH_NAMES}
    # item 3 (T15): raw (non-normalized) per-run annual sums, for the per-dwelling report
    # AND for the new C5 sanity bound.
    raw_annual_sum = {a: {"facility": [], "nonhvac": []} for a in ARCH_NAMES}
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

        # ---- scale-free normalization -- divide by this run's OWN annual mean
        # hourly value, per series, BEFORE anything else. Guard against a degenerate
        # (all-zero) series by skipping the run rather than dividing by zero.
        mean_fac = float(np.nanmean(kwh_fac))
        mean_nonhvac = float(np.nanmean(kwh_nonhvac))
        if not (mean_fac > 0) or not (mean_nonhvac > 0):
            skipped.append({**r, "reason": f"zero_or_nan_annual_mean: fac={mean_fac}, nonhvac={mean_nonhvac}"})
            continue

        raw_annual_sum[r["arch"]]["facility"].append(float(np.nansum(kwh_fac)))
        raw_annual_sum[r["arch"]]["nonhvac"].append(float(np.nansum(kwh_nonhvac)))

        run_df = calendar.copy()
        run_df["kwh_facility"] = kwh_fac / mean_fac
        run_df["kwh_nonhvac"] = kwh_nonhvac / mean_nonhvac
        per_arch_frames[r["arch"]].append(run_df)

    n_loaded = sum(len(v) for v in per_arch_frames.values())
    print(f"[T70] loaded {n_loaded} runs ok, {len(skipped)} skipped", flush=True)

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

    for entity, frame_weight_list in entities.items():
        for series, value_col in SERIES_COLS.items():
            for calendar_name, daytype_col in (("eplus", "daytype_eplus"),
                                                ("real2022", "daytype_real2022")):
                full_tbl = full_sub_table(frame_weight_list, value_col, daytype_col)
                for period_name, months in periods.items():
                    period_tbl = full_tbl[full_tbl["month"].isin(months)]
                    if period_tbl.empty:
                        continue
                    for daytype in ("weekday", "weekend", "holiday"):
                        sub = period_tbl[period_tbl["daytype"] == daytype][
                            ["DATE", "HOUR", "TOTAL_CONSUMPTION", "PREMISE_COUNT"]]
                        _profile_rows, metric_row = compute_slice_outputs(
                            "Toronto", 2022, period_name, daytype, sub)
                        if metric_row is not None:
                            metric_row.update({"series": series, "archetype": entity,
                                                "calendar": calendar_name})
                            all_metric_rows.append(metric_row)
        print(f"[T70] entity {entity} done, t={time.time()-t0:.0f}s", flush=True)

    metrics_df = pd.DataFrame(all_metric_rows)
    metrics_path = os.path.join(OUT_DIR, "sim_toronto_2022_shape_metrics_rebuilt.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"[out] wrote {metrics_path} ({len(metrics_df)} rows)", flush=True)

    # ---- sim_vs_measured_toronto_2022_shape_rebuilt.csv ----
    # Two calendar blocks (T15 item 2, unchanged): "eplus" (primary -- the day type the
    # occupancy schedule actually ran against) and "real2022" (kept so the size of the fix
    # is visible; task doc Ruling 3). Both joined against the SAME measured T02 numbers.
    # mean_kwh_per_premise EXCLUDED from the join (T15 item 1: ~1.0 by construction after
    # normalization). max_kwh_per_premise KEPT (T15 Decisions: task text names only
    # mean_kwh_per_premise for removal). data_vintage="rebuilt_2022" column added per the
    # task doc's explicit instruction, so this file is never confused with T15's old one.
    metric_cols = ["max_kwh_per_premise", "load_factor",
                   "peak_to_avg", "midday_share", "mean_peak_hour"]

    measured = pd.read_csv(T02_METRICS_PATH)
    measured = measured[measured["year"].astype(str) == "2022"].copy()

    join_rows = []
    period_order = (["shoulder", "winter", "summer", "full_year"]
                     + [f"month_{m:02d}" for m in range(1, 13)])
    daytype_order = ["weekday", "weekend", "holiday"]

    for calendar_name in ("eplus", "real2022"):
        sim_stock = metrics_df[(metrics_df["archetype"] == "StockWeighted")
                                & (metrics_df["calendar"] == calendar_name)].copy()
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
                                "calendar": calendar_name, "measured_scope": measured_scope,
                                "metric": metric, "sim": sim_v, "measured": meas_v,
                                "sim_minus_measured": (sim_v - meas_v)
                                    if (pd.notna(sim_v) and pd.notna(meas_v)) else np.nan,
                                "data_vintage": "rebuilt_2022",
                            })

    join_df = pd.DataFrame(join_rows)
    join_path = os.path.join(OUT_DIR, "sim_vs_measured_toronto_2022_shape_rebuilt.csv")
    join_df.to_csv(join_path, index=False)
    print(f"[out] wrote {join_path} ({len(join_df)} rows)", flush=True)

    # ---- per-dwelling annual Facility kWh (T15 item 3, unchanged) + C5 sanity bound ----
    annual_meter_mean = {}
    annual_per_dwelling = {}
    for a in ARCH_NAMES:
        vals = raw_annual_sum[a]["facility"]
        if not vals:
            annual_meter_mean[a] = None
            annual_per_dwelling[a] = None
            continue
        m = float(np.mean(vals))
        annual_meter_mean[a] = m
        annual_per_dwelling[a] = m / DWELLING_COUNT[a]

    # ---- C5: rebuild-vs-old sanity bound (task doc section 2). Guard only, never fails
    # the job -- just flags if the ratio (new/old) sits outside [0.5, 2.0]. ----
    c5_rows = {}
    for a in ARCH_NAMES:
        new_v = annual_meter_mean.get(a)
        old_v = T15_OLD_ANNUAL_FACILITY_KWH_MEAN.get(a)
        if new_v is None or old_v in (None, 0):
            c5_rows[a] = {"new_annual_facility_kwh_mean": new_v,
                          "old_t15_annual_facility_kwh_mean": old_v,
                          "ratio_new_over_old": None, "within_0.5_2.0": None}
            continue
        ratio = new_v / old_v
        c5_rows[a] = {
            "new_annual_facility_kwh_mean": new_v,
            "old_t15_annual_facility_kwh_mean": old_v,
            "ratio_new_over_old": ratio,
            "within_0.5_2.0": bool(0.5 <= ratio <= 2.0),
        }
    c5_all_within_bound = all(v.get("within_0.5_2.0") for v in c5_rows.values())
    print(f"[T70] C5 sanity bound per archetype: {c5_rows}", flush=True)
    print(f"[T70] C5 all archetypes within 0.5-2.0 ratio bound: {c5_all_within_bound}", flush=True)

    meta = {
        "job_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "elapsed_sec": time.time() - t0,
        "input_root": INPUT_ROOT,
        "n_runs_per_archetype": n_by_arch,
        "n_runs_loaded_ok": n_loaded,
        "n_runs_skipped": len(skipped),
        "skipped": skipped,
        "row_counts": {
            "sim_toronto_2022_shape_metrics_rebuilt.csv": len(metrics_df),
            "sim_vs_measured_toronto_2022_shape_rebuilt.csv": len(join_df),
        },
        "dwelling_count": DWELLING_COUNT,
        "dwelling_count_evidence": DWELLING_COUNT_EVIDENCE,
        "dwelling_count_reasoning": (
            "Task Ruling 2: the rebuild (T21) changes occupancy schedules (2022-diaries "
            "only), not building geometry / IDF zone structure -- so DWELLING_COUNT, "
            "derived from Scenario_2022.idf ZoneList/ZoneGroup objects in T15, does not "
            "need re-deriving for the rebuilt runs, which share the same Toronto_5A "
            "archetype IDF templates. Not re-grepped on the rebuilt tree's IDFs in this run."
        ),
        "annual_facility_kwh_meter_mean_per_archetype": annual_meter_mean,
        "annual_facility_kwh_per_dwelling_estimate": annual_per_dwelling,
        "c5_rebuild_vs_old_sanity_bound": c5_rows,
        "c5_all_within_0.5_2.0_bound": c5_all_within_bound,
        "note": ("meter_mean = mean over the archetype's loaded runs of that run's raw "
                 "(non-normalized) annual Facility kWh sum; per_dwelling = meter_mean / "
                 "DWELLING_COUNT[archetype]. For SingleD, DWELLING_COUNT=1 so meter_mean "
                 "== per_dwelling. C5 compares this run's meter_mean against T15's OLD "
                 "(now-retired-tree) meter_mean, hardcoded from impl/T15_out/run_meta.json "
                 "-- a sanity bound, not an exact-match test; the rebuild is EXPECTED to "
                 "shift these numbers."),
    }
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print(f"[T70] done in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
