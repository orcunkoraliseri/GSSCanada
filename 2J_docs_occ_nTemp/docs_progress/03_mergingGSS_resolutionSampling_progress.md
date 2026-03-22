# Step 3E — Resolution Downsampling: Progress Log (Tasks 1–18)

This document tracks the implementation progress of the 4:00 AM origin 144-slot to 48-slot downsampling phase in `03_mergingGSS.py`.

---

## Group 0 — Setup & Constants

### Task #1 — Add Phase H function skeleton
- **Status:** COMPLETED
- **Actions:** Added `downsample_to_30min(hetus_wide_df)` function skeleton and integrated its call into the `main()` pipeline immediately following the Phase G export.

### Task #2 — Define BEM_PRIORITY constant
- **Status:** COMPLETED
- **Actions:** Created the `BEM_PRIORITY` dictionary mapping the 14 confirmed activity categories (from `02_harmonizeGSS.py`) to their BEM priority ranks (1–14). 
- **Rationale:** Ensures that energy-model-critical activities (Sleep, Work) are preserved during 3-way tie resolutions.

---

## Group 1 — Load and Split Columns

### Task #3 — H.1a: Load hetus_wide.csv and verify row count
- **Status:** COMPLETED
- **Actions:** Implemented data loading from `outputs_step3/hetus_wide.csv`. Added an assertion to verify the expected 64,061 respondent rows.

### Task #4 — H.1b: Separate identity columns from slot columns
- **Status:** COMPLETED
- **Actions:** Dynamically identified metadata/identity columns versus the 288 source slot columns (`slot_NNN` and `home_NNN`).

### Task #5 — H.1c: Extract activity matrix as numpy array
- **Status:** COMPLETED
- **Actions:** Converted activity columns to a high-performance `(64061, 144)` float array for vectorized processing.

### Task #6 — H.1d: Extract AT_HOME matrix as numpy array
- **Status:** COMPLETED
- **Actions:** Converted AT_HOME columns to a `(64061, 144)` float array.

---

## Group 2a — Activity Majority Vote

### Task #7 — H.2a: Reshape activity array to (n × 48 × 3)
- **Status:** COMPLETED
- **Actions:** Reshaped the flat activity matrix into a 3D windowed array `(64061, 48, 3)` where every 3 slots represent one 30-min window.

### Task #8 — H.2b: Write _nanmode_axis2() helper function
- **Status:** COMPLETED
- **Actions:** Implemented a robust mode solver that handles strict majorities (>=2 slots) and flags ties as `NaN`.

### Task #9 — H.2c: Apply nanmode to get act_30 with tie sentinels
- **Status:** COMPLETED
- **Actions:** Executed the majority vote across all 3.07 million slots. Logged the frequency of 3-way ties requiring priority resolution.

---

## Group 2b — AT_HOME Binary Vote

### Task #10 — H.3a: Reshape AT_HOME array to (n × 48 × 3)
- **Status:** COMPLETED
- **Actions:** Windowed the binary presence matrix into `(64061, 48, 3)`.

### Task #11 — H.3b: Compute AT_HOME binary majority vote
- **Status:** COMPLETED
- **Actions:** Implemented vectorized binary sum logic. Marks a 30-min slot as `1` (Home) if >=2 underlying slots are `1`. Verified zero NaN propagation.

---

## Group 3 — Tie Resolution

### Task #12 — H.4a: Detect 3-way tie positions
- **Status:** COMPLETED
- **Actions:** Isolated the indices of all activity slots that failed the majority vote.

### Task #13 — H.4b: Resolve ties using BEM priority order
- **Status:** COMPLETED
- **Actions:** Applied the BEM priority ranked-choice solver to resolve all ambiguous transitions. Verified completion with a zero-NaN assertion.

---

## Group 4 — Assemble output DataFrame

### Task #14 — H.5a: Build act30 DataFrame with Int16 dtype
- **Status:** COMPLETED
- **Actions:** Generated the 48 activity columns (`act30_001`–`act30_048`) with `Int16` nullable integer types.

### Task #15 — H.5b: Build hom30 DataFrame with Int8 dtype
- **Status:** COMPLETED
- **Actions:** Generated the 48 Home Presence columns (`hom30_001`–`hom30_048`) with `Int8` types.

### Task #16 — H.5c: Concatenate meta + act30 + hom30
- **Status:** COMPLETED
- **Actions:** Consolidated identity/demographic columns with the new 96 temporal columns into the final `hetus_30min` DataFrame.

---

## Group 5 — Export & Summary

### Task #17 — H.6a: Write hetus_30min.csv
- **Status:** COMPLETED
- **Actions:** Persisted the final downsampled dataset to `outputs_step3/hetus_30min.csv`.

### Task #18 — H.6b: Print post-export summary
- **Status:** COMPLETED
- **Actions:** Added logging to `main()` to report the final shape, column counts, and absence of NaNs in the produced file.

---

## Group 6 — Validation Suite (V1–V8)

### Task #19 — V1: Shape check
- **Status:** COMPLETED
- **Actions:** Confirmed 64,061 respondent rows and successfully validated the 48-slot activity (`act30_`) and 48-slot presence (`hom30_`) column counts.

### Task #20 — V2: Zero NaN in act30 and hom30
- **Status:** COMPLETED
- **Actions:** Verified 100% data completeness. Zero NaNs remain across the entire temporal 30-min matrix (3.07 million data points).

### Task #21 — V3: Activity distribution comparison
- **Status:** COMPLETED
- **Actions:** Compared the weighted category frequencies in `hetus_30min` vs `hetus_wide`. All 14 activity categories match the 10-min ground truth within < 0.5 percentage points (PP).

### Task #22 — V4: Weighted AT_HOME rate per cycle
- **Status:** COMPLETED
- **Actions:** Implemented dynamic verification by calculating weighted presence rates from both `hetus_wide` and `hetus_30min` per cycle. Verified match within < 0.1 PP across all four cycles.

### Task #23 — V5: Night slot plausibility (04:00–07:59 AM)
- **Status:** COMPLETED
- **Actions:** Confirmed night-time data integrity: Sleep rates (71.6%) and AT_HOME rates (87.4%) exceed the energy-modeling thresholds of 70% and 85%, respectively.

### Task #24 — V6: 3-way tie rate < 5%
- **Status:** COMPLETED
- **Actions:** Verified that ambiguous transitions requiring priority resolution occurred in only 0.82% of all slots, well below the 5% caution threshold.

### Task #25 — V7: DDAY_STRATA distribution unchanged
- **Status:** COMPLETED
- **Actions:** Confirmed that demographic stratum distributions (Weekday/Saturday/Sunday) were preserved exactly during the downsampling pass.

### Task #26 — V8: Manual spot-check 5 random respondents
- **Status:** COMPLETED
- **Actions:** Inspected 5 randomly selected respondents (rows: 41905, 7296, 1639, 48598, 18024). Manually verified that `act30` and `hom30` values correctly represent the majority vote of their underlying 10-min source slots.

---

## Final Project Status: Phase H Complete
Phase H is fully implemented, rigorously validated, and successfully integrated into the main `03_mergingGSS.py` pipeline. The downsampled 30-min resolution data is officially ready for downstream training in Step 4.

**Primary Output:** `outputs_step3/hetus_30min.csv` (64,061 rows × 120 columns).

---

---

# Phase I — Co-Presence Tiling: Progress Log (Tasks 27–)

This section tracks implementation of Phase I: tiling the 9 episode-level co-presence columns from `merged_episodes.csv` into the same 30-min slot format as `hetus_30min.csv`.

**Status:** PENDING
**Prerequisite:** Phase H complete ✅
**Target output:** `outputs_step3/copresence_30min.csv` (64,061 rows × 433 columns)

---

## Group 7 — Setup & Load

### Task #27 — Add Phase I function skeleton
- **Status:** PENDING
- **Actions:** Add `tile_copresence_to_30min()` function skeleton to `03_mergingGSS.py` after Phase H. Add call in `main()` after Phase H block.

### Task #28 — Define co-presence column list constant
- **Status:** PENDING
- **Actions:** Define `COP_COLS = ["Alone", "Spouse", "Children", "parents", "otherInFAMs", "otherHHs", "friends", "others", "colleagues"]` as a module-level constant. Confirm these names match the actual column headers in `merged_episodes.csv`.

---

## Group 8 — Load Inputs

### Task #29 — I.1: Load merged_episodes.csv and verify
- **Status:** PENDING
- **Actions:** Load `outputs_step3/merged_episodes.csv`. Verify presence of `occID`, `startMin`, `endMin`, `CYCLE_YEAR`, and all 9 co-presence columns. Print row count (~1,049,480) and unique occID count (64,061).

### Task #30 — I.2: Load hetus_30min.csv for occID order reference
- **Status:** PENDING
- **Actions:** Extract the ordered occID list from `hetus_30min.csv` (64,061 rows). Build an `occid_to_idx` dict for O(1) row-index lookups during the tiling loop.

---

## Group 9 — Tiling Loop (I.3)

### Task #31 — I.3a: Pre-allocate 9 × (64,061 × 144) NaN arrays
- **Status:** PENDING
- **Actions:** Allocate one float64 array of shape (64,061 × 144) per co-presence column (or a single (9 × 64,061 × 144) array). Initialise all values to NaN.

### Task #32 — I.3b: Sort episodes by occID for efficient grouped access
- **Status:** PENDING
- **Actions:** Sort `merged_episodes` by `occID` and build a group index (start/end row per occID) for fast iteration without repeated `.groupby()` calls.

### Task #33 — I.3c: Tiling loop — episode → 10-min slots
- **Status:** PENDING
- **Actions:** Iterate over all respondents; for each episode, compute `slot_start = startMin//10` and `slot_end = endMin//10` (0-indexed), and fill the NaN array for each co-presence column. Handle endMin=0 wrap-around (endMin → 144). Log progress every 10,000 respondents.

---

## Group 10 — Downsample to 30-Min (I.4)

### Task #34 — I.4a: Reshape each (64,061 × 144) array to (64,061 × 48 × 3)
- **Status:** PENDING
- **Actions:** Apply `.reshape(n, 48, 3)` to each of the 9 10-min arrays.

### Task #35 — I.4b: Binary majority vote → (64,061 × 48) output per column
- **Status:** PENDING
- **Actions:** For each column: `sum_present = nansum(cop_3d == 1, axis=2)`; `valid_count = sum(~isnan, axis=2)`; assign 1 if `sum_present >= 2`, else 2; NaN if `valid_count == 0`. Log NaN rate per column.

---

## Group 11 — Assemble & Export

### Task #36 — I.5a: Build {ColName}30_NNN DataFrames (Int8) for each column
- **Status:** PENDING
- **Actions:** For each of 9 columns, create a DataFrame (64,061 × 48) with columns named `{ColName}30_{001..048}`, cast to `pd.Int8Dtype()`.

### Task #37 — I.5b: Concatenate all 9 DataFrames + occID
- **Status:** PENDING
- **Actions:** Concatenate occID column + 9 co-presence DataFrames (in COP_COLS order) into `copresence_30min`. Verify shape (64,061 × 433).

### Task #38 — I.6a: Write copresence_30min.csv
- **Status:** PENDING
- **Actions:** Write to `outputs_step3/copresence_30min.csv`. Log file size.

### Task #39 — I.6b: Print post-export summary
- **Status:** PENDING
- **Actions:** Print shape, column count per co-presence variable, NaN counts per column (colleagues expected all-NaN for 2005/2010 rows).

---

## Group 12 — Validation Suite (VI-1 through VI-7)

### Task #40 — VI-1: Shape check
- **Status:** PENDING
- **Actions:** Assert 64,061 rows and 433 columns (1 occID + 432 co-presence slots).

### Task #41 — VI-2: occID alignment with hetus_30min
- **Status:** PENDING
- **Actions:** Assert `copresence_30min["occID"].equals(hetus_30min["occID"])` — identical order, no mismatches.

### Task #42 — VI-3: No all-NaN respondents for primary 8 columns
- **Status:** PENDING
- **Actions:** For each of [Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others]: assert no respondent has all-NaN across their 48 slots.

### Task #43 — VI-4: colleagues NaN pattern by cycle
- **Status:** PENDING
- **Actions:** For 2005/2010 rows: assert all 48 `colleagues30_NNN` slots are NaN (100%). For 2015/2022 rows: assert NaN rate < 100%.

### Task #44 — VI-5: Value range check
- **Status:** PENDING
- **Actions:** For all non-NaN values across all 9×48 co-presence slot columns: assert values ∈ {1, 2}.

### Task #45 — VI-6: Co-presence prevalence plausibility
- **Status:** PENDING
- **Actions:** Compute proportion of slots with value=1 (present) for `Alone30_NNN` (expect ~30–50%) and `Spouse30_NNN` (expect ~20–40%) across all respondents. Log and verify directionally plausible.

### Task #46 — VI-7: Manual spot-check 5 random respondents
- **Status:** PENDING
- **Actions:** For 5 randomly selected occIDs: cross-check `Alone30_001` against the source episodes in `merged_episodes.csv` covering 10-min slots 1–3 (04:00–04:29). Confirm majority vote is correct.

---

## Group 14 — Co-Presence Before/After Plot in `03_mergingGSS_val.py`

### Task #47 — Add Section 8a: Co-Presence Prevalence Before vs. After 30-Min Tiling
- **Status:** PENDING
- **Dependencies:** Task #38 (copresence_30min.csv must exist); Phase H output (hetus_30min.csv must exist)
- **Actions:** Add `validate_copresence_30min()` method to `Step3Validator` in `03_mergingGSS_val.py`. Plot compares episode-level prevalence (before tiling, from `merged_episodes.csv`) vs. 30-min slot prevalence (after tiling, from `copresence_30min.csv`) for all 9 co-presence columns across 4 cycles. Figure layout: 2-row grid — Row 1: four per-cycle panels (grouped bars, blue = episode, orange = slot); Row 2: single delta panel (slot − episode in pp, one line per cycle). Wire into `run()` and `build_html_report()` as plot key `"8a_copre_before_after"`.
