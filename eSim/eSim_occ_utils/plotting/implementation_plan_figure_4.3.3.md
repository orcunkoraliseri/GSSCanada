# Generate Figure 4.3.3: Seasonal and Diurnal Demand Profiles

## Goal Description
Create a 1x4 panel visualization (Figure 4.3.3) showing hourly heating (Winter) and cooling (Summer) load profiles for representative days.
- **Format**: 1 Row x 4 Columns.
    - **(a) Winter Weekday (Jan)**: Heating Load.
    - **(b) Winter Weekend (Jan)**: Heating Load.
    - **(c) Summer Weekday (Jul)**: Cooling Load.
    - **(d) Summer Weekend (Jul)**: Cooling Load.
- **X-axis**: Hour of Day (0-23).
- **Y-axis**: Average Hourly Load (W/m²).
- **Curves**: Default, 2005, 2015, 2025.

## Data Sources
- `eplusout.sql` files from `iter_1` of each scenario across the three cities.
- **Variables**: `Heating:EnergyTransfer` (for Winter), `Cooling:EnergyTransfer` (for Summer).
- **Normalization**: Profiles will be normalized by Net Conditioned Building Area.
- **Aggregation**: Averaged across all 3 cities.

## Figure Layout (1x4 Grid)

```
      (a) Win WD (Jan) [Heat]   (b) Win WE (Jan) [Heat]   (c) Sum WD (Jul) [Cool]   (d) Sum WE (Jul) [Cool]
    |                         |                         |                         |
    |      /-- 2025           |            /-- 2025     |      _-- 2025           |      _-- 2025
    |     /   ...             |           /   ...       |     /   ...             |     /   ...
kW/m|    /-- Default          |          /-- Default    |   _/-- Default          |   _/-- Default
    |_______________________  |_______________________  |_______________________  |_______________________
           Hour (0-23)               Hour (0-23)               Hour (0-23)               Hour (0-23)
```

## Proposed Changes

### Script Development
#### [NEW] [plot_figure_4.3.3.py](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/eSim_occ_utils/plotting/plot_figure_4.3.3.py)
- **Logics**:
    - **Data**: Same as before (extract Heat/Cool for Jan/Jul).
    - **Plotting**: 
        - 1 Row, 4 Columns.
        - Panel 0: Winter Weekday -> Heating.
        - Panel 1: Winter Weekend -> Heating.
        - Panel 2: Summer Weekday -> Cooling.
        - Panel 3: Summer Weekend -> Cooling.
        - Row-independent scaling is no longer applicable; instead, use variable-specific scales (Heat vs Cool).
- **Output**:
    - `eSim_occ_utils\plotting\Figure_4.3.3_Diurnal_Profiles.png`

## Verification Plan
- Confirm Winter panels show Heating (High W/m²).
- Confirm Summer panels show Cooling (Lower W/m²).
- Check X-axis and Legends.
