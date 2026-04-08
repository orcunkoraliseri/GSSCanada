"""
Regression tests for PresenceFilter and LightingGenerator.

Run with:  pytest eSim_tests/test_schedule_generator.py -v

Fixtures
--------
  always_home    — presence=1.0 every hour
  always_away    — presence=0.0 every hour
  fractional     — presence=0.4 every hour (partial occupancy)
  single_absence — absent only hours 9-16, home otherwise

These tests act as a tripwire: if any refactor of schedule_generator.py
silently changes EUI-relevant behaviour, at least one assertion will fail.
"""

import sys
import os
import pytest

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils.schedule_generator import PresenceFilter, LightingGenerator

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

# DOE MidRise fallback values (matches idf_optimizer._get_fallback_schedules)
DEFAULT_EQUIP = [
    0.45, 0.41, 0.39, 0.38, 0.38, 0.43, 0.54, 0.65,
    0.66, 0.67, 0.69, 0.70, 0.69, 0.66, 0.65, 0.68,
    0.80, 1.00, 1.00, 0.93, 0.89, 0.85, 0.71, 0.58
]

DEFAULT_LIGHTS = [
    0.01, 0.01, 0.01, 0.01, 0.03, 0.07, 0.08, 0.07,
    0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.04,
    0.08, 0.11, 0.15, 0.18, 0.18, 0.12, 0.07, 0.03
]


# ---------------------------------------------------------------------------
# Presence schedule fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def always_home():
    return [1.0] * 24


@pytest.fixture
def always_away():
    return [0.0] * 24


@pytest.fixture
def fractional():
    """0.4 every hour — one of 2.5 household members home."""
    return [0.4] * 24


@pytest.fixture
def single_absence():
    """Away hours 9–16 (8 hours), home otherwise."""
    return [0.0 if 9 <= h <= 16 else 1.0 for h in range(24)]


# ---------------------------------------------------------------------------
# PresenceFilter tests
# ---------------------------------------------------------------------------

class TestPresenceFilterAlwaysHome:
    """When everyone is always home the result should equal the blended formula
    at presence=1.0: result = 1.0*default + 0.0*baseload = default."""

    def test_result_equals_default_when_fully_home(self, always_home):
        pf = PresenceFilter(DEFAULT_EQUIP, always_home)
        result = pf.apply(always_home)
        for h in range(24):
            assert abs(result[h] - DEFAULT_EQUIP[h]) < 1e-9, (
                f"Hour {h}: expected {DEFAULT_EQUIP[h]:.4f}, got {result[h]:.4f}"
            )

    def test_no_value_below_zero(self, always_home):
        pf = PresenceFilter(DEFAULT_EQUIP, always_home)
        result = pf.apply(always_home)
        assert all(v >= 0.0 for v in result)


class TestPresenceFilterAlwaysAway:
    """When nobody is ever home every hour returns baseload."""

    def test_all_hours_equal_baseload(self, always_away):
        pf = PresenceFilter(DEFAULT_EQUIP, always_away)
        result = pf.apply(always_away)
        expected = pf.base_load
        for h in range(24):
            assert abs(result[h] - expected) < 1e-9, (
                f"Hour {h}: expected baseload {expected:.4f}, got {result[h]:.4f}"
            )

    def test_baseload_uses_typical_away_hours_fallback(self, always_away):
        """With no absent hours available, base_load should use 9 AM–5 PM values."""
        pf = PresenceFilter(DEFAULT_EQUIP, always_away)
        typical_away_min = min(DEFAULT_EQUIP[h] for h in range(9, 17))
        assert abs(pf.base_load - typical_away_min) < 1e-9


class TestPresenceFilterFractional:
    """Partial occupancy (0.4) must produce values strictly between baseload and default."""

    def test_blended_value_is_between_base_and_default(self, fractional):
        pf = PresenceFilter(DEFAULT_EQUIP, fractional)
        result = pf.apply(fractional)
        for h in range(24):
            low = pf.base_load
            high = DEFAULT_EQUIP[h]
            assert low <= result[h] <= high + 1e-9, (
                f"Hour {h}: result {result[h]:.4f} not in [{low:.4f}, {high:.4f}]"
            )

    def test_blended_formula_correct(self, fractional):
        """Verify occ*default + (1-occ)*baseload for all hours."""
        occ = 0.4
        pf = PresenceFilter(DEFAULT_EQUIP, fractional)
        result = pf.apply(fractional)
        for h in range(24):
            expected = occ * DEFAULT_EQUIP[h] + (1.0 - occ) * pf.base_load
            assert abs(result[h] - expected) < 1e-9, (
                f"Hour {h}: expected {expected:.4f}, got {result[h]:.4f}"
            )

    def test_24_values_returned(self, fractional):
        pf = PresenceFilter(DEFAULT_EQUIP, fractional)
        assert len(pf.apply(fractional)) == 24


class TestPresenceFilterSingleAbsence:
    """Absent hours 9-16 get baseload; present hours get blended formula."""

    def test_absent_hours_get_baseload(self, single_absence):
        pf = PresenceFilter(DEFAULT_EQUIP, single_absence)
        result = pf.apply(single_absence)
        for h in range(9, 17):
            assert abs(result[h] - pf.base_load) < 1e-9, (
                f"Hour {h} (absent): expected base_load {pf.base_load:.4f}, got {result[h]:.4f}"
            )

    def test_present_hours_use_default(self, single_absence):
        """At presence=1.0, blended formula gives exactly default_val."""
        pf = PresenceFilter(DEFAULT_EQUIP, single_absence)
        result = pf.apply(single_absence)
        for h in list(range(0, 9)) + list(range(17, 24)):
            assert abs(result[h] - DEFAULT_EQUIP[h]) < 1e-9, (
                f"Hour {h} (present): expected {DEFAULT_EQUIP[h]:.4f}, got {result[h]:.4f}"
            )

    def test_baseload_from_absent_hours(self, single_absence):
        """Base_load must be the minimum of DEFAULT_EQUIP during absent hours 9-16."""
        pf = PresenceFilter(DEFAULT_EQUIP, single_absence)
        expected_base = min(DEFAULT_EQUIP[h] for h in range(9, 17))
        assert abs(pf.base_load - expected_base) < 1e-9


# ---------------------------------------------------------------------------
# LightingGenerator tests (non-seasonal path)
# ---------------------------------------------------------------------------

class TestLightingGeneratorNoStat:
    """Without a .stat file, LightingGenerator uses the conservative fallback."""

    def test_always_home_returns_default_values(self, always_home):
        lg = LightingGenerator(epw_path=None)
        result = lg.generate(always_home, DEFAULT_LIGHTS)
        for h in range(24):
            assert abs(result[h] - DEFAULT_LIGHTS[h]) < 1e-9, (
                f"Hour {h}: expected {DEFAULT_LIGHTS[h]:.4f}, got {result[h]:.4f}"
            )

    def test_always_away_returns_baseload(self, always_away):
        lg = LightingGenerator(epw_path=None)
        result = lg.generate(always_away, DEFAULT_LIGHTS)
        # All hours should be the same base_load (min of 9AM–5PM typical away)
        away_min = min(DEFAULT_LIGHTS[h] for h in range(9, 17))
        for h in range(24):
            assert abs(result[h] - away_min) < 1e-9, (
                f"Hour {h}: expected baseload {away_min:.4f}, got {result[h]:.4f}"
            )

    def test_24_values_returned(self, single_absence):
        lg = LightingGenerator(epw_path=None)
        assert len(lg.generate(single_absence, DEFAULT_LIGHTS)) == 24

    def test_generate_monthly_without_stat_returns_same_as_generate(self, single_absence):
        """Without solar data, daylight factors are all 1.0, so monthly == non-seasonal."""
        lg = LightingGenerator(epw_path=None)
        base = lg.generate(single_absence, DEFAULT_LIGHTS)
        monthly = lg.generate_monthly(single_absence, DEFAULT_LIGHTS, month="Jan")
        for h in range(24):
            assert abs(base[h] - monthly[h]) < 1e-9, (
                f"Hour {h}: base {base[h]:.4f} != monthly {monthly[h]:.4f}"
            )

    def test_no_negative_values(self, fractional):
        lg = LightingGenerator(epw_path=None)
        result = lg.generate(fractional, DEFAULT_LIGHTS)
        assert all(v >= 0.0 for v in result)


# ---------------------------------------------------------------------------
# Helpers for Task-15 tests
# ---------------------------------------------------------------------------

def _make_hh(weekday_profile, weekend_profile=None):
    """Build a minimal household dict as load_schedules() would produce."""
    if weekend_profile is None:
        weekend_profile = weekday_profile
    return {
        'metadata': {'hhsize': 2},
        'Weekday': [{'hour': h, 'occ': weekday_profile[h], 'met': 1.0} for h in range(24)],
        'Weekend': [{'hour': h, 'occ': weekend_profile[h], 'met': 1.0} for h in range(24)],
    }


from eSim_bem_utils.integration import (
    validate_household_schedule,
    find_archetype_household,
    ARCHETYPE_PROFILES,
)

# One realistic household per archetype
WORKER_HH    = _make_hh(ARCHETYPE_PROFILES['Worker'])
STUDENT_HH   = _make_hh(ARCHETYPE_PROFILES['Student'])
RETIREE_HH   = _make_hh(ARCHETYPE_PROFILES['Retiree'])
SHIFT_HH     = _make_hh(ARCHETYPE_PROFILES['ShiftWorker'])

# Illogical: all-zero weekday (nobody home ever)
ILLOGICAL_HH = _make_hh([0.0] * 24)


# ---------------------------------------------------------------------------
# validate_household_schedule tests (Task 15)
# ---------------------------------------------------------------------------

class TestValidateHouseholdSchedule:

    def test_worker_is_valid(self):
        assert validate_household_schedule(WORKER_HH) is True

    def test_student_is_valid(self):
        assert validate_household_schedule(STUDENT_HH) is True

    def test_retiree_is_valid(self):
        assert validate_household_schedule(RETIREE_HH) is True

    def test_shift_worker_is_valid(self):
        assert validate_household_schedule(SHIFT_HH) is True

    def test_all_zero_is_invalid(self):
        assert validate_household_schedule(ILLOGICAL_HH) is False

    def test_out_of_range_value_is_invalid(self):
        bad = _make_hh([1.5] + [1.0] * 23)
        assert validate_household_schedule(bad) is False

    def test_presence_hours_below_minimum_is_invalid(self):
        # Total presence = 1.0 — below the [2, 24] floor
        sparse = _make_hh([0.0] * 23 + [1.0])
        assert validate_household_schedule(sparse) is False

    def test_excessive_spike_pattern_is_invalid(self):
        # 6 isolated single-hour spikes surrounded by zeros
        spiky = [0.0] * 24
        for h in [1, 4, 7, 10, 14, 18]:
            spiky[h] = 1.0
        assert validate_household_schedule(_make_hh(spiky)) is False


# ---------------------------------------------------------------------------
# find_archetype_household tests (Task 15)
# ---------------------------------------------------------------------------

class TestFindArchetypeHousehold:

    def _make_schedules(self):
        return {
            'worker_hh':  WORKER_HH,
            'student_hh': STUDENT_HH,
            'retiree_hh': RETIREE_HH,
            'shift_hh':   SHIFT_HH,
        }

    def test_worker_archetype_returns_worker_hh(self):
        scheds = self._make_schedules()
        result = find_archetype_household(scheds, 'Worker')
        assert result == 'worker_hh'

    def test_retiree_archetype_returns_retiree_hh(self):
        scheds = self._make_schedules()
        result = find_archetype_household(scheds, 'Retiree')
        assert result == 'retiree_hh'

    def test_unknown_archetype_raises(self):
        scheds = self._make_schedules()
        with pytest.raises(ValueError):
            find_archetype_household(scheds, 'Unknown')

    def test_candidates_subset_respected(self):
        scheds = self._make_schedules()
        # Only offer student and shift worker; worker archetype should match student
        result = find_archetype_household(scheds, 'Worker', candidates=['student_hh', 'shift_hh'])
        assert result in ('student_hh', 'shift_hh')
