"""
Task 27 Step 5 — Cross-region Option 3 smoke test.

Runs Option 3 (Comparative single-building, Standard mode) three times:
  Run A — Quebec HH 5326   → expects Montreal EPW
  Run B — Ontario HH 57536 → expects Toronto EPW
  Run C — Alberta HH 689   → expects Calgary EPW

Uses Method B monkey-patching (same pattern as Task 26):
  - builtins.input is patched to feed all interactive prompts automatically
  - integration.find_best_match_household is patched to force the target HH

EnergyPlus is invoked via simulation.run_simulations_parallel; if that fails
(ProcessPoolExecutor crash), the script falls back to running EnergyPlus
directly for each prepared IDF.

Usage:
    py -3 eSim_tests/run_task27_cross_region.py
"""
import os
import sys
import time
import glob
import subprocess
import builtins
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force UTF-8 output on Windows to avoid cp1252 errors
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import eSim_bem_utils.main as main_module
from eSim_bem_utils import simulation, config

ENERGYPLUS_EXE = config.ENERGYPLUS_EXE
SIM_RESULTS_DIR = main_module.SIM_RESULTS_DIR

# Target HH per PR — IDs are from the 2005 CSV (first_year in Option 3's schedule map).
# HH IDs are not stable across years; the same integer maps to a different household
# in different year CSVs. These were verified via find_best_match_household on
# BEM_Schedules_2005.csv with region filter for each PR.
CROSS_REGION_RUNS = [
    {"label": "Run_A_Quebec",  "pr": "Quebec",  "hh_id": "4893",  "epw_city": "Montreal"},
    {"label": "Run_B_Ontario", "pr": "Ontario", "hh_id": "5203",  "epw_city": "Toronto"},
    {"label": "Run_C_Alberta", "pr": "Alberta", "hh_id": "11851", "epw_city": "Calgary"},
]


def make_input_seq(sim_mode_idx=1, idf_idx=1, dt_idx=1, confirm="y"):
    """Return a generator that yields answers to all Option 3 input() calls in order."""
    answers = [
        str(sim_mode_idx),   # select_simulation_mode -> 1 = Standard
        str(idf_idx),        # select_file IDF        -> 1 = Montreal
        str(dt_idx),         # dwelling_type          -> 1 = SingleD
        confirm,             # proceed to run
    ]
    return iter(answers)


def run_option3_for(run_cfg: dict) -> dict:
    """
    Execute option_comparative_simulation with HH forced to run_cfg['hh_id'].
    Returns a dict with batch_dir, epw_resolved, success flag.
    """
    target_hh = run_cfg["hh_id"]
    label = run_cfg["label"]
    print(f"\n{'='*60}")
    print(f"  {label} — forcing HH {target_hh} (PR={run_cfg['pr']})")
    print(f"{'='*60}")

    answer_iter = make_input_seq()
    epw_resolved = {"path": None}

    # Patch find_best_match_household to always return our target HH
    real_find = main_module.integration.find_best_match_household

    def forced_hh(schedules, candidates, *args, **kwargs):
        if target_hh in schedules:
            return target_hh
        # fallback if year CSV doesn't have this HH (unlikely for 2022)
        return real_find(schedules, candidates, *args, **kwargs)

    # Patch resolve_epw_path to capture the resolved EPW
    real_resolve = config.resolve_epw_path

    def capturing_resolve(pr_region, weather_dir):
        result = real_resolve(pr_region, weather_dir)
        epw_resolved["path"] = result
        epw_resolved["pr"] = pr_region
        return result

    patches = [
        mock.patch("builtins.input", side_effect=answer_iter),
        mock.patch.object(main_module.integration, "find_best_match_household", side_effect=forced_hh),
        mock.patch.object(main_module.config, "resolve_epw_path", side_effect=capturing_resolve),
    ]

    batch_dirs_before = set(glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*")))

    try:
        for p in patches:
            p.start()
        main_module.option_comparative_simulation()
    except StopIteration:
        # All inputs consumed normally — OK
        pass
    except Exception as exc:
        print(f"  [option_comparative_simulation raised]: {exc}")
    finally:
        for p in patches:
            p.stop()

    # Find the new batch directory
    batch_dirs_after = set(glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*")))
    new_dirs = batch_dirs_after - batch_dirs_before
    batch_dir = sorted(new_dirs)[-1] if new_dirs else None

    if batch_dir:
        print(f"  Batch dir: {os.path.basename(batch_dir)}")
    else:
        print("  WARNING: no new batch dir found")

    # Check if EnergyPlus already ran (eplusout.sql present)
    ran_ok = False
    if batch_dir:
        sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql"))
        if sql_files:
            ran_ok = True
            print(f"  EnergyPlus outputs found: {len(sql_files)} scenarios")

    # Fallback: run EnergyPlus directly if ProcessPoolExecutor failed
    if batch_dir and not ran_ok:
        print("  ProcessPoolExecutor may have failed — running EnergyPlus directly...")
        scenarios = ["2005", "2010", "2015", "2022", "2025", "Default"]
        for sc in scenarios:
            idf_path = os.path.join(batch_dir, sc, f"Scenario_{sc}.idf")
            epw_path = epw_resolved.get("path")
            out_dir  = os.path.join(batch_dir, sc)
            if not os.path.exists(idf_path):
                print(f"    {sc}: IDF not found, skipping")
                continue
            if not epw_path or not os.path.exists(epw_path):
                print(f"    {sc}: EPW not found ({epw_path}), skipping")
                continue
            cmd = [
                ENERGYPLUS_EXE,
                "--weather", epw_path,
                "--output-directory", out_dir,
                "--idd", config.IDD_FILE,
                idf_path,
            ]
            print(f"    Running EnergyPlus for {sc}...", end=" ", flush=True)
            r = subprocess.run(cmd, capture_output=True, text=True)
            ok_flag = "EnergyPlus Completed Successfully" in r.stdout
            print("OK" if ok_flag else f"FAILED (rc={r.returncode})")
        sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql"))
        ran_ok = bool(sql_files)

    return {
        "label": label,
        "batch_dir": batch_dir,
        "epw_resolved": epw_resolved,
        "ran_ok": ran_ok,
    }


if __name__ == "__main__":
    run_results = []
    for run_cfg in CROSS_REGION_RUNS:
        result = run_option3_for(run_cfg)
        run_results.append((run_cfg, result))
        time.sleep(2)  # Avoid timestamp collision in batch name

    print("\n" + "="*60)
    print("CROSS-REGION RUN SUMMARY")
    print("="*60)
    for run_cfg, res in run_results:
        epw_path = res["epw_resolved"].get("path", "NOT_RESOLVED")
        epw_file = os.path.basename(epw_path) if epw_path else "NOT_RESOLVED"
        city_ok = run_cfg["epw_city"].upper() in epw_file.upper()
        ok_flag = res["ran_ok"] and city_ok
        status = "PASS" if ok_flag else "FAIL"
        print(f"  [{status}] {res['label']}")
        print(f"    EPW resolved: {epw_file}")
        print(f"    Expected city: {run_cfg['epw_city']}  city_ok={city_ok}")
        print(f"    EnergyPlus ran: {res['ran_ok']}")
        if res["batch_dir"]:
            print(f"    Batch dir: {os.path.basename(res['batch_dir'])}")
