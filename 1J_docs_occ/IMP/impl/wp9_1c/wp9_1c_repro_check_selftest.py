# =============================================================================
# wp9_1c_repro_check_selftest.py
# Tiny, LOCAL, synthetic self-test for wp9_1c_repro_check.py (T6). Builds four
# small CSV pairs in a temp directory and calls run_check() directly (no
# subprocess) against each, in "seen failing first" order (memory rule: run
# the failing/edge cases before the first passing case):
#   1. missing file            -> NOT_EVALUABLE
#   2. WD/WE labels swapped on half the households -> FAIL
#   3. one row dropped         -> FAIL (via R1)
#   4. identical files         -> EXACT   (passing case, run LAST)
#
# Run: py wp9_1c_repro_check_selftest.py
# =============================================================================

import os
import shutil
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp9_1c_repro_check as chk

# 4 households x 2 Day_Type x 3 hours (0,1,2) = 24 rows.
HOUSEHOLDS = ["HH1", "HH2", "HH3", "HH4"]
HOURS = [0, 1, 2]


def _make_reference_df():
    rows = []
    for hh in HOUSEHOLDS:
        for day_type, occ in (("Weekday", 0.80), ("Weekend", 0.30)):
            for hour in HOURS:
                rows.append({
                    "SIM_HH_ID": hh,
                    "Day_Type": day_type,
                    "Hour": hour,
                    "HHSIZE": 3,
                    "DTYPE": "SingleD",
                    "BEDRM": 3,
                    "CONDO": 0,
                    "ROOM": 6,
                    "REPAIR": 1,
                    "PR": "Ontario",
                    "Occupancy_Schedule": round(occ, 3),
                    "Metabolic_Rate": 100.0,
                })
    return pd.DataFrame(rows)


def _write(df, path):
    df.to_csv(path, index=False)


def main():
    tmp_dir = tempfile.mkdtemp(prefix="wp9_1c_repro_selftest_")
    try:
        ref_path = os.path.join(tmp_dir, "reference.csv")
        df_ref = _make_reference_df()
        _write(df_ref, ref_path)

        print("=== 1. SEEN FAILING FIRST: missing candidate file -> NOT_EVALUABLE ===")
        missing_path = os.path.join(tmp_dir, "does_not_exist.csv")
        verdict = chk.run_check(missing_path, ref_path)
        assert verdict == "NOT_EVALUABLE", f"expected NOT_EVALUABLE, got {verdict}"
        print(f"RESULT: {verdict} PASS\n")

        print("=== 2. Weekday/Weekend labels swapped on half the households -> FAIL ===")
        df_swap = df_ref.copy()
        swapped_hh = set(HOUSEHOLDS[: len(HOUSEHOLDS) // 2])  # HH1, HH2
        mask = df_swap["SIM_HH_ID"].isin(swapped_hh)
        swap_map = {"Weekday": "Weekend", "Weekend": "Weekday"}
        df_swap.loc[mask, "Day_Type"] = df_swap.loc[mask, "Day_Type"].map(swap_map)
        swap_path = os.path.join(tmp_dir, "swapped.csv")
        _write(df_swap, swap_path)
        verdict = chk.run_check(swap_path, ref_path)
        assert verdict == "FAIL", f"expected FAIL, got {verdict}"
        print(f"RESULT: {verdict} PASS\n")

        print("=== 3. One row dropped -> FAIL (R1) ===")
        df_dropped = df_ref.iloc[1:].copy()  # drop the first row
        dropped_path = os.path.join(tmp_dir, "dropped.csv")
        _write(df_dropped, dropped_path)
        verdict = chk.run_check(dropped_path, ref_path)
        assert verdict == "FAIL", f"expected FAIL, got {verdict}"
        print(f"RESULT: {verdict} PASS\n")

        print("=== 4. Identical files -> EXACT (passing case, run last) ===")
        identical_path = os.path.join(tmp_dir, "identical.csv")
        _write(df_ref.copy(), identical_path)
        verdict = chk.run_check(identical_path, ref_path)
        assert verdict == "EXACT", f"expected EXACT, got {verdict}"
        print(f"RESULT: {verdict} PASS\n")

        print("ALL FOUR REPRO-CHECK SELFTEST OUTCOMES PASSED")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
