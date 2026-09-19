"""
EUI extractor for Task 26 — compares BEFORE and AFTER Option 3 runs.
Reads eplusout.sql from each scenario subdirectory, extracts per-end-use
kWh/m² via AnnualBuildingUtilityPerformanceSummary, and prints a markdown table.

Usage:
    py -3 eSim_tests/extract_option3_eui.py <before_dir> <after_dir>

Both dirs must contain subdirectories: 2005/ 2010/ 2015/ 2022/ 2025/ Default/
each with an eplusout.sql inside.
"""
import os
import sys
import sqlite3

# ── conversion constants (same as generate_report.py) ──────────────────────
KBTU_TO_KWH = 0.29307107
FT2_TO_M2   = 0.09290304

# End-use rows in EnergyPlus TabularData
END_USES = [
    ("Heating",           "Space Heating:Electricity + Space Heating:Natural Gas"),
    ("Cooling",           "Space Cooling"),
    ("Interior Lighting", "Interior Lighting"),
    ("Interior Equipment","Interior Equipment"),
    ("Fans",              "Fans"),
    ("Water Systems",     "Water Systems"),
]
# Row names actually used in EnergyPlus SQL TabularDataWithStrings
EPLUS_ROW_NAMES = {
    "Heating":            ["Space Heating", "Heating"],
    "Cooling":            ["Space Cooling", "Cooling"],
    "Interior Lighting":  ["Interior Lighting"],
    "Interior Equipment": ["Interior Equipment"],
    "Fans":               ["Fans"],
    "Water Systems":      ["Water Systems"],
}

ALL_FUEL_COLS = [
    'Electricity', 'Natural Gas', 'Propane', 'Fuel Oil No 1', 'Fuel Oil No 2',
    'Coal', 'Diesel', 'Gasoline', 'Other Fuel 1', 'Other Fuel 2',
    'District Cooling', 'District Heating Water', 'District Heating Steam',
]

SCENARIOS = ["2005", "2010", "2015", "2022", "2025", "Default"]


def _to_kwh(value_str, unit):
    try:
        val = float(value_str)
    except (TypeError, ValueError):
        return 0.0
    if unit == 'kBtu':
        return val * KBTU_TO_KWH
    if unit == 'GJ':
        return val * 277.778
    if unit == 'J':
        return val / 3_600_000.0
    if unit in ('kWh', 'kwh'):
        return val
    return 0.0


def get_area(cur):
    cur.execute(
        "SELECT Value, Units FROM TabularDataWithStrings "
        "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
        "AND TableName='Building Area' "
        "AND RowName='Net Conditioned Building Area' AND ColumnName='Area'"
    )
    row = cur.fetchone()
    if row:
        val, unit = row
        if unit == 'ft2':
            return float(val) * FT2_TO_M2
        return float(val)
    return 1.0


def get_end_use_kwh(cur, row_name):
    total = 0.0
    for col in ALL_FUEL_COLS:
        cur.execute(
            "SELECT Value, Units FROM TabularDataWithStrings "
            "WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' "
            "AND TableName='End Uses' AND RowName=? AND ColumnName=?",
            (row_name, col),
        )
        res = cur.fetchone()
        if res and res[0]:
            total += _to_kwh(res[0], res[1])
    return total


def extract_eui(batch_dir, compute_total=False):
    """
    Returns dict: {scenario: {end_use_label: kWh_per_m2, 'area_m2': float}}

    compute_total: if True, adds a 'Total' key = sum of all end-use EUIs.
    Default is False so existing callers are unaffected.
    """
    results = {}
    for scenario in SCENARIOS:
        sql_path = os.path.join(batch_dir, scenario, "eplusout.sql")
        if not os.path.exists(sql_path):
            print(f"  WARNING: {sql_path} not found — skipping {scenario}")
            results[scenario] = None
            continue
        conn = sqlite3.connect(sql_path)
        cur  = conn.cursor()
        area = get_area(cur)
        eui  = {"area_m2": area}
        for label, row_names in EPLUS_ROW_NAMES.items():
            total_kwh = 0.0
            for rn in row_names:
                total_kwh += get_end_use_kwh(cur, rn)
            eui[label] = round(total_kwh / area, 2) if area > 0 else 0.0
        conn.close()
        if compute_total:
            eui["Total"] = round(sum(eui[k] for k in EPLUS_ROW_NAMES), 2)
        results[scenario] = eui
    return results


def pct_delta(before, after):
    if before is None or before == 0:
        return "n/a"
    delta = (after - before) / abs(before) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"


def build_markdown_table(before_eui, after_eui, before_ts, after_ts, hh_id):
    labels = list(EPLUS_ROW_NAMES.keys())
    header = "| Scenario | Run | " + " | ".join(labels) + " |"
    sep    = "|---|---|" + "|".join(["---"] * len(labels)) + "|"
    lines  = [header, sep]

    for sc in SCENARIOS:
        b = before_eui.get(sc)
        a = after_eui.get(sc)

        def fmt(d, k):
            if d is None: return "MISSING"
            return f"{d.get(k, 0.0):.2f}"

        def fmt_d(k):
            if b is None or a is None: return "n/a"
            return pct_delta(b.get(k, 0), a.get(k, 0))

        lines.append("| " + sc + f" | BEFORE ({before_ts}) | " +
                     " | ".join(fmt(b, k) for k in labels) + " |")
        lines.append("| " + sc + f" | AFTER  ({after_ts}) | " +
                     " | ".join(fmt(a, k) for k in labels) + " |")
        lines.append("| " + sc + " | Delta % | " +
                     " | ".join(fmt_d(k) for k in labels) + " |")
        lines.append("|---|---|" + "|".join(["---"] * len(labels)) + "|")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        print("Usage: py -3 extract_option3_eui.py <before_dir> <after_dir>")
        sys.exit(1)

    before_dir, after_dir = sys.argv[1], sys.argv[2]
    before_ts = os.path.basename(before_dir).replace("Comparative_HH1p_", "")
    after_ts  = os.path.basename(after_dir).replace("Comparative_HH1p_", "")
    hh_id     = "4893"

    print(f"Extracting BEFORE run: {before_dir}")
    before_eui = extract_eui(before_dir)
    print(f"Extracting AFTER run:  {after_dir}")
    after_eui  = extract_eui(after_dir)

    table = build_markdown_table(before_eui, after_eui, before_ts, after_ts, hh_id)
    print("\n" + table)

    return before_eui, after_eui, table, before_ts, after_ts


if __name__ == "__main__":
    main()
