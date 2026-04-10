# Building-Type-Aware Occupant Assignment for Neighbourhood Simulations

## Goal

Modify Options 5, 6, and 7 so that each building in a neighbourhood IDF receives occupancy schedules drawn from the **correct dwelling type** (DTYPE), rather than pooling all dwelling types together as is done today.

---

## Current Behaviour (the problem)

| Aspect | Single-building (Options 2-4) | Neighbourhood (Options 5-7) |
|--------|-------------------------------|----------------------------|
| Dwelling type filter | User selects one DTYPE (e.g. `MidRise`) | Hard-coded to `None` (all DTYPEs pooled) |
| Schedule selection | Filtered to matching DTYPE before SSE ranking | SSE ranking across all DTYPEs indiscriminately |
| Building identity | N/A (one building) | `Bldg_0`, `Bldg_1`, ... — no type metadata |

**Consequence:** A MidRise apartment building in the neighbourhood can receive a schedule originally generated for a single-detached household, and vice versa.

---

## Evidence from Existing Neighbourhood IDFs

Zone names inside each IDF carry clear building-type signals:

| IDF | Buildings | Zone name pattern | Implied DTYPE |
|-----|-----------|-------------------|---------------|
| NUS_RC1 | 4 | `000_living_unit1_2_a25d9605`, `000_Room_23_f2d32505` | Low-rise residential (SingleD / SemiD / Attached) |
| NUS_RC2 | 4 | `-019.60_living_unit1_1_a8a609ec`, `-019.60_Room_24_e2b9dc3f` | Low-rise residential |
| NUS_RC3 | 28 | `..._living_unit1_14_7c0cd45e`, `..._Room_30_0ae27f69` | Low-rise residential (rowhouse/attached) |
| NUS_RC4 | 36 | `Midrise_Apartment0_Apartment_0_2f180702` | MidRise |
| NUS_RC5 | 36 | `0_Apartment_0_2d56054e` | MidRise (ambiguous, no prefix) |
| NUS_RC6 | 90 | `highRiseApartment0__F2_N1_Apartment_38e6badf` | HighRise |

The hex hash at the end of each zone name is the grouping key (already used by `neighbourhood.get_building_groups()`). The **text before the hash** encodes the building archetype, but `neighbourhood.py` currently ignores it.

---

## DTYPE Values Available in Schedule CSVs

The `BEM_Schedules_*.csv` files contain a `DTYPE` column with these values and approximate counts (from 2025 CSV):

| DTYPE | Households | Notes |
|-------|-----------|-------|
| SingleD | 13,402 | Large pool, always available |
| MidRise | 4,864 | |
| HighRise | 2,516 | |
| Attached | 1,111 | |
| DuplexD | 864 | |
| SemiD | 823 | |
| Movable | 232 | Small pool, fallback may be needed |
| OtherA | 70 | Very small pool |

---

## Implementation Plan

### Task 1: Add `infer_building_dtype()` to `neighbourhood.py`

- **Aim:** Parse zone names for each building group and return a DTYPE string per building.
- **What to do:** Add a new function `infer_building_dtype(zones: list[str]) -> str` that examines the representative zone names for a building group and returns one of the 8 DTYPE values.
- **How to do it:**
  1. Take the list of zone names belonging to one building (already available from `get_building_groups()`).
  2. Check zone names against keyword patterns (case-insensitive):
     - `highRiseApartment` or `HighRise` -> `'HighRise'`
     - `Midrise_Apartment` or `midrise` -> `'MidRise'`
     - `Apartment` (without highrise/midrise prefix) -> `'MidRise'` (conservative default for ambiguous apartment labels like NUS_RC5)
     - `living_unit` or `Room_` (the low-rise residential pattern in RC1/RC2/RC3) -> `'SingleD'` (default low-rise; could be refined later with a sidecar file)
     - `Corridor` or `Office` only (non-residential zones that appear alongside apartment zones) -> inherit the type from sibling zones in the same building group
  3. If no pattern matches, return `'SingleD'` as a safe default (largest pool).
- **Why:** This is the core detection logic. Zone names are the only building-type signal available in the IDF.
- **Impact:** `neighbourhood.py` only — no changes to other files yet.
- **Steps:**
  1. Write `infer_building_dtype(zones)` function.
  2. Write a helper `_infer_dtype_from_zone_name(zone_name: str) -> str | None` with the keyword rules above.
  3. For a building group, apply the helper to all zone names; the most common non-None result wins (majority vote).
- **Expected result:** Calling `infer_building_dtype(['Midrise_Apartment0_Apartment_0_2f180702', 'Midrise_Apartment0_Corridor_2_07bc34ae'])` returns `'MidRise'`.
- **How to test:** Run against all 6 NUS_RC IDFs and print the inferred DTYPE per building. Verify manually against the zone names above.

---

### Task 2: Extend `get_building_groups()` to return DTYPE metadata

- **Aim:** Make the DTYPE available to callers alongside the existing space-name lists.
- **What to do:** Change the return value of `get_building_groups()` from `dict[str, list[str]]` to `dict[str, dict]`, where each value is `{'spaces': [...], 'dtype': 'MidRise'}`.
- **How to do it:**
  1. After grouping spaces by hex hash (existing logic), call `infer_building_dtype()` for each group.
  2. Store the result alongside the space list.
  3. Update the print summary to show DTYPE counts (e.g., `"Grouped into 36 buildings: 33 MidRise, 3 Corridor"`).
- **Why:** Downstream code (main.py, integration.py) needs the DTYPE per building to filter schedule selection.
- **Impact:** Every caller of `get_building_groups()` must be updated to use the new dict structure. Callers:
  - `neighbourhood.prepare_neighbourhood_idf()` — accesses `buildings[bldg_id]` as a space list -> change to `buildings[bldg_id]['spaces']`
  - `neighbourhood.get_water_equipment_building_map()` — same pattern
  - `neighbourhood.get_num_buildings_from_idf()` — just counts keys, no change needed
- **Steps:**
  1. Modify `get_building_groups()`.
  2. Update `prepare_neighbourhood_idf()` to use `bldg_data['spaces']` instead of raw list.
  3. Update `get_water_equipment_building_map()` similarly.
  4. Update the print statements.
- **Expected result:** `get_building_groups(content)` returns `{'Bldg_0': {'spaces': [...], 'dtype': 'MidRise'}, ...}`.
- **How to test:** Run `get_building_groups()` on each NUS_RC IDF. Confirm space counts are unchanged and DTYPEs look correct.

---

### Task 3: Propagate building DTYPE from `neighbourhood.py` to `main.py`

- **Aim:** Make the per-building DTYPE list available in Options 5, 6, 7 so it can be used for schedule filtering.
- **What to do:** Add a new function `get_building_dtypes_from_idf(idf_path: str) -> list[str]` to `neighbourhood.py` that returns an ordered list of DTYPEs, one per building (indexed same as `Bldg_0`, `Bldg_1`, ...).
- **How to do it:**
  1. Read the IDF, call `get_building_groups()`, extract the `'dtype'` from each group.
  2. Return as `['MidRise', 'MidRise', 'HighRise', ...]` in `Bldg_0..N` order.
- **Why:** `main.py` needs a simple list to pass into the household selection logic. This keeps the interface clean.
- **Impact:** `neighbourhood.py` only.
- **Steps:**
  1. Implement the function (thin wrapper around `get_building_groups()`).
  2. Print a summary: `"Building types: 33 MidRise, 3 Corridor(->MidRise)"`.
- **Expected result:** Returns `['MidRise'] * 36` for NUS_RC4.
- **How to test:** Call on all 6 IDF files.

---

### Task 4: Modify schedule selection in Option 5 (`option_neighbourhood_simulation`)

- **Aim:** Filter households by DTYPE per building when assigning schedules.
- **What to do:** Replace the current "pool all, rank by SSE, random sample" logic with per-building type-aware selection.
- **How to do it:**
  1. After detecting buildings, call `neighbourhood.get_building_dtypes_from_idf()` to get the DTYPE list.
  2. Load schedules **without** DTYPE filter (as today — `dwelling_type=None`) so all households are available.
  3. Pre-group loaded households by their `metadata['dtype']` value into a dict: `{'SingleD': [hh1, hh2, ...], 'MidRise': [...], ...}`.
  4. For each building `i`, pick from the pool matching `building_dtypes[i]`:
     - Filter that pool through `filter_matching_households()` for SSE ranking.
     - Sample from the top quarter (same logic as current `top_cut`).
     - If the matching pool is too small (fewer than needed), fall back to the closest DTYPE using a fallback hierarchy:
       - `HighRise` -> `MidRise` -> `Attached` -> `SemiD` -> `DuplexD` -> `SingleD`
       - (i.e., apartment types fall back to other apartment types first, then low-rise)
     - Print a warning when falling back.
  5. Continue with the rest of the existing flow (EPW auto-selection, IDF preparation, injection).
- **Why:** This is where the actual behaviour change happens for Option 5. Household selection becomes type-aware.
- **Impact:** `main.py:option_neighbourhood_simulation()` (lines ~952-1081).
- **Steps:**
  1. Add DTYPE detection call after `n_buildings` detection.
  2. After loading `all_schedules`, group by DTYPE.
  3. Replace the flat `filter_matching_households()` + `random.sample()` block with per-building typed selection loop.
  4. Add summary print: `"Assigned: 24 SingleD, 6 MidRise, 6 HighRise schedules"`.
- **Expected result:** Running Option 5 on NUS_RC4 assigns only MidRise households. Running on NUS_RC6 assigns only HighRise households.
- **How to test:**
  1. Run Option 5 on NUS_RC4 and check that all assigned households have `metadata['dtype'] == 'MidRise'`.
  2. Run on NUS_RC1 and check that assigned households are low-rise types.
  3. Check fallback by temporarily filtering to a DTYPE with very few households.

---

### Task 5: Modify schedule selection in Option 6 (`option_comparative_neighbourhood_simulation`)

- **Aim:** Same type-aware selection, but applied per-year with hhsize consistency across years.
- **What to do:** Extend the existing hhsize-matching logic to also enforce DTYPE matching.
- **How to do it:**
  1. Detect building DTYPEs (same as Task 4).
  2. For the base year: select households matching each building's DTYPE, then SSE-rank within that filtered set. Record both `hhsize_profile` and `dtype_profile`.
  3. For subsequent years: match by *both* DTYPE and hhsize (existing `hhsize_profile` loop at `main.py:1237`). The current code searches for `target_hhsize` — extend the filter to also require matching DTYPE:
     ```python
     size_candidates = [
         hh for hh in sorted_year_hhs
         if year_schedules[hh].get('metadata', {}).get('hhsize', 0) == target_hhsize
         and year_schedules[hh].get('metadata', {}).get('dtype', '') == target_dtype
         and hh not in used_hhs
     ]
     ```
  4. Fallback chain (same as Task 4) if exact DTYPE match not available in a given year.
- **Why:** Cross-year comparison should hold building type constant so differences reflect temporal occupancy changes, not DTYPE mixing.
- **Impact:** `main.py:option_comparative_neighbourhood_simulation()` (lines ~1108-1290).
- **Steps:**
  1. Add DTYPE detection after building count.
  2. Modify base-year selection loop to be DTYPE-aware.
  3. Modify per-year matching loop to filter by (DTYPE, hhsize).
  4. Keep existing SSE matching within the filtered set.
  5. Add per-scenario summary of DTYPE assignments.
- **Expected result:** All 6 scenarios for a given building assign the same DTYPE; only the year's occupancy patterns differ.
- **How to test:** Run Option 6 on NUS_RC4. Verify all scenarios use MidRise households. Check the exported schedule CSVs to confirm.

---

### Task 6: Modify schedule selection in Option 7 (`option_batch_comparative_neighbourhood_simulation`)

- **Aim:** Same type-aware selection for the Monte Carlo loop.
- **What to do:** Apply the same DTYPE-aware selection as Task 5, but within the iteration loop.
- **How to do it:**
  1. Detect building DTYPEs once (before the iteration loop).
  2. Pre-group candidate pools by DTYPE (once, before iterating — same as current `sorted_year_hhs_cache`).
  3. Inside the iteration loop (`main.py:2010`), modify base-year sampling to respect building DTYPEs:
     - Currently: `random.sample(candidate_pool, n_buildings)` — flat sample from all types.
     - New: for each building position, sample from the DTYPE-matched sub-pool.
  4. Modify per-scenario matching (inner loop at `main.py:2054`) to filter by DTYPE + hhsize (same pattern as Task 5).
- **Why:** Monte Carlo averaging should not blur the signal by mixing dwelling types across iterations.
- **Impact:** `main.py:option_batch_comparative_neighbourhood_simulation()` (lines ~1839-2090).
- **Steps:**
  1. Add DTYPE detection.
  2. Pre-compute per-DTYPE candidate pools (alongside existing `sorted_year_hhs_cache`).
  3. Modify `random.sample` block to sample per-DTYPE.
  4. Modify inner matching loop for DTYPE + hhsize.
  5. Print DTYPE summary per iteration.
- **Expected result:** Each iteration respects building types. Averaging across iterations reflects only stochastic variation within the correct DTYPE pool.
- **How to test:** Run Option 7 with N=2 on NUS_RC4. Inspect exported schedules across both iterations to confirm all households are MidRise.

---

### Task 7: Add a sidecar override mechanism (optional, low priority)

- **Aim:** Allow manual DTYPE assignment when zone-name inference is ambiguous or incorrect.
- **What to do:** Support an optional JSON sidecar file alongside the IDF.
- **How to do it:**
  1. For `NUS_RC1.idf`, check for `NUS_RC1_dtypes.json` in the same directory.
  2. Expected format:
     ```json
     {
       "Bldg_0": "SemiD",
       "Bldg_1": "SemiD",
       "Bldg_2": "Attached",
       "Bldg_3": "Attached"
     }
     ```
  3. If the sidecar exists, use it; otherwise fall back to zone-name inference (Tasks 1-3).
  4. Print: `"Building types: loaded from NUS_RC1_dtypes.json"` or `"Building types: inferred from zone names"`.
- **Why:** Zone-name inference is heuristic. Some IDFs (especially RC1/RC2/RC3 with generic `living_unit` / `Room` names) may not map cleanly to a single DTYPE. A sidecar gives full control.
- **Impact:** `neighbourhood.py` (new function `load_dtype_overrides()`), called from `get_building_dtypes_from_idf()`.
- **Steps:**
  1. Implement `load_dtype_overrides(idf_path)`.
  2. Integrate into `get_building_dtypes_from_idf()` with fallback to inference.
  3. Document the sidecar format.
- **Expected result:** Placing a `_dtypes.json` file overrides automatic inference.
- **How to test:** Create a sidecar for NUS_RC1, run Option 5, verify the overrides are applied.

---

### Task 8: End-to-end validation test script

- **Aim:** Verify the entire DTYPE-aware assignment pipeline works correctly across all 6 neighbourhood IDFs without running EnergyPlus simulations.
- **What to do:** Write a standalone test script `eSim_tests/test_dtype_assignment.py` that exercises Tasks 1-6 in a dry-run mode.
- **How to do it:**
  1. **DTYPE inference test:** For each of the 6 NUS_RC IDFs, call `get_building_groups()` and verify the inferred DTYPEs match expected values:
     - NUS_RC1: all 4 buildings -> `SingleD` (low-rise)
     - NUS_RC2: all 4 buildings -> `SingleD` (low-rise)
     - NUS_RC3: all 28 buildings -> `SingleD` (low-rise)
     - NUS_RC4: all 36 buildings -> `MidRise`
     - NUS_RC5: all 36 buildings -> `MidRise`
     - NUS_RC6: all 90 buildings -> `HighRise`
  2. **Schedule filtering test:** Load `BEM_Schedules_2025.csv` with `dwelling_type=None`. Group by DTYPE. For each IDF, simulate the per-building selection loop (Task 4 logic) and assert:
     - Every assigned household's `metadata['dtype']` matches the building's inferred DTYPE.
     - No household is assigned twice within a single run.
     - The total number of assigned households equals `n_buildings`.
  3. **Fallback test:** Temporarily restrict the schedule pool to force fallback (e.g., remove all `HighRise` households from the loaded dict). Run selection for NUS_RC6. Assert:
     - Fallback triggers and assigns `MidRise` households (next in hierarchy).
     - A warning is printed.
  4. **Sidecar override test:** Create a temporary `_dtypes.json` for NUS_RC1 that overrides all buildings to `Attached`. Run `get_building_dtypes_from_idf()`. Assert all buildings return `Attached`. Delete the temp file after test.
  5. **Cross-year consistency test (Option 6 logic):** Run the hhsize+DTYPE matching loop for 2 years (e.g., 2025 and 2015). Assert that every building position gets the same DTYPE in both years.
  6. **Regression check:** Verify that `prepare_neighbourhood_idf()` still produces the correct number of People/Lights/Equipment objects (unchanged from before — the return type of `get_building_groups()` changed but the downstream object count must not).
- **Why:** Running actual EnergyPlus simulations takes minutes per scenario. This script validates the assignment logic in seconds and can be re-run after any refactor.
- **Impact:** New file `eSim_tests/test_dtype_assignment.py`. No changes to production code.
- **Steps:**
  1. Write the test script with clear pass/fail assertions and printed summaries.
  2. Run it once to establish baseline.
  3. Run it again after each of Tasks 1-7 to catch regressions.
- **Expected result:** All assertions pass. Output looks like:
  ```
  === DTYPE Inference Tests ===
  NUS_RC1: 4 buildings, all SingleD ........... PASS
  NUS_RC2: 4 buildings, all SingleD ........... PASS
  NUS_RC3: 28 buildings, all SingleD .......... PASS
  NUS_RC4: 36 buildings, all MidRise .......... PASS
  NUS_RC5: 36 buildings, all MidRise .......... PASS
  NUS_RC6: 90 buildings, all HighRise ......... PASS

  === Schedule Filtering Tests ===
  NUS_RC4 (MidRise): 36/36 households match ... PASS
  NUS_RC6 (HighRise): 90/90 households match .. PASS
  No duplicates ................................ PASS

  === Fallback Test ===
  HighRise pool empty, fell back to MidRise ... PASS

  === Sidecar Override Test ===
  NUS_RC1 overridden to Attached .............. PASS

  === Cross-Year Consistency ===
  2025 vs 2015 DTYPE match .................... PASS

  === Regression: Object Counts ===
  NUS_RC4: 36 People, 36 Lights, 36 Equip .... PASS

  All tests passed.
  ```
- **How to test:** `py eSim_tests/test_dtype_assignment.py` from the project root.

---

## Files Modified

| File | Changes |
|------|---------|
| `eSim_bem_utils/neighbourhood.py` | Tasks 1, 2, 3, 7: Add `infer_building_dtype()`, modify `get_building_groups()` return type, add `get_building_dtypes_from_idf()`, add sidecar loader |
| `eSim_bem_utils/main.py` | Tasks 4, 5, 6: Modify `option_neighbourhood_simulation()`, `option_comparative_neighbourhood_simulation()`, `option_batch_comparative_neighbourhood_simulation()` |
| `eSim_tests/test_dtype_assignment.py` | Task 8: New file — end-to-end validation test script |

**No changes to `integration.py`** — the injection logic is already per-building and DTYPE-agnostic. The fix is entirely in *which household gets assigned to which building*, not in *how schedules are written into the IDF*.

---

## Fallback Hierarchy

When a building's inferred DTYPE has too few households in the schedule pool, fall back in this order:

```
HighRise  ->  MidRise  ->  Attached  ->  SemiD  ->  DuplexD  ->  SingleD
MidRise   ->  HighRise ->  Attached  ->  SemiD  ->  DuplexD  ->  SingleD
Attached  ->  SemiD    ->  DuplexD   ->  SingleD ->  MidRise  ->  HighRise
SemiD     ->  Attached ->  DuplexD   ->  SingleD ->  MidRise  ->  HighRise
DuplexD   ->  SemiD    ->  Attached  ->  SingleD ->  MidRise  ->  HighRise
SingleD   ->  SemiD    ->  DuplexD   ->  Attached ->  MidRise ->  HighRise
Movable   ->  SingleD  ->  SemiD     ->  Attached ->  DuplexD ->  MidRise
OtherA    ->  SingleD  ->  (same as Movable)
```

Rationale: apartment types fall back to other apartment types first; low-rise types fall back to other low-rise types first.

---

## Risk / Edge Cases

1. **Ambiguous zone names (NUS_RC5):** Zone names like `0_Apartment_0_2d56054e` lack explicit `Midrise`/`HighRise` prefix. The inference defaults to `MidRise` based on zone count heuristics (12 zones/building, typical of midrise). The sidecar override (Task 7) provides a manual escape hatch.

2. **Mixed-type neighbourhoods:** Some future IDFs may contain both MidRise and SingleD buildings. The per-building approach handles this naturally because each building is typed independently.

3. **Small DTYPE pools:** For `Movable` (232 HH) and `OtherA` (70 HH), the pool may be too small for Monte Carlo sampling diversity. The fallback hierarchy prevents simulation failures.

4. **Non-residential zones:** Some buildings contain `Corridor` or `Office` zones (e.g., ground-floor commercial in NUS_RC4/RC6). These are grouped with the same hex hash as their residential neighbours, so they inherit the building's residential DTYPE. No separate handling needed since EnergyPlus applies the residential schedule to the entire SpaceList.

---

## Execution Order

Tasks 1-3 first (infrastructure in `neighbourhood.py`), then Tasks 4-6 (Options 5/6/7 in `main.py`), then Task 7 (optional sidecar).

Tasks 4, 5, 6 can be implemented independently of each other once Tasks 1-3 are done.

Task 8 should be written early (after Task 3) and run after every subsequent task to catch regressions.

---

## Progress Log

Record a short report for each completed task here. Include: what was done, what files were changed, any deviations from the plan, and test results.

### Task 1
- **Status:** DONE
- **Date:** 2026-04-10
- **Report:** Added `_infer_dtype_from_zone_name(zone_name)` and `infer_building_dtype(zones)` to `neighbourhood.py` (inserted before `get_building_groups`). Helper checks `highrise > midrise > apartment > living_unit > room_` in case-insensitive order, returns None for non-residential zones. `infer_building_dtype` does majority vote over non-None results, falls back to `'SingleD'`. No other files changed.

### Task 2
- **Status:** DONE
- **Date:** 2026-04-10
- **Report:** Changed `get_building_groups()` return type from `dict[str, list[str]]` to `dict[str, dict]` where each value is `{'spaces': [...], 'dtype': '...'}`. Print summary now shows DTYPE counts. Updated `get_water_equipment_building_map()` and `prepare_neighbourhood_idf()` to use `bldg_data['spaces']` instead of raw list. `get_num_buildings_from_idf()` needed no change (only counts keys).

### Task 3
- **Status:** DONE
- **Date:** 2026-04-10
- **Report:** Added `get_building_dtypes_from_idf(idf_path)` (thin wrapper returning ordered DTYPE list) and `load_dtype_overrides(idf_path)` (JSON sidecar loader) to `neighbourhood.py`. Task 7 sidecar logic was included here since it's a single function. Print summary shows DTYPE breakdown. Only `neighbourhood.py` changed.

### Task 4
- **Status:** NOT STARTED
- **Date:**
- **Report:**

### Task 5
- **Status:** NOT STARTED
- **Date:**
- **Report:**

### Task 6
- **Status:** NOT STARTED
- **Date:**
- **Report:**

### Task 7
- **Status:** NOT STARTED
- **Date:**
- **Report:**

### Task 8
- **Status:** NOT STARTED
- **Date:**
- **Report:**

---

## Execution Prompt for Sonnet

Copy and paste the block below into a fresh Claude Code session to begin implementation.

~~~
You are implementing a plan documented in:
C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\eSim_docs_ubem_utils\docs_ubem\occAssignNeighbourhood.md

Read that file first — it contains 8 tasks for adding building-type-aware occupant assignment to neighbourhood simulations (Options 5, 6, 7 in the BEM menu).

Context:
- The project is a building energy modeling (BEM) pipeline. The entry point is `run_bem.py` which calls `eSim_bem_utils/main.py`.
- Neighbourhood IDFs contain multiple buildings. Zone names carry building-type signals (e.g. "Midrise_Apartment", "highRiseApartment", "living_unit") but the code currently ignores them and pools all dwelling types together when assigning occupancy schedules.
- The plan adds DTYPE inference from zone names in `neighbourhood.py`, then uses it in `main.py` Options 5/6/7 to select households from the correct dwelling type pool.

Key files you will modify:
- `eSim_bem_utils/neighbourhood.py` — Tasks 1, 2, 3, 7
- `eSim_bem_utils/main.py` — Tasks 4, 5, 6
- `eSim_tests/test_dtype_assignment.py` — Task 8 (new file)

Key files to read for context (do NOT modify unless the plan says to):
- `eSim_bem_utils/integration.py` — understand `load_schedules()`, `filter_matching_households()`, `find_best_match_household()`
- `eSim_bem_utils/config.py` — path configuration
- `BEM_Setup/Neighbourhoods/NUS_RC*.idf` — the 6 neighbourhood IDF files (zone name patterns)

Rules:
1. Follow the plan task by task in order (1 -> 2 -> 3 -> 8 -> 4 -> 5 -> 6 -> 7). Write Task 8 (test script) right after Task 3 so it can validate each subsequent task.
2. After completing each task, update the Progress Log section at the bottom of `occAssignNeighbourhood.md` with: status DONE, today's date, and a short report (what changed, any deviations, test result).
3. After Tasks 1-3 and Task 8, run the test script (`py eSim_tests/test_dtype_assignment.py`) and paste the output into the Task 8 progress log. The inference tests should pass at that point.
4. After each of Tasks 4, 5, 6, re-run the test script to confirm no regressions.
5. Do NOT modify `integration.py`. The fix is in schedule *selection*, not schedule *injection*.
6. Do NOT refactor or clean up code outside the scope of each task.
7. Use `py` (not `python` or `python3`) to run scripts — this is a Windows machine where `py` is the launcher.
8. Commit after each task with the format: `[bem]: Task N — short description`.

Start by reading the plan file and `neighbourhood.py`, then begin Task 1.
~~~
