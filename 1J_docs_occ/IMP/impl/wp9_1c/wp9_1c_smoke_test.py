# =============================================================================
# wp9_1c_smoke_test.py
# Tiny, LOCAL, synthetic smoke test for wp9_1c_2025_rebuild.py's two runtime
# overrides. No CSV I/O, no cluster paths, no TensorFlow/sklearn/matplotlib
# import (wp9_1c_2025_rebuild.py only imports previous.eSim_dynamicML_mHead
# inside install_overrides(), which this test never calls -- it calls the
# override functions directly against lightweight fake "self" objects).
#
# Run: py wp9_1c_smoke_test.py
# =============================================================================

import os
import sys

import numpy as np
import pandas as pd

# The driver copies the original module's print lines verbatim, including a
# U+1F680 emoji (previous/eSim_dynamicML_mHead.py:2345). Windows' default
# console codepage (cp1252) cannot encode it; reconfigure stdout for this
# local test only -- the driver text itself is left untouched (Linux/cluster
# stdout is UTF-8 by default and never hits this).
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp9_1c_2025_rebuild as drv


def make_person_grid(loc_pattern, act_pattern, dens_pattern):
    return pd.DataFrame({
        'ind_occPRE': loc_pattern,
        'ind_occACT': act_pattern,
        'ind_density': dens_pattern,
    })


def test_aggregate_household_override():
    class FakeAgg:
        res = 5
        slots = 288
    self_ = FakeAgg()

    n = 288
    # Person A: home (1) for slots [0, 100), away after; activity 1 while home.
    a_loc = [1] * 100 + [0] * (n - 100)
    a_act = [1] * 100 + [0] * (n - 100)
    a_den = [0] * n
    # Person B: home (1) for slots [50, 150); activity 2 while home.
    b_loc = [0] * 50 + [1] * 100 + [0] * (n - 150)
    b_act = [0] * 50 + [2] * 100 + [0] * (n - 150)
    b_den = [0] * n

    person_a = make_person_grid(a_loc, a_act, a_den)
    person_b = make_person_grid(b_loc, b_act, b_den)

    hh_df = drv.aggregate_household_override(self_, [person_a, person_b])

    assert len(hh_df) == n, f"expected {n} rows, got {len(hh_df)}"
    assert 'occCount' in hh_df.columns and 'nGrid' in hh_df.columns, "occCount/nGrid missing (P2 not applied)"
    assert (hh_df['nGrid'] == 2).all(), "nGrid must equal len(people_grids) for every slot"
    assert hh_df['occCount'].iloc[0] == 1, "slot 0: only A home -> occCount should be 1"
    assert hh_df['occCount'].iloc[75] == 2, "slot 75: A and B both home -> occCount should be 2"
    assert hh_df['occCount'].iloc[200] == 0, "slot 200: nobody home -> occCount should be 0"

    # Early-return (empty household) branch.
    hh_df_empty = drv.aggregate_household_override(self_, [])
    assert (hh_df_empty['occCount'] == 0).all(), "empty household: occCount must be 0"
    assert (hh_df_empty['nGrid'] == 0).all(), "empty household: nGrid must be 0"

    print("aggregate_household_override: PASS "
          "(occCount tracks headcount, nGrid == len(people_grids), empty branch is 0/0)")


def _make_bem_input_df(hh_size, occ_count_pattern, n_grid):
    """24 five-minute slots = 2 hours, one household, one day type."""
    n = 24
    time_slots = pd.date_range("00:00", "01:55", freq="5min").strftime('%H:%M')
    return pd.DataFrame({
        'SIM_HH_ID': ['HH1'] * n,
        'Day_Type': ['Weekday'] * n,
        'Time_Slot': time_slots,
        'HHSIZE': [hh_size] * n,
        'DTYPE': ['1'] * n,
        'BEDRM': [3] * n,
        'CONDO': [0] * n,
        'ROOM': [6] * n,
        'REPAIR': [1] * n,
        'PR': ['35'] * n,
        'occPre': [1] * n,
        'occDensity': [0] * n,
        'occActivity': ['0'] * n,
        'occCount': occ_count_pattern,
        'nGrid': [n_grid] * n,
    })


class FakeConv:
    dtype_map = {'1': 'SingleD'}
    pr_map = {'35': 'Ontario'}

    def _calculate_watts(self, act_str):
        return 0.0


def test_process_households_override_grid_and_hhsize():
    self_ = FakeConv()
    # 12 slots at occCount=1, 12 at occCount=2 -> mean 1.5 in each of the 2 hours.
    occ_count_pattern = [1, 2] * 12
    hh_size = 4
    n_grid = 4  # deliberately equal to hh_size so grid and hhsize give the same number here

    os.environ['OCC_DENOM'] = 'grid'
    df_grid = drv.process_households_override(self_, _make_bem_input_df(hh_size, occ_count_pattern, n_grid).copy())
    expected = round(1.5 / n_grid, 3)
    got = df_grid['Occupancy_Schedule'].iloc[0]
    assert np.isclose(got, expected), f"grid mode: expected occCount/nGrid={expected}, got {got}"
    print(f"grid mode: Occupancy_Schedule = {got} (expected occCount/nGrid = {expected}) PASS")

    os.environ['OCC_DENOM'] = 'hhsize'
    df_hhsize = drv.process_households_override(self_, _make_bem_input_df(hh_size, occ_count_pattern, n_grid).copy())
    expected_h = round(1.5 / hh_size, 3)
    got_h = df_hhsize['Occupancy_Schedule'].iloc[0]
    assert np.isclose(got_h, expected_h), f"hhsize mode: expected occCount/HHSIZE={expected_h}, got {got_h}"
    print(f"hhsize mode: Occupancy_Schedule = {got_h} (expected occCount/HHSIZE = {expected_h}) PASS")

    # nGrid=0 for the grid-mode zero-division guard (0/0 -> 0.0, not NaN/inf).
    os.environ['OCC_DENOM'] = 'grid'
    df_zero_grid = drv.process_households_override(self_, _make_bem_input_df(hh_size, [0] * 24, 0).copy())
    got_z = df_zero_grid['Occupancy_Schedule'].iloc[0]
    assert got_z == 0.0, f"nGrid=0 should give Occupancy_Schedule 0.0 (fillna guard), got {got_z}"
    print(f"grid mode, nGrid=0: Occupancy_Schedule = {got_z} (expected 0.0, div-by-zero guard) PASS")


def test_unset_occ_denom_raises_first():
    """Seen failing FIRST, per task doc T2: run with OCC_DENOM unset and record the ValueError."""
    self_ = FakeConv()
    if 'OCC_DENOM' in os.environ:
        del os.environ['OCC_DENOM']
    df = _make_bem_input_df(hh_size=2, occ_count_pattern=[1] * 24, n_grid=2)
    try:
        drv.process_households_override(self_, df.copy())
    except ValueError as e:
        print(f"unset OCC_DENOM: raised ValueError as expected -> {e}")
        return
    raise AssertionError("expected ValueError for unset OCC_DENOM, none was raised")


if __name__ == "__main__":
    print("=== SEEN FAILING FIRST: OCC_DENOM unset ===")
    test_unset_occ_denom_raises_first()

    print("\n=== P2 override (aggregation) ===")
    test_aggregate_household_override()

    print("\n=== P3 override (converter), both OCC_DENOM modes ===")
    test_process_households_override_grid_and_hhsize()

    print("\nALL SMOKE TESTS PASSED")
