# T34. Canadian open data for occupancy: Montreal, Toronto and the national level

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. Overlaps `T20` to `T30` on purpose: this prompt looks
through one country instead of one source family, and catches what the family prompts miss.

## Why we are asking

The researcher is in Montreal, one fellowship is Canadian, and angle `A8` (Canadian transfer) needs
Canadian ground truth that the earlier rounds found scarce. Canada has federal, provincial and
municipal open-data portals, utility programs and university data holdings. We need one inventory of
everything Canadian that bears on occupancy, presence, household activity or residential load, with
access terms, so the Canadian arm of any 5J angle knows what it can stand on.

## What we need

### Item 1. The inventory

Data-source cards (brief section 9) for every Canadian source, grouped by custodian:

1. Statistics Canada: PUMF files and tables with presence-relevant variables beyond GSS, Census and
   SHEU (for example LFS, Canadian Housing Survey, experimental statistics), and anything available
   only in Research Data Centres that would matter (name it, do not assume access).
2. NRCan and CanmetENERGY: housing-stock and end-use data, EnerGuide data, the Canadian Housing
   Stock model inputs, any metered sets.
3. Utilities and system operators: Hydro-Québec open data (hourly demand, any residential sets, any
   research access), IESO, Toronto Hydro, Hydro Ottawa, BC Hydro, and the Green Button program in
   Ontario.
4. Municipal portals: Ville de Montréal and Toronto open data (pedestrian and cycling counters, building
   energy disclosure, permits, population by small area, any building occupancy data), and the
   Québec open-data portal (Données Québec).
5. Transport agencies: ARTM origin-destination survey, DMG Transportation Tomorrow Survey, STM and TTC
   ridership open data.
6. University and consortium holdings: Canadian research data repositories (Borealis, FRDR), CRDCN
   holdings that matter, and any instrumented-home or thermostat study with released data.

### Item 2. Ground truth for a Canadian UBEM

Which of item 1 could serve as building-level or district-level ground truth for energy (for example
Toronto and Montreal benchmarking disclosure) and at what aggregation. Quote the disclosure rules.

### Item 3. Canadian occupancy studies using non-survey data

Works that used any Canadian non-survey source for residential or urban occupancy. Section C rows.

## Named leads

open.canada.ca; donnees.montreal.ca; open.toronto.ca; donneesquebec.ca; Hydro-Québec open data;
IESO data directory; NRCan open data; Borealis; FRDR; CRDCN; ARTM; DMG; *Energy and Buildings*,
*Journal of Building Performance Simulation*, *Canadian Journal of Civil Engineering*, eSim
conference proceedings.

## Hard constraints specific to this prompt

* Each portal row is a dataset page you opened, not a portal homepage. A homepage alone is `NO
  RETRIEVABLE FILE`.
* Québec Law 25 and federal privacy rules are out of scope here; `T36` covers them. Quote only the
  dataset's own licence (for example the Open Government Licence Canada or Québec).
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: the three Canadian sources that come closest to measured residential
presence or hourly residential load for Montreal or Toronto, and whether any is open without
application.

**Section F** is item 1. **Section B** is item 2. **Section C** is item 3. **Section D** assesses the
Canadian arm of `A14` together with `A8`. **Section G** carries your negative controls.
