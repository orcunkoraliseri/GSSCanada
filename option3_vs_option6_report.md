# Comparative Review: Option 3 vs Option 6 Schedule Integration

## Executive Summary

The review confirms that **Option 6 (Neighbourhood Comparative)** successfully implements the same schedule integration logic as **Option 3 (Single Building Comparative)**, ensuring that both methods use the "MidRise Apartment" schedules as a baseline and apply identical "Presence Filter" logic for integrated scenarios.

However, a **critical discrepancy** was identified in the **Default Scenario** for Option 6. While Option 3 retains the original physics (power densities) of the user's IDF, Option 6's Default scenario relies on hardcoded power density values (4 W/m² for Lights, 9.05 W/m² for Equipment) generated during the neighbourhood IDF preparation process. This creates an apples-to-oranges comparison if the original input IDFs differ from these hardcoded defaults.

## Comparison Framework

The comparison is based on the logic defined in `Default Schedule Standardization.md` and `OccIntegPlan_lightEquipDHW.md`.

| Feature | Option 3 (Benchmark) | Option 6 (Neighbourhood) | Status |
| :--- | :--- | :--- | :--- |
| **Baseline Schedule** | DOE MidRise Apartment (loaded from `schedule.json`) | DOE MidRise Apartment (loaded from `schedule.json`) | ✅ Parity |
| **Logic: Lighting** | Daylight Method (`LightingGenerator`) on top of Baseline | Daylight Method (`LightingGenerator`) on top of Baseline | ✅ Parity |
| **Logic: Equip/DHW** | Presence Filter (`presence > 0.001?`) on top of Baseline | Presence Filter (`presence > 0.001?`) on top of Baseline | ✅ Parity |
| **Physics: Default Scenario** | **Preserves Original IDF Densities**<br>(`idf_optimizer` only updates schedule names) | **Uses Hardcoded Densities**<br>(`prepare_neighbourhood_idf` destroys objects; `inject_default` does not restore) | ❌ **Discrepancy** |
| **Physics: Integrated Scenarios** | **Preserves Original IDF Densities** | **Restores Original Densities**<br>(`inject_neighbourhood_schedules` explicitly parses original IDF) | ✅ Parity |

## Detailed Findings

### 1. Parity in Integration Logic
Both options correctly utilize the `LightingGenerator` and `PresenceFilter` classes. The code in `integration.inject_neighbourhood_schedules` (Option 6) mirrors `integration.inject_schedules` (Option 3) almost exactly, including the recently added verification fix for `PresenceFilter` logic.

### 2. The Power Density Gap
The discrepancy lies in how the **Default Scenario** is constructed.

*   **Option 3**: The user provides an IDF. `idf_optimizer.standardize_residential_schedules` iterates through existing `LIGHTS`/`ELECTRICEQUIPMENT` objects and changes their *Schedule_Name*. The *Watts_per_Zone_Floor_Area* remains whatever the user defined (e.g., 3.0 W/m² for a high-efficiency home).

*   **Option 6**:
    1.  `neighbourhood.prepare_neighbourhood_idf` is called first. It removes all original `LIGHTS` and `ELECTRICEQUIPMENT` objects and creates new per-building objects with **Hardcoded** values:
        *   Lights: 4.0 W/m²
        *   Equipment: 9.057 W/m²
    2.  **Integrated Scenarios (2025 etc)**: The function `inject_neighbourhood_schedules` accepts an `original_idf_path`. It contains specific logic to parse this original IDF and **update** the densities in the generated neighbourhood IDF to match.
    3.  **Default Scenario**: The function `inject_neighbourhood_default_schedules` **does not** accept `original_idf_path`. It injects the standard schedules but leaves the hardcoded densities (4.0 / 9.05) in place.

### Impact
If a user is simulating a Passive House neighbourhood with low Lighting Power Density (LPD of 2.0 W/m²):
*   **2025 Scenario**: Will use 2.0 W/m² (correctly restored).
*   **Default Scenario**: Will use 4.0 W/m² (hardcoded default).
*   **Result**: The difference between Default and 2025 will be artificially inflated, not just due to schedules, but due to a 2x difference in installed power density.

## Recommendations

To achieve full parity, the Default Scenario workflow in Option 6 must be refined to support density restoration.

### Refinement Plan
1.  **Modify `inject_neighbourhood_default_schedules`**:
    *   Add `original_idf_path` as an optional argument.
    *   Implement the same "density restoration" logic found in `inject_neighbourhood_schedules` (parsing `original_idf_path` and overwriting `Watts_per_Zone_Floor_Area`).
2.  **Update `main.py`**:
    *   Pass the `original_idf_path` (the user-selected IDF) when calling `inject_neighbourhood_default_schedules`.

This change requires no new simulations for verification, just a code refactor to ensure the "Default" baseline is physically consistent with the user's input model.
