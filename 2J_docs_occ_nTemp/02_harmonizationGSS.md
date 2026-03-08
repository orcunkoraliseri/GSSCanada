# Step 2 — Data Harmonization: Implementation Plan (v2)

## Goal

Transform the four raw Step 1 CSV outputs (`main_{year}.csv` + `episode_{year}.csv` for 2005/2010/2015/2022) into a unified, cross-cycle-compatible schema. Column names, category codes, missing-value conventions, and metadata flags must be identical across all eight files before Step 3 merging.

**Output directory**: `outputs_step2/`

---

## Research Findings (from data investigation)

### Finding 1 — SURVMNTH Absent from 2005 and 2010

Searched **all** columns in both raw files:
- 2005 SAS file: ~500 non-bootstrap variables — **no match** for SURV, MNTH, MONTH, INTM, COLL, REFM, DATE, INTD, DIAR
- 2010 SPS syntax: ~500 non-bootstrap variables — **no match** for any month-related keyword

> [!CAUTION]
> **SURVMNTH does not exist** in the 2005 or 2010 PUMF releases. The GSS Cycle 19 (2005) and Cycle 24 (2010) PUMFs did not include interview month to protect respondent confidentiality. Only the `DVTDAY` (diary day of week, 1–7) is available. This means `SURVMNTH` will be `NaN` for these two cycles, and the 84-strata (DDAY × SURVMNTH) matrix reduces to 7-strata (DDAY only) for 2005/2010.
>
> **Impact on downstream**: Step 3's `STRATA_ID = DDAY × SURVMNTH` cannot be computed for 2005/2010. Step 4's Conditional Transformer will need to handle this gap (missing SURVMNTH conditioning for these cycles). We should proceed by setting `SURVMNTH = NaN` and flagging this limitation for the modeling steps.

### Finding 2 — Activity Code Systems Are Incompatible

| Cycle | Column | Unique Codes | Code Format | Example |
|---|---|---|---|---|
| 2005 | `ACTCODE` | 182 | 3-digit integer (2–990) | 801, 802, 803 |
| 2010 | `ACTCODE` | 264 | 3-digit + decimal sub-codes | 801.1, 801.2, 801.3 |
| 2015 | `TUI_01` | 64 | Sequential 1–63 + code 95 | 1, 2, …, 63, 95 |
| 2022 | `TUI_01` | 121 | 4-digit hierarchical (101–9999) | 101, 102, 231, 9999 |

**All four coding schemes are mutually incompatible.** The reference scheme is 2015's 63-code flat TUI_01. We need **three crosswalk tables**:
- `ACTCODE_2005 → TUI_01_63` (182 → 63)
- `ACTCODE_2010 → TUI_01_63` (264 → 63, collapsing decimal sub-codes)
- `TUI_01_2022 → TUI_01_63` (121 → 63)

These must be built from the codebook PDFs.

### Finding 3 — Location/Home Codes Differ Per Cycle

| Cycle | Column | Home Code | Code Range | Missing |
|---|---|---|---|---|
| 2005 | `PLACE` | **1** | 1–21 | 97, 98, 99 |
| 2010 | `PLACE` | **1** | 1–21 | 97, 98, 99 |
| 2015 | `LOCATION` | **300** | 300–321 | 999 |
| 2022 | `LOCATION` | **3300** | 3300–3323 | 3399, 9999 |

The `recode_location()` function must map **cycle-specific home codes** to `occPRE = 1` (home) vs `0` (not home).

### Finding 4 — Sentinel Values (96/97/98/99) Per Column

Columns where 96–99 appear as **missing-value sentinels** (should → NaN):

| Column (raw) | Cycles | Sentinel Values | Notes |
|---|---|---|---|
| `WKWE` | 2005, 2010 | 97, 98, 99 | Class of worker |
| `LANCH` | 2005, 2010 | 98, 99 | Language |
| `INCM` | 2005, 2010 | 98, 99 | Income |
| `EDU10` | 2005, 2010 | 98, 99 | Education |
| `WKWEHR_C` | 2005 | 97, 98, 99 | Hours worked (continuous) |
| `ACT7DAYS` | 2015 | 97, 98, 99 | Labour force activity |
| `WET_110` | 2015 | 96, 97, 98, 99 | Class of worker |
| `NOC1110Y` | 2015 | 96, 97, 98, 99 | Occupation |
| `EHG_ALL` | 2015 | 97, 98, 99 | Education |
| `MARSTAT` | 2022 | 99 | Marital status |
| `NOCLBR_Y` | 2022 | 96, 99 | Occupation |
| `WHWD140G` | 2022 | 96, 99 | Hours worked |
| `ATT_150C` | 2022 | 99 | Commuting mode |

Columns where 96–99 are **valid values** (must NOT be nullified):
- `RECID` (respondent ID — contains all integer values including 96–99)
- `AGEGR10` (codes 1–7 only, no sentinels)
- `SEX` / `GENDER2` (codes 1–2 only)
- `HSDSIZEC` (codes 1–5 or 1–6)
- `PRV` (province codes 10–59)
- `LUC_RST` (codes 1–3)

### Finding 5 — Demographic Value Distributions

| Variable | 2005 | 2010 | 2015 | 2022 | Compatible? |
|---|---|---|---|---|---|
| `AGEGR10` | 1–7 | 1–7 | 1–7 | 1–7 | ✅ Direct align |
| `SEX`/`GENDER2` | 1–2 | 1–2 | 1–2 | 1–2 | ✅ Rename only |
| `MARSTAT` | 1–6, **8, 9** | 1–6, **8, 9** | 1–6 | 1–6, **99** | ⚠️ Map 8→NaN, 9/99→NaN |
| `HSDSIZEC` | 1–6 | 1–6 | 1–6 | 1–5 | ⚠️ 2022 caps at 5 |
| `REGION` | 1–5 | 1–5 | *(absent)* | *(absent)* | Need PR→REGION map |
| `PRV` | *(absent)* | 10–59 | 10–59 | 10–59 | 2005 only has REGION |
| `LUC_RST` | 1–3 | 1–3 | 1–3 | 1–3 | ✅ Direct align |
| `LFSGSS`/`ACT7DAYS`/`ACT7DAYC` | 1–5, **8, 9** | 1–5, **8, 9** + ACT7DAYS 1–6, **8, 9** | 1–6, **97, 98, 99** | 1–5, **9** | ⚠️ Complex recode |

### Finding 6 — COLLECT_MODE

From GSS documentation and the pipeline overview:
- **2005 (Cycle 19)**: CATI (landline RDD) → `COLLECT_MODE = 0`
- **2010 (Cycle 24)**: CATI (landline RDD) → `COLLECT_MODE = 0`
- **2015 (Cycle 29)**: CATI (landline + cellular RDD) → `COLLECT_MODE = 0` *(still telephone-administered)*
- **2022 (GSSP)**: EQ (self-administered web) → `COLLECT_MODE = 1`

---

## Proposed Changes

### Step 1 Backfill (Minor)

#### [MODIFY] [01_readingGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/01_readingGSS.py)

Since `SURVMNTH` genuinely does not exist in the 2005/2010 PUMFs, **no Step 1 change is needed**. The harmonization script will handle this by setting `SURVMNTH = NaN` for these cycles. (However, 2005 has `DVTDAY` but it was not extracted — we already have it as the column is already in Step 1.)

---

### Harmonization Module

#### [NEW] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)

A single new module implementing the full harmonization pipeline. Structure:

##### Module Constants

**`MAIN_RENAME_MAP`**: Per-cycle rename dictionaries mapping raw column names → unified names.

```python
MAIN_RENAME_2005 = {
    "RECID": "occID", "AGEGR10": "AGEGRP", "sex": "SEX",
    "marstat": "MARSTH", "HSDSIZEC": "HHSIZE", "REGION": "PR",
    "LUC_RST": "CMA", "WKWE": "COW", "wght_per": "WGHT_PER",
    "DVTDAY": "DDAY", "LANCH": "KOL", "LFSGSS": "LFTAG",
    "INCM": "TOTINC", "EDU10": "ATTSCH", "WKWEHR_C": "HRSWRK",
}
# ... similar for 2010, 2015, 2022
```

**`EPISODE_RENAME_MAP`**: Per-cycle rename dictionaries for episode files.

**`SENTINEL_MAP`**: Per-column dict specifying which values are missing sentinels.

```python
SENTINEL_MAP = {
    "COW": {97, 98, 99},      # from WKWE/WET_110/WET_120
    "KOL": {98, 99},           # from LANCH/LAN_01
    "TOTINC": {98, 99},        # from INCM/INCG1
    "ATTSCH": {98, 99},        # from EDU10/EHG_ALL/EDC_10
    "HRSWRK": {96, 97, 98, 99},
    "NOCS": {96, 97, 98, 99},
    "LFTAG": {8, 9, 97, 98, 99},
    "MARSTH": {8, 9, 99},
    "MODE": {99},
}
```

##### Recode Functions

1. **`recode_sex(df, cycle)`** — Rename only (all cycles already use 1=Male, 2=Female).

2. **`recode_marsth(df, cycle)`**:
   - 2005/2010: codes 1–6 + sentinels 8, 9 → map 8/9 → NaN, keep 1–6
   - 2015: codes 1–6 (clean)
   - 2022: codes 1–6 + sentinel 99 → map 99 → NaN
   - Unified: `{1: Married, 2: Common-law, 3: Widowed, 4: Separated, 5: Divorced, 6: Single}`

3. **`recode_agegrp(df, cycle)`** — All cycles use identical 1–7 coding. **No recoding needed** — just rename.

4. **`recode_lftag(df, cycle)`** ✅ Collapse to 5-cat:
   - 2005/2010 `LFSGSS`: 1–5 + sentinels 8, 9 → map 8/9 → NaN
   - 2010 also has `ACT7DAYS`: 1–6 + sentinels 8, 9
   - 2015 `ACT7DAYS`: 1–6, sentinels 97/98/99 → NaN; **collapse cat 6 → nearest 1–5**
   - 2022 `ACT7DAYC`: 1–5 + sentinel 9 → map 9 → NaN
   - Unified: **5-category** (1=Employed at work, 2=Employed absent, 3=Unemployed, 4=Not in LF, 5=Not stated→NaN)

5. **`recode_pr(df, cycle)`**:
   - 2005: only `REGION` (1–5: Atlantic/Quebec/Ontario/Prairies/BC)
   - 2010: has both `REGION` and `PRV` → use `PRV` (10–59)
   - 2015/2022: `PRV` (10–59)
   - **For 2005**: map REGION → a "region-level PR" code. Cannot recover individual provinces from REGION since it's already aggregated. Keep as-is and flag.

6. **`recode_cma(df, cycle)`** — All cycles already use `LUC_RST` with codes 1–3. **Rename only**.

7. **`recode_hhsize(df, cycle)`** ✅ Collapse to 5-cat: 2005–2015 remap code 6→5 (merge "6+" into "5+"). 2022 already 1–5. Unified: {1, 2, 3, 4, 5="5+"}.

8. **`recode_cow(df, cycle)`** — Map sentinels 97/98/99 → NaN. Source: `WKWE`, `WET_110`, `WET_120`.

9. **`recode_hrswrk(df, cycle)`** ✅ Categorical bins:
   - 2005/2010 `WKWEHR_C`: continuous hours → sentinels 97/98/99 → NaN → **bin to brackets**
   - 2015 `WHWD140C`: sentinels → NaN → **bin to brackets**
   - 2022 `WHWD140G`: sentinels {96, 99} → NaN → **bin to brackets**
   - Preserve original continuous as `HRSWRK_RAW`

10. **`recode_attsch(df, cycle)`** — Map sentinels 98/99 → NaN. Source: `EDU10`, `EHG_ALL`, `EDC_10`.

11. **`recode_kol(df, cycle)`** — Map sentinels 98/99 → NaN. Source: `LANCH`, `LAN_01`.

12. **`derive_mode(df, cycle)`** ✅ Hierarchical priority:
    - 2005: **no commute mode columns** → set `MODE = NaN`
    - 2010: derive from `CTW_Q140_C01–C09` multi-select (**hierarchical**: car driver > car passenger > transit > bicycle > walk > other)
    - 2015: derive from `CTW_140A–I` multi-select (**same hierarchical priority**)
    - 2022: use `ATT_150C` directly; map sentinel 99 → NaN

13. **`recode_totinc(df, cycle)`** ✅ Discretize CRA:
    - 2005/2010 `INCM`: categorical brackets + sentinels 98/99 → NaN
    - 2015 `INCG1`: categorical brackets
    - 2022 `INC_C`: CRA-linked continuous → **discretize via `pd.cut()` to matching 2005–2015 bracket boundaries**
    - Preserve 2022 original as `TOTINC_RAW`
    - Append `TOTINC_SOURCE` column

##### Activity Code Crosswalk (Critical)

**`build_activity_crosswalk()`** — We need to construct crosswalk tables from the codebook PDFs:

| Codebook | Path |
|---|---|
| 2005 (C19) | [12M0019GPE.pdf](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/codebooks/Codebook_2005/12M0019GPE.pdf) |
| 2010 Episode | [Episode File - Data Dictionary.pdf](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/codebooks/Codebook_2010/Episode%20File%20-%20Data%20Dictionary%20and%20Alphabetical%20Index.pdf) |
| 2015 Episode | [GSS29_PUMF_episodes.pdf](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/codebooks/Codebook_2015/GSS29_PUMF_episodes.pdf) |
| 2022 Episode | [TU_2022_Episode_PUMF.pdf](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/codebooks/Codebook_2022/TU_2022_Episode_PUMF.pdf) |

**Strategy**: Extract the activity code → label mapping from each codebook, then build a crosswalk to the 2015 63-code scheme by matching labels. For 2010's decimal sub-codes (e.g., 801.1, 801.2), collapse to the parent integer code first, then map to the 63-code scheme.

**`apply_activity_crosswalk(df, cycle)`** — Applies the crosswalk from the [execution Excel workbook](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_activityCodes/Data%20Harmonization_activityCategories%20-%20execution.xlsx), mapping `occACT` to unified 14-category scheme.

##### Location & Co-Presence Recoding

**`apply_presence_crosswalk(df, cycle)`** — Maps PLACE/LOCATION codes to unified 18-category `occPRE` using the [presence execution Excel workbook](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data%20Harmonization_presenceCategories%20-%20execution.xlsx). Also derives `AT_HOME` binary flag.

**`harmonize_copresence(df, cycle)`** — Renames and cleans social contact columns to 8 unified co-presence variables (`Alone`, `Spouse`, `Children`, `friends`, `otherHHs`, `others`, `parents`, `otherInFAMs`). Converts sentinels (7/8/9) to NaN.

See dedicated plan: [02_harmonizationGSS_pre_coPre.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_pre_coPre.md)

##### Metadata Flags

| Flag | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|
| `CYCLE_YEAR` | 2005 | 2010 | 2015 | 2022 |
| `SURVYEAR` | 2005 | 2010 | 2015 | 2022 |
| `SURVMNTH` | NaN | NaN | *(from data)* | *(from data)* |
| `COLLECT_MODE` | 0 | 0 | 0 | 1 |
| `TUI_10_AVAIL` | 0 | 0 | 1 | 1 |
| `BS_TYPE` | `MEAN_BS` | `MEAN_BS` | `STANDARD_BS` | `STANDARD_BS` |
| `TOTINC_SOURCE` | `SELF` | `SELF` | `SELF` | `CRA` |

##### Episode QA: Diary Closure

**`check_diary_closure(df)`**:
1. Parse HHMM STARTIME/ENDTIME (integers like 400, 730, 1630)
2. Compute duration per episode in minutes (handle wrap-around at 2400→0400)
3. Sum per `occID`, assert == 1440
4. Add `DIARY_VALID` column: 1 if sum == 1440, 0 otherwise

##### Orchestrator

**`harmonize_cycle(cycle_year, main_df, episode_df)`** → returns `(harmonized_main, harmonized_episode)`

**`harmonize_all_cycles(input_dir, output_dir)`** → reads Step 1 CSVs, calls `harmonize_cycle()` on each, exports to `outputs_step2/`.

---

### Activity Code Crosswalk

Activity codes will be mapped to a **unified 14-category scheme** using the execution Excel workbook (4 per-cycle sheets, zero conflicts).

See the dedicated crosswalk plan for full details: [02_harmonizationGSS_actCodes.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_actCodes.md)

**Output columns per episode**: `occACT` (1–14), `occACT_raw` (original code), `occACT_label` (category name)

### Presence & Co-Presence

Location codes mapped to **18-category `occPRE`** using the presence execution Excel. Social contact columns consolidated to **8 unified co-presence columns**.

See the dedicated plan: [02_harmonizationGSS_pre_coPre.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_pre_coPre.md)

**Output columns per episode**: `occPRE` (1–18), `occPRE_raw`, `AT_HOME` (binary), `Alone`, `Spouse`, `Children`, `friends`, `otherHHs`, `others`, `parents`, `otherInFAMs`

---

### Validation

See the separate expanded validation plan: [02_harmonizationGSS_val.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_val.md)

---

## User Review Required

> [!WARNING]
> **SURVMNTH gap for 2005/2010**: This is a fundamental data limitation. The 84-strata goal (7 days × 12 months) can only be achieved for 2015 and 2022. For 2005/2010, we're limited to 7 strata (days only). This has implications for:
> - Step 3's `STRATA_ID` computation
> - Step 4's Conditional Transformer conditioning
> - The ~5.8M synthetic diary-day target (will be lower for 2005/2010)
>
> Should we proceed with `SURVMNTH = NaN` for 2005/2010, or is there an alternative data source (e.g., RDC microdata with collection dates)?

> [!NOTE]
> ✅ **Activity code crosswalks**: Resolved — using the user's pre-built 14-category scheme from reference CSVs. 7 ambiguous 2005 codes have been disambiguated and confirmed. See [02_harmonizationGSS_actCodes.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_actCodes.md).

> [!NOTE]
> **Province for 2005**: The 2005 PUMF only has `REGION` (5 macro-regions), not individual province codes `PRV`. This means `PR` for 2005 will have coarser granularity (5 categories) vs. the 10 province codes available in 2010+.

