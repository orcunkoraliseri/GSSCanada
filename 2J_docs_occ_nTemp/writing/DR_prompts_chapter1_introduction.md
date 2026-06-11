# Chapter 1 (Introduction) — Deep-Research Prompt Pack

**Document type:** Web-LLM deep-research prompt pack (run externally) · **Status:** ready to execute · **Date:** 2026-06-11
**Purpose:** Chapter 1 is the most reference-heavy chapter. These five self-contained prompts gather and *verify* the external literature behind the introduction's funnel (§1.1 performance gap → §1.2 two tracks + gap matrix → §1.3 non-stationarity/WFH → §1.5 contributions framing), returning resolvable DOIs and the exact quantitative claim each source supports. **You run these in a web-based deep-research tool (Gemini / ChatGPT / Claude with web). I (the manager) do not run them.** Return the outputs as `.md` under `writing/deepResearch/` named `DR-I1.md` … `DR-I5.md`; I then verify and fold the confirmed citations into `Chapter_01_Introduction.md` and the master bibliography.

> **Why a separate Ch-1 pack.** The existing `DR_prompts_methodology_literature.md` (DR-S1…S9, DR-X1) and the 10 returned reports in `writing/deepResearch/` already verified much of the *methods* literature and several of these very cites (Chen et al. 2022 = Applied Energy 325:119890; Yan et al. 2015 = Build. Environ. 107:264–278; Widén & Wäckelgård 2010 = 10.1016/j.apenergy.2009.11.006; Barrero-Bloom-Davis 2021 = NBER WP 28731; Cicala 2023; Khalil & Fatmi 2022 = Sustainable Cities & Society 81:103832; Guo et al. 2026 = arXiv:2603.18440; Yin et al. 2025). **Do not re-research those from scratch** — the prompts below ask the tool to *confirm or correct* the DOI we already hold and, more importantly, to extract the *introduction-specific* framing/quote/number we still need.

> **Hallucination guard (applies to every prompt).** Deep-research LLMs invent plausible DOIs and page ranges. Every prompt instructs the tool to return only DOIs/URLs it can actually resolve, to mark anything unconfirmable as `UNVERIFIED`, and to surface contradicting evidence rather than smoothing it over. Treat any citation not returned with a resolvable DOI/URL as not-yet-verified.

---

## Standard output format (request at the end of every prompt)

For each source, return a block:

```
- CITATION: <full reference — authors, year, title, venue, vol(issue), pages>
- DOI/URL: <resolvable DOI or stable URL; or "UNVERIFIED — could not confirm">
- SUPPORTS (our claim): <the one sentence / number in our introduction this source backs>
- DIRECT QUOTE: "<short verbatim quote>" (location: <section/page/figure>)
- CONFIDENCE: high / medium / low
- CONTRADICTS / CAVEAT: <any evidence that complicates the claim, or "none">
```

End every prompt with: *"List sources you could NOT verify separately under a NOT-VERIFIED heading; do not pad the list with adjacent papers I did not ask for unless they are clearly stronger replacements, in which case flag them as SUGGESTED-REPLACEMENT with a one-line reason."*

---

## DR-I1 — The performance gap and occupant behaviour as its dominant driver (§1.1)

```
I am verifying the literature for the opening of a building-energy journal paper. For each item below, confirm the exact citation and a resolvable DOI/URL, and extract the single strongest sentence (with a short verbatim quote and its location) that supports the stated claim. Be rigorous: do not invent DOIs; mark anything you cannot resolve as UNVERIFIED.

1. de Wilde, P. (2014) — the foundational statement of the building "performance gap" between predicted and measured energy use. I need the canonical paper (I believe Automation in Construction, 2014) and a sentence defining/quantifying the gap.
2. Yan, D. et al. (2015) — occupant behaviour as the dominant source of uncertainty / unexplained variance in building performance simulation. I believe Building and Environment, vol. 107. Confirm vol/pages/DOI and a sentence positioning occupant behaviour as the key driver.
3. Hong, T., Yan, D., D'Oca, S., Chen, C. (2017) "Ten questions concerning occupant behavior in buildings" — Building and Environment 114:518–530, DOI 10.1016/j.buildenv.2016.12.006. Confirm and give the sentence on the magnitude/importance of occupant behaviour.
4. IEA EBC Annex 66 (Definition and Simulation of Occupant Behavior in Buildings) AND Annex 79 (Occupant-Centric Building Design and Operation). I need the correct programmatic reference for EACH (Annex 66 final report / Wang et al. summary, and Annex 79 introduction — I hold Wagner et al. 2020, Building and Environment, as the Annex 79 intro). Confirm both, with DOIs/URLs.
5. The claim that deterministic ASHRAE/ISO schedules produce residential energy discrepancies "of up to 41%." I currently anchor this to Wilke, Haldi & Robinson (2011, IBPSA), Mitra, Chu & Cetin (2020) and Elsayed et al. (2023, Build. Environ. 236:110307). Tell me which source actually carries the "up to 41%" figure (or the closest defensible discrepancy magnitude) and quote it; if the 41% cannot be sourced, give the best-supported alternative discrepancy figure with its citation.
6. A defensible source for the framing that static schedules misrepresent the TIMING (load shape / peak hour), not only the MAGNITUDE (annual kWh), of residential demand — ideally something tying occupancy-schedule choice to peak-hour or load-shape error.

[then the Standard output format + the NOT-VERIFIED instruction]
```

---

## DR-I2 — High-fidelity stochastic occupant models, single-building / retrospective (§1.2, track a)

```
I am scoring a "two tracks that rarely meet" argument in a building-energy paper: track (a) is high-fidelity stochastic occupant/activity models applied at the SINGLE-BUILDING scale and RETROSPECTIVELY. For each source below, confirm the exact citation + resolvable DOI, and extract one sentence establishing (i) what it models (presence / activity / electricity) and (ii) that its application scale is single-building/dwelling and its horizon is retrospective (not forecasting a future year). Do not invent DOIs; mark unresolvable items UNVERIFIED.

1. Richardson, I., Thomson, M., Infield, D., Clifford, C. (2010) "Domestic electricity use: A high-resolution energy demand model" — Energy and Buildings 42(10):1878–1887. (Distinct from Richardson, Thomson & Infield 2008, the occupancy model — confirm BOTH the 2008 occupancy paper and the 2010 electricity paper and keep them separate.)
2. Widén, J. and Wäckelgård, E. (2010) — high-resolution stochastic model of household activity/electricity. I hold DOI 10.1016/j.apenergy.2009.11.006 (Applied Energy). Confirm.
3. Wilke, U. et al. (2013) — bottom-up stochastic model of occupant activities (EPFL thesis and/or journal article). Confirm the precise 2013 form (thesis vs paper) and DOI/handle.
4. Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F. (2014) "A method for the identification and modelling of realistic domestic occupancy sequences…" — Building and Environment 75:67–78. Confirm DOI and the 04:00 diary-origin / day-start convention if mentioned.
5. Armstrong, M.M. et al. (2009) — Canadian residential occupancy/load profile modelling (I believe a Journal of Building Performance Simulation or NRC-CanmetENERGY paper). Confirm citation + DOI.
6. Osman, M. et al. (2023) — Canadian time-use-based occupancy modelling (distinct from Osman & Ouf 2021 review, Build. Environ. 196:107785, which I already hold). Confirm whether a 2023 Osman primary-modelling paper exists; if not, say so.
7. Ferreira, ... et al. (2024) — a recent (2024) Canadian occupancy or residential-load modelling paper. Identify the most likely intended paper, confirm citation + DOI, and flag if ambiguous.

[then the Standard output format + the NOT-VERIFIED instruction]
```

---

## DR-I3 — Stock/urban-scale engines and the gap-matrix competitors (§1.2, track b + Table 1)

```
I am building a six-dimension capability matrix (Table 1) that scores competitor studies against: (1) time-series occupancy, (2) a calibrated behavioural model, (3) forecast to a FUTURE year, (4) activity- and end-use resolution, (5) stock/urban scale, (6) load-shape and peak focus. For each source, confirm the citation + resolvable DOI and then score it explicitly on each of the six dimensions with a one-line justification + supporting quote. Do not invent DOIs.

1. Reinhart, C.F. and Cerezo Davila, C. (2016) "Urban building energy modeling — A review of a nascent field" — Building and Environment. Confirm DOI; extract its characterisation of the schedules typically used at stock/urban scale (baseline-year / simplified).
2. Chen, Y. et al. (2022) — paired / stock-scale building energy simulation. I hold this as Applied Energy 325:119890 (2022 journal version of arXiv:2111.01881). Confirm, and score it: it is the CLOSEST methodological precedent but RETROSPECTIVE (no forecast to a future year). Give the quote that establishes the paired/stock-scale design and the quote (or absence) on forecasting.
3. Yin, ... et al. (2025) — occupancy forecasting through a structural break using statistical probability modelling, WITHOUT bottom-up building-energy simulation. Confirm the exact paper, authors, venue, DOI. Score it: closest on the FORECAST dimension but fails dimensions (4) activity/end-use resolution and (5)/(6) bottom-up stock-scale load-shape simulation. Quote the sentence showing it stops at statistical modelling.
4. Any OTHER 2020–2026 study that plausibly occupies the same open cell (calibrated behavioural occupancy + forecast to a future year + stock-scale paired BEM of load shape). I want to be sure the "open cell" claim is defensible — if a genuine competitor exists, name it and score it; if not, state that the cell appears open.

[then the Standard output format + the NOT-VERIFIED instruction]
```

---

## DR-I4 — Non-stationarity and the COVID/work-from-home structural break (§1.3)

```
I am supporting the claim that occupant behaviour underwent a STRUCTURAL (persistent), not transient, break at COVID-19, with grid-relevant electricity consequences, and that forecasting occupancy through this break is an open problem. For each source confirm citation + resolvable DOI/URL and extract the exact quantitative claim with a verbatim quote + location. Do not invent DOIs.

1. Barrero, J.M., Bloom, N., Davis, S.J. (2021) "Why working from home will stick" — NBER Working Paper 28731. Confirm, and extract the number for how far work-from-home settles ABOVE its pre-pandemic level (I claim "roughly twice").
2. Guo, ... et al. (2026) — work-from-home prevalence/persistence. I hold arXiv:2603.18440. Confirm authors/title and the persistence figure it supports.
3. Cicala, S. (2023) — pandemic-era residential electricity demand. I claim a weather-adjusted increase of ABOUT +7.9% in residential electricity. Confirm the paper (venue/DOI/working-paper no.) and the exact figure + its weather-adjustment basis.
4. Khalil, M. and Fatmi, M.R. (2022) — structural change in residential in-home energy demand (Canadian context). I hold Sustainable Cities and Society 81:103832, DOI 10.1016/j.scs.2022.103832, and a structural in-home-demand figure on the order of +12%. Confirm the citation and the exact percentage (initial vs structural/persistent).
5. Yin, ... et al. (2025) AND Bielskus, J. et al. (2021) — sources framing occupancy FORECASTING (through disruption / non-stationary conditions) as an open problem. Confirm both citations + DOIs and quote the sentence that frames forecasting/prediction under disruption as unresolved.
6. Any Canadian or North-American smart-meter / load-research evidence (2021–2026) that weekday residential load profiles took on a WEEKEND-like shape post-COVID — to strengthen the load-shape (not just magnitude) framing. Identify the strongest such source with its number.

[then the Standard output format + the NOT-VERIFIED instruction]
```

---

## DR-I5 — Standards, schedule baselines, and Canadian statistical sources (§1.1, §1.2, §1.4)

```
I am pinning down the standards and national-data references an introduction must cite precisely. For each, return the authoritative, correctly-formatted citation with a stable URL or catalogue number. These are reference/standards items, so I need the exact issuing body, edition/year, and identifier — not a paraphrase. Mark anything you cannot pin down as UNVERIFIED.

1. The static/deterministic residential schedule baselines that practice relies on: (a) ASHRAE Standard 90.1 reference/prototype building schedules (and the DOE Commercial/Residential Prototype Building Models that implement them); (b) NREL OpenStudio-Standards schedule library. Give the correct citation for each as a "default schedule" source.
2. The Canadian code-archetype basis used elsewhere in the paper: National Energy Code of Canada for Buildings (NECB) 2017 and National Building Code of Canada (NBC) 2020 Section 9.36. Confirm correct issuing body (National Research Council Canada / Canadian Commission on Building and Fire Codes), edition, and catalogue identifiers.
3. Statistics Canada — General Social Survey (GSS) Time Use: the correct catalogue/citation for the cycles used (2005, 2010, 2015, 2022). Provide the StatCan catalogue numbers / PUMF references and stable URLs.
4. Statistics Canada — Census of Population 2021 PUMF and the dwelling/demographic variables: correct citation + catalogue number + URL.
5. Statistics Canada — population projections, specifically the M1 (medium-growth) projection scenario used to drive the 2030 demographic injection. Give the correct StatCan projection publication, the M1 scenario definition, and a stable URL.
6. NRCan Survey of Household Energy Use (SHEU) 2019 — the end-use calibration benchmark. Confirm the correct citation/URL for the SHEU 2019 data tables (equipment and lighting per-dwelling energy).

[then the Standard output format + the NOT-VERIFIED instruction]
```

---

## After the reports return (manager checklist)

1. Drop `DR-I1.md … DR-I5.md` into `writing/deepResearch/`.
2. Manager verifies each returned DOI resolves (the tools hallucinate — spot-check by resolving, as was done for the methods pack).
3. Replace the flagged in-text cites in `Chapter_01_Introduction.md`'s "External literature requiring deep-research verification" block with confirmed entries; move them into a single verified reference list at combine-time.
4. Reconcile against `methodology_assessment_and_paper_skeleton.md` Part 5 so a citation verified there is not re-entered with a different DOI.
5. Confirm the Table 1 gap-matrix scoring (DR-I3) is defensible cell-by-cell before the matrix is finalised; if DR-I3 surfaces a genuine competitor in the open cell, revisit the novelty claim in §1.2/§1.5.
6. Lock the "up to 41%" discrepancy figure (DR-I1 item 5) to a real source or replace it with the best-supported alternative.
