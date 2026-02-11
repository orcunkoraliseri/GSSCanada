# Occupancy Data Processing: 06CEN05GSS and 16CEN15GSS Pipelines

## 1. Introduction

This chapter describes the data processing pipelines for the two real-world occupancy datasets used in this study: **06CEN05GSS** (Census 2006 + General Social Survey 2005) and **16CEN15GSS** (Census 2016 + General Social Survey 2015).

> [!IMPORTANT]
> Unlike the synthetic 25CEN22GSS dataset, the 06CEN05GSS and 16CEN15GSS datasets are derived entirely from **existing Statistics Canada microdata**. No synthetic classification or agent generation is applied—all individuals and their time-use diaries are real survey respondents. The processing pipeline focuses exclusively on harmonizing, linking, and converting these real observations into building energy model (BEM) inputs.

The two pipelines share a common methodological core but differ in the number of processing steps. Table 1 provides an overview.

**Table 1. Pipeline Comparison**

| Feature | 06CEN05GSS | 16CEN15GSS |
|---------|-----------|-----------|
| Census Year | 2006 | 2016 |
| GSS Year | 2005 (Cycle 19 – Time Use) | 2015 (Cycle 29 – Time Use) |
| Pipeline Steps | 4 | 5 |
| Harmonized Variables | 11 | 9 |
| Default Sample | 5% | 10% |
| DTYPE Detail | Already detailed (1–8) | Requires expansion (1–3 → 1–8) |
| Unique Step | — | DTYPE Expansion (ML-based) |

---

## 2. Shared Pipeline Steps

Both pipelines share four core steps. While details of variable mappings differ between survey cycles, the methodological approach is identical.

### 2.1 Step 1: Census–GSS Alignment (Harmonization)

**Purpose**: Harmonize the coding schemes between Census and GSS microdata so that demographic variables can be compared and used for profile matching.

**Motivation**: The Census and GSS use different variable coding systems for the same demographic concepts. For example, Census may encode age in 5-year groups (codes 1–13) while GSS uses 10-year groups (codes 1–7). Alignment creates a common schema by mapping one coding system to the other.

**Process**:

1. **Load Census Data**: Read the filtered Census Public Use Microdata File (PUMF). Reconstruct household structures using sequential household IDs.
2. **Load GSS Data**: Read the GSS time-use episode file and merge with GSS demographic data (main file). For GSS 2015, this involves parsing fixed-width text files using SPSS `.sps` column specifications.
3. **Apply Harmonization Functions**: For each demographic variable, a dedicated function maps value codes to a common scheme. The mapping direction depends on which dataset has the simpler coding (generally mapping the more detailed dataset to the simpler one).
4. **Clean Invalid Codes**: Remove records with ambiguous responses (e.g., "Don't Know" = 8, "Not Stated" = 9 in GSS).
5. **Validate Alignment**: Compare unique value sets between harmonized Census and GSS to confirm alignment. Generate side-by-side distribution comparison plots.
6. **Save**: Export aligned Census and GSS DataFrames to CSV.

**Harmonized Variables**:

**Table 2. Demographic Variables Harmonized by Each Pipeline**

| Variable | Description | 06CEN05GSS | 16CEN15GSS | Mapping Notes |
|----------|-------------|:----------:|:----------:|---------------|
| AGEGRP | Age Group | ✓ | ✓ | Census 5-year → GSS 10-year groups |
| SEX | Sex | ✓ | ✓ | Direct match (1=Male, 2=Female) |
| MARSTH | Marital Status | ✓ | ✓ | GSS detailed → Census simplified |
| HHSIZE | Household Size | ✓ | ✓ | Census 7+ capped at 6 |
| LFTAG | Labour Force Activity | ✓ | ✓ | Census 14-category → GSS 5-category |
| CMA | Census Metropolitan Area | ✓ | ✓ | Census named CMAs → GSS urban/rural |
| PR | Province/Region | ✓ | ✓ | Census region codes → GSS province codes |
| KOL | Knowledge of Official Languages | ✓ | ✓ | Drop "Neither"/"DK"/"NS" |
| TOTINC | Total Income | ✓ | ✓ | Census continuous $ → GSS categorical brackets |
| ATTSCH | School Attendance | ✓ | ✗ | GSS Full/Part-time → Census Attending/Not |
| NOCS | Occupation Classification | ✓ | ✗ | GSS DK/NS codes → 99 |

> [!NOTE]
> The 16CEN15GSS pipeline harmonizes 9 variables (omitting ATTSCH and NOCS), reflecting differences in variable availability between GSS 2005 and GSS 2015 PUMF releases.

**Implementation**: `06CEN05GSS_alignment.py` / `16CEN15GSS_alignment.py`

---

### 2.2 Step 2: Profile Matching

**Purpose**: Assign real GSS time-use schedules to Census agents based on demographic similarity.

**Motivation**: The Census provides detailed demographic data for all Canadians but contains no time-use information. The GSS contains detailed 24-hour time-use diaries but covers only a sample of the population (~20,000 respondents). Profile matching bridges this gap by assigning each Census agent the time-use diary of a demographically similar GSS respondent.

**Process**:

The `MatchProfiler` class implements a **tiered matching** strategy:

1. **Tier 1 — Perfect Match**: Match on all harmonized columns simultaneously. If an exact demographic twin exists in the GSS, use their schedule.
2. **Tier 2 — Relaxed Match**: If no perfect match is found, progressively drop the least discriminating variables (e.g., NOCS, KOL) and retry matching with the remaining subset.
3. **Tier 3 — Minimal Match**: Match on core variables only (e.g., AGEGRP, SEX, LFTAG).

For each Census agent, matching is performed separately for **Weekday** and **Weekend** day types, using the GSS `DDAY` variable to distinguish diary day types.

After matching, the `ScheduleExpander` class retrieves the full variable-length episode lists for each matched GSS respondent. These episodes contain:

- Start time and end time (in minutes from midnight)
- Activity code
- Location code (home/away)
- Duration

The expanded schedules are saved as a comprehensive CSV linking Census agent demographics with their assigned GSS time-use episodes.

**Sampling**: A configurable sample percentage (default: 5% for 06CEN05GSS, 10% for 16CEN15GSS) controls the number of Census agents processed. This enables rapid prototyping and testing before full-scale runs.

**Validation**: The `validate_matching_quality()` function analyzes:
- Distribution of matches across tiers (% perfect, relaxed, minimal)
- Behavioral consistency of assigned schedules
- Sample verification of individual agent-schedule pairs

**Implementation**: `06CEN05GSS_ProfileMatcher.py` / `16CEN15GSS_ProfileMatcher.py`

---

### 2.3 Step 3 (06CEN) / Step 4 (16CEN): Household Aggregation

**Purpose**: Transform individual-level, variable-length episode lists into standardized household-level occupancy profiles at 5-minute resolution.

**Motivation**: GSS time-use diaries are recorded at the individual level with variable-length episodes (e.g., "slept from 00:00 to 07:30, commuted from 07:30 to 08:15..."). Building energy simulation requires household-level schedules at regular time intervals. This step bridges that gap.

**Process**:

The `HouseholdAggregator` class performs four sub-steps:

**A. Grid Construction (Individual)**: Convert each person's variable-length episode list into a fixed 288-slot array (24 hours × 12 slots/hour = 5-minute resolution). Each slot is assigned:
- Activity code (mapped from GSS activity classification)
- Location flag (home = 1, away = 0)
- Metabolic state

**B. Household Assembly**: Group all individuals belonging to the same household (via `HHID`) and day type (Weekday/Weekend).

**C. Occupancy Aggregation**: For each 5-minute time slot, calculate:
- **Fractional Occupancy**: Number of household members at home ÷ total household members (value 0.0–1.0)
- **Dominant Activity**: Most common activity code among present members
- **Metabolic Aggregate**: Sum of metabolic rates for present members

**D. Demographic Merge**: Preserve all static Census demographic columns (DTYPE, BEDRM, ROOM, TOTINC, etc.) alongside the aggregated temporal profiles.

**Resolution**: 288 time slots per day (5-minute intervals).

**Validation**: The `validate_household_aggregation()` function verifies:
- Occupancy fractions are within [0, 1]
- All households have 288 time slots
- No missing values in critical columns
- Household size consistency

**Visualization**: The `visualize_multiple_households()` function generates grid plots for random household samples, showing temporal occupancy patterns and activity distributions.

**Implementation**: `06CEN05GSS_HH_aggregation.py` / `16CEN15GSS_HH_aggregation.py`

---

### 2.4 Step 4 (06CEN) / Step 5 (16CEN): BEM Conversion

**Purpose**: Convert 5-minute household occupancy profiles into hourly BEM schedules compatible with EnergyPlus.

**Motivation**: EnergyPlus building energy models require hourly schedule inputs for occupancy, metabolic heat gains, and residential characteristics. This step downsamples and reformats the 5-minute profiles.

**Process**:

The `BEMConverter` class performs:

1. **Temporal Downsampling**: Aggregate 5-minute slots into hourly values (12 slots → 1 hour):
   - Fractional occupancy: hourly average of the 12 constituent slots
   - Activity/metabolic: mode or weighted average

2. **Metabolic Rate Calculation**: Map GSS activity codes to metabolic rates in Watts using a standardized activity-to-Watts lookup table. The `_calculate_watts()` method parses activity code strings and returns the average metabolic rate for multi-activity periods.

3. **Output Schema**: Generate a structured DataFrame with:
   - `HHID`, `DayType` (Weekday/Weekend)
   - `Hour_00` through `Hour_23` — fractional occupancy per hour
   - `Watts_00` through `Watts_23` — metabolic rate per hour (W)
   - Residential variables: `DTYPE`, `BEDRM`, `ROOM`, `TOTINC`, `HHSIZE`, etc.

4. **Save**: Export to CSV and generate summary statistics.

**Validation**: The `visualize_bem_distributions()` function generates two plot files:
1. **Temporal Plots**: Occupancy and metabolic rate distributions across hours, with sample household profiles
2. **Non-Temporal Plots**: Distribution of residential variables (dwelling type, bedrooms, rooms, income)

**Implementation**: `06CEN05GSS_occToBEM.py` / `16CEN15GSS_occToBEM.py`

---

## 3. Unique Step: DTYPE Expansion (16CEN15GSS Only)

### 3.1 Step 3: DTYPE Expansion and Refinement

**Purpose**: Refine the coarse dwelling type classification (DTYPE 1–3) available in Census 2016 into the detailed 8-category classification (DTYPE 1–8) used in Census 2006 and required for BEM configuration.

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

4. **Quota-Calibrated Prediction**: Rather than using raw model predictions (which may not match known national distributions), a **quota sampling** algorithm is applied:
   - Calculate prediction probabilities for each household
   - Enforce target distribution ratios based on historic Census proportions:
     - **Apartments**: 34% high-rise, 66% low-rise
     - **Other**: 33% row, 29% semi-detached, 29% duplex, 7% mobile, 2% other
   - Assign categories by selecting the top-ranked candidates for each quota target

5. **Validation**: Compare the refined DTYPE distribution against historic Census distributions using the `validate_refinement_model()` function.

**Training Data**: Census 2006 (`cen06_filtered2.csv`) and Census 2011 (`cen11_filtered2.csv`) — both contain the detailed 8-category DTYPE classification.

**Training Features**: BEDRM, ROOM, PR, HHSIZE, CONDO, REPAIR, TOTINC, CFSIZE, ROOM_PER_PERSON, BEDRM_RATIO, INCOME_PER_PERSON

**Implementation**: `16CEN15GSS_DTYPE_expansion.py`

---

## 4. Pipeline Summary and Data Flow

### 4.1 06CEN05GSS Data Flow (4 Steps)

```
Census 2006 PUMF ──┐
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
GSS 2005 Episodes ─┘                                       │
                                                            ▼
                          [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                            │
                                                            ▼
                          [Step 3: HH Aggregation] ──▶ Household 5-min Profiles (288 slots)
                                                            │
                                                            ▼
                          [Step 4: BEM Conversion] ──▶ Hourly BEM Schedules (24 hours)
```

### 4.2 16CEN15GSS Data Flow (5 Steps)

```
Census 2016 PUMF ──┐
                    ├──▶ [Step 1: Alignment] ──▶ Aligned Census & GSS DataFrames
GSS 2015 Episodes ─┘                                       │
                                                            ▼
                          [Step 2: Profile Matching] ──▶ Matched Keys + Expanded Schedules
                                                            │
                                                            ▼
Census 2006 PUMF ──┐
Census 2011 PUMF ──┤──▶ [Step 3: DTYPE Expansion] ──▶ Refined Schedules (DTYPE 1-8)
                   │                                        │
                   │    (ML training data)                   ▼
                                        [Step 4: HH Aggregation] ──▶ Household 5-min Profiles
                                                            │
                                                            ▼
                                        [Step 5: BEM Conversion] ──▶ Hourly BEM Schedules
```

### 4.3 Output Directory Structure

```
Occupancy/
├── Outputs_06CEN05GSS/
│   ├── Alignment/              # Step 1 outputs
│   ├── ProfileMatching/        # Step 2 outputs (Keys + Full Schedules)
│   ├── HH_aggregation/         # Step 3 outputs (5-min grids + validation)
│   └── occToBEM/               # Step 4 outputs (hourly BEM schedules + plots)
│
├── Outputs_16CEN15GSS/
│   ├── Alignment/              # Step 1 outputs
│   ├── ProfileMatching/        # Step 2 outputs
│   ├── DTYPE_expansion/        # Step 3 outputs (refined schedules + validation)
│   │   └── Validation/         # DTYPE distribution comparison reports
│   ├── HH_aggregation/         # Step 4 outputs
│   └── occToBEM/               # Step 5 outputs
```

---

## 5. Key Differences from 25CEN22GSS

| Aspect | 06CEN05GSS / 16CEN15GSS | 25CEN22GSS |
|--------|--------------------------|------------|
| **Data Origin** | Real Statistics Canada microdata (Census PUMF + GSS Time Use) | Synthetic dataset generated from models |
| **Classification** | No classification applied — categories come directly from survey data | Requires synthetic classification and agent generation |
| **Occupancy Diaries** | Real 24-hour time-use diaries from GSS respondents | Synthetically generated occupancy schedules |
| **Pipeline Complexity** | 4–5 steps (harmonize → match → aggregate → convert) | Additional steps for synthetic data generation |
| **DTYPE Source** | Census PUMF (06CEN: detailed; 16CEN: coarse + ML expansion) | Synthetically assigned |

> [!NOTE]
> All three datasets ultimately produce the same output format: **hourly BEM schedules** with fractional occupancy, metabolic rates, and residential variables. The shared downstream steps (Household Aggregation and BEM Conversion) use identical logic regardless of data origin, ensuring consistency across all three temporal scenarios in the simulation framework.

---

## 6. Module Reference

**Table 3. Module Inventory**

| Module | 06CEN05GSS | 16CEN15GSS | Purpose |
|--------|:----------:|:----------:|---------|
| `*_main.py` | ✓ | ✓ | Pipeline controller with interactive menu |
| `*_alignment.py` | ✓ | ✓ | Census–GSS demographic harmonization |
| `*_ProfileMatcher.py` | ✓ | ✓ | Tiered profile matching and schedule expansion |
| `*_DTYPE_expansion.py` | ✗ | ✓ | ML-based dwelling type refinement |
| `*_HH_aggregation.py` | ✓ | ✓ | 5-minute household grid construction |
| `*_occToBEM.py` | ✓ | ✓ | Hourly BEM schedule conversion |

All modules are located under `occ_utils/06CEN05GSS/` and `occ_utils/16CEN15GSS/` respectively.
