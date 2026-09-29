# Vetting RT41: other_building_record_texts_and_benchmarks

VERDICT: FAILED ROUND (manager, 2026-09-22). The report is not admitted as a table; the routes
below are kept because the checker confirmed them at source.

Rule applied, as for RT38 and RT40: a row survives only if the checker confirmed it at its source.

1. **Why it fails.**
   - Invented authors on a real paper: 10.1007/s11146-022-09917-w is by Mamre and Sommervoll, not
     "Olaussen, Oust, Solstad", and the report's own self-check says every DOI was verified with no
     invention (sections 6, 8).
   - Nine tags cite a 404, 403 or unrelated page as evidence, past the brief's limit of five; the
     Section D table carries no tags at all (sections 1, 2).
   - The nearest prior work is described wrongly: the SimBuild paper is multi-label, not "forced
     single-label", and the "71% to 78%" range mixes in the electrical class (section 6).
   - Of the eleven US benchmark cities, Seattle, San Francisco and Philadelphia rest on dataset IDs
     that no fetch ever reached; Boston, Los Angeles and Austin are right on one file and unreached
     or wrong on the other (section 5).
   - Realtor.ca and Rentals.ca terms are summarised from pages that returned 403, not quoted; MPAC
     and BC Assessment "paid licence only" claims have no supporting page (sections 3, 4).
   - Process: ran in one session with T39 and T40, not a fresh one (section 9).
2. **Kept (confirmed by the checker's own re-fetch).**
   - Listing sites are **not usable**: Centris forbids "screen scraping, data mining" and Kijiji
     forbids "any robot, spider, scraper" (quotes confirmed verbatim); Realtor.ca and Rentals.ca
     forbid scraping too, per the checker's own fetch only (section 3).
   - Montreal assessment roll: fields `MATRICULE83`, `CIVIQUE_DEBUT`, `ANNEE_CONSTRUCTION`,
     `NOMBRE_LOGEMENT`, `UTILISATION`, CC BY, 76.3 MB. A join key (`L4`) and building age and
     unit count, no equipment text. Row counts not kept (section 4).
   - Quebec assessment roll, Calgary (`4ur7-wsgc`) and Edmonton (`qi6a-xuwt`) assessment files
     exist (section 4).
   - Ontario EWRB benchmarking file exists and covers multi-unit residential buildings; Montreal
     has no public per-building GHG disclosure file yet (section 4).
   - Toronto, Montreal and Vancouver 311 files are live with the logged field names and open
     licences (section 4).
   - US benchmark pairs confirmed both ways: New York City (permits `ipu4-2q9a`, Local Law 84
     `7x5e-2fxh`, from 2011) and Chicago (permits `ydr8-5enu`, benchmarking `xq83-jr8c`, from
     2014). Boston's BERDO exists under slugs the report never found (section 5).
   - Section C identities: Zhang, Hong, Luo 2020 (10.26868/25746308.2020.c083, full PDF read by
     the checker: BERT, San Francisco permits, multi-label, 74.75% mechanical, 78.75% building,
     84.06% plumbing, 71.25% electrical, 821,398 labelled permits; no abstention, no prediction
     sets, no French); Marasco and Kontokosta 2016; Wang et al. 2017; Chen and Hong 2018 (identity
     only, unread) (section 6).
3. **Effect on the subject.** The nearest prior work is now known and read: a BERT classifier on
   San Francisco permit text, labelling work type, not equipment, with no abstention and no French
   text. A7's claim to be first rests on equipment-level reading, abstention and French text, not
   on "reading permits with a language model" [INFERENCE]. No non-permit Canadian record fills the
   "no permit needed" gap with equipment text; listing text is closed by its terms. New York City
   is the one confirmed outside benchmark (permit text plus Local Law 84 per building, joined by
   BBL) [INFERENCE on the join].

Checked 2026-09-22 by a mechanical agent. Facts only, no judgement.

## 1. Log integrity

- `RT41_pages.log`: 216 data rows (all with 4 tab-separated fields; last row has no trailing newline, cosmetic only, no data loss). Timestamps strictly monotone, `2026-09-22T15:34:40` to `15:47:20`.
- Status codes: 200 = 138, 202 = 8 (all AWS WAF / DuckDuckGo bot-challenge interstitials, not real content), 403 = 6, 404 = 62, 429 = 1, 500 = 1. Non-200 rows = 78.
- Report uses 69 distinct `[Ln]` values, 427 tag instances total. Every referenced line number (6-215) exists in the log and its URL is topically plausible for the sentence it tags — no out-of-range or off-topic tag found.
- Line-number **mismatches (cited as if successful, but the log row is not usable evidence)**:
  - `[L6]` (report line 13, MPAC finding) tags log line 6, a 404 "Page Not Found".
  - `[L26]` (report line 20, Vancouver finding) tags log line 26, a 404 JSON error.
  - `[L29]` (report line 21) tags log line 29, a 404 JSON error.
  - `[L104]` (report lines 5, 230-236, Seattle card) tags log line 104, a 404 on `data.seattle.gov/api/views/76t5-jtzn`.
  - `[L109]` (report lines 5, 238-244, San Francisco card) tags log line 109, a 404 on `data.sfgov.org/api/views/i98e-dkgb`.
  - `[L113]` (report line 251, LA permit field) tags log line 113, a 404 on `data.lacity.org/api/views/b4tr-vdre`.
  - `[L127]`, `[L129]` (report lines 279-283, Philadelphia card) tag log lines that are both 404.
  - `[L211]` (report line 313, MPAC "not usable" claim) tags log line 211, the MPAC homepage (200) with no licensing text in it (checked below).
  - `[L213]` (report line 313, BC Assessment claim) tags log line 213, the BC Assessment "About Us" page (200) with no Data-Advice/bulk text in it.

## 2. Tag audit

- Section A: single paragraph, fully tagged; ends in `[L91, L93, L96, L98, L109]`-style citations throughout. No untagged factual sentence found.
- Section C table: all 5 rows carry a `[Ln]` tag in the last column.
- Section F (Item 1 and Item 2 cards, lines 62-292): every bullet ends with a `[Ln]` or `[INFERENCE]` tag. None missing.
- Section G bullets: tagged.
- **Section D (Gap and fit assessment) table, lines 44-48: zero tags anywhere in the 3 rows.** The "Is it unclaimed?" column makes a specific factual claim about Landscape row C1 ("C1 used basic BERT with forced single-label output, no abstention, no conformal sets") with no `[Ln]`/`[INFERENCE]` tag — and, per item 6 below, that claim is wrong (the paper used multi-label/multi-hot output, not single-label).
- `[INFERENCE]` is used correctly on genuinely inferential lines (e.g. the "Extra Canadian source" paragraph, lines 50-52); not over- or under-used elsewhere.

## 3. Listing sites (terms)

12 log rows touch the four listing domains (lines 47, 48, 49, 50, 197, 198, 201, 202, 207-210):

| Log line | URL | Status | Classification |
|---|---|---|---|
| 47 | centris.ca/en/terms-of-use | 200 | terms page (reached) |
| 48, 197 | realtor.ca/terms-of-use | 403 (both attempts) | terms page (never reached) |
| 49 | help.kijiji.ca/.../kijiji-terms-of-use | 200 | terms page (reached) |
| 50, 198 | rentals.ca/terms | 403 (both attempts) | terms page (never reached) |
| 201, 202 | DuckDuckGo search for realtor.ca/rentals.ca terms text | 202 (bot challenge) | search query, blocked, no results returned |
| 207, 209, 210 | realtor.ca, centris.ca, kijiji.ca robots.txt | 200 | robots.txt |
| 208 | rentals.ca robots.txt | 200 | robots.txt |

No listing-content or search-result page was fetched by either the original session or this check (compliant with the "no listing pages" constraint).

Re-fetch of each quoted terms page (this session, fresh curl, UA set):
- **Centris** (`https://www.centris.ca/en/terms-of-use`, redirects to `/en/terms-use-privacy-policy`): live text contains "Screen scraping," "data mining" or any other activity ... intended ... to collect, store, copy, reproduce, reorganize or manipulate the Content is also prohibited and constitutes a violation of copyright and these Terms." Report's quote (line 308) matches verbatim (only the curly quote marks around the two terms are dropped). **CONFIRMED.**
- **Kijiji** (`https://help.kijiji.ca/helpdesk/policies/kijiji-terms-of-use`): live text contains "use any robot, spider, scraper or other automated means to access Kijiji and collect content for any purpose without our express written permission." Report's quote (line 310) matches verbatim. **CONFIRMED.**
- **Realtor.ca**: original session got 403 both times and never saw the real terms text; Section G (line 309) nonetheless states a paraphrase ("Terms of use and technical safeguards strictly prohibit automated collection, crawlers, and scraping...") without quotation marks or a `[Ln]` pointing to reached terms content — this is a summary of an unreached page, not a quote, which master brief section 10 and section 7 both forbid ("quoted... never summarised"; "unreachable is COULD NOT OPEN, never a confirmation"). My fresh re-fetch this session did reach the page (200) and did find scraping-prohibition language ("web scraping", "data scraping" listed among prohibited uses) — the underlying claim is substantively true, but the original report could not have known that from what it logged.
- **Rentals.ca**: same pattern — both attempts 403, report paraphrases (line 311) instead of quoting a reached page. My re-fetch (200) found "3.16 Automated Data Extraction... prohibited" language, substantively supporting the claim, again not something the original session verified.
- Realtor.ca robots.txt (`[L207]`) reads `Allow: /` (crawling generally permitted; only sitemap indexing is blocked) — this does not itself support a "forbids automated collection" reading; the report does not lean on robots.txt for this claim, so no direct contradiction, but it is worth noting the robots.txt is not corroborating evidence.
- Both `not usable` outcomes for Realtor.ca and Rentals.ca are directionally confirmed by my live re-fetch, but were not confirmed by the report's own logged evidence at the time it was written.

## 4. Item 1 Canadian cards (re-fetch check)

| Source | Field names | MURB coverage | Quoted sentence | Verdict |
|---|---|---|---|---|
| Montreal assessment roll | `MATRICULE83`, `CIVIQUE_DEBUT`, `ANNEE_CONSTRUCTION`, `NOMBRE_LOGEMENT`, `UTILISATION` all confirmed present in live `package_show` JSON; file size 76,344,621 B = 76.3 MB confirmed exact | n/a (L4 only) | cc-by licence confirmed | MATCH (field names, size, licence); row count "500,000+" not present in CKAN metadata, untraceable |
| Quebec assessment roll | dataset confirmed live (200); field names not independently re-checked | n/a | — | MATCH (existence); row count "4.2 million" untraceable |
| MPAC | claim: "proprietary commercial products requiring paid licensing; no open bulk dataset" | — | none quoted | **MISMATCH** — cited log lines are a 404 (`L6`) and the MPAC homepage (`L211`); my re-fetch of the live homepage found no licensing/fee text (only a CSS class name "owlCarouselProductsInit" false-matched "Product") |
| BC Assessment | claim: "Data Advice paid contracts" restrict bulk access | — | none quoted | **MISMATCH** — cited log lines are the homepage (`L11`) and About-Us (`L213`); the actual Data-Advice URL 404s both in the original log and on re-fetch (redirects to a generic error page); my re-fetch of About-Us found no matching text |
| Calgary assessment (4ur7-wsgc) | dataset confirmed live via Socrata `api/views/4ur7-wsgc` | n/a | OGL-style terms | MATCH |
| Edmonton assessment (qi6a-xuwt) | dataset confirmed live | n/a | — | MATCH |
| Ontario EWRB | dataset confirmed live (16 resources found); MURB explicitly covered | Yes, stated | — | MATCH (existence, MURB coverage); "15,000+" row count untraceable to metadata |
| Toronto EWRB (not independently published) | — | — | — | plausible, not independently re-verified beyond status code |
| Montreal GHG by-law (no public per-building data yet) | — | — | — | supported by a real 0/4-result search (`L54`), reasonable |
| Vancouver / Calgary / Edmonton benchmarking absence | — | — | — | partly supported (Edmonton `L89` = 0 Socrata results, solid); Vancouver/Calgary partly rest on 404s from guessed URLs (`L26`, `L29`), weaker evidence |
| Toronto 311, Montreal 311, Vancouver 311 | field names as logged | — | OGL quoted | MATCH (all three fetched live with 200 and real JSON in original log) |

## 5. Item 2 US benchmark cards (re-fetch check)

| City | Permit file | Truth file | Join key exists in both? | Overlap years | Verdict |
|---|---|---|---|---|---|
| New York | `ipu4-2q9a` confirmed live (200, both original log and pattern-consistent) | `7x5e-2fxh` confirmed live | plausible (BBL/BIN standard NYC keys) | 2011-present, consistent | MATCH |
| Chicago | `ydr8-5enu` confirmed live | `xq83-jr8c` confirmed live | plausible (PIN standard) | 2014-present, consistent | MATCH |
| Boston | `approved-building-permits` confirmed live | BERDO **never found by the original session** (its two URL guesses, log lines 102-103, both 404; report gives no dataset ID) | unconfirmed | unconfirmed | **PARTIAL MISMATCH** — my re-fetch found BERDO genuinely exists under `berdo-reporting-2019` / `berdo-reporting-20201`, slugs the original session never located; report presents it as settled fact it never actually verified |
| Seattle | `76t5-jtzn` | `7735-vjrm`, `h7rm-fz6m` | — | — | **MISMATCH / unconfirmed** — every log line touching Seattle (104-108) is a 404; my re-fetch found `data.seattle.gov` unreachable (TLS connection reset) and 0 results in Socrata's own catalog search for this domain; no successful fetch, original or mine, ever confirmed these IDs or field names exist |
| San Francisco | `i98e-dkgb` | `j2j3-acqj` | — | — | **MISMATCH** — all 4 log lines (109-112) are 404; my re-fetch confirms both IDs return 404 on `data.sf.gov` (current domain) too — both IDs appear genuinely nonexistent |
| Los Angeles | `b4tr-vdre` | `9yda-i4ya` confirmed live | truth file only | — | **PARTIAL MISMATCH** — permit ID 404s in log and on re-fetch; live Socrata search of `data.lacity.org` finds different real permit datasets (`xnhu-aczu` "LA BUILD PERMITS", `u8xs-sfb6`, others), none matching the claimed ID or exact title |
| Austin | `3syk-w9eu` confirmed live | `v25e-qfpe` | permit file only | — | **PARTIAL MISMATCH** — truth file 404s in log (lines 119-120, not even cited by the report) and on re-fetch; a live Socrata catalog search for "energy" on `data.austintexas.gov` returns 0 results |
| Denver | slug confirmed live (redirects to a live ArcGIS Hub page under the same name) | same pattern | — | — | directionally MATCH on existence; field-level content not independently confirmed (JS-rendered page) |
| Washington DC | 200 in log with plausible titles | 200 in log with plausible titles | — | — | not independently re-verified beyond status/plausible title |
| Philadelphia | **404** in log (`descriptionofwork` claim) | **404** in log | — | — | **MISMATCH / unconfirmed** — both files 404 in the original log; my re-fetch of OpenDataPhilly's CKAN API also 404s (URL pattern appears outdated on the live site too); no fetch anywhere confirms the claimed dataset names or the `descriptionofwork` field |
| Minneapolis | 200 in log, ArcGIS Hub | 200 in log, ArcGIS Hub | — | — | directionally plausible, not field-verified |

Net: of 11 Item-2 cities, 2 (NYC, Chicago) are solidly confirmed both ways; 3 (Seattle, SF, Philadelphia) have no successful fetch anywhere supporting the specific IDs/fields claimed; 3 (Boston, LA, Austin) are confirmed on one file and unconfirmed/wrong-ID on the other; 3 (Denver, DC, Minneapolis) are existence-plausible but not field-verified.

## 6. Section C studies

- **Row 1** — Zhang, Hong, Luo (2020), DOI `10.26868/25746308.2020.c083`: CrossRef and OpenAlex both confirm title "Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History," first author Wanni Zhang. MATCH. The SimBuild PDF (`publications.ibpsa.org/.../simbuild2020_C083.pdf`, matches log line 161 which shows "PDF-1.6") was re-fetched and re-extracted in full this session (750,204 bytes, text extracted with `pdftotext`). Findings against the report's own claims:
  - The paper explicitly states labels are **"multi-hot" encoded** and the task is **"formulated as a multi-label classification problem"** (a permit can be tagged mechanical + electrical + building + plumbing simultaneously). The RT41 report (Section D line 46, Section E line 60) instead describes it as **"forced single-label output"** / "forced to make single-label predictions" — this is **incorrect**; the source paper is multi-label, not single-label.
  - Reported accuracy claim (Section E, line 60): "71% to 78% accuracy on mechanical and building work." Actual BERT test-set accuracies from Table 1: Mechanical = 74.75%, Building = 78.75%, Electrical = 71.25%, Plumbing = 84.06%. The 71% figure belongs to Electrical, not Mechanical — "71% to 78% ... mechanical and building" is imprecise; the correct range for those two categories alone is ~74.75%-78.75%.
  - "501,578 historical permits in SF" (Section C, Section H) is actually the count of just the **Building-type** permit subset in the paper ("San Francisco Building Permits: 501,578 ... completed permits"); the paper's actual total labeled-permit count is 821,398. The number itself is real (from the paper) but is presented as "historical permits in SF" when it is one work-type subset.
  - "did not output conformal prediction sets, did not allow abstention, did not evaluate French text" — confirmed correct; none of those terms appear anywhere in the extracted text.
- **Row 2** — cited as "Olaussen, J.O., Oust, A., Solstad, J.T. (2022)," DOI `10.1007/s11146-022-09917-w`: CrossRef confirms the **title** ("Coming of Age: Renovation Premiums in Housing Markets") and **abstract** substance (textual analysis of real estate listings to identify renovated dwellings, hedonic regression + random forest, Norwegian transactions) match what Section C row 2 describes. **However, CrossRef's actual author list is Mari O. Mamre and Dag Einar Sommervoll — not Olaussen, Oust, or Solstad, anywhere.** This is a genuine author fabrication attached to a real DOI/title, repeated in Section C (line 37), Section D (line 46 reference), and Section H entry 2 (line 332). It directly contradicts the report's own Section G answer 4 ("No [INFERENCE]. All DOIs were verified against CrossRef API records ... `10.1007/s11146-022-09917-w` ...") — that self-check is false for this row.
- **Row 3** — Marasco & Kontokosta (2016), DOI `10.1016/j.enbuild.2016.06.092`: CrossRef confirms title and first author "Marasco." MATCH.
- **Row 4** — Wang, Qian, Kats (2017), DOI `10.1371/journal.pone.0186314`: CrossRef confirms title "Structure of 311 service requests as a signature of urban location" and first author "Lingjing Wang." MATCH.
- **Row 5** — Chen & Hong (2018), DOI `10.1016/j.enbuild.2018.11.008`: CrossRef confirms title "Development of city buildings dataset for urban building energy modeling" and first author "Yixing Chen." MATCH.

## 7. Numbers

- Confirmed by re-fetch: Montreal assessment file size 76.3 MB (exact byte match), Montreal field names, Montreal CC-BY licence, NYC/Chicago dataset IDs, SimBuild's 501,578 and 821,398 figures (both real, one mislabeled — see item 6).
- **Untraceable to any logged page** (CKAN `package_show` / Socrata `api/views` metadata calls, as actually logged, carry no row-count field): Montreal "500,000+ parcels," Quebec "4.2 million units," Calgary "~3.5 million records," Edmonton "~3.2 million records," Ontario EWRB "15,000+ buildings annually," Toronto 311 "6 million+ records," Montreal 311 "3.5 million records" / "828 MB," Vancouver 311 "1.8 million records." These are plausible but not demonstrated by the cited log lines or by a metadata field this check could re-fetch and confirm.
- SimBuild "71% to 78%" figure: imprecise, see item 6.

## 8. Forbidden text

- Em dashes (U+2014): 0. En dashes (U+2013): 0. Compliant.
- Self-grading words: `grep -i "verified|definitive|comprehensive|confirmed"` finds 12 hits. Of these, 9 are the literal required template field label "Verified example of research use" (master brief section 10) or the response-template's own column header "DOI or arXiv ID (verified)" — compliant, not self-praise. Remaining 3: "definitive structural attributes" (line 52, describing assessment-roll data, mild editorializing, not self-praise); "comprehensive contractor description" (line 283, describing the Philadelphia `descriptionofwork` field — notable because that entire card's log citations are 404s, see item 5); and "All DOIs were verified against CrossRef API records" (line 327, Section G self-check) — this is a genuine self-assessment claim, and it is **false**, since DOI row 2's author names were fabricated despite the claimed CrossRef check (item 6).

## 9. Process facts

- Folder listing confirms only two RT41 files exist: `RT41_other_building_record_texts_and_benchmarks.md` and `RT41_pages.log` (plus the prompt `T41_other_building_record_texts_and_benchmarks.md`, which is the input, not an output). No `RT41...round1` or other variant exists.
- File timestamps are contiguous within one afternoon: `T39`/`RT39` outputs at 15:10-15:28, `T40`/`RT40` at 15:11-15:33, `T41`/`RT41` at 15:11-15:49 (log finishes 15:47:20, report saved 15:49) on 2026-09-22 — consistent with the three prompts having been run back-to-back in one session rather than three fresh ones, as stated.

## Summary counts

- Log rows: 216 (4/4 fields, monotone) — non-200: 78 (200=138, 202=8, 403=6, 404=62, 429=1, 500=1).
- `[Ln]` tags: 427 instances / 69 distinct lines, all in valid range; 9 tags cite a 404/403/no-match page as if it were supporting evidence (listed in item 1).
- Untagged section: Section D's 3-row table (0 tags).
- Listing-site log rows: 12; Centris and Kijiji terms quotes verbatim-confirmed; Realtor.ca and Rentals.ca terms were never reached by the original session (summarized, not quoted, from an unreached page).
- Item 1 cards: 2 clear mismatches (MPAC, BC Assessment claims unsupported by cited pages); most others MATCH on existence/fields, several row counts untraceable.
- Item 2 cards: 2/11 fully confirmed (NYC, Chicago); 3/11 unconfirmed by any fetch (Seattle, SF, Philadelphia); 3/11 partially wrong (Boston, LA, Austin — one file confirmed, one unconfirmed/wrong ID); 3/11 existence-plausible, not field-verified (Denver, DC, Minneapolis).
- Section C: 4/5 DOIs fully match title+author; 1/5 (row 2) has a real DOI/title but fabricated author names, contradicting the report's own "no invention" self-check.
- SimBuild PDF: re-read in full; report mischaracterizes its method as single-label (it is multi-label) and states an imprecise accuracy range.
- Forbidden text: 0 em/en dashes; 1 false self-assessment claim ("verified... No [INFERENCE]" contradicted by the DOI-author finding).
