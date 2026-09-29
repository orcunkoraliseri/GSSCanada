# Vetting RT31: Fusing Time-Use Diaries with Measured Occupancy Sources: Methods and Precedents

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-18).

1. **Kept:** Item 1 (six method families with one assumption each; the statistical matching book
   checks clean) and Item 3 (three concrete rules against circular validation, which answer the
   question directly). The StatMatch and synthpop licences (GPL) are confirmed on their CRAN pages.
2. **Struck: all of Item 2.** Once corrected, no row fuses a diary or travel survey with a measured
   source. Anda et al. 2021 says it uses "only" mobile phone data (U1); its "22 % error reduction on
   loop detector counts" is unsupported (U2); Barbour et al. 2019 validates against census counts and
   national energy-intensity benchmarks, not "regional load curves" (U5); Ferrando et al. 2020 is a
   review.
3. **Struck: row L02.** Two real papers are merged into it: the DOI is Chong, Lam, Pozzi and Yang
   2017, while "Chong and Menberg" is a different 2018 paper. The PopGen URL is a 404 (the real
   repository sits under another GitHub organisation).
4. **Batch finding.** The tool opened no web page for this report. The 2 of 4 wrong author lists
   are the same class of defect as RT19.

**What this means for the fusion form (A14, role R4):** still open. This report found no survey plus
measured-signal fusion in building energy, but its search was too weak to call that a gap. The
"8,000 ecobee homes" in Section E was confirmed only in order of magnitude and is not quoted.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 2, wrong author lists 2, not resolved 0); use claims 6 (supported 1,
not in abstract 2, contradicted 3); URLs 4 (opened 3 at 200, 1 returned 404); quoted strings 4
(found 4); numeric facts 8 (confirmed 4, contradicted 3, not confirmed 1); prompt items 3 (dropped 0);
dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | HTTP status | CrossRef title (first 80 chars) | Title match | CrossRef authors | Report authors | Author verdict | Year/venue |
|---|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.trc.2021.103118 | 200 | "Synthesising digital twin travellers: Individual travel demand from..." | MATCH | Cuauhtemoc Anda; Sergio A. Ordonez Medina; Kay W. Axhausen | Anda, C.; Ordonez Medina, S. A.; Axhausen, K. W. | MATCH (3/3 correct) | 2021, Transp. Res. Part C, vol 128 p 103118 - matches |
| D2 | 10.1016/j.enbuild.2017.08.069 | 200 | "Bayesian calibration of building energy models with large datasets" | MATCH | Adrian Chong; Khee Poh Lam; Matteo Pozzi; Junjing Yang | Chong, A.; Menberg, K. | AUTHOR MISMATCH: "Menberg" is not an author of this paper at all; the actual co-authors (Lam, Pozzi, Yang) are all silently dropped | 2017, Energy and Buildings, vol 154 p 343-355 - matches |
| D3 | 10.1038/s41467-019-11685-w | 200 | "Planning for sustainable cities by estimating building occupancy with mobile phones" | MATCH | Edward Barbour; Carlos Cerezo Davila; Siddharth Gupta; Christoph Reinhart; Jasleen Kaur; Marta C. Gonzalez | Barbour, E.; Carlos, C.; Gonzalez, M. C. | AUTHOR MISMATCH: 3 of 6 real authors dropped (Gupta, Reinhart, Kaur); second author's real surname "Cerezo Davila" is truncated to "Carlos" (which is actually his given name) | 2019, Nature Communications, vol 10 issue 1, article 3736 - matches |
| D4 | 10.1016/j.scs.2020.102408 | 200 | "Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches" | MATCH | Martina Ferrando; Francesco Causone; Tianzhen Hong; Yixing Chen | Ferrando, M.; Causone, F.; Hong, T.; Chen, Y. | MATCH (4/4 correct, in order) | 2020, Sustainable Cities and Society, vol 62 p 102408 - matches |

Count of author lists wrong: 2 of 4 (D2, D3).

**Important compounding fact for D2.** A real paper by Chong and Menberg does exist: "Guidelines for
the Bayesian calibration of building energy models", Energy and Buildings, vol 174, p 527-547
(2018), DOI 10.1016/j.enbuild.2018.06.031 per web search (not independently CrossRef-checked in this
note). The report has attached the real Chong & Menberg citation text to the DOI, volume and page
range of a *different*, unrelated paper by Chong, Lam, Pozzi and Yang. This is not merely a dropped
co-author; it is two real papers merged into one row.

**Statistical matching book (checked with extra care per instruction).** "D'Orazio, Di Zio, & Scanu
(2006), Statistical Matching: Theory and Practice, Wiley" (Table B1 row 1) is confirmed via Wiley's
own catalogue page and CRAN documentation: authors Marcello D'Orazio, Marco Di Zio, Mauro Scanu;
publisher John Wiley & Sons; published 24 March 2006; ISBN 978-0-470-02353-2. Title, authors, year and
publisher all MATCH. This reference has no DOI in the report and none was resolved by this note (book,
not article); no error found in it.

---

## 2. Use claims (given extra care: every fusion precedent, checking that the abstract names BOTH a
diary-type source and a measured source)

| # | Claim (report text) | Abstract words (OpenAlex, rebuilt) | Verdict |
|---|---|---|---|
| U1 | Section A / Table C1 L01: Anda et al. (2021) "combined aggregated mobile network call records with travel survey diaries" | "we propose a framework designed **only** with user-aggregated mobile phone data to synthesise realistic daily individual mobility ... Digital Twin Travellers." No mention anywhere in the abstract of a travel survey or diary dataset. | **CONTRADICTED**. The abstract explicitly restricts the method's inputs to mobile phone data alone ("only with"). This is the report's single positive precedent for diary+measured fusion and its own abstract says the opposite. |
| U2 | Table C1 L01: "Fused model reduced traffic volume error by 22% over survey alone on held-out loop detector counts" | Abstract's own stated validation is "a one-day mobility population score to measure the similarity between the population of generated agents and the real mobile phone user population." No loop detectors, no 22%, no comparison to a "survey alone" baseline anywhere in the abstract. | **CONTRADICTED** on validation method named; the "22%" figure itself is **NOT CONFIRMED** (full text is paywalled, could not be checked directly). |
| U3 | Table B1 row 3 / Table C1 L02: Chong & Menberg (2017), "Calibrating UBEM occupancy parameters to smart meter data", EnergyPlus model + smart meter logs | No abstract available (CrossRef and OpenAlex both return none for this DOI). | **NO ABSTRACT**. Also see D2 above: the DOI belongs to a different author team than the one named. |
| U4 | Table C1 L03: Barbour et al. (2019) "Combined mobile phone CDR telemetry with building spatial footprint data" | OpenAlex abstract does not mention building footprints explicitly, but the paper's own PMC full text states: "Building data are obtained from the city of Boston, for 82,542 buildings" and describes assigning phone-inferred stays to those building footprints. | **SUPPORTED** (confirmed in full text, not the abstract itself). |
| U5 | Table C1 L03: "Evaluated against regional load curves; did not validate against micro-level physical sensor logs" | PMC full text: validation is against census tract population counts and against CBECS/RBECS national energy-use-intensity survey averages ("average difference of the modeled EUI compared to the CBECS/RBECS averages ... ranged between 5% and 20%"), and the paper states explicitly: "lack of available real occupancy data on a sufficiently large scale for comparison." | **CONTRADICTED** in part: no "regional load curves" appear anywhere; the actual comparators are census counts and CBECS/RBECS EUI benchmarks. The "no sensor validation" half of the claim is correct. |
| U6 | Table C1 L04: Ferrando et al. (2020) review "Highlighted absence of multi-source validation benchmarks in urban building energy simulation" | No abstract available (CrossRef and OpenAlex both return none). | **NO ABSTRACT**. |

Note on scope: L03 (Barbour) and L04 (Ferrando) are placed in a table headed "Studies fusing survey
data with measured physical signals" (Section C), but neither paper fuses a time-use or travel survey
with anything; Barbour fuses mobile-phone data with GIS building footprints (no survey at all), and
Ferrando is a review with no primary fusion of its own. Of the 4 rows in Table C1, 0 unambiguously
meet the prompt's Item 2 definition ("fused a time-use or travel survey with a measured source") once
U1 is corrected; L01 was the only candidate and its own abstract says it did not use a survey.

---

## 3. URLs and quotes

| # | URL | Status | Claim being checked | Result |
|---|---|---|---|---|
| W1 | `https://cran.r-project.org/package=StatMatch` | 200 | Licence "GPL-2.0 / GPL-3.0"; developer D'Orazio | FOUND. Page states "GPL-2 \| GPL-3"; maintainer/author Marcello D'Orazio confirmed. |
| W2 | `https://cran.r-project.org/package=synthpop` | 200 | Licence "GPL-2.0 / GPL-3.0"; developer "University of Edinburgh" | Licence FOUND ("GPL-2 \| GPL-3"). Developer name NOT FOUND as stated: the CRAN page names author Beata Nowok (plus contributors) and states no institutional affiliation at all; "University of Edinburgh" is not on the page. |
| W3 | `https://github.com/foss-analytics/popgen` | **404** | "GitHub repository", "Open source (GPL)" | PAGE NOT READABLE (does not exist). A real PopGen/IPU repository exists at a different address, `github.com/foss-transportationmodeling/popgen` (and a newer `tomnetutc/PopGen3`), associated with Arizona State University (Ram Pendyala group) per external search. The report's URL is wrong. |
| W4 | `https://www.pymc.io/` | 200 (redirect page only) | Licence "Apache 2.0 / BSD 3-Clause" | The fetched landing page carries no licence text (just a redirect stub). Checked the PyMC GitHub repository instead: confirms Apache License 2.0. Report's claim is directionally right but not verifiable from the URL it actually gives. |

No double-quoted strings in the report are attributed to any of these four URLs (the report's Section
F licence cells are paraphrased, not quoted). The double-quoted strings that do exist and are
checkable are the 4 "CrossRef returned title" strings in Section H (see below).

---

## 4. Key numeric facts

| # | Fact | Verdict | Basis |
|---|---|---|---|
| N1 | Anda et al. fused mobile CDR with travel survey diaries | **CONTRADICTED** | OpenAlex abstract: "designed only with" mobile phone data |
| N2 | 22% traffic-volume error reduction on held-out loop detector counts | **NOT CONFIRMED** | Not in abstract; full text paywalled, not opened |
| N3 | Chong & Menberg (2017), Energy and Buildings 154:343-355 | **CONFIRMED** (bibliographic fields only) | CrossRef; but see D2, wrong authors attached to these correct volume/pages |
| N4 | Barbour et al., Nat. Commun. 10:3736, "evaluated against regional load curves" | **CONTRADICTED** (volume/article number correct; validation description wrong) | CrossRef article-number 3736 confirmed; PMC full text shows census + CBECS/RBECS comparison, not load curves |
| N5 | "8,000 ecobee homes in Canada" (Section E, Rule 3) | **CONFIRMED** (order of magnitude) | External search: a published study applied an ecobee-derived framework to "over 8,000 Canadian households" |
| N6 | StatMatch / SynthPop licensed GPL-2.0/GPL-3.0 | **CONFIRMED** | CRAN pages (W1, W2) |
| N7 | PopGen at `github.com/foss-analytics/popgen` | **CONTRADICTED** | URL returns 404; real org name is different (W3) |
| N8 | PyMC licensed Apache 2.0 | **CONFIRMED** | GitHub repository page (not the URL the report gives) |

Confirmed 4 (N3, N5, N6, N8), contradicted 3 (N1, N4, N7), not confirmed 1 (N2).

---

## 5. Completeness

T31 prompt items:

| Item | Requirement | Verdict |
|---|---|---|
| 1 | Six method families, each with a canonical reference, a worked example on activity/mobility/occupancy data, and a one-sentence assumption | ANSWERED. Section B (Table B1) has 6 rows; every row carries an assumption sentence. |
| 2 | Precedents fusing a time-use/travel survey with a measured source, with the two sources, method, validation, and whether fused beat each source alone on held-out data | ANSWERED, but see Section 2 above: the flagship precedent (L01) does not survive its own abstract, and 2 of the other 3 rows (L03, L04) do not involve a survey/diary source at all. |
| 3 | Validation design answering the circularity question directly (not "use cross-validation") | ANSWERED. Section E gives 3 explicit rules (never validate on the calibration set; three-tier source separation; spatial/temporal holdouts), which does answer the question directly as required. |

Named leads (Journal of Official Statistics, Survey Methodology, JRSS Series A, Transportation
Research Part C, Computers Environment and Urban Systems, Journal of Artificial Societies and Social
Simulation, Energy and Buildings): only 2 of these 7 venues (Transportation Research Part C, Energy and
Buildings) appear anywhere in the report's citations. This is not a numbered prompt item, so it is not
scored as DROPPED, but 5 of 7 named venues produced zero citations.

Section F (data-source card columns per brief section 9): does not apply cleanly. Brief section 9's
column list (years covered, unit, occupancy variable, temporal/spatial resolution, sample size, R1-R4
roles, redistribution terms, selection bias, one verified BEM-use example) is written for rows
describing **data sources**. RT31's Section F is a registry of **software tools/packages** (StatMatch,
SynthPop, PopGen, PyMC/Stan), which is a different kind of artefact than T19-T30's source cards; most
of section 9's columns (years covered, occupancy variable, sample size, R1-R4 roles, bias, BEM-use
example) have no natural equivalent for a software package and are absent. The columns that do apply
(licence and access terms) are present.

---

## 6. Dashes

Checked with `py` on the raw file: em dash (U+2014) count = 0; en dash (U+2013) count = 0.

---

## 7. Rules

- No named individual is connected to a fellowship programme anywhere in the report.
- No proposal to change the 4J gate appears anywhere in the report.
- No claim that this report itself was vetted or accepted appears anywhere in the report (Section G Q2
  discusses what a "crowded topic" finding would look like, not a vetting claim about this report).
