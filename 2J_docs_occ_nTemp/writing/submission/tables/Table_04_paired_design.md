# Table 4 — Held-vs-Varied Paired Frozen-Frame Experimental Design

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 3b Steps 7–8; `08_simulation.md` §Background — experimental design

## Section A — Factors held constant

| Factor | Description |
|---|---|
| IDF geometry & envelope | Canadian NECB17/NBC936 Z6 archetype IDF (`BEM_setup/Buildings_MTL/`); held fixed across all 6 cities and all 5 cycle-years |
| TMY weather file | City-specific EPW (one per city); the same file used for every cycle-year run within a city |
| Household IDs (SIM_HH_ID) | Two independent fixed panels, each held constant *within* its own cycle-years: (i) 2005/2010/2015 — N = 50 household IDs sampled once per cell from the original 144,507-household frame, stratified to DTYPE × PR; (ii) 2022/2030 — a *separate* N = 50 household IDs sampled once per cell from the refined 144,465-household frame (2026-07-09 region-tier relink; ~0.03% ID churn vs. the original linkage), also stratified to DTYPE × PR. Household identity is not carried across the two panels — see Attribution logic below. |
| n per cell | 50 households |

## Section B — Factors varied

| Factor | Values |
|---|---|
| Occupancy time-series | One calibrated 30-min AT_HOME + metabolic + equipment + lighting schedule per household per cycle-year (drawn from `BEM_Schedules_{year}.csv`) |
| Cycle-years | 2005 · 2010 · 2015 · 2022 (calibrated observed) · 2030 (forecast) |

**Total = 4 archetypes × 6 cities × 5 years × 50 HH = 6,000 runs**; within-HH differencing removes between-HH MC variance *within each panel*; cross-year Δ = purely behavioural for comparisons made within a panel (2005↔2010↔2015 among themselves; 2022↔2030 between themselves).

**Attribution logic:** IDF and weather are held constant across all five cycle-years; household IDs are held constant *within* each of the two panels (2005-2015; 2022-2030) but differ *between* the panels. The within-household paired difference in energy output is attributable *solely* to the change in the predicted occupancy time-series for any comparison made within a single panel — this covers the paper's primary inferential target, the 2022→2030 comparison (§5.3-§5.4), which is fully within-panel. The 2015→2022 transition in the longitudinal trajectory (Figure S8) crosses the panel boundary — it compares two independently-drawn household samples and is a cross-sectional trend, not a matched within-household difference (§7 Limitations).

**MC convergence:** 95% CI half-width mean 1.80%, worst cell 4.04% at N = 50 (load-shape precision, not annual-kWh precision).

---

> **Footnote:** 1 of 6,000 runs (OtherDwelling × Kelowna 5B × 2010) required a DX-coil sizing fix (Gross Rated Sensible Heat Ratio autosize → 0.75) after a deterministic EnergyPlus sizing fatal — Sub-step 8G; effect on results negligible (EUI Δ ≤ 0.013 kWh/m²).
