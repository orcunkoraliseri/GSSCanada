# Building Energy Model (BEM) Simulation Methodology

## 1. Introduction and Scope

This document describes the end-to-end methodology for integrating time-use survey (TUS)–derived occupancy data into EnergyPlus Building Energy Models (BEMs). The pipeline transforms aggregated household occupancy patterns from the Canadian General Social Survey (GSS) into hourly building simulation schedules, runs comparative simulations across multiple survey years (2005, 2015, 2025), and produces normalized Energy Use Intensity (EUI) breakdowns for analysis. The system supports both single-building and neighbourhood-scale simulations with a unified occupancy integration framework.

---

## 2. Software Architecture

### 2.1 Module Structure

The simulation framework is organized into a `eSim_bem_utils/` Python package with the following modules:

| Module | Responsibility |
|--------|---------------|
| `integration.py` | Schedule injection, occupancy-to-IDF conversion, household matching |
| `simulation.py` | EnergyPlus execution wrapper, parallel batch processing |
| `plotting.py` | EUI visualization, comparative bar charts, time-series profiles |
| `idf_optimizer.py` | IDF version management, output configuration, speed optimization, schedule standardization |
| `schedule_generator.py` | Lighting, Equipment, and DHW schedule generation from presence data |
| `main.py` | Menu-driven CLI entry point and workflow orchestration |

### 2.2 High-Level Pipeline

The simulation pipeline follows a sequential workflow:

```
┌───────────────────────────────────────────────────────┐
│  1. User selects simulation type via run_bem.py       │
│     (Single Building / Neighbourhood / Comparative)   │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  2. Load base IDF and TUS-derived schedule CSV        │
│     • Filter by dwelling type (e.g., SingleD)         │
│     • Sample or match households by profile           │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  3. IDF Optimization (idf_optimizer.py)               │
│     • Version alignment (→ EnergyPlus 24.2)           │
│     • Output variable injection                       │
│     • Speed optimizations                             │
│     • Default schedule standardization                │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  4. Occupancy Integration (integration.py)            │
│     • Inject presence, lighting, equipment,           │
│       DHW, and metabolic schedules                    │
│     • Apply Presence Filter method to each end-use    │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  5. Parallel EnergyPlus Execution                     │
│     • concurrent.futures-based batch runner            │
│     • ExpandObjects and platform-specific E+ paths    │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  6. Results Extraction and Visualization              │
│     • SQL/CSV result parsing                          │
│     • Conversion from kBtu to kWh                     │
│     • Normalization by net conditioned floor area     │
│     • Comparative EUI bar charts and time-series      │
└───────────────────────────────────────────────────────┘
```

---

## 3. IDF Preparation and Optimization

### 3.1 Automated IDF Corrections

Before any schedule injection or simulation, the `idf_optimizer.py` module applies a series of automated corrections to ensure compatibility with EnergyPlus 24.2 and consistent output reporting:

| Check | Action if Needed |
|-------|-----------------|
| EnergyPlus version ≠ 24.2 | Upgrades version identifier to 24.2 |
| `ZoneAveraged` in People MRT calculation | Changes to `EnclosureAveraged` (deprecated field fix) |
| Missing `Output:SQLite` | Adds `SimpleAndTabular` output mode |
| Missing energy output variables | Injects 7 end-use reporting variables |
| Missing surface property objects | Injects `OtherSideCoefficients` for slab-on-grade models |
| Timestep ≠ 4 | Sets simulation timestep to 4 per hour |
| Inefficient solar distribution | Sets to `FullExterior` |

The seven output variables added to every simulation ensure consistent end-use reporting:

1. Zone Lights Electricity Energy
2. Zone Electric Equipment Electricity Energy
3. Fan Electricity Energy
4. Zone Air System Sensible Heating Energy
5. Zone Air System Sensible Cooling Energy
6. Zone Ideal Loads Supply Air Total Heating Energy
7. Zone Ideal Loads Supply Air Total Cooling Energy

### 3.2 Speed Optimizations

To enable rapid iteration across many household scenarios, the optimizer applies the following performance settings:

| Setting | Optimized Value | Rationale |
|---------|----------------|-----------|
| Shadow Calculation Method | `PixelCounting` (512 px) | Faster than PolygonClipping |
| Shadow Update Frequency | Every 60 days | Reduces recalculation overhead |
| Max Shadow Figures | 5,000 | Down from 15,000 default |
| HVAC Max Iterations | 10 | Reduced from 20; ~10% faster |
| Inside Convection | `TARP` | Accurate for heating/cooling loads |
| Outside Convection | `DOE-2` | Balanced speed/accuracy |
| Timestep | 4 per hour | ~15% faster than 6 per hour |

Three run-period modes are available depending on the analysis stage:

| Mode | Days Simulated | Relative Speedup | Use Case |
|------|---------------|-------------------|----------|
| `standard` | 365 | 1.0× (baseline) | Final validation and published results |
| `weekly` | 168 (24 TMY weeks) | ~2.5× | Iterative development and testing |
| `design_day` | 2–4 | ~33× | HVAC sizing verification only |

Benchmark results using a Montreal TMY weather file confirm 54.8 s for a full-year simulation, 21.7 s for the weekly mode (2.52× faster, ~3.3% EUI difference), and 1.7 s for design-day mode.

---

## 4. Default Schedule Standardization

### 4.1 Problem Statement

Single-building and neighbourhood IDF sets originate from different sources and contain inconsistent default operational schedules. Without standardization, the Default scenario baseline varies between simulation types, undermining the comparability of occupancy-integrated results against the Default reference.

### 4.2 Selected Reference Schedules

Standard residential schedules are sourced from the **U.S. Department of Energy (DOE) Commercial Reference Buildings**, specifically the **MidRise Apartment** archetype. This archetype was selected as the closest available residential proxy because:

- Neither the EnergyPlus `Schedules.idf` library (ASHRAE 90.1-1989) nor the DOE reference building library provides schedules specifically for detached houses or single-family homes.
- MidRise Apartment schedules represent realistic dwelling-unit-level behavior patterns (occupancy, lighting, equipment, hot water use) that are applicable to individual residential units.

The schedule data is parsed from the **OpenStudio Standards Gem** maintained by the National Renewable Energy Laboratory (NREL), distributed through the **Ladybug Tools Schedule Library** (`schedule.json`).

### 4.3 Hourly Schedule Profiles

#### Occupancy (`ApartmentMidRise OCC_APT_SCH`)

| Hour | 0–6 | 7 | 8 | 9–15 | 16 | 17 | 18–20 | 21–23 |
|------|-----|---|---|------|----|----|-------|-------|
| Fraction | 1.0 | 0.85 | 0.39 | 0.25 | 0.30 | 0.52 | 0.87 | 1.0 |

Pattern: high night occupancy (sleeping), low daytime (work/school), gradual evening return.

#### Equipment (`ApartmentMidRise EQP_APT_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00–04:00 | 0.38–0.45 |
| 05:00–08:00 | 0.43–0.66 |
| 09:00–15:00 | 0.65–0.70 |
| 16:00–17:00 | 0.80–1.00 (peak) |
| 18:00–23:00 | 0.58–0.93 |

#### Lighting (`ApartmentMidRise LTG_APT_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00–04:00 | 0.01–0.03 |
| 05:00–08:00 | 0.03–0.08 |
| 09:00–15:00 | 0.02–0.04 |
| 16:00–19:00 | 0.08–0.18 (peak) |
| 20:00–23:00 | 0.03–0.12 |

#### Domestic Hot Water (`ApartmentMidRise APT_DHW_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00–04:00 | 0.01–0.08 |
| 05:00–08:00 | 0.27–1.00 (morning peak) |
| 09:00–16:00 | 0.41–0.76 |
| 17:00–20:00 | 0.73–0.86 (evening peak) |
| 21:00–23:00 | 0.29–0.61 |

#### Metabolic Activity Level

Constant **95 W** (seated, light activity) applied uniformly.

### 4.4 Standardization Data Flow

The standardization is implemented as a two-step process:

```
┌─────────────────────────────────────────────────────────────┐
│           ANY IDF (Single Building or Neighbourhood)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: idf_optimizer.py                                   │
│  → standardize_residential_schedules()                      │
│  • Replaces existing schedules with MidRise Apartment       │
│    profiles for People, Lights, Equipment, and WaterUse     │
│  • Ensures ALL IDFs start from the SAME baseline            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
   ┌──────────────────┐          ┌───────────────────────┐
   │ DEFAULT SCENARIO │          │ 2025 / 2015 / 2005    │
   │ (No modification)│          │ (Occupancy-integrated) │
   └──────────────────┘          └───────────────────────┘
              │                               │
              │                               ▼
              │          ┌─────────────────────────────────┐
              │          │ STEP 2: integration.py           │
              │          │ → inject_schedules() /           │
              │          │   inject_neighbourhood_schedules()│
              │          │ • Takes MidRise baseline          │
              │          │ • Applies occupancy formula:      │
              │          │   result = occ × MAX(midrise,     │
              │          │            floor) + (1-occ) ×     │
              │          │            baseload               │
              │          └─────────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
                   ┌──────────────────────┐
                   │  EnergyPlus          │
                   │  Simulation          │
                   └──────────────────────┘
```

For **neighbourhood simulations**, where the input IDF may lack occupancy schedules entirely, the optimizer includes a fallback mechanism: it searches for a Single Building IDF in `0_BEM_Setup/Buildings/*.idf`, parses the schedules for Lights, Equipment, and WaterUse, and uses them as the Default baseline. This ensures that neighbourhood Default-vs-Integrated comparisons rely on the same baseline physics as single-building comparisons.

---

## 5. Occupancy Integration: The Presence Filter Method

### 5.1 Overview

The core contribution of this pipeline is the integration of GSS-derived household occupancy profiles into EnergyPlus internal load schedules. The method, termed the **Presence Filter**, modulates the standardized default schedules using a binary presence mask derived from the time-use survey data. The approach applies uniformly to three end-use categories: **Lighting**, **Electrical Equipment** (Miscellaneous Electric Loads), and **Domestic Hot Water (DHW)**.

### 5.2 Occupancy Data Processing

Household-level occupancy schedules are derived from the Canadian General Social Survey (GSS) for three survey cycles:

- **GSS Cycle 19 (2005)**: Time-Use Survey, 10-minute diary episodes
- **GSS Cycle 29 (2015)**: Time-Use Survey, 10-minute diary episodes
- **GSS Cycle 39 (2025)**: Synthetic population generated by a Conditional Variational Autoencoder (CVAE) trained on the 2021 Census PUMF and GSS Cycle 33 (2022) data, then projected to 2025 via cluster-momentum extrapolation (`25CEN22GSS_classification` pipeline).

> **Building stock assumption (2025 forecast):** Building stock characteristics (dwelling type, bedroom count, room count, and condominium status) for the 2025 synthetic population are held at the 2021 distribution. Statistics Canada has not released a comprehensive housing inventory for 2022–2025, and any extrapolation would introduce more uncertainty than it removes. The 2025 results therefore reflect **demographic drift only**, not changes in the housing stock. See `eSim_occ_utils/25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py`, function `generate_future_population()`, for implementation details.

The raw diary data is aggregated to hourly resolution and converted into:

1. **Fractional occupancy profiles** (0.0–1.0): proportion of household members present at each hour.
2. **Binary presence masks** (0 or 1): indicating whether any household member is at home.
3. **Metabolic rate schedules**: activity-specific metabolic rates in Watts assigned to each occupant.

The schedule CSVs are filtered by dwelling type (e.g., `SingleD` for single detached houses) to ensure consistency with the base IDF geometry.

### 5.3 Occupancy Scaling

For each household, the simulation updates `PEOPLE.Number_of_People` based on the actual household size (`hhsize`) from the TUS data. Conflicting headcount calculation methods (e.g., per-area calculations) are cleared to ensure correct absolute scaling.

### 5.4 The Presence Filter Algorithm

The Presence Filter method was developed to address limitations of simpler integration approaches:

- **Binary switching** (1.0 when home, 0.0 when away) caused unrealistic spikes—particularly in water heating, where instantaneous full-load switching produced non-physical demand profiles.
- **Direct presence multiplication** (`default × presence_fraction`) produced overly conservative estimates that under-predicted actual loads.

The final method preserves the **natural shape** of default schedule profiles while modulating based on occupancy presence:

#### General Formula

```
IF household is active (presence = 1):
    Load = Default Schedule Value at that hour
ELSE (presence = 0):
    Load = Base Load
```

Where:
- **Default Schedule Value**: the hourly fractional value from the standardized MidRise Apartment schedule.
- **Base Load**: the minimum value from the default schedule during absent hours, representing always-on loads.

#### Baseload Calculation

Baseload values are **not predefined constants** but are **dynamically calculated** for each household from the standardized default schedules. The calculation algorithm:

1. **Identify absent hours**: Determine hours when `presence_schedule[hour] < 0.001` (household away).
2. **Extract default values**: Retrieve `default_schedule[hour]` for all absent hours.
3. **Calculate minimum**: `baseload = min(default_schedule values during absent hours)`.

**Fallback logic**: If no absent hours exist (household always home), the algorithm uses typical work hours (9 AM–5 PM) to calculate the baseload.

This approach ensures that baseload values:
- Represent realistic standby loads from validated DOE reference building data
- Vary by household based on actual absence patterns
- Avoid arbitrary constants

**Example**: For a household absent 8 AM–5 PM, if the equipment default schedule during those hours is [0.66, 0.70, 0.70, 0.69, 0.66, 0.65, 0.65, 0.69, 0.80], then `baseload = 0.65` (representing refrigerators, standby power, etc.).

For the full integration formula used during schedule injection:

```
if occupancy > 0:
    result = occupancy × default_schedule + (1 − occupancy) × baseload
else:
    result = baseload
```

When occupants are present, the load blends proportionally between the full DOE default value and the baseload. A household with fractional occupancy (e.g., one of five members home, occupancy = 0.20) produces 20% of the peak default load rather than the full default value. This preserves the design intent that the TUS injection only modifies hours in which occupants are recorded as active. When no occupant is present, only the baseload operates.

### 5.5 End-Use-Specific Implementation

#### 5.5.1 Lighting

Lighting schedules are generated using the **Daylight Threshold Method**, which differs from the binary Presence Filter applied to Equipment and DHW.

For each of the 12 calendar months, the `LightingGenerator` reads the monthly mean global horizontal irradiance from the EnergyPlus Weather Statistics (`.stat`) file co-located with the simulation weather data. A **150 Wh/m² threshold** separates high-daylight months from low-daylight months. In high-daylight months, the base lighting demand is suppressed by a **daylight scaling factor** (minimum floor 0.30) reflecting the contribution of natural light; in low-daylight months, the full presence-modulated profile is used. This produces 12 monthly `Schedule:Compact` blocks (`Through: 1/31`, `Through: 2/28`, …) that capture Canada's strong seasonal daylight asymmetry without requiring a coupled daylighting simulation.

The occupied-hour load is computed using the same blending formula as Equipment and DHW:

```
if occupancy > 0:
    result = occupancy × (daylight_scaled_default) + (1 − occupancy) × baseload
else:
    result = baseload
```

**Implementation**: `LightingGenerator.generate_monthly()` in `eSim_bem_utils/schedule_generator.py`; called from `inject_schedules()` and `inject_neighbourhood_schedules()` in `integration.py`.

#### 5.5.2 Electrical Equipment (MELs)

Equipment loads distinguish between **base loads** (refrigerators, standby power—always running) and **active loads** (televisions, cooking appliances—requiring occupant presence). The Presence Filter preserves realistic usage patterns (e.g., lower equipment use at 6 AM vs. 6 PM) rather than applying binary min/max toggling.

The baseload for equipment is dynamically calculated as the minimum value from the default equipment schedule during hours when the household is absent. This represents the continuous draw from appliances that operate regardless of occupancy (refrigerators, cable boxes, HVAC controls, etc.).

**Implementation**: `PresenceFilter` class in `eSim_bem_utils/schedule_generator.py`.

#### 5.5.3 Domestic Hot Water (DHW)

Major hot water draws (showers, sinks) are constrained to coincide with occupant presence, preventing high-usage events during vacancy. The baseload during absence represents small recirculation losses or leak loads, calculated as the minimum value from the default DHW schedule during absent hours. This approach preserves the characteristic morning and evening shower peaks when occupants are present.

**Implementation**: `PresenceFilter` class in `eSim_bem_utils/schedule_generator.py`, applied through `inject_schedules()` in `eSim_bem_utils/integration.py`.

### 5.6 Schedule Parsing

The integration module implements a hierarchy-aware IDF schedule parser capable of extracting 24-hour profiles from multiple EnergyPlus schedule formats:

- **`Schedule:Year` → `Schedule:Week` → `Schedule:Day:Hourly`**: The full DOE schedule hierarchy.
- **`Schedule:Compact`**: Handles complex inline `Until: HH:MM, Value` patterns common in auto-generated IDFs.

This parser is critical for extracting the original default profiles that form the basis for occupancy modulation.

---

## 6. Comparative Simulation Framework

### 6.1 Simulation Options

The pipeline provides a menu-driven interface with the following simulation modes:

| Option | Mode | Description |
|--------|------|-------------|
| 1 | Visualization | 3D interactive model viewer for IDF geometry inspection |
| 2 | Single Simulation | Run a single household against the base IDF |
| 3 | Comparative (Single Building) | Multi-scenario analysis: 2025, 2015, 2005, and Default—run in parallel |
| 4 | Comparative Variant | Extended comparative options |
| 5 | Results Visualization | Review and compare existing simulation results |
| 6 | Neighbourhood Batch | Batch comparative simulation across all buildings in a neighbourhood IDF |
| 7 | Neighbourhood Variant | Extended neighbourhood comparative options |

### 6.2 Household Matching for Comparatives

To ensure valid cross-year comparisons, the pipeline constrains household selection so that compared households exhibit similar gross occupancy patterns. Since the Default baseline assumes a **standard working day** (absent 8 AM–4 PM), households from TUS datasets are matched against a `TARGET_WORKING_PROFILE`:

- **Home**: 00:00–08:00
- **Away**: 08:00–16:00
- **Home**: 16:00–24:00

The matching algorithm:

1. Randomly samples a subset of 50–100 candidate households (filtered by household size and dwelling type).
2. Computes the **Sum of Squared Errors (SSE)** between each candidate's hourly presence profile and the target working profile.
3. Selects the candidate with the lowest SSE (closest match to the working-day pattern).

This ensures that comparative plots isolate the impact of *technological* and *behavioral* differences (e.g., lighting efficiency, appliance base loads, activity patterns) across survey years, rather than reflecting gross occupancy category differences (e.g., retiree vs. full-time worker schedules).

### 6.3 Selection-Bias Sensitivity for TARGET_WORKING_PROFILE (Task 22)

The longitudinal comparison requires a fixed household-selection criterion to ensure that cross-year EUI differences reflect genuine demand shifts rather than accidental demographic composition differences between cohorts. The current criterion — minimum SSE to a standard 9-to-5 working-day profile (`TARGET_WORKING_PROFILE`) — systematically favours employed, daytime-absent households. This raises a potential cherry-picking objection.

**Quantifying the bias.** The pipeline provides `export_sse_distances_csv()` in `integration.py`, which writes one row per household containing: `HH_ID`, `SSE_to_target`, `included` (0/1), `hhsize`, and `match_tier`. Running this after each comparative selection produces an audit CSV that allows the researcher to:

- Plot the SSE distribution of included vs excluded households.
- Compare the demographic composition of the included cohort (hhsize, match-tier) to the full GSS pool.
- Report the fraction of full-time workers, retired, and student households in the matched sub-sample vs the source population.

**Robustness check.** An alternative sensitivity run can substitute `TARGET_WORKING_PROFILE` with one of the four `ARCHETYPE_PROFILES` defined in `integration.py` (Worker / Student / Retiree / ShiftWorker). If the headline 5-year EUI trend (direction and magnitude) is stable across at least two profile targets, the comparison is demonstrably robust to the target choice. If results diverge substantially, the paper should report both as a sensitivity range.

**Recommended paper statement:** *"Household selection is constrained to minimize the SSE between the household's weekday presence profile and a standard 9-to-5 target profile. The matched sub-cohort was verified to contain [X]% full-time-employed households vs [Y]% in the full GSS pool, a bias of [ΔZ]%. A sensitivity run substituting a retiree target profile produced a headline EUI trend within ±[N]%, confirming the longitudinal result is robust to the choice of selection target."*

### 6.4 Parallel Execution

Simulations are executed concurrently using Python's `concurrent.futures` module. Each household scenario (Default, 2025, 2015, 2005) is prepared as an independent IDF and run in parallel, with automatic result extraction upon completion. The `simulation.py` module handles platform-specific EnergyPlus paths and ExpandObjects pre-processing.

---

## 7. Results Processing and Visualization

### 7.1 Output Extraction

Simulation results are extracted from EnergyPlus SQL output databases (`eplusout.sql`). Raw energy values reported in kBtu are converted to kWh and normalized by the **Net Conditioned Floor Area** (m²) to produce EUI values in kWh/m².

### 7.2 Visualization Outputs

The plotting module produces two primary visualization types:

1. **Comparative Bar Charts**: Disaggregated end-use energy demand across all scenarios (Default, 2025, 2015, 2005), enabling direct comparison of lighting, equipment, heating, cooling, fans, and DHW intensities.

2. **Annual Time-Series Profiles**: Monthly demand line plots for all scenarios normalized to kWh/m², showing seasonal variation and the effect of occupancy integration on each end-use category.

For batch (neighbourhood) simulations, the module dynamically selects between histograms (for grouped building results) and disaggregated bar charts (for individual households), ensuring clear and accurate labeling.

### 7.3 Verification Results

The pipeline has been verified against multiple households (e.g., Household 2402, 4270) with the following outcomes:

- **Lighting and Equipment**: Occupancy-integrated scenarios show reduced consumption compared to Default, with reductions proportional to absence hours while maintaining original profile shapes.
- **Domestic Hot Water**: Successfully resolved an earlier "100× spike" issue caused by binary switching. Final values show realistic variation (~10–50 kWh/m²) through the presence-mask multiplication approach.
- **Cross-Scenario Consistency**: Parallel execution confirmed for all four scenarios with consistent result extraction.

### 7.4 External Benchmark Validation: NRCan SHEU-2017 (Task 7)

To anchor the framework to measured residential energy consumption, simulated per-end-use EUI for the **Default scenario** (DOE MidRise baseline, no occupancy modification) is compared against the **NRCan Survey of Household Energy Use 2017 (SHEU-2017)** reference values for single-detached dwellings.

**SHEU-2017 Single-Detached Residential EUI Reference — Quebec and Ontario**

| End-Use | SHEU-2017 Quebec (kWh/m²) | SHEU-2017 Ontario (kWh/m²) | Framework Default | % Difference (QC) | % Difference (ON) |
|---|---|---|---|---|---|
| Space Heating | ~87 | ~76 | _run Option 3_ | — | — |
| Space Cooling | ~3 | ~8 | _run Option 3_ | — | — |
| Domestic Hot Water | ~27 | ~22 | _run Option 3_ | — | — |
| Lighting | ~8 | ~7 | _run Option 3_ | — | — |
| Appliances / Plug Loads | ~18 | ~17 | _run Option 3_ | — | — |
| **Total** | **~143** | **~130** | _run Option 3_ | — | — |

> **Note:** SHEU-2017 values are reported per dwelling; normalization to kWh/m² uses SHEU-reported mean floor areas of 164 m² (Quebec) and 171 m² (Ontario) for single-detached dwellings. Source: Natural Resources Canada, *Survey of Household Energy Use 2017 — Detailed Statistical Report*, Table 9 and Table 12.

**Validation protocol:**
1. Run Option 3 (Default scenario) with the Montreal EPW for a representative 2-person, single-detached household.
2. Extract per-end-use EUI from `eplusout.sql` using the existing `plotting.calculate_eui()` function.
3. Fill in the "Framework Default" column above and compute % difference per end-use.
4. If any end-use deviates by more than ±20 %, recalibrate the corresponding baseline parameter (lighting density W/m², equipment density W/m², or infiltration ACH) in `schedule.json` or the IDF template, and re-run until within tolerance.
5. Repeat with the Toronto EPW to validate the Ontario column.

**Acceptance criterion:** All per-end-use EUI values within ±20 % of SHEU-2017 averages, or a documented justification for systematic gaps (e.g., MidRise geometry vs. single-detached insulation levels).

---

## 8. References

1. U.S. Department of Energy. *Commercial Reference Buildings*. 16 common building types. Developed to comply with ASHRAE Standard 90.1 (2004, 2010, 2013, 2016, 2019). https://www.energy.gov/eere/buildings/commercial-reference-buildings

2. National Renewable Energy Laboratory. *OpenStudio Standards Gem*. https://github.com/NREL/openstudio-standards

3. Ladybug Tools. *Honeybee Energy Standards — Schedule Library*. https://github.com/ladybug-tools/honeybee-energy-standards

4. DOE Building Energy Codes Program. *Prototype Building Models — IECC Residential*. https://www.energycodes.gov/prototype-building-models#Residential
