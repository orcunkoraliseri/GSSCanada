# T04. The occupant-behaviour frontier after Annex 79: generative occupants, LLM household simulators, and what the field says it still lacks

> **Corrections 2026-09-19 (round 2).** Round 1 of this prompt failed vetting: six of twelve DOIs pointed at other papers, our own CENTUS paper was given an invented
> title, and two dataset DOIs returned 404.
> These rules add to everything below and win where they differ.
> * Read only three files: `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and this prompt. Open no other
>   file in the project: no `RT` report, no `VETTING_*.md` note, no `*_round1.md`, nothing in `_scan/`,
>   no `.json`. Where the text below says to build on another prompt's answer, search yourself instead.
> * Write only two files, in `5J_docs_occ/DeepResearch/`: `RT04_occupant_behaviour_frontier.md` and `RT04_pages.log`. Creating,
>   editing, renaming or deleting any other file in the project voids this report. Scratch scripts go
>   outside `C:\Users\o_iseri\Desktop\GSSCanada\`. No script may write report text.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the CrossRef record whose call is in the log,
>   never typed. If CrossRef lists two authors, you list two. One work carries one DOI, the same in
>   every section.
> * The page log `RT04_pages.log` has one line per page, API call or search query, written when you
>   open it, tab-separated: the time as `YYYY-MM-DDTHH:MM:SS`, the full URL or query string, the HTTP
>   status, and about 200 characters copied verbatim from the body as returned. No quote, number,
>   licence, deadline or URL may appear in the report without a matching log line. The vetter re-opens
>   each page and searches for each excerpt.
> * A CrossRef lookup proves that a paper exists, not what it says. Any sentence about what a paper did,
>   found or named as future work needs a log line for its abstract or full text. Without one, mark the
>   row `TITLE ONLY` and say nothing about its content.
> * A page counts as opened only if it returned 200 and its excerpt is in the log. An error, a bot
>   block or a login you did not pass is `COULD NOT OPEN`, never "opened", "read" or "verified".
> * In Section G, the "read in full" and "abstract only" lists name only items whose fetch is in the
>   log. A negative control that names an item you did not fetch voids the report.
> * Every `NOT FOUND`, "no study", "remains open" or "unclaimed" lists the queries behind it, and each
>   query has a log line.
> * Do not grade your own work: never write "verified", "confirmed", "definitive" or "without
>   exception" about the report. The log is the evidence.
> * Name no individuals connected to the fellowship programmes. Never propose a change to the 4J
>   pre-registered gate, null or threshold. No em dashes and no en dashes, in the report or the log.
> **For this prompt:**
> * Our CENTUS paper appears at most once, as one `OURS` row copied verbatim from brief section 2,
>   DOI `10.1016/j.enbuild.2026.117155`. Do not describe it further.
> * Item 1: Annex 79 deliverables and their open problems are quoted only from pages you opened.
>   Item 1.3: "read in full" needs a logged full-text fetch.
> * Item 5: a dataset DOI, Zenodo or figshare record is admitted only if it resolved on the day, with
>   its identifier pasted from the record page. Otherwise `COULD NOT OPEN` and the URLs tried.
> * Item 4: if nothing exists, `NOT FOUND` with the queries is the right answer.

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`.

## Why we are asking

Our four papers sit inside occupant-behaviour modelling for building energy. That field organised
itself around IEA EBC Annex 66 and Annex 79 for a decade. Annex 79 has closed. We need to know what
the field considers finished, what it considers open, and whether the generative and language-model
methods that arrived in 2024 to 2026 are being adopted, resisted, or ignored by the people who review
in *Energy and Buildings* and *Building and Environment*.

We also need to know, plainly, whether time-use-survey-derived occupancy, our signature input, is now
seen as a settled technique or as a niche.

## What we need

### Item 1. The agenda after Annex 79

1. Annex 79's final deliverables: list them, with the open problems each names, quoted.
2. Any successor annex, ASHRAE task group, or IBPSA working group on occupant behaviour active in
   2025 or 2026: name, scope, and the research questions it lists.
3. The three most cited 2024 to 2026 reviews of occupant behaviour modelling for building energy, and
   the gaps each names. Read in full; say so.

### Item 2. Generative occupants and LLM household simulators

Map every 2023 to 2026 work that uses a generative model, an LLM, or an agent-based simulation with
LLM-driven agents to produce occupant presence, activity, or behaviour for buildings or districts.
For each: data, model, whether conditioned on demographics, output resolution, how validated, and the
authors' named future work. Include the generative-agents line of work from social simulation if it
has been applied to buildings, and say if it has not.

### Item 3. Time-use surveys as an occupancy source, 2024 to 2026

1. Which groups, other than the authors of the master brief, published time-use-derived occupancy for
   BEM or UBEM in 2024 to 2026, with what survey, what country, what method, what scale.
2. Is there any published **cross-national** time-use-derived occupancy model other than ours? A
   model trained on one country and tested on another counts. Search under mobility and activity-based
   travel demand vocabularies too.
3. What do reviewers and reviews say time-use approaches lack? We expect: no within-year variation, no
   response to weather, no interaction between occupants, no feedback from the building state. Confirm,
   correct, or extend that list with citations.

### Item 4. Occupancy that responds to weather and heat

Is there published work in which occupant presence or activity **changes with outdoor temperature,
heat waves, or extreme events**, estimated from survey or sensor data at population scale? This is
the hinge of angle `A2`. Report what exists, what data it used, and whether any of it reached a
building energy model. If the honest answer is that presence is treated as weather-independent
everywhere, say so in Section A.

### Item 5. Datasets

The open occupancy and behaviour datasets a reviewer would expect us to know: the ASHRAE Global
Occupant Behavior Database, ecobee Donate Your Data, the Building Data Genome, the HUE and other
residential datasets, national time-use archives (HETUS, MTUS, ATUS, Canadian GSS), and any released
2024 to 2026. For each: what it contains, resolution, licence, access route, and whether it could serve
as **held-out validation** for a generated occupancy population. Section F rows.

### Item 6. What the field still cannot do

Close with a list of five capabilities the field's own agenda documents say are missing, each with the
document that says so, and mark for each whether our assets in master brief section 3 address it,
partly address it, or do not touch it.

## Named leads

IEA EBC Annex 79 and Annex 66 deliverable pages; ASHRAE MTG.OBB; IBPSA Building Simulation 2025;
*Energy and Buildings*, *Building and Environment*, *Building Simulation*, *Journal of Building
Performance Simulation*; arXiv `cs.AI`, `cs.MA`, `cs.CY`; the Centre for Time Use Research and MTUS
documentation; Eurostat HETUS pages; BuildSys and e-Energy proceedings.

## Hard constraints specific to this prompt

* Every citation verified through CrossRef or arXiv; Section H shows the returned titles.
* Do not describe our own papers back to us. If a search returns them, list them as `OURS` in one row
  and move on.
* Item 4 is the one where invention is most tempting. If nothing exists, `NOT FOUND` with the searches
  run is the correct answer.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers in its first two sentences: is time-use-derived occupancy seen as settled or
niche, with the evidence; and does any published occupancy model respond to heat at population scale.

**Section C** is the generative and LLM occupants table from item 2 plus the time-use table from
item 3.

**Section D** maps item 6 onto our assets.

**Section F** is the dataset table from item 5.

**Section G** carries the "what time-use lacks" list from item 3.3 and your negative controls.
