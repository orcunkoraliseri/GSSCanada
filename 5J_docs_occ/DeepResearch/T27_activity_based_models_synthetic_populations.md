# T27. Activity-based travel models and their open synthetic populations as occupancy engines

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
> * Every scenario named in item 1 (eqasim Île-de-France, Switzerland, Lyon and the other eqasim
>   cities; MATSim Berlin and other published scenarios; ActivitySim examples; POLARIS; Montreal,
>   Québec, Toronto; Madrid, Bologna, London) gets a card or `NOT FOUND`.
> * Each licence is the SPDX identifier read from the repository's own LICENSE file, with its URL logged.
> * Item 2: a coupling row needs a primary study whose abstract or text names both the travel model and
>   the building side, quoted. A review is not a primary row.
> * Item 3: before calling the time-use enrichment question "unclaimed", log the search query and its
>   result count.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. Read with `T26`, which covers the surveys these models
are estimated on.

## Why we are asking

Transport research already builds what we build: a synthetic population of every resident of a
region, each with a 24-hour activity plan (home, work, school, shop, home) with times and locations.
MATSim, ActivitySim, POLARIS, SimMobility and similar frameworks produce these plans; some pipelines
are fully open and reproducible from open inputs (for example the eqasim synthesis for Île-de-France
and Switzerland). Each plan says when a person is at home, at the address level. That is a
population-scale, spatially explicit occupancy generator (`R1`) built by another field, and possibly
already calibrated to counts. We need to know whether any exists for our regions, whether it is open,
and whether building-energy research has coupled to it.

## What we need

### Item 1. Open synthetic populations with daily plans

Data-source cards (brief section 9) for every open or academically obtainable synthetic population
with activity plans. At least: eqasim Île-de-France, Switzerland, Lyon, and any other eqasim cities;
the MATSim open scenarios (Berlin, other published scenarios); ActivitySim example regions; POLARIS;
any Montreal, Québec or Toronto MATSim or activity-based model (for example university models of the
Montreal region); any Spanish (Madrid), Italian (Bologna) or London open scenario. For each add:
whether in-home activities are split (sleep, work at home, leisure at home) or collapsed into "home";
the inputs and their licences; whether the pipeline, not just the output, is open.

### Item 2. Coupling to buildings

Every work that coupled an activity-based or agent-based travel model to building energy, residential
or commercial occupancy, or urban energy (for example MATSim with a UBEM, or with CityGML). Section C
rows with: which model, which building side, what occupancy variable crossed over, spatial scale, and
whether energy results were validated.

### Item 3. What travel plans lack for buildings

In-home activity detail (cooking, sleeping, appliance use), weekends, people who make no trips, and
within-day return trips are known weaknesses. Report what the literature says about each, and any
work that enriched travel plans with time-use diaries for in-home activities.

### Item 4. Calibration

How these synthetic populations are calibrated (counts, travel surveys, census marginals), and
whether the calibration targets include anything about time at home.

## Named leads

eqasim GitHub organisation and papers; MATSim documentation and scenario gallery; ActivitySim
documentation; *Transportation Research Part C*, *Procedia Computer Science* (ANT conference),
*Environment and Planning B*, *Computers, Environment and Urban Systems*, *Energy and Buildings*,
*Applied Energy*, *Sustainable Cities and Society*.

## Hard constraints specific to this prompt

* Separate "open output" from "open pipeline". A published population file that cannot be rebuilt
  is flagged.
* Each MATSim or ActivitySim scenario must have a repository or data URL you opened.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: does an open synthetic population with daily plans exist for Montreal,
Toronto, Lyon, Madrid, Bologna or London, and has anyone driven a UBEM with it.

**Section F** is item 1. **Section C** is item 2. **Section D** assesses "activity-based travel
populations as the occupancy engine of a UBEM, with time-use filling in-home activity" as a form of
`A14`. **Section E** covers item 3. **Section G** carries item 4 and your negative controls.
