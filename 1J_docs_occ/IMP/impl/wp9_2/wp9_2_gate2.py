"""
WP9 Stage 2 -- Gate 2: check the draw manifest before any EnergyPlus run.

Task doc: 1J_docs_occ/IMP/impl/2026-09-19_WP9_stage2_draw_manifest.md ("Gate 2" section).

Each check (G2.0..G2.5) prints exactly one line:
    G2.x: PASS | FAIL | NOT_EVALUABLE -- <numbers>
A check that cannot run (missing input) or crashes prints NOT_EVALUABLE, never FAIL.
Last line: GATE2 SUMMARY: G2.0=.. G2.1=.. G2.2=.. G2.3=.. G2.4=.. G2.5=..

The script's own exit code is 0 whenever it ran to the end -- the verdict is ALWAYS
in the printed lines above, never in the exit code.

This script reads only files: the raw grid CSVs (G2.0), the draw manifest and its
pool_summary.csv, and the neighbourhood IDFs (via the staged eSim_bem_utils package,
import only, for an INDEPENDENT recount of building dtypes -- it does not trust
manifest_inputs.txt's own claims). It imports the eligibility helpers from
wp9_2_manifest.py (same directory) rather than re-deriving that arithmetic a second
time, to avoid two copies of the same formula silently drifting apart.
"""

import argparse
import csv
import hashlib
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp9_2_manifest as wm  # noqa: E402


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


def read_csv_rows(path):
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------- G2.0

def check_g2_0(grid_files):
    """grid_files: list of (label, path). Household with >1 distinct HHSIZE/DTYPE/PR."""
    if not grid_files:
        return "NOT_EVALUABLE", "no grid files given"

    per_file_counts = []
    total_bad = 0
    for label, path in grid_files:
        seen = {}
        for row in read_csv_rows(path):
            hh_id = row.get("SIM_HH_ID", "")
            key = (row.get("HHSIZE", ""), row.get("DTYPE", ""), row.get("PR", ""))
            seen.setdefault(hh_id, set()).add(key)
        bad = sum(1 for hh_id, keys in seen.items() if len(keys) > 1)
        per_file_counts.append(f"{label}={bad}")
        total_bad += bad

    verdict = "PASS" if total_bad == 0 else "FAIL"
    detail = f"total_multi_label_households={total_bad} per_file=[{', '.join(per_file_counts)}]"
    return verdict, detail


# ------------------------------------------------------------------- shared helpers

def recompute_neighbourhood_eligibility(idf_paths_by_nu, pool_summary_rows, years, code_dir):
    """
    Independent recount: re-derive, from the IDFs and pool_summary.csv alone
    (never from the manifest), which neighbourhoods are eligible and their
    building dtype lists / counts. Returns:
        eligible_nus: dict nu -> {'building_dtypes': [...], 'n_buildings': int}
        excluded_nus: dict nu -> reason string
    """
    wm.add_code_path(code_dir)
    import eSim_bem_utils.neighbourhood as neighbourhood

    counts_by_key = wm.pool_counts_by_key(pool_summary_rows)
    sizes_present_by_dtype = {}
    for r in pool_summary_rows:
        sizes_present_by_dtype.setdefault(r["dtype"], set()).add(r["hhsize"])

    eligible_nus = {}
    excluded_nus = {}
    for nu, idf_path in idf_paths_by_nu.items():
        building_dtypes = wm.get_buildings_for_neighbourhood(neighbourhood, idf_path)
        b_count = Counter(building_dtypes)
        ok = True
        for d, need in b_count.items():
            sizes_present = sizes_present_by_dtype.get(d, set())
            elig = wm.eligible_sizes_for(d, sizes_present, counts_by_key, years, need)
            if not elig:
                excluded_nus[nu] = f"no eligible size for dtype {d}"
                ok = False
                break
        if ok:
            eligible_nus[nu] = {
                "building_dtypes": building_dtypes,
                "n_buildings": len(building_dtypes),
            }
    return eligible_nus, excluded_nus


# --------------------------------------------------------------------------- G2.1

def check_g2_1(manifest_rows, idf_paths_by_nu, pool_summary_rows, years, expected_draws, code_dir):
    if manifest_rows is None:
        return "NOT_EVALUABLE", "manifest not provided"
    if pool_summary_rows is None:
        return "NOT_EVALUABLE", "pool_summary not provided"
    if not idf_paths_by_nu:
        return "NOT_EVALUABLE", "no IDFs provided"

    eligible_nus, excluded_nus = recompute_neighbourhood_eligibility(
        idf_paths_by_nu, pool_summary_rows, years, code_dir
    )

    expected_total = sum(
        expected_draws * len(years) * info["n_buildings"] for info in eligible_nus.values()
    )
    actual_total = len(manifest_rows)

    nus_in_manifest = {r["neighbourhood"] for r in manifest_rows}
    nus_expected = set(eligible_nus.keys())
    nu_set_mismatch = nus_in_manifest != nus_expected

    dtype_mismatches = 0
    hhsize_mismatches = 0
    for r in manifest_rows:
        if str(r["hh_dtype"]) != str(r["building_dtype"]):
            dtype_mismatches += 1
        if str(r["hh_hhsize"]) != str(r["stratum_hhsize"]):
            hhsize_mismatches += 1

    verdict = "PASS"
    if actual_total != expected_total:
        verdict = "FAIL"
    if dtype_mismatches or hhsize_mismatches:
        verdict = "FAIL"
    if excluded_nus:
        verdict = "FAIL"
    if nu_set_mismatch:
        verdict = "FAIL"

    detail = (
        f"expected_rows={expected_total} actual_rows={actual_total} "
        f"dtype_mismatches={dtype_mismatches} hhsize_mismatches={hhsize_mismatches} "
        f"excluded_neighbourhoods={len(excluded_nus)} ({excluded_nus}) "
        f"neighbourhood_set_mismatch={nu_set_mismatch}"
    )
    return verdict, detail


# --------------------------------------------------------------------------- G2.2

def check_g2_2(manifest_rows):
    if manifest_rows is None:
        return "NOT_EVALUABLE", "manifest not provided"

    groups = defaultdict(list)
    for r in manifest_rows:
        key = (r["neighbourhood"], r["draw"], r["year"])
        groups[key].append(r["hh_id"])

    dup_instances = 0
    dup_groups = 0
    for key, hh_ids in groups.items():
        c = Counter(hh_ids)
        extra = sum(v - 1 for v in c.values() if v > 1)
        if extra:
            dup_instances += extra
            dup_groups += 1

    verdict = "PASS" if dup_instances == 0 else "FAIL"
    detail = f"duplicate_instances={dup_instances} groups_affected={dup_groups} groups_checked={len(groups)}"
    return verdict, detail


# --------------------------------------------------------------------------- G2.3

def check_g2_3(manifest_rows, expected_draws):
    if manifest_rows is None:
        return "NOT_EVALUABLE", "manifest not provided"

    by_nu_draw_set = defaultdict(set)
    by_nu_draw_stratum = defaultdict(set)
    for r in manifest_rows:
        by_nu_draw_set[(r["neighbourhood"], r["draw"])].add((r["year"], r["hh_id"]))
        by_nu_draw_stratum[(r["neighbourhood"], r["draw"])].add((r["building_index"], r["stratum_hhsize"]))

    nus = sorted({nu for nu, _ in by_nu_draw_set})
    per_nu_lines = []
    all_pass = True
    for nu in nus:
        draws_for_nu = [k for (n, k) in by_nu_draw_set if n == nu]
        sigs = set()
        for draw in draws_for_nu:
            sigs.add(frozenset(by_nu_draw_set[(nu, draw)]))
        strata_sigs = set()
        for draw in draws_for_nu:
            strata_sigs.add(frozenset(by_nu_draw_stratum[(nu, draw)]))
        distinct_sets = len(sigs)
        distinct_strata = len(strata_sigs)
        n_draws_present = len(draws_for_nu)
        ok = (distinct_sets == expected_draws) and (n_draws_present == expected_draws)
        all_pass = all_pass and ok
        per_nu_lines.append(
            f"{nu}: draws={n_draws_present} distinct_household_sets={distinct_sets} "
            f"distinct_stratum_profiles={distinct_strata}"
        )

    if not nus:
        return "NOT_EVALUABLE", "no neighbourhoods in manifest"

    verdict = "PASS" if all_pass else "FAIL"
    detail = "; ".join(per_nu_lines)
    return verdict, detail


# --------------------------------------------------------------------------- G2.4

def check_g2_4(manifest_rows, pool_summary_rows, years):
    if manifest_rows is None:
        return "NOT_EVALUABLE", "manifest not provided"
    if pool_summary_rows is None:
        return "NOT_EVALUABLE", "pool_summary not provided"

    stats_by_key = {}
    for r in pool_summary_rows:
        key = (str(r["year"]), str(r["dtype"]), str(r["hhsize"]))
        mean_v = float(r["mean_weekday_hours"])
        sd_v = float(r["sd_weekday_hours"])
        stats_by_key[key] = (mean_v, sd_v * sd_v)

    rows_by_year = defaultdict(list)
    for r in manifest_rows:
        rows_by_year[str(r["year"])].append(r)

    per_year_lines = []
    all_pass = True
    years_checked = 0
    for year in years:
        rows = rows_by_year.get(str(year), [])
        if not rows:
            continue
        years_checked += 1
        n = len(rows)
        M = sum(float(r["weekday_hours"]) for r in rows) / n
        e_sum = 0.0
        var_sum = 0.0
        missing_stats = 0
        for r in rows:
            key = (str(year), str(r["building_dtype"]), str(r["stratum_hhsize"]))
            stat = stats_by_key.get(key)
            if stat is None:
                missing_stats += 1
                continue
            e_sum += stat[0]
            var_sum += stat[1]
        E = e_sum / n if n else 0.0
        SE = math.sqrt(var_sum) / n if n else 0.0
        if SE == 0.0:
            z = 0.0 if abs(M - E) < 1e-9 else float("inf")
        else:
            z = (M - E) / SE
        ok = abs(z) <= 3
        all_pass = all_pass and ok
        per_year_lines.append(
            f"{year}: n={n} M={M:.4f} E={E:.4f} SE={SE:.6f} z={z:.4f} missing_stats={missing_stats}"
        )

    if years_checked == 0:
        return "NOT_EVALUABLE", "no years present in manifest"

    verdict = "PASS" if all_pass else "FAIL"
    detail = "; ".join(per_year_lines)
    return verdict, detail


# --------------------------------------------------------------------------- G2.5

def _row_key_tuple(r, fields):
    return tuple(str(r.get(f, "")) for f in fields)


def check_g2_5(manifest_path, repeat_manifest_path, draws10_manifest_path, draws10_count):
    if not repeat_manifest_path or not draws10_manifest_path:
        return "NOT_EVALUABLE", "repeat/draws10 manifest not provided"
    if not (os.path.isfile(manifest_path) and os.path.isfile(repeat_manifest_path)
            and os.path.isfile(draws10_manifest_path)):
        return "NOT_EVALUABLE", "one of the three manifest files is missing"

    md5_main = md5_of_file(manifest_path)
    md5_repeat = md5_of_file(repeat_manifest_path)
    full_build_match = (md5_main == md5_repeat)

    main_rows = read_csv_rows(manifest_path)
    draws10_rows = read_csv_rows(draws10_manifest_path)

    fields = wm.MANIFEST_FIELDS
    main_first10 = [
        _row_key_tuple(r, fields) for r in main_rows if int(r["draw"]) <= draws10_count
    ]
    draws10_all = [_row_key_tuple(r, fields) for r in draws10_rows]

    row_for_row_match = (main_first10 == draws10_all)

    verdict = "PASS" if (full_build_match and row_for_row_match) else "FAIL"
    detail = (
        f"full_build_md5_match={full_build_match} (main={md5_main} repeat={md5_repeat}) "
        f"draws10_row_for_row_match={row_for_row_match} "
        f"main_first{draws10_count}_rows={len(main_first10)} draws10_rows={len(draws10_all)}"
    )
    return verdict, detail


# --------------------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(description="WP9 Stage 2 Gate 2")
    p.add_argument("--code-dir", default=None,
                    help="Directory directly containing eSim_bem_utils (needed for G2.1)")
    p.add_argument("--grid-file", action="append", default=[], metavar="LABEL=PATH",
                    help="Repeatable: a grid CSV to check under G2.0, as LABEL=PATH")
    p.add_argument("--manifest", default=None, help="draw_manifest.csv to gate")
    p.add_argument("--pool-summary", default=None, help="pool_summary.csv for this manifest")
    p.add_argument("--idf-dir", default=None, help="Directory containing NUS_RC{1..6}.idf")
    p.add_argument("--neighbourhoods", default="NUS_RC1,NUS_RC2,NUS_RC3,NUS_RC4,NUS_RC5,NUS_RC6")
    p.add_argument("--years", default=",".join(wm.YEARS_DEFAULT))
    p.add_argument("--expected-draws", type=int, default=30)
    p.add_argument("--repeat-manifest", default=None, help="second full build, for G2.5")
    p.add_argument("--draws10-manifest", default=None, help="--draws 10 build, for G2.5")
    p.add_argument("--draws10-count", type=int, default=10)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    grid_files = []
    for item in args.grid_file:
        if "=" not in item:
            eprint(f"FATAL: --grid-file must be LABEL=PATH, got: {item}")
            return 2
        label, path = item.split("=", 1)
        grid_files.append((label, path))

    manifest_rows = None
    if args.manifest:
        if os.path.isfile(args.manifest):
            manifest_rows = read_csv_rows(args.manifest)
        else:
            eprint(f"WARNING: --manifest given but not found: {args.manifest}")

    pool_summary_rows = None
    if args.pool_summary:
        if os.path.isfile(args.pool_summary):
            pool_summary_rows = read_csv_rows(args.pool_summary)
        else:
            eprint(f"WARNING: --pool-summary given but not found: {args.pool_summary}")

    idf_paths_by_nu = {}
    if args.idf_dir:
        for nu in [x.strip() for x in args.neighbourhoods.split(",") if x.strip()]:
            idf_path = os.path.join(args.idf_dir, f"{nu}.idf")
            if os.path.isfile(idf_path):
                idf_paths_by_nu[nu] = idf_path
            else:
                eprint(f"WARNING: IDF not found for {nu}: {idf_path}")

    years = [y.strip() for y in args.years.split(",") if y.strip()]

    verdicts = {}

    v, d = check_g2_0(grid_files)
    eprint(f"G2.0: {v} -- {d}")
    verdicts["G2.0"] = v

    try:
        v, d = check_g2_1(manifest_rows, idf_paths_by_nu, pool_summary_rows, years,
                           args.expected_draws, args.code_dir)
    except Exception as e:
        v, d = "NOT_EVALUABLE", f"crashed: {e!r}"
    eprint(f"G2.1: {v} -- {d}")
    verdicts["G2.1"] = v

    try:
        v, d = check_g2_2(manifest_rows)
    except Exception as e:
        v, d = "NOT_EVALUABLE", f"crashed: {e!r}"
    eprint(f"G2.2: {v} -- {d}")
    verdicts["G2.2"] = v

    try:
        v, d = check_g2_3(manifest_rows, args.expected_draws)
    except Exception as e:
        v, d = "NOT_EVALUABLE", f"crashed: {e!r}"
    eprint(f"G2.3: {v} -- {d}")
    verdicts["G2.3"] = v

    try:
        v, d = check_g2_4(manifest_rows, pool_summary_rows, years)
    except Exception as e:
        v, d = "NOT_EVALUABLE", f"crashed: {e!r}"
    eprint(f"G2.4: {v} -- {d}")
    verdicts["G2.4"] = v

    try:
        v, d = check_g2_5(args.manifest, args.repeat_manifest, args.draws10_manifest,
                           args.draws10_count)
    except Exception as e:
        v, d = "NOT_EVALUABLE", f"crashed: {e!r}"
    eprint(f"G2.5: {v} -- {d}")
    verdicts["G2.5"] = v

    summary = " ".join(f"{k}={verdicts[k]}" for k in ["G2.0", "G2.1", "G2.2", "G2.3", "G2.4", "G2.5"])
    eprint(f"GATE2 SUMMARY: {summary}")
    eprint("GATE2 SCRIPT DONE (exit 0 -- verdicts are in the lines above, not the exit code)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
