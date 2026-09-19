# Generate Table 4.3.4: Peak Heating and Cooling Loads

## Goal Description
Generate a CSV table (Table 4.3.4) identifying the Peak Heating and Peak Cooling loads (W/m²) and their timing for each scenario.
- **Columns**: Scenario, Peak Heating (W/m²), Time (Heat), Peak Cooling (W/m²), Time (Cool).
- **Formatting**:
    - **Loads**: Rounded to 2 decimal places.
    - **Time**: "MMM DD HH:00" (e.g., "Jan 15 08:00").

### Table Layout

| Scenario       | Peak Heating (W/m²) | Time (Heat)     | Peak Cooling (W/m²) | Time (Cool)     |
|:---------------|:--------------------|:----------------|:--------------------|:----------------|
| Default        | --                  | MMM DD HH:00    | --                  | MMM DD HH:00    |
| 2005           | --                  | MMM DD HH:00    | --                  | MMM DD HH:00    |
| 2015           | --                  | MMM DD HH:00    | --                  | MMM DD HH:00    |
| 2025           | --                  | MMM DD HH:00    | --                  | MMM DD HH:00    |

## Data Sources
- `eplusout.sql` files from `iter_1` of each scenario across the three cities.
- **Variables**: 
    - `Zone Air System Sensible Heating Energy` (Sum of all zones)
    - `Zone Air System Sensible Cooling Energy` (Sum of all zones)
- **Normalization**: Net Conditioned Building Area.
- **Scope**:
    - Primarily **Toronto (5A)** as the representative case for "Timing" analysis.

## Methodology
1. **Extraction**:
    - For each Scenario (Default, 2005, 2015, 2025):
        - Load SQL data for Toronto (iter_1).
        - Convert Energy (J) to Power (W) -> (J / 3600).
        - Normalize by Area -> W/m².
2. **Analysis**:
    - **Heating**: Find Max Value. Retrieve Month, Day, Hour.
    - **Cooling**: Find Max Value. Retrieve Month, Day, Hour.
3. **Output**:
    - Save to `eSim_occ_utils\plotting\Table_4.3.4_Peak_Loads.csv`.

### Alternative Figure Layout (Figure 4.3.4)

### Alternative Figure Layout (Figure 4.3.4)

If this data were plotted instead of tabulated:
- **Type**: 1x2 Subplot Grid (Bar Charts).
- **Format**:
    - **(a) Heating**: Left subplot, Red bars.
    - **(b) Cooling**: Right subplot, Blue bars.
- **X-axis**: Scenario.
- **Y-axis**: Peak Load (W/m²), scaled independently or appropriately.
- **Annotations**: Place the "Time of Peak" (e.g., "Jan 15 08:00") directly above each bar.

```
       (a) Peak Heating                (b) Peak Cooling
       |      "Jan 15"                 |
W/m²   |         [ ]                   |       "Jul 20"
       |         [ ]                   |         [ ]
       |         [ ]                   |         [ ]
       |__________________             |__________________
        Default  2005 ...               Default  2005 ...
```

## Proposed Changes

### Script Development
#### [NEW] [plot_figure_4.3.4.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/eSim_occ_utils/plotting/plot_figure_4.3.4.py)
- **Functions**:
    - `get_peak(df, variable)`: Returns (MaxVal, TimestampStr).
- **Execution**:
    - Iterate Scenarios.
    - Print table to console.
    - Save to CSV.

## Verification Plan
- Check if Peak Heating occurs in Winter.
- Check if Peak Cooling occurs in Summer.
- Verify "Default" peaks align with standard assumptions.
- Verify "GSS" peaks timing vs Default.
