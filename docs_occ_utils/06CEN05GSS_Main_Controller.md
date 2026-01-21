# 06CEN05GSS Main Controller Module

Unified controller for the occupancy modeling pipeline.

## Overview

The main controller (`06CEN05GSS_main.py`) provides a menu-driven interface to run all pipeline steps from one place.

## Pipeline Steps

| Step | Module | Description |
|------|--------|-------------|
| 1 | Alignment | Harmonize Census 2006 with GSS 2005 |
| 2 | Profile Matching | Assign GSS schedules to Census agents |
| 3 | HH Aggregation | Convert to 5-minute household grids |
| 4 | BEM Conversion | Generate hourly schedules for EnergyPlus |

## Data Flow

```
DataSources_GSS/Main_files/ --> [Alignment] --> Outputs_Aligned/06CEN05GSS_alignment/
Outputs_CENSUS/                                          |
                                                         v
                              [Profile Matching] --> 06CEN05GSS_ProfileMatching/
                                                         |
                                                         v
                              [HH Aggregation] --> 06CEN05GSS_HH_aggregation/
                                                         |
                                                         v
                              [BEM Conversion] --> 06CEN05GSS_occToBEM/
```

## Menu Options

- 1: Step 1 - Alignment (Census + GSS harmonization)
- 2: Step 2 - Profile Matching (assign schedules)
- 3: Step 3 - HH Aggregation (5-min grids)
- 4: Step 4 - BEM Conversion (hourly schedules)
- 5: Run Full Pipeline (Steps 1-4)
- 6: Census DTYPE Analysis (utility)
- 7: GSS Header Reader (utility)
- 8: Change Sample Percentage
- 0: Exit

## Usage

### Interactive Menu
```bash
python occ_utils/06CEN05GSS_main.py
```

### With Custom Sample
```bash
python occ_utils/06CEN05GSS_main.py --sample 10
```

### Run Specific Step Directly
```bash
python occ_utils/06CEN05GSS_main.py --run 5  # Full pipeline
```

## Sample Percentage

- Default: 5%
- Controls data sampling in Profile Matching
- Propagates through HH Aggregation and BEM Conversion
- Output files include sample suffix (e.g., `_sample5pct.csv`)

## Location

`occ_utils/06CEN05GSS_main.py`
