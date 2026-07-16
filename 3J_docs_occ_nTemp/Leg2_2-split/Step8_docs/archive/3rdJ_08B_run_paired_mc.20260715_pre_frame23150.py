"""3rdJ_08B_run_paired_mc.py — Step 8B: Residential Paired MC driver (3J Leg-2).

Headless single-cell driver for the SLURM array.  One invocation = one
(archetype × city × scenario) cell.  N=50 households are drawn from the 3J
23,211-HH stock using a deterministic per-cell seed so that all scenario tasks
for the same (arch × city) pair draw the SAME 50 households — enforcing the
paired design within `run_step8_paired_mc()`.

SLURM usage (see run_residential_array.sh):
    Cell index SLURM_ARRAY_TASK_ID ∈ [0..167]
    idx → (arch_idx, city_idx, scen_idx) via int division / modulo.

Local smoke-test usage:
    py 3rdJ_08B_run_paired_mc.py --arch SingleD --city Toronto_5A --scenario 2022 --n 2 --mode weekly
    (mode=weekly = 24 TMY weeks only, much faster; never use for the real campaign)

Pool-size audit (OD-8F):
    py 3rdJ_08B_run_paired_mc.py --pool-audit
    Prints per-(DTYPE × PR) counts from BEM_Schedules_2split_2022.csv and
    flags any cell < 50 HH (→ with-replacement sampling for that cell).

2026-06-28 built.
"""
import os
import sys
import argparse
import csv
from pathlib import Path
from collections import Counter

# Engine lives two directories up from this file (Step8_docs/).
HERE = Path(__file__).resolve().parent  # Step8_docs/
sys.path.insert(0, str(HERE))

from eSim_bem_utils_3J.main import (
    run_step8_paired_mc,
    STEP8_ARCHETYPES,
    STEP8_CITIES,
    STEP8_BUILDINGS_DIR,
    STEP8_RESULTS_DIR,
    SCHEDULE_FILE_MAP,
    COMPARATIVE_SCENARIOS,
    WEATHER_DIR,
)

import glob as _glob


def _find_one(folder, ext, substr):
    hits = [p for p in _glob.glob(os.path.join(folder, f"*{ext}"))
            if substr.lower() in os.path.basename(p).lower()]
    return hits[0] if hits else None


def resolve_cell(arch_name, city_name):
    """Return (idf_path, epw_path, region, dtype, cell_label) or raise."""
    arch = next((a for a in STEP8_ARCHETYPES if a["name"] == arch_name), None)
    city = next((c for c in STEP8_CITIES if c["name"] == city_name), None)
    if arch is None:
        raise ValueError(f"Unknown archetype '{arch_name}'. Valid: {[a['name'] for a in STEP8_ARCHETYPES]}")
    if city is None:
        raise ValueError(f"Unknown city '{city_name}'. Valid: {[c['name'] for c in STEP8_CITIES]}")
    idf = _find_one(STEP8_BUILDINGS_DIR, ".idf", arch["idf"])
    epw = _find_one(WEATHER_DIR, ".epw", city["epw"])
    if idf is None:
        raise FileNotFoundError(f"IDF not found for arch={arch_name} (substr='{arch['idf']}') "
                                f"in {STEP8_BUILDINGS_DIR}")
    if epw is None:
        raise FileNotFoundError(f"EPW not found for city={city_name} (substr='{city['epw']}') "
                                f"in {WEATHER_DIR}")
    label = f"{arch['name']}__{city['name']}"
    return idf, epw, city["region"], arch["dtype"], label


def cell_is_done(arch_name, city_name, scenario, out_root, n=50):
    """Return True if ALL N×1 hourly_meters.csv exist for this cell+scenario."""
    label = f"{STEP8_ARCHETYPES[[a['name'] for a in STEP8_ARCHETYPES].index(arch_name)]['name']}__{city_name}"
    cell_dir = os.path.join(out_root, label)
    if not os.path.isdir(cell_dir):
        return False
    found = 0
    for root, _dirs, files in os.walk(cell_dir):
        if "hourly_meters.csv" in files and scenario in root:
            found += 1
    return found >= n


def run_pool_audit(scenario="2022"):
    """OD-8F: print per-(DTYPE × PR) pool sizes. Flag any < 50."""
    csv_path = SCHEDULE_FILE_MAP.get(scenario)
    if not csv_path or not os.path.exists(csv_path):
        print(f"ERROR: schedule file not found for '{scenario}': {csv_path}")
        return
    seen = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            hid = row["SIM_HH_ID"]
            if hid not in seen:
                seen[hid] = (row["DTYPE"], row["PR"])
    ctr = Counter(seen.values())
    print(f"\nOD-8F Pool-size audit (from {os.path.basename(csv_path)})")
    print(f"{'Arch':13s} {'City/PR':12s}  {'PR':10s}  {'Pool':>7s}  {'Status'}")
    any_thin = False
    for a in STEP8_ARCHETYPES:
        for c in STEP8_CITIES:
            n = ctr.get((a["dtype"], c["region"]), 0)
            thin = n < 50
            flag = "  <-- THIN: with-replacement" if thin else ""
            if thin:
                any_thin = True
            print(f"  {a['name']:13s} {c['name']:12s}  {c['region']:10s}  {n:7d}{flag}")
    if not any_thin:
        print("\n  [GATE PASS §3.3] All cells have >= 50 HH. No with-replacement needed.")
    else:
        print("\n  [NOTE §3.3] Thin cells will use with-replacement sampling (logged in manifest).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Step 8B residential paired-MC driver")
    ap.add_argument("--cell-idx", type=int, default=None,
                    help="SLURM_ARRAY_TASK_ID (0-167); overrides --arch/--city/--scenario")
    ap.add_argument("--arch",     default=None)
    ap.add_argument("--city",     default=None)
    ap.add_argument("--scenario", default=None,
                    help="One of: " + " | ".join(COMPARATIVE_SCENARIOS))
    ap.add_argument("--n",        type=int,   default=50,
                    help="MC sample size (default 50; use 2 for smoke test)")
    ap.add_argument("--seed",     type=int,   default=42)
    ap.add_argument("--mode",     default="standard",
                    choices=["standard", "weekly"],
                    help="'standard' = full annual (campaign); 'weekly' = 24 TMY weeks (smoke)")
    ap.add_argument("--out-dir",  default=None,
                    help="Override output root (default STEP8_RESULTS_DIR)")
    ap.add_argument("--pool-audit", action="store_true",
                    help="Print OD-8F pool audit and exit")
    ap.add_argument("--skip-done", action="store_true", default=True,
                    help="Skip cell if hourly_meters.csv already complete (resume-on-restart)")
    args = ap.parse_args()

    if args.pool_audit:
        run_pool_audit()
        return

    # Decode index or use named arguments
    if args.cell_idx is not None:
        idx = args.cell_idx
        na = len(STEP8_ARCHETYPES)  # 4
        nc = len(STEP8_CITIES)      # 6
        ns = len(COMPARATIVE_SCENARIOS)  # 7
        if not (0 <= idx < na * nc * ns):
            raise ValueError(f"--cell-idx {idx} out of range [0, {na*nc*ns - 1}]")
        scen_idx = idx % ns
        city_idx = (idx // ns) % nc
        arch_idx = idx // (nc * ns)
        arch_name = STEP8_ARCHETYPES[arch_idx]["name"]
        city_name = STEP8_CITIES[city_idx]["name"]
        scenario  = COMPARATIVE_SCENARIOS[scen_idx]
        print(f"[cell-idx={idx}] arch={arch_name}  city={city_name}  scenario={scenario}")
    else:
        if not all([args.arch, args.city, args.scenario]):
            ap.error("Provide --cell-idx OR (--arch AND --city AND --scenario)")
        arch_name = args.arch
        city_name = args.city
        scenario  = args.scenario

    if scenario not in COMPARATIVE_SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'. Valid: {COMPARATIVE_SCENARIOS}")

    out_root = args.out_dir or STEP8_RESULTS_DIR
    idf, epw, region, dtype, label = resolve_cell(arch_name, city_name)

    # Resume-on-restart gate
    if args.skip_done and cell_is_done(arch_name, city_name, scenario, out_root, args.n):
        print(f"[SKIP] {label} x {scenario} already has >= {args.n} hourly_meters.csv. Done.")
        return

    cell_out = os.path.join(out_root, label)
    print(f"  IDF      : {os.path.basename(idf)}")
    print(f"  EPW      : {os.path.basename(epw)}")
    print(f"  Region   : {region}  (PR filter in schedule CSV)")
    print(f"  DTYPE    : {dtype}")
    print(f"  Scenario : {scenario}")
    print(f"  N        : {args.n}  seed={args.seed}  mode={args.mode}")
    print(f"  Output   : {cell_out}")

    result = run_step8_paired_mc(
        idf_path=idf,
        epw_path=epw,
        region=region,
        dtype=dtype,
        n=args.n,
        seed=args.seed,
        years=[scenario],  # one scenario per task; same N=50 HHs across tasks (paired by seed)
        sim_mode=args.mode,
        output_dir=cell_out,
        cell_label=label,
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
