# T07. Foundation models for human activity and multi-country time use: is an "occupancy foundation model" claimed, and what corpora would one stand on

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Read together with `T13`, which asks why our own model
lost.

## Why we are asking

Angle `A3` widens the corpus and changes the method to close a transfer gap our fourth paper measured.
The obvious widening is to the harmonised multi-country time-use archives (MTUS, ATUS, the Canadian
GSS we already hold, HETUS national files) and the obvious rhetoric is "a foundation model for
occupancy". Before we use either, we need to know whether anyone has already claimed a foundation
model for human daily activity, what the time-series foundation models of 2024 to 2026 actually do
on load and occupancy data, and what each candidate corpus would cost us in access and harmonisation.

## What we need

### Item 1. Foundation-model claims for daily activity, mobility and time use

Every 2023 to 2026 work that presents a pretrained model for human daily activity sequences, mobility
trajectories or time-use diaries and calls it, or evaluates it as, a foundation model or a
general-purpose pretrained model: data scale, countries, architecture, whether weights are released,
what downstream tasks were tested, and **whether any transfer to an unseen country or region was
measured, with the metric**. Section C rows.

### Item 2. Time-series foundation models on building loads and occupancy

For Chronos, TimesFM, Moirai, Lag-Llama, TimeGPT and their 2025 to 2026 successors: has any peer-reviewed
or preprint work applied them to building energy load, occupancy or appliance data? What did zero-shot
and fine-tuned performance look like against task-specific baselines? Report only measured comparisons.
Then say whether these models are relevant to **generating a population of diaries** at all, or only
to forecasting one series, because that distinction decides whether they matter to us.

### Item 3. The corpora

For each of the following, one Section F row: content, countries, waves, diary resolution, activity
coding list, harmonisation to HETUS or to MTUS categories, access route and eligibility for a
Canadian-based researcher, licence and redistribution terms, whether microdata or only tabulations are
obtainable, URL opened, date checked.

1. MTUS (Multinational Time Use Study), all releases.
2. ATUS (American Time Use Survey), including the ATUS-X extracts.
3. Eurostat HETUS scientific-use files (state plainly the eligibility rule and whether a Canadian
   university can qualify; the master brief says not today).
4. National HETUS-round files obtainable directly from institutes: which countries beyond Spain, UK,
   Italy and France release diary microdata to foreign researchers.
5. Any non-European, non-North-American national time-use survey with public diary microdata.
6. Any large-scale mobility or smartphone-derived activity dataset that could serve as a held-out
   check on presence, with its licence.

### Item 4. Harmonisation cost

For MTUS and ATUS specifically: which activity, location and co-presence variables exist, at what
resolution, and how do their coding lists map to the HETUS Activity Coding List? Cite the published
crosswalks. If no official crosswalk exists for a pair, say `NO OFFICIAL CROSSWALK` and name the closest
academic one. This decides whether widening the corpus is a data-engineering month or a year.

### Item 5. What "foundation model" would cost us in review

Name the reviewers' likely objections to a paper that calls a diary generator a foundation model:
scale, task diversity, emergent transfer. Say which of them our compute (master brief section 3, item 5)
makes unanswerable. Then propose the most modest defensible label for a multi-corpus pretrained diary
generator, with a precedent for the label.

## Named leads

MTUS and CTUR documentation; BLS ATUS documentation and IPUMS ATUS-X; Eurostat microdata access pages;
national statistical institute microdata pages (Statistics Netherlands, INSEE, Destatis, Statistics
Finland, Statistics Norway via Sikt, Statistics Poland, KOSTAT, Statistics Japan, Statistics Korea,
Australian Bureau of Statistics); arXiv `cs.LG`, `cs.AI`, `cs.CY`; *Transportation Research Part C*,
*Computers, Environment and Urban Systems*, *EPJ Data Science*, *Scientific Data*.

## Hard constraints specific to this prompt

* Every access rule quoted from the provider's page with the date checked. Eligibility rules change and
  differ by nationality of the institution.
* Do not state that a corpus is harmonised to HETUS unless the provider's documentation says so.
* Item 2 must not drift into a forecasting review. One paragraph on relevance to population
  generation is the deliverable.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers in its first two sentences: has anyone claimed and released a pretrained model
for daily human activity with measured cross-country transfer; and can a Canadian university obtain
MTUS and ATUS diary microdata today.

**Section C** is the foundation-model table from item 1 and the time-series application table from
item 2.

**Section F** is the corpus table from item 3.

**Section E** is the harmonisation cost from item 4 and the label question from item 5.

**Section G** carries the crosswalk gaps and your negative controls.
