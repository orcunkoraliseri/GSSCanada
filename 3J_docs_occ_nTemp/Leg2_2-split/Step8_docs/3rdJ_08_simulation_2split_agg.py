#!/usr/bin/env python3
"""3rdJ_08_simulation_2split_agg.py — Step 8D: two-channel EUI / load-shape aggregation.

Two-pass "summarize-on-read" (ported from 2J `08_simulation_plots.py`), generalised to
BOTH campaign channels of the 3J Leg-2 two-channel campaign:

  RESIDENTIAL  campaign/<arch>__<city>/sample_NNN_HH<id>/<scenario>/hourly_meters.csv
  OFFICE       office/<arch>__<envelope>__<cz>/<scenario>/hourly_meters.csv

Pass 1 (this script): stream every run's 8760-h hourly_meters.csv, reduce to compact
per-run rows, read annual EUI from the retained eplusout.sql, and persist:
    outputs_step8/agg/{agg_diurnal,agg_peak,agg_annual,agg_meta}.csv

Pass 2 (the validator, 3rdJ_08_simulation_2split_val.py §4/§5/§7): reads ONLY these small
agg tables — no second heavy scan of the campaign.

Every agg table carries a `channel` (resid|office) column and uses `scenario` (7 labels)
in place of 2J's `year`. Residential meters port verbatim from 2J (identical CSV header).
Office CSVs are wide per-zone `<ZONE> ZN:Zone <var> [J]` — summed by regex to a facility-
equivalent electricity series plus a total occupant-count series (AT_WORK round-trip).

Usage (from Step8_docs/ ; on Speed submit via run_aggregation.sh):
    py 3rdJ_08_simulation_2split_agg.py [--camp DIR] [--office DIR] [--out DIR] [--rebuild]

Env overrides (set by the SLURM wrapper): STEP8_CAMP_DIR, STEP8_OFFICE_DIR.

2026-07-01 built (Step 8D).
"""
from __future__ import annotations
import os
import re
import sys
import argparse
import sqlite3
import warnings

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Reusable pure helpers from the engine copy (plotting.py has no intra-package imports).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))          # .../Step8_docs
try:
    from eSim_bem_utils_3J import plotting as _plotting
except Exception as _e:                                                 # pragma: no cover
    _plotting = None
    warnings.warn(f"Could not import eSim_bem_utils_3J.plotting ({_e}); EUI will be NaN.")

# ---------------------------------------------------------------------------
# CONFIG — kept in lock-step with 3rdJ_08_simulation_2split_val.py
# ---------------------------------------------------------------------------
HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "outputs_step8")
AGG_DIR = os.path.join(OUT_DIR, "agg")

CAMP_DEFAULT   = os.environ.get("STEP8_CAMP_DIR")   or os.path.join(OUT_DIR, "campaign_N50")
OFFICE_DEFAULT = os.environ.get("STEP8_OFFICE_DIR") or os.path.join(OUT_DIR, "office")

SCENARIOS = ["2005", "2010", "2015", "2022",
             "2030-conservative", "2030-hybrid", "2030-fullyhybrid"]

ARCHETYPES_RESID  = ["SingleD", "MidRise", "OtherDwelling", "HighRise"]
ARCHETYPES_OFFICE = ["Office_Knowledge", "Office_Public", "Office_Sales"]
ENVELOPES = ["Tall", "SuperTall"]
CZ_LIST   = ["5A", "5B", "5C", "6A", "6B", "7A"]
CITY_REGION = {
    "Toronto_5A": "Ontario", "Kelowna_5B": "BC", "Vancouver_5C": "BC",
    "Montreal_6A": "Quebec", "Calgary_6B": "Alberta", "Winnipeg_7A": "Prairies",
}

# --- residential meters (BY NAME; column order in hourly_meters.csv is not stable) ---
FACILITY = "Electricity:Facility"          # site electricity TOTAL (incl. lights+equip+fan)
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP  = "InteriorEquipment:Electricity"
M_FAN    = "Fan Electricity Energy"
M_HEAT   = "Heating:EnergyTransfer"        # zone thermal load (NOT delivered fuel)
M_COOL   = "Cooling:EnergyTransfer"
M_WATER  = "WaterSystems:EnergyTransfer"
RESID_METERS = [FACILITY, M_LIGHTS, M_EQUIP, M_FAN, M_HEAT, M_COOL, M_WATER]
_ANN_COL = {FACILITY: "elec_facility_kWh", M_LIGHTS: "lights_kWh", M_EQUIP: "equip_kWh",
            M_FAN: "fan_kWh", M_HEAT: "heating_ET_kWh", M_COOL: "cooling_ET_kWh",
            M_WATER: "water_ET_kWh"}

# --- office wide-schema regexes (per-zone columns, values in J) ---
_OFF_ELEC_RE = re.compile(r"(Lights|Electric Equipment) Electricity Energy", re.IGNORECASE)
_OFF_OCC_RE  = re.compile(r"Zone People Occupant Count", re.IGNORECASE)
_OFF_FAC_RE  = re.compile(r"^\s*Electricity:Facility", re.IGNORECASE)

OFF_ELEC = "office_elec"        # facility-equivalent electricity (kW)
OFF_OCC  = "office_occ"         # total occupant count (persons)

# --- diurnal reduction grid (kept lean; only what the val gates consume) ---
J_PER_KWH = 3.6e6
MIDDAY = (9, 17)                # WFH / core-work window 09:00–17:00
SEASON_WINDOWS = {
    "all":     set(range(1, 366)),
    "heating": set(range(1, 32)),
    "cooling": set(range(182, 213)),
}
SEASONS  = ["all", "heating", "cooling"]
DAYTYPES = ["weekday", "weekend"]


def is_weekend(doy):
    """Jan 1 = Sunday (EnergyPlus default in this pipeline). Verbatim from 2J reporting.py."""
    wd = (doy - 1) % 7
    return wd == 0 or wd == 6


_DOY = np.arange(1, 366)
_WEEKEND = np.array([is_weekend(int(d)) for d in _DOY])
_SEASON_MASK = {s: np.array([int(d) in SEASON_WINDOWS[s] for d in _DOY]) for s in SEASONS}


def _daytype_mask(daytype):
    if daytype == "weekday":
        return ~_WEEKEND
    if daytype == "weekend":
        return _WEEKEND
    return np.ones(365, dtype=bool)


def _circular_mean_hour(hours):
    """Circular mean of hours-of-day (0–23), handling the 23→0 wrap."""
    if len(hours) == 0:
        return np.nan, np.nan, np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    mean_h = (np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0
    return mean_h, s, c


# ---------------------------------------------------------------------------
# DISCOVERY
# ---------------------------------------------------------------------------
_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)


def load_cell_manifest(cell_dir):
    """{sample_int: {sim_hh_id, hhsize, dtype, pr}} or {} if no manifest."""
    path = os.path.join(cell_dir, "cell_manifest.csv")
    if not os.path.exists(path):
        return {}
    try:
        df = pd.read_csv(path, dtype=str)
        out = {}
        for _, r in df.iterrows():
            out[int(r["sample"])] = {
                "sim_hh_id": str(r.get("sim_hh_id", "")),
                "hhsize": r.get("hhsize", ""),
                "dtype": r.get("dtype", ""), "pr": r.get("pr", ""),
            }
        return out
    except Exception:
        return {}


def _scenario_subdirs(parent):
    """Yield (scenario, run_dir) for scenario subdirs that hold a non-empty hourly_meters.csv."""
    for scen in SCENARIOS:
        rd = os.path.join(parent, scen)
        hm = os.path.join(rd, "hourly_meters.csv")
        try:
            if os.path.isdir(rd) and os.path.getsize(hm) > 1000:
                yield scen, rd
        except OSError:
            continue


def discover_resid_runs(camp_dir):
    """Walk the residential campaign generically (samples may hold 1-or-many scenarios)."""
    runs = []
    if not os.path.isdir(camp_dir):
        return runs
    for cell_name in sorted(os.listdir(camp_dir)):
        cell_dir = os.path.join(camp_dir, cell_name)
        if not os.path.isdir(cell_dir) or "__" not in cell_name:
            continue
        arch, _, city = cell_name.partition("__")
        if arch not in ARCHETYPES_RESID or city not in CITY_REGION:
            continue
        cz = city.rsplit("_", 1)[-1]
        manifest = load_cell_manifest(cell_dir)
        for samp_name in sorted(os.listdir(cell_dir)):
            m = _RUN_RE.match(samp_name)
            if not m:
                continue
            samp_dir = os.path.join(cell_dir, samp_name)
            if not os.path.isdir(samp_dir):
                continue
            sample = int(m.group(1))
            meta = manifest.get(sample, {})
            sim_hh_id = meta.get("sim_hh_id") or m.group(2)
            for scen, run_dir in _scenario_subdirs(samp_dir):
                runs.append({
                    "channel": "resid", "arch": arch, "city": city, "cz": cz,
                    "region": CITY_REGION[city], "envelope": "",
                    "sample": sample, "sim_hh_id": str(sim_hh_id),
                    "hhsize": meta.get("hhsize", ""), "scenario": scen,
                    "cell": cell_name, "run_dir": run_dir,
                })
    return runs


def discover_office_runs(office_dir):
    """Walk the office campaign: flat <arch>__<envelope>__<cz>/<scenario>/ (no MC samples)."""
    runs = []
    if not os.path.isdir(office_dir):
        return runs
    for cell_name in sorted(os.listdir(office_dir)):
        cell_dir = os.path.join(office_dir, cell_name)
        if not os.path.isdir(cell_dir):
            continue
        toks = cell_name.split("__")
        if len(toks) != 3:
            continue
        arch, envelope, cz = toks
        if arch not in ARCHETYPES_OFFICE or envelope not in ENVELOPES or cz not in CZ_LIST:
            continue
        for scen, run_dir in _scenario_subdirs(cell_dir):
            runs.append({
                "channel": "office", "arch": arch, "city": "", "cz": cz,
                "region": "", "envelope": envelope,
                "sample": "", "sim_hh_id": "", "hhsize": "",
                "scenario": scen, "cell": cell_name, "run_dir": run_dir,
            })
    return runs


# ---------------------------------------------------------------------------
# HOURLY READERS  (both return an (8760+, n) DataFrame with named series in J,
# except OFF_OCC which is a persons count)
# ---------------------------------------------------------------------------
def load_resid_hourly(run_dir):
    csv = os.path.join(run_dir, "hourly_meters.csv")
    if not os.path.exists(csv):
        return None
    try:
        return pd.read_csv(csv)
    except Exception:
        return None


def load_office_hourly(run_dir):
    """Collapse the wide per-zone office CSV to OFF_ELEC (J/h) + OFF_OCC (persons)."""
    csv = os.path.join(run_dir, "hourly_meters.csv")
    if not os.path.exists(csv):
        return None
    try:
        raw = pd.read_csv(csv)
    except Exception:
        return None
    cols = list(raw.columns)
    fac = [c for c in cols if _OFF_FAC_RE.search(c)]
    if fac:                                            # true facility total if E+ wrote one
        elec = pd.to_numeric(raw[fac[0]], errors="coerce").to_numpy()
    else:                                              # else sum zone lights + equipment
        elec_cols = [c for c in cols if _OFF_ELEC_RE.search(c)]
        if not elec_cols:
            return None
        elec = pd.to_numeric(raw[elec_cols].stack(), errors="coerce") \
                 .groupby(level=0).sum().reindex(range(len(raw))).to_numpy()
    occ_cols = [c for c in cols if _OFF_OCC_RE.search(c)]
    if occ_cols:
        occ = pd.to_numeric(raw[occ_cols].stack(), errors="coerce") \
                .groupby(level=0).sum().reindex(range(len(raw))).to_numpy()
    else:
        occ = np.full(len(raw), np.nan)
    return pd.DataFrame({OFF_ELEC: elec, OFF_OCC: occ})


def _eui_from_sql(run_dir):
    """(conditioned_floor_area_m2, eui_kWh_m2, total_energy_kWh) via calculate_eui, or NaNs."""
    sql = os.path.join(run_dir, "eplusout.sql")
    if _plotting is None or not os.path.exists(sql):
        return np.nan, np.nan, np.nan
    try:
        conn = sqlite3.connect(sql)
        eui = _plotting.calculate_eui(conn)
        conn.close()
        area = eui.get("conditioned_floor_area") or eui.get("total_floor_area") or np.nan
        return (float(area) if area else np.nan,
                float(eui.get("eui", np.nan)),
                float(eui.get("total_energy", np.nan)))
    except Exception:
        return np.nan, np.nan, np.nan


# ---------------------------------------------------------------------------
# SUMMARISE ONE RUN
# ---------------------------------------------------------------------------
_KEY_COLS = ["channel", "arch", "city", "cz", "region", "envelope",
             "sample", "sim_hh_id", "scenario", "cell"]


def _key(rm):
    return {k: rm.get(k, "") for k in _KEY_COLS}


def _to_grid(series_J, energy=True):
    """(>=8760,) J/h (or persons) -> (365,24) kW (or persons). None if too short."""
    arr = pd.to_numeric(pd.Series(series_J), errors="coerce").to_numpy()
    if arr.shape[0] < 8760:
        return None
    arr = arr[:8760]
    if energy:
        arr = arr / J_PER_KWH                          # J/h -> average kW over the hour
    return arr.reshape(365, 24)


def _diurnal_rows(key, meter, grid, unit):
    rows = []
    for season in SEASONS:
        for daytype in DAYTYPES:
            mask = _SEASON_MASK[season] & _daytype_mask(daytype)
            days = np.where(mask)[0]
            if days.size == 0:
                continue
            prof = np.nanmean(grid[days], axis=0)
            for h in range(24):
                rows.append({**key, "meter": meter, "season": season, "daytype": daytype,
                             "hour": h, "value": float(prof[h]), "unit": unit,
                             "n_days": int(days.size)})
    return rows


def _peak_and_shape(key, grid):
    """Peak row + load-shape scalars on a (365,24) kW grid."""
    flat = grid.reshape(-1)
    daily_peak = grid.max(axis=1)
    daily_peak_hr = grid.argmax(axis=1)
    amax = int(np.nanargmax(flat))
    mean_h, ssin, ccos = _circular_mean_hour(daily_peak_hr)
    peak_row = {**key,
                "peak_kW_annual": float(np.nanmax(flat)),
                "peak_hour_annual": amax % 24,
                "peak_doy_annual": amax // 24 + 1,
                "mean_daily_peak_kW": float(np.nanmean(daily_peak)),
                "mean_peak_hour": float(mean_h),
                "peak_hour_sin": float(ssin), "peak_hour_cos": float(ccos)}
    mean24, max24, tot = float(np.nanmean(grid)), float(np.nanmax(flat)), float(np.nansum(grid))
    shape = {
        "load_factor": mean24 / max24 if max24 else np.nan,
        "peak_to_avg": max24 / mean24 if mean24 else np.nan,
        "midday_share": float(grid[:, MIDDAY[0]:MIDDAY[1]].sum() / tot) if tot else np.nan,
        "mean_peak_hour": float(mean_h),
    }
    return peak_row, shape


def summarize_resid_run(rm, df):
    key = _key(rm)
    n = 0 if df is None else len(df)
    meta = {**key, "run_dir": rm["run_dir"], "has_hourly": df is not None,
            "n_hours": n, "status": "ok"}
    if df is None or n < 8760:
        meta["status"] = "missing" if df is None else "short"
        return [], None, None, meta

    diurnal, grids = [], {}
    for meter in RESID_METERS:
        if meter not in df.columns:
            continue
        grids[meter] = _to_grid(df[meter], energy=True)
    fac = grids.get(FACILITY)
    if fac is not None:                                # diurnal only on the facility load
        diurnal += _diurnal_rows(key, FACILITY, fac, "kW")

    annual = {**key, "hhsize": rm.get("hhsize", "")}
    for meter in RESID_METERS:
        g = grids.get(meter)
        annual[_ANN_COL[meter]] = float(np.nansum(g)) if g is not None else np.nan
    area, eui, tot_e = _eui_from_sql(rm["run_dir"])
    annual.update(conditioned_floor_area_m2=area, eui_kWh_m2=eui, total_energy_kWh=tot_e,
                  elec_total_kWh=annual.get("elec_facility_kWh", np.nan),
                  occ_peak_persons=np.nan, occ_mean_persons=np.nan, occ_midday_persons=np.nan)
    peak_row = None
    if fac is not None:
        peak_row, shape = _peak_and_shape(key, fac)
        annual.update(shape)
    else:
        annual.update(load_factor=np.nan, peak_to_avg=np.nan,
                      midday_share=np.nan, mean_peak_hour=np.nan)
    return diurnal, peak_row, annual, meta


def summarize_office_run(rm, df):
    key = _key(rm)
    n = 0 if df is None else len(df)
    meta = {**key, "run_dir": rm["run_dir"], "has_hourly": df is not None,
            "n_hours": n, "status": "ok"}
    if df is None or n < 8760:
        meta["status"] = "missing" if df is None else "short"
        return [], None, None, meta

    elec = _to_grid(df[OFF_ELEC], energy=True) if OFF_ELEC in df.columns else None
    occ  = _to_grid(df[OFF_OCC],  energy=False) if OFF_OCC  in df.columns else None
    diurnal = []
    if elec is not None:
        diurnal += _diurnal_rows(key, OFF_ELEC, elec, "kW")
    if occ is not None:
        diurnal += _diurnal_rows(key, OFF_OCC, occ, "persons")

    annual = {**key, "hhsize": ""}
    for c in _ANN_COL.values():                        # keep a uniform annual schema
        annual[c] = np.nan
    annual["elec_facility_kWh"] = float(np.nansum(elec)) if elec is not None else np.nan
    annual["elec_total_kWh"] = annual["elec_facility_kWh"]
    area, eui, tot_e = _eui_from_sql(rm["run_dir"])
    annual.update(conditioned_floor_area_m2=area, eui_kWh_m2=eui, total_energy_kWh=tot_e)
    if occ is not None:
        wd = _daytype_mask("weekday")
        occ_wd = occ[np.where(wd)[0]]
        annual.update(
            occ_peak_persons=float(np.nanmax(occ)),
            occ_mean_persons=float(np.nanmean(occ)),
            occ_midday_persons=float(np.nanmean(occ_wd[:, MIDDAY[0]:MIDDAY[1]])),
        )
    else:
        annual.update(occ_peak_persons=np.nan, occ_mean_persons=np.nan,
                      occ_midday_persons=np.nan)
    peak_row = None
    if elec is not None:
        peak_row, shape = _peak_and_shape(key, elec)
        annual.update(shape)
    else:
        annual.update(load_factor=np.nan, peak_to_avg=np.nan,
                      midday_share=np.nan, mean_peak_hour=np.nan)
    return diurnal, peak_row, annual, meta


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
AGG_FILES = {"diurnal": "agg_diurnal.csv", "peak": "agg_peak.csv",
             "annual": "agg_annual.csv", "meta": "agg_meta.csv"}


def build_agg_tables(camp_dir, office_dir, out_dir):
    os.makedirs(os.path.join(out_dir, "agg"), exist_ok=True)
    agg_dir = os.path.join(out_dir, "agg")

    resid = discover_resid_runs(camp_dir)
    office = discover_office_runs(office_dir)
    print(f"[agg] discovered {len(resid)} resid + {len(office)} office runs", flush=True)

    diurnal, peak, annual, meta = [], [], [], []
    plan = [("resid", resid, load_resid_hourly, summarize_resid_run),
            ("office", office, load_office_hourly, summarize_office_run)]
    for chan, runs, loader, summ in plan:
        for i, rm in enumerate(runs, 1):
            df = loader(rm["run_dir"])
            d, p, a, m = summ(rm, df)
            diurnal += d
            if p:
                peak.append(p)
            if a:
                annual.append(a)
            meta.append(m)
            if i % 200 == 0 or i == len(runs):
                print(f"[agg:{chan}] {i}/{len(runs)}", flush=True)

    tables = {"diurnal": pd.DataFrame(diurnal), "peak": pd.DataFrame(peak),
              "annual": pd.DataFrame(annual), "meta": pd.DataFrame(meta)}
    for k, dfk in tables.items():
        dfk.to_csv(os.path.join(agg_dir, AGG_FILES[k]), index=False)
    n_ok = int((tables["meta"]["status"] == "ok").sum()) if len(tables["meta"]) else 0
    print(f"[agg] wrote {agg_dir} | runs ok={n_ok}/{len(meta)} | "
          f"diurnal={len(diurnal)} peak={len(peak)} annual={len(annual)}", flush=True)
    return tables


def load_agg_tables(out_dir):
    agg_dir = os.path.join(out_dir, "agg")
    return {k: (pd.read_csv(os.path.join(agg_dir, fn))
                if os.path.exists(os.path.join(agg_dir, fn)) else pd.DataFrame())
            for k, fn in AGG_FILES.items()}


def main():
    ap = argparse.ArgumentParser(description="Step 8D two-channel aggregation.")
    ap.add_argument("--camp", default=CAMP_DEFAULT)
    ap.add_argument("--office", default=OFFICE_DEFAULT)
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--rebuild", action="store_true",
                    help="rebuild even if agg tables already exist")
    args = ap.parse_args()

    have = os.path.exists(os.path.join(args.out, "agg", AGG_FILES["meta"]))
    if have and not args.rebuild:
        print(f"[agg] tables already present in {os.path.join(args.out, 'agg')} "
              f"(use --rebuild to refresh); nothing to do.")
        return
    print("=== Step 8D aggregation ===", flush=True)
    print(f"  camp   = {args.camp}", flush=True)
    print(f"  office = {args.office}", flush=True)
    print(f"  out    = {args.out}", flush=True)
    build_agg_tables(args.camp, args.office, args.out)
    print("[done] aggregation complete.", flush=True)


if __name__ == "__main__":
    main()
