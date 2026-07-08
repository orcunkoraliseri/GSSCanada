"""extract_enduse_annual_from_tbl.py — Step 8 Fix v3 End-Uses extractor, LOCAL variant.

Same output/schema as extract_enduse_annual.py (which queries eplusout.sql via sqlite3
on the cluster), but parses the much smaller eplustbl.csv "End Uses" table instead —
used for a local run while the Speed cluster is unavailable (2026-07-08, ~2wk window).
Values cross-checked identical to the sqlite path for MidRise sample_001 2022
(heating_gas_GJ=78.34, cooling_elec_GJ=136.12). Stdlib only (os, glob, csv, re).

Usage: py investigation/extract_enduse_annual_from_tbl.py
Env:   STEP8_CAMP_DIR (default outputs_step8/campaign_subset_v3_enduse relative to Step8_docs)
       STEP8_ENDUSE_OUT (default <Step8_docs>/outputs_step8/agg/agg_enduse_annual.csv)
"""
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # Step8_docs/investigation/
STEP8_DOCS = os.path.dirname(HERE)                          # Step8_docs/

CAMP_DIR = os.environ.get(
    "STEP8_CAMP_DIR",
    os.path.join(STEP8_DOCS, "outputs_step8", "campaign_subset_v3_enduse"),
)
OUT_PATH = os.environ.get(
    "STEP8_ENDUSE_OUT",
    os.path.join(STEP8_DOCS, "outputs_step8", "agg", "agg_enduse_annual.csv"),
)

CELL_RE = re.compile(r"^(?P<arch>[^_]+(?:[A-Za-z]+)?)__(?P<city>[A-Za-z]+)_(?P<cz>[0-9A-Za-z]+)$")
SAMPLE_RE = re.compile(r"^sample_(?P<sample>\d+)_HH(?P<hh>\w+)$")

# End Uses column order in eplustbl.csv (ABUPS "End Uses" table):
# Electricity, Natural Gas, Gasoline, Diesel, Coal, Fuel Oil No 1, Fuel Oil No 2,
# Propane, Other Fuel 1, Other Fuel 2, District Cooling, District Heating Water,
# District Heating Steam, Water [m3 or gal]
COL_ELEC, COL_GAS = 0, 1
COL_DIST_COOL, COL_DIST_HW, COL_DIST_HS = 10, 11, 12

# OutputControl:Table:Style's unit-conversion setting differs by archetype family
# (apartment prototypes = GJ/SI; house prototypes = kBtu/IP — confirmed 2026-07-08 by
# comparing eplustbl.csv headers: SingleD/OtherDwelling say "Electricity [kBtu]" +
# "Water [gal]", MidRise/HighRise say "Electricity [GJ]" + "Water [m3]"). Convert
# everything to GJ so cross-archetype ratios (gate 4.9) are apples-to-apples.
_GJ_PER_UNIT = {"GJ": 1.0, "kBtu": 0.0010550559}
_UNIT_RE = re.compile(r"\[([^\]]+)\]")


def _gj_multiplier(header_row):
    """header_row = the parsed 'End Uses' header row, e.g.
    ['', '', 'Electricity [GJ]', 'Natural Gas [GJ]', ...]. Unit is uniform across the
    whole table (OutputControl:Table:Style applies one conversion per run)."""
    if len(header_row) <= 2:
        return 1.0
    m = _UNIT_RE.search(header_row[2])
    unit = m.group(1) if m else "GJ"
    try:
        return _GJ_PER_UNIT[unit]
    except KeyError:
        raise ValueError(f"unrecognized End Uses unit {unit!r} — extend _GJ_PER_UNIT")

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


def _extract_end_uses(tbl_path):
    """Return dict: {RowName: [14 float values]} for the Heating/Cooling rows of the
    first 'End Uses' table in eplustbl.csv (ABUPS report, not 'End Uses By ...')."""
    with open(tbl_path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        lines = fh.readlines()

    out = {}
    in_table = False
    header_seen = False
    multiplier = 1.0
    for line in lines:
        stripped = line.strip()
        if stripped == "End Uses":
            in_table = True
            header_seen = False
            continue
        if in_table and stripped == "End Uses By Subcategory":
            break
        if not in_table:
            continue
        if not stripped:
            continue
        parts = next(csv.reader([line]))
        if not header_seen:
            # header row: ,,Electricity [GJ],Natural Gas [GJ],... (or [kBtu] for houses)
            header_seen = True
            multiplier = _gj_multiplier(parts)
            continue
        row_name = parts[1].strip() if len(parts) > 1 else ""
        if row_name not in ("Heating", "Cooling"):
            continue
        vals = []
        for cell in parts[2:16]:
            try:
                vals.append(float(cell.strip()) * multiplier)
            except ValueError:
                vals.append(0.0)
        out[row_name] = vals
    return out


def _row_for_tbl(tbl_path, campaign_root):
    rel = os.path.relpath(tbl_path, campaign_root)
    parts = rel.split(os.sep)
    if len(parts) != 4:
        raise ValueError(f"unexpected path depth ({len(parts)}): {rel}")
    cell, sample_dir, scenario, _fname = parts
    arch, city, cz = _parse_cell(cell)
    sample, hh_id = _parse_sample_dir(sample_dir)

    vals = _extract_end_uses(tbl_path)
    heating = vals.get("Heating", [0.0] * 14)
    cooling = vals.get("Cooling", [0.0] * 14)

    heating_gas = heating[COL_GAS]
    heating_elec = heating[COL_ELEC]
    heating_district = heating[COL_DIST_COOL] + heating[COL_DIST_HW] + heating[COL_DIST_HS]
    cooling_elec = cooling[COL_ELEC]
    cooling_gas = cooling[COL_GAS]
    cooling_district = cooling[COL_DIST_COOL] + cooling[COL_DIST_HW] + cooling[COL_DIST_HS]

    return {
        "cell": cell, "arch": arch, "city": city, "cz": cz,
        "scenario": scenario, "sample": sample, "hh_id": hh_id,
        "heating_gas_GJ": heating_gas, "heating_elec_GJ": heating_elec,
        "heating_district_GJ": heating_district,
        "cooling_elec_GJ": cooling_elec, "cooling_gas_GJ": cooling_gas,
        "cooling_district_GJ": cooling_district,
    }


def main():
    pattern = os.path.join(CAMP_DIR, "*", "*", "*", "eplustbl.csv")
    tbl_paths = sorted(glob.glob(pattern))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    n_dirs = len(tbl_paths)
    n_parsed = 0
    n_skipped = 0

    with open(OUT_PATH, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for tbl_path in tbl_paths:
            try:
                row = _row_for_tbl(tbl_path, CAMP_DIR)
                writer.writerow(row)
                n_parsed += 1
            except Exception as exc:
                print(f"  [SKIP] {tbl_path}: {exc}", flush=True)
                n_skipped += 1

    print(f"dirs={n_dirs} parsed={n_parsed} skipped={n_skipped}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
