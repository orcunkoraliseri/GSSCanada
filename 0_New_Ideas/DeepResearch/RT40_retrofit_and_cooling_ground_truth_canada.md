# RT40. What can check the model: truth on heat pumps, air conditioning and retrofits in Canadian homes

## Section A. Direct answer

No openly accessible Canadian database currently releases address-level ground truth on heat pumps, air conditioning, insulation, or window retrofits that a university researcher can freely download and link directly to a civic address [L18, L28, INFERENCE]. The primary national per-dwelling truth repository is Natural Resources Canada's EnerGuide Rating System database of pre- and post-retrofit home energy audits, but its public open data release is strictly aggregated to the Forward Sortation Area (FSA, first three characters of the postal code) to comply with the federal Privacy Act [L18, L28]. A university researcher can obtain per-building microdata with full postal codes or addresses only by executing a formal bilateral Research Data Sharing Agreement directly with NRCan (specifically the Office of Energy Efficiency / CanmetENERGY) or with provincial energy ministries administering EnerGuide delivery (such as Transition energetique Quebec for Renoclimat), under strict non-disclosure terms that prohibit redistribution of identifiable property records [L18, L28, INFERENCE]. Provincial utility rebate registries (Hydro-Quebec LogisVert, Enbridge Home Efficiency Rebate Plus, CleanBC, and Efficiency Nova Scotia) publish only aggregate program participation counts and financial expenditures, keeping address-level rebate claims strictly confidential [L8, L10, L13, L14, INFERENCE]. For non-linkable aggregate validation (role L3), the highest-fidelity public benchmarks are Statistics Canada's Households and Environment Survey (Table 38-10-0019-01 for air conditioning and Table 38-10-0286-01 for heating systems), which provide biennial stock shares at the Census Metropolitan Area (CMA) level for Montreal, Toronto, and other major cities from 2013 to 2023 [L38].

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Public EnerGuide geographic resolution | EnerGuide Rating System open data is published exclusively at Forward Sortation Area (FSA) level, never by civic address | fact | open.canada.ca [L18] | Tier 1 | 2026-09-22 | H |
| 2 | Researcher access to EnerGuide microdata | Researchers obtain pre- and post-retrofit audit microdata via bilateral Research Data Sharing Agreements with NRCan, with public release of full postal codes or addresses prohibited | fact | NRCan / Mohareb et al. (2022) [L18, L28] | Tier 1 | 2026-09-22 | H |
| 3 | Greener Homes Grant data release | NRCan releases only equipment eligibility lists and national/provincial aggregate evaluation totals; address-level grant data is closed | fact | open.canada.ca / natural-resources.canada.ca [L3, L4] | Tier 1 | 2026-09-22 | H |
| 4 | Quebec Renoclimat and LogisVert privacy | Transition energetique Quebec and Hydro-Quebec keep property-level heat-pump and insulation subsidies confidential; only program-level totals are published | fact | transitionenergetique.gouv.qc.ca / hydroquebec.com [L6, L8, L9] | Tier 1 | 2026-09-22 | H |
| 5 | Ontario HER+ and Toronto HELP access | Enbridge HER+ and Toronto HELP publish no public address-level database of approved retrofit loans or equipment rebates | fact | enbridgegas.com / toronto.ca [L10, L11] | Tier 1 | 2026-09-22 | H |
| 6 | BC, NS, MB provincial rebate access | CleanBC Better Homes, Efficiency Nova Scotia, and Efficiency Manitoba maintain internal audit registries but release zero address-level recipient data | fact | betterhomesbc.ca / efficiencyns.ca [L13, L14, L15] | Tier 1 | 2026-09-22 | H |
| 7 | StatCan HES Air Conditioning table | Table 38-10-0019-01 reports air conditioning equipment shares biennially from 2013 to 2023 at CMA level (56 geographic members) | fact | www150.statcan.gc.ca [L30, L38] | Tier 1 | 2026-09-22 | H |
| 8 | StatCan HES Primary Heating table | Table 38-10-0286-01 reports primary heating systems and energy sources biennially from 2013 to 2023 at CMA level | fact | www150.statcan.gc.ca [L31, L38] | Tier 1 | 2026-09-22 | H |
| 9 | StatCan SHS equipment table | Table 11-10-0228-01 reports air conditioner and heating appliance counts annually from 2010 to 2023 at provincial level | fact | www150.statcan.gc.ca [L32, L38] | Tier 1 | 2026-09-22 | H |
| 10 | Census heating questions | The Canadian Census long-form questionnaire asks only about annual fuel expenditure amounts (Question E9 in 2021) and contains zero questions on heating equipment or heat pumps | fact | statcan.gc.ca Housing Reference Guide [L75, L76] | Tier 1 | 2026-09-22 | H |
| 11 | NRCan CEUD residential stock tables | Table 27 (Heating System Stock by Building Type) and Table 33 (Cooling System Stock) report annual provincial/regional stocks from 1990 to recent year | fact | oee.nrcan.gc.ca [L34, L40, L67, L73] | Tier 1 | 2026-09-22 | H |
| 12 | Prior validation of record reading | Prior literature validates permit/record extraction primarily against energy benchmarking disclosure (Zhang et al. 2020) or EPC certificates against meter data (Coyne & Denny 2021) | fact | SimAUD / Energy Efficiency [L214, L117] | Tier 1 | 2026-09-22 | H |

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| 1 | Mohareb, Eugene; Gillich, Aaron; Bristow, David (2022), Buildings and Cities | 10.5334/bc.202 [L27] | Evaluated spatial and temporal drivers of residential energy retrofits across Canada using the national ecoENERGY pre- and post-retrofit audit database matched to census data at FSA level | NRCan ecoENERGY audit database (2007-2012) and Statistics Canada Census/NHS | 640,000 retrofitted homes across Canada aggregated to FSAs | Did not process address-level records; could not link audits to municipal building permits; data restricted to FSA aggregations due to privacy [L28] | full |
| 2 | Coyne, Bryan; Denny, Eleanor (2021), Energy Efficiency | 10.1007/s12053-021-09960-1 [L117] | Tested the accuracy of pre- and post-retrofit Energy Performance Certificate (EPC) ratings and heating equipment attributes against actual smart-metered gas and electricity consumption microdata | National EPC database and metered utility consumption in Ireland | Thousands of residential dwellings | Evaluated official engineering audit certificates rather than natural language permit texts [L117] | abstract |
| 3 | Ali, Usman; Shamsi, Mohammad Haris; Hoare, Cathal; Alshehri, Fawaz; Mangina, Eleni; O'Donnell, James (2019), Building Simulation | 10.26868/25222708.2019.210232 [L119] | Trained machine learning models on building feature datasets to predict residential energy ratings, scoring model predictions directly against ground-truth on-site EPC audit records | Irish National Energy Performance Certificate (EPC) register | Tens of thousands of residential audits | Evaluated tabular feature classifiers rather than free-text NLP on municipal building permits [L119] | abstract |
| 4 | Zhang, Wanni; Hong, Tianzhen; Luo, Xuan (2020), SimAUD | 10.26868/25746308.2020.c083 [L214] | Validated an NLP text-mining pipeline on municipal permit descriptions by matching extracted HVAC and envelope retrofit events against building energy benchmarking disclosure records | San Francisco building permits and ENERGY STAR benchmarking data | Over 1,000,000 permit records | Evaluated on commercial buildings in San Francisco; did not evaluate Canadian residential dwellings [L214] | abstract |

## Section D. Gap and fit assessment

### Scoring Montreal and Toronto models against truth [INFERENCE]

To score a language model that reads Montreal or Toronto building permit text to predict heat pumps, air conditioning, insulation, and window replacements, university researchers face two distinct scoring regimes:

1. **Scoring against per-dwelling truth (role L2):**
   * *Best candidate source:* NRCan EnerGuide Rating System home evaluation microdata (pre-retrofit `D` files and post-retrofit `E` files) [L18, L28]. The pre- and post-retrofit audit records hold authoritative, on-site verified ground truth recorded by certified Energy Advisors using blower-door tests and physical inspection, explicitly noting primary and secondary heating systems (including heat pump make, model, capacity, and COP), central air conditioning presence, foundation/attic insulation RSI values, and window U-factors [L18, L28, INFERENCE].
   * *Required access route:* A formal bilateral Data Sharing Agreement with NRCan Office of Energy Efficiency / CanmetENERGY, or a sub-agreement through Transition energetique Quebec for Montreal (Renoclimat evaluation records) [L18, L6, INFERENCE].
   * *Primary bias:* Severe self-selection and socioeconomic participation bias [L28, INFERENCE]. Homes that undergo EnerGuide evaluations represent higher-income homeowners voluntarily applying for grants (such as the Canada Greener Homes Grant, ecoENERGY, or Renoclimat) [L4, L6, L28]. These households have substantially higher retrofit rates than the general housing stock, and older or lower-income rental properties are heavily under-represented [L28, INFERENCE]. Furthermore, because audits occur only when an owner seeks a subsidy, un-subsidized heat-pump installations or self-financed window replacements are missing [INFERENCE].

2. **Scoring against aggregate municipal truth (role L3):**
   * *Best candidate source:* Statistics Canada Households and Environment Survey (HES), specifically Table 38-10-0019-01 (Air conditioners by CMA) and Table 38-10-0286-01 (Primary heating systems and energy sources by CMA) [L30, L31, L38].
   * *Strengths:* Provides rigorous, probability-sampled population estimates of the actual proportion of dwellings with central air conditioning, heat pumps, and electric heating specifically for the Montreal CMA and Toronto CMA biennially through 2023 [L38].
   * *Primary bias:* Survey response bias and sampling error at the CMA level; cannot distinguish which specific buildings hold the equipment, and excludes institutional/collective dwellings [L38, INFERENCE].

| Candidate angle | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A7: Model validation against EnerGuide / HES | partly; prior literature evaluates spatial patterns (Mohareb et al. 2022) but has never linked permit text NLP predictions to audit truth [L28] | OpenUBEM archetypes, GSS occupancy schedule generator [BRIEF s.2, s.3] | Direct address-level audit records without formal NRCan bilateral research agreement [L18, L28] | The model cannot be evaluated at the building level using open data alone; validation must either rely on FSA aggregations or restricted data access [L18, INFERENCE] | 3 to 5 months |

## Section E. What this changes in our planning

1. **Adopt a two-tier validation strategy:** Because open data contains zero address-level truth on Canadian home equipment, 5J cannot claim open address-level validation out of the box [L18, L28, INFERENCE]. The project should validate the model at two distinct tiers: (a) Tier 1 aggregate validation against Statistics Canada HES Tables 38-10-0019-01 and 38-10-0286-01 at the CMA level for Montreal and Toronto [L38, Section B rows 7 and 8]; and (b) Tier 2 spatial validation against open EnerGuide FSA-level counts (open.canada.ca) across postal districts [L18, Section B row 1].
2. **Pursue an NRCan CanmetENERGY data sharing agreement in parallel:** If address-level scoring is deemed essential by reviewers, the group must apply for an academic research agreement with NRCan's Housing Division for full postal code or address-level EnerGuide files, acknowledging that agreement processing requires several months [L18, L28, INFERENCE].
3. **Calibrate for the Greener Homes Grant audit surge:** Permit text reading models applied to 2021-2024 records will coincide with the massive influx of heat-pump retrofits spurred by the Canada Greener Homes Grant and Loan [L3, L4, INFERENCE]. Model predictions must be compared with the known temporal surge in federal heat pump grants [L3, L4].
4. **Discard the Canadian Census as an equipment validation source:** The planning assumption that Census microdata could provide heating equipment or air conditioning labels must be permanently discarded; the Census long form captures only dollar fuel expenditures (Question E9), containing zero equipment stock variables [L75, L76, Section B row 10].

## Section F. Concrete artefacts to retrieve

### Item 1. Per-dwelling truth sources (role L2)

#### Card 1: NRCan EnerGuide Rating System Open Data
* **Source name and custodian:** EnerGuide Rating System Open Data; Office of Energy Efficiency, Natural Resources Canada (NRCan) [L18].
* **City or province:** National (Canada-wide) [L18].
* **Years covered and update status:** 2004 to 2026; updated annually (calendar-year CSV releases from 2004 through 2026) [L18].
* **Unit:** Dwelling evaluation record (pre-retrofit audit or post-retrofit audit) [L18].
* **Total row count:** Over 1,200,000 evaluation records across historical program waves [L18, L28].
* **Names of free-text fields:** NONE; fully structured technical audit schema [L18].
* **Free-text language:** Bilingual documentation (English and French); data fields are numeric codes and measurements [L18].
* **Separation of residential:** Entire dataset is exclusively residential low-rise housing (single-family detached, semi-detached, row houses) [L18].
* **Structured work-type and equipment fields:** Primary heating system type, secondary heating system type, heat pump type (air-source, ground-source), heat pump COP/HSPF, central air conditioning presence and SEER, ceiling insulation RSI, wall insulation RSI, foundation insulation RSI, window U-factor and solar heat gain coefficient, blower-door air changes per hour at 50 Pa (ACH@50) [L18, L28].
* **Roles:** L2 (label), L3 (aggregate check), L4 (link key at FSA level) [BRIEF s.10].
* **Link key:** Forward Sortation Area (`FSA`, first three characters of postal code), city, province, evaluation date; civic address and full six-character postal code are suppressed [L18].
* **Access route and eligibility:** Open download on open.canada.ca for FSA-level files, checked 2026-09-22 [L18]. Full address-level database requires a formal bilateral Research Data Sharing Agreement directly with NRCan CanmetENERGY / Office of Energy Efficiency [L18, L28]. "Data is provided by calendar year, at the Forward Sortation Area level (FSA, the first 3 digits of the postal code) for files since 2004" [L18].
* **Licence name:** Open Government Licence - Canada [L18]. Derived aggregate models may be redistributed [L18].
* **Known bias:** Voluntary program participation bias; represents homeowners with capital and incentive to undergo paid energy evaluations for federal/provincial rebate programs [L28, INFERENCE].
* **Verified research use:** Mohareb, Gillich, Bristow (2022) used the ecoENERGY / EnerGuide database of 640,000 retrofitted homes to study spatial and temporal drivers of domestic retrofits across Canadian FSAs [L27, L28].

#### Card 2: Canada Greener Homes Grant and Loan Records
* **Source name and custodian:** Canada Greener Homes Initiative Data; Natural Resources Canada and Canada Mortgage and Housing Corporation (CMHC) [L3, L4].
* **City or province:** National (Canada-wide) [L3, L4].
* **Years covered and update status:** 2021 to 2026 (grant intake closed February 2024; loan program ongoing) [L4].
* **Unit:** Grant/loan recipient file [L4].
* **Total row count:** Approximately 500,000 grant applicants and 165,000+ completed retrofits [L4].
* **Names of free-text fields:** NONE [L3, L4].
* **What is released:** Only national and provincial summary totals, press release figures, and eligible equipment product lists on open.canada.ca; zero address-level or postal-area microdata is published publicly [L3, L4].
* **Roles:** L3 (aggregate check only); cannot serve L2 without restricted government data agreement [BRIEF s.10, INFERENCE].
* **Link key:** None in public releases [L3, L4].
* **Access route and eligibility:** Closed source for property-level data; aggregate summaries open on natural-resources.canada.ca [L4].
* **Licence name:** Open Government Licence - Canada (for public aggregate documents) [L3].
* **Known bias:** Heavy concentration in heat-pump grants ($5,000 grant cap prompted massive heat pump adoption between 2021 and 2024) [L4, INFERENCE].
* **Verified research use:** NONE FOUND for building-level model scoring [L79, L80].

#### Card 3: Oil to Heat Pump Affordability (OHPA) Program
* **Source name and custodian:** Oil to Heat Pump Affordability Program; Natural Resources Canada [L5].
* **City or province:** National (targeted to low-to-median income households heating with oil, with enhanced funding in Atlantic provinces) [L5].
* **Years covered and update status:** 2022 to 2026; active [L5].
* **Unit:** Household funding record [L5].
* **What is released:** Program eligibility guidelines, aggregate applicant counts, and quarterly federal reporting; zero per-building records released [L5].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Access route and eligibility:** Closed source for property microdata [L5].
* **Licence name:** Crown Copyright / Government of Canada [L5].
* **Known bias:** Exclusively covers conversions from heating oil to heat pumps among qualifying income brackets [L5, INFERENCE].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 4: Quebec Renoclimat
* **Source name and custodian:** Programme Renoclimat; Ministere de l'Environnement, de la Lutte contre les changements climatiques, de la Faune et des Parcs (MELCCFP) / Transition energetique Quebec [L6].
* **City or province:** Province of Quebec [L6].
* **Years covered and update status:** 2007 to 2026; active [L6].
* **Unit:** Home energy audit and financial assistance record [L6].
* **What is released:** Renoclimat operates as Quebec's delivery agent for EnerGuide evaluations; property-level audit results are transmitted to NRCan's EnerGuide database and held privately by the Quebec government [L6, L18]. Only provincial annual reports and aggregate participant counts are published [L6].
* **Terms for linking:** Researchers can access Renoclimat microdata only through formal research data sharing agreements with the Government of Quebec or via NRCan's EnerGuide agreement [L6, L18, INFERENCE].
* **Roles:** L2 (under restricted agreement), L3 (aggregate check) [BRIEF s.10].
* **Licence name:** Closed government administrative database [L6].
* **Known bias:** Captures insulation and heat pump retrofits, but requires blower-door test before and after work [L6, INFERENCE].
* **Verified research use:** NONE FOUND for address-joined NLP scoring [L79, L80].

#### Card 5: Hydro-Quebec LogisVert and Chauffez vert
* **Source name and custodian:** Programme LogisVert et Chauffez vert; Hydro-Quebec and Transition energetique Quebec [L7, L8].
* **City or province:** Province of Quebec [L7, L8].
* **Years covered and update status:** LogisVert launched 2023 (ongoing); Chauffez vert active 2013 to 2026 [L7, L8].
* **Unit:** Rebate claim record [L7, L8].
* **What is released:** Hydro-Quebec publishes an open data portal (donnees-ouvertes), but releases only network load profiles, substations, and aggregate consumption; property-level rebate records for heat pumps and insulation are strictly confidential commercial customer data [L8, L9]. Only total participant numbers and cumulative subsidy amounts appear in annual reports [L8].
* **Roles:** L3 (aggregate check only) [BRIEF s.10].
* **Terms for linking:** No public linking permitted; customer addresses are protected under Quebec private sector privacy legislation (Loi 25) [L8, L9, INFERENCE].
* **Licence name:** Closed utility customer database [L8, L9].
* **Known bias:** LogisVert offers direct rebates for efficient heat pumps without requiring a full blower-door test, capturing a wider demographic than Renoclimat, but data is completely closed [L8, INFERENCE].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 6: Enbridge Home Efficiency Rebate Plus (HER+) - Ontario
* **Source name and custodian:** Home Efficiency Rebate Plus (HER+); Enbridge Gas and Natural Resources Canada [L10].
* **City or province:** Province of Ontario [L10].
* **Years covered and update status:** 2023 to 2024 (delivered co-funded Greener Homes Grant subsidies across Ontario; closed to new applicants February 2024) [L10].
* **Unit:** Household rebate record [L10].
* **What is released:** Enbridge Gas publishes only aggregate provincial program reports and marketing summaries; no address-level or postal-code database is released [L10].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Terms for linking:** Closed private utility data; no researcher access portal exists [L10, INFERENCE].
* **Licence name:** Proprietary corporate utility data [L10].
* **Known bias:** Co-delivered with EnerGuide, inheriting EnerGuide homeowner selection bias [L10, L18, INFERENCE].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 7: Toronto Home Energy Loan Program (HELP)
* **Source name and custodian:** Home Energy Loan Program (HELP); Environment and Climate Division, City of Toronto [L11].
* **City or province:** Toronto, Ontario [L11].
* **Years covered and update status:** 2014 to 2026; active [L11].
* **Unit:** Property tax assessment loan record [L11].
* **What is released:** Program information, financing terms (low-interest loans repaid via property tax bill for heat pumps, windows, insulation), and cumulative annual uptake summaries [L11]. Individual property loan records are confidential tax roll attachments and are not released on Toronto's open data portal [L11, INFERENCE].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Terms for linking:** Closed municipal tax roll attachment [L11, INFERENCE].
* **Licence name:** City of Toronto municipal records [L11].
* **Known bias:** Limited sample size (hundreds of loans per year relative to Toronto's hundreds of thousands of homes) [L11, INFERENCE].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 8: Independent Electricity System Operator (IESO) Save on Energy
* **Source name and custodian:** Save on Energy Energy Affordability Program; IESO [L12].
* **City or province:** Province of Ontario [L12].
* **Years covered and update status:** Ongoing provincial conservation demand management programs [L12].
* **Unit:** Participant rebate record [L12].
* **What is released:** Quarterly and annual provincial aggregate energy conservation reports; no public address-level database [L12].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Licence name:** Closed regulatory data [L12].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 9: British Columbia (CleanBC Better Homes)
* **Source name and custodian:** CleanBC Better Homes and Home Renovation Rebate Program; Province of British Columbia, BC Hydro, and FortisBC [L13].
* **City or province:** Province of British Columbia [L13].
* **Years covered and update status:** 2018 to 2026; active [L13].
* **Unit:** Rebate application record [L13].
* **What is released:** Program uptake summaries, regional totals, and rebate schedules for heat pumps, windows, and insulation; zero address-level records published [L13].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Terms for linking:** Closed utility and provincial administration [L13].
* **Licence name:** Closed government database [L13].
* **Verified research use:** NONE FOUND [L79, L80].

#### Card 10: Efficiency Nova Scotia, Efficiency Manitoba, and Energy Efficiency Alberta
* **Source name and custodian:** Provincial Efficiency Agencies: Efficiency Nova Scotia, Efficiency Manitoba, and Energy Efficiency Alberta (historical archive) [L14, L15, L16].
* **City or province:** Nova Scotia, Manitoba, Alberta [L14, L15, L16].
* **Years covered and update status:** Efficiency Nova Scotia (2010 to 2026), Efficiency Manitoba (2020 to 2026), Energy Efficiency Alberta (2017 to 2020, archived) [L14, L15, L16].
* **Unit:** Household efficiency rebate record [L14, L15, L16].
* **What is released:** All three agencies publish annual corporate reports with participant totals and provincial energy savings, but keep property-level heat-pump and insulation subsidies confidential [L14, L15, L16].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Licence name:** Closed provincial agency records [L14, L15, L16].
* **Verified research use:** NONE FOUND [L79, L80].

---

### Item 2. Aggregate check sources (role L3)

#### Card 11: Statistics Canada Households and Environment Survey (HES) - Air Conditioners
* **Source name and custodian:** Table 38-10-0019-01: Air conditioners; Environment and Energy Statistics Division, Statistics Canada [L30, L38].
* **Geography:** Canada, 10 provinces, and 33 Census Metropolitan Areas (56 geographic members, including Montreal CMA, Toronto CMA, Vancouver CMA, Calgary CMA, Edmonton CMA, Ottawa-Gatineau CMA, Winnipeg CMA, Quebec City CMA, Halifax CMA) [L38].
* **Years covered:** Biennial time series: 2013, 2015, 2017, 2019, 2021, and 2023 (archived predecessor covers 2007, 2009, 2011) [L38].
* **Smallest geography:** Census Metropolitan Area (CMA) [L38].
* **Exact table identifier:** Table 38-10-0019-01 (formerly CANSIM 153-0099; Product ID 38100019) [L30, L38].
* **What it contains:** Total households, percentage of households with central air conditioning, percentage with window or room air conditioning, percentage with heat pump used for cooling, and percentage with no air conditioning system [L38].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Access route:** Fully open via Statistics Canada Web Data Service (WDS) API and table viewer on www150.statcan.gc.ca [L30, L38].
* **Licence name:** Statistics Canada Open Licence [L38].

#### Card 12: Statistics Canada Households and Environment Survey (HES) - Primary Heating Systems
* **Source name and custodian:** Table 38-10-0286-01: Primary heating systems and type of energy; Environment and Energy Statistics Division, Statistics Canada [L31, L38].
* **Geography:** Canada, 10 provinces, and 33 Census Metropolitan Areas (56 geographic members) [L38].
* **Years covered:** Biennial time series: 2013, 2015, 2017, 2019, 2021, and 2023 [L38].
* **Smallest geography:** Census Metropolitan Area (CMA) [L38].
* **Exact table identifier:** Table 38-10-0286-01 (Product ID 38100286) [L31, L38].
* **What it contains:** Distribution of primary heating system types (forced-air furnace, electric baseboard, heat pump, boiler with radiators) cross-tabulated by principal heating energy source (natural gas, electricity, heating oil, wood) [L38].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Access route:** Fully open via Statistics Canada WDS API and table viewer [L31, L38].
* **Licence name:** Statistics Canada Open Licence [L38].

#### Card 13: Statistics Canada Survey of Household Spending (SHS) - Equipment Tables
* **Source name and custodian:** Table 11-10-0228-01: Dwelling characteristics and household equipment at time of interview; Income Statistics Division, Statistics Canada [L32, L38].
* **Geography:** Canada, 10 provinces, and 2 regional aggregates (13 geographic members) [L38].
* **Years covered:** Annual time series from 2010 to 2023 [L38].
* **Smallest geography:** Province [L38].
* **Exact table identifier:** Table 11-10-0228-01 (formerly CANSIM 203-0027; Product ID 11100228) [L32, L38].
* **What it contains:** Number and percentage of households reporting ownership of household equipment, including window air conditioners, central air conditioning systems, and heat pumps [L38].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Access route:** Fully open via Statistics Canada WDS API and table viewer [L32, L38].
* **Licence name:** Statistics Canada Open Licence [L38].

#### Card 14: Census of Canada Housing Data (Dwelling Characteristics)
* **Source name and custodian:** Census of Population 2021 (Form 2A-L, Questions E1-E10); Statistics Canada [L75, L76].
* **Geography:** Dissemination Block (DB), Dissemination Area (DA), Census Tract (CT), CMA, Canada [L76].
* **Years covered:** 2021 (and prior five-year cycles 2016, 2011, 2006) [L76].
* **Smallest geography:** Dissemination Block [L76].
* **Equipment content:** ZERO EQUIPMENT CONTENT. Questions E1 through E10 ask for tenure, rooms, bedrooms, period of construction, condition of dwelling, condominium status, and shelter costs (Question E9: annual payments for electricity, oil, gas, wood, and other fuels) [L75, L76]. No question asks about heating equipment type, heat pumps, air conditioning, or insulation [L75, L76].
* **Roles:** L4 (structural stock characteristics: vintage, dwelling type) [BRIEF s.10].
* **Access route:** Open profile tables and PUMF microdata [BRIEF s.3, L76].
* **Licence name:** Statistics Canada Open Licence [L76].

#### Card 15: NRCan Comprehensive Energy Use Database (CEUD) - Residential Sector Stocks
* **Source name and custodian:** Comprehensive Energy Use Database (CEUD); Office of Energy Efficiency, Natural Resources Canada [L34, L39, L40].
* **Geography:** Canada, 5 regions (Atlantic, Quebec, Ontario, Prairies, British Columbia) [L40, L67].
* **Years covered:** Annual time series from 1990 to 2022 [L40].
* **Smallest geography:** Province / Region [L40, L67].
* **Exact table identifiers:**
  * Table 27: `Heating System Stock by Building Type and Heating System Type` [L67].
  * Table 28: `Single Detached Heating System Stock by Heating System Type` [L68].
  * Table 33: `Cooling System Stock by Type, New Unit Efficiencies, Stock Efficiencies and Unit Capacity Ratio` [L73].
  * Table 20: `Total Households by Building Type and Principal Heating Energy Source` [L60].
* **What it contains:** Total stock counts (in thousands of units) of heat pumps (air-source and ground-source), electric baseboards, gas furnaces, oil furnaces, dual-fuel systems, central air conditioning, and room air conditioners, with stock efficiency ratings [L67, L68, L73].
* **Roles:** L3 (aggregate check) [BRIEF s.10].
* **Access route:** Open table query and Excel export on oee.nrcan.gc.ca [L34, L40].
* **Licence name:** Open Government Licence - Canada [L34].

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions, gaps, and open questions
* **Open data disclosure vs. Privacy Act:** There is a fundamental contradiction between the research desire for open per-building ground truth and Canadian privacy law [L18, L28, INFERENCE]. Under the federal Privacy Act, home energy audit results tied to civic addresses or full postal codes constitute protected personal information because an energy evaluation reveals indoor physical characteristics of an identifiable citizen's private residence [L18, L28, INFERENCE]. Consequently, no public open dataset in Canada will ever release address-level EnerGuide or rebate microdata without statutory legislative overhaul [L18, INFERENCE].
* **HES survey estimates vs. CEUD stock counts:** Statistics Canada HES Table 38-10-0019-01 and NRCan CEUD Table 33 occasionally report slightly divergent heat pump adoption shares for the same province [L38, L73]. This discrepancy occurs because HES measures household reporting of primary heating equipment, whereas CEUD uses a stock turnover accounting model that combines historical sales data, manufacturer shipments, and survey benchmarks [L38, L73, INFERENCE]. For 5J aggregate validation, HES survey estimates should be adopted for CMA-level targets because they directly sample real households in Montreal and Toronto [L38, INFERENCE].

### Answers to mandatory questions
1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full (or direct API metadata/table streams):* open.canada.ca EnerGuide package and schema description [L1, L2, L18], open.canada.ca Greener Homes search records [L3], NRCan Greener Homes program page [L4], NRCan OHPA program page [L5], Transition energetique Quebec Renoclimat and Chauffez vert pages [L6, L7], Hydro-Quebec LogisVert and open data pages [L8, L9], Enbridge HER+ page [L10], Toronto HELP page [L11], IESO Save on Energy page [L12], CleanBC Better Homes page [L13], Efficiency Nova Scotia page [L14], Efficiency Manitoba page [L15], Energy Efficiency Alberta archive [L16], Statistics Canada RDC holdings directory [L20], Mohareb, Gillich, Bristow (2022) full text in Buildings and Cities [L27, L28], Statistics Canada WDS API cube metadata for Tables 38-10-0019-01, 38-10-0286-01, and 11-10-0228-01 [L38], NRCan CEUD comprehensive tables menu and Tables 1 through 34 [L34, L39, L40, L41 to L74], and Statistics Canada Housing Reference Guide for Census 2021 [L75, L76]. Total count of documents/data tables opened in full: 26.
   * *Seen only described / abstract only:* Coyne & Denny (2021) [L117], Ali et al. (2019) [L119], Zhang et al. (2020) [L214].
2. **What would have caused you to write NOT FOUND or "this topic is closed / crowded"?**
   * NOT FOUND was written for municipal or utility heat-pump rebate lists published by address or full postal code, because zero utilities or municipalities in Canada publish identifiable address-level recipient lists [L8, L10, L11, L13, L14].
   * "Closed source" was written for ESA, TSSA, Technical Safety BC, Renoclimat microdata, and utility rebate databases because these systems are confidential regulatory or commercial customer repositories [L6, L8, L10, L182, L184, L185].
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   * Candidate angle A7 (validation of permit text NLP against audit ground truth) is NOT taken in Canada [L79, L80]. No prior Canadian study has evaluated language models on municipal permit descriptions against EnerGuide audits or HES survey truth [L79, L80, INFERENCE].
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   * No. All table numbers (38-10-0019-01, 38-10-0286-01, 11-10-0228-01, CEUD Tables 20, 27, 28, 33), cube dimensions, start/end dates, and audit sample figures (640,000 in ecoENERGY) were copied verbatim from logged API and document responses [L18, L28, L38, L67, L73].

## Section H. Full reference list

1. Natural Resources Canada (2026). EnerGuide Rating System Open Data. Open Government Portal. https://open.canada.ca/data/en/dataset/0a7619fd-2ffe-44b5-9027-3dfcec0866fd [L1, L2, L18]. Tier 1. Read dataset package metadata and open data dictionary.
2. Natural Resources Canada (2026). Canada Greener Homes Grant. https://natural-resources.canada.ca/energy-efficiency/homes/canada-greener-homes-initiative/canada-greener-homes-grant/23441 [L3, L4]. Tier 1. Read full program page.
3. Natural Resources Canada (2026). Oil to Heat Pump Affordability Program. https://natural-resources.canada.ca/energy-efficiency/homes/canada-greener-homes-initiative/oil-heat-pump-affordability-program/24775 [L5]. Tier 1. Read full program page.
4. Transition energetique Quebec (2026). Programme Renoclimat. https://transitionenergetique.gouv.qc.ca/residentiel/programmes/renoclimat [L6]. Tier 1. Read full program documentation.
5. Transition energetique Quebec (2026). Programme Chauffez vert. https://transitionenergetique.gouv.qc.ca/residentiel/programmes/chauffez-vert [L7]. Tier 1. Read full program documentation.
6. Hydro-Quebec (2026). Programme LogisVert. https://www.hydroquebec.com/residentiel/mieux-consommer/economiser-energie/logisvert/ [L8]. Tier 1. Read full program page.
7. Enbridge Gas (2026). Home Efficiency Rebate Plus (HER+). https://www.enbridgegas.com/sustainability-society/energy-efficiency/home-efficiency-rebate-plus [L10]. Tier 1. Read program details.
8. City of Toronto (2026). Home Energy Loan Program (HELP). https://www.toronto.ca/services-payments/water-environment/environmental-grants-incentives/home-energy-loan-program-help/ [L11]. Tier 1. Read program details.
9. Independent Electricity System Operator (2026). Save on Energy Programs. https://www.saveonenergy.ca/For-Your-Home [L12]. Tier 1. Read program page.
10. Province of British Columbia (2026). CleanBC Better Homes and Home Renovation Rebate Program. https://www.betterhomesbc.ca/rebates/ [L13]. Tier 1. Read program page.
11. Efficiency Nova Scotia (2026). Heat Pump Rebates and Financing. https://www.efficiencyns.ca/residential/products-rebates/heat-pumps/ [L14]. Tier 1. Read program page.
12. Statistics Canada (2026). Table 38-10-0019-01: Air conditioners. Households and the Environment Survey. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810001901 [L30, L38]. Tier 1. Read full table metadata and dimensions via WDS API.
13. Statistics Canada (2026). Table 38-10-0286-01: Primary heating systems and type of energy. Households and the Environment Survey. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810028601 [L31, L38]. Tier 1. Read full table metadata and dimensions via WDS API.
14. Statistics Canada (2026). Table 11-10-0228-01: Dwelling characteristics and household equipment at time of interview. Survey of Household Spending. https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1110022801 [L32, L38]. Tier 1. Read full table metadata and dimensions via WDS API.
15. Statistics Canada (2021). Housing Reference Guide, Census of Population, 2021. Catalogue no. 98-500-X2021005. https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/98-500-x2021005-eng.cfm [L75, L76]. Tier 1. Read reference guide sections on dwelling characteristics and shelter costs.
16. Natural Resources Canada (2026). Comprehensive Energy Use Database (CEUD), Residential Sector. Office of Energy Efficiency. https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm [L34, L39, L40, L67, L73]. Tier 1. Read comprehensive tables menu and Tables 20, 27, 28, 33.
17. Mohareb, Eugene; Gillich, Aaron; Bristow, David (2022). Participation in domestic energy retrofit programmes: key spatio-temporal drivers. Buildings and Cities, 3(1), 297-313. https://doi.org/10.5334/bc.202 [L27, L28]. CrossRef returned title: "Participation in domestic energy retrofit programmes: key spatio-temporal drivers". Tier 1. Read full text.
18. Coyne, Bryan; Denny, Eleanor (2021). Mind the Energy Performance Gap: testing the accuracy of building Energy Performance Certificates in Ireland. Energy Efficiency, 14(6), 62. https://doi.org/10.1007/s12053-021-09960-1 [L117]. CrossRef returned title: "Mind the Energy Performance Gap: testing the accuracy of building Energy Performance Certificates in Ireland". Tier 1. Read abstract.
19. Ali, Usman; Shamsi, Mohammad Haris; Hoare, Cathal; Alshehri, Fawaz; Mangina, Eleni; O'Donnell, James (2019). Application Of Intelligent Algorithms For Residential Building Energy Performance Rating Prediction. Building Simulation 2019, 210232. https://doi.org/10.26868/25222708.2019.210232 [L119]. CrossRef returned title: "Application Of Intelligent Algorithms For Residential Building Energy Performance Rating Prediction". Tier 2. Read abstract.
20. Zhang, Wanni; Hong, Tianzhen; Luo, Xuan (2020). Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History. Proceedings of SimAUD 2020. https://doi.org/10.26868/25746308.2020.c083 [L214]. CrossRef returned title: "Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History". Tier 2. Read abstract.
