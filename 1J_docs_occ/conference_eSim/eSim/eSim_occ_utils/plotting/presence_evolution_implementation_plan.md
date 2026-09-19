# Presence Schedule Evolution — Comparative Plot

**Goal**: Create a publication-quality figure showing how Canadian residential presence patterns have evolved from 2005→2015→2025.

## Data Sources

| Year | File |
|------|------|
| 2005 | [BEM_Schedules_2005.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/0_BEM_Setup/BEM_Schedules_2005.csv) |
| 2015 | [BEM_Schedules_2015.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/0_BEM_Setup/BEM_Schedules_2015.csv) |
| 2025 | [BEM_Schedules_2025.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/0_BEM_Setup/BEM_Schedules_2025.csv) |

Columns used: `Hour`, `Day_Type` (Weekday/Weekend), `Occupancy_Schedule` (0–1).

---

## Proposed Changes

#### [NEW] [plot_presence_evolution.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/eSim_occ_utils/plotting/plot_presence_evolution.py)

---

## Processing Logic

### Row 1: Presence Schedules (Weekday + Weekend in Same Subplot)

One subplot per year (3 total). Each subplot:
1. Filter BEM data by year, plot **two** `sns.lineplot` curves (Weekday + Weekend).
2. Use `estimator='mean'`, `errorbar=('sd', 1)` — matching existing temporal plots.
3. Palette: `{'Weekday': 'green', 'Weekend': 'teal'}` (same as shared screenshots).
4. Y-axis: `[0, 1.05]`, X-axis: `[0, 24]` with ticks every 4 hours.

### Row 2: Summary Metrics (Dual-Axis per Year)

One subplot per year (3 total). Each subplot combines:
- **Bar chart** (left axis): Mean daily occupied hours (Weekday vs Weekend).
  - Computed as: `mean(Occupancy_Schedule) × 24` per day type.
- **Marker/annotation** (right axis or overlaid): Daytime occupancy fraction (09:00–17:00).
  - Computed as: `mean(Occupancy_Schedule)` for hours 9–16, per day type.
  - Plotted as points or annotated values on the bars.

---

## Figure Layout

```
         2005                  2015                  2025
┌──────────────────┬──────────────────┬──────────────────┐
│ (a) Presence     │ (a) Presence     │ (a) Presence     │
│  ── Weekday      │  ── Weekday      │  ── Weekday      │
│  ── Weekend      │  ── Weekend      │  ── Weekend      │
│  (mean ± sd)     │  (mean ± sd)     │  (mean ± sd)     │
├──────────────────┼──────────────────┼──────────────────┤
│ (b) Occ. Hours   │ (b) Occ. Hours   │ (b) Occ. Hours   │
│  █ WD  █ WE      │  █ WD  █ WE      │  █ WD  █ WE      │
│  + Daytime Frac. │  + Daytime Frac. │  + Daytime Frac. │
└──────────────────┴──────────────────┴──────────────────┘
```

Layout: `plt.subplots(2, 3, figsize=(20, 12))`

---

## Verification Plan

1. Run: `python3 eSim_occ_utils/plotting/plot_presence_evolution.py`
2. Visually confirm:
   - Row 1 matches the style of the shared screenshots (weekday/weekend with SD bands)
   - 2025 weekday shows elevated daytime presence vs 2005/2015
   - Row 2 bars and daytime fractions are consistent with the curves above
