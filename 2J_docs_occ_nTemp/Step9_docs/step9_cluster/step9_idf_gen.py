#!/usr/bin/env python3
"""
step9_idf_gen.py — Stage A: generate paired baseline + activity IDFs for Step 9.

Creates IDFs for 3 cells x N=20 HH x 2 years x 2 treatments = 240 IDFs.
- baseline: loaded from BEM_Schedules_{year}_CLASSIC_BAK_2026-05-31.csv (13-col;
  integration.py uses presence-filter path when Equipment_Fraction column absent)
- activity: loaded from BEM_Schedules_{year}.csv (17-col with Step-9 fracs;
  integration.py uses activity-driven path when Equip_Design_W > 0)

Sampling is deterministic via _step8_cell_seed(seed=42, cell_label) — reproduces
the same HH sample as the _bigtest campaign.

Writes all IDFs under:
  <run_root>/idfs/<cell_label>/<treatment>/sample_XXX_HHyyy/<year>/Scenario_<year>.idf
Writes:
  <run_root>/step9_manifest.csv  — (idx, cell, treatment, hh_id, year, idf_path, epw_path)

Usage:
  python step9_idf_gen.py --root /speed-scratch/o_iseri/step9_run --n 20 --seed 42
"""
import argparse
import csv
import hashlib
import os
import random
import sys
from pathlib import Path

# Make Step8_docs importable (engine lives there)
HERE   = Path(__file__).resolve().parent
S9DOCS = HERE.parent               # Step9_docs/
ROOT2J = S9DOCS.parent             # 2J_docs_occ_nTemp/
S8DOCS = ROOT2J / "Step8_docs"     # 2J_docs_occ_nTemp/Step8_docs/
sys.path.insert(0, str(S8DOCS))    # for eSim_bem_utils_2J + run_bem
sys.path.insert(0, str(ROOT2J))    # for activity_loads (needed by 07_aug_to_bem via import)

from eSim_bem_utils_2J import integration
from eSim_bem_utils_2J.main import (
    STEP8_ARCHETYPES, STEP8_CITIES, STEP8_BUILDINGS_DIR,
    WEATHER_DIR, BEM_SETUP_DIR,
)

# Three cells matching _bigtest
CELLS = [
    {"archetype": "SingleD",  "city": "Winnipeg_7A",  "dtype": "SingleD",  "region": "Prairies"},
    {"archetype": "HighRise", "city": "Montreal_6A",  "dtype": "HighRise", "region": "Quebec"},
    {"archetype": "MidRise",  "city": "Toronto_5A",   "dtype": "MidRise",  "region": "Ontario"},
]
YEARS      = ["2022", "2030"]
TREATMENTS = ["baseline", "activity"]


def _cell_seed(base: int, label: str) -> int:
    h = int(hashlib.sha256(label.encode("utf-8")).hexdigest()[:8], 16)
    return (int(base) * 1_000_003 + h) % (2 ** 31)


def _find_one(folder, ext, substr):
    import glob as _g
    hits = [p for p in _g.glob(os.path.join(folder, f"*{ext}"))
            if substr.lower() in os.path.basename(p).lower()]
    return hits[0] if hits else None


def _resolve_idf_epw(arch_name, city_name):
    arch = next((a for a in STEP8_ARCHETYPES if a["name"] == arch_name), None)
    city = next((c for c in STEP8_CITIES     if c["name"] == city_name), None)
    if not arch or not city:
        return None, None
    idf = _find_one(STEP8_BUILDINGS_DIR, ".idf", arch["idf"])
    epw = _find_one(WEATHER_DIR,         ".epw", city["epw"])
    return idf, epw


def _sched_csv(year: str, treatment: str) -> str:
    """Return path to the correct BEM_Schedules CSV for this treatment."""
    if treatment == "baseline":
        # 13-col baseline derived from the SAME run as activity — guaranteed same HH IDs.
        return os.path.join(BEM_SETUP_DIR, f"BEM_Schedules_{year}_baseline.csv")
    else:  # activity
        return os.path.join(BEM_SETUP_DIR, f"BEM_Schedules_{year}.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/speed-scratch/o_iseri/step9_run")
    ap.add_argument("--n",    type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    run_root  = args.root
    idf_root  = os.path.join(run_root, "idfs")
    manifest  = os.path.join(run_root, "step9_manifest.csv")
    os.makedirs(idf_root, exist_ok=True)

    print(f"=== Step 9 IDF generator | n={args.n} seed={args.seed} ===")
    print(f"  IDF root : {idf_root}")
    print(f"  Manifest : {manifest}")

    manifest_rows = []
    idx = 0

    for cell in CELLS:
        arch_name = cell["archetype"]
        city_name = cell["city"]
        dtype     = cell["dtype"]
        region    = cell["region"]
        cell_label = f"{arch_name}__{city_name}"

        idf_arch, epw_path = _resolve_idf_epw(arch_name, city_name)
        if not idf_arch:
            print(f"  ERROR: cannot resolve IDF for {arch_name} (STEP8_BUILDINGS_DIR={STEP8_BUILDINGS_DIR})")
            sys.exit(2)
        if not epw_path:
            print(f"  ERROR: cannot resolve EPW for {city_name} (WEATHER_DIR={WEATHER_DIR})")
            sys.exit(2)

        print(f"\n  Cell: {cell_label}")
        print(f"    IDF arch: {os.path.basename(idf_arch)}")
        print(f"    EPW:      {os.path.basename(epw_path)}")

        # Load schedule CSVs for all treatment×year combos (once per CSV path)
        loaded = {}
        for treatment in TREATMENTS:
            for year in YEARS:
                csv_path = _sched_csv(year, treatment)
                if csv_path not in loaded:
                    if not os.path.exists(csv_path):
                        print(f"  ERROR: missing {csv_path}")
                        sys.exit(2)
                    print(f"    Loading {treatment}/{year}: {os.path.basename(csv_path)}")
                    loaded[csv_path] = integration.load_schedules(
                        csv_path, dwelling_type=dtype, region=region
                    )

        # Deterministic per-cell sample (same as run_step8_paired_mc)
        rng  = random.Random(_cell_seed(args.seed, cell_label))
        # Intersect all treatment×year pools so sampled HH IDs exist in every CSV.
        _all_keys = [set(loaded[_sched_csv(yr, trt)].keys()) for yr in YEARS for trt in TREATMENTS]
        pool = sorted(set.intersection(*_all_keys))
        if not pool:
            print(f"  ERROR: empty candidate pool for {cell_label}")
            sys.exit(2)
        if len(pool) >= args.n:
            sampled = rng.sample(pool, args.n)
        else:
            sampled = [rng.choice(pool) for _ in range(args.n)]
            print(f"  WARN: pool ({len(pool)}) < n={args.n}; sampling with replacement.")
        print(f"    Pool: {len(pool)}, sampled: {len(sampled)}")

        # Generate IDFs
        for s_idx, hh_id in enumerate(sampled, 1):
            sample_tag = f"sample_{s_idx:03d}_HH{hh_id}"
            for treatment in TREATMENTS:
                for year in YEARS:
                    csv_path = _sched_csv(year, treatment)
                    sched    = loaded[csv_path]
                    if hh_id not in sched:
                        print(f"  WARN: HH {hh_id} absent in {treatment}/{year} CSV — skipping")
                        continue
                    out_dir = os.path.join(idf_root, cell_label, treatment, sample_tag, year)
                    os.makedirs(out_dir, exist_ok=True)
                    idf_out = os.path.join(out_dir, f"Scenario_{year}.idf")
                    try:
                        integration.inject_schedules(
                            idf_arch, idf_out, hh_id, sched[hh_id],
                            epw_path=epw_path,
                            sim_results_dir=out_dir,
                            batch_name=f"{cell_label}_{treatment}",
                            run_period_mode="standard",
                            output_frequency="Hourly",
                        )
                        manifest_rows.append({
                            "idx":       idx,
                            "cell":      cell_label,
                            "treatment": treatment,
                            "hh_id":     hh_id,
                            "year":      year,
                            "idf_path":  idf_out,
                            "epw_path":  epw_path,
                        })
                        idx += 1
                    except Exception as e:
                        print(f"  [inject FAIL] {cell_label}/{treatment}/{sample_tag}/{year}: {e}")

    # Write manifest
    fields = ["idx", "cell", "treatment", "hh_id", "year", "idf_path", "epw_path"]
    with open(manifest, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(manifest_rows)

    print(f"\n=== IDF generation COMPLETE ===")
    print(f"  Total IDFs: {idx}")
    print(f"  Manifest:   {manifest}")
    if idx != len(CELLS) * args.n * len(YEARS) * len(TREATMENTS):
        expected = len(CELLS) * args.n * len(YEARS) * len(TREATMENTS)
        print(f"  WARN: expected {expected} IDFs, got {idx} — check log for skipped.")
    else:
        print(f"  Count check: OK ({idx} = {len(CELLS)} cells × {args.n} HH × {len(YEARS)} yr × {len(TREATMENTS)} treatments)")


if __name__ == "__main__":
    main()
