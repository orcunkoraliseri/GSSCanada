# T19. Occupancy data beyond national time-use surveys: the field map

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. **Run first and alone in wave 5**; `T20` to `T37` read against it.

## Why we are asking

Every occupancy model we have built draws on national time-use surveys joined to censuses. Angle `A14`
asks whether other open data could generate, constrain or validate occupancy for building energy
modelling. Before we send one prompt per source family, we need the map: which source families have
been used for residential or urban occupancy at all, how often, since when, and which families the
building-energy field has not touched.

## What we need

### Item 1. The families, counted

For each source family below, run one OpenAlex query (give the exact query string, the filter and the
date run) for works that use the family **to derive building occupancy, presence or schedules for
energy modelling**, and report the count per year from 2015 to 2026. Then open the five most cited
hits of each family and say, per hit, whether it really uses that source for occupancy (a hit that
only mentions it does not count; report the true-positive share of the five).

1. Smart thermostats and home automation (ecobee, Nest, and similar).
2. Home sensor datasets (motion, door, CO2, Wi-Fi, plug loads) in dwellings.
3. Smart-meter and disaggregated electricity data used to infer presence.
4. Distribution-network or feeder load data used as an occupancy signal.
5. Aggregated mobile-phone mobility (for example community mobility reports, operator data).
6. Day and night population grids and daytime population estimates.
7. Household travel surveys and travel diaries.
8. Activity-based travel demand models and their synthetic populations (MATSim, ActivitySim and
   similar).
9. Labour-force, housing and energy-use surveys that ask about time at home or work schedules.
10. Crowdsourced and web sources (points of interest, opening hours, footfall).
11. National time-use surveys, as the **reference count** the other ten are compared with.

### Item 2. Reviews and taxonomies

Every review from 2018 to 2026 that classifies occupancy data sources for building energy modelling
(including the IEA EBC Annex 66 and Annex 79 deliverables). For each: the taxonomy it used, which of
the eleven families above it covers, and which it omits. Section C rows.

### Item 3. The urban scale

Which families have been used at **district or urban scale** (more than about 100 buildings), rather
than for one building or one household? One sentence and the rows that decide it, per family.

### Item 4. Families that fuse two sources

Studies that combine a time-use survey with one of families 1 to 10 (for example calibrating
survey-generated schedules to mobility data, or validating them with thermostat presence). Section C
rows; say which role (`R1` to `R4`, brief section 9) each source played.

## Named leads

OpenAlex; Scopus search strings where available; IEA EBC Annex 66 and Annex 79 final reports;
*Energy and Buildings*, *Building and Environment*, *Applied Energy*, *Journal of Building Performance
Simulation*, *Energy Research and Social Science*, *Transportation Research Part C*, *Computers,
Environment and Urban Systems*, *Sustainable Cities and Society*, *Scientific Data*.

## Hard constraints specific to this prompt

* Every count carries its query string, filters and date. We will re-run them; a count that does not
  reproduce fails the round.
* The true-positive share of item 1 is mandatory. A family with a large count and zero true positives
  is reported as such, not as a busy field.
* Do not rank the families by promise. This prompt maps; `T38` ranks.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which families are well used for building occupancy, which are rare, and
which are absent. Say plainly if the national time-use survey (family 11) is itself a small niche.

**Section B** is the count table (family by year) with the true-positive share per family.

**Section C** holds the reviews (item 2) and the fusion studies (item 4).

**Section D** is not applicable; write `not applicable to this prompt`.

**Section F** gives, per family, one exemplary dataset with the data-source card of brief section 9.

**Section G** carries your negative controls and the families you could not count.
