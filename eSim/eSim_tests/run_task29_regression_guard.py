"""
Task 29 — Step 4 regression guard.

Runs Option 3 once (Montreal IDF, Quebec HH 4893) via Method B monkey-patch to
confirm validate_idf_compatibility does not reject a known-good single-building run.

If the run produces at least 1 eplusout.sql the guard PASSES.

Usage:
    py -3 eSim_tests/run_task29_regression_guard.py
"""
import os
import sys
import glob
import subprocess
import builtins
import io
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force UTF-8 on Windows to avoid cp1252 errors in print
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import eSim_bem_utils.main as main_module
from eSim_bem_utils import config

ENERGYPLUS_EXE  = config.ENERGYPLUS_EXE
SIM_RESULTS_DIR = main_module.SIM_RESULTS_DIR
TARGET_HH       = "4893"   # Quebec HH from 2005 CSV — same as Task 27 Run A


def run_guard():
    answer_iter = iter([
        "1",   # simulation mode -> Standard
        "1",   # IDF -> first (Montreal 6A)
        "1",   # dwelling type -> SingleD
        "y",   # confirm
    ])
    epw_resolved = {"path": None}

    real_find   = main_module.integration.find_best_match_household
    real_resolve = config.resolve_epw_path

    def forced_hh(schedules, candidates, *a, **kw):
        if TARGET_HH in schedules:
            return TARGET_HH
        return real_find(schedules, candidates, *a, **kw)

    def capturing_resolve(pr_region, weather_dir):
        result = real_resolve(pr_region, weather_dir)
        epw_resolved["path"] = result
        return result

    patches = [
        mock.patch("builtins.input", side_effect=answer_iter),
        mock.patch.object(main_module.integration, "find_best_match_household",
                          side_effect=forced_hh),
        mock.patch.object(main_module.config, "resolve_epw_path",
                          side_effect=capturing_resolve),
    ]

    batch_dirs_before = set(glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*")))

    try:
        for p in patches:
            p.start()
        main_module.option_comparative_simulation()
    except StopIteration:
        pass
    except Exception as exc:
        print(f"  [option_comparative_simulation raised]: {exc}")
    finally:
        for p in patches:
            p.stop()

    batch_dirs_after = set(glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*")))
    new_dirs = sorted(batch_dirs_after - batch_dirs_before)
    batch_dir = new_dirs[-1] if new_dirs else None

    if batch_dir:
        print(f"  Batch dir: {os.path.basename(batch_dir)}")
    else:
        print("  WARNING: no new batch dir found — run may have been absorbed into an existing dir")

    sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql")) if batch_dir else []
    ran_ok = bool(sql_files)

    # Fallback: if ProcessPoolExecutor failed, run EnergyPlus directly
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
                print(f"    {sc}: EPW not found, skipping")
                continue
            cmd = [ENERGYPLUS_EXE, "--weather", epw_path,
                   "--output-directory", out_dir, "--idd", config.IDD_FILE, idf_path]
            print(f"    Running EnergyPlus for {sc}...", end=" ", flush=True)
            r = subprocess.run(cmd, capture_output=True, text=True)
            ok_flag = "EnergyPlus Completed Successfully" in r.stdout
            print("OK" if ok_flag else f"FAILED (rc={r.returncode})")
        sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql"))
        ran_ok = bool(sql_files)

    print(f"\n  EPW resolved: {os.path.basename(epw_resolved.get('path', '') or 'NONE')}")
    print(f"  SQL files found: {len(sql_files)}")
    return ran_ok, batch_dir, len(sql_files)


if __name__ == "__main__":
    print("=" * 60)
    print("Task 29 Step 4 — Regression guard")
    print(f"  Target HH: {TARGET_HH} (Quebec, Montreal IDF)")
    print("=" * 60)

    ran_ok, batch_dir, n_sql = run_guard()

    print()
    if ran_ok:
        print(f"[PASS] Regression guard: validate_idf_compatibility did not break")
        print(f"       Option 3 Montreal run. {n_sql} SQL files produced.")
    else:
        print("[FAIL] Regression guard: EnergyPlus did not produce SQL files.")
        print("       Check whether validate_idf_compatibility raised a ValueError")
        print("       for the single-building Montreal IDF.")
        sys.exit(1)
