# BEM Simulation Workflow Walkthrough

I have finalized a robust, end-to-end BEM simulation and analysis pipeline. This module integrates household schedules into EnergyPlus, optimizes models for simulation, and provides high-fidelity visualization of results.

## Final Workflow Overview

The tool now features a **Menu-Driven Interface** (accessible via `run_bem.py`):

1.  **Visualize a Building**: 3D interactive model viewer to inspect the IDF geometry.
2.  **Run a Simulation**:
    *   **Schedule Filtering**: Filter by dwelling type (e.g., 'SingleD' for base building matching).
    *   **Random Sampling**: Simulates a random selection of households for unbiased testing.
    *   **IDF Optimization**: Automatically fixes deprecated fields, adds necessary output variables, and optimizes simulation settings.
    *   **Parallel Execution**: Runs simulations concurrently for maximum speed.
3.  **Comparative Simulation (Option 3)** (New):
    *   **Multi-Scenario Analysis**: Runs 2025, 2015, 2005, and Default baselines in parallel.
    *   **Smart Matching**: Selects a household from 2025 and automatically finds matching-sized households from other years.
    *   **Grouped Visualization**: Produces a comparative bar chart of end-use energy demand across all 4 scenarios.
    *   **Annual Time-Series Profiles**: Generates a grid of line plots showing monthly demand for all 4 scenarios (normalized to kWh/m²).
4.  **Visualize Performance (Option 5)**:
    *   **Unified Search**: Now finds both standard batches and comparative simulation folders.
    *   **Dynamic Presentation**: Smartly determines when to show histograms (for groups) vs. disaggregated bar charts (for individual households), avoiding confusing "0.2 household" labels.
    *   **Accurate EUI Breakdown**: Results are converted from kBtu to kWh and normalized by **Net Conditioned Floor Area** in m².

## Enhanced Occupancy Integration (Final Implementation)

The tool now implements a sophisticated occupancy-driven load projection system:

1.  **Occupancy Scaling**: 
    - Automatically updates `PEOPLE.Number_of_People` based on the actual household size (`hhsize`) from TUS data.
    - Clears conflicting headcount calculation methods to ensure correct absolute scaling.

2.  **Sophisticated Schedule Multiplication**:
    - **Original Approach**: Binary presence mask (1.0 home / 0.0 away) - discarded as it caused unrealistic spikes (especially in water heating).
    - **Final Formula**: `updated_schedule = default_schedule × presence_mask`.
    - This preserves the original shape of lighting, equipment, and water heating loads while residents are home, while zeroing them out gracefully when they are away.

3.  **Robust Schedule Parsing**:
    - Implemented a hierarchy-aware parser that can extract 24-hour profiles from:
        - `Schedule:Year` → `Schedule:Week` → `Schedule:Day:Hourly`
        - `Schedule:Compact` (Handles complex `Until: HH:MM, Value` patterns).
    - Successfully processes diverse load profiles like showers, dishwashers, and lights.

## Updated Directory Structure

- `eSim_bem_utils/`:
    - `integration.py`: Final implementation of high-fidelity schedule multiplication and robust IDF injection.
    - `main.py`: Refined Option 3/5 with better formatting and logic.
    - `plotting.py`: Added `plot_comparative_timeseries_subplots` for annual profile comparison.
- `docs/`: 
    - `occupancy_integration.md`: [UPDATED] Detailed final documentation of the current occupancy logic and math.
    - `walkthrough.md`: [NEW] Detailed walkthrough of the final simulation workflow.

## Final Verification Results

- Verified with household `2402`, `4270`, and others.
- **Lighting/Equipment**: Shows reduction compared to Default based on presence patterns, while maintaining original profile shape.
- **Water Heating**: Successfully resolved the "100x spike" issue. Values now show realistic variation (~10-50 kWh/m²) by correctly multiplying the small base flow fractions by the presence mask.
- Verified successful parallel execution and result extraction for all 4 scenarios.

## How to Run

```bash
python3 run_bem.py
```
1. Select **Option 3** to run a comparative study across scenario years.
2. Select **Option 5** to review and compare existing results.
