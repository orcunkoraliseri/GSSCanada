# Generate Figure 4.3.1: Energy Demand Bar Chart with Error Bars

## Goal Description
Create a visualization (Figure 4.3.1) showing Annual Heating and Cooling Demand (kWh/m²) for each scenario (Default, 2005, 2015, 2025) across the three cities (Toronto, Montreal, Winnipeg).
- **Format**: 2x3 Grid (2 Rows, 3 Columns).
- **Row 1**: Heating Demand (Blue tint).
- **Row 2**: Cooling Demand (Red tint).
- **Columns**: Toronto, Montreal, Winnipeg.
- **Styling**: Lighter/Less opaque colors (e.g., alpha=0.6) for better visibility.
- **Annotations**: Percentage difference arrow for key comparison (Default vs 2025).

## Data Sources
1. `Prairies_Comparative_Analysis_Report.csv` (Winnipeg)
2. `Ontario_Comparative_Analysis_Report.csv` (Toronto)
3. `Quebec_Comparative_Analysis_Report.csv` (Montreal)

## Figure Layout (2×3 Grid)

```
      Toronto (5A)           Montreal (6A)           Winnipeg (7)
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ (a) Heating Demand    │ (b) Heating Demand    │ (c) Heating Demand    │
│                       │                       │                       │
│   █   █   █   █       │   █   █   █   █       │   █   █   █   █       │
│   █   █   █   █       │   █   █   █   █       │   █   █   █   █       │
│   █   █   █   █       │   █   █   █   █       │   █   █   █   █       │
│  Def '05 '15 '25     │  Def '05 '15 '25     │  Def '05 '15 '25     │
│                       │                       │                       │
│  Color: Light Blue    │  Color: Light Blue    │  Color: Light Blue    │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ (d) Cooling Demand    │ (e) Cooling Demand    │ (f) Cooling Demand    │
│                       │                       │                       │
│   ░   ░   ░   ░       │   ░   ░   ░   ░       │   ░   ░   ░   ░       │
│   ░   ░   ░   ░       │   ░   ░   ░   ░       │   ░   ░   ░   ░       │
│  Def '05 '15 '25     │  Def '05 '15 '25     │  Def '05 '15 '25     │
│                       │                       │                       │
│  Color: Light Red     │  Color: Light Red     │  Color: Light Red     │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

**Design Details**:
- **Y-axis Scale**:
    - **Row 1 (Heating)**: Shared Y-axis across all 3 cities (e.g., 0-100 kWh/m²) to allow direct comparison of magnitude.
    - **Row 2 (Cooling)**: Shared Y-axis across all 3 cities (e.g., 0-5 kWh/m²) because cooling loads are much smaller and would be invisible on the heating scale.
- **Colors**: Use lighter shades (e.g., `skyblue`, `lightcoral`) or `alpha=0.7` to mimic the requested transparency.
- **Error Bars**: Standard Deviation (Black caps).

## Proposed Changes

### Script Development
#### [NEW] [plot_figure_4.3.1.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/occ_utils/plotting/plot_figure_4.3.1.py)
- **Inputs**: The three report CSVs.
- **Logic**:
    1. Parse each CSV to extract `Mean(kWh/m2)` and `StdDev` for Heating and Cooling.
    2. Setup matplotlib Figure with 2 rows x 3 columns.
    3. Loop through Cities (Columns):
        - **Top Plot (Row 0)**: Heating Data. Blue bars. Annotate % diff.
        - **Bottom Plot (Row 1)**: Cooling Data. Red bars. Annotate % diff.
    4. Apply shared Y-limits per row.
    5. Clean formatting (remove inner y-labels, keep bottom x-labels).
- **Output**:
    - Saves image to `occ_utils\plotting\Figure_4.3.1_Energy_Demand.png`.

## Verification Plan
### Visual Inspection
- Confirm separation of Heating and Cooling into distinct rows.
- Verify that Cooling bars are clearly visible (not squashed by heating scale).
- Check that Y-axis is shared per row.
- Verify lighter color opacity.
