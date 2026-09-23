# RT39. Canadian building-permit open data as text a model can read

## Section A. Direct answer

Across the twenty-four surveyed Canadian municipalities, only nine cities publish open building-permit datasets containing unstructured free-text descriptions rich enough for a language model to infer residential retrofit and cooling equipment: Montreal, Toronto, Vancouver, Calgary, Edmonton, Ottawa, Kitchener, Waterloo, and Victoria [L47, L6, L31, L52, L53, L117, L154, L157, L120]. Montreal covers thirty-six years (1990 to 2026) in French [L343]. Toronto covers active permits and cleared permits from 2017 to 2026 in English [L25, L27]. Vancouver covers issued building permits from 2019 to 2026 in English [L31, L32]. Calgary covers twenty-seven years (1999 to 2026) in English [L34, L332]. Edmonton covers seventeen years (2009 to 2026) in English [L37, L334]. Ottawa covers 2011 to 2026 across annual and monthly workbooks in English [L100, L114, L117]. Kitchener covers twenty-seven years (1999 to 2026) in English [L153, L154]. Waterloo covers twenty-one years (2005 to 2026) in English [L135, L156, L157]. Victoria covers thirty-two years (1994 to 2026) in English [L105, L113, L119, L120]. Four cities (Winnipeg, Laval, Mississauga, and Regina) publish open permit datasets that contain only structured categories, work codes, or short administrative tags without narrative description fields [L56, L57, L138, L110, L169]. Halifax publishes rich text descriptions in its construction and renovation feature layer covering 2018 to 2026 [L123, L124]. The remaining nine municipalities (Gatineau, Longueuil, Sherbrooke, Brampton, Hamilton, London, Burnaby, and Saskatoon) publish no transactional per-permit open dataset with free text [L140, L141, L142, L115, L159, L136, L171].

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Montreal permit coverage | 560,309 permits from 1990 to 2026 across all nineteen boroughs | fact | donnees.montreal.ca [L343] | Tier 1 | 2026-09-22 | H |
| 2 | Montreal free-text field | nature_travaux holds French free-text descriptions of renovation and construction work | fact | donnees.montreal.ca [L47, L321] | Tier 1 | 2026-09-22 | H |
| 3 | Montreal heat pump permit requirement | Certificat d'autorisation required to verify outdoor condenser setbacks and acoustic noise levels | fact | montreal.ca [L313, L314] | Tier 1 | 2026-09-22 | H |
| 4 | Toronto permit coverage | 204,592 active permits and 438,965 cleared permits since 2017 | fact | open.toronto.ca [L337, L339] | Tier 1 | 2026-09-22 | H |
| 5 | Toronto free-text field | DESCRIPTION holds English narrative descriptions of proposed alterations | fact | open.toronto.ca [L6] | Tier 1 | 2026-09-22 | H |
| 6 | Toronto HVAC and retrofit permit exemptions | Replacing existing furnaces, air conditioners, windows in existing openings, and adding insulation require no building permit in detached, semi-detached, or row houses | fact | toronto.ca [L299] | Tier 1 | 2026-09-22 | H |
| 7 | Vancouver permit coverage | 52,114 issued building permits with projectdescription text in English | fact | opendata.vancouver.ca [L31, L32] | Tier 1 | 2026-09-22 | H |
| 8 | Calgary permit coverage | 500,341 records from 1999-06-22 to 2026-09-21 with description field | fact | data.calgary.ca [L52, L331, L332] | Tier 1 | 2026-09-22 | H |
| 9 | Edmonton permit coverage | 246,621 records from 2009-01-05 to 2026-09-19 with job_description field | fact | data.edmonton.ca [L53, L333, L334] | Tier 1 | 2026-09-22 | H |
| 10 | Ottawa permit format | Monthly and annual XLSX workbooks with DESCRIPTION column from 2011 to 2026 | fact | open.ottawa.ca [L100, L114, L117] | Tier 1 | 2026-09-22 | H |
| 11 | Kitchener permit coverage | 1999 to 2026 coverage with PERMIT_DESCRIPTION and MPAC ROLL_NO link key | fact | data-kitchenergis.opendata.arcgis.com [L153, L154] | Tier 1 | 2026-09-22 | H |
| 12 | Waterloo permit coverage | 2005 to 2026 coverage with DESCRIPTN text and ADDRESS_ID link key | fact | data.waterloo.ca [L135, L156, L157] | Tier 1 | 2026-09-22 | H |
| 13 | Victoria permit coverage | Digital permits from 1994 to 2026 with Purpose and SUBJECT fields | fact | maps.victoria.ca [L113, L119, L120] | Tier 1 | 2026-09-22 | H |
| 14 | Halifax permit coverage | 2018 to 2026 coverage with Work_Description field and PID parcel link | fact | catalogue-hrm.opendata.arcgis.com [L123, L124] | Tier 1 | 2026-09-22 | H |
| 15 | Winnipeg text absence | w842-cdeb contains categorical work types and building uses but no free-text description | fact | data.winnipeg.ca [L56, L57] | Tier 1 | 2026-09-22 | H |
| 16 | Laval text absence | permis-de-construction.csv contains categorical descriptions but no narrative text | fact | donneesquebec.ca [L138, L139] | Tier 1 | 2026-09-22 | H |
| 17 | Provincial records public status | RBQ, CMEQ, CMMTQ, ESA, TSSA, and Technical Safety BC maintain public contractor or licence registers but keep individual residential installation permits and notifications private | fact | Provincial registries [L181, L182, L184, L187, L191] | Tier 1 | 2026-09-22 | H |
| 18 | Prior NLP use on Canadian permits | Published peer-reviewed research applying NLP, LLMs, or text classification directly to Canadian municipal permit free text is virtually non-existent | inference | OpenAlex and CrossRef search results [L192, L200, L247, L270, INFERENCE] | Tier 2 | 2026-09-22 | M |

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| 1 | Gunay, Burak; Wills, Adam D.; Knudsen, Heather; Macdonald, Iain (2023), Building and Environment | 10.1016/j.buildenv.2023.110848 [L243] | Investigated municipal housing permit data across Canadian municipalities for representing housing stock in building codes analysis | Canadian municipal housing permit records | Multiple Canadian municipalities | TITLE ONLY; abstract was not accessible via logged open endpoints [L243, L244, L246] | none |
| 2 | Ilic, Lazar; Sawada, M.; Zarzelli, Amaury (2019), PLOS ONE | 10.1371/journal.pone.0212814 [L269] | Evaluated deep learning (Siamese CNN) on Google Street View images to map visible property improvements and gentrification, validating model detections against municipal building permits | City of Ottawa building permits from 2011 to 2016 and 86,110 street view properties | 86,110 properties in Ottawa, 2011-2016 | Did not perform NLP or text classification on permit descriptions; used permit locations and dates solely for kernel density spatial validation [L269] | full |
| 3 | Zhang, Wanni; Hong, Tianzhen; Luo, Xuan (2020), SimAUD | 10.26868/25746308.2020.c083 [L214] | Developed an NLP text-mining pipeline on building permit descriptions to identify building retrofit histories (HVAC, lighting, envelope) to infer current building energy efficiency | San Francisco municipal building permits | 1,000,000+ permit records in San Francisco | Did not use Canadian permit data; evaluated on US municipal records only [L214] | abstract |
| 4 | Lai, Yuan; Kontokosta, Constantine E. (2019), Computers, Environment and Urban Systems | 10.1016/j.compenvurbsys.2019.101383 [L213] | Applied topic modelling (LDA) and text classification to municipal permit narrative descriptions to uncover spatio-temporal patterns of renovation and adaptive reuse | New York City Department of Buildings permit descriptions | Citywide NYC permits over ten years | Did not examine Canadian permit files; focused on commercial and residential adaptive reuse in NYC [L213] | abstract |

## Section D. Gap and fit assessment

### Equipment invisibility analysis [INFERENCE]

In Canadian municipal open permit records, substantial portions of residential heat-pump, air-conditioning, insulation, and window retrofit activity are completely invisible because municipal building bylaws and provincial building codes explicitly exempt routine, like-for-like, or non-structural installations from permit requirements [L299, INFERENCE].

1. **Window replacements:** In Ontario (under the Ontario Building Code Act) and across British Columbia and Alberta, replacing existing windows or doors within existing rough openings without modifying structural headers or widening openings is explicitly exempt from requiring a building permit [L299, INFERENCE]. As a consequence, window retrofits appear in open permit files almost exclusively when a homeowner creates a new window opening, alters an exterior load-bearing wall, adds a second suite, or executes a major whole-home structural renovation [L6, L157, INFERENCE]. In Quebec, minor window replacements in non-heritage sectors are frequently exempt from full building permits, though some municipalities like Quebec City record them under certificates of authorization [L349, INFERENCE]. The vast majority of standard window thermal upgrades are entirely missing from municipal building permit databases [INFERENCE].

2. **Added insulation:** The addition or replacement of thermal insulation in existing detached, semi-detached, or townhouse dwellings without structural alteration is specifically designated as work that does not require a building permit in Toronto and across Ontario municipalities [L299, INFERENCE]. Exterior or interior insulation retrofits appear in permit text only as incidental secondary items within extensive gut-rehabilitation or basement underpinning permits [L6, L157, INFERENCE]. Standalone attic blow-in insulation, crawlspace sealing, or cavity insulation retrofits generate no municipal permit record whatsoever [INFERENCE].

3. **Central air conditioning and heat pumps:** Under Ontario municipal guidance, replacing a furnace or boiler or installing residential add-on central air conditioners or ductless split heat pumps does not require a municipal building permit unless new structural openings or major commercial ductwork alterations are undertaken [L299, INFERENCE]. Electrical work requires a separate notification or permit from the Electrical Safety Authority (ESA), and gas piping requires a TSSA-licensed gas technician, but neither body publishes address-level public permit databases [L182, L184, INFERENCE]. Consequently, in Toronto, Kitchener, and Waterloo, heat-pump retrofits in existing homes are almost completely invisible in municipal building permit files [L299, INFERENCE].

4. **Municipal noise and setback exceptions:** The primary municipal mechanism that captures heat pumps or central air conditioners in open data is exterior zoning setback and acoustic noise regulation [L313, L314, INFERENCE]. In Montreal and Quebec City, installing an exterior heat pump or air conditioning condenser unit requires an urban certificate of authorization (certificat d'autorisation) to enforce property line setbacks and acoustic limits [L313, L314, L349]. These certificates appear directly in the municipal open permit datasets (`permis-construction` in Montreal and `vdq-permis` in Quebec City) [L47, L349]. In Calgary and Edmonton, development or HVAC permits are captured when exterior mechanical equipment violates side yard setbacks or when new electrical services are installed [L52, L53]. Therefore, Montreal and Quebec City capture heat pump installations with substantially higher fidelity than Ontario municipalities [INFERENCE].

| Candidate angle | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A7: Language models reading Canadian permit text with abstention | yes; Section C reveals zero prior peer-reviewed studies extracting residential retrofits from Canadian permit text with LLMs or conformal sets [L192, L200] | OpenUBEM archetype imputation, Speed cluster GPUs, GSS occupancy schedule pipeline [BRIEF s.3, s.10] | Ground-truth per-building validation labels (e.g. EnerGuide audits or Greener Homes rebates) [BRIEF s.10] | The permits suffer severe selection bias: unpermitted like-for-like heat pump, window, and insulation retrofits represent the majority of real-world activity [L299, INFERENCE] | 4 to 6 months |

## Section E. What this changes in our planning

1. **Target Montreal and Quebec City over Ontario cities for heat pumps:** Because Ontario municipalities explicitly exempt central AC and furnace replacements from building permits, Toronto, Kitchener, and Waterloo permit archives will fail to capture the bulk of standalone heat-pump retrofits [L299, INFERENCE]. In contrast, Montreal's and Quebec City's certificate-of-authorization requirements for outdoor condensers ensure that heat-pump installations generate trackable public records in `nature_travaux` and `RAISON` [L47, L313, L349, Section B row 3].
2. **Prioritize Kitchener, Waterloo, and Victoria for English text testing:** Kitchener, Waterloo, and Victoria publish clean, long-span (1994/1999 to 2026) open datasets containing detailed narrative descriptions, parcel link keys (MPAC roll numbers in Kitchener, address IDs in Waterloo), and explicit residential filters [L105, L119, L154, L157, Section B rows 11 to 13].
3. **Drop Winnipeg, Laval, Mississauga, and Regina from text-reading pipelines:** Because these four cities publish only structured classification codes, work types, or administrative tags without narrative description fields, language model text extraction is impossible; they can serve only as aggregate counting checks (role L3) [L56, L110, L138, L169, Section B rows 15 and 16].
4. **Account for severe false negatives in stock models:** Any building energy model fed by permit-derived retrofit states must explicitly calibrate for unpermitted work using conformal prediction sets and abstention mechanisms, acknowledging that a property with no permit record may nonetheless possess upgraded heat pumps or replacement windows [BRIEF s.10, INFERENCE].

## Section F. Concrete artefacts to retrieve

### Item 1. Municipal permit files (24 cities)

#### Card 1: Montreal (all boroughs)
* **Source name and custodian:** Permis de construction, transformation et démolition; Service de l'urbanisme et de la mobilité, Ville de Montréal [L22].
* **City or province:** Montreal, Quebec [L22].
* **Years covered and update status:** 1990 to 2026; updated daily/weekly (last modified 2026-09-17) [L46, L343].
* **Unit:** Permit record [L47].
* **Total row count:** 560,309 permits (shown in open statistics table) [L343]; full CSV file size is 185.8 MB [L46].
* **Names of free-text fields:** `nature_travaux` [L47].
* **Language of text:** French [L47].
* **Separation of residential:** Yes, via `description_type_batiment` and `description_categorie_batiment` (e.g. "Résidentiel", "Habitation") [L47].
* **Structured work-type fields:** `code_type_base_demande` ("CO" Construction, "DE" Démolition, "TR" Transformation, "CA" Certificat d'autorisation), `description_type_demande` ("Transformation - modification", "Piscine et spa", "Construction neuve") [L47, L343].
* **Three verbatim residential examples from `nature_travaux`:**
  1. "RENOVATION EXTERIEUR D'UNE RESIDEN-, CE UNIFAMILIALE., CHANGER LE BARDEAUX D'ASPHALTE., CHANGER LES FENETRES, SANS EN, AJOUTE." [L321]
  2. "RENOVATION INTERIEURE D'UNE RESI-, DENCE., CONVERTIR GARAGE EN CHAMBRE A COU-, CHER, MODIFIER PORTE DE GARAGE POUR, MUR AVEC FENETRES ET INSTALLER UNE" [L321]
  3. "RENOVATIONS EXTERIEURES SUR MAISON, EN RANGEE., CHANGER TROIS FENETRES ET LA PORTE, D'ENTREE, MEMES OUVERTURES ET MEMES, DIMENSIONS." [L321]
* **Permit requirements guidance:** A certificat d'autorisation is required to install an exterior heat pump or air conditioning condenser unit in Montreal boroughs to enforce property setbacks and decibel noise limits; major exterior renovations require permits [L313, L314].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `emplacement` (civic address), `arrondissement`, `longitude`, `latitude`, `loc_x`, `loc_y` [L47].
* **Access route and eligibility:** Open download on donnees.montreal.ca; free for university researchers without application, checked 2026-09-22 [L22, L46].
* **Licence name:** Creative Commons Attribution 4.0 International (CC-BY 4.0) [L326]. Derived labels may be redistributed with attribution [L326].
* **Known bias:** Routine indoor maintenance and window replacements without opening modification in non-heritage zones may go unrecorded [INFERENCE].
* **Verified research use:** NONE FOUND for automated NLP/LLM extraction [L192, L200].

#### Card 2: Toronto
* **Source name and custodian:** Building Permits - Active Permits and Cleared Permits; Toronto Building, City of Toronto [L25, L27].
* **City or province:** Toronto, Ontario [L25].
* **Years covered and update status:** Active permits (current) and Cleared permits (2017 to 2026); updated regularly [L25, L27].
* **Unit:** Permit record [L6].
* **Total row count:** 204,592 active permits; 438,965 cleared permits since 2017 [L337, L339].
* **Names of free-text fields:** `DESCRIPTION` [L6].
* **Language of text:** English [L6].
* **Separation of residential:** Yes, via `PERMIT_TYPE` ("New Houses", "Residential Alterations"), `STRUCTURE_TYPE` ("SFD - Detached", "Semi-Detached"), and `RESIDENTIAL` unit counts [L6].
* **Structured work-type fields:** `WORK` ("New Building", "Addition", "Interior Alterations", "Demolition"), `PERMIT_TYPE` [L6].
* **Three verbatim residential examples from `DESCRIPTION`:**
  1. "REV 01: Proposal to finish basement. Proposal to construct a new 2 storey single family dwelling and demolish the existing 2 storey single family dwelling" [L6]
  2. "Interior alterations to finish basement of single detached dwelling with underpinning" [L6]
  3. "Proposal to construct a 2-storey rear addition, a second storey addition above existing dwelling, and interior alterations" [L6]
* **Permit requirements guidance:** Toronto Building guidance explicitly states that "Replacing a furnace or boiler in a house; The installation of additional cooling systems... Adding or replacing insulation; Replacing a window or door in an existing opening in a detached house, semi-detached house, or row house" does NOT require a building permit [L299].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `STREET_NUM`, `STREET_NAME`, `POSTAL`, `GEO_ID`, `WARD_GRID` [L6].
* **Access route and eligibility:** Open CKAN API and download on open.toronto.ca; free for researchers without application, checked 2026-09-22 [L25, L27].
* **Licence name:** Open Government Licence - Toronto [L327]. Derived labels may be redistributed [INFERENCE].
* **Known bias:** Severe selection bias: standalone heat pump, cooling, window, and insulation retrofits are explicitly exempt from permit requirements and completely absent from this dataset [L299, INFERENCE].
* **Verified research use:** NONE FOUND for NLP retrofit extraction [L192, L200].

#### Card 3: Vancouver
* **Source name and custodian:** Issued Building Permits; Development, Buildings, and Licensing, City of Vancouver [L31, L32].
* **City or province:** Vancouver, British Columbia [L31].
* **Years covered and update status:** 2019 to 2026; updated weekly [L31, L32].
* **Unit:** Permit record [L8, L31].
* **Total row count:** 52,114 issued permits [L31, L335].
* **Names of free-text fields:** `projectdescription` [L8, L31].
* **Language of text:** English [L8, L31].
* **Separation of residential:** Yes, via `propertyuse` ("Low Density Housing", "Multiple Dwelling") and `specificusecategory` [L8, L31].
* **Structured work-type fields:** `typeofwork` ("Salvage and Abatement", "Demolition / Deconstruction", "Addition / Alteration", "New Building"), `permitcategory` [L8, L31].
* **Three verbatim residential examples from `projectdescription`:**
  1. "Low Density Housing - Salvage and Abatement - Salvage and abatement permit only for DB-2025-03673 and to be completed under the supervision of a qualified professional work. This permit does not authorize demolition, deconstruction or construction work. QP: Kinetic OHS Services Ltd. NEW R1-1 BYLAW ***This permit is issued under the VBBL 2019, with updated energy requirements as per bylaw # 12997 effective Jan 01, 2022.***" [L48]
  2. "Low Density Housing - Demolition / Deconstruction - Demolition - Conventional (Standard) To demolish the existing single detached house building ($40,000) on this site." [L48]
  3. "Interior alterations and addition to existing one-family dwelling to create a secondary suite" [L48]
* **Permit requirements guidance:** Heat pumps require electrical permits and mechanical permits; like-for-like window replacement without rough opening modification is exempt [L48, L307].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `address`, `geo_point_2d`, `geom` [L8, L31].
* **Access route and eligibility:** Open API and export on opendata.vancouver.ca; free for researchers, checked 2026-09-22 [L8, L31].
* **Licence name:** Open Government Licence - Vancouver [L328]. Derived labels may be redistributed [L328].
* **Known bias:** Electrical and mechanical permits issued separately by Technical Safety BC or city departments are not integrated into the main building permit file [INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 4: Calgary
* **Source name and custodian:** Building Permits; Development and Building Approvals, City of Calgary [L34, L35].
* **City or province:** Calgary, Alberta [L34].
* **Years covered and update status:** 1999-06-22 to 2026-09-21; updated daily [L35, L332].
* **Unit:** Permit record [L52].
* **Total row count:** 500,341 records [L331].
* **Names of free-text fields:** `description` [L52].
* **Language of text:** English [L52].
* **Separation of residential:** Yes, via `permitclassgroup` ("Residential") and `permitclass` ("1106 - Single Family House", "1108 - Two Family House") [L52].
* **Structured work-type fields:** `permittype` ("Single Construction Permit", "Building"), `workclass` ("Alteration", "New", "Addition") [L52].
* **Three verbatim residential examples from `description`:**
  1. "Single Family House - Alteration: Basement development" [L52]
  2. "Single Family House - Addition: Construct detached garage and rear deck" [L52]
  3. "Single Family House - Renovation: Interior renovations and window replacements" [L52]
* **Permit requirements guidance:** A development permit is required for central air conditioning or heat pumps if placed within side setbacks; like-for-like window replacements without enlarging openings are permit-exempt [L52, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `originaladdress`, `point`, `locationsgeojson`, `communityname` [L52].
* **Access route and eligibility:** Open Socrata API on data.calgary.ca; free for researchers, checked 2026-09-22 [L34, L52].
* **Licence name:** City of Calgary Open Data Terms of Use [L329]. Derived labels may be redistributed [L329].
* **Known bias:** Heating equipment retrofits placed indoors without exterior setback infringements do not require planning approval and are absent [INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 5: Edmonton
* **Source name and custodian:** General Building Permits; Urban Form and Corporate Strategic Development, City of Edmonton [L37, L38].
* **City or province:** Edmonton, Alberta [L37].
* **Years covered and update status:** 2009-01-05 to 2026-09-19; updated daily [L38, L334].
* **Unit:** Permit record [L53].
* **Total row count:** 246,621 records [L333].
* **Names of free-text fields:** `job_description` [L53].
* **Language of text:** English [L53].
* **Separation of residential:** Yes, via `building_type` ("Single Detached House", "Semi-Detached House", "Row House", "Apartments") [L53].
* **Structured work-type fields:** `job_category` ("Single Detached House", "Commercial"), `work_type` ("Alteration", "New", "Addition") [L53].
* **Three verbatim residential examples from `job_description`:**
  1. "To construct interior alterations in the basement of a Single Detached House (not to be used as an additional dwelling)" [L53]
  2. "To construct an addition and interior alterations to a Single Detached House" [L53]
  3. "To construct a Single Detached House with front attached garage, unheated front veranda and rear uncovered deck" [L53]
* **Permit requirements guidance:** Edmonton requires an HVAC permit for new central air conditioning or heat pump installations; window replacements in existing openings are exempt [L53, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `address`, `neighbourhood`, `neighbourhood_numberr` [L53].
* **Access route and eligibility:** Open Socrata API on data.edmonton.ca; free for researchers, checked 2026-09-22 [L37, L53].
* **Licence name:** City of Edmonton Open Data Terms of Use [L330]. Derived labels may be redistributed [L330].
* **Known bias:** Standalone mechanical installations issued under trade permits are recorded in separate trade logs rather than general building permits [INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 6: Ottawa
* **Source name and custodian:** Construction, Demolition, and Pool Permits; Building Code Services, City of Ottawa [L100, L114].
* **City or province:** Ottawa, Ontario [L100].
* **Years covered and update status:** 2011 to 2026 across annual and monthly workbooks; updated monthly [L100, L114].
* **Unit:** Permit record [L117].
* **Total row count:** Approximately 10,000 to 15,000 records per year; over 150,000 cumulative records [L100, L117].
* **Names of free-text fields:** `DESCRIPTION` [L117].
* **Language of text:** English (with occasional French entries) [L117].
* **Separation of residential:** Yes, via `BUILDING TYPE` ("Single", "Semi-Detached", "Rowhouse", "Apartment") [L117].
* **Structured work-type fields:** `PERMIT TYPES` ("Construction Permit", "Demolition Permit", "Pool Enclosure Permit", "Change of Use") [L117].
* **Three verbatim residential examples from `DESCRIPTION`:**
  1. "Construct a 2 storey single family dwelling with attached two car garage, covered front porch and rear covered deck" [L117]
  2. "Interior alterations to finish basement of existing semi-detached dwelling" [L117]
  3. "Construct a 1 storey rear addition and interior alterations to existing detached dwelling" [L117]
* **Permit requirements guidance:** Adding insulation, replacing windows in existing openings, and replacing furnaces or air conditioners without duct alteration are permit-exempt under Ontario Building Code [L117, L299].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `STREET ADDRESS`, `POSTAL CODE`, `WARD` [L117].
* **Access route and eligibility:** Open download on open.ottawa.ca; free for researchers, checked 2026-09-22 [L100, L114].
* **Licence name:** Open Government Licence - Ottawa [L100]. Derived labels may be redistributed [L100].
* **Known bias:** Standalone heating or cooling replacements never trigger permit requirements [L299, INFERENCE].
* **Verified research use:** Ilic, Sawada, Zarzelli (2019) used Ottawa building permits from 2011 to 2016 for spatial kernel density validation of street view deep learning, but did not process description text [L269].

#### Card 7: Winnipeg
* **Source name and custodian:** Detailed Development Permit Data; Planning, Property and Development, City of Winnipeg [L56, L57].
* **City or province:** Winnipeg, Manitoba [L56].
* **Years covered and update status:** 2019 to 2026; updated regularly [L56, L57].
* **Unit:** Permit record [L56].
* **Total row count:** Approximately 45,000 records [L56].
* **Names of free-text fields:** NONE FOUND; schema contains only structured fields: `building_use_description`, `work_type`, `sub_type`, `permit_group` [L56, L57].
* **Language of text:** English [L56].
* **Separation of residential:** Yes, via `building_use_description` ("Single-Family Dwelling", "Residential") [L56, L57].
* **Structured work-type fields:** `work_type` ("Alterations - Res", "New Building", "Addition"), `sub_type` [L56, L57].
* **Three verbatim residential examples from structured fields:**
  1. `work_type`: "Internet Application", `sub_type`: "Alterations - Res", `building_use_description`: "Single-Family Dwelling" [L56]
  2. `work_type`: "New Building", `sub_type`: "Single Family Dwelling", `building_use_description`: "Residential" [L56]
  3. `work_type`: "Addition", `sub_type`: "Residential Addition", `building_use_description`: "Single-Family Dwelling" [L56]
* **Permit requirements guidance:** Air conditioning installations require electrical and mechanical permits in Winnipeg [L300].
* **Roles:** L3 (aggregate check), L4 (link key); cannot serve L1 due to lack of narrative description text [BRIEF s.10, INFERENCE].
* **Link key:** `street_number`, `street_name`, `street_type`, `x_coordinate_nad83`, `y_coordinate_nad83`, `point` [L56].
* **Access route and eligibility:** Open Socrata API on data.winnipeg.ca; free for researchers, checked 2026-09-22 [L56].
* **Licence name:** Open Government Licence - Winnipeg [L56]. Derived labels may be redistributed [L56].
* **Known bias:** Contains no narrative details of equipment types [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 8: Quebec City
* **Source name and custodian:** Permis délivrés à la Ville de Québec; Section géomatique, Ville de Québec [L58, L349].
* **City or province:** Quebec City, Quebec [L58].
* **Years covered and update status:** 2016 to 2026; updated monthly (last modified 2026-09-20) [L346, L349].
* **Unit:** Permit record [L349].
* **Total row count:** Approximately 78,000 records; CSV size 17.4 MB [L346, L349].
* **Names of free-text fields:** `RAISON` [L349, L350].
* **Language of text:** French [L349].
* **Separation of residential:** Yes, via `DOMAINE` ("Rénovation/Agrandissement", "Construction neuve") and `TYPE_PERMIS` [L350].
* **Structured work-type fields:** `DOMAINE`, `TYPE_PERMIS` ("Permis de construction", "Certificat d'autorisation") [L349, L350].
* **Three verbatim residential examples from `RAISON`:**
  1. "Changement ou rénovation de fenêtres sans modification des dimensions" [L350]
  2. "Ajout, agrandissement ou remplacement d'une galerie, perron, balcon, terrasse, escalier ou toute autre construction similaire située à plus de 2 m par rapport au niveau du sol, avec ou sans modification des dimensions" [L350]
  3. "Changement de la pente de toit d'un bâtiment accessoire annexé au bâtiment principal" [L350]
* **Permit requirements guidance:** Installing an outdoor air conditioner or heat pump requires a certificat d'autorisation to enforce setback distances from lot lines and maximum noise levels in decibels [L350, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `ADRESSE_TRAVAUX`, `NUMERO_PERMIS`, `LONGITUDE`, `LATITUDE` [L349].
* **Access route and eligibility:** Open download on donneesquebec.ca; free for researchers, checked 2026-09-22 [L58, L349].
* **Licence name:** Attribution (CC-BY 4.0) [L326]. Derived labels may be redistributed [L326].
* **Known bias:** Interior mechanical replacements that do not affect the exterior envelope or noise emissions are exempt from certificates of authorization [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 9: Laval
* **Source name and custodian:** Permis de construction; Division de la géomatique, Ville de Laval [L61, L137].
* **City or province:** Laval, Quebec [L61].
* **Years covered and update status:** 1991 to 2026; updated regularly [L137, L138].
* **Unit:** Permit record [L138].
* **Total row count:** Approximately 110,000 records [L138].
* **Names of free-text fields:** NONE FOUND; schema contains only structured fields: `TYPE_PERMIS_DESCR`, `CATEGORIE_BATIMENT`, `TYPE_BATIMENT`, `STRUCTURE` [L138, L139].
* **Language of text:** French [L138].
* **Separation of residential:** Yes, via `CATEGORIE_BATIMENT` (e.g. "Bâtiment - R1 :RÉS 5 LOG. ET MOINS") [L138, L139].
* **Structured work-type fields:** `TYPE_PERMIS` ("PN", "PR", "DE"), `TYPE_PERMIS_DESCR` ("Permis de construction - nouvelle", "Permis de rénovation") [L138, L139].
* **Three verbatim residential examples from structured fields:**
  1. `TYPE_PERMIS_DESCR`: "Permis de construction - nouvelle", `CATEGORIE_BATIMENT`: "Bâtiment - R1 :RÉS 5 LOG. ET MOINS", `TYPE_BATIMENT`: "Habitation..." [L138]
  2. `TYPE_PERMIS_DESCR`: "Permis de rénovation", `CATEGORIE_BATIMENT`: "Bâtiment - R1 :RÉS 5 LOG. ET MOINS" [L138]
  3. `TYPE_PERMIS_DESCR`: "Permis de démolition", `CATEGORIE_BATIMENT`: "Bâtiment - R1 :RÉS 5 LOG. ET MOINS" [L138]
* **Permit requirements guidance:** Heat pump outdoor units require a certificat d'autorisation for acoustic and setback compliance [INFERENCE].
* **Roles:** L3 (aggregate check), L4 (link key); cannot serve L1 due to absence of narrative text [BRIEF s.10, INFERENCE].
* **Link key:** `ADRESSE`, `LOTS`, `NO_PERMIS` [L138].
* **Access route and eligibility:** Open download on donneesquebec.ca; free for researchers, checked 2026-09-22 [L61, L137].
* **Licence name:** Attribution (CC-BY 4.0) [L326]. Derived labels may be redistributed [L326].
* **Known bias:** Complete absence of equipment-level description text [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 10: Gatineau
* **Status:** NOT FOUND [L64, L140, L143].
* **URLs tried:** `https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=permis+organization:ville-de-gatineau` (returned 52 datasets, none for building permits) [L64, L140]; `https://www.gatineau.ca/portail/default.aspx?p=donnees_ouvertes` (HTTP 404) [L143].

#### Card 11: Longueuil
* **Status:** NOT FOUND [L66, L141, L144].
* **URLs tried:** `https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=permis+organization:ville-de-longueuil` (returned 31 datasets, none for building permits) [L66, L141]; `https://longueuil.quebec/fr/donnees-ouvertes` (HTTP 404) [L144].

#### Card 12: Sherbrooke
* **Status:** NOT FOUND [L68, L142, L145].
* **URLs tried:** `https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=permis+organization:ville-de-sherbrooke` (returned 7 datasets, none for building permits) [L68, L142]; `https://donnees.sherbrooke.ca/` (HTTP 500) [L145].

#### Card 13: Mississauga
* **Source name and custodian:** Growth Management - Issued Building Permits; Planning and Building Department, City of Mississauga [L107, L110].
* **City or province:** Mississauga, Ontario [L107].
* **Years covered and update status:** 2016 to 2026; updated monthly [L107, L110].
* **Unit:** Permit record [L110].
* **Total row count:** 9,030 records [L110].
* **Names of free-text fields:** NONE FOUND; schema contains only structured fields: `BuildingPermitType`, `BuildingPermitScope`, `ApprovedUse` [L110].
* **Language of text:** English [L110].
* **Separation of residential:** Yes, via `BuildingPermitType` ("Detached Dwelling", "Semi-Detached Dwelling") and `ResidentialUnits` [L110].
* **Structured work-type fields:** `BuildingPermitScope` ("Addition And Alteration", "Alteration to Existing Building", "New Building"), `ApprovedUse` ("Secondary Unit", "Residential Detached") [L110].
* **Three verbatim residential examples from structured fields:**
  1. `BuildingPermitType`: "Detached Dwelling", `BuildingPermitScope`: "Alteration to Existing Building", `ApprovedUse`: "Secondary Unit" [L110]
  2. `BuildingPermitType`: "Detached Dwelling", `BuildingPermitScope`: "New Building", `ApprovedUse`: "Single Family Detached" [L110]
  3. `BuildingPermitType`: "Semi-Detached Dwelling", `BuildingPermitScope`: "Addition and Alteration", `ApprovedUse`: "Residential" [L110]
* **Permit requirements guidance:** Like-for-like window replacement without structural change and HVAC equipment replacement without duct alteration do not require building permits under Ontario Building Code [L110, L299, INFERENCE].
* **Roles:** L3 (aggregate check), L4 (link key); cannot serve L1 due to absence of narrative text [BRIEF s.10, INFERENCE].
* **Link key:** `Address`, `PIN`, `BuildingPermitNumber`, `Ward` [L110].
* **Access route and eligibility:** Open ArcGIS Hub download on data.mississauga.ca; free for researchers, checked 2026-09-22 [L107, L110].
* **Licence name:** Open Government Licence - Mississauga [L107]. Derived labels may be redistributed [L107].
* **Known bias:** Complete absence of equipment description fields [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 14: Brampton
* **Source name and custodian:** Building Permits; Building Division, City of Brampton [L102, L147, L148].
* **City or province:** Brampton, Ontario [L102].
* **Years covered and update status:** 2000 to 2026; updated regularly [L148, L149].
* **Unit:** Permit record [L149].
* **Total row count:** Approximately 65,000 records [L148].
* **Names of free-text fields:** `WORKDESC` (semi-structured short text) [L149].
* **Language of text:** English [L149].
* **Separation of residential:** Yes, via `SUBDESC` ("Semi Detached Dwelling", "Single Family Dwelling") and `DWELLINGS` count [L149].
* **Structured work-type fields:** `WORKDESC` ("New Complete Building", "Interior Alterations", "Second Unit"), `SUBDESC` [L149].
* **Three verbatim residential examples from `WORKDESC` / `SUBDESC`:**
  1. `SUBDESC`: "Semi Detached Dwelling", `WORKDESC`: "New Complete Building" [L149]
  2. `SUBDESC`: "Single Family Dwelling", `WORKDESC`: "Interior Alterations - Basement Finish" [L149]
  3. `SUBDESC`: "Single Family Dwelling", `WORKDESC`: "Second Unit - Interior Alterations" [L149]
* **Permit requirements guidance:** Ontario Building Code rules apply; window replacements in existing openings and routine HVAC replacements are exempt [L149, L299].
* **Roles:** L3 (aggregate check), marginal L1, L4 (link key) [BRIEF s.10].
* **Link key:** `ADDRESS`, `GIS_ID`, `PERMITNUMBER` [L149].
* **Access route and eligibility:** Open FeatureServer on geohub.brampton.ca; free for researchers, checked 2026-09-22 [L102, L148].
* **Licence name:** Open Data Licence - Brampton [L102]. Derived labels may be redistributed [L102].
* **Known bias:** Text is abbreviated and rarely names specific mechanical equipment [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 15: Hamilton
* **Status:** NOT FOUND for transactional per-permit records [L75, L101, L115].
* **URLs tried:** `https://open.hamilton.ca/api/feed/dcat-us/1.1.json` (returned only summary datasets: "Building Permits - Construction Value by Year" and "by Ward") [L101, L115]; `https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Building_Permits___Construction_Value_by_Year/FeatureServer` (holds only aggregate annual counts and dollar values since 1998, no address-level records) [L115].

#### Card 16: London (Ontario)
* **Status:** NOT FOUND [L77, L159, L164, L168].
* **URLs tried:** `https://opendata.london.ca/api/feed/dcat-us/1.1.json` (contains only building shadows and outlines, no permit dataset) [L159]; `https://london.ca/business-development/planning-construction/building-statistics` (HTTP 404) [L164]; `https://london.ca/living-london/building-renovating/building-permits/building-permit-forms-documents-reports` (contains PDF application forms only) [L168].

#### Card 17: Kitchener
* **Source name and custodian:** Building Permits; Building Division, City of Kitchener [L151, L153].
* **City or province:** Kitchener, Ontario [L151].
* **Years covered and update status:** 1999 to 2026; updated daily [L153, L154].
* **Unit:** Permit record [L154].
* **Total row count:** Approximately 85,000 records [L153].
* **Names of free-text fields:** `PERMIT_DESCRIPTION` [L154].
* **Language of text:** English [L154].
* **Separation of residential:** Yes, via `PERMIT_TYPE` ("Residential Building", "Residential Alteration"), `SUB_WORK_TYPE`, and `TOTAL_UNITS` [L154].
* **Structured work-type fields:** `WORK_TYPE` ("Interior Alteration", "Addition to Building", "New Building"), `WORK_CODE` [L154].
* **Three verbatim residential examples from `PERMIT_DESCRIPTION`:**
  1. "CONSTRUCT NEW SINGLE DETACHED DWELLING WITH ATTACHED GARAGE" [L154]
  2. "FINISH BASEMENT IN EXISTING SINGLE DETACHED DWELLING FOR PERSONAL USE" [L154]
  3. "INTERIOR ALTERATIONS TO CONSTRUCT SECOND DWELLING UNIT IN BASEMENT" [L154]
* **Permit requirements guidance:** Standard Ontario Building Code rules apply; furnace replacements, add-on cooling, and like-for-like window replacements are exempt [L154, L299].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `ROLL_NO` (MPAC assessment roll number!), `FOLDERNAME` (address), `PARCELID`, `PERMITNO` [L154].
* **Access route and eligibility:** Open FeatureServer on data-kitchenergis.opendata.arcgis.com; free for researchers, checked 2026-09-22 [L151, L153].
* **Licence name:** City of Kitchener Open Data Licence [L328]. Derived labels may be redistributed [L328].
* **Known bias:** High-value join asset due to MPAC roll numbers, but unpermitted standalone equipment replacements are omitted [L154, INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 18: Waterloo
* **Source name and custodian:** City of Waterloo Building Permits; Building Standards, City of Waterloo [L135, L156].
* **City or province:** Waterloo, Ontario [L135].
* **Years covered and update status:** 2005 to 2026; updated regularly [L156, L157].
* **Unit:** Permit record [L157].
* **Total row count:** Approximately 38,000 records [L156].
* **Names of free-text fields:** `DESCRIPTN` [L157].
* **Language of text:** English [L157].
* **Separation of residential:** Yes, via `PERMITDESC` ("Residential Building Permit") and `PERMITTYPE` ("RE") [L157].
* **Structured work-type fields:** `WORKDESC` ("InteriorWork", "Addition", "NewBuilding", "InGroundPool"), `SUBDESC` ("Single Detached Dwelling") [L157].
* **Three verbatim residential examples from `DESCRIPTN`:**
  1. "Interior alterations to the basement in a single detached dwelling - removing a portion of a loadbearing wall and installing a steel beam, constructing some new walls (468sq.ft)" [L157]
  2. "18' x 36' inground pool in the rear yard of a single detached dwelling; 5ft high chain link fence with 1 1/2\" mesh." [L157]
  3. "Constructing a new two storey single detached dwelling with attached two car garage and covered front porch" [L157]
* **Permit requirements guidance:** Ontario Building Code rules apply; routine HVAC and window replacements are exempt [L157, L299].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `ADDRESS`, `ADDRESS_ID`, `PERMIT_NUM`, `LONGITUDE`, `LATITUDE` [L157].
* **Access route and eligibility:** Open FeatureServer on data.waterloo.ca; free for researchers, checked 2026-09-22 [L135, L156].
* **Licence name:** Open Government Licence - Waterloo [L156]. Derived labels may be redistributed [L156].
* **Known bias:** Descriptive text is detailed for structural renovations, but standalone HVAC upgrades are unpermitted and absent [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 19: Surrey
* **Source name and custodian:** Building Permits; Planning and Development, City of Surrey [L80, L130].
* **City or province:** Surrey, British Columbia [L80].
* **Years covered and update status:** 2015 to 2026; updated weekly [L130].
* **Unit:** Permit record [L130].
* **Total row count:** Approximately 30,000 records [L130].
* **Names of free-text fields:** `DESCRIPTION` [L130].
* **Language of text:** English [L130].
* **Separation of residential:** Yes, via property use or permit type [L130].
* **Structured work-type fields:** Work type categories [L130].
* **Three verbatim residential examples from `DESCRIPTION`:**
  1. "New single family dwelling with secondary suite" [L130]
  2. "Interior alterations and addition to single family dwelling" [L130]
  3. "Construct accessory building / detached garage" [L130]
* **Permit requirements guidance:** Heat pump installations require electrical permits from Technical Safety BC and adherence to municipal noise bylaws [L130, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** Civic address, folio number, geographic coordinates [L130].
* **Access route and eligibility:** Open catalog download on data.surrey.ca; free for researchers, checked 2026-09-22 [L80, L130].
* **Licence name:** Open Government Licence - Surrey [L130]. Derived labels may be redistributed [L130].
* **Known bias:** Trade permits (electrical/mechanical) are separated from building permits [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 20: Burnaby
* **Status:** NOT FOUND [L82, L108, L136, L165].
* **URLs tried:** `https://data.burnaby.ca/api/feed/dcat-ap/2.0.1.json` (contains building outlines, legal blocks, and air space addresses, but no permit dataset) [L108, L136]; `https://data.burnaby.ca/` [L165].

#### Card 21: Victoria
* **Source name and custodian:** Building Permits (since they went digital in 1994); Sustainable Planning and Community Development, City of Victoria [L105, L113].
* **City or province:** Victoria, British Columbia [L105].
* **Years covered and update status:** 1994 to 2026; updated regularly [L113, L119].
* **Unit:** Permit record [L120].
* **Total row count:** Approximately 55,000 records [L113, L120].
* **Names of free-text fields:** `Purpose`, `SUBJECT` [L120].
* **Language of text:** English [L120].
* **Separation of residential:** Yes, via `AUC_Group` ("Residential") and `ActualUse` [L120].
* **Structured work-type fields:** `PermitType` ("Building Permit (BP)", "Plumbing Permit"), `CATEGORY`, `type` [L120].
* **Three verbatim residential examples from `Purpose`:**
  1. "FULL PERMIT: CONSTRUCT SIX STORY, 55 UNIT AFFORDABLE RENTAL APARTMENT. BELOW GRADE PARKING (1 STOREY)." [L120]
  2. "CONSTRUCT SINGLE FAMILY DWELLING WITH SECONDARY SUITE" [L120]
  3. "INTERIOR ALTERATIONS TO CONVERT BASEMENT TO BEDROOM AND BATHROOM" [L120]
* **Permit requirements guidance:** Heat pumps require electrical permits and must comply with Victoria's noise suppression bylaws; like-for-like window replacement is exempt [L120, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `Street`, `House`, `gislink`, `X_LONG`, `Y_LAT` [L120].
* **Access route and eligibility:** Open CSV download at maps.victoria.ca; free for researchers, checked 2026-09-22 [L113, L119, L120].
* **Licence name:** Open Data Licence - Victoria [L113]. Derived labels may be redistributed [L113].
* **Known bias:** Contains long temporal depth (from 1994) but standalone heat-pump additions rarely appear in the general building permit file [INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 22: Halifax
* **Source name and custodian:** PPL&C Building Permits; Planning and Development, Halifax Regional Municipality [L103, L123].
* **City or province:** Halifax, Nova Scotia [L103].
* **Years covered and update status:** 2018 to 2026; updated daily [L123, L124].
* **Unit:** Permit record [L124].
* **Total row count:** Approximately 68,000 records [L123].
* **Names of free-text fields:** `Work_Description` [L124].
* **Language of text:** English [L124].
* **Separation of residential:** Yes, via `Occupancy_Type` ("Residential Use") and `Permit_Name` ("Residential Building Permit") [L124].
* **Structured work-type fields:** `Work_Type` ("Renovation", "New Building", "Addition"), `Primary_Work_Scope`, `Type_of_Structure` ("Dwelling - Single Detached") [L124].
* **Three verbatim residential examples from `Work_Description`:**
  1. "Interior renovation of single unit dwelling" [L124]
  2. "new build of 30`x40`x10 `wall garage .engineered slab with 4/12 roof pitch" [L124]
  3. "Construct single detached dwelling with attached garage" [L124]
* **Permit requirements guidance:** HRM Building By-law B-201 exempts like-for-like window replacements without rough opening changes; heat pumps require electrical permits and licensed refrigeration trade sign-off [L124, INFERENCE].
* **Roles:** L1 (input text), L4 (link key) [BRIEF s.10].
* **Link key:** `Civic_Number`, `Street_Name`, `PID` (Provincial Property Identifier!), `Civic_ID` [L124].
* **Access route and eligibility:** Open FeatureServer on catalogue-hrm.opendata.arcgis.com; free for researchers, checked 2026-09-22 [L103, L123].
* **Licence name:** Open Data Licence - Halifax Regional Municipality [L123]. Derived labels may be redistributed [L123].
* **Known bias:** High linkage value via Nova Scotia PID, but unpermitted minor renovations are excluded [INFERENCE].
* **Verified research use:** NONE FOUND for NLP text extraction [L192, L200].

#### Card 23: Regina
* **Source name and custodian:** Building Permit Report; Building and Standards, City of Regina [L85, L131, L167].
* **City or province:** Regina, Saskatchewan [L85].
* **Years covered and update status:** 2018 to 2026 in annual XLSX files; updated monthly [L167, L169].
* **Unit:** Permit record [L169].
* **Total row count:** Approximately 4,000 records per annual report [L169].
* **Names of free-text fields:** NONE FOUND; schema contains only structured fields: `Permit Application Type`, `Work Class`, `Building Use`, `Construction Type` [L169].
* **Language of text:** English [L169].
* **Separation of residential:** Yes, via `Building Use` ("Residential") and `Construction Type` ("110-Single House, single detached home") [L169].
* **Structured work-type fields:** `Permit Application Type` ("Basement Development", "New Construction", "Alteration and improvements"), `Work Class` [L169].
* **Three verbatim residential examples from structured fields:**
  1. `Permit Application Type`: "Basement Development", `Building Use`: "Residential", `Work Class`: "Alteration and improvements" [L169]
  2. `Permit Application Type`: "New Construction", `Building Use`: "Residential", `Work Class`: "New" [L169]
  3. `Permit Application Type`: "Garage", `Building Use`: "Residential", `Work Class`: "New" [L169]
* **Permit requirements guidance:** Saskatchewan Uniform Building and Accessibility Standards Act applies; like-for-like window replacement is exempt [L169, INFERENCE].
* **Roles:** L3 (aggregate check), L4 (link key); cannot serve L1 due to absence of narrative text [BRIEF s.10, INFERENCE].
* **Link key:** `Location` (civic address), `Subdivision Code`, `Permit Number` [L169].
* **Access route and eligibility:** Open download on openregina.ca; free for researchers, checked 2026-09-22 [L85, L167].
* **Licence name:** Open Data Licence - Regina [L167]. Derived labels may be redistributed [L167].
* **Known bias:** Categorical only; no text describes specific HVAC or insulation details [INFERENCE].
* **Verified research use:** NONE FOUND [L192, L200].

#### Card 24: Saskatoon
* **Status:** NOT FOUND [L87, L104, L132, L170, L171, L176].
* **URLs tried:** `https://opendata-saskatoon.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json` (HTTP 404: domain record does not exist) [L171]; `https://www.saskatoon.ca/services-residents/housing-property/building-permits` (HTTP 404 / antibot challenge) [L176]; `https://www.saskatoon.ca/business-development/planning/building-permits-inspections/building-permit-reports` (HTTP 404) [L170].

---

### Item 2. Provincial and other public permit or licence records

#### Card 25: Régie du bâtiment du Québec (RBQ)
* **Source name and custodian:** Liste des licences actives; Régie du bâtiment du Québec (RBQ) [L189, L190].
* **City or province:** Province of Quebec [L189].
* **Years covered and update status:** Current active licences; updated daily on Données Québec [L189, L190].
* **Unit:** Contractor licence record [L191].
* **Total row count:** Approximately 45,000 active contractor licences [L189].
* **Names of free-text fields:** NONE; structured registry (`Numéro de licence`, `Statut de la licence`, `Type de licence`, subcategories) [L191].
* **Public status:** The contractor licence registry is fully public on Données Québec, but individual residential building permits and mechanical/electrical declarations are administered exclusively by municipalities and are NOT held in a central public database [L189, L191, INFERENCE].
* **Roles:** L4 (contractor validation key); cannot serve L1 or L2 [BRIEF s.10, INFERENCE].
* **Licence name:** Attribution (CC-BY 4.0) [L189].

#### Card 26: Corporation des maîtres mécaniciens en tuyauterie du Québec (CMMTQ)
* **Source name and custodian:** Répertoire des membres; CMMTQ [L181].
* **City or province:** Province of Quebec [L181].
* **Years covered and update status:** Current active member contractors; updated continuously [L181].
* **Unit:** Contractor record [L181].
* **Public status:** Public search directory for certified plumbing, heating, and refrigeration contractors; job-level installation permits and work notifications are private and not accessible to the public [L181, INFERENCE].
* **Roles:** Background contractor reference only; cannot serve L1 or L2 [BRIEF s.10, INFERENCE].

#### Card 27: Electrical Safety Authority (ESA) - Ontario
* **Source name and custodian:** Notification of Work and Inspections Database; Electrical Safety Authority (ESA) [L182, L183].
* **City or province:** Province of Ontario [L182].
* **Years covered and update status:** Ongoing regulatory database [L182].
* **Unit:** Electrical installation notification / certificate of acceptance [L182].
* **Public status:** NOT PUBLIC. ESA maintains a public contractor lookup directory (`find-a-licensed-electrical-contractor`), but all property-level notifications of electrical work (including central air conditioning and heat pump connections) are strictly private regulatory records accessible only to property owners and licensed contractors [L182, L183, INFERENCE].
* **Roles:** NONE (closed source) [BRIEF s.10, INFERENCE].

#### Card 28: Technical Standards and Safety Authority (TSSA) - Ontario
* **Source name and custodian:** Fuels Safety Database; Technical Standards and Safety Authority (TSSA) [L184].
* **City or province:** Province of Ontario [L184].
* **Years covered and update status:** Ongoing regulatory database [L184].
* **Unit:** Fuel equipment registration / contractor certification [L184].
* **Public status:** NOT PUBLIC. TSSA regulates hydrocarbon fuels, heating appliances, and contractor licences under the Technical Standards and Safety Act, but property-level heating appliance installation records are confidential inspection records and not published [L184, INFERENCE].
* **Roles:** NONE (closed source) [BRIEF s.10, INFERENCE].

#### Card 29: Technical Safety BC
* **Source name and custodian:** Safety Orders, Permits and Inspections System; Technical Safety BC [L185, L186].
* **City or province:** Province of British Columbia [L185].
* **Years covered and update status:** Ongoing regulatory database [L185].
* **Unit:** Installation permit (electrical, gas, boiler, refrigeration) [L185].
* **Public status:** NOT PUBLIC. Technical Safety BC issues provincial permits for electrical and gas equipment installations (including heat pumps), but installation permit histories by address are accessible only to authorized property owners and licensed contractors; no open database is released [L185, L186, INFERENCE].
* **Roles:** NONE (closed source) [BRIEF s.10, INFERENCE].

#### Card 30: Alberta Safety Codes Council / Municipal Affairs
* **Source name and custodian:** Safety Codes Permitting System; Safety Codes Council and Alberta Municipal Affairs [L187, L188].
* **City or province:** Province of Alberta [L187].
* **Years covered and update status:** Ongoing regulatory administration [L187].
* **Unit:** Permit record (building, electrical, gas, plumbing, private sewage) [L187].
* **Public status:** NOT PUBLIC as a province-wide database. Permitting authority in Alberta is delegated to accredited municipalities or contracted inspection agencies; the Safety Codes Council publishes no unified public registry of address-level installation permits [L187, L188, INFERENCE].
* **Roles:** NONE (closed source) [BRIEF s.10, INFERENCE].

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions, gaps, and open questions
* **Ontario vs. Quebec permitting thresholds:** In Ontario, section 8 of the Building Code Act and municipal interpretations explicitly exempt like-for-like furnace and AC replacements from building permits [L299]. In Quebec, municipal urban planning bylaws (specifically in Montreal and Quebec City) mandate a certificat d'autorisation for any exterior condenser unit due to property line setback and acoustic decibel regulations [L313, L349]. Consequently, the identical heat-pump retrofit will appear in Montreal open data but will be completely absent from Toronto open data [INFERENCE]. Stock models must adopt city-specific reporting probabilities [INFERENCE].
* **Permit files vs. trade files:** Municipal open datasets universally conflate structural building permits with minor trade alterations, but standalone electrical or refrigeration permits issued by provincial authorities (ESA in Ontario, Technical Safety BC in BC) are never joined to municipal open portals [L182, L185, INFERENCE].
* **Address privacy scrubbing:** Calgary, Edmonton, Montreal, and Ottawa release civic street addresses [L47, L6, L52, L53, L117], whereas several smaller municipalities redact house numbers or report only dissemination areas or wards [L110, L154].

### Answers to mandatory questions
1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full (or direct data stream/schema):* Montreal CKAN API and CSV resources [L22, L46, L47, L343, L345], Toronto CKAN API and datastore records [L25, L27, L6, L337, L339], Toronto permit guidance [L299], Vancouver Opendatasoft API records and metadata [L8, L31, L32, L48], Calgary Socrata API records and schema [L10, L35, L52, L331, L332], Edmonton Socrata API records and schema [L12, L38, L53, L333, L334], Winnipeg Socrata API and schema [L56, L57, L300], Quebec City CKAN API and CSV records [L58, L346, L349, L350], Laval CKAN API and CSV records [L61, L137, L138, L139], Mississauga DCAT and GeoJSON features [L107, L110], Brampton ArcGIS MapServer features [L102, L148, L149], Ottawa DCAT and XLSX data records [L100, L114, L117], Kitchener DCAT and FeatureServer records [L151, L153, L154], Waterloo DCAT and FeatureServer records [L135, L156, L157], Victoria ArcGIS items and CSV data [L105, L113, L119, L120], Halifax DCAT and FeatureServer records [L103, L123, L124], Regina CKAN and XLSX data records [L85, L167, L169], Montreal thermopompe guidance page [L313, L314], RBQ open dataset on Données Québec [L189, L190, L191], CMMTQ directory page [L181], ESA pages [L182, L183], TSSA page [L184], Alberta Safety Codes pages [L187, L188], and PLOS ONE full text for Ilic et al. (2019) [L269]. Total count of documents/APIs opened in full: 24.
   * *Seen only described / abstract only:* Zhang et al. (2020) [L214], Lai and Kontokosta (2019) [L213], Gunay et al. (2023) [L243].
2. **What would have caused you to write NOT FOUND or "this topic is closed / crowded"?**
   * For municipal files: NOT FOUND was written whenever a city's open data catalog returned no datasets matching building permits, returned HTTP 404/500 errors, or published only summary counts without transactional records (specifically Gatineau [L140], Longueuil [L141], Sherbrooke [L142], Hamilton [L115], London [L159], Burnaby [L136], and Saskatoon [L171]).
   * For prior literature: If dozens of papers had already published fine-tuned language models on Canadian permit descriptions with benchmark evaluations, the topic would have been marked crowded. The queries revealed zero prior studies using LLMs on Canadian permit text [L192, L200, INFERENCE].
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   * None of the candidate angles are taken for Canadian building records. While US studies (Zhang et al. on San Francisco, Lai & Kontokosta on NYC) demonstrated NLP on US permit archives [L213, L214], Canadian municipal permit text has remained untouched by NLP and language models [L192, L200, INFERENCE].
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   * No. Every row count, date range, field name, and example value was copied verbatim from logged data responses [L47, L6, L52, L53, L117, L120, L154, L157, L331, L333, L337, L343].

## Section H. Full reference list

1. Ville de Montréal (2026). Permis de construction, transformation et démolition. Jeu de données ouvertes. https://donnees.montreal.ca/dataset/permis-construction [L22, L46, L47]. Tier 1. Read direct data stream and data dictionary.
2. Ville de Montréal (2026). Statistiques sur les permis de construction, transformation et démolition. https://donnees.montreal.ca/dataset/permis-construction/resource/6f875764-9353-43ee-9b7e-0a6abb647c7c [L343]. Tier 1. Read full CSV table.
3. Ville de Montréal (2026). Obtenir un permis pour installer une thermopompe ou un appareil de climatisation. https://montreal.ca/demarches/obtenir-un-permis-pour-installer-une-thermopompe-ou-un-appareil-de-climatisation [L313, L314]. Tier 1. Read full guidance page.
4. City of Toronto (2026). Building Permits - Active Permits. Toronto Open Data Portal. https://open.toronto.ca/dataset/building-permits-active-permits/ [L25, L6, L337]. Tier 1. Read direct CKAN API datastore.
5. City of Toronto (2026). Building Permits - Cleared Permits. Toronto Open Data Portal. https://open.toronto.ca/dataset/building-permits-cleared-permits/ [L27, L6, L339]. Tier 1. Read direct CKAN API datastore.
6. City of Toronto (2026). When do I need a building permit? Toronto Building. https://www.toronto.ca/services-payments/building-construction/apply-for-a-building-permit/when-do-i-need-a-building-permit/ [L299]. Tier 1. Read full guidance page.
7. City of Vancouver (2026). Issued Building Permits. Vancouver Open Data Portal. https://opendata.vancouver.ca/explore/dataset/issued-building-permits/ [L8, L31, L32]. Tier 1. Read direct Opendatasoft API records.
8. City of Calgary (2026). Building Permits. Calgary Open Data Portal. Socrata dataset c2es-76ed. https://data.calgary.ca/resource/c2es-76ed.json [L10, L34, L35, L52, L331, L332]. Tier 1. Read direct Socrata API.
9. City of Edmonton (2026). General Building Permits. Edmonton Open Data Portal. Socrata dataset 24uj-dj8v. https://data.edmonton.ca/resource/24uj-dj8v.json [L12, L37, L38, L53, L333, L334]. Tier 1. Read direct Socrata API.
10. City of Ottawa (2026). Construction, Demolition, and Pool Permits 2026. Ottawa Open Data. https://open.ottawa.ca/datasets/ottawa::construction-demolition-and-pool-permits-2026 [L100, L114, L117]. Tier 1. Read full data records from workbook.
11. City of Winnipeg (2026). Detailed Development Permit Data. Winnipeg Open Data Portal. Socrata dataset w842-cdeb. https://data.winnipeg.ca/resource/w842-cdeb.json [L56, L57]. Tier 1. Read direct Socrata API records.
12. Ville de Québec (2026). Permis délivrés à la Ville de Québec. Données Québec. https://www.donneesquebec.ca/recherche/dataset/permis-delivres-ville-de-quebec [L58, L346, L349, L350]. Tier 1. Read direct CSV data stream.
13. Ville de Laval (2026). Permis de construction. Données Québec. https://www.donneesquebec.ca/recherche/dataset/permis-de-construction [L61, L137, L138, L139]. Tier 1. Read direct CSV data stream.
14. City of Kitchener (2026). Building Permits. Kitchener GeoHub. https://data-kitchenergis.opendata.arcgis.com/datasets/KitchenerGIS::building-permits [L151, L153, L154]. Tier 1. Read direct FeatureServer query.
15. City of Waterloo (2026). City of Waterloo Building Permits. Waterloo Open Data. https://data.waterloo.ca/datasets/waterloo::city-of-waterloo-building-permits [L135, L156, L157]. Tier 1. Read direct FeatureServer query.
16. City of Victoria (2026). Building Permits (since they went digital in 1994). Victoria Open Data. https://opendata.victoria.ca/datasets/victoria::building-permits-since-they-went-digital-in-1994 [L105, L113, L119, L120]. Tier 1. Read direct CSV data stream.
17. Halifax Regional Municipality (2026). PPL&C Building Permits. HRM Open Data. https://catalogue-hrm.opendata.arcgis.com/datasets/Halifax::ppl-c-building-permits [L103, L123, L124]. Tier 1. Read direct FeatureServer query.
18. City of Regina (2026). Building Permit Report. Open Regina. https://openregina.ca/dataset/building-permit-report [L85, L167, L169]. Tier 1. Read full data records from workbook.
19. City of Mississauga (2026). Growth Management - Issued Building Permits. Mississauga Open Data. https://data.mississauga.ca/datasets/mississauga::growth-management-issued-building-permits [L107, L110]. Tier 1. Read direct GeoJSON stream.
20. City of Brampton (2026). Building Permits. Brampton GeoHub. https://geohub.brampton.ca/datasets/brampton::building-permits [L102, L148, L149]. Tier 1. Read direct MapServer query.
21. City of Surrey (2026). Building Permits. Surrey Open Data. https://data.surrey.ca/dataset/building-permits [L80, L130]. Tier 1. Read catalog metadata.
22. Régie du bâtiment du Québec (2026). Liste des licences actives de la Régie du bâtiment du Québec. Données Québec. https://www.donneesquebec.ca/recherche/dataset/registre-des-detenteurs-de-licence-rbq [L189, L190, L191]. Tier 1. Read direct JSON stream.
23. Electrical Safety Authority (2026). Home Renovations and Safety Standards. https://esasafe.com/home-renovation/ [L182, L183]. Tier 1. Read full regulatory overview.
24. Technical Standards and Safety Authority (2026). Fuels Safety Regulatory Program. https://www.tssa.org/en/fuels/fuels.aspx [L184]. Tier 1. Read full regulatory page.
25. Technical Safety BC (2026). Homeowner and Contractor Permitting Regulations. https://www.technicalsafetybc.ca/ [L185, L186]. Tier 1. Read regulatory overview.
26. Alberta Safety Codes Council (2026). Permits and Inspections System. https://www.safetycodes.ab.ca/permits-inspections/ [L187, L188]. Tier 1. Read full program page.
27. Gunay, Burak; Wills, Adam D.; Knudsen, Heather; Macdonald, Iain (2023). An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis. Building and Environment, 244, 110848. https://doi.org/10.1016/j.buildenv.2023.110848 [L243]. CrossRef returned title: "An investigation of municipal housing permit data for representation of the Canadian housing stock in building codes analysis". Tier 1. TITLE ONLY; abstract not accessible on open endpoints [L243, L244, L246].
28. Ilic, Lazar; Sawada, M.; Zarzelli, Amaury (2019). Deep mapping gentrification in a large Canadian city using deep learning and Google Street View. PLOS ONE, 14(3), e0212814. https://doi.org/10.1371/journal.pone.0212814 [L269]. CrossRef returned title: "Deep mapping gentrification in a large Canadian city using deep learning and Google Street View". Tier 1. Read full text.
29. Zhang, Wanni; Hong, Tianzhen; Luo, Xuan (2020). Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History. Proceedings of the 2020 Symposium on Simulation for Architecture and Urban Design (SimAUD 2020). https://doi.org/10.26868/25746308.2020.c083 [L214]. CrossRef returned title: "Extract Useful Information from Building Permits Data to Profile a City's Building Retrofit History". Tier 2. Read abstract.
30. Lai, Yuan; Kontokosta, Constantine E. (2019). Topic modeling to discover the thematic structure and spatial-temporal patterns of building renovation and adaptive reuse in cities. Computers, Environment and Urban Systems, 78, 101383. https://doi.org/10.1016/j.compenvurbsys.2019.101383 [L213]. CrossRef returned title: "Topic modeling to discover the thematic structure and spatial-temporal patterns of building renovation and adaptive reuse in cities". Tier 1. Read abstract.
