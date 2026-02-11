# Figure 4.1.3: Default vs 2025 GSS-Derived Schedules

**Goal**: Create a "smoking gun" figure that juxtaposes DOE MidRise Apartment default assumptions (from `schedule.json`) against empirically-derived Canadian 2025 schedules.

---

## Data Sources

| Series | Occupancy Source | Metabolic Source |
|--------|-----------------|------------------|
| **Default** | `BEM_Setup/Templates/schedule.json` (parsed via `bem_utils.idf_optimizer`)<br>Profile: `ApartmentMidRise OCC_APT_SCH` | Same JSON<br>Profile: `ApartmentMidRise Activity Schedule` (95W) |
| **2025 GSS** | `BEM_Setup/BEM_Schedules_2025.csv` | `BEM_Setup/BEM_Schedules_2025.csv` |

---

## Figure Layout (1x2 Horizontal)

```
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│ (a) Occupancy Fraction               │  │ (b) Metabolic Rate (W/person)        │
│                                      │  │                                      │
│ 1.0 ├───────\          /─────       │  │ 100 ├───────\          /─────       │
│     │ Default \      /              │  │     │ Default \      /              │
│ 0.6 ├··········\~~~~/········       │  │  80 ├··········\~~~~/········       │
│     │   GSS     \__/                │  │     │   GSS     \__/                │
│ 0.0 └───────────────────────       │  │   0 └───────────────────────       │
│      0    6    12   18   24         │  │      0    6    12   18   24         │
│                                      │  │                                      │
│ Annotations:                         │  │ Annotations:                         │
│ - Night Overestimate (0-6h)          │  │ - Sleep Phase (0-6h)                 │
│ - Morning Transition (7-9h)          │  │ - Midday Overestimate (9-15h)        │
│ - Evening Gap (17-21h)               │  │ - Evening Activity (17-21h)          │
└──────────────────────────────────────┘  └──────────────────────────────────────┘
```

**Design details**:
- **Layout**: 1 Row x 2 Columns.
- **Lines**: Default (Red Dashed), 2025 GSS Mean (Blue Solid) + Shaded ±1σ.
- **Discrepancy Zone**: Fill between curves to highlight the "error".
- **Grid**: Standard styling.

---

## Proposed Changes

#### [NEW] [plot_default_vs_classification.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/occ_utils/plotting/plot_default_vs_classification.py)

- **Imports**: `bem_utils.idf_optimizer` to load standard schedules reliably.
- **Process**:
    1. Load Default schedules from JSON (via utility).
    2. Load 2025 GSS data (Weekday).
    3. Compute hourly mean/std.
    4. Plot 1x2 subplot.
    5. Annotate key zones.
- **Output**: `occ_utils/plotting/Fig_4_1_3_Default_vs_Classification.png`.

---

## Verification Plan

1. Run: `python3 occ_utils/plotting/plot_default_vs_classification.py`
2. Confirm:
    - Default curve matches JSON values (1.0 night).
    - GSS curve matches CSV data (~0.6 night).
    - Shading correctly highlights the gap.
