# Figure 4.1.4 Enhanced: Occupancy by Household Size (2×2 Grid)

**Goal**: Two-row figure — Row 1: occupancy curves, Row 2: bar chart metrics — both split Weekday | Weekend.

---

## Confirmed Values (from `BEM_Schedules_2025.csv`)

| HHSIZE | WD Hours | WE Hours | Daytime % | Mean Occ. |
|:------:|:--------:|:--------:|:---------:|:---------:|
| 1 (n=14) | 18.2 | 19.2 | 56.1% | 0.76 |
| 2 (n=345) | 12.9 | 13.8 | 31.6% | 1.08 |
| 3 (n=141) | 9.8 | 10.5 | 25.8% | 1.23 |
| 4 (n=93) | 7.5 | 8.5 | 16.5% | 1.25 |
| 5 (n=32) | 5.2 | 6.9 | 12.4% | 1.09 |

---

## Figure Layout (2×2 Grid)

```
┌───────────────────────────────────┬───────────────────────────────────┐
│ (a) Weekday Occupancy Curves      │ (b) Weekend Occupancy Curves      │
│  5 lines (HHSIZE 1–5) + ±1σ      │  5 lines (HHSIZE 1–5) + ±1σ      │
├───────────────────────────────────┼───────────────────────────────────┤
│ (c) Weekday Metrics               │ (d) Weekend Metrics               │
│                                   │                                   │
│  ▓▓                               │  ▓▓                               │
│  ▓▓  ▓▓                           │  ▓▓  ▓▓                           │
│  ▓▓  ▓▓  ▓▓                       │  ▓▓  ▓▓  ▓▓                       │
│  ▓▓  ▓▓  ▓▓  ▓▓                   │  ▓▓  ▓▓  ▓▓  ▓▓                  │
│  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓              │  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓             │
│  1p  2p  3p  4p  5p              │  1p  2p  3p  4p  5p              │
│                                   │                                   │
│  Left axis: Occupied Hours (bars) │  Left axis: Occupied Hours (bars) │
│  Right axis: Daytime Occ % (◆)    │  Right axis: Daytime Occ % (◆)   │
└───────────────────────────────────┴───────────────────────────────────┘
```

**Row 2 design**:
- **Bars** (left y-axis): Occupied hours per HHSIZE, colored to match Row 1 lines
- **Diamond markers** (right y-axis): Daytime occupancy % (09–17), connected by line
- X-axis: HHSIZE categories (1-person … 5-person)

---

## Script

[plot_hhsize_occupancy.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/plotting/plot_hhsize_occupancy.py)

**Output**: `eSim_occ_utils/plotting/Fig_4_1_4_HHSize_Occupancy.png`
