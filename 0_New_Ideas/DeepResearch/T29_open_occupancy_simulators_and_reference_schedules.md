# T29. Open occupancy simulators and reference schedule libraries: the baselines a new source must beat

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Any paper that brings a new occupancy source must show it changes something against what modellers
already use. Two families of "what modellers already use" exist: fixed reference schedules in codes
and standards, and open stochastic simulators (the Load Profile Generator, the CREST demand model,
StROBe, the LBNL Occupancy Simulator, the ResStock schedule generator, and others). Several of these
are themselves built from a time-use survey, so they share our blind spots. We need the list, what
each is built from, its licence, and whether any was ever validated against measured presence.

## What we need

### Item 1. Reference schedules in codes and standards

For each: issuing body, version, building types covered, residential occupancy schedule given (hours
and fractions, or a pointer), what it was derived from (quote), and whether it is freely readable.
At least: ASHRAE 90.1 Appendix G and the DOE prototype models, NECB 2020 and its schedules, ISO 17772
and EN 16798, SIA 2024 (Switzerland), UK NCM and CIBSE TM59, Spanish CTE, Italian UNI/TS 11300, the
Passive House Planning Package defaults.

### Item 2. Open stochastic occupancy and load simulators

Data-source cards (brief section 9, adapted: the "data" is the tool) for at least: Load Profile
Generator, CREST Demand Model, StROBe, LBNL Occupancy Simulator, the NREL ResStock and ComStock
schedule generators, obFMU, the Richardson occupancy model, synPRO, Urbs or any UBEM-native schedule
module (CityBES, CEA, UMI, TEASER, SimStadt). For each add: the survey or data it was estimated on,
country and year of that source, licence, maintained or not, and whether it outputs presence per
person.

### Item 3. Validation against measured presence

Which of items 1 and 2 were validated against measured presence (sensors, thermostats), not only
against another survey or a load curve? Section C rows with metric and value. `NOT FOUND` per tool is
a valid answer.

### Item 4. Comparisons between them

Studies that compared several of these schedules or simulators on the same building or stock, and how
much energy or peak results moved. Section C rows.

## Named leads

Tool repositories and documentation; DOE and PNNL prototype pages; NRC Canada NECB pages; *Journal of
Building Performance Simulation*, *Energy and Buildings*, *Building and Environment*, *Applied Energy*;
IBPSA Building Simulation proceedings; IEA EBC Annex 66 and 79 reports.

## Hard constraints specific to this prompt

* The data a simulator was built on is quoted from its own documentation or paper, with the country
  and survey year.
* Do not describe a tool as validated if it was only compared with the survey it was estimated on.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which widely used occupancy baselines have been validated against measured
presence, and how many are themselves built on a time-use survey.

**Section F** is items 1 and 2. **Section C** is items 3 and 4. **Section D** assesses "measured-presence
benchmark of the standard baselines" as a form of `A14`. **Section G** carries your negative controls.
