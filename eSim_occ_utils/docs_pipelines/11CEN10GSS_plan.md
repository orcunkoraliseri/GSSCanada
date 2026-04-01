# Implementation Plan: 11CEN10GSS Occupancy Modeling Pipeline

This document outlines the complete implementation of the occupancy modeling pipeline for **Census 2011** and **GSS 2010 (Cycle 24 – Time Use)**. It follows the established architecture of the `06CEN05GSS` and `16CEN15GSS` pipelines and documents all dataset-specific differences, column mappings, and validation requirements.

---

## 0. Current Implementation Status *(updated after verified end-to-end run)*

### Files created

| File | Status | Notes |
|------|--------|-------|
| `11CEN10GSS_main.py` | ✅ Complete | Interactive controller, 4-step menu |
| `11CEN10GSS_step0.py` | ✅ Complete | Episode preprocessing; uses hardcoded absolute path (minor) |
| `11CEN10GSS_alignment.py` | ✅ Complete | Verified codebook mappings; alignment rerun clean |
| `11CEN10GSS_ProfileMatcher.py` | ✅ Complete | Sample run passes |
| `11CEN10GSS_HH_aggregation.py` | ✅ Complete | Sample run passes |
| `11CEN10GSS_occToBEM.py` | ✅ Complete | Sample run passes |
| `__init__.py` | ✅ Present | Package marker added |

### Intermediate outputs produced

| File | Location | Rows | Status |
|------|----------|------|--------|
| `out10EP_ACT_PRE_coPRE.csv` | `DataSources_GSS/Episode_files/GSS_2010_episode/` | 283,287 | ✅ OK |
| `GSS_2010_Merged.csv` | `DataSources_GSS/Main_files/` | 283,287 | ✅ OK |
| `2011_LINKED.csv` | `DataSources_CENSUS/census_2011/` | 337,126 | ✅ OK |
| `Aligned_GSS_2010.csv` | `Outputs_11CEN10GSS/alignment/` | 219,584 | ✅ Clean, no duplicate `DDAY.1` column |
| `Aligned_Census_2010.csv` | `Outputs_11CEN10GSS/alignment/` | 273,678 | ✅ Non-empty, alignment complete |

**Resolved**: the alignment has been rerun and Steps 2–4 now complete successfully.

---

### 0.1 ✅ Resolved: `Aligned_Census_2010.csv` was empty

**Symptom**: All 337,126 Census rows are dropped during harmonization. The output file has column headers but zero data rows.

**Root cause**: `harmonize_pr()` was copied from `06CEN05GSS_alignment.py`, which expects Census **2006 aggregated regional codes** (1=Atlantic, 2=QC, 3=ON, 4=Prairies, 5=AB, 6=BC). Census **2011** PUMF uses the actual **2-digit Statistics Canada province codes** (10=NL, 11=PEI, 12=NS, 13=NB, 24=QC, 35=ON, 46=MB, 47=SK, 48=AB, 59=BC, 60+=Territories). The mapping dictionary `{1:10, 2:24, 3:35, 4:46, 5:48, 6:59}` finds no matching keys in the Census 2011 data, maps every row to 99, and then drops all of them in the filter step.

**Fix** — replace the Census-side mapping in `harmonize_pr()` inside `11CEN10GSS_alignment.py`:

```python
def harmonize_pr(df_census, df_gss):
    print("  Harmonizing PR...")

    # Census 2011 already uses 2-digit province codes — consolidate to regional representatives
    cen11_pr_map = {
        10: 10, 11: 10, 12: 10, 13: 10,  # Atlantic → NL representative
        24: 24,                             # Quebec
        35: 35,                             # Ontario
        46: 46, 47: 46,                    # Prairies → MB representative
        48: 48,                             # Alberta
        59: 59,                             # BC
        # Territories (60, 61, 62) map to 99 → dropped (too small for matching)
    }
    df_census['PR'] = pd.to_numeric(df_census['PR'], errors='coerce').fillna(99).astype(int)
    df_census['PR'] = df_census['PR'].map(cen11_pr_map).fillna(99).astype(int)
    df_census = df_census[~df_census['PR'].isin([99])].copy()

    # GSS 2010: same province codes, same consolidation (unchanged)
    gss_pr_mapping = {10:10, 11:10, 12:10, 13:10, 24:24, 35:35, 46:46, 47:46, 48:48, 59:59}
    df_gss['PR'] = pd.to_numeric(df_gss['PR'], errors='coerce').fillna(99).astype(int)
    df_gss['PR'] = df_gss['PR'].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[~df_gss['PR'].isin([99])].copy()

    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss
```

**Resolution**: re-ran `python 11CEN10GSS_alignment.py`. `Aligned_Census_2010.csv` now has 273,678 rows.

---

### 0.2 ✅ Resolved: Duplicate `DDAY` / `DDAY.1` column in `Aligned_GSS_2010.csv`

**Symptom**: The aligned GSS file has two day-type columns — `DDAY` (from the episode file) and `DDAY.1` (created when `DVTDAY` from the main file was renamed to `DDAY` after merge, producing a duplicate).

**Root cause**: `out10EP_ACT_PRE_coPRE.csv` already has a `DDAY` column. The GSS 2010 main file also has `DVTDAY`, which `RENAME_MAP_10` renames to `DDAY`. After `pd.merge()`, both columns are present. When `rename_adjusted` renames `DVTDAY → DDAY`, the DataFrame gets two identically-named columns, which appear as `DDAY` and `DDAY.1` when written to CSV and read back.

**Fix** — in `read_merge_save_gss_2010()`, drop `DVTDAY` after the merge (before renaming), since `DDAY` from the episode file is the authoritative column:

```python
# After df_merged = pd.merge(...), before renaming:
if 'DVTDAY' in df_merged.columns and 'DDAY' in df_merged.columns:
    df_merged = df_merged.drop(columns=['DVTDAY'])

rename_adjusted = {k: v for k, v in rename_dict.items() if k != 'RECID' and k in df_merged.columns}
df_merged = df_merged.rename(columns=rename_adjusted)
```

**Resolution**: the aligned GSS output now contains a single `DDAY` column and no `DDAY.1`.

---

### 0.3 ✅ Verified: `harmonize_marsth()` mapping for Census 2011

`cen11.sps` defines Census 2011 `MARSTH` as:
- `1` = Never legally married and not living common law
- `2` = Legally married and not separated
- `3` = Living common law
- `4` = Separated and not living common law
- `5` = Divorced and not living common law
- `6` = Widowed and not living common law

The harmonization collapses these to the shared 3-way scheme used by the pipeline:
- Census `1` -> single
- Census `2` + `3` -> married/common-law
- Census `4` + `5` + `6` -> widowed/separated/divorced

This mapping is now documented in `11CEN10GSS_alignment.py`, and the aligned outputs match on `MARSTH`.

---

### 0.4 ✅ Verified: `harmonize_totinc()` refusal codes for GSS 2010 `INCM`

`GSSMain_2010_syntax.SPS` shows `INCM` categories `1` through `12`, with refusal/missing codes `97`, `98`, and `99` (the syntax also marks `97 thru 99` as missing). The alignment now filters those values explicitly before harmonization.

The GSS side is treated as a 12-category income variable, matching the Census income bins after harmonization.

---

## 1. Overview

The **11CEN10GSS** pipeline integrates:
- **Census 2011 PUMF**: `0_Occupancy/DataSources_CENSUS/cen11.dat` + `cen11.sps`
- **GSS 2010 (Cycle 24) Main file**: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010.DAT` + `GSSMain_2010_syntax.SPS`
- **GSS 2010 Episode file**: `0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT` + `C24_Episode File_SPSS_withno_bootstrap.SPS`

**Pipeline steps** (4 steps total, no DTYPE expansion):

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `11CEN10GSS_alignment.py` | Harmonize Census 2011 and GSS 2010 variables |
| 2 | `11CEN10GSS_ProfileMatcher.py` | Assign GSS schedules to Census agents |
| 3 | `11CEN10GSS_HH_aggregation.py` | Aggregate to 5-minute household grids |
| 4 | `11CEN10GSS_occToBEM.py` | Convert to hourly BEM schedules |

Main controller: `11CEN10GSS_main.py` (already implemented).

Outputs directory: `0_Occupancy/Outputs_11CEN10GSS/`

---

## 2. Data Sources and File Structure

### 2.1 Census 2011 PUMF

**File**: `0_Occupancy/DataSources_CENSUS/cen11.dat`
**Schema**: `0_Occupancy/DataSources_CENSUS/cen11.sps`
**Format**: Fixed-width text, LRECL=368

Key columns used in the pipeline (from `cen11.sps`):

| Column | Positions | Description | Used for |
|--------|-----------|-------------|----------|
| `HH_ID` | 1–6 | Household ID | Household assembly |
| `CF_RP` | 41 | Census family reference person (1/2/3) | Household assembly |
| `AGEGRP` | 32–33 | Age group (3–13) | Harmonization / matching |
| `ATTSCH` | 36 | School attendance (1/2) | Harmonization / matching |
| `CMA` | 48–50 | Census metropolitan area (3-digit codes) | Harmonization / matching |
| `DTYPE` | 54 | Structural type of dwelling (1–10) | BEM output |
| `KOL` | 108 | Knowledge of official languages | Harmonization / matching |
| `LFTAG` | 110–111 | Labour force activity (1–14) | Harmonization / matching |
| `MARSTH` | 128 | Marital status (1–3) | Harmonization / matching |
| `NOCS` | 147–148 | National Occupational Classification | Harmonization / matching |
| `PR` | 161–162 | Province/territory code | Harmonization / matching |
| `SEX` | 177 | Sex (1/2) | Harmonization / matching |
| `TOTINC` | 182–188 | Total income (continuous dollars) | Harmonization / matching |
| `BEDRM` | 38 | Number of bedrooms | BEM output |
| `ROOM` | 175–176 | Number of rooms | BEM output |
| `CONDO` | 51 | Condominium status | BEM output |
| `REPAIR` | 174 | Repair needs | BEM output |
| `WEIGHT` | 203–220 | Person weight | Sampling |

> **Note**: Census 2011 does **not** include a direct `HHSIZE` column in the PUMF. Household size must be **derived** by counting persons sharing the same `HH_ID`, or sourced from the pre-filtered CSV if already computed. Verify in `cen11_filtered.csv` whether `HHSIZE` was added during Census preprocessing.

### 2.2 GSS 2010 Main File (Cycle 24)

**File**: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010.DAT`
**Schema**: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010_syntax.SPS`
**Format**: Fixed-width text, LRECL=17534

Key columns to extract (`COLS_MAIN_10`):

```python
COLS_MAIN_10 = [
    'RECID',      # Record ID (merge key) -> occID
    'PRV',        # Province -> PR
    'HSDSIZEC',   # Household size -> HHSIZE
    'AGEGR10',    # Age group (1–7) -> AGEGRP
    'SEX',        # Sex -> SEX
    'MARSTAT',    # Marital status -> MARSTH
    'LANHSDC',    # Household language -> KOL
    'ACT7DAYS',   # Main activity (labour force) -> LFTAG
    'LUC_RST',    # Urban/rural -> CMA
    'INCM',       # Personal income (continuous) -> TOTINC
    'DVTDAY',     # Designated day type -> DDAY
    'WGHT_PER',   # Person weight
]
```

Rename map (`RENAME_MAP_10`):

```python
RENAME_MAP_10 = {
    'RECID':    'occID',
    'PRV':      'PR',
    'HSDSIZEC': 'HHSIZE',
    'AGEGR10':  'AGEGRP',
    'SEX':      'SEX',
    'MARSTAT':  'MARSTH',
    'LANHSDC':  'KOL',
    'ACT7DAYS': 'LFTAG',
    'LUC_RST':  'CMA',
    'INCM':     'TOTINC',
    'DVTDAY':   'DDAY',
}
```

> **Critical difference from GSS 2015**: The merge key in GSS 2010 is `RECID` (not `PUMFID`). Income `INCM` is coded as categorical brackets `1`–`12` with refusal codes `97`–`99`; those missing values are filtered before harmonization.

> **ATTSCH note**: No direct school attendance variable is visible in the GSS 2010 main file. If needed for matching, it may need to be derived (e.g., from age + activity) or dropped from the matching feature set.

### 2.3 GSS 2010 Episode File (Cycle 24)

**File**: `0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/C24EPISODE_withno_bootstrap.DAT`
**Schema**: `C24_Episode File_SPSS_withno_bootstrap.SPS`
**Format**: Fixed-width text, LRECL=76

Key episode columns:

| Column | Description |
|--------|-------------|
| `RECID` | Record ID – links to main file |
| `EPINO` | Sequential episode number |
| `DDAY` | Designated day (1=Sun, 2=Mon, …, 7=Sat) |
| `ACTCODE` | Activity code (decimal format) |
| `STARTMIN` | Episode start in minutes from midnight |
| `ENDMIN` | Episode end in minutes from midnight |
| `DURATION` | Duration in minutes |
| `PLACE` | Location code |
| `ALONE` | Social context – alone |
| `SPOUSE` | Social context – with spouse |
| `CHILDHSD` | Social context – with children |
| `MEMBHSD` | Social context – with other household members |

> The episode file must be parsed into the standard `out10EP_ACT_PRE_coPRE.csv` format (same columns as the 2005 and 2015 processed episode files) before running Step 1.

---

## 3. Step 0: GSS 2010 Episode Preprocessing

**Goal**: Convert raw `C24EPISODE_withno_bootstrap.DAT` into a processed CSV compatible with the pipeline.

**Expected output format**: `out10EP_ACT_PRE_coPRE.csv`
**Output location**: `0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/`

Required operations:
1. Parse fixed-width `.DAT` using the `.SPS` colspec (same `parse_sps_colspec` utility as `16CEN15GSS_alignment.py`).
2. Rename `RECID` → `occID` for merge consistency.
3. Compute `PRE` (presence at home): derive from `PLACE` code (location at home = 1 or equivalent 2010 code; verify against GSS 2010 codebook).
4. Compute `coPRE` (co-presence): mark episodes where other household members are present (`MEMBHSD == 1` or `SPOUSE == 1` or `CHILDHSD == 1`).
5. Verify `ACTCODE` format matches the encoding used in `06CEN05GSS` and `16CEN15GSS` (may be 5-digit decimal in 2010 vs integer codes in other years).
6. Save to `out10EP_ACT_PRE_coPRE.csv`.

---

## 4. Step 1: Alignment (`11CEN10GSS_alignment.py`)

**Goal**: Read Census 2011 and GSS 2010 data, apply harmonization functions, and save aligned DataFrames.

**Output directory**: `0_Occupancy/Outputs_11CEN10GSS/alignment/`
**Output files**:
- `Aligned_Census_2010.csv`
- `Aligned_GSS_2010.csv`

### 4.1 Census 2011 Input

Use the pre-filtered Census CSV from the preprocessing step:

```
0_Occupancy/DataSources_CENSUS/cen11_filtered.csv
```

If `HHSIZE` is missing from `cen11_filtered.csv`, derive it before alignment:
```python
df_census['HHSIZE'] = df_census.groupby('HH_ID')['HH_ID'].transform('count')
df_census.loc[df_census['HHSIZE'] >= 7, 'HHSIZE'] = 6  # cap at 6
```

### 4.2 GSS 2010 Input

Merge GSS 2010 main demographics with episode data:
1. Parse `GSSMain_2010.DAT` using `GSSMain_2010_syntax.SPS` → extract `COLS_MAIN_10`
2. Apply `RENAME_MAP_10`
3. Merge onto episodes from `out10EP_ACT_PRE_coPRE.csv` on `occID`

### 4.3 Harmonization Functions

All harmonization functions follow the same pattern as `06CEN05GSS_alignment.py`. The functions below note **only the differences** specific to the 2011/2010 data.

#### `harmonize_agegrp()` — **No change needed**

Census 2011 `AGEGRP` uses the same 3–13 encoding as Census 2006:
```
Census 3,4 → 1 (15-24)
Census 5,6 → 2 (25-34)
Census 7,8 → 3 (35-44)
Census 9,10 → 4 (45-54)
Census 11 → 5 (55-64)
Census 12 → 6 (65-74)
Census 13 → 7 (75+)
```
GSS 2010 `AGEGR10` uses the same 1–7 scale as GSS 2015.

#### `harmonize_attsch()` — **GSS 2010 may lack this variable**

Check whether `ATTSCH` is present in the GSS 2010 main file. If not available:
- Option A: Drop `ATTSCH` from the matching feature set entirely.
- Option B: Derive from `ACT7DAYS`: respondents currently in school (code 3 or similar) → 1; others → 2.

If available, apply the same mapping as `06CEN05GSS`:
```
GSS 1,2 → 1 (Attending)
GSS 7 → 2 (Not attending)
GSS 8,9 → Drop
```

#### `harmonize_cma()` — **Census 2011 uses 3-digit CMA codes**

Census 2011 `CMA` column uses 3-digit Statistics Canada CMA codes. Map to GSS urban/rural categories:
```python
# Census 2011 CMA → GSS LUC_RST (1=CMA 500k+, 2=CA 100k-500k, 3=Rural)
CMA_MAP_CEN11 = {
    # Major CMAs (population ≥ 500k)
    505: 1,  # Ottawa-Gatineau
    535: 1,  # Toronto
    462: 1,  # Ottawa (alt code – verify)
    825: 1,  # Calgary
    835: 1,  # Edmonton
    933: 1,  # Vancouver
    408: 1,  # Quebec City
    462: 1,  # Ottawa-Hull
    # Add remaining large CMAs ...
    996: 2,  # CA (non-CMA urban)
    997: 3,  # Rural
    999: 3,  # Not in CMA/CA
}
```
> Verify the exact 3-digit CMA codes used in the 2011 PUMF from the codebook. The 2006 pipeline used a 3-value simplification (1=major CMA, 2=other, 3=rural). Apply the same logic.

GSS 2010 `LUC_RST` uses the same 3-value scheme as GSS 2015:
```
1 = CMA (≥500k population)
2 = CA (urban, <500k)
3 = Rural
```
Drop Rural (3) from GSS to match Census coverage.

#### `harmonize_hhsize()` — **No change needed**

```
Census: 1–7 → cap 7+ to 6
GSS (HSDSIZEC): 1–6 (already compatible)
```

#### `harmonize_kol()` — **GSS 2010 uses LANHSDC (household language)**

`LANHSDC` in GSS 2010 is household language, not personal language ability. Encoding may differ. Verify codebook values:
- Expected encoding: 1=English, 2=French, 3=Both/Other
- Census `KOL`: 1=English only, 2=French only, 3=Both, 4=Neither → drop 4

Apply same filter logic as `06CEN05GSS`:
```
GSS: drop DK/NS values (8, 9, 99)
Census: drop 4 (Neither)
```

#### `harmonize_lftag()` — **No change needed (ACT7DAYS maps same as GSS 2015)**

Census 2011 `LFTAG` uses the same 1–14 encoding. Apply same Census → GSS mapping:
```
Census 1 → 1 (Employed full-time)
Census 2–6 → 2 (Employed other)
Census 7–11 → 3 (Unemployed)
Census 12,13 → 4 (Not in labour force)
Census 14 → 5 (Retired/Other)
Drop GSS category 6, 8, 9
```

#### `harmonize_marsth()` — **No change needed**

```
GSS 1 → 1 (Married)
GSS 2 → 2 (Common-law)
GSS 3,4,5,6 → 3 (Not married)
GSS 8,9 → Drop
Census: already [1, 2, 3]
```

#### `harmonize_nocs()` — **GSS 2010 uses NOCS2006_C10**

GSS 2010 uses `NOCS2006_C10` (10-category classification). Same mapping as other years:
```
GSS 97, 98 → 99 (Not applicable/DK)
Census: already compatible [1–10, 99]
```

#### `harmonize_pr()` — **No change needed**

Census 2011 `PR` uses the same 2-digit province codes as 2006. Apply identical mapping:
```python
# Census province region → GSS province code
census_to_gss_pr = {1: 10, 2: 24, 3: 35, 4: 46, 5: 48, 6: 59}
# GSS province collapse
gss_pr_mapping = {10:10, 11:10, 12:10, 13:10, 24:24, 35:35, 46:46, 47:46, 48:48, 59:59}
```

#### `harmonize_sex()` — **No change needed**

Both datasets: 1=Male, 2=Female.

#### `harmonize_totinc()` — **GSS 2010 `INCM` is categorical 1–12**

GSS 2015 used `INCG1` (pre-categorized, 1–12). GSS 2010 also uses bracketed income codes in `INCM`, with refusal/missing codes `97`–`99`. Census 2011 `TOTINC` is continuous dollars and is binned into the same 12-category scheme.

Bin the Census side and filter the GSS refusal codes before comparison:
```python
def map_income_to_category(x):
    """Maps continuous income (dollars) to 12-category scheme (2010 brackets)."""
    try:
        x = float(x)
    except:
        return 99
    if x <= 0:     return 1   # No income or loss
    if x < 5000:   return 2   # Under $5,000
    if x < 10000:  return 3   # $5,000–$9,999
    if x < 15000:  return 4   # $10,000–$14,999
    if x < 20000:  return 5   # $15,000–$19,999
    if x < 30000:  return 6   # $20,000–$29,999
    if x < 40000:  return 7   # $30,000–$39,999
    if x < 50000:  return 8   # $40,000–$49,999
    if x < 60000:  return 9   # $50,000–$59,999
    if x < 80000:  return 10  # $60,000–$79,999
    if x < 100000: return 11  # $80,000–$99,999
    return 12                  # $100,000 or more
```

Apply the binning only to Census `TOTINC`. GSS `TOTINC` is already on the 1–12 categorical scale after filtering `97`–`99`.

### 4.4 Household Assembly (Census 2011)

Use `assemble_households()` identical to `16CEN15GSS_alignment.py`. Census 2011 uses the same `CF_RP` field (1=reference person, 2=family member, 3=non-family member):

- Phase 1: HHSIZE=1 singles → direct assignment
- Phase 2: CF_RP=1 heads → assemble families
- Phase 3: Leftover CF_RP=3 → roommate groupings

**Output**: `0_Occupancy/DataSources_CENSUS/census_2011/2011_LINKED.csv`

### 4.5 Alignment Validation

Run `check_value_alignment()` on all `TARGET_COLS`:
```python
TARGET_COLS = ['AGEGRP', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']
# ATTSCH only if available in GSS 2010
```

All columns must reach **MATCH** status (identical unique value sets) before proceeding to Step 2.

---

## 5. Step 2: Profile Matching (`11CEN10GSS_ProfileMatcher.py`)

**Goal**: Assign GSS 2010 time-use schedules to Census 2011 agents using tiered demographic matching.

**Inputs**:
- `Aligned_Census_2010.csv`
- `Aligned_GSS_2010.csv`

**Output directory**: `0_Occupancy/Outputs_11CEN10GSS/ProfileMatching/`
**Output files** (for default 10% sample):
- `11CEN10GSS_Matched_Keys_sample10pct.csv` — lightweight keys CSV
- `11CEN10GSS_Full_Schedules_sample10pct.csv` — expanded schedules

### 5.1 MatchProfiler Configuration

The `MatchProfiler` class is copied from `16CEN15GSS_ProfileMatcher.py` with updated column names.

**Matching tiers** (adjust based on which columns survived harmonization):

```python
# Tier 1: All available matched columns
cols_t1 = ["HHSIZE", "AGEGRP", "MARSTH", "SEX", "KOL", "PR", "LFTAG", "TOTINC", "CMA"]

# Tier 2: Core demographics
cols_t2 = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "LFTAG", "PR"]

# Tier 3: Key constraints
cols_t3 = ["HHSIZE", "AGEGRP", "SEX"]

# Tier 4: Fail-safe
cols_t4 = ["HHSIZE"]

# Tier 5: Random fallback
```

If `ATTSCH` was retained → add to `cols_t1` and `cols_t2`.

### 5.2 Day Type Split

GSS 2010 `DDAY` encoding (same as GSS 2015):
```
Weekday catalog: DDAY ∈ {2, 3, 4, 5, 6}  (Mon–Fri)
Weekend catalog: DDAY ∈ {1, 7}            (Sun, Sat)
```

### 5.3 Sampling

Default sample: **10%** of Census 2011 population (set in `11CEN10GSS_main.py`).

```python
df_census_sampled = df_census.sample(frac=0.10, random_state=42)
```

### 5.4 Output Schema

`11CEN10GSS_Matched_Keys_sample10pct.csv` columns:
```
PID, SIM_HH_ID, occID_WD, occID_WE, Tier_WD, Tier_WE, HHSIZE, AGEGRP, SEX, ...
```

---

## 6. Step 3: Household Aggregation (`11CEN10GSS_HH_aggregation.py`)

**Goal**: Convert individual matched schedules into 5-minute household occupancy grids.

**Inputs**:
- `11CEN10GSS_Matched_Keys_sample10pct.csv`
- `out10EP_ACT_PRE_coPRE.csv` (GSS 2010 episode file)

**Output directory**: `0_Occupancy/Outputs_11CEN10GSS/HH_aggregation/`
**Output files**:
- `11CEN10GSS_Full_Aggregated_sample10pct.csv`
- `11CEN10GSS_Full_Schedules_sample10pct.csv`

### 6.1 HouseholdAggregator Configuration

The `HouseholdAggregator` class is copied from `16CEN15GSS_HH_aggregation.py` with updated path references.

**Resolution**: 5 minutes → 288 time slots per day.

**Sub-steps**:
- **Step A**: Expand matched keys → individual episode-level schedules per Census agent
- **Step B**: `occPre` — binary presence at home per household per time slot
- **Step C**: `occDensity` — social density (count of household members present)
- **Step D**: `occActivity` — aggregated activity sets per household per time slot

### 6.2 Household Identifier

Census 2011 uses `SIM_HH_ID` (generated in `assemble_households()`). No special handling needed — same convention as `06CEN05GSS` and `16CEN15GSS`.

---

## 7. Step 4: BEM Conversion (`11CEN10GSS_occToBEM.py`)

**Goal**: Convert 5-minute household grids into hourly schedules for EnergyPlus/BEM simulation.

**Input**: `11CEN10GSS_Full_Aggregated_sample10pct.csv`

**Output directory**: `0_Occupancy/Outputs_11CEN10GSS/occToBEM/`
**Output file**: `11CEN10GSS_BEM_Schedules_sample10pct.csv`

### 7.1 BEMConverter Configuration

The `BEMConverter` class is copied from `16CEN15GSS_occToBEM.py` with updated path references.

**Resolution**: Hourly aggregation → 24 time slots per day.

**Metabolic rate mapping** (same as existing pipelines):
```python
METABOLIC_MAP = {
    '1': 125,   # Employed paid work
    '2': 125,   # Employed unpaid work
    '3': 70,    # School
    '5': 70,    # Personal care / sleep
    '6': 100,   # Meals
    '7': 80,    # Household work
    '8': 80,    # Maintenance
    '9': 80,    # Shopping
    '10': 80,   # Services
    '11': 245,  # Physical activity / sport
    '12': 80,   # Civic/religious
    '13': 80,   # Social leisure
    '14': 70,   # Entertainment / passive
    '15': 70,   # Reading / other passive
}
```

**DTYPE mapping** (Census 2011 uses detailed DTYPE — no expansion needed):
```python
DTYPE_MAP = {
    1: 'SingleDetached',
    2: 'SemiDetached',
    3: 'RowHouse',
    4: 'DuplexFlat',
    5: 'ApartmentHighRise',   # 5+ storeys
    6: 'ApartmentLowRise',    # <5 storeys
    7: 'OtherSingleAttached',
    8: 'MovableDwelling',
}
```

> Census 2011 provides detailed DTYPE (1–8 or 1–10 depending on PUMF version). Verify the exact codes from the `cen11.sps` codebook. **No DTYPE expansion step is needed** (unlike `16CEN15GSS` which used Random Forest to refine coarse codes).

**PR mapping** (same as other pipelines):
```python
PR_MAP = {10: 'Atlantic', 24: 'Quebec', 35: 'Ontario', 46: 'Prairie', 48: 'Alberta', 59: 'BC'}
```

### 7.2 Output Schema

`11CEN10GSS_BEM_Schedules_sample10pct.csv` columns:
```
SIM_HH_ID, Hour_0 ... Hour_23,   # Fractional occupancy (0–1)
MetRate_0 ... MetRate_23,         # Metabolic rate per person (W)
DTYPE, BEDRM, ROOM, CONDO, REPAIR, PR
```

---

## 8. Key Differences from Existing Pipelines

| Aspect | 06CEN05GSS | 11CEN10GSS | 16CEN15GSS |
|--------|-----------|------------|------------|
| Census year | 2006 | 2011 | 2016 |
| GSS cycle | Cycle 19 (2005) | Cycle 24 (2010) | Cycle 29 (2015) |
| GSS merge key | `PUMFID` → `occID` | `RECID` → `occID` | `PUMFID` → `occID` |
| GSS income field | `INCG1` (categorical 1–12) | `INCM` (continuous $) | `INCG1` (categorical 1–12) |
| Census income | `TOTINC` (continuous $) | `TOTINC` (continuous $) | `TOTINC` (continuous $) |
| Income handling | Census mapped → categories | **Both** mapped → categories | Census mapped → categories |
| HHSIZE in Census | Direct column | **Must be derived** from `HH_ID` counts | Direct column |
| CMA in Census | Simple codes | 3-digit CMA codes | Simple codes |
| DTYPE detail | Full (1–8) | Full (1–8) | Coarse (1–3), needs expansion |
| DTYPE expansion step | No | **No** | Yes (RF classifier) |
| Total pipeline steps | 4 | **4** | 5 |
| Default sample % | 5% | **10%** | 10% |
| ATTSCH in GSS | Yes (`ATTSCH`) | **Verify** (may be absent) | Yes (`ATTSCH`) |

---

## 9. Directory Structure

```
eSim_occ_utils/
└── 11CEN10GSS/
    ├── 11CEN10GSS_main.py              ✅ Done
    ├── 11CEN10GSS_alignment.py         ⬜ To implement
    ├── 11CEN10GSS_ProfileMatcher.py    ⬜ To implement
    ├── 11CEN10GSS_HH_aggregation.py    ⬜ To implement
    ├── 11CEN10GSS_occToBEM.py          ⬜ To implement
    └── __init__.py                     ⬜ To create

0_Occupancy/
├── DataSources_CENSUS/
│   ├── cen11.dat                       ✅ Available
│   ├── cen11.sps                       ✅ Available
│   └── census_2011/                    (check for filtered CSV)
├── DataSources_GSS/
│   ├── Main_files/
│   │   ├── GSSMain_2010.DAT            ✅ Available
│   │   └── GSSMain_2010_syntax.SPS     ✅ Available
│   └── Episode_files/
│       └── GSS_2010_episode/
│           ├── C24EPISODE_withno_bootstrap.DAT     ✅ Available
│           ├── C24_Episode File_SPSS_withno_bootstrap.SPS  ✅ Available
│           └── out10EP_ACT_PRE_coPRE.csv           ⬜ To generate (Step 0)
└── Outputs_11CEN10GSS/
    ├── alignment/                      ⬜ Created by Step 1
    ├── ProfileMatching/                ⬜ Created by Step 2
    ├── HH_aggregation/                 ⬜ Created by Step 3
    └── occToBEM/                       ⬜ Created by Step 4
```

---

## 10. Verification and Validation Checkpoints

### After Step 0 (Episode Preprocessing)
- [ ] `out10EP_ACT_PRE_coPRE.csv` has the same columns as `out05EP_ACT_PRE_coPRE.csv` and `out15EP_ACT_PRE_coPRE.csv`
- [ ] `occID` column present (renamed from `RECID`)
- [ ] `ACTCODE` values are in the expected format

### After Step 1 (Alignment)
- [ ] `check_value_alignment()` returns **MATCH** for all shared columns
- [ ] Census 2011 `HHSIZE` derived correctly (compare distribution to GSS `HHSIZE`)
- [ ] Income `TOTINC` categories 1–12 appear in both datasets
- [ ] Generate distribution comparison plots: GSS 2010 sample vs Census 2011 population for `AGEGRP`, `SEX`, `HHSIZE`, `PR`

### After Step 2 (Profile Matching)
- [ ] Tier distribution: Tier 1 hits > 30% (acceptable), Tier 5 hits < 5%
- [ ] Every Census agent has both a `occID_WD` and `occID_WE` assignment
- [ ] `Matched_Keys` CSV row count = sampled Census population size

### After Step 3 (HH Aggregation)
- [ ] All 288 time slots populated for each `SIM_HH_ID`
- [ ] `occPre` values are binary (0/1)
- [ ] `occDensity` values bounded by household size
- [ ] Household counts consistent with Census 2011 benchmarks

### After Step 4 (BEM Conversion)
- [ ] `Hour_0` through `Hour_23` values are in [0, 1] (fractional occupancy)
- [ ] Metabolic rate values are non-negative
- [ ] DTYPE distribution matches Census 2011 DTYPE frequencies
- [ ] BEM output is compatible with `eSim_bem_utils` integration format

---

## 11. Execution Order

```bash
# From eSim_occ_utils/11CEN10GSS/

# Step 0: Preprocess GSS 2010 episodes (one-time)
# (Run manually or add a preprocessing utility)

# Run full pipeline interactively
python 11CEN10GSS_main.py

# Or run individual steps
python 11CEN10GSS_main.py --run 1   # Alignment
python 11CEN10GSS_main.py --run 2 --sample 10  # Profile matching
python 11CEN10GSS_main.py --run 3 --sample 10  # HH aggregation
python 11CEN10GSS_main.py --run 4 --sample 10  # BEM conversion

# Full pipeline at 10% sample
python 11CEN10GSS_main.py --run 5 --sample 10
```

---

## 12. Open Questions (Resolve Before Implementation)

1. **HHSIZE in Census 2011**: Does `cen11_filtered.csv` already contain an `HHSIZE` column, or must it be derived from `HH_ID` counts?

2. **ATTSCH in GSS 2010**: Is there a school attendance variable in `GSSMain_2010_syntax.SPS`? If not, should it be dropped from matching or derived?

3. **CMA codes in Census 2011**: Verify the exact 3-digit CMA codes from the `cen11.sps` codebook and confirm the mapping to GSS `LUC_RST` categories (1/2/3).

4. **ACTCODE format in GSS 2010**: Does `ACTCODE` in `C24EPISODE` use the same integer codes (1–14) as the 2005 and 2015 episode files, or a different classification scheme?

5. **INCM missing values in GSS 2010**: Confirmed refusal codes are 97, 98, and 99 in the 2010 codebook.

6. **LANHSDC vs KOL compatibility**: Verify that `LANHSDC` (household language) uses a value encoding comparable to Census 2011 `KOL` (knowledge of official languages). These may not be directly comparable — consider dropping `KOL` from matching if encoding is incompatible.

---

## progress_log

**Completed Steps:**
- **Step 0**: Implemented `11CEN10GSS_step0.py`. It parses `C24EPISODE_withno_bootstrap.DAT` with the `.SPS` dictionary, derives `PRE` and `coPRE`, and saves `out10EP_ACT_PRE_coPRE.csv`.
- **Step 1**: Implemented and verified `11CEN10GSS_alignment.py`.
  - Census and GSS codebook mappings were checked against `cen11.sps` and `GSSMain_2010_syntax.SPS`.
  - `MARSTH` and `INCM` handling were corrected and documented.
  - Alignment was rerun successfully with `Aligned_Census_2010.csv` at 273,678 rows and `Aligned_GSS_2010.csv` at 219,584 rows.
  - `check_value_alignment()` now reports `MATCH` for `AGEGRP`, `CMA`, `HHSIZE`, `KOL`, `LFTAG`, `MARSTH`, `NOCS`, `PR`, `SEX`, and `TOTINC`.
- **Step 2**: `11CEN10GSS_ProfileMatcher.py` completed and run with `--sample 10`.
  - Produced matched keys and expanded schedules under `Outputs_11CEN10GSS/ProfileMatching/`.
- **Step 3**: `11CEN10GSS_HH_aggregation.py` completed and run with `--sample 10`.
  - Produced aggregated household schedules and validation artifacts under `Outputs_11CEN10GSS/HH_aggregation/`.
- **Step 4**: `11CEN10GSS_occToBEM.py` completed and run with `--sample 10`.
  - Produced hourly BEM schedules and validation plots under `Outputs_11CEN10GSS/BEM/`.

All deliverables for tasks 0 through 4 are complete and recorded above in the verified run outputs.

---

## Final Verification (2026-03-31)

### 11CEN10GSS Pipeline — Verification Summary ✅

#### Source files (all present)

| File | Status |
|---|---|
| `11CEN10GSS_main.py` | ✅ |
| `11CEN10GSS_step0.py` | ✅ |
| `11CEN10GSS_alignment.py` | ✅ |
| `11CEN10GSS_ProfileMatcher.py` | ✅ |
| `11CEN10GSS_HH_aggregation.py` | ✅ |
| `11CEN10GSS_occToBEM.py` | ✅ |
| `__init__.py` | ✅ |

#### Intermediate files (row counts match plan)

| File | Expected | Actual |
|---|---|---|
| `out10EP_ACT_PRE_coPRE.csv` | 283,287 | **283,287** ✅ |
| `GSS_2010_Merged.csv` | 283,287 | **283,287** ✅ |
| `2011_LINKED.csv` | 337,126 | **337,126** ✅ |

#### Alignment outputs

| File | Expected rows | Actual |
|---|---|---|
| `Aligned_GSS_2010.csv` | 219,584 | **219,584** ✅ (25 columns, no `DDAY.1`) |
| `Aligned_Census_2010.csv` | 273,678 | **273,678** ✅ |

#### Downstream outputs (all present, non-empty)

- **ProfileMatching**: `Full_Schedules` (1M+ rows), `Matched_Keys`, `Validation_sample10pct.txt`
- **HH_aggregation**: `Full_Aggregated` (15M+ rows), `Validation_HH`, `Validation_Plot.png`
- **occToBEM**: `BEM_Schedules` (600K+ rows), two validation plots

#### Validation quality (from the .txt reports)

- Tier distribution is healthy — Tier 4 (FailSafe) is only 2.9% WD / 7.9% WE
- All 54,548 person-days have exactly 288 time slots (5-min resolution)
- No social density logic errors
- BEM output has the expected columns: `SIM_HH_ID`, `Day_Type`, `Hour`, `Occupancy_Schedule`, `Metabolic_Rate`, etc.

**The pipeline completed correctly end-to-end. All expected files exist, row counts match the plan's documented values, and the validation reports are clean.**
