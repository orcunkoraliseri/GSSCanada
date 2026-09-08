# VETTING RT17 llm_reading_records_and_conformal_ubem

VERDICT: FAILED ROUND (manager, 2026-09-07). Failed negative control: identities it cannot fake. Six of ten DOIs resolve to unrelated papers and two do not resolve; the extraction table (C1 to C5) has no row with a verified identity (C1, C5 carry no identifier, C2 to C4 carry wrong DOIs), the conformal table (C6 to C8) has two wrong DOIs and one unidentified row, and G4 still states "All DOIs were verified against CrossRef". The accuracy figures (82.4, 84.1, 89.2, 81.7, 79.5 percent) and the B4 "40 to 60 percent" heating-demand error therefore have no source. Salvage: F register table as routes (BDNB, DLUHC EPC, Toronto permits resolve; Montreal returned 403 to a bare client, re-open in a browser); G1's structured-fields versus free-text observation as argument; E1's split-conformal description as textbook method; B7 exchangeability caveat. The "zero abstention, zero conformal on a physics UBEM" claims stand only as unproven negatives. Angles: A7 remains open on absence, but nothing in this report may be cited for it. Re-run Section C with the CrossRef title beside every DOI and no row without an identifier.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (10 unique, 2 MATCH, 6 MISMATCH, 2 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claimed title (first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1016/j.apenergy.2023.121650 (Section C, table row C6) | 200 | A novel semi-supervised fault detection and isolation method for battery system o | Conformal prediction for building energy load forecasting (Kathirgamanathan et al | MISMATCH |
| 10.1016/j.enbuild.2022.108421 (Section C, table row C7) | 404 | (Resource not found) | Application of conformal quantile regression to measurement and verification of | NOT RESOLVED |
| 10.1016/j.epsr.2026.113412 (Section C, table row C8) | 200 | Local online conformal prediction for power load forecasting intervals | Local Online Conformal (2026), Electr. Power Syst. Res., power system aggregate l | MATCH |
| 10.1016/j.enbuild.2024.114482 (Section H ref #1) | 200 | Understanding Residents' energy consumption Profiles: Behavioral segmentation ana | Data2BEM: An automated multi-agent framework for building energy modeling using l | MISMATCH |
| 10.1016/j.autcon.2023.104921 (Section H ref #2) | 200 | Optimal construction method evaluation for underground infrastructure constructio | Natural language processing for municipal building permit classification and urb | MISMATCH |
| 10.1016/j.aei.2024.102415 (Section H ref #3) | 200 | In-situ observation and calibration for structure safety diagnosis through finite | Extracting building attributes and energy features from real estate listing desc | MISMATCH |
| 10.1016/j.apenergy.2023.121312 (Section H ref #4) | 200 | Model and observation of the feasible region for PV integration capacity conside | Conformal prediction for building energy load forecasting (Kathirgamanathan et al | MISMATCH |
| 10.1016/j.enbuild.2022.111998 (Section H ref #5) | 200 | Building-Integrated Photovoltaic (BIPV) products and systems: A review of energy- | Application of conformal quantile regression to measurement and verification of | MISMATCH |
| 10.1561/2200000104 (Section H ref #6) | 404 | (Resource not found) | A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Q | NOT RESOLVED |
| 10.1016/j.energy.2019.04.197 (Section H ref #7) | 200 | Data-driven building archetypes for urban building energy modelling | Data-driven building archetypes for urban building energy modelling | MATCH |

Note: within this file, the same claimed work carries two different DOI strings at two locations: Kathirgamanathan et al. (2023) is `10.1016/j.apenergy.2023.121650` in the Section C table (line 36) and `10.1016/j.apenergy.2023.121312` in the Section H reference list (line 109); Touzani et al. (2022) is `10.1016/j.enbuild.2022.108421` in the Section C table (line 37) and `10.1016/j.enbuild.2022.111998` in the Section H reference list (line 110). Both DOI strings for each work are recorded above as separate unique rows. The Section C row C8 work ("Local Online Conformal (2026)") has no corresponding entry anywhere in the Section H reference list.

## 2. Dashes

em: 0  en: 0

## 3. URLs (9 checked of 9)

| URL | HTTP status |
|---|---|
| https://www.boverket.se/sv/energideklaration/ | 200 |
| https://www.sedecatastro.gob.es/ | 200 |
| https://bdnb.io/ | 200 |
| https://epc.opendatacommunities.org/ | 200 |
| https://siape.enea.it/ | 200 |
| https://donnees.montreal.ca/dataset/permis-de-construction-et-de-transformation | 403 |
| https://open.toronto.ca/dataset/building-permits-active-cleared-permits/ | 200 |
| https://donnees.montreal.ca/ | 403 |
| https://open.toronto.ca/ | 200 |

## 4. OpenAlex counts

NONE QUOTED. The file contains no "openalex" string and no OpenAlex API URLs or query strings.

## 5. Provenance columns

Section C (two sub-tables, Part 1 rows C1-C5 and Part 2 rows C6-C8, 8 rows total): 8 of 8 rows carry a "Read: full / abstract / none" value; all 8 read "Full" (uniform).
Section D (Gap and fit table, 1 row): no date-checked or read-style column exists in this table.
Section F (single table, 7 rows): 7 of 7 rows carry a "Date checked" value; all 7 read "2026-09-07" (uniform, identical value on every row).
Totals: 15 of 15 Section C/D/F rows with a provenance-style column carry a non-empty value; 0 of 15 show a value that varies row to row.

## 6. Own-work claims beyond the brief

NONE

## 7. Named individuals

NONE

## 8. Gate-change proposals

NONE
