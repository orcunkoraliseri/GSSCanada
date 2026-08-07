"""
Task 30 Step 2 — Archetype monkey-patch runs.

Runs Option 3 (Comparative, Standard) three times, once per alternative archetype
(Student, Retiree, ShiftWorker).  Before each run, monkey-patches
integration.TARGET_WORKING_PROFILE to the archetype's profile so
find_best_match_household selects organically for that profile.

The Montreal 6A IDF and Montreal EPW are held constant (resolve_epw_path is
patched to always return Montreal) so only the occupancy profile varies.
TARGET_WORKING_PROFILE is restored after each run.

The Worker baseline is already on disk at Comparative_HH1p_1775675140.

Usage:
    py -3 eSim_tests/task30_archetype_runs.py
"""
import os
import sys
import glob
import subprocess
import time
import json
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force UTF-8 on Windows
import io as _io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import eSim_bem_utils.integration as integration_module
import eSim_bem_utils.main as main_module
from eSim_bem_utils import config

ENERGYPLUS_EXE  = config.ENERGYPLUS_EXE
SIM_RESULTS_DIR = main_module.SIM_RESULTS_DIR
TESTS_DIR       = os.path.dirname(__file__)
WEATHER_DIR     = os.path.join(PROJECT_ROOT, "BEM_Setup", "WeatherFile")

MONTREAL_EPW    = os.path.join(WEATHER_DIR,
    "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw")
ARCHETYPES      = ["Student", "Retiree", "ShiftWorker"]


def make_input_seq():
    """Answers for Option 3: Standard mode, Montreal IDF (#1), SingleD (#1), confirm."""
    return iter(["1", "1", "1", "y"])


def run_archetype(archetype_name: str) -> dict:
    """
    Monkey-patch TARGET_WORKING_PROFILE to the archetype profile, run Option 3,
    restore the profile, and return results dict.
    """
    original_profile = integration_module.TARGET_WORKING_PROFILE
    archetype_profile = integration_module.ARCHETYPE_PROFILES[archetype_name]

    print(f"\n{'='*60}")
    print(f"  Archetype: {archetype_name}")
    print(f"  Profile: {archetype_profile}")
    print(f"{'='*60}")

    # --- PATCH ---
    integration_module.TARGET_WORKING_PROFILE = archetype_profile

    selected_hh = {"id": None}
    epw_used    = {"path": MONTREAL_EPW}

    # Wrap find_best_match_household to capture which HH was selected
    real_find = integration_module.find_best_match_household
    def recording_find(schedules, candidates=None, day_type="Weekday"):
        hh = real_find(schedules, candidates, day_type)
        selected_hh["id"] = hh
        return hh

    # Always return Montreal EPW regardless of household's PR
    def fixed_epw(pr_region, weather_dir):
        return MONTREAL_EPW

    answer_iter = make_input_seq()
    patches = [
        mock.patch("builtins.input", side_effect=answer_iter),
        mock.patch.object(integration_module, "find_best_match_household",
                          side_effect=recording_find),
        mock.patch.object(main_module.config, "resolve_epw_path",
                          side_effect=fixed_epw),
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
        # --- RESTORE ---
        integration_module.TARGET_WORKING_PROFILE = original_profile

    # Find new batch dir
    batch_dirs_after = set(glob.glob(os.path.join(SIM_RESULTS_DIR, "Comparative_*")))
    new_dirs = sorted(batch_dirs_after - batch_dirs_before)
    batch_dir = new_dirs[-1] if new_dirs else None

    if batch_dir:
        print(f"  Batch dir: {os.path.basename(batch_dir)}")
    else:
        print("  WARNING: no new batch dir found")

    sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql")) if batch_dir else []
    ran_ok = bool(sql_files)

    # Fallback: direct EnergyPlus invocation
    if batch_dir and not ran_ok:
        print("  ProcessPoolExecutor failed — running EnergyPlus directly (Task 26 fallback)...")
        scenarios = ["2005", "2010", "2015", "2022", "2025", "Default"]
        for sc in scenarios:
            idf_path = os.path.join(batch_dir, sc, f"Scenario_{sc}.idf")
            out_dir  = os.path.join(batch_dir, sc)
            if not os.path.exists(idf_path):
                print(f"    {sc}: IDF not found, skipping")
                continue
            cmd = [ENERGYPLUS_EXE,
                   "--weather", MONTREAL_EPW,
                   "--output-directory", out_dir,
                   "--idd", config.IDD_FILE,
                   idf_path]
            print(f"    Running {sc}...", end=" ", flush=True)
            r = subprocess.run(cmd, capture_output=True, text=True)
            ok = "EnergyPlus Completed Successfully" in r.stdout
            print("OK" if ok else f"FAILED (rc={r.returncode})")
        sql_files = glob.glob(os.path.join(batch_dir, "*", "eplusout.sql"))
        ran_ok = bool(sql_files)

    hh_id = selected_hh["id"]
    print(f"  Selected HH: {hh_id}")
    print(f"  SQL files:   {len(sql_files)}")
    print(f"  EPW used:    {os.path.basename(MONTREAL_EPW)}")

    return {
        "archetype": archetype_name,
        "batch_dir": batch_dir,
        "hh_id":     hh_id,
        "sql_count": len(sql_files),
        "ran_ok":    ran_ok,
    }


if __name__ == "__main__":
    results = []
    for name in ARCHETYPES:
        res = run_archetype(name)
        results.append(res)
        time.sleep(2)  # avoid timestamp collision in batch names

    print("\n" + "=" * 60)
    print("ARCHETYPE RUN SUMMARY")
    print("=" * 60)
    print(f"{'Archetype':<14} {'HH ID':<12} {'SQL':<6} {'Batch dir'}")
    print("-" * 60)
    for r in results:
        bd = os.path.basename(r["batch_dir"]) if r["batch_dir"] else "NONE"
        print(f"{r['archetype']:<14} {str(r['hh_id']):<12} {r['sql_count']:<6} {bd}")

    # Save manifest for downstream scripts
    manifest_path = os.path.join(TESTS_DIR, "task30_archetype_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nManifest written: {os.path.basename(manifest_path)}")

    all_ok = all(r["ran_ok"] for r in results)
    sys.exit(0 if all_ok else 1)
