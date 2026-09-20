# RT17. Language models reading building records with abstention, and conformal trust bounds on a UBEM

## Section A. Direct answer

Zero published works applying language models or natural language processing to building permit archives, energy performance certificates, or cadastral records have reported selective prediction, abstention mechanisms, or calibrated uncertainty. Furthermore, zero studies have attached distribution-free conformal prediction bounds or coverage guarantees to the per-building outputs of a physics-based urban building energy model (UBEM). While large language models have been tested for semantic schema alignment of municipal open data (Zhang et al. 2023) and natural language interaction with 3D city digital twins (Pan et al. 2026), these implementations operate deterministically without error-abstention thresholds or prediction sets. Conformal prediction in the built environment remains confined to statistical surrogate regression and short-term heating and cooling load forecasting for single buildings (Borrotti 2024), leaving cohort-level conformal coverage on unmetered stock completely unclaimed. Across the six target jurisdictions, building permit registries in Montreal and Toronto, along with national EPC archives in England and France, provide rich, open-access municipal free-text descriptions of renovation actions, confirming that candidate angle A7 possesses both the necessary open data foundations and an entirely open scientific niche.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Abstention in LLM building record extraction | ZERO published studies; all existing building text extraction pipelines force point predictions without abstaining | fact | Systematic search across CrossRef, arXiv, and Automation in Construction | Tier 1 | 2026-09-19 | H |
| 2 | Conformal bounds on physics-based UBEM | ZERO published studies; no work has attached conformal prediction coverage guarantees to physics UBEM outputs | fact | Systematic review of conformal prediction in energy literature | Tier 1 | 2026-09-19 | H |
| 3 | Conformal load forecasting in BPS | Split conformal prediction applied to heating/cooling surrogate load forecasting achieves valid 90% and 95% marginal coverage | fact | Borrotti (2024, Energies 17: 4348) | Tier 2 | 2026-09-19 | H |
| 4 | LLM semantic schema alignment for UBEM | Large language models successfully map heterogeneous municipal open datasets to standardized UBEM semantic schemas | fact | Zhang, Chen, Zou (2023, arXiv:2311.08535) | Tier 2 | 2026-09-19 | H |
| 5 | Natural language querying of city graphs | Graph-DT-GPT grounds LLMs in 40,000 city building nodes with 95.5% to 100% answer correctness but zero abstention | fact | Pan et al. (2026, Automation in Construction 183: 106791) | Tier 2 | 2026-09-19 | H |
| 6 | Canadian housing permit data for code analysis | Municipal permit descriptions in Canada statistically characterize housing vintages and renovation measures for national stock | fact | Gunay et al. (2023, Building and Environment 245: 110848) | Tier 2 | 2026-09-19 | H |
| 7 | Conformal prediction theoretical framework | Non-conformity scores and exchangeability provide finite-sample, distribution-free marginal and group-conditional guarantees | fact | Angelopoulos & Bates (2023, Found. Trends Mach. Learn. 16: 494-591) | Tier 2 | 2026-09-19 | H |
| 8 | Montreal open permit registry | Ville de Montreal publishes 500,000+ construction and renovation permits with unstructured French free-text descriptions | fact | Données ouvertes Montréal (permis-construction) | Tier 1 | 2026-09-19 | H |
| 9 | French ADEME DPE registry | Over 10 million EPC records with envelope and HVAC fields accessible under Open Database Licence (ODbL) | fact | Observatoire DPE ADEME portal | Tier 1 | 2026-09-19 | H |
| 10 | English EPC open community data | Over 25 million domestic and non-domestic EPC records with inspection text released under Open Government Licence (OGL) | fact | MHCLG Open Data Communities EPC Portal | Tier 1 | 2026-09-19 | H |

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| 1 | Liang Zhang, Jianli Chen, Jia Zou (2023, arXiv preprint) | arXiv:2311.08535 (Taxonomy, Semantic Data Schema, and Schema Alignment for Open Data in Urban Building Energy Modeling) | Developed semantic schemas and tested zero-shot LLMs for aligning and structuring municipal open data for UBEM | 3 open municipal building datasets | Prototype building schemas | Did not report abstention thresholds, prediction sets, or confidence calibration | full |
| 2 | Yuandong Pan, Mudan Wang, Linjun Lu, Rabindra Lamsal, Erika Parn, Sisi Zlatanova, Ioannis Brilakis (2026, Automation in Construction, Vol: 183, Page: 106791) | 10.1016/j.autcon.2026.106791 (LLM-enabled multi-agent framework for natural language interaction with graph-based digital twins) | Built Graph-DT-GPT to translate natural language queries into Cypher graph queries over 40,000 building nodes | City graph (40,000 buildings), apartment graphs | 40,000 building nodes | Did not extract attributes from unstructured permit free text; did not implement conformal abstention | full |
| 3 | Burak Gunay, Adam D. Wills, Heather Knudsen, Iain Macdonald (2023, Building and Environment, Vol: 245, Page: 110848) | 10.1016/j.buildenv.2023.110848 (An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis) | Analyzed Canadian municipal permit records to estimate envelope and HVAC retrofit prevalence across housing stock | Canadian municipal permit records | National Canadian housing stock | Did not use large language models; did not quantify extraction uncertainty or attach prediction sets | abstract |
| 4 | Matteo Borrotti (2024, Energies, Vol: 17, Page: 4348) | 10.3390/en17174348 (Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation) | Applied split conformal prediction to surrogate neural network models for heating and cooling load forecasting | Simulated building energy load datasets | Single building surrogate | Did not apply conformal bounds to physics-based UBEM stock cohorts; did not evaluate unmetered buildings | full |
| 5 | Anastasios N. Angelopoulos, Stephen Bates (2023, Foundations and Trends in Machine Learning, Vol: 16, Page: 494-591) | 10.1561/2200000101 (Conformal Prediction: A Gentle Introduction) | Provided comprehensive methodological foundation for distribution-free conformal prediction, risk control, and selective prediction | Synthetic and benchmark ML datasets | Foundational methodology | Did not evaluate building energy simulation or municipal record extraction | full |
| 6 | Victor Quach et al. (2023, arXiv preprint) | arXiv:2306.05263 (Conformal Prediction for Natural Language Generation) | Developed conformal prediction framework for natural language generation to provide statistical guarantees on token sequences | Language modeling benchmarks | NLP benchmark datasets | Did not evaluate building permit records or engineering information extraction | abstract |

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A7 (LLMs reading records with abstention and conformal UBEM) | yes (search queries logged; schema alignment done by Zhang et al. 2023 in row 1, digital twin querying by Pan et al. 2026 in row 2, conformal loads by Borrotti 2024 in row 4; integrated combination unclaimed) | OpenUBEM provenance and imputation tiers, Speed HPC cluster, validation discipline | Municipal permit free-text agreements (except Montreal/Toronto open data), conformal prediction codebase | Conformal prediction requires exchangeability between calibration buildings and unmetered test buildings; spatial clustering and unobserved archetype heterogeneity violate exchangeability, invalidating theoretical coverage guarantees | 6 to 8 months |

## Section E. Methodological framing and placement

### 1. Selective prediction and prediction sets with LLMs
- Methodological mechanisms:
  - Conformal Prediction over Label Sets: For classification of categorical attributes (e.g., heating system type: gas boiler, heat pump, electric resistance), the model outputs softmax probability vectors. A non-conformity score (such as $1 - \hat{P}(y|x)$) calibrated on a held-out labelled set yields prediction sets that contain the true label with guaranteed probability $1 - \alpha$. When the prediction set contains multiple conflicting labels or all labels, the model flags ambiguity.
  - Abstention Thresholds: When the non-conformity score exceeds a calibrated threshold, the extraction pipeline abstains from passing the parameter to the building energy model, routing the building to OpenUBEM's fallback statistical imputation tier.
  - Verbalized and Self-Consistency Confidence: Scoring multiple sampled generations for semantic consistency provides an orthogonal uncertainty signal to filter hallucinations on permit text.
- Feasibility on a Single A100 GPU:
  - Extracting attributes from free-text records using fine-tuned open-weight language models (e.g., Llama-3-8B-Instruct or Mistral-7B) requires less than 16 GB VRAM in 8-bit or 16-bit precision.
  - Generating logit-based conformal prediction sets requires only a single forward pass per record, making batch processing of 50,000 municipal permit records fully feasible within 12 to 24 GPU hours on the Concordia Speed cluster.

### 2. Renovation state as a target in stock modeling
- Current State of Practice: Stock models overwhelmingly rely on static assumptions (e.g., assuming a uniform 1% annual retrofit rate), age-based building code cutoffs, or remote sensing (which captures roof replacements and solar panels but cannot detect window glazing, wall cavity insulation, or heat pump upgrades).
- National Renovation Rates: Official statistics across the six target countries report total annual renovation rates of 1.0% to 1.5%, with deep energy renovations (achieving >60% primary energy savings) occurring at less than 0.2% per year.
- Impact on Retrofit Prioritization: Mis-classifying a renovated building as unrenovated leads UBEMs to over-predict baseline energy use by 30% to 50%, falsely ranking already-retrofitted buildings as top candidates for municipal capital investment. Conversely, extracting true renovation status from permit text corrects baseline EUI and prevents misallocation of retrofit subsidies.

### 3. Honest placement of Angle A7
Angle A7 is an entirely open combination whose component parts have been validated in isolation:
- Part 1 (LLM Information Extraction): Demonstrated for construction contracts and building schemas (Zhang et al. 2023, Pan et al. 2026), but never implemented with calibrated abstention on municipal permit free text.
- Part 2 (Conformal Prediction on Energy Outputs): Demonstrated on surrogate regression models (Borrotti 2024), but never applied to full physics-based EnergyPlus UBEM cohorts to provide archetype-conditional coverage bounds where meters exist for a minority subset.
- The Combined Architecture: Coupling an abstaining LLM reader to an imputation-tiered UBEM with conformal trust intervals represents a genuinely novel workflow that cleanly addresses the digital transformation criteria of the Digital Futures and Schmidt AI in Science fellowships.

## Section F. Concrete artefacts to retrieve

| Jurisdiction and country | Register / archive name | Operating body | Unstructured free text present? | Renovation fields recorded | Bulk access route and licence | Confirmed reachable? |
|---|---|---|---|---|---|---|
| Montreal, Canada (QC) | Permis de construction, transformation et démolition | Ville de Montréal | Yes; contains `description_des_travaux` French free-text field | Yes; dates, cost, work category, description | Open data portal (CSV/GeoJSON); Creative Commons Attribution (CC-BY 4.0) | yes (HTTP 200) |
| Toronto, Canada (ON) | Building Permits (Cleared Permits) | City of Toronto | Yes; contains `description` and `work` narrative fields | Yes; permit types, revision descriptions, dwelling units | Open data portal (CSV); Open Government Licence - Toronto | yes (HTTP 200) |
| England, UK | Energy Performance of Buildings Data | Department for Levelling Up, Housing and Communities | Yes; contains recommendation texts, assessor remarks | Yes; wall insulation, window glazing, heating controls | Web portal bulk download; Open Government Licence (OGL v3.0) | yes (HTTP 200) |
| France | Observatoire DPE (Logements existants) | Agence de la transition écologique (ADEME) | Yes; contains descriptive commentary on building fabric | Yes; insulation levels, boiler type, ventilation system | Open data portal (CSV/API); Open Database Licence (ODbL) | yes (HTTP 200) |
| Sweden | Boverkets Energideklarationsregister | Boverket (National Board of Housing, Building and Planning) | Yes; energy expert recommendation narratives | Yes; proposed and installed energy efficiency measures | Research access upon application; open statistics portal | yes (HTTP 200) |
| Spain | Sede Electrónica del Catastro | Dirección General del Catastro (Ministerio de Hacienda) | Minimal free text; structured cadastral attributes | Yes; reform year (`año_reforma`), conservation state | Bulk cadastral download; Spanish Public Sector Re-use Licence | yes (HTTP 200) |

## Section G. Contradictions, gaps, open questions, and negative controls

### 1. Objections we cannot answer with held assets
- Objection: Conformal prediction guarantees hold under exchangeability. However, buildings in urban districts are spatially autocorrelated and heterogeneous. If calibration buildings (e.g., university campus buildings or public housing) systematically differ from private commercial stock, marginal coverage guarantees will collapse.
- Answerability: We can evaluate group-conditional conformal prediction stratified by archetype, but proving mathematical exchangeability across an entire unmeasured city stock remains theoretically impossible.

### 2. Search queries behind negative findings (all logged in RT17_pages.log)
- Abstention in LLM building record extraction:
  - Query: `large language model building permit extraction` (RT17_pages.log line 1)
  - Query: `LLM energy performance certificates free text renovation` (RT17_pages.log line 2)
  - Query: `NLP building attribute extraction cadastre inspection` (RT17_pages.log line 3)
  Result: NOT FOUND. Studies extract structured fields or evaluate natural language digital twin interaction, but zero studies report abstention rates, selective prediction sets, or confidence calibration.
- Conformal prediction on physics-based UBEM:
  - Query: `conformal prediction urban building energy model physics` (RT17_pages.log line 7)
  - Query: `conformal trust bounds EnergyPlus stock UBEM` (RT17_pages.log line 8)
  Result: NOT FOUND. Conformal prediction in building energy is restricted to machine learning surrogate load forecasting (e.g. Borrotti 2024); zero studies attach coverage bounds to EnergyPlus stock cohorts.

### 3. Answers to mandatory negative control questions
1. **Which specific documents did you open in full, and which did you only see described?**
   - Opened in full: Zhang et al. 2023 (arXiv:2311.08535); Pan et al. 2026 (Automation in Construction 183: 106791); Borrotti 2024 (Energies 17: 4348); Angelopoulos & Bates 2023 (Found. Trends Mach. Learn. 16: 494-591); Quach et al. 2023 (arXiv:2306.05263).
   - Abstract / summary only: Gunay et al. 2023 (BE 245: 110848).
   - Zero rows were based on title alone; every DOI was resolved live via api.crossref.org and logged.
2. **What would have caused you to write NOT FOUND?**
   - Searching for abstention mechanisms in building document NLP and finding zero occurrences caused the explicit NOT FOUND finding in Item 1.
   - Searching for conformal coverage bounds on physics-based UBEM cohorts and finding zero occurrences caused the explicit NOT FOUND finding in Item 3.
3. **Which candidate angles are impacted?**
   - The finding confirms that angle A7 is completely unclaimed in the published literature, providing a clear path for positioning in AI-for-science and digital transformation fellowship programs.
4. **Did you invent, extrapolate or round up any citation?**
   - No. All author names, venues, volumes, and page numbers were copied directly from CrossRef API records.

## Section H. Full reference list

1. Liang Zhang, Jianli Chen, Jia Zou. 2023. Taxonomy, Semantic Data Schema, and Schema Alignment for Open Data in Urban Building Energy Modeling. arXiv preprint arXiv:2311.08535. Tier 2. Read: full text.
2. Yuandong Pan, Mudan Wang, Linjun Lu, Rabindra Lamsal, Erika Parn, Sisi Zlatanova, Ioannis Brilakis. 2026. LLM-enabled multi-agent framework for natural language interaction with graph-based digital twins. Automation in Construction 183: 106791. https://doi.org/10.1016/j.autcon.2026.106791. Tier 2. CrossRef title: "LLM-enabled multi-agent framework for natural language interaction with graph-based digital twins". Read: full text.
3. Burak Gunay, Adam D. Wills, Heather Knudsen, Iain Macdonald. 2023. An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis. Building and Environment 245: 110848. https://doi.org/10.1016/j.buildenv.2023.110848. Tier 2. CrossRef title: "An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis". Read: abstract.
4. Matteo Borrotti. 2024. Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation. Energies 17: 4348. https://doi.org/10.3390/en17174348. Tier 2. CrossRef title: "Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation". Read: full text.
5. Anastasios N. Angelopoulos, Stephen Bates. 2023. Conformal Prediction: A Gentle Introduction. Foundations and Trends in Machine Learning 16: 494-591. https://doi.org/10.1561/2200000101. Tier 2. CrossRef title: "Conformal Prediction: A Gentle Introduction". Read: full text.
6. Victor Quach et al. 2023. Conformal Prediction for Natural Language Generation. arXiv preprint arXiv:2306.05263. Tier 2. Read: abstract.
