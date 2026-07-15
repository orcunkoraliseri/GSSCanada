#!/usr/bin/env python3
"""
08_simulation_plots.py - Step 8 (2nd journal) results-figure generator (Sub-step 8E).

Aggregates the paired Monte-Carlo EnergyPlus outputs (produced by run_paired_mc.py) and
renders the results figures that present the paper's novelty: predicted occupancy
*time-series* -> energy *load shape* and *peak timing*, headlined by the 2022 -> 2030 shift.

Two-pass "summarize-on-read":
  Pass 1 (aggregate): stream each run's hourly_meters.csv (8760 x meters, J), reduce to compact
                      per-(cell,sample,year) summaries, persist to outputs_step8/agg/*.csv.
  Pass 2 (figures):   each plot_figNN() reads only the small agg tables.

Figure catalogue + rationale: 2J_docs_occ_nTemp/08_simulation_plots.md

Run from 2J_docs_occ_nTemp/Step8_docs/ , e.g.:
  py 08_simulation_plots.py --results-dir <..\\..\\BEM_Setup\\SimResults_Step8\\_pilot_N3> --rebuild-agg --figs all
"""
import os
import re
import sys
import glob
import argparse
import sqlite3
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Reusable pure helpers from the engine copy (plotting.py has NO intra-package imports -> safe/light).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from eSim_bem_utils_2J import plotting as _plotting
except Exception as _e:  # pragma: no cover - degrade gracefully
    _plotting = None
    warnings.warn(f"Could not import eSim_bem_utils_2J.plotting ({_e}); EUI/area will be NaN.")

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))            # .../Step8_docs
_J2_DIR   = os.path.dirname(_THIS_DIR)                            # .../2J_docs_occ_nTemp
_REPO     = os.path.dirname(_J2_DIR)                              # .../GSSCanada-main
BEM_SETUP_DIR   = os.path.join(_REPO, "BEM_Setup")
DEFAULT_RESULTS = os.path.join(BEM_SETUP_DIR, "SimResults_Step8")
DEFAULT_OUT     = os.path.join(_J2_DIR, "outputs_step8")
DEFAULT_SCHED   = BEM_SETUP_DIR

# Grid (hardcoded to keep this analysis script decoupled from the E+ runtime stack).
ARCHETYPES = [
    {"name": "SingleD",       "dtype": "SingleD"},
    {"name": "OtherDwelling", "dtype": "OtherDwelling"},
    {"name": "MidRise",       "dtype": "MidRise"},
    {"name": "HighRise",      "dtype": "HighRise"},
]
CITIES = [
    {"name": "Toronto_5A",   "region": "Ontario"},
    {"name": "Kelowna_5B",   "region": "BC"},
    {"name": "Vancouver_5C", "region": "BC"},
    {"name": "Montreal_6A",  "region": "Quebec"},
    {"name": "Calgary_6B",   "region": "Alberta"},
    {"name": "Winnipeg_7A",  "region": "Prairies"},
]
YEARS = ("2005", "2010", "2015", "2022", "2030")
ARCH_NAMES = [a["name"] for a in ARCHETYPES]
ARCH_DTYPE = {a["name"]: a["dtype"] for a in ARCHETYPES}
CITY_REGION = {c["name"]: c["region"] for c in CITIES}
VALID_CELLS = {f"{a['name']}__{c['name']}" for a in ARCHETYPES for c in CITIES}

# Stock weights (renormalized over the 4 modelled archetypes; Movable dropped).
_RAW_STOCK = {"SingleD": 0.529, "MidRise": 0.213, "OtherDwelling": 0.130, "HighRise": 0.128}
_SW_SUM = sum(_RAW_STOCK.values())
STOCK_WEIGHTS = {k: v / _SW_SUM for k, v in _RAW_STOCK.items()}

# Meters indexed BY NAME (column order in hourly_meters.csv is NOT stable across runs).
FACILITY = "Electricity:Facility"           # site electricity TOTAL (already includes lights+equip+fan)
M_LIGHTS = "InteriorLights:Electricity"
M_EQUIP  = "InteriorEquipment:Electricity"
M_FAN    = "Fan Electricity Energy"
M_HEAT   = "Heating:EnergyTransfer"          # thermal zone load (NOT delivered fuel)
M_COOL   = "Cooling:EnergyTransfer"
M_WATER  = "WaterSystems:EnergyTransfer"
KEEP_METERS = [FACILITY, M_LIGHTS, M_EQUIP, M_FAN, M_HEAT, M_COOL, M_WATER]
ELEC_COMPONENTS = [M_LIGHTS, M_EQUIP, M_FAN]     # decomposition only; never summed with FACILITY
THERMAL_METERS  = [M_HEAT, M_COOL, M_WATER]
# Zone-level duplicates of the :Electricity meters -> dropped on read.
DROP_METERS = ["Zone Lights Electricity Energy", "Zone Electric Equipment Electricity Energy"]

ENDUSE_COLOR = {
    FACILITY: "#333333", M_LIGHTS: "#FF7900", M_EQUIP: "#EF2700",
    M_FAN: "#9370DB", M_HEAT: "#8A1100", M_COOL: "#041991", M_WATER: "#00CED1",
}
ENDUSE_LABEL = {
    FACILITY: "Electricity (facility)", M_LIGHTS: "Interior lighting",
    M_EQUIP: "Interior equipment", M_FAN: "Fans",
    M_HEAT: "Heating load (thermal)", M_COOL: "Cooling load (thermal)",
    M_WATER: "Water systems (thermal)",
}

# Step-8 palette (do NOT reuse engine SCENARIO_COLORS: lacks 2030 + wrong hues).
YEAR_STYLE = {
    "2005": dict(color="#BDBDBD", lw=1.3, ls="--", zorder=1),
    "2010": dict(color="#9E9E9E", lw=1.3, ls="--", zorder=1),
    "2015": dict(color="#6E6E6E", lw=1.6, ls="-",  zorder=2),
    "2022": dict(color="#F2A900", lw=2.4, ls="-",  zorder=4),   # amber
    "2030": dict(color="#C8102E", lw=2.9, ls="-",  zorder=5),   # red / bold
}
BAND_ALPHA = 0.18
DELTA_COLOR = "#C8102E"
MIDDAY = (9, 17)                 # WFH window (09:00-17:00)
MIDDAY_SHADE = dict(color="#FFF3CC", alpha=0.45, zorder=0)

# Seasons by day-of-year (1-based). Jan=heating, Jul=cooling, Apr+Oct=shoulder, all=full year.
SEASON_WINDOWS = {
    "all":      set(range(1, 366)),
    "heating":  set(range(1, 32)),
    "shoulder": set(range(91, 121)) | set(range(274, 305)),
    "cooling":  set(range(182, 213)),
}
SEASONS = list(SEASON_WINDOWS.keys())
DAYTYPES = ["all", "weekday", "weekend"]


def is_weekend(doy):
    """Jan 1 = Sunday (EnergyPlus default in this pipeline). Verbatim from reporting.py:302-310."""
    wd = (doy - 1) % 7
    return wd == 0 or wd == 6


# Precomputed day masks (len 365, day-of-year order).
_DOY = np.arange(1, 366)
_WEEKEND = np.array([is_weekend(int(d)) for d in _DOY])
_SEASON_MASK = {s: np.array([int(d) in SEASON_WINDOWS[s] for d in _DOY]) for s in SEASONS}


def _daytype_mask(daytype):
    if daytype == "weekday":
        return ~_WEEKEND
    if daytype == "weekend":
        return _WEEKEND
    return np.ones(365, dtype=bool)


# ---------------------------------------------------------------------------
# AGGREGATION LAYER
# ---------------------------------------------------------------------------
_RUN_RE = re.compile(r"sample_(\d+)_HH(.+)", re.IGNORECASE)


def load_cell_manifest(cell_dir):
    """{(sample, sim_hh_id_str): {hhsize, dtype, pr, source}}, keyed by the exact
    (sample-index, HH-id) PAIR — not by HH id alone — because the post-refresh 2022/2030
    re-sim (P1 fresh sampling, 2026-07-10/11) can redraw a household that was ALSO in the
    original historic sample, but under a DIFFERENT sample index. That produces two
    physically distinct sample_NNN_HHnnnn directories sharing the same HH id (e.g.
    sample_030_HH62718 = original/historic, sample_022_HH62718 = new 2022/2030-only), which
    an HH-id-only key would wrongly conflate. Merges the original cell_manifest.csv
    ("orig") with cell_manifest.csv.new_2022_2030_* ("new_2022_2030") if present.
    """
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


def discover_runs(results_dir):
    """Walk results_dir -> list of run dicts. Ignores non-cell dirs (e.g. plotting scratch)."""
    runs = []
    for cell_name in sorted(os.listdir(results_dir)):
        cell_dir = os.path.join(results_dir, cell_name)
        if not os.path.isdir(cell_dir) or "__" not in cell_name:
            continue
        arch, _, city = cell_name.partition("__")
        if arch not in ARCH_NAMES or city not in CITY_REGION:
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
            sample_from_dir = int(m.group(1))
            hh_from_dir = m.group(2)
            meta = manifest.get((sample_from_dir, str(hh_from_dir)), {})
            sample = sample_from_dir
            is_new_sample = meta.get("source") == "new_2022_2030"
            for year in YEARS:
                ydir = os.path.join(samp_dir, year)
                if not os.path.isdir(ydir):
                    continue
                # 2022/2030 refreshed via P1 fresh sampling (2026-07-10/11): a directory
                # only carries CONFIRMED-fresh 2022/2030 data if its (sample, hh) pair
                # matches the new manifest — otherwise any 2022/2030 folder present is a
                # pre-refresh leftover and must be excluded. Historic years are untouched by
                # the re-sim and always kept when present: a directory can legitimately be
                # BOTH the new-manifest source for 2022/2030 AND still hold valid 2005-2015
                # data, when the fresh resample happens to land on the same (sample, hh)
                # slot as the original run (single directory, updated in place).
                if year in ("2022", "2030") and not is_new_sample:
                    continue
                runs.append({
                    "arch": arch, "city": city, "cz": cz, "region": CITY_REGION[city],
                    "sample": sample, "sim_hh_id": str(hh_from_dir),
                    "hhsize": meta.get("hhsize", ""), "year": year,
                    "run_dir": ydir, "cell": cell_name,
                    "manifest": bool(manifest),
                })
    return runs


def load_run_hourly(run_dir):
    """Return a DataFrame of hourly meters (J) indexed by name, or None. Prefers the CSV."""
    csv = os.path.join(run_dir, "hourly_meters.csv")
    if os.path.exists(csv):
        try:
            df = pd.read_csv(csv)
            return df
        except Exception:
            pass
    sql = os.path.join(run_dir, "eplusout.sql")
    if _plotting is not None and os.path.exists(sql):
        try:
            conn = sqlite3.connect(sql)
            hourly = _plotting.get_hourly_meter_data(conn)
            conn.close()
            if hourly:
                n = max(len(v) for v in hourly.values())
                d = {"hour": list(range(n))}
                for k, v in hourly.items():
                    d[k] = list(v) + [np.nan] * (n - len(v))
                return pd.DataFrame(d)
        except Exception:
            return None
    return None


def _eui_from_sql(run_dir):
    """(conditioned_floor_area_m2, eui_kWh_m2) via reused calculate_eui, or (nan, nan)."""
    sql = os.path.join(run_dir, "eplusout.sql")
    if _plotting is None or not os.path.exists(sql):
        return np.nan, np.nan
    try:
        conn = sqlite3.connect(sql)
        eui = _plotting.calculate_eui(conn)
        conn.close()
        area = eui.get("conditioned_floor_area") or eui.get("total_floor_area") or np.nan
        return float(area) if area else np.nan, float(eui.get("eui", np.nan))
    except Exception:
        return np.nan, np.nan


def _circular_mean_hour(hours):
    """Circular mean of hours-of-day (0-23), handling the 23->0 wrap."""
    if len(hours) == 0:
        return np.nan, np.nan, np.nan
    ang = 2 * np.pi * np.asarray(hours, dtype=float) / 24.0
    s, c = np.sin(ang).mean(), np.cos(ang).mean()
    mean_h = (np.arctan2(s, c) * 24.0 / (2 * np.pi)) % 24.0
    return mean_h, s, c


def _circular_sd_hours(s, c):
    """Circular (angular) standard deviation in hours, from the mean sin/cos returned by
    _circular_mean_hour (Mardia's circular SD = sqrt(-2 ln R), R = resultant vector length).
    Appropriate dispersion measure for hour-of-day data; a plain linear std() is invalid
    once samples split across morning/evening peak modes (23->0 wrap + bimodality)."""
    R = float(np.hypot(s, c))
    if not np.isfinite(R) or R <= 0:
        return np.nan
    R = min(R, 1.0)  # guard tiny float overshoot past 1.0
    return float(np.sqrt(-2.0 * np.log(R)) * 24.0 / (2 * np.pi))


def _stock_weighted_circular_mean(stock_peak_year):
    """National, archetype-stock-weighted circular mean (+ circular SD) of the per-cell TRUE
    stock-aggregate peak hour, for one year's slice of agg['stock_peak'] (one row per cell).
    Each archetype's STOCK_WEIGHTS share is split equally across its (up to 6) cities, then
    per-cell (sin, cos) means are weight-averaged and re-angled -- algebraically identical to
    pooling every city's 365 daily argmax hours (equal per-city day-count) and weighting the
    pooled per-archetype result by STOCK_WEIGHTS, i.e. reproduces the 17.22h/17.02h 2022/2030
    figure already validated ad hoc in this doc's Progress Log (2026-07-15, Task #20 row)."""
    s_acc = c_acc = w_acc = 0.0
    for arch in ARCH_NAMES:
        sub = stock_peak_year[stock_peak_year["arch"] == arch]
        if sub.empty:
            continue
        w_each = STOCK_WEIGHTS.get(arch, 0) / len(sub)
        s_acc += w_each * sub["stock_peak_hour_sin"].sum()
        c_acc += w_each * sub["stock_peak_hour_cos"].sum()
        w_acc += w_each * len(sub)
    if w_acc == 0:
        return np.nan, np.nan
    s_m, c_m = s_acc / w_acc, c_acc / w_acc
    mean_h = (np.arctan2(s_m, c_m) * 24.0 / (2 * np.pi)) % 24.0
    return float(mean_h), _circular_sd_hours(s_m, c_m)


def summarize_run(rm, df):
    """Reduce one run's 8760-h df to compact rows. Returns (diurnal, peak, peak_hours, annual, meta)."""
    key = {k: rm[k] for k in ("arch", "city", "cz", "region", "sample", "sim_hh_id", "year")}
    n = 0 if df is None else len(df)
    meta = {**key, "run_dir": rm["run_dir"], "has_hourly": df is not None,
            "n_hours": n, "status": "ok"}
    if df is None or n < 8760:
        meta["status"] = "missing" if df is None else "short"
        return [], None, [], None, meta

    diurnal_rows, peak_hour_rows = [], []
    # 24-h diurnal mean load (kW) per meter x season x daytype.
    meter_2d = {}      # meter -> (365,24) kW
    for meter in KEEP_METERS:
        if meter not in df.columns:
            continue
        kw = pd.to_numeric(df[meter], errors="coerce").to_numpy()[:8760] / 3.6e6  # J/h -> kW
        grid = kw.reshape(365, 24)
        meter_2d[meter] = grid
        for season in SEASONS:
            for daytype in DAYTYPES:
                mask = _SEASON_MASK[season] & _daytype_mask(daytype)
                days = np.where(mask)[0]
                if days.size == 0:
                    continue
                prof = grid[days].mean(axis=0)
                for h in range(24):
                    diurnal_rows.append({**key, "meter": meter, "season": season,
                                         "daytype": daytype, "hour": h,
                                         "load_kW": float(prof[h]), "n_days": int(days.size)})

    # Peak + load-shape scalars on FACILITY electricity.
    peak_row, annual_row = None, None
    fac = meter_2d.get(FACILITY)
    annual = {**key, "hhsize": rm.get("hhsize", "")}
    for meter in KEEP_METERS:
        if meter in meter_2d:
            annual[_ann_col(meter)] = float(meter_2d[meter].sum())  # kWh/yr (sum of hourly kW)
        else:
            annual[_ann_col(meter)] = np.nan
    area, eui = _eui_from_sql(rm["run_dir"])
    annual["conditioned_floor_area_m2"] = area
    annual["eui_kWh_m2"] = eui
    if fac is not None:
        flat = fac.reshape(-1)
        daily_peak = fac.max(axis=1)            # 365 daily peak kW
        daily_peak_hr = fac.argmax(axis=1)      # 365 daily peak hours
        amax = int(flat.argmax())
        mean_h, ssin, ccos = _circular_mean_hour(daily_peak_hr)
        peak_row = {**key,
                    "peak_kW_annual": float(flat.max()),
                    "peak_hour_annual": amax % 24,
                    "peak_doy_annual": amax // 24 + 1,
                    "mean_daily_peak_kW": float(daily_peak.mean()),
                    "mean_peak_hour": float(mean_h),
                    "peak_hour_sin": float(ssin), "peak_hour_cos": float(ccos)}
        for d0 in range(365):
            peak_hour_rows.append({**key, "doy": d0 + 1, "peak_hour": int(daily_peak_hr[d0]),
                                   "peak_kW": float(daily_peak[d0])})
        mean24 = fac.mean()
        max24 = flat.max()
        annual["load_factor"] = float(mean24 / max24) if max24 else np.nan
        annual["peak_to_avg"] = float(max24 / mean24) if mean24 else np.nan
        annual["midday_share"] = float(fac[:, MIDDAY[0]:MIDDAY[1]].sum() / fac.sum()) if fac.sum() else np.nan
        annual["mean_peak_hour"] = float(mean_h)
    else:
        for c in ("load_factor", "peak_to_avg", "midday_share", "mean_peak_hour"):
            annual[c] = np.nan
    annual_row = annual
    return diurnal_rows, peak_row, peak_hour_rows, annual_row, meta


def _ann_col(meter):
    return {FACILITY: "elec_facility_kWh", M_LIGHTS: "lights_kWh", M_EQUIP: "equip_kWh",
            M_FAN: "fan_kWh", M_HEAT: "heating_ET_kWh", M_COOL: "cooling_ET_kWh",
            M_WATER: "water_ET_kWh"}[meter]


AGG_FILES = {"diurnal": "agg_diurnal.csv", "peak": "agg_peak.csv",
             "peak_hours": "agg_peak_hours.csv", "annual": "agg_annual.csv", "meta": "agg_meta.csv",
             "stock_peak": "agg_stock_peak.csv"}


def _stock_peak_rows(stock_accum):
    """Reduce the (arch, city, year) -> summed-hourly-kW accumulator into one row per
    cell x year: a TRUE stock-aggregate peak-hour statistic (sum all households' hourly kW
    into one building-stock profile, argmax per day, circular-mean the 365 argmax hours) --
    distinct from summarize_run()'s per-household 'mean_peak_hour' (a household-level circular
    mean). See 08_09_injection_bug_status.md Progress Log, 2026-07-15 (Task #21 continuation)."""
    rows = []
    for (arch, city, year), acc in stock_accum.items():
        grid = acc["kw"].reshape(365, 24)
        daily_peak_hr = grid.argmax(axis=1)
        mean_h, ssin, ccos = _circular_mean_hour(daily_peak_hr)
        rows.append({
            "arch": arch, "city": city, "cz": acc["cz"], "region": acc["region"], "year": year,
            "n_hh": acc["n"], "stock_mean_peak_hour": float(mean_h),
            "stock_circ_sd_hours": _circular_sd_hours(ssin, ccos),
            "stock_peak_hour_sin": float(ssin), "stock_peak_hour_cos": float(ccos),
            "stock_evening_frac": float(np.mean((daily_peak_hr >= 15) & (daily_peak_hr <= 21))),
        })
    return rows


def build_agg_tables(results_dir, out_dir):
    """Pass 1: stream all runs, reduce, persist agg/*.csv. Returns dict of DataFrames."""
    agg_dir = os.path.join(out_dir, "agg")
    os.makedirs(agg_dir, exist_ok=True)
    runs = discover_runs(results_dir)
    print(f"[agg] discovered {len(runs)} runs under {results_dir}")
    diurnal, peak, peak_hours, annual, meta = [], [], [], [], []
    # (arch, city, year) -> {"kw": np.zeros(8760), "n": int, "cz":..., "region":...}: running sum
    # of every household's hourly Electricity:Facility kW in this cell/year, built for free off
    # the same `df` each run already reads -- no extra I/O pass. Feeds _stock_peak_rows() below.
    stock_accum = {}
    for i, rm in enumerate(runs, 1):
        df = load_run_hourly(rm["run_dir"])
        d, p, ph, a, m = summarize_run(rm, df)
        diurnal += d
        if p:
            peak.append(p)
        peak_hours += ph
        if a:
            annual.append(a)
        meta.append(m)
        if df is not None and len(df) >= 8760 and FACILITY in df.columns:
            kw = pd.to_numeric(df[FACILITY], errors="coerce").to_numpy()[:8760] / 3.6e6
            key = (rm["arch"], rm["city"], rm["year"])
            acc = stock_accum.setdefault(key, {"kw": np.zeros(8760), "n": 0,
                                                "cz": rm["cz"], "region": rm["region"]})
            acc["kw"] += kw
            acc["n"] += 1
        if i % 50 == 0 or i == len(runs):
            print(f"[agg] {i}/{len(runs)} runs processed")
    tables = {
        "diurnal": pd.DataFrame(diurnal), "peak": pd.DataFrame(peak),
        "peak_hours": pd.DataFrame(peak_hours), "annual": pd.DataFrame(annual),
        "meta": pd.DataFrame(meta), "stock_peak": pd.DataFrame(_stock_peak_rows(stock_accum)),
    }
    for k, df in tables.items():
        df.to_csv(os.path.join(agg_dir, AGG_FILES[k]), index=False)
    n_ok = int((tables["meta"]["status"] == "ok").sum()) if len(tables["meta"]) else 0
    print(f"[agg] wrote {agg_dir} | runs ok={n_ok}/{len(meta)} | "
          f"diurnal rows={len(diurnal)} peak rows={len(peak)} | "
          f"stock_peak cells x years={len(stock_accum)}")
    return tables


def load_agg_tables(out_dir):
    agg_dir = os.path.join(out_dir, "agg")
    tables = {}
    for k, fn in AGG_FILES.items():
        p = os.path.join(agg_dir, fn)
        tables[k] = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
    return tables


# ---------------------------------------------------------------------------
# SHARED PLOT HELPERS
# ---------------------------------------------------------------------------
def _save(fig, out_dir, name):
    fig_dir = os.path.join(out_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    path = os.path.join(fig_dir, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.replace(".png", ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {path}")
    return path


def _mc_band(matrix):
    """matrix: (n_samples, 24) -> (mean24, p5_24, p95_24). Robust to tiny n."""
    a = np.asarray(matrix, dtype=float)
    if a.ndim == 1:
        a = a[None, :]
    mean = np.nanmean(a, axis=0)
    if a.shape[0] >= 3:
        lo, hi = np.nanpercentile(a, 5, axis=0), np.nanpercentile(a, 95, axis=0)
    else:
        lo = hi = mean
    return mean, lo, hi


def _band(ax, x, mean, lo, hi, color, label, lw=2.2, ls="-", zorder=3):
    ax.plot(x, mean, color=color, lw=lw, ls=ls, label=label, zorder=zorder)
    if not np.allclose(lo, hi, equal_nan=True):
        ax.fill_between(x, lo, hi, color=color, alpha=BAND_ALPHA, lw=0, zorder=zorder - 1)


def _year_legend(years):
    return [Line2D([0], [0], color=YEAR_STYLE[y]["color"], lw=YEAR_STYLE[y]["lw"],
                   ls=YEAR_STYLE[y]["ls"], label=y) for y in years if y in YEAR_STYLE]


def _shade_midday(ax):
    ax.axvspan(MIDDAY[0], MIDDAY[1], **MIDDAY_SHADE)


def _diurnal_matrix(diurnal, cell, year, meter, season="all", daytype="all"):
    """Return (n_samples, 24) kW matrix for a cell/year/meter slice."""
    d = diurnal[(diurnal["arch"] + "__" + diurnal["city"] == cell) &
                (diurnal["year"].astype(str) == str(year)) &
                (diurnal["meter"] == meter) & (diurnal["season"] == season) &
                (diurnal["daytype"] == daytype)]
    if d.empty:
        return None
    piv = d.pivot_table(index="sample", columns="hour", values="load_kW")
    piv = piv.reindex(columns=range(24))
    return piv.to_numpy()


def _cells_for_arch(diurnal, arch):
    cells = sorted(set(diurnal[diurnal["arch"] == arch]["arch"] + "__" +
                       diurnal[diurnal["arch"] == arch]["city"]))
    return cells


# ---------------------------------------------------------------------------
# FIGURE LAYER
# ---------------------------------------------------------------------------
def plot_fig01_occupancy(out_dir, sched_dir, dtype="SingleD"):
    """Fig 1 - diurnal AT_HOME occupancy driver from BEM_Schedules (chunked read)."""
    cols = ["Day_Type", "Hour", "Occupancy_Schedule", "DTYPE"]
    curves = {}   # year -> {Day_Type: np.array(24)}
    for year in YEARS:
        path = os.path.join(sched_dir, f"BEM_Schedules_{year}.csv")
        if not os.path.exists(path):
            continue
        acc = {}  # (dt,hr) -> [sum,count]
        for chunk in pd.read_csv(path, usecols=cols, chunksize=1_000_000):
            c = chunk[chunk["DTYPE"] == dtype]
            if c.empty:
                continue
            g = c.groupby(["Day_Type", "Hour"])["Occupancy_Schedule"].agg(["sum", "count"])
            for (dt, hr), row in g.iterrows():
                k = (dt, int(hr))
                s = acc.get(k, [0.0, 0])
                s[0] += row["sum"]; s[1] += row["count"]; acc[k] = s
        out = {}
        for (dt, hr), (s, ct) in acc.items():
            out.setdefault(dt, np.full(24, np.nan))
            if 0 <= hr < 24 and ct:
                out[dt][hr] = s / ct
        curves[year] = out
    if not curves:
        print("[fig01] no BEM_Schedules found; skipped")
        return None
    daytypes = ["Weekday", "Weekend"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, dt in zip(axes, daytypes):
        _shade_midday(ax)
        for year, out in curves.items():
            if dt in out:
                st = YEAR_STYLE.get(year, {})
                ax.plot(range(24), out[dt] * 100, **st)
        ax.set_title(f"{dt} - {dtype}")
        ax.set_xlabel("Hour of day"); ax.set_xlim(0, 23); ax.grid(alpha=0.3)
    axes[0].set_ylabel("At-home fraction (%)")
    axes[0].legend(handles=_year_legend(list(curves.keys())), title="Cycle", fontsize=8)
    fig.suptitle("Fig 1 - Occupancy driver: diurnal at-home shift (mid-day = WFH window)",
                 fontweight="bold")
    return _save(fig, out_dir, "fig01_occupancy_driver.png")


def plot_fig02_diurnal_elec(agg, out_dir, rep_cell):
    """Fig 2 - HEADLINE diurnal electricity load shape, 2022 vs 2030 (+ 2x2 archetypes)."""
    diurnal = agg["diurnal"]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    _shade_midday(ax)
    for year in ("2022", "2030"):
        mat = _diurnal_matrix(diurnal, rep_cell, year, FACILITY)
        if mat is None:
            continue
        mean, lo, hi = _mc_band(mat)
        st = YEAR_STYLE[year]
        _band(ax, range(24), mean, lo, hi, st["color"], year, lw=st["lw"], zorder=st["zorder"])
    ax.set_xlabel("Hour of day"); ax.set_ylabel("Electricity demand (kW)")
    ax.set_xlim(0, 23); ax.set_ylim(bottom=0); ax.grid(alpha=0.3); ax.legend(title="Cycle")
    ax.set_title(f"Fig 2 - Diurnal electricity load: 2022 vs 2030 ({rep_cell})", fontweight="bold")
    p = _save(fig, out_dir, "fig02_diurnal_electricity.png")

    # 2x2 small multiples across archetypes (use each archetype's rep city = rep_cell's city).
    city = rep_cell.split("__", 1)[1]
    fig2, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, arch in zip(axs.ravel(), ARCH_NAMES):
        cell = f"{arch}__{city}"
        _shade_midday(ax)
        any_data = False
        for year in ("2022", "2030"):
            mat = _diurnal_matrix(diurnal, cell, year, FACILITY)
            if mat is None:
                continue
            any_data = True
            mean, lo, hi = _mc_band(mat)
            st = YEAR_STYLE[year]
            _band(ax, range(24), mean, lo, hi, st["color"], year, lw=st["lw"], zorder=st["zorder"])
        ax.set_title(arch + ("" if any_data else " (no data)"))
        ax.set_xlim(0, 23); ax.set_ylim(bottom=0); ax.grid(alpha=0.3)
    for ax in axs[-1]:
        ax.set_xlabel("Hour of day")
    for ax in axs[:, 0]:
        ax.set_ylabel("Electricity (kW)")
    axs[0, 0].legend(title="Cycle", fontsize=8)
    fig2.suptitle(f"Fig 2b - Diurnal electricity by archetype ({city})", fontweight="bold")
    _save(fig2, out_dir, "fig02b_diurnal_electricity_by_archetype.png")
    return p


def plot_fig03_peak_hour(agg, out_dir, rep_cell):
    """Fig 3 - distribution of daily peak hour, 2022 vs 2030 (+ polar mean inset)."""
    ph = agg["peak_hours"]
    if ph.empty:
        print("[fig03] no peak_hours; skipped"); return None
    ph = ph.copy(); ph["cell"] = ph["arch"] + "__" + ph["city"]
    sub = ph[ph["cell"] == rep_cell]
    fig = plt.figure(figsize=(9, 4.8))
    ax = fig.add_subplot(1, 2, 1)
    for year in ("2022", "2030"):
        v = sub[sub["year"].astype(str) == year]["peak_hour"].to_numpy()
        if v.size == 0:
            continue
        st = YEAR_STYLE[year]
        ax.hist(v, bins=np.arange(-0.5, 24.5, 1), histtype="step", density=True,
                color=st["color"], lw=st["lw"], label=year)
    ax.set_xlabel("Hour of daily peak"); ax.set_ylabel("Density"); ax.set_xlim(0, 23)
    ax.grid(alpha=0.3); ax.legend(title="Cycle")
    axp = fig.add_subplot(1, 2, 2, projection="polar")
    for year in ("2022", "2030"):
        v = sub[sub["year"].astype(str) == year]["peak_hour"].to_numpy()
        if v.size == 0:
            continue
        mean_h, _, _ = _circular_mean_hour(v)
        ang = 2 * np.pi * mean_h / 24.0
        axp.annotate("", xy=(ang, 1), xytext=(0, 0),
                     arrowprops=dict(color=YEAR_STYLE[year]["color"], width=2))
    axp.set_theta_zero_location("N"); axp.set_theta_direction(-1)
    axp.set_xticks(np.linspace(0, 2 * np.pi, 24, endpoint=False))
    axp.set_xticklabels([str(h) for h in range(24)], fontsize=6)
    axp.set_yticklabels([]); axp.set_title("Mean peak hour", fontsize=9)
    fig.suptitle(f"Fig 3 - Peak-hour shift ({rep_cell})", fontweight="bold")
    return _save(fig, out_dir, "fig03_peak_hour_shift.png")


def plot_fig04_paired_delta(agg, out_dir, rep_cell):
    """Fig 4 - paired within-HH delta load by hour, 2030 - 2022 (CI ribbon)."""
    diurnal = agg["diurnal"]
    d = diurnal[(diurnal["arch"] + "__" + diurnal["city"] == rep_cell) &
                (diurnal["meter"] == FACILITY) & (diurnal["season"] == "all") &
                (diurnal["daytype"] == "all")]
    if d.empty:
        print("[fig04] no diurnal for rep cell; skipped"); return None
    # "year" comes back int64 when agg tables are loaded from cached CSV (load_agg_tables()),
    # but str when freshly built in-memory (build_agg_tables()) -- cast so the "2022"/"2030"
    # membership check below is dtype-stable regardless of which path populated `agg`.
    d = d.assign(year=d["year"].astype(str))
    piv = d.pivot_table(index=["sim_hh_id", "hour"], columns="year", values="load_kW").reset_index()
    if "2022" not in piv.columns or "2030" not in piv.columns:
        print("[fig04] need both 2022 & 2030; skipped"); return None
    piv = piv.dropna(subset=["2022", "2030"])
    piv["delta"] = piv["2030"] - piv["2022"]
    g = piv.groupby("hour")["delta"]
    mean = g.mean().reindex(range(24))
    n = g.count().reindex(range(24)).fillna(0)
    sd = g.std().reindex(range(24))
    se = sd / np.sqrt(n.replace(0, np.nan))
    ci = 1.96 * se
    fig, ax = plt.subplots(figsize=(8.5, 5))
    _shade_midday(ax)
    ax.axhline(0, color="#888", lw=1)
    ax.plot(range(24), mean.values, color=DELTA_COLOR, lw=2.6, label="mean Δ (2030 − 2022)")
    ax.fill_between(range(24), (mean - ci).values, (mean + ci).values,
                    color=DELTA_COLOR, alpha=BAND_ALPHA, lw=0, label="95% CI")
    ax.set_xlabel("Hour of day"); ax.set_ylabel("Δ electricity demand (kW)")
    ax.set_xlim(0, 23); ax.grid(alpha=0.3); ax.legend()
    ax.set_title(f"Fig 4 - Paired within-household Δ load by hour ({rep_cell})", fontweight="bold")
    return _save(fig, out_dir, "fig04_paired_delta_by_hour.png")


def plot_fig05_diurnal_season(agg, out_dir, rep_cell):
    """Fig 5 - diurnal-by-season small multiples: {heating,shoulder,cooling} x {elec,heat,cool}."""
    diurnal = agg["diurnal"]
    seasons = ["heating", "shoulder", "cooling"]
    meters = [FACILITY, M_HEAT, M_COOL]
    fig, axs = plt.subplots(len(meters), len(seasons), figsize=(13, 9), sharex=True)
    for i, meter in enumerate(meters):
        for j, season in enumerate(seasons):
            ax = axs[i, j]
            for year in ("2022", "2030"):
                mat = _diurnal_matrix(diurnal, rep_cell, year, meter, season=season)
                if mat is None:
                    continue
                mean, lo, hi = _mc_band(mat)
                st = YEAR_STYLE[year]
                _band(ax, range(24), mean, lo, hi, st["color"], year, lw=st["lw"])
            ax.set_xlim(0, 23); ax.set_ylim(bottom=0); ax.grid(alpha=0.3)
            if i == 0:
                ax.set_title(season.capitalize())
            if j == 0:
                ax.set_ylabel(ENDUSE_LABEL[meter].split(" (")[0] + "\n(kW)", fontsize=9)
    for ax in axs[-1]:
        ax.set_xlabel("Hour of day")
    axs[0, 0].legend(handles=_year_legend(["2022", "2030"]), fontsize=8)
    fig.suptitle(f"Fig 5 - Diurnal load by season ({rep_cell}); thermal rows = zone load, not fuel",
                 fontweight="bold")
    return _save(fig, out_dir, "fig05_diurnal_by_season.png")


def plot_fig06_carpet(agg, out_dir, results_dir, rep_cell):
    """Fig 6 - 8760-h carpet (24 x 365) for one representative run, 2022 vs 2030."""
    meta = agg["meta"]
    m = meta[(meta["arch"] + "__" + meta["city"] == rep_cell) & (meta["status"] == "ok")] \
        if not meta.empty else meta
    if m.empty:
        print("[fig06] no ok run for rep cell; skipped"); return None
    sample = sorted(m["sample"].unique())[0]
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    vmax = None
    grids = {}
    for year in ("2022", "2030"):
        row = m[(m["sample"] == sample) & (m["year"].astype(str) == year)]
        if row.empty:
            continue
        df = load_run_hourly(row.iloc[0]["run_dir"])
        if df is None or FACILITY not in df.columns:
            continue
        kw = pd.to_numeric(df[FACILITY], errors="coerce").to_numpy()[:8760] / 3.6e6
        grids[year] = kw.reshape(365, 24).T   # (24, 365)
    if not grids:
        print("[fig06] no facility data; skipped"); return None
    vmax = max(np.nanmax(g) for g in grids.values())
    for ax, year in zip(axs, ("2022", "2030")):
        if year not in grids:
            ax.set_visible(False); continue
        im = ax.pcolormesh(np.arange(1, 366), np.arange(24), grids[year],
                           cmap="viridis", vmin=0, vmax=vmax, shading="auto")
        ax.set_title(year); ax.set_xlabel("Day of year")
        fig.colorbar(im, ax=ax, label="kW")
    axs[0].set_ylabel("Hour of day")
    fig.suptitle(f"Fig 6 - Annual electricity carpet ({rep_cell}, sample {sample})", fontweight="bold")
    return _save(fig, out_dir, "fig06_carpet_8760.png")


def plot_fig07_delta_cz(agg, out_dir):
    """Fig 7 - paired Δ peak-kW by archetype x climate zone (heatmap)."""
    peak = agg["peak"]
    if peak.empty:
        print("[fig07] no peak table; skipped"); return None
    # Same cached-CSV-reload dtype issue as fig04 above (year: int64 from disk vs str
    # in-memory) -- cast before pivoting so the "2022"/"2030" column check is dtype-stable.
    peak = peak.assign(year=peak["year"].astype(str))
    piv = peak.pivot_table(index=["arch", "city", "cz", "sim_hh_id"], columns="year",
                           values="peak_kW_annual").reset_index()
    if "2022" not in piv.columns or "2030" not in piv.columns:
        print("[fig07] need both years; skipped"); return None
    piv = piv.dropna(subset=["2022", "2030"])
    piv["delta"] = piv["2030"] - piv["2022"]
    mat = piv.groupby(["arch", "cz"])["delta"].mean().unstack("cz")
    mat = mat.reindex(index=[a for a in ARCH_NAMES if a in mat.index])
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    vmax = np.nanmax(np.abs(mat.to_numpy())) or 1.0
    im = ax.imshow(mat.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(mat.shape[1])); ax.set_xticklabels(mat.columns)
    ax.set_yticks(range(mat.shape[0])); ax.set_yticklabels(mat.index)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.to_numpy()[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Δ peak kW (2030 − 2022)")
    ax.set_xlabel("Climate zone"); ax.set_ylabel("Archetype")
    ax.set_title("Fig 7 - Paired Δ peak demand by archetype × climate zone", fontweight="bold")
    return _save(fig, out_dir, "fig07_delta_by_cz.png")


def plot_fig08_stock(agg, out_dir):
    """Fig 8 - stock-weighted ensemble diurnal load + coincidence factor, 2022 vs 2030.

    Coincidence factor = diversified stock peak (peak of the stock-weighted mean diurnal
    profile) / weighted-mean of individual-dwelling peaks. CF < 1 quantifies how occupant
    diversity smooths the aggregate peak.
    """
    diurnal, peak = agg["diurnal"], agg["peak"]
    if diurnal.empty:
        print("[fig08] no diurnal; skipped"); return None
    fig, ax = plt.subplots(figsize=(9, 5))
    _shade_midday(ax)
    cf_text = []
    for year in ("2022", "2030"):
        per_arch, weights, indiv_peak = [], [], []
        for arch in ARCH_NAMES:
            d = diurnal[(diurnal["arch"] == arch) & (diurnal["year"].astype(str) == year) &
                        (diurnal["meter"] == FACILITY) & (diurnal["season"] == "all") &
                        (diurnal["daytype"] == "all")]
            if d.empty:
                continue
            prof = d.groupby("hour")["load_kW"].mean().reindex(range(24)).to_numpy()
            per_arch.append(prof); weights.append(STOCK_WEIGHTS.get(arch, 0))
            ip = np.nan
            if not peak.empty:
                pk = peak[(peak["arch"] == arch) & (peak["year"].astype(str) == year)]["peak_kW_annual"]
                ip = pk.mean() if len(pk) else np.nan
            indiv_peak.append(ip)
        if not per_arch:
            continue
        w = np.array(weights, dtype=float); w = w / w.sum()
        ens = np.average(np.vstack(per_arch), axis=0, weights=w)
        st = YEAR_STYLE[year]
        ax.plot(range(24), ens, color=st["color"], lw=st["lw"], label=f"{year} stock load")
        ip_arr = np.array(indiv_peak, dtype=float)
        if np.isfinite(ip_arr).any():
            denom = np.nansum(w * ip_arr)
            cf = ens.max() / denom if denom else np.nan
            cf_text.append(f"{year}: CF={cf:.2f}")
    ax.set_xlabel("Hour of day"); ax.set_ylabel("Stock-weighted electricity (kW/dwelling)")
    ax.set_xlim(0, 23); ax.set_ylim(bottom=0); ax.grid(alpha=0.3); ax.legend(loc="upper left")
    if cf_text:
        ax.text(0.98, 0.03, "Coincidence factor\n" + "\n".join(cf_text), transform=ax.transAxes,
                ha="right", va="bottom", fontsize=9,
                bbox=dict(boxstyle="round", fc="#FFF3CC", alpha=0.8))
    ax.set_title("Fig 8 - Stock-weighted ensemble load shape + coincidence factor",
                 fontweight="bold")
    return _save(fig, out_dir, "fig08_stock_weighted.png")


def plot_fig09_longitudinal(agg, out_dir):
    """Fig 9 - 2005->2030 trajectory of load-shape metrics with the COVID break.

    'Mean peak hour' panel reports TWO distinct, both-valid statistics (decision recorded in
    08_09_injection_bug_status.md Progress Log, 2026-07-15, Task #21 continuation):
      PRIMARY (plotted line/errorbar)  - stock-aggregate: sum all households' hourly kW into
        one building-stock profile per cell, argmax per day, circular-mean the 365 argmax
        hours, archetype-stock-weighted to national (agg['stock_peak'], via
        _stock_weighted_circular_mean()). Continues the manuscript's existing ~17.5-17.7h
        narrative; lands ~17.2h/17.0h for 2022/2030.
      SECONDARY (text annotation only) - household-level circular mean of each dwelling's own
        already-collapsed daily-peak-hour (agg['annual']['mean_peak_hour'], via
        _circular_mean_hour()/_circular_sd_hours()); reported for 2022/2030 only, as evidence
        of growing household-level schedule heterogeneity (WFH-driven) -- NOT discarded, just
        no longer the panel's headline line.
    """
    annual = agg["annual"]
    stock_peak = agg.get("stock_peak", pd.DataFrame())
    if annual.empty:
        print("[fig09] no annual; skipped"); return None
    metrics = [("midday_share", "Mid-day energy share"), ("load_factor", "Load factor"),
               ("peak_to_avg", "Peak-to-average"), ("mean_peak_hour", "Mean peak hour")]
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (col, label) in zip(axs.ravel(), metrics):
        if col not in annual.columns:
            ax.set_visible(False); continue
        g = annual.groupby(annual["year"].astype(str))[col]
        ys = [y for y in YEARS if y in g.groups]
        if col == "mean_peak_hour":
            # mean_peak_hour is a circular quantity (hour-of-day, wraps at 24h). The household-
            # level per-run values (via _circular_mean_hour(); a plain arithmetic mean/std
            # across households is invalid once a real minority of households peak in the
            # morning, e.g. mixing 5h and 19h arithmetically pulls toward ~12h, nonsensical) and
            # the TRUE stock-aggregate (agg['stock_peak']) are two different, both-valid
            # statistics that diverge once the household population is bimodal (see docstring
            # above) -- plot the stock-aggregate as PRIMARY, keep the household-level circular
            # mean as a secondary annotation, not discarded.
            if not stock_peak.empty and {"stock_peak_hour_sin", "stock_peak_hour_cos"} <= set(stock_peak.columns):
                sp = stock_peak.assign(year=stock_peak["year"].astype(str))  # int64-on-reload guard (see fig04/fig07)
                mean, sd = [], []
                for y in ys:
                    m_h, s_h = _stock_weighted_circular_mean(sp[sp["year"] == y])
                    mean.append(m_h); sd.append(s_h)
                primary_is_stock = True
            else:
                print("[fig09] agg['stock_peak'] missing/incomplete; falling back to "
                      "household-level circular mean as primary (stock-aggregate unavailable).")
                mean, sd = [], []
                for y in ys:
                    vals = g.get_group(y).dropna().to_numpy()
                    mean_h, s, c = _circular_mean_hour(vals)
                    mean.append(mean_h); sd.append(_circular_sd_hours(s, c))
                primary_is_stock = False

            # Secondary finding (household-level dispersion), 2022/2030 only -- computed
            # regardless of which line is primary, so it's always available for the annotation.
            hh_lines = []
            for y in ("2022", "2030"):
                if y not in g.groups:
                    continue
                vals = g.get_group(y).dropna().to_numpy()
                if vals.size == 0:
                    continue
                mean_h, s, c = _circular_mean_hour(vals)
                sd_h = _circular_sd_hours(s, c)
                morning_frac = float(np.mean((vals >= 0) & (vals < 12))) * 100
                hh_lines.append(f"{y}: {mean_h:.1f}h (sd {sd_h:.1f}h), {morning_frac:.0f}% morning-leaning")
            if hh_lines:
                note = "Household-level dispersion (secondary)" if primary_is_stock else \
                       "Household-level circular mean (fallback primary)"
                ax.text(0.98, 0.03, note + "\n" + "\n".join(hh_lines), transform=ax.transAxes,
                        ha="right", va="bottom", fontsize=8,
                        bbox=dict(boxstyle="round", fc="#FFF3CC", alpha=0.8))
        else:
            mean = [g.get_group(y).mean() for y in ys]
            sd = [g.get_group(y).std() for y in ys]
        x = list(range(len(ys)))
        ax.errorbar(x, mean, yerr=sd, marker="o", color="#333", capsize=3)
        if "2015" in ys and "2022" in ys:
            ax.axvline((ys.index("2015") + ys.index("2022")) / 2, color="#C8102E",
                       ls="--", lw=1.2, label="COVID break")
        ax.set_xticks(x); ax.set_xticklabels(ys); ax.set_title(label); ax.grid(alpha=0.3)
    axs[0, 0].legend(fontsize=8)
    fig.suptitle("Fig 9 - Longitudinal load-shape trajectory 2005 → 2030", fontweight="bold")
    return _save(fig, out_dir, "fig09_longitudinal.png")


def plot_fig10_eui(agg, out_dir):
    """Fig 10 (secondary) - annual EUI by archetype x city, 2022 vs 2030."""
    annual = agg["annual"]
    if annual.empty or "eui_kWh_m2" not in annual.columns:
        print("[fig10] no EUI; skipped"); return None
    a = annual.dropna(subset=["eui_kWh_m2"])
    if a.empty:
        print("[fig10] EUI all NaN; skipped"); return None
    a = a.copy(); a["cell"] = a["arch"] + "__" + a["city"]
    cells = sorted(a["cell"].unique())
    x = np.arange(len(cells)); w = 0.38
    fig, ax = plt.subplots(figsize=(max(8, len(cells) * 0.8), 5))
    for k, year in enumerate(("2022", "2030")):
        means = [a[(a["cell"] == c) & (a["year"].astype(str) == year)]["eui_kWh_m2"].mean()
                 for c in cells]
        sds = [a[(a["cell"] == c) & (a["year"].astype(str) == year)]["eui_kWh_m2"].std()
               for c in cells]
        ax.bar(x + (k - 0.5) * w, means, w, yerr=sds, capsize=2,
               color=YEAR_STYLE[year]["color"], label=year)
    ax.set_xticks(x); ax.set_xticklabels(cells, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("EUI (kWh/m²·yr)"); ax.legend(title="Cycle"); ax.grid(alpha=0.3, axis="y")
    ax.set_title("Fig 10 - Annual EUI by archetype × city (secondary)", fontweight="bold")
    return _save(fig, out_dir, "fig10_eui_bars.png")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _resolve_rep_cell(agg, requested):
    diurnal = agg["diurnal"]
    cells = set((diurnal["arch"] + "__" + diurnal["city"]).unique()) if not diurnal.empty else set()
    if requested in cells:
        return requested
    for c in sorted(cells):
        if c.startswith("SingleD__"):
            print(f"[rep] {requested} absent; using {c}"); return c
    if cells:
        c = sorted(cells)[0]; print(f"[rep] {requested} absent; using {c}"); return c
    return requested


def main():
    p = argparse.ArgumentParser(description="Step-8 results figures (8E).")
    p.add_argument("--results-dir", default=DEFAULT_RESULTS)
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--figs", default="all", help='"all", "none", or e.g. "1,2,4"')
    p.add_argument("--rebuild-agg", action="store_true")
    p.add_argument("--rep-cell", default="SingleD__Montreal_6A")
    p.add_argument("--schedules-dir", default=DEFAULT_SCHED)
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    agg_dir = os.path.join(args.out, "agg")
    have_agg = os.path.exists(os.path.join(agg_dir, AGG_FILES["meta"]))
    if args.rebuild_agg or not have_agg:
        agg = build_agg_tables(args.results_dir, args.out)
    else:
        print(f"[agg] loading cached agg from {agg_dir} (use --rebuild-agg to refresh)")
        agg = load_agg_tables(args.out)

    if args.figs.strip().lower() == "none":
        print("[done] aggregation only (--figs none)."); return

    rep = _resolve_rep_cell(agg, args.rep_cell)
    registry = {
        1: lambda: plot_fig01_occupancy(args.out, args.schedules_dir, ARCH_DTYPE.get(rep.split("__")[0], "SingleD")),
        2: lambda: plot_fig02_diurnal_elec(agg, args.out, rep),
        3: lambda: plot_fig03_peak_hour(agg, args.out, rep),
        4: lambda: plot_fig04_paired_delta(agg, args.out, rep),
        5: lambda: plot_fig05_diurnal_season(agg, args.out, rep),
        6: lambda: plot_fig06_carpet(agg, args.out, args.results_dir, rep),
        7: lambda: plot_fig07_delta_cz(agg, args.out),
        8: lambda: plot_fig08_stock(agg, args.out),
        9: lambda: plot_fig09_longitudinal(agg, args.out),
        10: lambda: plot_fig10_eui(agg, args.out),
    }
    which = list(registry) if args.figs.strip().lower() == "all" else \
        [int(x) for x in args.figs.split(",") if x.strip().isdigit()]
    for fid in which:
        fn = registry.get(fid)
        if not fn:
            continue
        try:
            fn()
        except Exception as e:
            import traceback
            print(f"[fig{fid:02d}] FAILED: {e}")
            traceback.print_exc()
    print(f"[done] figures -> {os.path.join(args.out, 'figures')}")


if __name__ == "__main__":
    main()
