# Future Research — O2: UBEM Collaboration Potential

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, opportunity O2).

**Status:** Parked for future work. Not in scope for the eSim 2026 paper.

---

## The opportunity in plain language

The pipeline produces 30-minute occupancy schedules in EnergyPlus
`Schedule:Compact` format, stratified by archetype × ASHRAE climate zone ×
Weekday/Saturday/Sunday. That output format is *exactly* what Urban Building
Energy Modelling (UBEM) groups need when they want to simulate thousands of
buildings across a city instead of one building at a time.

Most UBEM workflows today use synthetic or copy-pasted occupancy schedules
because there is no good source of geographically-stratified, behavior-aware
schedules. This pipeline produces one for Canada.

## Why this is worth coming back to

- The marginal cost is low. The occupancy outputs already exist after Step 7.
  Sharing them with a UBEM group is mostly a packaging task, not a research
  task.
- It opens a co-author / collaboration channel without requiring more
  modelling work on the occupancy side.
- UBEM groups care about *climate-zone × archetype* schedules specifically,
  which is the natural slice of this pipeline's output.

## What a future project would look like

1. Pick one Canadian city with a CityGML or similar 3D building stock model
   (Toronto, Montreal, Vancouver have candidates).
2. Map each building in the stock model to one of the GSS archetypes via the
   Step 5 linkage logic.
3. Run UBEM simulations with (a) generic occupancy schedules and (b) this
   pipeline's archetype-specific schedules.
4. Report the city-level EUI difference and the spatial pattern of where the
   difference is largest.

## What is needed before this is feasible

- Step 7 outputs must be finalized and stable.
- A partner group with an existing UBEM stack (Eurac, MIT SUL, Concordia, NRCan).
- A small data-sharing agreement to handle the synthetic schedules (PUMF
  derivatives are usually shareable, but check with StatCan first).

## Risk if delayed

Low. UBEM is a growing field, but the methodology and outputs from this
pipeline do not become stale quickly. Worth revisiting any time after the
eSim paper is submitted.
