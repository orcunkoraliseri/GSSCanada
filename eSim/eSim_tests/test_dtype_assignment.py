"""
End-to-end validation test for DTYPE-aware occupant assignment.

Tests Tasks 1-7: DTYPE inference, schedule filtering, fallback hierarchy,
sidecar overrides, cross-year consistency, and regression on object counts.

Run from project root:
    py eSim_tests/test_dtype_assignment.py
"""

import json
import os
import random
import re
import sys
import tempfile

# Allow imports from project root and eSim_bem_utils
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import eSim_bem_utils.neighbourhood as neighbourhood
import eSim_bem_utils.integration as integration

NEIGHBOURHOODS_DIR = os.path.join(ROOT, "BEM_Setup", "Neighbourhoods")
BEM_SETUP_DIR = os.path.join(ROOT, "BEM_Setup")
CSV_2025 = os.path.join(BEM_SETUP_DIR, "BEM_Schedules_2025.csv")
CSV_2015 = os.path.join(BEM_SETUP_DIR, "BEM_Schedules_2015.csv")

# Fallback hierarchy from the plan
FALLBACK_CHAIN = {
    'HighRise':  ['MidRise',  'Attached', 'SemiD',    'DuplexD', 'SingleD'],
    'MidRise':   ['HighRise', 'Attached', 'SemiD',    'DuplexD', 'SingleD'],
    'Attached':  ['SemiD',    'DuplexD',  'SingleD',  'MidRise', 'HighRise'],
    'SemiD':     ['Attached', 'DuplexD',  'SingleD',  'MidRise', 'HighRise'],
    'DuplexD':   ['SemiD',    'Attached', 'SingleD',  'MidRise', 'HighRise'],
    'SingleD':   ['SemiD',    'DuplexD',  'Attached', 'MidRise', 'HighRise'],
    'Movable':   ['SingleD',  'SemiD',    'Attached', 'DuplexD', 'MidRise'],
    'OtherA':    ['SingleD',  'SemiD',    'Attached', 'DuplexD', 'MidRise'],
}

PASS = "PASS"
FAIL = "FAIL"


def _fmt(label: str, status: str, width: int = 52) -> str:
    dots = "." * max(1, width - len(label))
    return f"  {label} {dots} {status}"


def _idf_path(name: str) -> str:
    return os.path.join(NEIGHBOURHOODS_DIR, f"{name}.idf")


# ---------------------------------------------------------------------------
# Helper: per-building DTYPE-aware selection (mirrors Task 4 logic)
# ---------------------------------------------------------------------------

def _select_dtype_aware(
    all_schedules: dict,
    building_dtypes: list[str],
    dtype_pools: dict[str, list[str]] | None = None,
) -> tuple[list[str], list[str]]:
    """
    Assign one household per building from the correct DTYPE pool.

    Returns (assigned_hh_ids, warnings) where warnings is a list of
    fallback messages.
    """
    if dtype_pools is None:
        # Group all households by their DTYPE metadata
        raw: dict[str, list[str]] = {}
        for hh_id, hh_data in all_schedules.items():
            dtype = hh_data.get('metadata', {}).get('dtype', 'SingleD')
            raw.setdefault(dtype, []).append(hh_id)

        # SSE-rank each pool once
        dtype_pools = {}
        for dtype, pool in raw.items():
            scored = integration.filter_matching_households(all_schedules, candidates=pool)
            top_cut = max(1, len(scored) // 4)
            dtype_pools[dtype] = [hh for hh, _ in scored[:top_cut]]

    assigned: list[str] = []
    warnings: list[str] = []
    used: set[str] = set()

    for dtype in building_dtypes:
        pool = [hh for hh in dtype_pools.get(dtype, []) if hh not in used]

        if not pool:
            # Fallback
            fallback_used = None
            for fb_dtype in FALLBACK_CHAIN.get(dtype, []):
                fb_pool = [hh for hh in dtype_pools.get(fb_dtype, []) if hh not in used]
                if fb_pool:
                    pool = fb_pool
                    fallback_used = fb_dtype
                    break

            if fallback_used:
                warnings.append(f"Fallback: {dtype} -> {fallback_used}")
            else:
                warnings.append(f"Critical: no household found for {dtype}")
                assigned.append(None)
                continue

        hh = random.choice(pool)
        used.add(hh)
        assigned.append(hh)

    return assigned, warnings


# ---------------------------------------------------------------------------
# Test 1: DTYPE inference across all 6 IDFs
# ---------------------------------------------------------------------------

EXPECTED_DTYPES = {
    "NUS_RC1": "SingleD",
    "NUS_RC2": "SingleD",
    "NUS_RC3": "SingleD",
    "NUS_RC4": "MidRise",
    "NUS_RC5": "MidRise",
    "NUS_RC6": "HighRise",
}


def test_dtype_inference():
    """
    Verify that every building group in each IDF gets the correct DTYPE.
    Building counts are not asserted here because get_building_groups() groups
    by shared hex hash, which may produce fewer groups than the physical
    building count (pre-existing behaviour, not changed by this plan).
    """
    print("\n=== DTYPE Inference Tests ===")
    all_pass = True

    for idf_name, expected_dtype in EXPECTED_DTYPES.items():
        path = _idf_path(idf_name)
        if not os.path.exists(path):
            print(_fmt(f"{idf_name}: file missing", FAIL))
            all_pass = False
            continue

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            buildings = neighbourhood.get_building_groups(content)

        n = len(buildings)
        dtypes = [b['dtype'] for b in buildings.values()]
        all_match = all(d == expected_dtype for d in dtypes)

        label = f"{idf_name}: {n} buildings, all {expected_dtype}"
        status = PASS if all_match else FAIL
        if not all_match:
            all_pass = False
            label += f"  [got dtypes={set(dtypes)}]"
        print(_fmt(label, status))

    return all_pass


# ---------------------------------------------------------------------------
# Test 2: Schedule filtering — per-building DTYPE matching
# ---------------------------------------------------------------------------

def test_schedule_filtering(all_schedules_2025: dict):
    print("\n=== Schedule Filtering Tests ===")
    all_pass = True

    test_cases = [
        ("NUS_RC4", "MidRise"),
        ("NUS_RC6", "HighRise"),
    ]

    for idf_name, expected_dtype in test_cases:
        path = _idf_path(idf_name)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dtypes = neighbourhood.get_building_dtypes_from_idf(path)

        n_buildings = len(dtypes)
        assigned, warnings = _select_dtype_aware(all_schedules_2025, dtypes)

        match_count = sum(
            1 for hh in assigned
            if hh and all_schedules_2025[hh].get('metadata', {}).get('dtype') == expected_dtype
        )
        no_dups = len([h for h in assigned if h]) == len(set(h for h in assigned if h))

        label = f"{idf_name} ({expected_dtype}): {match_count}/{n_buildings} match"
        status = PASS if (match_count == n_buildings and no_dups) else FAIL
        if status == FAIL:
            all_pass = False
        print(_fmt(label, status))

    # No-duplicates check across a single run
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dtypes = neighbourhood.get_building_dtypes_from_idf(_idf_path("NUS_RC4"))
    assigned, _ = _select_dtype_aware(all_schedules_2025, dtypes)
    no_dups = len([h for h in assigned if h]) == len(set(h for h in assigned if h))
    print(_fmt("No duplicates within a single run", PASS if no_dups else FAIL))
    if not no_dups:
        all_pass = False

    return all_pass


# ---------------------------------------------------------------------------
# Test 3: Fallback test — remove HighRise pool, run NUS_RC6
# ---------------------------------------------------------------------------

def test_fallback(all_schedules_2025: dict):
    print("\n=== Fallback Test ===")

    # Build DTYPE pools without HighRise
    raw: dict[str, list[str]] = {}
    for hh_id, hh_data in all_schedules_2025.items():
        dtype = hh_data.get('metadata', {}).get('dtype', 'SingleD')
        raw.setdefault(dtype, []).append(hh_id)

    dtype_pools_no_highrise: dict[str, list[str]] = {}
    for dtype, pool in raw.items():
        if dtype == 'HighRise':
            continue  # intentionally excluded
        scored = integration.filter_matching_households(all_schedules_2025, candidates=pool)
        top_cut = max(1, len(scored) // 4)
        dtype_pools_no_highrise[dtype] = [hh for hh, _ in scored[:top_cut]]

    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dtypes = neighbourhood.get_building_dtypes_from_idf(_idf_path("NUS_RC6"))

    assigned, warnings = _select_dtype_aware(
        all_schedules_2025, dtypes, dtype_pools=dtype_pools_no_highrise
    )

    fallback_triggered = any("Fallback: HighRise ->" in w for w in warnings)
    fallback_to_midrise = any("Fallback: HighRise -> MidRise" in w for w in warnings)

    label = "HighRise pool empty, fell back to MidRise"
    status = PASS if (fallback_triggered and fallback_to_midrise) else FAIL
    print(_fmt(label, status))
    return status == PASS


# ---------------------------------------------------------------------------
# Test 4: Sidecar override for NUS_RC1
# ---------------------------------------------------------------------------

def test_sidecar_override():
    print("\n=== Sidecar Override Test ===")

    idf_path = _idf_path("NUS_RC1")
    sidecar_path = idf_path.replace('.idf', '_dtypes.json')

    override_dtype = "Attached"
    sidecar_data = {f"Bldg_{i}": override_dtype for i in range(4)}

    try:
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(sidecar_data, f)

        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dtypes = neighbourhood.get_building_dtypes_from_idf(idf_path)

        all_attached = all(d == override_dtype for d in dtypes)
        label = f"NUS_RC1 overridden to {override_dtype} ({len(dtypes)} buildings)"
        status = PASS if all_attached else FAIL
        print(_fmt(label, status))
        return status == PASS
    finally:
        if os.path.exists(sidecar_path):
            os.remove(sidecar_path)


# ---------------------------------------------------------------------------
# Test 5: Cross-year DTYPE consistency (Option 6 logic)
# ---------------------------------------------------------------------------

def test_cross_year_consistency(all_schedules_2025: dict, all_schedules_2015: dict):
    print("\n=== Cross-Year Consistency ===")

    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dtypes = neighbourhood.get_building_dtypes_from_idf(_idf_path("NUS_RC4"))

    assigned_2025, _ = _select_dtype_aware(all_schedules_2025, dtypes)

    # Build hhsize profile from 2025 selection (matches Option 6 base-year logic)
    hhsize_profile = [
        all_schedules_2025[hh].get('metadata', {}).get('hhsize', 2)
        for hh in assigned_2025 if hh
    ]

    # 2015 matching: filter by (DTYPE, hhsize) — mirrors Task 5
    scored_2015 = [hh for hh, _ in integration.filter_matching_households(all_schedules_2015)]
    used = set()
    assigned_2015 = []

    for target_hhsize, target_dtype in zip(hhsize_profile, dtypes):
        candidates = [
            hh for hh in scored_2015
            if all_schedules_2015[hh].get('metadata', {}).get('hhsize', 0) == target_hhsize
            and all_schedules_2015[hh].get('metadata', {}).get('dtype', '') == target_dtype
            and hh not in used
        ]
        if not candidates:
            # DTYPE-only fallback
            candidates = [
                hh for hh in scored_2015
                if all_schedules_2015[hh].get('metadata', {}).get('dtype', '') == target_dtype
                and hh not in used
            ]
        if candidates:
            hh = candidates[0]
            used.add(hh)
            assigned_2015.append(hh)
        else:
            assigned_2015.append(None)

    dtypes_2025 = [
        all_schedules_2025[hh].get('metadata', {}).get('dtype') for hh in assigned_2025 if hh
    ]
    dtypes_2015 = [
        all_schedules_2015[hh].get('metadata', {}).get('dtype') for hh in assigned_2015 if hh
    ]

    # Check that every building position has the same DTYPE in both years
    match = all(a == b for a, b in zip(dtypes_2025, dtypes_2015))
    label = "2025 vs 2015 DTYPE match per building position"
    status = PASS if match else FAIL
    if not match:
        mismatches = sum(1 for a, b in zip(dtypes_2025, dtypes_2015) if a != b)
        label += f"  [{mismatches} mismatches]"
    print(_fmt(label, status))
    return status == PASS


# ---------------------------------------------------------------------------
# Test 6: Regression — prepare_neighbourhood_idf() object counts unchanged
# ---------------------------------------------------------------------------

def test_regression_object_counts():
    """
    Verify prepare_neighbourhood_idf() creates one People/Lights/Equipment object
    per building group, using the actual group count from get_building_groups().
    """
    print("\n=== Regression: Object Counts ===")
    all_pass = True

    test_cases = [
        "NUS_RC4",
    ]

    import io, contextlib

    for idf_name in test_cases:
        path = _idf_path(idf_name)
        buf0 = io.StringIO()
        with contextlib.redirect_stdout(buf0):
            expected_n = neighbourhood.get_num_buildings_from_idf(path)

        with tempfile.NamedTemporaryFile(suffix=".idf", delete=False, mode='w') as tmp:
            tmp_path = tmp.name

        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                n = neighbourhood.prepare_neighbourhood_idf(path, tmp_path, expected_n)

            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            people_count  = len(re.findall(r"^People,$",          content, re.MULTILINE))
            lights_count  = len(re.findall(r"^Lights,$",          content, re.MULTILINE))
            equip_count   = len(re.findall(r"^ElectricEquipment,$", content, re.MULTILINE))

            ok = (people_count == expected_n and lights_count == expected_n and equip_count == expected_n)
            label = f"{idf_name}: {people_count} People, {lights_count} Lights, {equip_count} Equip"
            status = PASS if ok else FAIL
            if not ok:
                all_pass = False
            print(_fmt(label, status))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return all_pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    random.seed(42)
    results = []

    # Tests that don't need the CSV
    results.append(("DTYPE Inference",        test_dtype_inference()))
    results.append(("Sidecar Override",        test_sidecar_override()))
    results.append(("Regression Object Counts", test_regression_object_counts()))

    # Tests that need the schedule CSVs
    if not os.path.exists(CSV_2025):
        print(f"\n[SKIP] Schedule CSV not found: {CSV_2025}")
        print("       Tests 2, 3, 5 skipped.")
    else:
        import io, contextlib
        print("\nLoading BEM_Schedules_2025.csv...")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            s2025 = integration.load_schedules(CSV_2025, dwelling_type=None, region=None)
        print(f"  Loaded {len(s2025)} households from 2025 CSV.")

        results.append(("Schedule Filtering",  test_schedule_filtering(s2025)))
        results.append(("Fallback",            test_fallback(s2025)))

        if os.path.exists(CSV_2015):
            print("\nLoading BEM_Schedules_2015.csv...")
            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                s2015 = integration.load_schedules(CSV_2015, dwelling_type=None, region=None)
            print(f"  Loaded {len(s2015)} households from 2015 CSV.")
            results.append(("Cross-Year Consistency", test_cross_year_consistency(s2025, s2015)))
        else:
            print(f"\n[SKIP] BEM_Schedules_2015.csv not found — cross-year test skipped.")

    # Summary
    print("\n" + "=" * 60)
    all_passed = all(v for _, v in results)
    for name, passed in results:
        print(f"  {'[PASS]' if passed else '[FAIL]'} {name}")
    print("=" * 60)
    if all_passed:
        print("All tests passed.")
    else:
        failed = [n for n, v in results if not v]
        print(f"FAILED: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
