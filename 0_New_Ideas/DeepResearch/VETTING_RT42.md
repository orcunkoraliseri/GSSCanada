# Vetting RT42: openness_of_the_permit_reading_climate_form

VERDICT: FAILED ROUND (manager, 2026-09-22). The report is not admitted as a table; the points
below are kept because the checker confirmed them at source.

Rule applied, as for RT38, RT40 and RT41: a row survives only if the checker confirmed it at its source.

1. **Why it fails.**
   - Two accuracy figures are not in their sources: Zhang 2020 is given "87.2% to 94.6%" (the
     paper's test accuracy is 71.25% to 84.06%), and Gunay 2023 is given "83% to 99% archetype
     matching" (the paper reports a 0 to 7 distance score, city means 2.0 to 2.8) (sections 4, 6).
   - The report's own self-check says every figure "reflects the retrieved text verbatim"; the two
     mismatches above contradict it (section 9).
   - Four Section F rows say "Confirmed reachable: yes" for pages never fetched (Montreal and
     Toronto portals) or whose own fetch returned 403 (SimBuild PDF, MDPI page) (summary).
   - The Gunay row contradicts itself on French (P3 "no", Language "English and French") (section 4).
   - Reference 9 (EPlus-LLM) names authors that CrossRef and OpenAlex do not carry; one log line is a
     hand-typed web-search paraphrase cited beside real fetches (sections 1, 4).
2. **Kept (confirmed by the checker's own re-fetch).**
   - Both known works were surfaced by real logged searches, so the search reached the right corner
     of the literature (section 3).
   - Gunay 2023, read in full: seven cities including Montreal; French handled by hard-coded
     keywords ("sous", "sol", "etage") inside association rules, no language model; no equipment,
     HVAC, heat pump or AC extraction; results weight building-code archetypes (sections 4, 5).
   - Zhang 2020, read in full: multi-label BERT on four work types, 821,398 permits, no abstention,
     no French, no energy model (section 6).
   - Borrotti 2024 (10.3390/en17174348) is real conformal prediction in building energy, but on
     simulated heating and cooling loads, not on text: the nearest work for the abstention part
     (section 4).
   - Geske and Voelker 2025 propagate refurbishment-state uncertainty through an urban energy model
     (City Energy Analyst, Germany); the city "Weimar" is not confirmed (section 4).
   - All 19 "found nothing" queries re-run by the checker returned only unrelated titles (section 7).
3. **Effect on the subject.**
   - The four-part combination stays unclaimed as far as these searches reach: no study found reads
     equipment or retrofit state from record text with a language model, abstains with stated
     coverage, reads French, and feeds an energy model [INFERENCE].
   - This is weaker than "open": the checker's own independent search was cut off by rate limits
     after 1 of 15 queries, and three SSRN or paywalled 2025 to 2026 papers (Pauling; Wu et al.
     Geo2UBEM, 10.2139/ssrn.7333555, an LLM agent inferring UBEM parameters; Jiang et al.) were
     never opened. Geo2UBEM is the one to read first; if it infers retrofit or system state from
     text, the "language model fills UBEM inputs" part is taken.
   - Novelty wording to use: retrofit and cooling state from French record text, with abstention at
     stated coverage, carried as uncertainty into a stock model with time-use occupancy. Not "first
     language model for UBEM inputs".

Checked 2026-09-22 by a mechanical agent. Facts only, no judgement.

## 1. Log integrity

- `RT42_pages.log`: 185 rows, all with exactly 4 tab-separated fields (`awk -F'\t' '{print NF}' | sort | uniq -c` gives `185  4`).
- Timestamps: strictly monotone, `2026-09-22T17:57:15` to `2026-09-22T18:01:31`. No out-of-order row found.
- Status code counts: 200 = 156, 403 = 5, 404 = 22, 406 = 2. Sum = 185, matches row count.
- Per-minute distribution: 17:57 = 46, 17:58 = 109, 17:59 = 25, 18:00 = 4, 18:01 = 1. A front-loaded burst of automated API calls tapering to a few slower calls at the end (the two arxiv 406 lines and the single search_web line); nothing that looks like a block of lines written after the fact.
- Non-fetch line: exactly one. Line 185: `2026-09-22T18:01:31  search_web:"Geo2UBEM: 3D Geometry Abstraction and LLM Multi-Agent Parameter Inference for Automated Urban Building Energy Modeling" abstract  200  It appears that the specific paper titled "Geo2UBEM..." does not exist as a widely indexed...`. Column 2 is not a URL; column 3 (`200`) is a hand-assigned status, not a real HTTP code, since this is a paraphrased tool-call result, not a fetch. This is the only such line in the file.
- Duplicate fetches: several DOIs and URLs are fetched 2-3 times across the session (Zhang 2020 DOI and its Semantic Scholar record: 3x each; Gunay 2023 DOI: 2x; Borrotti DOI: 3x; Geske/Voelker DOI: 3x; Jiang DOI: 3x; the two SSRN CrossRef DOIs: 2x each; the NRC accepted-manuscript PDF: 2x). All repeats keep the same monotone timestamp order (first pass 17:57-17:58, a second verification pass 17:58-17:59, a third pass for a few DOIs at 18:00), consistent with sequential re-verification sweeps rather than backfilled entries.

## 2. Tag audit

- Section A (lines 5-12, 8 sentences): every sentence ends with a `[Ln]` and/or `[INFERENCE]` tag. No untagged factual sentence.
- Section C (the 8-row landscape table, lines 28-37): the table format specified by prompt T42's "Item 1" instructions has no `[Ln]` column (columns are authors, year, venue, DOI, record type, city, model, extracted, P1-P4, abstention, language, accuracy, Read). No table cell carries an inline `[Ln]`/`[INFERENCE]` tag; sourcing for the row rests on the DOI and the Section H reference-list entry, not an inline tag.
- Section D (5 bullets, lines 43-51: P1, P2, P3, P4, Full Combination): every bullet ends with `[INFERENCE]`, and every individual sentence inside each bullet also carries its own `[Ln]`/`[INFERENCE]` tag. Fully compliant with the "Section D bullets must be marked [INFERENCE]" rule.
- Section G (bullets and the four numbered Q&A, lines 73-98): all factual bullets tagged; no untagged sentence found.
- Tags pointing to a non-200 or non-fetch line:
  - `L8` (403, IBPSA PDF forbidden), `L89` (404, Semantic Scholar), `L144` (404, Semantic Scholar), `L169` (404, Semantic Scholar), `L177` (403, SSRN), `L178` (403, SSRN): all six are used only in the Section G "Work that could not be opened" bullet (line 83), citing the failed fetch as evidence that the fetch failed. This is a legitimate use, not a case of a failed line being cited as if it supported a positive claim.
  - `L185` (the hand-typed, non-HTTP `search_web` line): cited in Section H, reference entry 7 (Geo2UBEM), as `[L143, L156, L185]`, alongside two real CrossRef fetches (`L143`, `L156`). It is not visually or textually distinguished from the two real fetches in that tag group.
  - No tag was found citing a 404/403/empty line as if it were positive supporting evidence for a claim (the pattern seen in RT41 was not found here).

## 3. Positive controls

- Gunay et al. 2023 (`10.1016/j.buildenv.2023.110848`): surfaced by the CrossRef free-text query at log line 1: `https://api.crossref.org/works?query=%22municipal%20housing%20permit%20data%22%20Gunay&rows=5`. Independently re-fetched this query: the #1 returned item is DOI `10.1016/j.buildenv.2023.110848`, title "An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis." Confirmed surfaced by a genuine search query, not a direct DOI lookup.
- Zhang, Hong, Luo 2020 (`10.26868/25746308.2020.c083`): surfaced by the CrossRef free-text query at log line 5: `https://api.crossref.org/works?query=Zhang%20Hong%20Luo%20SimBuild%202020%20building%20permit&rows=5`. Independently re-fetched this query: the #1 returned item is DOI `10.26868/25746308.2020.c083`, matching title. Confirmed surfaced by a genuine search query, not a direct DOI lookup.
- Both positive controls pass the prompt's specific requirement.

## 4. Section C rows

CrossRef identity check (title / first author / year / venue), independently re-fetched for all 8 DOIs plus the Section-H-only entry 9: all 9 DOIs resolve to the exact title, author list, year and venue the report states. No wrong-paper resolution found (unlike the RT41 pattern).

Row-by-row content check:

- **Row 1, Zhang/Hong/Luo 2020.** PDF independently re-fetched (750,204 bytes, matches size found in a prior vetting pass) and re-extracted with `pdftotext`. Confirmed: labels are "multi-hot" encoded ("the labels for the training dataset are 'multi-hot' encoded as 'is_mechanical', 'is_building', 'is_electrical', and 'is_plumbing'"), task is "formulated as a multi-label classification problem," 821,398 permits labeled, four categories (mechanical, electrical, plumbing, building) - all MATCH. Zero occurrences of "french," "abstention," "conformal," "reject option," or "selective classification" anywhere in the extracted text - MATCH with the report's P2/P3 = no. Reported accuracy in the report, "Test accuracy 87.2% to 94.6% across categories," does **not** match the paper's own test-set (`test_acc_bert`) figures, which read Building 78.75%, Electrical 71.25%, Mechanical 74.75%, Plumbing 84.06% (all four digit strings independently located in the extracted table text: 0.7875, 0.7125, 0.7475, 0.8406). The 87-94% band is closer to the paper's validation-accuracy or majority-class "default" rows, not the held-out test accuracy. **MISMATCH** on the accuracy figure.
- **Row 2, Gunay et al. 2023.** PDF independently re-fetched (2,301,048 bytes; a browser-style User-Agent got HTTP 410 from the entire `nrc-publications.canada.ca` domain, including its own homepage, at the time of this check; a plain `curl/8.0` User-Agent succeeded with 200 and a real PDF). Re-extracted with `pdftotext -layout`. Confirmed: "permit records from seven Canadian municipalities: Halifax, Nova Scotia; Montreal, Quebec; Ottawa and Toronto, Ontario; Edmonton and Calgary, Alberta; and Vancouver, British Columbia" - seven cities and Montreal's inclusion MATCH. French handling: "the term basement without the term no basement or bsmt (for Montreal French terms sous and sol)... the term storey (for Montreal etage)" - confirmed hardcoded keyword substitution within association-rule mining, not NLP or a language model - MATCHES the report's Section B row 4 claim exactly. Equipment/HVAC: "heat pump" appears three times in the extracted text, all inside the literature-review discussion of a different study (Papineau et al., on split vs. central heat pumps), never as something Gunay's own method extracts from permits; no occurrence of "HVAC," "furnace," "boiler," "air condition," or "heating fuel" outside that same review paragraph - MATCHES the report's claim that equipment, HVAC and retrofit states are omitted. Extracted attribute list: "dwelling type, floor and footprint area, foundation type, number of above-grade storeys, availability of an attached garage, and number of bedrooms" - matches the report's row-2 list verbatim. Stock-model feed: "enable assignment of realistic frequency/weighting factors for each building archetype" - MATCHES the report's Section B row 6 claim. Reported accuracy in the report, "83% to 99% archetype matching across cities," was **not found** anywhere in the extracted text; the paper instead reports a 0-to-7 archetype-match distance score, with per-city averages between 2.0 and 2.8 (no percentage match-rate of this form appears). **MISMATCH / unsupported figure.** Page numbers: this PDF's `pdftotext` extraction carries no recoverable page-number markers, so quotes above are given without page numbers.
  - Internal contradiction in the same table row: the P3 column reads "no," while the Language column for the identical row reads "English and French (keyword dictionaries)." The row asserts both that French text is not covered and that it is.
- **Row 3, Borrotti 2024.** CrossRef and an independently re-fetched Semantic Scholar abstract both confirm the paper is genuinely about conformal prediction applied to simulated heating/cooling load forecasting in Building Performance Simulation - this **is** conformal prediction in building energy, as the report states, but is regression/interval prediction on numeric loads, not text classification (consistent with the report's own P1-P4 = no row). The report's own log shows one attempt to open the live article page (`https://www.mdpi.com/1996-1073/17/17/4348`, log line 180) returning 403; consistent with the report's "Read: abstract" label.
- **Row 4, Geske and Voelker 2025.** CrossRef identity MATCH. The Semantic Scholar record for this DOI, independently re-fetched, has `"abstract": null`, so the report's "Read: abstract" tag citations (`L138, L139, L163`, all CrossRef or Semantic Scholar) do not actually carry abstract text in what was logged. OpenAlex (never fetched anywhere in this log) does carry a real abstract, independently retrieved for this check, confirming "a case study in Germany" using the City Energy Analyst software and a stochastic simulation algorithm to propagate refurbishment-state uncertainty - broadly consistent with the report's "Probabilistic archetype sampling... Sensitivity and error propagation reported" description, but the specific city "Weimar" named in the report's Section C row 4 appears in neither the OpenAlex abstract nor the CrossRef record (which carries no author affiliation field); this check could not independently confirm "Weimar" from any source it could reach.
- **Row 5, Zhang and Chen 2024.** CrossRef identity MATCH; about LLM-based interpretable HVAC control logic. All P1-P4 columns correctly marked "no" (background/nearest-neighbor row, not a P1-P4 crossover).
- **Row 6, Pauling 2026 (SSRN).** CrossRef identity MATCH. SSRN page independently re-confirmed to return 403 under both a browser User-Agent and a bare `curl` User-Agent - genuinely unreachable at the time of the original run and at the time of this check. TITLE ONLY label is consistent with that.
- **Row 7, "Geo2UBEM," Wu et al. 2026 (SSRN).** CrossRef DOI `10.2139/ssrn.7333555` independently re-fetched and confirmed to resolve to the exact title and author list ("WEI WU," "Ming Qu," "Zhe Wu," "Yongfei Li") the report gives - the DOI, title and author list are real and CrossRef-registered. What is true is that Semantic Scholar 404s on this DOI, and the hand-typed, non-HTTP `search_web` log line (line 185) states the title "does not exist as a widely indexed publication" - that line is the agent's own paraphrase of a web-search result, not an HTTP fetch failure, and it sits in tension with the CrossRef record obtained in the same session. SSRN's own page independently re-confirmed 403 (Cloudflare) under both User-Agents used in this check. The report's TITLE ONLY label is defensible (no abstract or full text was ever opened by any method), but Section H cites the non-fetch line `L185` as supporting evidence next to two real fetches without flagging it as a different kind of evidence.
- **Row 8, Jiang et al. 2025.** CrossRef identity MATCH; TITLE ONLY, not independently re-opened by this check (paywalled *Energy* journal article).
- **Section H entry 9, "Jia, W., Zhang, L. (2026), EPlus-LLM" (not given a Section C row).** CrossRef DOI `10.63044/w26jia171` independently re-fetched: the CrossRef `author` field for this record is an **empty array**; OpenAlex likewise lists no authorships for this DOI. The names "Jia, W., Zhang, L." attributed to this entry could not be confirmed from any source this check could reach, in tension with the master brief's rule that authors are copied from the CrossRef record, never from memory.

## 5. Gunay 2023 claims

Covered inline in item 4's Row 2 discussion (independently re-fetched and re-read full text): seven cities confirmed by name (Halifax, Montreal, Ottawa, Toronto, Edmonton, Calgary, Vancouver); Montreal is included; French terms "sous" and "sol" (sous-sol, basement) and "etage" (storey) are handled by hardcoded keyword substitution inside association-rule mining, not by any NLP model or language model; the paper's own extraction never covers equipment, HVAC, heating fuel, heat pumps or air conditioning (its three "heat pump" mentions are all inside a literature-review paragraph about a different study); results feed a stock model by weighting NBC archetype frequencies. Page numbers could not be recovered from this PDF's text extraction (no page-number markers survive `pdftotext`), so the quotes above are given without page numbers.

## 6. Zhang 2020 claims

Covered inline in item 4's Row 1 discussion (independently re-fetched and re-read full text, PDF confirmed 750,204 bytes): multi-label / "multi-hot" encoding confirmed verbatim; 821,398 labeled permits confirmed; four work-type classes (mechanical, electrical, plumbing, building) confirmed; no equipment-level labels beyond these four broad categories; zero occurrences of "abstention," "conformal," "reject option" or "selective classification"; zero occurrences of "french"; the paper does not feed an energy model or EnergyPlus simulation (no such term appears in the extracted text). All of these match the report's own characterization. Only the specific accuracy figure quoted by the report ("87.2% to 94.6%") is a mismatch against the paper's own test-set numbers (71.25% to 84.06%), as detailed in item 4.

## 7. "Not found" claims

Section G lists 8 grouped "not found" bullets covering P1 through P4 and the full combination, each with its own log line(s). Independently re-fetched all 19 of the underlying CrossRef free-text queries cited across those bullets (`"building permit" "heat pump"`, `"building permit" "air conditioning"`, `"permit text" retrofit`, `NLP "building permits" retrofit`, `"conformal prediction" "building energy"`, `"conformal prediction" "building stock"`, `"conformal prediction" "building permit"`, `"conformal prediction" "urban building energy"`, `"selective classification" "building"`, `"reject option" "building energy"`, `"permis de construction" "fouille de texte"`, `"permis de construction" NLP`, `"permis de construire" "traitement automatique"`, `"permis de construction" "apprentissage automatique"`, `Montreal "permis de construction" text`, `"permis de batir" "pompe a chaleur"`, `"permis de construire" "pompe a chaleur"`, `"building permit" "urban building energy"`, `"building permits" EnergyPlus`, `UBEM "building permit"`, `"permis de construction" Montreal`, `"permis de construire" renovation "langage naturel"`). For every one of these, the top-5 returned titles are unrelated noise (general HVAC/legal/urbanism/zoning documents, forecasting papers, classification-scheme documents), none combining a language model or text classifier with permit-derived equipment or retrofit state. This is consistent with the report's "these queries found nothing" framing; none of the report's "not found" bullets says "no such work exists." The CrossRef `total-results` counts logged (in the millions) are the size of CrossRef's fuzzy-matched corpus, not a phrase-exact hit count; the log's ~200-character snippet is consumed by JSON boilerplate before it reaches any `title` field, so the log by itself gives no evidence of what a query actually returned - only that a 200 response was received. That gap was filled here by live re-fetching, not by the log.

## 8. Independent spot search

Attempted the 15 planned queries via OpenAlex and Semantic Scholar. OpenAlex returned, on the very first call, `"error":"Rate limit exceeded"` (shared, unauthenticated network-wide daily budget, reset stated as ~100 minutes away) - no OpenAlex query in this check returned results. Semantic Scholar's unauthenticated search endpoint returned one successful result set before switching to HTTP 429 ("Too Many Requests") for every subsequent call in this check:
- `"conformal prediction" "building energy"` (Semantic Scholar, successful): top 5 = Borrotti 2024 (`10.3390/en17174348`, the report's own positive control for P2), an arXiv scrap-material conformal-classification paper, a smart-building-energy-forecasting uncertainty paper, an energy-storage-arbitrage conformal-risk paper, and a drug-property conformal-prediction paper. None of the remaining four touch building permits, retrofit/cooling state text extraction, or French text.
- All other 14 planned queries (`large language model building permit`; `large language model urban building energy model`; `LLM building attributes archetype`; `text classification energy audit retrofit`; `selective classification building`; `abstention building classification`; `permis de construire apprentissage automatique`; `language model retrofit extraction building record`; `conformal prediction urban building energy model`; `reject option building energy classification`; `heat pump detection permit text`; `building permit natural language processing extraction`; `LLM building stock modeling`; `French building permit machine learning`) returned no results before hitting the rate limit; none could be completed in this check. This is a limitation of this check's own environment budget, not a finding about the report.

## 9. Forbidden text

- Em dashes (U+2014): 0. En dashes (U+2013): 0. Compliant.
- Self-grading words: `verified` - 0 occurrences. `definitive` - 0. `comprehensive` - 0. `completely` - 6 occurrences (lines 5, 12, 45 x2, 47, 49), all used to describe the state of the literature ("completely open and unclaimed," "completely outside text processing," "P2 is completely unclaimed"), not a claim about the report's own quality. `confirmed` - 2 occurrences: the response-template's own column header "Confirmed reachable?" (line 62, a required template field, not self-praise), and "confirmed from Semantic Scholar" (Section G, line 73), a factual description of where metadata came from.
- One self-check claim in Section G answer 4 (line 98): "Every cited paper traces to an exact resolving CrossRef DOI logged at the time of fetch, and every metric or finding reflects the retrieved text verbatim." Per item 4 above, this is not accurate for two rows: the Zhang 2020 accuracy figure (87.2%-94.6%, not found in the source table) and the Gunay 2023 accuracy figure (83%-99% archetype matching, not found in the source text).

## 10. Process facts

- File timestamps: `RT42_pages.log` last modified 2026-09-22 18:01:31 (local), `RT42_openness_of_the_permit_reading_climate_form.md` last modified 2026-09-22 18:02:17 (local) - a 46-second gap, consistent with the log being finished before the report was written, as required.
- `T42_openness_of_the_permit_reading_climate_form.md` (the prompt) is timestamped 16:47:10, over an hour before the RT42 log's first row (17:57:15).
- No other file in the `DeepResearch` folder was modified in the 17:50-18:10 window on 2026-09-22; only `RT42_pages.log` and `RT42_openness_of_the_permit_reading_climate_form.md` fall inside it. This differs from the RT41 pattern (RT39, RT40 and RT41 all show file activity inside one shared afternoon session); RT42's own files show no such overlap with another RT number.

## Summary counts

- Log: 185 rows, 4/4 fields, timestamps monotone, 1 non-fetch line (`search_web`, line 185). Status codes: 200 = 156, 403 = 5, 404 = 22, 406 = 2.
- `[Ln]`/`[INFERENCE]` tags: 58 distinct line numbers used, range L1-L185, all within the log's 185 rows. 6 tag uses point at 404/403 lines, all inside the legitimate "could not be opened" bullet. 1 tag use (`L185`) points at the non-fetch `search_web` line, used undistinguished from real fetches in a Section H entry.
- Section C: 8/8 table rows plus the 1 reference-list-only entry (9 total) have their DOI identity (title/author/year/venue) independently confirmed against CrossRef. 2/9 rows carry an accuracy or statistic not found in the source text when independently re-read (Zhang 2020's "87.2%-94.6%"; Gunay 2023's "83%-99% archetype matching"). 1 row (Gunay, row 2) is internally self-contradictory on whether French text is covered (P3 = no vs. Language = "English and French"). 1 reference (entry 9, EPlus-LLM) has author names that are not confirmable from CrossRef (empty author field) or OpenAlex.
- Section F: of 6 artefact rows, 2 ("Confirmed reachable? yes") cite log lines that never fetched the target URL at all (Montreal and Toronto permit portals, both tagged to unrelated CrossRef literature-search calls); 2 more ("Confirmed reachable? yes") cite API-metadata fetch lines rather than a fetch of the target URL itself, while the log's own actual attempt to open that same target URL (IBPSA SimBuild PDF, Energies/MDPI article page) returned 403 in both cases; 1 (NRC Gunay manuscript) is correctly evidenced by two real 200 fetches of that exact URL; 1 (MAPIE GitHub) is honestly marked `[INFERENCE]` rather than falsely claimed as fetched.
- Positive controls: both Gunay 2023 and Zhang 2020 independently confirmed surfaced via a genuine logged search query (not a direct DOI lookup), as the prompt requires.
- Independent spot search: 1 of 15 planned OpenAlex/Semantic Scholar queries returned results before rate-limiting from both services' unauthenticated tiers; no missed P1-P4 crossover work found in that one result set.
- Forbidden text: 0 em/en dashes. No self-praise vocabulary beyond one self-check claim (Section G answer 4, "every metric or finding reflects the retrieved text verbatim") that is contradicted by the two accuracy-figure mismatches found in item 4.
- Process: only RT42's own report and log files fall inside its 17:50-18:10 run window; no overlap found with another RT-numbered session, unlike RT41.
