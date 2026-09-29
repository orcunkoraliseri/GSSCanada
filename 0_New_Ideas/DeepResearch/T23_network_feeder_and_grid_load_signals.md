# T23. Open feeder, substation and system load as an aggregate check on occupancy

> **Corrections 2026-09-18 (round 2).** Round 1 of this prompt failed vetting: invented co-authors,
> quotes that are not on their pages, named items dropped without a word, and no page opened. These
> rules add to everything below and win where they differ.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the same CrossRef record
>   (`api.crossref.org/works/<DOI>`), never typed. If CrossRef lists two authors, you list two.
> * Every page you open, CrossRef and OpenAlex calls included, gets a line in `RT<NN>_pages.log`
>   (format in the runner). Every quote, variable name, licence, count and URL in the report must be
>   traceable to a log line. A claim with no log line is not admitted.
> * Every item and every named source below gets its own heading or card. If you could not find it,
>   write `NOT FOUND` and list the URLs you tried; they must be in the log.
> * Round 1 dropped both hard constraints of this prompt. Every card carries the file format, the most
>   recent timestamp you saw, and the sentence that the occupancy signal is indirect.
> * Every operator named in items 1 and 2 gets a card or a `NOT FOUND` line with the URL tried.
> * Copy each licence name from the licence page itself, including any NC or ND suffix.
> * A Section C row is admitted only if the measured side is feeder or substation load, not bills or
>   whole-system demand.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Some network operators now publish half-hourly or hourly load for low-voltage feeders and secondary
substations that serve a few dozen to a few hundred homes. System operators publish hourly demand for
whole provinces and countries. These are not presence data, but a residential feeder's daily shape
carries the fingerprint of when people are home. If the feeder data are open and geolocated, they
could check (`R3`) whether an occupancy-driven district simulation reproduces the **shape** of real
neighbourhood demand, and record the work-from-home shift (`R4`). We need to know what is published,
at what granularity, and whether anyone used it to test occupancy assumptions.

## What we need

### Item 1. Low-voltage and substation open data

Data-source cards (brief section 9) for every network operator that publishes feeder- or
substation-level load openly. At least: UK Power Networks open data portal, SSEN LV feeder data,
Northern Powergrid, Electricity North West, National Grid Electricity Distribution, Liander and
Enexis (Netherlands), E-REDES (Portugal), Enedis open data (France), any Spanish, Italian or German
distribution operator, and any Canadian distribution utility (Hydro-Québec, Hydro Ottawa, Toronto
Hydro, BC Hydro). Add: whether the share of residential customers on the feeder is published, whether
the feeder can be located on a map, and whether heating is electric in that area.

### Item 2. System-level hourly demand

One card each for IESO (Ontario), Hydro-Québec open data, AESO, BC Hydro, ENTSO-E Transparency,
REE (Spain), Terna (Italy), National Grid ESO (UK), RTE (France). Only the facts needed: resolution,
years, licence, and whether residential demand is separated from other sectors.

### Item 3. Occupancy tested against feeder data

Works that compared a bottom-up residential simulation driven by occupancy schedules (time-use,
stochastic, or standard) with measured feeder or substation load. Section C rows with: the occupancy
source, the metric (peak timing, shape correlation, load factor), and the result. Say whether any
isolated the occupancy contribution from weather and appliance assumptions.

### Item 4. The confound

How does the literature separate occupancy from weather, heating fuel, solar generation and appliance
stock when reading a feeder load shape? Name the methods, and say whether any are credible at the
feeder scale.

## Named leads

Operator open-data portals; *Applied Energy*, *Energy and Buildings*, *Energy*, *IEEE Transactions on
Power Systems*, *Sustainable Energy, Grids and Networks*; CIRED proceedings; Ofgem and UK network
innovation project reports.

## Hard constraints specific to this prompt

* A portal counts only if you reached a download or API page for load data. Report the file format
  and the most recent timestamp you saw.
* Do not present feeder load as occupancy. State in every card that the occupancy signal is indirect.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which operators publish geolocated, sub-hourly residential feeder load
openly today, and whether any serve Canada, Spain, Italy or the UK districts in brief section 3.

**Section F** is items 1 and 2. **Section C** is item 3. **Section D** assesses "feeder load shape as a
held-out check on district occupancy" as a form of `A14`. **Section G** carries item 4 and your negative
controls.
