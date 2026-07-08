"""extract_enduse_annual.py — Step 8 Fix v3 End-Uses extractor (2J port).

Ported from 3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/extract_enduse_annual.py
(2026-07-08). Reads AnnualBuildingUtilityPerformanceSummary / End Uses (Heating, Cooling) from
every campaign run's eplusout.sql and writes one row per run to agg_enduse_annual.csv. Stdlib
only (os, glob, csv, re, sqlite3) so it runs under any cluster python module. See
step8_enduse_rebase_implementation_plan.md and
step8_resid_heating_cooling_dominance_investigation.md SS7/SS11 (3J companion doc).

Cluster/full-campaign path only — NOT used in this pass (2JV3 runs entirely off the local
eplustbl.csv variant, extract_enduse_annual_from_tbl.py, per the zero-sbatch constraint). Ported
now so it's ready for the later full-campaign canonical regen (all 6,000 runs via sbatch) once
Speed compute is back.

Only the default path resolution changed vs the 3J original: 2J's outputs_step8/ sits directly
under 2J_docs_occ_nTemp/ (no intermediate Step8_docs/ layer), so OUT_PATH resolves one level
shallower. Cell/sample regexes unchanged (confirmed identical layout,
eSim_bem_utils_2J/main.py:2056).

Usage: py investigation/extract_enduse_annual.py
Env:   STEP8_CAMP_DIR (default /speed-scratch/o_iseri/step8_2j/campaign — placeholder, confirm
       actual 2J scratch root before cluster use)
       STEP8_ENDUSE_OUT (default <outputs_step8>/agg/agg_enduse_annual.csv)
"""
import csv
import glob
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # outputs_step8/investigation/
OUTPUTS_STEP8 = os.path.dirname(HERE)                       # outputs_step8/

CAMP_DIR = os.environ.get("STEP8_CAMP_DIR", "/speed-scratch/o_iseri/step8_2j/campaign")
OUT_PATH = os.environ.get(
    "STEP8_ENDUSE_OUT",
    os.path.join(OUTPUTS_STEP8, "agg", "agg_enduse_annual.csv"),
)

QUERY = """
    SELECT RowName, ColumnName, Value, Units FROM TabularDataWithStrings
    WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
      AND TableName='End Uses' AND RowName IN ('Heating','Cooling')
"""

# OutputControl:Table:Style's unit-conversion setting differs by archetype family
# (apartment prototypes = GJ/SI; house prototypes = kBtu/IP) — confirmed by inspecting
# eplustbl.csv headers across archetypes (2026-07-08). Convert everything to GJ so
# cross-archetype ratios (gate 4.9) are apples-to-apples.
_GJ_PER_UNIT = {"GJ": 1.0, "kBtu": 0.0010550559}


def _to_gj(value, units):
    try:
        mult = _GJ_PER_UNIT[units]
    except KeyError:
        raise ValueError(f"unrecognized End Uses unit {units!r} — extend _GJ_PER_UNIT")
    return value * mult

CELL_RE = re.compile(r"^(?P<arch>[^_]+(?:[A-Za-z]+)?)__(?P<city>[A-Za-z]+)_(?P<cz>[0-9A-Za-z]+)$")
SAMPLE_RE = re.compile(r"^sample_(?P<sample>\d+)_HH(?P<hh>\w+)$")

FIELDNAMES = [
    "cell", "arch", "city", "cz", "scenario", "sample", "hh_id",
    "heating_gas_GJ", "heating_elec_GJ", "heating_district_GJ",
    "cooling_elec_GJ", "cooling_gas_GJ", "cooling_district_GJ",
]


def _parse_cell(cell_name):
    m = CELL_RE.match(cell_name)
    if not m:
        return cell_name, "", ""
    return m.group("arch"), m.group("city"), m.group("cz")


def _parse_sample_dir(sample_dir):
    m = SAMPLE_RE.match(sample_dir)
    if not m:
        return "", ""
    return m.group("sample"), m.group("hh")


def _extract_end_uses(sql_path):
    """Return dict: {(RowName, ColumnName): float_GJ} for Heating/Cooling rows,
    unit-converted to GJ regardless of the run's OutputControl:Table:Style setting."""
    conn = sqlite3.connect(sql_path)
    try:
        cur = conn.cursor()
        cur.execute(QUERY)
        rows = cur.fetchall()
    finally:
        conn.close()
    out = {}
    for row_name, col_name, value, units in rows:
        try:
            val = float(str(value).strip())
        except (TypeError, ValueError):
            continue
        out[(row_name, col_name)] = _to_gj(val, units)
    return out


def _row_for_sql(sql_path, campaign_root):
    rel = os.path.relpath(sql_path, campaign_root)
    parts = rel.split(os.sep)
    # <cell>/<sample_dir>/<scenario>/eplusout.sql
    if len(parts) != 4:
        raise ValueError(f"unexpected path depth ({len(parts)}): {rel}")
    cell, sample_dir, scenario, _fname = parts
    arch, city, cz = _parse_cell(cell)
    sample, hh_id = _parse_sample_dir(sample_dir)

    vals = _extract_end_uses(sql_path)
    heating_gas = vals.get(("Heating", "Natural Gas"), 0.0)
    heating_elec = vals.get(("Heating", "Electricity"), 0.0)
    heating_district = (
        vals.get(("Heating", "District Heating"), 0.0)
        + vals.get(("Heating", "District Cooling"), 0.0)
        + vals.get(("Heating", "District Heating Water"), 0.0)
        + vals.get(("Heating", "District Heating Steam"), 0.0)
    )
    cooling_elec = vals.get(("Cooling", "Electricity"), 0.0)
    cooling_gas = vals.get(("Cooling", "Natural Gas"), 0.0)
    cooling_district = (
        vals.get(("Cooling", "District Cooling"), 0.0)
        + vals.get(("Cooling", "District Heating"), 0.0)
        + vals.get(("Cooling", "District Heating Water"), 0.0)
        + vals.get(("Cooling", "District Heating Steam"), 0.0)
    )

    return {
        "cell": cell, "arch": arch, "city": city, "cz": cz,
        "scenario": scenario, "sample": sample, "hh_id": hh_id,
        "heating_gas_GJ": heating_gas, "heating_elec_GJ": heating_elec,
        "heating_district_GJ": heating_district,
        "cooling_elec_GJ": cooling_elec, "cooling_gas_GJ": cooling_gas,
        "cooling_district_GJ": cooling_district,
    }


def main():
    pattern = os.path.join(CAMP_DIR, "*", "*", "*", "eplusout.sql")
    sql_paths = sorted(glob.glob(pattern))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    n_dirs = len(sql_paths)
    n_parsed = 0
    n_skipped = 0

    with open(OUT_PATH, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for sql_path in sql_paths:
            try:
                row = _row_for_sql(sql_path, CAMP_DIR)
                writer.writerow(row)
                n_parsed += 1
            except Exception as exc:
                print(f"  [SKIP] {sql_path}: {exc}", flush=True)
                n_skipped += 1

    print(f"dirs={n_dirs} parsed={n_parsed} skipped={n_skipped}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
