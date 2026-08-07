# Generate Figure 4.3.2: Temporal Trend in Energy Demand

## Goal Description
Create a line chart visualization (Figure 4.3.2) showing the trajectory of energy demand from 2005 to 2025 relative to the "Default" baseline across the three cities (Toronto, Montreal, Winnipeg).
- **Format**: 2x3 Grid (2 Rows, 3 Columns).
- **Row 1**: Heating Demand (Red line).
- **Row 2**: Cooling Demand (Blue line).
- **X-axis**: Years (2005, 2015, 2025).
- **Y-axis**: Annual Energy Demand (kWh/m²).
- **Baseline**: Static horizontal dashed line for the "Default" baseline (Heating in Row 1, Cooling in Row 2).
- **Narrative**: Highlighting the gap between static assumptions and behavioral evolution.

## Data Sources
1. `Prairies_Comparative_Analysis_Report.csv` (Winnipeg)
2. `Ontario_Comparative_Analysis_Report.csv` (Toronto)
3. `Quebec_Comparative_Analysis_Report.csv` (Montreal)

## Figure Layout (2×3 Grid)

```
      Toronto (5A)           Montreal (6A)           Winnipeg (7)
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ (a) Heating Trend     │ (b) Heating Trend     │ (c) Heating Trend     │
│                       │                       │                       │
│    /--- (Heating)     │    /--- (Heating)     │    /--- (Heating)     │
│   /                   │   /                   │   /                   │
│  *------- (Def Heat)  │  *------- (Def Heat)  │  *------- (Def Heat)  │
│                       │                       │                       │
│  2005  2015  2025     │  2005  2015  2025     │  2005  2015  2025     │
├───────────────────────┼───────────────────────┼───────────────────────┤
│ (d) Cooling Trend     │ (e) Cooling Trend     │ (f) Cooling Trend     │
│                       │                       │                       │
│         /-- (Cooling) │         /-- (Cooling) │         /-- (Cooling) │
│        /              │        /              │        /              │
│  *----/-- (Def Cool)  │  *----/-- (Def Cool)  │  *----/-- (Def Cool)  │
│                       │                       │                       │
│  2005  2015  2025     │  2005  2015  2025     │  2005  2015  2025     │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

**Implementation Details**:
- **Scales**: Shared Y-axis per ROW. 
    - Row 1 (Heating) will have a large scale (e.g., 0-100).
    - Row 2 (Cooling) will have a small scale (e.g., 0-5).
- **Lines**: 
    - Heating: Red (`#d62728`), marker='s'.
    - Cooling: Blue (`#1f77b4`), marker='^'.
    - Baseline: Gray dashed line (`:`).
- **Annotations**: 
    - Label the % gap between 2025 and Default for both Heating and Cooling.

## Proposed Changes

### Script Development
#### [NEW] [plot_figure_4.3.2.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/eSim_occ_utils/plotting/plot_figure_4.3.2.py)
- **Inputs**: The three report CSVs.
- **Logic**:
    1. Parse CSVs.
    2. Create 2x3 subplot grid.
    3. Loop Cities:
        - Top: Plot Heating trajectory + Default Heating line.
        - Bottom: Plot Cooling trajectory + Default Cooling line.
        - Annotate gaps.
- **Output**:
    - Saves image to `eSim_occ_utils\plotting\Figure_4.3.2_Temporal_Trend.png`.

## Verification Plan
### Visual Inspection
- Confirm Heating and Cooling are separated.
- Check that Cooling trend is now clearly visible (not flatlined).
- Verify "Default" baseline appears in both rows.
