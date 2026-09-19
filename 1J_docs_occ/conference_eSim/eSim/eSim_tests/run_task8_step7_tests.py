#!/usr/bin/env python3
"""
Task 8: run Step 7b + 7c + 7d from DONE_option8_batch_all_neighbourhoods.md
sequentially in one shot.

Drives the BEM helpers directly (no interactive menu). Each substep stops
the run on the first failure so later steps do not run against broken
state. Intended to validate the Option 7 refactor and Option 10 batch
driver without launching `run_bem.py` six times by hand.

Usage (from repo root):
    python eSim_tests/run_task8_step7_tests.py                 # 7b, 7c, 7d
    python eSim_tests/run_task8_step7_tests.py --iter 2        # override iter_count
    python eSim_tests/run_task8_step7_tests.py --sim-mode weekly
    python eSim_tests/run_task8_step7_tests.py --skip-7d       # skip failure injection
    python eSim_tests/run_task8_step7_tests.py --only 7b       # run a single substep

Exit code is non-zero if any substep fails.
"""

import argparse
import glob
import os
import shutil
import sys
import time
import traceback

# Make repo root importable when this script is run from eSim_tests/.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eSim_bem_utils import main as bem_main  # noqa: E402
from eSim_bem_utils import neighbourhood  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _banner(title: str) -> None:
    line = "=" * 72
    print(f"\n{line}\n{title}\n{line}")


def _discover_neighbourhoods() -> list:
    files = sorted(
        glob.glob(os.path.join(bem_main.NEIGHBOURHOODS_DIR, "NUS_RC*.idf")),
        key=bem_main._sort_key_by_city,
    )
    return files


def _pick_epw(epw_index: int) -> tuple:
    epws = sorted(
        glob.glob(os.path.join(bem_main.WEATHER_DIR, "*.epw")),
        key=bem_main._sort_key_by_city,
    )
    if not epws:
        raise RuntimeError(f"No EPW files in {bem_main.WEATHER_DIR}")
    if epw_index >= len(epws):
        raise RuntimeError(
            f"--epw-index {epw_index} out of range (found {len(epws)} EPWs)"
        )
    epw = epws[epw_index]
    region = bem_main.get_region_from_epw(epw)
    return epw, region


def _check_artifacts(result: dict, substep: str) -> list:
    """Return list of problems found in the per-neighbourhood result dict."""
    problems = []
    out_dir = result.get("output_dir")
    if not out_dir or not os.path.isdir(out_dir):
        problems.append(f"{substep}: output_dir missing ({out_dir})")
        return problems
    agg = result.get("aggregated_csv")
    if agg and not os.path.exists(agg):
        problems.append(f"{substep}: aggregated_csv missing ({agg})")
    eui = result.get("eui_plot")
    if eui and not os.path.exists(eui):
        problems.append(f"{substep}: eui_plot missing ({eui})")
    ts = result.get("ts_plot")
    if ts and not os.path.exists(ts):
        problems.append(f"{substep}: ts_plot missing ({ts})")
    return problems


# --------------------------------------------------------------------------- #
# 7b — refactor regression: single neighbourhood via _run_mc_neighbourhood
# --------------------------------------------------------------------------- #

def step_7b(iter_count: int, sim_mode: str, epw_index: int) -> dict:
    _banner("Step 7b — refactor regression: Option 7 path, NUS_RC1")

    neighbourhoods = _discover_neighbourhoods()
    if not neighbourhoods:
        raise RuntimeError("No NUS_RC*.idf files found")
    idf_path = neighbourhoods[0]
    print(f"  IDF: {os.path.basename(idf_path)}")

    epw, region = _pick_epw(epw_index)
    print(f"  EPW: {os.path.basename(epw)} (region='{region}')")

    n_buildings = neighbourhood.get_num_buildings_from_idf(idf_path)
    if n_buildings == 0:
        raise RuntimeError(f"0 buildings detected in {idf_path}")
    dtypes = neighbourhood.get_building_dtypes_from_idf(idf_path)
    print(f"  n_buildings={n_buildings}  sim_mode={sim_mode}  iter={iter_count}")

    batch_dir = os.path.join(
        bem_main.SIM_RESULTS_DIR,
        f"Task8_7b_MC_N{iter_count}_{int(time.time())}",
    )
    os.makedirs(batch_dir, exist_ok=True)

    t0 = time.time()
    result = bem_main._run_mc_neighbourhood(
        idf_path, epw, region, sim_mode, iter_count, batch_dir,
        n_buildings, dtypes,
    )
    dt = time.time() - t0
    result["elapsed_s"] = round(dt, 1)

    print(f"\n  status={result.get('status')}  elapsed={dt:.1f}s")
    if result.get("status") != "ok":
        raise RuntimeError(f"7b failed: {result.get('error')}")

    problems = _check_artifacts(result, "7b")
    if problems:
        raise RuntimeError("7b artifact check failed:\n    " + "\n    ".join(problems))

    print("  7b PASS")
    return {"substep": "7b", "batch_dir": batch_dir, "result": result}


# --------------------------------------------------------------------------- #
# 7c — batch smoke: all NUS_RC*.idf via _run_mc_neighbourhood loop
# --------------------------------------------------------------------------- #

def step_7c(iter_count: int, sim_mode: str, epw_index: int,
            tag: str = "7c") -> dict:
    _banner(f"Step {tag} — batch smoke: ALL NUS_RC*.idf (single EPW)")

    neighbourhoods = _discover_neighbourhoods()
    if not neighbourhoods:
        raise RuntimeError("No NUS_RC*.idf files found")
    print(f"  Found {len(neighbourhoods)} neighbourhoods:")
    for p in neighbourhoods:
        print(f"    - {os.path.basename(p)}")

    epw, region = _pick_epw(epw_index)
    print(f"  Shared EPW: {os.path.basename(epw)} (region='{region}')")
    print(f"  sim_mode={sim_mode}  iter={iter_count}")

    ts = int(time.time())
    batch_dir = os.path.join(
        bem_main.SIM_RESULTS_DIR,
        f"Task8_{tag}_BatchAll_MC_N{iter_count}_{ts}",
    )
    os.makedirs(batch_dir, exist_ok=True)
    log_path = os.path.join(batch_dir, "batch_log.txt")

    rows = []
    for i, idf_path in enumerate(neighbourhoods, 1):
        name = os.path.basename(idf_path)
        t0 = time.time()
        print(f"\n  [{i}/{len(neighbourhoods)}] {name} — start")
        try:
            n_buildings = neighbourhood.get_num_buildings_from_idf(idf_path)
            if n_buildings == 0:
                raise RuntimeError("0 buildings detected")
            dtypes = neighbourhood.get_building_dtypes_from_idf(idf_path)

            result = bem_main._run_mc_neighbourhood(
                idf_path, epw, region, sim_mode, iter_count, batch_dir,
                n_buildings, dtypes,
            )
        except Exception as e:
            result = {
                "idf": name, "n_buildings": "", "output_dir": "",
                "aggregated_csv": "", "eui_plot": "", "ts_plot": "",
                "status": "failed", "error": str(e),
            }
        dt = time.time() - t0
        result["elapsed_s"] = round(dt, 1)
        rows.append(result)

        with open(log_path, "a") as lf:
            lf.write(
                f"[{i}/{len(neighbourhoods)}] {name} "
                f"{result.get('status','?')} {dt:.1f}s "
                f"{result.get('error','') or ''}\n"
            )
        print(
            f"  [{i}/{len(neighbourhoods)}] {name} — "
            f"{result.get('status','?')} ({dt:.1f}s)"
        )

    csv_path = os.path.join(batch_dir, "batch_summary.csv")
    with open(csv_path, "w", newline="") as cf:
        cf.write("idf,n_buildings,status,elapsed_s,error,aggregated_csv,eui_plot,ts_plot\n")
        for r in rows:
            cf.write(",".join([
                str(r.get("idf", "")),
                str(r.get("n_buildings", "")),
                str(r.get("status", "")),
                str(r.get("elapsed_s", "")),
                (str(r.get("error") or "")).replace(",", ";"),
                str(r.get("aggregated_csv", "") or ""),
                str(r.get("eui_plot", "") or ""),
                str(r.get("ts_plot", "") or ""),
            ]) + "\n")

    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\n  {tag} summary: {ok}/{len(rows)} ok")
    print(f"  batch_dir: {batch_dir}")

    if tag == "7c":
        # Strict pass criterion: every neighbourhood must succeed.
        if ok != len(rows):
            failed = [r for r in rows if r.get("status") != "ok"]
            msg = "\n    ".join(
                f"{r.get('idf')}: {r.get('error')}" for r in failed
            )
            raise RuntimeError(f"7c failures:\n    {msg}")
        # Artifact check on every row.
        problems = []
        for r in rows:
            problems.extend(_check_artifacts(r, f"7c:{r.get('idf')}"))
        if problems:
            raise RuntimeError("7c artifact check failed:\n    " + "\n    ".join(problems))
        print("  7c PASS")

    return {
        "substep": tag, "batch_dir": batch_dir,
        "rows": rows, "summary_csv": csv_path, "log": log_path,
    }


# --------------------------------------------------------------------------- #
# 7d — failure isolation: inject a broken synthetic IDF and re-run 7c
# --------------------------------------------------------------------------- #

BROKEN_IDF_NAME = "NUS_RC_broken_TASK8.idf"


def step_7d(iter_count: int, sim_mode: str, epw_index: int) -> dict:
    _banner("Step 7d — failure isolation: inject broken NUS_RC IDF")

    broken_path = os.path.join(bem_main.NEIGHBOURHOODS_DIR, BROKEN_IDF_NAME)
    if os.path.exists(broken_path):
        raise RuntimeError(
            f"{BROKEN_IDF_NAME} already exists at {broken_path}; "
            "refusing to overwrite. Delete it manually and retry."
        )

    print(f"  Injecting broken IDF: {broken_path}")
    # 0-building file — neighbourhood.get_num_buildings_from_idf should return 0
    # (or raise), which triggers the batch loop's try/except.
    with open(broken_path, "w") as bf:
        bf.write("! Task 8 failure-injection stub — intentionally invalid\n")

    try:
        result = step_7c(iter_count, sim_mode, epw_index, tag="7d")
    finally:
        if os.path.exists(broken_path):
            os.remove(broken_path)
            print(f"  Removed broken IDF: {broken_path}")

    rows = result["rows"]
    broken_rows = [r for r in rows if r.get("idf") == BROKEN_IDF_NAME]
    other_rows = [r for r in rows if r.get("idf") != BROKEN_IDF_NAME]

    if not broken_rows:
        raise RuntimeError(
            "7d: broken IDF did not appear in batch_summary — glob filter mismatch?"
        )
    if broken_rows[0].get("status") != "failed":
        raise RuntimeError(
            f"7d: broken IDF did NOT fail as expected (status={broken_rows[0].get('status')})"
        )
    bad = [r for r in other_rows if r.get("status") != "ok"]
    if bad:
        msg = ", ".join(f"{r.get('idf')}={r.get('status')}" for r in bad)
        raise RuntimeError(f"7d: sibling neighbourhoods should all be ok, got: {msg}")

    print(f"  7d PASS — broken IDF isolated, {len(other_rows)} siblings ok")
    return result


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    p = argparse.ArgumentParser(description="Task 8: chained Step 7b/7c/7d runner")
    p.add_argument("--iter", type=int, default=2, dest="iter_count",
                   help="Monte Carlo iteration count (default: 2)")
    p.add_argument("--sim-mode", default="weekly",
                   choices=["standard", "weekly", "comparison"],
                   help="Simulation mode passed to _run_mc_neighbourhood (default: weekly)")
    p.add_argument("--epw-index", type=int, default=0,
                   help="Index into sorted EPW list for the shared EPW (default: 0)")
    p.add_argument("--skip-7d", action="store_true",
                   help="Skip the failure-injection substep")
    p.add_argument("--only", choices=["7b", "7c", "7d"],
                   help="Run only the named substep")
    args = p.parse_args()

    substeps = []
    if args.only:
        substeps = [args.only]
    else:
        substeps = ["7b", "7c"]
        if not args.skip_7d:
            substeps.append("7d")

    print(f"Task 8 runner — substeps={substeps} iter={args.iter_count} "
          f"sim_mode={args.sim_mode} epw_index={args.epw_index}")
    print(f"Repo root: {REPO_ROOT}")

    t_start = time.time()
    failures = []

    for step in substeps:
        try:
            if step == "7b":
                step_7b(args.iter_count, args.sim_mode, args.epw_index)
            elif step == "7c":
                step_7c(args.iter_count, args.sim_mode, args.epw_index)
            elif step == "7d":
                step_7d(args.iter_count, args.sim_mode, args.epw_index)
        except Exception as e:
            print(f"\n!!! {step} FAILED: {e}")
            traceback.print_exc()
            failures.append(step)
            # Stop on first failure — later substeps assume earlier ones passed.
            break

    dt = time.time() - t_start
    _banner(f"Task 8 complete — elapsed {dt/60:.1f} min")
    if failures:
        print(f"FAILED substeps: {failures}")
        return 1
    print(f"PASS substeps: {substeps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
