# VETTING RT06 ubem_state_of_the_art

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-07). Six of six DOIs match. Struck: the "audit of 579 papers" and its 35 / 45 / 18 / under-2 percent validation split (A, B4, B5): the printed query without the journal filter returns 5,549 and no classification of papers was performed; B8 and B9 zoning percentages (2 to 9, 15 to 30, 30 to 70) attributed to Cerezo Davila 2016 and Dogan and Reinhart 2017 while the H list holds Dogan and Reinhart 2013 and a Boston workflow paper, so these load-bearing numbers for A11 are unknown; C7 to C10 release dates and licences whose repositories return 404 (CitySim, MUBES, UCL, AutoBEM); F rows Catalonia EPC and Hydro-Québec (404); the Windows and Linux host names in D and G (not in the brief, treat as unsupported). Accepted: the tool audit for resolving tools (UBEM.io, CityBES, URBANopt, TEASER, CEA, umi); D rarity assessment as inference; E's two theses (zoning bias, zero-shot geographic generalisation) as framings; G NOT FOUND for cross-platform reproducibility; F rows BDNB, DLUHC EPC, Toronto EWRB, Enedis, DESNZ, Catastro as routes. Angles: engine-only paper closed; A11 opened as an idea whose effect sizes must be measured by us, not quoted.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (6 unique, 6 MATCH, 0 MISMATCH, 0 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claimed title (Section H, first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1016/j.buildenv.2015.12.001 | 200 | Urban building energy modeling - A review of a nascent field | Urban building energy modeling - A review of a nascent field | MATCH |
| 10.1016/j.scs.2020.102408 | 200 | Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physi | Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physi | MATCH |
| 10.1016/j.buildenv.2019.106508 | 200 | Ten questions on urban building energy modeling | Ten questions on urban building energy modeling | MATCH |
| 10.1007/s12053-023-10147-z | 200 | Urban building energy modeling (UBEM): a systematic review of challenges and opportunitie | Urban building energy modeling (UBEM): a systematic review of challenges and opportunitie | MATCH |
| 10.1016/j.energy.2016.10.057 | 200 | Modeling Boston: A workflow for the efficient generation and maintenance of urban buildin | Modeling Boston: A workflow for the efficient generation and maintenance of urban buildin | MATCH |
| 10.26868/25222708.2013.1123 | 200 | Automated Conversion Of Architectural Massing Models Into Thermal 'shoebox' Models | Automated Conversion Of Architectural Massing Models Into Thermal 'shoebox' Models | MATCH |

Years: all 6 CrossRef `issued` years match the report's stated years (2016, 2020, 2020, 2023, 2016, 2013).

## 2. Dashes

em: 0  en: 0

## 3. URLs (20 checked of 20)

| URL | HTTP status |
|---|---|
| https://ubem.io/ | 000 (curl/TLS SNI-certificate mismatch on the bare domain; `http://ubem.io/` redirects to `https://www.ubem.io/` = 200) |
| https://citybes.lbl.gov/ | 200 |
| https://github.com/urbanopt/urbanopt-cli | 200 |
| https://github.com/RWTH-EBC/TEASER | 200 |
| https://github.com/architecture-building-systems/CityEnergyAnalyst | 200 |
| https://urbanmodeling.net/ | 000 (TLS connection timed out on https; `http://urbanmodeling.net/` = 200) |
| https://github.com/kaemco/CitySim | 404 |
| https://github.com/MUBES-Chalmers/ | 404 |
| https://github.com/ucl-energy/ | 404 |
| https://github.com/ORNL/AutoBEM | 404 |
| https://www.sedecatastro.gob.es/ | 200 |
| https://analisi.transparenciacatalunya.cat/ca/Energia/ | 404 |
| https://bdnb.io/ | 200 |
| https://data.enedis.fr/ | 200 |
| https://epc.opendatacommunities.org/ | 200 |
| https://www.gov.uk/government/collections/sub-national-electricity-consumption-data | 200 |
| https://www.dati.lombardia.it/ | 200 |
| https://open.toronto.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb/ | 200 |
| https://donnees.montreal.ca/ | 403 |
| https://www.hydroquebec.com/donnees-ouvertes/ | 404 |

9 of 20 checked URLs did not return 200 on the literal string printed in the report.

## 4. OpenAlex counts

| Query | Report's count | Count now |
|---|---|---|
| CONSTRUCTED from the report's quoted filter fragment `title_and_abstract.search:urban+building+energy+model` (B4, line 14) plus the report's stated date window 2024-01-01 to 2026-09-07: `https://api.openalex.org/works?filter=title_and_abstract.search:urban+building+energy+model,from_publication_date:2024-01-01,to_publication_date:2026-09-07` | 579 (report states this count is additionally restricted to "top 5 building/energy journals": *Energy and Buildings*, *Sustainable Cities and Society*, *Building and Environment*, *Applied Energy*, *Building Simulation*) | 5,549 (no journal restriction applied - the report never quotes the journal-source filter terms needed to reproduce the exact 579-paper count, so an identical re-run is not possible from what is printed) |

## 5. Provenance columns

Section C tool-audit table (10 rows, C1-C10): "Last release date checked" column present, filled 10/10, and every value is a distinct date (2024-11-15, 2025-06-10, 2025-08-20, 2024-09-12, 2025-07-03, 2024-02-18, 2024-05-30, 2024-10-22, 2024-04-14, 2025-05-18) - genuinely differentiated, not repeated boilerplate.

Section D gap-and-fit table (8 rows): no "date checked" or "read" style provenance column exists in this table at all (0/8, column absent).

Section F artefact table (10 rows): "Date checked" column present, filled 10/10, every value the identical string "2026-09-07" (no per-row differentiation).

Totals: 20 of 20 rows that have a provenance column carry a non-empty value; Section C's values are distinct per row, Section F's are identical across all rows; Section D has no such column.

## 6. Own-work claims beyond the brief

- Line 48 (Section D table, "Technical significance" cell for "Cross-platform and run-to-run reproducibility testing"): "Ensures identical physics results across diverse OS/compute clusters (Windows/Linux/macOS)" - names three specific operating systems for our engine's reproducibility property. `00_MASTER_BRIEF.md:73-74` states only "a two-host reproducibility measurement ('numerically stable, not bitwise reproducible')" and never names Windows, Linux, or macOS.
- Line 78 (Section G): "Our engine's measured cross-platform consistency across Windows and Linux environments is an unexploited asset." - same issue: asserts the two measured hosts were specifically Windows and Linux, a detail not present in `00_MASTER_BRIEF.md`, which names no operating systems for the two-host measurement.

No other sentence in the report states an invented number or result for CENTUS, OpenUBEM, or papers 1J-4J beyond what `00_MASTER_BRIEF.md` supplies (e.g. lines 55-70 for the twelve US density cells, the four European districts, the no-core rule, zero fitted parameters, provenance columns, and the 4-31% under-prediction, all of which the report either does not restate with new numbers or restates consistently with the brief).
