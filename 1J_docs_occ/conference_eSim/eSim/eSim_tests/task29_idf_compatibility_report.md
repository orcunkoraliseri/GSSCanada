# Task 29 — IDF / Dwelling-Type Compatibility Check Report

**Date:** 2026-04-09  
**Purpose:** Verify that `validate_idf_compatibility()` correctly catches mode mismatches
(neighbourhood IDF used in single mode, or vice versa) and emits a soft warning on
dwelling-type filename mismatch.  Confirm it does not break any correct run.

---

## Implementation Notes

`validate_idf_compatibility()` was pre-existing in `integration.py:1023` with only a
SpaceList-based neighbourhood detector.  The actual neighbourhood IDFs in
`BEM_Setup/Neighbourhoods/` (e.g. `NUS_RC1.idf`) have **no** `Neighbourhood_*` SpaceList
objects — their structure is identified by zone count (96 zones vs 7 for single-building
Montreal IDF).  The implementation was updated at lines 1059-1076 to add:

```python
zone_count = len(_re.findall(r'^Zone,', raw, _re.MULTILINE))
has_neighbourhood_structure = neighbourhood_spacelists > 0 or zone_count > 20
```

**Threshold rationale:** `> 20` zones catches neighbourhood IDFs (96 zones) while giving
ample headroom for single-building models (max observed: 7 zones for Montreal 6A IDF).
No filename-specific exceptions added — the threshold is the only tuning knob.

The two wire-up lines were already present in `inject_schedules` (line 1255) and
`inject_neighbourhood_schedules` (line 1632) from a prior partial implementation.  No
changes to either function signature were needed.

---

## Step 3 — Test Harness Results

Test script: `eSim_tests/test_idf_compatibility.py`  
Output file: `eSim_tests/test_idf_compatibility_output.txt`

| # | Description | Expected | Result |
|---|---|---|---|
| 1 | Happy path: Montreal IDF, mode='single', dtype='SingleD' | No exception | **PASS** |
| 2 | Happy path: NUS_RC1.idf, mode='neighbourhood' | No exception | **PASS** |
| 3 | Mode mismatch: Montreal IDF in mode='neighbourhood' | ValueError | **PASS** |
| 4 | Mode mismatch: NUS_RC1.idf in mode='single' | ValueError | **PASS** |
| 5 | Dtype warning: Montreal + dtype='MidRise' | [Warning] printed | **PASS** |
| 6 | Dtype silent-pass: Montreal + dtype='SingleD' | No warning | **PASS** |

**Result: 6/6 PASS**

Detection mechanism verified:
- Montreal IDF: 7 zones (≤ 20) → single-building ✓
- NUS_RC1.idf: 96 zones (> 20) → neighbourhood ✓

---

## Step 4 — Regression Guard

Script: `eSim_tests/run_task29_regression_guard.py`  
Run: Option 3 Standard, Montreal 6A IDF, Quebec HH 4893, Method B monkey-patch.

| Metric | Value |
|---|---|
| Batch dir | `Comparative_HH1p_1775735913` |
| EPW auto-resolved | `CAN_QC_Montreal…716120_TMYx_6A.epw` |
| EnergyPlus runs | 6/6 successful |
| SQL files found | 6 |
| `validate_idf_compatibility` raised? | No |

**Result: PASS** — the validator correctly accepted the single-building Montreal IDF in
`inject_schedules()` (mode='single') and did not interfere with any simulation step.

---

## Verdict

`validate_idf_compatibility()` is working correctly.  The zone-count heuristic (> 20
zones = neighbourhood) cleanly separates the two IDF classes in this repo.  The dtype
check warns but never raises, as required.  No EUI values are affected by this change
(validator exits silently on correct inputs).
