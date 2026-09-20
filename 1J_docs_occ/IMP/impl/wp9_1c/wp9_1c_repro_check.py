# =============================================================================
# wp9_1c_repro_check.py
# WP9 Stage 1c (T6) reproduction gate. Compares a candidate BEM_Schedules_2025
# file (e.g. BEM_Schedules_2025_original.csv, produced by
# wp9_1c_2025_rebuild.py --convert original) against the reference April file
# (BEM_Schedules_2025_APRIL.csv, md5 3e34561bb96f2cdd0107ea5bdef1432e, 1,146,337
# lines incl. header). Bands are fixed HERE, before any real run (task doc T6):
#
#   R1 rows      -- the set of (SIM_HH_ID, Day_Type, Hour) is identical in both
#                    files and row counts are equal (April = 1,146,336 data
#                    rows). PASS/FAIL; a FAIL here stops the check (R2/R3 are
#                    not meaningful without a matching row set) and the overall
#                    verdict is FAIL.
#   R2 values    -- on joined rows, max |diff| of Occupancy_Schedule and of
#                    Metabolic_Rate. EXACT if both <= 0.0005 (April is written
#                    to 3 decimals, float_format='%.3f', run_step3.py:131).
#                    Otherwise report the share of rows that differ and the 48
#                    per-(Day_Type, Hour) mean differences of Occupancy_
#                    Schedule; STATISTICAL if all 48 hourly means are within
#                    0.01; else FAIL.
#   R3 building  -- HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR: count
#                    mismatches per column on joined rows. Any mismatch -> FAIL
#                    (DTYPE is the likely offender if the two Random Forests --
#                    both random_state=42 -- ever disagree).
#
# Prints exactly one line: `REPRO VERDICT: EXACT | STATISTICAL | FAIL |
# NOT_EVALUABLE`. NOT_EVALUABLE if a file is missing, unreadable, or missing an
# expected column -- a crash must NEVER print FAIL. The process always exits 0;
# the verdict LINE is the result, never the exit code (memory rule 58: a
# crashed check that still prints a verdict is indistinguishable from one that
# ran cleanly unless the crash path is forced to a distinct, honest verdict).
#
# Usage: python wp9_1c_repro_check.py <candidate.csv> <reference_april.csv>
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-19_WP9_stage1c_2025.md (T6, T8 step 3)
# =============================================================================

from __future__ import annotations

import sys
import traceback

import numpy as np
import pandas as pd

KEY_COLS = ["SIM_HH_ID", "Day_Type", "Hour"]
BUILDING_COLS = ["HHSIZE", "DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR"]
VALUE_COLS = ["Occupancy_Schedule", "Metabolic_Rate"]
EXACT_TOL = 0.0005
STAT_TOL = 0.01
EXPECTED_HOURLY_CELLS = 48  # 2 Day_Type x 24 Hour


def _read(path, label):
    try:
        df = pd.read_csv(path, low_memory=False)
    except FileNotFoundError:
        print(f"{label}: file not found: {path}")
        return None
    except Exception as e:  # noqa: BLE001 -- deliberate: any read failure -> NOT_EVALUABLE
        print(f"{label}: could not be read ({type(e).__name__}: {e})")
        return None

    missing = [c for c in KEY_COLS + BUILDING_COLS + VALUE_COLS if c not in df.columns]
    if missing:
        print(f"{label}: missing expected column(s) {missing}")
        return None
    return df


def _cols_equal(a: pd.Series, b: pd.Series) -> pd.Series:
    """
    True where the two building-column values agree. Numeric columns are
    compared numerically (tolerant of int64-vs-float64 read differences);
    label columns (e.g. PR/DTYPE after the converter's dtype_map/pr_map string
    remap) are compared as trimmed strings.
    """
    a_num = pd.to_numeric(a, errors="coerce")
    b_num = pd.to_numeric(b, errors="coerce")
    both_numeric = a_num.notna().all() and b_num.notna().all()
    if both_numeric:
        return (a_num - b_num).abs() < 1e-9
    return a.astype(str).str.strip() == b.astype(str).str.strip()


def run_check(candidate_path: str, reference_path: str) -> str:
    df_c = _read(candidate_path, "candidate")
    df_r = _read(reference_path, "reference")
    if df_c is None or df_r is None:
        print("REPRO VERDICT: NOT_EVALUABLE")
        return "NOT_EVALUABLE"

    # --- R1: rows ---
    keys_c = set(map(tuple, df_c[KEY_COLS].itertuples(index=False, name=None)))
    keys_r = set(map(tuple, df_r[KEY_COLS].itertuples(index=False, name=None)))
    row_count_equal = len(df_c) == len(df_r)
    keys_equal = keys_c == keys_r
    r1_pass = row_count_equal and keys_equal
    print(
        f"R1 rows: candidate={len(df_c):,} rows, reference={len(df_r):,} rows, "
        f"row_count_equal={row_count_equal}, key_sets_equal={keys_equal} -> "
        f"{'PASS' if r1_pass else 'FAIL'}"
    )
    if not r1_pass:
        only_c = keys_c - keys_r
        only_r = keys_r - keys_c
        print(f"    keys only in candidate: {len(only_c):,}; keys only in reference: {len(only_r):,}")
        print("REPRO VERDICT: FAIL")
        return "FAIL"

    # --- join on keys (R1 passed: key sets are identical, so an inner join
    # keeps every row unless a key is duplicated within one of the files) ---
    merged = df_c.merge(df_r, on=KEY_COLS, suffixes=("_c", "_r"), how="inner")
    if len(merged) != len(df_r):
        print(
            f"    WARNING: join produced {len(merged):,} rows, expected {len(df_r):,} "
            f"(duplicate keys within a file?)"
        )

    # --- R2: values ---
    r2_exact = True
    r2_stat = True
    hourly_means = None
    for col in VALUE_COLS:
        diff = (merged[f"{col}_c"] - merged[f"{col}_r"]).abs()
        diff_scored = diff.fillna(np.inf)  # a NaN never silently counts as "equal"
        max_diff = diff_scored.max()
        share_diff = (diff_scored > EXACT_TOL).mean()
        nan_count = diff.isna().sum()
        print(
            f"R2 {col}: max|diff|={max_diff:.6f}, share of rows > {EXACT_TOL} = "
            f"{share_diff:.4%}, NaN diffs = {nan_count:,}"
        )
        if not (max_diff <= EXACT_TOL):
            r2_exact = False

    if not r2_exact:
        col = "Occupancy_Schedule"
        merged["_diff"] = (merged[f"{col}_c"] - merged[f"{col}_r"])
        hourly_means = merged.groupby(["Day_Type", "Hour"])["_diff"].mean()
        print(f"    {len(hourly_means)} per-(Day_Type,Hour) mean diffs of {col}:")
        for (day_type, hour), mean_diff in hourly_means.items():
            print(f"      {day_type} {int(hour):02d}:00 mean diff = {mean_diff:+.6f}")
        cells_ok = len(hourly_means) == EXPECTED_HOURLY_CELLS
        if not cells_ok:
            print(
                f"    WARNING: expected {EXPECTED_HOURLY_CELLS} (Day_Type,Hour) cells, "
                f"got {len(hourly_means)}"
            )
        r2_stat = cells_ok and bool((hourly_means.abs() <= STAT_TOL).all())

    # --- R3: building columns ---
    r3_pass = True
    for col in BUILDING_COLS:
        equal_mask = _cols_equal(merged[f"{col}_c"], merged[f"{col}_r"])
        mismatch = int((~equal_mask).sum())
        print(f"R3 {col}: mismatches = {mismatch:,}")
        if mismatch > 0:
            r3_pass = False

    if not r3_pass:
        print("REPRO VERDICT: FAIL")
        return "FAIL"

    if r2_exact:
        print("REPRO VERDICT: EXACT")
        return "EXACT"
    if r2_stat:
        print("REPRO VERDICT: STATISTICAL")
        return "STATISTICAL"
    print("REPRO VERDICT: FAIL")
    return "FAIL"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: wp9_1c_repro_check.py <candidate.csv> <reference_april.csv>")
        print("REPRO VERDICT: NOT_EVALUABLE")
        return 0

    candidate_path, reference_path = sys.argv[1], sys.argv[2]
    try:
        run_check(candidate_path, reference_path)
    except Exception:  # noqa: BLE001 -- deliberate: a crash must print NOT_EVALUABLE, never FAIL
        print("EXCEPTION during reproduction check (verdict forced to NOT_EVALUABLE, never FAIL):")
        traceback.print_exc()
        print("REPRO VERDICT: NOT_EVALUABLE")
    return 0  # always exit 0; the verdict line is the result


if __name__ == "__main__":
    sys.exit(main())
