# -*- coding: utf-8 -*-
"""4J Step 10 --- THE REAL-STOCK CAMPAIGN.  Work items 10.3 / 10.7 / 10.10.

Authority: `2026-08-28_Step10_closure_questions_for_the_author.md` section 6 ---
Q1 (a), Q2 (a), Q3 (a), Q4 (a), ruled by the author 2026-08-28.

WHAT THIS IS
------------
41 real footprints x 5 f-levels = 205 EnergyPlus cells, run locally on
EnergyPlus 23.1.0.  Two arms, never pooled:

  ARM D  18 buildings, `DWELLING_LAYOUT_EMITTED`, one INDEPENDENT diary per
         dwelling zone.  This is the only population in the whole project in
         which `N_u > 1`.
  ARM F  23 buildings, `FALLBACK_PENDING_LAYOUT`, one diary for the whole
         building repeated across its storey zones.  `G10.22` calls this a
         LOWER BOUND, and it is here to be that bound, not to be averaged in.

WHAT IT IS NOT
--------------
* It is NOT the EU archetype campaign.  That campaign (`EU-08`, 395 cells of the
  frozen 510-cell spec) carries ONE `presence_hid` per cell, so `N_u = 1`
  everywhere and it cannot test `H10` at all.  `D-EU-31` governs it and is
  scoped to it (Q4 (a)); nothing here quotes a certified-cell number.
* It is NOT a measured-accuracy claim.  Step 10 section 11 forbids one, and the
  heating figures here are HEATING-ONLY (Zone Ideal Loads hourly variable), with
  no lighting, no appliances, no DHW and no cooling --- the same two-end-use
  model `FINDING 169` / `FINDING 171` measured on `S3`.
* It is NOT a national stock claim.  The corpus is the Lyon
  (`FR-LYO-HAUTCOEURPENTES`) footprint census; the `ES` / `GB` / `IT` labels are
  the 10.4 exercise's DIARY-AND-WEATHER relabelling and nothing more.  The
  envelope is each building's own observed FR TABULA archetype, taken from the
  census, never re-derived here.

THE ONE THING THIS CAMPAIGN EXISTS TO MEASURE
---------------------------------------------
`CF(N_u) = P_peak,building / sum_z P_peak,z`, per building, per f.  Arm D gives
`N_u` in 2..28; Arm F gives `N_u = 1` by construction at every zone count, which
is the control that proves `CF < 1` in Arm D is diversity and not zone count.

`G10.19` requires 30 dwelling-partitioned buildings PER FOLD and the corpus has
es 9 / uk 5 / it 3.  It is therefore recorded FAIL-by-population, permanently,
and `H10` is reported as INFO with `N` declared and residuals shown.  That was
ruled, in writing, before this file ran.

SIX PREFLIGHT REFUSALS, none downgradeable
------------------------------------------
  R1  prereg.md md5 != e4243e07cdd80c9c846b91f40e3e8c45
  R2  building table sha256 changed
  R3  layout census sha256 changed  (the geometry authority)
  R4  EnergyPlus binary is not 23.1  (the manifest cannot disagree with itself)
  R5  cell count != 41 x 5
  R6  run order is not deterministic

Usage:
    python 4thJ_step10_realstock_campaign.py --dry-run
    python 4thJ_step10_realstock_campaign.py --workers 6
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOURJ = HERE.parent
OPENUBEM_ROOT = Path(os.environ.get("OPENUBEM_ROOT", r"C:/Users/o_iseri/Desktop/OpenUBEM"))
if str(OPENUBEM_ROOT) not in sys.path:
    sys.path.insert(0, str(OPENUBEM_ROOT))

BUILDING_TABLE = FOURJ / "Step10_docs/outputs_step10/building_table_exercise_es_uk_it.csv"
CENSUS_PATH = OPENUBEM_ROOT / "openubem/outputs/eu_evidence/EU-04/s1_layout_reachability_census.csv"
MANIFEST_GPKG = OPENUBEM_ROOT / "openubem/outputs/eu02/FR-LYO-HAUTCOEURPENTES/02_residential_manifest.gpkg"
FR_ARCHETYPES = OPENUBEM_ROOT / "openubem/data/construction/tabula_archetypes_fr.json"
WEATHER_DIR = OPENUBEM_ROOT / "openubem/data/weather"
WEATHER_REGISTRY = WEATHER_DIR / "weather_registry.json"
PREREG = FOURJ / "Step6_docs/outputs_step6/prereg.md"
PREREG_MD5 = "e4243e07cdd80c9c846b91f40e3e8c45"

DEFAULT_OUT = FOURJ / "Step10_docs/outputs_step10/realstock_campaign"
DEFAULT_RUN_ROOT = Path(r"C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/step10_realstock")

#: `D-S10-1` Option A, ruled 2026-08-26 --- the pinned majority calendar year per fold.
FOLD_EPW = {
    "es": "es_madrid_2009_2010_y2010.epw",
    "uk": "uk_london_2014_2015_y2014.epw",
    "it": "it_bologna_2013_2014_y2014.epw",
}
COUNTRY_TO_FOLD = {"ES": "es", "GB": "uk", "IT": "it"}
F_LEVELS = (0.00, 0.15, 0.30, 0.50, 1.00)
ARM_D_SOURCE = "EUROPEAN_DWELLING_LAYOUT"
ARM_F_SOURCE = "FALLBACK_ONE_ZONE_PER_FLOOR"
CHAINING_RULE = "independent"          # the `10.1` closure notice's lift, by identity
FLOOR_TO_FLOOR_M = 3.0
J_TO_KWH = 1.0 / 3.6e6
REQUIRED_EP_VERSION = "23.1"
EXPECTED_BUILDINGS = 41
EXPECTED_CASES = ("A", "B")
RETAIN_RUN_DIRS = 4                    # the Step 8 / 10.4 precedent: score all, keep a sample

# A diverging heat balance that EnergyPlus still calls a success.  Screened here
# because no gate downstream of this file can see it.
UNSTABLE_MARKERS = (
    "Temperature out of range",
    "CalcHeatBalanceInsideSurf",
    "Inside surface heat balance did not converge",
    "Zone Air Heat Balance did not converge",
)


class PreflightError(RuntimeError):
    """A refusal raised before any cell is built.  Never downgraded to a warning."""


# ---------------------------------------------------------------------------
# digests
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def energyplus_version(exe: Path) -> str:
    out = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=60)
    text = (out.stdout or "") + (out.stderr or "")
    m = re.search(r"(\d+\.\d+\.\d+[-\w]*)", text)
    if not m:
        raise PreflightError("EnergyPlus did not report a version: %r" % text[:200])
    return m.group(1)


# ---------------------------------------------------------------------------
# 10.4's assignment, imported rather than restated
# ---------------------------------------------------------------------------
def load_paired_module():
    """10.9 pairing, imported rather than restated.

    `G10.20` requires BOTH cases on the same footprint, archetype, weather, `f`
    and seed policy.  Reproducing that pairing here rather than importing it
    would make the simulated pair a different pair from the emitted one.
    """
    spec = importlib.util.spec_from_file_location(
        "s10paired", str(HERE / "4thJ_step10_paired.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------
def preflight(cells, energyplus_exe: Path) -> dict:
    if not PREREG.is_file():
        raise PreflightError("R1 prereg.md is not on disk: %s" % PREREG)
    live = md5_file(PREREG)
    if live != PREREG_MD5:
        raise PreflightError("R1 prereg.md md5 %s != frozen %s" % (live, PREREG_MD5))
    if not BUILDING_TABLE.is_file():
        raise PreflightError("R2 building table missing: %s" % BUILDING_TABLE)
    if not CENSUS_PATH.is_file():
        raise PreflightError("R3 layout census missing: %s" % CENSUS_PATH)
    version = energyplus_version(energyplus_exe)
    if not version.startswith(REQUIRED_EP_VERSION):
        raise PreflightError(
            "R4 EnergyPlus is %s; this campaign is pinned to %s. A 23.1-labelled "
            "manifest written by another binary is unfalsifiable afterwards."
            % (version, REQUIRED_EP_VERSION))
    n_buildings = len({c["building_id"] for c in cells})
    if n_buildings != EXPECTED_BUILDINGS:
        raise PreflightError("R5 building count is %d, expected %d"
                             % (n_buildings, EXPECTED_BUILDINGS))
    expected = EXPECTED_BUILDINGS * len(EXPECTED_CASES) * len(F_LEVELS)
    if len(cells) != expected:
        raise PreflightError("R5 cell count is %d, expected %d" % (len(cells), expected))
    cases = {c["case"] for c in cells}
    if cases != set(EXPECTED_CASES):
        raise PreflightError("R5 cases present are %r, expected %r"
                             % (sorted(cases), EXPECTED_CASES))
    # G10.20 own pairing clause, enforced BEFORE the campaign rather than scored after it.
    per_building = {}
    for cell in cells:
        per_building.setdefault((cell["building_id"], cell["sensitivity_f"]), set()).add(cell["case"])
    unpaired = [k for k, v in per_building.items() if v != set(EXPECTED_CASES)]
    if unpaired:
        raise PreflightError("R5 %d (building, f) pairs are missing a case: %r"
                             % (len(unpaired), unpaired[:3]))
    order = [c["cell_id"] for c in cells]
    if order != sorted(order):
        raise PreflightError("R6 run order is not deterministic")
    if len(set(order)) != len(order):
        raise PreflightError("R6 cell ids are not unique")
    registry = json.loads(WEATHER_REGISTRY.read_text(encoding="utf-8"))
    weather = {}
    for fold, name in FOLD_EPW.items():
        path = WEATHER_DIR / name
        if not path.is_file():
            raise PreflightError("pinned EPW missing for fold %s: %s" % (fold, path))
        weather[fold] = {"epw": name, "sha256": sha256_file(path)}
    return {
        "prereg_md5": live,
        "building_table_sha256": sha256_file(BUILDING_TABLE),
        "layout_census_sha256": sha256_file(CENSUS_PATH),
        "manifest_gpkg_sha256": sha256_file(MANIFEST_GPKG),
        "energyplus_version_measured": version,
        "n_buildings": n_buildings,
        "n_cells": len(cells),
        "weather": weather,
        "weather_registry_sha256": sha256_file(WEATHER_REGISTRY),
        "registry_entries": len(registry) if isinstance(registry, (list, dict)) else None,
    }


# ---------------------------------------------------------------------------
# the cell list
# ---------------------------------------------------------------------------
def build_cells(paired_mod, seed_base: int = 1):
    """One record per (building, case, f).  The pairing is 10.9, byte-for-byte."""
    import pandas as pd

    assign_mod = paired_mod.A
    rows = assign_mod.read_building_table(str(BUILDING_TABLE))
    # The population is the layout STATUS, not the zone source: 256 rows are
    # REFUSED_BY_LAYOUT_CONTRACT and also carry the fallback zone source.
    rows = [r for r in rows
            if r["layout_status"] in ("DWELLING_LAYOUT_EMITTED", "FALLBACK_PENDING_LAYOUT")]
    by_fold, _by_name = assign_mod.step7_index()
    assignments, skipped = paired_mod.build_pairs(rows, by_fold, seed_base=seed_base)
    if skipped:
        raise PreflightError("pairing skipped %d rows and this campaign refuses to run "
                             "a partial population: %r" % (len(skipped), skipped[:3]))

    census = pd.read_csv(CENSUS_PATH).set_index("building_id")
    grouped = {}
    for a in assignments:
        grouped.setdefault((a["building_id"], a["case"]), []).append(a)
    for units in grouped.values():
        units.sort(key=lambda u: u["unit_index"])

    table = {r["building_id"]: r for r in rows}
    cells = []
    for key in sorted(grouped):
        building_id, case = key
        units = grouped[key]
        row = table[building_id]
        arm = "D" if row["zone_source"] == ARM_D_SOURCE else "F"
        fold = COUNTRY_TO_FOLD[row["country"]]
        crow = census.loc[building_id]
        # `N_u` is the number of INDEPENDENT diaries, never the zone count.
        n_u = len({u["presence_md5"] for u in units})
        for f in F_LEVELS:
            cells.append({
                "cell_id": "%s__%s__case%s__f%03d"
                           % (fold, building_id, case, int(round(f * 100))),
                "building_id": building_id,
                "case": case,
                "zone_semantics": units[0]["zone_semantics"],
                "country": row["country"],
                "fold": fold,
                "arm": arm,
                "layout_status": row["layout_status"],
                "zone_source": row["zone_source"],
                "zone_count_declared": row["zone_count"],
                "n_u": n_u,
                "sensitivity_f": f,
                "archetype_id": str(crow["archetype_id"]),
                "building_type": str(crow["building_type"]),
                "observed_dwellings": int(crow["observed_dwellings"]),
                "observed_storeys": int(crow["observed_storeys"]),
                "footprint_area_m2": float(row["footprint_area_m2"]),
                "units": units,
            })
    cells.sort(key=lambda c: c["cell_id"])
    return cells


# ---------------------------------------------------------------------------
# geometry and IDF
# ---------------------------------------------------------------------------
def load_fr_record(archetype_id: str) -> dict:
    records = json.loads(FR_ARCHETYPES.read_text(encoding="utf-8"))["records"]
    for record in records:
        if record["archetype_id"] == archetype_id:
            return record
    raise ValueError("FR TABULA archetype not in registry: %r" % archetype_id)


def build_zones_for_cell(cell, manifest):
    """Zones re-derived from the real footprint, never from the CSV's zone_count."""
    from shapely.geometry.polygon import orient
    from openubem.geometry.european_residential import (
        allocate_european_dwellings,
        european_layout_to_zone_specs,
        generate_european_dwelling_layout,
    )
    from openubem.geometry.zoning import build_zones

    building_id = cell["building_id"]
    matches = manifest.loc[manifest["osm_id"].astype(str) == building_id, "geometry"]
    if matches.empty:
        raise ValueError("building_id missing from the Lyon manifest: %r" % building_id)
    footprint = matches.iloc[0]
    allocation = allocate_european_dwellings(
        archetype_id=cell["archetype_id"],
        building_type=cell["building_type"],
        n_apartment=cell["observed_dwellings"],
        n_storey=cell["observed_storeys"],
        plate_area_m2=float(footprint.area),
    )
    # 🔴 ONE FLOOR IS NOT THE BUILDING.  `european_layout_to_zone_specs` emits a
    # single storey; the census's dwelling count is the whole building.  Emitting
    # only the first floor would silently discard every diary above it and turn an
    # `N_u = 11` building into an `N_u = 3` one WITHOUT failing anything.  The
    # allocation's own per-storey table is the authority, and `floor_index` /
    # `z_floor_m` are the hooks it is meant to be read through.
    probe = generate_european_dwelling_layout(
        footprint, requested_dwelling_count=allocation.units_per_floor)
    # 🔴 THE CENSUS DECIDES THE ARM, NOT THE PROBE.  `s1_layout_reachability_census.csv`
    # is pinned by refusal `R3` and is the geometry authority; four Arm F buildings
    # (`PARTITION_AUDIT_FAILED`) DO emit a layout when re-probed at `units_per_floor`,
    # because the census audited a different requested count.  Letting a successful
    # probe promote them into Arm D would manufacture `N_u > 1` for buildings the
    # census refused to partition.  The disagreement is RECORDED, never acted on.
    want_dwelling_route = cell["arm"] == "D"
    cell["probe_emitted"] = bool(probe.dwelling_layout_emitted)
    cell["probe_disagrees_with_census_arm"] = bool(
        probe.dwelling_layout_emitted != want_dwelling_route)
    if want_dwelling_route and not probe.dwelling_layout_emitted:
        raise ValueError(
            "census says Arm D for %s but the layout contract refuses %d dwellings "
            "per floor (%s); the building is refused rather than downgraded"
            % (building_id, allocation.units_per_floor, probe.fallback_reason))
    if want_dwelling_route:
        zones = []
        empty_storeys = 0
        for floor in allocation.floor_allocations:
            # `D-EU-01` gives floors the quotient dwelling count plus a remainder to
            # the first storeys, so a building with fewer dwellings than storeys has
            # storeys carrying ZERO dwellings. Those storeys have no conditioned
            # dwelling zone; the allocation says so, and the census zone count counts
            # dwellings, not storeys. Skipping them is what keeps the two agreeing.
            if floor.dwelling_count <= 0:
                empty_storeys += 1
                continue
            floor_layout = generate_european_dwelling_layout(
                footprint, requested_dwelling_count=floor.dwelling_count)
            if not floor_layout.dwelling_layout_emitted:
                raise ValueError(
                    "storey %d of %s requests %d dwellings and the layout contract "
                    "refuses it (%s); the building is refused rather than partially built"
                    % (floor.storey_index, building_id, floor.dwelling_count,
                       floor_layout.fallback_reason))
            zones.extend(european_layout_to_zone_specs(
                floor_layout, building_id=building_id,
                floor_index=floor.storey_index,
                z_floor_m=floor.storey_index * FLOOR_TO_FLOOR_M,
                height_m=FLOOR_TO_FLOOR_M))
        layout = probe
        emitted = True
        cell["storeys_without_a_dwelling"] = empty_storeys
    else:
        layout = probe
        cell["storeys_without_a_dwelling"] = 0
        zones = build_zones(
            building_id, footprint, cell["archetype_id"],
            num_floors=int(cell["observed_storeys"]),
            strategy="one_zone_per_floor", floor_to_floor_m=FLOOR_TO_FLOOR_M,
        )
        emitted = False
    for zone in zones:
        oriented = orient(zone["floor_polygon"], sign=1.0)
        zone["floor_polygon"] = oriented
        zone["coords_m"] = list(oriented.exterior.coords)[:-1]
    # The arm was decided by the census; the route above was driven by it, so this
    # is a self-check on the branch taken, not a second opinion on the geometry.
    if emitted != (cell["arm"] == "D"):
        raise ValueError(
            "geometry route disagrees with the census arm for %s: emitted=%s arm=%s"
            % (building_id, emitted, cell["arm"]))
    return zones, layout.status


def build_idf_for_cell(cell, record, zones, run_dir: Path, epw_path: Path, paired_mod):
    from geomeppy import IDF
    from eppy.modeleditor import IDDAlreadySetError
    from openubem.config import ENERGYPLUS_IDD_PATH
    from openubem.idf.european_controls import add_european_heating_controls
    from openubem.idf.european_physics import add_european_internal_mass, add_nomass_construction
    from openubem.idf.builder import write_zone_volumes
    from openubem.idf.surfaces import extrude_geometry
    from openubem.semantic.european_schedules import emit_step8_gain_schedule
    from scripts.run_eu_s2_campaign import IDF_HEADER_TEMPLATE

    try:
        IDF.setiddname(str(ENERGYPLUS_IDD_PATH))
    except IDDAlreadySetError:
        pass

    with epw_path.open(encoding="utf-8", errors="replace") as stream:
        fields = stream.readline().strip().split(",")
    city = fields[1]
    latitude, longitude, time_zone, elevation = (float(v) for v in fields[6:10])

    run_dir.mkdir(parents=True, exist_ok=True)
    idf_path = run_dir / ("%s.idf" % cell["cell_id"])
    idf_path.write_text(
        IDF_HEADER_TEMPLATE.format(city=city, latitude=latitude, longitude=longitude,
                                   time_zone=time_zone, elevation=elevation),
        encoding="utf-8")
    idf = IDF(str(idf_path))
    extrude_geometry(idf, zones, [])
    write_zone_volumes(idf, zones)

    def construction(component):
        f_red = float(record["f_red_temp"])
        return add_nomass_construction(
            idf, "EU_%s" % component,
            float(record["u_%s_w_m2k" % component]) * f_red,
            float(record["delta_u_tb_w_m2k"]) * f_red)

    wall, roof, floor = construction("wall"), construction("roof"), construction("floor")
    for surface in idf.idfobjects["BUILDINGSURFACE:DETAILED"]:
        kind = str(surface.Surface_Type).upper()
        if kind == "WALL":
            surface.Construction_Name = wall
        elif kind in ("ROOF", "ROOFCEILING"):
            surface.Construction_Name = roof
        elif kind in ("FLOOR", "CEILING"):
            surface.Construction_Name = floor

    f = cell["sensitivity_f"]
    units = cell["units"]
    schedules = []
    for index, zone in enumerate(zones):
        # 🔴 The unit list is 10.4's, and its length is the census zone_count. If the
        # geometry emits a different number of zones the mapping is not defined and
        # the cell is refused rather than silently recycled.
        if index >= len(units):
            raise ValueError("zone %d has no assigned dwelling for %s (units=%d, zones=%d)"
                             % (index, cell["building_id"], len(units), len(zones)))
        unit = units[index]
        area = float(zone["floor_polygon"].area)
        add_european_internal_mass(idf, zone["name"], area,
                                   c_m_wh_m2k=float(record["c_m_wh_m2k"]))
        idf.newidfobject(
            "SIZING:ZONE", Zone_or_ZoneList_Name=zone["name"],
            Zone_Cooling_Design_Supply_Air_Temperature_Input_Method="SupplyAirTemperature",
            Zone_Cooling_Design_Supply_Air_Temperature=13.0,
            Zone_Heating_Design_Supply_Air_Temperature_Input_Method="SupplyAirTemperature",
            Zone_Heating_Design_Supply_Air_Temperature=50.0,
            Zone_Cooling_Design_Supply_Air_Humidity_Ratio=0.008,
            Zone_Heating_Design_Supply_Air_Humidity_Ratio=0.008,
        )
        names = add_european_heating_controls(idf, record, zone["name"])
        legacy = idf.getobject("OTHEREQUIPMENT", names["gains"])
        if legacy is not None:
            idf.removeidfobject(legacy)
        limits = idf.getobject("SCHEDULETYPELIMITS", "EU_Step8_AnyNumber_Wm2")
        if limits is not None:
            idf.removeidfobject(limits)
        presence = None
        if f > 0.0:
            presence = paired_mod.S.read_presence(unit["presence_path"])
        info = emit_step8_gain_schedule(
            idf,
            sensitivity_f=f,
            dwelling_zone=zone["name"],
            dwelling_id=zone["name"],
            emitted_csv_path=run_dir / ("%s_gain.csv" % zone["name"]),
            presence=presence,
            chaining_rule=CHAINING_RULE if f > 0.0 else None,
        )
        schedules.append({
            "zone": zone["name"], "unit_index": unit["unit_index"],
            "presence_file": unit["presence_file"], "presence_md5": unit["presence_md5"],
            "seed": unit["seed"], "independent": unit["independent"],
            "gain_sha256": info["sha256"], "mean_phi_int_w_m2": info["mean_phi_int_w_m2"],
            "zone_area_m2": area,
        })

    # 🔴 PORTABLE SCHEDULE PATHS. `emit_step8_gain_schedule` writes an ABSOLUTE
    # Windows path into `Schedule:File`, which cannot resolve on Speed. EnergyPlus
    # resolves a bare file name against the run directory, and the run directory is
    # exactly where the CSV already sits. Rewriting to the basename makes the SAME
    # IDF BYTES valid on both platforms --- which is the only way the platform arm
    # compares PLATFORMS rather than comparing two different files.
    for sched in idf.idfobjects["SCHEDULE:FILE"]:
        sched.File_Name = str(sched.File_Name).replace("\\", "/").rsplit("/", 1)[-1]

    idf.newidfobject("OUTPUT:VARIABLE", Key_Value="*",
                     Variable_Name="Zone Ideal Loads Zone Total Heating Energy",
                     Reporting_Frequency="Hourly")
    idf.saveas(str(idf_path))
    return idf_path, schedules


# ---------------------------------------------------------------------------
# run and extract
# ---------------------------------------------------------------------------
def parse_hourly_heating(csv_path: Path):
    """Return (zone_names, per-zone hourly J lists).  Read from the file EnergyPlus wrote."""
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("eplusout.csv has no header: %s" % csv_path)
        columns = [c for c in reader.fieldnames
                   if "zone ideal loads zone total heating energy" in c.casefold()
                   and "[j]" in c.casefold() and "(hourly)" in c.casefold()]
        if not columns:
            raise ValueError("eplusout.csv lacks the hourly heating variable: %s" % csv_path)
        series = {c: [] for c in columns}
        for row in reader:
            for c in columns:
                series[c].append(float(row[c]))
    return columns, series


def percentile_linear(sorted_values, q):
    """Linear-interpolation percentile, the definition 10.9 already scored q99 with."""
    if not sorted_values:
        raise ValueError("no values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def cell_metrics(columns, series):
    n_hours = len(next(iter(series.values())))
    zone_totals = {c: sum(v) for c, v in series.items()}
    zone_peaks = {c: max(v) for c, v in series.items()}
    building_hourly = [sum(series[c][h] for c in columns) for h in range(n_hours)]
    p_peak_building_j = max(building_hourly)
    sum_zone_peaks_j = sum(zone_peaks.values())
    peak_hour = building_hourly.index(p_peak_building_j)
    cf = (p_peak_building_j / sum_zone_peaks_j) if sum_zone_peaks_j > 0 else None
    # `G10.21`(i) asks for the 99th-percentile hourly power BESIDE the peak.
    # `FINDING 159` measured q99 == peak in 2,970 of 2,970 cells on the emitted
    # phi channel; whether that survives the thermal response is exactly what a
    # simulated cell can answer, so it is recorded here rather than assumed.
    ordered = sorted(building_hourly)
    q99_j = percentile_linear(ordered, 0.99)
    return {
        "n_hours": n_hours,
        "annual_heating_kwh": sum(zone_totals.values()) * J_TO_KWH,
        "peak_hourly_building_kw": p_peak_building_j / 3.6e6,
        "sum_zone_peaks_kw": sum_zone_peaks_j / 3.6e6,
        "coincidence_factor": cf,
        "peak_hour_index_0based": peak_hour,
        "q99_hourly_building_kw": q99_j / 3.6e6,
        "q99_equals_peak": bool(q99_j == p_peak_building_j),
        "n_zone_columns": len(columns),
    }


def run_cell(cell, args, manifest, paired_mod, energyplus_exe: Path, keep: set):
    started = time.time()
    fold = cell["fold"]
    epw_path = WEATHER_DIR / FOLD_EPW[fold]
    run_dir = Path(args.run_root) / cell["cell_id"]
    record = {
        "cell_id": cell["cell_id"], "building_id": cell["building_id"],
        "country": cell["country"], "fold": fold, "arm": cell["arm"],
        "case": cell["case"], "zone_semantics": cell["zone_semantics"],
        "layout_status": cell["layout_status"], "zone_source": cell["zone_source"],
        "archetype_id": cell["archetype_id"], "building_type": cell["building_type"],
        "observed_dwellings": cell["observed_dwellings"],
        "observed_storeys": cell["observed_storeys"],
        "footprint_area_m2": cell["footprint_area_m2"],
        "sensitivity_f": cell["sensitivity_f"], "n_u": cell["n_u"],
        "zone_count_declared": cell["zone_count_declared"],
        "chaining_rule": CHAINING_RULE if cell["sensitivity_f"] > 0 else "not_applicable_f0",
        "epw": FOLD_EPW[fold], "energyplus_version_declared": REQUIRED_EP_VERSION,
        "completed": False, "error": None,
    }
    try:
        zones, layout_status = build_zones_for_cell(cell, manifest)
        record["zone_count_built"] = len(zones)
        # 🔴 The gate that would have caught the one-floor bug. The census's zone
        # count IS the dwelling count for arm D and the storey count for arm F; a
        # geometry that builds fewer zones silently drops diaries and still runs.
        if len(zones) != cell["zone_count_declared"]:
            raise ValueError(
                "zone count built (%d) != census zone count (%d) for %s"
                % (len(zones), cell["zone_count_declared"], cell["building_id"]))
        record["layout_route_status"] = layout_status
        record["storeys_without_a_dwelling"] = cell.get("storeys_without_a_dwelling", 0)
        record["probe_emitted"] = cell.get("probe_emitted")
        record["probe_disagrees_with_census_arm"] = cell.get("probe_disagrees_with_census_arm")
        record["floor_area_m2"] = sum(float(z["floor_polygon"].area) for z in zones)
        tabula = load_fr_record(cell["archetype_id"])
        idf_path, schedules = build_idf_for_cell(cell, tabula, zones, run_dir, epw_path, paired_mod)
        record["idf_sha256"] = sha256_file(idf_path)
        record["n_distinct_presence"] = len({s["presence_md5"] for s in schedules})

        if getattr(args, "emit_only", False):
            # STAGE MODE. The author reversed `Q3` and ordered the campaign onto
            # Speed. Speed has no `shapely` and no `geopandas`, so the geometry is
            # NEVER rebuilt there: the IDF and its hourly gain schedules are emitted
            # HERE and shipped, and Speed runs EnergyPlus and nothing else. The
            # `idf_sha256` recorded above is what makes the two platforms comparable.
            record["emit_only"] = True
            record["schedules"] = schedules
            record["runtime_s"] = round(time.time() - started, 3)
            manifest_dir = Path(args.out) / "manifests"
            manifest_dir.mkdir(parents=True, exist_ok=True)
            (manifest_dir / ("%s.json" % cell["cell_id"])).write_text(
                json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            return record

        proc = subprocess.run(
            [str(energyplus_exe), "-w", str(epw_path), "-x", "-r", "-d", ".", str(idf_path)],
            cwd=run_dir, capture_output=True, text=True, timeout=args.timeout)
        err_path = run_dir / "eplusout.err"
        err_text = err_path.read_text(encoding="utf-8", errors="replace") if err_path.is_file() else ""
        record["eplus_return_code"] = proc.returncode
        record["severe_count"] = len(re.findall(r"\*\*\s*Severe\s*\*\*", err_text, re.I))
        record["fatal_count"] = len(re.findall(r"\*\*\s*Fatal\s*\*\*", err_text, re.I))
        record["unstable_markers"] = sum(1 for m in UNSTABLE_MARKERS if m in err_text)
        completed = (proc.returncode == 0 and "Completed Successfully" in err_text)
        if completed:
            columns, series = parse_hourly_heating(run_dir / "eplusout.csv")
            record.update(cell_metrics(columns, series))
            area = record["floor_area_m2"]
            record["eui_heating_kwh_m2"] = (record["annual_heating_kwh"] / area) if area > 0 else None
            record["completed"] = True
        record["schedules"] = schedules
    except Exception as exc:                                  # noqa: BLE001
        record["error"] = "%s: %s" % (type(exc).__name__, exc)
        record["traceback"] = traceback.format_exc()[-1500:]
    record["runtime_s"] = round(time.time() - started, 3)

    manifest_dir = Path(args.out) / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / ("%s.json" % cell["cell_id"])).write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    if cell["building_id"] not in keep and run_dir.is_dir() and not args.keep_all:
        # The measurement is already off disk; the run tree is 205 x tens of MB.
        for path in sorted(run_dir.rglob("*"), reverse=True):
            try:
                path.unlink() if path.is_file() else path.rmdir()
            except OSError:
                pass
        try:
            run_dir.rmdir()
        except OSError:
            pass
        record["run_dir_retained"] = False
    else:
        record["run_dir_retained"] = True
    return record


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--emit-only", action="store_true",
                    help="build every IDF and its schedules into --run-root and stop; "
                         "no EnergyPlus is invoked. This is the Speed staging mode.")
    ap.add_argument("--keep-all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="", help="substring filter on cell_id (smoke use only)")
    args = ap.parse_args()

    from openubem.config import ENERGYPLUS_PATH
    energyplus_exe = Path(ENERGYPLUS_PATH) / (
        "energyplus.exe" if sys.platform == "win32" else "energyplus")

    paired_mod = load_paired_module()
    cells = build_cells(paired_mod)
    checks = preflight(cells, energyplus_exe)
    if args.only:
        cells = [c for c in cells if args.only in c["cell_id"]]
    if args.limit:
        cells = cells[:args.limit]

    Path(args.out).mkdir(parents=True, exist_ok=True)
    keep = set(sorted({c["building_id"] for c in cells})[:RETAIN_RUN_DIRS])
    summary = {
        "campaign": "4J Step 10 real-stock campaign",
        "cases": {"A": "one diary replicated to every zone (synchronised control)",
                  "B": "N_u independent diaries, one per zone (the diversity case)"},
        "authority": "Step10_docs/docs/2026-08-28_Step10_closure_questions_for_the_author.md section 6, Q1(a) Q2(a) Q3(a) Q4(a)",
        "basis": "HEATING-ONLY, Zone Ideal Loads hourly variable. No lighting, no appliances, no DHW, no cooling.",
        "corpus_note": ("Lyon FR-LYO-HAUTCOEURPENTES footprint census; the ES/GB/IT labels are the "
                        "10.4 exercise's diary-and-weather relabelling and carry no national stock claim."),
        "d_eu_31_scope": "scoped to the 149 certified EU archetype cells (Q4(a)); no certified-cell number is used here",
        "f_levels": list(F_LEVELS),
        "arms": {"D": "DWELLING_LAYOUT_EMITTED, independent diary per dwelling zone",
                 "F": "FALLBACK_PENDING_LAYOUT, one diary repeated across storey zones (G10.22 lower bound)"},
        "preflight": checks,
        "n_cells": len(cells),
        "retained_run_dirs_for": sorted(keep),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    print(json.dumps({k: v for k, v in summary.items() if k != "preflight"}, indent=1))
    print("preflight OK: EnergyPlus %s, %d cells, %d buildings"
          % (checks["energyplus_version_measured"], len(cells), checks["n_buildings"]))
    if args.dry_run:
        (Path(args.out) / "campaign_summary_dryrun.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        for cell in cells[:5]:
            print("  %s case=%s arm=%s N_u=%d zones=%d"
                  % (cell["cell_id"], cell["case"], cell["arm"],
                     cell["n_u"], cell["zone_count_declared"]))
        return 0

    import geopandas as gpd
    manifest = gpd.read_file(MANIFEST_GPKG)

    results = []
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_cell, c, args, manifest, paired_mod, energyplus_exe, keep): c
                   for c in cells}
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            results.append(record)
            done += 1
            print("[%3d/%3d] %-58s %s %s" % (
                done, len(cells), record["cell_id"],
                "OK " if record["completed"] else "FAIL",
                ("CF=%.4f" % record["coincidence_factor"]) if record.get("coincidence_factor")
                else (record.get("error") or "")[:60]), flush=True)

    results.sort(key=lambda r: r["cell_id"])
    columns = ["cell_id", "building_id", "case", "zone_semantics", "country", "fold",
               "arm", "layout_status",
               "archetype_id", "building_type", "sensitivity_f", "n_u",
               "zone_count_declared", "zone_count_built", "n_distinct_presence",
               "storeys_without_a_dwelling", "probe_disagrees_with_census_arm",
               "floor_area_m2", "footprint_area_m2", "idf_sha256", "epw",
               "eplus_return_code", "severe_count", "fatal_count", "unstable_markers",
               "completed", "annual_heating_kwh", "eui_heating_kwh_m2",
               "peak_hourly_building_kw", "sum_zone_peaks_kw", "coincidence_factor",
               "q99_hourly_building_kw", "q99_equals_peak",
               "peak_hour_index_0based", "runtime_s", "error"]
    manifest_csv = Path(args.out) / "realstock_campaign_manifest.csv"
    with io.open(manifest_csv, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for record in results:
            writer.writerow(record)

    summary["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summary["completed_cells"] = sum(1 for r in results if r["completed"])
    summary["failed_cells"] = sum(1 for r in results if not r["completed"])
    summary["total_runtime_s"] = round(sum(r["runtime_s"] for r in results), 1)
    summary["manifest_csv"] = str(manifest_csv)
    summary["manifest_csv_sha256"] = sha256_file(manifest_csv)
    (Path(args.out) / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("completed %d of %d cells in %.1f s -> %s"
          % (summary["completed_cells"], len(results), summary["total_runtime_s"], manifest_csv))
    return 0 if summary["failed_cells"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
