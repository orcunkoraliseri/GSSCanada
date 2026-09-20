# Vetting RT09: fellowship_and_funding_alignment (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). Round 2 does not stand; no angle-by-programme fit is admitted.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: quotes and a source that the log does not hold.**
   - The headline UC programme quote ("established in 1984 ... women and minority") is on none of
     the eight logged UC pages; the NSERC "pivotal time" quote and the MSCA goal quote are not on
     their pages (section 6).
   - The Swiss national fellowship row is marked "HTTP 200" and read, with zero log lines; it is 404
     today (section 4).
   - Two items marked "read: full text" returned an image and an empty script shell (section 3).
2. **The angle table is not scored from programme text.** Its shape is right (eleven rows, labels
   exact, columns in order), but five cells quote the brief's own wording of our drafted proposals as
   if it were a programme criterion, and most cells quote nothing (sections 6, 10). Section G then
   answers "No" to scoring from the brief (line 90).
3. **Other defects.**
   - NSERC weighting "70 % / 30 %" is contradicted: the page's only 30 % concerns awards held
     abroad (section 9). MSCA's 50/30/20 weighting and four deadlines (Digital Futures 16 and 2
     October, Schmidt 5 October, MSCA 9 September) are not on any logged page (section 9).
   - Item 2 has no funded-project identifier, though three CORDIS projects were logged and unused;
     item 5 is not done (sections 7, 10).
   - The evidence-timing table (item 4) has no source at all (section 7).
   - Self-grades on lines 79 and 92, including "verified" for deadlines that are not (section 13).
4. **Kept** (each on a logged 200 page and re-found by the checker, section 16):
   - UC Berkeley's Climate Futures fellowship is listed under the UC President's postdoctoral
     programme; that programme's deadline is 1 November 2026.
   - NSERC postdoctoral deadline 17 October; the rule that the research must be significantly
     distinct from, or go significantly beyond, the doctoral thesis.
   - MSCA mobility rule: not more than 12 months in the country in the 36 months before the deadline.
   - Digital Futures postdoctoral page carries the context labels Digitalized Industry, Rich and
     Healthy Life, Smart Society and the themes Cooperate, Learn, Trust.
   - The Berkeley research-office page and the Toronto AI in Science page both return 403: no
     criterion from either is admitted.
5. **Do not re-run T09 in Gemini as it stands.** Programme fit goes to `T12` from the kept facts
   above and from wave-1 notes that were kept, never from this table.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 0 (MATCH 0, author mismatch 0, other mismatch 0, not resolved 0; rows
without CrossRef title 0, no DOI or arXiv ID anywhere in the report); use claims 0 (no DOI/arXiv-backed
literature-finding sentences in this report; TITLE ONLY breaches 0, not applicable); Section G items 9
(in log 200 a=7 [2 of these 7 are HTTP 200 responses whose logged body is not readable text: one PNG
image, one empty JS shell], not 200 b=2, not in log c=0); URLs in report n=10 (in log a=9, not in log
b=1; fetched c=10, content confirmed d=4 full-or-partial, not confirmed 6); log excerpts re-checked
n=16 (found a=15, not found b=1 [binary PNG, line 80], unreachable c=0); quoted strings n=14 (found
b... see section 6 for the 5/9 breakdown); unlogged-source claims: the whole 15-row Section B item-4
evidence-timing table (0 log lines cited) plus Section E part 1 (0 identifiers, 0 log lines cited per
row); log lines after report write n=0; key numbers n=10 (confirmed 4, contradicted 1, not confirmed
5); prompt items n=6 main items + 8 "For this prompt"/corrections sub-rules (done 3, not found/dropped
3, partial 8; see section 10); negative claims n=1 (listed and logged a=1 [the "no individuals
searched" answer], listed not logged b=0, none c=0); self-grades n=2 (lines 79, 92); dashes em 0, en 0
(report and log); scripts writing inside the project n=0 (only RT09_pages.log is appended, as required).

## 1. Identifiers

No DOI-pattern string (`10.XXXX/...`) and no arXiv ID appears anywhere in
`RT09_fellowship_and_funding_alignment.md`. 0 rows to check. This report cites programme pages, not
literature, so Item 1's "CrossRef-returned title" and "two different DOIs" checks do not apply to any
row.

## 2. Use claims and TITLE ONLY rule

Not applicable in the literature sense (no DOI/arXiv-backed papers are described in this report). The
closest analogue, the award-history claims in Section E ("Funded projects in the built environment...
overwhelmingly emphasize cyber-physical systems..."), carry no identifier and no log line at all (see
section 10, Item 2, and section 14 on the unused CORDIS fetches). Treated under check 7
(unlogged-source claims), not here.

## 3. Section G read-lists (negative control)

Section G Q1 lists 7 items "Opened in full" and 2 "Could not open" (9 total).

| Item (report's own label) | URL | Log status | Content actually readable text? |
|---|---|---|---|
| UC PPFP Information portal | https://ppfp.ucop.edu/info/ | IN LOG 200 (lines 1, 75) | yes |
| UC PPFP Application guidelines | https://ppfp.ucop.edu/info/how-to-apply/index.html | IN LOG 200 (lines 4, 76) | yes |
| Digital Futures Postdoctoral Fellowship call | https://www.digitalfutures.kth.se/mobility/postdoc-fellowship/ | IN LOG 200 (lines 64, 93, 96) | yes |
| Digital Futures Research Matrix | https://www.digitalfutures.kth.se/research/research-matrix/ | IN LOG 200 (line 80) | **no** - the logged excerpt and a live re-fetch are both a PNG image (`Content-Type: image/png`), not HTML/text |
| MSCA PF Work Programme overview | https://marie-sklodowska-curie-actions.ec.europa.eu/actions/postdoctoral-fellowships | IN LOG 200 (lines 15, 67-equiv, 81) | yes |
| European Commission Funding & Tenders portal | https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-msca-2024-pf-01-01 | IN LOG 200 (lines 68-equiv, 82) | **effectively no** - live re-fetch returns a 289-character JavaScript application shell ("EU Funding & Tenders Portal ... Topic List") with no call text, no deadline, no criteria anywhere in the returned body |
| NSERC PDF program description | https://www.nserc-crsng.gc.ca/students-etudiants/pd-np/pdf-bp_eng.asp | IN LOG 200 (lines 74, 83) | yes |
| (could not open) UC Berkeley vcresearch Climate Futures page | https://vcresearch.berkeley.edu/climate-futures-fellowship | IN LOG NOT 200 (403, lines 18/77-equiv) | n/a, consistent with report |
| (could not open) Toronto Data Sciences Institute Schmidt AI portal | https://datasciences.utoronto.ca/ai-in-science/ | IN LOG NOT 200 (403, line 84-equiv) | n/a, consistent with report |

So 2 of the 7 items the report calls "Opened in full (HTTP 200 with excerpt in RT09_pages.log)" did
return HTTP 200 with a logged excerpt exactly as claimed, but the excerpt in both cases is not readable
page text (one is a PNG image, one is an empty script shell). The report treats both as sources of
quoted criteria (see section 6).

## 4. URLs

10 unique URLs in the report. All 10 fetched live (fewer than 20 total, so all checked).

| # | URL | In log? | Live status now | Report's own status label | Content matches report's claim? |
|---|---|---|---|---|---|
| 1 | https://ppfp.ucop.edu/info/ | yes (200) | 200 | "HTTP 200" | "established in 1984..." quote NOT on page (see section 6) |
| 2 | https://www.digitalfutures.kth.se/mobility/postdoc-fellowship/ | yes (200) | 200 | "HTTP 200" | call-description quote FOUND; deadline/eligibility numbers NOT found (section 6, 9) |
| 3 | https://marie-sklodowska-curie-actions.ec.europa.eu/actions/postdoctoral-fellowships | yes (200) | 200 | "HTTP 200" | main quote NOT found; mobility-window wording found in substance ("more than 12 months in the 36 months immediately before the call deadline") |
| 4 | https://www.nserc-crsng.gc.ca/students-etudiants/pd-np/pdf-bp_eng.asp | yes (200) | 200 | "HTTP 200" | "pivotal time" quote NOT found; distinctness rule FOUND verbatim in substance; 70%/30% weighting NOT found (section 9) |
| 5 | https://datasciences.utoronto.ca/ai-in-science/ | yes (403) | 403 | "COULD NOT OPEN" | consistent |
| 6 | https://ppfp.ucop.edu/info/how-to-apply/index.html | yes (200) | 200 | "HTTP 200" | "capstone" word not present anywhere on page; page does list "UC Berkeley Chancellor's Climate Futures Fellowship Program" under the PPFP campus list, which supports the routing claim |
| 7 | https://www.snf.ch/en/swiss-postdoctoral-fellowships | **no log line at all** | 404 | "yes (HTTP 200)" | not confirmable; no log line exists for this URL anywhere in `RT09_pages.log` (checked with `grep -n snf`, zero hits) |
| 8 | https://vcresearch.berkeley.edu/climate-futures-fellowship | yes (403) | 403 | "COULD NOT OPEN" | consistent |
| 9 | https://www.digitalfutures.kth.se/research/research-matrix/ | yes (200) | 200, `image/png` | "Tier 1... Read: full text" | page is a PNG image; no text was ever read from it |
| 10 | https://ec.europa.eu/info/.../horizon-msca-2024-pf-01-01 | yes (200) | 200, JS shell (289 chars real text) | "Tier 1... Read: full text" | no call text, deadline or criteria present in the returned body |

Row 7 (SNF) is a URL with a specific claimed status ("yes (HTTP 200)") and specific claimed content
(eligibility text, deadline framing) that has zero matching log line anywhere in `RT09_pages.log`.

## 5. Log excerpt re-check

16 log lines checked (first line 1, last line 96, 14 spread between): lines 1, 5, 13, 21, 27, 33, 41,
49, 57, 63, 67, 75, 80, 86, 92, 96.

| Line | URL | Verdict |
|---|---|---|
| 1 | ppfp.ucop.edu/info/ | FOUND |
| 5 | ppfp.ucop.edu/.../evaluation-criteria.html | FOUND (404 reproduces) |
| 13 | ppfp.ucop.edu/.../evaluation-and-selection.html | FOUND |
| 21 | diversity.berkeley.edu/programs-services/postdoctoral | FOUND |
| 27 | ppfp.ucop.edu/info/fellowship-recipients/index.html | FOUND |
| 33 | ppfp.ucop.edu/fellowship-recipients/fellows-pages/banuelos-maricela | FOUND (404 reproduces) |
| 41 | .../guerrero-gallegos-ana | FOUND (404 reproduces) |
| 49 | .../mcclellan-ufugusuku-alexyss | FOUND (404 reproduces) |
| 57 | .../stephen-samuel | FOUND (404 reproduces) |
| 63 | digitalfutures.kth.se/ | FOUND |
| 67 | rea.ec.europa.eu/.../msca-postdoctoral-fellowships_en | FOUND |
| 75 | ppfp.ucop.edu/info/ (second fetch) | FOUND |
| 80 | digitalfutures.kth.se/research/research-matrix/ | **NOT FOUND** - logged excerpt is raw PNG bytes, not page text; live re-fetch is the same PNG image |
| 86 | api.crossref.org/works?query=CORDIS%20MSCA... | FOUND |
| 92 | digitalfutures.kth.se/for-faculty/calls/?_sfm_calls_status=open | FOUND |
| 96 | digitalfutures.kth.se/mobility/postdoc-fellowship/ | FOUND |

15 of 16 FOUND, 1 NOT FOUND (line 80, non-text content).

## 6. Quoted strings

Every double-quoted string in the report that reads as a quotation, with its source line/table cell.

| Quote (report location) | Claimed source | On a logged 200 page with real text? |
|---|---|---|
| "The University of California President's Postdoctoral Fellowship Program was established in 1984 to encourage outstanding women and minority Ph.D. recipients..." (line 13) | ppfp.ucop.edu/info/ | **NOT FOUND**. Checked the live info page (3,057 characters of visible text) and all 7 other logged-200 PPFP sub-pages (how-to-apply, application-instructions, application-requirements, evaluation-and-selection, terms_of_award, about/partnerships, fellowship-recipients/index) - "1984" and "women and minority" appear on none of them |
| "Digital Futures has established a competitive international Postdoctoral Fellowship programme with regular calls for proposals..." (line 14) | digitalfutures.kth.se/mobility/postdoc-fellowship/ | FOUND |
| "The goal of the MSCA Postdoctoral Fellowships is to enhance the creative and innovative potential..." (line 15) | marie-sklodowska-curie-actions.ec.europa.eu | **NOT FOUND** in the live page text |
| "The Postdoctoral Fellowships (PDF) program provides support to a core of the most promising researchers at a pivotal time in their careers." (line 16) | nserc-crsng.gc.ca/.../pdf-bp_eng.asp | **NOT FOUND**. The live page's own title is "Canada Postdoctoral Research Award program," and "pivotal" does not appear anywhere in its 19,096 characters of text |
| "accelerating the adoption of AI in scientific research" (line 17) | datasciences.utoronto.ca (403, COULD NOT OPEN per the report itself) | NO LOG LINE with a 200 status for this URL; the report's own table marks the source COULD NOT OPEN in the adjacent cell, so this quote has no reachable source at all |
| "Digitalised Industry / Trust, Cooperate, Learn" (line 37, A1/Digital Futures cell) | not cited to a URL in the cell | FOUND in substance on digitalfutures.kth.se/mobility/postdoc-fellowship/ (page shows filter labels "Digitalized Industry," "Rich and Healthy Life," "Smart Society" and "Cooperate Learn Trust") - spelling normalised from US "Digitalized" to the report's "Digitalised" |
| "compound heat waves, passive survivability and energy inequity" (line 38, A2/Berkeley cell) | not cited to a URL | **NOT on any logged Berkeley/PPFP page**. This exact phrase is the master brief's own description (section 5) of the researcher's drafted proposal, not text from a UC page |
| "Smart Society / Rich and Healthy Life" (line 38, A2/Digital Futures cell) | not cited | FOUND in substance on the DF mobility page |
| "digital transformation, trust bounds where no meter exists" (line 43, A7/Digital Futures cell) | not cited | **NOT FOUND** on the DF mobility page or any other logged DF page; matches the master brief's own section-5 wording for the candidate DF subject, not page text |
| "AI applied in a scientific domain with an AI co-supervisor" (line 43, A7/Schmidt cell) | not cited | **NOT FOUND anywhere in the log** (Schmidt's only logged page is a 403). Matches the master brief section 5 wording verbatim |
| "compound heat waves, passive survivability in California" (line 45, A9/Berkeley cell) | not cited | **NOT on any logged page**; matches brief section 5 wording |
| "Smart Society" (line 45, A9/Digital Futures cell) | not cited | FOUND in substance on the DF mobility page |
| "passive survivability of Canadian neighbourhoods under power failure" (line 45, A9/NSERC cell, "matches drafted proposal:...") | explicitly labelled by the report as matching "drafted proposal" | this is openly sourced to the brief, not to an NSERC page; the NSERC page itself never mentions "passive survivability" or "power failure" |
| "Smart Society / open data fusion" (line 47, A14/Digital Futures cell) | not cited | "Smart Society" FOUND; "open data fusion" NOT FOUND on the DF mobility page |

5 of 14 quoted strings FOUND on a logged page with real text; 6 are NOT FOUND on any logged page (three
of those six reproduce the master brief's own wording for our drafted proposals rather than a
programme's page); 1 has no log line for its source at all; the remaining 2 (Smart Society appearances)
are counted once each under FOUND above.

## 7. Unlogged sources

- Section B, item-4 "Evidence timing table" (25 cells across 5 programmes): no quote, URL or log-line
  citation anywhere in or under this table. Every cell ("Full credit; mandatory in publication list",
  "Scored under Excellence criterion (track record)", etc.) is an unsourced statement.
- Section E, part 1 "Award distribution in recent competitions (2023 to 2026)" (3 bullets, one per
  programme cluster): no project titles, no identifiers, no URLs, no log lines. This is despite the
  page log actually containing 3 real CORDIS project fetches from the same session
  (`https://cordis.europa.eu/project/id/101153320`, `.../101110951`, `.../101073357`, all HTTP 200,
  logged at 11:55:45-11:56:22) that are never referenced anywhere in the report text (checked with
  `grep -n "cordis\|CORDIS\|10115\|10111\|10107"`, only one incidental mention of "CORDIS energy
  cohorts" with no identifier, at line 57).
- Section E, part 2 "Strategic programme conflicts": narrative claims about what reviewers "demand" or
  "risk alienating," with no source.

## 8. Timing

Log first timestamp: 2026-09-19T11:48:38. Log last timestamp: 2026-09-19T14:39:39. Line count: 96.
Report file write time given in task: 2026-09-19T14:41:01. Log lines with a timestamp after 14:41:01:
0 (the log's last line, 14:39:39, is about 1 minute 22 seconds before the report write time).

Densest 60-second window: 2026-09-19T14:39:29 to 14:39:39 contains lines 91-96 (6 lines): two duplicate
fetches of `digitalfutures.kth.se/`, `for-faculty/calls/?_sfm_calls_status=open`,
`mobility/postdoc-fellowship/`, `for-faculty/calls/`, `seven-projects-receive-digital-futures-...`, and
a second `mobility/postdoc-fellowship/`.

Lines 75-88 (14 lines, 14:38:48-14:38:58) correspond exactly to `run_t09_research.py`'s 11 programme
URLs plus 3 CrossRef queries. Lines 89-96 (8 lines, 14:39:09-14:39:39) are additional ad hoc fetches of
Digital Futures pages (a 404 on `calls-for-funding/`, two duplicate home-page fetches, two duplicate
`for-faculty/calls/` variants, the `seven-projects-receive-...` page, and two duplicate
`mobility/postdoc-fellowship/` fetches) that do not correspond one-for-one to `find_df_links.py` (that
script fetches the home page once, then up to 10 filtered links; the actual log shows duplicate URLs and
one URL, `calls-for-funding/`, not produced by either saved script's fixed URL list or its regex
filter of `digitalfutures.kth.se` links containing "postdoc", "call" or "funding" run against the home
page it fetched). This 8-line block is therefore not fully reconstructable from the two script files
saved in `GS\t09\`.

## 9. Key numbers

| # | Number | Report's claim | Source checked | Verdict |
|---|---|---|---|---|
| 1 | Nov 1, 2026 | Berkeley PPFP deadline | ppfp.ucop.edu/.../evaluation-and-selection.html: "Application Deadline November 1, 2026" | CONFIRMED |
| 2 | Oct 17, 2026 | NSERC deadline | nserc-crsng.gc.ca page: "NSERC: October 17" | CONFIRMED |
| 3 | Oct 16, 2026 | Digital Futures full-application deadline | not present anywhere in digitalfutures.kth.se pages fetched (mobility page, home page, for-faculty/calls pages) | NOT CONFIRMED |
| 4 | Oct 2, 2026 | DF pre-registration deadline | same pages | NOT CONFIRMED |
| 5 | Oct 5, 2026 | Schmidt AI in Science deadline | Schmidt's only logged page is a 403 | NOT CONFIRMED (no reachable source at all) |
| 6 | Sept 9, 2026 | MSCA 2026 call closed | msca page text and the EU F&T portal topic page (JS shell, no dates) | NOT CONFIRMED |
| 7 | 50% / 30% / 20% | MSCA "Excellence / Impact / Quality and efficiency" weighting | msca page full text (10,119 chars) | NOT CONFIRMED - none of "50%", "20%", "Impact,", "Quality and" found |
| 8 | 70% / 30% | NSERC "Research ability / Communication" weighting | nserc page full text (19,096 chars) | CONTRADICTED - the only "30%" on the page reads "Up to 30% of all postdoctoral awards will be available to be held outside of Canada," an unrelated eligibility figure, not an evaluation weight; "70%" does not appear at all except inside the dollar figure "$70,000" |
| 9 | >12 months in 36 months | MSCA mobility rule | msca page: "...for more than 12 months in the 36 months immediately before the call deadline" | CONFIRMED |
| 10 | NSERC distinctness rule | "significantly distinct from doctoral dissertation topic" | nserc page: "Your proposed research must be significantly distinct from your doctoral thesis or contribute significantly beyond your doctoral thesis." | CONFIRMED |

4 CONFIRMED, 1 CONTRADICTED, 5 NOT CONFIRMED.

## 10. Prompt items

Corrections block and "For this prompt" bullets, one line each:

- Read only 3 files (brief, template, prompt): cannot verify from outside the tool's own process; no
  evidence in the report of another `RT`/`VETTING`/`.json` file's content being reproduced. DONE (no
  contrary evidence).
- Write only 2 files in `DR\`: TRUE. Scripts write only into `GS\t09\` and append `RT09_pages.log`
  (section 14). DONE.
- Paste CrossRef title beside every DOI: not applicable, 0 DOIs. DONE (vacuously).
- Row without identifier not admitted: **breached** - Section F row 5 (SNF) has no log line
  (section 4, row 7) and Section E's award-history rows have no identifiers at all despite 3 real
  CORDIS identifiers being logged and unused (section 7). NOT DONE for these rows.
- Our own papers copied verbatim from brief section 2: not applicable, the report never describes our
  own papers.
- Author/year/volume/pages pasted from CrossRef: not applicable, 0 DOIs.
- Page log format and "no quote without a matching log line": **breached** repeatedly (section 6: 6 of
  14 quoted strings not on any logged page; section 4 row 7: SNF status asserted with zero log line).
- "A CrossRef lookup proves a paper exists, not what it says": not applicable, 0 CrossRef paper lookups
  used in the report text.
- "A page counts as opened only if 200 and excerpt in log": literally satisfied for the PNG and JS-shell
  pages (both are 200 with a logged excerpt), but the excerpts are not text, so the report's own
  "Read: full text" labels for those two rows are not supported by the logged content (section 3).
- Section G negative controls must name only fetched items: satisfied on its face (both lists only name
  fetched URLs), but see below.
- Every NOT FOUND/no-study/remains-open lists its queries: only one such claim exists in the whole
  report (Q2's "zero individuals were searched for or named," line 87), and it is consistent with the
  log (no individual-name search queries appear in `RT09_pages.log`, aside from a name-search style
  block from an earlier `t09`/PPFP fellows-directory scrape at 11:52:54-11:53:20 that predates this
  prompt's own scope and is not about "searching for individuals connected to fellowship applications"
  in the forbidden sense - it targets the PPFP fellows directory, a different search). LISTED AND
  LOGGED.
- Do not grade your own work ("verified", "confirmed", etc.): **breached**, lines 79 and 92 (section
  13).
- No em/en dashes: DONE, 0 in report and 0 in log.
- Item 1, every quote/deadline from a 200 page: **breached** for 6 of 14 quoted strings (section 6) and
  for 3 of the "key numbers" (Oct 16, Oct 2, Oct 5, Sept 9 - section 9).
- Item 2, identifier per funded project: **NOT DONE** - Section E part 1 carries zero funded-project
  identifiers (section 7).
- Item 3, table shape: **DONE** - exactly 11 rows (A1-A10, A14), labels match brief section 4 verbatim
  (minus trailing periods), columns in the prompt's order (section 15/16 below has the full check).
  Item 3, "one item-1 criterion... quoted" per cell: **NOT DONE** for most cells - only 9 of 55 cells
  carry a quote-marked phrase at all (section 6 lists them), and of those, several quote the master
  brief's description of our own drafted proposals rather than an item-1 programme criterion
  (A2/Berkeley, A7/Digital Futures, A7/Schmidt, A9/Berkeley, A9/NSERC - section 6).
- Item 5, map calls for angles scored strong at >=2 programmes: **NOT DONE**. Angles scoring "strong"
  at 2 or more of the 5 programmes in the Section D table are A1 (2: Digital Futures, Schmidt), A2 (3:
  Berkeley, MSCA, NSERC), A7 (3: Digital Futures, NSERC, Schmidt), A9 (2: Berkeley, NSERC), A14 (2:
  Digital Futures, MSCA) - 5 angles. Section F instead repeats the same 5 core programmes from Section
  B (UC PPFP, Digital Futures, NSERC, MSCA, plus SNF) with no angle column and no connection to A1,
  A2, A7, A9 or A14 anywhere in the table or its surrounding text.

## 11. Negative claims

Only one qualifying statement in the whole report: Section G Q2, line 87, "zero individuals were
searched for or named," which is consistent with the log. LISTED AND LOGGED: 1. LISTED NOT LOGGED: 0.
NONE: 0.

## 12. Our own work

No row in the report describes the author's own papers, engine or brief-section-2 assets. Not
applicable.

## 13. Rule breaches

- Em dashes (U+2014): 0 in report, 0 in log.
- En dashes (U+2013): 0 in report, 0 in log.
- Named individuals connected to fellowship programmes in the report text: no (checked with a name-
  pattern grep and manual read of Sections A, B, D, E, F, G, H; the only individual-shaped data
  anywhere in this job's trail is inside `GS\t09`'s upstream log lines 28-61 and the
  `web-cdn.ucop.edu/ppfp-search/_data/data.json` fetch at line 62, none of which is quoted, named or
  used in the report).
- Proposal to change the 4J pre-registered gate, null or threshold: no line found.
- Self-grades the tool applies to its own report or rows: 2 found.
  - Line 79: "official UC Office of the President documentation (...) **confirms** that all Chancellor's
    and Climate Futures fellowships are processed via the unified PPFP application system with an
    immutable November 1 deadline." The word "immutable" and "unified... system" are the report's own
    framing; the cited page never uses either word (checked against `ppfp_info` and the how-to-apply
    pages' full text).
  - Line 92: "No. All deadlines (...) were **verified** against official agency notices." Contradicted
    by section 9: 3 of the 5 stated deadlines (Oct 16, Oct 2, Oct 5, Sept 9 - 4 of 5 non-Berkeley/NSERC
    deadlines) have no matching text on any logged 200 page.

## 14. Scripts

Read `GS\research_fetcher.py`, `GS\t09\run_t09_research.py`, `GS\t09\find_df_links.py`.

(i) Files written inside `C:\Users\o_iseri\Desktop\GSSCanada\` other than `RT09_pages.log`: none. Both
scripts use `LOG_PATH = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\DeepResearch\RT09_pages.log"`
and append-only via `research_fetcher.log_page` (`research_fetcher.py:11-20`, opens with mode `"a"`).
`run_t09_research.py` writes `t09_fetched_summary.json` to its own current working directory
(`t09_fetched_summary.json`, line 59-60 of that script, no path prefix), which lands in `GS\t09\`, not
inside the GSSCanada tree, consistent with the file actually found there.

(ii) Does any script write report text (Markdown, table rows, sections)? No. Neither script contains a
Markdown-formatting string, a table-row template, or any string resembling report prose; both only call
`research_fetcher.fetch_url` / `crossref_lookup` and print short status lines to stdout.

(iii) The logger writes the excerpt from the returned HTTP body itself, not a summary or constructed
string: `research_fetcher.py:27-30`:
```
body = response.read().decode("utf-8", errors="replace")
excerpt = body[:250]
if log_path:
    log_page(log_path, url, status, excerpt)
```
and `log_page` (lines 11-20) truncates that to 200 characters, collapses whitespace, and replaces em/en
dashes. This is confirmed by the fact that the research-matrix line (log line 80) contains raw PNG
bytes: the logger faithfully wrote whatever bytes the server actually returned, including a non-text
response.

(iv) Network calls in the scripts that bypass the logger: none found. `research_fetcher.fetch_url`
always takes `log_path` and logs every call including `crossref_lookup` (`research_fetcher.py:48`,
passes `log_path=log_path` into `fetch_url`) and `openalex_search` (line 93, same). Both scripts in
`GS\t09\` only call `research_fetcher.fetch_url(..., log_path=LOG_PATH)`. Note (section 8): 8 log
lines (89-96) are not individually explained by either saved script's fixed code path, meaning some
fetching in this job happened through code not preserved as a file in `GS\t09\`; those calls still went
through the logger (they are all in the log), so this is a completeness gap in the saved scratch
scripts, not a logger bypass.

(v) `t09_fetched_summary.json` holds short (<=250-character) raw HTML head fragments for 10 URLs (the
`run_t09_research.py` fetch list). None of this fragment text (titles, meta tags, boilerplate HTML)
appears verbatim as report prose; the report's Section A/B/D/E/F/G text is original prose and table
cells, not copies of these JSON fragments. No sign of generated report text stored in the JSON scratch
file.

## 15. The five most serious defects found

1. The report's headline UC PPFP quote ("established in 1984 to encourage outstanding women and
   minority Ph.D. recipients...", line 13) is not present on the page it is cited to, or on any of the
   7 other logged-200 UC PPFP pages checked (section 6).
2. Section F lists the SNF Swiss Postdoctoral Fellowships URL as "yes (HTTP 200)" and Section H marks
   it Tier 1, "Read: summary," but `RT09_pages.log` contains zero lines for `snf.ch` anywhere, and the
   URL now returns 404 (sections 4, 6).
3. The Digital Futures "Research Matrix" URL (cited as "Read: full text" in Section H) and the EU
   Funding & Tenders "topic-details" URL (also "Read: full text") both returned HTTP 200 with a logged
   excerpt, but the first is a PNG image and the second is a 289-character JavaScript shell with no
   call content; neither can have supplied any of the text attributed to them (sections 3, 4, 5).
4. Several Section D table cells' "quoted item-1 criterion" (A2/Berkeley, A7/Digital Futures,
   A7/Schmidt, A9/Berkeley, A9/NSERC) quote the master brief's own description of the researcher's
   drafted proposals, not text from any programme's page, while Section G Q3 answers "No" to "did any
   cell receive a score because the brief said the programme wants it?" (section 6, line 90).
5. Item 5 (map calls for angles scoring "strong" at >=2 programmes: A1, A2, A7, A9, A14) is not done;
   Section F repeats the same 5 core programmes from Section B, unconnected to any angle (section 10).

## 16. What checks out (facts the manager could keep, each with its source)

- Berkeley PPFP deadline Nov 1, 2026: confirmed verbatim on `ppfp.ucop.edu/info/how-to-apply/evaluation-and-selection.html` ("Application Deadline November 1, 2026").
- NSERC deadline Oct 17, 2026: confirmed on `nserc-crsng.gc.ca/.../pdf-bp_eng.asp` ("NSERC: October 17").
- NSERC distinctness-from-thesis rule: confirmed verbatim in substance on the same NSERC page ("Your
  proposed research must be significantly distinct from your doctoral thesis or contribute significantly
  beyond your doctoral thesis").
- MSCA mobility rule (>12 months in prior 36 months): confirmed in substance on
  `marie-sklodowska-curie-actions.ec.europa.eu/actions/postdoctoral-fellowships`.
- Both COULD NOT OPEN rows (Berkeley vcresearch page, Toronto datasciences.utoronto.ca page) are
  correctly marked: both return HTTP 403 live and in the log.
- Digital Futures's three research-matrix societal-context labels (Digitalized Industry, Rich and
  Healthy Life, Smart Society) and three theme labels (Cooperate, Learn, Trust) are genuinely present
  on `digitalfutures.kth.se/mobility/postdoc-fellowship/`, confirming the substance (not the exact
  wording) of several Section D "Digital Futures" cell quotes.
- The UC PPFP how-to-apply index page genuinely lists "UC Berkeley Chancellor's Climate Futures
  Fellowship Program" as a campus-specific programme under the PPFP umbrella, supporting the Section A
  routing claim that the Berkeley fellowship is administered through PPFP.
- Item 3 table shape (row count, row labels, column order) matches the prompt's corrections-block
  table exactly: 11 rows, `A1` through `A10` plus `A14`, labels copied verbatim (minus trailing
  periods) from brief section 4, in the column order ID / Angle / Berkeley Climate Futures / Digital
  Futures / MSCA PF / NSERC PDF / Schmidt AI in Science / Fit across all five.
- No em dashes, no en dashes, and no named individuals appear anywhere in the report or the log.
- No script wrote anything inside the GSSCanada project tree other than the append-only pages log, and
  no script contains report-writing code.
