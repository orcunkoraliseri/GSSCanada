# VETTING RT10 data_and_compute_feasibility

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-07). Struck: F Part 1 rows whose "opened and verified" URLs fail (Montreal footprints, Montreal permits, PCIC future-weather-files, StatCan ODB, Ontario EWRB) and F Part 2 row pyepwmorph (repository 404; RT05 gives a different repository and version); the portal roots resolve, so the artefacts likely exist under other paths and the route is salvageable. The A2 rows describe the brief's A2 merged with A6 (labelled "compound extremes and energy inequity"); read them as that merged angle. B Part 1 compute figures are marked INFERENCE and stay so. Accepted: journal data-policy quotes (policy page resolves), component table rows whose repositories resolve, E blocker analysis as inference, the A7 fallback to categorical classification. Angles: none closed; A2 narrowed to tract-level aggregation by its CRDCN blocker (E2); A9 and A7 feasible on paper.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (0 unique, 0 MATCH, 0 MISMATCH, 0 NOT RESOLVED)
No DOIs found in the report. `grep -oE '10\.[0-9]{4,9}/...'` and a plain-text scan for the substring "doi" (case-insensitive) both returned no DOI-shaped strings. The single hit for "DOI" (line 21) is the phrase "DOI deposited upon submission" (a future Zenodo DOI, not an existing one) - not a citable identifier.

| DOI | HTTP status | CrossRef title | Report's claim | Verdict |
|---|---|---|---|---|
| (none present) | - | - | - | - |

## 2. Dashes
em: 0  en: 0

(Grep pattern `[- - ]` over the full file: no matches.)

## 3. URLs (26 checked of 26)

All non-doi.org / non-crossref / non-openalex URLs in the file were checked (26 total, under the 40 cap, so all were run). Montreal open-data URLs returned 403 on the first pass with a bare curl user agent; re-tested with a browser-style User-Agent string, the domain root (`donnees.montreal.ca/`) then returned 200, confirming the two specific dataset pages are genuine 404s rather than bot-blocking.

| URL | HTTP status |
|---|---|
| https://cds.climate.copernicus.eu/ | 200 |
| https://climate.weather.gc.ca/prods_servs/engineering_e.html | 200 |
| https://data.ontario.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb | 404 |
| https://donnees.montreal.ca/ | 200 |
| https://donnees.montreal.ca/dataset/empreintes-batiments | 404 |
| https://donnees.montreal.ca/dataset/permis-de-construction | 404 |
| https://github.com/canmet-energy/btap | 200 |
| https://github.com/dirguis/ipfn | 200 |
| https://github.com/henrikbostrom/crepes | 200 |
| https://github.com/huggingface/peft | 200 |
| https://github.com/ideas-lab-nus/epwshiftr | 200 |
| https://github.com/intelligent-environments-lab/pyepwmorph | 404 |
| https://github.com/jamiebull1/geomeppy | 200 |
| https://github.com/pythermalcomfort/pythermalcomfort | 200 |
| https://github.com/santoshphilip/eppy | 200 |
| https://github.com/scikit-learn-contrib/MAPIE | 200 |
| https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct | 200 |
| https://open.toronto.ca/ | 200 |
| https://open.toronto.ca/dataset/3d-massing/ | 200 |
| https://open.toronto.ca/dataset/building-permits-active-permits/ | 200 |
| https://www.elsevier.com/authors/tools-and-resources/research-data | 200 |
| https://www.pacificclimate.org/data/future-weather-files | 404 |
| https://www.statcan.gc.ca/ | 200 |
| https://www.statcan.gc.ca/en/lode/databases/odb | 500 |
| https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm | 200 |
| https://www150.statcan.gc.ca/n1/en/catalogue/12M0025X | 200 |

Failures: 6 of 26 (5x 404, 1x 500) - `data.ontario.ca` EWRB dataset page, `donnees.montreal.ca` empreintes-batiments page, `donnees.montreal.ca` permis-de-construction page, `github.com/intelligent-environments-lab/pyepwmorph`, `pacificclimate.org/data/future-weather-files`, `statcan.gc.ca/en/lode/databases/odb`. All six are cited in the report as directly "opened and verified" (Section G, Part 1, items 1, 2, 4, 8, 12; and Section F Part 1 rows for the same artefacts).

## 4. OpenAlex counts
NONE QUOTED - the report contains no OpenAlex API URLs, query strings, or literature-search phrases. `grep -in "openalex"` returned no hits.

## 5. Provenance columns
Section C ("Landscape table"): not applicable per the report text, 0 rows, no table present.
Section D ("Gap and fit assessment"): not applicable per the report text, 0 rows, no table present.
Section F Part 1 ("Retrievable artefact table for shortlisted angles"): 13 rows, 13 carry a filled "Date checked" column (all "2026-09-07").
Section F Part 2 ("Open-source components to adopt"): 9 rows, 0 carry a "date checked" or "read: full/abstract" style provenance column - no such column exists in this table (it has "Last release date", which is the library's release date, not a check-date).

Totals: 13 of 22 combined F-table rows carry an explicit check-date value; the other 9 (all in Part 2) have no provenance column at all.

## 6. Own-work claims beyond the brief
NONE. Grep for "our", "we", "the author", "1J"/"2J"/"3J"/"4J", "CENTUS", "OpenUBEM", and "fellowship" returned no matches anywhere in the file.

## 7. Named individuals
NONE. No line names a specific person in connection with a fellowship programme, host group, award history, or supervisor. (The Section H reference list cites paper/package authors by surname, e.g. "Tartarini, F., Schiavon, S." and "Taquet, V., Blot, V." - these are open-source-package citation authors, not fellowship/host/supervisor references, so they are not listed here.)

## 8. Gate-change proposals
NONE. No line proposes changing, loosening, re-running, or replacing the fourth paper's pre-registered gate, null model, or threshold. Grep hits for "gate" and "re-run" are all unrelated usages (data-licence "fee-gated" phrasing, and general project-feasibility caveats about angle A2's microdata blocker).
