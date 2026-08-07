# Implementation Plan - BEM Integration

## Goal Description
Integrate GSS-based BEM schedules (2005, 2015, 2025) into EnergyPlus simulations. The system will iterate through households in the schedule files, inject their specific occupancy and metabolic profiles into a base building model, run simulations, and visualize the results.

## User Review Required
> [!NOTE]
> **Parallelization**: Since the method implies running one simulation per household, this could result in many simulations. The system will support parallel execution using `concurrent.futures`.

## Proposed Changes
### Directory Structure
Create `eSim_bem_utils/` package in the project root:
- `__init__.py`
- `integration.py`: Handles CSV reading and IDF schedule injection.
- `simulation.py`: Wraps EnergyPlus execution (adapted from reference).
- `plotting.py`: Visualizes results (adapted from reference).
- `main.py`: Entry point for the workflow.

### Modules

#### `integration.py`
- **Class `ScheduleHandler`**:
  - method `load_schedules(csv_path)`: Reads CSV, groups by `SIM_HH_ID`.
  - method `create_schedule_object(hh_id, schedule_data)`: Generates `Schedule:Compact` strings for Weekday/Weekend.
  - method `inject_into_idf(idf_path, output_path, schedules)`: Uses `eppy` or string replacement to:
    - Remove old `People` or `Schedule` objects (optional, or just update pointers).
    - Insert new `Schedule:Compact` objects for Occupancy and Activity Level.
    - Update `People` object to point to new schedules.

#### `simulation.py`
- Adapted from `BEMSetup_Reference/runner.py`.
- Function `run_batch(idf_files, epw_file, n_workers)`: Runs simulations in parallel.
- Handles `ExpandObjects` and platform-specific E+ paths.

#### `plotting.py`
- Adapted from `BEMSetup_Reference/visualizer.py` and `read_results.py`.
- Function `plot_comparison(results_2005, results_2015, results_2025)`: Plots EUI or other metrics.

### Workflow (`main.py`)
1. User selects Schedule Year (2005, 2015, 2025).
2. Code loads corresponding CSV.
3. Code iterates through Households (optional: sample size limit).
4. Generates `HH_{id}.idf` for each.
5. Runs simulations.
6. Aggregates results.

## Verification Plan
### Automated Tests
- **Integration Test**: Run 1 household for 1 day. Check if `eplusout.err` has no fatal errors.
- **Output Check**: Verify `eplusout.csv`/`eplusout.sql` exists.

### Manual Verification
- Inspect generated IDF to ensure simple `Schedule:Compact` looks correct.
- Compare result plots against expectations (e.g., 2025 efficiency vs 2005).
