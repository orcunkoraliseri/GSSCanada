# Occupancy Data Integration for BEM (Building Energy Model)

This document explains how time-use survey (TUS) derived occupancy data is integrated into the EnergyPlus simulation using a **proportional weighted approach** that accurately reflects household size effects on energy consumption.

---

## 1. Core Methodology: Hybrid Proportional Approach

We use a **Hybrid Proportional Approach** that combines two proven strategies:
1. **MAX Function** - Ensures when someone is home, energy use is at least the default schedule OR an active floor (whichever is higher)
2. **Proportional Weighting** - Scales linearly with occupancy fraction

### The Master Formula

```
Schedule_Value = Occupancy × MAX(Default_Schedule, Active_Floor) + (1 - Occupancy) × Baseload
```

Where:
- `Occupancy` = Fraction of household members present (0.0 to 1.0)
- `Default_Schedule` = Original building schedule value from the IDF
- `Active_Floor` = Minimum active level (0.50 for lights/equipment)
- `Baseload` = Minimum consumption when empty (always-on loads)

### Why This Works

| Scenario | Pure Proportional | Hybrid Approach |
|----------|-------------------|-----------------|
| Default schedule = 0.90, occ = 1.0 | 0.50 (too low!) | 0.90 ✓ |
| Default schedule = 0.20, occ = 1.0 | 0.50 | 0.50 ✓ |
| Default schedule = 0.90, occ = 0.0 | 0.05 (baseload) | 0.05 ✓ |

### Example Calculation

For a **4-person household**, Default_Schedule = 0.80, Active Floor = 0.50, Baseload = 0.05:

| People Home | Occupancy | Calculation | Result |
|-------------|-----------|-------------|--------|
| 0 of 4 | 0.00 | 0.00 × MAX(0.80, 0.50) + 1.00 × 0.05 | **0.050** |
| 1 of 4 | 0.25 | 0.25 × MAX(0.80, 0.50) + 0.75 × 0.05 | **0.238** |
| 2 of 4 | 0.50 | 0.50 × MAX(0.80, 0.50) + 0.50 × 0.05 | **0.425** |
| 4 of 4 | 1.00 | 1.00 × MAX(0.80, 0.50) + 0.00 × 0.05 | **0.800** |

---

## 2. Integration Rules by Load Type

| Schedule Type | Active Floor | Baseload | Formula |
| :--- | :--- | :--- | :--- |
| **Lighting** | 0.50 | 0.05 | `occ × MAX(default, 0.50) + (1-occ) × 0.05` |
| **Equipment** (Electric) | 0.50 | 0.35 | `occ × MAX(default, 0.50) + (1-occ) × 0.35` |
| **Hot Water** | Default Schedule | 0.00 | `occ × default + (1-occ) × 0.00` |
| **Gas Equipment** | Default Schedule | 0.00 | `occ × default + (1-occ) × 0.00` |

### Physical Justification

| Load Type | Baseload Reason | Active Floor Reason |
|-----------|-----------------|---------------------|
| **Lighting** | Security lights, night lights | Room lighting for activities |
| **Equipment** | Fridge, router, always-on devices | TVs, computers, appliances in use |
| **Hot Water** | None (no draws when away) | Shower, cooking, cleaning events |

---

## 3. Comparison: Binary vs Proportional Approach

**Scenario:** 9:00 AM weekday, 1 of 4 household members working from home.

| Method | Occupancy Value | Lights Calculation | Result |
|--------|-----------------|-------------------|--------|
| **Binary (old)** | 0.25 < 0.30 threshold | Baseload applied | **0.05** |
| **Proportional (new)** | 0.25 | 0.25 × 0.50 + 0.75 × 0.05 | **0.163** |

The proportional approach correctly reflects that 1 person at home uses some energy, but less than a full household.

---

## 4. Technical Implementation Details

| Object Type | Field Modified | Baseload | Active Floor |
| :--- | :--- | :--- | :--- |
| `LIGHTS` | `Schedule_Name` | **0.05** | **0.50** |
| `ELECTRICEQUIPMENT` | `Schedule_Name` | **0.35** | **0.50** |
| `WATERUSE:EQUIPMENT` | `Flow_Rate_Fraction...` | **0.00** | Default |
| `GASEQUIPMENT` | `Schedule_Name` | **0.00** | Default |

---

## 5. Objects Unmodified (HVAC)

**HVAC thermostat schedules are intentionally NOT modified.**

| Object Type | Reason for Exclusion |
| :--- | :--- |
| `ThermostatSetpoint:DualSetpoint` | "Set and Forget" Behavior: Canadian households rarely adjust thermostats based on short-term occupancy. |
| HVAC Availability Schedules | Systems remain available 24/7 to maintain building physics. |

---

## 6. Occupancy Inputs

| Parameter | IDF Field | Description |
| :--- | :--- | :--- |
| `Number_of_People` | Integer | Set to actual household size (`hhsize`) from TUS |
| `Number_of_People_Schedule_Name` | Fraction (0–1) | Fractional **presence** derived from TUS |
| `Activity_Level_Schedule_Name` | Watts | **Metabolic rate** per person based on activity |

---

## 7. Scientific Basis

The proportional weighted approach is based on occupancy-responsive building energy models used in academic research:

- **Wang, D., Federspiel, C. C., & Arens, E. (2005).** "Modeling Occupancy in Single Person Offices." *Energy and Buildings*, 37(2), 121-126. DOI: [10.1016/j.enbuild.2004.06.015](https://doi.org/10.1016/j.enbuild.2004.06.015)

- **U.S. Department of Energy.** *Building Energy Codes Program - Residential Prototype Building Models.* Uses fractional schedules for plug loads and lighting that scale with occupancy. [Link](https://www.energycodes.gov/prototype-building-models)

- **Azar, E., & Menassa, C. C. (2012).** "A Comprehensive Analysis of the Impact of Occupancy Parameters in Energy Simulation of Office Buildings." *Energy and Buildings*, 55, 841-853. DOI: [10.1016/j.enbuild.2012.10.002](https://doi.org/10.1016/j.enbuild.2012.10.002)

---

## 8. References

- [EnergyPlus People Object](https://bigladdersoftware.com/epx/docs/24-2/input-output-reference/group-internal-gains.html#people)
- Statistics Canada GSS Time-Use Survey datasets (2005, 2015, 2025)

