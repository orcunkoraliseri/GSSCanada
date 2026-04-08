# Occupancy Data Processing: All Historical Cycles

## 1. Introduction

This chapter describes the data processing pipelines for the four real-world occupancy datasets used in this study, spanning nearly two decades of Canadian Census and General Social Survey data:

| Pipeline | Census Year | GSS Cycle | GSS Year | Period Label |
|----------|:-----------:|:---------:|:--------:|:------------:|
| **06CEN05GSS** | 2006 | Cycle 19 — Time Use | 2005 | Mid-2000s |
| **11CEN10GSS** | 2011 | Cycle 24 — Time Use | 2010 | Early 2010s |
| **16CEN15GSS** | 2016 | Cycle 29 — Time Use | 2015 | Mid-2010s |
| **21CEN22GSS** | 2021 | Cycle 38 — Time Use | 2022 | Early 2020s |

> [!IMPORTANT]
> Unlike the synthetic 25CEN22GSS dataset, all four historical pipelines are derived entirely from **existing Statistics Canada microdata**. No synthetic classification or agent generation is applied — all individuals and their time-use diaries are real survey respondents. The processing pipelines focus exclusively on harmonizing, linking, and converting these real observations into building energy model (BEM) inputs.

The four pipelines share a common methodological core but differ in the number of processing steps, the set of harmonized variables, preprocessing requirements, and dwelling type (DTYPE) detail available in the Census PUMF. Table 1 provides a comparative overview.

**Table 1. Pipeline Comparison Across All Cycles**

| Feature | 06CEN05GSS | 11CEN10GSS | 16CEN15GSS | 21CEN22GSS |
|---------|:----------:|:----------:|:----------:|:----------:|
| Census Year | 2006 | 2011 | 2016 | 2021 |
| GSS Year | 2005 | 2010 | 2015 | 2022 |
| GSS Data Format | SAS7bdat | Fixed-width DAT + SPS | Fixed-width TXT + SPS | SAS7bdat |
| Pipeline Steps | 4 | 4 (+Step 0) | 5 | 4 (+Step 0) |
| Harmonized Variables | 11 | 10 | 9 | 8 |
| Default Sample | 5% | 10% | 10% | 10% |
| DTYPE Detail | Already detailed (1–8) | Already detailed (1–8) | Requires expansion (1–3 → 1–8) | Coarse (1–3) |
| Unique Step | — | Episode Preprocessing | DTYPE Expansion (ML-based) | Episode Preprocessing |
| HHSIZE Cap | 6 | 6 | 6 | 5 |
| Income Brackets | 12 | 12 | 7 | Not harmonized |
| BEM Output Resolution | Hourly (24 h) | Hourly (24 h) | Hourly (24 h) | Hourly (24 h) |

---

## 2. Step 0: Episode Preprocessing (11CEN10GSS and 21CEN22GSS Only)

### 2.1 Purpose

Convert raw GSS episode files into a standardized CSV format with harmonized activity codes, time formats, and presence indicators. This step runs automatically before the interactive pipeline menu.

### 2.2 Motivation

The GSS 2010 and GSS 2022 episode files require preprocessing because their raw formats (fixed-width DAT and SAS7bdat, respectively) use survey-specific activity coding schemes, decimal minute timestamps, and varied social companion variable names. Preprocessing normalizes these into the common schema expected by downstream steps.

> [!NOTE]
> The 06CEN05GSS and 16CEN15GSS pipelines do not require a dedicated Step 0 because their GSS episode data is parsed and normalized within the alignment step itself.

### 2.3 Process

1. **Read Raw Episode File**: Parse the GSS episode file using column specifications extracted from SPSS syntax files (GSS 2010) or directly from SAS format (GSS 2022).
2. **Rename Identifiers**: Map survey-specific IDs to common names (`RECID`/`PUMFID` → `occID`, `INSTANCE` → `EPINO`).
3. **Harmonize Activity Codes**: Map raw 3-digit GSS activity codes to a common 14-category activity classification using cycle-specific lookup tables (see Section 7.1).
4. **Convert Time Formats**: Transform decimal minutes-from-midnight to HHMM integer format (e.g., 540 minutes → 0900). Handles midnight wrapping via modulo 1440.
5. **Derive Presence Indicators**:
   - `PRE` / `occPRE`: Binary home presence (1 if location = home, 0 otherwise)
   - `coPRE`: Binary co-presence (1 if spouse, children, or other household members present)
6. **Create Social Alias Columns**: Standardize companion variables (`Spouse`, `Children`, `otherInFAMs`, `Alone`, `parents`, `Friends`, etc.) from survey-specific column names.
7. **Save**: Export to CSV (`out10EP_ACT_PRE_coPRE.csv` / `out22EP_ACT_PRE_coPRE.csv`).

### 2.4 Cycle-Specific Details

**Table 2. Step 0 Comparison**

| Aspect | 11CEN10GSS | 21CEN22GSS |
|--------|:----------:|:----------:|
| Input Format | Fixed-width DAT + SPSS `.SPS` | SAS7bdat |
| Raw Episode File | `C24EPISODE_withno_bootstrap.DAT` | `TU_ET_2022_Episode_PUMF.sas7bdat` |
| Home Location Code | `PLACE == 1` | `LOCATION == 3300` |
| Activity Map | `ACT_MAP_10` (range-based fallback) | `ACT_MAP_22` (code-block mapping) |
| Social Variables | SPOUSE, CHILDHSD, MEMBHSD | TUI_06A through TUI_06J, TUI_07, TUI_15 |
| Additional Derived | — | `techUse`, `wellbeing`, `colleagues` |
| Output Columns | ~20 | ~33 |

**Implementation**: `11CEN10GSS_step0.py` / `21CEN22GSS_step0.py`

---

## 3. Shared Pipeline Steps

All four pipelines share four core processing steps. While variable mappings and data formats differ between survey cycles, the methodological approach is identical.

### 3.1 Step 1: Census–GSS Alignment (Harmonization)

**Purpose**: Harmonize the coding schemes between Census and GSS microdata so that demographic variables can be compared and used for profile matching.

**Motivation**: The Census and GSS use different variable coding systems for the same demographic concepts. For example, Census may encode age in 5-year groups (codes 1–13) while GSS uses 10-year groups (codes 1–7). Alignment creates a common schema by mapping one coding system to the other.

**Process**:

1. **Load Census Data**: Read the filtered Census Public Use Microdata File (PUMF). Reconstruct household structures using sequential household IDs via the `assemble_households()` function.
   - **Phase 1 — Singles**: Each individual with HHSIZE = 1 becomes a standalone household.
   - **Phase 2 — Families**: Family heads (CF_RP = 1) anchor households; family members and non-family persons are assigned to fill remaining slots.
   - **Phase 3 — Roommates**: Remaining non-family agents (CF_RP = 3) are grouped by household size.
   - Each household receives a unique `SIM_HH_ID`.

2. **Load GSS Data**: Read the GSS time-use episode file and merge with GSS demographic data (main file). The reading method varies by cycle:
   - **06CEN05GSS**: SAS7bdat format with chunk-based merging
   - **11CEN10GSS**: Fixed-width text parsed using SPSS `.SPS` column specifications
   - **16CEN15GSS**: Fixed-width text parsed using SPSS `.SPS` column specifications
   - **21CEN22GSS**: SAS7bdat format with social alias standardization

3. **Apply Harmonization Functions**: For each demographic variable, a dedicated function maps value codes to a common scheme. The mapping direction depends on which dataset has the simpler coding (generally mapping the more detailed dataset to the simpler one).

4. **Clean Invalid Codes**: Remove records with ambiguous responses (e.g., "Don't Know", "Not Stated", rural areas without Census equivalents).

5. **Filter Implausible Records**: Remove records with ROOM > 15 (implausible residential buildings) and child records (AGEGRP codes for ages < 15).

6. **Validate Alignment**: Compare unique value sets between harmonized Census and GSS to confirm alignment. Generate side-by-side distribution comparison plots.

7. **Save**: Export aligned Census and GSS DataFrames to CSV.

#### 3.1.1 Harmonized Variables by Cycle

**Table 3. Demographic Variables Harmonized by Each Pipeline**

| Variable | Description | 06CEN | 11CEN | 16CEN | 21CEN | Harmonized Range |
|----------|-------------|:-----:|:-----:|:-----:|:-----:|:----------------:|
| AGEGRP | Age Group | ✓ | ✓ | ✓ | ✓ | 1–7 |
| SEX | Sex | ✓ | ✓ | ✓ | ✓ | 1–2 |
| MARSTH | Marital Status | ✓ | ✓ | ✓ | ✓ | 1–3 |
| HHSIZE | Household Size | ✓ | ✓ | ✓ | ✓ | 1–6 (1–5 for 21CEN) |
| LFTAG | Labour Force Activity | ✓ | ✓ | ✓ | ✓ | 1–5 |
| CMA | Census Metropolitan Area | ✓ | ✓ | ✓ | ✓ | 1–2 |
| PR | Province/Region | ✓ | ✓ | ✓ | ✓ | {10, 24, 35, 46, 48, 59} |
| KOL | Knowledge of Official Languages | ✓ | ✓ | ✓ | ✓ | 1–3 |
| TOTINC | Total Income | ✓ | ✓ | ✓ | ✗ | 1–12 (06/11CEN); 1–7 (16CEN) |
| ATTSCH | School Attendance | ✓ | ✗ | ✗ | ✗ | 1–2 |
| NOCS | Occupation Classification | ✓ | ✓ | ✗ | ✗ | 1–10, 99 |
| **Total** | | **11** | **10** | **9** | **8** | |

> [!NOTE]
> Variable availability decreases across newer PUMF releases. GSS 2015 and 2022 omit ATTSCH and NOCS from their public-use files. GSS 2022 additionally omits TOTINC, reflecting Statistics Canada's evolving disclosure control practices.

#### 3.1.2 Harmonization Mapping Details

**AGEGRP (Age Group)** — All cycles map Census 5-year groups to GSS 10-year groups:

| Harmonized Code | Age Range | Census Codes (5-yr) | GSS Codes (10-yr) |
|:---:|---|---|---|
| 1 | 15–24 | 3, 4 | 1 |
| 2 | 25–34 | 5, 6 | 2 |
| 3 | 35–44 | 7, 8 | 3 |
| 4 | 45–54 | 9, 10 | 4 |
| 5 | 55–64 | 11 | 5 |
| 6 | 65–74 | 12 | 6 |
| 7 | 75+ | 13 | 7 |

Census codes 1–2 (ages 0–14) are filtered out. GSS codes 96–99 (unknown/not stated) are dropped.

**SEX** — Direct match in most cycles (1 = Male, 2 = Female). The 21CEN22GSS pipeline swaps GSS values (GSS 1 → 2, GSS 2 → 1) to align with the Census convention.

**MARSTH (Marital Status)** — All cycles harmonize to 3 categories:

| Code | Category | Census Values | GSS Values |
|:---:|---|---|---|
| 1 | Married / Common-law | 1 (Married), 2 (Common-law) | 1, 2 |
| 2 | Single / Never married | 3 (Not married) in 06CEN; varies | 6 |
| 3 | Widowed / Separated / Divorced | — | 3, 4, 5 |

> [!NOTE]
> The Census 2006 PUMF uses a simplified 3-category marital status (1=Married, 2=Common-law, 3=Not married), so GSS values are mapped to the Census scheme. Later Census years provide more detail, and the mapping direction reverses.

**HHSIZE (Household Size)** — Census values 7+ are capped at 6 for all cycles except 21CEN22GSS, which caps at 5. GSS values are already within range.

**LFTAG (Labour Force Activity)** — Census 14-category classification mapped to GSS 5-category:

| Harmonized Code | Category | Census Codes |
|:---:|---|---|
| 1 | Employed full-time | 1 |
| 2 | Employed other (part-time, self-employed) | 2–6 |
| 3 | Unemployed / seeking | 7–11 |
| 4 | Not in labour force | 12, 13 |
| 5 | Retired / Other | 14 |

GSS codes 6, 8, 9 (unclassified) are dropped.

**CMA (Census Metropolitan Area)** — Harmonized to a binary urban classification:

| Code | Category | Census Codes | GSS Codes |
|:---:|---|---|---|
| 1 | Major CMA (500K+) | 462, 505, 535, 825, 835, 933, 408 | 1 |
| 2 | Other urban | 996, 999 | 2 |
| — | Rural (dropped) | 997 | 3 |

> [!NOTE]
> The specific Census CMA codes included as "Major CMA" vary slightly by cycle (e.g., 21CEN22GSS uses {462, 535, 825, 835, 933}). Rural records are excluded in all cycles to maintain Census–GSS comparability.

**PR (Province/Region)** — Aggregated to 6 regional codes:

| Code | Region | Census Province Codes |
|:---:|---|---|
| 10 | Atlantic | 10 (NL), 11 (PE), 12 (NS), 13 (NB) |
| 24 | Quebec | 24 |
| 35 | Ontario | 35 |
| 46 | Prairies | 46 (MB), 47 (SK) |
| 48 | Alberta | 48 |
| 59 | British Columbia | 59 |

Territories (60–62) are dropped.

**KOL (Knowledge of Official Languages)** — Harmonized to 3 categories: 1 = English only, 2 = French only, 3 = Both. "Neither" (Census 4) and DK/NS (GSS 4, 7–9, 99) are dropped.

**TOTINC (Total Income)** — Census continuous dollar values are binned into categorical brackets matching the GSS scheme. The number of brackets varies:
- **06CEN05GSS / 11CEN10GSS**: 12 brackets (from ≤$0 to ≥$100K)
- **16CEN15GSS**: 7 brackets (from ≤$0 to ≥$100K, wider bands)
- **21CEN22GSS**: Not harmonized (TOTINC unavailable in GSS 2022 PUMF)

**ATTSCH (School Attendance)** — 06CEN05GSS only. GSS Full-time/Part-time → Census Attending (1), GSS Not attending → Census Not (2). DK/NS dropped.

**NOCS (Occupation Classification)** — 06CEN05GSS and 11CEN10GSS only. GSS DK/NS codes (88, 97, 98) mapped to 99 (Not applicable).

**Implementation**: `06CEN05GSS_alignment.py` / `11CEN10GSS_alignment.py` / `16CEN15GSS_alignment.py` / `21CEN22GSS_alignment.py`

---

### 3.2 Step 2: Profile Matching

**Purpose**: Assign real GSS time-use schedules to Census agents based on demographic similarity.

**Motivation**: The Census provides detailed demographic data for all Canadians but contains no time-use information. The GSS contains detailed 24-hour time-use diaries but covers only a sample of the population (~20,000–25,000 respondents per cycle). Profile matching bridges this gap by assigning each Census agent the time-use diary of a demographically similar GSS respondent.

**Process**:

The `MatchProfiler` class implements a **tiered matching** strategy:

1. **Catalog Preparation**: The GSS dataset is split into two catalogs based on the diary day variable (`DDAY`):
   - **Weekday** catalog: DDAY ∈ {2, 3, 4, 5, 6} (Monday–Friday)
   - **Weekend** catalog: DDAY ∈ {1, 7} (Sunday, Saturday)
   Each catalog is deduplicated by `occID` to create unique demographic profiles for matching.

2. **Tiered Matching**: For each Census agent, the algorithm cascades through progressively relaxed matching tiers until a match is found:

**Table 4. Matching Tiers Across Cycles**

| Tier | Name | 06CEN05GSS (11 cols) | 11CEN10GSS (9 cols) | 16CEN15GSS (9 cols) | 21CEN22GSS (8 cols) |
|:---:|---|---|---|---|---|
| 1 | Perfect | All 11 vars | All 9 vars | All 9 vars | All 8 vars |
| 2 | Core | HHSIZE, AGEGRP, SEX, MARSTH, LFTAG, PR | Same 6 | Same 6 | Same 6 |
| 3 | Constraints | HHSIZE, AGEGRP, SEX | Same 3 | Same 3 | Same 3 |
| 4 | Fail-Safe | HHSIZE | HHSIZE | HHSIZE | HHSIZE |
| 5 | Random | Any GSS record | Any | Any | Any |

3. **Day-Type Matching**: Each Census agent receives two separate matches — one from the weekday catalog (`MATCH_ID_WD`) and one from the weekend catalog (`MATCH_ID_WE`), each with its corresponding tier label.

4. **Schedule Expansion**: After matching, the `ScheduleExpander` class retrieves the full variable-length episode lists for each matched GSS respondent. These episodes contain:
   - Start time and end time (in HHMM format)
   - Activity code (harmonized 1–14)
   - Location / presence indicator (home/away)
   - Duration
   - Social companion indicators

The expanded schedules are saved as a comprehensive CSV linking Census agent demographics with their assigned GSS time-use episodes.

**Sampling**: A configurable sample percentage controls the number of Census agents processed:

| Pipeline | Default Sample | Sampling Method |
|----------|:--------------:|-----------------|
| 06CEN05GSS | 5% | By household (preserves all members) |
| 11CEN10GSS | 10% | By household + by GSS occupant |
| 16CEN15GSS | 10% | By household + by GSS occupant |
| 21CEN22GSS | 10% | By household + by GSS occupant |

**Validation**: The `validate_matching_quality()` function analyzes:
- Distribution of matches across tiers (% perfect, core, constraints, fail-safe, random)
- Behavioral consistency: for employed agents, average work duration (~300–600 min/day expected)
- Episode count sanity checks (typically 10–30 episodes per person per day type)

**Implementation**: `06CEN05GSS_ProfileMatcher.py` / `11CEN10GSS_ProfileMatcher.py` / `16CEN15GSS_ProfileMatcher.py` / `21CEN22GSS_ProfileMatcher.py`

---

### 3.3 Household Aggregation

> Step 3 for 06CEN05GSS and 11CEN10GSS; Step 4 for 16CEN15GSS; Step 3 for 21CEN22GSS.

**Purpose**: Transform individual-level, variable-length episode lists into standardized household-level occupancy profiles at 5-minute resolution.

**Motivation**: GSS time-use diaries are recorded at the individual level with variable-length episodes (e.g., "slept from 00:00 to 07:30, commuted from 07:30 to 08:15..."). Building energy simulation requires household-level schedules at regular time intervals. This step bridges that gap.

**Process**:

The `HouseholdAggregator` class performs four sub-steps:

**A. Grid Construction (Individual)**: Convert each person's variable-length episode list into a fixed 288-slot array (24 hours × 12 slots/hour = 5-minute resolution). Each slot is assigned:
- `ind_occPRE`: Location presence — 1 = home, 0 = away
- `ind_occACT`: Activity code (harmonized 1–14)
- `ind_density`: Social density — count of co-present companions (only counted when the person is home)

Episode time conversion: HHMM → minutes → slot index (e.g., 1030 → 630 min → slot 126). Midnight-wrapping episodes (e.g., 23:00–07:00) are handled by splitting across day boundaries.

**B. Household Assembly**: Group all individuals belonging to the same household (via `SIM_HH_ID`) and day type (Weekday/Weekend).

**C. Occupancy Aggregation**: For each 5-minute time slot, calculate:
- **`occPre`** (Binary Presence): 1 if any household member is at home, 0 if the house is empty
- **`occDensity`** (Social Density): Sum of social companion counts across all present household members
- **`occActivity`** (Activity Set): Comma-separated set of unique activity codes among present members (e.g., "1,5,9"); "0" if no one is home

**D. Demographic Merge**: Preserve all static Census demographic columns (DTYPE, BEDRM, ROOM, TOTINC, HHSIZE, CONDO, REPAIR, PR, etc.) alongside the aggregated temporal profiles.

**Resolution**: 288 time slots per day (5-minute intervals).

**Validation**: The `validate_household_aggregation()` function verifies:
- **Completeness**: All person-days have exactly 288 time slots
- **Logic**: No social density when house is empty (`occPre = 0` → `occDensity = 0`)
- **Activity consistency**: Activity string = "0" when house is empty

**Visualization**: The `visualize_multiple_households()` function generates a 4×4 grid plot (16 sample households) showing:
- Green fill: Occupancy presence over time
- Blue line: Social density over time
- X-axis: Time of day (288 slots = 24 hours)

**Implementation**: `06CEN05GSS_HH_aggregation.py` / `11CEN10GSS_HH_aggregation.py` / `16CEN15GSS_HH_aggregation.py` / `21CEN22GSS_HH_aggregation.py`

---

### 3.4 BEM Conversion

> Step 4 for 06CEN05GSS and 11CEN10GSS; Step 5 for 16CEN15GSS; Step 4 for 21CEN22GSS.

**Purpose**: Convert 5-minute household occupancy profiles into hourly BEM schedules compatible with EnergyPlus.

**Motivation**: EnergyPlus building energy models require hourly schedule inputs for occupancy, metabolic heat gains, and residential characteristics. This step downsamples and reformats the 5-minute profiles.

**Process**:

The `BEMConverter` class performs:

1. **Temporal Downsampling**: Aggregate 5-minute slots into hourly values (12 slots → 1 hour) using mean aggregation for presence and density, and average for metabolic rates.

2. **Metabolic Rate Calculation**: Map harmonized activity codes to metabolic rates in Watts using a standardized activity-to-Watts lookup table based on the 2024 Compendium of Physical Activities.

**Table 5. Activity-to-Metabolic-Rate Mapping**

| Activity Code | Activity Category | MET | Watts |
|:---:|---|:---:|:---:|
| 1 | Work & Related | 1.8 | 125 |
| 2 | Household Work | 2.5 | 175 |
| 3 | Caregiving | 2.7 | 190 |
| 4 | Shopping / Services | 2.8 | 195 |
| 5 | Sleep | 1.0 | 70 |
| 6 | Eating | 1.5 | 105 |
| 7 | Personal Care | 2.4 | 170 |
| 8 | Education | 1.6 | 110 |
| 9 | Socializing | 1.3 | 90 |
| 10 | Passive Leisure (TV, Reading) | 1.2 | 85 |
| 11 | Active Leisure (Exercise) | 3.5 | 245 |
| 12 | Volunteer | 1.5 | 105 |
| 13 | Travel | 2.0 | 140 |
| 14 | Miscellaneous | 1.9 | 135 |
| 0 | Empty / Away | — | 0 |

> [!NOTE]
> When multiple activities are present in a single time slot (e.g., activity string "1,5,9"), the `_calculate_watts()` method averages the corresponding metabolic rates: (125 + 70 + 90) / 3 = 95 W.

3. **Occupancy Fraction Calculation**:

```
estimated_count[t] = occPre[t] × (occDensity[t] + 1)
occupancy_schedule[t] = min(estimated_count[t] / HHSIZE, 1.0)
```

Where:
- `occPre[t]` ∈ [0, 1] — fraction of the hour with someone home
- `occDensity[t]` — average social density during the hour
- `HHSIZE` — total household members
- Result clipped to [0, 1]

4. **Residential Attribute Mapping**: Convert numeric codes to descriptive labels:

**DTYPE (Dwelling Type)**:

| Code | Label | Available In |
|:---:|---|---|
| 1 | SingleD (Single-Detached) | All cycles |
| 2 | SemiD (Semi-Detached) | 06CEN, 11CEN, 16CEN (after expansion) |
| 3 | Attached (Row House) | 06CEN, 11CEN, 16CEN (after expansion) |
| 4 | DuplexD (Duplex) | 06CEN, 11CEN, 16CEN (after expansion) |
| 5 | HighRise (5+ Storeys) | 06CEN, 11CEN, 16CEN (after expansion) |
| 6 | MidRise (< 5 Storeys) | 06CEN, 11CEN, 16CEN (after expansion) |
| 7 | OtherA (Other Attached) | 06CEN, 11CEN, 16CEN (after expansion) |
| 8 | Movable (Mobile Home) | 06CEN, 11CEN, 16CEN (after expansion) |

> [!NOTE]
> The 21CEN22GSS pipeline uses the coarse 3-category DTYPE directly (1 = SingleD, 2 = Apartment, 3 = OtherDwelling) without ML-based expansion.

**PR (Province/Region)**:

| Code | Label |
|:---:|---|
| 10 | Atlantic |
| 24 | Quebec |
| 35 | Ontario |
| 46 | Prairies |
| 48 | Alberta |
| 59 | BC |

5. **Output Schema**: Generate a structured DataFrame with:
   - `SIM_HH_ID`, `Day_Type` (Weekday/Weekend), `Hour` (0–23)
   - `HHSIZE` — Household size
   - `DTYPE` — Dwelling type (string label)
   - `BEDRM` — Bedroom count
   - `CONDO` — Condominium status
   - `ROOM` — Total room count
   - `REPAIR` — Repair condition code
   - `PR` — Province/region (string label)
   - `Occupancy_Schedule` — Fractional occupancy [0.0–1.0]
   - `Metabolic_Rate` — Watts per person (0–250 typical)

6. **Validation**: The BEM converter includes a sanity check comparing mean nighttime (hours 0–6) vs. daytime (hours 9–17) occupancy. For residential buildings, nighttime occupancy should exceed daytime (people sleep at home).

7. **Visualization**: Two plot files are generated:
   - **Temporal Plots** (3×2 grid): Occupancy distribution, metabolic distribution, average presence schedules (weekday vs. weekend), average metabolic intensity, and sample household profiles (dual-axis: occupancy + metabolic rate)
   - **Non-Temporal Plots** (2×2 grid): Distribution of dwelling types, bedroom counts, total rooms, and provinces/regions

**Implementation**: `06CEN05GSS_occToBEM.py` / `11CEN10GSS_occToBEM.py` / `16CEN15GSS_occToBEM.py` / `21CEN22GSS_occToBEM.py`

---

## 4. Unique Step: DTYPE Expansion (16CEN15GSS Only)

### 4.1 Step 3: DTYPE Expansion and Refinement

**Purpose**: Refine the coarse dwelling type classification (DTYPE 1–3) available in Census 2016 into the detailed 8-category classification (DTYPE 1–8) used in Census 2006/2011 and required for BEM configuration.

**Motivation**: Census 2016 PUMF provides only three dwelling type categories:

| Coarse DTYPE | Description |
|:---:|---|
| 1 | Single-detached house |
| 2 | Apartment |
| 3 | Other (semi-detached, row house, duplex, mobile, etc.) |

Building energy simulation requires finer dwelling type resolution to select appropriate baseline IDF models and configure building parameters. The detailed 8-category classification is:

| Detailed DTYPE | Description |
|:---:|---|
| 1 | Single-detached house |
| 2 | Semi-detached house |
| 3 | Row house |
| 4 | Duplex / apartment in duplex |
| 5 | Apartment in building with 5+ storeys (high-rise) |
| 6 | Apartment in building with < 5 storeys (low-rise) |
| 7 | Other single-attached house |
| 8 | Movable dwelling |

> [!IMPORTANT]
> Coarse DTYPE 1 (Single-detached) maps directly to Detailed DTYPE 1 with no refinement needed. Only coarse types 2 and 3 require machine learning-based expansion.

**Process**:

The `DTypeRefiner` class uses **Random Forest classifiers** trained on historic Census data (2006 and 2011) which already contain the detailed DTYPE classification:

1. **Merge Keys**: Retrieve additional Census variables (CFSIZE, TOTINC, CONDO, REPAIR, ROOM, BEDRM) from the matched Census keys file into the profile matching output.

2. **Feature Engineering**: Derive additional predictive features:
   - `ROOM_PER_PERSON` = ROOM ÷ HHSIZE
   - `BEDRM_RATIO` = BEDRM ÷ ROOM
   - `INCOME_PER_PERSON` = TOTINC ÷ HHSIZE

3. **Model Training**: Train two separate Random Forest classifiers on historic Census data:
   - **Model A (Apartments)**: Trained on records with DTYPE ∈ {5, 6}. Distinguishes between high-rise (5) and low-rise (6) apartments.
   - **Model B (Other Dwellings)**: Trained on records with DTYPE ∈ {2, 3, 4, 7, 8}. Distinguishes between semi-detached, row house, duplex, mobile, and other dwellings.
   - Both models use 200 estimators, max depth 20, and balanced class weights.
   - Model B applies custom class weights (Semi/Row weighted 2.0×) to address class imbalance.

**Training Features**: BEDRM, ROOM, PR, HHSIZE, CONDO, REPAIR, TOTINC, CFSIZE, ROOM_PER_PERSON, BEDRM_RATIO, INCOME_PER_PERSON

4. **Quota-Calibrated Prediction**: Rather than using raw model predictions (which may not match known national distributions), a **quota sampling** algorithm is applied:
   - Calculate prediction probabilities for each household
   - Enforce target distribution ratios based on historic Census proportions:
     - **Apartments**: 34% high-rise, 66% low-rise
     - **Other**: 33% row, 29% semi-detached, 29% duplex, 7% mobile, 2% other
   - Assign categories by selecting the top-ranked candidates for each quota target

5. **Validation**: Compare the refined DTYPE distribution against historic Census distributions using the `validate_refinement_model()` function.

**Training Data**: Census 2006 (`cen06_filtered2.csv`) and Census 2011 (`cen11_filtered2.csv`) — both contain the detailed 8-category DTYPE classification.

**Implementation**: `16CEN15GSS_DTYPE_expansion.py`

> [!NOTE]
> The 21CEN22GSS pipeline also receives coarse DTYPE (1–3) from Census 2021 but does **not** include a DTYPE expansion step. It uses the coarse classification directly (1 = SingleD, 2 = Apartment, 3 = OtherDwelling).

---

## 5. Pipeline Orchestration

Each pipeline is controlled by a `*_main.py` script that provides:
- An interactive menu system for step-by-step execution
- Command-line argument support (`--sample` for percentage, `--run` for direct step execution)
- Dynamic module loading via `importlib.util`
- Error handling with pass/fail feedback at each step
- Pipeline summary after full execution

**Table 6. Menu Options Across Cycles**

| Option | 06CEN05GSS | 11CEN10GSS | 16CEN15GSS | 21CEN22GSS |
|--------|:----------:|:----------:|:----------:|:----------:|
| Step 1: Alignment | ✓ | ✓ | ✓ | ✓ |
| Step 2: Profile Matching | ✓ | ✓ | ✓ | ✓ |
| Step 3: DTYPE Expansion | ✗ | ✗ | ✓ | ✗ |
| Step 3/4: HH Aggregation | ✓ (Step 3) | ✓ (Step 3) | ✓ (Step 4) | ✓ (Step 3) |
| Step 4/5: BEM Conversion | ✓ (Step 4) | ✓ (Step 4) | ✓ (Step 5) | ✓ (Step 4) |
| Full Pipeline | ✓ | ✓ | ✓ | ✓ |
| Census DTYPE Analysis | ✓ | ✓ | ✓ | ✗ |
| GSS Header Reader | ✓ | ✗ | ✗ | ✗ |
| Change Sample % | ✓ | ✓ | ✓ | ✓ |

**Step 0** (11CEN10GSS and 21CEN22GSS) runs automatically before the menu appears.

**Command-line usage** (all cycles):
```bash
python *_main.py                     # Interactive menu
python *_main.py --sample 25         # Set sample percentage
python *_main.py --sample 10 --run 5 # Run full pipeline at 10%
```

---

## 6. Pipeline Data Flow Diagrams

### 6.1 06CEN05GSS Data Flow (4 Steps)

```
Census 2006 PUMF ──┐
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
GSS 2005 Episodes ─┘          (11 vars)                   │
                                                           ▼
                         [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                           │
                                                           ▼
                         [Step 3: HH Aggregation] ──▶ Household 5-min Profiles (288 slots)
                                                           │
                                                           ▼
                         [Step 4: BEM Conversion] ──▶ Hourly BEM Schedules (24 hours)
```

### 6.2 11CEN10GSS Data Flow (Step 0 + 4 Steps)

```
GSS 2010 Raw DAT ──▶ [Step 0: Episode Preprocessing] ──▶ Harmonized Episode CSV
                                                                │
Census 2011 PUMF ──┐                                            │
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
Harmonized GSS ────┘          (10 vars)                   │
                                                           ▼
                         [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                           │
                                                           ▼
                         [Step 3: HH Aggregation] ──▶ Household 5-min Profiles (288 slots)
                                                           │
                                                           ▼
                         [Step 4: BEM Conversion] ──▶ Hourly BEM Schedules (24 hours)
```

### 6.3 16CEN15GSS Data Flow (5 Steps)

```
Census 2016 PUMF ──┐
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
GSS 2015 Episodes ─┘          (9 vars)                    │
                                                           ▼
                         [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                           │
                                                           ▼
Census 2006 PUMF ──┐
Census 2011 PUMF ──┤──▶ [Step 3: DTYPE Expansion] ──▶ Refined Schedules (DTYPE 1-8)
                   │                                       │
                   │    (ML training data)                  ▼
                                       [Step 4: HH Aggregation] ──▶ Household 5-min Profiles
                                                           │
                                                           ▼
                                       [Step 5: BEM Conversion] ──▶ Hourly BEM Schedules
```

### 6.4 21CEN22GSS Data Flow (Step 0 + 4 Steps)

```
GSS 2022 SAS7bdat ──▶ [Step 0: Episode Preprocessing] ──▶ Harmonized Episode CSV
                                                                │
Census 2021 PUMF ──┐                                            │
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
Harmonized GSS ────┘          (8 vars)                    │
                                                           ▼
                         [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                           │
                                                           ▼
                         [Step 3: HH Aggregation] ──▶ Household 5-min Profiles (288 slots)
                                                           │
                                                           ▼
                         [Step 4: BEM Conversion] ──▶ Hourly BEM Schedules (24 hours)
```

---

## 7. Activity Code Harmonization

### 7.1 Harmonized Activity Categories

All pipelines map raw GSS activity codes to a common 14-category classification. The mapping tables differ by GSS cycle because each survey uses a different activity coding scheme, but the output categories are consistent.

**Table 7. Harmonized Activity Categories (1–14)**

| Code | Category | Description |
|:---:|---|---|
| 1 | Work & Related | Paid work, employment activities |
| 2 | Household Work | Cleaning, cooking, maintenance |
| 3 | Caregiving | Child care, elder care |
| 4 | Shopping / Services | Errands, purchases |
| 5 | Sleep | Sleeping, lying quietly |
| 6 | Eating | Meals, snacks |
| 7 | Personal Care | Grooming, hygiene, dressing |
| 8 | Education | School, studying, classes |
| 9 | Socializing | Conversations, social events |
| 10 | Passive Leisure | TV, reading, relaxing |
| 11 | Active Leisure | Sports, exercise, walking |
| 12 | Volunteer | Civic activities, volunteering |
| 13 | Travel | Commuting, driving, transit |
| 14 | Miscellaneous | Other activities |
| 0 | Empty | No activity / away from home |

### 7.2 Cycle-Specific Mapping Approaches

- **GSS 2005 (06CEN05GSS)**: Activity codes mapped during alignment step via SAS7bdat processing.
- **GSS 2010 (11CEN10GSS)**: Uses `ACT_MAP_10` — explicit code-to-category mapping with range-based fallback (e.g., all 2xx codes → Household Work if not explicitly mapped). Raw codes are SPSS implied-decimal format (stored integer / 10).
- **GSS 2015 (16CEN15GSS)**: Activity codes mapped during alignment step, similar structure to GSS 2005.
- **GSS 2022 (21CEN22GSS)**: Uses `ACT_MAP_22` — code-block mapping where activity codes are grouped in hundreds (e.g., 100–199 → Sleep/Personal, 400 → Employment, 500 → Social/Leisure).

---

## 8. DTYPE Handling Across Cycles

The availability of detailed dwelling type information varies significantly across Census PUMF releases:

**Table 8. DTYPE Availability and Handling**

| Pipeline | Census DTYPE | Categories | Handling | Result |
|----------|:----------:|:---------:|---------|:------:|
| 06CEN05GSS | Detailed | 1–8 | Direct pass-through | 8 types |
| 11CEN10GSS | Detailed | 1–8 | Direct pass-through | 8 types |
| 16CEN15GSS | Coarse | 1–3 | ML expansion (Random Forest) | 8 types |
| 21CEN22GSS | Coarse | 1–3 | No expansion (coarse used directly) | 3 types |

> [!IMPORTANT]
> The transition from detailed to coarse DTYPE in Census 2016 and 2021 PUMFs reflects Statistics Canada's disclosure control changes. The 16CEN15GSS pipeline addresses this through ML-based expansion using historical Census data as training data. The 21CEN22GSS pipeline uses the coarse classification directly.

---

## 9. Input Data Sources

### 9.1 Census PUMF Files

**Table 9. Census Input Files**

| Pipeline | Census File | Year | Records | DTYPE Detail |
|----------|-------------|:----:|:-------:|:----:|
| 06CEN05GSS | `cen06_filtered.csv` / `2006_LINKED.csv` | 2006 | ~80K+ | 1–8 |
| 11CEN10GSS | `cen11_filtered.csv` | 2011 | ~200K | 1–8 |
| 16CEN15GSS | `cen16_filtered.csv` | 2016 | ~274K | 1–3 |
| 21CEN22GSS | `cen21_filtered.csv` | 2021 | ~250K+ | 1–3 |

All Census files are located under `0_Occupancy/Outputs_CENSUS/` (filtered) or `0_Occupancy/DataSources_CENSUS/` (raw PUMF).

### 9.2 GSS Data Files

**Table 10. GSS Input Files**

| Pipeline | GSS Main File | GSS Episode File | Format |
|----------|---------------|-------------------|--------|
| 06CEN05GSS | `GSSMain_2005.sas7bdat` | Pre-processed CSV | SAS7bdat |
| 11CEN10GSS | `GSSMain_2010.DAT` + `.SPS` | `C24EPISODE_withno_bootstrap.DAT` + `.SPS` | Fixed-width |
| 16CEN15GSS | `GSSMain_2015.TXT` + `.SPS` | Pre-processed CSV | Fixed-width |
| 21CEN22GSS | `GSSMain_2022.sas7bdat` | `TU_ET_2022_Episode_PUMF.sas7bdat` | SAS7bdat |

GSS main files are located under `0_Occupancy/DataSources_GSS/Main_files/`.
GSS episode files are located under `0_Occupancy/DataSources_GSS/Episode_files/`.

---

## 10. Output Directory Structure

```
0_Occupancy/
├── Outputs_06CEN05GSS/
│   ├── alignment/              # Step 1: Aligned_Census_2005.csv, Aligned_GSS_2005.csv
│   ├── ProfileMatching/        # Step 2: Matched Keys + Full Schedules + Validation
│   ├── HH_aggregation/         # Step 3: 5-min grids + Validation reports + Plots
│   └── occToBEM/               # Step 4: BEM Schedules + Temporal/Non-temporal plots
│
├── Outputs_11CEN10GSS/
│   ├── alignment/              # Step 1: Aligned_Census_2010.csv, Aligned_GSS_2010.csv
│   ├── ProfileMatching/        # Step 2: Matched Keys + Full Schedules + Validation
│   ├── HH_aggregation/         # Step 3: 5-min grids + Validation reports + Plots
│   └── occToBEM/               # Step 4: BEM Schedules + Temporal/Non-temporal plots
│
├── Outputs_16CEN15GSS/
│   ├── alignment/              # Step 1: Aligned_Census_2015.csv, Aligned_GSS_2015.csv
│   ├── ProfileMatching/        # Step 2: Matched Keys + Full Schedules + Validation
│   ├── DTYPE_expansion/        # Step 3: Refined Schedules (DTYPE 1-8)
│   │   └── Validation/         #          DTYPE distribution comparison reports
│   ├── HH_aggregation/         # Step 4: 5-min grids + Validation reports + Plots
│   └── occToBEM/               # Step 5: BEM Schedules + Temporal/Non-temporal plots
│
├── Outputs_21CEN22GSS/
│   ├── alignment/              # Step 1: Aligned_Census_2022.csv, Aligned_GSS_2022.csv
│   ├── ProfileMatching/        # Step 2: Matched Keys + Full Schedules + Validation
│   ├── HH_aggregation/         # Step 3: 5-min grids + Validation reports + Plots
│   └── occToBEM/               # Step 4: BEM Schedules + Temporal/Non-temporal plots
```

### 10.1 Output File Naming Convention

All output files follow the pattern: `{PIPELINE}_{OutputType}_sample{N}pct.{ext}`

Examples:
- `06CEN05GSS_BEM_Schedules_sample25pct.csv`
- `11CEN10GSS_Matched_Keys_sample10pct.csv`
- `16CEN15GSS_Full_Aggregated_sample25pct.csv`
- `21CEN22GSS_Validation_HH_sample1pct.txt`

### 10.2 Output File Summary

**Table 11. Key Output Files per Step**

| Step | File Pattern | Content | Rows (typical 25%) |
|------|-------------|---------|:---:|
| Alignment | `Aligned_Census_*.csv` | Harmonized Census demographics | ~50K–224K |
| Alignment | `Aligned_GSS_*.csv` | Harmonized GSS demographics + episodes | ~240K–1.3M |
| Profile Matching | `*_Matched_Keys_*.csv` | Census agents with matched GSS IDs | ~54K |
| Profile Matching | `*_Full_Schedules_*.csv` | Expanded episodes with Census metadata | ~1.7M–1.8M |
| Profile Matching | `*_Validation_*.txt` | Matching tier distribution report | — |
| DTYPE Expansion | `*_Full_Schedules_Refined_*.csv` | Schedules with DTYPE 1–8 (16CEN only) | ~1.7M |
| HH Aggregation | `*_Full_Aggregated_*.csv` | 5-min household grids (288 slots × agents × 2 day types) | ~31M–32M |
| HH Aggregation | `*_Validation_HH_*.txt` | Completeness and logic checks | — |
| HH Aggregation | `*_Validation_Plot_*.png` | 16-household visual verification | — |
| BEM Conversion | `*_BEM_Schedules_*.csv` | Hourly occupancy + metabolic schedules | ~1.4M–1.5M |
| BEM Conversion | `*_BEM_temporals.png` | 6-panel temporal distributions | — |
| BEM Conversion | `*_BEM_non_temporals.png` | 4-panel residential variable distributions | — |

---

## 11. Key Differences from 25CEN22GSS

| Aspect | Historical Pipelines (06/11/16/21 CEN) | 25CEN22GSS |
|--------|----------------------------------------|------------|
| **Data Origin** | Real Statistics Canada microdata (Census PUMF + GSS Time Use) | Synthetic dataset generated from models |
| **Classification** | No classification applied — categories come directly from survey data | Requires synthetic classification and agent generation |
| **Occupancy Diaries** | Real 24-hour time-use diaries from GSS respondents | Synthetically generated occupancy schedules |
| **Pipeline Complexity** | 4–5 steps (harmonize → match → [expand] → aggregate → convert) | Additional steps for synthetic data generation (CVAE) |
| **DTYPE Source** | Census PUMF (06/11CEN: detailed; 16CEN: ML expansion; 21CEN: coarse) | Synthetically assigned |
| **Population Coverage** | Limited to Census/GSS sample years | Can project to future years (2025, 2030) |

> [!NOTE]
> All datasets ultimately produce the same output format: **hourly BEM schedules** with fractional occupancy, metabolic rates, and residential variables. The shared downstream steps (Household Aggregation and BEM Conversion) use identical logic regardless of data origin, ensuring consistency across all temporal scenarios in the simulation framework.

---

## 12. Cross-Cycle Evolution

### 12.1 Data Availability Trends

The progressive reduction in harmonized variables across cycles reflects Statistics Canada's evolving disclosure control practices for PUMF releases:

```
06CEN05GSS  ──▶  11 variables (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, CMA, PR, KOL, TOTINC, ATTSCH, NOCS)
                       ↓  ATTSCH removed
11CEN10GSS  ──▶  10 variables (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, CMA, PR, KOL, TOTINC, NOCS)
                       ↓  NOCS removed
16CEN15GSS  ──▶   9 variables (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, CMA, PR, KOL, TOTINC)
                       ↓  TOTINC removed
21CEN22GSS  ──▶   8 variables (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, CMA, PR, KOL)
```

### 12.2 DTYPE Detail Erosion

```
Census 2006  ──▶  8 detailed dwelling types (1–8)
Census 2011  ──▶  8 detailed dwelling types (1–8)
Census 2016  ──▶  3 coarse types (1–3) → ML expansion restores 8 types
Census 2021  ──▶  3 coarse types (1–3) → used as-is (no expansion)
```

### 12.3 GSS Format Evolution

```
GSS 2005  ──▶  SAS7bdat (directly readable via pandas)
GSS 2010  ──▶  Fixed-width DAT + SPSS .SPS syntax (requires Step 0 parsing)
GSS 2015  ──▶  Fixed-width TXT + SPSS .SPS syntax (parsed in alignment step)
GSS 2022  ──▶  SAS7bdat (requires Step 0 for activity code normalization)
```

### 12.4 Income Bracket Compression

```
06CEN05GSS  ──▶  12 income brackets (≤$0, <$5K, ..., ≥$100K)
11CEN10GSS  ──▶  12 income brackets (same as 2005)
16CEN15GSS  ──▶   7 income brackets (≤$0, <$20K, ..., ≥$100K — wider bands)
21CEN22GSS  ──▶   Not available (TOTINC removed from PUMF)
```

---

## 13. Module Reference

**Table 12. Module Inventory Across All Cycles**

| Module | 06CEN | 11CEN | 16CEN | 21CEN | Purpose |
|--------|:-----:|:-----:|:-----:|:-----:|---------|
| `*_main.py` | ✓ | ✓ | ✓ | ✓ | Pipeline controller with interactive menu |
| `*_step0.py` | ✗ | ✓ | ✗ | ✓ | GSS episode preprocessing |
| `*_alignment.py` | ✓ | ✓ | ✓ | ✓ | Census–GSS demographic harmonization |
| `*_ProfileMatcher.py` | ✓ | ✓ | ✓ | ✓ | Tiered profile matching and schedule expansion |
| `*_DTYPE_expansion.py` | ✗ | ✗ | ✓ | ✗ | ML-based dwelling type refinement |
| `*_HH_aggregation.py` | ✓ | ✓ | ✓ | ✓ | 5-minute household grid construction |
| `*_occToBEM.py` | ✓ | ✓ | ✓ | ✓ | Hourly BEM schedule conversion |

All modules are located under their respective directories:
- `eSim_occ_utils/06CEN05GSS/`
- `eSim_occ_utils/11CEN10GSS/`
- `eSim_occ_utils/16CEN15GSS/`
- `eSim_occ_utils/21CEN22GSS/`

---

## 14. Shared Classes and Methods

### 14.1 MatchProfiler (All Cycles)

| Method | Purpose |
|--------|---------|
| `__init__(df_census, df_gss, ...)` | Initialize with Census/GSS DataFrames; split GSS into weekday/weekend catalogs |
| `run_matching()` | Iterate through Census agents, find best weekday and weekend GSS matches |
| `_find_best_match(agent, catalog)` | Apply tiered matching hierarchy; return (matched_id, tier_name) |
| `_print_match_stats(df_matched)` | Print tier distribution for weekday and weekend |

### 14.2 ScheduleExpander (All Cycles)

| Method | Purpose |
|--------|---------|
| `__init__(df_gss_raw, id_col)` | Index GSS raw data by occID for O(1) episode retrieval |
| `get_episodes(matched_id)` | Retrieve all episodes for a given GSS occupant ID |

### 14.3 HouseholdAggregator (All Cycles)

| Method | Purpose |
|--------|---------|
| `__init__(resolution_min=5)` | Initialize with 5-minute resolution (288 slots) |
| `process_all(df_expanded)` | Group by household and day type; process all groups |
| `_create_individual_grid(episodes)` | Convert episodes to 288-slot grid (presence, activity, density) |
| `_aggregate_household(people_grids)` | Aggregate individual grids to household level |

### 14.4 BEMConverter (All Cycles)

| Method | Purpose |
|--------|---------|
| `__init__(output_dir)` | Initialize with metabolic, DTYPE, and PR mapping tables |
| `process_households(df_full)` | Resample 5-min to 60-min; calculate occupancy fractions and metabolic rates |
| `_calculate_watts(act_str)` | Parse activity string and return average metabolic rate |

### 14.5 DTypeRefiner (16CEN15GSS Only)

| Method | Purpose |
|--------|---------|
| `__init__(output_dir)` | Initialize with feature lists |
| `train_models(df_historic)` | Train Random Forest classifiers (Model A: Apartments, Model B: Other) |
| `apply_refinement(df_forecast)` | Apply quota-calibrated predictions to coarse DTYPE |
| `_add_derived_features(df)` | Calculate ROOM_PER_PERSON, BEDRM_RATIO, INCOME_PER_PERSON |

---

## 15. Validation Framework

Each pipeline includes automated validation at every step:

**Table 13. Validation Checks by Step**

| Step | Check | Method | Pass Criteria |
|------|-------|--------|---------------|
| Alignment | Value alignment | `check_value_alignment()` | Census and GSS unique values match |
| Alignment | Distribution comparison | `plot_distribution_comparison()` | Visual plausibility |
| Profile Matching | Tier distribution | `validate_matching_quality()` | < 1% random fallback (Tier 5) |
| Profile Matching | Worker behavior | Work duration analysis | ~300–600 min/day for employed agents |
| Profile Matching | Episode counts | Episode statistics | 10–30 episodes per person per day |
| DTYPE Expansion | Distribution match | `validate_refinement_model()` | Refined matches historic proportions |
| HH Aggregation | Grid completeness | `validate_household_aggregation()` | All person-days have 288 slots |
| HH Aggregation | Logic consistency | Ghost row detection | No density in empty houses |
| HH Aggregation | Visual inspection | `visualize_multiple_households()` | Plausible occupancy patterns |
| BEM Conversion | Temporal sanity | Nighttime vs. daytime comparison | Nighttime occupancy > daytime |
| BEM Conversion | Range checks | Occupancy ∈ [0, 1], Metabolic ≥ 0 | All values within bounds |
| BEM Conversion | Distribution plots | `visualize_bem_distributions()` | Visual plausibility |

---

## 16. Quick Reference

### 16.1 Running a Pipeline

```bash
# Interactive mode (any cycle)
cd eSim_occ_utils/{CYCLE}/
python {CYCLE}_main.py

# Direct execution with sample percentage
python {CYCLE}_main.py --sample 25 --run 5    # Full pipeline at 25%
python {CYCLE}_main.py --sample 10 --run 1    # Alignment only at 10%
```

### 16.2 Time Resolution Summary

| Level | Resolution | Slots/Day | Stage |
|-------|:---------:|:---------:|-------|
| Raw GSS Episode | Variable | 10–50 typical | Input |
| Individual Grid | 5 minutes | 288 | HH Aggregation |
| Household Profile | 5 minutes | 288 | HH Aggregation output |
| BEM Schedule | 60 minutes | 24 | BEM Conversion output |

### 16.3 Day Type Codes (DDAY)

| Code | Day | Grouping |
|:---:|---|---|
| 1 | Sunday | Weekend |
| 2 | Monday | Weekday |
| 3 | Tuesday | Weekday |
| 4 | Wednesday | Weekday |
| 5 | Thursday | Weekday |
| 6 | Friday | Weekday |
| 7 | Saturday | Weekend |
