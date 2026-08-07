# 21CEN22GSS Pipeline: Detailed Task Breakdown

**Reference plan**: `eSim_occ_utils/docs_pipelines/21CEN22GSS_plan.md`  
**Primary code references**: `eSim_occ_utils/11CEN10GSS/` and `eSim_occ_utils/16CEN15GSS/`  
**Column reference only**: `eSim_occ_utils/25CEN22GSS_classification/`  
**Target package**: `eSim_occ_utils/21CEN22GSS/`  
**Target output root**: `0_Occupancy/Outputs_21CEN22GSS/`

This file translates the plan into implementation tasks with five questions for every task:

- what to do
- how to do it
- why to do it
- what result to expect
- how to test it

The intent is to make the work executable without guesswork.

---

## Progress Snapshot

| Task group | Status |
|-----------|--------|
| Package scaffold | ✅ Done |
| Step 0: Episode preprocessing | ✅ Done |
| **Step 0 bug fixes (B4–B6)** | ✅ Done |
| Step 1: Alignment | ✅ Done |
| **Alignment bug fix (C14)** | ✅ Done |
| Step 2: Profile matching | ✅ Done |
| Step 3: HH aggregation | ✅ Done |
| Step 4: BEM conversion | ✅ Done |
| Main controller | ✅ Done |
| **Output validation pass (I1)** | ✅ Done |

**Note (2026-04-01):** Three bugs and one silent bug from the 11CEN10GSS pipeline are confirmed present in the current 21CEN22GSS scripts. The existing B and C tasks were completed against the original plan which did not include these fixes. Tasks B4–B6, C14, and I1 are new additions to address them.

---

## A. Package Scaffold

### A1. Create the new package folder and marker file

**What to do**  
Create `eSim_occ_utils/21CEN22GSS/` and add `__init__.py`.

**How to do it**  
Mirror the layout of `eSim_occ_utils/11CEN10GSS/`. Start with an empty `__init__.py` and add the six pipeline scripts later.

**Why to do it**  
The rest of the work assumes a stable package location. Without the folder and marker file, imports and relative path assumptions become messy immediately.

**Expected result**  
The repo contains:

- `eSim_occ_utils/21CEN22GSS/__init__.py`

**How to test**  
- Confirm the folder exists.
- Run an import smoke test that loads the package path without error.

---

## B. Step 0: GSS 2022 Episode Preprocessing

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_step0.py`.

### B1. Read and normalize the episode SAS file

**What to do**  
Read `TU_ET_2022_Episode_PUMF.sas7bdat`, keep only the schedule-relevant columns, and rename them to the legacy names used by the downstream pipeline.

**How to do it**  
1. Read the file with `pandas.read_sas(..., format="sas7bdat", encoding="latin1")`.
2. Keep:
   - `PUMFID`
   - `INSTANCE`
   - `ACTIVITY`
   - `STARTMIN`
   - `ENDMIN`
   - `DURATION`
   - `LOCATION`
   - `TUI_06A`
   - `TUI_06B`
   - `TUI_06C`
   - `TUI_06D`
   - `TUI_06E`
   - `TUI_06F`
   - `TUI_06G`
   - `TUI_06H`
   - `TUI_06I`
   - `TUI_06J`
   - `TUI_07`
   - `TUI_15`
3. Rename:
   - `PUMFID -> occID`
   - `INSTANCE -> EPINO`
   - `ACTIVITY -> ACTCODE`
4. Do not add `DDAY` here. It does not live in the episode file for 2022.

**Why to do it**  
This is the minimum episode schema the rest of the legacy pipeline needs. It standardizes the 2022 raw file into the naming pattern used in 2010 and 2015 workflows.

**Expected result**  
A DataFrame with `168078` rows and columns:

- `occID`
- `EPINO`
- `ACTCODE`
- `STARTMIN`
- `ENDMIN`
- `DURATION`
- `LOCATION`
- `TUI_06A`
- `TUI_06B`
- `TUI_06C`
- `TUI_06D`
- `TUI_06E`
- `TUI_06F`
- `TUI_06G`
- `TUI_06H`
- `TUI_06I`
- `TUI_06J`
- `TUI_07`
- `TUI_15`

**How to test**  
- Row count is close to `168078`.
- `df['occID'].nunique() == 12336` if the local file is unchanged.
- `DDAY` is not present.
- `STARTMIN` and `ENDMIN` are within `0..1440`.
- `DURATION` is non-negative.

### B2. Derive `PRE` and `coPRE`

**What to do**  
Add occupancy-presence fields required by the downstream scripts.

**How to do it**  
Use the working 2022 definitions already validated locally:

```python
df["PRE"] = (df["LOCATION"] == 3300.0).astype(int)
df["coPRE"] = (
    (df["TUI_06B"] == 1.0) |
    (df["TUI_06C"] == 1.0) |
    (df["TUI_06D"] == 1.0)
).astype(int)
```

Keep the full episode context columns if possible; only `TUI_06B`, `TUI_06C`, and `TUI_06D` are required for the `coPRE` derivation itself.

**Why to do it**  
`PRE` and `coPRE` are the core occupancy signals used by matching, aggregation, and BEM conversion.

**Expected result**  
Two binary columns:

- `PRE` in `{0,1}`
- `coPRE` in `{0,1}`

Expected means using the current local files:

- `PRE` around `0.723`
- `coPRE` around `0.335`

**How to test**  
- `df["PRE"].isin([0, 1]).all()`
- `df["coPRE"].isin([0, 1]).all()`
- `0.68 <= df["PRE"].mean() <= 0.76`
- `0.28 <= df["coPRE"].mean() <= 0.38`

### B3. Save the processed episode CSV

**What to do**  
Write the preprocessed episode file for later reuse.

**How to do it**  
Save:

`0_Occupancy/DataSources_GSS/Episode_files/GSS_2022_episode/out22EP_ACT_PRE_coPRE.csv`

Recommended output columns:

- `occID`
- `EPINO`
- `ACTCODE`
- `STARTMIN`
- `ENDMIN`
- `DURATION`
- `LOCATION`
- `PRE`
- `coPRE`
- `TUI_06A`
- `TUI_06B`
- `TUI_06C`
- `TUI_06D`
- `TUI_06E`
- `TUI_06F`
- `TUI_06G`
- `TUI_06H`
- `TUI_06I`
- `TUI_06J`
- `TUI_07`
- `TUI_15`

Optional compatibility improvement:

- also write a copy to `0_Occupancy/Outputs_GSS/out22EP_ACT_PRE_coPRE.csv` if you want the file to be reusable by the classification workflow

**Why to do it**  
This avoids re-reading the SAS file during every alignment run and matches the cached-file pattern used by other pipelines.

**Expected result**  
`out22EP_ACT_PRE_coPRE.csv` exists and is ready for Step 1.
The saved episode file also keeps the 2022 co-presence / context fields needed by later steps.

**How to test**  
- File exists.
- Reloaded row count still matches the in-memory DataFrame.
- Reloaded columns match the expected list exactly.

### B4. Add `occACT` column: map raw GSS 2022 ACTCODE to harmonized 1-14 categories

**What to do**
Add an `ACT_MAP_22` dictionary and `_map_actcode()` function to `21CEN22GSS_step0.py`, then derive a new `occACT` column before saving the episode CSV.

**How to do it**
1. Confirm the meaning of each GSS 2022 ACTCODE by inspecting mean duration, time-of-day distribution, and home-fraction for each code in the data.
2. Define `ACT_MAP_22` as a plain dict mapping raw codes to harmonized 1-14 integers. Start from the candidate mapping in `21CEN22GSS_plan.md` Section 10, Bug B.
3. Add `_map_actcode(code_raw)` that does an exact-key lookup with a fallback of `14` (Other) for unmapped codes.
4. Before `df.to_csv(...)`, add:
   ```python
   df["occACT"] = df["ACTCODE"].apply(_map_actcode)
   ```
5. Add `occACT` to `OUTPUT_COLUMNS`.

**Why to do it**
The `metabolic_map` in `occToBEM.py` uses keys `'1'`–`'14'`. Raw 3-4 digit GSS 2022 codes never match these keys, so every active slot falls back to 100 W. The `occACT` column fixes this by pre-mapping codes in step0, exactly as was done in `11CEN10GSS_step0.py`.

**Expected result**
`out22EP_ACT_PRE_coPRE.csv` gains an `occACT` column with integer values in `1..14`.

**How to test**
- `df["occACT"].isin(range(1, 15)).all()`
- Code 100 (Sleep) maps to 5
- Code 400 (Work) maps to 1
- `df["occACT"].value_counts()` shows spread across multiple categories, not a single value

---

### B5. Add `start`/`end` columns: convert decimal minutes to HHMM format

**What to do**
Add `_min_to_hhmm()` to `21CEN22GSS_step0.py` and derive `start`/`end` HHMM columns before saving.

**How to do it**
Confirmed: GSS 2022 `STARTMIN` and `ENDMIN` are decimal minutes from midnight (verified values: 240=4:00 AM, 480=8:00 AM, max=1675). The `_create_individual_grid` method in `HH_aggregation.py` parses these using HHMM logic unless a `start` column exists.

Add the converter:
```python
def _min_to_hhmm(minutes_raw):
    minutes_raw = int(minutes_raw) % 1440  # wrap past midnight
    h = minutes_raw // 60
    m = minutes_raw % 60
    return h * 100 + m
```

Before `df.to_csv(...)`, add:
```python
df["start"] = df["STARTMIN"].apply(_min_to_hhmm)
df["end"]   = df["ENDMIN"].apply(_min_to_hhmm)
```

Add `start` and `end` to `OUTPUT_COLUMNS`.

**Why to do it**
`HH_aggregation._create_individual_grid` falls back to `STARTMIN` when no `start` column exists, then applies HHMM parsing to what is actually decimal minutes. A 9 AM work episode (STARTMIN=540) is parsed as 5:40 AM (340 min) — shifted 3+ hours too early. This is the same critical bug that caused flat occupancy patterns in 11CEN10GSS.

**Expected result**
`out22EP_ACT_PRE_coPRE.csv` gains `start` and `end` columns in HHMM integer format.

**How to test**
- `_min_to_hhmm(0) == 0`
- `_min_to_hhmm(240) == 400` (4:00 AM)
- `_min_to_hhmm(540) == 900` (9:00 AM)
- `_min_to_hhmm(1440) == 0` (midnight wrap)
- `df["start"].between(0, 2359).all()`

---

### B6. Add social alias columns for household co-presence

**What to do**
Derive `Spouse`, `Children`, `otherInFAMs` alias columns (and additional 2022 aliases) in `21CEN22GSS_step0.py` before saving the episode CSV.

**How to do it**
`HH_aggregation.py` looks for title-case social column names to compute `occDensity`. The step0 currently saves only raw TUI columns (`TUI_06A`–`TUI_06J`). Add:

```python
df["Alone"]       = (pd.to_numeric(df["TUI_06A"], errors="coerce") == 1.0).astype(int)
df["Spouse"]      = (pd.to_numeric(df["TUI_06B"], errors="coerce") == 1.0).astype(int)
df["Children"]    = (pd.to_numeric(df["TUI_06C"], errors="coerce") == 1.0).astype(int)
df["otherInFAMs"] = (pd.to_numeric(df["TUI_06D"], errors="coerce") == 1.0).astype(int)
df["parents"]     = (pd.to_numeric(df["TUI_06E"], errors="coerce") == 1.0).astype(int)
df["Friends"]     = (pd.to_numeric(df["TUI_06F"], errors="coerce") == 1.0).astype(int)
df["otherHHs"]    = (pd.to_numeric(df["TUI_06G"], errors="coerce") == 1.0).astype(int)
df["colleagues"]  = (pd.to_numeric(df["TUI_06H"], errors="coerce") == 1.0).astype(int)
df["Others"]      = (pd.to_numeric(df["TUI_06I"], errors="coerce") == 1.0).astype(int)
df["techUse"]     = (pd.to_numeric(df["TUI_07"],  errors="coerce") == 1.0).astype(int)
df["wellbeing"]   = (pd.to_numeric(df["TUI_15"],  errors="coerce") == 1.0).astype(int)
```

Add these columns to `OUTPUT_COLUMNS`.

**Why to do it**
Without these aliases, `HH_aggregation`'s `valid_social` list is always empty. `occDensity` is always 0, and the BEM formula `occPre × (occDensity + 1)` never counts co-presence — silently ignoring household social interaction for every time slot.

**Expected result**
`out22EP_ACT_PRE_coPRE.csv` includes `Spouse`, `Children`, `otherInFAMs`, and the other TUI aliases as binary integer columns.

**How to test**
- `df["Spouse"].isin([0, 1]).all()`
- `df["Spouse"].mean()` is reasonably close to `df["coPRE"].mean()` (not 0.0)
- After re-running aggregation, `occDensity` has a distribution above zero for home-present time slots

---

## C. Step 1: Alignment

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_alignment.py`.

### C1. Copy the 11CEN10GSS alignment skeleton and update paths

**What to do**  
Use `11CEN10GSS_alignment.py` as the starting structure for the new alignment module.

**How to do it**  
Copy and then edit:

- module docstring
- file names
- output directories
- target-year strings
- `main()` wiring

Keep these components:

- `assemble_households()`
- `data_alignment()`
- alignment summary helpers
- `check_value_alignment()`

Use `eSim_occ_utils.occ_config.BASE_DIR` for all occupancy-root paths.

**Why to do it**  
The 2021/2022 pipeline is still a legacy pipeline. Reusing the 2011 structure minimizes risk and keeps downstream behavior familiar.

**Expected result**  
A runnable alignment module with the correct new filenames and path structure.

**How to test**  
- Import the module without executing `main()`.
- Confirm there are no leftover `11CEN10GSS` file names in the new script.

### C2. Use `cen21_filtered.csv` as the default Census input

**What to do**  
Feed the alignment step from the cleaned Census CSV, not from raw fixed-width parsing.

**How to do it**  
Use:

`0_Occupancy/Outputs_CENSUS/cen21_filtered.csv`

as the primary census input. Treat `cen21.dat` and `cen21.sps` as reference material for code meanings, not the default runtime source.

Then run `assemble_households()` on the cleaned CSV to produce:

`0_Occupancy/Outputs_21CEN22GSS/alignment/2021_LINKED.csv`

**Why to do it**  
This avoids re-implementing Census preprocessing that already exists elsewhere in the repo and keeps the new pipeline focused on legacy alignment and matching.

**Expected result**  
`2021_LINKED.csv` exists and contains household-linked Census records with `SIM_HH_ID` and usable residential columns.

**How to test**  
- Output file exists.
- `SIM_HH_ID` is present.
- `HH_ID` is present.
- Household sizes are non-null and positive.

### C3. Read the GSS 2022 main SAS file and merge it onto episodes

**What to do**  
Implement the GSS main-file reader and merge step.

**How to do it**  
1. Read `GSSMain_2022.sas7bdat` with `pd.read_sas()`.
2. Keep only the required columns for V1:
   - `PUMFID`
   - `PRV`
   - `HSDSIZEC`
   - `AGEGR10`
   - `GENDER2`
   - `MARSTAT`
   - `LANHSDC`
   - `ACT7DAYC`
   - `LUC_RST`
   - `DDAY`
3. Rename `PUMFID -> occID` before the merge.
4. Merge onto `out22EP_ACT_PRE_coPRE.csv` using `occID`.
5. Save the merged result as:
   - `0_Occupancy/Outputs_21CEN22GSS/alignment/GSS_2022_Merged.csv`

Do not make `TOTINC` mandatory in V1. The mapping of `INC_C` should be treated as optional until verified.

**Why to do it**  
This creates the raw GSS library that alignment and profile matching depend on.

**Expected result**  
The merged GSS file has the same number of rows as the episode file and includes demographic columns plus exactly one `DDAY`.

**How to test**  
- Row count equals the Step 0 episode row count.
- `DDAY` exists.
- `DDAY.1` does not exist.
- `sorted(df["DDAY"].dropna().unique()) == [1,2,3,4,5,6,7]`

### C4. Finalize the core harmonization columns for V1

**What to do**  
Set the alignment target columns and matching columns for the first working version.

**How to do it**  
Use this V1 core set:

- `HHSIZE`
- `AGEGRP`
- `SEX`
- `MARSTH`
- `KOL`
- `PR`
- `LFTAG`
- `CMA`

Do not require `TOTINC`, `ATTSCH`, or `NOCS` for the first end-to-end implementation.

**Why to do it**  
These eight columns have the clearest implementation path from verified local files and existing scripts. They are enough to produce a usable first pipeline.

**Expected result**  
The alignment code has one explicit source of truth for the V1 target columns and the matcher uses the same set.

**How to test**  
- Search the alignment file and matcher file for the same column set.
- Run a unique-value comparison report after alignment.

### C5. Implement `harmonize_agegrp()`

**What to do**  
Map Census 2021 age groups to the 7-band GSS 2022 age groups.

**How to do it**  
Reuse the same Census-to-GSS age-band mapping already used in `11CEN10GSS` and the classification alignment:

- `1,2` -> drop
- `3,4` -> `1`
- `5,6` -> `2`
- `7,8` -> `3`
- `9,10` -> `4`
- `11` -> `5`
- `12` -> `6`
- `13+` -> `7`

On the GSS side, keep valid `AGEGR10` values `1..7`.

**Why to do it**  
Age is one of the highest-signal matching variables. If it is wrong, matching quality collapses.

**Expected result**  
Both aligned datasets use the same 7 age groups.

**How to test**  
- Unique values match exactly across Census and GSS.
- No under-15 Census records remain.

### C6. Implement `harmonize_hhsize()`

**What to do**  
Bring Census household size onto the same 2022 GSS scale.

**How to do it**  
Use the existing `HHSIZE` from `2021_LINKED.csv` or derive it inside household assembly if needed. Cap Census values to `5` because observed `HSDSIZEC` values in GSS 2022 are `1..5`.

Recommended rule:

- Census `>= 5 -> 5`
- GSS keep only `1..5`

**Why to do it**  
This is a required core matching variable and a critical fallback variable in lower matching tiers.

**Expected result**  
Both aligned datasets contain `HHSIZE` values only in `1..5`.

**How to test**  
- Census `HHSIZE.max() <= 5`
- GSS `HHSIZE.max() <= 5`
- No null `HHSIZE`

### C7. Implement `harmonize_sex()` with an explicit verification checkpoint

**What to do**  
Standardize Census 2021 `GENDER` and GSS 2022 `GENDER2` to a shared legacy `SEX` column.

**How to do it**  
1. On the Census side, explicitly reverse the verified `cen21.sps` coding:
   - `1=Woman+`
   - `2=Man+`
2. Output a legacy `SEX` convention compatible with older pipelines.
3. On the GSS side, inspect `GENDER2` carefully before freezing the direction.
4. Cross-check against the existing logic in:
   - `eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py`

Do not bury this logic in a one-line rename. Keep it as a named harmonization function with a printout of unique values before and after.

**Why to do it**  
This is the easiest place to introduce a silent, high-impact error.

**Expected result**  
Both aligned datasets contain only the two expected legacy sex codes.

**How to test**  
- Unique values match across both datasets.
- The function prints pre-map and post-map unique values.
- Matching output later shows reasonable tier distributions rather than extreme fallback.

### C8. Implement `harmonize_marsth()`

**What to do**  
Collapse Census 2021 and GSS 2022 marital-status codes into the 3-category legacy scheme.

**How to do it**  
Target categories:

- `1` = never married / single
- `2` = married or common-law
- `3` = separated / divorced / widowed

For Census 2021:

- `1 -> 1`
- `2,3 -> 2`
- `4 -> 3`

For GSS 2022:

- inspect `MARSTAT`
- filter out `99`
- collapse `1..6` into the same 3 legacy categories

**Why to do it**  
This is part of the core matcher and a stable demographic variable across years once recoded.

**Expected result**  
Both aligned datasets contain exactly the same 3 marital-status codes.

**How to test**  
- Unique values match across both datasets.
- No `99` remains in GSS.

### C9. Implement `harmonize_kol()`

**What to do**  
Use `LANHSDC` as the V1 language / KOL proxy and align it with Census `KOL`.

**How to do it**  
1. Rename `LANHSDC -> KOL` in the merged GSS file.
2. Keep only valid GSS values observed locally: `1..4`, drop `9`.
3. Decide whether to keep all `1..4` or only `1..3`.

Recommended V1 choice:

- keep `1..3`
- drop `4` on both sides if it represents a non-comparable “neither / other” bucket

That matches the simpler legacy practice in `11CEN10GSS` and `16CEN15GSS`.

**Why to do it**  
Language is useful for matching, but only if the categories mean the same thing on both sides.

**Expected result**  
A clean `KOL` column with the same category set in both aligned files.

**How to test**  
- Print unique values before filtering and after filtering.
- Confirm final unique values match across Census and GSS.

### C10. Implement `harmonize_pr()` and `harmonize_cma()`

**What to do**  
Collapse region and urbanicity to shared categories.

**How to do it**

For `PR`:

- aggregate raw Census and GSS province codes to the legacy regional scheme used by the older pipelines
- recommended output values:
  - Atlantic -> `10`
  - Quebec -> `24`
  - Ontario -> `35`
  - Prairies -> `46`
  - Alberta -> `48`
  - BC -> `59`
- drop territories unless you explicitly add a new shared category

For `CMA`:

- on the Census side, observed `CMA` values in `cen21_filtered.csv` are:
  - `462`, `535`, `825`, `835`, `933`, `999`
- map the first five to `1`
- map `999` to `2`
- on the GSS side, keep `LUC_RST` values `1` and `2` only for V1 and drop `3`

**Why to do it**  
Both variables are useful matching features, and both need reduction to cross-dataset categories.

**Expected result**  
`PR` and `CMA` each have identical unique value sets across both aligned outputs.

**How to test**  
- `set(df_census["PR"].unique()) == set(df_gss["PR"].unique())`
- `set(df_census["CMA"].unique()) == set(df_gss["CMA"].unique())`

### C11. Implement `harmonize_lftag()`

**What to do**  
Collapse Census 2021 `LFACT` and GSS 2022 `ACT7DAYC` to the labour-force scheme expected by legacy matchers.

**How to do it**  
Start from the logic already used in `16CEN15GSS_alignment.py`.

Recommended V1 mapping:

- Census `1 -> 1`
- Census `2..6 -> 2`
- Census `7..11 -> 3`
- Census `12,13 -> 4`
- Census `14 -> 5`
- Census invalid / NA -> drop

On the GSS side:

- rename `ACT7DAYC -> LFTAG`
- keep `1..5`
- drop `9`

**Why to do it**  
Labour-force status strongly shapes weekday occupancy behavior and is part of the core match set.

**Expected result**  
Aligned Census and GSS files share the same `LFTAG` categories.

**How to test**  
- Unique values match.
- No invalid categories remain.

### C12. Leave `TOTINC`, `ATTSCH`, and `NOCS` as optional follow-up tasks

**What to do**  
Do not make these variables blockers for the first working alignment.

**How to do it**  
1. Keep the code structure ready for future optional harmonizers.
2. Document why each one is deferred.
3. If one is added, add it behind a deliberate validation step rather than silently folding it into Tier 1.

**Why to do it**  
The first end-to-end pipeline is more valuable than a speculative “full-featured” matcher with unverified category mappings.

**Expected result**  
The first legacy 2021/2022 pipeline can run without guessing an income or occupation crosswalk.

**How to test**  
- Core alignment still produces non-empty outputs.
- The matcher works with the reduced column set.

### C13. Save aligned outputs and produce an alignment report

**What to do**  
Write the aligned Census and GSS CSVs and generate a readable value-alignment summary.

**How to do it**  
Save:

- `0_Occupancy/Outputs_21CEN22GSS/alignment/Aligned_Census_2022.csv`
- `0_Occupancy/Outputs_21CEN22GSS/alignment/Aligned_GSS_2022.csv`

Also save a text summary similar to the legacy pipelines.

**Why to do it**  
Alignment is the main risk surface. The report makes debugging possible without reading raw CSVs by hand.

**Expected result**  
Both aligned CSVs are non-empty and the summary report clearly shows which columns match and which do not.

**How to test**  
- Files exist.
- Both CSVs can be reloaded.
- The report prints the same target-column set expected by the matcher.

### C14. Filter ROOM outliers in Census alignment

**What to do**
Add a ROOM cap (`<= 15`) immediately after loading Census data in `21CEN22GSS_alignment.py`.

**How to do it**
In `data_alignment()`, after loading `cen21_filtered.csv`, add:

```python
if "ROOM" in df_census.columns:
    df_census["ROOM"] = pd.to_numeric(df_census["ROOM"], errors="coerce")
    df_census = df_census[df_census["ROOM"] <= 15].copy()
```

This removes records with physically implausible room counts (same fix applied in `11CEN10GSS_alignment.py`).

**Why to do it**
Census 2021 raw ROOM values include extreme outliers (the same `cen21_filtered.csv` source that produced max=88 in 11CEN10GSS). These pass through unmodified and appear as implausible tails in the BEM non-temporal ROOM distribution plot. About 47 households (<0.4%) are expected to be removed.

**Expected result**
`Aligned_Census_2022.csv` has `ROOM` values only in `[1, 15]`.

**How to test**
- `df_census["ROOM"].max() <= 15`
- Row count decreases by ~47 relative to the unfiltered run (or no rows if already filtered upstream)

---

## D. Step 2: Profile Matching

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_ProfileMatcher.py`.

### D1. Copy the 11CEN10GSS matcher and update Tier 1

**What to do**  
Reuse the existing tiered matcher structure and adapt only the filenames and Tier 1 column list.

**How to do it**  
Copy `11CEN10GSS_ProfileMatcher.py` and update:

- module name
- output names
- input aligned filenames
- Tier 1 columns

Recommended V1 Tier 1:

- `HHSIZE`
- `AGEGRP`
- `SEX`
- `MARSTH`
- `KOL`
- `PR`
- `LFTAG`
- `CMA`

Keep Tier 2 through Tier 5 exactly in the legacy pattern unless a concrete mismatch requires change.

**Why to do it**  
The matching logic already exists and is aligned with the rest of the legacy pipeline.

**Expected result**  
A working matcher with minimal new logic.

**How to test**  
- Import succeeds.
- Matcher runs on a small sample without crashing.
- Tier labels appear in the output.

### D2. Save matched keys and expanded schedules

**What to do**  
Produce the two standard matching outputs:

- matched IDs
- full schedule expansion

**How to do it**  
Keep the existing two-phase structure:

1. `MatchProfiler`
2. `ScheduleExpander`

Save outputs to:

- `ProfileMatching/21CEN22GSS_Matched_Keys_sample{pct}pct.csv`
- `ProfileMatching/21CEN22GSS_Full_Schedules_sample{pct}pct.csv`

Carry forward the key Census residential columns required by HH aggregation and BEM conversion.

**Why to do it**  
The aggregation stage depends on the expanded schedule table, not just on the matched IDs.

**Expected result**  
Full-schedule output looks like the `16CEN15GSS` sample output structure, with Census fields copied through and episode rows expanded per matched GSS record.
The expanded schedules also keep the preserved 2022 episode context fields and the harmonized alias names used by HH aggregation:

- `Alone`
- `Spouse`
- `Children`
- `otherInFAMs`
- `parents`
- `Friends`
- `otherHHs`
- `colleagues`
- `Others`
- `techUse`
- `wellbeing`

**How to test**  
- `MATCH_ID_WD` and `MATCH_ID_WE` have no nulls.
- `Day_Type` is present.
- Expanded schedules include Census residential columns like `Census_DTYPE`, `Census_BEDRM`, `Census_ROOM`, `Census_CONDO`, `Census_REPAIR`.

### D3. Generate a matching-quality report

**What to do**  
Write the same kind of tier-distribution validation text used by the legacy matcher modules.

**How to do it**  
Keep the existing validation-report logic and update filenames.

**Why to do it**  
You need fast visibility into whether the 2021/2022 mappings are producing good matches or falling through to fail-safe tiers.

**Expected result**  
A text report showing weekday and weekend tier distributions.

**How to test**  
- Validation file exists.
- Tier percentages sum to roughly 100 percent for both weekday and weekend.

---

## E. Step 3: Household Aggregation

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_HH_aggregation.py`.

### E1. Copy the legacy 5-minute aggregation workflow

**What to do**  
Reuse the existing household aggregation logic.

**How to do it**  
Copy `11CEN10GSS_HH_aggregation.py` and update:

- module names
- input/output filenames
- folder names

Do not rewrite the aggregation algorithm.

**Why to do it**  
This stage is already stable and downstream-compatible.

**Expected result**  
The new module creates a full 5-minute household schedule table with the same schema style as the `16CEN15GSS` output.
The aggregated 2022 output should also keep the preserved episode context columns and the derived household aliases needed by BEM conversion.

**How to test**  
- The aggregated CSV is created.
- Expected columns exist: `Time_Slot`, `occPre`, `occDensity`, `occActivity`, `SIM_HH_ID`, `Day_Type`.

### E2. Verify the household-time grid integrity

**What to do**  
Make sure aggregation produced complete daily grids.

**How to do it**  
For each `SIM_HH_ID` and `Day_Type`, count rows and verify a full 24-hour day at 5-minute resolution.

Expected rows per household-day:

- `288`

**Why to do it**  
Missing or duplicated time steps here will contaminate BEM schedules later.

**Expected result**  
Every grouped household-day has exactly `288` rows.

**How to test**  
- Group by `SIM_HH_ID` and `Day_Type`
- Check the group-size distribution
- Confirm the minimum and maximum are both `288`

### E3. Save aggregation validation artifacts

**What to do**  
Write the standard validation text and plot files.

**How to do it**  
Preserve the validation/report behavior from the reference pipeline and rename outputs for `21CEN22GSS`.

**Why to do it**  
This makes the new pipeline feel like the existing ones and supports quick quality checks.

**Expected result**  
Validation files exist under `HH_aggregation/`.

**How to test**  
- Text report exists.
- Plot file exists.
- Report mentions sample size and household counts.
 - Validation report states that all person-days have exactly `288` time slots.

---

## F. Step 4: Occupancy to BEM Conversion

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py`.

### F1. Copy the 11CEN10GSS BEM converter and replace the DTYPE map

**What to do**  
Reuse the resampling and BEM-schedule logic but simplify dwelling-type labels to the 2021 schema.

**How to do it**  
Copy `11CEN10GSS_occToBEM.py` and replace the 2011 `dtype_map` with:

```python
{
    "1": "SingleD",
    "2": "Apartment",
    "3": "OtherDwelling",
}
```

Keep the hourly resampling and metabolic-rate mapping logic unchanged unless the input schema forces a small edit.

**Why to do it**  
The 2021 dwelling-type variable is genuinely coarser. Pretending otherwise would create fake building categories.

**Expected result**  
Hourly BEM schedules with the same overall structure as `16CEN15GSS_BEM_Schedules_sample10pct.csv`, but with 3 dwelling-type labels.
The hourly output should carry forward the household-level residential fields from the aggregated file and should expose the 2021 dwelling-type labels as readable categories.

**How to test**  
- Output columns exist:
  - `SIM_HH_ID`
  - `Day_Type`
  - `Hour`
  - `HHSIZE`
  - `DTYPE`
  - `BEDRM`
  - `CONDO`
  - `ROOM`
  - `REPAIR`
  - `PR`
  - `Occupancy_Schedule`
  - `Metabolic_Rate`
- `DTYPE` only contains the 3 expected labels.

### F2. Verify hourly schedule integrity

**What to do**  
Confirm that the BEM table is structurally correct.

**How to do it**  
Group by `SIM_HH_ID` and `Day_Type` and check the hourly rows.

Expected rows per household-day:

- `24`

Also check:

- `Occupancy_Schedule` stays within `[0, 1]`
- `Metabolic_Rate >= 0`

**Why to do it**  
This is the last stage before the schedules are used by BEM integration.

**Expected result**  
A clean hourly schedule table with no out-of-range occupancy values.

**How to test**  
- Group-size check equals `24`
- Occupancy min/max check
- Metabolic rate min check

### F3. Save the standard temporal and non-temporal plots

**What to do**  
Generate the same validation graphics produced by the other pipelines.

**How to do it**  
Keep the legacy plotting helper and rename the output files:

- `21CEN22GSS_BEM_temporals.png`
- `21CEN22GSS_BEM_non_temporals.png`

**Why to do it**  
These plots provide a fast visual check that the occupancy fractions and daily rhythms are sensible.

**Expected result**  
Both plot files exist in `occToBEM/`.

**How to test**  
- Both plot files exist.
- They open without error.

### F4. Write a short BEM validation report

**What to do**  
Save a compact text report summarizing the hourly conversion checks.

**How to do it**  
Write a text file under `occToBEM/` with:

- household-day row count check
- occupancy range check
- metabolic rate range check
- sample-household sanity check

**Why to do it**  
The report gives a quick record that the hourly conversion completed cleanly without inspecting the CSV manually.

**Expected result**  
A BEM validation text file exists next to the CSV and plots.

**How to test**  
- Text file exists.
- It mentions the 24-row household-day check.
- It mentions the occupancy and metabolic rate range checks.

---

## G. Main Controller

Create `eSim_occ_utils/21CEN22GSS/21CEN22GSS_main.py`.

### G1. Copy the 11CEN10GSS controller and keep a 4-step menu

**What to do**  
Create the interactive controller for the new pipeline.

**How to do it**  
Copy `11CEN10GSS_main.py` and update:

- title strings
- imported module filenames
- full-pipeline menu numbering

Keep:

- Step 1: Alignment
- Step 2: Profile Matching
- Step 3: HH Aggregation
- Step 4: BEM Conversion
- full-pipeline run option
- sample-percentage option

Do not add a DTYPE-expansion step.

**Why to do it**  
This preserves the user-facing behavior of the legacy pipelines while respecting the simpler 2021 dwelling-type structure.

**Expected result**  
The new controller launches and can call each stage independently.
The interactive menu references `21CEN22GSS` and exposes the 4-step workflow plus the sample-percentage utility.

**How to test**  
- Import the module.
- Run the script and confirm the menu text references `21CEN22GSS`.
- Confirm each action points to the correct new module file.

---

## H. Final Integration Checks

### H1. Run narrow smoke tests before any large sample run

**What to do**  
Perform the smallest useful end-to-end checks.

**How to do it**  
Recommended order:

1. import Step 0, alignment, matcher, aggregation, BEM modules
2. run Step 0
3. run alignment
4. run `sample_pct=1` or `sample_pct=10` through matching, aggregation, and BEM conversion

**Why to do it**  
This localizes failures and avoids wasting time on heavy runs before the schema is stable.

**Expected result**  
A small sample completes and writes files in every output subfolder.
The 2021/2022 pipeline can be imported module-by-module without syntax errors, and the 1% sample artifacts already exist from the staged runs.

**How to test**  
- Check that each expected output file exists.
- Confirm no stage is empty.

### H2. Decide whether `TOTINC` becomes a V1.1 enhancement

**What to do**  
Make a deliberate decision on income handling after the first working pipeline exists.

**How to do it**  
Only after V1 works:

1. verify the meaning of `INC_C` from local documentation or trusted existing code
2. if the mapping is defensible, add `harmonize_totinc()`
3. then decide whether to add `TOTINC` back into Tier 1

**Why to do it**  
Income can help matching, but a guessed mapping is worse than no mapping.

**Expected result**  
A conscious documented choice rather than a silent assumption.
For V1, `TOTINC` remains deferred because the `INC_C` crosswalk has not been verified tightly enough to justify a Tier 1 income feature.

**How to test**  
- If implemented, `TOTINC` unique values match across aligned datasets.
- If not implemented, the plan and code both clearly say it is deferred.

---

## I. Bug Fix Validation Pass

These tasks apply **after** completing B4–B6 and C14. They verify that the three confirmed bugs and one silent bug are no longer present in the pipeline output.

### I1. Re-run the pipeline and validate the output plots

**What to do**
After fixing step0 and alignment, re-run the full pipeline on a small sample and inspect the BEM temporal and non-temporal plots.

**How to do it**
Run in order:
1. `python 21CEN22GSS_step0.py` — regenerates `out22EP_ACT_PRE_coPRE.csv` with `occACT`, `start`, `end`, and social alias columns
2. `python 21CEN22GSS_alignment.py` — applies ROOM filter, reads updated episode file
3. `python 21CEN22GSS_ProfileMatcher.py --sample 10`
4. `python 21CEN22GSS_HH_aggregation.py --sample 10`
5. `python 21CEN22GSS_occToBEM.py --sample 10`

Then inspect:
- `occToBEM/21CEN22GSS_BEM_temporals.png`
- `occToBEM/21CEN22GSS_BEM_non_temporals.png`

**Why to do it**
The pipeline ran without crashing before the bugs were identified. A clean run is not sufficient — the plots must show physically correct occupancy behavior.

**Expected result**
All five checks below pass.

**How to test**

| Check | Pass criterion |
|-------|---------------|
| Diurnal occupancy (temporal plot) | Average presence clearly peaks at night (~0.7–0.9) and dips during work hours (9–17h weekdays); not flat |
| Metabolic rate distribution (temporal plot) | Spread from ~70 W (Sleep) to ~200 W; no single massive spike at 100 W |
| Sample household weekday (temporal plot) | Dynamic trace: departure dip and evening return visible; not a constant flat line |
| ROOM distribution (non-temporal plot) | No tail beyond 15 rooms |
| occDensity check | After aggregation, `occDensity > 0` for a substantial fraction of `occPre==1` rows; not all zeros |

If any check fails, diagnose against `debug_11CEN10GSS.md` reproduction notes before changing code.

---

## Progress Log

### 2026-03-31

| Task | Report | Result | Test |
|------|--------|--------|------|
| A1 | Created `eSim_occ_utils/21CEN22GSS/__init__.py` and established the new package scaffold for the 2021/2022 pipeline. | Package folder now exists and can be imported as a module package marker. | Verified the package directory was missing before creation, then added the marker file. |
| B1-B3 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_step0.py`, parsed `TU_ET_2022_Episode_PUMF.sas7bdat`, derived `PRE` and `coPRE`, and saved the canonical episode CSV. | `out22EP_ACT_PRE_coPRE.csv` now exists in the episode folder and the compatibility copy is present in `Outputs_GSS`. | Ran the script successfully; output reported `168,078` rows, `12,336` respondents, `PRE mean=0.723`, and `coPRE mean=0.335`. |
| C1-C13 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_alignment.py`, assembled Census 2021 from `cen21_filtered.csv`, merged GSS 2022 main/episode files, and harmonized the core matching columns. | `2021_LINKED.csv`, `GSS_2022_Merged.csv`, `Aligned_Census_2022.csv`, `Aligned_GSS_2022.csv`, and alignment summary files were written under `Outputs_21CEN22GSS/alignment`. | Ran the script end to end; the final alignment check showed matches for `AGEGRP`, `HHSIZE`, `SEX`, `MARSTH`, `KOL`, `PR`, `LFTAG`, and `CMA`. |
| D1-D3 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_ProfileMatcher.py`, kept the legacy tiered matching flow, and saved the sample matching outputs plus validation report. | `21CEN22GSS_Matched_Keys_sample1pct.csv`, `21CEN22GSS_Full_Schedules_sample1pct.csv`, and `21CEN22GSS_Validation_sample1pct.txt` were written under `Outputs_21CEN22GSS/ProfileMatching`. | Ran the matcher on a 1% sample successfully. `MATCH_ID_WD` and `MATCH_ID_WE` were populated, and the expanded schedules retained the episode context columns plus the derived alias fields. |
| E1-E3 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_HH_aggregation.py`, reused the legacy 5-minute household aggregation flow, and wrote the aggregated output plus validation artifacts. | `21CEN22GSS_Full_Aggregated_sample1pct.csv`, `21CEN22GSS_Validation_HH_sample1pct.txt`, and `21CEN22GSS_Validation_Plot_sample1pct.png` were written under `Outputs_21CEN22GSS/HH_aggregation`. | Ran the aggregator on the 1% matching sample successfully. The validation report confirmed all `5,722` person-days had exactly `288` time slots, and the presence/density/activity checks passed. |
| F1-F4 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py`, reused the legacy hourly resampling flow, and wrote the BEM output plus validation artifacts. | `21CEN22GSS_BEM_Schedules_sample1pct.csv`, `21CEN22GSS_Validation_BEM_sample1pct.txt`, `21CEN22GSS_BEM_temporals.png`, and `21CEN22GSS_BEM_non_temporals.png` were written under `Outputs_21CEN22GSS/occToBEM`. | Ran the converter on the 1% aggregation sample successfully. The validation report confirmed all `2,950` household-days had exactly `24` hourly rows, with occupancy in `[0,1]` and non-negative metabolic rates. |
| G1 | Created `eSim_occ_utils/21CEN22GSS/21CEN22GSS_main.py`, wired the new modules into a 4-step controller, and preserved the sample-percentage menu option. | The controller now launches an interactive `21CEN22GSS` menu and can dispatch Alignment, Profile Matching, HH Aggregation, BEM Conversion, or the full pipeline. | Ran `python3 eSim_occ_utils/21CEN22GSS/21CEN22GSS_main.py --help` successfully; the parser exposes `--sample` and `--run {1,2,3,4,5}`. |
| H1-H2 | Performed the final smoke-test pass by importing all six `21CEN22GSS` modules and reviewing the integration checks. | The pipeline modules import cleanly, the staged 1% artifacts already exist in every output folder, and `TOTINC` stays deferred in V1. | Imported `21CEN22GSS_step0`, `21CEN22GSS_alignment`, `21CEN22GSS_ProfileMatcher`, `21CEN22GSS_HH_aggregation`, `21CEN22GSS_occToBEM`, and `21CEN22GSS_main` without syntax errors. |
| I1 | Re-ran the 1% end-to-end pipeline after the bug fixes, then checked the regenerated episode, alignment, aggregation, and BEM outputs. | `out22EP_ACT_PRE_coPRE.csv` now includes harmonized `occACT`, HHMM `start`/`end`, and social alias columns; `ROOM` is capped at 11 in the aligned Census output; the 1% BEM run shows nighttime occupancy above daytime occupancy and metabolic rates spanning 0–245 W. | Verified `occACT` stays in `1..14`, `occDensity` is positive for a majority of home-present slots, and the BEM validation report still passes the 24-row and non-negative checks. |
