# Implementation Plan of Lighting & Equipment & DHW

## 1. Pre-requisite: Default Schedule Standardization
Before implementing the occupancy-based logic for Lighting, Equipment, and DHW, we first establish a standardized baseline for all schedules (ie., presence, lighting, equipment, dhw).
*   **Source**: We replace existing schedules in the `.idf` with standardized "ApartmentMidrise" versions (/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup/Templates/schedule.json).
*   **Reference**: See [Default Schedule Standardization.md](Default%20Schedule%20Standardization.md) for the detailed mapping and implementation of these base schedules.
*   **Input for Integration**: The "Default Schedule" referred to in the sections below is this standardized ApartmentMidrise schedule.

---

## 2. Lighting: Daylight-Responsive Lighting (Seasonal)

### 2.1 Objective
To simulate realistic seasonal lighting variations by combining **occupancy presence** with **local solar radiation data**. Lighting demand is reduced during daylight hours when sufficient natural light is available, while maintaining the occupancy-driven base load behavior.

### 2.2 Data Sources & Input
The primary environmental data is derived from the EnergyPlus Weather Statistics (`.stat`) file corresponding to the simulation region.

*   **Global Horizontal Solar Radiation**: Extracted from the "Average Hourly Statistics for Global Horizontal Solar Radiation [Wh/m²]" table in the `.stat` file.
*   **Files**:
    *   `CAN_ON_Toronto...TMYx.stat`
    *   `CAN_QC_Montreal...TMYx.stat`

### 2.3 Methodology: Presence + Daylight Scaling
This method modulates the standardized lighting schedule based on two factors:
1.  **Presence**: Is the household active?
2.  **Daylight Availability**: Is there sufficient natural light?

#### The Logic Rule:
1.  **Base Schedule**: Generated using the *Presence Filter Method* (same as Equipment):
    *   *Active*: Use Default Schedule Value.
    *   *Absent*: Use Base Load (minimum).
2.  **Daylight Factor**: Calculated hourly for each month based on solar radiation.
    *   *Threshold*: **150 Wh/m²** (Global Horizontal).
    *   If Solar > 150: Reduce lighting factor linearly (down to a minimum of 0.3).
    *   If Solar ≤ 150: Factor = 1.0 (Full artificial light).
3.  **Final Schedule**: `Base Schedule * Daylight Factor`

#### Implementation:
*   **Monthly Variation**: The system generates **12 distinct daily profiles** (one for each month) to capture seasonal changes in sunrise/sunset times and solar intensity.
*   **IDF Structure**: Schedules are injected as `Schedule:Compact` objects with 12 monthly `Through:` blocks (e.g., `Through: 1/31`, `Through: 2/28`, etc.), allowing EnergyPlus to simulate seasonal lighting variances accurately.

#### Outcome:
*   **Winter (Dec/Jan)**: Higher lighting demand due to short days and low solar angle.
*   **Summer (Jun/Jul)**: Lower lighting demand due to extended daylight hours and higher solar intensity.

---

## 3. Equipment (MELs): "The Presence Filter Method"

### 3.1 Objective
To adjust standard/default equipment schedules (e.g., NECB or ASHRAE profiles) so they reflect actual household occupancy. This distinguishes between **Base Loads** (fridges, standby power) which run constantly, and **Active Loads** (TVs, cooking) which require an occupant. The method preserves the natural shape of usage patterns.

### 3.2 Methodology: Presence Filter with Gradual Changes
This method filters the default schedule using the generated Presence Schedule while preserving realistic usage patterns.

#### Definitions:
*   **Default Schedule Value**: The hourly value from the standardized ApartmentMidrise equipment schedule (varies by hour, e.g., higher in morning/evening).
*   **Base Load**: The minimum value from the default schedule during absent hours (representing standby power, fridges, etc.).

#### The Logic Rule:
```
IF (Household is Active/Home)
THEN Equipment Load = Default Schedule Value at that hour (preserves gradual changes)
ELSE Equipment Load = Base Load (minimum from absent hours)
```

#### Rationale:
Unlike binary Min/Max toggling, this approach:
- Preserves realistic usage patterns (e.g., lower equipment use at 6 AM vs. 6 PM)
- Maintains the "shape" of the default profile
- Only applies base load floor during confirmed absence

---

## 4. Domestic Hot Water (DHW): "The Presence Filter Method"

### 4.1 Objective
To ensure that major hot water draws (showers, sinks) generally coincide with occupant presence, preventing high-usage events when the house is empty. The method preserves the natural shape of DHW demand patterns.

### 4.2 Methodology: Presence Filter with Gradual Changes
Similar to the Equipment logic, this method uses the Presence Schedule to modulate DHW demand while preserving realistic usage patterns.

#### Definitions:
*   **Default Schedule Value**: The hourly value from the standardized ApartmentMidrise DHW schedule (varies by hour, e.g., peaks during morning showers).
*   **Base Load (Leak/Recirc)**: The minimum value from the default schedule during absent hours (typically 0 or a small recirculation loss).

#### The Logic Rule:
```
IF (Household is Active/Home)
THEN DHW Load = Default Schedule Value at that hour (preserves gradual changes)
ELSE DHW Load = Base Load (minimum from absent hours)
```

#### Rationale:
Unlike binary Min/Max toggling, this approach:
- Preserves morning/evening shower peaks when present
- Maintains realistic demand curves
- Only applies base load floor during confirmed absence

---

## 5. Implementation Reference

*   **Module**: `bem_utils/schedule_generator.py`
    *   `LightingGenerator`: Implements Lighting Presence Filter
    *   `PresenceFilter`: Implements Equipment/DHW Presence Filter
    *   `StatFileParser`: Parses `.stat` files for solar radiation data
*   **Integration**: `bem_utils/integration.py`
    *   `inject_schedules()`: Applies filters for single-building simulations
    *   `inject_neighbourhood_schedules()`: Applies filters for neighbourhood simulations
    *   `find_best_match_household()`: Selects households matching Standard Working Day for comparatives
    *   `TARGET_WORKING_PROFILE`: The standard profile used for matching

---

## 6. Comparative Simulation Methodology

To ensure valid comparisons between datasets (2005/2015/2025) and the Default baseline, we constrain the household selection process for comparative simulations (Options 3, 4, 6, 7).

### 6.1 Objective
Compare energy performance of "like-for-like" occupants. Since the "Default" baseline assumes a standard working day (Absent 8am-5pm), we must select households from the TUS datasets that exhibit similar behavior.

### 6.2 Selection Logic
1.  **Candidate Pool**: Randomly sample a subset of households (e.g., 50-100) from the dataset (matching Household Size).
2.  **Best Match**: Calculate the Sum of Squared Errors (SSE) between each candidate's presence profile and the **TARGET_WORKING_PROFILE**.
3.  **Selection**: Choose the candidate with the lowest SSE (closest match).

**TARGET_WORKING_PROFILE** (Standard Working Day):
-   Home: 00:00 - 08:00
-   Away: 08:00 - 16:00
-   Home: 16:00 - 24:00

This ensures that comparative plots visualize the impact of *technological* and *behavioral* differences (e.g., lighting efficiency, base loads, activity levels) rather than gross occupancy differences (e.g., Retiree vs Worker).

---

## 7. Resources

*   **Lighting**: [DOE Building Energy Codes Program - Prototype Building Models, IECC Prototype Building Models, Single-family detached house](https://www.energycodes.gov/prototype-building-models#Residential)
*   **Equipment and DHW**: [honeybee energyplus default schedules](https://github.com/ladybug-tools/honeybee-energy-standards/tree/master/honeybee_energy_standards/schedules)

