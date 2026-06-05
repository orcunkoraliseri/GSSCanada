#!/usr/bin/env python3
"""
extract_meters.py — sqlite3-only hourly meter extractor.

Replicates plotting.get_hourly_meter_data() without pandas.
Designed to run inside the NREL energyplus container (Python 3 + sqlite3 built-in).

Usage:
    python3 extract_meters.py <eplusout.sql> <output_hourly_meters.csv>
"""
import sqlite3
import csv
import sys


def extract(sql_path, out_csv):
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()

    # --- Step 1: get meter dictionary (same filter as plotting.py) ---
    cur.execute("""
        SELECT ReportDataDictionaryIndex, KeyValue, Name, Units
        FROM ReportDataDictionary
        WHERE ReportingFrequency = 3 OR ReportingFrequency = 'Hourly'
    """)
    meta = cur.fetchall()

    # Map index → name for matching meters (last same-name idx wins, matches plotting.py)
    index_map = {}
    for idx, kv, name, units in meta:
        if any(x in name for x in ['EnergyTransfer', 'Electricity', 'WaterSystems']):
            index_map[idx] = name

    if not index_map:
        print("ERROR: no matching meters found in ReportDataDictionary", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: fetch hourly run-period data ---
    indices_csv = ",".join(str(i) for i in index_map)
    cur.execute(f"""
        SELECT rd.ReportDataDictionaryIndex, rd.Value
        FROM ReportData rd
        JOIN Time t ON rd.TimeIndex = t.TimeIndex
        JOIN EnvironmentPeriods ep ON t.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex
        WHERE ep.EnvironmentType = 3
          AND rd.ReportDataDictionaryIndex IN ({indices_csv})
        ORDER BY t.TimeIndex ASC
    """)
    all_rows = cur.fetchall()
    conn.close()

    # --- Step 3: pivot to {name: [values]} ---
    # Collect per-index first
    data_by_idx = {}
    for row_idx, val in all_rows:
        if row_idx not in data_by_idx:
            data_by_idx[row_idx] = []
        data_by_idx[row_idx].append(val)

    # Build results: last idx with same name wins (matches plotting.py iteration order)
    results = {}
    for idx, name in index_map.items():
        if idx in data_by_idx:
            results[name] = data_by_idx[idx]

    if not results:
        print("ERROR: no hourly data extracted for run-period", file=sys.stderr)
        sys.exit(1)

    meters = list(results.keys())
    nrows = max(len(v) for v in results.values())

    # --- Step 4: write CSV ---
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hour"] + meters)
        for h in range(nrows):
            w.writerow([h] + [results[m][h] if h < len(results[m]) else "" for m in meters])

    print(f"Written {nrows} rows, {len(meters)} meters -> {out_csv}")
    for m in meters:
        ann_kWh = sum(results[m]) / 3_600_000
        print(f"  {m}: annual {ann_kWh:.1f} kWh")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_meters.py <eplusout.sql> <output.csv>", file=sys.stderr)
        sys.exit(1)
    extract(sys.argv[1], sys.argv[2])
