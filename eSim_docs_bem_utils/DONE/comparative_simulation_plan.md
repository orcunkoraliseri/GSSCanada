# Implementation Plan: Comparative Simulation Feature (Option 3)

## Goal
Add a new menu option (3) that runs a comparative analysis across 6 scenarios:
1. **2005 Schedules** - Injected from `BEM_Schedules_2005.csv`
2. **2010 Schedules** - Injected from `BEM_Schedules_2010.csv`
3. **2015 Schedules** - Injected from `BEM_Schedules_2015.csv`
4. **2022 Schedules** - Injected from `BEM_Schedules_2022.csv`
5. **2025 Schedules** - Injected from `BEM_Schedules_2025.csv`
6. **Default** - Base IDF without schedule injection (uses original IDF schedules)

> The 2010 and 2022 scenarios were added in a second pass; see `eSim_docs_bem_utils/2010_22_expansion.md` for the expansion history.

## Proposed Changes

### 1. [MODIFY] [main.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_bem_utils/main.py)

Add new function `option_comparative_simulation()`:
- Prompts user to select base IDF, weather file, and dwelling type
- Randomly selects 1 household ID present across all 3 schedule files
- For each scenario:
  - Injects schedules (or uses base IDF for default)
  - Runs EnergyPlus simulation
  - Extracts EUI results
- Calls plotting function to generate comparative chart

Update `main_menu()` to include Option 3.

---

### 2. [MODIFY] [plotting.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_bem_utils/plotting.py)

Add new function `plot_comparative_eui()`:
- **Input**: Dictionary of results `{'2025': {...}, '2015': {...}, '2005': {...}, 'Default': {...}}`
- **Output**: Grouped bar chart with:
  - X-axis: End-use categories (Heating, Cooling, Lighting, etc.)
  - Y-axis: EUI (kWh/m²)
  - 4 bars per category (one for each scenario)
  - Clear legend identifying each scenario

---

## Verification Plan

### Automated Tests
1. Run Option 3 from the menu
2. Verify 4 simulations complete successfully
3. Verify 4 individual breakdown plots are generated
4. Verify 1 comparative grouped bar plot is generated

### Expected Output
- `SimResults_Plotting/Comparative_HH_{id}_2025.png`
- `SimResults_Plotting/Comparative_HH_{id}_2015.png`
- `SimResults_Plotting/Comparative_HH_{id}_2005.png`
- `SimResults_Plotting/Comparative_HH_{id}_Default.png`
- `SimResults_Plotting/Comparative_Summary_HH_{id}.png` (the grouped bar chart)
