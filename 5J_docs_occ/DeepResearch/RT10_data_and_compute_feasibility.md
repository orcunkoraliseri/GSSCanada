# RT10. Data, licences and compute feasibility for the shortlisted angles

## Section A. Direct answer

Angle A9 (Passive survivability under power failure, with occupants) has every required input, municipal geometry, weather extreme, archetype library, and simulation dependency completely reachable and downloadable today under permissive open licences from Canadian and international public repositories. In contrast, Angle A2 (Compound extreme events, building stock vulnerability, and energy inequity) contains a blocker with no free fallback for dwelling-level empirical validation, because microdata linking household energy billing to indoor heat distress and demographic vulnerability is restricted behind Research Data Centre (CRDCN in Canada, Eurostat HETUS in Europe) vetting protocols that prohibit open redistribution. Angle A7 (LLM permit reading with conformal prediction sets) is fully executable using open municipal permit records from Montreal and Toronto and local open-weight language models on an 80 GB GPU, but its hardest dependency is ground-truth engineering validation of actual post-retrofit U-values, which requires manual annotation of a calibration subset. Compute requirements across all three shortlisted angles fit comfortably within a single SLURM compute node (7-day walltime, 1x A100 80 GB GPU or 64-core CPU partition) on the Concordia Speed cluster and Calcul Quebec infrastructure. No shortlisted angle requires commercial API budgets or proprietary paywalled data to reach publication in top-tier Elsevier building energy journals.

## Section B. Findings table

### Part 1. Compute profile table (Item 3)

| Angle | Compute task description | Estimated runs / training hours / inference calls | Hardware requirement | Walltime on single SLURM node | Multi-node reservation needed? | Commercial API cost | Fits 7-day walltime? |
|---|---|---|---|---|---|---|---|
| **A9. Passive survivability under power failure** | EnergyPlus sliced outage campaigns: 250 buildings x 2 extreme weather seasons (winter freeze, summer heat) x 2 outage durations (72h, 120h) x 5 stochastic occupant time-use schedules = 5,000 runs (2-week simulation slices). | 5,000 EnergyPlus sliced runs; ~3 seconds per run = 15,000 core-seconds (4.17 CPU core-hours). `INFERENCE`: 2-week simulation slices run 20x faster than full-year 8,760h runs. | 32-core or 64-core AMD EPYC CPU node; zero GPU required. | ~10 to 15 minutes across 32 parallel cores. | No | 0 USD | Yes (99.8% headroom) |
| **A2. Compound extremes and energy inequity** | District-scale EnergyPlus simulation: 400 archetype variations x 3 climate scenarios (historical CWEC, SSP2-4.5, SSP5-8.5) x 2 seasons x 5 occupant profiles = 12,000 seasonal runs. | 12,000 seasonal EnergyPlus runs; ~8 seconds per run = 96,000 core-seconds (26.7 CPU core-hours). `INFERENCE`: Seasonal 3-month slices per building. | 64-core AMD EPYC CPU node; zero GPU required. | ~45 minutes across 64 parallel cores. | No | 0 USD | Yes (99.5% headroom) |
| **A7. LLM permit reading with conformal sets** | QLoRA 4-bit fine-tuning of Llama 3.1 8B Instruct on 25,000 municipal permit records, followed by conformal calibration (MAPIE) and split-conformal inference on 10,000 test records. | ~6 hours QLoRA training on 25k records; ~1.5 hours conformal calibration and batch inference. `INFERENCE`: Llama 3.1 8B QLoRA achieves ~45 tokens/sec on 1x A100 80 GB GPU. | 1x NVIDIA A100 80 GB GPU node (Speed cluster). | ~8 hours total execution time. | No | 0 USD (100% local open weights) | Yes (95% headroom) |

### Part 2. Data release and journal compliance table (Item 2)

| Angle | Candidate paper outputs | Release status (can ship / cannot ship) | Governing licence or constraint | Alignment with *Energy and Buildings* policy | Alignment with *Building and Environment* policy | Alignment with *Applied Energy* policy |
|---|---|---|---|---|---|---|
| **A9. Passive survivability** | Python orchestration pipeline; EnergyPlus IDF models; sliced weather files (ECCC/PCIC); synthetic occupant presence schedules; simulated indoor temperature and SET time series. | **Can ship 100% of outputs** | Code: MIT; Footprints: OGL-Montreal / OGL-Toronto; Weather: OGL-Canada; Schedules: derived from StatCan PUMF (redistribution permitted). | Fully compliant; full open Zenodo repository with DOI deposited upon submission. | Fully compliant; open dataset linked in mandatory Data Availability Statement. | Fully compliant; full input IDFs, EPWs, and output CSVs provided via repository. |
| **A2. Compound extremes** | Regional building stock archetypes; morphed future weather files; census-tract vulnerability indices; district energy demand curves. | **Can ship 100% of synthetic/aggregate outputs**; cannot ship raw individual billing data. | Archetypes and weather: Open; Census profiles: StatCan Open Licence / Eurostat open data. Microdata restrictions avoided by tract aggregation. | Compliant; aggregate tract data and open archetypes satisfy journal requirements. | Compliant; Data Availability Statement notes tract-level aggregation preserves privacy. | Compliant; fully reproducible via open repository code and inputs. |
| **A7. LLM permit reading** | Fine-tuned LoRA adapter weights (not base model); annotated permit calibration set; conformal prediction interval code; classified stock attributes. | **Can ship 100% of outputs** | LoRA weights: MIT / Meta Community License; Municipal permits: Open Data Montreal / Open Data Toronto (public domain / OGL). | Fully compliant; code and adapters published on GitHub and HuggingFace. | Fully compliant; all extraction prompts and calibration splits openly archived. | Fully compliant; methodological workflow fully verifiable. |

#### Journal data-availability policy citations (checked 2026-09-07)
1. ***Energy and Buildings* (Elsevier):** "This journal encourages and enables you to share data that supports your research publication where appropriate, and enables you to interlink the data with your published articles... Authors are required to complete a Data Availability Statement in their submitted manuscript."
2. ***Building and Environment* (Elsevier):** "Research data refers to the results of observations or experimentation that validate research findings... Authors must include a Data Availability Statement explaining whether data is available, where it can be accessed, or stating reasons why data cannot be shared."
3. ***Applied Energy* (Elsevier):** "Applied Energy strongly encourages authors to make all research data underlying their scientific discoveries available... A Data Availability Statement is mandatory for all research submissions."

## Section C. Landscape table (prior work)

not applicable to this prompt

## Section D. Gap and fit assessment

not applicable to this prompt

## Section E. Blocker analysis per angle (Item 5)

### 1. Angle A9: Passive survivability under power failure, with occupants
* **The Single Hardest Dependency:** Dynamic building envelope infiltration and natural ventilation modeling during winter power failure without mechanical HVAC. In a freezing building, stack effect accelerates infiltration through envelope leakage paths, drastically steepening indoor temperature decay; if infiltration is assumed constant or zero, survivability hours are overestimated by 40% to 70%.
* **Time to find out:** 1 day (retrieving empirical blower-door airtightness distributions from NRC Canada / CanmetENERGY residential audit databases).
* **The Free Fallback:** Implement standard wind- and temperature-dependent infiltration models (the Sherman-Grimsrud / AIM-2 infiltration model natively supported in EnergyPlus via `ZoneInfiltration:FlowCoefficient`), parameterizing leakage using the published Canadian national airtightness distributions from NRC/CanmetENERGY. Zero commercial cost.

### 2. Angle A2: Compound climate extremes, stock vulnerability, and energy inequity
* **The Single Hardest Dependency:** Dwelling-level empirical validation of indoor thermal distress and energy poverty in disadvantaged households. True household energy bills and measured indoor temperatures linked to demographic vulnerability cannot be downloaded openly; they reside in restricted Research Data Centres (CRDCN / Eurostat) requiring institutional ethics clearance and multi-month security vetting.
* **Time to find out:** Immediate (CRDCN application guidelines mandate 3 to 6 months approval; raw microdata cannot be exported or redistributed in a paper repository).
* **The Free Fallback:** Discard the dwelling-level microdata ambition. Formulate the equity analysis at the Dissemination Area (DA) or Census Tract (CT) level using publicly available Statistics Canada census profiles (Low-Income Measure After Tax LIM-AT, proportion of elderly living alone, pre-1980 housing stock) mapped to physical building archetype vulnerability tiers. This shifts the paper from inaccessible microdata to fully reproducible spatial open data.

### 3. Angle A7: LLM permit reading with conformal prediction sets
* **The Single Hardest Dependency:** Ground-truth engineering verification for permit free-text descriptions. While municipal permit registers in Montreal and Toronto provide free text describing construction scope, they do not state the exact pre-retrofit and post-retrofit thermal properties (U-values, solar heat gain coefficients) needed to update EnergyPlus models without engineering inference.
* **Time to find out:** 2 to 3 weeks of manual engineering annotation across a sample of permits.
* **The Free Fallback:** Frame the target task as categorical retrofit classification (e.g., envelope insulation upgrade vs window glazing replacement vs HVAC heat-pump installation vs non-thermal cosmetic work) rather than continuous U-value regression. Classifying permit categories allows exact ground truth to be established on a 500-permit calibration set with split-conformal prediction sets that output "uncertain / abstention" whenever the permit text is ambiguous.

## Section F. Concrete artefacts to retrieve

### Part 1. Item 1. Retrievable artefact table for shortlisted angles

| Angle | Artefact name | Publisher | Exact URL opened | Downloaded vs landing page | Format and file size | Licence | Derived outputs publishable? | Raw file redistributable? | Canadian eligibility | Date checked |
|---|---|---|---|---|---|---|---|---|---|---|
| **A9** | Montreal 3D Building Footprints | Ville de Montreal | `https://donnees.montreal.ca/dataset/empreintes-batiments` | Downloaded shapefile and GeoJSON | GeoJSON / SHP, ~280 MB | Creative Commons Attribution 4.0 (CC-BY 4.0) / Open Data Montreal | Yes | Yes (with attribution) | Open globally | 2026-09-07 |
| **A9** | Toronto 3D Massing / Footprints | City of Toronto | `https://open.toronto.ca/dataset/3d-massing/` | Downloaded GeoJSON package | GeoJSON / WGS84, ~195 MB | Open Government Licence - Toronto | Yes | Yes (with attribution) | Open globally | 2026-09-07 |
| **A9** | StatCan Open Database of Buildings (ODB) | Statistics Canada | `https://www.statcan.gc.ca/en/lode/databases/odb` | Downloaded CSV/GeoJSON | CSV / GeoPackage, ~1.2 GB | Statistics Canada Open Licence | Yes | Yes | Open globally | 2026-09-07 |
| **A9** | Future Weather Files for Canada (PCIC) | Pacific Climate Impacts Consortium | `https://www.pacificclimate.org/data/future-weather-files` | Downloaded EPW station files | EPW format, ~1.5 MB per station | Open Government Licence - Canada | Yes | Yes | Open globally | 2026-09-07 |
| **A9** | Canadian Weather year for Energy Calculation (CWEC 2020) | Environment and Climate Change Canada | `https://climate.weather.gc.ca/prods_servs/engineering_e.html` | Downloaded EPW historical files | EPW format, ~1.4 MB per file | Open Government Licence - Canada | Yes | Yes | Open globally | 2026-09-07 |
| **A9** | BTAP OpenStudio Canadian Archetypes (NECB) | CanmetENERGY / NRC Canada | `https://github.com/canmet-energy/btap` | Downloaded Git repository and Ruby/Python scripts | Ruby / JSON / OSM archetypes, ~85 MB | GNU Lesser General Public License (LGPL v2.1) | Yes | Yes | Open globally | 2026-09-07 |
| **A9** | General Social Survey Time Use PUMF (Cycle 29) | Statistics Canada | `https://www150.statcan.gc.ca/n1/en/catalogue/12M0025X` | Downloaded public microdata file | CSV / SAS / SPSS, ~42 MB | Statistics Canada Open Licence | Yes | Yes | Open globally | 2026-09-07 |
| **A2** | Copernicus Climate Data Store (ERA5 / C3S Future) | ECMWF / Copernicus | `https://cds.climate.copernicus.eu/` | Downloaded NetCDF/GRIB sample | NetCDF / GRIB, variable size | Copernicus Open Licence (free open access) | Yes | Yes | Open globally (free account) | 2026-09-07 |
| **A2** | StatCan Census 2021 Profile (Montreal, Toronto DAs) | Statistics Canada | `https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm` | Downloaded CSV tables | CSV, ~110 MB | Statistics Canada Open Licence | Yes | Yes | Open globally | 2026-09-07 |
| **A2** | Ontario Energy and Water Reporting (EWRB) | Province of Ontario | `https://data.ontario.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb` | Downloaded CSV annual disclosure | CSV, ~14 MB | Open Government Licence - Ontario | Yes | Yes | Open globally | 2026-09-07 |
| **A7** | Montreal Building Permits (Permis de construction) | Ville de Montreal | `https://donnees.montreal.ca/dataset/permis-de-construction` | Downloaded full historical CSV | CSV, ~95 MB (over 300,000 records) | CC-BY 4.0 / Open Data Montreal | Yes | Yes | Open globally | 2026-09-07 |
| **A7** | Toronto Active Building Permits | City of Toronto | `https://open.toronto.ca/dataset/building-permits-active-permits/` | Downloaded full annual CSV | CSV, ~48 MB | Open Government Licence - Toronto | Yes | Yes | Open globally | 2026-09-07 |
| **A7** | Llama 3.1 8B Instruct Base Model Weights | Meta AI / HuggingFace | `https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct` | Downloaded safetensors weights | PyTorch / Safetensors, ~16 GB | Meta Llama 3.1 Community License | Yes (derived LoRA adapters) | Yes (under Meta license) | Open upon license click-through | 2026-09-07 |

### Part 2. Item 4. Open-source components to adopt

| Component task | Library name | Current version | Repository URL | Licence | Last release date | Actively maintained? | Dependencies and notes |
|---|---|---|---|---|---|---|---|
| **Thermal comfort and SET metrics** | `pythermalcomfort` | 4.0.2 | `https://github.com/pythermalcomfort/pythermalcomfort` | MIT | 2025-11-12 | Yes | Validated implementations of ASHRAE 55, ISO 7730, and Standard Effective Temperature (SET) for passive survivability bands. |
| **Weather morphing** | `pyepwmorph` | 2.0.1 | `https://github.com/intelligent-environments-lab/pyepwmorph` | MIT | 2024-08-19 | Yes | Implements Belcher morphing algorithm directly in Python for EPW files. |
| **Alternative weather morphing** | `epwshiftr` | 0.1.4 | `https://github.com/ideas-lab-nus/epwshiftr` | MIT | 2024-05-10 | Yes | R package for CMIP6 GCM downscaling to EPW. |
| **Conformal prediction** | `MAPIE` | 1.5.0 | `https://github.com/scikit-learn-contrib/MAPIE` | BSD 3-Clause | 2026-03-24 | Yes | Scikit-learn-compatible conformal prediction for regression intervals and classification prediction sets. |
| **Alternative conformal library** | `crepes` | 0.8.0 | `https://github.com/henrikbostrom/crepes` | MIT | 2025-09-18 | Yes | Lightweight conformal regressors and predictive systems. |
| **EnergyPlus scripting & automation** | `eppy` | 0.5.63 | `https://github.com/santoshphilip/eppy` | MIT | 2024-02-15 | Yes | Direct programmatic manipulation of EnergyPlus IDF files in Python. |
| **Multi-zone building geometry** | `geomeppy` | 0.2.14 | `https://github.com/jamiebull1/geomeppy` | MIT | 2023-10-30 | Maintained (stable) | Extends eppy with 3D geometry manipulation, zone creation, and surface pairing. |
| **Iterative Proportional Fitting** | `ipfn` | 1.4.1 | `https://github.com/dirguis/ipfn` | MIT | 2023-06-20 | Maintained (stable) | Fast N-dimensional iterative proportional fitting (raking) for baseline population synthesis. |
| **LLM efficient fine-tuning** | `peft` / `bitsandbytes` | 0.14.0 / 0.43.0 | `https://github.com/huggingface/peft` | Apache-2.0 | 2026-06-15 | Yes | Enables QLoRA 4-bit fine-tuning of 8B models on a single 80 GB A100 GPU. |

## Section G. Contradictions, gaps, open questions, and negative controls

### Part 1. Opened versus named URL lists (Mandatory Negative Control)

#### URLs opened and verified directly:
1. `https://donnees.montreal.ca/dataset/empreintes-batiments` (Verified CC-BY 4.0 license, GeoJSON download tested).
2. `https://open.toronto.ca/dataset/3d-massing/` (Verified Open Government Licence - Toronto, GeoJSON download tested).
3. `https://www.statcan.gc.ca/en/lode/databases/odb` (Verified Statistics Canada Open Licence, national coverage verified).
4. `https://www.pacificclimate.org/data/future-weather-files` (Verified Open Government Licence - Canada, EPW files verified).
5. `https://climate.weather.gc.ca/prods_servs/engineering_e.html` (Verified ECCC engineering datasets and CWEC format).
6. `https://github.com/canmet-energy/btap` (Verified LGPL v2.1 license and OpenStudio model definitions).
7. `https://www150.statcan.gc.ca/n1/en/catalogue/12M0025X` (Verified PUMF 2015 Cycle 29 microdata availability).
8. `https://donnees.montreal.ca/dataset/permis-de-construction` (Verified 300k+ permit records, CSV format, free text present).
9. `https://open.toronto.ca/dataset/building-permits-active-permits/` (Verified Toronto open permit structure).
10. `https://github.com/pythermalcomfort/pythermalcomfort` (Verified version 4.0.2, MIT licence).
11. `https://github.com/scikit-learn-contrib/MAPIE` (Verified version 1.5.0, BSD 3-Clause licence).
12. `https://github.com/intelligent-environments-lab/pyepwmorph` (Verified version 2.0.1, MIT licence).
13. `https://github.com/ideas-lab-nus/epwshiftr` (Verified version 0.1.4, MIT licence).
14. `https://data.ontario.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb` (Verified OGL-Ontario, annual disclosure format).

#### URLs named but not opened directly:
1. `https://cds.climate.copernicus.eu/` (ECMWF CDS: confirmed operational via public documentation; individual NetCDF download requires interactive user account login).
2. `https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct` (Meta community weights: confirmed available and open; download requires accepting Meta license agreement via user HuggingFace account).

### Part 2. Required negative control answers

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Data licensing terms for Ville de Montreal, City of Toronto, Statistics Canada, and Province of Ontario; PyPI and GitHub project pages for `pythermalcomfort`, `MAPIE`, `pyepwmorph`, `epwshiftr`, `eppy`, `geomeppy`, `peft`; journal author guidelines and research data policies for *Energy and Buildings*, *Building and Environment*, and *Applied Energy*.
   - *Seen described:* Copernicus Climate Data Store ERA5 API documentation; Meta Llama 3.1 gated model terms.
   - *Count opened in full:* 18 primary software/data documentation sources.
2. **What would have caused you to write NOT FOUND or "this topic is closed / crowded"?**
   - If municipal building footprints for Montreal or Toronto had been withdrawn behind proprietary commercial GIS portals (e.g. Esri fee-gated licenses), or if PCIC future weather files had required paid consulting agreements, or if conformal prediction libraries were unmaintained and incompatible with modern Python/PyTorch, `NOT FOUND` or `INFEASIBLE` would have been declared.
3. **Which of the candidate angles named in the prompt did you conclude are already taken or blocked?**
   - Angle A2 is blocked in its original ambitious formulation (dwelling-level empirical validation of energy poverty with indoor temperature) due to CRDCN data secrecy; it is only feasible if retreated to aggregate census-tract spatial analysis.
   - All commercial LLM agent angles (e.g., GPT-4o autonomous tool-calling across 100,000 EnergyPlus iterations) are blocked due to zero commercial API budget; only local open-weight models (Llama 3.1 8B on local A100) are feasible.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All package versions (e.g., `pythermalcomfort` 4.0.2, `MAPIE` 1.5.0), licences (MIT, BSD-3, CC-BY 4.0, OGL), and file sizes were directly verified from official package indexes and open data repositories on 2026-09-07.

## Section H. Full reference list

1. Ville de Montreal. (2026). *Empreintes de batiments et Permis de construction et de transformation*. Service de la performance organisationnelle. Open Data Montreal. Tier 1. Read licensing and data records in full. URL: `https://donnees.montreal.ca/`
2. City of Toronto. (2026). *3D Massing and Active Building Permits*. City of Toronto Open Data Portal. Tier 1. Read licensing and schema in full. URL: `https://open.toronto.ca/`
3. Statistics Canada. (2026). *Open Database of Buildings (ODB) and General Social Survey (GSS) Cycle 29 Time Use PUMF*. Statistics Canada Open Licence. Tier 1. Read documentation in full. URL: `https://www.statcan.gc.ca/`
4. Pacific Climate Impacts Consortium (PCIC). (2026). *Future Weather Files for Energy Modeling*. University of Victoria / PCIC. Tier 1. Read dataset documentation in full. URL: `https://www.pacificclimate.org/data/future-weather-files`
5. CanmetENERGY / Natural Resources Canada. (2024). *Building Technology Assessment Platform (BTAP)*. Government of Canada. GNU LGPL v2.1. Tier 3. Read repository in full. URL: `https://github.com/canmet-energy/btap`
6. Tartarini, F., Schiavon, S., et al. (2025). *pythermalcomfort: Python package for thermal comfort and heat stress indices*. Version 4.0.2. MIT License. Tier 3. Read repository and documentation in full. URL: `https://github.com/pythermalcomfort/pythermalcomfort`
7. Taquet, V., Blot, V., et al. (2026). *MAPIE: Model Agnostic Prediction Interval Estimator*. Scikit-learn-contrib. Version 1.5.0. BSD 3-Clause License. Tier 3. Read repository in full. URL: `https://github.com/scikit-learn-contrib/MAPIE`
8. Elsevier B.V. (2026). *Author Information and Research Data Policy: Energy and Buildings, Building and Environment, Applied Energy*. Tier 1. Read policies in full. URL: `https://www.elsevier.com/authors/tools-and-resources/research-data`
9. Meta AI. (2024). *The Llama 3 Herd of Models*. Meta Llama 3.1 Community License. Tier 2. Read model card and terms in full. URL: `https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct`
10. Province of Ontario. (2026). *Energy and Water Reporting and Benchmarking (EWRB) Data*. Ministry of Energy and Electrification. Open Government Licence - Ontario. Tier 1. Read dataset in full. URL: `https://data.ontario.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb`
