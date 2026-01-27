# Implementation Plan of Lighting & Equipment & DHW

## 1. Pre-requisite: Default Schedule Standardization
Before implementing the occupancy-based logic for Lighting, Equipment, and DHW, we first establish a standardized baseline for all schedules (ie., presence, lighting, equipment, dhw).
*   **Source**: We replace existing schedules in the `.idf` with standardized "ApartmentMidrise" versions (/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup/Templates/schedule.json).
*   **Reference**: See [Default Schedule Standardization.md](Default%20Schedule%20Standardization.md) for the detailed mapping and implementation of these base schedules.
*   **Input for Integration**: The "Default Schedule" referred to in the sections below is this standardized ApartmentMidrise schedule.

---

## 2. Lighting: "The Presence Filter Method"

### 2.1 Objective
To modulate electrical lighting load based on occupancy presence while preserving the natural shape of default lighting profiles. Lighting energy follows the default schedule when the household is active, and drops to base load when absent.

### 2.2 Data Sources & Input
The primary environmental data is derived from the EnergyPlus Weather Statistics (`.stat`) file.

*   **Table 1: Average Hourly Statistics for Global Horizontal Solar Radiation [Wh/m²]**
    *   *Usage*: Provides the 24-hour average solar profile for each month. Used for visualization purposes to show daylight conditions.
    *   *Files*: Located in `/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup/WeatherFile`
        *   `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx.stat`
        *   `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx.stat`
*   **Table 2: Monthly Sunshine/Daylight (Daily Average) [hours]**
    *   *Usage*: Validates the "active daylight hours" window.

### 2.3 Methodology: Presence Filter with Gradual Changes
This method preserves the natural shape of the default lighting schedule while modulating based on occupancy.

#### Definitions:
*   **Default Schedule Value**: The hourly value from the standardized ApartmentMidrise lighting schedule (varies by hour).
*   **Base Load**: The minimum value from the default schedule during absent hours (representing standby/minimal lighting).

#### The Logic Rule:
```
IF (Household is Active/Home)
THEN Lighting Load = Default Schedule Value at that hour (preserves gradual changes)
ELSE Lighting Load = Base Load (minimum from absent hours)
```

#### Parameters:
*   **Threshold (reference)**: 150 Wh/m² (Global Horizontal). Used for visualization to indicate daylight conditions.

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
