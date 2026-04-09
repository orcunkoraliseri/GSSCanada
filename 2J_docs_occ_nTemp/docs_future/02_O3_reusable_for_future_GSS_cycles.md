# Future Research — O3: Reusable Infrastructure for Future GSS Cycles

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, opportunity O3).

**Status:** Parked for future work. Not in scope for the eSim 2026 paper.

---

## The opportunity in plain language

Statistics Canada releases a new GSS Time Use cycle roughly every 5–7 years.
The next cycle (likely 2027 or 2028) will arrive *after* this paper is
published. Because the harmonization layer (Step 2) is built explicitly to
absorb cross-cycle variable mismatches, adding a new cycle should be a
*configuration change*, not a new research project.

Concretely: when GSS 2027/28 is released, only Step 2's variable mapping
table needs updating. Steps 3–7 inherit the new cycle automatically.

## Why this is worth coming back to

- The infrastructure investment has already been paid. Re-running the
  pipeline on a new cycle is the cheapest possible follow-up paper.
- A 5-cycle (2005, 2010, 2015, 2022, 2027/28) longitudinal series is
  considerably stronger than the current 4-cycle series for trend analysis.
- The COVID-distorted 2022 anchor stops being the most recent observation,
  which materially improves the forecast credibility.

## What a future project would look like

1. Wait for the new GSS cycle release.
2. Update Step 2 mapping table to harmonize the new cycle's variables.
3. Re-run Steps 3 through 6.
4. Publish: "Updated Canadian residential occupancy projections — 5-cycle
   analysis 2005–202X."
5. The DRIFT_MATRIX between 2022 and 2027/28 is itself a result: it answers
   "did the COVID shift persist or revert?"

## What is needed before this is feasible

- Statistics Canada to release the next cycle.
- A few days of harmonization work to absorb whatever new variable names
  StatCan introduced.
- Re-running the HPC training pass (~10–16 GPU-hours).

## Risk if delayed

None. This opportunity *requires* waiting for new data anyway. The right
move is to keep the pipeline code in a state that is easy to revisit.
A short README in `eSim_occ_utils/` describing how to add a new cycle
would be the only maintenance task worth doing now.
