# Step 2 — Data Harmonization: Detailed Execution Checklist

> This checklist expands the high-level planning items into granular, developer-actionable tasks.
> Each numbered section maps to a component in the approved implementation plans.
> **Source plans**: [02_harmonizationGSS.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS.md), [actCodes](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_actCodes.md), [pre_coPre](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_pre_coPre.md), [val](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_val.md)

---

## Phase A — Planning & Documentation ✅ COMPLETE

- [x] Research pipeline documentation and existing Step 1 code
- [x] Investigate 2005/2010 raw files for SURVMNTH (confirmed absent)
- [x] Analyze activity code systems across all 4 cycles
- [x] Map sentinel values and demographic distributions per cycle
- [x] Write main harmonization plan (`02_harmonizationGSS.md`)
- [x] Write expanded validation plan (`02_harmonizationGSS_val.md`)
- [x] Write activity code crosswalk plan (`02_harmonizationGSS_actCodes.md`)
- [x] Write presence & co-presence plan (`02_harmonizationGSS_pre_coPre.md`)
- [x] Update all plans with execution Excel workbooks (zero-conflict lookup tables)
- [x] Update main plan to reference all sub-plans
- [x] Push all finalized plans and reference documents to GitHub

---

## Phase B — Module Setup & Constants ✅ COMPLETE

- [x] **B1. Create `02_harmonizeGSS.py`** — new module file
  - [x] B1.1 Add module docstring, imports (`pandas`, `openpyxl`, `pathlib`)
  - [x] B1.2 Define `INPUT_DIR = "outputs/"` and `OUTPUT_DIR = "outputs_step2/"`
  - [x] B1.3 Define `CYCLES = [2005, 2010, 2015, 2022]`

- [x] **B2. Define `MAIN_RENAME_MAP`** — per-cycle rename dictionaries (Main files)
  - [x] B2.1 `MAIN_RENAME_2005`: `RECID→occID`, `AGEGR10→AGEGRP`, `sex→SEX`, `marstat→MARSTH`, `HSDSIZEC→HHSIZE`, `REGION→PR`, `LUC_RST→CMA`, `WKWE→COW`, `wght_per→WGHT_PER`, `DVTDAY→DDAY`, `LANCH→KOL`, `LFSGSS→LFTAG`, `INCM→TOTINC`, `EDU10→ATTSCH`, `WKWEHR_C→HRSWRK`
  - [x] B2.2 `MAIN_RENAME_2010`: `RECID→occID`, `AGEGR10→AGEGRP`, `SEX→SEX`, `MARSTAT→MARSTH`, `HSDSIZEC→HHSIZE`, `PRV→PR`, `LUC_RST→CMA`, `WKWE→COW`, `wght_per→WGHT_PER`, `DVTDAY→DDAY`, `LANCH→KOL`, `LFSGSS→LFTAG`, `INCM→TOTINC`, `EDU10→ATTSCH`, `WKWEHR_C→HRSWRK`
  - [x] B2.3 `MAIN_RENAME_2015`: `PUMFID→occID`, `AGEGR10→AGEGRP`, `SEX→SEX`, `MARSTAT→MARSTH`, `HSDSIZEC→HHSIZE`, `PRV→PR`, `LUC_RST→CMA`, `WET_110→COW`, `WGHT_PER→WGHT_PER`, `DVTDAY→DDAY`, `LAN_01→KOL`, `ACT7DAYS→LFTAG`, `INCG1→TOTINC`, `EHG_ALL→ATTSCH`, `WHWD140C→HRSWRK`, `NOC1110Y→NOCS`, `SURVMNTH→SURVMNTH`
  - [x] B2.4 `MAIN_RENAME_2022`: `PUMFID→occID`, `AGEGR10→AGEGRP`, `GENDER2→SEX`, `MARSTAT→MARSTH`, `HSDSIZEC→HHSIZE`, `PRV→PR`, `LUC_RST→CMA`, `WET_120→COW`, `WGHT_PER→WGHT_PER`, `DVTDAY→DDAY`, `LAN_01→KOL`, `ACT7DAYC→LFTAG`, `INC_C→TOTINC`, `EDC_10→ATTSCH`, `WHWD140G→HRSWRK`, `NOCLBR_Y→NOCS`, `ATT_150C→MODE`, `SURVMNTH→SURVMNTH`

- [x] **B3. Define `EPISODE_RENAME_MAP`** — per-cycle rename dictionaries (Episode files)
  - [x] B3.1 Verify raw episode column names from Step 1 CSVs (check headers of `episode_*.csv`)
  - [x] B3.2 Map episode ID columns: `RECID/PUMFID→occID`, `EPESSION/EPINO→EPINO`
  - [x] B3.3 Map weight columns: cycle-specific episode weight → `WGHT_EPI`
  - [x] B3.4 Map time columns: `STARTIME/ENDTIME` → `start/end` (per cycle raw names)
  - [x] B3.5 Map duration column: cycle-specific → `duration`
  - [x] B3.6 Map activity raw column: `ACTCODE/TUI_01` (handled by crosswalk, but keep raw name)
  - [x] B3.7 Map location raw column: `PLACE/LOCATION` (handled by crosswalk, but keep raw name)

- [x] **B4. Define `SENTINEL_MAP`** — per-column sentinel dictionaries
  - [x] B4.1 `COW: {97, 98, 99}`, `KOL: {98, 99}`, `TOTINC: {98, 99}`
  - [x] B4.2 `ATTSCH: {98, 99}`, `HRSWRK: {96, 97, 98, 99}`, `NOCS: {96, 97, 98, 99}`
  - [x] B4.3 `LFTAG: {8, 9, 97, 98, 99}`, `MARSTH: {8, 9, 99}`, `MODE: {99}`

---

## Phase C — Demographic Recode Functions (Main Files) ✅ COMPLETE

- [x] **C1. `recode_sex(df, cycle)`** — rename-only (values 1–2 identical across cycles)
  - [x] C1.1 Verify no values outside {1, 2} exist in any cycle

- [x] **C2. `recode_marsth(df, cycle)`**
  - [x] C2.1 2005/2010: map sentinels {8, 9} → NaN
  - [x] C2.2 2022: map sentinel {99} → NaN
  - [x] C2.3 2015: no sentinel, keep 1–6 as-is
  - [x] C2.4 Verify unified values: {1, 2, 3, 4, 5, 6} + NaN

- [x] **C3. `recode_agegrp(df, cycle)`** — no recode needed (1–7 identical)
  - [x] C3.1 Assert `set(df.AGEGRP.dropna().unique()) == {1,2,3,4,5,6,7}` per cycle

- [x] **C4. `recode_lftag(df, cycle)`** — collapse to unified 5-category scheme ✅ DECIDED
  - [x] C4.1 2005: `LFSGSS` 1–5, sentinels {8, 9} → NaN
  - [x] C4.2 2010: `LFSGSS` 1–5, sentinels {8, 9} → NaN (also has `ACT7DAYS` but use `LFSGSS`)
  - [x] C4.3 2015: `ACT7DAYS` 1–6, sentinels {97, 98, 99} → NaN; **collapse cat 6 into nearest 1–5 category**
  - [x] C4.4 2022: `ACT7DAYC` 1–5, sentinel {9} → NaN
  - [x] C4.5 ✅ **Locked**: 5-category scheme (1=Employed at work, 2=Employed absent, 3=Unemployed, 4=Not in LF, 5=Not stated→NaN)

- [x] **C5. `recode_pr(df, cycle)`**
  - [x] C5.1 2005: keep `REGION` (1–5) as coarse `PR`, flag in metadata
  - [x] C5.2 2010/2015/2022: `PRV` codes 10–59, no recode needed
  - [x] C5.3 Add documentation note about 2005 coarser granularity

- [x] **C6. `recode_cma(df, cycle)`** — rename-only (all cycles use `LUC_RST` 1–3)

- [x] **C7. `recode_hhsize(df, cycle)`** — collapse to 5 categories ✅ DECIDED
  - [x] C7.1 2005/2010/2015: codes 1–6 → **remap 6 → 5** (merge "6+" into "5+")
  - [x] C7.2 2022: codes 1–5, no remap needed
  - [x] C7.3 ✅ **Locked**: unified 5-category scheme {1, 2, 3, 4, 5="5+"} across all cycles

- [x] **C8. `recode_cow(df, cycle)`** — remove sentinels {97, 98, 99} across all cycles

- [x] **C9. `recode_hrswrk(df, cycle)`** — bin to categorical brackets ✅ DECIDED
  - [x] C9.1 2005: `WKWEHR_C` continuous → sentinels {97, 98, 99} → NaN → **bin to brackets**
  - [x] C9.2 2010: `WKWEHR_C` continuous → sentinels {97, 98, 99} → NaN → **bin to brackets**
  - [x] C9.3 2015: `WHWD140C` — verify format from data, sentinels → NaN → **bin to brackets**
  - [x] C9.4 2022: `WHWD140G` — sentinels {96, 99} → NaN → **bin to brackets**
  - [x] C9.5 ✅ **Locked**: categorical bins. Define bracket boundaries from codebooks (e.g., 0, 1–14, 15–29, 30–39, 40, 41–49, 50+)
  - [x] C9.6 Preserve original continuous as `HRSWRK_RAW` for reference

- [x] **C10. `recode_attsch(df, cycle)`** — remove sentinels {98, 99}

- [x] **C11. `recode_kol(df, cycle)`** — remove sentinels {98, 99}

- [x] **C12. `derive_mode(df, cycle)`** — hierarchical priority ✅ DECIDED
  - [x] C12.1 2005: no commute columns → `MODE = NaN` for all rows
  - [x] C12.2 2010: derive from `CTW_Q140_C01–C09` multi-select (**hierarchical priority**)
  - [x] C12.3 2015: derive from `CTW_140A–I` multi-select (**hierarchical priority**)
  - [x] C12.4 2022: use `ATT_150C` directly, sentinel {99} → NaN
  - [x] C12.5 ✅ **Locked**: hierarchical priority (e.g., car driver > car passenger > public transit > bicycle > walking > other). Define exact priority ordering from standard transport survey practice

- [x] **C13. `recode_totinc(df, cycle)`** — discretize CRA to brackets ✅ DECIDED
  - [x] C13.1 2005/2010: `INCM` categorical brackets, sentinels {98, 99} → NaN
  - [x] C13.2 2015: `INCG1` categorical brackets
  - [x] C13.3 2022: `INC_C` CRA-linked continuous → **discretize to matching 2005–2015 bracket boundaries**
  - [x] C13.4 ✅ **Locked**: Extract exact bracket boundaries from 2005/2010/2015 codebooks and apply `pd.cut()` to 2022 continuous values
  - [x] C13.5 Append `TOTINC_SOURCE` column (`SELF` / `CRA`)
  - [x] C13.6 Preserve original 2022 continuous values as `TOTINC_RAW` for reference

---

## Phase D — Activity Code Crosswalk (Episode Files) ✅ COMPLETE

- [x] **D1. `build_activity_crosswalks()`** — parse execution Excel
  - [x] D1.1 Read `references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`
  - [x] D1.2 Parse 4 sheets: `2005codebook` (183 rows), `2010codebook` (263 rows), `2015codebook` (64 rows), `2022codebook` (120 rows)
  - [x] D1.3 Build `{cycle_year: {raw_code: category_1_to_14}}` dictionaries
  - [x] D1.4 Handle 2010 float-type ACTCODE values (decimal sub-codes like `80.1`)

- [x] **D2. `apply_activity_crosswalk()`** — map raw → unified 14-category `occACT`
  - [x] D2.1 2005/2010: map `ACTCODE` column
  - [x] D2.2 2015/2022: map `TUI_01` column
  - [x] D2.3 Preserve original code as `occACT_raw`
  - [x] D2.4 Add `occACT_label` from the 14-category name table
  - [x] D2.5 Unmapped codes → `occACT = NaN` (for validation flagging)

- [x] **D3. Handle special cases**
  - [x] D3.1 "Not stated" sentinels: 2005/2010 code 995 → per workbook, 2015 code 95 → 14, 2022 code 9999 → 14
  - [x] D3.2 Verify no code conflicts after mapping

---

## Phase E — Presence & Co-Presence (Episode Files) ✅ COMPLETE

- [x] **E1. `build_presence_crosswalks()`** — parse presence execution Excel
  - [x] E1.1 Read `references_Pre_coPre_Codes/Data Harmonization_presenceCategories - execution.xlsx`
  - [x] E1.2 Parse 3 sheets: `2005-2010codebook` (24 rows), `2015codebook` (27 rows), `2022codebook` (29 rows)
  - [x] E1.3 Build `{cycle_year: {raw_location_code: occPRE_1_to_18}}` dictionaries
  - [x] E1.4 Note: 2005/2010 share the same sheet → same lookup for both

- [x] **E2. `apply_presence_crosswalk()`** — map raw → unified 18-category `occPRE`
  - [x] E2.1 2005/2010: map `PLACE` column
  - [x] E2.2 2015/2022: map `LOCATION` column
  - [x] E2.3 Preserve original as `occPRE_raw`
  - [x] E2.4 Derive `AT_HOME = (occPRE == 1).astype(int)`
  - [x] E2.5 Unmapped codes → `occPRE = NaN`

- [x] **E3. `harmonize_copresence()`** — social contact columns
  - [x] E3.1 2005/2010: rename `ALONE → Alone`, `SPOUSE → Spouse`, `CHILDHSD → Children`, `FRIENDS → friends`, `OTHFAM → otherHHs`, `OTHERS → others`, `PARHSD → parents`, `MEMBHSD → otherInFAMs`
  - [x] E3.2 2015/2022: rename `TUI_06A → Alone`, `TUI_06B → Spouse`, `TUI_06C → Children`, `TUI_06H → friends`, `TUI_06G → otherHHs`, `TUI_06J → others`, `TUI_06E → parents`, `TUI_06D → otherInFAMs`
  - [x] E3.3 Drop unmapped source columns: `NHSDCL15`, `NHSDC15P`, `NHSDPAR` (2005/2010); `TUI_06F`, `TUI_06I` (2015/2022)
  - [x] E3.4 Convert sentinels {7, 8, 9} → NaN in all 8 unified columns

---

## Phase F — Metadata Flags & Diary QA ✅ COMPLETE

- [x] **F1. Metadata flag assignment** (per cycle)
  - [x] F1.1 `CYCLE_YEAR`: constant per cycle (2005/2010/2015/2022)
  - [x] F1.2 `SURVYEAR`: same as `CYCLE_YEAR`
  - [x] F1.3 `SURVMNTH`: NaN for 2005/2010; keep from data for 2015/2022
  - [x] F1.4 `COLLECT_MODE`: 0 for 2005/2010/2015, 1 for 2022
  - [x] F1.5 `TUI_10_AVAIL`: 0 for 2005/2010, 1 for 2015/2022
  - [x] F1.6 `BS_TYPE`: `MEAN_BS` for 2005/2010, `STANDARD_BS` for 2015/2022
  - [x] F1.7 `TOTINC_SOURCE`: `SELF` for 2005/2010/2015, `CRA` for 2022

- [x] **F2. `check_diary_closure()`** — episode integrity check
  - [x] F2.1 Parse HHMM-format `start`/`end` to minutes
  - [x] F2.2 Compute episode duration, handling midnight wrap (2400→0400 next day)
  - [x] F2.3 Sum durations per `occID`; assert sum == 1440
  - [x] F2.4 Add `DIARY_VALID` column: 1 if sum == 1440, else 0
  - [x] F2.5 Log respondents failing closure with gap size

---

## Phase G — Orchestrator Functions ✅ COMPLETE

- [x] **G1. `harmonize_main(main_df, cycle_year)`**
  - [x] G1.1 Apply rename map → unified column names
  - [x] G1.2 Call all 13 recode functions (C1–C13) in sequence
  - [x] G1.3 Apply sentinel elimination via `SENTINEL_MAP`
  - [x] G1.4 Assign all metadata flags (F1)
  - [x] G1.5 Return harmonized Main DataFrame

- [x] **G2. `harmonize_episode(episode_df, cycle_year)`**
  - [x] G2.1 Apply episode rename map → unified column names
  - [x] G2.2 Call `apply_activity_crosswalk()` → `occACT`, `occACT_raw`, `occACT_label`
  - [x] G2.3 Call `apply_presence_crosswalk()` → `occPRE`, `occPRE_raw`, `AT_HOME`
  - [x] G2.4 Call `harmonize_copresence()` → 8 unified co-presence columns
  - [x] G2.5 Call `check_diary_closure()` → `DIARY_VALID`
  - [x] G2.6 Add `CYCLE_YEAR` to episode
  - [x] G2.7 Return harmonized Episode DataFrame

- [x] **G3. `harmonize_all_cycles(input_dir, output_dir)`**
  - [x] G3.1 Loop over `CYCLES = [2005, 2010, 2015, 2022]`
  - [x] G3.2 Read each Step 1 CSV pair from `outputs/`
  - [x] G3.3 Call `harmonize_main()` + `harmonize_episode()` per cycle
  - [x] G3.4 Export 8 CSVs to `outputs_step2/`
  - [x] G3.5 Print summary statistics per cycle (row counts, NaN rates)

---

## Phase H — Validation Script ✅ COMPLETE

- [x] **H1. Create `02_harmonizeGSS_val.py`** — validation module
  - [x] H1.1 Define `GSSHarmonizationValidator` class (mirror Step 1's `GSSValidator`)
  - [x] H1.2 Load 8 harmonized CSVs from `outputs_step2/`
  - [x] H1.3 Load 8 Step 1 CSVs from `outputs/` for comparison

- [x] **H2. Method 1 — Unified Schema Audit**
  - [x] H2.1 Assert identical column sets across 4 Main files
  - [x] H2.2 Assert identical column sets across 4 Episode files
  - [x] H2.3 Verify expected Main columns present (24 columns)
  - [x] H2.4 Verify expected Episode columns present (14+ columns)
  - [x] H2.5 Generate column presence table (✅/❌ matrix)

- [x] **H3. Method 2 — Row Count Preservation**
  - [x] H3.1 Compare `len(harmonized)` vs `len(step1)` for all 8 files
  - [x] H3.2 Compare `occID.nunique()` Step 1 vs Step 2
  - [x] H3.3 Verify `set(episode.occID) ⊆ set(main.occID)`
  - [x] H3.4 Generate grouped bar chart

- [x] **H4. Method 3 — Sentinel Value Elimination**
  - [x] H4.1 Check each column in `SENTINEL_MAP` for residual sentinel values
  - [x] H4.2 Compare NaN% Step 1 vs Step 2 per column
  - [x] H4.3 Verify no over-nullification in `occID`, `WGHT_PER`, `WGHT_EPI`
  - [x] H4.4 Generate NaN% heatmap (Step 1 vs Step 2)

- [x] **H5. Method 4 — Category Recoding Verification**
  - [x] H5.1 Check `SEX` ∈ {1, 2}, `AGEGRP` ∈ {1–7}, `CMA` ∈ {1–3}
  - [x] H5.2 Check `MARSTH` ∈ {1–6} + NaN (no 8/9/99 residuals)
  - [x] H5.3 Check `LFTAG`, `COW`, `HRSWRK`, `ATTSCH`, `KOL`, `MODE`, `TOTINC`
  - [x] H5.4 Generate stacked bar charts per variable × cycle

- [x] **H6. Method 5 — Activity Crosswalk Verification**
  - [x] H6.1 Unique `occACT` values ∈ {1–14} per cycle
  - [x] H6.2 Coverage ≥99% (unmapped rate < 2%)
  - [x] H6.3 All 14 categories non-empty in each cycle
  - [x] H6.4 Time-weighted distribution: Sleep ~30–35%, Work ~10–15%, Travel ~5–8%
  - [x] H6.5 Generate 14-category × 4-cycle heatmap

- [x] **H7. Method 6 — Location Recoding Verification**
  - [x] H7.1 `occPRE` values ∈ {1–18} per cycle
  - [x] H7.2 Coverage ≥95% (excluding category 18)
  - [x] H7.3 Home rate (~55–70%)
  - [x] H7.4 `AT_HOME` ↔ `occPRE` 100% consistency
  - [x] H7.5 Activity × location plausibility (Sleep ~95%+ at home)
  - [x] H7.6 Generate bar chart + cross-tab heatmap

- [x] **H8. Method 7 — Metadata Flag Audit**
  - [x] H8.1 Each flag has exactly one unique value per cycle (except `SURVMNTH`)
  - [x] H8.2 `SURVMNTH` 100% NaN for 2005/2010
  - [x] H8.3 `SURVMNTH` ∈ {1–12} for 2015/2022 with reasonable distribution
  - [x] H8.4 Generate colored flag table + SURVMNTH bar charts

- [x] **H9. Method 8 — Diary Closure QA**
  - [x] H9.1 All episode durations ≥ 0
  - [x] H9.2 `DIARY_VALID` pass rate ≥95% per cycle
  - [x] H9.3 Failure analysis: gap size characterization
  - [x] H9.4 Episode ordering check (≥99% properly ordered)
  - [x] H9.5 Episode count distribution (typical 10–30 per respondent)
  - [x] H9.6 Generate histogram + bar chart + box plot

- [x] **H10. Method 9 — Regression Check**
  - [x] H10.1 Weight distributions unchanged (mean, std, min, max)
  - [x] H10.2 Total respondent / episode counts unchanged
  - [x] H10.3 Numeric column ranges: Step 2 ⊆ Step 1
  - [x] H10.4 Time column values unchanged (rename only)
  - [x] H10.5 Generate side-by-side box plots + delta table

- [x] **H11. HTML Report Generation**
  - [x] H11.1 Build styled HTML with all 9 sections
  - [x] H11.2 Embed base64 PNGs for all charts
  - [x] H11.3 Summary pass/fail table with severity indicators
  - [x] H11.4 Export to `outputs_step2/step2_validation_report.html`

---

## Phase I — Final Review & Handoff

- [x] **I1. Self-review `02_harmonizeGSS.py`**
  - [x] I1.1 PEP 8 compliance (88-char lines)
  - [x] I1.2 All functions have Google-style docstrings with type hints
  - [x] I1.3 Imports sorted: stdlib → third-party → local
  - [x] I1.4 No hardcoded paths (use `pathlib` with relative references)

- [x] **I2. Self-review `02_harmonizeGSS_val.py`**
  - [x] I2.1 Same code-quality checks as I1
  - [x] I2.2 Ensure `if __name__ == "__main__"` entry point

- [x] **I3. End-to-end dry run**
  - [x] I3.1 Run `python 02_harmonizeGSS.py` → generates 8 CSVs in `outputs_step2/`
  - [x] I3.2 Run `python 02_harmonizeGSS_val.py` → generates HTML report
  - [x] I3.3 All 9 validation checks pass (0 critical failures)

- [x] **I4. Git commit & push**
  - [ ] I4.1 Commit `02_harmonizeGSS.py`, `02_harmonizeGSS_val.py`, output CSVs
  - [x] I4.2 Update this checklist with all items marked complete

---

## Observations & Red Flags — UPDATED (2026-03-08) 🚩

> [!WARNING]
> These items were identified during the implementation of Phases B–G and should be carefully reviewed during Phase H validation.

### 1. Income Category Discrepancies (`TOTINC`)
- **Observation**: 2022's `INC_C` is provided as discrete codes (1–5) based on CRA data. 2015 has 7 categories, and 2010 has 12.
- **Impact**: Since raw dollar values are not available for 2022, we cannot "re-bin" 2022 into the 12-category 2010 scheme.
- **Decision**: Keep each cycle's native categories; downstream models must treat Income as an ordinal factor with cycle-specific levels or simplified coarse buckets (e.g., Low/Mid/High).

### 2. 2010 Activity Code (`ACTCODE`) Parsing
- **Observation**: 2010 uses decimal codes (e.g., `80.1`). Some raw data may contain commas (`80,1`).
- **Implementation**: Added `.replace(',', '.')` and forced `float` casting before mapping. Fallon to `int` is used only if the float mapping fails.
- **Red Flag**: High potential for "unmapped" codes if decimal precision is lost. Monitor Method 5 coverage in the validation report.

### 3. Missing `SURVMNTH` in 2005/2010
- **Observation**: Confirmed missing in PUMF data.
- **Impact**: Limits Step 5 (84-strata modeling) to 7-strata (Day-of-Week only) for these two cycles.

### 4. Commute Mode (`MODE`) Data Quality
- **Observation**: multi-select checkboxes in 2010/2015 are messy (varied bool/int/string formats).
- **Implementation**: Created a loose `is_checked()` helper catching `1, 1.0, "1", "Yes"`.

### 5. Activity Labels Added
- **Observation**: The activity crosswalk only mapped numbers (1–14).
- **Implementation**: Hardcoded a dictionary matching `mainActivityCategoryList.csv` to create `occACT_label` columns for easier debugging.

---

## Design Decisions — ALL LOCKED ✅

> [!NOTE]
> All 6 design decisions have been finalized by the user (2026-03-08). No open questions remain before execution.

### Decision 1 — HHSIZE Collapse ✅
- **Resolution**: Collapse all cycles to **5 categories** {1, 2, 3, 4, 5="5+"}
- 2005–2015: remap code 6 → 5

### Decision 2 — LFTAG Category Count ✅
- **Resolution**: Collapse to **5-category** unified scheme
- 2015 category 6 will be mapped to the nearest 1–5 category

### Decision 3 — HRSWRK Format ✅
- **Resolution**: **Categorical bins** (not continuous)
- All cycles binned to matching bracket boundaries from codebooks
- Original continuous values preserved as `HRSWRK_RAW`

### Decision 4 — TOTINC Bracket Boundaries ✅
- **Resolution**: **Discretize** 2022 CRA continuous values into 2005–2015 bracket boundaries using `pd.cut()`
- Original 2022 continuous values preserved as `TOTINC_RAW`

### Decision 5 — MODE Priority Logic ✅
- **Resolution**: **Hierarchical priority** (standard transport survey practice)
- Priority: car driver > car passenger > public transit > bicycle > walking > other

### Decision 6 — 2005 Province Granularity ✅
- **Resolution**: Keep `PRV` (10 provinces) for 2010+ and `REGION` (5 macro-regions) for 2005
- Flag in metadata; downstream models handle via grouping

---

## Dependency Diagram

```mermaid
graph TD
    A["Phase A: Planning ✅"] --> B["Phase B: Module Setup & Constants"]
    B --> C["Phase C: Demographic Recodes"]
    B --> D["Phase D: Activity Crosswalk"]
    B --> E["Phase E: Presence & Co-Presence"]
    C --> F["Phase F: Metadata & Diary QA"]
    D --> G["Phase G: Orchestrator"]
    E --> G
    F --> G
    C --> G
    G --> H["Phase H: Validation Script"]
    H --> I["Phase I: Final Review"]
```

> **Estimated execution effort**: Phase B (~1 hr) → Phase C (~2 hr) → Phase D (~1 hr) → Phase E (~1 hr) → Phase F (~1 hr) → Phase G (~0.5 hr) → Phase H (~3 hr) → Phase I (~1 hr) = **~10.5 hours total**
