"""
replot_existing_montecarlo.py

Re-generates the Monte Carlo EUI bar chart and time-series plot from
an already-completed simulation run, without re-running any simulations.

Usage:
    py replot_existing_montecarlo.py

The script reads all eplusout.sql files from the specified batch directory,
re-runs calculate_eui() and get_meter_data() (with the fixed plotting.py),
and saves new plots + a new aggregated CSV to a 'replot/' subdirectory.
"""

import os
import sys
import sqlite3
import numpy as np

# Force non-interactive backend before any matplotlib import (avoids GUI hang on Windows)
import matplotlib
matplotlib.use('Agg')

# Make eSim_bem_utils importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from eSim_bem_utils import plotting

# --- Configuration ---
BATCH_DIR = os.path.join(
    BASE_DIR, "BEM_Setup", "SimResults",
    "MonteCarlo_Neighbourhood_N10_1775555644"
)
PLOT_OUT_DIR = os.path.join(BATCH_DIR, "replot")
os.makedirs(PLOT_OUT_DIR, exist_ok=True)

SCENARIOS = ['2005', '2010', '2015', '2022', '2025']
ITER_COUNT = 10
BATCH_NAME = "MonteCarlo_Neighbourhood_N10_1775555644"


def get_meter_data_fast(conn):
    """
    Optimized version of plotting.get_meter_data that pre-filters by dictionary index
    to avoid a full-table scan on large (400+ MB) SQL files.
    """
    import pandas as pd

    TARGET_METERS = [
        'InteriorLights:Electricity',
        'InteriorEquipment:Electricity',
        'Fans:Electricity',
        'Heating:EnergyTransfer',
        'Cooling:EnergyTransfer',
        'WaterSystems:EnergyTransfer',
        'Electricity:Facility',
    ]

    meta_df = pd.read_sql_query(
        "SELECT ReportDataDictionaryIndex, Name, Units "
        "FROM ReportDataDictionary "
        "WHERE ReportingFrequency = 5 OR ReportingFrequency = 'Monthly'",
        conn
    )
    # Filter to only the meters we actually need
    meta_df = meta_df[meta_df['Name'].isin(TARGET_METERS)]
    if meta_df.empty:
        return {}

    idx_list = ",".join(str(int(x)) for x in meta_df['ReportDataDictionaryIndex'].tolist())
    index_map = {int(row['ReportDataDictionaryIndex']): (row['Name'], row['Units'])
                 for _, row in meta_df.iterrows()}

    # Fetch only the rows we need, filtered by index and environment type
    data_df = pd.read_sql_query(f"""
        SELECT rd.ReportDataDictionaryIndex, rd.Value
        FROM ReportData rd
        JOIN Time t ON rd.TimeIndex = t.TimeIndex
        JOIN EnvironmentPeriods ep ON t.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex
        WHERE rd.ReportDataDictionaryIndex IN ({idx_list})
          AND ep.EnvironmentType = 3
        ORDER BY t.TimeIndex ASC
    """, conn)

    results = {}
    for idx, (name, units) in index_map.items():
        subset = data_df[data_df['ReportDataDictionaryIndex'] == idx]
        values = []
        for v in subset['Value'].tolist():
            if units == 'J':
                values.append(v / 3600000.0)
            elif units == 'GJ':
                values.append(v * 277.778)
            elif units == 'kBtu':
                values.append(v * 0.293071)
            else:
                values.append(v)
        results[name] = values
    return results


def collect_results(batch_dir, scenarios, iter_count):
    """Walk the batch directory and run calculate_eui + get_meter_data on each SQL."""
    all_eui = {s: [] for s in scenarios}
    all_meters = {s: [] for s in scenarios}

    total = iter_count * len(scenarios) + 1
    done = 0

    for i in range(1, iter_count + 1):
        for scenario in scenarios:
            sql_path = os.path.join(batch_dir, f"iter_{i}", scenario, "eplusout.sql")
            if not os.path.isfile(sql_path):
                print(f"  [SKIP] missing: {sql_path}")
                continue
            conn = sqlite3.connect(sql_path)
            try:
                eui_result = plotting.calculate_eui(conn)
                meter_result = get_meter_data_fast(conn)
                all_eui[scenario].append(eui_result)
                all_meters[scenario].append(meter_result)
            finally:
                conn.close()
            done += 1
            print(f"  [{done}/{total}] iter_{i}/{scenario}", flush=True)

    # Default scenario (single run, not iterated)
    default_sql = os.path.join(batch_dir, "Default", "eplusout.sql")
    if os.path.isfile(default_sql):
        conn = sqlite3.connect(default_sql)
        try:
            eui_result = plotting.calculate_eui(conn)
            meter_result = get_meter_data_fast(conn)
            all_eui['Default'] = [eui_result]
            all_meters['Default'] = [meter_result]
        finally:
            conn.close()
        done += 1
        print(f"  [{done}/{total}] Default", flush=True)
    else:
        print(f"  [SKIP] missing Default SQL: {default_sql}")

    return all_eui, all_meters


def aggregate(all_eui, all_meters, scenarios_with_default):
    """Build mean/std dicts matching the format expected by plot_kfold_comparative_eui."""
    # Derive category list from the first non-empty result
    sample_result = None
    for s in scenarios_with_default:
        if all_eui.get(s):
            sample_result = all_eui[s][0]
            break
    if sample_result is None:
        raise RuntimeError("No valid EUI results found.")

    end_uses = sample_result.get('end_uses_normalized', {}) or sample_result.get('end_uses', {})
    categories = list(end_uses.keys())
    print(f"  Categories found: {categories}")

    aggregated = {'mean': {}, 'std': {}}
    for s in scenarios_with_default:
        results_list = all_eui.get(s, [])
        if not results_list:
            continue
        aggregated['mean'][s] = {}
        aggregated['std'][s] = {}
        for cat in categories:
            values = [r.get('end_uses_normalized', r.get('end_uses', {})).get(cat, 0.0)
                      for r in results_list]
            aggregated['mean'][s][cat] = float(np.mean(values)) if values else 0.0
            aggregated['std'][s][cat] = float(np.std(values)) if len(values) > 1 else 0.0

    # Meter aggregation
    sample_meter = None
    for s in scenarios_with_default:
        if all_meters.get(s):
            sample_meter = all_meters[s][0]
            break

    meter_names = list(sample_meter.keys()) if sample_meter else []
    aggregated_meters = {'mean': {}, 'std': {}}
    for s in scenarios_with_default:
        meter_list = all_meters.get(s, [])
        if not meter_list:
            continue
        aggregated_meters['mean'][s] = {}
        aggregated_meters['std'][s] = {}
        for meter in meter_names:
            all_values = [m.get(meter, [0] * 12) for m in meter_list]
            stacked = np.array(all_values)
            aggregated_meters['mean'][s][meter] = np.mean(stacked, axis=0).tolist()
            aggregated_meters['std'][s][meter] = (
                np.std(stacked, axis=0).tolist() if len(stacked) > 1 else [0] * 12
            )

    floor_area = (sample_result.get('conditioned_floor_area', 0.0)
                  or sample_result.get('total_floor_area', 0.0))

    return categories, aggregated, meter_names, aggregated_meters, floor_area


def save_csv(categories, aggregated, scenarios_with_default, out_path):
    with open(out_path, 'w') as f:
        f.write("EndUse," + ",".join([f"{s}_mean,{s}_std" for s in scenarios_with_default]) + "\n")
        for cat in categories:
            row = [cat]
            for s in scenarios_with_default:
                mean_val = aggregated['mean'].get(s, {}).get(cat, 0.0)
                std_val = aggregated['std'].get(s, {}).get(cat, 0.0)
                row.extend([f"{mean_val:.4f}", f"{std_val:.4f}"])
            f.write(",".join(row) + "\n")
    print(f"  CSV saved: {out_path}")


def main():
    print("=== Replot Existing Monte Carlo Run ===")
    print(f"Batch dir : {BATCH_DIR}")
    print(f"Output dir: {PLOT_OUT_DIR}\n")

    scenarios_with_default = SCENARIOS + ['Default']

    print("Collecting EUI and meter data...")
    all_eui, all_meters = collect_results(BATCH_DIR, SCENARIOS, ITER_COUNT)
    counts = {s: len(all_eui[s]) for s in scenarios_with_default}
    print(f"  SQL files loaded per scenario: {counts}\n")

    print("Aggregating...")
    categories, aggregated, meter_names, aggregated_meters, floor_area = aggregate(
        all_eui, all_meters, scenarios_with_default
    )
    print(f"  Floor area: {floor_area:.1f} m²\n")

    print("Saving CSV...")
    csv_path = os.path.join(PLOT_OUT_DIR, "aggregated_eui_replot.csv")
    save_csv(categories, aggregated, scenarios_with_default, csv_path)

    print("Generating EUI bar chart...")
    eui_plot_path = os.path.join(PLOT_OUT_DIR, f"MonteCarlo_Neighbourhood_EUI_{BATCH_NAME}_replot.png")
    plotting.plot_kfold_comparative_eui(
        aggregated, categories, eui_plot_path,
        K=ITER_COUNT, region="Montreal", idf_name=BATCH_NAME
    )

    print("Generating time-series plot...")
    ts_plot_path = os.path.join(PLOT_OUT_DIR, f"MonteCarlo_Neighbourhood_TimeSeries_{BATCH_NAME}_replot.png")
    plotting.plot_kfold_timeseries(
        aggregated_meters, meter_names, ts_plot_path,
        floor_area=floor_area, K=ITER_COUNT, region="Montreal",
        idf_name=BATCH_NAME, sim_mode='standard'
    )

    print("\n=== Done ===")
    print(f"Check {PLOT_OUT_DIR} for:")
    print(f"  - aggregated_eui_replot.csv")
    print(f"  - MonteCarlo_Neighbourhood_EUI_..._replot.png")
    print(f"  - MonteCarlo_Neighbourhood_TimeSeries_..._replot.png")


if __name__ == "__main__":
    main()
