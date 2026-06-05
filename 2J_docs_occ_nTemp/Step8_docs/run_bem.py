#!/usr/bin/env python3
"""
run_bem.py — 2nd-journal (Step 8) BEM simulation entry point.

Drives the paired Monte-Carlo campaign over the frozen 2022 frame:
  4 dwelling archetypes (MTL set) x 6 climate-zone cities x 5 cycle-years
  (2005/2010/2015/2022/2030) x N households = the load-shape experiment.

This is SEPARATE from the conference/journal-1 run_bem.py at the repo root
(which drives eSim_bem_utils/). It imports the versioned engine copy
eSim_bem_utils_2J (this same folder), so the original engine is never touched.

Run:  py 2J_docs_occ_nTemp/Step8_docs/run_bem.py
"""
import os
import sys
import glob

# Make the versioned engine package importable (it lives next to this file).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eSim_bem_utils_2J.main import (
    run_step8_paired_mc,
    BEM_SETUP_DIR,
    STEP8_BUILDINGS_DIR,
    STEP8_RESULTS_DIR,
    STEP8_ARCHETYPES,
    STEP8_CITIES,
    WEATHER_DIR,
    COMPARATIVE_YEARS,
)


def _find_one(folder, ext, substr):
    hits = [p for p in glob.glob(os.path.join(folder, f"*{ext}"))
            if substr.lower() in os.path.basename(p).lower()]
    return hits[0] if hits else None


def resolve_cell(archetype_name, city_name):
    """Return (idf_path, epw_path, region, dtype, cell_label) for a named cell, or None."""
    arch = next((a for a in STEP8_ARCHETYPES if a["name"] == archetype_name), None)
    city = next((c for c in STEP8_CITIES if c["name"] == city_name), None)
    if not arch or not city:
        return None
    idf = _find_one(STEP8_BUILDINGS_DIR, ".idf", arch["idf"])
    epw = _find_one(WEATHER_DIR, ".epw", city["epw"])
    if not idf or not epw:
        return None
    return idf, epw, city["region"], arch["dtype"], f"{arch['name']}__{city['name']}"


def all_cells():
    return [(a["name"], c["name"]) for a in STEP8_ARCHETYPES for c in STEP8_CITIES]


def report_pools():
    """Print per-(DTYPE x PR) candidate pool sizes from BEM_Schedules_2022.csv."""
    import csv as _csv
    from collections import Counter
    sched = os.path.join(BEM_SETUP_DIR, "BEM_Schedules_2022.csv")
    seen = {}
    with open(sched, encoding="utf-8-sig") as f:
        for row in _csv.DictReader(f):
            hid = row["SIM_HH_ID"]
            if hid not in seen:
                seen[hid] = (row["DTYPE"], row["PR"])
    ctr = Counter(seen.values())
    print("\nPer-(archetype x city) candidate pool sizes (2022 frozen frame):")
    for a in STEP8_ARCHETYPES:
        for c in STEP8_CITIES:
            n = ctr.get((a["dtype"], c["region"]), 0)
            flag = "  <-- THIN (<50): will sample WITH replacement" if n < 50 else ""
            print(f"  {a['name']:13s} x {c['name']:12s} (PR={c['region']:8s}): {n:6d}{flag}")


def print_hpc_plan(n=50, seed=42):
    cells = all_cells()
    nyr = len(COMPARATIVE_YEARS)
    print(f"\n# Step 8 — {len(cells)}-cell HPC array plan (N={n}, seed={seed}, annual)")
    print(f"# One array task = one (archetype x city) cell = {n} HH x {nyr} yr "
          f"= {n*nyr} E+ runs.")
    print(f"# Grand total = {len(cells)} cells x {n*nyr} = {len(cells)*n*nyr} annual runs.")
    for a, c in cells:
        print(f"py run_paired_mc.py --archetype {a} --city {c} --n {n} --seed {seed} "
              f"--sim-mode standard")


def _menu():
    print("\n=== Step 8 (2nd journal) — paired Monte-Carlo runner ===")
    print(f"  Engine : eSim_bem_utils_2J  |  years: {', '.join(COMPARATIVE_YEARS)}")
    print(f"  Results: {STEP8_RESULTS_DIR}")
    print("  1. Smoke test (1 cell: SingleD x Montreal, N=2, 2022+2030, annual)")
    print("  2. Run ONE cell (choose archetype + city, N=50, annual)")
    print("  3. Run FULL grid locally (all cells, N=50, annual)  [VERY LONG]")
    print("  4. Report per-cell pool sizes")
    print("  5. Print HPC array plan")
    print("  q. Quit")
    return input("Select: ").strip().lower()


def _choose(items, label):
    for i, it in enumerate(items, 1):
        print(f"  {i}. {it}")
    while True:
        s = input(f"Select {label} (1-{len(items)}): ").strip()
        try:
            k = int(s) - 1
            if 0 <= k < len(items):
                return items[k]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


def main():
    arch_names = [a["name"] for a in STEP8_ARCHETYPES]
    city_names = [c["name"] for c in STEP8_CITIES]
    while True:
        ch = _menu()
        if ch == "q":
            break
        elif ch == "1":
            idf, epw, region, dtype, label = resolve_cell("SingleD", "Montreal_6A")
            run_step8_paired_mc(idf, epw, region, dtype, n=2, seed=42,
                                years=("2022", "2030"), sim_mode="standard",
                                cell_label=f"SMOKE_{label}")
        elif ch == "2":
            a = _choose(arch_names, "archetype")
            c = _choose(city_names, "city")
            cell = resolve_cell(a, c)
            if not cell:
                print("Could not resolve that cell (missing IDF/EPW?).")
                continue
            idf, epw, region, dtype, label = cell
            run_step8_paired_mc(idf, epw, region, dtype, n=50, seed=42, sim_mode="standard")
        elif ch == "3":
            cells = all_cells()
            total = len(cells) * 50 * len(COMPARATIVE_YEARS)
            confirm = input(f"Run all {len(cells)} cells x 50 HH x {len(COMPARATIVE_YEARS)} yr "
                            f"= {total} annual E+ runs locally? (y/n): ")
            if confirm.lower() != "y":
                continue
            summary = []
            for a, c in cells:
                cell = resolve_cell(a, c)
                if not cell:
                    print(f"skip {a} x {c} (unresolved)")
                    continue
                idf, epw, region, dtype, label = cell
                summary.append(run_step8_paired_mc(idf, epw, region, dtype,
                                                   n=50, seed=42, sim_mode="standard"))
            ok = sum(1 for s in summary if s.get("status") == "ok")
            print(f"\nGrid complete: {ok}/{len(summary)} cells ok.")
        elif ch == "4":
            report_pools()
        elif ch == "5":
            print_hpc_plan()
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()
