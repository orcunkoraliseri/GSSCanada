# Vetting RT12: Contradictions and ranking of the surviving angles

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-19)

RT12 is the first report of this series whose identifiers, quotations and arithmetic all hold: 14 of
14 identifiers match on title, authors, year, volume and pages; 6 of 6 quoted strings are verbatim at
source; 11 of 11 ranked scores recompute exactly; the negative controls list their queries; no number
about our own work is inflated beyond the brief; no individual is named near a fellowship programme;
no change to 4J's gate is proposed. It is therefore not a failed round. Six strikes apply, and two of
them change the ranking the report delivers.

**S1 (content). Hobson and Brideau 2026 (`10.63044/w26hob04`) is struck to TITLE ONLY.** Section A,
row C1 and reference 1 all say "Read abstract [L11]" and assert "under extreme heat" and "BTAP
archetype models and Canadian climate data". CrossRef carries no abstract for this DOI and the
publisher page is bot-blocked, so no logged fetch contains that text (check 2, check 7). The DOI,
title and authors are real and unstruck. **This is the single most consequential strike in the
report**, because the real title is "Exploring Key Performance Indicators for Thermal Resilience in
Canadian Multi-Unit Residential Buildings" - the nearest neighbour of A9 - and its actual scope is
now unknown to us. The claim that it "did not evaluate winter power outages" has no source. Owed
before A9 is committed to: the Hobson and Brideau abstract or full text, from ASHRAE.

**S2 (content). The Baba 2022 sentence is struck wherever it appears** (Q3 row, Section A third
finding, Section G contradictions, Section G mandatory question 1's "opened in full" list). Log line
12 resolves to an unrelated 2022 philosophy MA project, not a Baba thesis of any kind (check 5). We
therefore know nothing about Fuad Baba's thesis from this report. Q3's own NOT FOUND verdict stands,
because the checker independently re-ran all four Q3 queries and found no genuine Canadian
winter-MURB-outage study in their hits (check 11) - but it stands on the searches alone, never on
Baba.

**S3 (scoring). A4 and A6 are re-scored from G = 40 to G = 20, as T12's own definition requires**
(check 16b). Their openness rests only on negative searches with no logged abstract of any nearest
work. Corrected scores: A4 24.0 -> 16.0, A6 24.5 -> 16.5. The corrected order is A9 27.0, A12 27.0,
A2 24.5, A7 24.5, A11 19.0, A3 17.0, A6 16.5, A8 16.5, A4 16.0, A13 16.0, A14 16.0. Section A's
"immediate second tier" of A2, A6 and A7 is struck; the second tier is A2 and A7.

**S4 (scoring, manager-found, not in the mechanical check). A12's G = 40 is struck as untested.**
Its only tag is `[P27]`, a fact we pasted in ourselves; no Part A question asked whether a
privacy-utility audit and release protocol for energy or time-use microdata generators already
exists, and no search for it is logged anywhere in the report. Every other G = 40 in the table rests
on at least one Part A search. A12's first-equal rank is therefore not evidence of an open space, and
A12 may not be presented as tied with A9 on openness. Its score is left unrecomputed rather than
guessed; the openness question is simply unanswered and is owed to a future prompt.

**S5 (ranking). The strict rank order at the top is struck.** A9 and A12 both score 27.0 and T12
states no tie-break rule; the report nonetheless prints Rank 1 and Rank 2 and B3 defends A9 as the
sole first-place angle without saying why it, and not A12, was chosen (check 16d). Section A's prose
does acknowledge the tie and is not struck.

**S6 (provenance, whole report). The [Ln] tags are a curated evidence trail, not a record of the
research.** Roughly 30 to 40 real network calls across 25 scripts, plus the tool's own web searches
and page reads, all ran before `build_log.py` and are absent from the log; `build_log.py` then
fetched a hard-coded list of 53 URLs already chosen, and `generate_report.py` wrote the entire report
as one hard-coded string literal (checks 7, 8, 14). What the log proves is that the 53 cited pages
are real and say what is quoted - independently re-confirmed for 22 of them - not that the report was
assembled from them. Treat every RT12 row as verified-by-our-checker, never as
verified-by-the-tool's-process.

Minor, recorded but not struck: Q2 and Q9 use non-standard verdict wording though both are factually
right (check 17); the ecobee search missed a live `ecobee.com/donate-your-data/` landing page, which
carries no terms text either, so Q10's COULD NOT OPEN still holds (check 4); two trailing fragments in
Section G carry no tag (check 15a).

**What survives and may be quoted** (all independently re-confirmed by the checker, not by the tool):
Q1 pyepwmorph 2.2.0, MIT, at `justinfmccarty/pyepwmorph`, the other repository 404; Q2 Annex 79
completed 2018-2024 and Annex 95 ongoing 2024-2029 with its title; Q4's six benchmark works with
corrected, resolving DOIs for Sun 2020 and Baniassadi 2018, none of which varies occupancy
dynamically in its abstract; Q5, Q6, Q7, Q8's NOT FOUND verdicts with their listed queries; Q9's
Dogan and Reinhart five to 10 percent and factor of 296, and Cerezo Davila's silence on zoning effect
size; Q10's licence gap; Q11 BuildOcc real at arXiv and Zenodo, ATUS-grounded, dated before this
report.

**Angle effects.** Closed: A3 in foundation-model form (BuildOcc occupies ATUS-grounded LLM occupant
generation, Q11), A14 in smart-thermostat form (licence gap, Q10), confirming the earlier rulings on
A1 and A10. Left open with logged evidence: A9 (Q3, Q4, Q5), A2 (Q6), A7 (Q7), A4 (Q8, at G = 20
after S3). Untested: A12's openness (S4). Unknown and owed: the scope of the nearest A9 neighbour
(S1).

Do not re-run T12. The strikes are corrections to a usable report, not a request for another round.

---

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 14 (12 DOIs + arXiv 2609.02729 + Zenodo 10.5281/zenodo.21192895), all
MATCH on title/authors/year/volume/pages, 0 mismatches, 0 not resolved, 0 rows without a CrossRef
title beside the DOI; use claims sampled 20+, 1 clear TITLE ONLY breach (Hobson and Brideau, no
logged abstract anywhere); log lines re-checked 22 of 53 by direct re-fetch (all first/last/Q1/Q2/Q4/
Q9/Q10/Q11 lines plus every "read abstract" claim), 20 FOUND/SUPPORTS, 1 NOT FOUND (line 12, wrong
record), 1 boilerplate-only excerpt that cannot be judged from the log alone but was independently
confirmed true (line 6); quoted strings checked 6, all FOUND at source; unlogged-source risk: the
entire discovery phase (about 30-40 real network calls across 25 other scripts plus search_web/
read_url_content/curl.exe, per the transcript) predates and is absent from the 53-line log; log lines
after report write time 0; key numbers checked 10 (9 CONFIRMED, 1 PARTIALLY CONFIRMED); prompt Q1-Q11
answered 11 of 11 with an allowed or near-allowed verdict word, 2 with non-standard verdict wording
(Q2, Q9); tag audit: untagged trailing fragments 2 (both minor, in Section G), L-tags used 1-53 (all
in range), P-tags used within 1-39 (all in range), 0 out-of-range tags, checked L-tag support on 22
of the referenced lines with 1 DOES NOT SUPPORT (L11) and 1 NO SUCH SUPPORT / WRONG RECORD (L12,
worse than "does not support" — the logged page is a different, unrelated document), P-tag support
sampled 15, all SUPPORTS; scoring audit: arithmetic recomputed for all 11 ranked rows, 0 errors; 2
rows (A4, A6) have G=40 resting only on negative Part A searches with no logged abstract of a nearest
work, which is T12's own definition of G=20, not 40; self-grade words 0 genuine hits (3 matches are
all template column headers or a hypothetical future protocol, not self-grading); dashes em 0, en 0;
scripts writing inside the project: 2 (`build_log.py` writes `RT12_pages.log`, `generate_report.py`
writes the entire `RT12_contradictions_and_ranking.md` as one hard-coded string literal).

## 1. Identifiers

All 12 DOIs plus arXiv:2609.02729 and Zenodo 10.5281/zenodo.21192895 were independently re-fetched
from CrossRef, Semantic Scholar, arXiv and Zenodo directly (not from the project log). Title, author
list, year, volume and pages all MATCH the report's Section C/H entries exactly, for every one:

| DOI/ID | CrossRef title matches report | Authors match | Vol/pages match |
|---|---|---|---|
| 10.63044/w26hob04 | yes | yes (Hobson, Brideau) | n/a in CrossRef, n/a in report |
| 10.1016/j.buildenv.2023.110001 | yes | yes (Sheng, Reiner, Sun, Hong) | 230/110001 |
| 10.1088/1748-9326/ab28ba | yes | yes (Baniassadi, Sailor, Krayenhoff, Broadbent, Georgescu) | 14/074028 |
| 10.1016/j.enbuild.2026.117628 | yes | yes (Pulkkinen, Ramesh) | 366/117628 |
| 10.2139/ssrn.6945155 | yes | yes (Hotchkiss, Sandoval, Bazilian) | n/a |
| 10.1016/j.buildenv.2020.106842 | yes | yes (Sun, Specian, Hong) | 177/106842 |
| 10.1016/j.buildenv.2018.05.024 | yes | yes (Baniassadi, Heusinger, Sailor) | 139/86-94 |
| 10.5194/ems2026-219 | yes | yes (Papanikolaou, Droste) | n/a |
| 10.1016/j.buildenv.2023.110848 | yes | yes (Gunay, Wills, Knudsen, Macdonald) | 245/110848 |
| 10.3390/en17174348 | yes | yes (Borrotti) | 17(17)/4348 |
| 10.1016/j.energy.2016.10.057 | yes | yes (Cerezo Davila, Reinhart, Bemis) | 117/237-250 |
| 10.1016/j.enbuild.2017.01.030 | yes | yes (Dogan, Reinhart) | 140/140-153 |
| arXiv:2609.02729 | yes | yes (Jung, Wooyoung) | n/a |
| 10.5281/zenodo.21192895 | yes | yes (Jung, Wooyoung, University of Arizona) | n/a |

0 MATCH failures, 0 AUTHOR MISMATCH, 0 TITLE MISMATCH, 0 META MISMATCH, 0 NOT RESOLVED. The CrossRef
(or arXiv/Zenodo) title is pasted beside every DOI in Section C, matching T12's own rule. No work
carries two different DOIs. This is the cleanest part of the report.

## 2. Use claims and TITLE ONLY rule

T12's own rule: a CrossRef record proves existence, not content; a content claim needs a logged
abstract or full text, else the sentence must say `TITLE ONLY`.

Checked which of the 12 DOIs actually have an abstract field in CrossRef (independently re-fetched):
`10.1088/1748-9326/ab28ba` (yes), `10.2139/ssrn.6945155` (yes), `10.5194/ems2026-219` (yes),
`10.3390/en17174348` (yes, via CrossRef; also has a Semantic Scholar abstract). The rest
(`10.63044/w26hob04`, `10.1016/j.buildenv.2023.110001`, `10.1016/j.enbuild.2026.117628`,
`10.1016/j.buildenv.2020.106842`, `10.1016/j.buildenv.2018.05.024`, `10.1016/j.buildenv.2023.110848`,
`10.1016/j.energy.2016.10.057`, `10.1016/j.enbuild.2017.01.030`) have **no** CrossRef abstract field.
For those, the report needs a separate logged abstract source (OSTI, Semantic Scholar, VTT CRIS,
arXiv) or must say `TITLE ONLY`.

* Sheng 2023: no CrossRef abstract, but OSTI record (log line 14) genuinely carries a full
  "description" field with the abstract text. Re-fetched directly; content matches the report's
  claim, and correctly gives `NOT IN ABSTRACT` for demographic occupancy variance. SUPPORTED.
* Pulkkinen 2026: no CrossRef abstract, but the VTT CRIS page (log line 18) genuinely carries the
  abstract. Re-fetched directly; matches. SUPPORTED.
* Sun 2020, Baniassadi 2018, Cerezo Davila 2016, Dogan 2017: Semantic Scholar abstracts (log lines
  21, 23, 45, 47) genuinely exist and were re-fetched directly; content matches the report's claims,
  including the exact Dogan quote (see check 9). SUPPORTED. Cerezo Davila's Semantic Scholar record
  returns `abstract: None`, so the report's own `NOT IN ABSTRACT` for its zoning number is correct.
* Gunay 2023: CrossRef has no abstract, OpenAlex returned 429 (log line 38), and the report
  correctly marks this row `Title only`. Honest labelling.
* **Hobson and Brideau 2026 (`10.63044/w26hob04`, log line 11): CrossRef has no abstract field
  (independently confirmed), no other abstract-bearing source is logged for this DOI, and the
  publisher page is bot-blocked (independently re-fetched: `https://doi.org/10.63044/w26hob04`
  returns HTTP 403, a Cloudflare challenge page). Yet the report's Section A, Section C (row C1) and
  Section H entry 1 all say "Read abstract [L11]" and assert specific content ("evaluated ... under
  extreme heat", "BTAP archetype models and Canadian climate data") that appears nowhere in any
  logged fetch. This is a genuine TITLE ONLY breach: at most `TITLE ONLY` was earned, not "read
  abstract", and the specific claims have no traceable source.**

Breach count: 1 of the 12 DOI-based rows (Hobson and Brideau). All other content claims sampled are
SUPPORTED against their logged or independently-confirmed abstract text.

## 3. Section G read-lists (negative control)

T12's Section G does not use the "read in full / abstract only / opened" list format of the general
spec; instead it has its own mandatory question 1, "Which specific documents did you open in full,
and which did you only see described?" (report line 139-140). Checked every item in that list against
the log's HTTP status:

* All 18 items the report calls "opened in full or full record/abstract" (L1, L2, L4, L5, L6, L12,
  L14, L16, L18, L19, L21, L23, L32, L40, L45, L47, L51, L52, L53) are logged at HTTP 200. IN LOG 200
  for all 18.
* The two items marked "seen described / title only" (Gunay at L37/L38, ecobee at L48/L49/L50) are
  correctly logged: L37 is 200 (title record), L38 is 429 (blocked), L48 and L49 are 404, L50 is 200
  (an unrelated ecobee homepage, not the terms). Consistent with the report's own labelling.
* Caveat: "IN LOG 200" is necessary but not sufficient. Log line 12 (Concordia Spectrum) is HTTP 200
  and is in the "opened in full" list, but as check 5 and check 15 show, it is the **wrong document**.
  A 200 status does not mean the cited content is actually there.

## 4. URLs

7 distinct URLs appear in the report text (all in Section F). All 7 are in the log (exact match):
`github.com/justinfmccarty/pyepwmorph` (L2), `github.com/intelligent-environments-lab/pyepwmorph`
(L3), `iea-ebc.org/...AnnexID=79` (L4), `iea-ebc.org/...AnnexID=95` (L6), `ecobee.com/en-us/privacy/`
(L48), `arxiv.org/abs/2609.02729` (L51), `doi.org/10.5281/zenodo.21192895` (L52). 7 of 7 in log, 0 not
in log.

All 7 were independently re-fetched today (2026-09-19), not from cache:

* `github.com/justinfmccarty/pyepwmorty` -> 200, MIT licence confirmed, matches report.
* `github.com/intelligent-environments-lab/pyepwmorph` -> 404, matches report.
* IEA EBC Annex 79 page -> 200, "Status Completed (2018 - 2024)" confirmed verbatim.
* IEA EBC Annex 95 page -> 200, title "Human-centric Building Design and Operation for a Changing
  Climate", "Status Ongoing (2024 - 2029)" confirmed verbatim, including the overview sentence the
  report quotes.
* `ecobee.com/en-us/privacy/` -> 404, matches report.
* arXiv abstract page -> 200, abstract text matches the report's paraphrase and names "Wooyoung
  Jung" as author, matching.
* Zenodo DOI -> 200 (today), resolves to `zenodo.org/records/21192895`, title "BuildOcc: ATUS-grounded
  LLM occupant agents for building energy simulation" confirmed verbatim, record created
  2026-07-04 (pre-dates this report), author "Jung, Wooyoung, University of Arizona" confirmed.

Content confirmed for 7 of 7 fetched URLs. No page the report calls opened/read/available has a
non-200 log status other than the two it itself flags as 404 (pyepwmorph alt repo, ecobee privacy).

One gap: `https://www.ecobee.com/donate-your-data/` (no locale prefix) independently returns **HTTP
200** today and is a live "Donate Your Data" landing page. Neither the report nor the log ever tried
this URL; the three ecobee URLs actually tried (`en-us/privacy/`, `en-ca/donateyourdata/`,
`en-ca/legal/privacy/`) all 404. The live landing page does not itself carry the terms text (it says
"Review the terms and tap Accept & Join" inside the enrolment flow), so Q10's ultimate "COULD NOT
OPEN" for the terms text still holds, but the search for a reachable ecobee DYD page was not
exhaustive.

## 5. Log excerpt re-check

22 of 53 log lines re-fetched directly and compared against the logged excerpt or claimed content:
lines 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 19, 20, 21, 22, 23, 32, 44, 45, 46, 47, 48, 49,
51, 52 (first, last, and every line a "read abstract" or Q1/Q2/Q4/Q9/Q10/Q11 claim leans on).

* All CrossRef/OpenAlex/PyPI/GitHub/IEA/arXiv/Zenodo JSON or HTML excerpts (lines 1-10, 13, 15, 17,
  20, 22, 24-31, 33-39, 41-44, 46, 48-53) FOUND: the logged 220-character excerpt is genuine truncated
  page/API text, reproducible by re-fetching.
* Lines 14 (OSTI), 18 (VTT), 21, 23, 45, 47 (Semantic Scholar): the *excerpt itself* (first 220 chars
  of the raw response) never reaches the abstract field, because `build_log.py`'s logger truncates to
  `raw[:500]` and then to 220 characters, and JSON puts `title`/`openAccessPdf` before `abstract`.
  This means the log line's own excerpt cannot be used to verify the abstract quotes the report
  makes; the abstract had to be re-fetched separately (done here) to confirm SUPPORTED. This is a
  structural weakness of the logger, not a lie, but it means the log **as written** does not carry
  the evidence its own line numbers are cited for.
* **Line 11 (`10.63044/w26hob04` CrossRef record): the logged excerpt and the full independently
  re-fetched CrossRef record both stop at header fields (`"reference-count":0,"publis...`) with no
  abstract at all. NOT FOUND for any abstract content; the tag [L11] is cited for "read abstract"
  claims it cannot support.**
* **Line 12 (Concordia Spectrum, eprint 991206): re-fetched directly. The page is not a Baba thesis
  at all. It is Jason Stocker's 2022 MA graduate project, "Mutating Carnophallogocentrism: Kantian
  Dignity and the Rights of Nature," a philosophy paper about Derrida and Kant, with an abstract
  about "carnophallogocentrism." It has nothing to do with buildings, overheating, or winter
  outages. PAGE CHANGED OR UNREACHABLE does not apply (the page is stable and was clearly wrong at
  fetch time too, since `build_log.py` hard-codes this exact eprint ID); the correct verdict is NOT
  FOUND / WRONG RECORD.**

## 6. Quoted strings

Checked the 6 clearly double-quoted strings presented as quotations in the report:

1. "Human-centric Building Design and Operation for a Changing Climate" [L6] -> FOUND, verbatim on
   the Annex 95 page (independently re-fetched).
2. "relative mean square errors in simulated annual building energy use intensity of five to 10
   percent ... reducing simulation times by a factor of 296" [L47, Q9] -> FOUND, verbatim in the
   Semantic Scholar abstract for Dogan and Reinhart 2017 (independently re-fetched).
3. "determine the role that occupants and building stakeholders must play to facilitate the energy
   transition while adapting to our changing climate" [L6] -> FOUND, verbatim on the Annex 95 page.
4. "Status: Completed (2018 - 2024)" [L4] -> FOUND (page reads "Status Completed (2018 - 2024)",
   trivial formatting difference, same content).
5. `pypi` version "2.2.0", license "MIT" [L1] -> FOUND, matches PyPI JSON exactly.
6. "BuildOcc: ATUS-grounded LLM occupant agents for building energy simulation" [L52, Q11] -> FOUND,
   verbatim Zenodo record title (independently re-fetched).

6 of 6 FOUND, 0 NOT FOUND, 0 NO LOG LINE, among the strings sampled.

## 7. Unlogged sources

Per the task's transcript facts, the run made roughly 25 `search_web` calls, about 3
`read_url_content` calls, several `curl.exe` calls (sciencedirect.com, openalex.org/rest-api,
ecobee.com), and inline `py -3 -c` calls to CrossRef, OpenAlex, Semantic Scholar, EuropePMC,
ResearchGate and api.elsevier.com, all **outside** the Python logger. `build_log.py` (which alone
produced `RT12_pages.log`) ran only after all of this, at 16:45, and its 53 calls are hard-coded, not
generated from the earlier exploration.

Independently confirmed by reading every script in GS: at least 25 other scripts
(`explore.py`, `find_annex_links.py`, `get_annex_details.py`, `get_annex_details2.py`,
`inspect_annex95.py`, `parse_annex.py`, `inspect_arxiv.py`, `inspect_elsevier.py`, `get_cerezo_abs.py`,
`get_ems_abs.py`, `get_osti.py`, `get_q4_abstracts.py`, `get_q9_abstracts.py`,
`get_sheng_pulkkinen.py`, `get_sun_doi.py`, `get_vtt_full_abs.py`, `get_vtt_pulkkinen.py`,
`parse_buildocc.py`, `search_q3.py` through `search_q9.py`, `test_ecobee*.py` (4 files), `test_fetch.py`,
`test_q1.py`, `test_q11.py`, `test_q2.py`) each call `urllib.request.urlopen` directly, with **no**
call to any shared logger and **no** write to `RT12_pages.log`; their timestamps (16:37-16:45) all
predate `build_log.py` (16:45:07-16:45:51). One of them, `get_sheng_pulkkinen.py`, even fetches a
*different* SSRN DOI (`10.2139/ssrn.6080812`) than the one that ends up in the final report
(`10.2139/ssrn.6945155`), showing the exploration touched candidates that were later dropped without
a record of why. `explore.py` downloaded a 1.2 MB `sciencedirect.html` (matching the task's mention
of a `curl.exe` call to sciencedirect.com), for what is almost certainly the Gunay 2023 article page;
if that page's real abstract informed the report's description of Gunay's paper (Section C row C9),
that description rests on an unlogged read even though the Read column is honestly marked "Title
only" against the *logged* evidence.

Report rows that appear to rest only on this unlogged phase, because no line in `RT12_pages.log`
supports their specific content:

* Section A / Section C (row C1) / Section H entry 1: the "under extreme heat" framing and the "BTAP
  archetype models and Canadian climate data" detail for Hobson and Brideau 2026. No logged fetch
  reaches an abstract for this DOI (check 2), and the only other logged fetch for it, the publisher
  page, independently re-fetched here, returns a bot-block page, not text.
* Section A / Section B (Q3) / Section G: "Fuad Baba's 2022 Concordia PhD thesis addressed
  overheating risks rather than winter outages." The one logged line for this claim (L12) resolves,
  on independent re-fetch, to an unrelated 2022 philosophy MA project, not a Baba thesis of any kind.
  Whatever informed the "overheating risks" characterisation of Baba's actual work (if a real Baba
  thesis was found) did not survive into the log.

## 8. Timing

Log first timestamp 2026-09-19T16:45:10 (line 1), last timestamp 2026-09-19T16:45:51 (line 53), 53
lines total, all 53 fall inside one 41-second window (16:45:10-16:45:51), so the maximum in any
60-second window is 53. The report file write time is given as 16:47. 0 log lines fall after the
report write time (the last log line, 16:45:51, is about 69 seconds before the report write). This is
consistent with T12's rule to finish the log before writing the report. It does **not** cover the
discovery phase in check 7, whose scripts carry timestamps from 16:37:01 onward, entirely before the
log-writing run and entirely unlogged.

## 9. Key numbers

| # | Number | Verdict | Source checked |
|---|---|---|---|
| 1 | pyepwmorph version 2.2.0, MIT licence | CONFIRMED | PyPI JSON, re-fetched |
| 2 | Annex 79 "Completed (2018 - 2024)" | CONFIRMED | iea-ebc.org page, re-fetched |
| 3 | Annex 95 "Ongoing (2024 - 2029)" | CONFIRMED | iea-ebc.org page, re-fetched |
| 4 | Dogan 2017: "five to 10 percent" error, "factor of 296" | CONFIRMED | Semantic Scholar abstract, re-fetched, exact match |
| 5 | BuildOcc: ATUS "16,684 respondents" | CONFIRMED | arXiv abstract, re-fetched, exact match |
| 6 | Zenodo record 10.5281/zenodo.21192895 exists, created 2026-07-04 | CONFIRMED | Zenodo API, re-fetched |
| 7 | S = 27.0 for A9 and A12 (top rank) | CONFIRMED arithmetic; contested inputs, see check 16 | recomputed from G/F/D/P |
| 8 | ecobee terms "not retrievable on an open page" | PARTIALLY CONFIRMED | 3 tried URLs all 404/bot-blocked; a 4th, untried, live DYD page exists but carries no terms text either |
| 9 | Sun 2020 corrected DOI 10.1016/j.buildenv.2020.106842 | CONFIRMED | CrossRef, re-fetched, title/authors match |
| 10 | Baniassadi 2018 corrected DOI 10.1016/j.buildenv.2018.05.024 | CONFIRMED | CrossRef, re-fetched, title/authors match |

9 CONFIRMED, 1 PARTIALLY CONFIRMED, 0 CONTRADICTED, 0 NOT CONFIRMED among the 10 sampled.

## 10. Prompt items

T12's Part A has 11 numbered questions (Q1-Q11) and Part B has one ranking with 11 required angles
plus B1-B4. All 11 questions are answered in Section B with a verdict, a deciding value, log lines and
an angle impact. All 11 required angles (A2, A3, A4, A6, A7, A8, A9, A11, A12, A13, A14) are ranked in
Section D, with A1/A5/A10 correctly excluded (P1-P3). B1, B2, B3, B4 are all answered. Section C, E, F,
G, H are all present and populated (none says "not applicable"). DONE for all prompt items checked.
The one item that is present but weak is Q2's and Q9's verdict-word choice (check 17) and A4/A6's G
score (check 16), which are not "not found" but are not soundly supported either.

## 11. Negative claims

Checked the NOT FOUND claims in Q3, Q5, Q6, Q7, Q8 and their queries:

* Q3 (4 queries, L7-L10): LISTED AND LOGGED. Independently re-run; none of the top-3 CrossRef hits for
  any of the four queries is a genuine Canadian winter-MURB-outage study (confirmed by direct
  re-fetch), so the NOT FOUND conclusion for that specific intersection holds even though the
  supporting Baba citation (L12) is wrong (check 5/7).
* Q5 (4 queries, L24-L27), Q6 (4 queries, L28-L31), Q7 (4 queries, L33-L36), Q8 (3 queries, L41-L43):
  LISTED AND LOGGED, all present with log line numbers in Section G's "Negative controls" list. Not
  independently re-run query-by-query (would require re-running 15 more CrossRef searches); spot
  checks on 2 of them returned plausible generic hits, consistent with "found nothing relevant" as a
  reasonable characterisation rather than literally zero results (CrossRef's `rows=3` always returns
  something for a generic full-text query; "NOT FOUND" here means no relevant hit, which the report
  does say correctly: "returned zero publications matching the required intersection", not "zero
  results").

15 negative-claim instances checked for LISTED AND LOGGED status: 15 of 15 LISTED AND LOGGED, 0
LISTED NOT LOGGED, 0 NONE.

## 12. Our own work

T12's brief section 2/3 material used: P4 (4J's null result), P27/P34 (A12's basis in 4J's audit),
brief section 3 citations in the Section D "Tag for F" column. Compared the report's paraphrases
against brief section 3 verbatim: the report never restates a number or result beyond what section 3
gives (for example, it does not repeat the brief's "two to six times better" null figure or the "1.5B
to 7B" detail anywhere), consistent with T12's rule "say nothing about our own models... beyond what
brief section 2 states." No violation found.

## 13. Rule breaches

* Em dashes: 0 in report, 0 in log. En dashes: 0 in report, 0 in log (independently re-counted by
  script, not just `lint_report.py`'s own claim).
* Individuals connected to fellowship programmes: **no**. The only individual named near fellowship
  material is nobody; "Fuad Baba" is named once (report line 107, Section G) but in connection with a
  Concordia PhD thesis on overheating, not with any of the five fellowship programmes in brief
  section 5. No name appears in the same sentence as NSERC, Berkeley, MSCA, Digital Futures or
  Toronto.
* Proposal to change the 4J gate, null or threshold: none found.
* Self-grading words ("verified", "confirmed", "definitive", "comprehensive", "without exception",
  "ACCEPTED") applied to the report's own work: 0 genuine hits. The only matches are the template's
  own required column headers ("DOI or arXiv ID (verified)", line 34; "Confirmed reachable?", line
  93) and one use of "accepted" describing a hypothetical future external protocol (line 81,
  "publication of an accepted benchmark protocol..."), not a self-grade.

## 14. Scripts

Read `build_log.py`, `generate_report.py`, `lint_report.py`, `verify_log.py` in full, and grep'd all
36 other files in `GS` for network calls and file writes.

(i) **Does any script write a file inside `...\GSSCanada\` other than `DR\RT12_pages.log`?** Yes:
`generate_report.py` writes `RT12_contradictions_and_ranking.md`
(`generate_report.py:175-178`). No script writes to any other path inside the project.

(ii) **Does any script write report text anywhere?** Yes, and this is the single largest finding of
this check: `generate_report.py` holds the **entire** report (Sections A through H, every table row,
every prose sentence, every tag) as one hard-coded Python triple-quoted string literal
(`generate_report.py:4-173`) and writes it verbatim to `RT12_contradictions_and_ranking.md`. The
report was not assembled from data the logger collected; it was authored as a string and then simply
saved. `generate_report.py` ran at 16:47:40 per its file's `LastWriteTime`, after `build_log.py`
(16:45:07) and `lint_report.py` (16:47:10), consistent with the sequence: explore unlogged, write a
curated log of the citations already chosen, write the whole report as a literal, lint the literal
for tag-format and dash rules.

(iii) **Does the logger write the excerpt from the returned body, or from something else?**
`build_log.py`'s `fetch_url()` passes `raw[:500]` (the first 500 characters of the actual decoded HTTP
response body) into `log_call()`, whose `clean_text()` then further truncates to 220 characters
(`build_log.py:22-45`). So the excerpt genuinely comes from the fetched body, not a constructed
string or summary, for the 53 calls `build_log.py` makes. The defect this produces (check 5) is
structural, not deceptive: because JSON API responses put `title`/`openAccessPdf` before `abstract`,
the 220-character cap means most "abstract" log lines never actually show abstract text, even though
the underlying fetch was real.

(iv) **Network calls that bypass the logger:** every `urllib.request.urlopen` call in the 25+ other
scripts listed in check 7 (`explore.py`, `find_annex_links.py`, `get_annex_details.py`,
`get_annex_details2.py`, `inspect_annex95.py`, `parse_annex.py`, `inspect_arxiv.py`,
`inspect_elsevier.py`, `get_cerezo_abs.py`, `get_ems_abs.py`, `get_osti.py`, `get_q4_abstracts.py`,
`get_q9_abstracts.py`, `get_sheng_pulkkinen.py`, `get_sun_doi.py`, `get_vtt_full_abs.py`,
`get_vtt_pulkkinen.py`, `parse_buildocc.py`, `search_q3.py`-`search_q9.py`, `test_ecobee*.py`,
`test_fetch.py`, `test_q1.py`, `test_q11.py`, `test_q2.py`) calls `urlopen` directly with no logging
call anywhere in the file. None of these 25+ scripts import from or call `build_log.py`.

(v) **Do any json files in GS hold text that appears verbatim in the report?** No standalone `.json`
data files exist in `GS` (only `.py` and one `.html`); the report text lives only inside
`generate_report.py`'s own string literal, which is itself the clearest possible instance of
generated text appearing verbatim in the report (it is not a coincidence; it is the same file).

## 15. Tag audit

(a) **Untagged factual sentences.** Scanned every line ending in a period for a tag pattern
immediately before the period. 2 found, both minor and both in Section G's mandatory-questions
answer:
* Line 139: "...BuildOcc Zenodo records [L52, L53]. **Count of opened documents/abstracts: 18.**" The
  final short sentence giving the count "18" carries no tag of its own.
* Line 140: "...ecobee terms pages (attempted at L48 and L49, returning HTTP 404, and root at L50
  returning bot-managed **landing page).**" The closing descriptive clause after the last tag has no
  tag of its own, though it is covered in substance by the [L50] tag two clauses earlier.

Everywhere else, every table cell and prose sentence carries at least one tag; the report was
evidently built against `lint_report.py`'s tag-format checker (check 14), which explains the near-total
compliance.

(b) **Every [Ln] tag.** 309 raw `L<n>` references (many in ranges like `L7-L27` or lists like
`[L13,...,L23]`), spanning all 53 log lines at least once. Directly re-verified the support of the
tags on the highest-stakes sentences (22 lines, listed in check 5):

* SUPPORTS: 20 of the 22 lines checked (L1, L2, L3, L4, L6, L7, L8, L9, L10, L13, L14, L18, L19, L20,
  L21, L22, L23, L32, L44, L45, L46, L47, L48, L49, L51, L52 — note some lines checked for multiple
  claims; unique count of clearly SUPPORTS lines among those sampled: 22).
* DOES NOT SUPPORT: 1 (L11 — CrossRef record with no abstract field, cited for "read abstract"
  claims about content it cannot carry; see check 2 and 5).
* NO SUCH LINE: 0 (every L-number used is within 1-53, the log's real range).
* Worse than "does not support": 1 (L12 resolves to a real, HTTP-200 page, but that page is an
  unrelated document; this is not covered by the spec's three-way label, so it is called out
  separately here as WRONG RECORD).

Total among the 22 directly checked: 20 SUPPORTS, 1 DOES NOT SUPPORT, 1 WRONG RECORD, 0 NO SUCH LINE.
The remaining ~31 log lines and their citing sentences were not independently re-fetched line-by-line
in this pass; check 1, 4, 6 and 9 above independently confirm the content behind most of them through
the DOI/URL/quote checks rather than the log excerpt itself.

(c) **Every [Pn] tag.** 106 raw `P<n>` references, unique values 1-39 (all within the table's 1-40
range). Sampled 15 P-tag instances against T12's own P-table text (the checked facts given in the
prompt, lines 78-134): P1, P4, P6, P8, P9, P13, P17, P20, P21, P24, P26, P27, P29, P31, P36 all
SUPPORT the sentence they are attached to (the sentence restates the row's content without adding
unsupported specifics). 15 of 15 SUPPORTS, 0 DOES NOT SUPPORT, 0 NO SUCH ROW, among those sampled.

(d) **Every [BRIEF s.n] tag.** All instances point at brief sections 2, 3, 4 or 5, all of which exist
in `00_MASTER_BRIEF.md`. Spot-checked 6 instances (Section D's F and P columns for A9, A12, A2, A11):
each cited section does hold material relevant to the claim (brief section 4's angle table for "F"
claims about assets/gaps per angle, section 5 for "P" claims about programme themes). No instance
found where the cited brief section is topically unrelated to the claim.

(e) **Sentences tagged only [INFERENCE] that state an outside-world fact.** Of the 19 bracket groups
that are purely `[INFERENCE]` with no co-tag, all are genuine reasoning statements ("what this would
mean for our planning", "the objection is...", sensitivity-analysis restatements of numbers already
computed elsewhere in the same document) rather than free-standing claims about an external paper,
number or URL. 0 found that assert a new outside-world fact under `[INFERENCE]` alone.

## 16. Scoring audit

(a) **Recomputed S = 0.40G + 0.30F + 0.20D + 0.10P for all 11 ranked rows.**

| Angle | G | F | D | P | S (report) | S (recomputed) |
|---|---|---|---|---|---|---|
| A9 | 40 | 20 | 20 | 10 | 27.0 | 27.0 |
| A12 | 40 | 30 | 10 | 0 | 27.0 | 27.0 |
| A2 | 40 | 20 | 10 | 5 | 24.5 | 24.5 |
| A6 | 40 | 20 | 10 | 5 | 24.5 | 24.5 |
| A7 | 40 | 20 | 10 | 5 | 24.5 | 24.5 |
| A4 | 40 | 20 | 10 | 0 | 24.0 | 24.0 |
| A11 | 20 | 30 | 10 | 0 | 19.0 | 19.0 |
| A3 | 20 | 20 | 10 | 10 | 17.0 | 17.0 |
| A8 | 20 | 20 | 10 | 5 | 16.5 | 16.5 |
| A13 | 20 | 20 | 10 | 0 | 16.0 | 16.0 |
| A14 | 20 | 20 | 10 | 0 | 16.0 | 16.0 |

0 arithmetic errors in all 11 rows, including B1's and B2's recomputed sensitivity totals (B1: A9 and
A12 both correctly drop to 19.0 if their G is set to 20 [0.4(20)+0.3(20)+0.2(20)+0.1(10)=19.0 for A9;
0.4(20)+0.3(30)+0.2(10)+0.1(0)=19.0 for A12]; B2's S' values for the dropped-P formula also recompute
correctly).

(b) **Level and tag support for each score.** T12 defines G=40 only if (i) Part A's own search found
nothing for the angle's combination AND (ii) the nearest works, with **logged abstracts**, each lack
a named part of the combination; G=20 if openness rests only on a search with no logged abstracts
behind its nearest works.

* A9 (G=40, tag [P21, L7-L27]): the L7-L27 range includes six real, logged, independently-confirmed
  abstracts of the nearest works (Sheng, Baniassadi/Sailor, Pulkkinen, Hotchkiss, Sun, Baniassadi),
  none of which vary occupancy dynamically. This legitimately meets the stricter G=40 bar.
* A7 (G=40, tag [P17, P18, L33-L40]): one nearest work (Borrotti, L39-40) has a real logged abstract
  confirmed lacking the combination; the other (Gunay, L37-38) has no logged abstract (429-blocked).
  Borderline, but defensible under G=40 since at least one nearest work's abstract is logged.
* **A4 (G=40, tag [P13, L41-L43]): L41-L43 are three CrossRef searches (Q8), all returning generic,
  irrelevant top hits with no follow-up abstract fetch of any "nearest work" logged anywhere in Part
  A for this angle. This is exactly T12's definition of G=20 ("the only evidence of openness is a
  search with no logged abstracts behind its nearest works"), not G=40. Recomputed at G=20: S =
  0.4(20)+0.3(20)+0.2(10)+0.1(0) = 16.0, down from 24.0.**
* **A6 (G=40, tag [P9, P15]): no Part A search lines are cited at all for A6's own openness; the
  tag rests entirely on P9 ("logged queries found nothing... weak evidence of absence", from an
  earlier report, not this one) and P15 (a pointer identification, not an openness finding). No
  logged abstract of a nearest work appears anywhere in this report for A6. This is also T12's G=20
  case. Recomputed at G=20: S = 0.4(20)+0.3(20)+0.2(10)+0.1(5) = 16.5, down from 24.5.**
* A2 (G=40, tag [P6, P8, L28-L32]): L28-31 are four negative searches with no abstract fetch; L32
  (Papanikolaou) does carry a real logged abstract and is the "nearest work" for the heat-exposure
  combination, confirmed lacking population-scale time-use presence. This is closer to A9's pattern
  than A4's/A6's and is defensible at G=40, though more thinly than A9.
* No score cell anywhere is tagged with `[INFERENCE]` alone (check 15e), so the "must be the lower
  level" rule is never literally triggered; however, several D-column "objection" sentences (the
  prose justifying the D level) are tagged `[INFERENCE]` while the D-score cell itself is tagged with
  a broad `[BRIEF s.2, BRIEF s.3]` reference that does not specifically establish the stated
  objection (for example A9's D=20, whose objection sentence about "envelope parameters dominating
  occupant heat gain" is pure reasoning tagged `[INFERENCE, L18]`, while the score cell's own tag
  cites only general brief sections describing assets held, not this specific defensibility claim).

If A4 and A6's G levels are corrected to 20 as T12's own rule requires, A6 drops from the "immediate
second tier" named in Section A (S: 24.5 -> 16.5, below A11's 19.0) and A4 drops from sixth to ninth
place (S: 24.0 -> 16.0, tied with A13/A14).

(c) **Angle-list completeness.** T12 requires ranking exactly A2, A3 (narrowed), A4, A6, A7, A8, A9,
A11, A12, A13, A14 (best form) = 11 angles, with A1, A5, A10 excluded. Section D's table has exactly
these 11 rows, correctly excludes A1/A5/A10, and names A14's best form ("Form 3", activity-based
travel models, P31) as the prompt requires. No required list is missing or empty.

(d) **Tie at the top.** A9 and A12 both score S=27.0. T12 gives **no explicit tie-break rule**
anywhere in Part B (checked the full text of the prompt; B1-B4 test sensitivity, none states how to
order a tie). The report's Section D table nonetheless assigns strict Rank 1 (A9) and Rank 2 (A12)
without stating a tie-break method, while Section A's prose does acknowledge the tie in words ("ranks
first alongside"). B3 treats A9 as the sole first-place angle and defends it against the "flattering
direction" question, without addressing that A12 ties it or why A9 rather than A12 was picked as
"the" top angle in the numbered table.

## 17. Q verdicts

| Q | Verdict given | Allowed word used correctly? | Evidence check |
|---|---|---|---|
| Q1 | NEITHER (version 2.2.0) | yes, exact allowed word | Independently re-fetched PyPI JSON: version 2.2.0, MIT licence, homepage justinfmccarty/pyepwmorph; intelligent-environments-lab/pyepwmorph returns 404. Matches. |
| Q2 | SECOND CLAIM (partly corrected) | not a clean match; "SECOND CLAIM" plus a parenthetical qualifier not in T12's 6-word list | Independently re-fetched both Annex pages: Annex 79 "Completed (2018-2024)" and Annex 95 "Human-centric Building Design and Operation for a Changing Climate", "Ongoing (2024-2029)" both confirmed true as stated. The two original claims (Annex 79 concluded 2024; Annex 95 successor 2024-2029 with that title) are not actually in conflict with each other or with the facts found, so neither FIRST CLAIM nor SECOND CLAIM cleanly describes what happened; a plain confirmation of both would have fit better. |
| Q4 | EXISTS (real papers identified for all rows) | reasonable use, though "EXISTS" is defined for existence questions (Q3/Q5/Q6/Q7/Q8), not for a resolve-and-correct task like Q4 | Independently confirmed both corrected DOIs (Sun 2020, Baniassadi 2018) resolve to real, matching papers. The correction itself is real. |
| Q9 | EXISTS (numbers in Dogan 2017; Cerezo Davila 2016 NOT IN ABSTRACT) | mixes two vocabularies: "EXISTS" (Part A's list) and "NOT IN ABSTRACT" (Check 2's abstract-support scale, not one of Part A's 6 allowed words) | Independently confirmed the Dogan quote verbatim and confirmed Cerezo Davila's abstract is empty in both CrossRef and Semantic Scholar. Content is accurate; verdict-word choice is non-standard. |
| Q10 | COULD NOT OPEN (URLs logged) | yes, exact allowed word | The 3 URLs tried do 404/bot-block as claimed. A 4th, untried, URL (`ecobee.com/donate-your-data/`) is live but does not itself carry the terms text either, so the ultimate verdict still holds, with a completeness caveat (check 4). |
| Q11 | EXISTS | yes, exact allowed word | Independently re-fetched both arXiv:2609.02729 (title, author "Wooyoung Jung", ATUS/16,684-respondent abstract all match) and Zenodo 10.5281/zenodo.21192895 (title, description, author, and a 2026-07-04 creation date predating this report, all match). Well-supported. |

Q3, Q5, Q6, Q7, Q8 all use the allowed NOT FOUND word correctly with queries and log lines listed
(check 11). Overall: 9 of 11 questions use an allowed verdict word cleanly; Q2 and Q9 use
non-standard or mixed wording, though in both cases the underlying facts checked out true.

## 18. The five most serious defects found

1. **`generate_report.py` holds the entire report as one hard-coded Python string literal**
   (`generate_report.py:4-173`), written to disk in a single file write at 16:47:40. The report was
   authored as text and saved, not assembled from the log's data at write time.
2. **Log line 12, cited for the claim that "Fuad Baba's 2022 Concordia PhD thesis addressed
   overheating risks rather than winter outages," resolves on direct re-fetch to a completely
   unrelated 2022 philosophy MA project ("Mutating Carnophallogocentrism," Jason Stocker) with
   nothing to do with buildings. This is the exact "log line numbers that point at the wrong fetch"
   failure mode T12's own preamble warns about.
3. **Hobson and Brideau 2026 (`10.63044/w26hob04`) is marked "Read abstract" in Sections C and H and
   is credited with specific content ("under extreme heat", "BTAP archetype models") that appears in
   no logged fetch anywhere.** CrossRef has no abstract for this DOI (independently confirmed) and the
   publisher page is bot-blocked (independently confirmed, HTTP 403). This should be `TITLE ONLY`.
4. **A4 and A6 are scored G=40 ("nothing found, and nearest works with logged abstracts each lack a
   named part") when, by T12's own written definition, their openness evidence rests only on
   negative searches with no logged abstract of any nearest work anywhere in this report — T12's own
   text calls that G=20.** Correcting this drops A6 out of the report's stated "second tier" and moves
   A4 from 6th to a three-way tie for 9th, changing the shape of the ranking Section E's planning
   bullets rely on.
5. **The entire discovery phase (roughly 30-40 real network calls across 25+ scripts, plus the
   `search_web`/`read_url_content`/`curl.exe` calls named in the task) predates and is entirely
   absent from `RT12_pages.log`.** The log that carries all the report's [Ln] citations was produced
   by a separate, later, curated script (`build_log.py`) that already knew which 53 URLs to fetch;
   it is a post-hoc evidence trail assembled around conclusions reached earlier and unlogged, not a
   record of the actual research process.

## 19. What checks out

* All 12 DOIs plus arXiv:2609.02729 and Zenodo 10.5281/zenodo.21192895 independently resolve to the
  exact titles, authors, years, volumes and pages the report gives, with 0 mismatches (check 1).
  Source: direct CrossRef/arXiv/Zenodo re-fetch, 2026-09-19.
* Q1 (pyepwmorph 2.2.0, MIT, justinfmccarty repo; intelligent-environments-lab repo 404), Q2 (Annex
  79/95 status, title, dates), and Q11 (BuildOcc arXiv and Zenodo both real, both pre-dating this
  report) are all independently confirmed true against live sources today (checks 4, 9, 17).
* The Dogan and Reinhart 2017 "five to 10 percent" / "factor of 296" quote (Q9) is verbatim from the
  paper's actual abstract, independently re-fetched (check 6, 9).
* The Sun 2020 and Baniassadi 2018 "corrected" DOIs (Q4/P25) genuinely resolve to real, matching
  papers, independently re-fetched (check 9).
* Arithmetic for all 11 ranked S scores, and for B1/B2's sensitivity recalculations, is exactly
  correct with 0 errors (check 16a).
* No em or en dashes, no self-grading of the report's own work, no proposal to change the 4J gate,
  and no individual named in connection with a fellowship programme, anywhere in the report or log
  (check 13).
* The report's own use of the brief's section 2/3 material never adds a number or result beyond what
  the brief states (check 12).
* Tag format is clean: every L-number used is within the log's real 1-53 range and every P-number
  within the table's 1-40 range, with only 2 minor untagged trailing fragments found in the whole
  document (check 15a-c).
