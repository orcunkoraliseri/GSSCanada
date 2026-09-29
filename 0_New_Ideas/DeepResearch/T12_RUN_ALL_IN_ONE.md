# T12, all in one paste (brief + template + prompt)

Built 2026-09-19 by the manager from three files, copied verbatim and unchanged:
`00_MASTER_BRIEF.md` (Part 1), `_RESPONSE_TEMPLATE.md` (Part 2) and
`T12_contradictions_and_ranking.md` (Part 3). Submit this one file, once, in one fresh session.

How to read it:

* Read all three parts before you start. Part 3 is the task; Parts 1 and 2 are its context.
* Where Part 3 says "paste the brief, then the template, then this prompt", that is already done:
  this file is that paste.
* Where Part 3 says "read only three files", it means these three parts. Open no other file in the
  project.
* Part 3's rules win over Parts 1 and 2 where they differ. Everything else in Part 3 applies as
  written, including the two output files `RT12_contradictions_and_ranking.md` and
  `RT12_pages.log` in `5J_docs_occ/DeepResearch/`.



====================================================================================================
# PART 1 OF 3: MASTER BRIEF (00_MASTER_BRIEF.md)
====================================================================================================

# 5J Deep Research: Master Brief (paste this block ahead of EVERY prompt)

This brief gives the shared context for the T-series prompts (`T01`, `T02`, `T03`, ...). Read it, then
answer only the prompt that follows it. Do not restate this brief in your answer.

Written 2026-09-07. Anything here about models, tools, calls or deadlines was true on that date and
may have moved. Date-check before you rely on it.

---

## 1. Who is asking

A postdoctoral building-performance researcher at Concordia University, Montreal, working on
**occupancy data for building energy modelling (BEM) and urban building energy modelling (UBEM) from
national time-use and census microdata**, with EnergyPlus as the simulation engine. Two projects
collaborate: **GSSCanada** (the occupancy generators and their validation) and **OpenUBEM** (an
open-source UBEM engine, `https://github.com/orcunkoraliseri/OpenUBEM`). The researcher is choosing
the subject of a **fifth journal paper (5J)** and is, in parallel, applying to postdoctoral
fellowships whose themes the paper should serve. The prompts in this series ask what the literature is
doing, where the open questions are, and how the researcher's assets fit them. **They do not ask you to
choose the paper.**

## 2. What has been built and published

| Paper | Data | Method | Result | Status |
|---|---|---|---|---|
| CENTUS (Iseri, Gursel Dino, Kalkan, *Energy and Buildings* 357 (2026) 117155, `10.1016/j.enbuild.2026.117155`) | Italy: ISTAT 2011 census plus 2013-14 Time Use Survey | LSTM and Transformer, multitask, activity (145 classes), presence, co-presence per hour, conditioned on demographics | Accuracy 0.98 for both deep models against 0.691 for a high-order Markov chain; claims HETUS harmonisation as the route to cross-national transfer, untested | Published |
| eSim 2026 conference paper | Statistics Canada GSS time-use, four cycles 2005 to 2022 | GSS to schedule to EnergyPlus proof of concept | At-home rate 63.5 % (2005) to 72.3 % (2022) | Published |
| 1J | Canadian census plus GSS, residential | HPC EnergyPlus campaign, paired Monte Carlo with occupancy varied and building frozen, activity-driven equipment and lighting loads | Occupancy-attributable demand, Canadian residential | Under review, *Journal of Building Performance Simulation* |
| 2J | Four GSS cycles (64,061 diaries), 2021 Census PUMF, NRCan SHEU 2019 as end-use benchmark | Conditional Transformer (about 29 M parameters) augments diaries; 2030 forecast under one high-persistence work-from-home scenario; 6,000 paired frozen-frame EnergyPlus runs | Residential load shape 2005 to 2030: at-home share up, annual electricity up only 1 to 3 %, evening peak fixed near 17:30, midday valley fills | Submitted *Building Simulation* 2026-08-07 |
| 3J | Same Canadian data plus provincial hotel statistics; PNNL tall mixed-use prototypes for Montreal and Calgary | Shared-encoder three-head Transformer (residential, office, retail) plus a SARIMA hotel channel; 56-cell EnergyPlus campaign 2005 to 2030 | Four channels peak at different hours; whole-building coincidence factor below 1; three of four channel EUI gates fail against reference bands borrowed from single-use stock | In preparation, *Building and Environment* |
| 4J | HETUS microdata for three countries, one wave each: Spain 2009-10, UK 2014-15, Italy 2013-14; actual-year ERA5 weather matched to fieldwork windows; TABULA-parameter EnergyPlus archetypes | One open-weight LLM (OLMo 3 7B, LoRA) fine-tuned once, strict three-fold leave-one-country-out; pre-registered gates; membership-inference audit | See section 3, item 2 | Mid-build, manuscript about to be written |

Everything above shares one method spine: a generator trained on one national microdata set, a
pre-registered validation table whose gates are seen failing before they are trusted, and a paired
EnergyPlus campaign that isolates the occupancy effect.

## 3. The assets we hold, and the honest state of each

1. **Harmonised time-use corpora.** HETUS diaries for Spain, UK and Italy on disk under national
   agreements (not redistributable); Canadian GSS time-use, four cycles, through the Research Data
   Centre; Canadian Census PUMF. A French HETUS file is held but excluded. Concordia is **not** a
   Eurostat-recognised research entity, so the 17-country Eurostat scientific-use corpus is not
   available to us today.
2. **A fine-tuned open-weight occupancy generator, with a negative headline result.** On the
   pre-registered transfer gate, the fine-tuned model did **not** beat the hard null: a pool of real
   diaries from the two training countries, demographically raked to the held-out country. The null
   reproduced the held-out country's time budget about **two to six times better** than the model on
   every age band of every fold, and growing the backbone from 1.5 B to 7 B parameters did not change
   that. The model does respond to its conditioning vector, at roughly half the required amplitude.
   The membership-inference audit failed its pre-registered bar, so **weights are not released**;
   synthetic diaries for Spain and Italy ship, the UK set is withheld. 4J is being written as a
   negative result on cross-national transfer with an LLM. Treat this as a fact about our work, not a
   thing to fix in your answer.
3. **OpenUBEM, an open-source UBEM engine.** Python, pip-installable: OpenStreetMap ingest, a
   rule-based 30-archetype classifier with a provenance column on every attribute, tiered imputation
   (fusion, spatial, statistical; machine-learning tier built but off by default), per-building
   EnergyPlus 23.1 models with ten real HVAC families and real service loads, parallel simulation on
   the Concordia Speed cluster, ten metered end-use EUIs, operational carbon, report-only validation
   gates, **zero fitted parameters**. Validated on twelve US city-density cells (New York, Los Angeles,
   Austin; 8,154 of 8,160 buildings simulated); it under-predicts measured stock EUI by roughly 4 to
   31 % depending on city and this is documented rather than calibrated away. Applied to four real
   European residential districts (Madrid Berruguete, Lyon Croix-Rousse, London St Dunstan's,
   Bologna Galvani 2) with **dwelling-level division of every floor plate and no corridor or core
   zone** (the "no-core" rule); the district EUIs are in restatement and not quotable today. An
   outdoor thermal-comfort module (UTCI at pedestrian height, five mitigation scenarios) exists but
   has no measured validation and sits outside the headline outputs. **Not present:** future or morphed
   weather, retrofit scenarios, grid or district-heating co-simulation, embodied carbon, any LLM or
   agent component, any health, equity or vulnerability module, Canadian archetypes (stubs only).
   Licence not yet declared (MIT intended).
4. **A validation discipline.** Every step has a validation doc with gates `G<step>.<n>`, a
   perturbation table in which each perturbation must break exactly one gate, pre-registered
   thresholds frozen by checksum before scoring, and a two-host reproducibility measurement
   ("numerically stable, not bitwise reproducible").
5. **Compute.** Concordia Speed HPC (SLURM, single-node GPU jobs, seven-day walltime, A100 80 GB
   class) and Calcul Québec. **Zero budget for commercial APIs or cloud GPUs.** Anything we build runs
   with open weights on one node.
6. **Openings the finished papers name themselves.** 2J: future weather files and an evolving dwelling
   stock instead of a frozen frame; a high-reversion work-from-home counter-scenario; room-level
   occupancy. 3J: reference EUI bands built for, and validated on, buildings that stack several uses.
   4J: a forecasting and scenario axis was designed in an earlier research round (shift-share
   decomposition of observed change plus counterfactuals conditioned on Eurostat EUROPOP and telework
   projections) and then ruled out of scope, so it is researched but unused; and the transfer gap
   itself, item 2 above.

## 4. The candidate angles for 5J (the vocabulary the prompts use)

These are **candidates**, not decisions. Several prompts ask you to find the work that already did
them.

| ID | Angle | Assets it uses | Asset it lacks |
|---|---|---|---|
| `A1` | **Agentic UBEM.** An open-weight language model plans and executes a district energy model end to end over OpenUBEM (site, archetypes, IDFs, simulation, validation), every step gated by the existing report-only checks, compared against the scripted pipeline with no agent | OpenUBEM, validation discipline, Speed | Any agent tooling; open-weight tool-use experience |
| `A2` | **Occupancy under heat.** Time-use-derived presence and activity combined with extreme or future weather to estimate occupancy-resolved indoor heat exposure at district scale: who is home, when, in which dwelling, at what indoor temperature | HETUS and GSS corpora, OpenUBEM districts, dwelling-level division, UTCI module | Future or extreme weather ingest; overheating metrics; occupant response to heat |
| `A3` | **Closing the transfer gap.** Why a fine-tuned LLM loses to a raked pool of real diaries, and what does beat it: retrieval over exemplar diaries, hybrids of donor sampling and generation, a wider and more diverse corpus (HETUS plus Canada plus US ATUS or MTUS), a different backbone class | 4J model and gates, all corpora | Eurostat corpus; US ATUS access is public and not yet used |
| `A4` | **The scenario axis.** Future population (official demographic and telework projections), future weather and an evolving dwelling stock, combined, for European or Canadian districts, 2030 to 2050 | 2J and 4J generators, OpenUBEM, the unused forecasting design | Future weather path; stock-evolution model |
| `A5` | **Activity-resolved demand flexibility.** Appliance and heating loads driven by diaries at district scale under electrification and heat-pump scenarios; flexibility potential and coincident peak | Activity-to-appliance mappings from 4J, OpenUBEM, GSS load-shape results | Grid or tariff model; measured smart-meter validation |
| `A6` | **Occupancy-resolved energy burden.** Who bears energy cost and heat exposure once occupancy is demographically resolved; equity and energy-poverty metrics at district scale | All corpora, OpenUBEM, dwelling division | Income and tenure data; vulnerability indices |
| `A7` | **Language models reading building records with abstention.** An LLM extracts renovation state or attributes from permit archives, energy-performance-certificate free text or cadastral records, emits prediction sets and abstains when evidence is thin, and feeds a stock model with uncertainty (conformal coverage by archetype) | OpenUBEM provenance and imputation tiers, validation discipline | Record archives (agreements needed); conformal-prediction experience |
| `A8` | **Canadian transfer.** OpenUBEM extended to Canadian archetypes (NECB) for Montreal and Toronto districts, with GSS-derived occupancy, validated against Canadian disclosure data at the aggregation the data allows, under cold and heat extremes | GSS pipeline, OpenUBEM, Speed | Canadian archetype library; Canadian building-level ground truth |
| `A9` | **Passive survivability under power failure, with occupants.** Hours a neighbourhood stays inside a habitable indoor band after loss of supply, winter and summer, with uncertainty, and with occupancy that says who is actually inside | OpenUBEM, GSS or HETUS occupancy, validation discipline | Outage physics validation; the habitability band standards |
| `A10` | **Reference bands for stacked mixed-use buildings.** Validation bands constructed for buildings that stack several uses, the opening 3J names | 3J campaign and channels | Measured mixed-use benchmarks |
| `A14` | **Occupancy from open data beyond national statistics.** Generate, constrain or validate occupant presence and activity with open or academically obtainable sources other than national time-use surveys and censuses: smart thermostats and home sensors, smart meters and network feeders, aggregated mobile-phone mobility, household travel diaries, activity-based travel models and their synthetic populations, day and night population grids. Added 2026-09-18; see section 9 | All corpora and pipelines, OpenUBEM, validation discipline | Any non-survey occupancy source in hand; data agreements; measured presence to validate against |

## 5. The fellowship programmes the paper should serve (themes only)

The researcher is applying to five programmes. The prompts use only their public themes.

* **UC Berkeley Chancellor's Climate Futures Fellowship** (via the UC President's Postdoctoral
  Fellowship Program): climate, energy and environment cohort; a public-impact capstone tool is
  required; the drafted proposal is on compound heat waves, passive survivability and energy inequity
  in disadvantaged Californian communities. Application deadline 2026-11-01.
* **Digital Futures postdoctoral fellowship (KTH, Stockholm University, RISE)**: technologies for
  digital transformation, scored on a research matrix (Smart Society, Digitalised Industry, Rich and
  Healthy Life, Educational Transformation, crossed with Trust, Cooperate, Learn), international
  research experience, two-year feasibility. Two candidate subjects are in play: an LLM that reads
  renovation state from municipal records with abstention, and conformal trust bounds on a UBEM
  where no meter exists. Pre-registration 2026-10-02, full application 2026-10-16.
* **Marie Sklodowska-Curie Postdoctoral Fellowship at ETH Zurich**: the drafted project couples a
  HETUS-trained generative occupant engine to the UBEM engine with a Geneva pilot; open science and
  two-way knowledge transfer are scored. The 2026 call closes 2026-09-09 and is unlikely; 2027 is the
  working target.
* **NSERC Postdoctoral Research Award (Canada)**: the proposal must be significantly distinct from the
  doctoral thesis (which was occupancy generation), so the live topic is passive survivability of
  Canadian neighbourhoods under power failure, winter and summer, with uncertainty. Deadline
  2026-10-17.
* **University of Toronto routes**, chiefly the Schmidt AI in Science Postdoctoral Fellowship: AI
  applied in a scientific domain, with an AI co-supervisor; the pitch is the occupant engine plus the
  UBEM engine adapted to Canadian data. Deadline 2026-10-05.

Across the five, UBEM appears in all, generative occupancy in three, LLMs in three, heat and
resilience in two, equity in one strongly. No programme text uses the words "agent" or "digital
twin".

## 6. Source-quality rules (apply to every prompt)

1. **Tier 1 (preferred)**: primary institutional documents: journal author guidelines and
   special-issue pages; funding-call texts on the funder's own portal; statistical-institute
   documentation; model cards and licence texts from the developers; standards bodies; IEA EBC annex
   deliverables.
2. **Tier 2**: peer-reviewed literature, and arXiv preprints where the preprint is the canonical
   reference. Give arXiv ID and version and say whether it was later published.
3. **Tier 3**: well-documented open-source repositories, benchmark leaderboards with a stated protocol,
   technical blog posts from the organisation that built the thing.
4. **Rejected**: content-farm summaries, undated posts, marketing pages, and any AI-generated overview
   presented as a source.

Every claim carries: the claim, the source's own wording or a tight paraphrase, document title,
issuing body, year or version, and a URL or stable identifier. An inference is labelled `INFERENCE`
with the assumption it rests on.

## 7. Answer discipline (this project has been burned, repeatedly, and specifically)

* Answer only what the prompt asks.
* **A citation is not evidence until opened.** Report only what you read in a source you reached.
  Anything unreachable is `COULD NOT OPEN`, never a confirmation. Say per claim whether you read the
  full text, the abstract, or neither.
* **Verify every DOI before citing it.** Fetch `https://api.crossref.org/works/<DOI>` and report the
  title, first author, venue and year the API returned. On an earlier round **9 of 15 DOIs resolved
  to unrelated papers**.
* **`NOT FOUND` is a valid and valuable answer.** Say what you searched. Do not invent a plausible
  paper, call, deadline, count, model version or licence clause.
* **Do not state, estimate or reproduce any result of our models or our engine.** Anything you say
  about our numbers is either copied from this brief or invented.
* **Never recommend the option that happens to flatter us.** If an angle is already published, or a
  topic is saturated, or our assets are ordinary in a field, say so in the first sentence of
  Section A. On the previous paper, three of five rounds proposed exactly the change that would have
  made a failing test pass after being told not to. We read that pattern as a signal about the
  report, not about the world.
* **Distinguish what exists today from what is announced.** For models, tools, calls and datasets give
  the date checked and say whether you verified the artefact is reachable now.
* **Date-check every count, deadline, version and funding figure.** This series asks about things that
  change monthly.
* Report negative results as absence of evidence, not evidence of absence.
* Return results in the schema given by `_RESPONSE_TEMPLATE.md`.
* **No em dashes and no en dashes anywhere in the output text.**

## 8. Vocabulary

| Term | What we mean by it |
|---|---|
| **Diary** | One respondent's one day as a sequence of time slots, each with an activity code, a location code and a co-presence flag. HETUS uses 144 ten-minute slots; our pipelines resample to 48 half-hour slots. |
| **Raked donor null** | Real diaries from other countries, re-weighted by iterative proportional fitting to the held-out country's published demographic marginals. The baseline our generator must beat. |
| **Channel** | A building use whose occupancy is generated separately: residential, office, retail, hotel. |
| **Fidelity** | How closely the generated population's distributions match the survey's, not how well one diary is predicted. |
| **No-core** | Dividing every residential floor plate directly into dwellings, with no corridor, stair or core zone. |
| **Report-only gate** | A validation check whose threshold is fixed before the run and never tuned so that it passes. |
| **Zero fitted parameters** | Every constant in the engine traces to a cited standard or measurement; nothing is calibrated to the validation target. |
| **Frozen frame** | An EnergyPlus campaign in which building, weather and household panel are held constant and only the occupancy time series varies, isolating the occupancy effect. |
| **Angle** | One of `A1` to `A10` or `A14` in section 4. |

## 9. Occupancy data sources beyond national statistics (prompts `T19` to `T38` only)

Added 2026-09-18. Ignore this section for `T01` to `T18`.

**Why.** Every paper in section 2 draws occupancy from the same class of source: a national time-use
survey (GSS, HETUS, ISTAT) joined to a national census. Those are public statistics, collected once
every five to ten years, from a sample of one or two diary days per person, with no measured
presence at all. Prompts `T19` to `T38` ask what **other** open or academically obtainable data
describe when people are at home, how many, and doing what, and whether any of it has been used for
building energy modelling. They scout sources; they do not choose the paper.

**What we already hold, so do not propose it as new:** Statistics Canada GSS time use (four cycles,
2005 to 2022), Canadian Census PUMF, NRCan SHEU 2019, HETUS national files for Spain, UK, Italy (and
France, held but excluded), ISTAT census. Everything else is new to us, including ATUS and MTUS,
which are named in `A3` but not yet used.

**Compute for this wave.** GPU nodes on the Concordia Speed cluster are free to us (section 3, item 5),
and are to be used once the subject is chosen. A source is therefore **not** ruled out because it is
large or heavy to process (billions of mobility pings, years of one-minute meter data, sensor
streams from thousands of homes). It is ruled out by access, licence, redistribution terms or bias.
Where processing cost matters, state it as a compute shape (records, storage, GPU or CPU hours,
labelled `INFERENCE`), never as a reason to drop the source.

**The four roles a source can play.** Every source row states which roles it can serve, and why.

| Role | Meaning |
|---|---|
| `R1` generate | The source itself yields per-person or per-household schedules that could drive a simulation |
| `R2` constrain | The source gives aggregate targets (share at home by hour, counts by area) that a generated population can be raked or calibrated to |
| `R3` validate | The source gives measured presence that a generated schedule could be scored against without having been fitted to it |
| `R4` change | The source records how presence changed over time (for example the work-from-home shift after 2020) at a frequency time-use surveys cannot |

**The data-source card.** In `T19` to `T38`, every row of Section F carries these columns, in this
order, in addition to the template's own: source name and custodian; country and geography;
years covered and whether it is still updated; unit (person, household, dwelling, device, grid cell,
area); **what occupancy variable it actually contains**, quoted from its documentation (presence,
count, motion events, activity code, trip times, load); temporal resolution; spatial resolution;
sample size; roles `R1` to `R4`; access route and **eligibility for a researcher at a Canadian
university**, quoted with the date checked; licence and **whether derived schedules may be
redistributed**, quoted; known selection bias (who owns the device, who answers the survey); one
verified example of its use in building energy research, or `NONE FOUND`.

**Extra hard rules for `T19` to `T38`.**
1. Paste the CrossRef-returned title beside every DOI in every table row. A row without a resolving
   identifier (DOI, arXiv ID, or a dataset landing page you opened) is not admitted to Sections C
   or F.
2. Our own papers are described only as section 2 describes them; never give one a title, a number
   or a result the brief does not state.
3. A dataset is `reachable` only if you opened its landing or download page on the date checked. A
   dataset described in a paper but not reachable is listed in Section G as `COULD NOT OPEN`.
4. Never call a source "open" unless its licence text says so. "Free for researchers on
   application" is `application`, not `open`. Terms of service that forbid scraping or
   redistribution are quoted, not summarised.
5. A source that cannot distinguish residential presence from any other presence (for example a
   count of phones in a grid cell) says so in its card; do not describe it as residential occupancy.
6. Proposals that would identify individuals, re-identify households, or scrape data against terms of
   service are out of scope. Say they exist if relevant and stop there.
7. (Added 2026-09-18 after `RT19`.) Write only your report, `RT<NN>_<topic>.md`. Never write a
   `VETTING_RT<NN>.md` note, never edit `README.md` or any other file, and never give your own report
   a verdict. Vetting is done by someone else, after you finish.


====================================================================================================
# PART 2 OF 3: RESPONSE TEMPLATE (_RESPONSE_TEMPLATE.md)
====================================================================================================

# Response template (the external assistant must follow this exactly)

Return **one Markdown file per prompt**, named `RT<NN>_<topic>.md` (for example
`RT01_field_map_llm_occupancy_ubem.md`), saved into `5J_docs_occ/DeepResearch/`, beside the prompt it
answers.

Sections A, B, G and H are required in every answer. Sections C to F are used where the prompt asks for
them; a prompt that does not need one says so, and you then write `not applicable to this prompt`
rather than deleting the heading. Keep the headings and their letters stable, because the responses are
read side by side.

This series scouts **research topics**, not engineering facts. The fabricable class here is therefore
different from earlier series: the danger is not an invented energy intensity but an **invented paper,
an invented funding call, an invented "gap"**, or a field map that flatters the asker. The controls in
Section G are written for that.

---

## Section A. Direct answer

Three to eight sentences. What the prompt asked, answered, before any table. If the honest answer is
that the topic is crowded, that the proposed angle is already published, or that the group's assets do
not support it, **say that in the first sentence**, not at the end.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|

One row per thing you want us to be able to cite. Every row needs a source. A row whose source is
"general knowledge" does not belong in this table; put it in Section G and label it as your own
assessment. For any **count, date, deadline, funding amount, version or quantity**, `Date checked` is
mandatory.

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|

Only works you actually opened. A work you know of but could not open is listed in Section G, not here.

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|

`no` is a permitted and useful value. Do not manufacture a gap by narrowing the angle until nobody has
done exactly that; say instead that the field is occupied.

## Section E. What this changes in our planning

Bullet list of the specific decisions, framings, or dropped ideas that follow, each tied to a Section B
or C row number.

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|

Datasets, benchmarks, code, calls for papers, special-issue calls, funding-programme documents. A
programme homepage or a search results page is **not** an answer; the row reads `NO RETRIEVABLE FILE`.

## Section G. Contradictions, gaps, open questions, and your own negative controls

Bullet list. Flag every place where two sources disagree, say which one we should adopt and why, and
name what you searched for and did not find.

Then answer these questions in plain sentences, always:

1. **Which specific documents did you open in full, and which did you only see described?** List them
   separately. If the count of documents you opened in full is zero, say zero.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?** Name the
   condition. A report that cannot reach a negative under any circumstance cannot fail.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?** If the
   answer is none, explain why the field has left every angle we named untouched, because that is the
   less likely state of the world.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?** Re-check your own
   Section C against the CrossRef titles you actually retrieved before answering.

Include here any citation defect you uncover: a DOI that resolves to the wrong paper, an arXiv ID with
no artefact, a funding call whose page no longer exists.

## Section H. Full reference list

Numbered, with title, author or issuing body, year, version or edition, and URL or stable identifier.
Mark each entry Tier 1, 2 or 3. Cross-reference the numbers used in Sections B, C and F.

For each entry state explicitly whether you **read the full text**, **read only the abstract or
summary**, or **could not open it**. For every DOI, give the title that
`https://api.crossref.org/works/<DOI>` actually returned. For every arXiv entry, give the arXiv ID, the
version you read, and whether it has since appeared in a peer-reviewed venue.

No em dashes and no en dashes anywhere in the output text.


====================================================================================================
# PART 3 OF 3: THE TASK (T12_contradictions_and_ranking.md)
====================================================================================================

# T12. Contradictions and ranking of the surviving angles

Paste `00_MASTER_BRIEF.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh
session. **Run alone.** Written 2026-09-19 by the manager, after every report `RT01` to `RT38` was
vetted.

## Why this prompt looks different

Thirty-eight reports have been vetted. In the last rounds the page logs were honest: every logged
excerpt was found again on its page. The failures were all in the text written after the fetching:
papers called "read" when only their CrossRef metadata was fetched, quotes that are on no page,
numbers that contradict the PDF the tool itself downloaded, log line numbers that point at the wrong
fetch, and self-grades ("verified") that the log contradicts.

So this prompt gives you the checked facts as a numbered table (`P1` to `P40` below) and asks
numbered questions. You write no free landscape. **Every sentence you write that states a fact ends
with a tag**:

* `[Pn]`: the fact is row `Pn` of the table below, used as it is written there;
* `[Ln]`: the fact is on the page logged at line `n` of your `RT12_pages.log` (lines counted from 1
  in the final file); several tags are allowed, as `[L12, L40]`;
* `[BRIEF s.n]`: the fact is in section `n` of the master brief;
* `[INFERENCE]`: your own reasoning, not a fact.

A factual sentence with no tag is struck by the vetter. A tag that points at a line whose excerpt does
not support the sentence is struck, and more than five such tags void the report.

## Rules (they win over the brief and the template where they differ)

* Read only three files: `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and this prompt. Open no other
  file in the project: no `RT` report, no `VETTING_*.md` note, no `*_round1.md`, nothing in `_scan/`.
* Write only two files, in `5J_docs_occ/DeepResearch/`: `RT12_contradictions_and_ranking.md` and
  `RT12_pages.log`. Creating, editing, renaming or deleting any other file in the project voids the
  report. Scratch scripts go outside `C:\Users\o_iseri\Desktop\GSSCanada\`. Scripts may fetch and
  log; no script may write report text.
* **Finish the log before you write the report**, and do not add to the log afterwards. Then the line
  numbers you cite are final.
* The page log has one line per page, API call or search query, written when you open it,
  tab-separated: time as `YYYY-MM-DDTHH:MM:SS`, the full URL or query string, the HTTP status, and
  about 200 characters copied verbatim from the body as returned. Log every call, including the ones
  you make only to look around.
* A page counts as opened only if it returned 200 **and** its logged excerpt is readable text of the
  thing you cite. An error, a bot block, an image, a script shell or a login page is `COULD NOT
  OPEN`, never "opened" or "read". If a page matters and the excerpt is boilerplate, fetch the part of
  the page that holds the text you need and log it as its own line.
* **A CrossRef record proves that a work exists, not what it says.** Any sentence about what a work
  did, found or measured needs a logged abstract or full text: the OpenAlex abstract
  (`https://api.openalex.org/works/https://doi.org/<DOI>`, rebuild `abstract_inverted_index`), the
  arXiv abstract page, or the publisher's page with the abstract in the excerpt. If you have only the
  CrossRef record, write `TITLE ONLY` and say nothing about the content. If OpenAlex returns 429,
  wait and retry, and log each try.
* Every DOI you give carries, beside it, the title CrossRef returns, and the author list pasted from
  that CrossRef record. If CrossRef lists two authors, you list two. One work carries one DOI in every
  section.
* A number is written only if it appears on a logged page, with its table or page where the source
  has one. Copy it exactly; never round, sum or recompute a published figure.
* Every "no study", "not found", "open" or "unclaimed" lists its queries beside it, each with its log
  line. Say it as "these queries found nothing", never as "none exists".
* Do not split the difference. Where two claims disagree, one of them is right, both are wrong, or
  you could not open the source. Averaging, "somewhere between" or "both may be valid" is not an
  answer.
* Do not introduce a new angle. The angles are the brief's `A1` to `A10` and `A14`, plus `A11`,
  `A12`, `A13`, defined in `P33` to `P35`.
* Do not grade your own report: never write "verified", "confirmed", "definitive", "comprehensive"
  or "without exception" about your work. The log is the evidence.
* Say nothing about our own models, results or numbers beyond what brief section 2 states. Name no
  individuals connected to the fellowship programmes. Never propose a change to the 4J pre-registered
  gate, null or threshold. No em dashes and no en dashes, in the report or the log.

## The checked facts (filled by the manager, 2026-09-19)

Each row is a fact that a checker found at its source. The last column names the vetting note that
holds the check; you may not open it, and you do not need to. "Pointer" means the work exists and is
correctly identified, and nobody has read it for us.

### Angles already decided (do not rank these; do not reopen them without a logged source)

| # | Fact | Held in |
|---|---|---|
| P1 | `A1` is closed as a paper, except an error-diagnostician form with a scripted ablation. Prior work with a logged abstract: Geo2UBEM (Wu et al., arXiv 2026), an autonomous multi-agent UBEM framework calibrated on six Purdue campus buildings (101,170 m2) | `VETTING_RT03`, `VETTING_RT02` |
| P2 | `A10` is closed as a paper; at most a short communication or an appendix. Kontokosta and Tull 2017 is the one checked empirical test of area weighting. Lim and Koo 2026 benchmark 3,001 buildings in Seoul (abstract) | `VETTING_RT16`, `VETTING_RT02` |
| P3 | `A5` is dropped: no report produced a supporting row for it | ideas document, ledger |
| P4 | `A3` is closed as a "beat the null" paper. What remains is a "cross-national pretrained generative sequence model" framing on corpora we can hold; the "foundation model" label is closed. MTUS and ATUS are open to a Canadian university; the Eurostat scientific-use files are closed to us | `VETTING_RT13`, `VETTING_RT07` |
| P5 | A hybrid "donor plus edit" generator was recommended by one report on rows that were struck or author-reported; it is a claim to test, not a finding | `VETTING_RT13` |

### Facts about the open angles

| # | Fact | Held in |
|---|---|---|
| P6 | `A2`: overheating assessed on static archetypes is taken; `A2` is open only with a presence module. The report returned NOT FOUND for heat-responsive presence and for indoor overheating validated at dwelling level | `VETTING_RT05` |
| P7 | `A2`: address-level income and bills are reachable only through the research data centres, which limits an exposure result to tract-level aggregation | `VETTING_RT10` |
| P8 | Heat-responsive presence at population scale: three logged queries found nothing. Weak evidence of absence | `VETTING_RT04` |
| P9 | A building-energy model coupled to time-activity data for heat exposure, and an energy-poverty indicator that uses time at home: logged queries found nothing for either. Weak evidence of absence | `VETTING_RT08` |
| P10 | British Columbia, summer 2021, Coroners review "Extreme Heat and Human Mortality: A Review of Heat-Related Deaths in B.C. in Summer 2021", 619 deaths: 98 % of heat injuries occurred indoors (pages 5, 17); 67 % aged 70 or older (page 5); 56 % lived alone (page 5, Table 8); 452 of 619, 73.0 %, in private residences (Table 7, page 38); air conditioning present 7.4 %, absent 66.9 %, unknown 24.1 % (Table 11, page 39) | `VETTING_RT08` |
| P11 | Chicago, July 1995, Semenza et al. 1996 (New England Journal of Medicine, DOI 10.1056/NEJM199607113350203), abstract: not leaving home each day, odds ratio 6.7; a working air conditioner, odds ratio 0.3 | `VETTING_RT08` |
| P12 | Pointers: Multnomah County 2021 final heat report, 68 of 72 (94 %) died in their own residence (page 10); Ballester et al. 2023, Nature Medicine, 61,672 heat-related deaths in Europe in summer 2022 (abstract) | `VETTING_RT08` |
| P13 | `A4` is open at the intersection of future population, future weather and stock change; fewer than five studies were found, and none with demographic occupancy. Its cost is a full factorial run matrix and a hindcast. No UBEM hindcasting study was found. Reyna and Chester 2017 and Sandberg et al. 2016 are correctly identified | `VETTING_RT14` |
| P14 | `A4`: the future peak-demand claim depends on an air-conditioning uptake assumption | `VETTING_RT05` |
| P15 | `A6`: Katia et al. 2023 and Heidelberger and Rakha 2022 (socioeconomic data in UBEM) are correctly identified pointers; Walker and Day 2012 and Sovacool and Dworkin 2015 (energy justice) likewise | `VETTING_RT08` |
| P16 | `A7` is partly taken for material stock (Schmid 2025 resolves). `A7` breaks the series signature (no occupancy, no time use). It is feasible on paper, with a fallback to categorical classification | `VETTING_RT01`, `VETTING_RT11`, `VETTING_RT10` |
| P17 | `A7`: three logged CrossRef phrasings found no precedent for records reading with abstention feeding a stock model. Weak evidence of absence | `VETTING_RT02` |
| P18 | `A7` pointers: Zhang et al. 2023, arXiv:2311.08535, uses language models to process three open municipal building datasets (abstract). Identity only: Pan et al. 2026 (DOI 10.1016/j.autcon.2026.106791), Gunay et al. 2023 (DOI 10.1016/j.buildenv.2023.110848, municipal housing permit data for the Canadian stock), Borrotti 2024 (DOI 10.3390/en17174348, conformal prediction for heating and cooling load in building simulation), Angelopoulos and Bates 2023 (DOI 10.1561/2200000101) | `VETTING_RT17` |
| P19 | `A7` data: Toronto building permits are under the Open Government Licence (Toronto); England EPC data under the Open Government Licence v3.0 | `VETTING_RT17` |
| P20 | `A8`: Shirzadi et al. tested seven NECB 2020 reference models (abstract). Open building-level disclosure data was not found for Montreal or Calgary. Montreal by-law 21-042 covers buildings of 2,000 m2 or more, or 25 or more homes; Ontario O. Reg. 506/18 covers buildings of 50,000 sq ft or more | `VETTING_RT02`, `VETTING_RT16`, `VETTING_RT34` |
| P21 | `A9` is open on two terms only: occupancy that varies with who lives there, and district scale. Searches found no survivability study with dynamic or demographic occupancy (three reports agree) | `VETTING_RT15`, `VETTING_RT11`, `VETTING_RT01` |
| P22 | `A9` rows that survived: Sheng et al. 2023 and Sailor et al. 2019, both with constant occupancy, quoted. Pulkkinen et al. 2026 (Energy and Buildings, cold-climate outage) is the nearest single-building prior and must appear in any `A9` novelty claim. A six-climate-zone US outage study of single-family homes (abstract) | `VETTING_RT15`, `VETTING_RT11`, `VETTING_RT02` |
| P23 | `A9`: Texas winter storm Uri, through Pecan Street, is the one measured-outage route found. Habitability references whose pages resolve: LEED IPpc100, WHO, RELi, the National Building Code; Toronto Green Standard 72-hour credit as a pointer | `VETTING_RT15` |
| P24 | `A9` winter arm: a Concordia winter-outage study of multi-unit residential buildings was claimed (Baba et al. 2022, Journal of Building Engineering); its DOI resolved to a precast-column paper, so whether such a study exists is unknown | `VETTING_RT15` |
| P25 | Rows claimed for `A9` that failed identity: Sun et al. 2020 (DOIs 10.1016/j.buildenv.2020.107068 does not resolve, 10.1016/j.buildenv.2020.106884 resolves to a different paper); Baniassadi et al. 2018 (DOI 10.1016/j.buildenv.2018.06.019 resolves to a body-heat-loss paper) | `VETTING_RT15`, `VETTING_RT11` |
| P26 | `A11`: an idea whose effect sizes must be measured by us; the zoning percentages that one report attributed to Cerezo Davila et al. 2016 and Dogan and Reinhart 2017 are unknown | `VETTING_RT06` |
| P27 | `A12`: open as a short protocol paper built from 4J's privacy audit as pre-registered; no standard audit exists in the literature searched; no privacy guidance was found in building-energy journals | `VETTING_RT18` |
| P28 | `A13`: no vetted row supports it | ideas document, ledger |
| P29 | `A14`, form 1: smart-thermostat presence as a source for, and check on, time-use schedules. Narrowed: done for Canada by Doma, Prajapati and Ouf 2024 (DOI 10.1016/j.buildenv.2024.111713) and for the US by Jung, Wang, Hong and Jazizadeh 2023 (DOI 10.1016/j.buildenv.2023.110628). Open: splits by household and dwelling type, arrival and departure times, matching the homes to the Canadian population. The ecobee licence terms were never read | `VETTING_RT20` |
| P30 | `A14`, form 2: Doma's comparison is hourly and in aggregate: Canadian time-use survey mean daily occupied share 71 %, thermostat profiles 68 %, 8,880 of 22,940 Canadian homes; the thesis says its aim was representativeness, "rather than to verify accuracy by quantifying the match"; the dataset carries no socio-demographic information. The energy consequence of the difference is unassessed | `VETTING_RT32` |
| P31 | `A14`, form 3: activity-based travel-model populations as the occupancy engine of a UBEM. Done abroad (a 2026 UrbanSim, POLARIS and CityBES co-simulation; Binder et al. 2020 for Tokyo; Yamaguchi et al. 2023 for Japan). Open: a Canadian version. Toronto model code is GPL-3.0; whether a Toronto or Montreal synthetic population may be used is unknown | `VETTING_RT27` |
| P32 | `A14`, form 4: open half-hourly feeder data exists for UK Power Networks (CC BY 4.0, free after registration). Hydro-Quebec publishes one hourly file for 3 Montreal substations, 64,605 rows, 2022-01-01 to 2024-06-30, CC BY-NC 4.0, no per-home rows, no presence field. Other `A14` forms are routes only | `VETTING_RT23` |

### Definitions of the three new angles (from one report; do not change them)

| # | Angle |
|---|---|
| P33 | `A11` zoning bias benchmark: what core-and-perimeter zoning does to a residential stock's simulated results relative to dwelling-level division with no core zone, measured on our own engine |
| P34 | `A12` privacy-utility and release protocol: a short paper on releasing a generator trained on survey microdata, built from 4J's pre-registered membership-inference audit and the partial release that followed it (brief section 3) |
| P35 | `A13` counterfactual shock synthesis: using the generator to synthesise occupancy under a shock that no survey observed |

### Programme facts

| # | Fact | Held in |
|---|---|---|
| P36 | UC Berkeley's Climate Futures fellowship is listed under the UC President's postdoctoral programme; that programme's deadline is 1 November 2026. The Berkeley research-office page and the Toronto AI in Science page return 403, so no criterion from either is known | `VETTING_RT09` |
| P37 | NSERC postdoctoral deadline 17 October; the page states that the research must be significantly distinct from, or go significantly beyond, the doctoral thesis | `VETTING_RT09` |
| P38 | MSCA postdoctoral fellowships: the researcher must not have lived or worked in the host country for more than 12 months in the 36 months before the deadline | `VETTING_RT09` |
| P39 | The Digital Futures postdoctoral page carries the context labels Digitalized Industry, Rich and Healthy Life, Smart Society and the themes Cooperate, Learn, Trust | `VETTING_RT09` |
| P40 | Every 2026 programme deadline falls before any possible 5J preprint, so 5J serves the 2027 cycle | manager's state note |

### Contradictions the manager has already settled (do not reopen)

* The Berkeley programme: the brief (section 5) and `P36` agree that the Climate Futures fellowship
  runs through the UC President's programme.
* NSERC: an earlier report said the thesis-distinctness rule was replaced; `P37` shows it on the
  programme's own page.
* `A2` is defined as in brief section 4. Two earlier reports merged `A2` with `A6`; that merged angle
  is not ranked.

## Part A. The open contradictions and unchecked claims

For each question: open the deciding source, log it, and give one verdict. Answer as a table with the
columns: question | verdict | the value or text that decides it, copied | log line(s) | what it
changes for which angle.

Verdict words: `FIRST CLAIM`, `SECOND CLAIM`, `NEITHER` (give the right value), `EXISTS` / `NOT
FOUND` (with its queries), or `COULD NOT OPEN` (with the URLs tried).

* **Q1. pyepwmorph.** One report said version 2.0.0 at the repository `justinfmccarty/pyepwmorph`;
  another said 2.0.1 at `intelligent-environments-lab/pyepwmorph`. Open the package's PyPI page and
  both repository URLs. Which version is current, where is the code, and under which licence?
* **Q2. Annex 79 and its successor.** One report said IEA EBC Annex 79 concluded in 2024; another
  named Annex 95 as a 2024 to 2029 successor, titled "Human-centric Building Design". Open the IEA EBC
  pages for both annexes. Give Annex 79's stated end and Annex 95's stated title, period and scope, as
  written on the pages.
* **Q3. The winter-outage competitor (decides the novelty of `A9`'s winter arm).** Does a published
  study exist of indoor conditions in Canadian (in particular Montreal) multi-unit residential
  buildings during a winter power outage? `P24` is the unverified claim. Search CrossRef and OpenAlex
  with at least three phrasings, log each, and for every candidate give the DOI, the CrossRef title
  and a logged abstract. Say whether any candidate varies occupancy.
* **Q4. `A9`'s rows survive their CrossRef titles.** For each work in `P22`, resolve it through
  CrossRef (log the query and the record), paste its title and authors, and fetch its abstract.
  Quote the abstract sentence that states how occupancy was treated, or write `NOT IN ABSTRACT`. For
  the two failed rows in `P25`, search for the real paper by title words and authors; give its DOI
  and CrossRef title, or `NOT FOUND`.
* **Q5. Occupancy in survivability studies.** Is there any published passive-survivability or
  thermal-autonomy study, at building or district scale, whose occupancy varies over time or by
  household (not a fixed schedule)? Search at least four phrasings (for example: passive
  survivability occupancy schedule; thermal autonomy power outage occupants; habitability outage
  household composition; outage indoor temperature occupant presence). For every hit you cite, a
  logged abstract. This tests `P21`.
* **Q6. Heat exposure with time-use presence.** Is there any published study that combines
  time-use or time-activity presence with a building thermal model to estimate indoor heat exposure
  of residents, at any scale? At least four phrasings, logged; a logged abstract for every hit. This
  tests `P6`, `P8` and `P9` together.
* **Q7. Language models reading building records.** Is there any published study in which a
  language model extracts building attributes or renovation state from permits, certificates or
  cadastral text **and** reports abstention, prediction sets or calibrated uncertainty? At least four
  phrasings, logged; a logged abstract for every hit. Then open the abstracts of Gunay et al. 2023
  and Borrotti 2024 (`P18`) and say, from the abstract only, what each did. This tests `P16` to `P18`.
* **Q8. Demographic occupancy in future scenarios.** Is there any published district or stock study
  that changes population and household composition, future weather and the building stock
  together? At least three phrasings, logged; a logged abstract for every hit. This tests `P13`.
* **Q9. The zoning effect sizes behind `A11`.** Resolve Cerezo Davila et al. 2016 and Dogan and
  Reinhart 2017 through CrossRef (title words and authors), fetch their abstracts, and copy any
  number they give for the effect of zoning simplification on simulated energy use. If the abstract
  gives none, `NOT IN ABSTRACT`. This tests `P26`.
* **Q10. The ecobee Donate Your Data terms.** Find and open the page that holds the terms under which
  researchers receive the data. Copy the clauses on publication of derived results and on
  redistribution. If the terms are behind a form or a login, `COULD NOT OPEN`. This decides the
  licence gap in `P29`.
* **Q11. The BuildOcc record.** Earlier reports cited "BuildOcc" as arXiv:2609.02729 with a Zenodo
  record 10.5281/zenodo.21192895; the Zenodo DOI returned 404 in three checks. Open the arXiv
  abstract page and the Zenodo DOI. Does it exist, what is its title, and does its abstract describe
  an occupancy generator? This decides whether `A3` has an unlisted competitor.

## Part B. One ranking of the open angles

Rank these eleven angles, and only these: `A2`, `A3` (in the narrowed form of `P4`), `A4`, `A6`,
`A7`, `A8`, `A9`, `A11`, `A12`, `A13`, `A14` (its best form among `P29` to `P32`, named). `A1`,
`A5` and `A10` are not ranked (`P1` to `P3`).

**The rule, stated here and applied without exception:**

S = 0.40 G + 0.30 F + 0.20 D + 0.10 P, with each part scored on the levels below and nowhere in
between.

* G, openness (0, 20 or 40): 40 if Part A's search for the angle's own combination found nothing
  **and** the nearest works (with logged abstracts) each lack a named part of it; 20 if the
  combination is partly done, or if the only evidence of openness is a search with no logged
  abstracts behind its nearest works; 0 if a work with a logged abstract does the combination.
* F, fit with what we hold (0, 20 or 30): 30 if the brief's section 3 assets cover every input; 20
  if one input from the "Asset it lacks" column of brief section 4 must be obtained; 0 if an input is
  blocked (closed data, a licence that forbids publication, or no route found).
* D, defensibility (0, 10 or 20): 20 if the strongest reviewer objection is answered by an asset we
  hold or a result a reader could check; 10 if it can only be qualified; 0 if it is fatal.
* P, programme fit (0, 5 or 10): from brief section 5 and `P36` to `P40` only. 10 if the angle is
  the drafted or live topic of two or more programmes; 5 if of one; 0 if of none. Programme themes
  in the brief are the researcher's framing, not programme criteria; say so where you use them.

Answer as one table with the columns: rank | angle | G | tag for G | F | tag for F | D | tag for D |
P | tag for P | S | the objection used for D, in one sentence | stand-alone paper or a module of
which angle. Every score cell carries its tag (`[Pn]`, `[Ln]`, `[BRIEF s.n]`); a score whose only
tag is `[INFERENCE]` must be the lower of the two levels it sits between, and say so.

Then answer, one line each:

* **B1.** Does the top three change if every G of 40 that rests on Part A searches alone is set to
  20? Give the new top three.
* **B2.** Does the top three change if P is dropped? Give it.
* **B3. The flattering direction.** Four earlier reports put `A9` first with maximal scores, and the
  consensus was partly inherited from one report to the next. If `A9` ranks first here, name the
  Part A rows (with their log lines) that put it there, other than the agreement of earlier reports.
  If an angle the brief describes warmly ranks first, say which evidence other than that warmth put
  it there.
* **B4.** For the top three, the one thing that, if found next month, would drop each angle by one
  G level.

## Deliverable

Use the template's sections as follows.

* **Section A**: the ranked list in eleven lines, each with S, then one line saying which Part A
  verdicts changed a fact in the table above.
* **Section B**: Part A, the answer table for Q1 to Q11.
* **Section C**: only the works you cite in Part A, one row each: DOI or arXiv ID with the CrossRef
  (or arXiv) title beside it, authors pasted from the record, the log line of the record, the log
  line of the abstract or `TITLE ONLY`, and the Part A question it answers.
* **Section D**: the Part B table and B1 to B4.
* **Section E**: for the top three only, what each changes in our planning, tagged.
* **Section F**: the artefacts from Q1, Q2, Q10 and Q11: URL, HTTP status, log line.
* **Section G**: your negative controls: (1) every query behind every `NOT FOUND`, with log lines;
  (2) the list of works whose abstract you fetched, each with its log line, and the list of works
  you know by CrossRef record only; (3) any tag you could not place, and the sentence you struck
  because of it.
* **Section H**: the full reference list, CrossRef titles beside the DOIs.

====================================================================================================
# END OF THE THREE PARTS. Now do Part 3.
====================================================================================================
