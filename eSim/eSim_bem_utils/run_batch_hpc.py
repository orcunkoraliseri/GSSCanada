"""
Headless batch runner for HPC (SLURM).

Replaces the interactive Option 10 menu with CLI arguments so that
SLURM job array tasks can invoke one neighbourhood simulation without
any user input.

Usage:
    python run_batch_hpc.py \
        --idf BEM_Setup/Neighbourhoods/NUS_RC1.idf \
        --region Quebec \
        --sim-mode weekly \
        --iter-count 20 \
        --output-dir /speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20

The --output-dir is the shared parent batch directory; a per-neighbourhood
subdirectory (e.g. .../BatchAll_MC_N20/NUS_RC1/) is created inside it by
_run_mc_neighbourhood, matching the layout produced by Option 10 locally.

Exit codes:
    0  — simulation completed successfully
    1  — simulation failed (error written to stdout)
    2  — argument / setup error (bad paths, missing files)
"""

import argparse
import os
import sys

# Ensure project root is on sys.path so eSim_bem_utils imports work when this
# script is invoked directly (e.g. python eSim_bem_utils/run_batch_hpc.py ...).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import neighbourhood, config

# Import shared constants and the MC helper from main.py.
# main.py is safe to import: its menu loop is guarded by __name__ == '__main__'.
from eSim_bem_utils.main import (
    _run_mc_neighbourhood,
    WEATHER_DIR,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Headless MC neighbourhood simulation for SLURM."
    )
    parser.add_argument("--idf", required=True,
                        help="Path to the neighbourhood IDF file.")
    parser.add_argument("--region", required=True,
                        help="Province/region string matching BEM CSV PR column "
                             "(e.g. Quebec, Ontario, BC).")
    parser.add_argument("--sim-mode", default="weekly",
                        help="Simulation mode passed to EnergyPlus wrapper "
                             "(default: weekly).")
    parser.add_argument("--iter-count", type=int, default=20,
                        help="Number of Monte Carlo iterations (default: 20).")
    parser.add_argument("--output-dir", required=True,
                        help="Parent output directory; a per-neighbourhood "
                             "subdirectory is created inside it.")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel EnergyPlus workers per MC iteration "
                             "(default: 1, serial). Pass $SLURM_CPUS_PER_TASK on "
                             "HPC to fill node cores. Full iteration-level "
                             "ProcessPoolExecutor is deferred (>40-line refactor).")
    parser.add_argument("--use-tmpdir", action="store_true", default=False,
                        help="Run each EnergyPlus instance inside $TMPDIR, then "
                             "copy eplusout.sql and CSVs back to --output-dir. "
                             "Reduces concurrent write pressure on /speed-scratch.")
    args = parser.parse_args()

    # Propagate flags to simulation layer via env vars (avoids signature changes
    # in _run_mc_neighbourhood; default=1 keeps smoke-test serial behaviour).
    os.environ["ESIM_WORKERS"] = str(args.workers)
    if args.use_tmpdir:
        os.environ["ESIM_USE_TMPDIR"] = "1"

    # --- Validate inputs ---
    idf_path = os.path.abspath(args.idf)
    if not os.path.isfile(idf_path):
        print(f"ERROR: IDF file not found: {idf_path}", flush=True)
        sys.exit(2)

    if args.iter_count < 1:
        print(f"ERROR: --iter-count must be >= 1, got {args.iter_count}", flush=True)
        sys.exit(2)

    # --- Resolve EPW ---
    try:
        epw_path = config.resolve_epw_path(args.region, WEATHER_DIR)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", flush=True)
        sys.exit(2)

    print(f"IDF      : {idf_path}", flush=True)
    print(f"EPW      : {epw_path}", flush=True)
    print(f"Region   : {args.region}", flush=True)
    print(f"Sim mode : {args.sim_mode}", flush=True)
    print(f"Iterations: {args.iter_count}", flush=True)
    print(f"Output   : {args.output_dir}", flush=True)

    # --- Read building metadata from IDF ---
    try:
        n_buildings = neighbourhood.get_num_buildings_from_idf(idf_path)
        if n_buildings == 0:
            raise RuntimeError("0 buildings detected in IDF.")
        building_dtypes = neighbourhood.get_building_dtypes_from_idf(idf_path)
    except Exception as exc:
        print(f"ERROR reading IDF metadata: {exc}", flush=True)
        sys.exit(2)

    print(f"Buildings: {n_buildings}", flush=True)

    # --- Create output directory ---
    os.makedirs(args.output_dir, exist_ok=True)

    # --- Run MC simulation ---
    result = _run_mc_neighbourhood(
        idf_path,
        epw_path,
        args.region,
        args.sim_mode,
        args.iter_count,
        args.output_dir,
        n_buildings,
        building_dtypes,
    )

    if result.get("status") == "ok":
        print(f"\nDone: {os.path.basename(idf_path)} — output: {result.get('output_dir')}", flush=True)
        sys.exit(0)
    else:
        print(f"\nFAILED: {os.path.basename(idf_path)} — {result.get('error')}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
