"""
Task 20 smoke test: run Option 3 for HH 4893 on Baseline_6A_Montreal,
compare DHW annual kWh against Session 7 reference batch
(Comparative_HH1p_1775675140).
"""
import os, sys, time, sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import integration, idf_optimizer, simulation, config
from eSim_bem_utils.main import (
    BUILDINGS_DIR, WEATHER_DIR, SIM_RESULTS_DIR, _build_schedule_file_map, COMPARATIVE_YEARS
)

# ── Fixed parameters ───────────────────────────────────────────────────────────
TARGET_HH        = '4893'
IDF_PATH         = os.path.join(BUILDINGS_DIR, 'Baseline_6A_Montreal_US+SF+CZ6A+gasfurnace+heatedbsmt+IECC_2021.idf')
EPW_PATH         = os.path.join(WEATHER_DIR, 'CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw')
REF_BATCH_DIR    = os.path.join(SIM_RESULTS_DIR, 'Comparative_HH1p_1775675140')
ENERGYPLUS_EXE   = config.ENERGYPLUS_EXE

SCENARIOS        = ['Default'] + list(COMPARATIVE_YEARS)   # Default + 2005..2025


def get_dhw_kwh(sql_path):
    """Return annual DHW WaterSystems:EnergyTransfer kWh from an SQL file."""
    if not os.path.exists(sql_path):
        return None
    conn = sqlite3.connect(sql_path)
    cur  = conn.cursor()
    cur.execute("""
        SELECT SUM(rd.Value)/3.6e6
        FROM ReportDataDictionary rdd
        JOIN ReportData rd ON rdd.ReportDataDictionaryIndex = rd.ReportDataDictionaryIndex
        WHERE rdd.Name = 'WaterSystems:EnergyTransfer'
          AND rdd.ReportingFrequency = 'Monthly'
    """)
    row = cur.fetchone()
    conn.close()
    return row[0] if (row and row[0]) else None


def main():
    print("=== Task 20 Smoke Test: Continuous DHW — HH 4893 / Baseline_6A_Montreal ===\n")

    # ── Load all schedule years ────────────────────────────────────────────────
    schedule_files  = _build_schedule_file_map()
    all_schedules   = {}
    for year, csv_path in schedule_files.items():
        if not os.path.exists(csv_path):
            print(f"  WARNING: {csv_path} missing, skipping {year}")
            continue
        all_schedules[year] = integration.load_schedules(csv_path, dwelling_type='SingleD', region=None)

    # HH 4893 is in 2005; for other years use best-match by hhsize (same as Option 3)
    base_year = '2005'
    if TARGET_HH not in all_schedules.get(base_year, {}):
        print(f"  ERROR: HH {TARGET_HH} not found in {base_year}")
        sys.exit(1)
    hhsize = all_schedules[base_year][TARGET_HH].get('metadata', {}).get('hhsize', 1)
    print(f"HH {TARGET_HH} (hhsize={hhsize}) found in {base_year}. Best-match for other years. OK\n")

    # ── Prepare batch directory ────────────────────────────────────────────────
    batch   = f"Comparative_HH{hhsize}p_task20_{int(time.time())}"
    batch_dir = os.path.join(SIM_RESULTS_DIR, batch)
    os.makedirs(batch_dir, exist_ok=True)
    print(f"Batch: {batch}")
    print(f"IDF  : {os.path.basename(IDF_PATH)}")
    print(f"EPW  : {os.path.basename(EPW_PATH)}\n")

    # Same households as Session 7 reference batch (Comparative_HH1p_1775675140)
    # so that the comparison is apples-to-apples (only continuous DHW differs).
    REF_HOUSEHOLDS = {
        '2005': '4893',
        '2010': '3287',
        '2015': '4509',
        '2022': '5326',
        '2025': '1422',
    }

    # ── Prepare IDFs ──────────────────────────────────────────────────────────
    jobs = []
    for scenario in SCENARIOS:
        scenario_dir = os.path.join(batch_dir, scenario)
        os.makedirs(scenario_dir, exist_ok=True)
        idf_out = os.path.join(scenario_dir, f'Scenario_{scenario}.idf')

        if scenario == 'Default':
            idf_optimizer.prepare_idf_for_simulation(
                IDF_PATH, idf_out, verbose=False,
                run_period_mode='standard', baseline='midrise',
            )
        elif scenario in all_schedules:
            year_schedules = all_schedules[scenario]
            year_hh = REF_HOUSEHOLDS.get(scenario)
            if year_hh not in year_schedules:
                print(f"  WARNING: HH {year_hh} not in {scenario} — using best-match")
                candidates = [hid for hid, d in year_schedules.items()
                              if d.get('metadata', {}).get('hhsize', 0) == hhsize]
                year_hh = integration.find_best_match_household(year_schedules, candidates or list(year_schedules.keys()))
            print(f"  {scenario}: HH {year_hh}")
            integration.inject_schedules(
                IDF_PATH, idf_out, year_hh,
                year_schedules[year_hh],
                epw_path=EPW_PATH,
                sim_results_dir=SIM_RESULTS_DIR,
                batch_name=batch,
                run_period_mode='standard',
            )
        else:
            print(f"  Skipping {scenario} — no schedules")
            continue
        jobs.append({'idf': idf_out, 'epw': EPW_PATH, 'output_dir': scenario_dir, 'name': scenario})
        print(f"  Prepared: {scenario}")

    # ── Run simulations ────────────────────────────────────────────────────────
    print(f"\nRunning {len(jobs)} EnergyPlus simulations in parallel …")
    simulation.run_simulations_parallel(jobs, ENERGYPLUS_EXE)
    print("Simulations done.\n")

    # ── Extract DHW and compare ────────────────────────────────────────────────
    print(f"{'Scenario':<10} {'New run (kWh)':>16} {'Reference (kWh)':>16} {'Δ (%)':>8}")
    print("-" * 56)

    max_pct_diff = 0.0
    for scenario in SCENARIOS:
        new_sql = os.path.join(batch_dir, scenario, 'eplusout.sql')
        ref_sql = os.path.join(REF_BATCH_DIR, scenario, 'eplusout.sql')
        new_val = get_dhw_kwh(new_sql)
        ref_val = get_dhw_kwh(ref_sql)

        if new_val is None:
            print(f"{scenario:<10} {'MISSING':>16}")
            continue
        if ref_val is None:
            print(f"{scenario:<10} {new_val:>16.1f} {'n/a':>16}")
            continue

        pct = 100.0 * (new_val - ref_val) / ref_val if ref_val else float('nan')
        max_pct_diff = max(max_pct_diff, abs(pct))
        flag = ' <-- DIVERGED (>5%)' if abs(pct) > 5 else ''
        print(f"{scenario:<10} {new_val:>16.1f} {ref_val:>16.1f} {pct:>7.1f}%{flag}")

    print("\n" + ("PASS: Max Δ ≤ 5%" if max_pct_diff <= 5 else f"ESCALATE: Max Δ = {max_pct_diff:.1f}% > 5%"))
    return max_pct_diff


if __name__ == '__main__':
    diff = main()
    sys.exit(1 if diff > 5 else 0)
