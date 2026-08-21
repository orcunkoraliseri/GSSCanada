# RL24. Which Published Sources Can We Actually Reach, Open and Use, for Census Marginals and for Building Archetype Parameters?

## Section A. Direct answer

For our three target countries (Spain, United Kingdom, Italy), no single published census table cross-tabulates all four demographic strata (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`) to our exact category definitions and age floor of 11. In the Eurostat Census Hub (2011 round), Hypercubes such as 1.4 and 5.1 provide 5-way cross-tabulations (`GEO` x `SEX` x `HST.H` x `CAS.L` x `AGE.M`), but they collapse homemakers and other inactive persons into a combined category (`CAS.L.2.4`) and group ages into 5-year bins starting at age 10 (`AGE.M.1.3: 10-14 years`), failing to isolate our exact age floor of 11. For the United Kingdom, 2011 census data is accessible through Eurostat and Nomis (under the Open Government Licence v3.0), but the UK is entirely absent from the Eurostat 2021 census round following Brexit; furthermore, the 2021 UK census exercise was fragmented across three separate statistical offices (ONS for England and Wales in 2021, NISRA for Northern Ireland in 2021, and NRS for Scotland delayed to 2022). For annual intercensal demographic series covering our exact survey waves (Spain 2009-2010, Italy 2013-2014, UK 2014-2015), national Labour Force Surveys (Spain EPA, Italy RCFL, UK APS/LFS) and annual population registers provide open, unrounded marginals, though economic status is universally restricted to ages 15+ (Italy, Eurostat) or 16+ (Spain, UK). For archetype parameters, TABULA and EPISCOPE distribute downloadable Excel workbooks (`tabula-values.xlsx`, `tabula-calculator.xlsx`) and national brochures under open academic research terms (Institut Wohnen und Umwelt / IEE), containing component U-values, envelope areas, and HVAC efficiencies across defined national construction periods (Spain: 6 periods; UK: 8 periods; Italy: 8 periods), but they provide no dynamic schedules, setpoint profiles, or EnergyPlus `.idf` models.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | 4-way cross-tabulated census marginals matching exact strata | Exactly zero single published tables exist per country that cross-tabulate our four demographic fields (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`) to our exact category boundaries and age floor of 11. | Fact | Eurostat Census Hub 2011/2021; INEbase; ISTAT; ONS Nomis [R1, R2, R3, R4] | Tier 1 | 2026-08-20 | H |
| B2 | Eurostat Census Hub 2011 hypercube depth | Regulation (EU) No 519/2010 defines Hypercubes 1.4, 2.4, 3.4, 4.4, 5.1 combining `GEO.L` x `SEX` x `HST.H` x `CAS.L` x `AGE.M` for Spain, Italy, and UK; however, `CAS.L` merges homemakers with other inactive, and `AGE.M` uses 10-14. | Fact | Commission Regulation (EU) No 519/2010; Regulation (EC) No 1201/2009 [R1, R5] | Tier 1 | 2026-08-20 | H |
| B3 | Separation of homemaker vs other inactive | Eurostat mandatory classification (`CAS.L`) collapses them into `2.4 Homemakers and others`; national LFS surveys (Spain EPA, Italy RCFL, UK LFS/Nomis KS601) explicitly publish separate counts for homemakers and other inactive. | Fact | Regulation (EC) No 1201/2009; INE EPA; ISTAT RCFL; ONS Nomis [R3, R4, R5, R6] | Tier 1 | 2026-08-20 | H |
| B4 | Minimum age floor in published economic status tables | No official source tabulates economic status below age 15 (Eurostat, ISTAT) or age 16 (Spain INE, UK ONS). Respondents aged 11-14 (or 11-15) are legally defined as children / full-time students / below working age. | Fact | Regulation (EC) No 1201/2009; INE; ONS; ISTAT [R1, R3, R4, R6] | Tier 1 | 2026-08-20 | H |
| B5 | UK inclusion in Eurostat Census rounds | YES in Census 2011 (transmitted under Regulation (EC) No 763/2008, rounded to base 5 for confidentiality); NO in Census 2021 (UK exited EU on 31 Jan 2020 and is absent from Eurostat 2021 Census Hub). | Fact | Eurostat Census Hub 2011/2021 metadata; ONS Dissemination Notices [R1, R7] | Tier 1 | 2026-08-20 | H |
| B6 | Fragmentation of UK 2021/2022 Census | No single native UK-wide 2021 census table exists. England and Wales was fielded in March 2021 (ONS), Northern Ireland in March 2021 (NISRA), and Scotland was postponed to March 2022 (NRS due to COVID-19). | Fact | ONS / NRS / NISRA 2021/2022 Census Joint Statements [R7, R8] | Tier 1 | 2026-08-20 | H |
| B7 | Intercensal annual alternatives for Spain (2009-10) | INE Padrón Continuo (population by single year of age and sex) and Encuesta de Población Activa (EPA, Op 293) provide quarterly/annual marginals under Law 37/2007 open re-use licence via Tempus3 JSON API. | Fact | INEbase / INE Tempus3 API [R3] | Tier 1 | 2026-08-20 | H |
| B8 | Intercensal annual alternatives for Italy (2013-14) | ISTAT Bilancio Demografico (population 1 Jan by single year of age and sex) and Rilevazione sulle Forze di Lavoro (RCFL) provide annual series under IODL 2.0 / CC BY 3.0 via I.Stat / IstatData SDMX. | Fact | ISTAT SIQual / I.Stat / IstatData [R6, R9] | Tier 1 | 2026-08-20 | H |
| B9 | Intercensal annual alternatives for UK (2014-15) | ONS Mid-Year Population Estimates (MYE) and Annual Population Survey (APS) / Labour Force Survey (LFS) provide annual marginals under Open Government Licence v3.0 via Nomis REST API. | Fact | Nomis Web / ONS API [R4] | Tier 1 | 2026-08-20 | H |
| B10 | TABULA / EPISCOPE downloadable data files | Downloadable Excel workbooks (`tabula-values.xlsx`, `tabula-calculator.xlsx`) and country PDF brochures are hosted at `https://episcope.eu/communication/download/` and `https://episcope.eu/building-typology/`. | Fact | EPISCOPE / TABULA Project Documentation [R10, R11] | Tier 1 | 2026-08-20 | H |
| B11 | TABULA web tool data endpoint status | The TABULA WebTool (`webtool.building-typology.eu`) uses an undocumented JSON/XML back-end; however, the complete underlying relational dataset is distributed as an open static workbook (`tabula-values.xlsx`). | Fact | TABULA WebTool Architecture Audit; IWU Documentation [R10, R11] | Tier 1 | 2026-08-20 | H |
| B12 | TABULA terms of use and redistribution | Open access for scientific research and education under Intelligent Energy Europe (IEE) programme rules (IWU Darmstadt / project consortium). Redistribution of derived parameter tables is permitted with attribution. | Fact | IWU Darmstadt / TABULA Final Report / IEE Project Terms [R11, R12] | Tier 1 | 2026-08-20 | H |
| B13 | Spanish TABULA construction period bands | Exactly 6 periods: `ES.01: < 1900`, `ES.02: 1901-1936`, `ES.03: 1937-1959`, `ES.04: 1960-1979`, `ES.05: 1980-2006 (NBE-CT-79)`, `ES.06: >= 2007 (CTE 2006)`. | Fact | TABULA `tabula-values.xlsx` sheet `Tab.ConstrYearClass`; IVE Brochure [R10, R13] | Tier 1 | 2026-08-20 | H |
| B14 | UK (Great Britain) TABULA period bands | Exactly 8 periods: `GB.01: < 1919`, `GB.02: 1919-1944`, `GB.03: 1945-1964`, `GB.04: 1965-1980`, `GB.05: 1981-1990`, `GB.06: 1991-2003`, `GB.07: 2004-2009`, `GB.08: >= 2010`. | Fact | TABULA `tabula-values.xlsx` sheet `Tab.ConstrYearClass`; BRE Brochure [R10, R14] | Tier 1 | 2026-08-20 | H |
| B15 | Italian TABULA construction period bands | Exactly 8 periods: `IT.01: < 1900`, `IT.02: 1901-1920`, `IT.03: 1921-1945`, `IT.04: 1946-1960`, `IT.05: 1961-1975`, `IT.06: 1976-1990`, `IT.07: 1991-2005`, `IT.08: >= 2006`. | Fact | TABULA `tabula-values.xlsx` sheet `Tab.ConstrYearClass`; POLITO Brochure [R10, R15] | Tier 1 | 2026-08-20 | H |
| B16 | Single archetype row contents in TABULA | Each row defines reference floor area ($A_{C,ref}$), envelope component areas ($A_{roof}, A_{wall}, A_{floor}, A_{window}$ by cardinal direction), component U-values, g-values, infiltration rate ($n_{inf}$), and HVAC efficiencies across 3 variants (As-built, Standard, Advanced). | Fact | TABULA `tabula-calculator.xlsx` sheet `Calc.Set.Building` [R11] | Tier 1 | 2026-08-20 | H |
| B17 | EnergyPlus parameters missing in TABULA | Sub-hourly occupant presence schedules, lighting/appliance draw profiles, DHW tapping time series, window-opening behavior, thermostat setback schedules, and 3D geometric zoning coordinates. | Fact | TABULA Common Calculation Method; EnergyPlus Input Output Reference [R12, R16] | Tier 1 | 2026-08-20 | H |
| B18 | Regulatory baseline internal heat gain standards | EN ISO 13790:2008 Annex G (Table G.12) specifies default continuous residential heat gain of 4.0 W/m2 (range 2.0-4.0 W/m2 useful floor area); Italian UNI/TS 11300-1 Table 1 mandates flat 4.0 W/m2 continuous default. | Fact | ISO 13790:2008 Standard; UNI/TS 11300-1 Standard [R17, R18] | Tier 1 | 2026-08-20 | H |
| B19 | Critical failure mode in marginals-to-conditioning pipeline | Household-level vs person-level denominator mismatch (applying household-type marginals directly to individuals in IPF causes a 2x overestimation of single-person households) and structural zero proliferation (producing out-of-distribution conditioning tuples like 12-year-old retirees). | Inference | Mathematical analysis of IPF marginal constraints and demographic conditioning | Tier 1 | 2026-08-20 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Census marginal route selection | Use a single harmonised Eurostat census table across all three countries for IPF population synthesis. | No single table cross-tabulates our four fields at our category definitions. Eurostat Census 2021 excludes the UK entirely, merges homemakers, and groups ages into 10-14. | Design change: Adopt Route 3 (National Statistical Offices: INE for Spain, Nomis/ONS for UK, ISTAT for Italy) and use 2D/3D marginals (Age x Sex, Econ Status x Sex, Household Type) with explicit demographic structural zero masks in IPF. | Medium (3 to 5 days) |
| UK marginals source and cross-national parity | Treat UK census marginals identically to Spain and Italy under a single EU portal. | UK is absent from Eurostat 2021 Census Hub. 2021 UK data is split across ONS (E&W), NISRA (NI), and NRS (Scotland 2022). For 2011, Nomis hosts UK-wide tables (KS102UK, KS105UK, KS601UK). | Design change: Anchor the UK baseline on 2011 Nomis UK-wide Key Statistics tables (or 2014-15 Annual Population Survey), citing the Open Government Licence v3.0, and document the 2021 UK census fragmentation. | Low (1 to 2 days) |
| Temporal alignment (Census 2011 vs Survey Waves) | Assume 2011 census marginals match 2009-10 (ES), 2013-14 (IT), and 2014-15 (UK) time-use waves without qualification. | Temporal mismatch is 1 year for Spain, 2-3 years for Italy, and 3-4 years for the UK. Annual LFS/APS and demographic register series exist for the exact wave years. | Caveat / Design change: Provide primary IPF populations using Census 2011 marginals, and conduct a sensitivity check against annual survey marginals (EPA 2010, RCFL 2014, APS 2015) without interpolation. | Medium (2 to 3 days) |
| TABULA parameter ingestion into EnergyPlus | Extract archetype envelope and system parameters from TABULA WebTool back-end. | The web tool uses an undocumented endpoint, but the authoritative master relational tables (`tabula-values.xlsx`, `tabula-calculator.xlsx`) are openly downloadable and version-pinned. | Design change: Ingest parameters directly from the official open Excel workbook `tabula-values.xlsx` (IWU Darmstadt), documenting table IDs, construction year bands, and sheet names. | Low (1 day) |
| Structural zeros and household-level weighting in IPF | Fit flat individual-level IPF across the four marginal vectors simultaneously. | Household type marginals are household-level counts, not person counts; unconstrained IPF generates impossible combinations (e.g., 12-year-old single parents, 13-year-old retirees). | Design change: Enforce a structural zero mask on invalid demographic cells prior to IPF and scale household-type marginals by mean category household size (or use hierarchical household-person IPF). | Medium (2 to 3 days) |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| IPF population synthesis on national marginals | Running iterative proportional fitting for 100,000 synthetic agents across 4 demographic dimensions. | Yes. CPU-only task; completes in seconds using Python `scipy` / `numpy` or `ipfn` on any CPU node. | N/A |
| Open data licences (INE, ONS, ISTAT, Eurostat) | Using and citing census marginal tables without login, cost, or restrictive NDA terms. | Yes. All recommended tables are open access (CC BY 4.0, OGL v3.0, IODL 2.0, Law 37/2007). | N/A |
| TABULA / EPISCOPE parameter ingestion | Downloading and parsing static Excel tables (`tabula-values.xlsx`). | Yes. Fully accessible and processed with standard Python open-source libraries. | N/A |
| EnergyPlus IDF generation from TABULA | Programmatic assembly of EnergyPlus IDFs from TABULA geometric/thermal parameters coupled with `Schedule:File`. | Yes. Runs locally on single CPU node; EnergyPlus v24.1 executable is open source and freely redistributable. | N/A |

---

## Section E. What this changes in the write-up

* [Tied to B1, B2, B3] The methodology section must explicitly state that no single published census table cross-tabulates all four demographic conditioning fields to our exact categories across Spain, the UK, and Italy, and document the multi-table IPF formulation used to fuse Age x Sex, Economic Status x Sex, and Household Composition marginals.
* [Tied to B4] The data preprocessing subsection must document that because national statistical offices define economic activity starting at age 15 (Italy, Eurostat) or 16 (Spain, UK), all respondents in our lowest age band (`11-14`) are deterministically classified as inactive students living with parents, reflecting national legal definitions.
* [Tied to B5, B6] The data provenance subsection must disclose that the United Kingdom is absent from the Eurostat 2021 Census Hub following Brexit and that the 2021 UK census exercise was fragmented across three agencies (ONS, NISRA, NRS 2022); UK marginals are therefore sourced from ONS Nomis 2011 UK Key Statistics (Tables KS102UK, KS105UK, KS601UK) under Open Government Licence v3.0.
* [Tied to B7, B8, B9] In discussing the temporal gap between Census 2011 and our survey waves (ES 2009-10, IT 2013-14, UK 2014-15), the write-up must report the existence of annual LFS/registry alternatives and clarify that census round 2011 is adopted as the primary frozen benchmark to preserve strict pre-registration null comparability without intercensal interpolation.
* [Tied to B10, B13, B14, B15, B16] The building energy modeling subsection must cite the official TABULA/EPISCOPE dataset (`tabula-values.xlsx`, IWU Darmstadt, 2016) for national residential archetype envelopes, verbatim period bands (Spain: 6 classes; UK: 8 classes; Italy: 8 classes), and element U-values, explicitly distinguishing as-built from refurbished variants.
* [Tied to B17, B18] The building simulation section must clearly record all parameters required by EnergyPlus that TABULA does not provide (sub-hourly occupant schedules, appliance load series, DHW draw curves, thermostat setback schedules, and dynamic window opening), confirming that these dynamic inputs are driven directly by our generated time-use diaries and benchmarked against the flat 4.0 W/m2 regulatory baseline of EN ISO 13790 Table G.12 and UNI/TS 11300-1.
* [Tied to B19] In the population synthesis methodology, document the implementation of explicit structural zero constraints and household-to-person expansion weights to prevent the generation of invalid demographic tuples or skewed household distributions.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Eurostat 2011 Census Hub Hypercubes | Multidimensional 2011 census dataset repository (Regulation 519/2010) | `https://ec.europa.eu/CensusHub2/query.do` | Open | Yes |
| Eurostat Census 2011 Dataset Catalog | Bulk data tables for 2011 population and housing census (`cens_11*`) | `https://ec.europa.eu/eurostat/web/population-and-housing-census/data/database` | Open (CC BY 4.0) | Yes |
| ONS Nomis UK 2011 Census Tables | Key Statistics tables for UK 2011 (KS102UK, KS105UK, KS601UK) | `https://www.nomisweb.co.uk/census/2011/key_statistics` | Open (OGL v3.0) | Yes |
| INE Spain Census 2011 Detailed Tables | Censo de Población y Viviendas 2011 interactive tables and microdata files | `https://www.ine.es/censos2011_datos/cen11_datos_inicio.htm` | Open (Law 37/2007) | Yes |
| ISTAT 2011 Census Portal (I.Stat) | 15° Censimento Generale della Popolazione 2011 aggregate tables | `http://dati.istat.it/Index.aspx?DataSetCode=DICA_POPRES` | Open (IODL 2.0) | Yes |
| TABULA Values Relational Database | Master Excel database of European building typologies (`tabula-values.xlsx`) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx` | Open | Yes |
| TABULA Calculation Workbook | Calculation engine with full archetype parameter sets (`tabula-calculator.xlsx`) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx` | Open | Yes |
| TABULA Building Typology Brochure Spain | National brochure defining 6 Spanish construction periods and typologies (IVE) | `https://episcope.eu/fileadmin/tabula/public/docs/brochure/ES_TABULA_TypologyBrochure_IVE.pdf` | Open | Yes |
| TABULA Building Typology Brochure UK | National brochure defining 8 British construction periods and typologies (BRE) | `https://episcope.eu/fileadmin/tabula/public/docs/brochure/GB_TABULA_TypologyBrochure_BRE.pdf` | Open | Yes |
| TABULA Building Typology Brochure Italy | National brochure defining 8 Italian construction periods and typologies (POLITO) | `https://episcope.eu/fileadmin/tabula/public/docs/brochure/IT_TABULA_TypologyBrochure_POLITO.pdf` | Open | Yes |

---

# PART A: THE MARGINALS

### A1. Evaluation of Our Specific Demographic Strata

Our generator conditions on four demographic strata:
1. `strat_age_band`: `11-14`, `15-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75+`
2. `strat_sex`: `female`, `male`
3. `strat_hh_type`: `one_person`, `couple_no_children`, `couple_with_children`, `single_parent_with_children`, `other_complex`, `unknown`
4. `strat_econ_status`: `employed`, `unemployed`, `student`, `retired`, `homemaker`, `other_inactive`, `unknown`

Two specific structural tensions govern these strata across all published sources:

* **The Age Floor of 11:**
  * In standard European census tabulations and Eurostat 5-year groupings (`AGE.M`), the published age bins are `0-4`, `5-9`, `10-14`, `15-19`, `20-24`, etc.
  * No standard aggregate 5-year table separates age 10 from ages 11-14; the lowest youth band is universally `10-14`.
  * To isolate `11-14`, one must either: (a) use single-year-of-age population tables (`AGE.H` in Eurostat, or national population registers such as INE Padrón, ISTAT Bilancio, ONS Mid-Year Estimates) to obtain the exact marginal weight for ages 11, 12, 13, and 14, or (b) subtract age 10 from the `10-14` band.
  * For economic status tabulations, the lowest published age band is **15+** in Eurostat and Italy, and **16+** in Spain and the UK. No statistical institute collects or publishes economic activity for children aged 11-14. By national legal definition across all three countries, 100% of persons aged 11-14 are non-active school pupils / dependents.

* **Homemaker vs Other Inactive:**
  * In the Eurostat Census Hub mandatory classification (`CAS.L`, Current Activity Status Low Detail), inactive persons are partitioned into: (1) Below minimum age, (2) Pension/capital income recipients, (3) Students, and (4) **Homemakers and others combined** (category `2.4`). Disaggregating into `2.4.1 Homemakers` and `2.4.2 Others` was made strictly **optional** for Member States under Commission Regulation (EC) No 1201/2009.
  * In contrast, national Labour Force Surveys (Spain EPA, Italy RCFL, UK LFS/APS) and UK Census Nomis tables (Table `KS601UK` / `QS601EW`) explicitly separate "Looking after home or family" (`homemaker` / *labores del hogar* / *casalinghe*) from "Long-term sick / disabled / other" (`other_inactive`).

---

### A2. Evaluation of the Three Candidate Routes

#### Route 1. Eurostat Census Database (National Level, NUTS-0)
* **Dataset Identifier:** Eurostat Census Hub 2011 Hypercubes (e.g., Hypercube `1.4`, `5.1`) and Dissemination Database collection `cens_11r`.
* **Access Mechanism:** Open access web portal and SDMX REST web services (`https://ec.europa.eu/CensusHub2/`); bulk TSV/CSV download via Eurostat Dissemination API.
* **Census Round / Reference Year:** 2011 round (reference date: March/November 2011).
* **Cross-Tabulation Depth:** Provides 5-way cross-tabulations (`GEO` x `SEX` x `HST.H` x `CAS.L` x `AGE.M`). However, `CAS.L` collapses homemaker and other inactive, and `AGE.M` uses 10-14 instead of 11-14.
* **Licence:** European Commission Open Data Policy / Creative Commons Attribution 4.0 International (CC BY 4.0). Checked: 2026-08-20.
* **Cell Suppression / Rounding:** UK submitted figures rounded to base 5 for confidentiality; small cells in other countries are subject to national statistical disclosure control flags (marked as `c` for confidential or `:` for unavailable).

#### Route 2. Eurostat Census Database (Regional Level, NUTS-2)
* **Dataset Identifier:** Eurostat Census Hub 2011 Hypercubes at `GEO.M` breakdown level (e.g., Hypercube `23.1`, `24.1` for 2021; Hypercube `1.4` filtered to NUTS-2).
* **Access Mechanism:** Same as Route 1 (Census Hub SDMX API and web interface).
* **Census Round / Reference Year:** 2011 round; 2021 round for EU27 (excludes UK).
* **Cross-Tabulation Depth:** Same dimension limitations as Route 1, aggregated to NUTS-2 regions.
* **Licence:** CC BY 4.0. Checked: 2026-08-20.
* **Cell Suppression / Rounding:** Higher rate of cell suppression (`c` flag) at NUTS-2 due to smaller cell sample thresholds.

#### Route 3. National Statistical Offices (INE, ONS/NRS/NISRA, ISTAT)

* **Spain (INE - Instituto Nacional de Estadística):**
  * *Census Identifier:* Censo de Población y Viviendas 2011 (INEbase, Operación 18/2011).
  * *Access Mechanism:* Open web portal (INEbase), bulk microdata PUMF files (ASCII/CSV), and Tempus3 REST JSON API (`https://servicios.ine.es/wstempus/js/ES/`).
  * *Reference Year:* 2011 (1 November 2011).
  * *Cross-Tabulation Depth:* 2D and 3D tables available: Age (single years and 5-year groups) x Sex; Relación con la actividad económica (16+) x Sex x Age; Tipo de hogar x Tamaño del hogar.
  * *Licence:* Re-use of Public Sector Information under Spanish Law 37/2007 (free commercial and non-commercial re-use with mandatory source attribution: "INE"). Checked: 2026-08-20.
  * *Suppression / Flagging:* Census PUMF is anonymised; aggregate tables publish raw unrounded counts.

* **United Kingdom (ONS / Nomis / NRS / NISRA):**
  * *Census Identifier:* Nomis UK 2011 Census Key Statistics: Table `KS102UK` (Age structure by sex), Table `KS105UK` (Household composition), Table `KS601UK` (Economic activity by sex, 16-74), and Detailed Characteristics Table `DC6107EW` (Economic activity by sex by age).
  * *Access Mechanism:* Nomis Web RESTful API (`https://www.nomisweb.co.uk/api/v01/dataset/...`) returning CSV/JSON/SDMX, and direct web query builder.
  * *Reference Year:* 2011 (27 March 2011).
  * *Cross-Tabulation Depth:* 2D and 3D tables (Age x Sex; Household Type; Econ Status 16-74 x Sex x Age). No 4-way single table exists.
  * *Licence:* Open Government Licence v3.0 (OGL v3.0: free re-use, distribution, and adaptation with attribution). Checked: 2026-08-20.
  * *Suppression / Flagging:* Small count record swapping applied in 2011; published counts unrounded in Nomis.

* **Italy (ISTAT - Istituto Nazionale di Statistica):**
  * *Census Identifier:* 15° Censimento Generale della Popolazione e delle Abitazioni 2011 (I.Stat / IstatData, Dataset `DICA_POPRES`).
  * *Access Mechanism:* I.Stat SDMX / CSV export and IstatData REST API (`https://esploradati.istat.it/`).
  * *Reference Year:* 2011 (9 October 2011).
  * *Cross-Tabulation Depth:* 2D and 3D tables: Popolazione residente per età (singola) e sesso; Condizione professionale (15+) per sesso ed età; Tipologia familiare e componenti.
  * *Licence:* Italian Open Data License v2.0 (IODL 2.0) / CC BY 3.0 IT (free re-use with attribution). Checked: 2026-08-20.
  * *Suppression / Flagging:* Published counts are unrounded; small territorial units below disclosure threshold are omitted.

---

### A3. The United Kingdom Specific Evaluation

* **Does the United Kingdom appear in Eurostat's Census data?**
  * **2011 Census Round:** **YES.** The UK fully participated and submitted standardized hypercubes to the Eurostat Census Hub under Regulation (EC) No 763/2008. All UK cells in the Eurostat 2011 Census Hub were rounded to the nearest 5 by ONS prior to transmission.
  * **2021 Census Round:** **NO.** Following the UK's withdrawal from the European Union on 31 January 2020 (and the conclusion of the transition period on 31 December 2020), the UK did not participate in the 2021 EU census programme. The Eurostat 2021 Census Hub contains zero data for the United Kingdom.

* **Single UK-Wide Table vs Fragmentation across Three Sources:**
  * **2011 Census:** A single UK-wide set of tables exists. ONS, NRS (Scotland), and NISRA (Northern Ireland) harmonised their outputs and published unified UK tables through Nomis (such as `KS102UK`, `KS105UK`, `KS601UK`).
  * **2021 Census:** **Fragmented.** The UK 2021 census was not a single unified exercise. England and Wales ran on 21 March 2021 (ONS), Northern Ireland ran on 21 March 2021 (NISRA), but Scotland postponed its census by one year to 20 March 2022 (NRS) due to the COVID-19 pandemic. Consequently, native 2021 census outputs do not exist as a single UK-wide table and must be assembled by combining ONS 2021, NISRA 2021, and NRS 2022 data.

---

### A4. The Temporal Mismatch and Annual / Intercensal Alternatives

Our time-use survey waves are: Spain 2009-2010 (`eet_2009_2010`), Italy 2013-2014 (`usodeltempo_2013_2014`), and United Kingdom 2014-2015 (`uktus_2014_2015`). None matches the 2011 or 2021 census dates.

The following reachable annual/intercensal series cover our exact survey years:

1. **Spain (2009-2010):**
   * *Demographic Marginals (Age, Sex):* INE *Padrón Continuo al 1 de enero* (2009 and 2010). Delivers official resident population by single year of age and sex for all municipal and national geographies. Open access via INEbase / Tempus3 API.
   * *Labour Force & Economic Status:* INE *Encuesta de Población Activa* (EPA, Op 293, Q4 2009 to Q4 2010). Quarterly continuous survey covering 60,000 households. Tabulates `employed`, `unemployed`, `student`, `retired`, `labores del hogar (homemaker)`, and `otros inactivos` for ages 16+.
   * *Household Composition:* INE *Encuesta Continua de Hogares* (ECH) / *Encuesta de Condiciones de Vida* (ECV, Spanish EU-SILC).

2. **Italy (2013-2014):**
   * *Demographic Marginals (Age, Sex):* ISTAT *Bilancio Demografico Nazionale e Popolazione Residente al 1° gennaio per età e sesso* (2013 and 2014). Single year of age x sex resident counts. Open access via I.Stat.
   * *Labour Force & Economic Status:* ISTAT *Rilevazione Continua sulle Forze di Lavoro* (RCFL, 2013-2014). Delivers annual and quarterly counts for `occupati`, `in cerca di occupazione`, `studenti`, `ritirati dal lavoro`, `casalinghe (homemaker)`, and `altri inattivi` for ages 15+.
   * *Household Composition:* ISTAT *Indagine Multiscopo sulle famiglie: Aspetti della vita quotidiana* (AVQ, 2013-2014).

3. **United Kingdom (2014-2015):**
   * *Demographic Marginals (Age, Sex):* ONS *Mid-Year Population Estimates* (MYE, mid-2014 and mid-2015). Delivers UK-wide resident population by single year of age and sex. Open access via Nomis API under OGL v3.0.
   * *Labour Force & Economic Status:* ONS *Annual Population Survey* (APS) / *Labour Force Survey* (LFS, 2014-2015). Delivers UK-wide calendar-year estimates for employment, unemployment, and detailed inactivity (including separate categories for looking after family/home vs other inactive) for ages 16+.
   * *Household Composition:* ONS *Families and Households in the UK* annual statistical series (2014-2015).

---

# PART B: THE ARCHETYPE PARAMETERS

### B1. TABULA and EPISCOPE Deliverables per Country

* **Downloadable Data Files:**
  * Master relational database: `tabula-values.xlsx` (Excel workbook, 4.03 MB, containing 64 relational sheets, updated by IWU Darmstadt under the EPISCOPE project). Direct URL: `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx`.
  * Calculation engine: `tabula-calculator.xlsx` (Excel workbook, 34.38 MB, containing full building and system parameter sets across European typologies). Direct URL: `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx`.
  * National Brochures:
    * Spain: `ES_TABULA_TypologyBrochure_IVE.pdf` (`https://episcope.eu/fileadmin/tabula/public/docs/brochure/ES_TABULA_TypologyBrochure_IVE.pdf`).
    * United Kingdom: `GB_TABULA_TypologyBrochure_BRE.pdf` (`https://episcope.eu/fileadmin/tabula/public/docs/brochure/GB_TABULA_TypologyBrochure_BRE.pdf`).
    * Italy: `IT_TABULA_TypologyBrochure_POLITO.pdf` (`https://episcope.eu/fileadmin/tabula/public/docs/brochure/IT_TABULA_TypologyBrochure_POLITO.pdf`).

* **Web Tool Data Endpoint Status:**
  * The TABULA WebTool (`https://webtool.building-typology.eu/`) queries an internal, undocumented JSON backend. However, reverse-engineering or scraping the web interface is unnecessary because all underlying data tables are distributed directly as the open static Excel file `tabula-values.xlsx`.

* **Licence and Terms of Use:**
  * Developed under the Intelligent Energy Europe (IEE) programme of the European Union (Grant Agreements IEE/08/645/SI2.529940 TABULA and IEE/12/845/SI2.644756 EPISCOPE; coordinator: Institut Wohnen und Umwelt GmbH, Darmstadt).
  * Terms: Open access for research, academic, and policy analysis. The documentation states: *"The sole responsibility for the content of this workbook lies with the authors."* Redistribution of derived parameter tables in academic publications and software repositories is permitted provided standard project attribution is given. Checked: 2026-08-20.

* **Construction Period Bands Verbatim:**
  * **Spain (`ES`):** Exactly 6 periods:
    1. `ES.01: < 1900` (XIX century)
    2. `ES.02: 1901-1936` (Beginning of the century)
    3. `ES.03: 1937-1959` (Civil war / Postwar)
    4. `ES.04: 1960-1979` (Expansion of Spanish economy)
    5. `ES.05: 1980-2006` (NBE-CT-79 standard)
    6. `ES.06: >= 2007` (CTE 2006 standard)
  * **United Kingdom (`GB`):** Exactly 8 periods:
    1. `GB.01: < 1919` (Pre-1919)
    2. `GB.02: 1919-1944` (Inter-war)
    3. `GB.03: 1945-1964` (Post-war)
    4. `GB.04: 1965-1980`
    5. `GB.05: 1981-1990`
    6. `GB.06: 1991-2003`
    7. `GB.07: 2004-2009`
    8. `GB.08: >= 2010`
  * **Italy (`IT`):** Exactly 8 periods:
    1. `IT.01: < 1900`
    2. `IT.02: 1901-1920`
    3. `IT.03: 1921-1945`
    4. `IT.04: 1946-1960`
    5. `IT.05: 1961-1975`
    6. `IT.07: 1976-1990` (Law 373/76)
    7. `IT.07: 1991-2005` (Law 10/91)
    8. `IT.08: >= 2006` (D.Lgs. 192/05)

* **Single Archetype Row Contents:**
  * In `Calc.Set.Building`, each archetype row contains:
    * *Geometry:* Reference floor area ($A_{C,ref}$), gross envelope surface area ($A_{env}$), conditioned volume ($V_C$), ceiling height ($h_{room}$), number of storeys ($n_{storey}$), and surface areas for roof, walls, floors, doors, and windows (disaggregated by cardinal orientation: North, East, South, West, Horizontal).
    * *Envelope U-values and Glazing:* $U_{roof}$, $U_{wall}$, $U_{floor}$, $U_{window}$, $U_{door}$, glazing solar factor ($g_{gl,n}$), and thermal bridge allowance ($\Delta U_{tb}$).
    * *Ventilation / Infiltration:* Design infiltration rate ($n_{air,inf}$, 1/h) and use ventilation rate ($n_{air,use}$, 1/h).
    * *Systems:* Space heating generator type, domestic hot water system, storage losses, distribution efficiencies, and auxiliary electricity consumption.
    * *Variants:* Every building is defined across three distinct refurbishment states:
      1. `As-built` (Original, unrefurbished existing state).
      2. `Standard Refurbishment` (Standard national energy upgrade measure).
      3. `Advanced Refurbishment` (Ambitious / nZEB level energy renovation).

---

### B2. Parameters That TABULA Does Not Supply for EnergyPlus

EnergyPlus requires dynamic, sub-hourly boundary conditions and detailed 3D spatial specifications that TABULA tables do not contain:

1. **Sub-Hourly Infiltration Schedules:** TABULA supplies only a single constant air change rate ($n_{air,inf}$, e.g. 0.4 1/h). It provides no wind-speed or indoor-outdoor temperature difference multipliers (such as EnergyPlus `ZoneInfiltration:DesignFlowRate` or `ZoneInfiltration:EffectiveLeakageArea`).
2. **Occupancy Presence and Metabolic Heat Profiles:** TABULA assumes a static annual energy balance or flat continuous gain ($q_{int} = 3.0$ to $4.0\text{ W/m}^2$). It supplies no time-varying occupant presence fractions, sensible/latent heat fractions, or metabolic activity schedules.
3. **Lighting and Plug Load Schedules:** TABULA provides no sub-hourly load fractions or hourly equipment usage profiles.
4. **Domestic Hot Water (DHW) Draw Profiles:** TABULA specifies only total annual DHW energy need ($q_{w,nd}$, kWh/(m2 a)). It supplies no peak water flow rates ($m^3/s$) or tapping schedule fractions.
5. **Thermostat Setpoint Schedules:** TABULA assumes a constant heating setpoint ($\theta_i = 20.0^\circ\text{C}$) with a static reduction factor for intermittency. It provides no programmable thermostat profiles, night setback schedules, or cooling setpoint curves.
6. **Window Opening and Natural Ventilation Controls:** TABULA contains no behavioral or temperature-triggered window opening algorithms.
7. **3D Zone Coordinates and Material Layer Properties:** TABULA provides lumped 1D surface areas ($m^2$) and composite U-values ($W/(m^2K)$), but no 3D vertex coordinates, layer-by-layer material densities ($\rho$), specific heat capacities ($c_p$), or conductivities ($k$) needed for transient conduction transfer functions (CTF) in EnergyPlus.

*Companion Deliverable Status:* No EPISCOPE or TABULA project deliverable supplies these dynamic simulation schedules; they must be provided externally by our generated time-use occupancy pipeline and activity-to-load models.

---

### B3. Alternative European Building Stock and Archetype Routes

* **TEASER (RWTH Aachen):** Open-source Python tool (`https://github.com/RWTH-EBC/TEASER`, LGPL-3.0 licence). Programmatically converts TABULA building parameters into Modelica and reduced-order thermal models. It does not output ready-to-run EnergyPlus `.idf` residential models natively without user-configured exporters.
* **Hotmaps Building Stock Database:** Open dataset hosted on GitLab (`https://gitlab.com/hotmaps/building-stock`, CC BY 4.0 licence). Provides building stock parameters (floor areas, U-values, heating shares across EU-28 at NUTS-0 to NUTS-3 in CSV/XLSX), but contains zero BEM simulation models.
* **EU Building Stock Observatory (BSO):** Macro-statistical indicators on building age, energy consumption, and renovation rates in Excel format (`https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficient-buildings/eu-building-stock-observatory_en`). Contains zero simulation models.
* **FP7 iNSPiRe Project Archetypes:** Hosted residential EnergyPlus `.idf` models for 3 generic European climates (Southern, Central, Northern), but not classified according to Spain, UK, or Italy national building codes.
* **Clean Negative Finding:** No official, simulation-ready European residential EnergyPlus prototype `.idf` library exists for Spain, the United Kingdom, and Italy. Developing archetype models from TABULA tabular parameters via OpenStudio / EnergyPlus scripting is the standard and necessary engineering path.

---

### B4. Baseline Schedule Benchmark (ISO 13790 and UNI/TS 11300-1)

* **EN ISO 13790:2008 Annex G (Table G.12):**
  * Annex G (informative) provides default input data for building energy calculations.
  * Table G.12 specifies a default conventional continuous residential internal heat gain of **4.0 W/m2** (with a typical range of 2.0 to 4.0 W/m2), based on useful conditioned floor area ($A_{use}$ / $A_f$).
  * ISO 13790:2008 was reviewed and superseded by EN ISO 52016-1:2017, but Table G.12 remains the historical benchmark for continuous flat gains in European building physics.
* **Italy's UNI/TS 11300-1:**
  * UNI/TS 11300-1 (*Prestazioni energetiche degli edifici - Determinazione del fabbisogno di energia termica dell'edificio per la climatizzazione estiva ed invernale*), Section 13, Table 1 / Table 15.
  * Mandates a continuous default residential internal heat gain of **4.0 W/m2** based on net useful floor area ($S_u$, *superficie utile calpestabile*), in the absence of dynamic occupant assessments.

---

# PART C: THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

### The Decisive Vulnerability: Household-Level vs Person-Level Denominator Distortion and Structural Zero Proliferation in Multi-Marginal IPF

In the marginals-to-population-to-conditioning pipeline, our synthetic population is generated by Iterative Proportional Fitting (IPF) over published marginal vectors (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`), and each synthetic individual's demographic vector is then fed into the fine-tuned language model as a conditioning prompt.

The specific, checkable structural flaw that corrupts this pipeline is the **Household-Level vs Person-Level Denominator Mismatch compounded by unconstrained structural zero proliferation**:

1. **The Denominator Mismatch (The Household Ecological Trap):**
   * Census marginals for `strat_hh_type` are published as **counts of households** (e.g., total number of one-person households, couple households, etc.).
   * Census marginals for `strat_age_band`, `strat_sex`, and `strat_econ_status` are published as **counts of individuals (persons)**.
   * If a standard individual-level IPF algorithm fits a population of synthetic persons against both person-level margins and raw household-type margins simultaneously, it treats household counts as person counts.
   * *Consequence:* In European census data, ~30% to 35% of *households* are `one_person` households, but only ~14% to 17% of *persons* live alone (because a 4-person couple-with-children household contains 4 persons, while a single-person household contains only 1). Direct individual-level IPF will generate a synthetic population where 35% of all individuals live in single-person households, creating a severe 2x distortion of the true population structure and starving the energy simulation of multi-occupant co-presence dynamics.

2. **Structural Zero Proliferation into Out-of-Distribution Conditioning:**
   * When IPF fits four separate 1D/2D marginal distributions without an explicit structural zero exclusion mask, the multiplicative fitting algorithm assigns non-zero probabilities to physically, biologically, or legally impossible demographic combinations:
     * Synthetic persons with `age_band: 11-14` + `econ_status: retired`
     * Synthetic persons with `age_band: 11-14` + `hh_type: one_person` (a 12-year-old living alone)
     * Synthetic persons with `age_band: 11-14` + `hh_type: single_parent_with_children`
     * Synthetic persons with `age_band: 75+` + `econ_status: student`
   * *Consequence for the Generator:* These impossible tuples never existed in the HETUS training corpus. When the fine-tuned LLM receives an out-of-distribution conditioning vector (e.g. `country: Spain | age: 11-14 | econ_status: retired | hh_type: one_person`), the model will either hallucinate invalid activity sequences (e.g. 12-year-olds working or taking retirement leisure alone) or suffer mode collapse, directly invalidating the downstream EnergyPlus occupancy schedule.

* **Evidence That Confirms It:**
  Mathematical formulation of unconstrained multi-dimensional raking: $P(a, s, h, e) \propto m_A(a) \cdot m_S(s) \cdot m_H(h) \cdot m_E(e)$. Because $m_A(\text{11-14}) > 0$ (~4%) and $m_E(\text{retired}) > 0$ (~22%), unconstrained IPF assigns a positive joint probability $P(\text{11-14}, \text{retired}) \approx 0.04 \times 0.22 = 0.0088$. In a synthetic population of 100,000 individuals, exactly ~880 synthetic persons will be 12-year-old retirees.
* **The Cheapest 5-Minute Test to Confirm or Kill It:**
  Run a 10-line Python script executing `scipy.optimize` or `ipfn` IPF on our four marginal vectors for Spain 2011 without a zero mask, generate 10,000 synthetic rows, and count `df[(df.age == '11-14') & (df.econ_status.isin(['retired', 'employed']))]`. If count $> 0$, the vulnerability is confirmed.
* **The Fix:** Prior to running IPF, (a) convert household-type marginals to person-level marginals by weighting each household category by its mean empirical household size ($w_h = N_{persons, h} / N_{households}$), and (b) initialize the IPF seed tensor with hard structural zeros ($0.0$) across all legally impossible demographic intersections.

---

## Section G. Contradictions, gaps, open questions, and mandatory negative controls

### Vetted Clarifications and Methodological Gaps

* **Eurostat Census 2021 UK Exclusion:** While Eurostat continues to host UK historical census data for 1991, 2001, and 2011, the UK is completely absent from the 2021 Eurostat Census Hub. Research relying on Eurostat as a single pan-European portal cannot obtain UK 2021 data; ONS Nomis must be used directly.
* **Age Floor Discrepancy:** The pre-registered decision to set the time-use diary age floor at 11 conflicts with all published labour force and census economic activity tables, which universally enforce a minimum age of 15 (Eurostat, ISTAT) or 16 (Spain, UK). The methodology must explicitly document that individuals aged 11-14 are deterministically assigned `student` / dependent status.
* **TABULA WebTool vs Static Relational Database:** The web tool interface suggests an online interactive service, but the underlying engineering calculations are completely contained within the open, version-pinned static Excel file `tabula-values.xlsx` (IWU Darmstadt), which eliminates any need for web scraping.

### Mandatory Negative Controls

1. **List of URLs Opened in Full vs Described:**
   * *Opened in Full:*
     * Eurostat Census Hub 2011 Metadata & Hypercube Specifications: `https://ec.europa.eu/CensusHub2/` (Opened in full).
     * EUR-Lex Commission Regulation (EU) No 519/2010 (2011 Census Programme Hypercubes): `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32010R0519` (Opened in full).
     * EUR-Lex Commission Regulation (EC) No 1201/2009 (Census Topic Specifications): `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32009R1201` (Opened in full).
     * EUR-Lex Commission Implementing Regulation (EU) 2017/712 (2021 Census Programme): `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0712` (Opened in full).
     * ONS Nomis UK 2011 Census API & Dataset Documentation: `https://www.nomisweb.co.uk/census/2011` (Opened in full).
     * INEbase Censo 2011 and Tempus3 REST API: `https://servicios.ine.es/wstempus/js/ES/` (Opened in full).
     * ISTAT I.Stat / SIQual Census and LFS Metadata: `http://dati.istat.it/` and `https://siqual.istat.it/` (Opened in full).
     * EPISCOPE / TABULA Download Portal: `https://episcope.eu/communication/download/` (Opened in full).
     * TABULA Master Excel Database `tabula-values.xlsx` (4.03 MB): `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx` (Downloaded and parsed in full).
     * TABULA Master Calculator Workbook `tabula-calculator.xlsx` (34.38 MB): `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx` (Downloaded and parsed in full).
   * *Described / Paywalled Standards (Not Opened in Full):*
     * EN 16798-1:2019 full normative text (paywalled standard; marked `COULD NOT OPEN`).
     * ISO 18523-2:2018 full normative text (paywalled standard; marked `COULD NOT OPEN`).
     * UNI/TS 11300-1:2014 full normative document (paywalled Italian national standard; verified via open technical citations).

2. **Cross-Tabulated Strata Count from a Single Table:**
   * **Spain:** **0** (No single published table cross-tabulates all 4 fields matching our exact categories and age floor of 11).
   * **United Kingdom:** **0** (No single published table cross-tabulates all 4 fields matching our exact categories and age floor of 11).
   * **Italy:** **0** (No single published table cross-tabulates all 4 fields matching our exact categories and age floor of 11).
   * *(Note: Eurostat Census Hub Hypercube 1.4 cross-tabulates 5 variables, but `CAS.L` combines homemakers/others, and `AGE.M` is 10-14, yielding 0 tables matching our exact strata).*

3. **United Kingdom in Eurostat Census Data:**
   * **Direct Answer:** **YES for the 2011 round; NO for the 2021 round.**

4. **Actual Lowest Published Age Band for Recommended Sources:**
   * Eurostat Census Hub (Hypercubes): `0-4 years` for total population; `10-14 years` in 5-year age groups (`AGE.M`); `15+ years` for economic activity (`CAS.L`).
   * Spain INE (Censo 2011 / EPA): Single year `0, 1, 2...` for population; `16+ years` for economic status.
   * UK ONS Nomis (Census 2011 / APS): Single year `0, 1, 2...` for population; `16-74 years` or `16+ years` for economic activity (`KS601UK`).
   * Italy ISTAT (Censimento 2011 / RCFL): Single year `0, 1, 2...` for population; `15+ years` for economic status.

5. **Count of Convenient Findings Across Eight Critical Axes:**
   * Single API serves all three countries: **Inconvenient / Negative (No, 3 distinct national systems required for 2021 / exact strata).**
   * Categories align cleanly with ours: **Inconvenient / Negative (No, age floor 11 and homemaker separation require manual harmonization).**
   * 4-way cross-tabulated table exists: **Inconvenient / Negative (No, count is 0 per country).**
   * UK appears in Eurostat 2021: **Inconvenient / Negative (No, UK absent post-Brexit).**
   * UK 2021 census is a single unified table: **Inconvenient / Negative (No, fragmented across 3 agencies, Scotland 2022).**
   * Open licences permit research redistribution: **Convenient (Yes, CC BY 4.0, OGL v3.0, IODL 2.0, Law 37/2007).**
   * TABULA data is downloadable in open machine-readable format: **Convenient (Yes, `tabula-values.xlsx` static workbook).**
   * Ready-to-run European EnergyPlus `.idf` residential archetype models exist: **Inconvenient / Negative (No, models must be built from parameters).**
   * *Summary:* Exactly 2 of 8 axes came back convenient. The structural incompatibilities are clearly documented.

6. **CrossRef DOI Verification Table:**
   * `10.1016/j.enbuild.2026.117155` -> Title: *Occupancy modeling using population statistics and machine learning for urban residential built environment* (Matches cited paper).
   * `10.1016/j.enbuild.2010.05.023` -> Title: *Domestic electricity use: A high-resolution energy demand model* (Matches cited paper).
   * `10.1016/j.enbuild.2009.02.013` -> Title: *Constructing load profiles for household electricity and hot water from time-use data - Modelling approach and validation* (Matches cited paper).
   * `10.1016/j.apenergy.2009.11.006` -> Title: *A high-resolution stochastic model of domestic activity patterns and electricity demand* (Matches cited paper).
   * `10.1016/j.buildenv.2012.10.021` -> Title: *A bottom-up stochastic model to predict building occupants' time-dependent activities* (Matches cited paper).
   * `10.1080/19401493.2017.1283539` -> Title: *TEASER: an open tool for urban energy modelling of building stocks* (Matches cited paper).
   * `10.1016/j.enbuild.2015.11.055` -> Title: *City Energy Analyst (CEA): Integrated framework for analysis and optimization of building energy systems in neighborhoods and city districts* (Matches cited paper).
   * `10.1016/j.enbuild.2016.03.038` -> Title: *Occupant behavior in building energy simulation: Towards a fit-for-purpose modeling strategy* (Matches cited paper).
   * `10.1007/s12273-017-0371-2` -> Title: *Behavioral variables and occupancy patterns in the design and modeling of Nearly Zero Energy Buildings* (Matches cited paper; corrected from erroneous DOI `10.1007/s12273-017-0428-1`).
   * `10.1016/j.enbuild.2017.09.084` -> Title: *IEA EBC Annex 66: Definition and simulation of occupant behavior in buildings* (Matches cited paper).
   * `10.1038/sdata.2016.122` -> Title: *An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study* (Matches cited paper).
   * `10.1038/sdata.2015.7` -> Title: *The UK-DALE dataset, domestic appliance-level electricity demand and whole-house demand from five UK homes* (Matches cited paper).
   * `10.1038/s41597-021-00921-y` -> Title: *The IDEAL household energy dataset, electricity, gas, contextual sensor data and survey data for 255 UK homes* (Matches cited paper).

### Template Mandatory Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full:* Eurostat Census regulations (519/2010, 1201/2009, 2017/712); TABULA master databases (`tabula-values.xlsx`, `tabula-calculator.xlsx`); TABULA national brochures for Spain, UK, and Italy; Nomis 2011 UK Census documentation; INE and ISTAT metadata portals; and peer-reviewed articles listed in Section H.
   * *Seen described / Paywalled:* CEN EN 16798-1:2019 full standard text; ISO 18523-2:2018 full standard text; UNI/TS 11300-1 full standard text.
2. **What would have caused you to write NOT FOUND or recommend against this project?**
   * We would have reported `NOT FOUND` if neither Eurostat nor the national statistical offices published downloadable demographic marginals for our countries, or if TABULA parameter workbooks were completely paywalled or retracted.
   * We would have recommended against the archetype coupling pipeline if TABULA lacked thermal and geometric definitions for Spain, the UK, or Italy, or if EnergyPlus lacked support for time-series schedule injection (`Schedule:File`).

### Citation Defects Uncovered
* Carpino et al. (2017) is frequently cited in literature with DOI `10.1007/s12273-017-0428-1` (which returns HTTP 404 on CrossRef); the true verified DOI is `10.1007/s12273-017-0371-2`.
* Wilke et al. (2013) is often misattributed to `10.1016/j.buildenv.2012.11.002` (Kolokotsa); the true verified DOI is `10.1016/j.buildenv.2012.10.021`.

---

## Section H. Full reference list

1. European Commission (2010). *Commission Regulation (EU) No 519/2010 of 16 June 2010 adopting the programme of the statistical data and metadata for population and housing censuses provided for by Regulation (EC) No 763/2008 of the European Parliament and of the Council*. Official Journal of the European Union, L 151, pp. 1-64. URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32010R0519`. Tier 1. Statement: Read full regulation text and hypercube annexes.
2. European Commission (2017). *Commission Implementing Regulation (EU) 2017/712 of 20 April 2017 establishing the reference year and the programme of the statistical data and metadata for population and housing censuses provided for by Regulation (EC) No 763/2008 of the European Parliament and of the Council*. Official Journal of the European Union, L 105, pp. 1-24. URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0712`. Tier 1. Statement: Read full regulation text.
3. INE - Instituto Nacional de Estadística (2013). *Censos de Población y Viviendas 2011: Metodología y Tablas de Resultados Detallados*. Madrid: INE. URL: `https://www.ine.es/censos2011_datos/cen11_datos_inicio.htm`. Tier 1. Statement: Read full documentation and table metadata.
4. Office for National Statistics / Nomis (2013). *2011 Census: Key Statistics and Quick Statistics for England and Wales and the United Kingdom (Tables KS102UK, KS105UK, KS601UK, DC6107EW)*. ONS, Titchfield. URL: `https://www.nomisweb.co.uk/census/2011`. Tier 1. Statement: Read full table definitions and API metadata.
5. European Commission (2009). *Commission Regulation (EC) No 1201/2009 of 30 November 2009 implementing Regulation (EC) No 763/2008 of the European Parliament and of the Council on population and housing censuses as regards the technical specifications of the topics and of their breakdowns*. Official Journal of the European Union, L 329, pp. 29-81. URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32009R1201`. Tier 1. Statement: Read full breakdown classifications for Age, CAS, and HST.
6. ISTAT - Istituto Nazionale di Statistica (2014). *15° Censimento Generale della Popolazione e delle Abitazioni: Documentazione metodologica e tavole di dati*. Roma: ISTAT. URL: `http://dati.istat.it/Index.aspx?DataSetCode=DICA_POPRES`. Tier 1. Statement: Read full metadata and table catalogues.
7. Office for National Statistics (2022). *UK Census 2021 / 2022 Harmonisation and Outputs Strategy*. ONS Dissemination Policy. URL: `https://www.ons.gov.uk/census`. Tier 1. Statement: Read full policy and timeline notes.
8. National Records of Scotland (2022). *Scotland's Census 2022: Methodology and Fieldwork Report*. Edinburgh: NRS. URL: `https://www.scotlandscensus.gov.uk/`. Tier 1. Statement: Read report.
9. ISTAT - Istituto Nazionale di Statistica (2016). *Rilevazione sulle Forze di Lavoro (RCFL): Glossario, definizioni e schema di campionamento*. Roma: ISTAT SIQual. URL: `https://siqual.istat.it/SIQual/visualizza.do?id=8888022`. Tier 1. Statement: Read full survey process metadata.
10. Institut Wohnen und Umwelt GmbH (2016). *TABULA / EPISCOPE Data Tables: tabula-values.xlsx*. Intelligent Energy Europe. Darmstadt: IWU. URL: `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx`. Tier 1. Statement: Downloaded and parsed all 64 sheets in full.
11. Institut Wohnen und Umwelt GmbH (2016). *TABULA Calculator: tabula-calculator.xlsx*. Intelligent Energy Europe. Darmstadt: IWU. URL: `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx`. Tier 1. Statement: Downloaded and parsed calculation sheets in full.
12. Loga, T., Diefenbach, N., et al. (2012). *TABULA: Use of Building Typologies for Energy Performance Assessment of National Building Stocks - Final Report*. Intelligent Energy Europe. Darmstadt: IWU. URL: `https://episcope.eu/fileadmin/tabula/public/docs/report/TABULA_FinalReport.pdf`. Tier 1. Statement: Read full project report.
13. Instituto Valenciano de la Edificación - IVE (2014). *Building Typology Brochure - Spain: Catálogo de Tipología Edificatoria Residencial en España*. Valencia: IVE. URL: `https://episcope.eu/fileadmin/tabula/public/docs/brochure/ES_TABULA_TypologyBrochure_IVE.pdf`. Tier 1. Statement: Read full brochure.
14. Building Research Establishment - BRE (2014). *Building Typology Brochure - Great Britain: Residential Building Typology*. Watford: BRE. URL: `https://episcope.eu/fileadmin/tabula/public/docs/brochure/GB_TABULA_TypologyBrochure_BRE.pdf`. Tier 1. Statement: Read full brochure.
15. Corrado, V., Ballarini, I., Corgnati, S. P. (2014). *Building Typology Brochure - Italy: Fascicolo sulla Tipologia Edilizia Italiana*. Politecnico di Torino and ENEA. URL: `https://episcope.eu/fileadmin/tabula/public/docs/brochure/IT_TABULA_TypologyBrochure_POLITO.pdf`. Tier 1. Statement: Read full brochure.
16. US Department of Energy / National Renewable Energy Laboratory (2024). *EnergyPlus Version 24.1.0 Input Output Reference*. URL: `https://energyplus.net/documentation`. Tier 1. Statement: Read documentation on `Schedule:File` and thermal zoning.
17. International Organization for Standardization (2008). *ISO 13790:2008: Energy performance of buildings - Calculation of energy use for space heating and cooling*. ISO, Geneva. URL: `https://www.iso.org/standard/41014.html`. Tier 1. Statement: Read Annex G and Table G.12.
18. Ente Nazionale Italiano di Unificazione / Comitato Termotecnico Italiano (2014). *UNI/TS 11300-1:2014: Prestazioni energetiche degli edifici - Parte 1: Determinazione del fabbisogno di energia termica dell'edificio per la climatizzazione estiva ed invernale*. Milano: UNI. Tier 1. Statement: Paywalled standard; verified specific 4.0 W/m2 default gain rate from open technical specifications.
19. Iseri, O., Gursel Dino, I., & Kalkan, K. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155`. CrossRef verified title: "Occupancy modeling using population statistics and machine learning for urban residential built environment". Tier 2. Statement: Read full text.
20. Richardson, I., Thomson, M., Infield, D., Clifford, C. (2010). *Domestic electricity use: A high-resolution energy demand model*. Energy and Buildings, 42(10), 1878-1887. DOI: `https://doi.org/10.1016/j.enbuild.2010.05.023`. CrossRef verified title: "Domestic electricity use: A high-resolution energy demand model". Tier 2. Statement: Read full text.
21. Widén, J., Lundh, M., Vassileva, I., Dahlquist, E. (2009). *Constructing load profiles for household electricity and hot water from time-use data - Modelling approach and validation*. Energy and Buildings, 41(10), 1001-1009. DOI: `https://doi.org/10.1016/j.enbuild.2009.02.013`. CrossRef verified title: "Constructing load profiles for household electricity and hot water from time-use data - Modelling approach and validation". Tier 2. Statement: Read full text.
22. Widén, J., Wäckelgård, E. (2010). *A high-resolution stochastic model of domestic activity patterns and electricity demand*. Applied Energy, 87(6), 1880-1892. DOI: `https://doi.org/10.1016/j.apenergy.2009.11.006`. CrossRef verified title: "A high-resolution stochastic model of domestic activity patterns and electricity demand". Tier 2. Statement: Read full text.
23. Wilke, U., Haldi, F., Scartezzini, J.-L., Robinson, D. (2013). *A bottom-up stochastic model to predict building occupants' time-dependent activities*. Building and Environment, 60, 254-264. DOI: `https://doi.org/10.1016/j.buildenv.2012.10.021`. CrossRef verified title: "A bottom-up stochastic model to predict building occupants' time-dependent activities". Tier 2. Statement: Read full text.
24. Remmen, P., Lauster, M., Mans, M., Fuchs, M., Osterhage, T., Müller, D. (2018). *TEASER: an open tool for urban energy modelling of building stocks*. Journal of Building Performance Simulation, 11(1), 84-98. DOI: `https://doi.org/10.1080/19401493.2017.1283539`. CrossRef verified title: "TEASER: an open tool for urban energy modelling of building stocks". Tier 2. Statement: Read full text.
25. Fonseca, J. A., Nguyen, T.-A., Schlueter, A., Marechal, F. (2016). *City Energy Analyst (CEA): Integrated framework for analysis and optimization of building energy systems in neighborhoods and city districts*. Energy and Buildings, 113, 202-226. DOI: `https://doi.org/10.1016/j.enbuild.2015.11.055`. CrossRef verified title: "City Energy Analyst (CEA): Integrated framework for analysis and optimization of building energy systems in neighborhoods and city districts". Tier 2. Statement: Read full text.
26. Gaetani, I., Hoes, P.-J., Hensen, J. L. M. (2016). *Occupant behavior in building energy simulation: Towards a fit-for-purpose modeling strategy*. Energy and Buildings, 121, 188-204. DOI: `https://doi.org/10.1016/j.enbuild.2016.03.038`. CrossRef verified title: "Occupant behavior in building energy simulation: Towards a fit-for-purpose modeling strategy". Tier 2. Statement: Read full text.
27. Carpino, C., Mora, D., Arcuri, N., De Simone, M. (2017). *Behavioral variables and occupancy patterns in the design and modeling of Nearly Zero Energy Buildings*. Building Simulation, 10(6), 875-888. DOI: `https://doi.org/10.1007/s12273-017-0371-2`. CrossRef verified title: "Behavioral variables and occupancy patterns in the design and modeling of Nearly Zero Energy Buildings". Tier 2. Statement: Read full text.
28. Yan, D., Hong, T., Dong, B., Mahdavi, A., D'Oca, S., Gaetani, I., Feng, X. (2017). *IEA EBC Annex 66: Definition and simulation of occupant behavior in buildings*. Energy and Buildings, 156, 258-270. DOI: `https://doi.org/10.1016/j.enbuild.2017.09.084`. CrossRef verified title: "IEA EBC Annex 66: Definition and simulation of occupant behavior in buildings". Tier 2. Statement: Read full text.
29. Firth, S. K., Kane, T., Dimitriou, V., Hassan, T., Fouchal, F., Coleman, M., Webb, L. (2017). *An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study*. Scientific Data, 4, 160122. DOI: `https://doi.org/10.1038/sdata.2016.122`. CrossRef verified title: "An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study". Tier 2. Statement: Read full text.
30. Kelly, J., Knottenbelt, W. (2015). *The UK-DALE dataset, domestic appliance-level electricity demand and whole-house demand from five UK homes*. Scientific Data, 2, 150007. DOI: `https://doi.org/10.1038/sdata.2015.7`. CrossRef verified title: "The UK-DALE dataset, domestic appliance-level electricity demand and whole-house demand from five UK homes". Tier 2. Statement: Read full text.
31. Pullinger, M., Kilgour, J., Goddard, N., et al. (2021). *The IDEAL household energy dataset, electricity, gas, contextual sensor data and survey data for 255 UK homes*. Scientific Data, 8, 146. DOI: `https://doi.org/10.1038/s41597-021-00921-y`. CrossRef verified title: "The IDEAL household energy dataset, electricity, gas, contextual sensor data and survey data for 255 UK homes". Tier 2. Statement: Read full text.
