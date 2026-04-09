# Explanation — T2: Statistics Canada Survey Redesigns

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, threat T2).

**Purpose:** A short explanation of why this issue exists, why it matters
for the pipeline, and what the project's exposure looks like.

---

## What the issue is

Statistics Canada has redesigned the GSS Time Use survey several times in
the four cycles this pipeline uses (2005, 2010, 2015, 2022). The redesigns
are not cosmetic — they change *how the data is collected* and
*what the variables measure*. The three biggest changes already absorbed
by Step 2 of this pipeline are:

1. **Sample frame change.** Earlier cycles (2005, 2010, parts of 2015) used
   Landline Random Digit Dialling. By 2022 the frame switched to the
   Dwelling Universe File. The two frames reach different households —
   landline RDD systematically under-samples mobile-only households, which
   skew younger and more urban.

2. **Collection mode change.** Cycles up to 2015 were CATI (Computer-
   Assisted Telephone Interview). 2022 was EQ (Electronic Questionnaire,
   web-based). The same person being interviewed gives slightly different
   answers depending on whether they are talking to a human on the phone
   or filling in a web form. This is encoded as `COLLECT_MODE` in the
   pipeline.

3. **Income measurement change.** Pre-2022 cycles asked respondents for
   self-reported income brackets. The 2022 cycle linked respondents to
   their CRA T1 tax records and used the actual filed income. Self-report
   and tax-record income agree on the median household but disagree on
   the tails — under-reporting at high income, over-reporting at low
   income.

## Why this matters for the pipeline

When you build a longitudinal model that pools data across cycles, the
model has to decide whether the observed change between cycle A and
cycle B is:

- **Real behavioral change** in the population, or
- **Instrument change** in how the data was collected.

If you cannot tell the two apart, your trend forecasts conflate the two
and you over- or under-estimate where the population is heading.

This pipeline addresses the *known* redesigns by encoding them as model
covariates (`COLLECT_MODE`, `TOTINC_SOURCE`, bootstrap method flag).
That lets the Conditional Transformer learn the artefact and subtract it
from the behavioral signal.

## What the residual exposure looks like

The risk T2 names is **future** redesigns, not past ones. Specifically:

- StatCan has not committed to a long-term stable design. The next cycle
  (2027/28) may introduce another sample frame change, another collection
  mode (e.g. mobile-app diary), or another income source.
- Any of these changes would invalidate the harmonization decisions baked
  into Step 2 for that new cycle.
- There is nothing the pipeline can do *today* to prevent this — the
  exposure is to a decision StatCan has not yet announced.

## What this means for the eSim 2026 paper

- The paper covers the four cycles 2005, 2010, 2015, 2022 with explicit
  documentation of the redesigns it absorbed.
- Reviewers may ask: "what happens when the next cycle arrives?"
- The honest answer is: "Step 2 mapping table needs an update; the rest
  of the pipeline runs unchanged. The risk is that the new cycle
  introduces a discrepancy we cannot encode as a covariate." That is a
  one-paragraph limitation in the discussion section.

## What to keep an eye on

- StatCan release notes for the next GSS Time Use cycle. The earliest
  signal of a redesign comes from the methodology document released
  alongside the new PUMF.
- Any preview of the new questionnaire — variable name changes are the
  cheapest signal that harmonization work is needed.
