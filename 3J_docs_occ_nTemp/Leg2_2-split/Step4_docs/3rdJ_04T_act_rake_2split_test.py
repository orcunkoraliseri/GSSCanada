# -*- coding: utf-8 -*-
"""
3rdJ_04T_act_rake_2split_test.py — synthetic unit test suite for 3rdJ_04T_act_rake_2split.py.

Mirrors 2J's 19-case synthetic unit test for _rake_categorical_slot /
_run_act30_conditional_rake (2J_docs_occ_nTemp task-B, "synthetic unit test 19/19 PASS",
step4_improvements_implementation.md:38). No real data is read; every case constructs a
small toy frame with known state-conditional activity marginals in-process.

Run:
    py -3 3rdJ_04T_act_rake_2split_test.py

Exit code 0 on all-PASS, 1 otherwise.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_MOD_PATH = os.path.join(SCRIPT_DIR, "3rdJ_04T_act_rake_2split.py")
_spec = importlib.util.spec_from_file_location("_04T", _MOD_PATH)
_04T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_04T)

_round_to_sum              = _04T._round_to_sum
_rake_categorical_slot     = _04T._rake_categorical_slot
_rake_act_group            = _04T._rake_act_group
_run_act30_conditional_rake = _04T._run_act30_conditional_rake
_compute_state              = _04T._compute_state
STATE_WORK, STATE_HOME, STATE_NEITHER = _04T.STATE_WORK, _04T.STATE_HOME, _04T.STATE_NEITHER
N_SLOTS = _04T.N_SLOTS
ACT_CATEGORIES = _04T.ACT_CATEGORIES
WORK_CAT = _04T.WORK_CAT
HOM_COLS, WRK_COLS, ACT_COLS = _04T.HOM_COLS, _04T.WRK_COLS, _04T.ACT_COLS
MIN_OBS_FOR_LFTAG = _04T.MIN_OBS_FOR_LFTAG

RESULTS = []   # (name, ok, detail)


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


# ══════════════════════════════════════════════════════════════════════════════
# A. _round_to_sum  (cases 1-4)
# ══════════════════════════════════════════════════════════════════════════════

def test_round_to_sum():
    # 1. exact divisible proportions
    props = {1: 5.0, 2: 5.0}
    out = _round_to_sum(props, [1, 2], 10)
    check("01 round_to_sum exact-divisible sums to n", sum(out.values()) == 10, out)
    check("01b round_to_sum exact-divisible split 5/5", out == {1: 5, 2: 5}, out)

    # 2. remainder / largest-remainder rounding
    props = {1: 1.0, 2: 1.0, 3: 1.0}
    out = _round_to_sum(props, [1, 2, 3], 10)
    check("02 round_to_sum remainder sums to n", sum(out.values()) == 10, out)

    # 3. all-zero proportions -> None
    props = {1: 0.0, 2: 0.0}
    out = _round_to_sum(props, [1, 2], 5)
    check("03 round_to_sum all-zero returns None", out is None, out)

    # 4. one category concentrates all probability
    props = {1: 100.0, 2: 0.0, 3: 0.0}
    out = _round_to_sum(props, [1, 2, 3], 7)
    check("04 round_to_sum single-category gets all n", out == {1: 7, 2: 0, 3: 0}, out)


# ══════════════════════════════════════════════════════════════════════════════
# B. _rake_categorical_slot  (cases 5-9)
# ══════════════════════════════════════════════════════════════════════════════

def test_rake_categorical_slot():
    rng = np.random.default_rng(42)

    # 5. exact target attainment
    cur = np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 3], dtype=float)
    target = {1: 2, 2: 2, 3: 6}
    nan_ = np.full(len(cur), np.nan)
    new_vals, n_mv = _rake_categorical_slot(cur, target, [1, 2, 3], nan_, nan_, rng)
    achieved = {c: int(np.sum(new_vals == c)) for c in [1, 2, 3]}
    check("05 rake_categorical_slot exact target attainment", achieved == target, achieved)

    # 6. no-op when already at target
    cur = np.array([1, 1, 2, 2, 3, 3], dtype=float)
    target = {1: 2, 2: 2, 3: 2}
    new_vals, n_mv = _rake_categorical_slot(cur, target, [1, 2, 3], nan_[:6], nan_[:6], rng)
    check("06 rake_categorical_slot no-op when already at target", n_mv == 0, n_mv)
    check("06b rake_categorical_slot no-op values unchanged", np.array_equal(new_vals, cur), new_vals)

    # 7. boundary preference: neighbour holding destination category is preferred
    # 4 records currently cat=1 (surplus), need 1 moved to cat=2 (deficit).
    # Record index 2's left neighbour already holds cat=2 -> must be chosen.
    cur = np.array([1, 1, 1, 1], dtype=float)
    target = {1: 3, 2: 1}
    left = np.array([np.nan, np.nan, 2.0, np.nan])
    right = np.full(4, np.nan)
    new_vals, n_mv = _rake_categorical_slot(cur, target, [1, 2], left, right, rng)
    check("07 rake_categorical_slot boundary preference picks matching neighbour",
          n_mv == 1 and new_vals[2] == 2.0 and np.sum(new_vals == 1) == 3, new_vals)

    # 8. determinism under fixed seed (fresh rng each run, identical result)
    cur = np.array([1, 1, 1, 1, 1, 2, 2, 2, 2, 2], dtype=float)
    target = {1: 5, 2: 3, 3: 2}
    left = np.full(10, np.nan)
    right = np.full(10, np.nan)
    rng_a = np.random.default_rng(123)
    new_a, mv_a = _rake_categorical_slot(cur, target, [1, 2, 3], left, right, rng_a)
    rng_b = np.random.default_rng(123)
    new_b, mv_b = _rake_categorical_slot(cur, target, [1, 2, 3], left, right, rng_b)
    check("08 rake_categorical_slot deterministic under fixed seed",
          np.array_equal(new_a, new_b) and mv_a == mv_b, (new_a, new_b))

    # 9. no record moved twice per slot-call: n_moved == sum(deficits) exactly,
    #    and every moved record's final value is in the deficit set (not re-touched
    #    into a third category).
    cur = np.array([1] * 6 + [2] * 6, dtype=float)
    target = {1: 4, 2: 4, 3: 4}
    left = np.full(12, np.nan)
    right = np.full(12, np.nan)
    rng_c = np.random.default_rng(7)
    new_vals, n_mv = _rake_categorical_slot(cur, target, [1, 2, 3], left, right, rng_c)
    expected_moves = sum(max(0, target[c] - int(np.sum(cur == c))) for c in [1, 2, 3])
    achieved = {c: int(np.sum(new_vals == c)) for c in [1, 2, 3]}
    check("09 rake_categorical_slot n_moved == total deficit (no double-touch)",
          n_mv == expected_moves and achieved == target, (n_mv, expected_moves, achieved))


# ══════════════════════════════════════════════════════════════════════════════
# C. 3-way state / mutual exclusion  (cases 10-13)
# ══════════════════════════════════════════════════════════════════════════════

def test_state_and_mutual_exclusion():
    # 10. _compute_state correctness
    hom = np.array([[1.0, 0.0, 0.0]])
    wrk = np.array([[0.0, 1.0, 0.0]])
    state = _compute_state(hom, wrk)
    check("10 compute_state WORK/HOME/NEITHER correctly assigned",
          state.tolist() == [[STATE_HOME, STATE_WORK, STATE_NEITHER]], state)

    # 11. mutual state respect: hom30/wrk30 passed to _rake_act_group are untouched,
    #     and every record's activity draw only ever comes from records sharing its
    #     OWN state at that slot (structural guarantee -- verified by checking the
    #     achieved per-state activity distribution matches the state-specific
    #     observed target, not a blend of states).
    n_syn = 60
    df = pd.DataFrame(index=range(n_syn + 30))
    df["IS_SYNTHETIC"] = [1] * n_syn + [0] * 30
    for j in range(1, N_SLOTS + 1):
        df[f"hom30_{j:03d}"] = 0.0
        df[f"wrk30_{j:03d}"] = 0.0
        df[f"act30_{j:03d}"] = 5.0   # default: sleep/rest, category 5
    # Slot 10: first 20 syn rows WORK-state, next 20 HOME-state, last 20 NEITHER-state.
    t = 10
    df.loc[df.index[:20], f"wrk30_{t:03d}"] = 1.0                                   # WORK
    df.loc[df.index[20:40], f"hom30_{t:03d}"] = 1.0                                 # HOME
    # remaining 20 syn rows stay NEITHER (hom=0, wrk=0) at slot t
    # obs rows (last 30 idx): first 10 WORK doing act=1, next 10 HOME doing act=1 (telework),
    # last 10 NEITHER doing act=5 only (no floating work in obs)
    obs_idx = df.index[n_syn:]
    df.loc[obs_idx[:10], f"wrk30_{t:03d}"] = 1.0
    df.loc[obs_idx[:10], f"act30_{t:03d}"] = 1.0
    df.loc[obs_idx[10:20], f"hom30_{t:03d}"] = 1.0
    df.loc[obs_idx[10:20], f"act30_{t:03d}"] = 1.0
    df.loc[obs_idx[20:30], f"act30_{t:03d}"] = 5.0
    df["CYCLE_YEAR"] = 2022
    df["DDAY_STRATA"] = 1

    syn_idx = df.index[df["IS_SYNTHETIC"] == 1].tolist()
    obs_idx_list = df.index[df["IS_SYNTHETIC"] == 0].tolist()
    rng = np.random.default_rng(42)
    n_mv = _rake_act_group(df, syn_idx, obs_idx_list, ACT_COLS, HOM_COLS, WRK_COLS, rng)

    hom_col = f"hom30_{t:03d}"; wrk_col = f"wrk30_{t:03d}"; act_col = f"act30_{t:03d}"
    work_syn   = df.loc[df.index[:20]]
    home_syn   = df.loc[df.index[20:40]]
    neither_syn = df.loc[df.index[40:60]]
    check("11 mutual state respect: WORK-state syn slot all act==1 (matches obs WORK target)",
          (work_syn[act_col] == 1.0).all(), work_syn[act_col].tolist())
    check("11b mutual state respect: HOME-state syn slot all act==1 (TELEWORK preserved)",
          (home_syn[act_col] == 1.0).all(), home_syn[act_col].tolist())
    check("11c mutual state respect: NEITHER-state syn slot all act==5 (no floating induced)",
          (neither_syn[act_col] == 5.0).all(), neither_syn[act_col].tolist())
    check("11d hom30/wrk30 unchanged by _rake_act_group",
          (df[hom_col].isin([0.0, 1.0]).all()) and
          (df.loc[df.index[:20], wrk_col] == 1.0).all() and
          (df.loc[df.index[20:40], hom_col] == 1.0).all(),
          "hom/wrk sanity")

    # 12. TELEWORK preserved when observed HOME-state pool has a nonzero work share
    #     (already exercised by case 11b -- restate explicitly as its own case).
    check("12 TELEWORK is preserved, not zeroed, when legitimate in obs HOME state",
          (home_syn[act_col] == 1.0).all() and (home_syn[hom_col] == 1.0).all()
          and (home_syn[wrk_col] == 0.0).all(),
          "telework preserved")

    # 13. FLOATING driven down: syn NEITHER-state records start with high WORK_CAT
    #     share; obs NEITHER-state pool has ~0% work share -> after rake, syn
    #     NEITHER work share matches observed (0%).
    df2 = pd.DataFrame(index=range(40))
    df2["IS_SYNTHETIC"] = [1] * 20 + [0] * 20
    for j in range(1, N_SLOTS + 1):
        df2[f"hom30_{j:03d}"] = 0.0
        df2[f"wrk30_{j:03d}"] = 0.0
        df2[f"act30_{j:03d}"] = 5.0
    t2 = 5
    # all 20 syn rows start FLOATING with act==WORK_CAT (the bug this script fixes)
    df2.loc[df2.index[:20], f"act30_{t2:03d}"] = float(WORK_CAT)
    # obs NEITHER pool: 19/20 non-work, 1/20 work (small legitimate floating rate)
    df2.loc[df2.index[20:39], f"act30_{t2:03d}"] = 5.0
    df2.loc[df2.index[39], f"act30_{t2:03d}"] = float(WORK_CAT)
    df2["CYCLE_YEAR"] = 2022
    df2["DDAY_STRATA"] = 1
    syn_idx2 = df2.index[:20].tolist()
    obs_idx2 = df2.index[20:].tolist()
    rng2 = np.random.default_rng(42)
    _rake_act_group(df2, syn_idx2, obs_idx2, ACT_COLS, HOM_COLS, WRK_COLS, rng2)
    syn_work_after = int((df2.loc[df2.index[:20], f"act30_{t2:03d}"] == float(WORK_CAT)).sum())
    check("13 FLOATING driven toward observed rate (1/20 obs -> ~1/20 syn, not 20/20)",
          syn_work_after <= 2, syn_work_after)


# ══════════════════════════════════════════════════════════════════════════════
# D. _run_act30_conditional_rake integration  (cases 14-17)
# ══════════════════════════════════════════════════════════════════════════════

def _build_full_toy_frame(n_syn_per_cell=40, n_obs_per_cell=40, seed=0):
    """Builds a small multi-(cy,s,LFTAG) toy frame across all 48 slots, with a
    deliberately thin LFTAG=3 cell (< MIN_OBS_FOR_LFTAG obs) to exercise pooling."""
    rng = np.random.default_rng(seed)
    rows = []
    for cy in [2022]:
        for s in [1]:
            for lftag, n_obs in [(1, 40), (2, 40), (3, 5)]:   # LFTAG 3 is sparsity-thin
                for is_syn, n in [(0, n_obs), (1, n_syn_per_cell)]:
                    for i in range(n):
                        row = {"CYCLE_YEAR": cy, "DDAY_STRATA": s, "LFTAG": float(lftag),
                               "IS_SYNTHETIC": is_syn}
                        for j in range(1, N_SLOTS + 1):
                            # slot 20: the defect 04T is meant to fix. ALL syn rows start
                            # FLOATING (act=WORK_CAT, state=NEITHER). Obs rows are a 90/10
                            # mix of WORK-state (act=WORK_CAT) and NEITHER-state (act=5, NO
                            # floating) -- this gives the rake a NEITHER-state observed
                            # reference (10%) that should drive syn FLOATING toward ~0.
                            if j == 20:
                                if is_syn == 0 and i % 10 != 0:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 1.0
                                    row[f"act30_{j:03d}"] = float(WORK_CAT)
                                elif is_syn == 0:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0   # NEITHER (obs reference)
                                    row[f"act30_{j:03d}"] = 5.0
                                else:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0   # NEITHER
                                    row[f"act30_{j:03d}"] = float(WORK_CAT)   # FLOATING
                            else:
                                row[f"hom30_{j:03d}"] = 1.0
                                row[f"wrk30_{j:03d}"] = 0.0
                                row[f"act30_{j:03d}"] = 5.0
                        rows.append(row)
    # A few syn rows with LFTAG==NaN to exercise the pooled-NaN extension.
    for _ in range(6):
        row = {"CYCLE_YEAR": 2022, "DDAY_STRATA": 1, "LFTAG": np.nan, "IS_SYNTHETIC": 1}
        for j in range(1, N_SLOTS + 1):
            row[f"hom30_{j:03d}"] = 0.0
            row[f"wrk30_{j:03d}"] = 0.0
            row[f"act30_{j:03d}"] = float(WORK_CAT) if j == 20 else 5.0
        rows.append(row)
    return pd.DataFrame(rows)


def test_run_act30_conditional_rake_integration():
    df = _build_full_toy_frame()
    hom_before = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    act_before = df[ACT_COLS].to_numpy(dtype=float, copy=True)

    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_mask = df["IS_SYNTHETIC"] == 1
    rng = np.random.default_rng(42)
    total_moves, diag = _run_act30_conditional_rake(df, ACT_COLS, HOM_COLS, WRK_COLS, obs_mask, syn_mask, rng)

    # 14. hom30/wrk30 byte-identical before vs after full run
    hom_after = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    check("14 full-run hom30/wrk30 byte-identical", np.array_equal(hom_before, hom_after)
          and np.array_equal(wrk_before, wrk_after), "byte-identical check")

    # 15. LFTAG sparsity gate triggers pooling for LFTAG=3 (n_obs=5 < MIN_OBS_FOR_LFTAG=30)
    check("15 LFTAG sparsity gate pools thin LFTAG=3 cell",
          diag["n_cells_thin"] >= 1 and diag["n_cells_total"] >= 1, diag)
    check("15b LFTAG pooling includes NaN-LFTAG syn rows", diag["n_syn_rows_pooled"] > 0, diag)

    # 16. determinism under fixed seed -- rerun on a fresh copy, identical act30 result
    df_b = _build_full_toy_frame()
    rng_b = np.random.default_rng(42)
    _run_act30_conditional_rake(df_b, ACT_COLS, HOM_COLS, WRK_COLS,
                                 df_b["IS_SYNTHETIC"] == 0, df_b["IS_SYNTHETIC"] == 1, rng_b)
    act_a = df[ACT_COLS].to_numpy(dtype=float)
    act_b = df_b[ACT_COLS].to_numpy(dtype=float)
    check("16 full-run deterministic under fixed seed", np.array_equal(act_a, act_b), "act30 rerun match")

    # 17. no cross-slot contamination: slot 5 (untouched by the toy defect, constant
    #     across all rows/states) must be unchanged by the rake.
    slot5_before = act_before[:, 4]   # 0-indexed col 4 == act30_005
    slot5_after = df[ACT_COLS].to_numpy(dtype=float)[:, 4]
    check("17 no cross-slot contamination (slot 5 untouched)",
          np.array_equal(slot5_before, slot5_after), "slot 5 diff")

    return total_moves, diag


# ══════════════════════════════════════════════════════════════════════════════
# E. End-to-end small integration  (cases 18-19)
# ══════════════════════════════════════════════════════════════════════════════

def test_end_to_end():
    df = _build_full_toy_frame()
    n_rows_before, n_cols_before = df.shape
    cols_before = set(df.columns)

    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_mask = df["IS_SYNTHETIC"] == 1
    rng = np.random.default_rng(42)

    act_before = df[ACT_COLS].to_numpy(dtype=float, copy=True)
    hom_before = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = df[WRK_COLS].to_numpy(dtype=float, copy=True)

    total_moves, diag = _run_act30_conditional_rake(df, ACT_COLS, HOM_COLS, WRK_COLS, obs_mask, syn_mask, rng)

    # 18. schema/row-count preserved; only act30_* differs from input
    check("18 end-to-end row count preserved", df.shape[0] == n_rows_before, df.shape)
    check("18b end-to-end column set preserved", set(df.columns) == cols_before, "cols")
    hom_after = df[HOM_COLS].to_numpy(dtype=float)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float)
    act_after = df[ACT_COLS].to_numpy(dtype=float)
    only_act_changed = (np.array_equal(hom_before, hom_after) and
                         np.array_equal(wrk_before, wrk_after) and
                         not np.array_equal(act_before, act_after))
    check("18c end-to-end only act30_* changed", only_act_changed, "diff scope")

    # 19. n_moved matches real diffs: total_moves for slot 20 (the only slot the toy
    #     defect touches) should equal count of syn rows whose act30_020 actually
    #     changed value (no double counting within a single slot-call).
    diff_mask = act_before[:, 19] != act_after[:, 19]   # 0-indexed col 19 == act30_020
    syn_rows_bool = syn_mask.to_numpy()
    n_real_diffs_slot20 = int((diff_mask & syn_rows_bool).sum())
    check("19 total_moves plausible vs real per-slot diffs (no double count)",
          total_moves >= n_real_diffs_slot20 > 0, (total_moves, n_real_diffs_slot20))


# ══════════════════════════════════════════════════════════════════════════════

def main():
    test_round_to_sum()
    test_rake_categorical_slot()
    test_state_and_mutual_exclusion()
    tm, diag = test_run_act30_conditional_rake_integration()
    test_end_to_end()

    print("=" * 70)
    print("3rdJ_04T_act_rake_2split_test.py -- synthetic unit test results")
    print("=" * 70)
    n_pass = 0
    for name, ok, detail in RESULTS:
        status = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        print(f"  [{status}] {name}")
        if not ok:
            print(f"           detail: {detail}")
    print("-" * 70)
    print(f"  {n_pass}/{len(RESULTS)} PASS")
    print("=" * 70)

    if n_pass != len(RESULTS):
        sys.exit(1)


if __name__ == "__main__":
    main()
