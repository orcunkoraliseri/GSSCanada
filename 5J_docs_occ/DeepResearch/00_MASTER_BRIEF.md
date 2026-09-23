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

## 10. The chosen form of `A7`: building records as input, and what can check them (prompts `T39` to `T42` only)

Added 2026-09-22. Ignore this section for `T01` to `T38`.

**The subject.** The fifth paper is now `A7` in a climate form. An open-weight language model, run on
our own GPUs, reads the free text of Canadian municipal building permits (French and English) and
recovers, for each residential building, its retrofit and cooling state: heat pump, air
conditioning, insulation, window replacement, heating fuel change. It gives a set of possible answers,
or abstains, when the text is too thin, with conformal coverage per archetype. That uncertain stock
then feeds a Canadian building energy model with time-use occupancy (the GSS pipeline of section 2),
to show how much the unknown retrofit and cooling state changes demand and indoor conditions for the
people actually at home. `A9` is no longer the 5J subject; do not discuss it.

**What we already know, so do not restate it as a finding.** Montreal and Toronto publish building
permit files on their open-data portals; we are checking those two files ourselves. European energy
certificate registers are already structured, so they are out of scope here.

**The four roles a record source can play.** Every Section F row states which roles it can serve.

| Role | Meaning |
|---|---|
| `L1` input text | Free text a model would read to infer retrofit or cooling state (a permit description, an assessment note, a listing text) |
| `L2` label | Per-building or per-dwelling truth that a model's answer can be scored against (an energy audit record, a rebate record, a measured inventory) |
| `L3` aggregate check | Counts or shares by area or year (for example the share of homes with air conditioning by city) that the model's totals can be compared with, without per-building linkage |
| `L4` link | A key that joins a record to a building footprint or to another source (civic address, lot or roll number, coordinates) |

**The record-source card.** Every Section F row carries, in this order: source name and custodian;
city or province; years covered and whether it is still updated; unit (permit, dwelling, building,
lot, address); total row count as shown on the page; **the names of the free-text fields, quoted from
the schema or data dictionary**; language of that text; whether residential records can be
separated, and by which field; any structured work-type field and its codes relevant to heat pumps,
air conditioning, insulation, windows or heating fuel; roles `L1` to `L4`; link key; access route and
eligibility for a researcher at a Canadian university, quoted with the date checked; licence name
copied from the licence page, and whether derived per-building labels may be redistributed, quoted;
known bias (for example: work that needs no permit, such as a window air conditioner, never appears);
one verified example of its use in research, or `NONE FOUND`.

**Extra hard rules for `T39` to `T42`.** Rules 1 to 7 of section 9 apply unchanged, and:
1. Read only `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and your one prompt. Open no other file in
   the project.
2. Write only two files, in `5J_docs_occ/DeepResearch/`: `RT<NN>_<slug>.md` and `RT<NN>_pages.log`.
   Any other file created, edited, renamed or deleted in the project voids the report. Scratch
   scripts live outside `C:\Users\o_iseri\Desktop\GSSCanada\`. No script may hold report text.
3. The page log is written **by the fetch itself, at the time of each fetch**: one tab-separated line
   per page, API call or search query, with time `YYYY-MM-DDTHH:MM:SS`, the full URL or query, the
   HTTP status, and about 200 characters copied verbatim from the body. Built-in web searches are
   logged too, with the query string. A log rebuilt afterwards from a list of URLs voids the report.
   Finish the log before writing the report and do not add to it afterwards.
4. Every sentence in the report that states a fact ends with a tag: `[Ln]` (the page at log line `n`
   holds it), `[BRIEF s.n]`, or `[INFERENCE]`. A factual sentence with no tag is struck; more than five
   tags that do not support their sentence void the report.
5. A dataset page counts as opened only if it returned 200 and its excerpt is readable text of that
   dataset. A field name, row count or licence counts only if it is on a logged page. Where the schema
   is only in a downloadable file, download its first rows or its dictionary and log that call.
6. A CrossRef record proves a work exists, not what it did. Any sentence about what a study did needs
   a logged abstract or full text; otherwise write `TITLE ONLY`.
7. Every "not found" lists its queries with their log lines. Say "these queries found nothing", never
   "none exists". No self-grades: never write "verified", "confirmed" or "complete" about your own work.
