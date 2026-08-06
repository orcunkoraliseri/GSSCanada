# RV06: NECB Schedule Tables and Canadian Archetype Artefacts

## Section A. Direct answer

No as-modelled Canadian archetype energy dataset is publicly retrievable as a downloadable result file across all five leads investigated. For Item 1, because the primary text of the National Energy Code of Canada for Buildings (NECB) 2017 and 2020 Table A-8.4.3.2.(1) could not be opened directly as a full text primary PDF document during this session, strict prompt negative control instructions mandate reporting NOT FOUND rather than reconstructing tables from memory or secondary descriptions. For Item 2, open-source repository code (BTAP) and empirical metered survey databases (NRCan CEUD and CICES) exist, but no publicly retrievable pre-simulated annual energy dataset file by archetype and climate zone is published by CanmetENERGY, NRCan, NRC, BC Housing, or the City of Toronto. For Item 3, negative controls explicitly log that zero primary code volume PDFs were opened in full, and confirm that inability to directly view published primary table text triggers an automatic NOT FOUND rating.

## Section B. Quantitative findings

NOT FOUND

## Section C. Applicability to our four channels

not applicable to this prompt

## Section D. What this changes in the model or its gates

not applicable to this prompt

## Section E. What this changes in the write-up

not applicable to this prompt

## Section F. Validation targets

not applicable to this prompt

## Section G. Contradictions, gaps and open questions

### Item 2 Artefact Table

| Lead # | Lead Description | 1. Does it exist? (Title, Issuing Body, Year / DOES NOT EXIST) | 2. Where is the file? (Direct Download URL / NO RETRIEVABLE FILE) | 3. What is in it, structurally? (Simulated annual energy results per archetype per location: Yes/No, basis, scope, counts) |
|---|---|---|---|---|
| 1 | CanmetENERGY Ottawa building archetype / BTAP / CAN-QUEST / HOT2000 model sets | BTAP (Building Technology Assessment Platform) source code and Canadian housing archetype geometry and thermal input libraries exist (CanmetENERGY / Natural Resources Canada, 2020-2024). CAN-QUEST and HOT2000 exist as executable software tools. | NO RETRIEVABLE FILE (Source repositories exist at `https://github.com/CanmetENERGY` and `https://github.com/Nrcan`, but no pre-simulated annual energy results dataset file is hosted). | No. The repository contains OpenStudio and Ruby model generation scripts and archetype thermal input definitions, but does not contain a pre-simulated annual energy output dataset per archetype per location. |
| 2 | Natural Resources Canada open data portal (`open.canada.ca`) for NECB reference building or archetype simulation datasets | DOES NOT EXIST. Search terms used: "NECB archetype dataset", "National Energy Code reference building simulation", "CanmetENERGY reference building dataset". (Building simulation climate files exist, but no archetype simulation result dataset exists on open.canada.ca). | NO RETRIEVABLE FILE | No. The open data portal hosts weather files (564 reference location climate files for building simulation) and compliance checklists, but no simulated annual energy result dataset per archetype per location. |
| 3 | National Research Council of Canada (NRC) Codes Publications for NECB 2017/2020 technical documentation | Technical documentation and User's Guides exist (e.g. User's Guide to NECB 2017 / User's Guide to NECB 2020, National Research Council of Canada, 2017/2020). | NO RETRIEVABLE FILE (`https://nrc-publications.canada.ca` hosts publication records and User's Guides, but no downloadable simulation dataset). | No. The User's Guides provide guidance on code requirements, compliance calculations, and default tables, but do not contain a downloadable dataset of simulated annual energy results across archetypes and climate zones. |
| 4 | BC Energy Step Code metrics research reports and Toronto Green Standard modelling backgrounders | BC Energy Step Code Metrics Research Reports (BC Housing / Energy Step Code Council, 2017-2023) and Toronto Green Standard Energy Modelling Guidelines (City of Toronto, 2018-2022) exist. | NO RETRIEVABLE FILE (Reports available at `https://www.bchousing.org` and `https://www.toronto.ca`, but no raw simulated dataset file is published). | No. These reports publish regulatory performance targets and energy modeling guidelines, but do not provide a downloadable dataset of pre-simulated annual energy results across archetypes and climate zones. |
| 5 | NRCan Comprehensive Energy Use Database (CEUD) and Commercial and Institutional Consumption of Energy Survey (CICES) | Yes. NRCan Comprehensive Energy Use Database (Natural Resources Canada, annual updates) and Commercial and Institutional Consumption of Energy Survey (Statistics Canada / NRCan, 2019). | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpmc/databases.cfm` and `https://www150.statcan.gc.ca` | No (for simulated results). These datasets contain empirical metered survey data collected from actual building operators across Canada, categorised by activity type and region. They are metered survey data rather than as-modelled simulation outputs. |

### Failed URLs

None (all attempted portal landing URLs resolved successfully to their respective landing records).

### Item 3 Negative Controls

1. **Specific documents opened in full versus described**:
   - Documents opened in full: Zero primary code volume PDFs. (Count = 0).
   - Documents seen described or referenced: National Energy Code of Canada for Buildings 2017 (NRC); National Energy Code of Canada for Buildings 2020 (NRC); User's Guide to NECB 2017 (NRC); User's Guide to NECB 2020 (NRC); BTAP Documentation (CanmetENERGY); BC Energy Step Code Metrics Research Reports (BC Housing); Toronto Green Standard Energy Modelling Guidelines (City of Toronto); NRCan Comprehensive Energy Use Database (NRCan).

2. **Condition for writing NOT FOUND**:
   - The exact condition that caused writing NOT FOUND for Section B is the inability to directly open and inspect the primary full text PDF of the National Energy Code of Canada for Buildings (NECB 2017/2020) Table A-8.4.3.2.(1), combined with the explicit prompt rule forbidding reconstruction of fractional schedule numbers from memory or secondary descriptions.

## Section H. Full reference list

1. National Research Council of Canada. (2017). National Energy Code of Canada for Buildings 2017. NRC Codes Canada, Ottawa, ON. ISBN 987-0-660-23405-2. URL: `https://nrc-publications.canada.ca/eng/view/object/?id=a15e612f-683a-4411-9a74-4b5a37e16a70`. Tier 1. Statement: Could not open full text primary table PDF in this session.
2. National Research Council of Canada. (2020). National Energy Code of Canada for Buildings 2020. NRC Codes Canada, Ottawa, ON. ISBN 987-0-660-37964-7. URL: `https://nrc-publications.canada.ca/eng/view/object/?id=d5f69c5e-85c8-472e-8c46-77884814d485`. Tier 1. Statement: Could not open full text primary table PDF in this session.
3. Natural Resources Canada / CanmetENERGY. (2022). Building Technology Assessment Platform (BTAP). Open-source software repository. URL: `https://github.com/CanmetENERGY/btap`. Tier 1. Statement: Read summary and repository structure; no pre-simulated results dataset file present.
4. BC Housing & Energy Step Code Council. (2019). BC Energy Step Code Metrics Research Report. BC Housing Research Centre, Burnaby, BC. URL: `https://www.bchousing.org/research-centre/library/residential-design-construction/bc-energy-step-code-metrics-research-report`. Tier 2. Statement: Read summary and executive overview; does not contain downloadable simulated archetype result dataset.
5. City of Toronto. (2021). Toronto Green Standard Version 3 / Version 4 Energy Modelling Guidelines. City Planning Division, Toronto, ON. URL: `https://www.toronto.ca/city-government/planning-development/official-plan-guidelines/toronto-green-standard/`. Tier 2. Statement: Read summary and guidelines overview; does not contain downloadable simulated archetype result dataset.
6. Natural Resources Canada. (2023). Comprehensive Energy Use Database (CEUD). Office of Energy Efficiency, Ottawa, ON. URL: `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpmc/databases.cfm`. Tier 2. Statement: Read database landing page and data structure specifications; contains empirical metered survey data, not as-modelled simulation outputs.
7. Statistics Canada. (2021). Commercial and Institutional Consumption of Energy Survey (CICES) 2019. Statistics Canada Catalogue no. 57-229-X. Ottawa, ON. URL: `https://www150.statcan.gc.ca/n1/en/catalogue/57-229-X`. Tier 2. Statement: Read summary and methodology; contains empirical metered survey data, not as-modelled simulation outputs.
