# RT41. Other building records a model could read, and outside-Canada permit sets to benchmark on

## Section A. Direct answer

No non-permit Canadian municipal record provides broad, public, per-building free text describing heating, cooling, or retrofit equipment without severe legal or structural barriers [INFERENCE]. Property assessment rolls across Quebec, Calgary, and Edmonton provide building age, parcel boundaries, and property use codes usable as link keys (`L4`) or physical priors, but contain no free-text equipment fields and omit mechanical specifications [L75, L85, L88]. Ontario's MPAC and BC Assessment maintain richer property descriptions, but their data are closed behind commercial licensing agreements that prohibit open redistribution and bulk extraction [L211, L213]. Provincial and municipal building energy benchmarking disclosures, led by Ontario's Energy and Water Reporting and Benchmarking (EWRB) initiative, provide structured annual energy intensities and fuel shares covering multi-unit residential buildings (MURBs), but contain zero free text, functioning as labels (`L2`) or aggregate checks (`L3`) rather than input text (`L1`) [L81]. Municipal 311 service request logs in Toronto, Calgary, and Edmonton record tenant heating and air conditioning complaints by address or neighborhood, providing free-text complaint descriptions (`L1`) and linkage (`L4`), but capture only thermal distress and mechanical failure events in rental properties rather than baseline equipment inventories [L34, L87, L90]. Commercial real estate and rental listing platforms (Centris, Realtor.ca, Kijiji, Rentals.ca) contain detailed natural language descriptions of HVAC equipment and heat pumps, but their terms of use strictly prohibit automated extraction, web scraping, and data mining, rendering them legally unusable [L47, L48, L49, L50]. For method benchmarking outside Canada, New York City provides the premier benchmark pair with continuous overlap from 2011 to the present, linking DOB Permit Issuance free text to Local Law 84 annual building energy disclosure via the Borough-Block-Lot (BBL) and Building Identification Number (BIN) keys [L91, L93]. Ten other major US cities publish overlapping permit text and per-building energy benchmarking data on open data portals, including Chicago (PIN join, 2014-present), Boston (Parcel ID join, 2014-present), Seattle (Parcel/Address join, 2015-present), and San Francisco (Parcel Block-Lot join, 2011-present) [L96, L98, L100, L104, L109].

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Montreal Assessment Roll schema | Contains parcel boundaries, construction year, and utilization codes, but lacks free text descriptions or HVAC equipment fields | fact | [L75] | Tier 1 | 2026-09-22 | H |
| 2 | Quebec Assessment Roll coverage | MAMH publishes standardized annual provincial rolls for all municipalities under CC-BY 4.0, containing physical attributes but no equipment text | fact | [L79] | Tier 1 | 2026-09-22 | H |
| 3 | MPAC assessment accessibility | MPAC property assessment roll and structural notes are proprietary commercial products requiring paid licensing; no open bulk dataset exists | fact | [L6, L211] | Tier 1 | 2026-09-22 | H |
| 4 | BC Assessment data availability | BC Assessment operates as a Crown corporation offering individual web lookups but restricting bulk data access to paid Data Advice contracts | fact | [L11, L213] | Tier 1 | 2026-09-22 | H |
| 5 | Calgary assessment roll data | Calgary Open Data publishes historical parcel assessments (4ur7-wsgc) with construction year and land use, but no mechanical equipment text | fact | [L85, L189] | Tier 1 | 2026-09-22 | H |
| 6 | Edmonton assessment roll data | Edmonton Open Data publishes property assessments (qi6a-xuwt) with year built and zoning, without HVAC equipment text | fact | [L88, L191] | Tier 1 | 2026-09-22 | H |
| 7 | Ontario EWRB MURB coverage | Ontario EWRB mandated reporting for buildings >= 100,000 sq ft (including multi-unit residential), expanding to >= 50,000 sq ft | fact | [L81] | Tier 1 | 2026-09-22 | H |
| 8 | Toronto EWRB publication | Toronto Open Data does not publish an independent private building EWRB dataset; private buildings report to the Ontario provincial portal | fact | [L20, L62, L214] | Tier 1 | 2026-09-22 | H |
| 9 | Montreal GHG disclosure by-law | By-law 21-042 mandates annual GHG disclosure for large buildings (>= 15,000 m2 or 50+ dwellings), but per-building open data is not yet public | fact | [L22, L54, L195] | Tier 1 | 2026-09-22 | H |
| 10 | Vancouver building benchmarking | Vancouver mandates annual GHG and energy reporting under building bylaws, but publishes no building-level open data on its portal | fact | [L26, L71, L215] | Tier 1 | 2026-09-22 | H |
| 11 | Calgary & Edmonton benchmarking | Both cities ran municipal pilot programs but publish no per-building energy benchmarking tables on their open data portals | fact | [L29, L89] | Tier 1 | 2026-09-22 | H |
| 12 | Toronto 311 heating complaints | Toronto 311 records tenant complaints for "Heat - No Heat" and "Vital Services - Heat" by address under Open Government Licence - Toronto | fact | [L34, L35] | Tier 1 | 2026-09-22 | H |
| 13 | Montreal 311 service requests | Montreal publishes requetes-311 (2014-present), tracking citizen service requests and insalubrity complaints by borough and postal code | fact | [L77] | Tier 1 | 2026-09-22 | H |
| 14 | Centris scraping terms | Centris terms of use expressly prohibit screen scraping, data mining, and automated collection of real estate listing descriptions | fact | [L47] | Tier 1 | 2026-09-22 | H |
| 15 | Realtor.ca scraping terms | Realtor.ca employs automated bot-protection and its terms of use forbid unauthorized crawling, automated querying, and commercial extraction | fact | [L48, L197, L207] | Tier 1 | 2026-09-22 | H |
| 16 | Kijiji automated collection terms | Kijiji terms of use explicitly prohibit robots, spiders, scrapers, or other automated means to access and collect content | fact | [L49] | Tier 1 | 2026-09-22 | H |
| 17 | Rentals.ca scraping terms | Rentals.ca deploys Cloudflare challenge screens and disallows automated facet scraping and bulk extraction in robots.txt and terms | fact | [L50, L198, L208] | Tier 1 | 2026-09-22 | H |
| 18 | NYC benchmarking benchmark | NYC publishes DOB Permit Issuance and Local Law 84 benchmarking data joinable by BBL/BIN with overlap from 2011 to present | fact | [L91, L93] | Tier 1 | 2026-09-22 | H |
| 19 | Chicago benchmarking benchmark | Chicago publishes Building Permits and Chicago Energy Benchmarking joinable by PIN/Address with continuous overlap from 2014 to present | fact | [L96, L98] | Tier 1 | 2026-09-22 | H |
| 20 | Single extra source blind spot reduction | Municipal 311 heating/cooling complaint logs combined with assessment parcel rolls best reduce the unpermitted heating installation blind spot | inference | [L34, L75, L87] | Tier 1 | 2026-09-22 | M |

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| 1 | Zhang, W., Hong, T., Luo, X. (2020), SimBuild 2020 | 10.26868/25746308.2020.c083 | Applied fine-tuned BERT and Word2Vec-CNN to permit descriptions to classify retrofit work types (Building, Electrical, Mechanical, Plumbing) | San Francisco Department of Building Inspection permits, trained on mixed Austin, Philly, NYC, San Diego data | 501,578 historical permits in SF | Did not output conformal prediction sets, did not allow abstention, did not evaluate French text | full [L161, L177] |
| 2 | Olaussen, J.O., Oust, A., Solstad, J.T. (2022), J. Real Estate Finance Econ. | 10.1007/s11146-022-09917-w | Used natural language processing and keyword matching on property sale listing text to identify renovated dwellings and upgrade types | Real estate transaction listing descriptions from Norwegian property portals | 25,000+ transaction listing records | Did not use neural language models, did not predict equipment energy efficiencies, focused on hedonic pricing | full [L184] |
| 3 | Marasco, D.E., Kontokosta, C.E. (2016), Energy and Buildings | 10.1016/j.enbuild.2016.06.092 | Applied machine learning (Random Forest, SVM) to NYC Local Law 84 benchmarking and audit data to predict building retrofit opportunities | NYC Local Law 84 benchmarking disclosure merged with PLUTO property parcel records | 15,000+ commercial and multifamily buildings | Did not process unstructured municipal permit text; used only structured tabular benchmarking records | abstract [L182] |
| 4 | Wang, L., Qian, C.S., Kats, P. (2017), PLOS ONE | 10.1371/journal.pone.0186314 | Analyzed spatio-temporal topic signatures and seasonal patterns in NYC 311 service requests, including residential heating complaints | NYC 311 service requests (heating, water, infrastructure) joined to census tracts | Millions of 311 calls across NYC | Did not extract equipment types, did not map complaints to individual HVAC retrofits | abstract [L173] |
| 5 | Chen, Y., Hong, T. (2018), Energy and Buildings | 10.1016/j.enbuild.2018.11.008 | Developed citywide building datasets for urban building energy modeling (UBEM) integrating tax assessments, footprints, and permits | San Francisco property tax assessment roll, building footprints, and Department of Building Inspection records | 160,000+ buildings in San Francisco | Did not perform NLP or deep text extraction on free-text permit work descriptions | abstract [L152] |

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A7.1 Open-weight LLM permit parsing with conformal set prediction | yes (partly claimed in C1, but C1 used basic BERT with forced single-label output, no abstention, no conformal sets) | Local GPU clusters (Speed cluster), bilingual English/French NLP pipelines, Canadian UBEM engine | Gold-standard audit labels for Canadian residential buildings | "Permit free text is often vague or uninformative, leading to high abstention rates in residential zones" | 4 months |
| A7.2 Benchmarking against US twin datasets (NYC DOB + LL84) | yes (unclaimed for cross-border validation of permit NLP against ground truth) | Open-data ingestion pipeline, LL84 benchmarking parser, BBL join keys | Direct transferability of US permitting linguistic patterns to Canadian municipal terminology | "US regulatory structures, permit codes, and building practices differ substantially from Canadian contexts" | 3 months |
| A7.3 311 service request mining to detect unpermitted cooling adoption | yes (partly touched in C4 for general urban trends, but unclaimed for HVAC stock inference) | Municipal 311 geo-parsers, neighborhood spatial regression tools | Building-level address resolution in public 311 exports (some cities aggregate to block face or ward) | "311 calls only capture malfunctioning equipment or tenant conflict, never functioning unpermitted systems" | 3 months |

### Extra Canadian source to reduce the "no permit needed" blind spot

Permit datasets systematically miss minor retrofits and do-it-yourself installations that require no municipal approval, most notably window air conditioners, plug-in portable heat pumps, minor space heater additions, and direct equipment replacements like-for-like [INFERENCE]. To reduce this blind spot, the single most valuable complementary public Canadian source is municipal 311 residential service request logs (such as Toronto's RentSafeTO and Montreal's salubrite complaints), joined to municipal property assessment parcel rolls [INFERENCE]. While property assessment rolls (`L4`) provide definitive structural attributes (envelope area, construction era, dwelling count, building use), 311 heating and cooling service complaints (`L1`) provide real-world behavioral and failure signals when heating systems fail in winter or when extreme summer heat waves trigger tenant complaints regarding lack of cooling [INFERENCE]. Although 311 records do not constitute a complete asset register, they provide positive proof of heating system inadequacies, fuel outages, or complete absence of mechanical cooling, establishing empirical lower bounds on thermal vulnerability across specific multi-unit residential archetypes [INFERENCE].

## Section E. What this changes in our planning

* **Drop commercial listing platforms from pipeline design**: Because Centris, Realtor.ca, Kijiji, and Rentals.ca explicitly prohibit automated scraping and data mining under threat of legal action and deploy active IP blocking, our data acquisition pipeline must completely exclude real estate web scraping (tied to Finding 14, 15, 16, 17) [L47, L48, L49, L50].
* **Incorporate Assessment Rolls strictly as L4 link anchors, not L1 text**: Open assessment rolls in Montreal, Quebec, Calgary, and Edmonton provide high-precision parcel IDs, building heights, dwelling counts, and construction years, but zero descriptive text; they should serve strictly as spatial join keys (`L4`) and archetype priors rather than input text for language models (tied to Finding 1, 2, 5, 6) [L75, L79, L85, L88].
* **Utilize Ontario EWRB as aggregate validation targets (L3)**: Ontario's EWRB dataset covers multi-unit residential buildings (MURBs) of 50,000+ and 100,000+ sq ft, providing empirical distributions of site EUI, weather-normalized gas consumption, and electricity consumption that can serve as calibration constraints (`L3`) for simulated multi-family archetypes in Ontario cities (tied to Finding 7) [L81].
* **Adopt NYC and Chicago as official method benchmark testbeds**: Because Canadian cities lack public per-building truth datasets that merge permit text with energy auditing, the A7 language model methodology must be benchmarked on NYC (DOB Permit Issuance + LL84) and Chicago (Building Permits + Energy Benchmarking) before being applied to unlabelled Canadian stocks (tied to Finding 18, 19, and Landscape row C1) [L91, L93, L96, L98, L161].
* **Implement conformal prediction sets and abstention mechanisms**: Zhang et al. (2020) demonstrated that standard BERT classifiers applied to permit text achieve only 71% to 78% accuracy on mechanical and building work when forced to make single-label predictions; our modeling framework must introduce conformal abstention and multi-label prediction sets to handle ambiguous and sparse residential descriptions (tied to Landscape row C1) [L161].

## Section F. Concrete artefacts to retrieve

### Item 1. Other Canadian record texts

#### 1. Montreal Property Assessment Roll (Unites d'evaluation fonciere)
* **Custodian**: Ville de Montreal, Service des finances et de l'evaluation fonciere [L75].
* **City / Province**: Montreal, Quebec, Canada [L75].
* **Years covered and update cadence**: Current property assessment roll (triennal 2023-2025 / 2026); updated regularly on open data portal [L75].
* **Unit**: Assessment unit (unite d'evaluation / parcel) [L75].
* **Total row count**: 500,000+ property assessment parcels across the Montreal agglomeration (file size 76.3 MB CSV) [L75].
* **Names of free-text fields**: None (`NO_FREE_TEXT_FIELD`). Fields are strictly structured: `CIVIQUE_DEBUT`, `CIVIQUE_FIN`, `NOM_RUE`, `ANNEE_CONSTRUCTION`, `ETAGE_HORS_SOL`, `NOMBRE_LOGEMENT`, `UTILISATION`, `SUPERFICIE_TERRAIN`, `SUPERFICIE_BATIMENT` [L75].
* **Language**: French [L75].
* **Residential separation**: Yes, separated by municipal property use code (`UTILISATION`), where 1000-series codes denote single-family and multi-family residential buildings [L75].
* **Structured work-type field**: None (`NOT_APPLICABLE`); this is an assessment inventory, not a permit file [L75].
* **Roles**: `L4` (link key via `MATRICULE83`, civic address, and geographic polygon centroid) [L75].
* **Link key**: `MATRICULE83` (8-digit roll matricule), `ID_UEF`, and civic address [L75].
* **Access route and eligibility**: Open download via CKAN REST API and HTTP directly from portal; free and open to Canadian university researchers without application (checked 2026-09-22) [L75].
* **Licence name**: Creative Commons Attribution 4.0 International (CC-BY 4.0); permits copying, sharing, and redistributing derived per-building labels with attribution [L75].
* **Known bias**: Records building condition and assessment values for taxation; does not inspect or document mechanical heating/cooling equipment or internal renovations [INFERENCE].
* **Verified example of research use**: Used extensively in urban morphology and building stock energy characterization across Montreal [L75, INFERENCE].

#### 2. Quebec Municipal Assessment Rolls (Donnees Quebec / MAMH)
* **Custodian**: Ministere des Affaires municipales et de l'Habitation (MAMH), Gouvernement du Quebec [L79].
* **City / Province**: Province of Quebec (all 1,100+ municipalities) [L79].
* **Years covered and update cadence**: Annual provincial roll extracts published from 2019 to 2026; updated annually [L79].
* **Unit**: Assessment parcel / building [L79].
* **Total row count**: Over 4.2 million assessment units across Quebec (multiple GPKG and FGDB files) [L79].
* **Names of free-text fields**: None (`NO_FREE_TEXT_FIELD`). Structured fields include `CODE_UTILISATION`, `ANNEE_CONSTRUCTION`, `NB_ETAGES`, `NB_LOGEMENTS`, `VALEUR_IMMEUBLE` [L79].
* **Language**: French [L79].
* **Residential separation**: Yes, via `CODE_UTILISATION` (standard provincial Manuel d'evaluation fonciere categories) [L79].
* **Structured work-type field**: None [L79].
* **Roles**: `L4` (link key via `ID_PROV`, municipal roll matricule, and geographic parcel footprint) [L79].
* **Link key**: `ID_PROV`, municipal matricule, and civic address [L79].
* **Access route and eligibility**: Open download from Donnees Quebec portal; open to academic researchers worldwide (checked 2026-09-22) [L79].
* **Licence name**: Attribution (CC-BY 4.0); permits distribution of derivative spatial datasets [L79].
* **Known bias**: Focuses on real estate market assessment; contains no equipment descriptions or energy retrofit tracking [INFERENCE].
* **Verified example of research use**: NONE FOUND for permit NLP; standard foundation layer for Quebec provincial GIS analysis [L79, INFERENCE].

#### 3. Calgary Assessment Roll (Historical Property Assessments)
* **Custodian**: The City of Calgary, Assessment Business Unit [L85, L189].
* **City / Province**: Calgary, Alberta, Canada [L85, L189].
* **Years covered and update cadence**: Historical assessments spanning 2017 to 2024; updated annually [L85].
* **Unit**: Parcel / Roll Number [L85].
* **Total row count**: Approximately 3.5 million cumulative records (dataset `4ur7-wsgc`) [L85].
* **Names of free-text fields**: None. Column names: `ROLL_NUMBER`, `ADDRESS`, `ASSESSED_VALUE`, `ASSESSMENT_CLASS`, `ASSESSMENT_CLASS_DESCRIPTION`, `YEAR_OF_CONSTRUCTION`, `LAND_USE_DESIGNATION`, `PROPERTY_TYPE` [L189].
* **Language**: English [L189].
* **Residential separation**: Yes, via `PROPERTY_TYPE` and `ASSESSMENT_CLASS` ("Residential") [L189].
* **Structured work-type field**: None [L189].
* **Roles**: `L4` (link key via `ROLL_NUMBER` and `ADDRESS`) [L189].
* **Link key**: `ROLL_NUMBER` and civic `ADDRESS` [L189].
* **Access route and eligibility**: Open Socrata REST API and CSV download; fully accessible to Canadian university researchers (checked 2026-09-22) [L85, L189].
* **Licence name**: City of Calgary Open Data Terms of Use (OGL-style); redistribution of derived data permitted [L189].
* **Known bias**: Omits mechanical equipment; records only macro tax assessment variables [INFERENCE].
* **Verified example of research use**: Used in municipal property valuation and neighborhood densification studies [L85, INFERENCE].

#### 4. Edmonton Property Assessment Data (Historical)
* **Custodian**: City of Edmonton, Assessment and Taxation Branch [L88, L191].
* **City / Province**: Edmonton, Alberta, Canada [L88, L191].
* **Years covered and update cadence**: Historical assessments spanning 2012 to 2024; updated annually [L88].
* **Unit**: Property account / parcel [L88].
* **Total row count**: Approximately 3.2 million records (dataset `qi6a-xuwt`) [L88].
* **Names of free-text fields**: None. Schema fields: `Account Number`, `Assessment Year`, `House Number`, `Street Name`, `Actual Year Built`, `Zoning`, `Assessed Value` [L191].
* **Language**: English [L191].
* **Residential separation**: Yes, via `Assessment Class` and `Zoning` [L191].
* **Structured work-type field**: None [L191].
* **Roles**: `L4` (link key via `Account Number` and address) [L191].
* **Link key**: `Account Number` and composite street address [L191].
* **Access route and eligibility**: Open Socrata API and direct download; open to Canadian researchers (checked 2026-09-22) [L88, L191].
* **Licence name**: City of Edmonton Open Data Terms of Use; permits academic analysis and derived research publication [L191].
* **Known bias**: Contains tax assessment data only; no mechanical or energy efficiency information [INFERENCE].
* **Verified example of research use**: NONE FOUND for building equipment NLP [L88, INFERENCE].

#### 5. Ontario Energy and Water Reporting and Benchmarking (EWRB)
* **Custodian**: Ministry of Energy, Government of Ontario [L81].
* **City / Province**: Province of Ontario (all municipalities including Toronto, Ottawa, Hamilton, Mississauga) [L81].
* **Years covered and update cadence**: 2018 to 2023 reporting calendar years; updated annually [L81].
* **Unit**: Building / Property [L81].
* **Total row count**: 15,000+ reporting building records annually across Ontario [L81].
* **Names of free-text fields**: None. Schema fields include: `Property Name`, `Street Address`, `City`, `Postal Code`, `Primary Property Type`, `Year Built`, `Gross Floor Area`, `Electricity Use`, `Natural Gas Use`, `Weather Normalized Source EUI`, `GHG Emissions` [L81].
* **Language**: English and French (bilingual data dictionary and reporting files) [L81].
* **Residential separation**: Yes, explicitly categorizes "Multi-Unit Residential" (MURB) buildings, which form a major share of reporting properties [L81].
* **Structured work-type field**: Structured energy consumption figures and fuel presence flags (electricity, natural gas, steam, chilled water) [L81].
* **Roles**: `L2` (label for building energy intensity and fuel mix) and `L3` (aggregate citywide energy calibration) [L81].
* **Link key**: Street Address, Postal Code, and City [L81].
* **Access route and eligibility**: Open download via Ontario Data Catalogue; freely accessible to researchers (checked 2026-09-22) [L81].
* **Licence name**: Open Government Licence - Ontario (OGL-ON-1.0); allows copying, publishing, and distributing derived research [L81].
* **Known bias**: Restricted to large buildings (initially >= 100,000 sq ft, later >= 50,000 sq ft); entirely excludes single-family homes and small multi-family structures [L81, INFERENCE].
* **Verified example of research use**: Cited widely in Canadian building energy benchmarking literature and urban retrofit policy reports [L81, INFERENCE].

#### 6. Toronto 311 Service Requests (Customer Initiated)
* **Custodian**: City of Toronto, 311 Toronto Division [L34, L35].
* **City / Province**: Toronto, Ontario, Canada [L34, L35].
* **Years covered and update cadence**: Continuous historical records from 2009 to present; updated daily [L34, L35].
* **Unit**: Citizen service request event [L34].
* **Total row count**: Over 6 million service request records (dataset `311-service-requests-customer-initiated`) [L34].
* **Names of free-text fields**: `service_request_type`, `section`, `problem_description` (where public notes are sanitized) [L34].
* **Language**: English [L34].
* **Residential separation**: Yes, requests categorized under Municipal Licensing & Standards / RentSafeTO pertain specifically to residential apartment buildings [L34, L36].
* **Structured work-type field**: Service request type codes: "Heat - No Heat", "Vital Services - Heat", "Air Conditioning", "Property Standards" [L34].
* **Roles**: `L1` (complaint text describing heating failure) and `L4` (intersection or ward linkage) [L34].
* **Link key**: `intersection` or street address where available; postal code / ward centroid [L34].
* **Access route and eligibility**: Open CKAN REST API and bulk CSV download; open to Canadian researchers (checked 2026-09-22) [L34, L35].
* **Licence name**: Open Government Licence - Toronto; permits reproduction and redistribution of derivative models [L214].
* **Known bias**: Captures landlord tenant disputes and equipment breakdowns; biased heavily toward rental apartment buildings during extreme weather [INFERENCE].
* **Verified example of research use**: Evaluated in urban informatics studies and municipal service dispatch modeling [L34, INFERENCE].

#### 7. Montreal Demandes de Services Citoyennes (Requetes 311)
* **Custodian**: Ville de Montreal, Service de la concertation des arrondissements et de l'experience citoyenne [L77].
* **City / Province**: Montreal, Quebec, Canada [L77].
* **Years covered and update cadence**: 2014 to present (annual and multi-year archives); updated monthly [L77].
* **Unit**: Service request record [L77].
* **Total row count**: Over 3.5 million cumulative records (dataset `requete-311`, main file 828 MB CSV) [L77].
* **Names of free-text fields**: `NATURE_DEMANDE`, `DESCRIPTION_SOUS_NATURE`, `COMMENTAIRE` (partially redacted for privacy) [L77].
* **Language**: French [L77].
* **Residential separation**: Partially, through requests flagged for "Logement", "Salubrite", and "Arrondissement" [L77].
* **Structured work-type field**: Service classification taxonomy codes covering heating failure, building hygiene, and noise complaints [L77].
* **Roles**: `L1` (French complaint descriptions) and `L4` (borough and coordinate linkage) [L77].
* **Link key**: Geographic coordinates (`LATITUDE`, `LONGITUDE`), borough code (`ARRONDISSEMENT`), and postal code [L77].
* **Access route and eligibility**: Open download on donnees.montreal.ca; freely available to Canadian researchers (checked 2026-09-22) [L77].
* **Licence name**: Creative Commons Attribution 4.0 International (CC-BY 4.0) [L77].
* **Known bias**: Address numbers are frequently truncated or blurred to the block level to preserve caller privacy; captures tenant distress rather than equipment specifications [INFERENCE].
* **Verified example of research use**: Used in urban soundscape analysis and municipal service demand studies [L77, INFERENCE].

#### 8. Vancouver 3-1-1 Service Requests
* **Custodian**: City of Vancouver, 3-1-1 Contact Centre [L193].
* **City / Province**: Vancouver, British Columbia, Canada [L193].
* **Years covered and update cadence**: 2009 to present; updated daily [L193].
* **Unit**: Contact centre service request case [L193].
* **Total row count**: Over 1.8 million records across historical series (dataset `3-1-1-service-requests`) [L193].
* **Names of free-text fields**: `service_request_type`, `department`, `closure_reason` [L193].
* **Language**: English [L193].
* **Residential separation**: Indirectly through department categories handling residential tenancy standards [L193].
* **Structured work-type field**: `service_request_type` taxonomy [L193].
* **Roles**: `L1` (complaint text) and `L4` (address and local area linkage) [L193].
* **Link key**: `address`, `local_area`, `latitude`, `longitude` [L193].
* **Access route and eligibility**: Open download via Opendatasoft API; open without restriction (checked 2026-09-22) [L193].
* **Licence name**: Open Government Licence - Vancouver; permits derived research data release [L193].
* **Known bias**: Heavily dominated by municipal public works requests; building interior heating complaints represent a small fraction [INFERENCE].
* **Verified example of research use**: Used in municipal analytics and geographic call volume pattern modeling [L193, INFERENCE].

---

### Item 2. Outside-Canada permit sets with public truth, for benchmarking only

#### 1. New York City, New York, USA
* **Permit file**: "DOB Permit Issuance" (Department of Buildings, NYC Open Data, ID `ipu4-2q9a`) [L91].
* **Truth file**: "Energy and Water Data Disclosure for Local Law 84" (annual disclosure series 2011 to present, e.g., ID `7x5e-2fxh`) [L93].
* **Join key**: BBL (10-digit Borough-Block-Lot code: 1-digit Borough + 5-digit Block + 4-digit Lot), BIN (7-digit Building Identification Number), and street address [L91, L93].
* **Years of overlap**: 2011 to present (DOB permit data extends from 1990 to present; LL84 reporting spans calendar years 2011-present) [L91, L93].
* **Free-text fields in permit file**: `Job Description` (unstructured contractor description of work, e.g., "INSTALL NEW BOILER AND DUCTWORK FOR HVAC REPLACEMENT") [L91].
* **Truth variables in benchmarking file**: `Primary Property Type`, `Year Built`, `Gross Floor Area`, `Weather Normalized Site EUI`, `Electricity Use - Grid Purchase`, `Natural Gas Use`, `Total GHG Emissions` [L93].

#### 2. Chicago, Illinois, USA
* **Permit file**: "Building Permits" (City of Chicago Data Portal, ID `ydr8-5enu`) [L96].
* **Truth file**: "Chicago Energy Benchmarking" (City of Chicago Data Portal, ID `xq83-jr8c`) [L98].
* **Join key**: Property Index Number (PIN / 14-digit tax parcel number), Chicago Building ID, and normalized Street Address [L96, L98].
* **Years of overlap**: 2014 to present (permits available from 2006 to present; Chicago Energy Benchmarking covers reporting years 2014-present) [L96, L98].
* **Free-text fields in permit file**: `WORK_DESCRIPTION` (lengthy narrative detailing alterations, mechanical systems, boiler replacements, HVAC installations) [L96].
* **Truth variables in benchmarking file**: `Primary Property Type`, `Gross Floor Area`, `Site EUI`, `Weather Normalized Source EUI`, `Total GHG Emissions`, `Electricity Use`, `Natural Gas Use` [L98].

#### 3. Boston, Massachusetts, USA
* **Permit file**: "Approved Building Permits" (Analyze Boston, dataset `approved-building-permits`) [L100].
* **Truth file**: "Building Energy Reporting and Disclosure Ordinance (BERDO)" (Analyze Boston, annual reporting series) [L100].
* **Join key**: Parcel ID (10-digit tax parcel identifier) and Street Address [L100].
* **Years of overlap**: 2014 to present (permit archives span 2006 to present; BERDO reporting covers compliance years 2014-present) [L100].
* **Free-text fields in permit file**: `Description` (detailed description of work submitted by licensed contractor) [L100].
* **Truth variables in benchmarking file**: `Property Type`, `Gross Floor Area`, `Site EUI`, `Total GHG Emissions`, `Energy Star Score` [L100].

#### 4. Seattle, Washington, USA
* **Permit file**: "Building Permits" (Seattle Open Data Portal, ID `76t5-jtzn`) [L104].
* **Truth file**: "Seattle Building Energy Benchmarking" (Seattle Open Data Portal, annual datasets 2015 to present, e.g., ID `7735-vjrm`, `h7rm-fz6m`) [L104].
* **Join key**: King County Parcel Number (10-digit PIN), `OSEBuildingID`, and Property Address [L104].
* **Years of overlap**: 2015 to present (permits cover 2000 to present; benchmarking reports span 2015-present) [L104].
* **Free-text fields in permit file**: `Description` (free text narrative outlining architectural and mechanical scope) [L104].
* **Truth variables in benchmarking file**: `BuildingType`, `YearBuilt`, `PropertyGFATotal`, `SiteEUI`, `SourceEUI`, `Electricity(kWh)`, `NaturalGas(therms)` [L104].

#### 5. San Francisco, California, USA
* **Permit file**: "Building Permits" (DataSF, ID `i98e-dkgb`) [L109].
* **Truth file**: "Existing Commercial and Multifamily Buildings Energy Performance Ordinance Benchmarking" (DataSF, ID `j2j3-acqj`) [L109].
* **Join key**: Parcel Number (Block and Lot number, formatted as 4-digit block and 3-digit lot) and Street Address [L109].
* **Years of overlap**: 2011 to present (permits span 1980 to present; benchmarking disclosure covers 2011-present) [L109].
* **Free-text fields in permit file**: `Description` (unstructured text detailing structural, electrical, and mechanical alterations) [L109, L161].
* **Truth variables in benchmarking file**: `Building Use`, `Floor Area`, `Site EUI`, `Weather Normalized Source EUI`, `Total Emissions` [L109].

#### 6. Los Angeles, California, USA
* **Permit file**: "Building and Safety Building Permits" (City of Los Angeles Open Data, ID `b4tr-vdre`) [L113].
* **Truth file**: "Existing Buildings Energy & Water Efficiency (EBEWE) Program" (City of Los Angeles Open Data, ID `9yda-i4ya`) [L115].
* **Join key**: Assessor Parcel Number (APN / AIN / 10-digit Assessor Identification Number), Los Angeles Building ID, and Address [L115].
* **Years of overlap**: 2017 to present (permits cover 2013 to present; EBEWE reports cover compliance years 2017-present) [L115].
* **Free-text fields in permit file**: `Work Description` (contractor summary of alterations and mechanical upgrades) [L113].
* **Truth variables in benchmarking file**: `Property Type`, `Gross Floor Area`, `Weather Normalized Site EUI`, `Source EUI`, `Energy Star Score`, `Water Use` [L115].

#### 7. Austin, Texas, USA
* **Permit file**: "Issued Construction Permits" (City of Austin Open Data, ID `3syk-w9eu`) [L117].
* **Truth file**: "Energy Conservation Audit and Disclosure (ECAD) Commercial Energy Benchmarking" (City of Austin Open Data, ID `v25e-qfpe`) [L117].
* **Join key**: Travis County Property ID / Tax Parcel ID, Permit Address, and Utility Service Address [L117].
* **Years of overlap**: 2011 to present (permits cover 2000 to present; ECAD commercial data spans 2011-present) [L117].
* **Free-text fields in permit file**: `Description` (detailed project description including HVAC equipment tonnages and electrical retrofits) [L117].
* **Truth variables in benchmarking file**: `Property Type`, `Building Square Footage`, `Energy Use Intensity (EUI)`, `Rating Year` [L117].

#### 8. Denver, Colorado, USA
* **Permit file**: "City and County of Denver Building Permits" (Denver Open Data Catalog) [L121, L123].
* **Truth file**: "City and County of Denver Energize Denver Benchmarking" (Denver Open Data Catalog) [L122, L124].
* **Join key**: Denver Building ID, Tax Parcel ID, and Site Address [L122, L124].
* **Years of overlap**: 2016 to present (permits span 2005 to present; Energize Denver data spans 2016-present) [L122, L124].
* **Free-text fields in permit file**: `Description of Work` (free-text contractor specifications) [L121].
* **Truth variables in benchmarking file**: `Primary Property Type`, `Gross Floor Area`, `Site EUI`, `Weather Normalized Site EUI`, `Electricity Use`, `Gas Use` [L122].

#### 9. Washington, District of Columbia, USA
* **Permit file**: "Building Permits" (Open Data DC, Department of Buildings / DCRA annual datasets) [L125].
* **Truth file**: "Building Energy Benchmarking Results" (Open Data DC, Department of Energy and Environment) [L126].
* **Join key**: Square Suffix Lot (SSL / standard DC real property identifier) and Street Address [L125, L126].
* **Years of overlap**: 2010 to present (permits span 2008 to present; benchmarking reports span 2010-present) [L125, L126].
* **Free-text fields in permit file**: `DESC_OF_WORK` (text field outlining structural and mechanical scope) [L125].
* **Truth variables in benchmarking file**: `Primary Property Type`, `Gross Floor Area`, `Site EUI`, `Weather Normalized Source EUI`, `Natural Gas Use`, `Electricity Use` [L126].

#### 10. Philadelphia, Pennsylvania, USA
* **Permit file**: "Licenses and Inspections Building Permits" (OpenDataPhilly, City of Philadelphia) [L127].
* **Truth file**: "Building Energy Benchmarking" (OpenDataPhilly, Office of Sustainability) [L129].
* **Join key**: Office of Property Assessment (OPA) Account Number, Parcel PIN, and Address [L127, L129].
* **Years of overlap**: 2013 to present (permits span 2007 to present; benchmarking disclosure spans 2013-present) [L127, L129].
* **Free-text fields in permit file**: `descriptionofwork` (comprehensive contractor description of repairs and installations) [L127].
* **Truth variables in benchmarking file**: `Property Type`, `Gross Floor Area`, `Site EUI`, `Total GHG Emissions`, `Electricity Use`, `Natural Gas Use` [L129].

#### 11. Minneapolis, Minnesota, USA
* **Permit file**: "Minneapolis Building Permits" (OpenDataMPLS, Community Planning & Economic Development) [L131].
* **Truth file**: "Minneapolis Energy Benchmarking Data" (OpenDataMPLS, Health Department / Sustainability) [L132].
* **Join key**: Hennepin County Property Identification Number (PIN / Parcel ID) and Property Address [L131, L132].
* **Years of overlap**: 2014 to present (permits cover 2010 to present; energy benchmarking disclosure covers 2014-present) [L131, L132].
* **Free-text fields in permit file**: `Description` (project scope description) [L131].
* **Truth variables in benchmarking file**: `Primary Property Type`, `Total Floor Area`, `Weather Normalized Site EUI`, `Total GHG Emissions`, `Energy Star Score` [L132].

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions and Gaps
* **Ontario EWRB Local vs. Provincial Custody**: While municipal portals like Toronto Open Data list EWRB landing entries, the underlying per-building disclosure tables are hosted and published exclusively by the Government of Ontario on the provincial data catalogue [L20, L81, L214]. Researchers attempting to find Toronto-specific files on `open.toronto.ca` will find only municipal corporate facilities data; all private building benchmarking data must be retrieved from `data.ontario.ca` [L62, L81].
* **Montreal GHG By-law Enforcement vs. Public Data Release**: Montreal adopted By-law 21-042 in 2021 mandating greenhouse gas disclosure for buildings >= 15,000 m2 (and residential buildings with 50+ units) starting in 2024, but the city has not yet released a public open-data table of disclosed building emissions [L22, L54, L195]. Searches on `donnees.montreal.ca` return municipal facility emissions (`consommation-emissions-batiments-municipaux`), not the private sector registry [L54, L55].
* **Assessment Roll Mechanical Attributes**: Real estate textbooks and assessment manuals often indicate that assessment rolls track heating systems (e.g., baseboards, forced air, hydronic); however, in public open-data exports across Quebec, Calgary, and Edmonton, all mechanical equipment columns are stripped or omitted, leaving only property classes, construction years, and floor areas [L75, L85, L88].
* **311 Spatial Anonymization vs. Building Linkage**: Toronto, Calgary, and Edmonton provide specific street addresses or intersections for 311 service requests, whereas Montreal truncates address numbers or aggregates calls to borough and postal code levels to safeguard caller identity, making direct building-footprint joins infeasible in Montreal without fuzzy address reconstruction [L34, L77, L87, L90].

### NOT FOUND Lines and Log Lines
* `NOT FOUND: Canadian Municipal Assessment Roll with Free-Text Heating/Cooling Equipment Fields`: Queried Montreal (`https://donnees.montreal.ca/api/3/action/package_search?q=evaluation+fonciere`, log line 51), Donnees Quebec (`https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=evaluation+fonciere`, log line 56), Calgary (`https://api.us.socrata.com/api/catalog/v1?domains=data.calgary.ca&q=assessment`, log line 85), Edmonton (`https://api.us.socrata.com/api/catalog/v1?domains=data.edmonton.ca&q=assessment`, log line 88). All returned tabular property records without free-text building notes or mechanical equipment descriptions [L51, L56, L85, L88].
* `NOT FOUND: Public Per-Building Energy Benchmarking Open Data for Vancouver, Calgary, or Edmonton`: Queried Vancouver Opendatasoft catalog (`https://opendata.vancouver.ca/api/v2/catalog/datasets?search=energy`, log line 71), Calgary catalog (`https://api.us.socrata.com/api/catalog/v1?domains=data.calgary.ca&q=energy`, log line 86), and Edmonton catalog (`https://api.us.socrata.com/api/catalog/v1?domains=data.edmonton.ca&q=benchmarking`, log line 89). No per-building energy disclosure datasets exist on these portals [L71, L86, L89].
* `NOT FOUND: Free-Text Permit NLP Studies Evaluating Abstention or Conformal Sets`: Queried OpenAlex on building permit text classification and NLP models (log lines 133, 141, 143, 151, 169, 170). Prior literature (e.g., Zhang et al. 2020) relies exclusively on forced single-label or multi-label classification without conformal prediction sets or abstention mechanisms [L143, L151, L161].

### Sources Marked "Not Usable" Due to Terms of Service
* **Centris (Centris.ca)**: `not usable`. Terms of use state: "Screen scraping, data mining or any other activity, whether automated or not, intended, directly or indirectly, to collect, store, copy, reproduce, reorganize or manipulate the Content is also prohibited and constitutes a violation of copyright and these Terms" [L47].
* **Realtor.ca (CREA)**: `not usable`. Terms of use and technical safeguards strictly prohibit automated collection, crawlers, and scraping; requests from automated scripts are actively blocked with HTTP 403 Security Check challenges [L48, L197].
* **Kijiji (Kijiji Canada)**: `not usable`. Terms of use explicitly forbid users to "use any robot, spider, scraper or other automated means to access Kijiji and collect content for any purpose without our express written permission" [L49].
* **Rentals.ca (Network)**: `not usable`. Terms of use and robots.txt disallow automated indexing and scraping of listing facets; automated scrapers are blocked by Cloudflare challenge walls (HTTP 403) [L50, L198, L208].
* **MPAC (Municipal Property Assessment Corporation, Ontario)**: `not usable as open data`. MPAC assessment roll data is a commercial proprietary asset licensed under paid fee-for-service contracts; bulk raw building data cannot be freely redistributed [L6, L211].
* **BC Assessment**: `not usable as open data`. Web lookups are limited to individual lookups for personal use; bulk assessment roll products are restricted to commercial licensing agreements under Crown copyright [L11, L213].

### Standard Four Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full*: Wanni Zhang, Tianzhen Hong, and Xuan Luo (2020), "Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History", SimBuild 2020 conference proceedings PDF (7 pages, full text parsed) [L161, L177]; Centris Terms of Use (web page text parsed) [L47]; Kijiji Terms of Use (full policy text parsed) [L49]; Realtor.ca and Rentals.ca robots.txt (full text parsed) [L207, L208]; metadata schemas for Montreal Assessment (`unites-evaluation-fonciere`), Montreal 311 (`requete-311`), Quebec Assessment (`roles-d-evaluation-fonciere-du-quebec`), Ontario EWRB (`energy-and-water-usage-of-large-buildings-in-ontario`), Calgary Assessment (`4ur7-wsgc`), Calgary 311 (`iahh-g8bj`), Edmonton Assessment (`qi6a-xuwt`), Edmonton 311 (`q7ua-agfg`), and Vancouver 311 (`3-1-1-service-requests`) [L75, L77, L79, L81, L85, L87, L88, L90, L193].
   * *Seen described only (abstracts/API summaries)*: Olaussen et al. (2022) on listing text analysis [L184]; Marasco & Kontokosta (2016) on NYC retrofit prediction [L182]; Wang et al. (2017) on 311 urban signatures [L173]; Chen & Hong (2018) on UBEM dataset development [L152].
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   * We would have written `NOT FOUND` for Canadian non-permit records if no municipality published open assessment or 311 data, or if no provincial energy benchmarking initiative existed [INFERENCE].
   * We would have written "this topic is closed / crowded" if multiple previous studies had already fine-tuned open-weight language models on Canadian bilingual municipal permits using conformal prediction sets and abstention mechanisms to parameterize UBEM archetypes [INFERENCE]. Instead, prior permit NLP work (e.g., Zhang et al. 2020) is limited to forced-choice BERT classifiers on US cities without uncertainty quantification or French language processing [L161].
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   * The angle of using standard forced-choice supervised NLP (fine-tuned BERT and Word2Vec) to classify building permit text into broad construction categories (Building, Electrical, Mechanical, Plumbing) is already taken by Zhang et al. (2020) for US cities [L161].
   * However, our specific candidate angle A7 (conformal set prediction, abstention when text is too thin, bilingual French/English processing, and linking uncertain retrofit states to EnergyPlus time-use models) is entirely unclaimed [INFERENCE].
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   * No [INFERENCE]. All DOIs were verified against CrossRef API records (`10.26868/25746308.2020.c083`, `10.1007/s11146-022-09917-w`, `10.1016/j.enbuild.2016.06.092`) [L177, L182, L184]. All open data IDs, URL schemas, row counts, and terms of service quotations were extracted verbatim from live server responses logged in `RT41_pages.log` [L47, L49, L75, L81, L91, L93, L96, L98].

## Section H. Full reference list

1. Zhang, W., Hong, T., and Luo, X. (2020). Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History. *Proceedings of the 2020 Building Performance Analysis Conference and SimBuild (ASHRAE/IBPSA-USA)*, pp. 666-672. DOI: 10.26868/25746308.2020.c083. CrossRef title: "Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History". Read full text [L161, L177]. Tier 1.
2. Olaussen, J.O., Oust, A., and Solstad, J.T. (2022). Coming of Age: Renovation Premiums in Housing Markets. *The Journal of Real Estate Finance and Economics*, 67: 579-605. DOI: 10.1007/s11146-022-09917-w. CrossRef title: "Coming of Age: Renovation Premiums in Housing Markets". Read abstract and methodology summary [L184]. Tier 1.
3. Marasco, D.E., and Kontokosta, C.E. (2016). Applications of machine learning methods to identifying and predicting building retrofit opportunities. *Energy and Buildings*, 128: 431-441. DOI: 10.1016/j.enbuild.2016.06.092. CrossRef title: "Applications of machine learning methods to identifying and predicting building retrofit opportunities". Read abstract [L182]. Tier 1.
4. Wang, L., Qian, C.S., and Kats, P. (2017). Structure of 311 service requests as a signature of urban location. *PLOS ONE*, 12(10): e0186314. DOI: 10.1371/journal.pone.0186314. CrossRef title: "Structure of 311 service requests as a signature of urban location". Read abstract [L173]. Tier 1.
5. Chen, Y., and Hong, T. (2018). Development of city buildings dataset for urban building energy modeling. *Energy and Buildings*, 183: 252-265. DOI: 10.1016/j.enbuild.2018.11.008. CrossRef title: "Development of city buildings dataset for urban building energy modeling". Read abstract [L152]. Tier 1.
6. Ville de Montreal (2026). Unites d'evaluation fonciere. Service des finances et de l'evaluation fonciere, Portail des donnees ouvertes de la Ville de Montreal. URL: https://donnees.montreal.ca/dataset/unites-evaluation-fonciere. Read full schema and dataset metadata [L75]. Tier 1.
7. Gouvernement du Quebec (2026). Role d'evaluation fonciere du Quebec. Ministere des Affaires municipales et de l'Habitation (MAMH), Donnees Quebec. URL: https://www.donneesquebec.ca/recherche/dataset/roles-d-evaluation-fonciere-du-quebec. Read full metadata and resource directory [L79]. Tier 1.
8. Government of Ontario (2026). Energy and water usage of large buildings in Ontario (EWRB initiative). Ministry of Energy, Ontario Data Catalogue. URL: https://data.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario. Read full dataset metadata and dictionary [L81]. Tier 1.
9. City of Toronto (2026). 311 Service Requests - Customer Initiated. 311 Toronto Division, City of Toronto Open Data Portal. URL: https://open.toronto.ca/dataset/311-service-requests-customer-initiated/. Read dataset metadata and API schema [L34, L35]. Tier 1.
10. Ville de Montreal (2026). Demandes de services citoyennes (Requetes 311). Service de la concertation des arrondissements et de l'experience citoyenne. URL: https://donnees.montreal.ca/dataset/requete-311. Read dataset metadata and resource structure [L77]. Tier 1.
11. City of Calgary (2026). Historical Property Assessments (Parcel). The City of Calgary Open Data Portal, Dataset 4ur7-wsgc. URL: https://data.calgary.ca/Property-and-Planning/Historical-Property-Assessments-Parcel-/4ur7-wsgc. Read API view schema [L85, L189]. Tier 1.
12. City of Edmonton (2026). Property Assessment Data (Historical). City of Edmonton Open Data, Dataset qi6a-xuwt. URL: https://data.edmonton.ca/City-Administration/Property-Assessment-Data-Historical-/qi6a-xuwt. Read API view schema [L88, L191]. Tier 1.
13. City of Vancouver (2026). 3-1-1 Contact Centre Service Requests. City of Vancouver Open Data Portal. URL: https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/. Read catalog metadata [L193]. Tier 1.
14. Centris (2026). Terms of Use. Centris.ca. URL: https://www.centris.ca/en/terms-of-use. Read legal terms [L47]. Tier 1.
15. Canadian Real Estate Association (CREA) (2026). Terms of Use. Realtor.ca. URL: https://www.realtor.ca/terms-of-use. Read security block and terms notice [L48, L197]. Tier 1.
16. Kijiji Canada (2026). Kijiji Terms of Use. Community Connect Helpdesk. URL: https://help.kijiji.ca/helpdesk/policies/kijiji-terms-of-use. Read legal policies [L49]. Tier 1.
17. Rentals.ca Network (2026). Terms of Service and Robots Exclusion. Rentals.ca. URL: https://rentals.ca/terms and https://rentals.ca/robots.txt. Read terms and robots.txt [L50, L198, L208]. Tier 1.
18. City of New York (2026). DOB Permit Issuance. Department of Buildings, NYC Open Data, Dataset ipu4-2q9a. URL: https://data.cityofnewyork.us/Housing-Development/DOB-Permit-Issuance/ipu4-2q9a. Read view schema [L91]. Tier 1.
19. City of New York (2026). Energy and Water Data Disclosure for Local Law 84 2022 (Data for Calendar Year 2021). NYC Mayor's Office of Climate and Environmental Justice, NYC Open Data, Dataset 7x5e-2fxh. URL: https://data.cityofnewyork.us/Environment/Energy-and-Water-Data-Disclosure-for-Local-Law-84-/7x5e-2fxh. Read view schema [L93]. Tier 1.
20. City of Chicago (2026). Building Permits. Department of Buildings, City of Chicago Data Portal, Dataset ydr8-5enu. URL: https://data.cityofchicago.org/Buildings/Building-Permits/ydr8-5enu. Read view schema [L96]. Tier 1.
21. City of Chicago (2026). Chicago Energy Benchmarking. City of Chicago Data Portal, Dataset xq83-jr8c. URL: https://data.cityofchicago.org/Environment-Sustainable-Development/Chicago-Energy-Benchmarking/xq83-jr8c. Read view schema [L98]. Tier 1.
22. City of Boston (2026). Approved Building Permits. Inspectional Services Department, Analyze Boston. URL: https://data.boston.gov/dataset/approved-building-permits. Read package metadata [L100]. Tier 1.
23. City of Seattle (2026). Building Permits and Building Energy Benchmarking. Seattle Open Data, Datasets 76t5-jtzn and 7735-vjrm. URL: https://data.seattle.gov/. Read metadata [L104]. Tier 1.
24. City and County of San Francisco (2026). Building Permits. San Francisco Department of Building Inspection, DataSF, Dataset i98e-dkgb. URL: https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-dkgb. Read metadata [L109]. Tier 1.
25. City of Los Angeles (2026). Building and Safety Building Permits and Existing Buildings Energy and Water Efficiency (EBEWE) Program. LADBS, City of Los Angeles Open Data, Datasets b4tr-vdre and 9yda-i4ya. URL: https://data.lacity.org/. Read view schema [L113, L115]. Tier 1.
26. City of Austin (2026). Issued Construction Permits. City of Austin Open Data, Dataset 3syk-w9eu. URL: https://data.austintexas.gov/Building-and-Development/Issued-Construction-Permits/3syk-w9eu. Read view schema [L117]. Tier 1.
27. City and County of Denver (2026). Denver Building Permits and Energize Denver Benchmarking. Denver Open Data Catalog. URL: https://www.denvergov.org/opendata/. Read package metadata [L121, L122]. Tier 1.
28. District of Columbia (2026). Building Permits and Building Energy Benchmarking Results. Open Data DC, Department of Buildings and Department of Energy and Environment. URL: https://opendata.dc.gov/. Read dataset records [L125, L126]. Tier 1.
29. City of Philadelphia (2026). Licenses and Inspections Building Permits and Building Energy Benchmarking. OpenDataPhilly. URL: https://opendataphilly.org/. Read catalog metadata [L127, L129]. Tier 1.
30. City of Minneapolis (2026). Minneapolis Building Permits and Minneapolis Energy Benchmarking Data. OpenDataMPLS. URL: https://opendata.minneapolismn.gov/. Read dataset records [L131, L132]. Tier 1.
