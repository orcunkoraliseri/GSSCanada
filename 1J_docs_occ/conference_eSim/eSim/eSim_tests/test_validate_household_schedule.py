"""
Task 15 unit tests — illogical-row filter.

Tests validate_household_schedule() from integration.py:219-266.
Scope: only the illogical-row filter half of Task 15.
Multi-archetype sampling is already covered by Task 30.

Run with:  pytest eSim_tests/test_validate_household_schedule.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils.integration import validate_household_schedule


def _make_hh(weekday_occ, weekend_occ=None):
    """Build a minimal household dict as load_schedules() would produce."""
    if weekend_occ is None:
        weekend_occ = weekday_occ
    return {
        'Weekday': [{'hour': h, 'occ': weekday_occ[h], 'met': 1.0} for h in range(24)],
        'Weekend': [{'hour': h, 'occ': weekend_occ[h], 'met': 1.0} for h in range(24)],
    }


def test_valid_mixed_day():
    """Realistic mixed-day profile (morning absence, afternoon/evening presence) → True."""
    # 7 zeros, then gradual presence ramp through work-from-home afternoon pattern
    profile = [0.0] * 7 + [0.5, 1, 1, 1, 0.5, 0.2, 0, 0, 0.5, 1, 1, 1, 1, 1, 1, 1, 1]
    assert len(profile) == 24
    assert validate_household_schedule(_make_hh(profile)) is True


def test_out_of_range():
    """Any occ value > 1.0 → False."""
    profile = [0.0] * 7 + [0.5, 1, 1, 1, 0.5, 0.2, 0, 0, 0.5, 1, 1, 1, 1, 1, 1, 1, 1]
    bad = list(profile)
    bad[8] = 1.5  # inject out-of-range value
    assert validate_household_schedule(_make_hh(bad)) is False


def test_all_zero_weekday():
    """All-zero weekday (nobody ever home — data error) → False."""
    assert validate_household_schedule(_make_hh([0.0] * 24)) is False


def test_total_below_minimum():
    """Single occ=0.5 at hour 0, rest 0 → total = 0.5 < 2.0 floor → False."""
    profile = [0.5] + [0.0] * 23
    assert validate_household_schedule(_make_hh(profile)) is False


def test_spike_pattern():
    """5 isolated 1.0-spikes surrounded by zeros → spike_count = 5 > 4 → False."""
    profile = [0.0] * 24
    for h in [2, 6, 10, 14, 18]:
        profile[h] = 1.0
    assert validate_household_schedule(_make_hh(profile)) is False
