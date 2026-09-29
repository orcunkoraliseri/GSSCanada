# T35. European open data for occupancy around the four districts: Madrid, Lyon, London, Bologna

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. The European counterpart of `T34`.

## Why we are asking

OpenUBEM already models four real residential districts: Madrid Berruguete, Lyon Croix-Rousse, London
St Dunstan's, Bologna Galvani 2 (brief section 3). Their occupancy so far can only come from national
HETUS files. Each of these cities and countries publishes other open data that may describe presence
locally: Spain's hourly phone-based mobility matrices, France's open synthetic populations and energy
data, London's datastore and network-operator feeder data, Bologna's open-data portal. We need one
inventory per district of what is local, open and relevant to occupancy.

## What we need

### Item 1. The inventory, per district

For each of the four districts, data-source cards (brief section 9) for every source that covers the
district's area at a resolution finer than the city, grouped by: national statistics beyond HETUS and
the census (labour force, housing, grid population); mobility (phone-based, travel surveys);
energy (smart-meter aggregates, feeder or substation load, building energy certificates with occupancy
fields); municipal open data (counters, population by small area, building registers); synthetic
populations (for example eqasim Lyon or Île-de-France, any Madrid or Bologna activity model). Give the
smallest spatial unit that contains the district for each source.

### Item 2. What is unique to one country

Name any source that exists in only one of Spain, France, the UK or Italy and has no equivalent in the
others, because a four-district comparison needs like-for-like inputs. Say which sources exist in all
four.

### Item 3. Use in building energy

Works that used any item 1 source for occupancy in building energy in these countries. Section C rows.

## Named leads

INE, MITMA or successor open mobility study; INSEE, SDES, Enedis open data, data.gouv.fr, eqasim;
ONS, London Datastore, UK Power Networks open data; Istat, Comune di Bologna open data, E-Distribuzione;
Eurostat regional statistics; JRC data catalogue.

## Hard constraints specific to this prompt

* A source counts for a district only if you confirmed its geography contains that district. Say how
  you confirmed it (a map layer, a code list).
* Do not quote any energy intensity for these districts; ours are under restatement (brief section 3).
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which occupancy-relevant open sources exist for all four districts at a
comparable resolution, and which district is best and worst served.

**Section F** is item 1. **Section B** is item 2. **Section C** is item 3. **Section D** assesses the
European arm of `A14`. **Section G** carries your negative controls.
