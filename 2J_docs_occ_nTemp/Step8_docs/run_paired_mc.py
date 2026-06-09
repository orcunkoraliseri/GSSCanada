#!/usr/bin/env python3
"""
run_paired_mc.py — headless single-cell driver for the Step 8 paired MC.

One invocation = ONE (archetype x climate-city) cell = N households x 5 years
of (annual) EnergyPlus runs. Designed for a SLURM/cloud job array: one array
task per cell (24 cells total). The per-cell seed is deterministic, so each
task reproduces the SAME household sample independently of the others.

Usage (one cell):
  py run_paired_mc.py --archetype SingleD --city Montreal_6A \
       --n 50 --seed 42 --sim-mode standard

Use `py run_bem.py` -> option 5 to print the full 24-cell array plan.

Exit codes: 0 ok | 1 run failed | 2 setup/arg error.
"""
import argparse
import os
import sys

# Make the versioned engine package + run_bem helpers importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eSim_bem_utils_2J.main import STEP8_ARCHETYPES, STEP8_CITIES, COMPARATIVE_YEARS
from eSim_bem_utils_2J import integration as _integ
from run_bem import resolve_cell, run_step8_paired_mc


def main():
    arch_names = [a["name"] for a in STEP8_ARCHETYPES]
    city_names = [c["name"] for c in STEP8_CITIES]

    p = argparse.ArgumentParser(description="Step 8 single-cell paired MC (headless).")
    p.add_argument("--archetype", required=True, choices=arch_names)
    p.add_argument("--city", required=True, choices=city_names)
    p.add_argument("--n", type=int, default=50, help="households per cell (default 50).")
    p.add_argument("--seed", type=int, default=42, help="base seed (default 42).")
    p.add_argument("--sim-mode", default="standard",
                   choices=["standard", "weekly", "comparison"],
                   help="standard = full annual (campaign); weekly = fast smoke.")
    p.add_argument("--years", default=None,
                   help="comma-separated years; default = all 5 (2005..2030).")
    p.add_argument("--output-dir", default=None,
                   help="cell output dir; default = SimResults_Step8/<archetype>__<city>.")
    p.add_argument("--sched-dir", default=None,
                   help="override schedule CSV dir (default=BEM_Setup); pass private dir for isolation.")
    args = p.parse_args()

    if args.n < 1:
        print(f"ERROR: --n must be >= 1, got {args.n}", flush=True)
        sys.exit(2)

    cell = resolve_cell(args.archetype, args.city)
    if not cell:
        print(f"ERROR: could not resolve cell {args.archetype} x {args.city} "
              f"(missing IDF or EPW?).", flush=True)
        sys.exit(2)
    idf, epw, region, dtype, label = cell
    years = tuple(y.strip() for y in args.years.split(",")) if args.years else None

    # Pre-load schedules from override dir if --sched-dir provided
    sched_preload = None
    if args.sched_dir:
        yrs_to_load = [str(y) for y in (list(years) if years else list(COMPARATIVE_YEARS))]
        sched_preload = {}
        for y in yrs_to_load:
            csv_path = os.path.join(args.sched_dir, f"BEM_Schedules_{y}.csv")
            if not os.path.exists(csv_path):
                print(f"ERROR: missing {csv_path}", flush=True)
                sys.exit(2)
            print(f"  Loading BEM_Schedules_{y}.csv from {args.sched_dir}", flush=True)
            sched_preload[y] = _integ.load_schedules(csv_path, dwelling_type=dtype, region=region)

    res = run_step8_paired_mc(
        idf, epw, region, dtype,
        n=args.n, seed=args.seed, years=years,
        sim_mode=args.sim_mode, output_dir=args.output_dir, cell_label=label,
        schedules=sched_preload,
    )

    status = res.get("status")
    if status == "ok":
        print(f"\nDONE {label}: E+ {res['n_run_ok']}/{res['n_jobs']} ok, "
              f"{res['n_hourly_ok']} hourly -> {res['output_dir']}", flush=True)
        sys.exit(0)
    print(f"\nFAILED {label}: status={status} | "
          f"E+ {res.get('n_run_ok', '?')}/{res.get('n_jobs', '?')} ok | "
          f"{res.get('error', '')}", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
