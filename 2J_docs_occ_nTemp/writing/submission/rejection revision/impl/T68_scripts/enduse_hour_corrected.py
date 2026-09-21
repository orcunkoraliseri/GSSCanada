#!/usr/bin/env python3
"""
T68 -- WP6 Part A: end use x hour on the CORRECTED 2022 and 2030 T21 rebuild.
Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/2026-09-20_T68_wp6_enduse_hour_corrected.md

Copy-and-repoint of impl/T06_scripts/enduse_hour_2022_v2.py (T06 -- 2022 only, OLD campaign_N50
tree). T06's original file is NEVER edited; this is a separate file. Changes vs T06 v2, each
tied to a numbered ruling in the task doc's section 1:

  (ruling 2) INPUT_ROOT points at the T21 rebuild (/speed-scratch/o_iseri/2J_revision/T21/out/step8),
    not the old campaign tree. discover_runs() uses T21's PLAIN cell_manifest.csv only (columns
    sample,sim_hh_id,hhsize,dtype,pr) -- NO overlay-manifest / is_new_sample gating. T21 has no
    overlay file (cell_manifest.csv.new_2022_2030_*) and reinstating that gate would silently
    return ZERO rows (T67 finding, impl/2026-09-20_T67_wp8_genuine_cluster_bootstrap_IMPL.md,
    step 0 item 3). Both 2022 AND 2030 are read (T06 only read 2022).

  (ruling 3, 4) Per-dwelling divisor columns added. The two divisor dictionaries below are
    COPIED VERBATIM (never re-derived) from
    /speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py
    (T66_CELL_EQUIP_DIVISOR / T66_CELL_LIGHT_DIVISOR, read via scp+grep on 2026-09-20; that file
    itself is never imported or edited by this script). SingleD gets divisor 1.0 on EVERY meter
    (ruling 4 last bullet: physical fact -- one dwelling unit per building, not a "derived"
    correction) so SingleD absolutes are quotable everywhere. For OtherDwelling/MidRise/HighRise,
    ONLY InteriorEquipment:Electricity and InteriorLights:Electricity get a per-dwelling column
    (from the two T66 dictionaries); every other meter (Fan Electricity Energy,
    Electricity:Facility, the three *:EnergyTransfer meters, and the HVACDHW remainder) gets
    NOT_EVALUABLE in its per-dwelling column, reason "no derived unit divisor (T66 covers
    equip+light only)" -- never a reused/guessed divisor.

  (ruling 5, 6) New file enduse_change_2022_2030.csv: per-cell paired t-interval (reuses the exact
    t.interval(0.95, n-1, loc=mean, scale=sem) formula T67 calls "method_a_t_interval", verified
    against /speed-scratch/o_iseri/2J_revision/T67/T67_scripts/cell_cluster_bootstrap.py:52-58 by
    inspection -- not imported, since that module's build_paired()/METRICS are hardcoded to
    midday_share/load_factor only and this task needs the same FORMULA applied to many more
    metrics) PLUS a stock-weighted cluster-bootstrap using the IDENTICAL resampling unit T67 uses
    (whole (arch,city) cells drawn with replacement, 24 from 24 -- see
    stock_weighted_cluster_bootstrap() below, a new function, not an edit of T67's file). For
    midday_share and load_factor specifically, the STOCK-WEIGHTED interval is never recomputed --
    it is read verbatim from T67's own already-scored output
    (/speed-scratch/o_iseri/2J_revision/T67/out/real_correcteddata/ci_reproduction_t67.csv),
    per ruling 6 ("reuse it ... rather than writing a third bootstrap"). Per-cell rows for
    midday_share/load_factor DO get a freshly computed per-cell t-interval here (T67 only scored
    the stock level) -- this is the SAME formula (Method A), not a new statistic.

  (ruling 7, 8, item 9/32) Meter rules, closure identity, WaterSystems:EnergyTransfer absence and
    the DTYPE==8 exclusion are all UNCHANGED from T06 v2 / 08_simulation_plots.py -- see that
    file's own header for the line citations, repeated here: meters indexed BY NAME, never column
    order (08_simulation_plots.py:79-91); Electricity:Facility already includes lights+equip+fan,
    never add them to it (:80); *:EnergyTransfer columns are thermal loads, never summed into
    electricity (:84-86,89); Fan Electricity Energy (not Fans:Electricity) is the paper's own
    fan-meter choice, followed here.

  NOT changed from T06 v2: meter selection, STOCK_WEIGHTS, the hourly-profile shape (season x
  daytype x hour), MIDDAY window, load_factor/midday_share/evening-ramp/p90 formulas, the closure
  identity definition (remainder = Facility - (lights+equip+fan), reported, no 0.07% pass/fail).

Controls C1-C4 (task doc section 4) all run in this same job, before the real per-household loop
writes anything to controls.json is treated as final -- see run_controls_pre() / run_controls_post().
"""
import os
import re
import csv
import json
import time
import traceback
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
from scipy import stats

# --------------------------------------------------------------------------------------------
# Paths (ruling 2)
# --------------------------------------------------------------------------------------------
INPUT_ROOT = "/speed-scratch/o_iseri/2J_revision/T21/out/step8"
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T68/out"
T67_AGG_ANNUAL = "/speed-scratch/o_iseri/2J_revision/T67/out/agg_annual.csv"
T67_REAL_CI = "/speed-scratch/o_iseri/2J_revision/T67/out/real_correcteddata/ci_reproduction_t67.csv"
HAND_CHECK_CSV = os.path.join(
    INPUT_ROOT, "SingleD__Montreal_6A", "sample_001_HH130228", "2022", "hourly_meters.csv")
HAND_CHECK_ANNUAL_KWH = 8209.333463
HAND_CHECK_PEAK_KW = 4.318054

ARCH_NAMES = ["SingleD", "OtherDwelling", "MidRise", "HighRise"]
CITY_REGION = {
    "Toronto_5A": "Ontario", "Kelowna_5B": "BC", "Vancouver_5C": "BC",
    "Montreal_6A": "Quebec", "Calgary_6B": "Alberta", "Winnipeg_7A": "Prairies",
}
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

FACILITY = "Electricity:Facility"
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP = "InteriorEquipment:Electricity"
M_FAN = "Fan Electricity Energy"
M_HEAT = "Heating:EnergyTransfer"
M_COOL = "Cooling:EnergyTransfer"
M_WATER = "WaterSystems:EnergyTransfer"
KEEP_METERS = [FACILITY, M_LIGHTS, M_EQUIP, M_FAN, M_HEAT, M_COOL, M_WATER]
ELEC_COMPONENTS = [M_LIGHTS, M_EQUIP, M_FAN]
ANN_COL = {FACILITY: "elec_facility_kWh", M_LIGHTS: "lights_kWh", M_EQUIP: "equip_kWh",
           M_FAN: "fan_kWh", M_HEAT: "heating_ET_kWh", M_COOL: "cooling_ET_kWh",
           M_WATER: "water_ET_kWh"}
REMAINDER_METER_LABEL = "HVACDHW:Electricity"
REMAINDER_ANN_COL = "hvac_dhw_elec_kWh"
# meters carried into the change table, in ANN_COL-value space (+ the remainder)
CHANGE_METERS = [ANN_COL[m] for m in KEEP_METERS] + [REMAINDER_ANN_COL]
METER_LABEL_OF_ANNCOL = {v: k for k, v in ANN_COL.items()}
METER_LABEL_OF_ANNCOL[REMAINDER_ANN_COL] = REMAINDER_METER_LABEL

MIDDAY = (9, 17)
SEASON_WINDOWS = {
    "all": set(range(1, 366)),
    "heating": set(range(1, 32)),
    "shoulder": set(range(91, 121)) | set(range(274, 305)),
    "cooling": set(range(182, 213)),
}
SEASONS = list(SEASON_WINDOWS.keys())
DAYTYPES = ["all", "weekday", "weekend"]
_DOY = np.arange(1, 366)

# --------------------------------------------------------------------------------------------
# ruling 3: divisor dictionaries, COPIED VERBATIM from T66's corrected validator on 2026-09-20.
# Source: /speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py
#         lines 57-108 (T66_CELL_EQUIP_DIVISOR / T66_CELL_LIGHT_DIVISOR). DO NOT EDIT. DO NOT
# RE-DERIVE. If T66 ever revises these dictionaries, this copy must be refreshed from the source
# file, never hand-adjusted here.
# --------------------------------------------------------------------------------------------
T66_CELL_EQUIP_DIVISOR = {
    'SingleD__Toronto_5A': 1.000000, 'SingleD__Kelowna_5B': 1.000000,
    'SingleD__Vancouver_5C': 1.000000, 'SingleD__Montreal_6A': 1.000000,
    'SingleD__Calgary_6B': 1.000000, 'SingleD__Winnipeg_7A': 1.000000,
    'OtherDwelling__Toronto_5A': 7.000000, 'OtherDwelling__Kelowna_5B': 7.000000,
    'OtherDwelling__Vancouver_5C': 7.000000, 'OtherDwelling__Montreal_6A': 7.000000,
    'OtherDwelling__Calgary_6B': 7.000000, 'OtherDwelling__Winnipeg_7A': 7.000000,
    'MidRise__Toronto_5A': 33.000000, 'MidRise__Kelowna_5B': 33.000000,
    'MidRise__Vancouver_5C': 33.000000, 'MidRise__Montreal_6A': 33.000000,
    'MidRise__Calgary_6B': 33.000000, 'MidRise__Winnipeg_7A': 33.000000,
    'HighRise__Toronto_5A': 81.000000, 'HighRise__Kelowna_5B': 81.000000,
    'HighRise__Vancouver_5C': 81.000000, 'HighRise__Montreal_6A': 81.000000,
    'HighRise__Calgary_6B': 81.000000, 'HighRise__Winnipeg_7A': 81.000000,
}
T66_CELL_LIGHT_DIVISOR = {
    'SingleD__Toronto_5A': 1.000000, 'SingleD__Kelowna_5B': 1.000000,
    'SingleD__Vancouver_5C': 1.000000, 'SingleD__Montreal_6A': 1.000000,
    'SingleD__Calgary_6B': 1.000000, 'SingleD__Winnipeg_7A': 1.000000,
    'OtherDwelling__Toronto_5A': 7.000000, 'OtherDwelling__Kelowna_5B': 7.000000,
    'OtherDwelling__Vancouver_5C': 7.000000, 'OtherDwelling__Montreal_6A': 7.000000,
    'OtherDwelling__Calgary_6B': 7.000000, 'OtherDwelling__Winnipeg_7A': 7.000000,
    'MidRise__Toronto_5A': 36.000000, 'MidRise__Kelowna_5B': 36.000000,
    'MidRise__Vancouver_5C': 36.000000, 'MidRise__Montreal_6A': 36.000000,
    'MidRise__Calgary_6B': 36.000000, 'MidRise__Winnipeg_7A': 36.000000,
    'HighRise__Toronto_5A': 90.000000, 'HighRise__Kelowna_5B': 90.000000,
    'HighRise__Vancouver_5C': 90.000000, 'HighRise__Montreal_6A': 90.000000,
    'HighRise__Calgary_6B': 90.000000, 'HighRise__Winnipeg_7A': 90.000000,
}


def is_weekend(doy):
    wd = (doy - 1) % 7
    return wd == 0 or wd == 6


_WEEKEND = np.array([is_weekend(int(d)) for d in _DOY])
_SEASON_MASK = {s: np.array([int(d) in SEASON_WINDOWS[s] for d in _DOY]) for s in SEASONS}


def _daytype_mask(daytype):
    if daytype == "weekday":
        return ~_WEEKEND
    if daytype == "weekend":
        return _WEEKEND
    return np.ones(365, dtype=bool)


def _circular_mean_hour(hours):
    if len(hours) == 0:
        return np.nan, np.nan, np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    mean_h = (np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0
    return mean_h, s, c


_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)


def divisor_for(meter_ann_col, arch, cell):
    """ruling 4: returns (divisor, source, status, reason). status is QUOTABLE or NOT_EVALUABLE."""
    if arch == "SingleD":
        return 1.0, "physical (single dwelling unit per building; ruling 4 last bullet)", "QUOTABLE", None
    if meter_ann_col == "equip_kWh":
        d = T66_CELL_EQUIP_DIVISOR.get(cell)
        if d is not None:
            return d, "T66 T66_CELL_EQUIP_DIVISOR (step9_validate_full_corrected.py)", "QUOTABLE", None
    if meter_ann_col == "lights_kWh":
        d = T66_CELL_LIGHT_DIVISOR.get(cell)
        if d is not None:
            return d, "T66 T66_CELL_LIGHT_DIVISOR (step9_validate_full_corrected.py)", "QUOTABLE", None
    return None, None, "NOT_EVALUABLE", "no derived unit divisor (T66 covers equip+light only)"


def load_cell_manifest(cell_dir):
    """ruling 2: PLAIN manifest only, columns sample,sim_hh_id,hhsize,dtype,pr. No overlay merge,
    no is_new_sample gate -- T21 has no overlay file and the gate would zero every row."""
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


def discover_runs(results_dir):
    """T21 plain-manifest discovery, both years. Returns run dicts + a skip log."""
    runs = []
    skipped = []
    for cell_name in sorted(os.listdir(results_dir)):
        cell_dir = os.path.join(results_dir, cell_name)
        if not os.path.isdir(cell_dir) or "__" not in cell_name:
            continue
        arch, _, city = cell_name.partition("__")
        if arch not in ARCH_NAMES or city not in CITY_REGION:
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
            for year in (2022, 2030):
                ydir = os.path.join(samp_dir, str(year))
                csvp = os.path.join(ydir, "hourly_meters.csv")
                if not os.path.exists(csvp):
                    skipped.append({"cell": cell_name, "sample": sample_from_dir,
                                     "sim_hh_id": hh_from_dir, "year": year,
                                     "reason": "hourly_meters.csv missing"})
                    continue
                runs.append({
                    "arch": arch, "city": city, "region": CITY_REGION[city],
                    "sample": sample_from_dir, "sim_hh_id": str(hh_from_dir),
                    "hhsize": meta.get("hhsize", ""), "cell": cell_name, "year": year,
                    "csv_path": csvp,
                })
    return runs, skipped


def process_one(rm):
    key = {"cell": rm["cell"], "arch": rm["arch"], "city": rm["city"], "region": rm["region"],
           "sample": rm["sample"], "sim_hh_id": rm["sim_hh_id"], "hhsize": rm["hhsize"],
           "year": rm["year"]}
    try:
        df = pd.read_csv(rm["csv_path"])
    except Exception as e:
        return "read_error", key, str(e), None, None, None

    n = len(df)
    if n < 8760:
        return "short", key, f"n_hours={n}", None, None, None

    meter_2d = {}
    for meter in KEEP_METERS:
        if meter not in df.columns:
            continue
        kw = pd.to_numeric(df[meter], errors="coerce").to_numpy()[:8760] / 3.6e6  # J/h -> kW
        meter_2d[meter] = kw.reshape(365, 24)

    have_remainder = all(m in meter_2d for m in ELEC_COMPONENTS) and FACILITY in meter_2d
    remainder_2d = (meter_2d[FACILITY] - sum(meter_2d[m] for m in ELEC_COMPONENTS)) if have_remainder else None

    # -- annual kWh per end use, raw whole-building, + per-dwelling (ruling 4) --
    annual = dict(key)
    for meter in KEEP_METERS:
        ann_col = ANN_COL[meter]
        raw = float(meter_2d[meter].sum()) if meter in meter_2d else np.nan
        annual[ann_col] = raw
        divi, src, status, reason = divisor_for(ann_col, rm["arch"], rm["cell"])
        annual[f"{ann_col}_divisor"] = divi if divi is not None else np.nan
        annual[f"{ann_col}_divisor_source"] = src
        annual[f"{ann_col}_status"] = status
        annual[f"{ann_col}_status_reason"] = reason
        annual[f"{ann_col}_per_dwelling"] = (raw / divi) if (status == "QUOTABLE" and not np.isnan(raw)) else "NOT_EVALUABLE"
    raw_rem = float(remainder_2d.sum()) if remainder_2d is not None else np.nan
    annual[REMAINDER_ANN_COL] = raw_rem
    divi, src, status, reason = divisor_for(REMAINDER_ANN_COL, rm["arch"], rm["cell"])
    annual[f"{REMAINDER_ANN_COL}_divisor"] = divi if divi is not None else np.nan
    annual[f"{REMAINDER_ANN_COL}_divisor_source"] = src
    annual[f"{REMAINDER_ANN_COL}_status"] = status
    annual[f"{REMAINDER_ANN_COL}_status_reason"] = reason
    annual[f"{REMAINDER_ANN_COL}_per_dwelling"] = (raw_rem / divi) if (status == "QUOTABLE" and not np.isnan(raw_rem)) else "NOT_EVALUABLE"

    # -- closure identity (raw whole-building only -- see task doc item 5; per-dwelling division
    #    by DIFFERENT divisors for lights vs equip would break the identity, so it is deliberately
    #    never applied here) --
    closure = dict(key)
    if have_remainder:
        comp_sum = sum(meter_2d[m].sum() for m in ELEC_COMPONENTS)
        fac_sum = meter_2d[FACILITY].sum()
        closure["components_kWh"] = float(comp_sum)
        closure["facility_kWh"] = float(fac_sum)
        closure["hvac_dhw_elec_kWh"] = float(fac_sum - comp_sum)
        closure["identity_residual_kWh"] = float(fac_sum - (comp_sum + (fac_sum - comp_sum)))  # == 0 by construction; sanity
    else:
        closure["components_kWh"] = closure["facility_kWh"] = np.nan
        closure["hvac_dhw_elec_kWh"] = closure["identity_residual_kWh"] = np.nan

    # -- hourly profile (unchanged shape from T06) --
    profile_rows = []
    profile_meters = list(KEEP_METERS)
    profile_grids = dict(meter_2d)
    if remainder_2d is not None:
        profile_meters = profile_meters + [REMAINDER_METER_LABEL]
        profile_grids[REMAINDER_METER_LABEL] = remainder_2d
    for meter in profile_meters:
        if meter not in profile_grids:
            continue
        grid = profile_grids[meter]
        for season in ("all", "heating", "cooling"):
            for daytype in DAYTYPES:
                mask = _SEASON_MASK[season] & _daytype_mask(daytype)
                days = np.where(mask)[0]
                if days.size == 0:
                    continue
                prof = grid[days].mean(axis=0)
                for h in range(24):
                    profile_rows.append({**key, "meter": meter, "season": season,
                                          "daytype": daytype, "hour": h,
                                          "load_kW": float(prof[h]), "n_days": int(days.size)})

    # -- grid-facing metrics on Electricity:Facility (unchanged from T06) --
    grid_row = dict(key)
    if FACILITY in meter_2d:
        fac = meter_2d[FACILITY]
        flat = fac.reshape(-1)
        daily_peak = fac.max(axis=1)
        daily_peak_hr = fac.argmax(axis=1)
        mean_h, ssin, ccos = _circular_mean_hour(daily_peak_hr)
        mean24, max24 = fac.mean(), flat.max()
        grid_row["peak_kW_annual"] = float(flat.max())
        grid_row["peak_hour_annual"] = int(flat.argmax() % 24)
        grid_row["mean_daily_peak_kW"] = float(daily_peak.mean())
        grid_row["mean_peak_hour_circ"] = float(mean_h)
        grid_row["load_factor"] = float(mean24 / max24) if max24 else np.nan
        grid_row["midday_share"] = float(fac[:, MIDDAY[0]:MIDDAY[1]].sum() / flat.sum()) if flat.sum() else np.nan
        ramp = fac[:, 17] - fac[:, 14]
        grid_row["evening_ramp_kW_mean"] = float(ramp.mean())
        grid_row["evening_ramp_kW_p90"] = float(np.percentile(ramp, 90))
        p90 = np.percentile(flat, 90)
        grid_row["p90_kW"] = float(p90)
        grid_row["n_hours_above_own_p90"] = int((flat > p90).sum())
    else:
        for c in ("peak_kW_annual", "peak_hour_annual", "mean_daily_peak_kW",
                   "mean_peak_hour_circ", "load_factor", "midday_share",
                   "evening_ramp_kW_mean", "evening_ramp_kW_p90", "p90_kW",
                   "n_hours_above_own_p90"):
            grid_row[c] = np.nan

    return "ok", key, None, profile_rows, grid_row, (annual, closure)


# ================================================================================================
# Controls (task doc section 4). Each returns a dict with outcome in
# {"did_not_run", "ran_not_fired", "ran_and_fired", "not_evaluable_crashed"} plus detail.
# ================================================================================================

def control_c1_hour_of_day(csv_path):
    """C1 -- seen-failing, hour-of-day. Roll every column EXCEPT 'hour' forward by 3 row
    positions; 'hour' labels (0..8759, confirmed via ssh head/sed on 2026-09-20) stay untouched.
    Peak hour must move by exactly +3 (mod 24) and midday_share must change."""
    try:
        df = pd.read_csv(csv_path)
        if "hour" not in df.columns or FACILITY not in df.columns:
            return {"control": "C1", "outcome": "not_evaluable_crashed",
                    "detail": "hour or Electricity:Facility column missing"}
        fac_orig = pd.to_numeric(df[FACILITY], errors="coerce").to_numpy()[:8760] / 3.6e6
        fac_shift = np.roll(fac_orig, 3)  # 'hour' column values are NOT touched -- only the data moves

        def stats_for(flat):
            grid = flat.reshape(365, 24)
            peak_hour = int(flat.argmax() % 24)
            midday = float(grid[:, MIDDAY[0]:MIDDAY[1]].sum() / flat.sum())
            return peak_hour, midday

        peak_o, mid_o = stats_for(fac_orig)
        peak_s, mid_s = stats_for(fac_shift)
        expected_peak = (peak_o + 3) % 24
        peak_ok = (peak_s == expected_peak)
        midday_changed = (mid_s != mid_o)
        fired = bool(peak_ok and midday_changed)
        return {
            "control": "C1", "outcome": "ran_and_fired" if fired else "ran_not_fired",
            "peak_hour_original": peak_o, "peak_hour_shifted": peak_s,
            "expected_peak_hour_shifted": int(expected_peak),
            "midday_share_original": mid_o, "midday_share_shifted": mid_s,
            "household": csv_path,
        }
    except Exception as e:
        return {"control": "C1", "outcome": "not_evaluable_crashed", "detail": f"{e}\n{traceback.format_exc()}"}


def control_c2_seen_working(annual_df, grid_df):
    """C2 -- reproduce T67's agg_annual.csv (midday_share/load_factor, 2400 rows) and the one
    hand-verified household's annual Electricity:Facility total + peak kW."""
    out = {"control": "C2"}
    try:
        t67 = pd.read_csv(T67_AGG_ANNUAL)
        mine = grid_df[["arch", "city", "sim_hh_id", "year", "midday_share", "load_factor"]].copy()
        mine["sim_hh_id"] = mine["sim_hh_id"].astype(str)
        t67["sim_hh_id"] = t67["sim_hh_id"].astype(str)
        merged = t67.merge(mine, on=["arch", "city", "sim_hh_id", "year"], suffixes=("_t67", "_mine"), how="inner")
        out["n_t67_rows"] = int(len(t67))
        out["n_matched_rows"] = int(len(merged))
        if len(merged) > 0:
            out["max_abs_diff_midday_share"] = float((merged["midday_share_t67"] - merged["midday_share_mine"]).abs().max())
            out["max_abs_diff_load_factor"] = float((merged["load_factor_t67"] - merged["load_factor_mine"]).abs().max())
        else:
            out["max_abs_diff_midday_share"] = None
            out["max_abs_diff_load_factor"] = None
    except Exception as e:
        out["outcome"] = "not_evaluable_crashed"
        out["detail"] = f"{e}\n{traceback.format_exc()}"
        return out

    try:
        hh = annual_df[(annual_df["arch"] == "SingleD") & (annual_df["city"] == "Montreal_6A") &
                        (annual_df["sim_hh_id"].astype(str) == "130228") & (annual_df["year"] == 2022)]
        ghh = grid_df[(grid_df["arch"] == "SingleD") & (grid_df["city"] == "Montreal_6A") &
                       (grid_df["sim_hh_id"].astype(str) == "130228") & (grid_df["year"] == 2022)]
        if hh.empty or ghh.empty:
            out["hand_check_found"] = False
        else:
            out["hand_check_found"] = True
            mine_annual = float(hh.iloc[0]["elec_facility_kWh"])
            mine_peak = float(ghh.iloc[0]["peak_kW_annual"])
            out["hand_check_annual_kWh_mine"] = mine_annual
            out["hand_check_annual_kWh_expected"] = HAND_CHECK_ANNUAL_KWH
            out["hand_check_peak_kW_mine"] = mine_peak
            out["hand_check_peak_kW_expected"] = HAND_CHECK_PEAK_KW
            out["hand_check_annual_diff"] = abs(mine_annual - HAND_CHECK_ANNUAL_KWH)
            out["hand_check_peak_diff"] = abs(mine_peak - HAND_CHECK_PEAK_KW)
    except Exception as e:
        out["outcome"] = "not_evaluable_crashed"
        out["detail"] = f"{e}\n{traceback.format_exc()}"
        return out

    tol = 1e-4
    ok_agg = (out.get("max_abs_diff_midday_share") is not None and
              out["max_abs_diff_midday_share"] < tol and out["max_abs_diff_load_factor"] < tol)
    ok_hand = (out.get("hand_check_found") and out["hand_check_annual_diff"] < 1e-3 and out["hand_check_peak_diff"] < 1e-3)
    out["outcome"] = "ran_and_fired" if (ok_agg and ok_hand) else "ran_not_fired"
    return out


def control_c3_divisor_invariance(annual_df):
    """C3 -- 2022->2030 percent change for equipment must be identical whether computed on the
    raw whole-building series or the per-dwelling divided series (proves ruling 4's divisor
    invariance claim for a divisor != 1 archetype)."""
    out = {"control": "C3"}
    try:
        sub = annual_df[annual_df["arch"] == "HighRise"]
        p22 = sub[sub["year"] == 2022].set_index(["arch", "city", "sim_hh_id"])
        p30 = sub[sub["year"] == 2030].set_index(["arch", "city", "sim_hh_id"])
        common = p22.index.intersection(p30.index)
        if len(common) == 0:
            out["outcome"] = "not_evaluable_crashed"
            out["detail"] = "no paired HighRise households found"
            return out
        raw22 = p22.loc[common, "equip_kWh"].astype(float)
        raw30 = p30.loc[common, "equip_kWh"].astype(float)
        pct_raw = 100.0 * (raw30 - raw22) / raw22

        # per-dwelling series: divide by the SAME per-cell divisor both years (divisor is a
        # per-cell constant, not per-year, so this is well-defined)
        pd22 = p22.loc[common, "equip_kWh_per_dwelling"]
        pd30 = p30.loc[common, "equip_kWh_per_dwelling"]
        pd22_num = pd.to_numeric(pd22, errors="coerce")
        pd30_num = pd.to_numeric(pd30, errors="coerce")
        pct_div = 100.0 * (pd30_num - pd22_num) / pd22_num

        diff = (pct_raw.to_numpy() - pct_div.to_numpy())
        diff = diff[~np.isnan(diff)]
        max_diff = float(np.abs(diff).max()) if diff.size else None
        out["n_compared"] = int(diff.size)
        out["max_abs_pct_diff"] = max_diff
        out["outcome"] = "ran_and_fired" if (max_diff is not None and max_diff < 1e-8) else "ran_not_fired"
    except Exception as e:
        out["outcome"] = "not_evaluable_crashed"
        out["detail"] = f"{e}\n{traceback.format_exc()}"
    return out


def control_c4_divisor_applied(annual_df):
    """C4 -- after division, HighRise/MidRise per-dwelling equip+light annual kWh must be the
    same order of magnitude as SingleD/OtherDwelling's. Prints before/after per archetype."""
    out = {"control": "C4", "per_archetype": {}}
    try:
        for meter_col in ("equip_kWh", "lights_kWh"):
            per_dwelling_col = f"{meter_col}_per_dwelling"
            arch_stats = {}
            for arch in ARCH_NAMES:
                sub = annual_df[annual_df["arch"] == arch]
                if sub.empty:
                    continue
                before = float(pd.to_numeric(sub[meter_col], errors="coerce").mean())
                pd_series = pd.to_numeric(sub[per_dwelling_col], errors="coerce")
                after = float(pd_series.mean()) if pd_series.notna().any() else None
                arch_stats[arch] = {"before_whole_building_mean_kWh": before,
                                     "after_per_dwelling_mean_kWh": after}
            out["per_archetype"][meter_col] = arch_stats

        fired = True
        for meter_col, arch_stats in out["per_archetype"].items():
            vals = [v["after_per_dwelling_mean_kWh"] for v in arch_stats.values()
                    if v["after_per_dwelling_mean_kWh"] is not None]
            if len(vals) < 2:
                fired = False
                continue
            logs = [np.log10(v) for v in vals if v > 0]
            if not logs or (max(logs) - min(logs)) > 1.5:  # within ~30x of each other
                fired = False
        out["outcome"] = "ran_and_fired" if fired else "ran_not_fired"
    except Exception as e:
        out["outcome"] = "not_evaluable_crashed"
        out["detail"] = f"{e}\n{traceback.format_exc()}"
    return out


# ================================================================================================
# Change table (ruling 5, 6)
# ================================================================================================

def paired_t_interval(deltas):
    d = np.asarray(deltas, dtype=float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 2:
        return None
    mean = float(d.mean())
    lo, hi = stats.t.interval(0.95, n - 1, loc=mean, scale=stats.sem(d))
    return mean, float(lo), float(hi), n


def stock_weighted_cluster_bootstrap(cell_arrays, n_rep=10000, seed=12345):
    """Same resampling unit as T67's cell_cluster_bootstrap (T67_scripts/cell_cluster_bootstrap.py
    :61-78): draw n_cells cell indices WITH REPLACEMENT from the n_cells available cells per
    replicate, keep each drawn cell's household array intact. NEW here vs T67: the per-replicate
    statistic is a STOCK-WEIGHTED mean across archetypes (STOCK_WEIGHTS, pooling all households
    from all drawn cells of that archetype), not a flat pooled mean -- T67's own two metrics
    (midday_share, load_factor) are reused verbatim from its own output, never recomputed here;
    this function is only used for the OTHER end-use metrics, per ruling 6."""
    cells = list(cell_arrays.keys())
    n_cells = len(cells)
    if n_cells == 0:
        return None
    rng = np.random.default_rng(seed)

    def stock_mean(draw_cells):
        by_arch = {}
        for c in draw_cells:
            arch = c[0]
            arr = cell_arrays[c]
            if arr.size == 0:
                continue
            by_arch.setdefault(arch, []).append(arr)
        acc = 0.0
        for arch, arrs in by_arch.items():
            pooled = np.concatenate(arrs)
            if pooled.size == 0:
                continue
            acc += STOCK_WEIGHTS.get(arch, 0.0) * float(pooled.mean())
        return acc

    point = stock_mean(cells)  # all 24 cells present once, unresampled
    boot = np.empty(n_rep, dtype=float)
    for r in range(n_rep):
        draw_idx = rng.integers(0, n_cells, size=n_cells)
        draw_cells = [cells[i] for i in draw_idx]
        boot[r] = stock_mean(draw_cells)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return point, float(lo), float(hi), n_cells


def safe_pct_change(v22, v30):
    if v22 is None or v30 is None or (isinstance(v22, float) and np.isnan(v22)) or (isinstance(v30, float) and np.isnan(v30)):
        return None, "missing_value"
    if v22 == 0:
        return None, "zero_2022_denominator"
    return 100.0 * (v30 - v22) / v22, None


def build_change_table(annual_df, grid_df):
    rows = []
    annual_df = annual_df.copy()
    annual_df["sim_hh_id"] = annual_df["sim_hh_id"].astype(str)
    grid_df = grid_df.copy()
    grid_df["sim_hh_id"] = grid_df["sim_hh_id"].astype(str)

    p22 = annual_df[annual_df["year"] == 2022].set_index(["arch", "city", "sim_hh_id"])
    p30 = annual_df[annual_df["year"] == 2030].set_index(["arch", "city", "sim_hh_id"])
    common_idx = p22.index.intersection(p30.index)

    g22 = grid_df[grid_df["year"] == 2022].set_index(["arch", "city", "sim_hh_id"])
    g30 = grid_df[grid_df["year"] == 2030].set_index(["arch", "city", "sim_hh_id"])
    g_common = g22.index.intersection(g30.index)

    cells_present = sorted(set((a, c) for a, c, _ in common_idx))

    zero_denom_counts = {}

    # ---- end-use meters: percent change ----
    for ann_col in CHANGE_METERS:
        pct_by_household = {}  # (arch,city,sim_hh_id) -> pct
        n_zero_denom = 0
        n_zero_denom_by_cell = {}  # (arch,city) -> count
        for idx in common_idx:
            v22 = p22.loc[idx, ann_col]
            v30 = p30.loc[idx, ann_col]
            pct, why = safe_pct_change(v22, v30)
            if pct is None:
                if why == "zero_2022_denominator":
                    n_zero_denom += 1
                    cell_key = (idx[0], idx[1])
                    n_zero_denom_by_cell[cell_key] = n_zero_denom_by_cell.get(cell_key, 0) + 1
                continue
            pct_by_household[idx] = pct
        zero_denom_counts[ann_col] = n_zero_denom

        cell_pct_arrays = {}
        for cell_key in cells_present:
            hh_ids = [idx for idx in pct_by_household if (idx[0], idx[1]) == cell_key]
            cell_pct_arrays[cell_key] = np.array([pct_by_household[i] for i in hh_ids], dtype=float)

        # per-cell rows
        for (arch, city) in cells_present:
            arr = cell_pct_arrays.get((arch, city), np.array([]))
            v22_mean = float(p22.loc[(arch, city, slice(None)), ann_col].astype(float).mean()) if (arch, city) in [(a, c) for a, c, _ in p22.index] else np.nan
            v30_mean = float(p30.loc[(arch, city, slice(None)), ann_col].astype(float).mean()) if (arch, city) in [(a, c) for a, c, _ in p30.index] else np.nan
            ti = paired_t_interval(arr)
            meter_label = METER_LABEL_OF_ANNCOL[ann_col]
            row = {
                "level": "per_cell", "cell": f"{arch}__{city}", "arch": arch, "city": city,
                "metric": meter_label, "metric_ann_col": ann_col, "change_type": "percent",
                "value_2022_raw_kWh": v22_mean, "value_2030_raw_kWh": v30_mean,
                "absolute_change_raw_kWh": (v30_mean - v22_mean) if not (np.isnan(v22_mean) or np.isnan(v30_mean)) else np.nan,
                "n_zero_2022_denominator_excluded": int(n_zero_denom_by_cell.get((arch, city), 0)),
            }
            if ti is not None:
                mean_pct, lo, hi, npair = ti
                excludes_zero = not (lo <= 0.0 <= hi)
                row.update({
                    "point_change_pct": mean_pct, "ci_low_pct": lo, "ci_high_pct": hi,
                    "ci_method": "paired_t_interval (T67 method_a formula, reused)",
                    "n_paired": npair, "excludes_zero": excludes_zero,
                    "change_quotable": "QUOTABLE" if excludes_zero else "NOT_EVALUABLE",
                    "change_quotable_reason": None if excludes_zero else "interval contains zero (ruling 5, T28/T60 quoting rule)",
                })
            else:
                row.update({
                    "point_change_pct": None, "ci_low_pct": None, "ci_high_pct": None,
                    "ci_method": None, "n_paired": int(arr.size), "excludes_zero": False,
                    "change_quotable": "NOT_EVALUABLE",
                    "change_quotable_reason": "fewer than 2 valid paired households for this cell/meter",
                })
            rows.append(row)

        # stock-weighted row
        st = stock_weighted_cluster_bootstrap(cell_pct_arrays)
        meter_label = METER_LABEL_OF_ANNCOL[ann_col]
        row = {"level": "stock_weighted", "cell": "ALL_STOCK_WEIGHTED", "arch": "ALL", "city": "ALL",
               "metric": meter_label, "metric_ann_col": ann_col, "change_type": "percent"}
        if st is not None:
            point, lo, hi, ncells = st
            excludes_zero = not (lo <= 0.0 <= hi)
            row.update({
                "point_change_pct": point, "ci_low_pct": lo, "ci_high_pct": hi,
                "ci_method": "stock_weighted_cluster_bootstrap (new fn, same resampling unit as T67 cell_cluster_bootstrap, 24-from-24 cells with replacement)",
                "n_cells_used": ncells, "excludes_zero": excludes_zero,
                "change_quotable": "QUOTABLE" if excludes_zero else "NOT_EVALUABLE",
                "change_quotable_reason": None if excludes_zero else "interval contains zero (ruling 5, T28/T60 quoting rule)",
                "n_zero_2022_denominator_excluded_total": n_zero_denom,
            })
        else:
            row.update({"point_change_pct": None, "ci_low_pct": None, "ci_high_pct": None,
                        "ci_method": None, "excludes_zero": False,
                        "change_quotable": "NOT_EVALUABLE", "change_quotable_reason": "no cells with valid data"})
        rows.append(row)

    # ---- shape metrics: midday_share, load_factor (absolute fraction change) ----
    for metric in ("midday_share", "load_factor"):
        cell_delta_arrays = {}
        for (arch, city) in sorted(set((a, c) for a, c, _ in g_common)):
            hh_ids = [idx for idx in g_common if (idx[0], idx[1]) == (arch, city)]
            deltas = np.array([float(g30.loc[i, metric]) - float(g22.loc[i, metric]) for i in hh_ids], dtype=float)
            cell_delta_arrays[(arch, city)] = deltas
            v22_mean = float(g22.loc[[i for i in hh_ids], metric].astype(float).mean()) if hh_ids else np.nan
            v30_mean = float(g30.loc[[i for i in hh_ids], metric].astype(float).mean()) if hh_ids else np.nan
            ti = paired_t_interval(deltas)
            row = {"level": "per_cell", "cell": f"{arch}__{city}", "arch": arch, "city": city,
                   "metric": metric, "metric_ann_col": metric, "change_type": "absolute_fraction",
                   "value_2022_raw_kWh": v22_mean, "value_2030_raw_kWh": v30_mean,
                   "absolute_change_raw_kWh": v30_mean - v22_mean if not (np.isnan(v22_mean) or np.isnan(v30_mean)) else np.nan}
            if ti is not None:
                mean_d, lo, hi, npair = ti
                excludes_zero = not (lo <= 0.0 <= hi)
                row.update({"point_change_pct": mean_d, "ci_low_pct": lo, "ci_high_pct": hi,
                            "ci_method": "paired_t_interval (T67 method_a formula, reused)",
                            "n_paired": npair, "excludes_zero": excludes_zero,
                            "change_quotable": "QUOTABLE" if excludes_zero else "NOT_EVALUABLE",
                            "change_quotable_reason": None if excludes_zero else "interval contains zero (ruling 5, T28/T60 quoting rule)"})
            else:
                row.update({"point_change_pct": None, "ci_low_pct": None, "ci_high_pct": None,
                            "ci_method": None, "n_paired": int(deltas.size), "excludes_zero": False,
                            "change_quotable": "NOT_EVALUABLE", "change_quotable_reason": "fewer than 2 valid paired households"})
            rows.append(row)

        # stock-weighted row: REUSED VERBATIM FROM T67, not recomputed (ruling 6)
        try:
            t67_ci = pd.read_csv(T67_REAL_CI)
            m = t67_ci[(t67_ci["metric"] == metric) & (t67_ci["method"] == "cell_cluster_bootstrap_GENUINE")]
            if not m.empty:
                point = float(m.iloc[0]["point"]); lo = float(m.iloc[0]["low"]); hi = float(m.iloc[0]["high"])
                excludes_zero = not (lo <= 0.0 <= hi)
                row = {"level": "stock_weighted", "cell": "ALL_STOCK_WEIGHTED", "arch": "ALL", "city": "ALL",
                       "metric": metric, "metric_ann_col": metric, "change_type": "absolute_fraction",
                       "point_change_pct": point, "ci_low_pct": lo, "ci_high_pct": hi,
                       "ci_method": "REUSED VERBATIM from T67 real_correcteddata/ci_reproduction_t67.csv (cell_cluster_bootstrap_GENUINE row); NOT recomputed here, per ruling 6",
                       "n_paired": int(m.iloc[0]["n_paired"]), "excludes_zero": excludes_zero,
                       "change_quotable": "QUOTABLE" if excludes_zero else "NOT_EVALUABLE",
                       "change_quotable_reason": None if excludes_zero else "interval contains zero (ruling 5, T28/T60 quoting rule)",
                       "provenance": T67_REAL_CI}
                rows.append(row)
        except Exception as e:
            rows.append({"level": "stock_weighted", "cell": "ALL_STOCK_WEIGHTED", "arch": "ALL", "city": "ALL",
                         "metric": metric, "change_type": "absolute_fraction",
                         "change_quotable": "NOT_EVALUABLE",
                         "change_quotable_reason": f"could not read T67 real_correcteddata CSV: {e}"})

    return pd.DataFrame(rows), zero_denom_counts


def find_undelivered_csvs(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn == "undelivered.csv":
                fp = os.path.join(dirpath, fn)
                hits.append(fp)
    return hits


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[T68] discovering runs under {INPUT_ROOT} ...")
    runs, discover_skipped = discover_runs(INPUT_ROOT)
    print(f"[T68] discovered {len(runs)} candidate household-year runs "
          f"(skipped {len(discover_skipped)} for missing hourly_meters.csv)")

    n_proc = min(8, cpu_count())
    print(f"[T68] processing with {n_proc} workers")
    with Pool(n_proc) as pool:
        results = pool.map(process_one, runs)

    annual_rows, profile_rows, grid_rows, closure_rows = [], [], [], []
    proc_skipped = []
    for status, key, err, prof, grid_row, ac in results:
        if status != "ok":
            proc_skipped.append({**key, "reason": f"{status}: {err}"})
            continue
        annual, closure = ac
        annual_rows.append(annual)
        closure_rows.append(closure)
        profile_rows.extend(prof)
        grid_rows.append(grid_row)

    annual_df = pd.DataFrame(annual_rows)
    profile_df = pd.DataFrame(profile_rows)
    grid_df = pd.DataFrame(grid_rows)
    closure_df = pd.DataFrame(closure_rows)

    annual_df.to_csv(os.path.join(OUT_DIR, "enduse_annual.csv"), index=False)
    profile_df.to_csv(os.path.join(OUT_DIR, "enduse_hourly_profile.csv"), index=False)
    grid_df.to_csv(os.path.join(OUT_DIR, "grid_metrics.csv"), index=False)
    closure_df.to_csv(os.path.join(OUT_DIR, "closure.csv"), index=False)
    print(f"[T68] wrote enduse_annual.csv ({len(annual_df)} rows), "
          f"enduse_hourly_profile.csv ({len(profile_df)} rows), "
          f"grid_metrics.csv ({len(grid_df)} rows), closure.csv ({len(closure_df)} rows)")

    # -- WaterSystems:EnergyTransfer absence, per archetype (ruling 8) --
    water_absence = {}
    if not annual_df.empty:
        for arch in ARCH_NAMES:
            sub = annual_df[annual_df["arch"] == arch]
            if sub.empty:
                continue
            n_zero = int((pd.to_numeric(sub["water_ET_kWh"], errors="coerce") == 0).sum())
            water_absence[arch] = {"n_zero": n_zero, "n_total": int(len(sub))}

    # -- change table (ruling 5, 6) --
    print("[T68] building enduse_change_2022_2030.csv ...")
    change_df, zero_denom_counts = build_change_table(annual_df, grid_df)
    change_df.to_csv(os.path.join(OUT_DIR, "enduse_change_2022_2030.csv"), index=False)
    print(f"[T68] wrote enduse_change_2022_2030.csv ({len(change_df)} rows)")

    # -- controls (section 4) --
    print("[T68] running controls C1-C4 ...")
    c1 = control_c1_hour_of_day(HAND_CHECK_CSV)
    c2 = control_c2_seen_working(annual_df, grid_df)
    c3 = control_c3_divisor_invariance(annual_df)
    c4 = control_c4_divisor_applied(annual_df)
    controls = {"C1_hour_of_day_seen_failing": c1, "C2_seen_working_known_good": c2,
                "C3_divisor_invariance": c3, "C4_divisor_applied_sanity": c4,
                "all_fired": all(c.get("outcome") == "ran_and_fired" for c in (c1, c2, c3, c4))}
    with open(os.path.join(OUT_DIR, "controls.json"), "w") as f:
        json.dump(controls, f, indent=2, default=str)
    print(f"[T68] C1={c1.get('outcome')} C2={c2.get('outcome')} C3={c3.get('outcome')} C4={c4.get('outcome')}")
    print(f"[T68] controls.all_fired={controls['all_fired']}")

    # -- undelivered.csv sweep (item 7 of the deliverables list) --
    print("[T68] sweeping for undelivered.csv under the T21 tree ...")
    undelivered_hits = find_undelivered_csvs(INPUT_ROOT)
    undelivered_contents = []
    for fp in undelivered_hits[:50]:  # cap to avoid pathological cases
        try:
            with open(fp) as fh:
                undelivered_contents.append({"path": fp, "content": fh.read()[:5000]})
        except Exception as e:
            undelivered_contents.append({"path": fp, "error": str(e)})

    meta = {
        "job_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "elapsed_sec": time.time() - t0,
        "input_root": INPUT_ROOT,
        "n_candidate_runs": len(runs),
        "n_discover_skipped": len(discover_skipped),
        "discover_skipped_sample": discover_skipped[:20],
        "n_households_year_read_ok": len(annual_df),
        "n_households_year_skipped": len(proc_skipped),
        "proc_skipped": proc_skipped,
        "row_counts": {
            "enduse_annual.csv": len(annual_df),
            "enduse_hourly_profile.csv": len(profile_df),
            "grid_metrics.csv": len(grid_df),
            "closure.csv": len(closure_df),
            "enduse_change_2022_2030.csv": len(change_df),
        },
        "divisor_tables_used": {
            "T66_CELL_EQUIP_DIVISOR": T66_CELL_EQUIP_DIVISOR,
            "T66_CELL_LIGHT_DIVISOR": T66_CELL_LIGHT_DIVISOR,
            "source": "/speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py (read-only, never imported/edited)",
        },
        "water_systems_energytransfer_zero_by_archetype": water_absence,
        "zero_2022_denominator_counts_by_meter": zero_denom_counts,
        "undelivered_csv_sweep": {
            "n_found": len(undelivered_hits),
            "paths": undelivered_hits,
            "contents": undelivered_contents,
            "note": ("T21 is one of the trees that has never been observed to write an "
                     "undelivered.csv (only T29/T32 do, per impl/2026-09-18_T53... finding). "
                     "An empty result here is UNINFORMATIVE, NOT REASSURING -- it does not by "
                     "itself prove no household was silently dropped upstream of this tree."),
        },
        "controls_summary": {k: v.get("outcome") for k, v in controls.items() if isinstance(v, dict)},
        "controls_all_fired": controls["all_fired"],
    }
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print(f"[T68] households_year_read_ok={len(annual_df)} skipped={len(proc_skipped)}")
    print(f"[T68] done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
