# Occupancy-Impact Energy Plotting

This merged document combines:

- `occImpactEnergyPlotting.md`
- `occImpactEnergyPlotting_tasks.md`

It preserves the design rationale, recommended plot set, implementation notes, and the task/progress log in one place.

---

## 1. Why this document exists

The current interim report (`fig1`-`fig5`, `Figure_4.3.1`-`4.3.4`) answers "how do code scenarios compare?" but only implicitly answers "what is the energy signature of our occupancy modeling?". The Default scenario uses unmodified archetype schedules, while the code-year scenarios (2005/2010/2015/2022/2025) use GSS-derived, Monte-Carlo-sampled occupancy schedules. The interesting causal question - how much of the EUI change is attributable to occupancy rather than code stringency - is never plotted directly.

The `eSim_occ_utils/plotting/BEM_*_Comparison*` family already makes this contrast on the occupancy side (presence, activity, metabolic rate). We need the energy-side counterpart: plots that take the same Default-vs-scenario lens and apply it to Heating, Cooling, Electric Equipment, and Water Systems (DHW).

Current gaps:

- No plot isolates the Default -> scenario delta per end-use. All existing plots treat Default as just another bar.
- No plot shows the coupling between occupancy-driven end-uses (Equipment, Lighting, DHW) and the thermally dependent end-uses (Heating, Cooling) - i.e. internal gains offsetting heating and adding to cooling.
- No plot reveals temporal re-shaping: whether GSS-derived schedules merely re-scale Default or genuinely change load-shape (timing of peaks, weekday/weekend spread, evening ramps).
- No plot expresses occupancy sensitivity per end-use (how much each end-use moves under occupancy modeling vs stays flat).

The ideas below are a menu, ranked in priority order. Pick 3-5 for the next report iteration rather than building all of them.

---

## 2. Tier A - High-impact, low-effort (recommended first)

### A.1 End-Use Delta Bar: (Scenario - Default)

What it shows:

- For every neighbourhood, a diverging horizontal bar per end-use showing `scenario_mean - Default_mean` (kWh/m2/yr), one colour per scenario.
- Positive bars mean occupancy modeling raised that end-use relative to the archetype default.
- Negative bars mean occupancy modeling lowered that end-use.
- Four panels: Heating, Cooling, Electric Equipment, Water Systems.

Why it works:

- Directly isolates the occupancy-modeling signal.
- Makes it visually obvious that, for example, "2025 heating is +3.1 kWh/m2/yr vs Default while cooling is -3.3 kWh/m2/yr" - the two tell a story together.

Data:

- `aggregated_eui.csv` (already generated; no SQL needed).

Sketch:

```python
delta = df[f"{sc}_mean"] - df["Default_mean"]  # per end-use
# 2x2 subplot grid: one panel per {Heating, Cooling, Electric Equipment, Water Systems}
# x-axis: scenarios; y-axis: delta EUI; facet/colour: neighbourhood
```

When to use:

- Headline plot - put it in Section 4 of the main report, alongside `fig4_improvement_vs_2005`.

### A.2 End-Use Radar Fingerprint (Default vs Scenario)

What it shows:

- Per neighbourhood, a radar/spider chart with five spokes (Heating, Cooling, Int. Lighting, Electric Equipment, Water Systems), normalized so Default = 1.0.
- One polygon per scenario.
- Radar shape shift = occupancy-driven fingerprint change.

Why it works:

- Totals can hide compensating shifts.
- If Heating goes up and Cooling goes down by the same amount, total EUI looks unchanged but the operational fingerprint has changed.
- Radar makes the shape-change legible.

Data:

- `aggregated_eui.csv`.

Sketch:

- Use `matplotlib.pyplot.subplot(projection='polar')`.
- Normalize each scenario by the Default vector before plotting.

Caveat:

- Radar is sometimes criticized for area distortion - label raw values at each vertex and keep scenarios to 2-3 per panel for readability.

### A.3 End-Use Sensitivity Tornado

What it shows:

- For each end-use, a horizontal bar whose length is `max - min` across all six scenarios (Default + 5 code years), one bar per neighbourhood.
- Long bars mean the end-use is sensitive to occupancy / code differences.
- Short bars mean the end-use is inelastic to these drivers.

Why it works:

- Ranks end-uses by responsiveness.
- Answers the reviewer question: "Which end-use should we trust the occupancy modeling to actually shift?"
- Will likely show Equipment and DHW as most sensitive, Lighting less so, and H/C somewhere in between depending on archetype.

Data:

- `aggregated_eui.csv`.

Sketch:

- Grouped horizontal bar.
- y-axis = end-use.
- colour = neighbourhood.
- value = range.
- Optionally annotate each bar with `(scenario_min, scenario_max)` labels.

### A.4 Equipment -> Cooling -> Heating Coupling Scatter

What it shows:

- Two-panel scatter.
- Left: x = Equipment EUI, y = Cooling EUI.
- Right: x = Equipment EUI, y = Heating EUI.
- One marker per (neighbourhood x scenario) pair.
- Colour by neighbourhood, shape by scenario.
- Fit a line to show the slope.

Why it works:

- Demonstrates the internal-gain coupling: as occupancy-driven equipment load rises, cooling should rise (positive slope) and heating should fall (negative slope).
- If the slopes are visible, the plot is a direct causal-chain argument for why occupancy modeling matters - the schedules are not just decorative, they change HVAC demand.

Data:

- `aggregated_eui.csv`.

Caveat:

- With 6 neighbourhoods x 6 scenarios = 36 points, this is sparse.
- Add regression line + R2 to show whether the signal is real or noise.

---

## 3. Tier B - Medium-effort, high narrative value

### B.1 Diurnal Load Shape Ribbon: Default vs Scenario

What it shows:

- Per neighbourhood, 4 panels (Winter Weekday / Winter Weekend / Summer Weekday / Summer Weekend), each showing two overlay lines: one for Default, one for the scenario of interest (for example 2025).
- Plot normalized Cooling + Equipment combined (or as two stacked ribbons) with Presence overlaid on a secondary axis.

Why it works:

- This is the direct visual equivalent of `BEM_Presence_Evolution_Comparison.png` on the energy side.
- Reviewers see the presence curve lining up (or not) with the load curve, and they see how Default's flat schedule produces a different load shape than the GSS-derived schedule.

Data:

- `eplusout.sql` (Heating:EnergyTransfer, Cooling:EnergyTransfer, Electric Equipment, Water Systems).
- Already partially extracted by `interim_report_gen.py` for Fig 4.3.3 - extend to include Equipment and DHW variables.

Sketch:

- Re-use the 4.3.3 diurnal extraction loop.
- Add `Electric Equipment:Energy` and `Water Use Equipment:Heating Energy` to the variable list.
- Pull `Zone People Occupant Count` as the presence overlay (secondary y-axis).

When to use:

- This is the "hero plot" for a journal submission - one panel per neighbourhood, appendix-caliber detail.

### B.2 Peak Load Time-Shift Diagram

What it shows:

- Scatter plot: x-axis = hour-of-day of peak Cooling (per scenario), y-axis = hour-of-day of peak Equipment, colour = scenario, marker size = peak magnitude.
- One plot per neighbourhood, or one combined plot faceted by season.

Why it works:

- Answers "Does occupancy modeling shift when peaks happen?" - critical for grid integration and demand-response studies.
- If Default peaks at 14:00 but 2025 peaks at 18:00, that's a different grid story even if total EUI is similar.

Data:

- `eplusout.sql`.
- Already have peak-timestamp extraction in `_extract_peak()` at `interim_report_gen.py:451-485` - extend to Equipment + DHW variables.

### B.3 Monthly End-Use Stack with Occupancy Modulation Overlay

What it shows:

- Per neighbourhood, stacked monthly EUI bars (Heating / Cooling / Equipment / DHW), with a line overlay of monthly mean occupancy presence on a secondary axis.
- 12 bars x 6 scenarios - pick 2 scenarios per neighbourhood (Default + 2025) to keep it readable.

Why it works:

- Shows the seasonal interaction: Equipment is nearly flat across the year, but H/C swings violently; presence modulates amplitude of that swing.
- Useful to demonstrate that occupancy matters differently in shoulder vs peak seasons.

Data:

- `eplusout.sql` (monthly aggregates from the same hourly variables).
- Add a monthly groupby on the existing extraction.

### B.4 Waterfall (Bridge) Chart: Default -> 2025 Total EUI

What it shows:

- A waterfall chart that decomposes `Total_2025 - Total_Default` into contributions from each end-use.
- Start bar = Default total.
- Step bars for each end-use delta (Equipment -X, Lighting -Y, Heating +Z, Cooling -W, DHW -V).
- End bar = 2025 total.

Why it works:

- Tells the single clearest narrative a non-technical reader can absorb: "Going from the archetype default schedule to our 2025 GSS-derived schedule costs X in heating, saves Y in cooling, saves Z in equipment - net A."

Data:

- `aggregated_eui.csv`.

Sketch:

- Manual implementation via `matplotlib` bar chart with computed `bottoms`.
- One chart per neighbourhood -> 6 panels; or a single grid chart.

---

## 4. Tier C - Exploratory, higher effort

### C.1 Occupancy-Weighted EUI ("Energy per Occupant-Hour")

What it shows:

- Re-normalize total EUI by the integrated occupant-hours implied by each scenario's schedule, producing kWh per occupant-hour rather than kWh/m2/yr.
- Bar per scenario, grouped by neighbourhood.

Why it works:

- EUI normalized by area penalizes schedules that have more people in the building (more equipment, more DHW).
- Normalizing by occupant-hours isolates schedule efficiency from schedule intensity.
- A counterintuitive result (for example the "best" scenario by EUI is actually the worst per occupant) would be a publishable finding.

Data:

- `aggregated_eui.csv` + integrated occupant-hours from the schedule CSVs or `Zone People Occupant Count` from SQL.

Caveat:

- Requires a clean definition of "occupant-hour".
- Be explicit about whether it's sum across zones, building total, or per-unit.

### C.2 2D Joint Histogram: Presence x Hourly Load

What it shows:

- For each scenario, a 2D histogram (heatmap) with x = number of occupants present (or normalized presence), y = Electric Equipment instantaneous load (kW).
- The slope of the density ridge tells you the occupancy-to-load gain factor under that schedule.

Why it works:

- Visual test of the assumption that equipment schedules scale linearly with occupancy.
- Deviations from linearity (saturation, thresholding) would show up as curved or capped distributions.
- Useful validation of the schedule generation logic.

Data:

- `eplusout.sql` (30-min or 60-min resolution, full year).

### C.3 Occupancy-Correlated vs Envelope-Driven EUI Partition

What it shows:

- Split each end-use's EUI into an occupancy-correlated portion and an envelope-driven portion via regression against presence timeseries.
- Stacked bar per scenario shows the partition.

Why it works:

- The cleanest attribution story: "Of the 37 kWh/m2/yr of heating, 8 is directly modulated by occupancy (via internal gains and DHW draw) and 29 is weather-driven."
- Enables a "what if occupancy modeling were perfect" upper-bound argument.

Data:

- `eplusout.sql` (hourly H/C, presence, equipment) + a regression layer.

Effort:

- Non-trivial - this crosses into attribution modeling, not just plotting.

### C.4 Default-vs-Scenario H/C Spaghetti

What it shows:

- Direct energy-side analog of `BEM_Temporal_Spaghetti_Comparison.png`.
- For each day of the year, plot the 24-hour Heating (or Cooling) profile as a thin line.
- Two overlapping spaghetti clouds: one for Default (grey), one for 2025 (blue).
- Median lines bold.

Why it works:

- Communicates the variance envelope introduced by occupancy modeling - Default's single-schedule cloud is narrow, the GSS-derived cloud is wider and bimodal (weekday vs weekend).
- Visually striking.

Data:

- `eplusout.sql`.
- Uses the same hourly extraction as 4.3.3 but aggregated differently.

Caveat:

- Very data-dense - one plot per neighbourhood, and even then cluttered.
- Consider limiting to a single season.

### C.5 Weekday vs Weekend End-Use Delta

What it shows:

- Per end-use, a bar chart of `(weekend_mean - weekday_mean)`.
- If occupancy modeling is doing its job, the weekend-weekday gap should be larger for GSS-derived scenarios than for Default.

Why it works:

- Default schedules are often identical on weekdays and weekends or use a simplified ratio.
- GSS-derived schedules encode genuine behavioral difference.
- This plot makes that difference quantitative.

Data:

- `eplusout.sql` with DayType filter (already used in 4.3.3 block).

---

## 5. Recommended package for the next report iteration

If you only implement three, implement these:

1. A.1 - End-Use Delta Bar (Scenario - Default). Direct, cheap, and the headline message.
2. A.3 - End-Use Sensitivity Tornado. Answers the "which end-uses actually move?" question cleanly.
3. B.1 - Diurnal Load Shape Ribbon. The one plot that connects the occupancy-side figures you already have to energy, panel-for-panel.

If you have room for five, add:

4. A.4 - Equipment -> Cooling/Heating Coupling Scatter (argues the causal mechanism).
5. B.4 - Waterfall Chart (a single panel that non-technical readers can read in 10 seconds).

---

## 6. Implementation notes

- All Tier A plots can be added to `interim_report_gen.py` as additional figure blocks below the existing `Figure_4.3.4` block. No new data extraction - everything is in `aggregated_eui.csv`.
- Tier B plots B.1-B.3 require extending the existing SQL extraction (`_extract_diurnal`, `_extract_peak`) to include `Electric Equipment:Energy`, `Water Use Equipment:Heating Energy`, and `Zone People Occupant Count`. The Parquet cache layer (`_sql_cache/`) will handle warm re-runs.
- Tier B plot B.4 (Waterfall) is pure `aggregated_eui.csv` work.
- Tier C plots require new data products (occupant-hours integration, regression attribution) and should be scoped as separate tasks, not bundled with the interim report refresh.
- Keep the colour convention consistent with existing plots: Heating `#d62728`, Cooling `#1f77b4`, Default grey `#7f7f7f` or black.
- Use `alpha=0.6-0.85` on bars and thicker 2.0-2.5 linewidths on Default reference lines (same convention as Figure 4.3.3 in `interim_report_gen.py:408-413`).
- For all new figures, save to `BatchAll_MC_N3_*/interim_report/` with filename prefix `Figure_Occ_*` to distinguish from the existing `fig*` and `Figure_4.3.*` families.

---

## 7. Resolved design decisions

These were previously open questions; each has been answered so downstream tasks can proceed without re-asking.

### 7.1 Counterfactual choice

Decision:

- Use Default as the primary counterfactual for all delta / ribbon / waterfall plots.
- Do not build a separate "schedule-only" counterfactual for this iteration.

Reasoning:

- Default is the only baseline that exists natively in every batch run with no extra simulation cost.
- The GSS-derived scenarios (2005-2025) differ from Default in schedule shape and potentially in a handful of archetype fields (lighting/equipment W/m2, occupant density).
- For the interim report the schedule-shape signal dominates the delta, and any residual archetype-field contribution is a known minor caveat rather than a confound worth solving before N >= 20 runs.

How to apply:

- Every delta plot caption must carry a short disclaimer:

> Default-scenario deltas reflect the combined effect of occupancy schedule shape and any archetype-field differences between the Default IDF and GSS-derived IDFs. The schedule-shape signal is expected to dominate; see Section 7.1 of `occImpactEnergyPlotting.md`.

- A secondary "schedule-only" counterfactual (identical IDFs, swap only `People`/`ElectricEquipment`/`Lights`/`WaterEquipment` schedules) is deferred as future work, not a blocker.

### 7.2 Presence timeseries availability

Checked:

- `BEM_Setup/SimResults/BatchAll_MC_N3_1776120359/_sql_cache/` currently holds only `diurnal_*.parquet` (Heating + Cooling) and `peak_*.json`.
- No presence, equipment, lights, or DHW timeseries are cached.

But the raw signal is present in every `eplusout.sql`:

| Variable | Reporting Frequency | Use |
|---|---|---|
| `Zone People Total Heating Energy` | Hourly, per zone (48 zones in RC1) | Presence/activity proxy - zero when empty, scales with count x metabolic |
| `InteriorEquipment:Electricity` | Hourly, building-level | Equipment load |
| `InteriorLights:Electricity` | Hourly, building-level | Lighting load |
| `WaterSystems:EnergyTransfer` | Hourly, building-level | DHW energy |
| `Water Use Equipment Heating Energy` | Hourly, per fixture | DHW (finer-grain alternative) |

How to apply:

- Extend `_extract_diurnal()` in `interim_report_gen.py:333-369` to pull the four building-level variables and a summed presence signal (aggregate `Zone People Total Heating Energy` across all zones).
- Cache under a new filename prefix (for example `occdiurnal_*.parquet`) so the existing H/C cache is not invalidated.

Note:

- `Zone People Occupant Count` is not in the current output set.
- If a true headcount is needed later, `Output:Variable,*,Zone People Occupant Count,Hourly;` must be added to the IDF generator.
- For now, `Zone People Total Heating Energy` is an acceptable presence/activity proxy and actually carries richer behavioural signal than raw count.

### 7.3 Monte-Carlo N sizing

Decision:

- N=3 is the fundamentals phase.
- The production N=20+ run will happen on cloud after these plots are implemented and validated.
- Plot titles and captions should indicate `(N=3)` but not carry "preliminary" warnings - the plotting code is the deliverable at this stage, not the final numbers.

How to apply:

- Hard-code scenario colour/line styles so the exact same script re-runs cleanly under any N.
- Use `aggregated_eui.csv` std columns for error bars and let them widen or tighten naturally as N grows.
- Do not add any N-dependent branching.

---

## 8. Occupancy-Impact Energy Plotting - Task List and Progress Log

**Companion to:** [`occImpactEnergyPlotting.md`](occImpactEnergyPlotting.md) and the design sections above.

**Target generator:** `interim_report_gen.py`

**Target batch:** `BEM_Setup/SimResults/BatchAll_MC_N3_1776120359/`

**Output directory:** `BatchAll_MC_N3_1776120359/interim_report/`

**Filename prefix for new figures:** `Figure_Occ_*`

**Created:** 2026-04-16

### Aim

Extend `interim_report_gen.py` so that, after the existing `fig1`-`fig5` and `Figure_4.3.1`-`Figure_4.3.4` blocks, it emits a second family of occupancy-impact figures (`Figure_Occ_*`) that directly answer "what changes in energy demand when we swap the Default archetype schedule for a GSS-derived, Monte-Carlo-sampled occupancy schedule?". Final deliverable is a single re-run of `interim_report_gen.py` against `BatchAll_MC_N3_1776120359/` that produces the full refreshed report.

Tasks are ordered so that every task leaves the script in a runnable state. Tasks 1-2 are CSV-only, Task 3 adds a cached SQL extraction that later tasks reuse, and Tasks 4-7 are additive figure blocks on top of Task 3.

### Task 1 - Tier A bundle: CSV-only delta, tornado, coupling, waterfall

Aim:

- Land the four quickest, highest-impact plots - all readable from `aggregated_eui.csv` alone, no SQL work, no new extraction layer.

Plots in this bundle:

- `Figure_Occ_A1_EndUse_Delta.png` - A.1 End-Use Delta Bar `(scenario - Default)`
- `Figure_Occ_A3_Sensitivity_Tornado.png` - A.3 End-Use Sensitivity Tornado
- `Figure_Occ_A4_Coupling_Scatter.png` - A.4 Equipment -> Heating/Cooling Coupling Scatter
- `Figure_Occ_B4_Waterfall.png` - B.4 Default -> 2025 Waterfall

Steps:

1. In `interim_report_gen.py`, after the `Figure_4.3.4` block (around line 564), add a new section header comment: `# -- Occupancy-Impact Figures (Tier A) --`.
2. Implement A.1: for each of the four end-uses (`Heating`, `Cooling`, `Electric Equipment`, `Water Systems`), build a grouped-bar subplot with x = scenario (excluding Default), y = `scenario_mean - Default_mean`, one bar per neighbourhood; use the existing `colors` palette; add a zero reference line.
3. Implement A.3: 2x2 or 1x4 subplot grid, one panel per end-use, horizontal bars showing `max_over_scenarios - min_over_scenarios` per neighbourhood. Annotate each bar with `(min scenario -> max scenario)` labels.
4. Implement A.4: two-panel scatter. Left panel x = Equipment EUI, y = Cooling EUI. Right panel x = Equipment EUI, y = Heating EUI. Marker colour by neighbourhood, marker shape by scenario (use `['o','s','^','D','v','*']`). Add `numpy.polyfit` linear regression line + R2 annotation per panel.
5. Implement B.4: one 2x3 subplot grid (one panel per neighbourhood). Each panel is a waterfall with bars at `Default_total`, then stepwise `delta_end_use` for each end-use, ending at `2025_total`. Use green for negative deltas (energy reduction), red for positive.
6. Save all four PNGs to `OUT` (`interim_report/`) at dpi=150; append their filenames to the `interim_summary.txt` figure list at the bottom of the script.
7. Add the disclaimer from Section 7.1 of `occImpactEnergyPlotting.md` to the super-title of A.1 and B.4 (short form: "Default-scenario delta includes schedule + archetype-field effects").

Expected result:

- 4 new PNGs in `interim_report/`.
- Cold run time increase < 5 s (pure pandas/matplotlib, no SQL).
- `interim_summary.txt` lists all new filenames.

Test method:

- Run `py interim_report_gen.py` against `BatchAll_MC_N3_1776120359/`.
- Confirm 4 new PNGs exist.
- Visually sanity-check: A.1 shows non-zero deltas for Equipment and H/C; A.4 coupling shows the expected positive slope for Equipment->Cooling; B.4 waterfall bars sum to the total delta.

### Task 2 - Radar fingerprint (A.2)

Aim:

- Add the polar-projection radar chart showing end-use fingerprint shape change per scenario, normalized to Default.

Plot:

- `Figure_Occ_A2_Radar_Fingerprint.png`

Steps:

1. After the Task 1 block, add a `# -- Figure_Occ_A2: Radar fingerprint --` section.
2. Use `plt.subplots(2, 3, subplot_kw={'projection': 'polar'}, figsize=(18, 12))` - one polar subplot per neighbourhood.
3. For each neighbourhood, compute `ratio = scenario_mean / Default_mean` per end-use (5 spokes). Close the polygon by appending the first value. Plot Default as a dotted circle at radius 1.0, and 2005/2015/2025 as three coloured polygons. Omit 2010/2022 to keep the radar readable.
4. Annotate each spoke with the end-use name and the Default absolute value in kWh/m2/yr (small text at the spoke tip).
5. Set `ax.set_ylim(0.7, 1.3)` initially; adjust per-panel if any end-use ratio falls outside.

Expected result:

- Single PNG showing 6 radar panels.
- Scenarios with flat fingerprint (for example RC4-RC6) will show polygons close to the Default circle; scenarios with strong re-shaping (for example RC1) will show visible distortion.

Test method:

- Visual only - confirm polygons are visible, spokes labelled, no overflow.
- Compare one spoke's annotated value against `aggregated_eui.csv` to verify normalization.

### Task 3 - Extend SQL extraction: Equipment / Lights / DHW / Presence

Aim:

- Unblock Tasks 4-7 by adding a cached SQL extraction layer for the four occupancy-driven signals.
- Do not touch the existing `_extract_diurnal` / `_extract_peak` caches - add a new extraction function with a new cache filename prefix.

Steps:

1. Add a new helper `_extract_occ_signals(sql_path, neighbourhood=None)` below `_extract_peak()` (around line 485). Variable dictionary to query:

```python
occ_vars = {
    'People':     'Zone People Total Heating Energy',      # hourly, per zone -> SUM across zones
    'Equipment':  'InteriorEquipment:Electricity',          # hourly, building
    'Lights':     'InteriorLights:Electricity',             # hourly, building
    'DHW':        'WaterSystems:EnergyTransfer',            # hourly, building
}
```

2. For the `People` variable, aggregate by `TimeIndex` with `SUM(Value)` across all zones so one scalar presence/activity value per hour is returned.
3. Return a DataFrame with columns `[Month, Day, Hour, DayType, People, Equipment, Lights, DHW]`, converting joules to `W/m2` using the existing `_get_area()` helper (divide by 3600 and by conditioned area). For `People`, divide by area to get `W/m2` of internal metabolic gain.
4. Wire caching: cache path `os.path.join(CACHE, f"occdiurnal_{n}_{sc}.parquet")` - different prefix from the existing `diurnal_` cache. Reuse `_cache_fresh()`.
5. In the main loop (around line 373), add a parallel collection loop that calls `_extract_occ_signals` for every `(n, sc)` pair and collects into `collected_occ`. This loop can coexist with the existing `collected_433` loop; do not merge them.
6. Log one line per skipped scenario so missing variables are visible.

Expected result:

- On cold run, `_sql_cache/` gains 36 new `occdiurnal_*.parquet` files (6 neighbourhoods x 6 scenarios).
- Warm re-runs near-instant.
- `collected_occ` DataFrame ready for Tasks 4-7.

Test method:

- Cold run: confirm new parquet files written, row count approximately 8760 per file (hourly annual).
- Load one parquet manually and check that `People`, `Equipment`, `Lights`, `DHW` columns are non-zero and physically plausible (Equipment ~2-10 W/m2, People ~0-5 W/m2 peak).
- Warm run: confirm no re-extraction (print statements fire the `_cache_fresh` branch).

### Task 4 - Diurnal Load Shape Ribbon (B.1)

Aim:

- The hero plot - direct energy-side twin of `BEM_Presence_Evolution_Comparison.png`.
- Shows diurnal load shape under Default vs 2025, with presence overlaid.

Plot:

- `Figure_Occ_B1_Diurnal_Ribbon.png` (one multi-panel grid) or `Figure_Occ_B1_Diurnal_Ribbon_{neighbourhood}.png` (one per nhood).

Steps:

1. After Task 3, add block `# -- Figure_Occ_B1: Diurnal load shape ribbon --`.
2. Reuse the Task-3 collected data; filter to January (`Month==1`) and July (`Month==7`), map DayType to `Weekday`/`Weekend` using the same helper as the 4.3.3 block.
3. For each neighbourhood, create a 1x4 subplot (Winter Weekday / Winter Weekend / Summer Weekday / Summer Weekend). On each panel:
   - Stacked ribbon (fill_between) of `Cooling` (blue) + `Equipment` (orange) for Default and for 2025, side by side or with alpha so both are visible.
   - Line overlay of the summed presence signal (`People` W/m2) on a secondary axis (`ax.twinx()`), one line for Default (grey dotted) and one for 2025 (black solid).
4. Use `wid_433` / `sty_433` / `clr_433` palette conventions from the existing 4.3.3 block for consistency.
5. If per-neighbourhood grids are too busy, emit one PNG per neighbourhood (6 files) instead of a single mega-figure.

Expected result:

- 1 or 6 PNG(s) clearly showing that Default has a flatter equipment/cooling curve with symmetric weekday/weekend, while 2025 shows behavioural peaks (morning ramp, evening peak) and a wider weekday/weekend spread.

Test method:

- Visual - the presence overlay for 2025 should show a clear weekday morning+evening double-peak while Default is flat.
- If the 2025 curve looks flat too, either the extraction is wrong or the schedule work is not yet discriminating - either way, a signal worth catching.

### Task 5 - Peak load time-shift diagram (B.2)

Aim:

- Show whether occupancy modeling shifts the hour-of-day at which peaks occur for Cooling, Equipment, and DHW.

Plot:

- `Figure_Occ_B2_Peak_TimeShift.png`

Steps:

1. Extend the existing `_extract_peak()` at line 451 with two additional variable pairs: `Equipment` (`InteriorEquipment:Electricity`) and `DHW` (`WaterSystems:EnergyTransfer`). Keep the existing Heating/Cooling extraction.
2. Cache additions: new JSON key `peak_occ_{n}_{sc}.json` to avoid invalidating existing `peak_*.json`.
3. After Task 4, add block `# -- Figure_Occ_B2: Peak time-shift --`.
4. For each neighbourhood, produce a scatter with x = peak hour of Cooling, y = peak hour of Equipment. Colour = scenario. Marker size scaled to peak magnitude. Add a diagonal `y=x` reference line.
5. Optionally include a second panel with x = peak hour of Equipment, y = peak hour of DHW.

Expected result:

- Single PNG showing 6 nhood panels.
- Default clusters at one `(x, y)` location.
- 2025 points scatter around it, revealing how the GSS-derived schedule shifts peak timing.

Test method:

- Visual plus numerical spot-check: for RC1, print peak-hour tuples per scenario to console; confirm they align with the scatter markers.

### Task 6 - Monthly end-use stack with presence overlay (B.3)

Aim:

- Show the seasonal interaction between occupancy-driven and weather-driven end-uses.

Plot:

- `Figure_Occ_B3_Monthly_Stack.png`

Steps:

1. Add a monthly aggregation on top of Task 3's extraction: `groupby(['Scenario', 'Month']).sum()` for Heating/Cooling/Equipment/Lights/DHW.
2. For each neighbourhood, produce a 1x2 subplot: left = Default monthly stacked bars; right = 2025 monthly stacked bars. Same y-axis for comparison.
3. Overlay a line of monthly total presence (sum of `People` aggregated to monthly) on a secondary axis.

Expected result:

- Single PNG with 6 nhoods x 2 panels = 12 subplots.
- Seasonal swing of H/C should be clearly visible.
- Equipment/Lights/DHW largely flat.
- Presence line shows whether monthly-mean presence itself moves (it should be roughly flat - humans do not vanish in July).

Test method:

- Sum of monthly bars should equal annual EUI from `aggregated_eui.csv` within rounding.
- Confirm for one nhood+scenario.

### Task 7 - Weekday vs Weekend End-Use Delta (C.5)

Aim:

- Quantitative check that GSS-derived schedules encode a larger weekday/weekend difference than Default does.

Plot:

- `Figure_Occ_C5_WeekdayWeekend_Delta.png`

Steps:

1. On Task 3's data, compute `daily_mean_per_daycat` for each `(Scenario, DayCat)`. Compute `delta = weekend_mean - weekday_mean` per end-use.
2. Grouped bar chart: one panel per end-use, x = scenario, y = delta, colour = neighbourhood.

Expected result:

- Single PNG with 4 or 5 panels (one per end-use).
- Default bars should be near zero or flat.
- 2005-2025 bars should show a non-zero, consistent sign (probably negative for Equipment - less on weekends is unusual, but the GSS profile for residential may show more weekend usage).

Test method:

- Visual.
- If Default bars are not flat, worth investigating whether archetype schedules already encode a weekday/weekend distinction.

### Task 8 - Final regeneration for `BatchAll_MC_N3_1776120359`

Aim:

- Single clean re-run of the fully updated `interim_report_gen.py` against the target batch, producing all existing + all new figures in one shot.
- Update the figures companion document so every new `Figure_Occ_*` PNG is listed.

Steps:

1. Verify environment: `py -c "import pandas, matplotlib, numpy, pyarrow; print('ok')"`. Install `pyarrow` if missing.
2. Delete nothing. Leave `_sql_cache/` in place - warm cache for H/C diurnal + peak stays valid; only new `occdiurnal_*.parquet` and `peak_occ_*.json` will be written this run.
3. From repo root, run:

```bash
ESIM_BATCH_DIR="C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults\BatchAll_MC_N3_1776120359" py interim_report_gen.py
```

(On Windows bash, use forward slashes or set the env var separately.)

4. Confirm stdout lists every expected `done` line: `fig1`-`fig5`, `Figure 4.3.1`-`4.3.4`, and the new `Figure_Occ_*` entries from Tasks 1-7.
5. Inventory `interim_report/`:
   - Existing: `fig1_total_eui_by_scenario.png`, `fig2_stacked_enduse.png`, `fig3_heating_cooling.png`, `fig4_improvement_vs_2005.png`, `fig5_heatmap.png`, `Figure_4.3.1_Energy_Demand.png`, `Figure_4.3.2_Temporal_Trend.png`, `Figure_4.3.3_Diurnal_Profiles.png`, `Figure_4.3.4_Peak_Loads.png`.
   - New: `Figure_Occ_A1_EndUse_Delta.png`, `Figure_Occ_A2_Radar_Fingerprint.png`, `Figure_Occ_A3_Sensitivity_Tornado.png`, `Figure_Occ_A4_Coupling_Scatter.png`, `Figure_Occ_B1_Diurnal_Ribbon*.png`, `Figure_Occ_B2_Peak_TimeShift.png`, `Figure_Occ_B3_Monthly_Stack.png`, `Figure_Occ_B4_Waterfall.png`, `Figure_Occ_C5_WeekdayWeekend_Delta.png`.
6. Open 2-3 new figures visually; flag any rendering issues (overlap, clipped labels, bad axis ranges) as a post-run fix list.
7. Update `eSim_docs_report/DONE_report_opt7_iter3_figures.md`: add a new section `## 5. Occupancy-Impact Figures (Figure_Occ_*)` listing each new filename, its generator task, and a one-line description. Update the Progress Log at the bottom of both `DONE_report_opt7_iter3.md` and the figures companion with the regeneration date and a one-line summary.
8. Update this document's Progress Log (below) with the final run timestamp, figure count, and any fix-list items.

Expected result:

- `interim_report/` contains all pre-existing figures (unchanged) plus 8-14 new `Figure_Occ_*` PNGs.
- `interim_summary.txt` lists all of them.
- Figures companion doc reflects the new figure family.
- No change to Sim_plots/ copying behaviour.

Test method:

- Stdout check: grep the run log for the string `done` and confirm count matches the expected figure total.
- File count: `ls "$BATCH/interim_report/" | wc -l` should be at least 18 PNGs + 1 txt.
- Smoke check: each Figure_Occ_* PNG file size > 50 KB (catches empty/broken saves).
- Documentation check: every new PNG has a row in the figures companion doc.

### How to work through this list

- Do not batch all tasks into one commit. Tasks 1, 2, 3 should each be a separate checkpoint because Task 3 is a cache-schema change that downstream tasks depend on.
- Do not modify the existing `fig1`-`fig5` or `Figure_4.3.*` blocks. All new code goes below `Figure_4.3.4` in `interim_report_gen.py`.
- Use the same colour palette as the existing blocks (Heating `#d62728`, Cooling `#1f77b4`, Default grey `#7f7f7f`, scenario palette from `colors` at line 30 of `interim_report_gen.py`).
- Keep caption disclaimers short but present - every delta plot needs the counterfactual caveat from Section 7.1 of `occImpactEnergyPlotting.md`.
- Cache keys must not collide. New caches use prefix `occdiurnal_*` and `peak_occ_*`; never overwrite the existing `diurnal_*` or `peak_*` entries.
- Fail gracefully. If a SQL variable is missing for one `(n, sc)` pair, skip with a log line; do not abort the whole figure.

### Progress Log

| Date | Event |
|---|---|
| 2026-04-16 | Document created alongside `occImpactEnergyPlotting.md`. Task list defined (8 tasks). No code changes yet. Counterfactual, presence-cache, and N=3 decisions resolved in `occImpactEnergyPlotting.md` Section 7. |
| 2026-04-16 | **Task 1 DONE** - Added `# -- Occupancy-Impact Figures (Tier A) --` block at `interim_report_gen.py:566-762`. Emits `Figure_Occ_A1_EndUse_Delta.png` (lines 574-609), `Figure_Occ_A3_Sensitivity_Tornado.png` (611-651), `Figure_Occ_A4_Coupling_Scatter.png` (653-698), `Figure_Occ_B4_Waterfall.png` (700-762). All 4 PNGs verified in `interim_report/` (112-148 KB). Disclaimer from Section 7.1 included in A1 and B4 super-titles. |
| 2026-04-16 | **Task 2 DONE** - Added `# -- Figure_Occ_A2: Radar fingerprint --` block at `interim_report_gen.py:764-816`. Emits `Figure_Occ_A2_Radar_Fingerprint.png` (646 KB). Polar subplots 2x3, 5 spokes, Default dotted circle + 2005/2015/2025 polygons, per-panel ylim auto-adjusted from ratio range. |
| 2026-04-16 | **Task 7 SKIPPED** - `aggregated_eui.csv` has no weekday/weekend split (schema: EndUse, sc_mean, sc_std only; no DayType column). `Figure_Occ_C5_WkWe_Delta.png` cannot be produced from CSV alone. Implement after Task 3 adds SQL extraction with DayType. Skip noted at `interim_report_gen.py:818-822`. |
| 2026-04-16 | **Task 3 DONE** - Added `_extract_occ_signals()` at `interim_report_gen.py:487-551`. Queries 5 building-level meters (`InteriorEquipment:Electricity`, `InteriorLights:Electricity`, `WaterSystems:EnergyTransfer`, `Heating:EnergyTransfer`, `Cooling:EnergyTransfer`) plus `Zone People Total Heating Energy` (SUM across zones). Added Task 3 collection loop at lines 632-679; cache prefix `occdiurnal_*` (new, no collision with `diurnal_*`). Cold run populated 36 parquet files (about 84-168 KB each) under `_sql_cache/`. Spot-check of `occdiurnal_NUS_RC1_2025.parquet`: 8772 rows, columns [Month, Day, Hour, DayType, People, Equipment, Lights, DHW, Heating, Cooling], Equipment mean 5.6 W/m2, People max 3.3 W/m2 - physically plausible. `grp_occ` shape: (3408, 11). Warm run: 11 s. |
| 2026-04-16 | **Task 4 DONE** - Added `# -- Figure_Occ_B1: Diurnal load shape ribbon --` block at `interim_report_gen.py:938-1020`. Design choice: 6 separate PNGs (one per neighbourhood, 1x4 grid: Winter WD / Winter WE / Summer WD / Summer WE). Rationale: a single 24-subplot combined grid would be too dense for the report; per-neighbourhood files match the 4.3.3 style and are independently citable. Stacked fill_between: Equipment (orange, `#ff7f0e`) base + Cooling (blue, `#1f77b4`) on top; Default alpha=0.25, 2025 alpha=0.55. Presence overlay on twinx (grey dotted = Default, black solid = 2025). Emits `Figure_Occ_B1_Diurnal_Ribbon_{NUS_RC1-RC6}.png` (286-340 KB each). All 6 PNGs verified `done` in stdout. |
| 2026-04-16 | **Task 5 DONE** - Added `_extract_peak_occ()` (new function, does not modify `_extract_peak()`). Queries Heating/Cooling via zone-SUM approach (same as `_extract_peak`); Equipment (`InteriorEquipment:Electricity`) and DHW (`WaterSystems:EnergyTransfer`) as building-level meters. Returns `{key: {peak_Wm2, peak_hour}}` where `peak_hour` is 0-based. Cache prefix `peak_occ_*` (36 new JSON files under `_sql_cache/`, no collision with `peak_*`). `Figure_Occ_B2_Peak_TimeShift.png` (143 KB): 2x3 grid, one panel per neighbourhood, scatter x=peak Cooling hour (0-23) vs y=peak Equipment hour (0-23), colour=scenario, size proportional to peak Cooling W/m2. y=x diagonal reference line. Spot-check NUS_RC1 2025: Heating 9h, Cooling 13h, Equipment 17h, DHW 6h - all physically plausible. Equipment vs DHW optional panel omitted (documented here). |
| 2026-04-16 | **Task 6 DONE** - Monthly end-use stack uses `collected_occ` (already in memory from Task 3; all 12 months). Groupby `['Neighbourhood','Scenario','Month']` sum, /1000 to convert Wh/m2 -> kWh/m2. No new SQL extraction needed. `Figure_Occ_B3_Monthly_Stack.png` (557 KB): 6x2 grid (rows=neighbourhoods, cols=[Default, 2025]). Stacked bars H/C/Equipment/Lights/DHW with end-use colour palette. twinx People heat-gain proxy line (black circles). Y-axes aligned per row (Default vs 2025 share same scale). Warm run: fast (no SQL, pure pandas groupby from cached parquets). |
| 2026-04-16 | **Task 7 IMPLEMENTED** (as part of Task 8) - `Figure_Occ_C5_WeekdayWeekend_Delta.png` (109 KB): replaced SKIP block with actual implementation using `grp_occ` (DayCat now available from Task 3 SQL). Groupby `['Neighbourhood','Scenario','DayCat']` mean across hours+seasons -> subtraction (Weekend - Weekday). 1x5 panel, one per end-use, x=scenario, y=delta W/m2, colour=neighbourhood. |
| 2026-04-16 | **Task 8 DONE** - Final clean run completed (warm, 16 s, exit 0). `interim_report/` inventory: 23 PNGs + `interim_summary.txt` (24 files total). All Figure_Occ_* files > 68 KB (smoke check passed). `DONE_report_opt7_iter3_figures.md` updated with Section 5 (14-row table, one row per Figure_Occ_* PNG) and new Progress Log entry. Task document closed. |

