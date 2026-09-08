# T15. Passive survivability and neighbourhood resilience under loss of supply: the state of the method, the standards, and whether anyone put real occupants inside

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Reads `T05` and `T08` for heat and health context.

## Why we are asking

Angle `A9` and two of the fellowship programmes in the master brief (section 5) centre on the hours a
building or a neighbourhood stays habitable after electrical supply fails, in winter cold and summer
heat, with an uncertainty statement, and with occupancy that says who is actually inside. Passive
survivability has a decade of single-building work and a growing neighbourhood literature. We need
the current state, the standards that define habitability, the way uncertainty is handled when no
outage can be measured, and above all whether occupancy in these studies is a fixed schedule or a
population.

## What we need

### Item 1. The method as published

Every 2015 to 2026 study that simulates indoor conditions after loss of HVAC or power for more than
one building, or for one building under a stated neighbourhood or stock framing. One Section C row
each plus columns for: season (cold, heat, both); duration of outage; habitability metric and
threshold (Standard Effective Temperature band, heat index, degree-hours, WBGT, the LEED passive
survivability pilot credit, the RELi or REDi frameworks); weather (typical, extreme year, future,
observed event); **occupancy assumption, quoted**; density or morphology as a variable; uncertainty
treatment; validation against any measured event. Section A must say how many treated occupancy as
a population rather than a schedule.

### Item 2. The habitability standards

For each standard or credit that defines a habitable or survivable indoor band: issuing body, version,
the band and its physiological basis, the population it assumes (healthy adult, elderly, infant),
whether it is season-specific, URL opened, date checked. Include LEED IPpc100 and its successors,
ASHRAE Standard 55 and Guideline 36 where relevant, the CIBSE and Passivhaus resilience guidance, the
Canadian National Building Code and NECB clauses on resilience if any exist, the WHO indoor
temperature guidance, and any 2024 to 2026 standard drafts on thermal resilience (ASHRAE, ISO,
CEN). Note where standards disagree on the band.

### Item 3. Density and morphology

What does the literature conclude about neighbourhood density and morphology during outages: shelter
in winter versus suppressed nocturnal cooling in summer, mutual shading, thermal mass, party walls?
Report only studies that varied morphology explicitly, with the direction and size of the effect, and
whether the sign reversed between seasons.

### Item 4. Uncertainty when nothing can be measured

Outages cannot be scheduled for measurement. How do the studies in item 1 justify their numbers:
Sobol or Morris sensitivity, Monte Carlo over envelope and behaviour, surrogate models, calibration
on non-outage periods, comparison with the few measured events (Texas 2021, Québec 1998 ice storm,
British Columbia 2021, Puerto Rico 2017)? Which of those events have published indoor-temperature
data? Section F rows for any dataset.

### Item 5. Occupants during outages

1. Empirical evidence on what people do during prolonged outages: stay, leave, shelter with
   neighbours, open windows, use unsafe heating; from surveys after real events. Population-scale
   sources preferred.
2. Whether any survivability study varied **presence** (who is home at the hour the outage starts,
   who leaves), and whether any used time-use or mobility data to do so. If `NOT FOUND`, that is the
   gap `A9` would fill, and Section A must say so.
3. Whether any study weighted survivability by the vulnerability of the actual occupants (age,
   health, mobility) rather than by dwelling count.

### Item 6. The Canadian frame

For Canada specifically: which neighbourhood typologies and archetypes have been used in resilience
or survivability studies; what utilities and agencies publish about outage frequency and duration;
whether any Canadian city has a published resilience or passive-survivability policy target. Report
what is downloadable.

## Named leads

*Building and Environment*, *Energy and Buildings*, *Sustainable Cities and Society*, *Building
Research and Information*, *Journal of Building Engineering*, *Applied Energy*; ASHRAE Transactions
and the ASHRAE resilience task groups; USGBC LEED pilot credit library; the RELi and REDi documents;
NRC Canada climate-resilient buildings reports; Hydro-Québec and Ontario outage reporting; the BC
Coroners Service heat-dome review; IEA EBC Annex 80.

## Hard constraints specific to this prompt

* Every band and threshold quoted from the standard with version and date checked.
* Every occupancy assumption quoted, not inferred.
* Do not name the researcher's own fellowship proposals or attempt to find them.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences how many survivability studies treated occupancy as
a population, and whether any used time-use or mobility data for presence during an outage.

**Section C** is the study table from item 1.

**Section F** is the standards table from item 2 and the measured-event datasets from item 4.

**Section E** is items 3 and 6.

**Section G** carries the uncertainty methods from item 4, the occupant evidence from item 5, and
your negative controls.
