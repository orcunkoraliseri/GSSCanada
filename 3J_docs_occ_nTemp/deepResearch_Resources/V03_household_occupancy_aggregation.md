# V03. Household occupancy aggregation conventions for building energy models

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C and F are lighter here; say `not applicable to this prompt` where the prompt does not ask
for them. **Section B and Section H are the deliverable.**

## Why we are asking

An earlier internal report addressed this exact question and its citation apparatus collapsed under
audit. Of its 15 references: **9 DOIs resolve to completely unrelated papers** (microalgae biodiesel,
piezoelectric pavements, tabique wall coatings, liquid-desiccant air conditioning), typically in the
right journal and often one character away from the correct DOI, which is precisely why they survived
casual checking. Two entries match no real paper that could be found at all. Two were clean.

The report's conclusions may well be directionally right. That is not the point: nothing in it can be
cited, because we can no longer tell which parts were read and which were generated. **We are rebuilding
the evidence base from zero.** Do not reuse its reference list. The broken report is at
`improvements/investigation/deepResearch Prompts/R1_household_occupancy_aggregation_report.md` if you
want to see the question it was asking, but treat every claim in it as unverified.

This matters to us because our pipeline computes **two different statistics from the same household
data for two different purposes**: a per-slot **maximum** across members, used only for household
formation and a plausibility exclusion, and a per-slot **mean** across members, which is the schedule
actually injected into EnergyPlus. Three separate audits misread that as a defect. We want to know what
the literature actually does.

## What we need

1. **The taxonomy, with who uses what.** For aggregating individual household members' presence into a
   dwelling-level occupancy schedule for building energy simulation, distinguish:
   * **mean / fraction present**, a continuous 0 to 1 value
   * **sum / count of members present**, 0 to N
   * **any-present binary**, 1 if anyone is home
   * **any-present scaled by household size**, the binary multiplied by N
   Give one row per study with the convention it uses, its temporal resolution, its country and stock,
   and whether the schedule feeds `People`, `ElectricEquipment`, `Lights` or several.

2. **The any-present x N question, stated carefully.** A prior claim was that **zero** studies use the
   binary scaled by household size. Test it. Then be precise about what you can support:
   "I searched for X and found no study using it" is **absence of evidence**; "study Y explicitly
   considers and rejects it" is **evidence of rejection**. Report which of the two you actually have.
   Do not let the first be written as the second.

3. **Explicit warnings.** Does any source explicitly warn against binary or scaled-binary household
   aggregation, for example on the grounds that it overestimates internal heat gains or distorts peak
   load? Quote the wording, with section or page. Mark clearly where you could reach only an abstract.

4. **The energy consequence, in numbers.** What is the reported magnitude of choosing one convention
   over another? Internal gain inflation, space heating error, peak demand error, annual EUI error.
   Give values with units and sources. If the literature does not quantify it, say so.

5. **The two-purpose split.** Where a model computes a **maximum** for one purpose (household
   formation, dwelling-occupied flags, plausibility screening) and a **mean** for another (the injected
   schedule), is that documented anywhere as normal practice, or is it undescribed in the literature?
   We are not asking for validation of our choice; we want to know whether it is conventional, unusual,
   or simply unreported.

6. **Anything recent.** Work from 2020 to 2026 on occupancy aggregation, occupant-centric modelling and
   the aggregation step specifically. The earlier report leaned heavily on 2008 to 2016 material.

## Named leads

Richardson, Thomson and Infield (Loughborough occupancy and domestic electricity demand models, 2008
and 2010); Widen and Wackelgard; Page, Robinson, Morel and Scartezzini on generalised stochastic
occupant presence; Aerts, Minnen, Glorieux, Wouters and Descamps; Wilke, Haldi, Scartezzini and
Robinson; Flett and Kelly; Fischer, Wolf, Scherer and Wille-Haussmann; Buttitta and Finn; Tanimoto,
Hagishima and Sagara; McKenna and Thomson; Swan, Ugursal and Beausoleil-Morrison on Canadian
residential end-use modelling (CHREM); IEA EBC **Annex 66** (Definition and Simulation of Occupant
Behavior in Buildings) and **Annex 79** (Occupant-Centric Building Design and Operation); NREL ResStock
technical documentation.

**Verify each one's real bibliographic record yourself.** Several of these were mis-cited in the broken
report with the wrong journal, wrong volume or wrong year, and two could not be matched to any real
paper. Treat the list above as search leads, not as citations.

## Deliverable

Section B must give one row per study with a **CrossRef-verified DOI**, and for every entry state
whether you read the full text, only the abstract, or neither. Section H must repeat, for each DOI, the
title that `https://api.crossref.org/works/<DOI>` actually returned, so we can check the match without
re-fetching.

Section G must name every citation defect you find along the way: DOIs that resolve to the wrong paper,
report numbers that do not exist, URLs that 404.

A short, fully verified list is worth far more to us than a long, partly verified one. The entire
purpose of this prompt is to be trustworthy where the last attempt was not.
