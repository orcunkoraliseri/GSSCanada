#!/usr/bin/env python
"""
t20_hhid_check.py -- T20 N2 household-ID literal set-equality check.

Closes the one unmeasured part of acceptance N2: the SIM_HH_ID sets of two
final 17-column BEM_Schedules_*.csv files (the files EnergyPlus reads) must
be exactly equal. Reads ONLY the SIM_HH_ID column, chunked, so multi-hundred
MB files never load in full.

Usage:
    python t20_hhid_check.py \
        --pair main_vs_2022f <2030_main_BEM_Schedules.csv> <2022_BEM_Schedules.csv> \
        --pair null_vs_2022f <2030_null_BEM_Schedules.csv> <2022_BEM_Schedules.csv> \
        [--expected-count 144465] [--chunksize 5000000]

Prints, per file (each file read once, cached across pairs that reuse it):
    [N2_HHID_ROWS] <file> rows=<n>
    rows-per-household: min=<a> max=<b> n_households=<c>

Prints, per pair:
    n_unique_a=<n> n_unique_b=<n> only_in_a=<n> only_in_b=<n>
    [N2_HHID] <label> PASS   -- both diffs are 0 AND both sets have
                                 --expected-count unique IDs
    [N2_HHID] <label> FAIL   -- plus the first 10 differing IDs

Exit code: 0 if every pair PASSes, 1 if any pair FAILs.
"""
import argparse
import sys

import pandas as pd


def read_hh_id_counts(path, chunksize):
    """Read only SIM_HH_ID (chunked) -> (total_row_count, {hh_id: n_rows})."""
    counts = {}
    total_rows = 0
    for chunk in pd.read_csv(path, usecols=["SIM_HH_ID"], chunksize=chunksize):
        total_rows += len(chunk)
        vc = chunk["SIM_HH_ID"].value_counts()
        for hh_id, n in vc.items():
            counts[hh_id] = counts.get(hh_id, 0) + int(n)
    return total_rows, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pair", nargs=3, action="append", required=True,
                     metavar=("LABEL", "FILE_A", "FILE_B"),
                     help="label fileA fileB; compares SIM_HH_ID sets of fileA vs fileB")
    ap.add_argument("--expected-count", type=int, default=144465,
                     help="expected unique SIM_HH_ID count per file (default 144465)")
    ap.add_argument("--chunksize", type=int, default=5_000_000)
    args = ap.parse_args()

    cache = {}

    def get(path):
        if path not in cache:
            rows, counts = read_hh_id_counts(path, args.chunksize)
            cache[path] = (rows, counts)
            print(f"[N2_HHID_ROWS] {path} rows={rows}")
            if counts:
                per_hh = list(counts.values())
                print(f"  rows-per-household: min={min(per_hh)} max={max(per_hh)} "
                      f"n_households={len(counts)}")
            else:
                print("  rows-per-household: n_households=0 (empty SIM_HH_ID column)")
        return cache[path]

    any_fail = False
    for label, file_a, file_b in args.pair:
        _, counts_a = get(file_a)
        _, counts_b = get(file_b)
        ids_a = set(counts_a.keys())
        ids_b = set(counts_b.keys())
        only_in_a = ids_a - ids_b
        only_in_b = ids_b - ids_a
        n_unique_a = len(ids_a)
        n_unique_b = len(ids_b)

        print(f"--- pair {label} ---")
        print(f"  file_a={file_a}")
        print(f"  file_b={file_b}")
        print(f"  n_unique_a={n_unique_a}")
        print(f"  n_unique_b={n_unique_b}")
        print(f"  only_in_a={len(only_in_a)}")
        print(f"  only_in_b={len(only_in_b)}")

        ok = (len(only_in_a) == 0 and len(only_in_b) == 0
              and n_unique_a == args.expected_count
              and n_unique_b == args.expected_count)

        if ok:
            print(f"[N2_HHID] {label} PASS")
        else:
            any_fail = True
            diffs = sorted(only_in_a | only_in_b, key=str)[:10]
            print(f"  first_10_differing_ids={diffs}")
            print(f"[N2_HHID] {label} FAIL")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
