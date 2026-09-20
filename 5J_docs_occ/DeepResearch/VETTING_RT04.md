# Vetting RT04: occupant_behaviour_frontier (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). Round 2 does not stand.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: the round-1 defect class recurs on a DOI the tool itself fetched.** The Annex 79
   book `10.1201/9781003176985` is given, three times and labelled "CrossRef title", as "Occupant-
   Centric Building Design and Operation" edited with a different second author and publisher; the
   tool's own log line 28 returned the true record, "Occupant-Centric Simulation-Aided Building
   Design", Routledge, with a different co-author (section 1).
2. **Rows with no fetch behind them.**
   - The ASHRAE Global Occupant Behavior Database DOI has zero log lines, a wrong lead author, and
     its "36 field studies, 15 countries" figure is unconfirmed (sections 1, 9).
   - All seven Section F dataset rows claim "reachable, HTTP 200" with none of their URLs in the log;
     no `COULD NOT OPEN` row, as the prompt required (section 10).
   - The successor annex is named "Annex 87" with a scope text found nowhere; the log shows only
     Annex 95, "Human-centric Building Design" (section 9).
   - Eight of twelve landscape rows describe content with no logged abstract (section 2).
3. **Other defects.** Building Data Genome 2 given as 3,053 buildings; its abstract says 3,053
   meters in 1,636 buildings (section 9). Item 1.1 quotes no Annex 79 deliverable although the pages
   were opened ten times. Negative claims cite wrong log lines and one query never ran (section 11).
   Six named leads dropped, and two on-topic works the tool found were dropped without a note.
4. **Kept.**
   - Identity: eleven identifiers match CrossRef exactly, among them Dai et al. 2026 (a multi-agent
     language-model occupant simulation), Doma et al. 2024, Jung et al. 2023, Schumann et al. 2023,
     Aragon et al. 2019, the reviews Vogl et al. 2026 and Bataynah et al. 2026, Duhirwe et al. 2024,
     Miller et al. 2020 (section 16). Unread pointers except as below.
   - Aragon et al. full text and the generative-agents paper (25 agents) abstract were fetched and
     re-found (sections 2, 9).
   - Annex 79 has four subtasks (logged and re-fetched); Annex 95 "Human-centric Building Design" is
     the successor-type annex the log actually shows (a pointer).
   - The corrected Annex 79 book record and the ASHRAE database first author (Liu et al., 2023) as
     CrossRef gives them.
   - Our CENTUS row: the DOI and CrossRef title are right; the row is paraphrased from brief section 2,
     not copied, and adds no fact (section 12).
   - For heat-responsive presence at population scale, three logged queries found nothing (log lines
     106 to 108). Evidence that three queries found nothing, not proof.
5. **Do not re-run T04 in Gemini as it stands.**

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 14 (MATCH 11, author mismatch 2, other mismatch 1, not resolved 0; rows
without CrossRef title 0, but 2 rows carry a pasted "CrossRef title" that does not match CrossRef);
use claims 12 (supported 2, not in abstract 0, contradicted 1, no abstract 9; TITLE ONLY breaches 8);
Section G read-list items 12 (in log 200 for content 3, in log not 200 for content 3, not in log for
content 6); URLs in report 16 distinct (in log 0, not in log 16; fetched 16, content confirmed for 1
directly contradicts the report, rest paywalled landing pages not independently readable); log excerpts
re-checked 10 (found 8, not found 0, unreachable 2); quoted strings 13 (found 11, not found 1, no log
line 1); unlogged-source claims 5 report locations; log lines after report write 0; key numbers 9
(confirmed 2, contradicted 2, not confirmed 5); prompt items: 4 "For this prompt" bullets checked, 1
done, 3 not done or violated; negative claims 2 (listed and logged 0, listed not logged 0 but both cite
WRONG line numbers, none 0); self-grades 0 clear violations (3 borderline non-self-referential uses of
"verified/confirmed"); dashes em 0, en 0 (report and log); scripts writing inside the project 0 (beyond
the one permitted log file).

## 1. Identifiers

All 13 DOIs that appear as table/reference rows, plus one inline-only identifier (SSRN 6819943), were
re-resolved live against `https://api.crossref.org/works/<DOI>` on 2026-09-19.

| DOI | HTTP now | CrossRef title (live) | Report's title/authors | Verdict |
|---|---|---|---|---|
| 10.1016/j.buildenv.2026.115121 | 200 | Predicting public building energy consumption in the early design stage using a multi-agent LLM for occupant behavior simulation | Same title; authors Rui Dai, Guoqiang Zhang, Linhu Wang, Liuchang Yang, Ge Bai match exactly; vol 304, page 115121, 2026 match | MATCH |
| 10.1145/3586183.3606763 | 200 | Generative Agents: Interactive Simulacra of Human Behavior | Title matches. Report authors: "Joseph C. O'Brien", "Carrie J. Cai". CrossRef authors: "Joseph O'Brien" (no middle initial), "Carrie Jun Cai" (Jun spelled out, not abbreviated) | AUTHOR MISMATCH (minor, invented middle initial / wrong abbreviation) |
| 10.1016/j.buildenv.2024.111713 | 200 | Developing a residential occupancy schedule generator based on smart thermostat data | Matches exactly (Aya Doma, Shruti Naginkumar Prajapati, Mohamed M. Ouf; vol 261, page 111713, 2024) | MATCH |
| 10.1016/j.buildenv.2023.110628 | 200 | Smart thermostat data-driven U.S. residential occupancy schedules... | Matches exactly (Jung, Wang, Hong, Jazizadeh; vol 243, page 110628, 2023) | MATCH |
| 10.26868/25222708.2023.1209 | 200 | A multi-sourced data and agent-based approach for complementing Time Use Surveys... | Matches (6 authors match; vol 18, 2023) | MATCH |
| 10.1080/09613218.2017.1399719 | 200 | Developing English domestic occupancy profiles | Matches exactly (5 authors; vol 47, pages 375-393, 2019) | MATCH |
| 10.1016/j.enbuild.2026.117522 | 200 | A review of challenges and opportunities in occupant modeling for future residential energy demand | Matches exactly (Vogl, Kleinebrahm, Raab, McKenna, Fichtner; vol 364, page 117522, 2026) | MATCH |
| 10.1016/j.enbuild.2026.116977 | 200 | Human-centered energy modeling: integrating occupant behavior in simulation workflows | Matches exactly (Bataynah, Alnusair, Heydarian, Asadi; vol 354, page 116977, 2026) | MATCH |
| 10.1016/j.rser.2024.114854 | 200 | Causal effects of policy and occupant behavior on cooling energy | Matches exactly (Duhirwe, Ngarambe, Yun; vol 206, page 114854, 2024) | MATCH |
| 10.1016/j.enbuild.2026.117155 | 200 | Occupancy modeling using population statistics and machine learning for urban residential built environment | Matches (this is our own CENTUS paper; report copies the same CrossRef title the round-1 vetting note said was invented last time; authors given as short surnames per brief) | MATCH |
| 10.1080/23744731.2023.2235971 | 200 | ASHRAE URP-1883: Development and Analysis of the ASHRAE Global Occupant Behavior Database | Title matches. Report calls this "Bing Dong et al." (first-author framing) in Section B row 6, Section C row 11, Section G, and Section H item 11. Live CrossRef author order is **Yapan Liu, Bing Dong, Tianzhen Hong, Bjarne Olesen, Thomas Lawrence, Zheng O'Neill** — Dong is the SECOND author, not the first. Volume 29, issue 8, pages 749-781 never given anywhere in the report | AUTHOR MISMATCH (wrong lead author) — see also Section 7/11, this DOI has zero log lines |
| 10.1038/s41597-020-00712-x | 200 | The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition | Title/authors match (Miller et al., vol 7, article 368, 2020) | MATCH |
| 10.1201/9781003176985 | 200 | **Occupant-Centric Simulation-Aided Building Design: Theory, Application, and Case Studies**, by William O'Brien and Farhang Tahmasebi, Routledge, 2023 | Report (Section B row 7, Section F, Section H item 13) claims: title **"Occupant-Centric Building Design and Operation"**, editors **"William O'Brien, Andreas Wagner"**, publisher **"CRC Press"**, and explicitly labels this the "CrossRef title:". None of title, second author, or publisher match. This exact DOI was fetched live by the tool itself at log line 28 (status 200) | **TITLE MISMATCH + AUTHOR MISMATCH** — the same failure class round 1 was failed for, on a new DOI |
| 10.2139/ssrn.6819943 (inline only, Section G) | 200 | Predicting Public Building Energy Consumption in the Early Design Stage Using a Multi-Agent LLM for Occupant Behavior Simulation | Report cites as the SSRN preprint of the Dai et al. paper; title matches | MATCH (not a table row, no CrossRef title required beside it) |

Two DOIs for one work: the Dai et al. paper is cited under two different DOIs (published `10.1016/j.buildenv.2026.115121` and preprint `10.2139/ssrn.6819943`), both treated as "the same work opened" in Section G's negative-control list.

CrossRef title pasted beside every DOI in table rows: yes, all 12 Section C rows and all 13 Section H
entries carry a parenthetical/quoted title. Two of those pasted titles (rows 11 and 13 above) do not
match what CrossRef actually returns.

## 2. Use claims and TITLE ONLY rule

For each Section C "What it did" row, whether a log line exists for the paper's abstract or full text
(not just a bare CrossRef metadata call):

| Work | Log evidence beyond CrossRef metadata | Verdict |
|---|---|---|
| Dai et al. (115121/6819943) | None. Only `works/<DOI>` (200, no abstract field for 115121) and Unpaywall (200, metadata only) | TITLE ONLY breach |
| Park et al. (3606763) | `arxiv.org/abs/2304.03442` fetched 3x, status 200 — genuine abstract-page content. Live re-check: abstract text includes "a small town of twenty five agents", matching the report's "25 generative agents" | SUPPORTED (abstract-level; report's "Read: full text" label is inflated — only the arXiv abstract page was ever fetched, never a PDF) |
| Doma et al. (111713) | None beyond metadata (no abstract field); `doi.org` redirect returned 403 | TITLE ONLY breach |
| Jung et al. (110628) | None; `sciencedirect.com` fetch and `doi.org` redirect both 403 | TITLE ONLY breach |
| Schumann et al. (1209) | None; `publications.ibpsa.org/.../bs2023_1209.pdf` returned 403 | TITLE ONLY breach |
| Aragon et al. (1399719) | `eprints.soton.ac.uk/416376/1/Occ_patterns_pure.pdf` fetched, 200, real PDF bytes | SUPPORTED (genuine full text) |
| Vogl et al. (117522) | None; single `works/<DOI>` call, no abstract field | TITLE ONLY breach |
| Bataynah et al. (116977) | None; single `works/<DOI>` call, no abstract field | TITLE ONLY breach |
| Duhirwe et al. (114854) | None; single `works/<DOI>` call (the very last log line), no abstract field | TITLE ONLY breach |
| CENTUS/OURS (117155) | None; `doi.org` redirect 403. (Content is brief-sourced, not independently described, so not counted as a hard breach) | no abstract grounding, not counted in breach total |
| Dong et al./ASHRAE DB (2235971) | **Zero log lines of any kind for this DOI or for "Dong"/"ASHRAE Global Occupant Behavior Database" succeeding** (only a 429-failed OpenAlex search and 429-failed CrossRef free-text searches near this topic) | TITLE ONLY breach, most severe — no evidence this DOI was ever resolved in-session |
| Miller et al. (00712-x) | `works/<DOI>` call, 200, **CrossRef record includes a full JATS abstract** (confirmed by live re-fetch) | Grounded, but CONTRADICTED — see Section 9 |

8 TITLE ONLY breaches (Dai, Doma, Jung, Schumann, Vogl, Bataynah, Duhirwe, Dong), against the prompt's
explicit rule that a bare CrossRef lookup "proves a paper exists, not what it says."

## 3. Section G read-lists (negative control)

Section G item 1 lists "Opened in full" (5 works) and "Abstract / summary only" (7 works).

| Listed as | Work | Log status for that content claim |
|---|---|---|
| full | Dai (SSRN 6819943 / BE 115121) | NOT IN LOG (only metadata calls) |
| full | Park (3606763) | IN LOG 200 (but it is the arXiv abstract page, not full text) |
| full | Jung (110628) | IN LOG NOT 200 (403 on the only content fetch attempted) |
| full | Aragon (1399719) | IN LOG 200 (genuine PDF) |
| full | CENTUS/OURS (117155) | IN LOG NOT 200 (403 on the only content fetch attempted) |
| abstract | Doma (111713) | NOT IN LOG (no abstract field, 403 on landing page) |
| abstract | Schumann (1209) | IN LOG NOT 200 (403 on the only PDF fetch attempted) |
| abstract | Vogl (117522) | NOT IN LOG (metadata call only) |
| abstract | Bataynah (116977) | NOT IN LOG (metadata call only) |
| abstract | Duhirwe (114854) | NOT IN LOG (metadata call only) |
| abstract | Dong/ASHRAE (2235971) | NOT IN LOG (zero log lines) |
| abstract | Miller (00712-x) | IN LOG 200 (abstract present in the same crossref call) |

Of 12 read-list entries: 3 IN LOG 200 (genuine content), 3 IN LOG NOT 200 (log line exists, fetch
failed), 6 NOT IN LOG (no content-level evidence at all).

## 4. URLs

16 distinct URLs appear in the report body (13 `doi.org/<DOI>` links matching Section 1's DOIs, plus 3
dataset URLs: `beta.ukdataservice.ac.uk`, `www.atusdata.org`, `www.timeuse.org/mtus`; `ecobee.com` is a
4th external URL, for 4 non-DOI URLs total). None of these 16 exact URLs (the `doi.org/...` redirect
form, or the 4 dataset landing pages) appear anywhere in `RT04_pages.log`. The log only contains
`api.crossref.org`, `api.unpaywall.org`, and a handful of directly-fetched non-DOI pages (Annex79/95,
ASHRAE, IBPSA, arXiv abstract, two PDFs) — none of which are the URLs printed in the report's own
Section F/H tables.

All 16 were fetched live (2026-09-19):

| URL | HTTP now | Note |
|---|---|---|
| doi.org/10.1016/j.buildenv.2023.110628 | 200 -> linkinghub.elsevier.com | paywalled landing, content not independently read |
| doi.org/10.1016/j.buildenv.2024.111713 | 200 -> linkinghub.elsevier.com | same |
| doi.org/10.1016/j.buildenv.2026.115121 | 200 -> linkinghub.elsevier.com | same |
| doi.org/10.1016/j.enbuild.2026.116977 | 200 -> linkinghub.elsevier.com | same |
| doi.org/10.1016/j.enbuild.2026.117522 | 200 -> linkinghub.elsevier.com | same |
| doi.org/10.1016/j.rser.2024.114854 | 200 -> linkinghub.elsevier.com | same |
| doi.org/10.1038/s41597-020-00712-x | 200 -> nature.com | same |
| doi.org/10.1080/09613218.2017.1399719 | 403 | now blocked (was reachable via eprints mirror in log) |
| doi.org/10.1080/23744731.2023.2235971 | 403 | now blocked |
| doi.org/10.1145/3586183.3606763 | 403 | now blocked (ACM paywall) |
| doi.org/10.1201/9781003176985 | 200 -> taylorfrancis.com/books/oa-edit/.../**occupant-centric-simulation-aided-**... | **the redirect slug itself confirms the true title, contradicting the report's Section B/F/H title** |
| doi.org/10.26868/25222708.2023.1209 | 403 | now blocked |
| www.atusdata.org/atus/ | 200 | reachable, content not independently confirmed against report's claims |
| www.ecobee.com/en-ca/donate-your-data/ | 200 | reachable, content not independently confirmed |
| www.timeuse.org/mtus | 200 | reachable, content not independently confirmed |
| beta.ukdataservice.ac.uk/.../study?id=8128 | 200 -> datacatalogue.ukdataservice.ac.uk/studies/study/8128 | reachable |

Section F's "Confirmed reachable?" column says "yes (HTTP 200)" for all 7 rows; none of those 7 exact
URLs have a log line, so all 7 "yes (HTTP 200)" entries rest on no logged fetch of that specific URL
(the ASHRAE row is the extreme case: zero log lines anywhere for that DOI, discussed in Sections 1, 3,
7, 11).

## 5. Log excerpt re-check

10 lines re-fetched live (first, last-ish, spread across the log, plus the two PDF fetches):

| Line | URL | Then | Now | Verdict |
|---|---|---|---|---|
| 1 | crossref works/117155 | 200 | 200 | FOUND |
| 15 | annex79.iea-ebc.org/publications | 200 | 200 | FOUND (after whitespace normalisation) |
| 28 | crossref works/9781003176985 | 200 | 200 | FOUND (the response body matches; report's title claim does not) |
| 56 | ibpsa.org/projects/ | 200 | 200 | FOUND (after whitespace normalisation) |
| 84 | arxiv.org/abs/2304.03442 | 200 | 200 | FOUND |
| 92 | publications.ibpsa.org/.../simbuild2026_1329.pdf | 200 | 403 | UNREACHABLE (page access changed since fetch) |
| 98 | crossref works?query=occupant modelling... | 200 | 200 | FOUND |
| 145 | eprints.soton.ac.uk/416376/1/Occ_patterns_pure.pdf | 200 | 401 | UNREACHABLE (page access changed since fetch) |
| 164 | crossref works/115121 | 200 | 200 | FOUND |
| 168 | crossref works/114854 | 200 | 200 | FOUND |

8 FOUND, 0 NOT FOUND, 2 UNREACHABLE (access changed after the run, not a report defect).

## 6. Quoted strings

All 13 double-quoted strings in the report are "CrossRef title:" quotes in Section H (see full list at
report lines 106-118).

| Quote (DOI) | Log line for that DOI | On the page/record? |
|---|---|---|
| 12 of the 13 (115121, 3606763, 111713, 110628, 1209, 1399719, 117522, 116977, 114854, 117155, 00712-x) | Yes | FOUND (matches CrossRef) |
| 2235971 (Dong/ASHRAE) | **None** | NO LOG LINE (title happens to match a live re-check, but nothing in the log supports it) |
| 9781003176985 (book) | Line 28 | **NOT FOUND** — the log line exists and returned 200, but the actual CrossRef body for that call is the Tahmasebi/O'Brien book, not "Occupant-Centric Building Design and Operation" |

Found 11, not found 1, no log line 1.

## 7. Unlogged sources

Per the run-transcript facts given for this task, several searches were made directly (printed to
screen, not written to `RT04_pages.log`) just before the report was written: an OpenAlex search for
"ASHRAE Global Occupant Behavior Database"; CrossRef free-text queries for that same phrase, for an
occupant-centric building design book, and for "review occupant behavior building energy modeling"
filtered from 2024 (plain, and filtered to Energy and Buildings / Building and Environment / RSER).
Independent grep of the log corroborates the gap: `RT04_pages.log` contains **zero lines** for "Dong",
"23744731", or "2235971" in any form, even though the report cites this DOI four times (Section B row
6, Section C row 11, Section F row 1, Section H item 11) and Section F asserts it is "Confirmed
reachable? yes (HTTP 200)". The only logged attempt near this topic is an OpenAlex search for
"ASHRAE Global Occupant Behavior Database" that returned 429 (line 155) and a set of CrossRef free-text
queries for "review occupant behavior... 2024/2025/2026" filtered by container title (lines 59-64 and
97-108) whose 200-char excerpts never show item DOIs. Report rows resting on this gap:

1. Section B row 6 (ASHRAE Global Occupant Behavior Database fact row)
2. Section C row 11 (Dong et al. landscape row)
3. Section F row 1 (ASHRAE DB artefact, "yes (HTTP 200)")
4. Section H item 11 (Dong et al. reference entry)
5. Section B row 8 partially: "IEA EBC Annex 87 (Energy and Indoor Environmental Quality Destination)"
   — the log shows extensive fetching of **Annex 95** ("Human-centric Building Design", lines 32-38),
   never "Annex 87" or that scope name in any form; "Annex 87" does not appear anywhere in the log.

## 8. Timing

Log first line: 2026-09-19T11:48:50. Log last line: 2026-09-19T14:35:05. 168 lines total. Maximum
lines in any 60-second window: 66, between 14:33:05 and 14:33:49 (the confirmatory CrossRef-metadata
flurry immediately before the report was written). There is a roughly 2.5-hour gap between line 95
(11:56:36) and line 96 (14:33:05). Report file write time given: 2026-09-19 14:35:32. Log lines after
that time: 0.

## 9. Key numbers

| # | Number | Claimed by | Source check | Verdict |
|---|---|---|---|---|
| 1 | "36 field studies... 15 countries and 10 building types" (ASHRAE URP-1883) | Section B row 6 | No log line for this DOI at all (Section 7) | NOT CONFIRMED |
| 2 | "3,053 buildings, 19 sites" (BDG2) | Section C row 12, Section H item 12 | Live CrossRef abstract for 10.1038/s41597-020-00712-x: "3,053 energy meters from **1,636 non-residential buildings**... from **19 sites**" | **CONTRADICTED** (3,053 is the meter count, not the building count; true building count is 1,636) |
| 3 | "25 generative agents in Smallville" | Section C row 2 | arXiv abstract page (logged, 200) reads "a small town of twenty five agents"; the town's proper name is not in the fetched abstract text | 25 CONFIRMED; "Smallville" not confirmed from logged text |
| 4 | "3% agreement with Canadian TUS in daily occupied hours" | Section B row 9 | No abstract/full-text log line for 111713 (only metadata + 403) | NOT CONFIRMED |
| 5 | "Over 8,000 Canadian homes" (Doma) | Section C row 3 | Same as above | NOT CONFIRMED |
| 6 | "91,747 US thermostats" (Jung) | Section C row 4 | Only 403s in log for this DOI's content | NOT CONFIRMED |
| 7 | Annex 79 "4 subtasks" | Section B row 7 | Live re-fetch of `annex79.iea-ebc.org/subtasks` (also logged 200 at lines 11, 13, etc.) lists Subtask 1-4 | CONFIRMED |
| 8 | "IEA EBC Annex 87" as the successor annex | Section B row 8 | Log shows only Annex 95 fetched, titled "Human-centric Building Design" | **CONTRADICTED** |
| 9 | Annex 87 scope "Energy and Indoor Environmental Quality Destination" | Section B row 8 | Not present anywhere in the log (Annex 95's logged title is different) | **CONTRADICTED** |

2 confirmed, 2 contradicted, 5 not confirmed.

## 10. Prompt items

Item-by-item (numbered items in the prompt body):

| Item | Status |
|---|---|
| 1.1 Annex 79 deliverables + open problems, quoted | **NOT DONE** — the tool fetched `annex79.iea-ebc.org/publications` and `/subtasks` repeatedly (10+ times, lines 2-22) but the report never quotes a single deliverable or open problem from those pages; Section A/B only assert generic closure |
| 1.2 successor annex/ASHRAE/IBPSA group | DONE with a defect — Annex 95 was genuinely researched (logged) but reported under the wrong number ("87") and wrong scope text (Section 7, 9) |
| 1.3 three most-cited reviews, read in full | NOT DONE — the report marks its review-type citations (Vogl, Bataynah) "abstract" not "full text", and no log line grounds even the abstract (Section 2) |
| 2. Generative/LLM occupant works mapped | Partly done — Dai and Park are mapped, but two on-topic works the tool itself found and one of which it fully downloaded were dropped without explanation (see Section 14v) |
| 3.1 groups other than us publishing time-use occupancy 2024-2026 | DONE (Doma, Jung, Schumann, Aragon listed), though grounding is thin (Section 2) |
| 3.2 cross-national time-use model other than ours | DONE, NOT FOUND with queries, but cited under the wrong log line numbers (Section 11) |
| 3.3 what reviewers say time-use lacks | DONE (Section G item 1) |
| 4. Weather/heat-responsive occupancy | DONE, NOT FOUND with queries, but cited under the wrong log line numbers (Section 11) |
| 5. Datasets | DONE as a table, but see "For this prompt" bullet (c) below — none actually satisfies the admission rule |
| 6. Five missing capabilities, mapped to assets | DONE (Section D) |
| Named lead: Annex 66 | DROPPED — zero mentions in log or report |
| Named lead: HUE dataset | DROPPED — zero mentions in log or report |
| Named lead: arXiv cs.AI/cs.MA/cs.CY | DROPPED — no category-scoped arXiv search in log; only one direct arXiv abstract page fetched |
| Named lead: Centre for Time Use Research | DROPPED by name — only its `timeuse.org/mtus` page is used |
| Named lead: Eurostat HETUS pages | DROPPED — zero mentions in log or report |
| Named lead: BuildSys, e-Energy proceedings | DROPPED — zero mentions in log or report |
| Named lead: IBPSA Building Simulation 2025 | Not specifically addressed; the only BS-venue paper used is 2023 (Schumann) |

"For this prompt" bullets:

(a) CENTUS at most once, verbatim, DOI given — see Section 12.
(b) Annex 79 deliverables/open problems "quoted only from pages you opened" — **violated by omission**:
    nothing is quoted at all, despite the pages being opened repeatedly (see 1.1 above).
(c) Item 5 dataset identifiers admitted only if resolved "with its identifier pasted from the record
    page", else `COULD NOT OPEN` — **violated**: Section F has zero `COULD NOT OPEN` rows, but none of
    the 7 rows' identifiers were pasted from an actually-fetched record/landing page (Section 4); the
    ASHRAE row rests on a DOI with no log line whatsoever.
(d) Item 4, `NOT FOUND` with queries when nothing exists — **followed in spirit**, but the specific log
    line numbers cited for the queries are wrong (Section 11).

## 11. Negative claims

Two `NOT FOUND` claims carry query lists in Section G:

**Population-scale heat-responsive presence** (3 queries, cited as "RT04_pages.log line 11/12/13"):
the actual log lines for these exact queries are **106, 107, 108**, not 11, 12, 13. Lines 11-13 of the
log are Annex79 subtask-page fetches, unrelated to heat or weather. LISTED, but cited at the WRONG line
numbers; the real log lines do exist and do return 200.

**Cross-national transfer** (2 queries, both cited as "RT04_pages.log line 9"): Query 1
("cross-national transfer time use occupancy energy modelling") is actually at log line **104**, not 9.
Query 2 ("time use synthetic population transferability cross-national") **does not appear anywhere in
the log** under any line number — grep for "synthetic" and "transferability" across the whole log
returns nothing. Line 9 of the log is an unrelated 404 (`annex79.iea-ebc.org/subtask-4`).

Both negative claims: LISTED, but with wrong or (for one query) nonexistent line citations. Neither
qualifies cleanly as "LISTED AND LOGGED" as cited, though the underlying queries mostly did happen
(Query 2 of the cross-national pair is the exception — that one never happened at all).

## 12. Our own work

CENTUS/OURS (`10.1016/j.enbuild.2026.117155`) appearances, quoted:

1. Section C row 10 (landscape table row): "OURS (Iseri, Gursel Dino, Kalkan, Energy and Buildings 357
   (2026) 117155) | 10.1016/j.enbuild.2026.117155 (Occupancy modeling using population statistics and
   machine learning for urban residential built environment) | Multitask deep model (LSTM and
   Transformer) predicting activity, presence, and co-presence from demographic vectors | ISTAT 2011
   census, 2013-14 Italian TUS | Urban residential | Single-country training; claims HETUS
   harmonisation as route to cross-national transfer | full"
2. Section D row 3 (asset-mapping table): "CENTUS co-presence prediction head; GSS household rosters"
   (names the engine as one of our assets, not a second citation row).
3. Section G item 1 (negative control list): "CENTUS (OURS, Energy and Buildings 117155)."
4. Section H item 10 (reference list, standard cross-reference): "OURS (Iseri, Gursel Dino, Kalkan,
   Energy and Buildings 357 (2026) 117155). ... CrossRef title: 'Occupancy modeling using population
   statistics and machine learning for urban residential built environment'. Read: full text."

Brief section 2's CENTUS row (for comparison): "CENTUS (Iseri, Gursel Dino, Kalkan, Energy and
Buildings 357 (2026) 117155, 10.1016/j.enbuild.2026.117155) | Italy: ISTAT 2011 census plus 2013-14
Time Use Survey | LSTM and Transformer, multitask, activity (145 classes), presence, co-presence per
hour, conditioned on demographics | Accuracy 0.98 for both deep models against 0.691 for a high-order
Markov chain; claims HETUS harmonisation as the route to cross-national transfer, untested | Published"

Row 1 is a paraphrase into the Landscape table's column schema, not a verbatim copy (wording is
reordered and condensed; e.g. "activity (145 classes)" and the 0.98/0.691 accuracy figures are
dropped). No fact, number, or title beyond what the brief states is added. The DOI appears once as a
full table row (item 1) and once more as a standard Section H reference entry (item 4); items 2 and 3
are short inline mentions, not additional described rows.

## 13. Rule breaches

Em dashes: 0 in report, 0 in log. En dashes: 0 in report, 0 in log.

Named individuals connected to fellowship programmes: none found (report line search for
fellowship/Berkeley/KTH/Marie Sklodowska/NSERC/Schmidt/ETH Zurich returns zero hits).

Proposals to change the 4J pre-registered gate, null, or threshold: none found.

Self-grading of the report's own work: no instance of "definitive", "without exception", or "ACCEPTED".
Three uses of "verified"/"confirmed" are prose, not self-grading of the report itself: line 53 ("no
other group has published a verified cross-national transfer pipeline" — describes the literature, not
this report); line 54 ("zero verified thermodynamic integration" — same); line 55 ("Item 4 confirmed
that..." — describes the outcome of the search, arguably borderline self-referential). None claims the
report itself is verified/confirmed/correct.

## 14. Scripts

`GS\research_fetcher.py` and all `.py` files in `GS\t04\` were read.

(i) File writes outside `GS`: only `run_queries.py` writes to a path under
`GSSCanada-main\5J_docs_occ\DeepResearch\` — and it writes only `RT04_pages.log` (creating it empty if
absent; the one file the spec allows). `fetch_t04_papers.py` and `search_real_papers.py` write
`t04_verified_papers.json` and `t04_openalex_results.json`, both inside `GS\t04\` (scratch, not the
project). No script writes anywhere else inside `C:\Users\o_iseri\Desktop\GSSCanada\`.

(ii) No script writes report text (Markdown, table rows, sections); grep for `.md` writes inside
`GS\t04\*.py` finds none.

(iii) The logger writes the excerpt from the actual returned body, not a summary or constructed
string. `research_fetcher.py` (repo root): `fetch_url()` sets `excerpt = body[:250]` from the real
HTTP response and passes it to `log_page()`, which does `" ".join(excerpt.split())[:200]`
(research_fetcher.py:27-30). `t04_fetcher.py` does the same: `body = body_bytes.decode(...)`,
`excerpt = clean_dashes(body[:250])`, `log_entry(url, status, excerpt)` (t04_fetcher.py:32-35). On
HTTPError/exception both loggers write the literal error string ("HTTPError: <code> <reason>"), also
from the actual response, not fabricated content.

(iv) Network calls bypassing the logger: none found in any saved script — every `fetch_url` variant in
both `research_fetcher.py` and `t04_fetcher.py` writes a log line unconditionally (t04_fetcher.py's
`fetch_url` has no `log_path` parameter at all; it always logs). Every script in `GS\t04\` that makes
network calls (`crossref_top_reviews.py`, `find_reviews.py`, `find_ob_reviews.py`, `inspect_reviews.py`,
`run_queries.py`, `search_real_papers.py`, `fetch_t04_papers.py`) imports one of these two loggers.
This means the run-transcript facts given for this task (an OpenAlex search and several CrossRef
free-text queries made outside the logger) were made through a channel with **no corresponding saved
script** in `GS\t04\` — consistent with the independent finding in Section 7 that DOI
`10.1080/23744731.2023.2235971` (Dong/ASHRAE) has zero log lines despite being cited four times in the
report.

(v) `t04_openalex_results.json` is 2 bytes (`[]`) — an empty list, confirming `search_real_papers.py`'s
OpenAlex calls never returned usable results (all 429s, matching the log). `t04_verified_papers.json`
(8,165 bytes) holds CrossRef records for a candidate DOI list that includes several never used in the
final report (e.g. `10.1080/09613218.2020.1798541`, `10.1016/j.enbuild.2020.110291`,
`10.1016/j.apenergy.2021.117117`, `10.5281/zenodo.3929456`) — these were investigated and dropped, not
signs of generated report text. No JSON file content appears verbatim in the report beyond ordinary
title/author metadata already covered in Section 1.

Additional fact found while reading the scripts: the log at 11:55:45-11:56:14 (lines 87-92) shows the
tool resolving and **fully downloading** two on-topic papers it never cites: "DEVELOPING AI OCCUPANT
AGENTS FOR OCCUPANT BEHAVIOR MODELING IN RESIDENTIAL BUILDINGS" (Vosoughkhosravi & Erfani, SSRN
`10.2139/ssrn.7284912`) and "Evaluating Prompt Engineering in Large Language Models (LLMs) for
Transforming Occupant Behavior Modeling" (Li & Ma, IBPSA SimBuild 2026, `10.26868/30680611.2026.1329`,
full PDF fetched at line 92, 4,433,713 bytes). Neither appears anywhere in
`RT04_occupant_behaviour_frontier.md`.

## 15. The five most serious defects found

1. The DOI for the Annex 79 book was fetched live by the tool itself (log line 28, status 200,
   returning "Occupant-Centric Simulation-Aided Building Design" by O'Brien and Tahmasebi), but the
   report presents a different title ("Occupant-Centric Building Design and Operation"), different
   second author ("Andreas Wagner" instead of "Farhang Tahmasebi"), and different publisher ("CRC
   Press" instead of "Routledge"), explicitly labelled as the "CrossRef title" three times.
2. `10.1080/23744731.2023.2235971` (ASHRAE Global Occupant Behavior Database, cited as "Bing Dong et
   al.") has zero log lines of any kind, is cited in four places in the report, and its first author
   per CrossRef is Yapan Liu, not Dong.
3. All 7 Section F dataset rows mark "Confirmed reachable? yes (HTTP 200)" with none of the exact URLs
   given ever appearing in the log.
4. The report names "IEA EBC Annex 87 (Energy and Indoor Environmental Quality Destination)" as the
   Annex 79 successor; the log shows only Annex 95 ("Human-centric Building Design") was researched,
   and "Annex 87" appears nowhere in the log.
5. Two fully downloaded/resolved on-topic papers (a SimBuild 2026 LLM-prompt-engineering paper, full
   PDF fetched; an SSRN AI-occupant-agents paper) were dropped from the report with no NOT FOUND note
   or explanation, while 8 of 12 landscape-table "What it did" claims rest on no logged abstract or
   full text (TITLE ONLY breaches).

## 16. What checks out

- 11 of 14 identifiers MATCH CrossRef cleanly (title, authors, venue, volume, page all consistent):
  Dai 115121, Doma 111713, Jung 110628, Schumann 1209, Aragon 1399719, Vogl 117522, Bataynah 116977,
  Duhirwe 114854, CENTUS 117155, Miller 00712-x, SSRN 6819943 (Sections 1, source: live CrossRef).
- Aragon et al. (1399719) full text was genuinely fetched (`eprints.soton.ac.uk` PDF, log line 145,
  200) and Park et al. (3606763) abstract content was genuinely fetched (`arxiv.org/abs/2304.03442`,
  logged 200) and its "25 agents" figure is confirmed in that fetched text (Sections 2, 9).
- No em or en dashes anywhere in the report or the log (Section 13).
- No fellowship individuals named, no 4J gate/null/threshold change proposed (Section 13).
- No script writes report text or writes any file inside the project other than the one permitted log
  file; the logger genuinely logs returned-body excerpts, not fabricated summaries (Section 14).
- Annex 79's "4 subtasks" claim (Section B row 7) is confirmed by both the log (lines 11, 13, etc.,
  status 200) and a live re-fetch of `annex79.iea-ebc.org/subtasks` (Section 9).
- The two `NOT FOUND` negative claims (heat-responsive presence, cross-national transfer) are
  substantively followed with real queries mostly present in the log, even though the line numbers
  cited for them are wrong (Section 11).
