"""3rdJ_08P_probe_driver.py -- Step 8 (3J Leg-3 4-split): PROBE cell runner.

Runs ONE probe cell out of the 7-cell §P pre-campaign probe table (manager handoff
2026-07-28_employee_step8_probes_P1P4.md §3.2). Each cell injects office/retail/hotel
schedule products (or none, or a deliberately-missing one) into the SuperTall v24.2
mixed-use tower IDF via inject_mixed_use(), ensures the output objects needed for the
P1-P4 gates, simulates via EnergyPlus (through a Singularity wrapper -- Speed is
AlmaLinux 9, the E+ binary is Ubuntu-compiled), extracts two hourly CSVs from the SQL
output, and writes a manifest.json carrying everything the gate script
(3rdJ_08P_probe_gates.py, run separately after the array lands) needs to score P1-P4.

Scope boundary (handoff §1): residential is OUT. No residential channel config is ever
built here; residential Spaces stay at NECB baseline in every cell (the injector already
skips residential Tag-2 unconditionally -- see commercial_integration.py L386-387).

Runs on the cluster only, via sbatch array (3rdJ_08P_probes.sh). Does NOT modify
commercial_integration.py, eSim_datapreprocessing.py, eSim_dynamicML_mHead.py, or
eSim_dynamicML_mHead_alignment.py.

2026-07-28 built (P1-P4 armament, employee handoff).
2026-07-28 fixed (job 1169671 bug-fix pass): channel_hourly.csv case-mismatch join bug
(zone_to_channel keys vs. SQL KeyValue -- see _build_zone_channel_map / _write_channel_hourly_csv);
loud unmapped-row reporting + hard-fail on 0 mapped rows; driver_md5 added to manifest; added
--postprocess-only (re-derive both CSVs + manifest from an existing eplusout.sql, no re-simulation).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (Linux, cluster-only; grouped here per 3rdJ_08W_audit_wiring.py convention)
# ---------------------------------------------------------------------------
SCRATCH8 = "/speed-scratch/o_iseri/step8_4split"
UPLOAD = SCRATCH8 + "/upload"
PROBES_ROOT = SCRATCH8 + "/probes"

# IDF stock: reused from Leg-2's v24.2 transition, NOT re-transitioned (handoff §2).
# SuperTall is the probe building (7,721,326 B, verified 2026-07-28).
IDF_SUPERTALL = (
    "/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/"
    "Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/"
    "SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf"
)

# EPW -- NOTE (2026-07-28, verified on cluster by ls): the handoff doc's stated path
# (.../step8_4split/upload/BEM_Setup/WeatherFile/...) does NOT exist; the file lives
# under the step8_2split upload tree, alongside the reused IDF stock. Corrected here;
# see the Progress Log entry for this discrepancy.
EPW = (
    "/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/"
    "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
)

SIF = "/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif"
SIF_EXE = "/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus"

STEP7_OUT = UPLOAD + "/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7"
INJECTOR_PY = UPLOAD + "/eSim_bem_utils/commercial_integration.py"

sys.path.insert(0, UPLOAD)  # fallback in case PYTHONPATH wasn't propagated to the job env


def _csv(name: str) -> str:
    return os.path.join(STEP7_OUT, name)


OFFICE_2022 = _csv("office_presence_multiplier_2022.csv")
OFFICE_2030 = _csv("office_presence_multiplier_2030.csv")
RETAIL_2022 = _csv("retail_presence_multiplier_2022.csv")
RETAIL_2030_CENTRAL = _csv("retail_presence_multiplier_2030_central.csv")
RETAIL_2030_OPT = _csv("retail_presence_multiplier_2030_opt.csv")
HOTEL_2022 = _csv("hotel_schedule_multiplier_2022.csv")
HOTEL_2030_CENTRAL = _csv("hotel_schedule_multiplier_2030_central.csv")
HOTEL_2030_OPT = _csv("hotel_schedule_multiplier_2030_opt.csv")

# Deliberately nonexistent -- the P4/W5 fall-back trip wire for cell 6. Never create this file.
RETAIL_NONEXISTENT = _csv("retail_presence_multiplier_2030_DOES_NOT_EXIST.csv")

# ---------------------------------------------------------------------------
# Probe cell table (handoff §3.2, SuperTall / MTL Z6, one-at-a-time design)
# ---------------------------------------------------------------------------
CELLS = [
    {"tag": "baseline_necb", "channels": {}},
    {"tag": "B_central", "channels": {
        "office": {"csv": OFFICE_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
        "retail": {"csv": RETAIL_2030_CENTRAL, "pr": "QC"},
        "hotel": {"csv": HOTEL_2030_CENTRAL, "pr": "QC"},
    }},
    {"tag": "var_office", "channels": {
        "office": {"csv": OFFICE_2030, "archetype": "Office_Knowledge", "band": "fullyhybrid"},
        "retail": {"csv": RETAIL_2030_CENTRAL, "pr": "QC"},
        "hotel": {"csv": HOTEL_2030_CENTRAL, "pr": "QC"},
    }},
    {"tag": "var_retail", "channels": {
        "office": {"csv": OFFICE_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
        "retail": {"csv": RETAIL_2030_OPT, "pr": "QC"},
        "hotel": {"csv": HOTEL_2030_CENTRAL, "pr": "QC"},
    }},
    {"tag": "var_hotel", "channels": {
        "office": {"csv": OFFICE_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
        "retail": {"csv": RETAIL_2030_CENTRAL, "pr": "QC"},
        "hotel": {"csv": HOTEL_2030_OPT, "pr": "QC"},
    }},
    {"tag": "cycle_2022", "channels": {
        "office": {"csv": OFFICE_2022, "archetype": "Office_Knowledge", "band": "observed"},
        "retail": {"csv": RETAIL_2022, "pr": "QC"},
        "hotel": {"csv": HOTEL_2022, "pr": "QC"},
    }},
    {"tag": "fallback_retail", "channels": {
        "office": {"csv": OFFICE_2030, "archetype": "Office_Knowledge", "band": "hybrid"},
        "retail": {"csv": RETAIL_NONEXISTENT, "pr": "QC"},
        "hotel": {"csv": HOTEL_2030_CENTRAL, "pr": "QC"},
    }},
]

# ---------------------------------------------------------------------------
# Output objects to ensure on every injected IDF (handoff §3.1 step 3 -- the Leg-2
# office SQL-gap lesson: do this on every path, no exceptions)
# ---------------------------------------------------------------------------
REQUIRED_METERS = [
    "Electricity:Facility", "Gas:Facility", "InteriorLights:Electricity",
    "InteriorEquipment:Electricity", "InteriorEquipment:Gas", "Fans:Electricity",
    "Pumps:Electricity", "Cooling:Electricity", "Heating:Electricity", "Heating:Gas",
    "WaterSystems:Electricity", "WaterSystems:Gas",
]
REQUIRED_VARIABLES = [
    "Zone People Occupant Count",
    "Zone Lights Electricity Energy",
    "Zone Electric Equipment Electricity Energy",
]
VAR_METRIC = {
    "Zone People Occupant Count": "people",
    "Zone Lights Electricity Energy": "lights",
    "Zone Electric Equipment Electricity Energy": "equip",
}
CHANNEL_AGG = {
    "residential": {"residential", "residential_common"},
    "office": {"office", "office_support"},
    "retail": {"retail"},
    "hotel": {"hotel", "hotel_support"},
    "service_MEP": {"service_mep"},
}
_FINE_TO_AGG = {fine: agg for agg, fines in CHANNEL_AGG.items() for fine in fines}

# Tag-2 field priority on a SPACE object -- verbatim from 3rdJ_08W_audit_wiring.py
# (empirically verified 2026-07-28 against the real IDF, L13682: eppy attribute `Tag_2`).
_SPACE_TAG2_FIELDS = ("Tag_2", "Space_Type_Name", "Space_Type", "Name")


def _get_space_tag2(space_obj) -> str:
    for f in _SPACE_TAG2_FIELDS:
        v = getattr(space_obj, f, "")
        if v:
            return str(v).strip()
    return ""


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_manifest(outdir: str, manifest: dict) -> str:
    path = os.path.join(outdir, "manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"[manifest] written: {path}")
    return path


# ---------------------------------------------------------------------------
# Step 3 -- ensure Output:SQLite / hourly Output:Meter / hourly Output:Variable(*) /
# full-year RunPeriod on the injected IDF (idempotent: add only what's missing).
# ---------------------------------------------------------------------------
def _ensure_output_objects(idf, verbose: bool = True) -> None:
    # Output:SQLite = SimpleAndTabular
    sql_objs = idf.idfobjects.get("OUTPUT:SQLITE", [])
    if not sql_objs:
        obj = idf.newidfobject("Output:SQLite")
        obj.Option_Type = "SimpleAndTabular"
        if verbose:
            print("  [ensure-outputs] added Output:SQLite (SimpleAndTabular)")
    else:
        for obj in sql_objs:
            if str(getattr(obj, "Option_Type", "")).strip() != "SimpleAndTabular":
                obj.Option_Type = "SimpleAndTabular"
                if verbose:
                    print("  [ensure-outputs] forced Output:SQLite Option_Type=SimpleAndTabular")

    # Hourly Output:Meter (add if absent, matched on name + Hourly frequency)
    existing_meters = set()
    for m in idf.idfobjects.get("OUTPUT:METER", []):
        freq = str(getattr(m, "Reporting_Frequency", "")).strip().lower()
        existing_meters.add((str(getattr(m, "Key_Name", "")).strip(), freq))
    n_added = 0
    for meter_name in REQUIRED_METERS:
        if (meter_name, "hourly") not in existing_meters:
            obj = idf.newidfobject("Output:Meter")
            obj.Key_Name = meter_name
            obj.Reporting_Frequency = "Hourly"
            n_added += 1
    if verbose and n_added:
        print(f"  [ensure-outputs] added {n_added} hourly Output:Meter objects")

    # Hourly Output:Variable, Key_Value="*" (add if absent, matched on key + name + frequency)
    existing_vars = set()
    for v in idf.idfobjects.get("OUTPUT:VARIABLE", []):
        freq = str(getattr(v, "Reporting_Frequency", "")).strip().lower()
        key = str(getattr(v, "Key_Value", "")).strip()
        name = str(getattr(v, "Variable_Name", "")).strip()
        existing_vars.add((key, name, freq))
    n_added_v = 0
    for var_name in REQUIRED_VARIABLES:
        if ("*", var_name, "hourly") not in existing_vars:
            obj = idf.newidfobject("Output:Variable")
            obj.Key_Value = "*"
            obj.Variable_Name = var_name
            obj.Reporting_Frequency = "Hourly"
            n_added_v += 1
    if verbose and n_added_v:
        print(f"  [ensure-outputs] added {n_added_v} hourly Output:Variable(*) objects")

    # RunPeriod = full year (Timestep left as-is per handoff §3.1 step 3)
    rps = idf.idfobjects.get("RUNPERIOD", [])
    if not rps:
        rp = idf.newidfobject("RunPeriod")
        rp.Name = "P_Probe_FullYear"
        rp.Begin_Month = 1
        rp.Begin_Day_of_Month = 1
        rp.End_Month = 12
        rp.End_Day_of_Month = 31
        if verbose:
            print("  [ensure-outputs] created full-year RunPeriod (none existed)")
    else:
        for rp in rps:
            changed = False

            def _asint(v):
                try:
                    return int(str(v).strip())
                except (TypeError, ValueError):
                    return None

            if _asint(getattr(rp, "Begin_Month", None)) != 1 or _asint(getattr(rp, "Begin_Day_of_Month", None)) != 1:
                rp.Begin_Month = 1
                rp.Begin_Day_of_Month = 1
                changed = True
            if _asint(getattr(rp, "End_Month", None)) != 12 or _asint(getattr(rp, "End_Day_of_Month", None)) != 31:
                rp.End_Month = 12
                rp.End_Day_of_Month = 31
                changed = True
            if verbose and changed:
                print(f"  [ensure-outputs] forced RunPeriod '{getattr(rp, 'Name', '')}' to full year")


# ---------------------------------------------------------------------------
# Step 5 -- SQL -> CSV extraction. Ports the query shape of Leg-2's
# eSim_bem_utils_3J/plotting.py::get_hourly_meter_data (ReportData/ReportDataDictionary,
# EnvironmentType=3, Hourly), reimplemented here restricted to the requested
# meters/variables and pivoted to one-column-per-series (stated in the Progress Log).
# ---------------------------------------------------------------------------
def _write_hourly_meters_csv(sql_path: str, out_csv: str) -> int:
    conn = sqlite3.connect(sql_path)
    try:
        placeholders = ",".join("?" * len(REQUIRED_METERS))
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, Name "
            "FROM ReportDataDictionary "
            f"WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name IN ({placeholders})",
            conn, params=REQUIRED_METERS,
        )
        if meta.empty:
            raise RuntimeError("no matching Hourly meter rows in ReportDataDictionary")
        idx_list = meta["ReportDataDictionaryIndex"].tolist()
        idx_placeholders = ",".join("?" * len(idx_list))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS idx, rd.Value AS value, rd.TimeIndex AS t "
            "FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({idx_placeholders}) "
            "ORDER BY rd.TimeIndex ASC",
            conn, params=idx_list,
        )
    finally:
        conn.close()

    idx_to_name = dict(zip(meta["ReportDataDictionaryIndex"], meta["Name"]))
    data["name"] = data["idx"].map(idx_to_name)
    pivot = data.pivot_table(index="t", columns="name", values="value", aggfunc="sum")
    pivot = pivot.reindex(sorted(pivot.index))
    for m in REQUIRED_METERS:
        if m not in pivot.columns:
            pivot[m] = 0.0
    pivot = pivot[REQUIRED_METERS]
    pivot.to_csv(out_csv, index=False)
    return len(pivot)


def _build_zone_channel_map(idf) -> tuple[dict, list]:
    zone_to_channel = {}
    unknown_zones = []
    for sp in idf.idfobjects.get("SPACE", []):
        zone_name = str(getattr(sp, "Zone_Name", "") or getattr(sp, "Name", "")).strip()
        tag2 = _get_space_tag2(sp)
        from eSim_bem_utils.commercial_integration import classify_tag2  # local import, avoids top-level order issues
        fine = classify_tag2(tag2)
        agg = _FINE_TO_AGG.get(fine)
        if agg is None:
            unknown_zones.append(zone_name)
            continue
        # Canonical key = upper-cased, stripped. EnergyPlus writes zone/space names in
        # ReportDataDictionary.KeyValue in ALL-CAPS regardless of the IDF's own case
        # (e.g. IDF 'Basement_Corridor ZN' -> SQL 'BASEMENT_CORRIDOR ZN'). Building this
        # map in the IDF's mixed case caused a 100% join miss against the SQL side (every
        # KeyValue.map() -> NaN, dropna emptied the table) -- diagnosed job 1169671,
        # 2026-07-28. Upper-case is the canonical form here because that's what EnergyPlus
        # emits; the SQL-side KeyValue is normalized the same way in _write_channel_hourly_csv.
        zone_to_channel[zone_name.upper()] = agg
    return zone_to_channel, unknown_zones


def _write_channel_hourly_csv(sql_path: str, injected_idf_path: str, eplus_idd: str, out_csv: str) -> int:
    from eppy.modeleditor import IDF
    IDF.setiddname(eplus_idd)
    idf = IDF(injected_idf_path)
    zone_to_channel, unknown_zones = _build_zone_channel_map(idf)
    if unknown_zones:
        distinct = sorted(set(unknown_zones))
        print(f"  [channel_hourly] {len(distinct)} distinct Space/zone names did not classify to a "
              f"known channel (<=10 shown): {distinct[:10]}")

    conn = sqlite3.connect(sql_path)
    try:
        var_names = list(VAR_METRIC.keys())
        placeholders = ",".join("?" * len(var_names))
        meta = pd.read_sql_query(
            "SELECT ReportDataDictionaryIndex, KeyValue, Name "
            "FROM ReportDataDictionary "
            f"WHERE (ReportingFrequency = 'Hourly' OR ReportingFrequency = 3) AND Name IN ({placeholders})",
            conn, params=var_names,
        )
        if meta.empty:
            raise RuntimeError("no matching Hourly Zone-variable rows in ReportDataDictionary")
        idx_list = meta["ReportDataDictionaryIndex"].tolist()
        idx_placeholders = ",".join("?" * len(idx_list))
        data = pd.read_sql_query(
            "SELECT rd.ReportDataDictionaryIndex AS idx, rd.Value AS value, rd.TimeIndex AS t "
            "FROM ReportData rd "
            "JOIN Time tm ON rd.TimeIndex = tm.TimeIndex "
            "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
            f"WHERE ep.EnvironmentType = 3 AND rd.ReportDataDictionaryIndex IN ({idx_placeholders}) "
            "ORDER BY rd.TimeIndex ASC",
            conn, params=idx_list,
        )
    finally:
        conn.close()

    idx_meta = meta.set_index("ReportDataDictionaryIndex")[["KeyValue", "Name"]]
    df = data.join(idx_meta, on="idx")
    df["metric"] = df["Name"].map(VAR_METRIC)
    # Normalize the SQL-side join key the same way as zone_to_channel's keys (upper + strip)
    # -- EnergyPlus's ReportDataDictionary.KeyValue is ALL-CAPS regardless of the IDF's own
    # case, so a mixed-case join here silently produced 0 matches (100% NaN, dropna emptied
    # the table downstream) -- diagnosed job 1169671, 2026-07-28.
    df["channel"] = df["KeyValue"].astype(str).str.strip().str.upper().map(zone_to_channel)
    n_total = len(df)
    n_mapped = int(df["channel"].notna().sum())
    n_unmapped = n_total - n_mapped
    print(f"  [channel_hourly] mapped={n_mapped} unmapped={n_unmapped} (of {n_total} report rows)")
    if n_unmapped:
        distinct_unmapped = sorted(set(df.loc[df["channel"].isna(), "KeyValue"].astype(str)))
        print(f"  [channel_hourly] {len(distinct_unmapped)} distinct unmapped KeyValue strings "
              f"(<=10 shown, verbatim): {distinct_unmapped[:10]}")
    if n_mapped == 0:
        # Hard error: a 0-row channel_hourly.csv must never be written and silently counted as
        # "produced" (this is exactly how job 1169671 went unnoticed). A SMALL unmapped set is
        # expected and tolerated -- plenum Spaces carry no Tag-2 and no loads (4 such in Tall,
        # accepted-as-documented) -- but total non-mapping means the join key is broken again.
        raise RuntimeError(
            f"channel_hourly: 0 of {n_total} report rows mapped to a channel -- refusing to "
            f"write a 0-row channel_hourly.csv. Check zone_to_channel casing / Tag-2 census "
            f"(sample unmapped KeyValues: {sorted(set(df['KeyValue'].astype(str)))[:10]})"
        )
    df = df.dropna(subset=["channel", "metric"])
    df["col"] = df["channel"] + "_" + df["metric"]

    pivot = df.pivot_table(index="t", columns="col", values="value", aggfunc="sum")
    pivot = pivot.reindex(sorted(pivot.index))

    channels = ["office", "retail", "hotel", "residential", "service_MEP"]
    metrics = ["people", "lights", "equip"]
    all_cols = [f"{c}_{m}" for c in channels for m in metrics]
    for c in all_cols:
        if c not in pivot.columns:
            pivot[c] = 0.0
    pivot = pivot[all_cols]
    pivot.to_csv(out_csv, index=False)
    return len(pivot)


SQL_EXTRACTION_METHOD = (
    "reimplemented locally in this driver, porting the query shape of "
    "Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py::get_hourly_meter_data "
    "(ReportData/ReportDataDictionary join, EnvironmentType=3, Hourly), restricted "
    "to the requested meters/variables and pivoted to one column per series/channel"
)


def _do_postprocess(sql_path: str, injected_idf_path: str, eplus_idd: str, outdir: str,
                     manifest: dict) -> tuple[int, int]:
    """Step 5 (SQL -> hourly_meters.csv + channel_hourly.csv), shared by the normal
    inject-simulate-postprocess path and --postprocess-only. Mutates manifest in place;
    returns (rows_hourly, rows_channel) so the caller can apply the same row-count gate."""
    hourly_csv = os.path.join(outdir, "hourly_meters.csv")
    channel_csv = os.path.join(outdir, "channel_hourly.csv")
    rows_hourly = rows_channel = 0

    if os.path.isfile(sql_path):
        try:
            rows_hourly = _write_hourly_meters_csv(sql_path, hourly_csv)
            print(f"[postprocess] hourly_meters.csv: {rows_hourly} rows -> {hourly_csv}")
        except Exception as e:
            print(f"[FAIL] hourly_meters extraction raised: {e}")
            manifest["hourly_meters_exception"] = str(e)
        try:
            rows_channel = _write_channel_hourly_csv(sql_path, injected_idf_path, eplus_idd, channel_csv)
            print(f"[postprocess] channel_hourly.csv: {rows_channel} rows -> {channel_csv}")
        except Exception as e:
            print(f"[FAIL] channel_hourly extraction raised: {e}")
            manifest["channel_hourly_exception"] = str(e)
    else:
        print(f"[FAIL] eplusout.sql not found at {sql_path}")

    manifest["hourly_meters_csv"] = {
        "path": hourly_csv, "rows": rows_hourly,
        "md5": md5_file(hourly_csv) if os.path.isfile(hourly_csv) else None,
    }
    manifest["channel_hourly_csv"] = {
        "path": channel_csv, "rows": rows_channel,
        "md5": md5_file(channel_csv) if os.path.isfile(channel_csv) else None,
    }
    return rows_hourly, rows_channel


# ---------------------------------------------------------------------------
# Main -- one probe cell
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Run one 3J Leg-3 Step-8 §P probe cell.")
    ap.add_argument("--cell", type=int, required=True, help="index into the CELLS table (0-6)")
    ap.add_argument("--force-inj-hash", type=str, default=None,
                     help="P3(a) only: override INJ_HASH instead of computing md5(injector)[:8]")
    ap.add_argument("--postprocess-only", action="store_true",
                     help="Skip injection + EnergyPlus entirely; re-derive hourly_meters.csv "
                          "and channel_hourly.csv from the already-existing "
                          "<outdir>/run/eplusout.sql for this cell, and rewrite manifest.json. "
                          "Errors clearly if that sql file is absent. Lets a post-processing-only "
                          "fix (e.g. job 1169671) be applied to completed sims without re-simulating.")
    args = ap.parse_args()

    # INJ_HASH fingerprints the *injector* (commercial_integration.py) only, so a
    # post-processing-only change to THIS driver does not (and should not) invalidate the
    # simulation output path/campaign dir. But the provenance of the derived CSVs still has
    # to be traceable back to the exact driver code that produced them, so the driver's own
    # md5 is recorded separately in the manifest (see below).
    driver_md5 = md5_file(os.path.abspath(__file__))

    if not (0 <= args.cell < len(CELLS)):
        print(f"[FAIL] --cell {args.cell} out of range 0..{len(CELLS) - 1}")
        sys.exit(1)
    cell = CELLS[args.cell]
    tag = cell["tag"]

    # ---- 1. Injector fingerprint (the structural stale-output guard, §6b) ----
    if not os.path.isfile(INJECTOR_PY):
        print(f"[FAIL] injector not found at {INJECTOR_PY}")
        sys.exit(1)
    inj_hash = args.force_inj_hash if args.force_inj_hash else md5_file(INJECTOR_PY)[:8]
    outdir = os.path.join(PROBES_ROOT, f"campaign_{inj_hash}", tag)
    os.makedirs(outdir, exist_ok=True)
    print(f"[setup] cell={args.cell} tag={tag} INJ_HASH={inj_hash}")
    print(f"[setup] outdir={outdir}")
    print(f"[setup] source IDF={IDF_SUPERTALL}")

    eplus_idd = os.environ.get("EPLUS_IDD", "")
    if not eplus_idd or not os.path.isfile(eplus_idd):
        print(f"[FAIL] EPLUS_IDD not set or file missing: '{eplus_idd}'")
        sys.exit(1)

    # ---- --postprocess-only: re-derive the two CSVs + manifest, no injection, no EnergyPlus ----
    if args.postprocess_only:
        injected_idf_path = os.path.join(outdir, "injected.idf")
        run_dir = os.path.join(outdir, "run")
        sql_path = os.path.join(run_dir, "eplusout.sql")
        if not os.path.isfile(sql_path):
            print(f"[FAIL] --postprocess-only: eplusout.sql not found at {sql_path} "
                  f"-- nothing to re-derive from (this cell must have been simulated already)")
            sys.exit(1)
        if not os.path.isfile(injected_idf_path):
            print(f"[FAIL] --postprocess-only: injected.idf not found at {injected_idf_path} "
                  f"-- needed to rebuild the Space->channel map")
            sys.exit(1)

        manifest_path = os.path.join(outdir, "manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"[postprocess-only] loaded existing manifest: {manifest_path}")
        else:
            print(f"[postprocess-only] no existing manifest at {manifest_path}; starting fresh "
                  f"(channels_requested/inject_mixed_use_result will be absent)")
            manifest = {
                "cell_index": args.cell, "cell_tag": tag, "scenario_label": tag,
                "INJ_HASH": inj_hash, "outdir": outdir, "channels_requested": {},
            }
        manifest["driver_md5"] = driver_md5
        manifest["postprocess_only"] = True

        rows_hourly, rows_channel = _do_postprocess(sql_path, injected_idf_path, eplus_idd, outdir, manifest)
        manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["sql_extraction_method"] = SQL_EXTRACTION_METHOD
        _write_manifest(outdir, manifest)

        exit_rc = 0
        if rows_hourly != 8760:
            print(f"[FAIL] hourly_meters.csv row count = {rows_hourly}, expected 8760")
            exit_rc = 1
        if rows_channel != 8760:
            print(f"[FAIL] channel_hourly.csv row count = {rows_channel}, expected 8760")
            exit_rc = 1
        print(f"[done] cell={args.cell} tag={tag} postprocess-only exit={exit_rc}")
        sys.exit(exit_rc)

    try:
        from eppy.modeleditor import IDF
    except ImportError as e:
        print(f"[FAIL] eppy not importable: {e}")
        sys.exit(1)
    try:
        from eSim_bem_utils.commercial_integration import inject_mixed_use
    except ImportError as e:
        print(f"[FAIL] cannot import eSim_bem_utils.commercial_integration: {e}")
        sys.exit(1)

    IDF.setiddname(eplus_idd)

    manifest = {
        "cell_index": args.cell,
        "cell_tag": tag,
        "scenario_label": tag,
        "INJ_HASH": inj_hash,
        "driver_md5": driver_md5,
        "outdir": outdir,
        "channels_requested": {},
    }
    for ch, cfg in cell["channels"].items():
        csv_path = cfg.get("csv", "")
        exists = bool(csv_path) and os.path.isfile(csv_path)
        manifest["channels_requested"][ch] = {
            "csv_path": csv_path,
            "csv_md5": md5_file(csv_path) if exists else None,
            "exists": exists,
            **{k: v for k, v in cfg.items() if k != "csv"},
        }

    # ---- 2. Inject ----
    injected_idf_path = os.path.join(outdir, "injected.idf")
    building_meta = {
        "building": "SuperTall", "city": "MTL", "cz": "Z6",
        "purpose": "P-probe", "cell_index": args.cell, "scenario_label": tag,
    }
    try:
        inj_result = inject_mixed_use(IDF_SUPERTALL, injected_idf_path, cell["channels"],
                                       building_meta, verbose=True)
    except Exception as e:
        print(f"[FAIL] inject_mixed_use raised: {e}")
        manifest["inject_exception"] = str(e)
        _write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["inject_mixed_use_result"] = inj_result
    fallback = sorted(set(inj_result.get("fallback", [])))
    banner_lines = []
    if fallback:
        manifest["FALLBACK_LOUD"] = fallback
        for ch in fallback:
            line = f"!!! FALLBACK: {ch} reverted to NECB baseline !!!"
            print(line)
            banner_lines.append(line)
    manifest["banner_lines"] = banner_lines

    # ---- 3. Ensure outputs on the injected IDF (every path, no exceptions) ----
    try:
        idf = IDF(injected_idf_path)
        _ensure_output_objects(idf, verbose=True)
        idf.saveas(injected_idf_path)
    except Exception as e:
        print(f"[FAIL] ensure-outputs step raised: {e}")
        manifest["ensure_outputs_exception"] = str(e)
        _write_manifest(outdir, manifest)
        sys.exit(1)

    manifest["injected_idf_md5"] = md5_file(injected_idf_path)

    # ---- 4. Simulate ----
    epwrap_dir = os.path.join(outdir, "epwrap")
    os.makedirs(epwrap_dir, exist_ok=True)
    wrapper_path = os.path.join(epwrap_dir, "energyplus")
    with open(wrapper_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"singularity exec --bind /speed-scratch --bind /nfs/speed-scratch {SIF} {SIF_EXE} \"$@\"\n")
    os.chmod(wrapper_path, 0o755)

    run_dir = os.path.join(outdir, "run")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[sim] launching EnergyPlus: wrapper={wrapper_path}")
    print(f"[sim] args: -w {EPW} -d {run_dir} {injected_idf_path}")
    import subprocess
    proc = subprocess.run([wrapper_path, "-w", EPW, "-d", run_dir, injected_idf_path])
    ep_rc = proc.returncode
    manifest["ep_return_code"] = ep_rc
    print(f"[sim] EnergyPlus return code = {ep_rc}")

    # ---- 5. Post-process ----
    sql_path = os.path.join(run_dir, "eplusout.sql")
    rows_hourly, rows_channel = _do_postprocess(sql_path, injected_idf_path, eplus_idd, outdir, manifest)
    manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["sql_extraction_method"] = SQL_EXTRACTION_METHOD

    _write_manifest(outdir, manifest)

    # ---- 7. Exit non-zero on EP failure or wrong row counts ----
    exit_rc = 0
    if ep_rc != 0:
        print(f"[FAIL] EnergyPlus exited nonzero ({ep_rc})")
        exit_rc = 1
    if rows_hourly != 8760:
        print(f"[FAIL] hourly_meters.csv row count = {rows_hourly}, expected 8760")
        exit_rc = 1
    if rows_channel != 8760:
        print(f"[FAIL] channel_hourly.csv row count = {rows_channel}, expected 8760")
        exit_rc = 1

    print(f"[done] cell={args.cell} tag={tag} exit={exit_rc}")
    sys.exit(exit_rc)


if __name__ == "__main__":
    main()
