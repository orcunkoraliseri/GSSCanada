# Vetting RT27: activity_based_models_synthetic_populations

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Its main claim cannot be checked.** The report says transport-model and building-energy coupling was
   "successfully demonstrated" (AutoBEM with POLARIS, in Chattanooga). The only source is one review (Ferrando et al.
   2020), whose abstract cannot be read. No primary coupling study with a checkable DOI is given (U3). Item 2 is
   therefore not answered.
2. **Licences and links are wrong.** Both eqasim licences are GPL-2.0, not MIT (N1, N2). The Switzerland and POLARIS
   URLs return 404.
3. **Named items dropped silently.** Madrid, Bologna, London and eqasim's other cities never appear. Item 3 asked for
   prior work that enriched travel plans with time-use diaries. The report gives an unsearched "unclaimed" opinion
   instead. Almost every card column is missing.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:**
   - Horl and Balac 2021 built an open synthetic population with activity chains for Paris and Ile-de-France. The
     "12 million agents" is not confirmed.
   - The eqasim pipeline paper (Horl and Balac 2021) covers Ile-de-France, Switzerland, Sao Paulo and California.
   - The real repositories are `eqasim-org/eqasim-france` (Lyon is a documented case) and
     `eqasim-org/eqasim-switzerland`, both GPL-2.0.
   - MATSim Berlin is GPL-2.0, with 1, 10 and 100 % samples. ActivitySim is BSD-3-Clause.

**What this means for the travel-model form (A14):** open, and still the most concrete European lead. Open
activity-chain populations exist for Paris, Lyon and Switzerland under GPL-2.0. Whether anyone has coupled one to a
building energy model, or filled its in-home time from diaries, is not established either way.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 3, wrong author lists 1, not resolved 0); use claims 7 (supported 3,
not in abstract 2, contradicted 0, no abstract 2); URLs 5 (opened 5, working 3, 404 2); quoted
strings 9 checked (found 3, not found 6); numeric facts 7 (confirmed 2, contradicted 2, not
confirmed 3); prompt items 4 main items answered, but 4 named sub-items dropped; dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | HTTP | CrossRef title (first 80) | Title match | CrossRef authors | Report authors | Author verdict | Year match | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.trc.2021.103291 | 200 | Synthetic population and travel demand for Paris and Ile-de-France based on open... | MATCH | Sebastian Horl, Milos Balac | Horl & Balac (2021) | MATCH | 2021 = 2021 | MATCH |
| D2 | 10.1016/j.procs.2021.03.089 | 200 | Introducing the eqasim pipeline: From raw data to agent-based transport simula... | MATCH | Sebastian Horl, Milos Balac | Horl, S. (2021) only, no co-author listed | **AUTHOR MISMATCH** (Balac silently dropped) | 2021 = 2021 | AUTHOR MISMATCH |
| D3 | 10.1016/j.scs.2020.102408 | 200 | Urban building energy modeling (UBEM) tools: A state-of-the-art review of bott... | MATCH | Martina Ferrando, Francesco Causone, Tianzhen Hong, Yixing Chen | Ferrando, Causone, Hong, Chen (2020) | MATCH | 2020 = 2020 | MATCH |
| D4 | 10.1016/j.trc.2021.103118 | 200 | Synthesising digital twin travellers: Individual travel demand from aggregated... | MATCH | Cuauhtemoc Anda, Sergio A. Ordonez Medina, Kay W. Axhausen | Anda, Ordonez Medina, Axhausen (2021) | MATCH | 2021 = 2021 | MATCH |

All 4 DOIs resolve. Wrong author lists: 1 of 4 (D2, Section H reference list gives Horl as sole
author; CrossRef lists two authors, Horl and Balac).

---

## 2. Use claims

| # | Claim (source cited) | Abstract words | Verdict |
|---|---|---|---|
| U1 | B1 row 1: "eqasim provides an entirely open, reproducible pipeline that synthesizes individual daily activity schedules... for Ile-de-France, Lyon, and Switzerland" (cited to D1, Horl & Balac 2021) | D1's abstract (OpenAlex) covers only "Paris and its surrounding region Ile-de-France"; it names no other city. Lyon and Switzerland are not mentioned. | **NOT IN ABSTRACT** |
| U2 | B1 row 3: "exactly 100% of in-home activities are collapsed into home" (cited to D2, Horl 2021) | D2's abstract describes the eqasim framework generally ("consistent pipeline from raw data to a final transport simulation... combining MATSim simulations with flexibly definable discrete choice models... for Ile-de-France, Switzerland, Sao Paulo and California"). No mention of activity-category collapse or a "100%" figure. | **NOT IN ABSTRACT** |
| U3 | Section A / B1 row 4: "several pioneering studies have coupled agent-based transport models (MATSim, POLARIS) with urban building energy models (such as AutoBEM and CityGML pipelines)... successfully demonstrated in US testbeds (AutoBEM/POLARIS in Chattanooga, TN)" (cited to D3, Ferrando et al. 2020) | D3 has no abstract in CrossRef or OpenAlex; the ScienceDirect page (fetched via its DOI redirect) returned only a "Redirecting" stub, no abstract text, and no occurrence of "AutoBEM", "POLARIS" or "Chattanooga" on the page reached. | **NO ABSTRACT** (unverifiable) |
| U4 | C1 L04: "Synthesized individual traveler schedules by combining mobile phone tracking data with agent-based transport models" (D4, Anda et al. 2021) | Abstract: "we propose a framework designed only with user-aggregated mobile phone data to synthesise realistic daily individual mobility" | **SUPPORTED** |
| U5 | C1 L02: "Documented the modular architecture of the open-source eqasim pipeline" (D2) | Abstract: "introduces the eqasim framework with the aim to provide a consistent pipeline from raw data to a final transport simulation" | **SUPPORTED** |
| U6 | C1 L03: "Reviewed bottom-up physics-based UBEM tools and examined coupling mechanisms between urban mobility and building thermal loads" (D3) | No abstract available (see U3). | **NO ABSTRACT** |
| U7 | C1 L01: "Built and validated an open synthetic population and 24-hour activity demand pipeline for Paris and Ile-de-France" (D1) | Abstract: "this paper introduces a process for generating a synthetic travel demand with individual households, persons, and their daily activity chains for Paris and its surrounding region Ile-de-France... entirely based on open data and open software" | **SUPPORTED** |

Note on U1/U3: the report's Section A headline sentence rests on exactly one paper (D3, Ferrando et
al. 2020, a review article) for the claim that transport-model-to-UBEM coupling has been
"successfully demonstrated." That paper's abstract could not be read (no CrossRef or OpenAlex
abstract; the ScienceDirect landing page only redirects). No other row in Table C1 names a primary
study that actually performed such a coupling; C1's own "What it did NOT do" column says D1, D2 and
D4 explicitly did **not** touch building energy. So the report's central coupling claim is carried
by a single unverifiable citation to what its own title says is a tools review, not a primary
coupling demonstration.

---

## 3. URLs and quoted strings

| # | URL (Table F1 row) | HTTP status | Notes |
|---|---|---|---|
| W1 | `https://github.com/eqasim-org/eqasim-java` (eqasim IDF & Lyon row) | 200 | Page loads, but this is the eqasim **simulation engine** repo, not the France population-synthesis pipeline. The actual France/Lyon pipeline lives at `github.com/eqasim-org/eqasim-france` (confirmed reachable, 200); its README lists Lyon only as one worked "case" (`cases/lyon.html`), documentation for running the pipeline on Lyon, not a separate ready output. |
| W2 | `https://github.com/eqasim-org/switzerland` (eqasim Switzerland row) | **404** | Repo does not exist at this path. Actual repo (confirmed reachable, 200) is `github.com/eqasim-org/eqasim-switzerland`. |
| W3 | `https://github.com/matsim-scenarios/matsim-berlin` | 200 | Loads. |
| W4 | `https://github.com/ActivitySim/activitysim` | 200 | Loads. |
| W5 | `https://www.anl.gov/es/polaris` | **404** | Page does not exist. Tried variants `anl.gov/es/polaris-model` (404) and `polarismodel.org` (connection failed). An `anl-polaris` GitHub org does exist (200) with repos `PILATES`, `polaris-analyser`, `polaris-dependencies`, `MEP`, but no repo named plainly `polaris` under it, and the report's stated URL is unreachable either way. |

Quoted strings (licence / access terms) checked against the fetched page text:

| # | Quoted string | Row | Page's actual licence (SPDX, from repo metadata) | Verdict |
|---|---|---|---|
| Q1 | "MIT License" | eqasim IDF & Lyon (W1) | **GPL-2.0** | **NOT FOUND / CONTRADICTED** |
| Q2 | "MIT License" | eqasim Switzerland (W2, and confirmed on the real repo `eqasim-switzerland`) | **GPL-2.0** | **NOT FOUND / CONTRADICTED** |
| Q3 | "GPL / Open Data" | MATSim Berlin (W3) | GPL-2.0 (confirmed) | FOUND (license matches; "10 %, 100 % samples" also confirmed: page text contains "10pct", "1pct" and "100%") |
| Q4 | "BSD 3-Clause" | ActivitySim (W4) | BSD-3-Clause (confirmed) | FOUND |
| Q5 | "Academic license required" | POLARIS (W5) | Page not reachable (404) | PAGE NOT READABLE |
| Q6-Q9 | "Free worldwide" (appears on 4 rows: eqasim IDF & Lyon, Switzerland, Berlin, ActivitySim) | Table F1 | Not a phrase that appears verbatim on any GitHub page; it is the report's own paraphrase of licence scope, presented in a column meant to carry quoted access terms per brief section 9 rule 4 ("terms that forbid... are quoted, not summarised"). | NOT FOUND (verbatim) |

Both eqasim licence claims are wrong in the same direction (MIT claimed, GPL-2.0 actual), and the
Switzerland and POLARIS repository URLs the report gives do not resolve.

---

## 4. Key numeric facts

| # | Fact | Verdict | What I tried |
|---|---|---|---|
| N1 | eqasim-java/eqasim-france licence = MIT | **CONTRADICTED** | GitHub repo metadata reads GPL-2.0 (SPDX id) for both `eqasim-java` and `eqasim-france` |
| N2 | eqasim Switzerland licence = MIT | **CONTRADICTED** | GitHub repo metadata for `eqasim-switzerland` reads GPL-2.0 |
| N3 | ActivitySim licence = BSD 3-Clause | CONFIRMED | GitHub repo metadata reads BSD-3-Clause |
| N4 | MATSim Berlin licence = GPL / Open Data, "10%, 100% samples" | CONFIRMED | GitHub repo metadata GPL-2.0; page text contains "10pct" and "100%" |
| N5 | POLARIS access terms = "Academic license required", URL `anl.gov/es/polaris` | NOT CONFIRMED | Page 404; could not locate an ANL POLARIS licence statement at any URL tried |
| N6 | Ile-de-France synthetic population scale = "12 million agents" (Table C1 L01) | NOT CONFIRMED | Not stated in D1's abstract (CrossRef has no abstract field; OpenAlex abstract gives no population count) |
| N7 | "approx. 15% to 20%" of population are non-traveling / statically generated (B1 row 5) | NOT CONFIRMED | Source given is "Transport modeling literature review (MATSim / ActivitySim)", not a specific paper or page; no percentage found on the ActivitySim or MATSim-Berlin pages fetched |

---

## 5. Completeness

T27 prompt items, checked against the report:

| Item | Ask | Status |
|---|---|---|
| Item 1 (Section F) | Data-source cards for eqasim IDF, Switzerland, Lyon, "any other eqasim cities" | **ANSWERED, incompletely.** Only IDF and Switzerland get rows. "Lyon" is folded into the IDF row's label but not given its own card. "Any other eqasim cities" (the eqasim org has public repos for Bavaria, California and Sao Paulo, confirmed by listing `github.com/eqasim-org`) is silently **DROPPED** -- never mentioned. |
| Item 1 (Section F) | MATSim open scenarios (Berlin, other published) | ANSWERED for Berlin only; "other published scenarios" DROPPED, no NOT-FOUND note. |
| Item 1 (Section F) | ActivitySim example regions | ANSWERED AS NOT FOUND in effect -- row says "example regional populations included" but names no region, and the fetched ActivitySim README names none either. |
| Item 1 (Section F) | POLARIS | ANSWERED, but the cited URL 404s (see Section 3). |
| Item 1 (Section F) | Montreal/Quebec/Toronto models | ANSWERED (MATSim-Montreal, TASHA rows). |
| Item 1 (Section F) | "any Spanish (Madrid), Italian (Bologna) or London open scenario" | **DROPPED.** "Madrid", "Bologna" and "London" do not appear anywhere in the report (checked by full-text search, case-insensitive). No row, no NOT-FOUND note, no mention at all. |
| Item 2 (Section C) | Which model, which building side, what occupancy variable crossed over, spatial scale, validated? | **ANSWERED with weak columns.** Table C1 has no "building side" or "occupancy variable crossed over" or "validated?" columns at all; that information, where present, is buried in free-text "What it did" cells. Three of the four Table C1 rows (L01, L02, L04) are pure transport-synthesis papers that the table's own "What it did NOT do" column says never touched building energy -- so only one row (L03, a review, not a primary coupling study, abstract unreadable) actually answers item 2's "coupled to buildings" test. |
| Item 3 (Section E) | In-home detail, weekends, non-travelers, within-day return trips, AND "any work that enriched travel plans with time-use diaries for in-home activities" | Weaknesses are discussed. The specific sub-ask -- prior work enriching travel plans with time-use diaries -- is **DROPPED**: no citation is given; Section G4 instead asserts "the specific integration of time-use micro-activity diaries... is unclaimed" as an opinion, without having searched for or ruled out prior art, and without a NOT-FOUND label. |
| Item 4 (Section G) | Calibration methods and whether targets include time at home | ANSWERED. |
| Data-source card columns (brief section 9) | source/custodian; country/geography; years covered/still updated; unit; occupancy variable quoted; temporal resolution; spatial resolution; sample size; roles R1-R4; access route + Canadian-researcher eligibility (quoted, dated); licence + redistribution (quoted); selection bias; one verified building-energy use or NONE FOUND | **Almost entirely MISSING.** Table F1's actual columns are: Model & custodian, Geography & scenario, Pipeline open?, Output data open?, In-home activities split?, Repository URL & access terms. Missing: years covered/still updated, unit, quoted occupancy-variable text, temporal resolution, spatial resolution, sample size, R1-R4 roles, Canadian-researcher eligibility, redistribution terms, selection bias, and a verified building-energy use example (or NONE FOUND) for each row. |
| Brief section 9 rule 3 | Unreachable datasets go in Section G as `COULD NOT OPEN` | Not followed literally; the report uses "NO RETRIEVABLE FILE" for Montreal/Toronto instead (functionally similar, different label; text-searched, `COULD NOT OPEN` appears 0 times). |

---

## 6. Dashes

`py` count on the report file: U+2014 (em dash) = 0. U+2013 (en dash) = 0.

---

## 7. Rules

- No named individual connected to a fellowship programme.
- No proposal to change the 4J gate.
- No claim that the report itself was vetted or accepted (Section G4 explicitly says all DOIs and
  URLs were "verified", which Sections 1 and 3 above show is only partly true: 2 of 5 URLs 404, 2 of
  4 licence claims contradicted, 1 of 4 author lists wrong).

---

## Angle-decision-relevant findings

- Section A's central claim -- that transport-model-to-UBEM coupling has been "successfully
  demonstrated" (AutoBEM/POLARIS, Chattanooga) -- rests on one review-paper citation whose abstract
  could not be read at all (Section 2, U3/U6). No primary coupling study is named anywhere with a
  checkable DOI.
- Open synthetic populations: eqasim's actual licence is GPL-2.0, not the "MIT License" the report
  states twice (Section 3/4, Q1/Q2, N1/N2); the Switzerland repo URL and the POLARIS URL both 404
  (Section 3, W2/W5).
- Lyon is real but is a documented "case" inside the `eqasim-france` pipeline, not the separate
  output the report's Table F1 implies via the `eqasim-java` engine-repo URL.
- Madrid, Bologna, London, and eqasim's other public cities (Bavaria, California, Sao Paulo) are
  named in the prompt and never mentioned in the report at all (Section 5).
