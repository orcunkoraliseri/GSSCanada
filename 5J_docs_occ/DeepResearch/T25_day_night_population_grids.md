# T25. Day and night population grids: how many people are in a district, hour by hour

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Census counts say where people sleep. Several open products estimate where they are during the day:
the European Commission JRC ENACT-POP grids (day and night population by month), LandScan USA and
LandScan HD (day and night), commuting-adjusted daytime population from the US Census, and Canadian
Census commuting flows. For a district energy model, these can fix the **number of people present**
in a neighbourhood by hour, and hence constrain (`R2`) the sum of generated household schedules. We
need to know what exists for our countries, at what grid size, and whether anyone used it for
building energy.

## What we need

### Item 1. The products

Data-source cards (brief section 9) for at least: JRC ENACT-POP (version, reference year, months,
grid, day and night definitions); JRC GHSL population layers; LandScan Global, LandScan USA, LandScan
HD (access and licence for a Canadian university); WorldPop; Meta High Resolution Settlement Layer;
US Census commuting-adjusted daytime population; Statistics Canada commuting flow tables and any
daytime population product; any Canadian day-night grid; any national day-night product for Spain,
Italy or the UK.

### Item 2. How day population is modelled

For ENACT-POP and LandScan specifically: which inputs (labour statistics, school enrolment,
tourism, points of interest, land use), which activity classes, and **whether a residential day
population (people at home during the day) is separated out**. Quote the method documents.

### Item 3. Validation of these products

Any study that validated day-time population grids against phone data, counts or surveys. Report the
error metric and value.

### Item 4. Use in building energy

Works that used a day-night population grid to set building occupancy, commercial and residential
occupant counts, or urban energy demand. Section C rows. Say whether any combined it with time-use
schedules.

## Named leads

JRC data catalogue and ENACT project pages; ORNL LandScan pages; Statistics Canada census commuting
tables; US Census daytime population pages; *Scientific Data*, *Remote Sensing of Environment*,
*Computers, Environment and Urban Systems*, *Sustainable Cities and Society*, *Energy and Buildings*.

## Hard constraints specific to this prompt

* Give the grid size and the reference year for each product; do not describe a 2011-based product as
  current.
* If residential day population is not separated in a product, say so; that decides whether it can
  constrain residential occupancy at all.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: is there an open day-night population grid covering Montreal, Toronto
and the four European districts of brief section 3, at what grid size and year, and does any separate
people at home during the day.

**Section F** is item 1. **Section C** is items 3 and 4. **Section D** assesses "day-night grids as a
headcount constraint on district occupancy" as a form of `A14`. **Section G** carries item 2 and your
negative controls.
