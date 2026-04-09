# O1 — Publishable Artifacts: Sketches

**SWOT Item:** O1 — The pipeline produces at least 5 publishable artifacts  
**Task:** TASK 6 in `00_SWOT_pipeline.md`  
**Date:** 2026-04-09  
**Nature:** Planning only. No code, no data, no file edits.

---

## Overview

Five artifacts emerge from the pipeline. They are ordered here by publishability
confidence — i.e., how much of the supporting computation already exists or is
nearly done, regardless of research novelty.

| # | Artifact | Computation state | Standalone? |
|---|----------|-------------------|-------------|
| 1 | DRIFT_MATRIX longitudinal shift | Steps 1–3 done; matrix computation is Step 6 output | Yes |
| 3 | COVID drift quantification | Subset of Artifact 1; data already in hand | Yes — short paper or eSim extended abstract |
| 2 | 30-min downsampling note | Requires one holdout experiment pre-Step 4 | Yes — methods note |
| 4 | Synthetic co-presence schedules | Requires Steps 4–7 | Only with Artifact 5 scaffolding |
| 5 | Progressive fine-tuning recipe | Requires Steps 4–6 | Yes — methodology paper |

---

## Artifact 1 — DRIFT_MATRIX: Longitudinal Canadian Time-Use Shift

### Novel claim
Canadian residential time-use behavior shifted measurably across three GSS
cycles in demographically stratified patterns that are invisible in aggregate
statistics — quantified here for the first time using Jensen-Shannon divergence
at the activity × demographic-stratum level.

### Target venue
*eSim 2026* (primary). If expanded: *Energy and Buildings* or *Building and
Environment* as a data/methods article.

### Figure ideas

**Figure A — Three transition heatmaps (one per shift: 2005→2010, 2010→2015, 2015→2022)**
- Rows: 14 activity categories (Sleep, Work, Passive Leisure, …)
- Columns: 6–8 demographic strata (Employed Weekday, Employed Weekend,
  Not-in-LF Weekday, Not-in-LF Weekend, …)
- Color: JS divergence (0 = no change, warm = large shift)
- Annotation: top-3 cells per heatmap circled
- Layout: 3 panels side by side; same color scale for direct comparison
- Key visual claim: the 2015→2022 panel is systematically hotter than
  2005→2010 and 2010→2015, making the COVID transition visually self-evident

**Figure B — Top-10 activity × stratum combinations (summary bar chart)**
- Horizontal bars ranked by JS divergence, pooled across all three transitions
- Color-coded by which transition drove the shift
- Doubles as the paper's "what changed most" executive summary

### What it requires to produce
`DRIFT_MATRIX_0510.csv`, `DRIFT_MATRIX_1015.csv`, `DRIFT_MATRIX_1522.csv` —
computed in Step 6 from the augmented synthetic population. Figures A and B
are then straightforward `seaborn.heatmap` + `matplotlib.barh` plots.

---

## Artifact 2 — Resolution Note: 30-min is Sufficient for BEM

### Novel claim
Downsampling HETUS time-use diaries from 10-minute to 30-minute resolution
before Transformer training reduces attention compute by ~9× with no
statistically detectable loss in BEM-relevant schedule fidelity — providing a
principled, use-case-specific justification for a resolution choice that most
studies make implicitly.

### Target venue
Short methods note at *eSim 2026*, or a paragraph in the methods section of
the main paper. Could stand alone as a 4-page conference paper if the
experiment is clean.

### Figure ideas

**Figure A — Resolution vs. information-loss trade-off curve**
- X-axis: resolution (10 min, 15 min, 20 min, 30 min, 60 min)
- Y-axis left: JS divergence between original and resampled AT_HOME schedule
  (measured on a held-out 10% of respondents)
- Y-axis right: attention FLOPs (quadratic in sequence length, so 10×
  decrease in sequence length → 100× decrease in attention cost)
- Two curves on one plot with dual y-axes; vertical dashed line at 30 min
- Key visual: the FLOPs curve drops steeply while JS stays flat until ~60 min

**Figure B — Example schedule comparison (one respondent)**
- Side-by-side 48-slot bar charts: original 144-slot (10 min) and downsampled
  48-slot (30 min) for the same respondent
- Show that block structure is preserved; only within-slot micro-transitions
  are lost
- Best used as a supplementary panel to make the argument concrete

### What it requires to produce
One lightweight experiment: downsample the existing `hetus_30min.csv` back to
60-min and back up from 10-min reference, compute JS divergence at each
resolution on the held-out 10% of `merged_episodes.csv`. Can be run in
< 30 minutes on a laptop; no HPC needed. Can be done before Step 4 starts.

---

## Artifact 3 — COVID Drift: AT_HOME Rate and Activity-Share Shift 2015→2022

### Novel claim
The 2015→2022 Canadian GSS time-use transition captures a 6.2 percentage-point
increase in residential at-home time (66.1% → 72.3%), driven primarily by Work
and Passive Leisure activity shifts — providing a time-use-survey-based
quantification of COVID-era behavioral change that is independent of building
meter data or smartphone tracking.

### Target venue
*eSim 2026* as a standalone result section, or as a letter/short communication
to *Energy Research & Social Science* or *Applied Energy*. High topical demand
through 2026.

### Figure ideas

**Figure A — Stacked activity-share bar chart: 2015 vs. 2022**
- Two vertical stacked bars (one per cycle), 14 activity categories color-coded
- The shift in AT_HOME occupancy (63.5% → 72.3%) visible as a border line
  across both bars — or plotted as a separate inset
- Annotation: delta labels on the 3–4 activities that shifted most (Work ↓,
  Passive Leisure ↑, Social ↓)
- Clean, conference-slide-friendly design

**Figure B — Per-stratum COVID lift (EMPLOYED WEEKDAY highlighted)**
- Small multiples: one bar pair (2015 / 2022) per LFTAG × DDAY_STRATA cell
- Employed Weekday is the cell where the shift is sharpest (WFH signature)
- Unemployed and Not-in-LF shown for contrast — smaller or opposite shifts
- Visual argument: the COVID AT_HOME lift is not uniform; it is concentrated
  in the working-hours stratum, consistent with remote work as the mechanism

### What it requires to produce
Already in hand from Tasks 1 and 2 of this SWOT audit. The AT_HOME rates
(63.5% → 72.3%) and per-activity JS values are computed. Only figure production
remains. This is the lowest-effort artifact.

---

## Artifact 4 — Synthetic Co-presence Schedules for BEM

### Novel claim
Occupancy schedules augmented with 9-column co-presence information enable
per-room internal-gain estimation that reduces whole-building EUI prediction
error relative to binary occupancy assumptions — demonstrated on a standard
Canadian residential archetype in EnergyPlus.

### Target venue
*eSim 2026* Step 7 results section. Longer form: *Building and Environment*
as a methods + results article once EnergyPlus comparison is complete.

### Figure ideas

**Figure A — Co-presence heatmap for one archetype (Employed, Weekday)**
- X-axis: 48 half-hour slots (4 AM → 4 AM)
- Y-axis: 9 co-presence columns (Alone, Spouse, Children, …)
- Color: share of synthetic population where that column == 1 at that slot
- Shows the daily rhythm of household assembly and dispersal
- Novel visual — no published Canadian residential time-use paper shows this

**Figure B — EUI comparison: binary vs. co-presence-aware BEM runs**
- Paired bar chart: total EUI and sub-metered HVAC / lighting / plug-load
  under binary occupancy vs. co-presence-aware occupancy
- Same building archetype (from `0_BEM_Setup/`), same weather file
- If the co-presence-aware run changes EUI by even 2–5%, that is a
  publishable demonstration of the method's practical relevance

### What it requires to produce
Steps 4–7 complete. This is the highest-effort artifact. Depends on a
functioning Model 1 (Step 4) and EnergyPlus integration (Step 7). Figure A
can be produced as a teaser from the Step 3 outputs before Step 4 is done
(show the observed co-presence distribution, not the synthetic one).

---

## Artifact 5 — Progressive Fine-tuning + Drift-matrix as a Generalizable Recipe

### Novel claim
A progressive fine-tuning scheme applied to a conditional generative model
trained on multi-cycle time-use surveys — with cycle-transition drift matrices
as both training signal and output — provides a statistically grounded method
for extrapolating occupancy behavior to unobserved future years that is
applicable to any HETUS-compatible national time-use survey.

### Target venue
*Building Simulation* or *Energy and Buildings* as a methods paper with the
Canadian GSS as the worked example. Could be submitted independently of the
eSim conference paper if Step 6 is complete before the conference.

### Figure ideas

**Figure A — Fine-tuning progression diagram**
- Timeline schematic: 2005 base model → fine-tune → 2010 model → fine-tune
  → 2015 model → fine-tune → 2022 model → forecast 2025/2030
- At each transition: small DRIFT_MATRIX thumbnail and one key metric
  (e.g., AT_HOME validation JS between synthetic and observed)
- Makes the Step 6 architecture self-explanatory in one figure

**Figure B — Forecast uncertainty envelope**
- X-axis: year (2005, 2010, 2015, 2022, [2025], [2030])
- Y-axis: AT_HOME % (or another aggregate metric)
- Observed values as points; synthetic (model output) as bands showing
  mean ± 1 SD across synthetic population
- 2025/2030 forecast shown with wider band (extrapolation uncertainty)
- Recency weights (2022 = 0.40) visible as annotation
- Makes the "forecasting under uncertainty" claim concrete

### What it requires to produce
Step 6 complete. Figure A can be drafted now as a schematic (no data needed).
Figure B requires the full synthetic population from Steps 4–6.

---

## Prioritization

| Priority | Artifact | Reason |
|----------|----------|--------|
| **1 — Do first** | Artifact 3 (COVID drift) | Data already in hand; lowest effort; highest topical demand |
| **2** | Artifact 2 (30-min note) | Pre-Step-4 experiment; clears a methods decision before training |
| **3** | Artifact 1 (DRIFT_MATRIX full) | Artifact 3 is a subset; extending to all 3 transitions adds little extra work once Step 6 runs |
| **4** | Artifact 5 (recipe) | Follows naturally from Step 6 completion |
| **5 — Do last** | Artifact 4 (co-presence BEM) | Highest effort; depends on Steps 4–7 all complete |

**Single-deadline risk mitigation:** If eSim 2026 abstract is due before Step 4
is complete, submit Artifacts 2 + 3 as the core results. They can stand alone.
Artifacts 1, 4, 5 become the journal follow-up.

---

## Progress Log

**2026-04-09 — Task 6 executed (Sonnet)**

Document written. No source files modified. No data computed. Ready for user
review and prioritization decisions.
