# Explanation — T3: Census–GSS Demographic Drift Over Time

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, threat T3).

**Purpose:** A short explanation of why this issue exists, why it matters
for the pipeline, and what the project's exposure looks like.

---

## What the issue is

The pipeline depends on two completely separate Statistics Canada data
sources, each anchored at its own point in time:

- **Census PUMF (2021)** — provides building characteristics: dwelling
  type, year of construction, number of bedrooms, condo status, etc.
  These are needed for BEM/UBEM integration in Step 7.
- **GSS Time Use 2022** — provides the most recent observed behavior:
  what people actually do during the day, who they are with, how often
  they are at home.

There is no shared respondent ID between the Census and the GSS. The
Step 5 linkage joins them *probabilistically* via shared sociodemographic
columns (age, sex, household size, province, employment status,
occupation group, etc.).

The drift problem is this: as the calendar moves forward, both anchors
get older, and the joint distribution of demographics + buildings + behavior
in the *real* Canadian population drifts away from what either anchor
captured.

## Why this matters for the pipeline

The probabilistic linkage assumes that "a 35–44 year old employed
woman in Ontario living in a 4-person household" in the 2021 Census looks
*demographically the same* as "a 35–44 year old employed woman in Ontario
living in a 4-person household" in the 2022 GSS. The assumption is fine
when the two anchors are 1 year apart. It gets weaker every year that
passes.

Concretely, by the time someone uses this pipeline's outputs in 2025
(or later), three things have drifted:

1. **Population composition.** Age distribution shifts, immigration
   composition shifts, household structure shifts (e.g. multi-generational
   households are growing in some provinces).
2. **Building stock.** New construction has been added, demolitions have
   removed older units. The 2021 Census snapshot of the stock is no
   longer current.
3. **Joint distribution.** Even if the marginals are stable, the *joint*
   relationship between demographics and dwelling type can drift — e.g.
   younger households moving into older condo stock as affordability
   pressure changes.

When the joint drifts, the linkage that mapped a Census record to a GSS
archetype based on shared sociodemographics becomes a less reliable proxy
for the real Census 2026 / GSS 2027 population.

## What the residual exposure looks like

- **For the eSim 2026 paper:** small. Both anchors are within ~1 year of
  each other (Census 2021 + GSS 2022). The joint drift is minimal at
  this distance.
- **For applications past 2025:** moderate. Drift accumulates roughly
  linearly until the next Census or GSS release, at which point it can
  be reset by re-running Step 5 on fresh data.
- **For applications past 2030:** material. By then the next Census
  (2026) and the next GSS cycle (likely 2027/28) will exist, and anyone
  still using this pipeline's 2021 + 2022 outputs is operating on stale
  joint structure.

## What this means for the eSim 2026 paper

- The paper anchors are recent (2021 + 2022). The drift threat is small
  at the time of publication.
- The paper should *acknowledge* the drift in the limitations section
  but does not need to do anything about it during the study.
- The natural mitigation is the O3 opportunity: re-run the pipeline when
  the next Census and GSS cycle land, which resets the anchor.

## What to keep an eye on

- Statistics Canada Census 2026 release schedule (PUMF typically arrives
  ~2 years after the Census date).
- Statistics Canada GSS Time Use cycle 2027/28 release schedule.
- Whichever lands first triggers a refresh opportunity for Step 5 of
  this pipeline.
