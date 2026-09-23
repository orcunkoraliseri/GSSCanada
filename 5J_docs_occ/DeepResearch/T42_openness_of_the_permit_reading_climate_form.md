# T42. Has anyone already done it: a language model reading building records for retrofit and cooling state, with abstention, feeding an energy model

Paste `00_MASTER_BRIEF.md` first (read its section 10), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. **Run it alone: do not run any other prompt in this session, before or
after.** Written 2026-09-22. Your files are `RT42_openness_of_the_permit_reading_climate_form.md` and
`RT42_pages.log`.

## Why we are asking

The fifth paper's subject is fixed (brief section 10). Before we build it, we need to know whether it
has already been done, in whole or in part. The claim has four parts:

* **P1.** A language model or text classifier reads the free text of building records (permits,
  assessment notes, audit notes, listings, inspection reports) and infers equipment or retrofit
  state: heat pump, air conditioning, insulation, windows, heating fuel.
* **P2.** The model gives a set of possible answers or abstains when the text is too thin, with
  stated coverage (conformal prediction, selective classification, reject option, or similar).
* **P3.** The text is French, or French and English together.
* **P4.** The inferred states, with their uncertainty, feed a building or urban building energy model,
  ideally with occupant schedules from time-use data.

## What we already know, so do not restate it as a finding

These two works are known to us. Use them as your positive controls (see below), not as findings.
* Gunay, Wills, Knudsen, Macdonald 2023, Building and Environment, 10.1016/j.buildenv.2023.110848:
  association-rule text mining on free-text permit fields, seven Canadian cities, over 240,000
  entries, for dwelling type, floor area and foundation. An open abstract is on the NRC Publications
  Archive (nrc-publications.canada.ca).
* Zhang, Hong, Luo 2020, SimBuild, 10.26868/25746308.2020.c083: BERT on San Francisco permits,
  multi-label work type, no abstention, no French.

## What we need

### Item 1. Prior work on each part and on their combinations

Search for studies from 2015 to today on P1, P1 with P2, P1 with P3, P1 with P4, and any work that
joins three or four parts. Also search the nearest neighbours:
* language models or text classifiers that fill missing inputs of urban building energy models
  (vintage, envelope, system type) from any text source;
* conformal prediction, prediction sets or abstention anywhere in building energy or building stock
  modelling;
* uncertainty in retrofit or cooling state propagated into stock energy results or indoor
  temperature of occupied dwellings.

Every Section C row carries: authors copied from the CrossRef record, year, venue, DOI or arXiv ID;
record type read (or "none"); city or country; model; what was extracted; parts covered (P1 to P4,
each yes or no); abstention or sets (yes or no); language of the text; reported accuracy; `Read:`
full, abstract, or `TITLE ONLY`.

### Item 2. Which part is open

For each part and for the full combination, the nearest study found and what it did not do.

## Named leads

OpenAlex, Semantic Scholar, arXiv, CrossRef, NRC Publications Archive, eScholarship, OSTI, IBPSA
proceedings (Building Simulation, SimBuild, eSim), ACM BuildSys and e-Energy, Tackling Climate Change
with Machine Learning workshops. Journals: Energy and Buildings, Building and Environment, Applied
Energy, Journal of Building Performance Simulation, Sustainable Cities and Society, Energy and AI.
Query terms, alone and combined: "building permit", "permit text", "natural language processing",
"large language model", "text classification", "heat pump", "air conditioning", "retrofit",
"urban building energy model", "building stock", "conformal prediction", "prediction set",
"abstention", "selective classification", "French", "permis de construction".

## Hard constraints specific to this prompt

* **Positive controls.** Your searches must surface both known works above through a logged search
  line. If a search that should find one of them does not, say so in Section G; it means the search
  is too weak to support any "not found" for that part.
* Before writing `TITLE ONLY`, try at least one open copy (publisher abstract page, institutional
  archive, arXiv, Semantic Scholar or OpenAlex abstract) and log each try.
* Authors are copied from the CrossRef record of that DOI, never from memory or a citing paper. If
  CrossRef and the paper disagree, report both.
* A study row counts only if its abstract or text is logged; `TITLE ONLY` rows may be listed but carry
  no claim about what the study did.
* Every "not found" lists its queries with their log lines: "these queries found nothing", never
  "no such work exists".
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first, in at most eight sentences: is the four-part combination open; which part
has the closest prior work, and by whom. **Section C** is item 1. **Section D** is item 2, one bullet per
part and one for the combination, each marked `[INFERENCE]`. **Section G** carries the positive-control
result, the queries that found nothing with their log lines, and any work you could not open.
