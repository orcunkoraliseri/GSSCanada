"""
WP10 Stage 4 patch: local seen-failing-first tests for Gate 4's manifest-driven
household selection and the random.choice guard, run BEFORE trusting Gate 4 on
real cluster data.

Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

Imports the ACTUAL patched eSim_bem_utils.main module (via a mirrored package dir
with only main.py swapped for the patched copy) so these are real tests of the
real patch code, not a reimplementation of it.

Run: py wp10_g4_selftest.py   (from this directory; expects ./testenv/eSim_bem_utils/
with a real eSim_bem_utils package plus the patched main.py inside it)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "testenv"))
import eSim_bem_utils.main as m  # noqa: E402

FAILURES = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Tiny synthetic fixture: 1 neighbourhood-ish stand-in, 2 buildings, 2 years.
# ---------------------------------------------------------------------------
NU = "NUS_TEST1"
YEARS = ["2005", "2010"]
N_BUILDINGS = 2

all_schedules = {
    "2005": {
        "HH_A": {"metadata": {"dtype": "SingleD", "hhsize": 2}, "occ": "a"},
        "HH_B": {"metadata": {"dtype": "MidRise", "hhsize": 3}, "occ": "b"},
    },
    "2010": {
        "HH_C": {"metadata": {"dtype": "SingleD", "hhsize": 2}, "occ": "c"},
        "HH_D": {"metadata": {"dtype": "MidRise", "hhsize": 3}, "occ": "d"},
    },
}

good_manifest = {
    (NU, 1, "2005", 0): "HH_A",
    (NU, 1, "2005", 1): "HH_B",
    (NU, 1, "2010", 0): "HH_C",
    (NU, 1, "2010", 1): "HH_D",
}

# --- Test 1: identical good case -> selection succeeds, right households, right shape.
result = m._wp10_select_households_for_draw(NU, 1, YEARS, all_schedules, N_BUILDINGS, good_manifest)
check(
    "T1 good manifest: both years present",
    set(result.keys()) == {"2005", "2010"},
    f"keys={list(result.keys())}",
)
check(
    "T1 good manifest: 2005 households in building_index order",
    [r["hh_id"] for r in result.get("2005", [])] == ["HH_A", "HH_B"],
    f"got={[r.get('hh_id') for r in result.get('2005', [])]}",
)
check(
    "T1 good manifest: 2010 households in building_index order",
    [r["hh_id"] for r in result.get("2010", [])] == ["HH_C", "HH_D"],
    f"got={[r.get('hh_id') for r in result.get('2010', [])]}",
)
check(
    "T1 good manifest: household metadata carried through (not just the id)",
    result["2005"][0].get("metadata", {}).get("dtype") == "SingleD",
)

# --- Test 2 (seen failing first, G4.0's failure mode): one row's household id
# changed to a value not equal to what a correct manifest would have given --
# selection must still succeed (it blindly trusts the manifest) but the row must
# visibly carry the WRONG id, which is exactly what G4.0 (comparing the echoed
# run against draw_manifest.csv) is built to catch downstream.
wrong_manifest = dict(good_manifest)
wrong_manifest[(NU, 1, "2005", 0)] = "HH_B"  # deliberately wrong: was HH_A
result_wrong = m._wp10_select_households_for_draw(NU, 1, YEARS, all_schedules, N_BUILDINGS, wrong_manifest)
check(
    "T2 wrong-manifest control: selection follows the manifest even when it disagrees "
    "with the correct draw (proves selection has no hidden fallback/ranking of its own)",
    result_wrong["2005"][0]["hh_id"] == "HH_B",
    f"got={result_wrong['2005'][0]['hh_id']}",
)

# --- Test 3 (seen failing first, missing row): a manifest missing one required
# (nu, draw, year, building_index) row must raise MANIFEST MISS, not silently fall
# back to any pool/ranking logic.
missing_row_manifest = dict(good_manifest)
del missing_row_manifest[(NU, 1, "2010", 1)]
try:
    m._wp10_select_households_for_draw(NU, 1, YEARS, all_schedules, N_BUILDINGS, missing_row_manifest)
    check("T3 missing manifest row raises MANIFEST MISS", False, "no exception raised")
except RuntimeError as e:
    check(
        "T3 missing manifest row raises MANIFEST MISS",
        "MANIFEST MISS" in str(e),
        f"message={e}",
    )

# --- Test 4 (seen failing first, household not in that year's schedules): manifest
# names a household id that this year's loaded schedules do not contain.
bad_hh_manifest = dict(good_manifest)
bad_hh_manifest[(NU, 1, "2010", 0)] = "HH_NOT_A_REAL_HOUSEHOLD"
try:
    m._wp10_select_households_for_draw(NU, 1, YEARS, all_schedules, N_BUILDINGS, bad_hh_manifest)
    check("T4 manifest household missing from schedules raises", False, "no exception raised")
except RuntimeError as e:
    check(
        "T4 manifest household missing from schedules raises",
        "MANIFEST HOUSEHOLD NOT IN SCHEDULES" in str(e),
        f"message={e}",
    )

# ---------------------------------------------------------------------------
# G4.1 guard mechanism: the exact install/restore pattern used inside
# _run_mc_neighbourhood, exercised standalone (the real nested function is not
# importable, so this reproduces it verbatim to prove the MECHANISM raises and
# restores correctly; the ABSENCE of any random.choice call site inside
# _run_mc_neighbourhood is checked separately below by source inspection).
# ---------------------------------------------------------------------------
import random as _random_mod

_orig_choice = _random_mod.choice


def _forbidden_choice(*_a, **_kw):
    raise RuntimeError("WP10 GUARD: random.choice() reached inside _run_mc_neighbourhood -- test")


# --- Test 5 (seen failing first, control: guard NOT installed -> random.choice works).
check(
    "T5 control: random.choice works normally before the guard is installed",
    _random_mod.choice([1]) == 1,
)

# --- Test 6: guard installed -> random.choice raises.
_random_mod.choice = _forbidden_choice
guard_raised = False
try:
    _random_mod.choice([1])
except RuntimeError as e:
    guard_raised = "WP10 GUARD" in str(e)
check("T6 guard installed: random.choice raises WP10 GUARD", guard_raised)

# --- Test 7: guard restored (finally-equivalent) -> random.choice works again.
_random_mod.choice = _orig_choice
check(
    "T7 guard restored: random.choice works normally again",
    _random_mod.choice([1]) == 1,
)

# ---------------------------------------------------------------------------
# G4.1 static check: the deployed _run_mc_neighbourhood source must contain the
# guard install/restore lines and must NOT contain any bare random.choice( call
# (i.e. every remaining "random.choice" text is inside the guard's own strings/
# names, never an actual call site left over from the old chooser).
# ---------------------------------------------------------------------------
import inspect

src = inspect.getsource(m._run_mc_neighbourhood)
check(
    "G4.1 static: guard install line present in _run_mc_neighbourhood",
    "random.choice = _wp10_forbidden_random_choice" in src,
)
check(
    "G4.1 static: guard restore line present in _run_mc_neighbourhood",
    "random.choice = _wp10_orig_random_choice" in src,
)
# Every remaining occurrence of "random.choice(" that is NOT a comment line and
# NOT the guard's own zero-arg "random.choice()" in its docstring/message text
# would be a real call site of the old chooser -- there must be none left.
_call_site_lines = [
    line for line in src.splitlines()
    if "random.choice(" in line
    and not line.strip().startswith("#")
    and "random.choice()" not in line  # guard's own text always says "choice()", zero-arg
]
check(
    "G4.1 static: zero real random.choice( call sites remain in _run_mc_neighbourhood",
    len(_call_site_lines) == 0,
    f"lines={_call_site_lines}",
)

print()
if FAILURES:
    print(f"SELFTEST SUMMARY: {len(FAILURES)} FAILED -- {FAILURES}")
    sys.exit(1)
else:
    print("SELFTEST SUMMARY: ALL PASS")
    sys.exit(0)
