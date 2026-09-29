# Vetting RT28: Surveys That Are Not Time-Use Surveys but Ask About Presence, Work Schedules or Time at Home (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19).

Rule applied to all six round-2 reports: a row survives only if this checker confirmed it at its
source; a row that is contradicted, or whose quote or fact has no log line, is struck. A log line
written after the text was composed does not count as reading; only the checker's own re-fetch does.

1. **Why it fails: the negative control is runner rule 10, "no quote, variable name, licence or count
   without a matching log line".** The log lines exist, but the pages do not hold what is quoted.
   - The headline variable, the Labour Force Survey `WAH_10` and its wording, is on none of the five
     logged pages (N1).
   - All three Census definitions are cited to pages about other concepts (population group,
     Indigenous ancestry, class of worker) (section 6, rows 17 to 19).
   - Two Section C quotes join a real opening clause of the abstract to an invented clause naming the
     English Housing Survey (rows 3 and 4).
   - Both RECS PDFs returned the same HTML page, so the four RECS variables were never read (section 4).
   - The Section G numbers for Pabilonia and Vernon have no source (N7).
   - Contradicted: the ACS "worked from home" code is 11, not 12, and `JWAP` is arrival time, not
     departure (N2); the internet-use survey's frequency is "Occasional", not biennial (N3).
2. **Kept, as checked pointers only (section 15):**
   - `USHRSPRI` definition, verbatim.
   - SHEU Table 8.1b (thermostats by owner or renter). Table 8.2a: winter dwelling temperature
     "when there and awake" and "when asleep"; the "not there" state is not on the logged page.
   - ACS `WKHP` and `JWMNP`; the Canadian Housing Survey runs every 2 years.
   - The four journal DOIs match CrossRef. Chen et al. 2022 (stochastic occupant-driven energy use in
     ResStock) stays as an unread pointer.
3. **Runner rules.** The text was written by a script holding the prose (rule 12), recorded, not the
   reason for the verdict. Every log line comes before the text was composed. Two log excerpts are
   metadata, not page text (lines 43 and 44). The word "exhaustive" in Section A has no search
   behind it (section 11). No dashes, no gate proposal, no named individual.
4. **What to tighten: do not re-run in Gemini.** Variable names must come from a codebook that was
   actually downloaded and searched. The Labour Force Survey and Census public-use codebooks and the
   RECS 2020 codebook are free downloads. Checking one variable in a codebook is mechanical work for a
   cheap agent, not deep research.

**What this means for the "other surveys constrain the diary" form (A14, role R2 constrain):** open
and unassessed. Which Canadian survey carries a usable work-from-home or presence variable, and at what
frequency, is not established by this report. SHEU's thermostat-by-occupancy-state tables are the one
confirmed Canadian presence-linked source.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 5 (MATCH 4, author mismatch 0, other mismatch 0, not resolved 1 [StatCan
catalogue DOI, not CrossRef-indexed]); use claims 3 (supported 0, not in abstract 2, contradicted 0,
no abstract 1); URLs in report 35 (in log 35, not in log 0; fetched live today 23, content confirmed
6, content contradicted or not found 17); log excerpts re-checked 14 (found 9, not found 5,
unreachable 0); quoted strings 35 (found 8, not found 20, no log line 7 -- some strings fall in more
than one category, see table); unlogged-source claims 2 (Section G's whole empirical narrative;
Section A's "exhaustive audit"); log lines after compose time 0 of 83; key numbers 9 (confirmed 3,
contradicted 5, not confirmed 1); prompt items 16 named leads (carded 16, not found 0, dropped 0);
dashes em 0, en 0 (report and log both).

---

## 1. DOIs

All identifiers in Section H, checked against `https://api.crossref.org/works/<DOI>` live today.

| # | DOI | CrossRef status | CrossRef title | CrossRef authors, year, vol, pages | Report states | Verdict |
|---|---|---|---|---|---|---|
| D1 | 10.1016/j.apenergy.2022.119890 | 200 | "Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model" | Jianli Chen, Rajendra Adhikari, Eric Wilson, Joseph Robertson, Anthony Fontanini, Ben Polly, Opeoluwa Olawale; 2022; Applied Energy; vol 325; p.119890 | Same title, same 7 authors in same order, same year/vol/page | MATCH |
| D2 | 10.1080/09613218.2017.1399719 | 200 | "Developing English domestic occupancy profiles" | Victoria Aragon, Stephanie Gauthier, Peter Warren, Patrick A. B. James, Ben Anderson; 2019; Building Research & Information; vol 47; pp.375-393 | Same title, same 5 authors, same year/vol/pages | MATCH |
| D3 | 10.1016/j.enbuild.2015.11.039 | 200 | "Combining energy efficiency measure approaches and occupancy patterns in building modelling in the UK residential context" | Erica Marshall, Julia K. Steinberger, Valerie Dupont, Timothy J. Foxon; 2016; Energy and Buildings; vol 111; pp.98-108 | Same title, same 4 authors, same year/vol/pages | MATCH |
| D4 | 10.1007/s11150-022-09601-1 | 200 | "Telework, Wages, and Time Use in the United States" | Sabrina Wulff Pabilonia, Victoria Vernon; 2022; Review of Economics of the Household; vol 20; pp.687-734 | Same title, same 2 authors, same year/vol/pages | MATCH |
| D5 | 10.25318/71m0001x-eng | 404 ("Resource not found") | n/a | n/a | Given as the LFS PUMF catalogue DOI, no CrossRef title pasted beside it (correctly, since it is a StatCan product DOI, not a journal-article DOI CrossRef indexes) | NOT RESOLVED (expected for a non-journal DOI; report does not claim a CrossRef title for it, so this is not a rule-1 breach) |

Note on process (log lines 81-83): the tool first tried DOI `10.1007/s11150-022-09605-3` for
Pabilonia & Vernon, got CrossRef 404, then found the correct DOI via an OpenAlex title search and
confirmed it. The self-correction happened before the report was written; only the corrected DOI
appears in RT28.

All four journal-article DOIs used in the report MATCH CrossRef on every field checked (title, full
author list and order, year, volume, pages).

---

## 2. Use claims (Section C)

Abstracts pulled from `https://api.openalex.org/works/https://doi.org/<DOI>`
(`abstract_inverted_index` rebuilt) and from CrossRef's `abstract` field.

| Row | Report's use claim | Abstract source | What the abstract actually says | Verdict |
|---|---|---|---|---|
| C1 Chen 2022 | Used EIA RECS & ATUS; extracted `ATHOME`, `TEMPHOME`, `TEMPGONE`, `TEMPNITE`; parameterized stochastic occupant presence and thermostat setpoints in ResStock | OpenAlex: no `abstract_inverted_index`. CrossRef: no `abstract` field. No full-text URL for this paper appears anywhere in `RT28_pages.log` | Cannot be checked against any source the tool actually opened | NO ABSTRACT (the report's quoted sentence and the RECS/ATUS/variable claims have no log line) |
| C2 Aragon 2019 | Used EHS & UK Time Use Survey; extracted `Hhldheat`, `Heatwkday`, `AllDayOcc`, `NumOccs` | OpenAlex abstract rebuilt successfully | Abstract: "The interview sample from the English Housing Survey 2014-15 was used to map household typologies... the paper develops occupancy patterns for England derived from 2015 UK Time Use Survey diaries for each household typology previously identified." The abstract never names `Hhldheat`, `Heatwkday`, `AllDayOcc` or `NumOccs`, and states the occupancy PATTERNS come from the Time Use Survey diaries, not from EHS heating/occupancy variables; EHS supplies only the household-typology sample | NOT IN ABSTRACT (the four named variables and the "EHS supplied the occupancy variables" framing are not supported; see quote fabrication in section 6 below) |
| C3 Marshall 2016 | Used EHS; extracted "heating schedule categories and daytime occupancy indicators" | OpenAlex abstract rebuilt successfully | Abstract: three occupancy patterns are "corresponding to a working family, a working couple and a daytime-present couple," and scenarios are "simulated using engineering building modelling software TRNSYS with data taken from literature." The word "English Housing Survey" does not appear anywhere in the abstract | NOT IN ABSTRACT (EHS is not named as the data source in the abstract; see quote fabrication below) |

This also weakens Section D: two of the three Section C rows used to justify "EHS-derived occupancy
profiles" as a precedent do not show EHS-sourced presence variables in their own abstracts.

---

## 3. Study type

The prompt does not demand a specific study type (results/protocol/review) for T28; Item 2 asks for
"works that used" the surveys and Item 3 asks for "studies that compared." All three Section C rows
and the Section G reference are presented as empirical/results papers, consistent with what CrossRef
and OpenAlex show (all four are standard journal articles, not reviews or protocols). No mismatch
found on this axis.

---

## 4. URLs

35 unique URLs appear in the report body; all 35 have a matching log line (exact or a clear substring
match), so 0 are "not in log." 23 of these were fetched live today (all StatCan IMDB/dictionary pages,
both RECS PDF links plus the RECS landing page, the ACS PUMS dictionary PDF, EU-LFS, EU-SILC, EHS,
INE, Istat, and the CHS/CIUS/COVID/SHEU StatCan survey pages). Results:

| URL (short) | Live status today | Claimed content on page | Actually found | Verdict |
|---|---|---|---|---|
| Census dict `ID=pop111` | 200 | POWST "Place of work status" | Page title and body: "Population group" | CONTENT NOT ON PAGE |
| Census dict `ID=pop145` | 200 | DEPAR "Time leaving for work" | Page title and body: "Indigenous ancestry" | CONTENT NOT ON PAGE |
| Census dict `ID=pop017` | 200 | COMMDUR "Commuting duration" | Page title and body: "Class of worker" | CONTENT NOT ON PAGE |
| LFS variable list (`Id=1587576`) | 200 | Contains `WAH_10`, `USHRSPRI`, `AHRSMAIN`, `FTPT` | Page lists LFS concept labels for August 2026 ("Usual work hours of employed person, category," "Actual hours worked...," etc.); no variable code strings anywhere; no "home," "telework," "remote" or "Location of work" concept on the page at all | CONTENT NOT ON PAGE (for `WAH_10` specifically; the hours concepts exist as labels only, no codes) |
| LFS hours definition (`assembleDESurv`, `DECId=116996`) | 200 | "Usual Work Hours definition" | "Usual work hours refers to the employed person's normal paid or contract hours, not counting any overtime." | CONFIRMED (exact match to the report's `USHRSPRI` quote) |
| LFS Guide (`71m0001x2021001-eng.htm`) | 200 | (implicitly, source for `WAH_10`) | No "WAH_10," "work from home," "telework" or "Location of work" text anywhere on the page | CONTENT NOT ON PAGE |
| LFS survey page (SDDS 3701) | 200 | (implicitly, source for `WAH_10`) | Same absence as above | CONTENT NOT ON PAGE |
| LFS catalogue (71M0001X) | 200 | (implicitly, source for `WAH_10`) | Same absence as above | CONTENT NOT ON PAGE |
| SHEU tables landing | 200 | General SHEU 2019 table index | Confirmed generic landing page, consistent | CONFIRMED (landing page only, no variable text expected) |
| SHEU Table 8.1b | 200 | "Thermostats by occupation mode (owner, renter)" | "Table 8.1b - Thermostats By Occupation Mode," columns Owner/Renter/Not stated | CONFIRMED |
| SHEU Table 8.2a | 200 | Three states: "when there and awake," "when sleeping," "when not there" | Found: "Dwelling temperature when there and awake during the winter" and "Dwelling temperature when asleep during the winter" (page says "asleep," not "sleeping"). "when not there" does not appear anywhere on page 1 (the only page logged) | PARTIALLY CONFIRMED (2 of 3 states; wording of the second is paraphrased, not verbatim; third state absent from the logged page) |
| RECS 2020 Questionnaire PDF | 200 | Questionnaire text with `ATHOME`, `TEMPHOME`, `TEMPGONE`, `TEMPNITE` | Returns a generic EIA "Consumption & Efficiency" HTML landing page, 54,621 bytes, `content-type: text/html`, identical byte-for-byte length to the codebook fetch below -- not the questionnaire | CONTENT NOT ON PAGE (fetch did not reach the questionnaire) |
| RECS codebook PDF | 200 | Codebook text | Same generic EIA HTML page, same 54,621 bytes | CONTENT NOT ON PAGE (fetch did not reach the codebook) |
| RECS 2020 landing page | 200 | General RECS 2020 portal | Confirmed real landing page; its own `.pdf` links are table files (`HC 1.1.pdf` etc.), not the questionnaire or codebook the report names | CONFIRMED (landing only) |
| ACS PUMS Data Dictionary 2022 PDF | 200 | `JWAP`/`DEPAR` = departure time; `JWMNP`; `JWTRNS` code 12 = "Worked from home"; `WKHP` | Real 134-page PDF. `JWAP` = "Time of arrival at work," not departure. The departure-time variable is `JWDP`. `JWTRNS` code for "Worked from home" is **11**, not 12 (code 12 is "Other method"). `JWMNP` = "Travel time to work" (matches). `WKHP` = "Usual hours worked per week past 12 months" (matches) | MIXED: `WKHP`/`JWMNP` CONFIRMED; `JWAP` variable/concept pairing and `JWTRNS` code both CONTRADICTED |
| EU-LFS microdata page | 200 | `HOMEWK` "Working at home," codes 1/2/3 | Page is an access-and-collections page; lists "EU-LFS scientific use files" and separately "EU-LFS public use files" as two different access tiers. No variable named `HOMEWK` or `HOMEWORK`, and no question wording, appears anywhere on the page | CONTENT NOT ON PAGE (variable name/wording); also see access-tier note below |
| EU-SILC microdata page | 200 | `HH050`, `HH010`/`HH020` variable codes | Access/collections page; no variable codes found | CONTENT NOT ON PAGE |
| EHS collections page | 200 | `Hhldheat`, `Heatwkday`, `AllDayOcc`, `NumOccs` | GOV.UK collections index page (list of yearly EHS report links); no variable codes on this page | CONTENT NOT ON PAGE |
| INE EPA methodology page | 200 | `TRAEST`, `HORAS` variable codes | Spanish-language methodology landing page; not checked for exact variable codes in this pass (flagged, not confirmed) | NOT CONFIRMED (time-limited) |
| Istat RFL archive page | 200 | `LAVDOM`, `ORATOT`, `TURNO` variable codes | Italian-language archive index page; not checked for exact variable codes in this pass (flagged, not confirmed) | NOT CONFIRMED (time-limited) |
| CHS survey page (SDDS 5269) | 200 | "Biennial (2018, 2020, 2022, 2024)" | StatCan field: "Frequency: Every 2 years" | CONFIRMED |
| CIUS survey page (SDDS 4432) | 200 | "Biennial (2018, 2020, 2022)" | StatCan field: "Frequency: **Occasional**." ("biennially" appears only in historical prose about the pre-2010 predecessor survey, not as the current classification) | CONTRADICTED |
| COVID survey page (SDDS 5323) | 200 | "Ad-hoc monthly / bi-monthly during 2020-2021" | StatCan field: "Frequency: Occasional" | ROUGHLY CONSISTENT (StatCan's own label is coarser than the report's) |
| SHEU survey page (SDDS 3814) | 200 | "Quadrennial / Occasional" | StatCan field: "Frequency: Irregular" | PARTIAL (report's "Occasional" is close to "Irregular"; "Quadrennial" is not the StatCan label) |

---

## 5. Log excerpt re-check

14 log lines picked across the whole log (first, last, evenly spread, plus every 200 the report leans
on for a quote), re-fetched live today and searched for the logged excerpt.

| Log line # | URL (short) | Logged excerpt (start) | Re-fetch result |
|---|---|---|---|
| 1 | `.../instrument/3701_Q1_V6` | "Archived - Labour Force Survey questionnaire..." | FOUND (title matches; not independently re-fetched in full, low risk) |
| 3 | `71m0001x2023001-eng.htm` | "We couldn't find that Web page (Error 404)" | Consistent with logged 404 status, not re-fetched (error page) |
| 16 | `.../n1/en/catalogue/71M0001X` | "Labour Force Survey: Public Use Microdata File..." | FOUND (matches live title) |
| 18 | `71m0001x2021001-eng.htm` | "Labour Force Survey: Public Use Microdata File..." | FOUND (matches live title) |
| 22 | `getSurvVariableList&Id=1587576` | "Variable(s) - Surveys and statistical programs - Labour Force Survey (LFS) - August 2026" | FOUND (matches live title exactly) |
| 26 | `assembleDESurv&DECId=116996` | "Variable(s) - ... Labour Force Survey (LFS) August 2026..." | FOUND (matches live page; body text for "Usual work hours" also confirmed, see check 4) |
| 28 | Census dict `pop111` | "Dictionary, Census of Population, 2021 - Population group" | FOUND (matches live title) -- but this is a summary/title excerpt only, not evidence for POWST wording (see check 4) |
| 29 | Census dict `pop145` | "Dictionary, Census of Population, 2021 - Indigenous ancestry" | FOUND (matches live title) -- not evidence for DEPAR |
| 30 | Census dict `pop017` | "Dictionary, Census of Population, 2021 - Class of worker" | FOUND (matches live title) -- not evidence for COMMDUR |
| 40 | SHEU Table 8.1b | "Table 8.1b \| Natural Resources Canada" | FOUND (matches live title) |
| 41 | SHEU Table 8.2a | "Table 8.2a \| Natural Resources Canada" | FOUND (matches live title) |
| 43 | RECS Questionnaire PDF | "Binary content length 54621 bytes, content-type: text/html; charset=UTF-8" | This is a metadata description, not "an excerpt of about 200 characters copied verbatim from the page body" as rule 10 requires. Re-fetch confirms the returned body IS a generic EIA HTML landing page, not the questionnaire, so the excerpt (such as it is) is honest about content-type but the format itself breaches rule 10, and the report's own "binary retrieved" annotation (line 47 of RT28) contradicts the log's own "text/html" record |
| 44 | RECS Codebook PDF | Same as line 43, identical byte count | Same finding; re-fetch confirms byte-identical generic landing page for both supposedly-different PDFs |
| 83 | CrossRef Pabilonia & Vernon | JSON starting `{"status":"ok",...}` | FOUND (status/JSON matches; confirms DOI resolved, see check 1) |

9 of 14 log lines re-checked FOUND (title/excerpt genuinely on the page); 5 flagged (2 log-format
breaches at lines 43-44, and 3 "found but not evidentiary" at lines 28-30 where the excerpt is real
but proves the page is about something else entirely, undercutting the report's own citation).

---

## 6. Quoted strings

Every double-quoted string and backticked variable name in the report (35 instances counted by
script), checked against its cited log line and, where feasible, against a live re-fetch.

| # | Quoted string / variable | Report's cited source | Verdict |
|---|---|---|---|
| 1 | `WAH_10` "Location of work" | LFS pages (5 logged URLs) | NOT FOUND on any of the 5 logged LFS pages, confirmed live |
| 2 | Chen 2022 abstract quote | (no explicit URL; implied CrossRef/OpenAlex) | NO LOG LINE (no full-text fetch logged; no abstract exists in either source) |
| 3 | Aragon 2019 quote, incl. "(1) characterizes domestic occupancy from the English Housing Survey (EHS)..." | OpenAlex abstract | NOT FOUND -- the real abstract clause at that position reads "(1) characterizes methods for collecting occupancy data and inferring patterns," not the quoted text. The quote is a fabricated splice: real sentence + ellipsis + an invented clause |
| 4 | Marshall 2016 quote, incl. "...compared for three domestic occupancy patterns derived from English Housing Survey data" | OpenAlex abstract | NOT FOUND -- the real abstract clause reads "compared for three distinct household occupancy patterns, corresponding to a working family, a working couple and a daytime-present couple." "English Housing Survey" never appears in the abstract. Fabricated splice, same pattern as #3 |
| 5-7 | "works from home exclusively" / "leaves for work between 07:00 and 07:30" / "heating set to 20C when awake" | None given (illustrative examples in prose) | NO LOG LINE (not presented as sourced quotes on their face, but are in quote marks) |
| 8 | "How did this person usually get to work LAST WEEK?" (ACS `JWTRNS`) | ACS PUMS Data Dictionary 2022 PDF | NOT FOUND -- this question-stem sentence does not appear in the 134-page dictionary PDF (checked with full text extraction); the dictionary gives variable labels and codes, not questionnaire wording |
| 9 | "Worked from home" (ACS) | Same PDF | FOUND (the label exists), but attached to the wrong code (report says 12, PDF says 11) |
| 10 | "Working at home" (EU-LFS `HOMEWK`) | EU-LFS microdata page | NOT FOUND on the logged page (an access page, not a codebook) |
| 11 | "On a typical weekday, how many days is someone at home during the day?" (RECS `ATHOME`) | RECS Questionnaire PDF | NO LOG LINE -- the logged fetch returned a generic EIA HTML page, not the questionnaire |
| 12 | "when there and awake" (SHEU) | SHEU Table 8.2a | FOUND (verbatim, live-confirmed) |
| 13 | "when sleeping" (SHEU) | SHEU Table 8.2a | NOT FOUND -- live page says "asleep," not "sleeping" |
| 14 | "when not there" (SHEU) | SHEU Table 8.2a | NOT FOUND -- absent from the logged page (page 1 only) |
| 15 | `WAH_10` full question wording | LFS pages | NOT FOUND (duplicate of #1) |
| 16 | `USHRSPRI` "Usual work hours refers to..." | LFS `assembleDESurv` page | FOUND (verbatim match, live-confirmed) |
| 17 | `POWST` "Place of work status refers to..." | Census dict `pop111` | NOT FOUND -- the cited page is titled "Population group" and never discusses place of work |
| 18 | `DEPAR` "Time leaving for work refers to..." | Census dict `pop145` | NOT FOUND -- cited page is "Indigenous ancestry" |
| 19 | `COMMDUR` "Commuting duration refers to..." | Census dict `pop017` | NOT FOUND -- cited page is "Class of worker" |
| 20-22 | SHEU 8.2a three states (Card 3, duplicate of #12-14) | Same page | Same verdicts as #12-14 |
| 23 | "Did you work from home during the past week due to COVID-19?" | SDDS 5323 survey page | NO LOG LINE -- the logged page is an IMDB metadata page; no questionnaire URL for this survey is in the log |
| 24 | `ATHOME` "On a typical weekday, how many days is someone at home during the daytime?" (Card 7, duplicate of #11) | RECS Questionnaire PDF | NO LOG LINE (same as #11) |
| 25-27 | `TEMPHOME`/`TEMPGONE`/`TEMPNITE` wording | RECS Questionnaire PDF | NO LOG LINE (fetch did not reach the questionnaire, per check 4) |
| 28 | `JWTRNS` "Worked from home" code 12 (Card 8, duplicate of #9) | ACS PUMS Dictionary PDF | Label FOUND, code CONTRADICTED (real code is 11) |
| 29 | `HOMEWK` "Person works at home" | EU-LFS microdata page | NOT FOUND (duplicate pattern of #10; this exact phrase does not appear on the page at all, nor does it match round-1's separately-verified real label "Working at home for the main job") |
| 30 | `HH050` "Ability to keep home adequately warm" | EU-SILC microdata page | NOT FOUND on the logged access page |
| 31-34 | "usual" / "primary" / "at home" / "on-site" | Prose, no cited source | NO LOG LINE (generic words in quote marks, not sourced claims) |
| 35 | Aragon 2019 quote first clause "Occupancy patterns are necessary to estimate energy demand..." | OpenAlex abstract | FOUND (this opening clause is verbatim in the real abstract; only the later spliced clause is fabricated, see #3) |

Rough tally: FOUND 8 (labels/openings genuinely on the cited page), NOT FOUND 20 (absent, wrong page,
or fabricated splice), NO LOG LINE 7 (no page ever actually reached the claimed content).

---

## 7. Unlogged sources

* Section A, line 15: "An exhaustive audit of the building energy modeling literature... confirms that
  no published building-energy study has utilized the Canadian LFS monthly microdata..." -- see check
  11 below; the closest logged search is generic and international, not Canada-specific.
* Section G, lines 296-309 (the whole "Benchmark Empirical Evidence" and "Observed Differences and
  Explanations" subsections attributed to Pabilonia & Vernon 2022): the DOI resolves correctly (check
  1, D4), but no log line shows the paper's abstract or full text was ever fetched. OpenAlex returns no
  abstract for this DOI (checked live today) and no other URL for this paper appears in
  `RT28_pages.log`. The specific numbers "5 to 10 percentage points" and "approximately 10-15%
  pre-pandemic" have no traceable source.

---

## 8. Timing

* Log first line: `2026-09-18T23:12:57`. Log last line: `2026-09-18T23:19:45`. Line count: 83.
* Maximum lines in any 60-second window: 28 (the OpenAlex/CrossRef verification burst around
  23:18:45-23:19:45).
* Report text composed (per task): `2026-09-18T23:20:21`. Report file written: `2026-09-18T23:20:37`.
* Log lines timestamped after compose time: **0 of 83**. The last log line (23:19:45) precedes compose
  time by 36 seconds; the write happens 16 seconds after compose. Unlike the timing problems recorded
  for other reports in this wave, RT28's log is entirely closed out before the report text was
  composed -- no page was opened after the citing text was written.

---

## 9. Key numbers

| # | Number | Report states | Source checked | Verdict |
|---|---|---|---|---|
| N1 | LFS work-location variable code | `WAH_10` | 5 logged LFS pages, live-refetched | CONTRADICTED (absent from all 5) |
| N2 | ACS `JWTRNS` code for "Worked from home" | Code 12 | ACS PUMS Data Dictionary 2022 PDF | CONTRADICTED (real code is 11; 12 is "Other method") |
| N3 | CIUS periodicity | "Biennial (every two years)" | StatCan SDDS 4432 page | CONTRADICTED (StatCan's own field says "Occasional") |
| N4 | SHEU Table 8.2a occupancy states | Three: "when there and awake," "when sleeping," "when not there" | SHEU Table 8.2a, live-refetched | CONTRADICTED for 2 of 3 (page says "asleep," and "when not there" is absent from the logged page) |
| N5 | `USHRSPRI` definition wording | "Usual work hours refers to the employed person's normal paid or contract hours, not counting any overtime." | LFS `assembleDESurv` page | CONFIRMED (verbatim) |
| N6 | CHS periodicity | "Biennial (2018, 2020, 2022, 2024)" | StatCan SDDS 5269 page | CONFIRMED ("Every 2 years") |
| N7 | Pabilonia & Vernon telework gap | "5 to 10 percentage points" | No abstract or full text available in any logged source | NOT CONFIRMED (no source states it) |
| N8 | Chen 2022 dataset used | EIA RECS & ATUS | No abstract in CrossRef or OpenAlex; no full-text log line | NOT CONFIRMED |
| N9 | SHEU Table 8.1b content | "Thermostats by occupation mode (owner, renter)" | SHEU Table 8.1b, live-refetched | CONFIRMED |

3 confirmed, 5 contradicted, 1 not confirmed.

---

## 10. Prompt items

Every survey named in Item 1's list and the corrections block gets a heading/card check.

| Country | Named lead | Status in RT28 |
|---|---|---|
| Canada | Labour Force Survey PUMF | CARDED (Card 1) -- but the headline variable quote (`WAH_10`) is not on any logged page (see checks 4, 6) |
| Canada | Census of Population PUMF | CARDED (Card 2) -- all three quoted variable definitions (`POWST`, `DEPAR`, `COMMDUR`) are on pages about unrelated concepts (see checks 4, 6) |
| Canada | Survey of Household Energy Use | CARDED (Card 3) -- Table 8.1b confirmed; Table 8.2a partially confirmed (2 of 3 states, one paraphrased) |
| Canada | Canadian Housing Survey | CARDED (Card 4) -- periodicity confirmed |
| Canada | Canadian Internet Use Survey | CARDED (Card 5) -- periodicity CONTRADICTED (see check 9, N3) |
| Canada | COVID-era StatCan telework survey | CARDED (Card 6) -- quoted question has no log line |
| US | Residential Energy Consumption Survey | CARDED (Card 7) -- all four quoted variables have no log line (RECS PDFs did not resolve, see check 4) |
| US | American Community Survey PUMS | CARDED (Card 8) -- mixed: `WKHP`/`JWMNP` confirmed, `JWAP` mispaired and `JWTRNS` code wrong |
| US | ATUS Leave and Job Flexibilities Module | CARDED (Card 9) -- sourced to a 403 page ("audited via NBER and academic records"); NBER URL in the log (line 58) returned 404, so the "audited via" claim also has no working log line |
| Europe | EU Labour Force Survey | CARDED (Card 10) -- variable name/wording not on the logged page |
| Europe | European Working Conditions Survey | CARDED (Card 11) -- sourced to a 429 page ("audited via UK Data Service"), no UK Data Service URL in the log |
| Europe | EU-SILC | CARDED (Card 12) -- variable codes not on the logged page |
| Europe | UK English Housing Survey | CARDED (Card 13) -- variable codes not on the logged page (a collections index, not a codebook) |
| Europe | Understanding Society | CARDED (Card 14) -- sourced to a 403 page, "audited via UK Data Service" with no such URL logged |
| Europe | Spain Encuesta de Población Activa | CARDED (Card 15) -- variable codes not checked against the (Spanish-language) logged page this pass |
| Europe | Italy Rilevazione sulle Forze di Lavoro | CARDED (Card 16) -- variable codes not checked against the (Italian-language) logged page this pass |

All 16 named leads received a full Section F card; none dropped or answered in prose only, which is
an improvement over round 1's pattern of silent drops. The defect in this round is not omission but
content: several cards cite a real, logged, HTTP-200 page whose actual content is a different concept
than the one quoted.

---

## 11. Negative claims

* Section A, line 10: "the LFS PUMF is the **sole** public Canadian survey that records
  work-from-home and work schedules at a monthly frequency with freely downloadable microdata files."
  This is a comparative claim across the report's own enumerated cards (LFS monthly vs. CHS/CIUS
  biennial/occasional), not a literature-search claim; no dedicated search query is needed or logged
  for it.
* Section A, line 15: "An exhaustive audit of the building energy modeling literature... confirms that
  no published building-energy study has utilized the Canadian LFS monthly microdata to dynamically
  adjust, re-weight, or update time-use occupancy between GSS Time Use cycles." The closest logged
  query is line 63: `("Labour Force Survey" OR "LFS") AND ("building energy" OR "work from home" OR
  "occupancy") AND "energy"`, 1,161 results, not Canada-specific and not restricted to "between waves"
  or "GSS." No query in the log combines "Canada," "LFS," "GSS," and "update between waves" together,
  and no log line shows any of the 1,161 results being opened or screened. The word "exhaustive" is not
  supported by a matching search.

---

## 12. Our own work

No row in RT28 describes the author's own papers, models or engine (OpenUBEM, CENTUS, 1J-4J). Brief
section 2 is not quoted or paraphrased anywhere in the report. No breach found on this axis.

---

## 13. Rule breaches

* Em dashes (U+2014): 0 in report, 0 in log. En dashes (U+2013): 0 in report, 0 in log.
* No named individual connected to a fellowship programme was found.
* No proposal to change the 4J pre-registered gate, null or threshold was found.
* No self-grade ("ACCEPTED," "verified," "vetted") was found; the report contains no verdict language
  about itself.
* Rule 10 (log format) breach: log lines 43-44 (`RT28_pages.log`) record "Binary content length 54621
  bytes, content-type: text/html; charset=UTF-8" as the excerpt for both the RECS questionnaire and
  codebook URLs. This is a content-metadata description, not "an excerpt of about 200 characters
  copied verbatim from the page body," and it is identical for two different claimed files -- itself
  evidence that neither fetch reached distinct PDF content.

---

## 14. The five most serious defects found (facts, one line each, no verdict words)

1. Section A's headline claim -- LFS variable `WAH_10` and its question wording -- does not appear on
   any of the five logged Statistics Canada LFS pages (variable list, hours-definition page, LFS
   guide, LFS survey page, LFS catalogue page), confirmed by live refetch of all five today.
2. All three quoted Census 2021 variable definitions (`POWST`, `DEPAR`, `COMMDUR`) are cited to
   dictionary pages that are, on both the log's own recorded titles and a live refetch, about
   unrelated concepts: "Population group," "Indigenous ancestry," and "Class of worker" respectively.
3. Two of three Section C use-claim quotations (Aragon 2019, Marshall 2016) splice a real opening
   clause of the paper's OpenAlex abstract to an invented closing clause that does not appear in the
   abstract at all ("...characterizes domestic occupancy from the English Housing Survey (EHS)..." and
   "...derived from English Housing Survey data").
4. Section G's entire empirical comparison (ATUS exceeds CPS telework by "5 to 10 percentage points";
   CPS captures "approximately 10-15%" pre-pandemic) is attributed to a correctly-identified DOI
   (Pabilonia & Vernon 2022) whose abstract or text was never fetched in the log; no source for these
   numbers exists among the opened pages.
5. Both RECS "questionnaire" and "codebook" PDF fetches (logged as "binary retrieved," HTTP 200)
   returned an identical, byte-for-byte generic EIA HTML landing page (54,621 bytes, `content-type:
   text/html`) rather than PDF content, confirmed live today; the four quoted RECS variables
   (`ATHOME`, `TEMPHOME`, `TEMPGONE`, `TEMPNITE`) have no working log line despite being presented as
   sourced from these two URLs.

---

## 15. What checks out (facts the manager could keep, each with its source)

* All four journal-article DOIs in Section H (Chen 2022, Aragon 2019, Marshall 2016, Pabilonia &
  Vernon 2022) resolve on CrossRef with title, full author list and order, year, volume and pages
  matching the report exactly. Source: `https://api.crossref.org/works/<DOI>`, checked live today.
* `USHRSPRI`'s quoted definition -- "Usual work hours refers to the employed person's normal paid or
  contract hours, not counting any overtime" -- is a verbatim match on the logged LFS `assembleDESurv`
  page (`DECId=116996`), confirmed live today.
* SHEU Table 8.1b's title, "Thermostats By Occupation Mode," and its owner/renter/not-stated column
  structure are confirmed verbatim on the logged page
  (`showTable.cfm?...rn=60&page=1`).
* SHEU Table 8.2a confirms two of the report's three thermostat states: "Dwelling temperature when
  there and awake during the winter" (exact) and a state for sleeping hours (the page's own wording is
  "asleep," close to but not identical to the report's "sleeping").
* ACS `WKHP` ("Usual hours worked per week past 12 months") and `JWMNP` ("Travel time to work") are
  confirmed verbatim in the real 134-page ACS PUMS Data Dictionary 2022 PDF, and the label "Worked from
  home" does exist as an ACS transportation-to-work category (though at code 11, not the report's 12).
* Canadian Housing Survey periodicity, "biennial," is confirmed on the logged StatCan SDDS 5269 page
  ("Frequency: Every 2 years").
* No em or en dashes appear anywhere in the report or the log (0/0 both), consistent with the hard
  rule.
* No log line in `RT28_pages.log` is timestamped after the report's compose time (23:20:21); the last
  log line (23:19:45) precedes it by 36 seconds, and the file was written 16 seconds after compose --
  the log is fully closed before the citing text exists, unlike timing problems recorded elsewhere in
  this wave.
* All 16 named leads from the prompt's Item 1 list received a Section F card; none were silently
  dropped or left as prose-only mentions, unlike round 1 of this same report family.

---

## Appendix. Method notes

DOIs checked via `https://api.crossref.org/works/<DOI>`. Abstracts attempted via
`https://api.openalex.org/works/https://doi.org/<DOI>` (`abstract_inverted_index` rebuilt) and via
CrossRef's `abstract` field; Chen 2022 and Pabilonia & Vernon 2022 returned no abstract from either
source. Official pages were re-fetched live with a standard browser User-Agent via Python `urllib`;
the ACS PUMS Data Dictionary PDF was downloaded and its text extracted with `pypdf` (134 pages,
~500,000 characters) before searching, so "not found" verdicts for that source reflect an actual text
search, not a failed fetch. The two RECS PDF URLs were also downloaded directly; both returned
identical HTML, not PDF content, confirming (rather than merely inferring from the log) that the fetch
did not reach the claimed source. Spain (INE) and Italy (Istat) variable-code claims (Cards 15-16)
were not independently checked against their logged pages in this pass due to time; flagged as
NOT CONFIRMED rather than silently passed.
