## Goal
Implement "Option 4: Run simulation with neighbourhood" to allow running simulations on neighbourhood IDFs (multiple buildings) with **per-building occupancy profiles** across all end-uses.

## Why a New Module (`neighbourhood.py`)?
The neighbourhood IDFs (`NUs_RC1.idf`, `NUs_RC2.idf`) are structurally different from single-building IDFs. A dedicated module is required for the following reasons:

1.  **Structural Explosion**: Neighbourhood IDFs often use a single "master" object (e.g., one `People` object for 48 spaces). To assign different schedules to each building, we must programmatically "explode" this single object into individual objects per building.
2.  **Building Recognition**: The module identifies building boundaries by analyzing zone/space naming prefixes (e.g., grouping rooms by their shared coordinate-based ID).
3.  **Automated Slot Creation**: It creates unique schedule "slots" (e.g., `Occ_Bldg_0` to `Occ_Bldg_23`) that the integration engine can then target.
4.  **Separation of Concerns**: This keeps the core integration logic focused on *data*, while `neighbourhood.py` handles the *topology* of the multi-building model.

## Scope of Integration
Each building in the neighbourhood will receive a unique profile for:
1.  **Presence**: Unique presence masks for each household.
2.  **Metabolic Rate**: Unique activity schedules for each building.
3.  **Occupancy Density**: `Number of People` adjusted per building based on household data.
4.  **Lighting**: Unique presence-adjusted lighting schedules per building.
5.  **Equipment**: Unique presence-adjusted equipment schedules per building.
6.  **Water Use**: Unique hot water schedules per building.

## Proposed Changes

### 1. New Module: `bem_utils/neighbourhood.py`
- **`get_building_groups(idf_content)`**:
    - Groups spaces/zones by building based on name prefixes.
- **`prepare_neighbourhood_idf(idf_path, output_path)`**:
    - **Explosion Logic**: Deletes shared master objects for `People`, `Lights`, and `ElectricEquipment`.
    - **Creation**: Generates N new objects for each category (one per building group).
    - **Water Mapping**: Re-targets the 48 `WaterUse:Equipment` objects to N unique schedule names.
    - **Naming Convention**: Uses `Occ_Bldg_X`, `Light_Bldg_X`, `Equip_Bldg_X`, `DHW_Bldg_X`, and `Activity_Bldg_X`.

### 2. Integration Update: `bem_utils/integration.py`
- **`inject_neighbourhood_schedules(idf, schedules_list)`**:
    - Iterates through the list of N loaded households.
    - Injects presence, metabolic, lighting, equipment, and water schedules into the corresponding numbered slots (`_Bldg_0`, `_Bldg_1`...).

### 3. Main Menu: `bem_utils/main.py`
- **`option_neighbourhood_simulation()`**:
    - Implements the high-level workflow: Select IDF -> Detect N buildings -> Load N schedules -> Prepare IDF -> Inject -> Run.

## Verification
- Run with `NUs_RC1.idf` (24 buildings).
- Inspect `in.idf` to confirm 24 distinct schedule names exist for all categories.
- Verify simulation completion.
