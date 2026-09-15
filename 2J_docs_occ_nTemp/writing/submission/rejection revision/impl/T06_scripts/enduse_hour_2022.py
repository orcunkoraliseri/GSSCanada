#!/usr/bin/env python3
"""
T06 -- WP6 on 2022: end use x hour of day.
Task doc: 2J_docs_occ_nTemp/writing/submission/rejection revision/impl/2026-09-15_T06_wp6_enduse_by_hour_2022.md

Reads the Step-8 campaign's 2022 hourly meter CSVs (1,200 households: 4 archetypes x 6 cities x 50),
uploaded to /speed-scratch/o_iseri/2J_revision/T06/input/ as campaign_N50/<cell>/sample_NNN_HHxxx/2022/hourly_meters.csv
plus each cell's cell_manifest.csv and cell_manifest.csv.new_2022_2030_* (same directory structure
as the local BEM_Setup/SimResults_Step8/campaign_N50 tree).

Meter rules, discover_runs / manifest-merge logic, weekday rule, MIDDAY window, load_factor,
midday_share and circular-mean-hour formulas are taken verbatim from
2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py (this file's own header cites the exact lines):
  - meters indexed BY NAME, not column order            (08_simulation_plots.py:79-91)
  - Electricity:Facility already includes lights+equip+fan, never add them to it (same lines)
  - *:EnergyTransfer meters are thermal loads, never summed into electricity     (same lines)
  - manifest merge (orig + new_2022_2030, keyed by (sample,hh), new wins) and
    is_new_sample gate for year in (2022,2030)            (08_simulation_plots.py:154-234)
  - Jan 1 = Sunday weekday/weekend rule                    (08_simulation_plots.py:128-131,
    itself "verbatim from reporting.py:302-310")
  - stock weighting: per-archetype STOCK_WEIGHTS split equally over the (up to 6) cities
    (08_simulation_plots.py:74-77, 300-321)
  - MIDDAY window = (9, 17)                                 (08_simulation_plots.py:114)
  - load_factor = mean(facility kW) / max(facility kW)      (08_simulation_plots.py:383-385)
  - midday_share = sum(facility kW, hours 9-17) / sum(facility kW) (08_simulation_plots.py:387)
  - circular mean/sd of hour-of-day                          (08_simulation_plots.py:278-297)

Grid metrics NOT in 08_simulation_plots.py, defined here per the T06 task doc step 2c:
  - evening ramp 14:00 -> 17:00 = facility kW(17) - facility kW(14), annual mean daily ramp
  - hours above the household's own 90th percentile = count of hourly facility kW values (8760)
    that exceed that household's own annual 90th percentile of hourly facility kW
"""
import os
import re
import glob
import json
import time
import traceback
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

INPUT_ROOT = "/speed-scratch/o_iseri/2J_revision/T06/input/campaign_N50"
OUT_DIR = "/speed-scratch/o_iseri/2J_revision/T06/out"

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
THERMAL_METERS = [M_HEAT, M_COOL, M_WATER]
ANN_COL = {FACILITY: "elec_facility_kWh", M_LIGHTS: "lights_kWh", M_EQUIP: "equip_kWh",
           M_FAN: "fan_kWh", M_HEAT: "heating_ET_kWh", M_COOL: "cooling_ET_kWh",
           M_WATER: "water_ET_kWh"}

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


def load_cell_manifest(cell_dir):
    """Merge cell_manifest.csv ('orig') with cell_manifest.csv.new_2022_2030_* ('new_2022_2030',
    takes priority), keyed by (sample, sim_hh_id). Verbatim logic from
    08_simulation_plots.py:154-186."""
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


def discover_2022_runs(results_dir):
    """Same gate as 08_simulation_plots.py:discover_runs, restricted to year='2022':
    a sample_NNN_HHxxx/2022/ dir only counts if (sample, hh) matches a 'new_2022_2030' manifest
    row (the post-refresh P1 fresh-sampling manifest, 2026-07-10/11)."""
    runs = []
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
            is_new_sample = meta.get("source") == "new_2022_2030"
            if not is_new_sample:
                continue
            ydir = os.path.join(samp_dir, "2022")
            csv = os.path.join(ydir, "hourly_meters.csv")
            if not os.path.exists(csv):
                continue
            runs.append({
                "arch": arch, "city": city, "region": CITY_REGION[city],
                "sample": sample_from_dir, "sim_hh_id": str(hh_from_dir),
                "hhsize": meta.get("hhsize", ""), "cell": cell_name, "csv_path": csv,
            })
    return runs


def process_one(rm):
    """One household's 2022 hourly_meters.csv -> annual dict, hourly-profile rows, grid-metrics
    dict, closure dict. Returns (status, annual_row, profile_rows, grid_row, closure_row)."""
    key = {"cell": rm["cell"], "arch": rm["arch"], "city": rm["city"], "region": rm["region"],
           "sample": rm["sample"], "sim_hh_id": rm["sim_hh_id"], "hhsize": rm["hhsize"]}
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

    # -- (a) annual kWh per end use --
    annual = dict(key)
    for meter in KEEP_METERS:
        annual[ANN_COL[meter]] = float(meter_2d[meter].sum()) if meter in meter_2d else np.nan

    # -- (d) closure check: lights+equip+fans vs Electricity:Facility --
    closure = dict(key)
    if all(m in meter_2d for m in ELEC_COMPONENTS) and FACILITY in meter_2d:
        comp_sum = sum(meter_2d[m].sum() for m in ELEC_COMPONENTS)
        fac_sum = meter_2d[FACILITY].sum()
        closure["components_kWh"] = float(comp_sum)
        closure["facility_kWh"] = float(fac_sum)
        closure["diff_kWh"] = float(comp_sum - fac_sum)
        closure["pct_diff"] = float(100.0 * (comp_sum - fac_sum) / fac_sum) if fac_sum else np.nan
    else:
        closure["components_kWh"] = closure["facility_kWh"] = np.nan
        closure["diff_kWh"] = closure["pct_diff"] = np.nan

    # -- (b) mean 24-h profile per end use, weekday/weekend, all-year/heating/cooling season --
    profile_rows = []
    for meter in KEEP_METERS:
        if meter not in meter_2d:
            continue
        grid = meter_2d[meter]
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

    # -- (c) grid-facing metrics on Electricity:Facility --
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
        # evening ramp 14:00 -> 17:00, mean over 365 days
        ramp = fac[:, 17] - fac[:, 14]
        grid_row["evening_ramp_kW_mean"] = float(ramp.mean())
        grid_row["evening_ramp_kW_p90"] = float(np.percentile(ramp, 90))
        # hours above the household's OWN 90th percentile of hourly facility kW
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


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[T06] discovering 2022 runs under {INPUT_ROOT} ...")
    runs = discover_2022_runs(INPUT_ROOT)
    print(f"[T06] discovered {len(runs)} candidate 2022 household runs")

    n_proc = min(8, cpu_count())
    print(f"[T06] processing with {n_proc} workers")
    with Pool(n_proc) as pool:
        results = pool.map(process_one, runs)

    annual_rows, profile_rows, grid_rows, closure_rows = [], [], [], []
    skipped = []
    for status, key, err, prof, grid_row, ac in results:
        if status != "ok":
            skipped.append({**key, "reason": f"{status}: {err}"})
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

    # -- archetype-level (then stock-weighted, split equally over 6 cities) summary,
    # appended into enduse_annual.csv-adjacent aggregate for convenience --
    if not annual_df.empty:
        per_arch = annual_df.groupby("arch")[[ANN_COL[m] for m in KEEP_METERS]].mean()
        stock_row = {}
        for col in per_arch.columns:
            acc = 0.0
            for arch in ARCH_NAMES:
                if arch in per_arch.index:
                    acc += STOCK_WEIGHTS.get(arch, 0.0) * per_arch.loc[arch, col]
            stock_row[col] = acc
        with open(os.path.join(OUT_DIR, "enduse_stock_weighted_2022.json"), "w") as f:
            json.dump({"per_archetype_mean_kWh": per_arch.to_dict(orient="index"),
                       "stock_weighted_kWh": stock_row,
                       "stock_weights": STOCK_WEIGHTS}, f, indent=2)

    closure_ok = np.nan
    closure_by_arch = None
    if not closure_df.empty:
        closure_ok = float((closure_df["pct_diff"].abs() <= 0.07).mean())
        closure_by_arch = (closure_df.groupby("arch")["pct_diff"]
                            .agg(["mean", "median", "std", "min", "max", "count"])
                            .to_dict(orient="index"))

    meta = {
        "job_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "elapsed_sec": time.time() - t0,
        "input_root": INPUT_ROOT,
        "n_candidate_runs": len(runs),
        "n_households_read_ok": len(annual_df),
        "n_households_skipped": len(skipped),
        "skipped": skipped,
        "row_counts": {
            "enduse_annual.csv": len(annual_df),
            "enduse_hourly_profile.csv": len(profile_df),
            "grid_metrics.csv": len(grid_df),
            "closure.csv": len(closure_df),
        },
        "closure_fraction_within_0.07pct": closure_ok,
        "closure_pct_diff_summary": (closure_df["pct_diff"].describe().to_dict()
                                      if not closure_df.empty else None),
        "closure_pct_diff_by_archetype": closure_by_arch,
    }
    with open(os.path.join(OUT_DIR, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print(f"[T06] households_read_ok={len(annual_df)} skipped={len(skipped)} "
          f"closure_within_0.07pct_fraction={closure_ok}")
    print(f"[T06] done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
