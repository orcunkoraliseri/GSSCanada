# Future Research — O4: Methodology Transferable Beyond Canada

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, opportunity O4).

**Status:** Parked for future work. Not in scope for the eSim 2026 paper.

---

## The opportunity in plain language

The pipeline's design is built around three ideas that are *not* Canada-
specific:

1. **HETUS 10-min → 30-min downsampling rationale** — applies to any time-
   use survey in the HETUS family (most European countries, Australia,
   New Zealand, parts of Latin America).
2. **Regime-flagging** for instrument changes (CATI → web, self-reported
   income → tax-linked income, etc.) — applies to any longitudinal survey
   that has gone through redesigns.
3. **Progressive fine-tuning + drift-matrix** for forecasting from
   repeated cross-sections — applies to any country with multiple
   time-use cycles.

Together, these form a *recipe* that another country could follow with
their own time-use survey to produce BEM-ready occupancy schedules.

## Why this is worth coming back to

- A pure methods paper has wider citation reach than a Canada-specific
  application paper.
- HETUS-using countries already have infrastructure for time-use data; they
  just lack the BEM-integration recipe.
- This is the kind of paper that lives in *Energy and Buildings*,
  *Building and Environment*, or *Applied Energy* and gets cited by every
  follow-up time-use × BEM project.

## What a future project would look like

1. Pick one or two HETUS-aligned countries with publicly available time-use
   microdata (UK Time Use Survey, German ZBE, Italian ISTAT, Spanish EET).
2. Apply Steps 1–6 of this pipeline to that country's data.
3. Compare: do the same architectural choices (30-min downsampling,
   progressive fine-tuning, drift matrix) hold up?
4. Publish a methods paper with Canada as the worked example and one
   non-Canadian country as the transferability demonstration.

## What is needed before this is feasible

- Access to one non-Canadian time-use microdata source (most are free for
  research with a data agreement).
- A clean, *documented* version of the pipeline code (not the
  Canada-coupled version that exists today).
- Roughly one paper-cycle of effort beyond the current eSim work.

## Risk if delayed

Low to moderate. Other groups may publish similar recipes first, but the
combination of HETUS downsampling + drift-matrix + progressive fine-tuning
is specific enough that an early-mover advantage exists for at least
2–3 years after the current paper.
