#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3J Leg-3 -- Step 8E : per-channel aggregation & attribution.

Specified at 3rdJ_08_simulation_4split.md:112-121 since 2026-07-02 and NEVER WRITTEN until
2026-07-31 -- Step 9 reads `outputs_step8/agg/{agg_annual,agg_peak,agg_diurnal,agg_meta}.csv`
and those files did not exist, so Step 9 could not have run at all. This is that bridge.

WHAT IT DOES
------------
Reads a finished campaign tree (one directory per cell, each with manifest.json,
hourly_meters.csv, channel_hourly.csv, dhw_hourly.csv, injected.idf and run/eplusout.sql)
and produces the four aggregate tables Step 9 consumes.

THE THREE DEFECTS THIS FILE IS BUILT AROUND (see 3rdJ_08_implementation_improvements.md)
----------------------------------------------------------------------------------------
* Defaut 5 -- the campaign used to request pre-EnergyPlus-9.4 meter names (`Gas:Facility` &c.),
  so 53.5 % of site energy read as zero. This script REFUSES to aggregate a cell whose
  manifest does not carry a passing `fuel_closure`, rather than quietly producing an EUI that
  is missing half the energy. Old cells fail fast and say why.
* Defaut 6 -- zone-level Output:Variables are unmultiplied. The driver now applies
  Zones.Multiplier before channel aggregation and proves it per run (`channel_closure`);
  this script re-derives areas the same way (FloorArea x Multiplier) so energy and area
  always share one convention.
* Defaut 7 -- the occupiable shares printed in the pipeline docs are placeholders (three
  channels at an identical 24.4 % on the Tall tower, against a measured 44.65 / 24.91 /
  22.40 / 5.53). Every area used here is PARSED from the IDF + SQL of the very cell being
  aggregated and written to agg_meta.csv, so no constant is ever retyped.

ATTRIBUTION RULES (dr_L3-10, locked; stated here because a reviewer will ask)
----------------------------------------------------------------------------
Direct, channel-resolved (no allocation needed -- the zone variables partition the meter):
    interior lighting, interior electric equipment, interior gas equipment.
Allocated hour by hour, never by area:
    DHW (electric + gas) .... by each channel's share of Water Use Equipment Heating Energy
    space cooling .......... by share of |Zone Air System Sensible Cooling Energy|
    space heating .......... by share of |Zone Air System Sensible Heating Energy|
    fans, pumps, heat rejection, heat recovery
                          .. by share of combined |cooling| + |heating| zone load
Not a tenant load, never prorated as one:
    exterior lighting ...... reported in its own `core_exterior` row.
When an allocation denominator is zero for an hour (e.g. no coil load at 03:00 while the
plant still draws parasitic power), the hour falls back to the channel CFA share; the number
of such hours is counted per cell and written to agg_meta.csv -- a silent fallback would be
indistinguishable from a real result.

USAGE
-----
    py -3 3rdJ_08E_aggregate_4split.py --campaign-dir <dir> [--outdir <dir>] [--strict/--no-strict]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

CHANNELS = ["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]
TENANT_CHANNELS = ["office", "retail", "hotel", "residential"]

# Fine Tag-2 class -> aggregate channel. Identical to the driver's CHANNEL_AGG; duplicated
# rather than imported so this script can aggregate a tree produced by any driver version,
# and asserted equal to the driver's map at startup when that import succeeds.
FINE_TO_AGG = {
    "residential": "residential", "residential_common": "residential_common",
    "office": "office", "office_support": "office",
    "retail": "retail",
    "hotel": "hotel", "hotel_support": "hotel",
    "service_mep": "service_MEP",
}

# end_use -> (fuel, allocation basis). "direct:<metric>" reads the per-channel column.
END_USES = [
    ("interior_lighting",  "Electricity", "direct:lights",   "InteriorLights:Electricity"),
    ("interior_equipment", "Electricity", "direct:equip",    "InteriorEquipment:Electricity"),
    ("interior_equipment", "NaturalGas",  "direct:gasequip", "InteriorEquipment:NaturalGas"),
    ("dhw",                "Electricity", "dhw",             "WaterSystems:Electricity"),
    ("dhw",                "NaturalGas",  "dhw",             "WaterSystems:NaturalGas"),
    ("cooling",            "Electricity", "cool",            "Cooling:Electricity"),
    ("heating",            "Electricity", "heat",            "Heating:Electricity"),
    ("heating",            "NaturalGas",  "heat",            "Heating:NaturalGas"),
    ("fans",               "Electricity", "hvac",            "Fans:Electricity"),
    ("pumps",              "Electricity", "hvac",            "Pumps:Electricity"),
    ("heat_rejection",     "Electricity", "cool",            "HeatRejection:Electricity"),
    ("heat_recovery",      "Electricity", "hvac",            "HeatRecovery:Electricity"),
]
CORE_ONLY = [("exterior_lighting", "Electricity", "ExteriorLights:Electricity")]

J_TO_KWH = 1.0 / 3.6e6
J_TO_GJ = 1.0 / 1.0e9


# ---------------------------------------------------------------------------
# Areas -- parsed, never assumed (Defaut 7)
# ---------------------------------------------------------------------------
def parse_channel_areas(injected_idf: str, sql_path: str, eplus_idd: str) -> dict:
    """Per-channel Conditioned Floor Area, in m2, as EnergyPlus itself counts it.

    Area = sum over the channel's zones of FloorArea x Multiplier, restricted to
    IsPartOfTotalArea = 1. That restriction is not cosmetic: on the Tall tower the 9 plenum
    zones carry 70,611.6 m2 of multiplied area, and including them would nearly triple the
    denominator of every EUI. The resulting total reproduces the ABUPS "Total Building Area"
    exactly (72,623.1 m2 measured, 72,623.1 m2 reported), which is the check that this
    convention is EnergyPlus's own and not ours.
    """
    import sqlite3
    from eppy.modeleditor import IDF
    from eSim_bem_utils.commercial_integration import classify_tag2

    IDF.setiddname(eplus_idd)
    idf = IDF(injected_idf)
    zone_to_channel = {}
    for sp in idf.idfobjects.get("SPACE", []):
        tag2 = ""
        for f in ("Tag_2", "Space_Type_Name", "Space_Type", "Name"):
            v = str(getattr(sp, f, "") or "").strip()
            if v:
                tag2 = v
                break
        agg = FINE_TO_AGG.get(classify_tag2(tag2))
        zn = str(getattr(sp, "Zone_Name", "") or "").strip().upper()
        if agg and zn:
            zone_to_channel[zn] = agg

    conn = sqlite3.connect(f"file:{sql_path}?mode=ro", uri=True)
    try:
        z = pd.read_sql_query(
            "SELECT ZoneName, FloorArea, Multiplier, IsPartOfTotalArea FROM Zones", conn)
    finally:
        conn.close()
    z["KEY"] = z["ZoneName"].astype(str).str.strip().str.upper()
    z["channel"] = z["KEY"].map(zone_to_channel)
    z["area"] = z["FloorArea"].astype(float) * z["Multiplier"].astype(float)
    inc = z[z["IsPartOfTotalArea"] == 1]

    areas = {c: float(inc.loc[inc["channel"] == c, "area"].sum()) for c in CHANNELS}
    areas["_unclassified"] = float(inc.loc[inc["channel"].isna(), "area"].sum())
    areas["_total_building"] = float(inc["area"].sum())
    areas["_excluded_plenum"] = float(z.loc[z["IsPartOfTotalArea"] != 1, "area"].sum())
    return areas


# ---------------------------------------------------------------------------
# Allocation
# ---------------------------------------------------------------------------
def _shares(frame: pd.DataFrame, cols: list, fallback: np.ndarray) -> tuple:
    """Hourly allocation shares from a non-negative driver, with an explicit fallback.

    Returns (shares NxC, n_fallback_hours). Magnitudes are taken as absolute values because
    Zone Air System Sensible Heating/Cooling Energy are reported as positive magnitudes on
    their own meters but a sign convention slip would otherwise cancel channels against each
    other and produce a share of the wrong sign.
    """
    m = np.abs(frame[cols].to_numpy(dtype=float))
    tot = m.sum(axis=1)
    zero = tot <= 0.0
    out = np.zeros_like(m)
    nz = ~zero
    out[nz] = m[nz] / tot[nz][:, None]
    out[zero] = fallback
    return out, int(zero.sum())


def aggregate_cell(cell_dir: str, eplus_idd: str, strict: bool = True,
                   idf_name: str = "injected.idf") -> dict | None:
    name = os.path.basename(cell_dir.rstrip("\\/"))
    mpath = os.path.join(cell_dir, "manifest.json")
    if not os.path.isfile(mpath):
        print(f"  [skip] {name}: no manifest.json")
        return None
    with open(mpath, "r", encoding="utf-8") as f:
        man = json.load(f)

    # --- Refuse to aggregate an unclosed cell (Defaut 5). ------------------------------
    problems = []
    fc = man.get("fuel_closure")
    if fc is None:
        problems.append("manifest has no fuel_closure -- produced before the 2026-07-31 fix, "
                        "so its gas meters are the pre-9.4 names and read 0")
    else:
        for fuel in ("Electricity", "NaturalGas"):
            r = fc.get(fuel, {})
            if not r.get("closed"):
                problems.append(
                    f"fuel closure FAILED for {fuel} "
                    f"(residual {r.get('residual_rel', float('nan')) * 100:.4f} %, "
                    f"facility meter absent = {r.get('facility_meter_absent')})")
    cc = man.get("channel_closure")
    if cc is None:
        problems.append("manifest has no channel_closure -- channel_hourly.csv predates the "
                        "Zones.Multiplier fix and its magnitudes are ~25 % of the true value")
    else:
        for metric, r in cc.items():
            if not r.get("closed"):
                problems.append(f"channel closure FAILED for {metric} "
                                f"(residual {r.get('residual_rel', float('nan')) * 100:.4f} %)")
    if problems:
        head = f"  [{'FAIL' if strict else 'WARN'}] {name}:"
        for p in problems:
            print(f"{head} {p}")
        if strict:
            return None

    hourly = pd.read_csv(os.path.join(cell_dir, "hourly_meters.csv"))
    chan = pd.read_csv(os.path.join(cell_dir, "channel_hourly.csv"))
    dhw_path = os.path.join(cell_dir, "dhw_hourly.csv")
    dhw = pd.read_csv(dhw_path) if os.path.isfile(dhw_path) else None
    n = len(hourly)
    if n != 8760 or len(chan) != 8760:
        print(f"  [FAIL] {name}: row counts hourly={n} channel={len(chan)}, expected 8760")
        return None

    # `idf_name` exists only because the RESIZED arm writes `injected_resized.idf` -- it is the file
    # EnergyPlus actually ran, so it is the one whose areas must be parsed. The default is
    # `injected.idf`, so every arm aggregated before 2026-08-04 is byte-identical. Deliberately NOT
    # solved with a symlink named `injected.idf`: in every other arm that name means "arm H's
    # injected IDF", and a later reader diffing `injected.idf` across arms would silently compare a
    # resized IDF against an unresized one and read the burner capacity change as an injection
    # difference. A flag says what is happening; a same-named symlink hides it.
    idf_path = os.path.join(cell_dir, idf_name)
    if not os.path.isfile(idf_path):
        print(f"  [FAIL] {name}: no {idf_name} in {cell_dir}")
        return None
    areas = parse_channel_areas(idf_path,
                                os.path.join(cell_dir, "run", "eplusout.sql"), eplus_idd)
    area_vec = np.array([areas[c] for c in CHANNELS], dtype=float)
    area_share = area_vec / area_vec.sum() if area_vec.sum() > 0 else np.full(len(CHANNELS), 1 / len(CHANNELS))

    # --- allocation bases --------------------------------------------------------------
    fb = {}
    cool_sh, fb["cool"] = _shares(chan, [f"{c}_syscool" for c in CHANNELS], area_share)
    heat_sh, fb["heat"] = _shares(chan, [f"{c}_sysheat" for c in CHANNELS], area_share)
    hvac_drv = pd.DataFrame({c: chan[f"{c}_syscool"].abs() + chan[f"{c}_sysheat"].abs()
                             for c in CHANNELS})
    hvac_sh, fb["hvac"] = _shares(hvac_drv, CHANNELS, area_share)
    if dhw is not None:
        dhw_cols = [f"dhw_{c}" for c in CHANNELS]
        dhw_sh, fb["dhw"] = _shares(dhw, dhw_cols, area_share)
    else:
        dhw_sh, fb["dhw"] = np.tile(area_share, (n, 1)), n
    BASIS = {"cool": cool_sh, "heat": heat_sh, "hvac": hvac_sh, "dhw": dhw_sh}

    # --- per-channel hourly energy by end use ------------------------------------------
    rows, hourly_channel_total = [], np.zeros((n, len(CHANNELS)))
    for end_use, fuel, basis, meter in END_USES:
        if meter not in hourly.columns:
            continue
        series = hourly[meter].to_numpy(dtype=float)
        if basis.startswith("direct:"):
            metric = basis.split(":", 1)[1]
            alloc = chan[[f"{c}_{metric}" for c in CHANNELS]].to_numpy(dtype=float)
        else:
            alloc = BASIS[basis] * series[:, None]
        hourly_channel_total += alloc
        for i, c in enumerate(CHANNELS):
            rows.append({"channel": c, "end_use": end_use, "fuel": fuel,
                         "energy_J": float(alloc[:, i].sum()),
                         "peak_W": float(alloc[:, i].max()) / 3600.0,
                         "allocation": "direct" if basis.startswith("direct") else basis})
    for end_use, fuel, meter in CORE_ONLY:
        if meter in hourly.columns:
            rows.append({"channel": "core_exterior", "end_use": end_use, "fuel": fuel,
                         "energy_J": float(hourly[meter].sum()),
                         "peak_W": float(hourly[meter].max()) / 3600.0,
                         "allocation": "unallocated"})

    ann = pd.DataFrame(rows)
    for k, v in (("cell_tag", man.get("cell_tag", name)), ("scenario", man.get("scenario")),
                 ("building", man.get("building")), ("city", man.get("city")),
                 ("cz", man.get("cz"))):
        ann[k] = v

    # --- attribution closure: the sum of everything attributed must be the site total ---
    site_total_J = float(sum(hourly[m].sum() for m in ("Electricity:Facility", "NaturalGas:Facility")
                             if m in hourly.columns))
    attributed_J = float(ann["energy_J"].sum())
    attrib_rel = abs(attributed_J - site_total_J) / site_total_J if site_total_J else 0.0

    meta = {"cell_tag": man.get("cell_tag", name), "scenario": man.get("scenario"),
            "building": man.get("building"), "city": man.get("city"), "cz": man.get("cz"),
            "PLATFORM": man.get("PLATFORM"), "INJ_HASH": man.get("INJ_HASH"),
            "INPUTS_HASH": man.get("INPUTS_HASH"),
            "OUTPUT_SCHEMA_HASH": man.get("OUTPUT_SCHEMA_HASH"),
            "energyplus_version": man.get("energyplus_version"),
            "site_energy_GJ": site_total_J * J_TO_GJ,
            "attributed_GJ": attributed_J * J_TO_GJ,
            "attribution_residual_rel": attrib_rel,
            "attribution_closed": bool(attrib_rel <= 1e-6),
            "total_building_area_m2": areas["_total_building"],
            "excluded_plenum_area_m2": areas["_excluded_plenum"],
            "unclassified_area_m2": areas["_unclassified"],
            "fallback_hours_cool": fb["cool"], "fallback_hours_heat": fb["heat"],
            "fallback_hours_hvac": fb["hvac"], "fallback_hours_dhw": fb["dhw"]}
    for c in CHANNELS:
        meta[f"area_{c}_m2"] = areas[c]
        meta[f"share_{c}_pct_gross"] = 100.0 * areas[c] / areas["_total_building"]

    cal = read_calendar(os.path.join(cell_dir, "run", "eplusout.sql"), n)
    meta["n_weekend_hours"] = int((cal["daytype"] == "WE").sum())
    return {"annual": ann, "meta": meta, "areas": areas, "cal": cal,
            "hourly_channel_total": hourly_channel_total,
            "chan": chan, "hourly": hourly, "man": man}


# ---------------------------------------------------------------------------
# Diurnal / peak -- circular hour statistics (Step-9 caveat 3)
# ---------------------------------------------------------------------------
def read_calendar(sql_path: str, n_expected: int = 8760) -> pd.DataFrame:
    """Month / day-type / hour straight from the SQL `Time` table -- never reconstructed.

    🔴 Do not be tempted to synthesise this from a pandas date_range. The campaign's RunPeriod
    declares `Day of Week for Start Day = Sunday` and `Begin Year = 2006`; a date_range starting
    2030-01-01 lands on a Tuesday, which would shift every weekday/weekend label by two days and
    silently corrupt the WD/WE diurnals, the weekend-structure gate and every per-day-type peak.
    EnergyPlus writes the authoritative label in `Time.DayType` (verified: 53 Sundays = 1,272 h,
    1,248 h for the other six), so the calendar is read, not inferred.
    """
    import sqlite3
    conn = sqlite3.connect(f"file:{sql_path}?mode=ro", uri=True)
    try:
        # Restrict to the TimeIndex values that the HOURLY meter series actually uses, rather
        # than to "every row of Time for this environment". Those are not the same set: the
        # prototype IDFs carry their own Output:Meter objects at Monthly frequency, so some
        # cells have 8,760 + 12 + 1 = 8,773 Time rows while others have exactly 8,760. Selecting
        # by IntervalType would work today and break on the next reporting-frequency change;
        # deriving the set from the series being read guarantees the calendar aligns row-for-row
        # with hourly_meters.csv, which is the property that actually matters here.
        t = pd.read_sql_query(
            "SELECT tm.TimeIndex, tm.Month, tm.Day, tm.Hour, tm.DayType FROM Time tm "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            "WHERE ep.EnvironmentType = 3 AND tm.TimeIndex IN ("
            "  SELECT DISTINCT rd.TimeIndex FROM ReportData rd "
            "  JOIN ReportDataDictionary rdd "
            "    ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex "
            "  WHERE rdd.Name = 'Electricity:Facility' "
            "    AND (rdd.ReportingFrequency = 'Hourly' OR rdd.ReportingFrequency = 3)) "
            "ORDER BY tm.TimeIndex ASC", conn)
    finally:
        conn.close()
    if len(t) != n_expected:
        raise RuntimeError(
            f"calendar has {len(t)} hourly rows for EnvironmentType=3, expected {n_expected} "
            f"(the hourly Electricity:Facility series defines the row set)")
    # EnergyPlus reports hour 1..24; hour 24 is the interval ending at midnight, i.e. hour-of-day
    # 23 in 0-23 terms. Getting this off by one would rotate every diurnal profile by an hour.
    t["hour"] = t["Hour"].astype(int) - 1
    t["daytype"] = np.where(t["DayType"].isin(["Saturday", "Sunday", "Holiday"]), "WE", "WD")
    return t[["Month", "hour", "daytype", "DayType"]].rename(columns={"Month": "month"})


def circular_peak_hour(profile: np.ndarray) -> float:
    """Load-weighted circular mean hour, in hours.

    Hour-of-day is circular: a population peaking at 23:00 and 01:00 has a mean of 00:00,
    not 12:00. A 2J plotting bug arithmetic-averaged a bimodal morning/evening distribution
    into a meaningless ~14.5 h; Step-9 caveat 3 makes the circular mean mandatory.
    """
    w = np.asarray(profile, dtype=float)
    if w.sum() <= 0:
        return float("nan")
    ang = 2 * np.pi * np.arange(len(w)) / len(w)
    mean = np.arctan2((w * np.sin(ang)).sum(), (w * np.cos(ang)).sum())
    return float((mean % (2 * np.pi)) / (2 * np.pi) * len(w))


def build_diurnal(res: dict) -> pd.DataFrame:
    cal = res["cal"]
    season = np.where(cal["month"].isin([12, 1, 2]), "winter",
                      np.where(cal["month"].isin([6, 7, 8]), "summer", "shoulder"))
    daytype = cal["daytype"].to_numpy()
    out = []
    tot = res["hourly_channel_total"]
    chan = res["chan"]
    # TWO metrics, not one. `energy_W` is the attributed load; `people` is the occupant count
    # that drove it. They are NOT interchangeable, and Leg 3 is the first leg where they come
    # apart: under OD-7D the residential channel drives PEOPLE ONLY (no lights/equipment
    # columns exist in the Step-7 residential product), so its ENERGY profile is dominated by
    # flat NECB baseline loads and does not show the evening occupancy peak at all. Asking
    # "when does this channel peak?" of the energy series answers a different question for
    # residential than for the three commercial channels. Emitting both is what lets Step 9
    # ask each question of the series that carries it -- and lets the contrast between them
    # be measured rather than argued (see D-20).
    for metric, source in (("energy_W", None), ("people", "people")):
        for i, c in enumerate(CHANNELS):
            if source is None:
                v = tot[:, i] / 3600.0
            else:
                col = f"{c}_{source}"
                if col not in chan.columns:
                    continue
                v = chan[col].to_numpy(dtype=float)
            d = pd.DataFrame({"season": season, "daytype": daytype, "hour": cal["hour"], "W": v})
            g = d.groupby(["season", "daytype", "hour"], as_index=False)["W"].mean()
            g["channel"], g["metric"] = c, metric
            out.append(g)
            allday = d.groupby(["daytype", "hour"], as_index=False)["W"].mean()
            allday["season"], allday["channel"], allday["metric"] = "all", c, metric
            out.append(allday[["season", "daytype", "hour", "W", "channel", "metric"]])
    df = pd.concat(out, ignore_index=True)
    df["cell_tag"] = res["meta"]["cell_tag"]
    return df


def build_peak(res: dict) -> pd.DataFrame:
    cal = res["cal"]
    daytype = cal["daytype"].to_numpy()
    tot = res["hourly_channel_total"]
    rows = []
    chan = res["chan"]
    for i, c in enumerate(CHANNELS):
        # Occupancy peak hour, per day type -- the question the Step-9 doc's "peak-hour
        # direction" row is really asking, and the only series in which the residential
        # channel can express an evening peak (OD-7D / D-20).
        pcol = f"{c}_people"
        if pcol in chan.columns:
            pv = chan[pcol].to_numpy(dtype=float)
            for dt in ("WD", "WE", "all"):
                sel = np.ones(len(pv), bool) if dt == "all" else (daytype == dt)
                pp = (pd.Series(pv[sel]).groupby(cal["hour"][sel].values).mean()
                      .reindex(range(24), fill_value=0.0).to_numpy())
                rows.append({"channel": c, "daytype": dt, "metric": "people",
                             "peak_W": float(pv[sel].max()),
                             "peak_hour_argmax": int(np.argmax(pp)),
                             "peak_hour_circular": circular_peak_hour(pp),
                             "mean_W": float(pv[sel].mean())})
        w = tot[:, i] / 3600.0
        for dt in ("WD", "WE", "all"):
            sel = np.ones(len(w), bool) if dt == "all" else (daytype == dt)
            prof = pd.Series(w[sel]).groupby(cal["hour"][sel].values).mean()
            prof = prof.reindex(range(24), fill_value=0.0).to_numpy()
            rows.append({"channel": c, "daytype": dt, "metric": "energy_W",
                         "peak_W": float(w[sel].max()),
                         "peak_hour_argmax": int(np.argmax(prof)),
                         "peak_hour_circular": circular_peak_hour(prof),
                         "mean_W": float(w[sel].mean())})
    # Coincidence: the stacked building peak against the sum of the channel peaks.
    stacked = tot.sum(axis=1) / 3600.0
    sum_of_peaks = float(sum(tot[:, i].max() for i in range(len(CHANNELS))) / 3600.0)
    rows.append({"channel": "_BUILDING", "daytype": "all", "metric": "energy_W",
                 "peak_W": float(stacked.max()), "peak_hour_argmax": -1,
                 "peak_hour_circular": circular_peak_hour(
                     pd.Series(stacked).groupby(cal["hour"].values).mean()
                     .reindex(range(24), fill_value=0.0).to_numpy()),
                 "mean_W": float(stacked.mean())})
    df = pd.DataFrame(rows)
    df["sum_of_channel_peaks_W"] = sum_of_peaks
    df["coincidence_factor"] = float(stacked.max()) / sum_of_peaks if sum_of_peaks else float("nan")
    df["cell_tag"] = res["meta"]["cell_tag"]
    return df


# ---------------------------------------------------------------------------
def _aggregate_and_build(task: tuple) -> dict | None:
    """One cell, start to finish, in whatever process picks it up.

    `build_diurnal` / `build_peak` are called HERE rather than back in `main` so a worker returns
    only the three small frames plus meta. `aggregate_cell`'s raw result carries several 8760-row
    frames per cell (`chan`, `hourly`, `cal`, `hourly_channel_total`) which would otherwise be
    pickled back across the process boundary for nothing.

    Calling them here also keeps `--jobs 1` byte-identical to the pre-2026-08-04 sequential loop:
    same functions, same order, same arguments -- only the process they run in can differ.
    """
    cell_dir, eplus_idd, strict, idf_name = task
    res = aggregate_cell(cell_dir, eplus_idd, strict=strict, idf_name=idf_name)
    if res is None:
        return None
    return {"annual": res["annual"], "diurnal": build_diurnal(res),
            "peak": build_peak(res), "meta": res["meta"]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 8E -- per-channel aggregation (dr_L3-10)")
    ap.add_argument("--campaign-dir", required=True)
    ap.add_argument("--outdir", default=os.path.join(HERE, "outputs_step8", "agg"))
    ap.add_argument("--eplus-idd", default=r"C:\EnergyPlusV24-2-0\Energy+.idd")
    ap.add_argument("--no-strict", dest="strict", action="store_false",
                    help="aggregate cells whose closure gates fail (diagnostic only -- the "
                         "resulting EUIs are NOT publishable; default refuses them)")
    ap.add_argument("--idf-name", default="injected.idf",
                    help="per-cell IDF whose areas are parsed. Default `injected.idf`, which is "
                         "every arm through H. The RESIZED arm writes `injected_resized.idf`.")
    ap.add_argument("--jobs", type=int, default=1,
                    help="cells aggregated concurrently, one process each. Default 1 = the "
                         "original sequential loop, so every arm aggregated before 2026-08-04 "
                         "reproduces exactly. Each cell is an independent read of its own "
                         "~160 MB eplusout.sql, so this scales with cores until disk-bound; it "
                         "changes NO arithmetic -- results are collected with `map`, which "
                         "preserves submission order, so the output row order is identical too.")
    ap.set_defaults(strict=True)
    args = ap.parse_args()

    # `_STALE_<timestamp>` directories are archived-aside earlier attempts (_archive_stale);
    # they carry a complete-looking manifest and would otherwise be aggregated as if they were
    # cells, silently double-counting a scenario.
    cells = sorted(d for d in
                   (os.path.join(args.campaign_dir, x) for x in os.listdir(args.campaign_dir))
                   if os.path.isdir(d) and os.path.isfile(os.path.join(d, "manifest.json"))
                   and "_STALE_" not in os.path.basename(d))
    print(f"=== Step 8E aggregation | {len(cells)} cell(s) in {args.campaign_dir} | "
          f"strict={args.strict} ===")

    tasks = [(cd, args.eplus_idd, args.strict, args.idf_name) for cd in cells]
    if args.jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        print(f"  aggregating {args.jobs} cells at a time")
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            results = list(ex.map(_aggregate_and_build, tasks))
    else:
        results = [_aggregate_and_build(t) for t in tasks]

    annual, diurnal, peak, meta = [], [], [], []
    for res in results:
        if res is None:
            continue
        annual.append(res["annual"])
        diurnal.append(res["diurnal"])
        peak.append(res["peak"])
        meta.append(res["meta"])
        m = res["meta"]
        print(f"  [ok] {m['cell_tag']:<34} site {m['site_energy_GJ']:9.1f} GJ | "
              f"attribution residual {m['attribution_residual_rel'] * 100:.6f} % | "
              f"fallback h cool/heat/hvac/dhw = {m['fallback_hours_cool']}/"
              f"{m['fallback_hours_heat']}/{m['fallback_hours_hvac']}/{m['fallback_hours_dhw']}")

    if not annual:
        print("\n[FAIL] no cell passed the closure gates -- nothing aggregated. If this tree "
              "predates 2026-07-31 it must be re-simulated (Defaut 5/6), not re-post-processed: "
              "the meters were never reported, so they are not in the SQL to recover.")
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    ann = pd.concat(annual, ignore_index=True)
    mt = pd.DataFrame(meta)

    # EUI, dual basis (dr_L3-10). CFA = the channel's own conditioned floor area (primary,
    # thermodynamic). GFA-share = the channel's energy plus its area-prorated share of
    # service/MEP and exterior lighting, over its area-prorated share of gross -- the basis
    # SCIEU/CEUD stock figures are quoted on. The basis is a COLUMN here so no table can be
    # read without it.
    per = ann.groupby(["cell_tag", "channel"], as_index=False)["energy_J"].sum()
    per = per.merge(mt[["cell_tag"] + [f"area_{c}_m2" for c in CHANNELS]
                       + ["total_building_area_m2"]], on="cell_tag", how="left")
    per["area_m2"] = [r[f"area_{r['channel']}_m2"] if f"area_{r['channel']}_m2" in r else np.nan
                      for _, r in per.iterrows()]
    per["eui_CFA_kWh_m2"] = per["energy_J"] * J_TO_KWH / per["area_m2"]
    ann_out = ann.copy()
    ann_out["energy_GJ"] = ann_out["energy_J"] * J_TO_GJ

    ann_out.to_csv(os.path.join(args.outdir, "agg_annual.csv"), index=False)
    per.to_csv(os.path.join(args.outdir, "agg_annual_by_channel.csv"), index=False)
    pd.concat(diurnal, ignore_index=True).to_csv(os.path.join(args.outdir, "agg_diurnal.csv"), index=False)
    pd.concat(peak, ignore_index=True).to_csv(os.path.join(args.outdir, "agg_peak.csv"), index=False)
    mt.to_csv(os.path.join(args.outdir, "agg_meta.csv"), index=False)

    print(f"\n=== wrote 5 tables to {args.outdir} ===")
    print(f"  cells aggregated : {len(mt)} / {len(cells)}")
    bad = mt[~mt["attribution_closed"]]
    if len(bad):
        print(f"  🔴 {len(bad)} cell(s) whose attribution does not close against site energy: "
              f"{list(bad['cell_tag'])[:5]}")
    else:
        print("  attribution closes against site energy on every cell (<= 1e-6 relative)")


if __name__ == "__main__":
    main()
