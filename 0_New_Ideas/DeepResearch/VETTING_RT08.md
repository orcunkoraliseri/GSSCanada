# Vetting RT08: heat_vulnerability_health_equity (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). Round 2 does not stand; its mortality shares are not admitted as written.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: the numbers item 1.2 exists for are wrong against documents the tool had fetched.**
   - BC 2021 "93 % (574 of 619) in private residences": the fetched Coroners PDF gives 452 of 619,
     73.0 % (Table 7, page 38) (section 9).
   - BC 2021 "99 % lacked central air conditioning": the same PDF gives 66.9 % No, 7.4 % Yes, 24.1 %
     unknown (Table 11, page 39).
   - Chicago 1995 odds ratios given as 2.2 and 0.2; the logged Semenza abstract says 6.7 (did not
     leave home each day) and 0.3 (working air conditioner).
   - Chicago "84 % (285 of 339) at home indoors", the headline of Section A, is in no logged source.
2. **Read claims without reads.** Six Section C rows are marked read (full or abstract) and describe
   content, while the log holds only CrossRef metadata with no abstract (sections 2, 15): the
   `TITLE ONLY` rule broken six times.
3. **Other defects.**
   - Four of nine author lists wrong against CrossRef (Semenza et al.: two given names; the BC
     chronic-disease paper credited to its last author, year 2022 for 2023; White-Newsome et al.: two
     invented co-authors, four omitted; Reid et al.: one given name) (section 1).
   - Section F: six index or tool rows say "reachable, HTTP 200" with no URL; two contradict logged
     404s, three have no log line (section 4).
   - Twelve named items dropped, including the Pacific Northwest and Western Europe shares although
     on-topic sources were fetched, and France and Italy indices (section 10).
4. **Kept** (each re-found at source by the checker):
   - BC 2021 Coroners review (619 deaths): 98 % of heat injuries occurred indoors (pages 5, 17);
     67 % aged 70 or older (page 5); 56 % lived alone (page 5, Table 8); 73.0 % in private
     residences, 452 of 619 (Table 7, page 38); air conditioning present 7.4 %, absent 66.9 %,
     unknown 24.1 % (Table 11, page 39). The document's own title is "Extreme Heat and Human
     Mortality: A Review of Heat-Related Deaths in B.C. in Summer 2021".
   - Semenza et al. 1996 (Chicago 1995), abstract: not leaving home each day, odds ratio 6.7;
     working air conditioner, odds ratio 0.3.
   - Pointers only, fetched in the log and never used by the report: Multnomah County 2021 final
     report, 68 of 72 (94 %) died in their own residence (page 10); Ballester et al. 2023, Nature
     Medicine, 61,672 heat deaths in Europe in summer 2022 (abstract).
   - Identity only: nine DOIs resolve to on-topic papers; five match CrossRef exactly (Taylor et al.
     2016, Katia et al. 2023, Heidelberger and Rakha 2022, Walker and Day 2012, Sovacool and Dworkin
     2015); the other four are kept with the CrossRef author lists, not the report's (section 1).
   - The two negatives (no coupled building-energy and time-activity exposure model; no energy-poverty
     indicator using time at home) rest on real logged queries that returned nothing, cited at wrong
     line numbers (section 11). Weak evidence of absence, not proof.
5. **Do not re-run T08 in Gemini as it stands.** The kept BC and Chicago figures are enough for the
   `A2` and `A9` framing in `T12`; any further share is read by a checker from the logged documents.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 10 (MATCH 5, author mismatch 4, other mismatch 1, not resolved 0; rows
without CrossRef title 0); use claims 10 (supported 4, not in abstract 0, contradicted 0, no abstract
6; TITLE ONLY breaches 6); Section G items 13 (in log 200 13, not 200 0, not in log 0); URLs in
report 10 (in log 10, not in log 0; fetched 10, content confirmed 10); log excerpts re-checked 18
(found 17, not found 0, unreachable/changed 1); quoted strings 9 (found 9, not found 0, no log line
0); unlogged-source claims 6; log lines after report write 0; key numbers 10 (confirmed 3,
contradicted 4, not confirmed 3); prompt items 31 (done 19, not found 0, dropped 12); negative
claims 2 (listed and logged 2, listed not logged 0, none 0); self-grades 0; dashes em 0, en 0;
scripts writing inside the project 0.

## 1. Identifiers

Report file write time given in task: 2026-09-19 14:37:05 (-04:00). All 9 DOIs re-fetched
independently from `https://api.crossref.org/works/<DOI>` on 2026-09-19; all returned HTTP 200.

| # | DOI | CrossRef title (paraphrase, <=90 chars) | Report author list | CrossRef author list | Report year/vol/page | CrossRef year/vol/page | Verdict |
|---|---|---|---|---|---|---|---|
| C1 | 10.1056/nejm199607113350203 | Heat-Related Deaths during the July 1995 Heat Wave in Chicago | Semenza, Rubin, Falter, **Jack D. Selanikio**, Flanders, **H. Lynn Howe**, Wilhelm | Semenza, Rubin, Falter, **Joel D. Selanikio**, Flanders, **Holly L. Howe**, Wilhelm | 1996/335/84-90 | 1996/335/84-90 | AUTHOR MISMATCH (2 of 7 names wrong: "Jack D." vs "Joel D."; "H. Lynn" vs "Holly L.") |
| C2 | 10.1029/2022gh000729 | Chronic Diseases Associated With Mortality in British Columbia... 2021... Extreme Heat Event | "Sarah B. Henderson et al." (2022) | Michael Joseph Lee, Kathleen E. McLean, Michael Kuo, Gregory R. A. Richardson, **Sarah B. Henderson** (2023) | 2022 | 2023 | AUTHOR MISMATCH (Henderson is 5th/last author, cited as if lead) + META MISMATCH (year 2022 vs 2023) |
| C3 | 10.1016/j.envres.2011.10.008 | Climate change and health: Indoor heat exposure in vulnerable populations | White-Newsome, Marie S. O'Neill, **C. Arden Pope**, Brisa N. Sanchez, **Stuart A. Batterman** | White-Newsome, Brisa N. Sanchez, **Olivier Jolliet**, **Zhenzhen Zhang**, **Edith A. Parker**, **J. Timothy Dvonch**, Marie S. O'Neill | 2012/112/20-27 | 2012/112/20-27 | AUTHOR MISMATCH (2 of 5 report names are not on the CrossRef record at all; 4 real co-authors omitted) |
| C4 | 10.1016/j.buildenv.2016.01.010 | Mapping indoor overheating and air pollution risk modification across Great Britain | Taylor, Davies, Mavrogianni, Shrubsole, Hamilton, Das, Jones, Oikonomou, Biddulph | same | 2016/99/1-12 | 2016/99/1-12 | MATCH |
| C5 | 10.26868/25222708.2023.1427 | Integrating unacknowledged socioeconomic energy vulnerabilities in UBEM workflows | Katia, Sherif, Rakha | same | 2023/18/(no page) | 2023/18/(no page) | MATCH |
| C6 | 10.1016/j.buildenv.2022.109374 | Inclusive urban building energy modeling through socioeconomic data | Heidelberger, Rakha | same | 2022/222/109374 | 2022/222/109374 | MATCH |
| C7 | 10.1289/ehp.0900683 | Mapping Community Determinants of Heat Vulnerability | Reid, **Michael S. O'Neill**, Gronlund, Brines, Brown, Diez-Roux, Schwartz | Reid, **Marie S. O'Neill**, Gronlund, Brines, Brown, Diez-Roux, Schwartz | 2009/117/1730-1736 | 2009/117/1730-1736 | AUTHOR MISMATCH (given name "Michael" vs "Marie"; the correct given name, Marie, is used elsewhere in the same report for the same person in row C3) |
| C8 | 10.1016/j.enpol.2012.01.044 | Fuel poverty as injustice: Integrating distribution, recognition and procedure | Walker, Day | same | 2012/49/69-75 | 2012/49/69-75 | MATCH |
| C9 | 10.1016/j.apenergy.2015.01.002 | Energy justice: Conceptual insights and practical applications | Sovacool, Dworkin | same | 2015/142/435-444 | 2015/142/435-444 | MATCH |
| non-DOI | BC Coroners PDF (row C10) | Actual document title (page 3 of the PDF): "Extreme Heat and Human Mortality: A Review of Heat-Related Deaths in B.C. in Summer 2021" | Report's title: "Extreme Heat Death Review Panel: A Review of Heat-Related Deaths in Summer 2021" | n/a | n/a | n/a | TITLE MISMATCH (report's title differs from the title printed on the fetched document itself) |

CrossRef title is pasted beside every DOI in every table row: yes, 9/9. No work carries two
different DOIs. 0 DOIs failed to resolve (round 1 had 5 of 5 exposure-model DOIs fail or mismatch;
round 2's 9 literature DOIs all resolve to genuinely on-topic papers, but 4 of 9 have author-list
and/or year errors against the record the tool itself fetched).

## 2. Use claims and TITLE ONLY rule

Section C's "What it did" cell for each of the 10 rows, checked against whether an abstract or full
text (not just a CrossRef metadata call) is in the log.

| Row | Read column says | Abstract/full text actually in log? | Verdict |
|---|---|---|---|
| C1 Semenza 1996 | full | Yes: PubMed abstract fetched (log line 28, PMID 8649494) | SUPPORTED for the case-control design and risk-factor framing |
| C2 Henderson/Lee 2022GH000729 | full | Only a CrossRef metadata call with an abstract field (log lines ~40, 112); no separate full-text fetch | SUPPORTED at abstract level (chronic-disease profiles, excess deaths); "Read: full" over-states what was fetched |
| C3 White-Newsome 2012 | abstract | No: CrossRef record has an empty abstract field (confirmed by independent refetch); no other fetch of this paper is in the log | NO ABSTRACT / TITLE ONLY breach -- the row still states specific content ("28 homes... Detroit") that no logged source names |
| C4 Taylor 2016 | abstract | No: CrossRef abstract field empty; no other fetch logged | NO ABSTRACT / TITLE ONLY breach |
| C5 Katia 2023 | full | No: CrossRef abstract field empty; the conference paper itself was never fetched | NO ABSTRACT / TITLE ONLY breach; the row and Section B row 6 both assert specific numeric content ("0.3% to 27%") with no logged source |
| C6 Heidelberger 2022 | abstract | No: CrossRef abstract field empty; no other fetch logged | NO ABSTRACT / TITLE ONLY breach |
| C7 Reid 2009 | full | Only a CrossRef metadata call, which does carry a real abstract (log lines ~42, 98) | SUPPORTED at abstract level; "Read: full" over-states what was fetched. Abstract says "factor analysis"; report's Section B row 7 says "principal component analysis" (a different, though related, technique) |
| C8 Walker and Day 2012 | full | No: CrossRef abstract field empty; no other fetch logged | NO ABSTRACT / TITLE ONLY breach (report's claim closely paraphrases the title itself, so it is low-risk, but it is still unlogged) |
| C9 Sovacool and Dworkin 2015 | full | No: CrossRef abstract field empty; no other fetch logged | NO ABSTRACT / TITLE ONLY breach (same as above) |
| C10 BC Coroners report | full | Yes: PDF fetched and its text is genuinely the source (log lines 20, 125; independently re-extracted and checked page by page) | SUPPORTED for the "what it did" cell; specific numbers drawn from it are checked in section 9 below |

Net: 6 of 10 Section C rows (C3, C4, C5, C6, C8, C9) claim a "full" or "abstract" read with no
logged abstract or full text at all, only a CrossRef bibliographic/metadata call. Per the round-2
correction ("Without one, mark the row TITLE ONLY and say nothing about its content"), these 6 rows
should carry `TITLE ONLY` and the report should say nothing about paper content beyond the title;
instead each states specific content (settings, methods, findings). 2 further rows (C2, C7) are
marked "full" when the log only supports "abstract."

## 3. Section G read-lists (negative control)

Section G.3.1 lists "Opened in full" (8 items) and "Abstract / summary only" (5 items).

| Item | List | In log with 200? |
|---|---|---|
| Semenza 1996 | full | IN LOG 200 (line 28 full PubMed abstract) |
| Henderson et al. 2022 | full | IN LOG 200 (metadata + CrossRef abstract, not a separate full-text fetch) |
| White-Newsome 2012 | full | IN LOG 200 (status only; body is CrossRef metadata with an empty abstract field) |
| Katia et al. 2023 | full | IN LOG 200 (status only; body is CrossRef metadata with an empty abstract field) |
| Reid et al. 2009 | full | IN LOG 200 (metadata + CrossRef abstract, not a separate full-text fetch) |
| Walker and Day 2012 | full | IN LOG 200 (status only; empty abstract field) |
| Sovacool and Dworkin 2015 | full | IN LOG 200 (status only; empty abstract field) |
| BC Coroners Service Report 2022 | full | IN LOG 200 (PDF fetch, genuine full text) |
| Taylor et al. 2016 | abstract | IN LOG 200 (status only; empty abstract field) |
| Heidelberger and Rakha 2022 | abstract | IN LOG 200 (status only; empty abstract field) |
| CalEnviroScreen 4.0 Report 2021 | abstract | IN LOG 200 (log line 101; re-fetched now, still 200; body is an Incapsula bot-block page with an empty `<body>`, not the report) |
| ClimateJust Portal 2024 | abstract | IN LOG 200 (log line 127; re-fetched now, still 200, genuine homepage content) |
| CUSP Portal 2024 | abstract | IN LOG 200 (log line 104; re-fetched now, still 200, genuine homepage content) |

All 13 named items have a literal HTTP 200 fetch somewhere in the log, so none is `NOT IN LOG` by
the letter of the check. Qualitatively: 6 of the 8 "full" items and 2 of the 5 "abstract" items rest
on a CrossRef metadata call whose abstract field is empty, or (CalEnviroScreen) on a bot-blocked
page with no visible content -- the fetch is real and logged, but it does not contain the text the
label implies was read.

## 4. URLs

10 distinct URLs appear in the report text (9 `doi.org` links plus the BC Coroners PDF URL, counted
once). All 10 are in the log and all 10 were re-fetched now; all returned the same status as logged
and their content was confirmed to match what the report cites them for (see sections 1 and 9).

Extra check (c): Section F (items 4 and 6) names 9 indices/tools but the report gives **no URL at
all** for any of the 9 rows -- only a "Confirmed reachable? yes (HTTP 200)" cell. Re-fetched now,
matched against the log's inferred URLs (the only URLs any T08 script ever tried for these names):

| Section F row | URL(s) actually attempted (from the log/scripts) | Log status | Re-fetched now |
|---|---|---|---|
| F1 CDC Social Vulnerability Index | none found in RT08_pages.log or any T08 script | NOT IN LOG | `atsdr.cdc.gov/placeandhealth/svi/index.html` -> 404 |
| F1 CalEnviroScreen 4.0 | `oehha.ca.gov/calenviroscreen/report/calenviroscreen-40` | 200 (line 101) | 200, still an Incapsula bot-block page, empty body |
| F1 Canadian Marginalization Index (Can-MARG) | none found in RT08_pages.log or any T08 script | NOT IN LOG | a plausible PHO URL -> 404 |
| F1 ClimateJust Heat Disadvantage Tool | `www.climatejust.org.uk/` | 200 (line 127) | 200, genuine content |
| F1 Indice de Vulnerabilidad al Calor (IVE), Madrid | none found in RT08_pages.log or any T08 script | NOT IN LOG | no specific IVE URL found to test |
| F2 CDC Heat and Health Tracker | `cdc.gov/heat-health-tracker/index.html` (line 100); `ephtracking.cdc.gov/Applications/heatracker/` (line 123) | **404** and **404** | 403 and 404 now (both still non-200) |
| F2 Climate Atlas of Canada | `climateatlas.ca/heat-and-health` (line 102); `climateatlas.ca/health` (line 124) | **404** and **404** | 404 and 404 now; the bare `climateatlas.ca/` root is 200 but that is not a URL the report or any script names for this row |
| F2 EU Energy Poverty Advisory Hub Dashboard | `energy-poverty.ec.europa.eu/` | 200 (line 103) | 200, genuine content |
| F2 CUSP Energy Poverty Map | `cuspnetwork.ca/energy-poverty/` | 200 (line 104) | 200, genuine content |

So of the 9 Section F rows claiming "Confirmed reachable? yes (HTTP 200)": 4 match a genuine 200 in
the log (CalEnviroScreen, ClimateJust, EPAH, CUSP -- though CalEnviroScreen's 200 is a bot-block
page), 2 directly contradict the log, which shows 404 for both URLs any script tried for that row
(CDC Heat and Health Tracker, Climate Atlas of Canada), and 3 have no log entry at all under any
name the scripts tried (CDC SVI, Can-MARG, IVE Madrid). This is the exact failure mode the prompt's
round-2 correction for items 4 and 6 names ("If a page returns 404, find the live page and log it,
or write COULD NOT OPEN").

## 5. Log excerpt re-check

18 log lines re-checked (first line, last line, and lines spread across both the 11:49-11:56 and
14:35-14:36 clusters), plus every line a report claim leans on:

| Log line (time) | URL | Re-fetch result |
|---|---|---|
| Line 1 (11:49:41, first) | cdc.gov/mmwr/preview/mmwrhtml/00038440.htm | FOUND: still 404 |
| Line 3 (11:49:42) | crossref Semenza DOI | FOUND: title/authors/year/vol/page reproduce exactly |
| Line 26 (11:52:18) | Multnomah County PDF | FOUND: text reproduces; page 10 contains "68/72, 94%... own residence" |
| Line 28 (11:53:36) | PubMed Semenza abstract | FOUND: text reproduces exactly, including odds ratios |
| Line 31 (11:53:36) | PubMed MMWR 1995 abstract | FOUND: text reproduces |
| Line 33 (11:53:56) | PubMed Whitman abstract | FOUND: text reproduces |
| Line 34 (11:54:07) | PMC Whitman XML | FOUND: reproduces the publisher-restricted abstract-only record |
| Line 20/125 (11:51:02, 14:36:30) | BC Coroners PDF | FOUND: text reproduces across all pages checked (3, 5, 17, 38, 39) |
| Line 39 (11:55:51) | crossref Vandentorren DOI 10.1093/eurpub/ckl063 | FOUND: title "August 2003 Heat Wave in France..." European Journal of Public Health 16:583-591 reproduces; abstract field is empty |
| Line 40 (11:55:51) | crossref Ballester DOI 10.1038/s41591-023-02419-z | FOUND: abstract reproduces (61,672 heat deaths, Europe, summer 2022) |
| Line 41 (11:55:51) | crossref MMWR 70(29)e1 DOI | FOUND: title reproduces (Pacific NW heat wave June 2021) |
| Line 42 (11:55:51) | crossref Kuras DOI 10.1289/EHP556 | FOUND: title reproduces (personal heat exposure research) |
| Line 100 (14:36:08) | cdc.gov/heat-health-tracker | Re-fetched now: 403 (logged as 404) -- status changed but still non-200 |
| Line 101 (14:36:08) | oehha.ca.gov CalEnviroScreen | FOUND: same Incapsula bot-block body reproduces |
| Line 102/124 (14:36:08, 14:36:29) | climateatlas.ca/heat-and-health, /health | FOUND: both still 404 |
| Line 103 (14:36:11) | energy-poverty.ec.europa.eu | FOUND: content reproduces |
| Line 104 (14:36:12) | cuspnetwork.ca/energy-poverty | FOUND: content reproduces |
| Line 127 (14:36:32, last) | climatejust.org.uk | FOUND: content reproduces |

17 of 18 FOUND (excerpt/content reproduces on re-fetch); 1 unreachable/changed (CDC tracker's status
code drifted from 404 to 403, still not open); 0 NOT FOUND. No fabricated excerpt was detected in
any re-checked line: `research_fetcher.py`'s `log_page()` writes `body[:250]` from the actual
response, confirmed by code reading (section 14) and by these 18 independent re-fetches. The defects
found in this report sit in the step from logged data to written claims, not in the log itself.

## 6. Quoted strings

The only double-quoted strings presented as quotations in the report are the 9 "CrossRef title:
..." strings in Section H. All 9 FOUND: each matches the title independently re-fetched from
CrossRef in section 1 above (verbatim). 0 not found, 0 with no log line.

## 7. Unlogged sources

6 claims rest on a source with no log line at all:

1. Section G.1, "Western Europe... over 70% of heat fatalities occurred at home" attributed to
   Vandentorren et al. (2006, *Am J Public Health* 96: 1318-1323). The only Vandentorren-related
   fetch attempt in the whole log is a PubMed search at 11:50:54 that returned `429 Too Many
   Requests` and was never retried. A DOI for the real Vandentorren paper (10.1093/eurpub/ckl063,
   *European Journal of Public Health* 16: 583-591, not *AJPH* 96: 1318-1323) was separately
   resolved via CrossRef at 11:55:51/14:36:27, but its abstract field is empty and no other fetch of
   it exists, so the "over 70%" figure and the citation the report gives for it are both unlogged.
2. Section A / Section B row 4, "84% in Chicago in 1995" (also written as "84% (285 of 339
   decedents)" in Section G). No logged source contains this figure: the Semenza 1996 abstract
   (line 28), the Whitman 1997 abstract (line 33) and the 1995 MMWR abstract (line 31) were checked
   directly and none states an indoor share, a percentage, or a "285" count.
3. Section B row 6, "altered simulated EUI by 0.3% to 27% in Atlanta" (Katia et al. 2023). No
   logged abstract or full text for this paper exists (section 2, row C5).
4. Section F1, CDC Social Vulnerability Index "Confirmed reachable? yes (HTTP 200)". No log line
   for any SVI URL exists anywhere in RT08_pages.log.
5. Section F1, Canadian Marginalization Index (Can-MARG) "Confirmed reachable? yes (HTTP 200)". No
   log line for any Can-MARG URL exists.
6. Section F1, Indice de Vulnerabilidad al Calor (IVE), Madrid, "Confirmed reachable? yes (HTTP
   200)". No log line for any Madrid/IVE-specific URL exists.

The run transcript's own note that the tool made direct network calls outside its logger is
confirmed in section 14 below (`print_semenza.py`, `print_mmwr1995.py`, `print_pmc_whitman.py`,
`resolve_redirect.py`, `resolve_spf.py`, and the `test_*.py` scripts all call
`research_fetcher.fetch_url()` without a `log_path`). In each case the same URL was also fetched
*with* logging elsewhere in the same session, so no report row appears to rest solely on an
unlogged direct call; the 6 claims above rest on no fetch of the relevant content at all (not even
an unlogged one), except item 1, whose DOI resolution is logged but whose content-bearing claim is
not.

## 8. Timing

Log first line: 2026-09-19T11:49:41. Log last line: 2026-09-19T14:36:32. Line count: 127. Status
code counts: 100 x 200, 16 x 404, 10 x 429, 1 x ERR (SSL failure). Maximum lines in any 60-second
window: 57 (in the 14:36:07-14:36:08 batch of key-DOI CrossRef lookups). Report file written
2026-09-19 14:37:05. Log lines after that time: 0.

There is a roughly 2h39m gap in the log between 11:56:28 and 14:35:55, consistent with the task's
note that the 11:49-11:56 activity is an earlier pass and the final pass runs from about 14:35 to
14:37.

## 9. Key numbers

10 numbers the report's conclusions and headline Section A sentence rest on, checked at their
logged source (independently re-extracted where a PDF is the source):

| # | Number | Report claim | Source checked | Result |
|---|---|---|---|---|
| 1 | 98% | BC 2021: 98% of deaths occurred indoors | BC Coroners PDF pages 5 and 17 ("98% of deaths occurred indoors"; "In almost all (98%) of the deaths, the heat injury occurred indoors"); denominator 619 (page 3) | CONFIRMED |
| 2 | 93% (574/619) | BC 2021: 93% (574 of 619) occurred in "private residences" | BC Coroners PDF page 38, Table 7 (Place of Injury): Private Residence - Multi-unit 242 (39.1%) + Private Residence - Detached 210 (33.9%) = 452/619 = 73.0% | CONTRADICTED (true value 452/619, 73.0%, not 574/619, 93%) |
| 3 | 99% | BC 2021: "99% of dwellings lacked central air conditioning" | BC Coroners PDF page 39, Table 11 (Air Conditioning Present): Yes 46 (7.4%), No 414 (66.9%), Unknown 149 (24.1%) | CONTRADICTED (true "No" share is 66.9%, not 99%; even "not confirmed Yes" is 92.6%) |
| 4 | 84% (285/339) | Chicago 1995: 84% (285 of 339) died at home indoors | Semenza 1996 PubMed abstract (log line 28); no indoor-share figure appears in the abstract at all | NOT CONFIRMED (no logged source states this number) |
| 5 | OR 2.2 | Chicago: "not leaving home daily (odds ratio 2.2)" | Same Semenza abstract: "did not leave home each day (odds ratio, 6.7)" | CONTRADICTED (logged value is 6.7, not 2.2) |
| 6 | OR 0.2 | Chicago: "working air conditioning reduced mortality risk (odds ratio 0.2)" | Same Semenza abstract: "working air conditioners (odds ratio, 0.3)" | CONTRADICTED (logged value is 0.3, not 0.2) |
| 7 | 67% | BC 2021: "67% were 70 years or older" | BC Coroners PDF page 5: "67% (415) of decedents were 70 years of age or older" | CONFIRMED |
| 8 | 56% | BC 2021: "56% lived alone" | BC Coroners PDF page 5 and Table 8 (page 38): "More than half (56%) lived alone"; 347/619 = 56.1% | CONFIRMED |
| 9 | "over 70%" | France 2003 (cited as Vandentorren 2006): "over 70% of heat fatalities occurred at home" | No logged abstract or full text for the resolved DOI (section 7, item 1) | NOT CONFIRMED |
| 10 | 0.3% to 27% | Katia et al. 2023: EUI altered "by 0.3% to 27% in Atlanta" | No logged abstract or full text for this paper at all (section 2, row C5) | NOT CONFIRMED |

3 CONFIRMED, 4 CONTRADICTED, 3 NOT CONFIRMED.

## 10. Prompt items

Corrections-block "For this prompt" bullets, checked one line each:

* (a) "every mortality share is quoted from a document whose fetch is in the log, with its
  denominator and its page or table": NOT MET for 3 of 5 numbers checked in section 9 (items 2, 3
  and 4 above give a wrong number, a wrong number, and an unlogged number respectively, despite the
  BC document itself being properly fetched and logged).
* (b) "each exposure-model row needs a resolving DOI with its CrossRef title and a logged abstract
  or full text that names the time-activity data used": no row in Section C describes a study that
  actually uses time-activity data to model exposure (Taylor 2016 explicitly "assumed static
  occupancy"; the others are epidemiology, UBEM-vulnerability or energy-justice papers). This is
  consistent with the report's own "NOT FOUND" conclusion for item 2.1, so the check applies to zero
  rows rather than failing against a populated one.
* (c) "every index and tool page carries its HTTP status in the log... If a page returns 404, find
  the live page and log it, or write COULD NOT OPEN": NOT MET, see section 4 (2 of 9 rows contradict
  a logged 404; 3 of 9 have no log entry at all; none is written as COULD NOT OPEN).

Numbered items 1-6 and named leads, condensed (DONE = content present and roughly on-topic; DROPPED
= named in the prompt, never appears in the report, whether or not it was ever fetched):

| Item / named source | Status |
|---|---|
| 1.1 indoor-temperature-predicts-mortality evidence | DONE (Section B rows 1, 5; Section C rows C1, C3) |
| 1.2 mortality shares: BC 2021 | DONE (numbers wrong, see section 9) |
| 1.2 mortality shares: Chicago 1995 | DONE (number unsourced, see section 9) |
| 1.2 mortality shares: Western Europe 2022/2023 | DROPPED as asked -- report substitutes an uncited France-2003 figure; the logged, on-topic Ballester et al. 2023 *Nature Medicine* record (61,672 heat deaths, Europe, summer 2022, with a full abstract in the log) is never cited anywhere in the report |
| 1.2 mortality shares: Pacific Northwest | DROPPED -- the Multnomah County, Oregon 2021 final report was fetched, downloaded and text-extracted (log line 26, `multnomah_extracted.txt`; 68/72, 94%, died in own residence, page 10) but does not appear anywhere in the report |
| 1.3 over-represented groups / time-at-home measured or assumed | DONE |
| 2.1 exposure models using time-activity data | DONE (NOT FOUND stated) |
| 2.2 BEM coupled to time-activity | DONE (NOT FOUND stated) |
| 3.1 EPOV / 10% / LIHC / hidden poverty / CUSP / StatCan indicator definitions | PARTIAL -- Section F2 names EPAH and CUSP but gives no indicator definitions, data sources or resolution table as asked |
| 3.2 time at home in energy-poverty indicators | DONE (NOT FOUND stated) |
| 3.3 UBEM-scale energy-burden study | DONE (Katia 2023, Heidelberger 2022; the specific number for Katia is unsourced, section 9) |
| 4 vulnerability indices: Canada | DONE (Can-MARG; reachability unlogged, section 4) |
| 4 vulnerability indices: United States | DONE (SVI, reachability unlogged; CalEnviroScreen, bot-blocked) |
| 4 vulnerability indices: Spain | DONE (IVE Madrid; reachability unlogged) |
| 4 vulnerability indices: France | DROPPED -- no French vulnerability index appears anywhere |
| 4 vulnerability indices: England | DONE (ClimateJust) |
| 4 vulnerability indices: Italy | DROPPED -- no Italian vulnerability index appears anywhere |
| 4 "name the ones a city could recompute from open data" | DROPPED -- no such column or sentence exists |
| 5 equity framing and pitfalls | DONE |
| 6 public tools | PARTIAL -- CDC tracker and Climate Atlas rows contradict the log (section 4); "city heat maps" and "EU urban data platforms" as distinct categories are not addressed |
| Named lead: *The Lancet Planetary Health* | DROPPED (a wrong-guess DOI for a Lancet Planetary Health paper was tried and 404'd; never retried; not cited) |
| Named lead: *Environmental Health Perspectives* | DONE (Reid 2009) |
| Named lead: *Environment International* | DROPPED (two wrong-guess DOIs tried, both resolved to unrelated papers, abandoned) |
| Named lead: *Urban Climate* | DROPPED (one wrong-guess DOI tried, resolved to an unrelated paper, abandoned) |
| Named lead: *Energy Research and Social Science* | DROPPED (two wrong-guess DOIs tried, both resolved to unrelated papers; the report's two justice citations are Energy Policy and Applied Energy instead) |
| Named lead: *Nature Cities* | DROPPED (no fetch attempt found anywhere in the log) |
| Named lead: *Sustainable Cities and Society* | DROPPED (no fetch attempt found anywhere in the log) |
| Named lead: BC Coroners Service heat-dome review | DONE |
| Named lead: Sante publique France | DROPPED -- fetched twice (log lines 35, 126) but not cited; the report's France citation (Vandentorren) is unlogged instead |
| Named lead: ISS Italy heat reports | DROPPED (no fetch attempt found anywhere in the log) |
| Named lead: Health Canada heat guidance | DROPPED (no fetch attempt found anywhere in the log) |
| Named lead: EU Energy Poverty Advisory Hub | DONE |
| Named lead: CUSP | DONE |
| Named lead: WHO housing and health guidelines | DROPPED (no fetch attempt found anywhere in the log) |

31 items counted; 19 DONE, 0 explicitly written up as NOT FOUND, 12 DROPPED (named in the prompt,
absent from the report).

## 11. Negative claims

2 explicit `NOT FOUND` declarations carry a query list with a cited log line:

* Section G.2, item 2.2 (coupled BEM + time-activity heat exposure): cites "RT08_pages.log line 5"
  and "line 6" for its two queries. Those two queries ARE in the log, verbatim, but at lines 75 and
  76 (2026-09-19T14:35:58 and 14:35:59), not at lines 5 and 6. Lines 5 and 6 of the actual log are
  unrelated OpenAlex 429 errors from the 11:50 session. The cited line numbers match the position of
  these two queries inside `run_t08_research.py`'s own `queries` list (1-indexed, items 5 and 6 of
  14), not the position in `RT08_pages.log`.
* Section G.2, item 3.2 (time at home in energy-poverty indicators): cites "line 7" for its query.
  Same pattern: the query is in the log verbatim at line 77 (2026-09-19T14:36:00), not line 7;
  line 7 of the script's own query list is item 7 of 14.

Both are LISTED AND LOGGED in the sense that the query text and a 200 response genuinely exist in
`RT08_pages.log`, just not at the line number the report cites.

## 12. Our own work

No row about the author's own papers, CENTUS, OpenUBEM, or any numeric result states anything beyond
what `00_MASTER_BRIEF.md` section 2/3 already says. Section E's "our proposed approach" language
(lines 58-61) is forward-looking reviewer-risk framing, not a stated result. 0 violations found.

## 13. Rule breaches

Em dashes (U+2014): 0 in report, 0 in log. En dashes (U+2013): 0 in report, 0 in log (the logger
code explicitly substitutes both with a hyphen before writing, confirmed in section 14). No
individual is named anywhere in connection with a fellowship programme (fellowships are not
discussed in this report at all). No proposal to change the 4J pre-registered gate, null or
threshold appears anywhere. Self-grade words ("verified", "confirmed", "definitive", "without
exception", "ACCEPTED") appear only as column headers copied from the response template ("DOI or
arXiv ID (verified)", "Confirmed reachable?") -- 0 instances of the tool grading its own report or
rows.

## 14. Scripts

Read: `research_fetcher.py` and all 34 files in `GS\t08\`.

(i) File writes inside `C:\Users\o_iseri\Desktop\GSSCanada\`: every script that writes to that tree
writes only to `LOG_PATH`, which is `...\DeepResearch\RT08_pages.log` (confirmed in 19 of the 34
scripts by grep). No script writes any other path inside that tree. `run_t08_research.py` line 13
opens `LOG_PATH` in write mode, but only inside `if not os.path.exists(LOG_PATH):`, and the log
already existed from the 11:49-11:56 session, so this did not truncate it.

(ii) No script writes report text (Markdown, table rows, prose sections) anywhere; all file writes
outside the log are JSON (`t08_verified_data.json`, `t08_exact_papers.json`, `doi_verified.json`,
`found_cr.json`) or a plain-text PDF extraction (`multnomah_extracted.txt`), all inside the GS
scratch folder.

(iii) `research_fetcher.py` lines 27-30: the logger writes `excerpt = body[:250]` from the actual
HTTP response body (`cleaned = " ".join(excerpt.split())[:200]`, with em/en dashes replaced by a
hyphen), not a summary or a constructed string. Confirmed independently in section 5: 17 of 18
re-fetched lines reproduce the logged excerpt's content.

(iv) Network calls that bypass the logger (call `research_fetcher.fetch_url()` without `log_path`,
or call `urllib.request.urlopen()` directly): `print_semenza.py:7`, `print_mmwr1995.py:7`,
`print_pmc_whitman.py:8` (console-display re-fetches of already-logged PubMed/PMC records);
`fetch_multnomah.py:16` and `parse_bc_pdf.py:11` (raw binary PDF downloads of URLs already logged
via a separate, logged `fetch_url()` call earlier in the same script); `resolve_redirect.py:6` and
`resolve_spf.py:6` (resolve a Google Vertex AI Search redirect URL to find the real target, not
logged); `test_cr_pm.py:6,13`, `test_oa.py:6`, `test_oa2.py:6` (early exploratory test calls with
generic queries, log_path omitted).

(v) JSON files in `GS\t08\` holding text that appears verbatim in the report: yes, expected for
correctly-cited works. `t08_verified_data.json`, `t08_exact_papers.json`, `doi_verified.json` and
`found_cr.json` all hold CrossRef titles and author strings (e.g. "Fuel poverty as injustice:
Integrating distribution, recognition and procedure in the struggle for affordable warmth") that
appear verbatim in Section C/H of the report -- this is the normal path for a correctly pasted
CrossRef title, not evidence of invented text. `doi_verified.json` and `found_cr.json` also hold
correctly-resolved records for Vandentorren 2006, Ballester 2023, MMWR 70(29)e1 and Kuras et al.
2017 that do NOT appear verbatim (or at all) in the report; see sections 7 and 10.

## 15. The five most serious defects found

1. Section A's headline sentence and Section G both state "84% in Chicago in 1995" / "84% (285 of
   339 decedents) died at home indoors"; no source in the log (Semenza 1996 abstract, Whitman 1997
   abstract, 1995 MMWR abstract) contains this figure.
2. The BC 2021 "private residence" share is given as "574 of 619, 93%"; the BC Coroners PDF itself
   (fetched and logged) states 452 of 619, 73.0% (Table 7, page 38), and the "99% lacked central air
   conditioning" figure is contradicted by the same PDF's Table 11 (page 39: 66.9% "No", 7.4% "Yes").
3. 6 of 9 index/tool rows in Section F claim "Confirmed reachable? yes (HTTP 200)" with no URL given
   in the report; 2 of those (CDC Heat and Health Tracker, Climate Atlas of Canada) directly
   contradict logged 404s, and 3 (CDC SVI, Can-MARG, IVE Madrid) have no log entry under any name any
   script tried.
4. 6 of 10 Section C rows (White-Newsome 2012, Taylor 2016, Katia 2023, Heidelberger 2022, Walker and
   Day 2012, Sovacool and Dworkin 2015) are marked "Read: full" or "Read: abstract" and describe
   specific paper content, while the log shows only a CrossRef metadata call with an empty abstract
   field for each.
5. The prompt's explicit "Pacific Northwest" and "Western Europe 2022 and 2023" mortality-share
   requirements are absent from the report despite on-topic, logged, fully-abstracted sources being
   fetched and available (Multnomah County 2021 final report, page 10: 68/72, 94%; Ballester et al.
   2023 *Nature Medicine*, full abstract: 61,672 heat deaths, Europe, summer 2022).

## 16. What checks out

* 9 of 9 report DOIs resolve to real, on-topic papers (compare round 1, where 5 of 5 exposure-model
  DOIs failed or resolved to unrelated topics). Source: independent CrossRef re-fetch, section 1.
* 5 of 9 DOI rows (Taylor 2016, Katia 2023, Heidelberger 2022, Walker and Day 2012, Sovacool and
  Dworkin 2015) match CrossRef on title, full author list, year, volume and page exactly. Source:
  section 1.
* The BC Coroners Service PDF, once fetched, genuinely supports the report's "98% indoors", "67%
  aged 70+" and "56% lived alone" figures, each with a correct page and correct denominator (619).
  Source: independently re-extracted PDF text, section 9.
* The Multnomah County 2021 PDF was correctly fetched, logged (200) and text-extracted, and its
  "94% died in own residence" figure (page 10) is internally consistent, even though the report never
  uses it. Source: `multnomah_extracted.txt`, section 10.
* The two `NOT FOUND` conclusions (item 2.2, coupled BEM/time-activity; item 3.2, time-at-home in
  energy-poverty indicators) are both backed by real, logged queries, just at mis-cited line numbers.
  Source: section 11.
* No em or en dash appears anywhere in the report or the log; no individual is named in connection
  with a fellowship programme; no proposal to alter the 4J gate appears; no script writes report text
  or any file inside the project other than `RT08_pages.log`. Source: sections 13-14.
