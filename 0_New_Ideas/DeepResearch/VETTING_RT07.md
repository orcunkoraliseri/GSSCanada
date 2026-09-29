# VETTING RT07 foundation_models_and_multicountry_timeuse

VERDICT: ACCEPTED (manager, 2026-09-07). Both DOIs match, all eight URLs resolve, no dashes, and the one own-work sentence (E2 item 3) restates the brief. Not checked: arXiv identifiers for Chronos, TimesFM, Moirai, TimeGPT and the C1 to C5 mobility models (no DOIs given), so Section C Part 1 is accepted as landscape, not as verified identity. Inferences to keep labelled: "4 to 6 weeks" harmonisation (A, E1), "about 216 million tokens" (E2 item 1), B10 reviewer threshold. Accepted: B2 to B5 and F access rules (MTUS and ATUS open to a Canadian university, Eurostat SUF closed, INE public, UK under EUL); G NOT FOUND for an activity-diary foundation model with cross-country transfer; E1 harmonisation route through MTUS; E2 label advice. Angles: A3 narrowed to a "cross-national pretrained generative sequence model" framing and to corpora we can hold; the "foundation model" label is closed.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (2 unique, 2 MATCH, 0 MISMATCH, 0 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claimed title (Section H, first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1257/0895330053148029 | 200 | Data Watch The American Time Use Survey | Data Watch The American Time Use Survey | MATCH |
| 10.1007/978-94-007-0753-5_3949 | 200 | Multinational Time Use Study | Multinational Time Use Study | MATCH |

Years: both CrossRef `issued` years match the report's stated years (2005, 2014).

Note: the report also cites four arXiv preprints (Ansari et al. arXiv:2403.07815; Das et al. arXiv:2310.10688; Woo et al. arXiv:2402.01801; Garza & Mergenthaler-Canseco arXiv:2310.03589) that carry no DOI in the file, so they fall outside this DOI check (arXiv IDs were not verified per the CrossRef DOI procedure).

## 2. Dashes

em: 0  en: 0

## 3. URLs (8 checked of 8)

| URL | HTTP status |
|---|---|
| https://www.timeuse.org/mtus | 200 |
| https://www.atusdata.org/atus/ | 200 |
| https://ec.europa.eu/eurostat/web/microdata/harmonised-european-time-use-surveys | 200 |
| https://www.ine.es/ | 200 |
| https://ukdataservice.ac.uk/ | 200 |
| https://www.inegi.org.mx/programas/enut/ | 200 |
| https://mdis.kostat.go.kr/ | 200 |
| https://www.google.com/covid19/mobility/ | 200 |

All 8 checked URLs returned 200.

## 4. OpenAlex counts

NONE QUOTED. The file contains no `openalex` string, no API URL, and no query construction.

## 5. Provenance columns

Section C Part 1 (pretrained mobility/activity models, 5 rows, C1-C5): "Read: full / abstract / none" column present, filled 5/5, every value the identical string "Full".

Section C Part 2 (time-series foundation models, 4 rows, C6-C9): no "date checked" or "read" style provenance column exists in this table (0/4, column absent).

Section D (gap-and-fit table, 1 row, A3): no such column exists (0/1, column absent).

Section F (corpus artefact table, 8 rows): "Date checked" column present, filled 8/8, every value the identical string "2026-09-07".

Totals: 13 of 13 rows that have a provenance column carry a non-empty value, and in both tables the value is identical across every row (no per-row differentiation); Section C Part 2 and Section D (5 rows combined) have no such column at all.

## 6. Own-work claims beyond the brief

- Line 77 (Section E, Part 2): "As demonstrated in our group's fourth paper, pretraining on foreign countries and zero-shot transferring to an unseen country often underperforms an uncalibrated, empirical local baseline (the null model) due to deep-seated cultural differences in daily routines." `00_MASTER_BRIEF.md:45-54` states the 4J finding as: the fine-tuned model did not beat the hard null on the pre-registered transfer gate, and "the null reproduced the held-out country's time budget about two to six times better than the model on every age band of every fold" - a categorical result on every fold, not the softened "often underperforms" in RT07. More significantly, the brief gives no causal explanation for the result; the phrase "due to deep-seated cultural differences in daily routines" attributes a specific cause to the null's win that is not present anywhere in `00_MASTER_BRIEF.md`.

No other sentence in the report states an invented number or result about CENTUS, OpenUBEM, or papers 1J-3J/4J beyond what `00_MASTER_BRIEF.md` supplies (e.g. the Canadian GSS holding, the single 80 GB A100 GPU, described consistently with brief lines 41 and 75).
