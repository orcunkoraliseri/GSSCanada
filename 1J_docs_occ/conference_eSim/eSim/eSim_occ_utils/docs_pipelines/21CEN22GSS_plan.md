# Implementation Plan: 21CEN22GSS Occupancy Modeling Pipeline

This document defines the recommended implementation approach for a new legacy-style pipeline for **Census 2021 + GSS 2022** under `eSim_occ_utils/21CEN22GSS/`.

The goal is not to redesign the project. The goal is to add one more script-oriented pipeline that behaves like `11CEN10GSS` and `16CEN15GSS`, reuses their structure wherever possible, and only introduces 2021/2022-specific logic where the data actually changed.

---

## 0. Current Status

### 0.1 What already exists

| Item | Status | Notes |
|------|--------|-------|
| `eSim_occ_utils/21CEN22GSS/` | ⬜ Not created | New pipeline package still needs to be added |
| `0_Occupancy/Outputs_21CEN22GSS/` | ⬜ Not created | Output root still needs to be added |
| `eSim_occ_utils/docs_pipelines/21CEN22GSS_plan.md` | ✅ Present | This file |
| `eSim_occ_utils/docs_pipelines/21CEN22GSS_tasks.md` | ✅ Present | Companion task file |
| `eSim_occ_utils/11CEN10GSS/` | ✅ Available | Best structural reference for a 4-step legacy pipeline |
| `eSim_occ_utils/16CEN15GSS/` | ✅ Available | Best reference for 2021-style CMA / BEM output conventions |
| `eSim_occ_utils/25CEN22GSS_classification/` | ✅ Available | Useful reference for 2021/2022 columns; do not modify for this task |

### 0.2 Verified local input files

These were checked directly in the repo on **March 31, 2026**:

| File | Status | Notes |
|------|--------|-------|
| `0_Occupancy/Outputs_CENSUS/cen21_filtered.csv` | ✅ Present | Recommended primary Census input for this pipeline |
| `0_Occupancy/DataSources_CENSUS/cen21.dat` | ✅ Present | Raw Census source |
| `0_Occupancy/DataSources_CENSUS/cen21.sps` | ✅ Present | Raw Census schema / codebook reference |
| `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2022.sas7bdat` | ✅ Present | Main GSS 2022 demographics file |
| `0_Occupancy/DataSources_GSS/Episode_files/GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat` | ✅ Present | Episode-level GSS 2022 time-use file |

### 0.3 Verified local GSS 2022 facts

These values were read directly from the local `.sas7bdat` files:

| Dataset | Verified fact |
|---------|----------------|
| Main file | `12336` rows |
| Episode file | `168078` rows |
| Episode file | `12336` unique `PUMFID` values |
| Main file | `DDAY` exists and uses `1..7` |
| Episode file | `DDAY` does **not** exist |
| Episode file | `LOCATION == 3300.0` is the dominant location code and is the working candidate for home presence |
| Episode file | Raw `PRE` mean using `LOCATION == 3300.0` is about `0.723` |
| Episode file | Raw `coPRE` mean using `TUI_06B/TUI_06C/TUI_06D == 1.0` is about `0.335` |

These are useful as sanity checks during implementation and testing.

---

## 1. Scope

### 1.1 Deliverable

Create a new package:

`eSim_occ_utils/21CEN22GSS/`

with the following files:

| File | Purpose | Primary reference |
|------|---------|-------------------|
| `21CEN22GSS_step0.py` | GSS 2022 episode preprocessing | New, with small reuse from classification ideas |
| `21CEN22GSS_alignment.py` | Census/GSS merge, household assembly, harmonization | `11CEN10GSS_alignment.py` |
| `21CEN22GSS_ProfileMatcher.py` | Tiered matching and schedule expansion | `11CEN10GSS_ProfileMatcher.py` |
| `21CEN22GSS_HH_aggregation.py` | 5-minute household grids | `11CEN10GSS_HH_aggregation.py` |
| `21CEN22GSS_occToBEM.py` | Hourly BEM schedules | `11CEN10GSS_occToBEM.py` |
| `21CEN22GSS_main.py` | Interactive pipeline controller | `11CEN10GSS_main.py` |
| `__init__.py` | Package marker | `11CEN10GSS/__init__.py` |

### 1.2 Non-goals

- Do not rewrite `25CEN22GSS_classification`.
- Do not invent a new package structure.
- Do not add DTYPE expansion unless explicitly requested later.
- Do not make this pipeline depend on EnergyPlus or BEM execution during development.

---

## 2. Recommended Input Strategy

### 2.1 Use the cleaned Census CSV, not the raw `.dat`, as the primary runtime input

The pragmatic input for this new legacy pipeline should be:

`0_Occupancy/Outputs_CENSUS/cen21_filtered.csv`

Reason:

- This matches how the newer project workflows already prepare Census data.
- It avoids duplicating raw fixed-width parsing logic inside the new pipeline.
- It keeps the new pipeline focused on household assembly, alignment, matching, aggregation, and BEM conversion.

The raw files:

- `0_Occupancy/DataSources_CENSUS/cen21.dat`
- `0_Occupancy/DataSources_CENSUS/cen21.sps`

should still be treated as the source of truth for code definitions, but not as the default runtime input unless `cen21_filtered.csv` is missing.

### 2.2 Use the raw GSS 2022 SAS files directly

For GSS 2022, the main and episode files are already in `.sas7bdat` format and can be read with `pandas.read_sas()`.

This is a real simplification relative to 2010 and 2015:

- no fixed-width parsing
- no `.sps` column-spec extraction
- no separate code just to decode record layouts

---

## 3. Target Output Structure

Create:

`0_Occupancy/Outputs_21CEN22GSS/`

with these subfolders:

| Folder | Purpose |
|--------|---------|
| `alignment/` | Census linked file, merged GSS file, aligned outputs, alignment summaries |
| `ProfileMatching/` | Matched keys, full schedules, validation report |
| `HH_aggregation/` | 5-minute household grids and aggregation validation |
| `occToBEM/` | Hourly BEM schedules and plots |

Recommended output filenames:

| Stage | File |
|------|------|
| Step 0 | `0_Occupancy/DataSources_GSS/Episode_files/GSS_2022_episode/out22EP_ACT_PRE_coPRE.csv` |
| Alignment | `alignment/2021_LINKED.csv` |
| Alignment | `alignment/GSS_2022_Merged.csv` |
| Alignment | `alignment/Aligned_Census_2022.csv` |
| Alignment | `alignment/Aligned_GSS_2022.csv` |
| Matching | `ProfileMatching/21CEN22GSS_Matched_Keys_sample{pct}pct.csv` |
| Matching | `ProfileMatching/21CEN22GSS_Full_Schedules_sample{pct}pct.csv` |
| Aggregation | `HH_aggregation/21CEN22GSS_Full_Aggregated_sample{pct}pct.csv` |
| BEM | `occToBEM/21CEN22GSS_BEM_Schedules_sample{pct}pct.csv` |

Use `Aligned_Census_2022.csv`, not `Aligned_Census_2021.csv`, because the legacy pipelines name aligned outputs by the **matching target year** shared with GSS.

---

## 4. 2021/2022 Data Decisions That Matter

### 4.1 Census 2021 variables that change the implementation

Verified from `cen21.sps`:

| Column | Verified values / issue | Implementation impact |
|--------|--------------------------|-----------------------|
| `AGEGRP` | `1..13`, with `1-2` representing ages under 15 | Drop `AGEGRP in {1, 2, 88}` before matching |
| `ATTSCH` | `0=did not attend`, `1=attended`, `8/9` invalid/not applicable | If used, remap to legacy `1/2` scheme deliberately |
| `DTYPE` | `1=Single-detached`, `2=Apartment`, `3=Other dwelling`, `8=NA` | Keep 3 coarse classes; no DTYPE expansion |
| `GENDER` | `1=Woman+`, `2=Man+`, `8=NA` | Reverse to legacy `SEX` convention before matching |
| `LFACT` | `1..14`, `99=NA` | Collapse to legacy labour-force categories |
| `MARSTH` | `1..4`, `8=NA` | Collapse to 3-category marital status used in legacy matchers |
| `PR` | 2-digit province codes | Aggregate to the regional scheme used in matching |

### 4.2 GSS 2022 variables that change the implementation

Verified from local column inspection:

| Column | Verified values / issue | Implementation impact |
|--------|--------------------------|-----------------------|
| `PUMFID` | Present in main and episode files | Use as merge key |
| `DDAY` | Present in main file only | Merge from main file; no duplicate-day-column problem |
| `HSDSIZEC` | Values observed: `1..5` | Treat as capped household-size category; cap Census to `5` |
| `AGEGR10` | Values observed: `1..7` | Same age-band target as prior pipelines |
| `GENDER2` | Values observed: `1,2` | Must verify semantic direction before freezing mapping |
| `MARSTAT` | Values observed: `1..6,99` | Requires collapse to legacy 3-category marital status |
| `LANHSDC` | Values observed: `1..4,9` | Usable as the `KOL` proxy, similar to prior pipelines |
| `ACT7DAYC` | Values observed: `1..5,9` | Strong candidate for `LFTAG` proxy |
| `LUC_RST` | Values observed: `1,2,3` | Use as the GSS side of CMA / urban-rural alignment |
| `INC_C` | Values observed: `1..5` | Do not assume a threshold mapping without validation |

### 4.3 Step 0 episode derivations

The episode file has these useful columns:

| Raw column | Use |
|-----------|-----|
| `PUMFID` | `occID` merge key |
| `INSTANCE` | `EPINO` |
| `ACTIVITY` | `ACTCODE` |
| `STARTMIN` / `ENDMIN` / `DURATION` | episode timing |
| `LOCATION` | home-presence proxy |
| `TUI_06A` | alone flag |
| `TUI_06B` / `TUI_06C` / `TUI_06D` | spouse / child / other-HH co-presence inputs |

Recommended derived fields:

- `PRE = 1` when `LOCATION == 3300.0`, else `0`
- `coPRE = 1` when any of `TUI_06B`, `TUI_06C`, `TUI_06D` equals `1.0`, else `0`

---

## 5. Recommended Matching Schema

### 5.1 Required core matching variables for V1

For the first working version, align and match on these columns:

`HHSIZE, AGEGRP, SEX, MARSTH, KOL, PR, LFTAG, CMA`

This is the safest set because all of them have a clear implementation path from local files and existing reference code.

### 5.2 Optional variables for V1.1, not blockers for first delivery

These should only be added after their mappings are explicitly verified:

| Variable | Reason to defer |
|---------|------------------|
| `TOTINC` | GSS 2022 `INC_C` is only `1..5`; threshold mapping to Census continuous income should not be guessed |
| `ATTSCH` | Census 2021 coding differs from earlier cycles; GSS 2022 proxy may work but needs confirmation |
| `NOCS` | Census 2021 uses `NOC21`, GSS uses `NOCLBR_Y`; the crosswalk may be too lossy for a first delivery |

Recommendation:

- Do **not** block the pipeline on these optional variables.
- Build the pipeline first with the required core matching set.
- If needed later, add them behind a second pass after value-alignment checks are stable.

---

## 6. Step-by-Step Implementation Strategy

### 6.1 Step 0: `21CEN22GSS_step0.py`

Start from scratch.

Responsibilities:

- read the raw episode SAS file
- keep only schedule-relevant columns
- rename to the legacy naming pattern used downstream
- derive `PRE` and `coPRE`
- save `out22EP_ACT_PRE_coPRE.csv`

Keep this file small and deterministic. It should not contain alignment logic.

### 6.2 Step 1: `21CEN22GSS_alignment.py`

Use `11CEN10GSS_alignment.py` as the main structural template.

Keep these pieces:

- `assemble_households()`
- `data_alignment()`
- value-alignment reporting
- output-directory handling

Change these pieces:

- GSS reader: use `pd.read_sas()` instead of `.DAT` + `.SPS`
- merge key: `PUMFID`
- Census input: use `cen21_filtered.csv`
- `HHSIZE`: cap to `5`
- `SEX`: reverse Census 2021 coding, and verify GSS 2022 direction before locking
- `LFTAG`: collapse from Census `LFACT` and GSS `ACT7DAYC`
- `DTYPE`: do not introduce expansion logic

### 6.3 Step 2: `21CEN22GSS_ProfileMatcher.py`

Copy from `11CEN10GSS_ProfileMatcher.py`.

Initial recommendation:

- keep the same tier structure
- change Tier 1 to the V1 core columns listed above
- only add `TOTINC`, `ATTSCH`, or `NOCS` after they are validated

The output format should remain compatible with `HH_aggregation`.

### 6.4 Step 3: `21CEN22GSS_HH_aggregation.py`

Copy from `11CEN10GSS_HH_aggregation.py` with minimal edits:

- new filenames
- new output root
- preserve the same 5-minute aggregation logic
- preserve the same validation style

The aggregation stage should not care that Census 2021 has only 3 dwelling-type categories. It just needs to carry the residential columns forward.

### 6.5 Step 4: `21CEN22GSS_occToBEM.py`

Copy from `11CEN10GSS_occToBEM.py`.

Required change:

- replace the detailed 2011 DTYPE map with a 2021 3-class map

Recommended DTYPE mapping for output labels:

| Census 2021 DTYPE | Label |
|-------------------|-------|
| `1` | `SingleD` |
| `2` | `Apartment` |
| `3` | `OtherDwelling` |

Do not fake a high-rise / mid-rise split at this stage.

### 6.6 Step 5: `21CEN22GSS_main.py`

Copy from `11CEN10GSS_main.py`.

Structure:

- 4 pipeline steps
- full-pipeline run option
- sample-percentage option
- no DTYPE-expansion menu entry

---

## 7. Validation Gates

### 7.1 Light validation only during development

Use narrow checks first:

- import smoke tests
- row-count checks
- unique-value checks
- a `sample_pct=1` or `sample_pct=10` run through matching / aggregation / BEM conversion

Avoid heavy full-population runs until the aligned outputs look correct.

### 7.2 Concrete acceptance criteria

The pipeline is in good shape when all of these are true:

1. Step 0 creates `out22EP_ACT_PRE_coPRE.csv` with about `168078` rows and `12336` unique `occID` values.
2. The merged GSS file keeps the episode row count unchanged and includes exactly one `DDAY` column.
3. `Aligned_Census_2022.csv` and `Aligned_GSS_2022.csv` are both non-empty.
4. Core alignment columns have matching unique value sets across both aligned files.
5. A sample matching run produces no null `MATCH_ID_WD` or `MATCH_ID_WE`.
6. HH aggregation produces `288` 5-minute rows per `SIM_HH_ID` and `Day_Type`.
7. BEM conversion produces `24` hourly rows per `SIM_HH_ID` and `Day_Type`.
8. `Occupancy_Schedule` stays within `[0, 1]`.

---

## 8. Main Risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| Gender-code direction in `GENDER2` is ambiguous from value inspection alone | A silent swap would contaminate matching quality | Treat sex/gender mapping as a first-class validation checkpoint |
| `INC_C` only shows `1..5` | Income matching can be wrong if thresholds are guessed | Keep `TOTINC` out of V1 matching unless mapping is verified |
| `HSDSIZEC` tops out at `5` | Household-size mismatches can destroy match yield | Explicitly cap Census `HHSIZE` to `5` |
| Census 2021 `DTYPE` is coarse | BEM labels cannot mimic 2011/2016 detail | Keep 3 classes and document the limitation |
| Over-copying from `25CEN22GSS_classification` | That code solves a different problem and is marked sensitive | Use it only as a column/mapping reference |

---

## 10. Known Bug Risks Inherited from 11CEN10GSS

These three bugs were found in the completed 11CEN10GSS pipeline only after comparing its output plots against reference pipelines. The same root causes apply here because 21CEN22GSS was built from the same template. All three are confirmed by inspecting the existing `out22EP_ACT_PRE_coPRE.csv`.

**Confirmed status (2026-04-01):** All three bugs are present in the current 21CEN22GSS scripts. They have not yet been fixed.

### Bug A: STARTMIN/ENDMIN are decimal minutes, not HHMM

GSS 2022 stores `STARTMIN` and `ENDMIN` as decimal minutes from midnight (0–1440+). The `_create_individual_grid` method in `HH_aggregation.py` parses the `start` / `STARTMIN` column using HHMM logic `(raw // 100) * 60 + (raw % 100)`, which is wrong for decimal minutes.

Confirmed from the saved CSV:
- `STARTMIN` values: 240, 245, 250, 255, … (decimal minutes starting at 4:00 AM)
- `STARTMIN` max: 1675 (past midnight, wraps)
- The current step0 saves `STARTMIN` raw and does not create `start`/`end` HHMM columns

If not fixed, every episode is placed in the wrong 5-minute slot (shifted 1–6 hours too early), producing a flat, unrecognizable occupancy pattern instead of the expected diurnal residential curve.

**Fix location:** `21CEN22GSS_step0.py` — add `_min_to_hhmm()` and derive `start`/`end` HHMM columns before saving.

### Bug B: ACTCODE raw codes are not mapped to harmonized 1-14 categories

GSS 2022 `ACTIVITY` column uses a compact hierarchical scheme (19 distinct codes: 100, 125, 150, 200, 230, 260, 300, 350, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 9999). The `metabolic_map` in `occToBEM.py` uses keys `'1'`–`'14'`. None of the raw GSS 2022 codes match any key, so every active time slot falls back to 100 W.

Confirmed from the saved CSV:
- Top 5 ACTCODE values: 100 (27,313 rows), 150 (23,059), 200 (23,016), 400 (22,975), 1200 (18,263)
- None of these match the metabolic_map key set `{'1', '2', ..., '14'}`

If not fixed, the metabolic rate distribution shows a single spike at 100 W and no variation across sleep, work, or leisure periods.

**Fix location:** `21CEN22GSS_step0.py` — add `ACT_MAP_22` and `_map_actcode()`, derive `occACT` column (harmonized 1-14) before saving.

Candidate GSS 2022 mapping (to verify against codebook before implementing):

| Raw code | Likely activity | Harmonized category |
|----------|----------------|---------------------|
| 100 | Sleep / personal needs | 5 (Sleep) |
| 125 | Sub-sleep or napping | 5 (Sleep) |
| 150 | Personal care / hygiene / eating | 7 (Personal Care) |
| 200 | Household work (cleaning, cooking) | 2 (Household Work) |
| 230 | Household work sub-category | 2 (Household Work) |
| 260 | Household work sub-category | 2 (Household Work) |
| 300 | Caregiving | 3 (Caregiving) |
| 350 | Caregiving sub-category | 3 (Caregiving) |
| 400 | Paid work | 1 (Work & Related) |
| 500 | Education | 8 (Education) |
| 600 | Shopping / services | 4 (Shopping) |
| 700 | Civic / volunteer | 12 (Volunteer) |
| 800 | Socializing / communication | 9 (Socializing) |
| 900 | Passive leisure (TV, reading) | 10 (Passive Leisure) |
| 1000 | Active leisure / sport | 11 (Active Leisure) |
| 1100 | Travel / transport | 13 (Travel) |
| 1200 | Recreation / mixed leisure | 10 (Passive Leisure) |
| 1300 | Other / unclassified | 14 (Other) |
| 9999 | Missing / not stated | 14 (Other) |

Confirm exact meanings by inspecting mean duration, time of day, and home/away fraction for each code in the data before finalizing.

### Bug C: ROOM outliers not filtered

Census 2021 `ROOM` values are passed through without any cap. The reference 11CEN10GSS run found 47 households with ROOM > 15 (max = 88), which are physically implausible. The same issue is expected here since `cen21_filtered.csv` draws from the same raw Census source.

If not filtered, the ROOM distribution plot will show an extreme tail that is absent from reference pipelines.

**Fix location:** `21CEN22GSS_alignment.py` — add `ROOM <= 15` filter after loading the Census data.

### Silent bug D: Social density always zero

`HH_aggregation.py` looks for columns named `Spouse`, `Children`, `otherInFAMs` (title case) to compute `occDensity`. The current step0 saves only the raw TUI columns (`TUI_06B`, `TUI_06C`, `TUI_06D`, etc.) without creating these aliases. Because none of the alias columns exist, `valid_social` in `HH_aggregation` is always empty, `occDensity` is always 0, and the BEM formula `occPre × (occDensity + 1)` collapses to `occPre × 1` — co-presence is never counted.

**Fix location:** `21CEN22GSS_step0.py` — add social alias derivations before saving:
- `Spouse = TUI_06B == 1.0`
- `Children = TUI_06C == 1.0`
- `otherInFAMs = TUI_06D == 1.0`
- (and any extended aliases for `parents`, `Friends`, `otherHHs`, etc. from the 2022 TUI columns)

### Diagnostic checks to run after fixes

After fixes are applied and the pipeline is re-run, the output plots must pass these checks before the pipeline is considered correct:

| Check | Pass criterion |
|-------|---------------|
| Diurnal occupancy pattern | Average presence clearly higher at night (0–6h) than during work hours (9–17h weekdays) |
| Metabolic rate distribution | Spread from ~70 W (Sleep) to ~200 W (Active Leisure); no single spike at 100 W |
| ROOM distribution | No values above 15 in the BEM non-temporal plot |
| occDensity | Non-zero for a significant fraction of home-present time slots |
| Sample household weekday | Dynamic occupancy trace with departures and returns, not a flat line |

---

## 9. Recommended Build Order

Build in this order:

1. Create the package folder and `__init__.py`.
2. Implement Step 0 and confirm its output counts.
3. Implement alignment and get the aligned CSVs clean.
4. Freeze the core matching columns.
5. Copy and adapt `ProfileMatcher`.
6. Copy and adapt `HH_aggregation`.
7. Copy and adapt `occToBEM`.
8. Add the interactive main controller.
9. Run a small sample end to end.

That order keeps the critical path short and makes failures easier to localize.
