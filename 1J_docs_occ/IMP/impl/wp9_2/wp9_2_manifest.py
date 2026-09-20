"""
WP9 Stage 2: draw the manifest of simulated households, BEFORE any EnergyPlus run.

Task doc: 1J_docs_occ/IMP/impl/2026-09-19_WP9_stage2_draw_manifest.md

Ruling B (author, 2026-09-19): each draw picks a RANDOM household from the same
(dwelling type, household size) group, with a fixed seed -- replacing the April
simulation's deterministic "best working-day match" rule
(integration.find_best_match_household).

This script builds `draw_manifest.csv` (+ `pool_summary.csv` + `manifest_inputs.txt`)
for the real (random) rule, and can also build an "April rule" CONTROL manifest with
the same strata/rows but households chosen by find_best_match_household instead, for
Gate 2's seen-failing controls (G2.3 / G2.4).

Imports ONLY from the staged eSim_bem_utils package (never edits it). The caller must
point --code-dir at the directory that directly CONTAINS the eSim_bem_utils package
(e.g. on the cluster: /speed-scratch/o_iseri/1J_rerun/code ; locally in this repo:
1J_docs_occ/conference_eSim/eSim).

Exit codes: 0 = ran to completion (including NOT_EVALUABLE neighbourhoods, which are
a normal, printed outcome, not a script failure). Non-zero = a hard error (bad args,
missing required input file, import failure).
"""

import argparse
import csv
import hashlib
import os
import random
import statistics
import sys

YEARS_DEFAULT = ["2005", "2010", "2015", "2022", "2025"]
MANIFEST_FIELDS = [
    "seed", "draw", "neighbourhood", "building_index", "building_dtype",
    "stratum_hhsize", "year", "hh_id", "hh_dtype", "hh_hhsize", "hh_pr",
    "weekday_hours", "weekend_hours",
]
POOL_SUMMARY_FIELDS = [
    "year", "dtype", "hhsize", "n_households", "mean_weekday_hours", "sd_weekday_hours",
]


def eprint(*a, **kw):
    print(*a, **kw)
    sys.stdout.flush()


def md5_of_file(path, chunk_size=1024 * 1024):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def add_code_path(code_dir):
    if code_dir and code_dir not in sys.path:
        sys.path.insert(0, code_dir)


def hours_from_entries(entries):
    """Sum of the 24 hourly 'occ' values for one day type."""
    return sum(float(e["occ"]) for e in entries)


def load_year_pool(integration_mod, grid_path, year, region):
    """
    Load one year's grid file with the exact loader the simulation uses, then apply
    the two extra filters from the task doc's Design section.

    Returns:
        final_pool: dict hh_id -> {'dtype','hhsize','pr','weekday_hours','weekend_hours'}
        raw_schedules: the full dict returned by integration.load_schedules() (needed
            unfiltered so find_best_match_household() can look candidates up by id)
        counts: dict with loader_count, blank_pr_dropped, incomplete_dropped, final_pool_size
    """
    raw_schedules = integration_mod.load_schedules(grid_path, region=region)
    loader_count = len(raw_schedules)

    blank_pr_dropped = 0
    after_pr = {}
    for hh_id, data in raw_schedules.items():
        pr = (data.get("metadata", {}).get("pr", "") or "").strip()
        if not pr:
            blank_pr_dropped += 1
            continue
        after_pr[hh_id] = data

    incomplete_dropped = 0
    final_pool = {}
    for hh_id, data in after_pr.items():
        wd = data.get("Weekday", [])
        we = data.get("Weekend", [])
        if len(wd) != 24 or len(we) != 24:
            incomplete_dropped += 1
            continue
        meta = data.get("metadata", {})
        final_pool[hh_id] = {
            "dtype": meta.get("dtype", ""),
            "hhsize": meta.get("hhsize", ""),
            "pr": meta.get("pr", ""),
            "weekday_hours": hours_from_entries(wd),
            "weekend_hours": hours_from_entries(we),
        }

    final_pool_size = len(final_pool)
    counts = {
        "loader_count": loader_count,
        "blank_pr_dropped": blank_pr_dropped,
        "incomplete_dropped": incomplete_dropped,
        "final_pool_size": final_pool_size,
    }
    eprint(
        f"YEAR {year}: loader_count={loader_count} blank_pr_dropped={blank_pr_dropped} "
        f"incomplete_dropped={incomplete_dropped} final_pool_size={final_pool_size}"
    )
    return final_pool, raw_schedules, counts


def build_stratum_index(final_pool):
    """(dtype, hhsize) -> sorted (text) list of hh_id, from one year's final pool."""
    idx = {}
    for hh_id, rec in final_pool.items():
        key = (rec["dtype"], rec["hhsize"])
        idx.setdefault(key, []).append(hh_id)
    for key in idx:
        idx[key].sort()
    return idx


def build_pool_summary_rows(pools_by_year):
    """pools_by_year: year -> final_pool dict. Returns list of pool_summary.csv rows."""
    rows = []
    for year in pools_by_year:
        by_key = {}
        for rec in pools_by_year[year].values():
            key = (rec["dtype"], rec["hhsize"])
            by_key.setdefault(key, []).append(rec["weekday_hours"])
        for (dtype, hhsize), hours_list in sorted(by_key.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
            n = len(hours_list)
            mean_h = statistics.mean(hours_list) if n else 0.0
            sd_h = statistics.stdev(hours_list) if n >= 2 else 0.0
            rows.append({
                "year": year, "dtype": dtype, "hhsize": hhsize,
                "n_households": n, "mean_weekday_hours": round(mean_h, 6),
                "sd_weekday_hours": round(sd_h, 6),
            })
    rows.sort(key=lambda r: (str(r["year"]), str(r["dtype"]), str(r["hhsize"])))
    return rows


def pool_counts_by_key(pool_summary_rows):
    """(year, dtype, hhsize) -> n_households (int), from pool_summary rows (in-memory
    or freshly read back from pool_summary.csv, where every value is a string)."""
    d = {}
    for r in pool_summary_rows:
        d[(str(r["year"]), str(r["dtype"]), str(r["hhsize"]))] = int(r["n_households"])
    return d


def eligible_sizes_for(dtype, sizes_present, counts_by_key, years, min_needed):
    """Sizes s such that in EVERY year, count(year, dtype, s) >= min_needed."""
    eligible = []
    for s in sorted(sizes_present, key=lambda x: str(x)):
        ok = True
        for year in years:
            n = counts_by_key.get((str(year), str(dtype), str(s)), 0)
            if n < min_needed:
                ok = False
                break
        if ok:
            eligible.append(s)
    return eligible


def weights_for_sizes(dtype, eligible_sizes, counts_by_key, years):
    """Mean-over-years share of each eligible size among eligible-size households of dtype."""
    if not eligible_sizes:
        return []
    per_year_shares = []
    for year in years:
        totals = {s: counts_by_key.get((str(year), str(dtype), str(s)), 0) for s in eligible_sizes}
        total = sum(totals.values())
        if total <= 0:
            per_year_shares.append({s: 0.0 for s in eligible_sizes})
        else:
            per_year_shares.append({s: totals[s] / total for s in eligible_sizes})
    weights = []
    for s in eligible_sizes:
        weights.append(statistics.mean(sh[s] for sh in per_year_shares))
    return weights


def get_buildings_for_neighbourhood(neighbourhood_mod, idf_path):
    return neighbourhood_mod.get_building_dtypes_from_idf(idf_path)


def build_manifest(
    integration_mod, neighbourhood_mod,
    grid_paths_by_year, idf_paths_by_nu, region, years, n_draws,
    seed_date, household_rule,
    pool_summary_out=None,
):
    """
    Returns (manifest_rows, pool_summary_rows, not_evaluable_lines).
    household_rule: 'random' (Ruling B) or 'april' (control -- find_best_match_household).
    """
    # 1. Load pools per year.
    pools_by_year = {}
    raw_schedules_by_year = {}
    for year in years:
        pool, raw, _counts = load_year_pool(integration_mod, grid_paths_by_year[year], year, region)
        pools_by_year[year] = pool
        raw_schedules_by_year[year] = raw

    stratum_index_by_year = {year: build_stratum_index(pools_by_year[year]) for year in years}
    pool_summary_rows = build_pool_summary_rows(pools_by_year)
    counts_by_key = pool_counts_by_key(pool_summary_rows)

    # All (dtype,size) pairs ever observed, per dtype -- candidate size universe.
    sizes_present_by_dtype = {}
    for r in pool_summary_rows:
        sizes_present_by_dtype.setdefault(r["dtype"], set()).add(r["hhsize"])

    manifest_rows = []
    not_evaluable_lines = []

    for nu in sorted(idf_paths_by_nu):
        idf_path = idf_paths_by_nu[nu]
        building_dtypes = get_buildings_for_neighbourhood(neighbourhood_mod, idf_path)
        n_buildings = len(building_dtypes)

        from collections import Counter
        b_count = Counter(building_dtypes)  # B(nu, d)

        eligible_sizes_by_dtype = {}
        weights_by_dtype = {}
        skip_nu = False
        for d, need in b_count.items():
            sizes_present = sizes_present_by_dtype.get(d, set())
            elig = eligible_sizes_for(d, sizes_present, counts_by_key, years, need)
            if not elig:
                line = f"NOT_EVALUABLE: no eligible size for {nu} {d}"
                eprint(line)
                not_evaluable_lines.append(line)
                skip_nu = True
                continue
            eligible_sizes_by_dtype[d] = elig
            weights_by_dtype[d] = weights_for_sizes(d, elig, counts_by_key, years)

        if skip_nu:
            continue

        for k in range(1, n_draws + 1):
            # Stratum (building size) draw -- buildings in IDF order.
            rng_s = random.Random(f"{seed_date}|{nu}|draw{k}|stratum")
            stratum_sizes = []
            for bi in range(n_buildings):
                d = building_dtypes[bi]
                sizes = eligible_sizes_by_dtype[d]
                weights = weights_by_dtype[d]
                chosen = rng_s.choices(sizes, weights=weights, k=1)[0]
                stratum_sizes.append(chosen)

            # Household draw -- one RNG per (nu, draw, year); buildings in IDF order.
            for year in years:
                seed_str = f"{seed_date}|{nu}|draw{k}|{year}"
                rng_y = random.Random(seed_str)
                used_this_year = set()
                s_index = stratum_index_by_year[year]
                raw_sched = raw_schedules_by_year[year]
                pool = pools_by_year[year]

                for bi in range(n_buildings):
                    d = building_dtypes[bi]
                    s = stratum_sizes[bi]
                    candidates_all = s_index.get((d, s), [])
                    candidates = [h for h in candidates_all if h not in used_this_year]

                    if not candidates:
                        line = (
                            f"NOT_EVALUABLE: no candidates left for {nu} draw{k} {year} "
                            f"building {bi} dtype {d} size {s}"
                        )
                        eprint(line)
                        not_evaluable_lines.append(line)
                        continue

                    if household_rule == "random":
                        hh_id = rng_y.choice(candidates)
                    elif household_rule == "april":
                        hh_id = integration_mod.find_best_match_household(
                            raw_sched, candidates=candidates, day_type="Weekday"
                        )
                    else:
                        raise ValueError(f"Unknown household_rule: {household_rule}")

                    used_this_year.add(hh_id)
                    rec = pool[hh_id]
                    manifest_rows.append({
                        "seed": seed_str,
                        "draw": k,
                        "neighbourhood": nu,
                        "building_index": bi,
                        "building_dtype": d,
                        "stratum_hhsize": s,
                        "year": year,
                        "hh_id": hh_id,
                        "hh_dtype": rec["dtype"],
                        "hh_hhsize": rec["hhsize"],
                        "hh_pr": rec["pr"],
                        "weekday_hours": round(rec["weekday_hours"], 6),
                        "weekend_hours": round(rec["weekend_hours"], 6),
                    })

    manifest_rows.sort(key=lambda r: (
        str(r["neighbourhood"]), int(r["draw"]), str(r["year"]), int(r["building_index"])
    ))
    return manifest_rows, pool_summary_rows, not_evaluable_lines


def write_manifest_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        w.writerows(rows)


def write_pool_summary_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=POOL_SUMMARY_FIELDS)
        w.writeheader()
        w.writerows(rows)


def write_manifest_inputs_txt(path, grid_paths_by_year, code_files, idf_paths_by_nu):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for year, p in sorted(grid_paths_by_year.items()):
            f.write(f"grid {year} {md5_of_file(p)} {p}\n")
        for label, p in code_files.items():
            f.write(f"code {label} {md5_of_file(p)} {p}\n")
        for nu, p in sorted(idf_paths_by_nu.items()):
            f.write(f"idf {nu} {md5_of_file(p)} {p}\n")


def build_parser():
    p = argparse.ArgumentParser(description="WP9 Stage 2 draw manifest builder")
    p.add_argument("--code-dir", required=True,
                    help="Directory directly containing the eSim_bem_utils package")
    p.add_argument("--grid-2005", required=True)
    p.add_argument("--grid-2010", required=True)
    p.add_argument("--grid-2015", required=True)
    p.add_argument("--grid-2022", required=True)
    p.add_argument("--grid-2025", required=True)
    p.add_argument("--idf-dir", required=True,
                    help="Directory containing NUS_RC{1..6}.idf")
    p.add_argument("--neighbourhoods", default="NUS_RC1,NUS_RC2,NUS_RC3,NUS_RC4,NUS_RC5,NUS_RC6")
    p.add_argument("--region", default="Quebec")
    p.add_argument("--draws", type=int, default=30)
    p.add_argument("--seed-date", default="20260919")
    p.add_argument("--household-rule", choices=["random", "april"], default="random")
    p.add_argument("--out-manifest", required=True)
    p.add_argument("--out-pool-summary", default=None)
    p.add_argument("--out-inputs", default=None)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    add_code_path(args.code_dir)
    import eSim_bem_utils.integration as integration
    import eSim_bem_utils.neighbourhood as neighbourhood

    years = YEARS_DEFAULT
    grid_paths_by_year = {
        "2005": args.grid_2005, "2010": args.grid_2010, "2015": args.grid_2015,
        "2022": args.grid_2022, "2025": args.grid_2025,
    }
    for year, path in grid_paths_by_year.items():
        if not os.path.isfile(path):
            eprint(f"FATAL: grid file for {year} not found: {path}")
            return 2

    nu_names = [x.strip() for x in args.neighbourhoods.split(",") if x.strip()]
    idf_paths_by_nu = {}
    for nu in nu_names:
        idf_path = os.path.join(args.idf_dir, f"{nu}.idf")
        if not os.path.isfile(idf_path):
            eprint(f"FATAL: IDF not found for {nu}: {idf_path}")
            return 2
        idf_paths_by_nu[nu] = idf_path

    manifest_rows, pool_summary_rows, not_evaluable_lines = build_manifest(
        integration, neighbourhood,
        grid_paths_by_year, idf_paths_by_nu, args.region, years, args.draws,
        args.seed_date, args.household_rule,
    )

    write_manifest_csv(manifest_rows, args.out_manifest)
    eprint(f"Wrote {len(manifest_rows)} manifest rows to {args.out_manifest}")

    if args.out_pool_summary:
        write_pool_summary_csv(pool_summary_rows, args.out_pool_summary)
        eprint(f"Wrote {len(pool_summary_rows)} pool_summary rows to {args.out_pool_summary}")

    if args.out_inputs:
        code_dir = os.path.abspath(args.code_dir)
        code_files = {
            "integration.py": os.path.join(code_dir, "eSim_bem_utils", "integration.py"),
            "neighbourhood.py": os.path.join(code_dir, "eSim_bem_utils", "neighbourhood.py"),
        }
        write_manifest_inputs_txt(args.out_inputs, grid_paths_by_year, code_files, idf_paths_by_nu)
        eprint(f"Wrote manifest_inputs.txt to {args.out_inputs}")

    eprint(f"NOT_EVALUABLE neighbourhoods: {len(not_evaluable_lines)}")
    eprint("MANIFEST BUILD DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
