# -*- coding: utf-8 -*-
"""
3rdJ_04T_act_rake_4split_test.py — synthetic unit test suite for
3rdJ_04T_act_rake_4split.py.

Forked from Leg-2's 3rdJ_04T_act_rake_2split_test.py (itself mirroring 2J's 19-case
synthetic unit test for _rake_categorical_slot / _run_act30_conditional_rake). Extends
every case to carry a third occupancy channel (ret30) and adds new cases (10b, 11e,
13b) exercising the 4-way state machine's RETAIL state and its WORK > RETAIL > HOME >
NEITHER priority. No real data is read; every case constructs a small toy frame with
known state-conditional activity marginals in-process.

Run:
    py -3 3rdJ_04T_act_rake_4split_test.py

Exit code 0 on all-PASS, 1 otherwise.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_MOD_PATH = os.path.join(SCRIPT_DIR, "3rdJ_04T_act_rake_4split.py")
_spec = importlib.util.spec_from_file_location("_04T", _MOD_PATH)
_04T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_04T)

_round_to_sum               = _04T._round_to_sum
_rake_categorical_slot      = _04T._rake_categorical_slot
_rake_act_group              = _04T._rake_act_group
_run_act30_conditional_rake  = _04T._run_act30_conditional_rake
_compute_state               = _04T._compute_state
STATE_WORK, STATE_RETAIL, STATE_HOME, STATE_NEITHER = (
    _04T.STATE_WORK, _04T.STATE_RETAIL, _04T.STATE_HOME, _04T.STATE_NEITHER
)
N_SLOTS = _04T.N_SLOTS
ACT_CATEGORIES = _04T.ACT_CATEGORIES
WORK_CAT = _04T.WORK_CAT
RETAIL_CAT = _04T.RETAIL_CAT
HOM_COLS, WRK_COLS, RET_COLS, ACT_COLS = _04T.HOM_COLS, _04T.WRK_COLS, _04T.RET_COLS, _04T.ACT_COLS
MIN_OBS_FOR_LFTAG = _04T.MIN_OBS_FOR_LFTAG

RESULTS = []   # (name, ok, detail)


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


# ══════════════════════════════════════════════════════════════════════════════
# A. _round_to_sum  (cases 1-4) -- unchanged from Leg-2 (generic helper)
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
# B. _rake_categorical_slot  (cases 5-9) -- unchanged from Leg-2 (generic helper)
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
# C. 4-way state / mutual exclusion  (cases 10-13, Leg-3-extended)
# ══════════════════════════════════════════════════════════════════════════════

def test_state_and_mutual_exclusion():
    # 10. _compute_state correctness -- WORK / RETAIL / HOME / NEITHER, 4 slots
    hom = np.array([[1.0, 0.0, 0.0, 0.0]])
    wrk = np.array([[0.0, 1.0, 0.0, 0.0]])
    ret = np.array([[0.0, 0.0, 1.0, 0.0]])
    state = _compute_state(hom, wrk, ret)
    check("10 compute_state WORK/RETAIL/HOME/NEITHER correctly assigned",
          state.tolist() == [[STATE_HOME, STATE_WORK, STATE_RETAIL, STATE_NEITHER]], state)

    # 10b. priority tie-break: WORK > RETAIL > HOME > NEITHER (the ~0% overlap safety
    #      net -- 04L guarantees exclusivity so this should not occur in production).
    hom_tb = np.array([[1.0, 1.0]])
    wrk_tb = np.array([[0.0, 1.0]])
    ret_tb = np.array([[1.0, 1.0]])
    state_tb = _compute_state(hom_tb, wrk_tb, ret_tb)
    check("10b compute_state priority: hom=1&ret=1&wrk=0 -> RETAIL wins over HOME",
          state_tb[0, 0] == STATE_RETAIL, state_tb)
    check("10c compute_state priority: hom=1&ret=1&wrk=1 -> WORK wins over both",
          state_tb[0, 1] == STATE_WORK, state_tb)

    # 11. mutual state respect: hom30/wrk30/ret30 passed to _rake_act_group are
    #     untouched, and every record's activity draw only ever comes from records
    #     sharing its OWN state at that slot (structural guarantee -- verified by
    #     checking the achieved per-state activity distribution matches the
    #     state-specific observed target, not a blend of states).
    n_syn = 80
    df = pd.DataFrame(index=range(n_syn + 40))
    df["IS_SYNTHETIC"] = [1] * n_syn + [0] * 40
    for j in range(1, N_SLOTS + 1):
        df[f"hom30_{j:03d}"] = 0.0
        df[f"wrk30_{j:03d}"] = 0.0
        df[f"ret30_{j:03d}"] = 0.0
        df[f"act30_{j:03d}"] = 5.0   # default: sleep/rest, category 5
    # Slot 10: 20 syn rows each of WORK / HOME / RETAIL / NEITHER states.
    t = 10
    df.loc[df.index[:20], f"wrk30_{t:03d}"] = 1.0                                    # WORK
    df.loc[df.index[20:40], f"hom30_{t:03d}"] = 1.0                                  # HOME
    df.loc[df.index[40:60], f"ret30_{t:03d}"] = 1.0                                  # RETAIL
    # remaining 20 syn rows (index 60:80) stay NEITHER (hom=0, wrk=0, ret=0) at slot t
    # obs rows (last 40 idx): 10 WORK doing act=1, 10 HOME doing act=1 (telework),
    # 10 RETAIL doing act=RETAIL_CAT (shopping), 10 NEITHER doing act=5 only (no
    # floating work/shopping in obs).
    obs_idx = df.index[n_syn:]
    df.loc[obs_idx[:10], f"wrk30_{t:03d}"] = 1.0
    df.loc[obs_idx[:10], f"act30_{t:03d}"] = 1.0
    df.loc[obs_idx[10:20], f"hom30_{t:03d}"] = 1.0
    df.loc[obs_idx[10:20], f"act30_{t:03d}"] = 1.0
    df.loc[obs_idx[20:30], f"ret30_{t:03d}"] = 1.0
    df.loc[obs_idx[20:30], f"act30_{t:03d}"] = float(RETAIL_CAT)
    df.loc[obs_idx[30:40], f"act30_{t:03d}"] = 5.0
    df["CYCLE_YEAR"] = 2022
    df["DDAY_STRATA"] = 1

    syn_idx = df.index[df["IS_SYNTHETIC"] == 1].tolist()
    obs_idx_list = df.index[df["IS_SYNTHETIC"] == 0].tolist()
    rng = np.random.default_rng(42)
    n_mv = _rake_act_group(df, syn_idx, obs_idx_list, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, rng)

    hom_col = f"hom30_{t:03d}"; wrk_col = f"wrk30_{t:03d}"; ret_col = f"ret30_{t:03d}"; act_col = f"act30_{t:03d}"
    work_syn    = df.loc[df.index[:20]]
    home_syn    = df.loc[df.index[20:40]]
    retail_syn  = df.loc[df.index[40:60]]
    neither_syn = df.loc[df.index[60:80]]
    check("11 mutual state respect: WORK-state syn slot all act==1 (matches obs WORK target)",
          (work_syn[act_col] == 1.0).all(), work_syn[act_col].tolist())
    check("11b mutual state respect: HOME-state syn slot all act==1 (TELEWORK preserved)",
          (home_syn[act_col] == 1.0).all(), home_syn[act_col].tolist())
    check("11c mutual state respect: NEITHER-state syn slot all act==5 (no floating induced)",
          (neither_syn[act_col] == 5.0).all(), neither_syn[act_col].tolist())
    check("11d hom30/wrk30/ret30 unchanged by _rake_act_group",
          (df[hom_col].isin([0.0, 1.0]).all()) and
          (df.loc[df.index[:20], wrk_col] == 1.0).all() and
          (df.loc[df.index[20:40], hom_col] == 1.0).all() and
          (df.loc[df.index[40:60], ret_col] == 1.0).all(),
          "hom/wrk/ret sanity")
    # 11e. RETAIL-state syn slot activity matches observed RETAIL target (shopping).
    check("11e mutual state respect: RETAIL-state syn slot all act==RETAIL_CAT",
          (retail_syn[act_col] == float(RETAIL_CAT)).all(), retail_syn[act_col].tolist())

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
        df2[f"ret30_{j:03d}"] = 0.0
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
    _rake_act_group(df2, syn_idx2, obs_idx2, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, rng2)
    syn_work_after = int((df2.loc[df2.index[:20], f"act30_{t2:03d}"] == float(WORK_CAT)).sum())
    check("13 FLOATING driven toward observed rate (1/20 obs -> ~1/20 syn, not 20/20)",
          syn_work_after <= 2, syn_work_after)

    # 13b. RETAIL-state activity raked toward observed RETAIL distribution (the
    #      retail-channel analogue of case 13, using the STATE_RETAIL group instead
    #      of STATE_NEITHER): syn RETAIL-state rows start wrongly coded act==5
    #      (sleep, not shopping); obs RETAIL-state pool is 100% RETAIL_CAT.
    df3 = pd.DataFrame(index=range(40))
    df3["IS_SYNTHETIC"] = [1] * 20 + [0] * 20
    for j in range(1, N_SLOTS + 1):
        df3[f"hom30_{j:03d}"] = 0.0
        df3[f"wrk30_{j:03d}"] = 0.0
        df3[f"ret30_{j:03d}"] = 0.0
        df3[f"act30_{j:03d}"] = 5.0
    t3 = 7
    # all 20 syn rows are physically RETAIL (ret30==1) but wrongly coded act==5
    df3.loc[df3.index[:20], f"ret30_{t3:03d}"] = 1.0
    df3.loc[df3.index[:20], f"act30_{t3:03d}"] = 5.0
    # obs RETAIL-state pool: all 20 obs rows are RETAIL-state doing shopping (act=RETAIL_CAT)
    df3.loc[df3.index[20:40], f"ret30_{t3:03d}"] = 1.0
    df3.loc[df3.index[20:40], f"act30_{t3:03d}"] = float(RETAIL_CAT)
    df3["CYCLE_YEAR"] = 2022
    df3["DDAY_STRATA"] = 1
    syn_idx3 = df3.index[:20].tolist()
    obs_idx3 = df3.index[20:].tolist()
    rng3 = np.random.default_rng(42)
    ret_before3 = df3[RET_COLS].to_numpy(dtype=float, copy=True)
    _rake_act_group(df3, syn_idx3, obs_idx3, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, rng3)
    syn_shop_after = int((df3.loc[df3.index[:20], f"act30_{t3:03d}"] == float(RETAIL_CAT)).sum())
    ret_after3 = df3[RET_COLS].to_numpy(dtype=float)
    check("13b RETAIL-state activity raked toward observed RETAIL_CAT target (20/20)",
          syn_shop_after == 20, syn_shop_after)
    check("13c RETAIL-state rake does not mutate ret30", np.array_equal(ret_before3, ret_after3), "ret30 diff")


# ══════════════════════════════════════════════════════════════════════════════
# D. _run_act30_conditional_rake integration  (cases 14-17)
# ══════════════════════════════════════════════════════════════════════════════

def _build_full_toy_frame(n_syn_per_cell=40, n_obs_per_cell=40, seed=0):
    """Builds a small multi-(cy,s,LFTAG) toy frame across all 48 slots, with a
    deliberately thin LFTAG=3 cell (< MIN_OBS_FOR_LFTAG obs) to exercise pooling.
    Slot 20 carries the Leg-2-inherited WORK/NEITHER FLOATING defect; slot 25 adds a
    Leg-3 RETAIL-state defect (syn rows physically at retail but wrongly act-coded)."""
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
                            if j == 20:
                                # slot 20: the Leg-2 defect. ALL syn rows start FLOATING
                                # (act=WORK_CAT, state=NEITHER). Obs rows are a 90/10 mix
                                # of WORK-state (act=WORK_CAT) and NEITHER-state (act=5,
                                # NO floating) -- gives the rake a NEITHER-state observed
                                # reference (10%) that should drive syn FLOATING toward ~0.
                                if is_syn == 0 and i % 10 != 0:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 1.0
                                    row[f"ret30_{j:03d}"] = 0.0
                                    row[f"act30_{j:03d}"] = float(WORK_CAT)
                                elif is_syn == 0:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0   # NEITHER (obs reference)
                                    row[f"ret30_{j:03d}"] = 0.0
                                    row[f"act30_{j:03d}"] = 5.0
                                else:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0   # NEITHER
                                    row[f"ret30_{j:03d}"] = 0.0
                                    row[f"act30_{j:03d}"] = float(WORK_CAT)   # FLOATING
                            elif j == 25:
                                # slot 25: the Leg-3 RETAIL-state defect. ALL syn rows are
                                # physically RETAIL (ret30==1) but wrongly act-coded (act=5,
                                # not shopping). Obs RETAIL-state rows all correctly do
                                # shopping (act=RETAIL_CAT).
                                if is_syn == 0:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0
                                    row[f"ret30_{j:03d}"] = 1.0
                                    row[f"act30_{j:03d}"] = float(RETAIL_CAT)
                                else:
                                    row[f"hom30_{j:03d}"] = 0.0
                                    row[f"wrk30_{j:03d}"] = 0.0
                                    row[f"ret30_{j:03d}"] = 1.0
                                    row[f"act30_{j:03d}"] = 5.0
                            else:
                                row[f"hom30_{j:03d}"] = 1.0
                                row[f"wrk30_{j:03d}"] = 0.0
                                row[f"ret30_{j:03d}"] = 0.0
                                row[f"act30_{j:03d}"] = 5.0
                        rows.append(row)
    # A few syn rows with LFTAG==NaN to exercise the pooled-NaN extension.
    for _ in range(6):
        row = {"CYCLE_YEAR": 2022, "DDAY_STRATA": 1, "LFTAG": np.nan, "IS_SYNTHETIC": 1}
        for j in range(1, N_SLOTS + 1):
            row[f"hom30_{j:03d}"] = 0.0
            row[f"wrk30_{j:03d}"] = 0.0
            row[f"ret30_{j:03d}"] = 0.0
            row[f"act30_{j:03d}"] = float(WORK_CAT) if j == 20 else 5.0
        rows.append(row)
    return pd.DataFrame(rows)


def test_run_act30_conditional_rake_integration():
    df = _build_full_toy_frame()
    hom_before = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    ret_before = df[RET_COLS].to_numpy(dtype=float, copy=True)
    act_before = df[ACT_COLS].to_numpy(dtype=float, copy=True)

    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_mask = df["IS_SYNTHETIC"] == 1
    rng = np.random.default_rng(42)
    total_moves, diag = _run_act30_conditional_rake(df, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, obs_mask, syn_mask, rng)

    # 14. hom30/wrk30/ret30 byte-identical before vs after full run
    hom_after = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    ret_after = df[RET_COLS].to_numpy(dtype=float, copy=True)
    check("14 full-run hom30/wrk30/ret30 byte-identical", np.array_equal(hom_before, hom_after)
          and np.array_equal(wrk_before, wrk_after) and np.array_equal(ret_before, ret_after),
          "byte-identical check")

    # 15. LFTAG sparsity gate triggers pooling for LFTAG=3 (n_obs=5 < MIN_OBS_FOR_LFTAG=30)
    check("15 LFTAG sparsity gate pools thin LFTAG=3 cell",
          diag["n_cells_thin"] >= 1 and diag["n_cells_total"] >= 1, diag)
    check("15b LFTAG pooling includes NaN-LFTAG syn rows", diag["n_syn_rows_pooled"] > 0, diag)

    # 16. determinism under fixed seed -- rerun on a fresh copy, identical act30 result
    df_b = _build_full_toy_frame()
    rng_b = np.random.default_rng(42)
    _run_act30_conditional_rake(df_b, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS,
                                 df_b["IS_SYNTHETIC"] == 0, df_b["IS_SYNTHETIC"] == 1, rng_b)
    act_a = df[ACT_COLS].to_numpy(dtype=float)
    act_b = df_b[ACT_COLS].to_numpy(dtype=float)
    check("16 full-run deterministic under fixed seed", np.array_equal(act_a, act_b), "act30 rerun match")

    # 17. no cross-slot contamination: slot 5 (untouched by the toy defects, constant
    #     across all rows/states) must be unchanged by the rake.
    slot5_before = act_before[:, 4]   # 0-indexed col 4 == act30_005
    slot5_after = df[ACT_COLS].to_numpy(dtype=float)[:, 4]
    check("17 no cross-slot contamination (slot 5 untouched)",
          np.array_equal(slot5_before, slot5_after), "slot 5 diff")

    # 17b. Leg-3 RETAIL-state defect (slot 25) actually gets fixed by the full-run
    #      integration path (not just the isolated _rake_act_group unit test).
    act_after = df[ACT_COLS].to_numpy(dtype=float)
    slot25_syn_after = act_after[syn_mask.to_numpy(), 24]   # 0-indexed col 24 == act30_025
    n_slot25_fixed = int((slot25_syn_after == float(RETAIL_CAT)).sum())
    check("17c full-run integration fixes the RETAIL-state defect at slot 25",
          n_slot25_fixed > 0, n_slot25_fixed)

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
    ret_before = df[RET_COLS].to_numpy(dtype=float, copy=True)

    total_moves, diag = _run_act30_conditional_rake(df, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, obs_mask, syn_mask, rng)

    # 18. schema/row-count preserved; only act30_* differs from input
    check("18 end-to-end row count preserved", df.shape[0] == n_rows_before, df.shape)
    check("18b end-to-end column set preserved", set(df.columns) == cols_before, "cols")
    hom_after = df[HOM_COLS].to_numpy(dtype=float)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float)
    ret_after = df[RET_COLS].to_numpy(dtype=float)
    act_after = df[ACT_COLS].to_numpy(dtype=float)
    only_act_changed = (np.array_equal(hom_before, hom_after) and
                         np.array_equal(wrk_before, wrk_after) and
                         np.array_equal(ret_before, ret_after) and
                         not np.array_equal(act_before, act_after))
    check("18c end-to-end only act30_* changed", only_act_changed, "diff scope")

    # 19. n_moved matches real diffs: total_moves for slot 20 (the Leg-2-inherited
    #     defect slot) should be >= count of syn rows whose act30_020 actually
    #     changed value (no double counting within a single slot-call), and > 0.
    diff_mask = act_before[:, 19] != act_after[:, 19]   # 0-indexed col 19 == act30_020
    syn_rows_bool = syn_mask.to_numpy()
    n_real_diffs_slot20 = int((diff_mask & syn_rows_bool).sum())
    check("19 total_moves plausible vs real per-slot diffs (no double count)",
          total_moves >= n_real_diffs_slot20 > 0, (total_moves, n_real_diffs_slot20))

    # 19b. same check for slot 25 (the Leg-3 RETAIL-state defect slot).
    diff_mask25 = act_before[:, 24] != act_after[:, 24]   # 0-indexed col 24 == act30_025
    n_real_diffs_slot25 = int((diff_mask25 & syn_rows_bool).sum())
    check("19c total_moves plausible vs real per-slot diffs at slot 25 (RETAIL defect)",
          total_moves >= n_real_diffs_slot25 > 0, (total_moves, n_real_diffs_slot25))


# ══════════════════════════════════════════════════════════════════════════════

def main():
    test_round_to_sum()
    test_rake_categorical_slot()
    test_state_and_mutual_exclusion()
    tm, diag = test_run_act30_conditional_rake_integration()
    test_end_to_end()

    print("=" * 70)
    print("3rdJ_04T_act_rake_4split_test.py -- synthetic unit test results")
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
