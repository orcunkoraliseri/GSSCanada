# Chapter 1 (Introduction) — Deep-Research Brief Pack

**Document type:** Deep-Research briefs for a web-based LLM (ChatGPT Deep Research / Gemini Deep Research / Perplexity / Claude) · **Status:** ready to run · **Date:** 2026-06-11
**Purpose:** Chapter 1 is the most reference-heavy chapter. The five briefs below gather and *verify* the external literature behind the introduction's funnel (§1.1 performance gap → §1.2 two tracks + gap matrix → §1.3 non-stationarity/WFH → §1.5 contributions framing), returning resolvable DOIs and the exact quantitative claim each source supports.

**How to use (Deep Research mode):** Each `DR-I#` is ONE self-contained research brief. Open your tool's **Deep Research** mode, copy everything inside a single fenced code block, and paste it as the research query — one brief per run. The tool will usually show a research plan or ask a scope question first; approve it and let it run (these take minutes and return a long cited report). Each brief already states its objective, scope, deliverable format, and constraints, and tells the agent to proceed without further questions. Save each result as `DR-I1.md` … `DR-I5.md` under `writing/deepResearch/`. I (manager) then verify the returned DOIs and fold the confirmed citations into `Chapter_01_Introduction.md` and the master bibliography.

> **Already verified — don't pay to re-research.** The methods pack (`DR_prompts_methodology_literature.md`) and the 10 reports already in `writing/deepResearch/` verified several of these (Chen et al. 2022 = Applied Energy 325:119890; Yan et al. 2015 = Build. Environ. 107:264–278; Widén & Wäckelgård 2010 = 10.1016/j.apenergy.2009.11.006; Barrero-Bloom-Davis 2021 = NBER WP 28731; Cicala 2023; Khalil & Fatmi 2022 = Sustainable Cities & Society 81:103832; Guo et al. 2026 = arXiv:2603.18440; Yin et al. 2025). Each brief tells the agent to *confirm or correct* the held DOI rather than start over, and to spend its effort on the introduction-specific quote/number still needed.

---

## DR-I1 — The performance gap and occupant behaviour as its dominant driver (§1.1)

```
RESEARCH OBJECTIVE: Verify the citations and extract the supporting evidence for the opening paragraph of a building-energy journal paper, which argues that the predicted-vs-measured "performance gap" is driven primarily by occupant behaviour, and that static deterministic schedules misrepresent not only annual energy magnitude but intraday timing.

CONTEXT: This is citation verification for a journal submission (residential occupancy → building energy load shape, Canada). Accuracy outweighs breadth: a confirmed DOI with a real supporting quote is worth more than extra sources. Conduct a thorough search and return a structured report.

SCOPE & METHOD: Prioritise peer-reviewed primary sources and authoritative programmatic reports. For every source, resolve the DOI on the publisher site or Crossref before reporting it; cross-check the title, authors, year, volume and pages. Do not invent DOIs, page ranges, or quotations. If you cannot confirm an item, label it UNVERIFIED rather than guessing or omitting it.

VERIFICATION TARGETS:
1. de Wilde, P. (2014) — foundational statement of the building "performance gap" between predicted and measured energy use (likely Automation in Construction, 2014). Need a sentence defining/quantifying the gap.
2. Yan, D. et al. (2015) — occupant behaviour as the dominant source of uncertainty in building performance simulation (likely Building and Environment vol. 107). Confirm vol/pages/DOI; need a sentence positioning occupant behaviour as the key driver.
3. Hong, T., Yan, D., D'Oca, S., Chen, C. (2017) "Ten questions concerning occupant behavior in buildings," Building and Environment 114:518–530, DOI 10.1016/j.buildenv.2016.12.006 — confirm and quote a sentence on the magnitude/importance of occupant behaviour.
4. IEA EBC Annex 66 (Definition and Simulation of Occupant Behavior in Buildings) AND Annex 79 (Occupant-Centric Building Design and Operation) — give the correct programmatic reference for EACH (Annex 66 final report or summary paper; Annex 79 introduction, held as Wagner et al. 2020, Building and Environment). Confirm both with DOIs/URLs.
5. The claim that deterministic ASHRAE/ISO schedules produce residential energy discrepancies "of up to 41%," currently anchored to Wilke, Haldi & Robinson (2011, IBPSA), Mitra, Chu & Cetin (2020), and Elsayed et al. (2023, Build. Environ. 236:110307). Determine which source actually carries the "up to 41%" figure (or the closest defensible discrepancy magnitude) and quote it; if 41% is unsupported, give the best-supported alternative with its citation.
6. A defensible source for the framing that static schedules misrepresent the TIMING (load shape / peak hour), not only the MAGNITUDE (annual kWh), of residential demand — ideally one tying occupancy-schedule choice to peak-hour or load-shape error.

DELIVERABLE: A report with one block per target, in exactly this format:
- CITATION: <authors, year, title, venue, vol(issue), pages>
- DOI/URL: <resolvable DOI or stable URL; or "UNVERIFIED — could not confirm">
- SUPPORTS (our claim): <the one sentence/number in our introduction this source backs>
- DIRECT QUOTE: "<short verbatim quote>" (location: <section/page/figure>)
- CONFIDENCE: high / medium / low
- CONTRADICTS / CAVEAT: <any evidence that complicates the claim, or "none">
End with a NOT-VERIFIED heading listing anything you could not confirm. If you find a clearly stronger replacement for any target, add it under SUGGESTED-REPLACEMENT with a one-line reason.

CONSTRAINTS: Do not ask me clarifying questions before starting — proceed with reasonable assumptions and state any you make. Do not fabricate. Prefer primary sources over blogs or vendor pages.
```

---

## DR-I2 — High-fidelity stochastic occupant models, single-building / retrospective (§1.2, track a)

```
RESEARCH OBJECTIVE: Verify the citations and confirm the scope/horizon of the "high-fidelity occupant model" track in a building-energy paper's literature argument — that these models are applied at the SINGLE-BUILDING scale and RETROSPECTIVELY (not forecasting a future year).

CONTEXT: This supports a "two tracks that rarely meet" framing. Citation verification for a journal submission; accuracy outweighs breadth. For each source I need confirmation of (i) what it models (presence / activity / electricity) and (ii) its application scale (single dwelling/building) and horizon (retrospective).

SCOPE & METHOD: Prioritise peer-reviewed primary sources. Resolve every DOI on the publisher site or Crossref before reporting; cross-check title/authors/year/volume/pages. Do not invent DOIs or quotations; label anything you cannot confirm as UNVERIFIED rather than guessing.

VERIFICATION TARGETS:
1. Richardson, I., Thomson, M., Infield, D., Clifford, C. (2010) "Domestic electricity use: A high-resolution energy demand model," Energy and Buildings 42(10):1878–1887. NOTE: DISTINCT from Richardson, Thomson & Infield (2008), the high-resolution occupancy model, Energy and Buildings 40(8):1560–1566. Confirm BOTH and keep them separate.
2. Widén, J. and Wäckelgård, E. (2010) — high-resolution stochastic model of household activity/electricity, held as DOI 10.1016/j.apenergy.2009.11.006 (Applied Energy). Confirm.
3. Wilke, U. et al. (2013) — bottom-up stochastic model of occupant activities (EPFL doctoral thesis and/or journal article). Confirm the precise 2013 form (thesis vs paper) and its DOI/handle.
4. Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F. (2014) "A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison," Building and Environment 75:67–78. Confirm DOI; note whether it mentions the 04:00 diary-origin / day-start convention.
5. Armstrong, M.M. et al. (2009) — Canadian residential occupancy/load profile modelling (likely Journal of Building Performance Simulation or an NRC/CanmetENERGY paper). Confirm citation + DOI.
6. Osman, M. et al. (2023) — Canadian time-use-based occupancy modelling, DISTINCT from Osman & Ouf (2021) review (Build. Environ. 196:107785). Determine whether a 2023 Osman primary-modelling paper exists; if not, say so plainly.
7. Ferreira, ... et al. (2024) — a recent (2024) Canadian occupancy or residential-load modelling paper. Identify the most likely intended paper, confirm citation + DOI, and flag if the identification is ambiguous.

DELIVERABLE: A report with one block per target, in exactly this format:
- CITATION: <authors, year, title, venue, vol(issue), pages>
- DOI/URL: <resolvable DOI or stable URL; or "UNVERIFIED — could not confirm">
- SUPPORTS (our claim): <what it models; single-building scale; retrospective horizon>
- DIRECT QUOTE: "<short verbatim quote>" (location: <section/page/figure>)
- CONFIDENCE: high / medium / low
- CONTRADICTS / CAVEAT: <e.g. if it is actually stock-scale or forecasting, say so; or "none">
End with a NOT-VERIFIED heading. Add SUGGESTED-REPLACEMENT only for a clearly stronger match, with a one-line reason.

CONSTRAINTS: Do not ask me clarifying questions before starting — proceed with reasonable assumptions and state any you make. Do not fabricate. Keep the two Richardson papers (2008 occupancy vs 2010 electricity) explicitly separate.
```

---

## DR-I3 — Stock/urban-scale engines and the gap-matrix competitors (§1.2, Table 1)

```
RESEARCH OBJECTIVE: Verify the competitor studies for a six-dimension capability matrix (Table 1) and score each on those dimensions, so the paper's "open cell" novelty claim is defensible.

CONTEXT: The matrix scores competitors against: (1) time-series occupancy, (2) a calibrated behavioural model, (3) forecast to a FUTURE year, (4) activity- and end-use resolution, (5) stock/urban scale, (6) load-shape and peak focus. The paper claims it uniquely satisfies all six. I need each competitor's citation confirmed and an explicit, quote-backed YES/PARTIAL/NO score on each dimension.

SCOPE & METHOD: Prioritise peer-reviewed primary sources. Resolve every DOI before reporting; cross-check details. Do not invent DOIs or quotations; mark UNVERIFIED rather than guessing. Read each paper's abstract/methods/results closely enough to score the six dimensions honestly.

VERIFICATION TARGETS:
1. Reinhart, C.F. and Cerezo Davila, C. (2016) "Urban building energy modeling — A review of a nascent field," Building and Environment. Confirm DOI; extract its characterisation of the schedules typically used at stock/urban scale (baseline-year / simplified).
2. Chen, Y. et al. (2022) — paired / stock-scale building energy simulation, held as Applied Energy 325:119890 (2022 journal version of arXiv:2111.01881). Confirm; score it (expected: CLOSEST methodological precedent but RETROSPECTIVE, no forecast to a future year). Quote the sentence establishing the paired/stock-scale design and the quote (or its absence) on forecasting.
3. Yin, ... et al. (2025) — occupancy forecasting through a structural break via statistical probability modelling, WITHOUT bottom-up building-energy simulation. Confirm exact paper/authors/venue/DOI; score it (expected: closest on FORECAST but failing dimensions 4, 5, 6). Quote the sentence showing it stops at statistical modelling.
4. Independently search for ANY other 2020–2026 study that plausibly occupies the same open cell (calibrated behavioural occupancy + forecast to a future year + stock-scale paired building-energy simulation of load shape). If a genuine competitor exists, name and score it; if none does, state explicitly that the cell appears open.

DELIVERABLE: A report with one block per study, in exactly this format:
- CITATION: <authors, year, title, venue, vol(issue), pages>
- DOI/URL: <resolvable DOI or stable URL; or "UNVERIFIED — could not confirm">
- SIX-DIMENSION SCORE: (1) time-series occupancy = YES/PARTIAL/NO — <why>; (2) calibrated behavioural = …; (3) forecast to future year = …; (4) activity/end-use = …; (5) stock scale = …; (6) load-shape/peak = …
- DIRECT QUOTE: "<short verbatim quote backing the key scores>" (location: <section/page/figure>)
- CONFIDENCE: high / medium / low
- CONTRADICTS / CAVEAT: <anything complicating the scoring, or "none">
If you find a genuine competitor for the open cell, flag it prominently as OPEN-CELL-COMPETITOR with a one-line reason. End with a NOT-VERIFIED heading.

CONSTRAINTS: Do not ask me clarifying questions before starting — proceed with reasonable assumptions and state any you make. Do not fabricate. Score conservatively: only mark a dimension YES if the paper clearly demonstrates it.
```

---

## DR-I4 — Non-stationarity and the COVID/work-from-home structural break (§1.3)

```
RESEARCH OBJECTIVE: Verify the citations and the exact quantitative claims behind the paper's argument that occupant behaviour underwent a STRUCTURAL (persistent), not transient, break at COVID-19, with grid-relevant electricity consequences, and that forecasting occupancy through this break is an open problem.

CONTEXT: Citation verification for a journal submission. For each source I need the exact number we attribute (a persistence level or an electricity-increase percentage) confirmed against the source, with a verbatim quote and location.

SCOPE & METHOD: Prioritise peer-reviewed papers and authoritative working papers (NBER, etc.). Resolve every DOI/URL before reporting; cross-check details. Do not invent figures, DOIs, or quotations; mark UNVERIFIED rather than guessing. Where a source reports both an initial spike and a settled/structural level, report both and make clear which we should cite.

VERIFICATION TARGETS:
1. Barrero, J.M., Bloom, N., Davis, S.J. (2021) "Why working from home will stick," NBER Working Paper 28731. Confirm; extract the figure for how far work-from-home settles ABOVE its pre-pandemic level (claimed "roughly twice").
2. Guo, ... et al. (2026) — work-from-home prevalence/persistence, held as arXiv:2603.18440. Confirm authors/title and the persistence figure it supports.
3. Cicala, S. (2023) — pandemic-era residential electricity demand; claimed weather-adjusted increase of ABOUT +7.9% in residential electricity. Confirm the paper (venue/DOI/working-paper number) and the exact figure plus its weather-adjustment basis.
4. Khalil, M. and Fatmi, M.R. (2022) — structural change in residential in-home energy demand (Canada), held as Sustainable Cities and Society 81:103832, DOI 10.1016/j.scs.2022.103832, structural figure on the order of +12%. Confirm the citation and the exact percentages (initial spike vs structural/persistent level).
5. Yin, ... et al. (2025) AND Bielskus, J. et al. (2021) — sources framing occupancy FORECASTING under disruption / non-stationary conditions as an open problem. Confirm both citations + DOIs and quote the sentence framing forecasting/prediction under disruption as unresolved.
6. Independently search for Canadian or North-American smart-meter / load-research evidence (2021–2026) that weekday residential load profiles took on a WEEKEND-like shape after COVID — to strengthen the load-shape (not just magnitude) framing. Identify the strongest such source with its number.

DELIVERABLE: A report with one block per target, in exactly this format:
- CITATION: <authors, year, title, venue, vol(issue), pages or WP number>
- DOI/URL: <resolvable DOI or stable URL; or "UNVERIFIED — could not confirm">
- SUPPORTS (our claim): <the exact persistence / electricity-increase number we attribute>
- DIRECT QUOTE: "<short verbatim quote>" (location: <section/page/figure>)
- CONFIDENCE: high / medium / low
- CONTRADICTS / CAVEAT: <e.g. a reversion estimate that complicates persistence, or "none">
End with a NOT-VERIFIED heading. Add SUGGESTED-REPLACEMENT only for a clearly stronger match.

CONSTRAINTS: Do not ask me clarifying questions before starting — proceed with reasonable assumptions and state any you make. Do not fabricate numbers or DOIs. Distinguish initial-spike from settled-structural figures wherever both exist.
```

---

## DR-I5 — Standards, schedule baselines, and Canadian statistical sources (§1.1, §1.2, §1.4)

```
RESEARCH OBJECTIVE: Pin down the authoritative, correctly-formatted citations (issuing body, edition/year, identifier, stable URL) for the standards and national-data sources an introduction must cite precisely.

CONTEXT: Citation verification for a journal submission. These are reference/standards items, so I need exact identifiers — catalogue numbers, standard numbers, official URLs — not paraphrases.

SCOPE & METHOD: Use official issuing-body sources (ASHRAE, NREL/DOE, National Research Council Canada, Statistics Canada, Natural Resources Canada). Confirm each identifier on the official site. Do not invent catalogue numbers or URLs; mark UNVERIFIED rather than guessing.

VERIFICATION TARGETS:
1. Static/deterministic residential schedule baselines that practice relies on: (a) ASHRAE Standard 90.1 reference/prototype building schedules, and the U.S. DOE Commercial/Residential Prototype Building Models that implement them; (b) the NREL OpenStudio-Standards schedule library. Give the correct citation for each as a "default schedule" source.
2. Canadian code-archetype basis: National Energy Code of Canada for Buildings (NECB) 2017, and National Building Code of Canada (NBC) 2020 Section 9.36. Confirm issuing body (National Research Council Canada / Canadian Commission on Building and Fire Codes), edition, and catalogue identifiers.
3. Statistics Canada — General Social Survey (GSS) Time Use: correct catalogue/citation for the cycles used (2005, 2010, 2015, 2022). Provide StatCan catalogue numbers / PUMF references and stable URLs.
4. Statistics Canada — Census of Population 2021 PUMF and the dwelling/demographic variables: correct citation + catalogue number + URL.
5. Statistics Canada — population projections, specifically the M1 (medium-growth) projection scenario used for a 2030 demographic injection. Give the correct StatCan projection publication, the M1 scenario definition, and a stable URL.
6. NRCan Survey of Household Energy Use (SHEU) 2019 — end-use calibration benchmark. Confirm the correct citation/URL for the SHEU 2019 data tables (equipment and lighting per-dwelling energy).

DELIVERABLE: A report with one block per item, in exactly this format:
- CITATION: <issuing body, year/edition, title>
- IDENTIFIER: <catalogue number / standard number / DOI>
- URL: <stable official URL; or "UNVERIFIED — could not confirm">
- NOTE: <e.g. the exact M1 scenario definition, or which SHEU table holds the end-use figures>
- CONFIDENCE: high / medium / low
End with a NOT-VERIFIED heading for anything you could not pin down.

CONSTRAINTS: Do not ask me clarifying questions before starting — proceed with reasonable assumptions and state any you make. Use only official issuing-body sources for identifiers; do not infer catalogue numbers.
```

---

## After the reports return (manager checklist — not for pasting)

1. Drop `DR-I1.md … DR-I5.md` into `writing/deepResearch/`.
2. Manager verifies each returned DOI actually resolves (deep-research tools still hallucinate — spot-check by resolving, as was done for the methods pack).
3. Replace the flagged in-text cites in `Chapter_01_Introduction.md`'s "External literature requiring deep-research verification" block with the confirmed entries; merge into one verified reference list at combine-time.
4. Reconcile against `methodology_assessment_and_paper_skeleton.md` Part 5 so a citation verified there is not re-entered with a different DOI.
5. Confirm the Table 1 gap-matrix scoring (DR-I3) is defensible cell-by-cell before the matrix is finalised; if DR-I3 surfaces a genuine competitor in the open cell, revisit the novelty claim in §1.2/§1.5.
6. Lock the "up to 41%" discrepancy figure (DR-I1 item 5) to a real source, or replace it with the best-supported alternative.
