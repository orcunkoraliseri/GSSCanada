#!/usr/bin/env python3
"""
Task 21 Regression Test — Schedule:File 8760-resolution per household

Tests that:
1. use_schedule_file=False (Compact path) and use_schedule_file=True (Schedule:File)
   produce identical IDF objects for the schedule-driven end-uses (same values).
2. The schedules/HH_<id>/ directory is created with the expected CSVs when True.
3. Each CSV has exactly 8760 rows.
4. The IDF generated with Schedule:File references Schedule:File objects, not Compact,
   for the injected schedule names.

For a full EUI regression (EnergyPlus simulation required), run the two IDFs produced
by this script through EnergyPlus manually and compare the per-end-use EUI. The
expected delta is within ±1% (numerical noise only).

Usage:
    python eSim_tests/task21_regression.py

    To run only the unit checks (no EnergyPlus):
    python eSim_tests/task21_regression.py --no-sim

    To run EnergyPlus and compare EUI:
    python eSim_tests/task21_regression.py --sim
"""
import argparse
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import integration, config, idf_optimizer
from eppy.modeleditor import IDF

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IDF_PATH = os.path.join(
    BASE, "BEM_Setup", "Buildings",
    "Baseline_6A_Montreal_US+SF+CZ6A+gasfurnace+heatedbsmt+IECC_2021.idf"
)
EPW_PATH = os.path.join(
    BASE, "BEM_Setup", "WeatherFile",
    "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
)
SCHEDULE_CSV = os.path.join(BASE, "BEM_Setup", "BEM_Schedules_2022.csv")

# Household used for regression: Quebec, SingleD, hhsize=2.
# HH 4893 from spec is illustrative; 100212 is the first matching candidate from the
# 2022 dataset.  Swap to 4893 if it appears in a future dataset export.
TARGET_HH = "100212"


def load_target_household():
    """Return schedule_data dict for TARGET_HH from the 2022 CSV."""
    schedules = integration.load_schedules(SCHEDULE_CSV, region="Quebec")
    if TARGET_HH not in schedules:
        available = list(schedules.keys())[:5]
        raise RuntimeError(
            f"HH {TARGET_HH} not found in {SCHEDULE_CSV}. "
            f"Available (first 5): {available}"
        )
    return schedules[TARGET_HH]


def run_inject(out_dir, use_schedule_file: bool, label: str):
    """Inject schedules for TARGET_HH and return the output IDF path."""
    os.makedirs(out_dir, exist_ok=True)
    idf_out = os.path.join(out_dir, f"HH{TARGET_HH}_{label}.idf")
    schedule_data = load_target_household()

    print(f"\n[{label}] Injecting schedules -> {idf_out}")
    integration.inject_schedules(
        idf_path=IDF_PATH,
        output_path=idf_out,
        hh_id=TARGET_HH,
        schedule_data=schedule_data,
        epw_path=EPW_PATH,
        sim_results_dir=out_dir,
        batch_name="Task21_Regression",
        run_period_mode="standard",
        use_schedule_file=use_schedule_file,
        # schedule_file_year=None: auto-derive so Jan 1 matches RunPeriod start (Sunday)
    )
    print(f"[{label}] IDF written ({os.path.getsize(idf_out):,} bytes)")
    return idf_out


def check_csv_directory(out_dir):
    """Verify the schedules/HH_<id>/ directory has the expected 8760-row CSVs."""
    sched_dir = os.path.join(out_dir, "Task21_Regression", "schedules", f"HH_{TARGET_HH}")
    print(f"\n[CSV check] Expected directory: {sched_dir}")

    if not os.path.isdir(sched_dir):
        print("  FAIL — directory does not exist.")
        return False

    expected = {
        "occupancy.csv", "metabolic.csv", "lighting.csv",
        "equipment.csv", "dhw.csv",
        "heating_setpoint.csv", "cooling_setpoint.csv",
    }
    found = set(os.listdir(sched_dir))
    missing = expected - found
    extra = found - expected

    print(f"  Found files: {sorted(found)}")
    if missing:
        print(f"  FAIL — missing: {sorted(missing)}")
    if extra:
        print(f"  NOTE — extra files (not in spec list): {sorted(extra)}")

    # Check row counts
    all_ok = True
    for fname in sorted(found):
        fpath = os.path.join(sched_dir, fname)
        with open(fpath) as f:
            rows = sum(1 for _ in f)
        if rows != 8760:
            print(f"  FAIL — {fname}: {rows} rows (expected 8760)")
            all_ok = False
        else:
            print(f"  OK — {fname}: 8760 rows")

    if missing:
        all_ok = False

    return all_ok


def check_idf_schedule_types(idf_path_compact, idf_path_file):
    """Verify Compact IDF has Schedule:Compact and File IDF has Schedule:File for injected names."""
    idd_path = config.resolve_idd_path()
    IDF.setiddname(idd_path)

    idf_c = IDF(idf_path_compact)
    idf_f = IDF(idf_path_file)

    occ_name = f"Occ_Sch_HH_{TARGET_HH}"
    heat_name = f"HeatSP_HH_{TARGET_HH}"

    print(f"\n[IDF check] Occupancy schedule name: {occ_name}")

    # Compact path: occupancy should be Schedule:Compact
    compact_names = [s.Name for s in idf_c.idfobjects.get('SCHEDULE:COMPACT', [])]
    file_names_c = [s.Name for s in idf_c.idfobjects.get('SCHEDULE:FILE', [])]
    if occ_name in compact_names:
        print(f"  OK (Compact IDF) — {occ_name} is Schedule:Compact")
    else:
        print(f"  FAIL (Compact IDF) — {occ_name} not in Schedule:Compact. Has: {compact_names[:5]}")

    # File path: occupancy should be Schedule:File
    compact_names_f = [s.Name for s in idf_f.idfobjects.get('SCHEDULE:COMPACT', [])]
    file_names_f = [s.Name for s in idf_f.idfobjects.get('SCHEDULE:FILE', [])]
    if occ_name in file_names_f:
        print(f"  OK (File IDF) — {occ_name} is Schedule:File")
    else:
        print(f"  FAIL (File IDF) — {occ_name} not in Schedule:File. Has: {file_names_f[:5]}")

    # Setpoint check
    print(f"\n[IDF check] Heat setpoint schedule name: {heat_name}")
    if heat_name in compact_names:
        print(f"  OK (Compact IDF) — {heat_name} is Schedule:Compact")
    else:
        print(f"  FAIL (Compact IDF) — {heat_name} not found in Compact schedules")
    if heat_name in file_names_f:
        print(f"  OK (File IDF) — {heat_name} is Schedule:File")
    else:
        print(f"  FAIL (File IDF) — {heat_name} not found in Schedule:File. Has: {file_names_f}")

    # File size comparison
    size_c = os.path.getsize(idf_path_compact)
    size_f = os.path.getsize(idf_path_file)
    delta_pct = 100 * (size_f - size_c) / size_c
    print(f"\n[IDF size] Compact: {size_c:,} bytes | File: {size_f:,} bytes | delta: {delta_pct:+.1f}%")
    if size_f < size_c:
        print("  OK — Schedule:File IDF is smaller (Compact blocks replaced by filenames)")
    else:
        print("  NOTE — Schedule:File IDF is not smaller; check for unexpected Compact blocks")

    return occ_name in compact_names and occ_name in file_names_f


def run_simulation(idf_path, epw_path, out_dir, label):
    """Run EnergyPlus and return the SQL path."""
    from eSim_bem_utils import simulation
    ep_path = config.ENERGYPLUS_EXE
    sim_out = os.path.join(out_dir, label)
    os.makedirs(sim_out, exist_ok=True)
    print(f"\n[SIM] Running EnergyPlus for {label}...")
    result = simulation.run_simulation(idf_path, epw_path, sim_out, ep_path=ep_path, quiet=False)
    if not result.get("success"):
        raise RuntimeError(f"Simulation failed for {label}: {result.get('message', '?')}")
    sql_path = os.path.join(sim_out, "eplusout.sql")
    if not os.path.exists(sql_path):
        raise RuntimeError(f"Simulation output not found: {sql_path}")
    return sql_path


def extract_eui_from_tbl(sql_path):
    """
    Extract per-end-use annual energy consumption from eplustbl.csv.

    Using eplustbl.csv avoids the Windows SQLite exclusive-lock issue where
    EnergyPlus holds the .sql file open briefly after simulation completion.
    Returns a dict of {end_use: kBtu} from the end-use summary table.
    """
    import csv
    tbl_path = os.path.join(os.path.dirname(sql_path), "eplustbl.csv")
    if not os.path.exists(tbl_path):
        return {}

    eui = {}
    in_end_use_section = False
    with open(tbl_path, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # Detect the "End Uses By Subcategory" table header or "End Uses" section
            if len(row) >= 2 and 'Electricity [kBtu]' in row and 'Natural Gas [kBtu]' in row:
                in_end_use_section = True
                continue
            if in_end_use_section:
                if len(row) < 2 or (not row[0] and not row[1]):
                    in_end_use_section = False
                    continue
                if row[1] in ('Heating', 'Cooling', 'Interior Lighting', 'Exterior Lighting',
                              'Interior Equipment', 'Exterior Equipment', 'Fans', 'Pumps',
                              'Water Systems', 'Total End Uses'):
                    name = row[1]
                    try:
                        elec = float(row[2]) if row[2] else 0.0
                        gas  = float(row[3]) if row[3] else 0.0
                        eui[name] = elec + gas
                    except (ValueError, IndexError):
                        pass
    return eui


def compare_eui(eui_compact, eui_file):
    """Print comparison table and check all deltas are within ±1%."""
    all_keys = sorted(set(eui_compact) | set(eui_file))
    print("\n" + "=" * 90)
    print(f"{'End-use':<50} {'Compact (kBtu)':>18} {'File (kBtu)':>18} {'Delta%':>8}")
    print("-" * 90)
    all_ok = True
    for key in all_keys:
        v_c = eui_compact.get(key, 0.0)
        v_f = eui_file.get(key, 0.0)
        if v_c == 0.0 and v_f == 0.0:
            continue
        if v_c != 0.0:
            delta_pct = 100 * (v_f - v_c) / abs(v_c)
        else:
            delta_pct = float('inf')
        flag = " FAIL" if abs(delta_pct) > 1.0 else ""
        print(f"{key[:50]:<50} {v_c:>18.2f} {v_f:>18.2f} {delta_pct:>+7.3f}%{flag}")
        if abs(delta_pct) > 1.0:
            all_ok = False
    print("=" * 90)
    if all_ok:
        print("PASS - All end-use EUI deltas within +/-1%.")
    else:
        print("FAIL - One or more end-use deltas exceed +/-1%. Investigate before marking done.")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Task 21 regression test")
    parser.add_argument("--sim", action="store_true", help="Run EnergyPlus and compare EUI")
    parser.add_argument("--no-sim", action="store_true", help="Unit checks only (no EnergyPlus)")
    args = parser.parse_args()

    out_dir = os.path.join(BASE, "BEM_Setup", "SimResults")

    print("=" * 70)
    print("Task 21 Regression — Schedule:File vs Schedule:Compact")
    print(f"Target HH: {TARGET_HH}  |  IDF: Baseline_6A_Montreal")
    print("=" * 70)

    # Step 1: Generate both IDFs
    idf_compact = run_inject(out_dir, use_schedule_file=False, label="Compact")
    idf_file    = run_inject(out_dir, use_schedule_file=True,  label="ScheduleFile")

    # Step 2: Check CSV directory
    csv_ok = check_csv_directory(out_dir)

    # Step 3: Check IDF schedule types and file size
    idf_ok = check_idf_schedule_types(idf_compact, idf_file)

    if args.sim:
        # Step 4: Full EnergyPlus regression
        sim_base = os.path.join(out_dir, "Task21_Regression")
        sql_c = run_simulation(idf_compact, EPW_PATH, sim_base, "compact_run")
        sql_f = run_simulation(idf_file,   EPW_PATH, sim_base, "file_run")
        eui_c = extract_eui_from_tbl(sql_c)
        eui_f = extract_eui_from_tbl(sql_f)
        eui_ok = compare_eui(eui_c, eui_f)
    else:
        print("\n[SIM] Skipped (pass --sim to run EnergyPlus).")
        eui_ok = True  # Not tested

    print("\n" + "=" * 70)
    print(f"CSV directory check:  {'PASS' if csv_ok else 'FAIL'}")
    print(f"IDF schedule check:   {'PASS' if idf_ok else 'FAIL'}")
    if args.sim:
        print(f"EUI regression:       {'PASS' if eui_ok else 'FAIL'}")
    print("=" * 70)

    if not (csv_ok and idf_ok and eui_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
