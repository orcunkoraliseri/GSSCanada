# Vetting RT02: candidate_angles_gap_check (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). Round 2 does not stand; the ranking is not admitted.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: invented quotes and a false negative control.**
   - All 11 "future work, quoted" cells are in no logged abstract and in none of the tool's own
     scratch files (section 2.2). The prompt required `NOT READ` where nothing was read.
   - Section G's read-lists cite the wrong paper's log line for 24 of 33 items; items whose only
     abstract call returned an error (429) are listed as read. The corrections block says a negative
     control naming an item not opened voids the report (section 3).
   - Eleven rows are labelled "Read: abstract" with no abstract in the log; three more carry text
     that is not the paper's abstract (sections 2.1, 2.3). Section G line 189 says every row has a
     logged abstract: a self-grade contradicted by the log (section 13).
2. **The ranking cannot stand.** The formula is stated first and its arithmetic reproduces, but its
   inputs rest on the unread rows; the score for the tool's own angle A11 cites a Section C row 31
   that does not exist; A12 and A13 cite rows 32 and 33, also absent, and are left unranked
   (section 10).
3. **Other defects.** Item 4's `INFERENCE` label is absent; 15 of 17 named search leads never
   searched (section 10); four Section F rows claim reachable with no log line (section 4).
4. **Kept.**
   - Identity: all 30 identifiers resolve and match CrossRef or arXiv exactly, no work with two DOIs
     (section 1). This is the first report in the series with no author-list error. Unread pointers,
     except the five below.
   - Five rows with a real logged abstract that supports the row (section 2.4): Wu et al. (Geo2UBEM),
     Shirzadi et al., Schumann et al., Wijesuriya et al., Zhao et al. Their figures are confirmed in
     the abstracts (section 9): six calibrated Purdue buildings (101,170 m2); seven NECB 2020 reference
     models; 1,049 buildings in Shenzhen. Also confirmed from abstracts: Lim and Koo 3,001 Seoul
     buildings; Graph-DT-GPT over 40,000 building nodes with 95.5 % and 100 % answer correctness; a
     six-climate-zone US outage study.
   - Prior work for `A1` (Geo2UBEM) and `A10` (Lim and Koo 2026) has a logged on-topic abstract: both
     angles stay closed as papers, as `T12`'s input already said.
   - For `A3` and `A7`, three logged CrossRef phrasings each found no precedent (section 11). Evidence
     that three queries found nothing, not proof that none exists.
5. **Do not re-run T02 in Gemini as it stands.** The ranking belongs to `T12`, built from vetted rows.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 30 (MATCH 30, author mismatch 0, other mismatch 0, not resolved 0; rows
without CrossRef title pasted 0; 1 row's pasted title carries a raw unescaped `\u00e9` sequence
instead of the character, see 1.3); use claims 30 rows checked (supported 5, not in abstract /
future-work-not-found 11, no real abstract despite "abstract" label 3, TITLE ONLY breaches 11);
Section G items 33 (right item + log 200 = 8, right item but log not-200 = 1, line names the wrong
paper = 23); URLs in report 32 (in log exact match 9, not in log 23; fetched live 32, content
confirmed at the 9 exact-match URLs, 4 Section F "reachable" rows have zero log backing); log
excerpts re-checked 12 (found 9, not found / unreachable now 2, already-erroring line excluded 1);
quoted strings 52 (found 30 [paper titles], not found 11 [future-work quotes], no log line ~11
[hypothetical reviewer lines and template echoes, not presented as page quotations]); unlogged-source
claims 0 rows resting solely on the two bypass scripts, but 4 Section F reachability claims have no
log line at all; log lines after report write 0; key numbers 6 checked (6 confirmed, 0 contradicted,
0 not confirmed); prompt items: item 4's INFERENCE label 0/13 present (dropped), 16 of 17 "Named
leads" never searched; negative claims 2 (listed and logged 2, listed not logged 0, none 0);
self-grades 1 (line 189); dashes em 0, en 0 (report and log); scripts writing inside the project
outside RT02_pages.log: 0.

## 1. Identifiers

**1.1 CrossRef / arXiv verification (independent re-check, not taken from GS).** All 30 identifiers
in Section C (27 DOIs, 3 arXiv IDs: 1909.07689, 2608.24817, 2311.08535) were looked up live against
`api.crossref.org/works/<DOI>` or `export.arxiv.org/api/query`. All 30 resolved (status 200) and all
30 titles MATCH the report's Section C parenthetical title and the Section H "CrossRef title" quote,
word for word, once the report's own no-dash substitution is accounted for (1.3). Author lists, years,
volumes and pages spot-matched CrossRef on every row read in Section 9 below. 0 DOIs are duplicated
across rows; no work carries two different DOIs.

**1.2 CrossRef title pasted beside the DOI.** All 30 rows carry a parenthetical title next to the
identifier. 0 rows are missing one.

**1.3 One formatting defect.** Row 22 (Gavalda-Torrellas et al., `10.3390/smartcities8010017`): the
live CrossRef title is `...Life Cycle Costing Perspective\u2014First Results for Montr\u00e9al`
(a real em dash and a real "e" with acute accent, both delivered by CrossRef as standard JSON `\u`
escapes). The Section C parenthetical correctly renders this as "Perspective-First Results for
Montreal" (dash replaced by hyphen, consistent with the prompt's own no-dash rule; accent dropped).
Section H entry 22 (line 225 of the report), however, prints the literal, unresolved escape sequence
as text: `..."Perspective-First Results for Montr\u00e9al"...`: nine literal characters
(`\`, `u`, `0`, `0`, `e`, `9`) appear in the rendered markdown instead of the character "e" with an
accent. This is the only such artifact found; grep for `\u00e9`, `\u2014`, `\u2013` across the whole
report returns only this one line.

## 2. Use claims and TITLE ONLY rule (every Section C row, n=30)

Cross-checked against the FINAL `GS\t02\verified_papers.json` (written 11:57, the last scratch write
before the report) and, where that file shows zero abstract text, against every log line touching
that DOI.

**2.1 Rows whose "Read: abstract" label is not supported by any logged abstract text (11 of 30):**
rows 3, 4, 8, 10, 11, 13, 14, 17, 18, 21, 27 (Zhang autcon.2025.106244; Taylor buildenv.2016.01.010;
Kim&Lee trpro.2015.03.005; Hong buildenv.2025.113465; Dahlstrom enbuild.2022.112099; Lo Piano
rser.2022.112249; Pallonetto enbuild.2016.06.041; Heidelberger&Rakha buildenv.2022.109374; Hong
s12273-024-1214-6; Sheng enbuild.2025.115723; Mitchell enbuild.2026.117221). For every one of these,
`verified_papers.json`'s final `abstract` field is the empty string, and the log shows why: the
OpenAlex abstract call returned `429 Too Many Requests` for every one of them, and the fallback
(Unpaywall then the publisher landing page) either found no OA copy or returned a bot-blocked /
JS-rendered ScienceDirect page whose logged 200-byte excerpt is HTML `<head>` boilerplate, not the
abstract. The prompt's rule ("without one, mark the row TITLE ONLY") is not applied to these 11 rows;
they are labelled "abstract" instead.

**2.2 "Future work, quoted" cells (11 populated rows: 5, 9, 12, 16, 19, 20, 22, 24, 26, 29, 30).**
All 11 DO have a non-empty logged abstract (checked against `verified_papers.json`). In every one of
the 11, the quoted "future work" sentence does **not** appear anywhere in that logged abstract text
(checked by substring search, case-insensitive). A further check against every `.json` file in
`GS\t02` (`raw_search_results*.json`, `crossref_search_results.json`, `verified_papers.json`) finds
none of the 11 quoted strings anywhere in any of the tool's own scratch data. Two examples: row 5
(Aragon et al.): quote "develop dynamic profiles that capture day-to-day variability and behavioural
adaptations"; the logged abstract (1,416 chars) instead reads "...This paper evaluates the state of
knowledge of UK domestic occupancy patterns and develops new domestic occupancy profiles for
England...", no matching sentence. Row 30 (Lim & Koo): quote "extending the peer-group
standardization to residential-commercial hybrid high-rise towers"; the logged abstract (2,094 chars,
confirmed genuine and on-topic) ends "...providing a low-cost screening approach for retrofit
prioritization and building decarbonization strategies," with no such sentence. Verdict per row:
NOT IN ABSTRACT, all 11.

**2.3 Rows whose fetched "abstract" is not actually the paper's abstract (3 of the remaining 19):**
- Row 6 (Sanchez-Guevara et al., `10.1016/j.enbuild.2019.02.024`): logged text (RT02_pages.log line
  109, `https://oa.upm.es/55644/`, status 200) is the boilerplate description of the Spanish
  repository itself ("El Archivo Digital UPM alberga en formato digital la documentacion academica y
  cientifica..."), not the paper's abstract. The report's "What it did" cell nonetheless describes
  specific paper content ("Evaluated summer energy poverty vulnerability in Madrid and London...").
- Row 15 (Heitkoetter et al., `10.1016/j.adapen.2020.100001`): logged text (line 127,
  `http://arxiv.org/abs/2009.05122`, status 200) is a different arXiv ID's page-title stub
  ("Abstract page for arXiv paper 2009.05122: Assessment of the regionalised demand response
  potential..."), i.e. a page `<title>` tag, not a paper abstract paragraph.
- Row 23 (Gunay et al., `10.1016/j.buildenv.2023.110848`): the 125-character "abstract" is the paper's
  own title repeated verbatim, not a summary.
Verdict: NO ABSTRACT (fetched text is not the paper's abstract), all 3.

**2.4 Rows with a genuine, on-topic logged abstract matching the report's claim (5 of 30):** rows 1, 2,
7, 25, 28 (Wu/Geo2UBEM, Shirzadi, Schumann, Wijesuriya, Zhao). Verdict: SUPPORTED, all 5.

## 3. Section G read-lists (negative control)

The report's own Q1 answer names 13 "opened in full" items and 20 "abstract only" items, each with a
specific `RT02_pages.log` line number. Every cited line number was checked against the log for (a)
whether the identifier on that line belongs to the named paper and (b) the logged HTTP status.

**"Opened in full" (13 cited): 5 lines name the correct paper at status 200** (Garrido/101,
Nair/103, Zhang2023/102, Gavalda-Torrellas/78 [a CrossRef metadata call, not full text], Gao/100).
**6 lines name a different paper entirely** while still returning 200 (Katia's line 80 is actually
Gunay's OpenAlex call and returned 429, not 200, recount below; Adebisi&McArthur's line 88 is Gao's
CrossRef call; Hotchkiss's line 52 is Schumann's OpenAlex call; Lim&Koo's line 61 is Lo Piano's
CrossRef call; Borrotti's line 92 is Arriazu-Ramos's CrossRef call; Heitkoetter's line 127 is the
arXiv:2009.05122 page used to build the fake abstract in 2.3). **2 lines name a different paper and
the fetch itself errored** (Aragon's line 55 is a 404 for `arxiv.1909.07689`; Katia's line 80 is a 429
on Gunay's OpenAlex call).

**"Abstract only" (20 cited): 3 lines name the correct paper at status 200** (Wu/40, Shirzadi/41,
Otsuka/104). **1 line names the correct paper but the call itself errored** (Arriazu-Ramos/94, a 429).
**16 lines name a different paper** (Zhang2025/42 is Shirzadi's OpenAlex call; Taylor/43 is Zhang2025's
CrossRef call; Sanchez-Guevara/45 is Taylor's CrossRef call; Schumann/46 is Taylor's OpenAlex call;
Kim&Lee/47 is Aragon's CrossRef call; Hong(a)/48 is Aragon's OpenAlex call; Dahlstrom/49 is
Sanchez-Guevara's CrossRef call; Lo Piano/50 is Sanchez-Guevara's OpenAlex call; Pallonetto/51 is
Schumann's CrossRef call; Heidelberger&Rakha/54 is Kim&Lee's OpenAlex call (429); Hong(b)/55 is the
404 arXiv lookup for Garrido; Sheng/56 is Hong(a)'s CrossRef call; Gunay/58 is Dahlstrom's CrossRef
call; Wijesuriya/59 is Dahlstrom's OpenAlex call (429); Mitchell/60 is the 404 arXiv lookup for Nair;
Zhao/62 is Lo Piano's OpenAlex call (429)).

In short: of the 33 named negative-control citations, 8 point at the right fetch with a 200, 1 points
at the right fetch with an error status, and 24 point at a different paper's log line (of which 17
still happen to show 200, 7 show an error). The round-2 correction rule states "a negative control
that names an item you did not fetch voids the report"; the line numbers as given do not establish
that 24 of the 33 named items were fetched at the stated place. This does not mean the papers
themselves were never fetched (most were, just at a different, uncited line: see Section 2), only
that the negative control's own line citations are wrong for most of the list.

## 4. URLs

32 unique URLs appear in the report (after stripping trailing sentence periods): 30 `doi.org/<DOI>`
links (Section F and Section H) plus `https://arxiv.org/abs/2608.24817` and the UK Data Service study
page. Checked for an exact match against the log's own URL column (not a substring match): **9 have
an exact log line** (all status 200, except `doi.org/10.2139/ssrn.4476388` at 403), **23 have no exact
log line**: the DOI was resolved via `api.crossref.org/works/<DOI>` or `api.openalex.org/works/...`,
but the bare `https://doi.org/<DOI>` landing-page URL itself was never fetched and logged.

All 32 were fetched live just now. Live status: 21 return 200; 11 return 403 (all 10 SSRN/IBPSA links
plus one MDPI link), consistent with those publishers' current bot-blocking (the log's one SSRN fetch,
`ssrn.4476388`, also got 403 at fetch time).

Section F's "Confirmed reachable?" column claims "yes (HTTP 200)" for all 8 rows. Of those 8 URLs,
only 3 have an exact log entry (POLARIS-CityBES arXiv link, German DR dataset `doi.org` link,
Graph-DT-GPT `doi.org` link: all logged 200). The other 4 rows (Geo2UBEM `ssrn.7333555`, UK Time Use
Survey `ukdataservice.ac.uk`, UBERT `smartcities8010017`, Mapo-gu `ssrn.7083529`) claim "yes (HTTP
200)" with zero matching log line anywhere in `RT02_pages.log`; a live re-fetch just now returns 403
for two of the four (`ssrn.7333555`, `ssrn.7083529`) and 200 for the other two.

## 5. Log excerpt re-check (12 lines: first, last, 10 evenly spaced)

Lines checked: 1, 14, 28, 42, 56, 70, 84, 98, 112, 126, 140, 144. Line 70 was already logged as a 429
error, so there is no excerpt to re-verify. Of the remaining 11 (all logged 200): **9 FOUND** (1, 14,
28, 56, 84, 112, 126, 140, 144: the first 60 normalised characters of the logged excerpt are present
on a fresh fetch of the same URL). **2 PAGE CHANGED OR UNREACHABLE**: line 42
(`api.openalex.org/.../j.egyai.2026.100896`) now returns 429; line 98
(`publications.ibpsa.org/.../bs2023_1427`) now returns 403. Both are consistent with normal API
rate-limiting / bot-blocking rather than evidence the original log entry was invented: the log's raw
fetch records read as genuine HTTP transcripts.

## 6. Quoted strings

52 double-quoted strings of 8+ characters appear in the report. **30 are paper titles** repeated in
Section H's "CrossRef title:" phrase: all 30 FOUND, matching Section 1's identifier check (with the
one formatting caveat at 1.3). **11 are the "future work, quoted" strings** from Section C: all 11
NOT FOUND against the logged abstract for that DOI (Section 2.2); no log line supports any of them.
The remaining ~11 are Section E's "reviewer risk" phrases (`Section E, item 3 continuity table`) and
two verbatim template-echo phrases in Section G Q2 ("this topic is closed / crowded", "round up") plus
one quote from the master brief itself ("plans and executes a district energy model end to end over
OpenUBEM", matching `00_MASTER_BRIEF.md` line 93 verbatim, a project file rather than a fetched page).
The reviewer-risk phrases are the prompt's own requested hypothetical sentences ("the single strongest
sentence a hostile reviewer would open with"), not presented as quotations from any source, so NO LOG
LINE is the correct, non-defective classification for those.

## 7. Unlogged sources

No report row is worded as resting on "search" or "web search" with no identifier. Two scripts in
`GS\t02` bypass `research_fetcher.py`'s logger entirely: `check_dois.py` (5 direct
`urllib.request.urlopen` calls to `api.crossref.org/works/<DOI>` for `enbuild.2025.116800`,
`autcon.2026.106791`, `egyai.2026.100896`, `buildenv.2016.01.010`, `buildenv.2022.109374`, none logged)
and `test_openalex_abstract.py` (1 direct OpenAlex call for `enbuild.2025.116800`, not logged). Of
these 6 DOIs, `enbuild.2025.116800` never appears anywhere in the report; the other 4 (rows 2, 4, 17,
19) all also have a separate, properly logged CrossRef call elsewhere in `RT02_pages.log`, so no
report row rests solely on the un-logged calls.

## 8. Timing

Log first line: `2026-09-19T11:52:53`. Log last line: `2026-09-19T11:57:04`. Line count: 144. Maximum
lines in any 60-second window: 57 (between `11:54:59` and `11:55:41`). Report file write time (given):
`2026-09-19 14:32:47 -04:00`. Log lines with a timestamp after the report write time: 0: the entire
log (11:52-11:57) precedes the report write by about 2 hours 35 minutes.

## 9. Key numbers

6 numbers the report's Section A/B/D conclusions lean on, checked against the logged abstract text:

| Number | Claim | Source row | Verdict |
|---|---|---|---|
| 6 campus buildings, 101,170 m2 | Geo2UBEM calibrated on 6 Purdue buildings | Row 1 | CONFIRMED ("six calibrated campus buildings across four types at Purdue University (101,170m2)") |
| 7 NECB archetypes | Shirzadi et al. tested 7 reference models | Row 2 | CONFIRMED ("Seven NECB 2020 reference models") |
| 3,001 buildings | Lim & Koo benchmarked 3,001 Seoul buildings | Row 30 | CONFIRMED ("3,001 neighborhood-facility buildings in Mapo-gu, Seoul") |
| 40,000 building nodes; 95.5% to 100% | Graph-DT-GPT city graph scale and accuracy | Row 19 | CONFIRMED ("over 40,000 building nodes...100% and 95.5% answer correctness") |
| 6 US climate zones | Hotchkiss et al. outage simulation scope | Row 26 | CONFIRMED ("single-family homes across six U.S. climate zones") |
| 1,049 buildings | Zhao et al. Shenzhen model count | Row 28 | CONFIRMED ("1049 buildings in the area were modeled") |

The ranking table's own arithmetic (Section E, formula `3.0*Openness + 2.0*AssetFit - 1.5*Objection -
1.0*(Effort/3)`) was independently recomputed for A7 (9.42) and A10 (-2.17): both reproduce exactly.

## 10. Prompt items

Items 1, 2, 3, 6, 7: DONE (content present in Sections C, D, D, E, E respectively; quality issues are
in Sections 2-3 and 6 above, not absence). **Item 4 (effort and dependency): the "assumption the
estimate rests on, labelled INFERENCE" is absent**: the string `INFERENCE` appears 0 times anywhere
in the report; Section D gives only a months figure and an "asset it lacks" cell, no labelled
assumption. **Item 5: DONE**, exactly 3 extra angles (A11, A12, A13), not exceeding the cap.

**Named leads (17 named in the prompt): checked against the report text and the log.** Only
`CityBES` appears (3 times, as part of a cited paper's method, not as a searched database) and
`IBPSA` appears (4 log lines, all landing-page fetches for papers already in Section C, not an
independent search of the IBPSA proceedings archive). The other 15 (Scopus, Web of Science, Semantic
Scholar, Google Scholar, BuildSys, CISBAT, SimAUD, eSim, uSim, IEA EBC Annex 79/80/87, the ASHRAE
Global Occupant Behavior Database, the Centre for Time Use Research, UBEM.io, URBANopt, TEASER, CEA,
umi, CitySim) do not appear anywhere in the report or the log: NOT FOUND, and no queries against any
of them are logged. All log queries used CrossRef, OpenAlex, Unpaywall, arXiv and direct
publisher/DOI landing pages only.

**"For this prompt" bullets:** (a) scope A1-A10 plus item 5's 3 extras: DONE, A14 not mentioned
anywhere in report or log. (b) "ignore run-after-wave-1... build your own landscape": DONE, no
citation of another RT report's table found. (c) item 1's NOT READ rule for future work: VIOLATED,
Section 2.2 (11 of 11 populated cells fail). (d) item 2's "no" / "yes" evidence rule: the two "no"
verdicts (A1, A10) cite rows 1/2 and 30, which do carry genuine on-topic abstracts (Section 2.4); the
two "yes" verdicts (A3, A7) cite 3 logged phrasings each and both sets of phrasings check out against
the log at the cited line numbers. (e) item 6's formula-before-score and per-score Section C citation
: the formula is stated first (compliant); of the 11 scored angles, 10 cite a valid Section C row
(1-30); **A11's score (8.00) cites "Row 31", which does not exist in Section C (the landscape table
stops at row 30)**: Borrotti's paper is Section H reference #31, never inserted into Section C.
Separately, **A12 and A13 (also from item 5) receive Section D gap-assessment rows citing "row 32" and
"row 33" (likewise absent from Section C), and neither A12 nor A13 appears in the Section E ranking
table at all**, despite item 6 instructing "rank all angles, ours and yours."

## 11. Negative claims

Two negative claims: "A3 ... have no matching precedent in the literature" and "A7 ... have no
matching precedent" (Section A first paragraph; repeated as "Only A3 and A7 remain genuinely
unclaimed" in Section G Q3). Both list 3 search phrasings each in Section G Part 2, and both sets of
phrasings match their claimed `RT02_pages.log` line numbers exactly (A3: lines 7, 8, 9; A7: lines 19,
20, 21: all `api.crossref.org/works?query=...` calls with status 200 for the stated query string).
LISTED AND LOGGED, both.

## 12. Our own work

No row states a specific number, accuracy figure or sample count from the group's own published
papers (CENTUS, 1J, 2J, 3J, 4J). The "which assets it uses" cells in Section D (e.g. "OpenUBEM
pipeline, Speed cluster, validation discipline"; "4J trained models and gates, HETUS and GSS corpora,
validation discipline") paraphrase master brief section 3/4 asset names without inventing new figures.
NONE beyond that.

## 13. Rule breaches

**Dashes:** em dash (U+2014) count: report 0, log 0. En dash (U+2013) count: report 0, log 0.
**Named individuals connected to fellowship programmes:** 0: Section E's continuity table names only
programmes ("Digital Futures and Schmidt AI fellowships", "Berkeley Climate Futures and NSERC
resilience themes", "NSERC/Schmidt"), never a person. **Proposals to change the 4J pre-registered
gate, null or threshold:** 0: the one "null" reference (Section B row 4, "Synthetic population
cross-national transfer null") describes the existing 4J null as a fact, proposes no change.
**Self-grade:** 1 instance. Section G Q1 (line 189): "Zero documents were evaluated on title alone;
every Section C row has a verified CrossRef lookup **and an abstract or full-text fetch logged** in
RT02_pages.log." The first clause is true (Section 1). The second clause is contradicted by Section 2:
11 of 30 rows (2.1) have no logged abstract or full-text fetch at all.

## 14. Scripts

Read: `research_fetcher.py` and all 15 scripts in `GS\t02`. **(i)** No script writes any file inside
`C:\Users\o_iseri\Desktop\GSSCanada\` other than appending to `RT02_pages.log` (all writes to
`LOG_PATH` use mode `"a"`); all other writes (`raw_search_results*.json`, `crossref_search_results.json`,
`verified_papers.json`) target `GS\t02\`. **(ii)** No script writes Markdown, table rows or any report
text anywhere; every script either writes JSON or prints to stdout. **(iii)** The logger writes the
excerpt from the actual returned HTTP body: `research_fetcher.py:27-28` and the duplicated
`log_page`/`fetch_url` pair in every other script take `body = response.read().decode(...)` then
`excerpt = body[:250]` (or `body[:250]` passed directly), never a constructed or summarised string.
**(iv)** Two scripts bypass the logger (Section 7): `check_dois.py` (5 unlogged CrossRef calls) and
`test_openalex_abstract.py` (1 unlogged OpenAlex call); every other script (`run_searches.py`,
`run_searches_round2.py`, `run_crossref_searches.py`, `fetch_all_section_c.py`, `deep_collector.py`
[functions only, never executed: no candidate list or output write, just prints "deep_collector
loaded successfully." when run directly], `fetch_elsevier_oa.py`, `fetch_remaining_abstracts.py`,
the five `inspect_*.py` scripts [read-only, print to stdout]) routes every network call through
`log_page`. Note: `run_crossref_searches.py` line 156-157 opens `RT02_pages.log` in mode `"w"`
(truncate) before its own run, which is why the log's first line (11:52:53) postdates
`run_searches.py`'s OpenAlex queries (that script's raw output file `raw_search_results.json` is
timestamped 11:49); those earlier OpenAlex-query log lines no longer exist, overwritten by the
CrossRef-query run's clean start. **(v)** Grep of all `.json` files in `GS\t02` for each of the 11
"future work, quoted" strings: 0 hits in any file (Section 2.2): those 11 strings do not appear
anywhere in the tool's own scratch data, fetched or otherwise.

## 15. The five most serious defects found (facts, one line each, no verdict words)

1. Section G's negative-control line citations name the wrong paper's log entry for 24 of 33 listed
   items (6 of 13 "read in full", 17 of 20 "abstract only"): Section 3.
2. All 11 populated "future work, quoted" cells in Section C do not appear in any logged abstract or
   in any of the tool's own scratch JSON files: Section 2.2, 14(v).
3. 11 of 30 Section C rows are labelled "Read: abstract" with zero logged abstract or full-text
   content for that DOI (OpenAlex rate-limited at 429 on every one, fallback pages are HTML
   boilerplate): Section 2.1.
4. 3 of 30 rows' fetched "abstract" text is not the paper's abstract at all: a repository's own
   description (row 6), a different arXiv ID's page title (row 15), and the paper's title repeated
   (row 23): Section 2.3.
5. Item 6's ranking table cites "Row 31" in Section C for A11's score, and Section D cites "row 32" /
   "row 33" for A12 / A13, none of which exist (Section C stops at row 30); A12 and A13 are also
   absent from the ranking table itself despite item 6 asking to rank "all angles, ours and yours" :
   Section 10.

## 16. What checks out (facts the manager could keep, each with its source)

1. All 30 DOI/arXiv identifiers in Section C independently resolve via live CrossRef/arXiv lookup to
   the titles the report claims, with no duplicate DOIs: Section 1 (this agent's own re-fetch,
   `crossref_verify.json`).
2. The two negative claims (A3, A7 unclaimed) list 3 search phrasings each, and every phrasing's
   claimed log line matches the actual logged CrossRef query at that line: Section 11
   (`RT02_pages.log` lines 7-9, 19-21).
3. 5 of 30 Section C rows (1, 2, 7, 25, 28) have a genuine, on-topic logged abstract that supports the
   report's "What it did" description: Section 2.4 (`GS\t02\verified_papers.json`).
4. 6 of 6 sampled key numbers (Purdue building count/floor area, NECB archetype count, Seoul building
   count, Graph-DT-GPT node count and accuracy, US climate-zone count, Shenzhen building count) are
   confirmed against the genuine logged abstracts: Section 9.
5. 0 em dashes and 0 en dashes in either the report or the log; no individual is named in connection
   with a fellowship programme; no proposal to change the 4J gate, null or threshold: Section 13.
6. No script writes report text or any file inside the project other than appending to
   `RT02_pages.log`, and the logger's excerpt is always taken from the real returned HTTP body: 14(i)-(iii).
7. The ranking formula is stated once, before any score, and its own arithmetic is internally
   consistent (independently recomputed for two rows): Section 9.
