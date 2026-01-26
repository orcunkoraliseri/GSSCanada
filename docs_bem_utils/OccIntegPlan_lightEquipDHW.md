# Implementation Plan of Lighting & Equipment & DHW

## 1. Pre-requisite: Default Schedule Standardization
Before implementing the occupancy-based logic for Lighting, Equipment, and DHW, we first establish a standardized baseline for all schedules (ie., presence, lighting, equipment, dhw).
*   **Source**: We replace existing schedules in the `.idf` with standardized "ApartmentMidrise" versions (/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup/Templates/schedule.json).
*   **Reference**: See [Default Schedule Standardization.md](Default%20Schedule%20Standardization.md) for the detailed mapping and implementation of these base schedules.
*   **Input for Integration**: The "Default Schedule" referred to in the sections below is this standardized ApartmentMidrise schedule.

## 2. Lighting: "The Daylight Threshold Method"

### 2.1 Objective
To convert binary occupancy presence into electrical lighting load (Watts) using a deterministic "gatekeeper" logic. This ensures lighting energy is only applied when the household is active and natural daylight is insufficient.

### 2.2 Data Sources & Input
The primary environmental data is derived from the EnergyPlus Weather Statistics (`.stat`) file.

*   **Table 1: Average Hourly Statistics for Global Horizontal Solar Radiation [Wh/m²]**
    *   *Usage*: Provides the 24-hour average solar profile for each month to determine when natural light falls below the critical threshold.
    *   *Files*: Located in `/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup/WeatherFile`
        *   `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx.stat`
        *   `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx.stat`
*   **Table 2: Monthly Sunshine/Daylight (Daily Average) [hours]**
    *   *Usage*: Validates the "active daylight hours" window.

### 2.3 Methodology: The "Gatekeeper" Logic
The core logic acts as a binary filter where **Occupancy is the "Trigger"** and **Daylight is the "Gatekeeper."**

#### The Logic Rule:
```
IF (Household is Active/Awake) AND (Solar Radiation < Threshold)
THEN Lighting Load = Installed Wattage
ELSE Lighting Load = 0
```

#### Parameters:
*   **Threshold**: 150 Wh/m² (Global Horizontal). This serves as the proxy for the indoor illuminance threshold (dusk/dawn).
*   **Wattage**: A constant value (e.g., 25 W per active zone for modern efficiency or 60 W for older standards) applied whenever the condition is met.

---

## 3. Equipment (MELs): "The Presence Filter Method"

### 3.1 Objective
To adjust standard/default equipment schedules (e.g., NECB or ASHRAE profiles) so they reflect actual household occupancy. This distinguishes between **Base Loads** (fridges, standby power) which run constantly, and **Active Loads** (TVs, cooking) which require an occupant.

### 3.2 Methodology: Min/Max Toggling
This method filters the default schedule using the generated Presence Schedule.

#### Definitions:
*   **Base Load**: The lowest value found in the Default Schedule (representing the floor/standby power).
*   **Active Load**: The highest value found in the Default Schedule (representing peak usage).

#### The Logic Rule:
```
IF (Household is Active/Home)
THEN Equipment Load = Active Load (The maximum value of the default schedule)
ELSE Equipment Load = Base Load (The minimum value of the default schedule)
```

---

## 4. Domestic Hot Water (DHW): "The Presence Filter Method"

### 4.1 Objective
To ensure that major hot water draws (showers, sinks) generally coincide with occupant presence, preventing high-usage events when the house is empty.

### 4.2 Methodology: Min/Max Toggling
Similar to the Equipment logic, this method uses the Presence Schedule to toggle the DHW demand between a resting state and a usage state.

#### Definitions:
*   **Base Load (Leak/Recirc)**: The lowest value found in the Default Schedule (typically 0 or a small recirculation loss).
*   **Active Load (Peak Draw)**: The highest value found in the Default Schedule (representing a shower or major draw).

#### The Logic Rule:
```
IF (Household is Active/Home)
THEN DHW Load = Active Load (The maximum value of the default schedule)
ELSE DHW Load = Base Load (The minimum value of the default schedule)
```
