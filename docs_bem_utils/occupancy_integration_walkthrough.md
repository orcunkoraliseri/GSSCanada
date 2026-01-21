# Occupancy Data Integration for BEM (Building Energy Model)

This document explains how time-use survey (TUS) derived occupancy data is integrated into the EnergyPlus simulation using a state-based logic that prevents energy underestimation.

---

## 1. Core Methodology: State-Based Logic

Instead of a simple binary multiplication (which causes the "Zero-Energy Fallacy"), we use a **State-Based Approach**. The schedule value is determined by whether the occupant is **Present** or **Absent**, with specific floors applied to ensure physical realism.

### The Master Formulas

#### The "Active Floor" (For Lights & Electric Equip)
*   **Logic:** If a person is home, energy usage rises to a minimum active level to support activity (e.g., computers, ambient light).
*   **Formula:** `If Present → MAX( Default_Schedule, Active_Floor_Value )`

#### The "Baseload Floor" (For Absence/Sleep)
*   **Logic:** Energy use rarely drops to absolute zero. We apply a minimum floor for "always-on" loads or human error.
*   **Formula:** `If Absent → Baseload_Value`

---

## 2. Integration Rules by Load Type

| Schedule Type | Strategy | Rule when Present | Rule when Absent | Physical Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Equipment** (Electric) | **Active Floor** | **MAX(Default, 0.50)** | **0.35 (Baseload)** | **Present:** TVs/PCs are active.<br>**Absent:** Fridge/Router never sleep. |
| **Lighting** | **Active Floor + Baseload** | **MAX(Default, 0.50)** | **0.05 (Baseload)** | **Present:** Lights required for activity.<br>**Absent:** Security lights, corridor nightlights, or forgetfulness. |
| **Hot Water** | **Event-Based** | **MAX(Default, 0.0)** | **0.0** | **Present:** Only uses original schedule events.<br>**Absent:** No draws possible. |
| **Gas Equipment** | **Event-Based** | **Default Schedule** | **0.0** | **Present:** Cooking/Fireplaces are intentional events, not continuous states.<br>**Absent:** Modern appliances have no pilot lights. |

---

## 3. Comparison: Why "Active Floor" Matters

**Scenario:** 11:00 AM on a weekday (Occupant is Working from Home).
**Assumptions:** Default Schedule = `0.15` (assumes most people are away).

| Feature | Old Method (Simple Mask) | New Method (Active Floor) |
| :--- | :--- | :--- |
| **Formula** | `0.15 × 1 (Present)` | `MAX( 0.15, 0.50 )` |
| **Resulting Value** | **0.15** (Low) | **0.50** (Moderate) |
| **Physical Meaning** | Occupant is home but sitting in the dark. | Occupant is home and actively using devices. |
| **Impact on Results** | Creates an artificial "Energy Gap". | Closes the gap; matches real-world intensity. |

---

## 4. Technical Implementation Details

The integration logic applies these rules to specific IDF objects.

| Object Type | Field Modified | Absent Value (Floor) | Present Injection (Active Floor) |
| :--- | :--- | :--- | :--- |
| `LIGHTS` | `Schedule_Name` | **0.05** | **0.50** |
| `ELECTRICEQUIPMENT` | `Schedule_Name` | **0.35** | **0.50** |
| `WATERUSE:EQUIPMENT` | `Flow_Rate_Fraction...` | **0.0** | **0.0** (None) |
| `GASEQUIPMENT` | `Schedule_Name` | **0.0** | None (Strict Default) |

---

## 5. Objects Unmodified (HVAC)

**HVAC thermostat schedules are intentionally NOT modified.**

| Object Type | Reason for Exclusion |
| :--- | :--- |
| `ThermostatSetpoint:DualSetpoint` | **"Set and Forget" Behavior:** Canadian households rarely adjust thermostats based on short-term occupancy. |
| HVAC Availability Schedules | Systems remain available 24/7 to maintain building physics. |

**Impact on Results:**
By keeping HVAC schedules constant, the simulation correctly captures the thermodynamic penalty of occupancy changes (e.g., when occupants are away, internal gains drop, causing the heating system to work harder to maintain the setpoint).

---

## 6. Occupancy Inputs

| Parameter | IDF Field | Description |
| :--- | :--- | :--- |
| `Number_of_People` | Integer | Set to actual household size (`hhsize`) from TUS |
| `Number_of_People_Schedule_Name` | Fraction (0–1) | Fractional **presence** (0 or 1) derived from TUS |
| `Activity_Level_Schedule_Name` | Watts | **Metabolic rate** per person based on activity |

---

## 7. References

- [EnergyPlus People Object](https://bigladdersoftware.com/epx/docs/24-2/input-output-reference/group-internal-gains.html#people)
- Statistics Canada GSS Time-Use Survey datasets (2005, 2015, 2025)
