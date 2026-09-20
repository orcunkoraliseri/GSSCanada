# Vetting RT17: llm_reading_records_and_conformal_ubem (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). Round 2 does not stand; `A7` is not settled by it.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: the negative control is false, by the prompt's own void rule.** Section G lists
   Pan et al. 2026 as "opened in full" and Gunay et al. 2023 as "abstract only"; the log holds only a
   bare CrossRef metadata call for each, with no abstract (section 3). The corrections block says a
   negative control naming an item not fetched voids the report.
2. **The round-1 defect class recurs.** `arXiv:2306.05263`, given as a conformal-prediction paper for
   language generation, resolves (log line 91, status 200) to an unrelated algebraic-geometry paper;
   the log showed the true title and the report did not use it (section 1).
3. **Other defects.**
   - None of the 8 key numbers is confirmed at source, and none carries the test-set size and
     table or page the prompt requires (section 9): the 90 %/95 % coverage, 95.5 % to 100 %
     correctness, 40,000 nodes, the three register record counts, the renovation rates, the 30 % to
     50 % over-prediction.
   - Section F's Montreal row names a field, a count and a CC-BY licence that are not on the Montreal
     page; Italy is dropped from Section F despite three logged Italy fetches (sections 4, 10).
   - Item 1's per-work columns (language, open weight, supervised or zero-shot, accuracy with
     ground-truth size) are not filled (section 10).
   - The negative claims cite wrong log lines (item 3 points at two unrelated 429 errors; one of
     item 1's three queries is itself a 429) (section 11).
4. **Kept.**
   - Identity only: five identifiers resolve and match CrossRef or arXiv exactly (Zhang et al. 2023
     arXiv:2311.08535, Pan et al. 2026, Gunay et al. 2023, Borrotti 2024, Angelopoulos and Bates
     2023) (section 1). Unread pointers; no use claim or figure attached to them is kept.
   - Zhang et al. 2023: language models used to process three open municipal building datasets, in
     its arXiv abstract (section 2).
   - Toronto building permits under the Open Government Licence (Toronto) and England EPC under the
     Open Government Licence v3.0, both on the live pages (section 4).
   - Process: no file written in the project besides the log; the logger writes real response text
     (section 14).
5. **Do not re-run T17 in Gemini as it stands.** The page log worked (14 of 14 excerpts found); the
   failures are in what the tool writes after fetching. `A7` goes to `T12` as pointers only.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: identifiers 6 (MATCH 5, author mismatch 0, other mismatch 1, not resolved 0; rows
without CrossRef title 0 of 4 DOI rows); use claims 6 (supported 2, not in abstract 1, contradicted 1,
no abstract 2; TITLE ONLY breaches 2); Section G items 6 (in log 200 4, not 200 0, not in log 2); URLs
in report 4 (in log 4 [normalised, doi.org vs api.crossref.org/works], not in log 0; fetched 4,
content confirmed 4); log excerpts re-checked 14 (found 14, not found 0, unreachable 0); quoted
strings 4 (found 4, not found 0, no log line 0); unlogged-source claims 1 (plus rows resting on no
identifiable source); log lines after report write 0; key numbers 8 (confirmed 0, contradicted 0, not
confirmed 8); prompt items 6 (done 4, done-partial 2, dropped 0, see section 10 for the Italy
sub-item); negative claims 2 (listed and logged 2, of which 1 of the 2 supporting queries for item 3
point at the wrong log lines and 1 of the 3 supporting queries for item 1 is itself a 429 error;
listed not logged 0; none 0); self-grades 0; dashes em 0, en 0 (report and log both); scripts writing
inside the project 0 (only RT17_pages.log is written there); scripts bypassing the logger 2
(find_boverket.py, inspect_boverket_api.py, both from an earlier pass, both `log=False`) plus 1 direct
unlogged CKAN call given in the task transcript, present in no script file in GS\t17.

## 1. Identifiers

Six identifiers appear in the report (Sections B, C, H): four DOIs, two arXiv IDs. No work carries two
different DOIs or IDs across sections (Sections B/C/H are internally consistent for every row).

| # | ID (location) | CrossRef/arXiv status (checked live) | Live title / authors / year / vol / pages | Report's claimed title / authors / year / vol / pages | CrossRef title pasted in table? | Verdict |
|---|---|---|---|---|---|---|
| 1 | arXiv:2311.08535 (Zhang, Chen, Zou; Section C row 1, H ref 1) | 200 (arxiv.org/abs/2311.08535) | "Taxonomy, Semantic Data Schema, and Schema Alignment for Open Data in Urban Building Energy Modeling" | same title, 2023 | n/a (arXiv, not a DOI row) | MATCH |
| 2 | 10.1016/j.autcon.2026.106791 (Pan et al.; Section C row 2, H ref 2) | 200 | "LLM-enabled multi-agent framework for natural language interaction with graph-based digital twins"; Pan, Wang, Lu, Lamsal, Parn, Zlatanova, Brilakis; 2026 (2026-03); Automation in Construction 183: 106791 | same title/authors/year/vol/page | yes | MATCH |
| 3 | 10.1016/j.buildenv.2023.110848 (Gunay et al.; Section C row 3, H ref 3) | 200 | "An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis"; Gunay, Wills, Knudsen, Macdonald; 2023 (2023-11); Building and Environment 245: 110848 | same title/authors/year/vol/page | yes | MATCH |
| 4 | 10.3390/en17174348 (Borrotti; Section C row 4, H ref 4) | 200 | "Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation"; Borrotti; 2024 (2024-08-30); Energies 17: 4348 | same title/authors/year/vol/page | yes | MATCH |
| 5 | 10.1561/2200000101 (Angelopoulos & Bates; Section C row 5, H ref 5) | 200 | "Conformal Prediction: A Gentle Introduction"; Angelopoulos, Bates; 2023 (2023-03-27); Foundations and Trends in Machine Learning 16: 494-591 | same title/authors/year/vol/pages | yes | MATCH |
| 6 | arXiv:2306.05263 (Quach et al.; Section C row 6, H ref 6) | 200 (arxiv.org/abs/2306.05263, log line 91) | "Effective homology and periods of complex projective hypersurfaces" (a SageMath computational-algebra paper, no author overlap, no NLP or conformal-prediction content) | "Conformal Prediction for Natural Language Generation" by Victor Quach et al. | n/a (arXiv row) | TITLE MISMATCH (the ID resolves to a real, unrelated paper) |

Row 6 is the same defect class round 1 failed on: an identifier that resolves (200) but to the wrong
work. The log itself shows the correct excerpt (title "[2306.05263] Effective homology and periods of
complex projective hypersurfaces", log line 91) right next to the correct 2311.08535 fetch (line 90);
the wrong title was not carried from the log into the report.

## 2. Use claims and TITLE ONLY rule

| Work | Claim in report | Log line(s) for abstract/full text | Content check | Verdict |
|---|---|---|---|---|
| Zhang et al. 2023 | "Developed semantic schemas and tested zero-shot LLMs ... 3 open municipal building datasets" | line 90, arxiv.org/abs/2311.08535 (abstract page, re-fetched in full: "we use three popular open data to show how they can be automatically processed ... using large language models") | "3 open datasets" and general LLM-processing claim supported; "zero-shot" is not stated in the abstract | SUPPORTED (general); "zero-shot" detail NOT IN ABSTRACT |
| Pan et al. 2026 | "Built Graph-DT-GPT to translate natural language queries into Cypher graph queries over 40,000 building nodes"; "95.5% to 100% answer correctness but zero abstention" | none — only line 65, a bare CrossRef bibliographic call (`api.crossref.org/works/10.1016/j.autcon.2026.106791`), which carries no abstract field (re-confirmed live: `abstract present: False`) | no abstract or full text was ever fetched for this DOI anywhere in the log | NO ABSTRACT / TITLE ONLY breach — Section C, Section H and Finding 5 all say "Read: full text" / "Opened in full" |
| Gunay et al. 2023 | "Analyzed Canadian municipal permit records to estimate envelope and HVAC retrofit prevalence across housing stock" | none — only line 64, bare CrossRef metadata call, no abstract field (re-confirmed live: `abstract present: False`) | no abstract-bearing fetch exists | NO ABSTRACT / TITLE ONLY breach — report and Section G both say "Read: abstract" |
| Borrotti 2024 | "Split conformal prediction applied to heating/cooling surrogate load forecasting achieves valid 90% and 95% marginal coverage" | line 68, CrossRef metadata call, which does carry an abstract (re-confirmed live) | the actual abstract text ("Results show that conformal prediction can be applied when any assumptions about input and output variables are made...") never states 90% or 95%, or heating/cooling specifically | NOT IN ABSTRACT (the general topic is supported, the specific figure is not) |
| Angelopoulos & Bates 2023 | "Non-conformity scores and exchangeability provide finite-sample, distribution-free marginal and group-conditional guarantees" | line 78, CrossRef metadata call, abstract present (re-confirmed live) | abstract covers distribution-free, non-asymptotic guarantees and "models that abstain"; does not use the words "non-conformity score" or "group-conditional" verbatim | SUPPORTED (paraphrase, textbook-level) |
| Quach et al. (arXiv:2306.05263) | "Developed conformal prediction framework for natural language generation ... statistical guarantees on token sequences" | line 91, arxiv.org/abs/2306.05263 | the actual page (re-fetched) is "Effective homology and periods of complex projective hypersurfaces," an algebraic-geometry paper with no conformal-prediction or NLP content | CONTRADICTED (claim describes a different paper than the one the ID resolves to) |

TITLE ONLY breaches: 2 (Pan et al., Gunay et al.).

## 3. Section G read-lists (negative control)

Section G.3.1 lists: opened in full = Zhang et al., Pan et al., Borrotti, Angelopoulos & Bates, Quach
et al. (5); abstract only = Gunay et al. (1).

| Item | Log line | Status | Verdict |
|---|---|---|---|
| Zhang et al. 2023 | 90 | 200 | IN LOG 200 (the fetch is an arXiv abstract page, not full text) |
| Pan et al. 2026 | none | — | NOT IN LOG (no abstract or full-text fetch exists) |
| Borrotti 2024 | 68 | 200 | IN LOG 200 |
| Angelopoulos & Bates 2023 | 78 | 200 | IN LOG 200 |
| Quach et al. (2306.05263) | 91 | 200 | IN LOG 200 (fetch succeeded but is the wrong paper) |
| Gunay et al. 2023 (claimed "abstract only") | none | — | NOT IN LOG (only a bare CrossRef metadata call exists, no abstract field) |

## 4. URLs

Only 4 URLs appear anywhere in the report body, all in Section H (`https://doi.org/10.1016/j.autcon.2026.106791`,
`https://doi.org/10.1016/j.buildenv.2023.110848`, `https://doi.org/10.3390/en17174348`,
`https://doi.org/10.1561/2200000101`). Section F (the register table) carries no URLs at all, only
prose descriptions of access routes and licences. All 4 fetched (all if fewer than 20, per the spec).
Each is in the log under its `api.crossref.org/works/<same DOI>` equivalent form (trivially
normalised) and each resolves to the content the report claims (see check 1). 4 of 4 in log
(normalised), 4 of 4 fetched, 4 of 4 content confirmed.

Extra check (b), Item 4 registers: no HTTP status in the log is 403 anywhere in RT17_pages.log (grep
confirms zero 403 lines; all failures are 404 or 429). `test_registers.py` (GS\t17\) does implement a
script-UA-then-browser-UA fallback keyed on `status == 403 or status == "ERR"`, but it was never
triggered this round because no register returned 403; Montreal's early wrong dataset slugs (lines 37,
41, 74) returned 404, not 403, and the final correct slug (line 92, 14:38:13) returned 200 on the
first (script-UA) attempt.

Extra check (b) continued, live re-fetch of all 6 named registers plus Italy (fetched with a
browser-like User-Agent, done now):

| Register | Live status | Claimed content check |
|---|---|---|
| Montreal, `donnees.montreal.ca/dataset/permis-construction` | 200 | Live page's actual free-text fields are `description_type_demande`, `description_type_batiment`, `description_categorie_batiment` (all `texte variable`). No field called `description_des_travaux` appears anywhere on the page. No occurrence of "Creative Commons," "CC-BY," or "500 000" / "500,000" / any record-count figure. |
| Toronto, `open.toronto.ca/dataset/building-permits-cleared-permits/` | 200 | "Licence : Open Government Licence - Toronto" found verbatim, matches report |
| England, `epc.opendatacommunities.org/` | 200 | "Open Government Licence v3.0" found verbatim, matches report; no occurrence of "25 million" anywhere on the page |
| France, `data.ademe.fr/datasets/dpe-v2-logements-existants` | 200 | No occurrence of "ODbL," "Open Database," or "10 million" anywhere in the fetched HTML |
| Sweden, `boverket.se/sv/energideklaration/` | 200 | Page shows "oppna data" (open data) and "API for energideklarationer" (confirms an open API exists); no occurrence of the word "application"/"ansokan" tied to research access in the fetched text |
| Spain, `sedecatastro.gob.es/` | 200 | No occurrence of "reutilizacion," "licencia," "Re-use," or "ano_reforma" on the fetched homepage |
| Italy, `siape.enea.it/` and `cened.it/` | both 200 (also logged at lines 34, 35) | fetched successfully, but Italy has no row anywhere in Section F (see check 10) |

## 5. Log excerpt re-check

14 log lines re-fetched, spread from the first line (1) to the last (92), including every 200 line
the report leans on: the 4 CrossRef DOI records (lines 65, 64, 68, 78), the 2 arXiv abstract pages
(lines 90, 91), and 8 register pages (Montreal line 92, Toronto line 75, England line 73, France line
72, Sweden line 76, Spain line 77, Italy line 34, Italy line 35). All 14 FOUND: each re-fetch returned
the same HTTP status and the same title/content type as the logged excerpt, so the logged excerpts
are genuine and reproducible. (Whether the report's specific *claims* about those pages are supported
is a separate question, covered in checks 2, 4, 6 and 9 — several are not.)

## 6. Quoted strings

Only 4 double-quoted strings presented as quotations appear in the report, all in Section H (the
CrossRef titles beside the 4 DOIs). All 4: FOUND, sourced to the log lines in check 1, and confirmed
to match the live CrossRef title exactly.

Not counted here (backtick, not double-quote, so outside the letter of this check, but noted as a
defect under check 4/9): `description_des_travaux` in Section F row 1 is presented as a literal field
name and is NOT FOUND on the logged/re-fetched Montreal page.

## 7. Unlogged sources

One unlogged source is given directly in the task: a direct call to the Montreal CKAN API
(`package_search`, query "permis construction") made outside `research_fetcher.py`/`fetch_helper.py`'s
logger. Confirmed absent from RT17_pages.log: the log's only `package_search` calls are for `q=permis`
(lines 46 and 89, both 200), never for "permis construction." No script inside GS\t17 issues a
`package_search?q=permis+construction` call either (search_exact_t17.py uses `q=permis`, logged).

Report rows that appear to rest on no identifiable logged (or given unlogged) content: Section F row 1
(Montreal) — the `description_des_travaux` field name, the "500,000+" permit count and the "Creative
Commons Attribution (CC-BY 4.0)" licence do not match either the logged Montreal page content (check
4) or the CKAN `q=permis` search results (which return a 22-dataset list headed by an unrelated
"Service de la culture, des sports..." dataset, not permit counts or licence text), nor anything
recoverable from the given unlogged CKAN call (its query term "permis construction" would return
dataset search hits, not field-level metadata or a record count either).

## 8. Timing

Log first timestamp: 2026-09-19T11:49:06. Log last timestamp: 2026-09-19T14:38:13. Line count: 92.
Maximum lines in any 60-second window: 39 (the final CrossRef/register burst ending at 14:38:03-14:38:13).
Report file write time given in task: 2026-09-19 14:38:32 (-04:00), 19 seconds after the last log
line. Log lines after the report write time: 0.

## 9. Key numbers

| # | Number | Claimed source | Check | Verdict |
|---|---|---|---|---|
| 1 | 90% and 95% marginal coverage | Borrotti 2024 (Finding 3) | Borrotti's actual CrossRef abstract (logged line 68) never states 90% or 95%, or heating/cooling specifically | NOT CONFIRMED |
| 2 | 95.5% to 100% answer correctness | Pan et al. 2026 (Finding 5) | no abstract or full text logged for this DOI at all (check 2) | NOT CONFIRMED |
| 3 | 40,000 building nodes | Pan et al. 2026 (Section C row 2) | same, no logged content | NOT CONFIRMED |
| 4 | 500,000+ construction/renovation permits | Montreal register (Finding 8, Section F) | not present on the logged/re-fetched Montreal dataset page (check 4) | NOT CONFIRMED |
| 5 | Over 10 million EPC records | France ADEME DPE (Finding 9) | not present on the logged/re-fetched ADEME page (check 4) | NOT CONFIRMED |
| 6 | Over 25 million EPC records | England EPC (Finding 10) | not present on the logged/re-fetched England EPC page (check 4) | NOT CONFIRMED |
| 7 | National renovation rates 1.0% to 1.5%; deep renovation <0.2%/year | Section E.2 | no source cited at all in Section E.2 for these figures, and no log line supports them | NOT CONFIRMED |
| 8 | 30% to 50% over-prediction of baseline energy use from misclassified renovation status | Section E.2 | no source cited at all | NOT CONFIRMED |

Every accuracy or coverage figure carried the extra hard rule "test-set size and table or page" from
the corrections block. None of the 8 numbers above carries a test-set size or a table/page reference
anywhere in the report; item 1 (LLM extraction accuracy against a labelled ground truth) is not
populated with any number at all in Section C.

## 10. Prompt items

| Item | Requirement | Status |
|---|---|---|
| 1 | LLM extraction from records, with per-work language/country, model/open-weight, supervised/zero-shot, accuracy + ground-truth size, stock-model feed, abstention reporting | DONE (partial) — Section C has the 2 works but the table's fixed columns do not carry per-work language/country, open-weight status, supervised/zero-shot, or an accuracy figure with ground-truth size; none of that is answered anywhere in the report |
| 2 | Selective prediction / conformal methods for LLM outputs, benchmarks, coverage, failure modes, GPU feasibility | DONE — Section E.1 |
| 3 | Conformal prediction in building energy/UBEM, physics-based coverage question | DONE — Section A, Finding 2, Section C rows 4-6 |
| 4 | Register contents for Sweden, Spain, France, England, Italy, Canada (QC, ON) | DONE (partial) — Section F has Sweden, Spain, France, England, Montreal, Toronto (6 rows) but Italy is entirely absent, despite 3 Italy register fetches in the log (lines 34, 35, 36, 45; siape.enea.it, cened.it, energia.regione.emilia-romagna.it) |
| 5 | Renovation state as a target, national rates, mis-estimation impact | DONE — Section E.2, but its numbers are uncited (see check 9) |
| 6 | Honest placement of the LLM+conformal combination | DONE — Section E.3 |

Extra check (c), Item 6: Section E.3 calls the combination "an entirely open combination" but does not
itself list the supporting queries beside that sentence; the queries are given separately in Section
G.2, cross-referenceable but not inline.

Named leads: journals *Automation in Construction* and *Building and Environment* were used as actual
sources (Pan et al., Gunay et al.); *Energy and Buildings*, *Advanced Engineering Informatics* and
*Applied Energy* were not. Registers named but fetched-yet-dropped from Section F: the French permit
database (`data.gouv.fr` SITADEL, fetched at line 31/14:37 area, no Section F row), the English
planning portal (`planning.data.gov.uk`, fetched, no Section F row), and the Emilia-Romagna
certificate register (fetched, no Section F row — see Item 4 above for the full Italy omission).

## 11. Negative claims

Two `NOT FOUND` claims, both with queries listed in Section G.2 with cited line numbers.

Item 1 ("zero studies report abstention...", 3 queries cited at log lines 1, 2, 3):
- Line 1 query, live: `LLM building permit extraction` (OpenAlex), status 200 — matches report's
  paraphrase reasonably.
- Line 2 query, live: `large language model building energy certificate` (OpenAlex), status 200 —
  report's paraphrase adds "free text renovation," not in the actual query text.
- Line 3 query, live: `natural language processing EPC building attributes` (OpenAlex), status **429**
  (rate-limit error) — this query never returned results; it is cited as supporting evidence for a
  "zero occurrences" finding, but no occurrences (zero or otherwise) were ever actually returned by it.

Item 3 ("zero studies attach coverage bounds to EnergyPlus stock cohorts", 2 queries cited at log
lines 7 and 8):
- Log line 7, live content: `text mining building inspection reports` (OpenAlex), status 429 — unrelated
  to conformal prediction or UBEM.
- Log line 8, live content: `large language model building stock archetype` (OpenAlex), status 429 —
  also unrelated.
- The queries the report actually describes (`conformal prediction urban building energy model
  physics`, `conformal trust bounds EnergyPlus stock UBEM`) are real and did run successfully, but at
  log lines 60 and 61 (both CrossRef, both status 200), not at lines 7 and 8 as cited.

Verdict: both negative claims LISTED AND LOGGED (the real underlying queries do exist and returned
usable results), but the specific line-number citations in Section G are wrong for item 3 (point at
unrelated 429 lines instead of the real lines 60-61), and one of item 1's three cited lines is itself
a 429 error rather than a completed zero-result search.

## 12. Our own work

None. Section D's asset column ("OpenUBEM provenance and imputation tiers, Speed HPC cluster,
validation discipline") draws only on brief section 3's asset list, as the template's column header
requires; no row states a number, title or result for CENTUS, 1J-4J, GSSCanada or OpenUBEM.

## 13. Rule breaches

Em dashes: 0 in report, 0 in log. En dashes: 0 in report, 0 in log (all counts by direct grep).

Named individuals connected to fellowship programmes: none found (the report names two fellowship
programmes, "Digital Futures" and "Schmidt AI in Science," at report lines 59 and 98, never a person).

Proposals to change the 4J pre-registered gate, null or threshold: none found; all occurrences of
"gate" and "threshold" in the report (lines 5, 13, 26, 29, 44, 58, 87) refer to the LLM's own
abstention/conformal thresholds inside the proposed A7 methodology, not to 4J.

Self-grades: none found in report prose. The two hits for "verified" (line 24) and "Confirmed" (line
63) are the response template's own column headers ("DOI or arXiv ID (verified)", "Confirmed
reachable?"), not the tool grading its own report. Section G.4's sentence "All author names, venues,
volumes, and page numbers were copied directly from CrossRef API records" is not on the banned-word
list, but is contradicted by check 1 row 6 (no CrossRef record was ever fetched for the Quach et al.
row; its identifier is an arXiv ID that resolves to a different paper).

## 14. Scripts

Read: `GS\research_fetcher.py`, and in `GS\t17\`: `fetch_helper.py`, `run_t17_research.py`,
`search_exact_t17.py`, `search_item1.py`, `run_verification.py`, `test_registers.py`,
`test_updated_registers.py`, `find_boverket.py`, `inspect_boverket_api.py`.

(i) No script writes any file inside `C:\Users\o_iseri\Desktop\GSSCanada\` other than
`RT17_pages.log` (`fetch_helper.py:10` and `research_fetcher.py` both hard-code `LOG_PATH` to
`RT17_pages.log`; the other outputs — `item1_candidates.json`, `registers_status.json`,
`t17_verified_data.json` — all write inside `GS\t17\`).

(ii) No script writes report text (Markdown, table rows, sections). All scripts only fetch, log and
print to stdout or JSON.

(iii) The logger writes the excerpt from the actually-returned response body: `fetch_helper.py:51`
(`excerpt = body[:250]`) and `research_fetcher.py:28` (`excerpt = body[:250]`), then both truncate/clean
to ~200 chars in `log_entry`/`log_page`. No constructed summary or JSON-field substitution is used for
the excerpt; it is the real body text (or `HTTPError {code}: {reason/body}` on failure).

(iv) Network calls that bypass the logger: `find_boverket.py:4` and `inspect_boverket_api.py:4`, each
call `fetch_url(..., browser_ua=True, log=False)` — one unlogged GET to
`boverket.se/sv/om-boverket/publicerat-av-boverket/oppna-data/` and one unlogged GET to
`boverket.se/sv/om-boverket/oppna-data/publikt-api-for-energideklarationer/`. Neither script's target
URL or content appears verbatim in the final report. Separately, per the task transcript, one direct
unlogged CKAN `package_search` call for "permis construction" was made outside any script file found
in `GS\t17\` (see check 7).

(v) `t17_verified_data.json` holds the exact CrossRef title/author/venue/volume/page strings for
`10.1016/j.autcon.2026.106791`, `10.1016/j.buildenv.2023.110848` and `10.3390/en17174348`, and those
strings appear verbatim in the report's Section H (legitimate reuse of a real CrossRef response, not a
sign of invention). The same JSON file also holds 4 other DOIs the `run_t17_research.py` script
guessed (`10.1016/j.autcon.2024.105574`, `10.1016/j.enbuild.2023.113333`, `10.1016/j.apenergy.2023.121731`,
`10.1016/j.enbuild.2021.111442`) whose CrossRef-returned titles are all unrelated to the topics the
script's own comments claim for them (e.g. "concrete defect detection," "Austrian passive cooling,"
"district heating fault diagnosis," "German heating-demand framework") — none of these 4 appear
anywhere in the final report, so these wrong guesses were correctly dropped rather than used.
`item1_candidates.json` (20 OpenAlex hits from an earlier pass, all LLM-survey/chemistry/agent papers,
none about building records) also does not appear anywhere in the final report.

## 15. The five most serious defects found (facts, one line each, no verdict words)

1. `arXiv:2306.05263`, cited as Quach et al. "Conformal Prediction for Natural Language Generation,"
   resolves (log line 91, status 200) to an unrelated paper, "Effective homology and periods of
   complex projective hypersurfaces."
2. Pan et al. 2026 (`10.1016/j.autcon.2026.106791`) is marked "Read: full text" / "Opened in full" and
   carries specific claims (40,000 nodes, 95.5-100% correctness) with no abstract or full-text fetch
   anywhere in the log — only a bare CrossRef bibliographic call (log line 65).
3. Gunay et al. 2023 (`10.1016/j.buildenv.2023.110848`) is marked "Read: abstract" / listed under
   "Abstract / summary only" in Section G, but no abstract-bearing fetch exists in the log (CrossRef
   record for this DOI carries no abstract field, confirmed live).
4. Section G's cited log-line numbers for the Item-3 negative-finding queries (lines 7, 8) point to
   two unrelated 429-error OpenAlex searches; the real matching CrossRef queries that did succeed sit
   at lines 60-61 instead. One of Item 1's three cited queries (line 3) is itself a 429 error, not a
   completed zero-result search.
5. Section F's Montreal row states a `description_des_travaux` field, a "500,000+" permit count and a
   "Creative Commons Attribution (CC-BY 4.0)" licence, none of which appear on the logged/re-fetched
   `donnees.montreal.ca/dataset/permis-construction` page (whose actual fields are
   `description_type_demande`, `description_type_batiment`, `description_categorie_batiment`, with no
   licence text or record count visible); Italy is entirely absent from Section F despite being named
   in prompt Item 4 and despite three logged Italy register fetches.

## 16. What checks out (facts the manager could keep, each with its source)

- 5 of 6 identifiers resolve to exactly the work claimed, with authors/year/volume/pages matching the
  live CrossRef/arXiv record and no double-DOI problem anywhere (unlike round 1). Source: check 1,
  live CrossRef/arXiv fetches this session.
- Zhang et al. 2023's general claim (LLMs used to process 3 open municipal datasets) is supported by
  its actual arXiv abstract. Source: `arxiv.org/abs/2311.08535`, re-fetched this session.
- Toronto's and England's licence claims ("Open Government Licence - Toronto", "Open Government
  Licence v3.0") are confirmed verbatim on the live register pages. Source: check 4, live re-fetch.
- Zero em dashes and zero en dashes in both report and log. Source: direct grep, this session.
- No named individuals, no 4J gate-change proposal, no banned self-grade language in report prose.
  Source: check 13, direct grep.
- No script writes anywhere inside the GSSCanada tree except `RT17_pages.log`; no script writes report
  text; the logger's excerpt is taken from the real response body, not a constructed summary. Source:
  check 14, direct read of `fetch_helper.py` and `research_fetcher.py`.
- The report was written (14:38:32) 19 seconds after the last log line (14:38:13); zero log lines fall
  after the report write time. Source: check 8, log timestamps this session.
- `test_registers.py` correctly implements a script-UA-then-browser-UA fallback for 403/error
  responses (never triggered this round because no register actually returned 403). Source: check 4,
  `test_registers.py:43-48`, `registers_status.json`.
