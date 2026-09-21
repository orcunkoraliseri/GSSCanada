# Table 4 — Held-vs-Varied Paired Frozen-Frame Experimental Design

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 3b Steps 7–8; `08_simulation.md` §Background — experimental design

## Section A — Factors held constant

| Factor | Description |
|---|---|
| IDF geometry & envelope | Canadian NECB17/NBC936 Z6 archetype IDF (`BEM_setup/Buildings_MTL/`); held fixed across all 6 cities and all 5 cycle-years |
| TMY weather file | City-specific EPW (one per city); the same file used for every cycle-year run within a city |
| Household IDs (SIM_HH_ID) | The same N = 50 household IDs are used for all five cycle-years within each archetype × city cell; sampled once per cell from the 144,507-household frame, stratified to DTYPE × PR |
| n per cell | 50 households |

## Section B — Factors varied

| Factor | Values |
|---|---|
| Occupancy time-series | One calibrated 30-min AT_HOME + metabolic + equipment + lighting schedule per household per cycle-year (drawn from `BEM_Schedules_{year}.csv`) |
| Cycle-years | 2005 · 2010 · 2015 · 2022 (calibrated observed) · 2030 (forecast) |

**Total = 4 archetypes × 6 cities × 5 years × 50 HH = 6,000 runs**; within-HH differencing removes between-HH MC variance; cross-year Δ = purely behavioural.

**Attribution logic:** Because IDF, weather, and household IDs are all held constant across cycle-years, the within-household paired difference in energy output is attributable *solely* to the change in the predicted occupancy time-series. Building physics, climate, and stock turnover difference out.

**MC convergence:** 95% CI half-width mean 1.80%, worst cell 4.04% at N = 50 (load-shape precision, not annual-kWh precision).

---

> **Footnote:** 1 of 6,000 runs (OtherDwelling × Kelowna 5B × 2010) required a DX-coil sizing fix (Gross Rated Sensible Heat Ratio autosize → 0.75) after a deterministic EnergyPlus sizing fatal — Sub-step 8G; effect on results negligible (EUI Δ ≤ 0.013 kWh/m²).
