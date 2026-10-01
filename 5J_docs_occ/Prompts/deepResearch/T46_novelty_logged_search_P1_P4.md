# T46. Logged search: occupancy time series as a surrogate input (P1) and time-use diaries feeding a learned energy model (P4)

Paste `00_MASTER_BRIEF_5J.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh session. **Run it alone.**
Written 2026-10-01 by the 5J manager (Step 8A; owed since O-2). Your files are `RT46_novelty_logged_search_P1_P4.md` and
`RT46_pages.log` (one line per page, record or file you opened: URL, what it was, full / abstract / title, date). Save both in
this folder.

## Why we are asking

The paper may write "first" or "to our knowledge" only if a LOGGED search finds nothing closer. RT45 (2026-09-28) gave verdicts
of "nobody has done this" with zero queries logged, so its verdicts cannot be used. This round is narrower and is judged by its
log, not by its conclusions. We already know the works listed under "Known" and will check that you find them.

## The two parts

* **P1.** A learned surrogate, metamodel or emulator of a building energy SIMULATION (EnergyPlus, TRNSYS, IDA ICE, DOE-2,
  Modelica, ESP-r or similar) whose inputs include an occupancy, presence, activity or schedule TIME SERIES (hourly or finer),
  not only a scalar (density, hours per day) or a schedule name.
* **P4.** Time-use diaries (HETUS, MTUS, ATUS, UK TUS, a national time-use survey) used as an INPUT to a trained model that
  predicts building energy use, as opposed to a model that only generates occupancy or activity sequences.

## Known (positive controls; describe each in two sentences from the registry record, then say whether your search found it)
* `10.26868/25222708.2015.2655` (He et al. 2015, paired occupancy design, no surrogate).
* Park and Park 2023 (a surrogate scored on retrofit differences; find the DOI from the registry).
* Pan et al. 2024, Journal of Building Performance Simulation, bi-LSTM urban building energy surrogate (find the DOI).
* `10.2172/1817464` (Li, Bae and Im 2021, ORNL report). We still need a DIRECT URL to a file of the full report and its own
  words (quoted, with page) on what the surrogate's inputs are. Write `NOT FOUND` if you cannot open it; never paraphrase a page
  you did not open.

## What we need

1. **The log.** For each part, at least 12 distinct queries across at least 4 sources (OpenAlex, Semantic Scholar, Crossref,
   Google Scholar or arXiv, plus Scopus or Web of Science if you can reach them), each with: source, exact query string,
   date, number of hits reported by the source, number of results you screened, and the IDs of the results you kept. Queries
   alone and combined: "surrogate", "metamodel", "emulator", "machine learning", "deep learning", "LSTM", "transformer",
   "EnergyPlus", "building energy simulation", "occupancy", "occupant", "presence", "schedule", "time series", "time use",
   "time-use survey", "diary", "HETUS", "ATUS", "MTUS", "activity", "residential", "dwelling", "household".
2. **Nearest works per part** (up to ten per part, 2010 to today): one Section C row each with authors and year from the
   registry record, venue, DOI or arXiv ID, the engine, the learned model, its INPUTS quoted or paraphrased with page or
   section, outputs and time step, how it was scored, whether occupancy is a time series input, `Read:` full, abstract or
   `TITLE ONLY`.
3. **Verdict per part:** done / partly done / open as far as searched, naming the Section C row that decides it, marked
   `[INFERENCE]`; an "open" verdict lists the log lines of its queries: "these queries found nothing", never "no such work".
4. **Unread items from RT45 vetting:** Westermann and Evins 2019 (review of surrogates in building design; follow its reference
   list for P1 and say which entries you checked), the Vosoughkhosravi review, CityTFT 2025, Govindarajan 2025 (full text:
   are occupancy schedules an input, and as what?).

## Hard constraints specific to this prompt
* Positive controls: the Known works must be found by your own logged queries or named as not found by them (that is a
  weakness of the search, say so in Section G). Misdescribing a Known work fails the round.
* Negative control: if both parts come back "open", the first sentence of Section A says the search was probably too weak.
* Before `TITLE ONLY`, try at least one open copy (publisher page, arXiv, Semantic Scholar or OpenAlex abstract) and log it.
* No accuracy or speed-up number unless quoted with its page. No em dashes and no en dashes anywhere.

## Deliverable
**Section A** (at most six sentences): is there a work that already feeds an occupancy time series (P1) or time-use diaries
(P4) into a learned model of simulated building energy, and which one is closest. **Section B**: facts we may cite.
**Section C**: Known works, then P1 and P4 rows. **Section D**: verdicts. **Section E**: what the framing should change.
**Section F**: the ORNL file link (or NOT FOUND) with the quoted input list. **Section G**: the full query log table, controls,
queries that found nothing, works you could not open, the four standard questions. **Section H**: full references.
