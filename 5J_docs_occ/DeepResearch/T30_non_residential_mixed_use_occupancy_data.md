# T30. Open occupancy data for offices, shops, hotels and mixed-use buildings

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. Read with `T16`.

## Why we are asking

Our third paper generated occupancy for four channels in one tall building: residential, office,
retail, hotel. The hotel channel had no time-use code at all and fell back on provincial occupancy
statistics; the office and retail channels came from what workers and shoppers reported in diaries.
OpenUBEM also meets many non-residential buildings from OpenStreetMap. Other open data may describe
non-residential presence far better: opening hours in OpenStreetMap, pedestrian and footfall counters
published by cities, Wi-Fi occupancy datasets from campuses and offices, hotel occupancy statistics,
office attendance indices after 2020. We need what exists and whether it reached building energy.

## What we need

### Item 1. The sources

Data-source cards (brief section 9) for at least:

1. OpenStreetMap `opening_hours`: coverage share by building type in Montreal, Toronto and the four
   European districts of brief section 3, if any published study or tool measured it; otherwise
   `NOT FOUND`.
2. City pedestrian and footfall counters with open data (for example Melbourne, Zurich, Montreal,
   Toronto, London, Madrid): resolution, years, licence.
3. Open office and campus occupancy datasets (Wi-Fi, badge, camera counts, CO2): for example the
   ASHRAE Global Occupant Behavior Database, the UCI occupancy detection sets, university campus
   datasets.
4. Office attendance and return-to-office indices after 2020 (published by any organisation, with
   methodology).
5. Hotel occupancy statistics by month or day for Canada, Spain, Italy, UK (official sources).
6. Retail and restaurant visit data with academic access (points-of-interest visit panels).

### Item 2. Use in building energy

Works that used any of item 1 to set non-residential occupancy schedules in building energy or UBEM.
Section C rows with the source, building type and whether the schedule was validated.

### Item 3. Schedules from opening hours

Has anyone converted `opening_hours` or similar tags into EnergyPlus or UBEM occupancy schedules at
scale? Report coverage achieved and fallback when tags are missing.

## Named leads

OpenStreetMap wiki and taginfo; city open-data portals; ASHRAE OB database; UCI Machine Learning
Repository; Statistics Canada, INE, Istat and ONS tourism statistics; *Energy and Buildings*,
*Building and Environment*, *Journal of Building Performance Simulation*, *Sustainable Cities and
Society*, *Building Simulation*.

## Hard constraints specific to this prompt

* Coverage figures for `opening_hours` must come from a query you ran (give the query, the tool and
  the date) or from a cited study. Never estimate coverage.
* Separate residential from non-residential rows; this prompt is about non-residential.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which open source best describes office, retail and hotel presence by hour
in Canadian and European cities, and has any UBEM used opening hours at scale.

**Section F** is item 1. **Section C** is items 2 and 3. **Section D** assesses "open non-residential
occupancy data for mixed-use buildings" as a form of `A14` and its relation to `A10`. **Section G** carries
your negative controls.
