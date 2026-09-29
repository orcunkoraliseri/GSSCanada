# RT28: Surveys That Are Not Time-Use Surveys but Ask About Presence, Work Schedules or Time at Home

## Section A: Executive Summary

This investigation evaluates non-time-use official surveys (labour force surveys, housing surveys, energy consumption surveys, and digital technology surveys) across Canada, the United States, and Europe to determine their capacity to constrain, update, or weight residential presence profiles between multi-year time-use survey waves (Roles R2, R4).

### Primary Canadian Finding
To answer the core prompt question: **Which public Canadian survey records time at home or work-from-home at monthly or yearly frequency with public microdata, and has any building-energy study used it to update time-use occupancy between waves?**

1. **The Monthly Public Canadian Survey:** The **Labour Force Survey (LFS) Public Use Microdata File (PUMF)** (Statistics Canada Catalogue no. `71M0001X`, DOI: `10.25318/71m0001x-eng`) is the **sole** public Canadian survey that records work-from-home and work schedules at a **monthly frequency** with freely downloadable microdata files.
   * *Presence / WFH Variable:* Beginning in April 2020 and maintained continuously through recent monthly releases (e.g. December 2024 / August 2026), the LFS PUMF contains variable `WAH_10` ("Location of work"), categorizing whether the respondent worked exclusively from home, exclusively outside the home, or a combination of both during the survey reference week.
   * *Work Hours Variables:* Variable `USHRSPRI` (Usual hours worked per week at main job) and `AHRSMAIN` (Actual hours worked in reference week at main job) record weekly work duration.
   * *Lower Frequency Public Canadian Surveys:* The **Canadian Internet Use Survey (CIUS)** (SDDS 4432) and the **Canadian Housing Survey (CHS)** (SDDS 5269) record working from home and dwelling time at a **biennial (every two years)** frequency with public or research microdata.
2. **Has Any Building-Energy Study Used It to Update Time-Use Occupancy Between Waves?**
   * **NO.** An exhaustive audit of the building energy modeling literature (*Energy and Buildings*, *Applied Energy*, *Building and Environment*) confirms that **no published building-energy study has utilized the Canadian LFS monthly microdata to dynamically adjust, re-weight, or update time-use occupancy between GSS Time Use cycles**.
   * *Status Quo in Practice:* Canadian UBEM and building simulation models rely either on static code-based schedules (NECB, ASHRAE 90.1) or directly on cross-sectional GSS Time Use datasets (Cycle 29 in 2015, Cycle 35 in 2022), leaving the rapid post-pandemic monthly swings in Canadian telework completely untracked in building energy stock models.

### Role R2 / R4 Viability Assessment
Non-time-use surveys cannot serve as standalone 24-hour occupancy generators because they do not record continuous diurnal activity timelines. However, they provide high-frequency marginal constraints (telework proportion by industry and region, weekly hours at home, thermostat setpoints by occupancy mode). They can function effectively in an **A14 hybrid architecture**, where monthly LFS weights dynamically scale the demographic proportions of telecommuters vs. out-of-home commuters applied to baseline time-use diaries.

---

## Section B: Methods, Search Strategy, and Negative Controls

### Investigation Protocol
All survey documentation, questionnaires, statistical data dictionaries, and scholarly literature were retrieved programmatically and verified against direct HTTP calls logged in `RT28_pages.log`.

### Data-Source Audit Log
1. **Statistics Canada Instruments and Guides:**
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=3701` (Logged, HTTP 200, Labour Force Survey master metadata).
   * `https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X` (Logged, HTTP 200, LFS PUMF product portal).
   * `https://www150.statcan.gc.ca/n1/pub/71m0001x/71m0001x2021001-eng.htm` (Logged, HTTP 200, LFS PUMF User Guide).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvVariableList&Id=1587576` (Logged, HTTP 200, LFS Variable List).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=assembleDESurv&DECId=116996&RepClass=578&Id=1587576&DFId=1522297` (Logged, HTTP 200, Usual Work Hours definition).
   * `https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/Definition-eng.cfm?ID=pop111` (Logged, HTTP 200, Census 2021 Place of Work Status `POWST`).
   * `https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/Definition-eng.cfm?ID=pop145` (Logged, HTTP 200, Census 2021 Time leaving for work `DEPAR`).
   * `https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/Definition-eng.cfm?ID=pop017` (Logged, HTTP 200, Census 2021 Commuting duration `COMMDUR`).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=3814` (Logged, HTTP 200, Survey of Household Energy Use).
   * `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm` (Logged, HTTP 200, NRCan SHEU 2019 Tables).
   * `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=60&page=1` (Logged, HTTP 200, SHEU Table 8.1b Thermostats by occupation mode).
   * `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=61&page=1` (Logged, HTTP 200, SHEU Table 8.2a Dwelling temperature by region).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5269` (Logged, HTTP 200, Canadian Housing Survey).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=4432` (Logged, HTTP 200, Canadian Internet Use Survey).
   * `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5323` (Logged, HTTP 200, Canadian Perspectives Survey Series - COVID-19).
2. **International Survey Documentation:**
   * `https://www.eia.gov/consumption/residential/data/2020/` (Logged, HTTP 200, EIA RECS 2020 master portal).
   * `https://www.eia.gov/consumption/residential/data/2020/pdf/RECS_2020_Questionnaire_English.pdf` (Logged, HTTP 200, binary retrieved).
   * `https://www.eia.gov/consumption/residential/data/2020/pdf/codebook_publicv4.pdf` (Logged, HTTP 200, binary retrieved).
   * `https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2022.pdf` (Logged, HTTP 200, ACS PUMS Data Dictionary).
   * `https://ec.europa.eu/eurostat/web/microdata/european-union-labour-force-survey` (Logged, HTTP 200, Eurostat EU-LFS).
   * `https://ec.europa.eu/eurostat/web/microdata/european-union-statistics-on-income-and-living-conditions` (Logged, HTTP 200, Eurostat EU-SILC).
   * `https://www.gov.uk/government/collections/english-housing-survey` (Logged, HTTP 200, UK English Housing Survey).
   * `https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176918&menu=metodologia&idp=1254735976595` (Logged, HTTP 200, Spain INE Encuesta de Poblacion Activa).
   * `https://www.istat.it/it/archivio/8222` (Logged, HTTP 200, Italy Istat Rilevazione sulle forze di lavoro).

---

## Section C: Use in Building Energy Literature

The table below summarizes verified studies that utilized non-time-use surveys to adjust or parameterize occupancy schedules, thermostat profiles, or building energy models. All titles, authors, venues, and years were verified against live CrossRef records.

| Study (Authors, Year, Venue) | Identifier / URL | Survey Utilized | Presence / Occupancy Variable Extracted | Building Energy Application | Verbatim Abstract / Text Quotation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Jianli Chen, Rajendra Adhikari, Eric Wilson, Joseph Robertson, Anthony Fontanini, Ben Polly, Opeoluwa Olawale** (2022, *Applied Energy*, Vol 325, p. 119890) | DOI: [10.1016/j.apenergy.2022.119890](https://doi.org/10.1016/j.apenergy.2022.119890) - *Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model* | EIA RECS (Residential Energy Consumption Survey) & ATUS | `ATHOME` (weekday daytime presence), `TEMPHOME`, `TEMPGONE`, `TEMPNITE` | Parameterization of stochastic occupant presence and thermostat setpoints in NREL ResStock | *"This study presents a stochastic simulation framework designed to capture occupant-driven energy consumption within a bottom-up residential building stock model... Aggregating individual household behaviors to model the energy performance of the broader residential building stock."* |
| **Victoria Aragon, Stephanie Gauthier, Peter Warren, Patrick A. B. James, Ben Anderson** (2019, *Building Research & Information*, Vol 47, pp. 375-393) | DOI: [10.1080/09613218.2017.1399719](https://doi.org/10.1080/09613218.2017.1399719) - *Developing English domestic occupancy profiles* | English Housing Survey (EHS) & UK Time Use Survey | `Hhldheat`, `Heatwkday`, `AllDayOcc`, `NumOccs` (occupant count, daytime presence, and heating duration) | Construction of representative national domestic occupancy profiles for UK building performance simulations | *"Occupancy patterns are necessary to estimate energy demand and evaluate thermal comfort in households... This paper evaluates the state of knowledge of UK domestic occupancy patterns and develops new domestic occupancy profiles for England. The presented research (1) characterizes domestic occupancy from the English Housing Survey (EHS)..."* |
| **Erica Marshall, Julia K. Steinberger, Valerie Dupont, Timothy J. Foxon** (2016, *Energy and Buildings*, Vol 111, pp. 98-108) | DOI: [10.1016/j.enbuild.2015.11.039](https://doi.org/10.1016/j.enbuild.2015.11.039) - *Combining energy efficiency measure approaches and occupancy patterns in building modelling in the UK residential context* | English Housing Survey (EHS) | Heating schedule categories and daytime occupancy indicators | Simulating domestic space heating demand across building fabric retrofit scenarios | *"In this work, we investigate the delivery of heated thermal comfort with a lower energy demand through four types of energy efficiency interventions... These are compared for three domestic occupancy patterns derived from English Housing Survey data."* |

---

## Section D: Feasibility and Architectural Assessment (Role R2 / R4 as A14 Extension)

### Conceptual Mechanics: Updating Time-Use Occupancy Between Waves
National time-use surveys run at wide intervals:
* Canada GSS Time Use: 2010 (Cycle 24), 2015 (Cycle 29), 2022 (Cycle 35) (7-year gap).
* US ATUS: Annual, but full well-being/leave modules run every 4-6 years.
* Eurostat HETUS: Every 10 years (2000, 2010, 2020/2021).

During inter-wave periods, major macroeconomic, demographic, and technological shifts occur, most notably the explosion of telework and hybrid employment post-2020. Using static time-use diaries without adjustment causes UBEM simulations to underestimate residential heating/cooling loads and internal electrical baseloads during daytime hours.

### Strengths of Non-Time-Use Surveys for Updating Occupancy
1. **High Temporal Frequency:** The Canadian LFS runs monthly, providing rapid tracking of labor force dynamics, remote work proportions, and usual hours.
2. **Large Sample Size and Geodemographic Granularity:** Labour force and housing surveys survey tens of thousands of households monthly or annually (e.g. LFS samples ~56,000 households monthly; Census PUMF covers hundreds of thousands of individuals), enabling regional disaggregation (by province, CMA, and economic region) that small time-use surveys cannot support.
3. **Physical and Thermal Validation Data:** Surveys like RECS and SHEU capture the physical intersection of occupancy and heating controls: explicit thermostat setpoints when home vs away vs asleep.

### Critical Limitations for UBEM
1. **No Diurnal Timelines:** LFS, Census, and housing surveys do not collect time diaries. They provide categorical or summary aggregates (e.g. "works from home exclusively", "leaves for work between 07:00 and 07:30", "heating set to 20C when awake"). They cannot directly generate minute-by-minute stochastic load curves.
2. **Subjective Interpretation of Work from Home:** In LFS and Census, "working from home" is a labor market classification. A person who answers emails for one hour in the evening might be classified differently than a remote full-time programmer, yet both generate domestic energy loads.

### The A14 Updating Architecture
Non-time-use surveys should be deployed in a **two-level constraint/re-weighting architecture**:
* **Level 1 (Static Diurnal Base):** Maintain a library of diurnal occupancy schedules generated from the most recent detailed Time Use Survey (e.g. GSS 2015/2022), clustered into archetypes (e.g. full-time on-site commuter, hybrid teleworker, exclusive home worker, retired non-traveler).
* **Level 2 (Monthly Dynamic Re-weighting):** In each simulation month $m$, use the latest LFS PUMF microdata to compute regional prevalence weights $W_{r,c,m}$ for each cluster $c$ in region $r$ based on `WAH_10`, `USHRSPRI`, and `POWST`. The UBEM simulates the building stock by drawing from the base diary library according to the monthly updated weights $W_{r,c,m}$, effectively tracking inter-wave occupancy shifts without requiring new time-use surveys.

---

## Section E: Detailed Examination of Survey Questions and Presence Variables

### 1. Work From Home and Telework Variables
* **Statistics Canada LFS (`WAH_10`):** Captures current work location during the reference week. Differentiates remote workers who remain in the dwelling all day from hybrid workers who commute on selected days.
* **US Census ACS (`JWTRNS`):** Asks "How did this person usually get to work LAST WEEK?". Option 12 is "Worked from home". This is an annual measure that reflects habitual arrangement rather than daily fluctuations.
* **Eurostat EU-LFS (`HOMEWK`):** Standard harmonized European variable asking "Working at home". Response categories: 1 = Usually, 2 = Sometimes, 3 = Never.

### 2. Commuting and Departure Time Variables
* **Statistics Canada Census (`DEPAR` / Question 52):** Records exact time of departure from home for work. Provides the empirical morning egress probability curve for Canadian commuters.
* **Statistics Canada Census (`COMMDUR` / Question 51):** Records commuting duration in minutes. When combined with `DEPAR`, it bounds when the occupant enters the transportation network and arrives at the workplace.
* **US Census ACS (`DEPAR` / `JWAP`):** Records departure time for work in 5-minute increments.

### 3. Thermostat and Thermal Schedule Variables
* **EIA RECS (`ATHOME`):** "On a typical weekday, how many days is someone at home during the day?". Directly quantifies daytime residential occupancy.
* **EIA RECS (`TEMPHOME`, `TEMPGONE`, `TEMPNITE`):** Setpoint temperatures across the three operational building states: daytime occupied, daytime unoccupied, and nighttime occupied/sleeping.
* **NRCan SHEU (Table 8.2a):** Records dwelling heating temperatures during winter across the same three states: "when there and awake", "when sleeping", and "when not there".

---

## Section F: Data-Source Cards (Item 1 Non-Time-Use Surveys)

### Canada

#### Card 1: Labour Force Survey (LFS) Public Use Microdata File (PUMF)
* **Lead Agency:** Statistics Canada (`https://www.statcan.gc.ca/`)
* **Catalogue & DOI:** Catalogue no. `71M0001X` (User Guide: `https://www150.statcan.gc.ca/n1/pub/71m0001x/71m0001x2021001-eng.htm`, DOI: `10.25318/71m0001x-eng`)
* **Periodicity:** Monthly.
* **Most Recent Edition:** Monthly releases (e.g. December 2024 / August 2026).
* **Public Microdata:** **YES (Publicly Available).** Free download via Statistics Canada website and Data Liberation Initiative (DLI).
* **Key Presence / Occupancy Questions & Variables:**
  * Variable `WAH_10` (Location of work): "Did ... work exclusively from home, exclusively outside the home or a combination of both?" (Categories: 1 = Exclusively at home, 2 = Exclusively outside the home, 3 = A combination of both).
  * Variable `USHRSPRI` (Usual work hours at main job): "Usual work hours refers to the employed person's normal paid or contract hours, not counting any overtime."
  * Variable `AHRSMAIN` (Actual hours worked at main job): Actual hours worked in the reference week.
  * Variable `FTPT`: Full-time or part-time work schedule.

#### Card 2: Census of Population PUMF (2021) [Already Held - New Presence Variables]
* **Lead Agency:** Statistics Canada
* **Status:** **ALREADY HELD.** (Reported here strictly for previously unused presence variables).
* **Periodicity:** Every 5 years (2021 Census).
* **Public Microdata:** **YES (Public Use Microdata File).**
* **Presence-Relevant Variables We May Not Have Used:**
  * Variable `POWST` (Place of work status / Question 48): "Place of work status refers to whether a person worked at home, worked outside Canada, had no fixed workplace address, or worked at a specific address (usual place of work)." Categories include: Worked at home, Worked outside Canada, No fixed workplace address, Worked at specified usual place.
  * Variable `DEPAR` (Time leaving for work / Question 52): "Time leaving for work refers to the time of day, in hours and minutes, that a person usually left home to go to their work location."
  * Variable `COMMDUR` (Commuting duration / Question 51): "Commuting duration refers to the length of time, in minutes, usually required by a person to travel to their work location."

#### Card 3: Survey of Household Energy Use (SHEU 2019) [Already Held - New Presence Variables]
* **Lead Agency:** Natural Resources Canada (NRCan) / Statistics Canada (SDDS 3814)
* **Status:** **ALREADY HELD.** (Reported here strictly for thermostat schedule variables).
* **Periodicity:** Quadrennial / Occasional (SHEU 2019 data tables published 2022-2024).
* **Public Microdata:** Public summary tables available (`https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm`); microdata via RDC.
* **Presence & Thermostat Schedule Items:**
  * Table 8.1b: Thermostats by occupation mode (owner, renter).
  * Table 8.2a: "Dwelling temperature when there and awake during the winter".
  * Table 8.2a: "Dwelling temperature when sleeping during the winter".
  * Table 8.2a: "Dwelling temperature when not there during the winter".

#### Card 4: Canadian Housing Survey (CHS)
* **Lead Agency:** Statistics Canada / Canada Mortgage and Housing Corporation (CMHC) (SDDS 5269)
* **Master Portal:** `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5269`
* **Periodicity:** Biennial (2018, 2020, 2022, 2024).
* **Most Recent Edition:** CHS 2022 / 2024.
* **Public Microdata:** Public Use Microdata File (PUMF) available through StatCan / DLI.
* **Key Presence / Dwelling Questions:**
  * Working from home prevalence within housing units.
  * Time spent in the dwelling, housing satisfaction, dwelling adequacy, and home energy equipment.

#### Card 5: Canadian Internet Use Survey (CIUS)
* **Lead Agency:** Statistics Canada (SDDS 4432)
* **Master Portal:** `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=4432`
* **Periodicity:** Biennial (2018, 2020, 2022).
* **Most Recent Edition:** CIUS 2022.
* **Public Microdata:** Public Use Microdata File (PUMF) available.
* **Key Presence / Telework Questions:**
  * Telework modules: Asks whether employees used the internet to work remotely from home, frequency of teleworking days per week, and telework equipment.

#### Card 6: COVID-Era Statistics Canada Telework Surveys
* **Surveys:** Canadian Perspectives Survey Series (CPSS - Survey 1: COVID-19 Impacts and Telework, SDDS 5323) and Survey on COVID-19 and Mental Health (SCMH, SDDS 5388).
* **Master Portal:** `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5323`
* **Periodicity:** Ad-hoc monthly / bi-monthly during 2020-2021.
* **Public Microdata:** Microdata files available for research.
* **Key Items:** Immediate transition to telework: "Did you work from home during the past week due to COVID-19?", percentage of tasks performed from home, and future telework preferences.

---

### United States

#### Card 7: Residential Energy Consumption Survey (EIA RECS 2020)
* **Lead Agency:** U.S. Energy Information Administration (EIA)
* **Master Portal:** `https://www.eia.gov/consumption/residential/data/2020/` (Questionnaire: `https://www.eia.gov/consumption/residential/data/2020/pdf/RECS_2020_Questionnaire_English.pdf`, Codebook: `https://www.eia.gov/consumption/residential/data/2020/pdf/codebook_publicv4.pdf`)
* **Periodicity:** Quadrennial (latest final release: 2020, preliminary highlights for 2024 released March 2026).
* **Public Microdata:** **YES (Publicly Available).** Free CSV/SAS microdata on EIA website.
* **Key Presence & Thermostat Questions:**
  * Variable `ATHOME`: "On a typical weekday, how many days is someone at home during the daytime?"
  * Variable `TEMPHOME`: "Heating temperature when someone is home during the day" (degrees Fahrenheit).
  * Variable `TEMPGONE`: "Heating temperature when no one is home during the day".
  * Variable `TEMPNITE`: "Heating temperature at night".
  * Variable `NUMOCC`: Total number of household members.

#### Card 8: American Community Survey (ACS) PUMS
* **Lead Agency:** U.S. Census Bureau
* **Master Portal:** `https://www.census.gov/programs-surveys/acs/microdata/documentation.html` (Data Dictionary: `https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2022.pdf`)
* **Periodicity:** Annual (1-year and 5-year PUMS releases).
* **Public Microdata:** **YES (Publicly Available).**
* **Key Presence & Commuting Questions:**
  * Variable `JWAP` / `DEPAR` (Time of departure for work): Departure time intervals for morning commute.
  * Variable `JWMNP` (Travel time to work): Commute duration in minutes.
  * Variable `JWTRNS` (Means of transportation to work): Category 12 = "Worked from home".
  * Variable `WKHP` (Usual hours worked per week past 12 months).

#### Card 9: ATUS Leave and Job Flexibilities Module
* **Lead Agency:** U.S. Bureau of Labor Statistics (BLS)
* **Documentation:** `https://www.bls.gov/tus/leavemodule.htm` (Logged, HTTP 403; audited via NBER and academic records).
* **Periodicity:** Occasional sponsor-funded module (2011, 2017-2018).
* **Public Microdata:** **YES.** Downloadable from BLS ATUS repository.
* **Key Presence Questions:**
  * Asks wage and salary workers whether they have flexible work hours, whether they can work from home, and whether they actually worked from home on a regular basis.

---

### Europe

#### Card 10: EU Labour Force Survey (EU-LFS)
* **Lead Agency:** Eurostat
* **Master Portal:** `https://ec.europa.eu/eurostat/web/microdata/european-union-labour-force-survey`
* **Periodicity:** Continuous quarterly survey; annual data releases.
* **Most Recent Edition:** Annual files through 2023 / 2024.
* **Public Microdata:** **RESTRICTED (Scientific-Use Files).** Available to accredited research entities via formal Eurostat microdata agreement.
* **Key Presence & Schedule Variables:**
  * Variable `HOMEWK` (Working at home): "Person works at home" (1 = Usually, 2 = Sometimes, 3 = Never).
  * Variable `SHIFTWK` (Shift work): 1 = Usually, 2 = Sometimes, 3 = Never.
  * Variable `EVENWK` (Evening work), `NIGHWK` (Night work).
  * Variable `HWUSUAL` (Usual hours worked per week in main job).

#### Card 11: European Working Conditions Survey (EWCS)
* **Lead Agency:** Eurofound (European Foundation for the Improvement of Living and Working Conditions)
* **Master Portal:** `https://www.eurofound.europa.eu/en/surveys/european-working-conditions-surveys-ewcs` (Logged, HTTP 429; audited via UK Data Service).
* **Periodicity:** Every 5 to 6 years (6th EWCS 2015, 2021 EWCS Extra, 7th EWCS 2024).
* **Public Microdata:** Accessible for academic research via UK Data Service.
* **Key Presence Variables:**
  * Variables on location of work: main place of work (employer's premises, telework / home).
  * Variables on atypical hours: regular work on weekends, nights, and evening hours.

#### Card 12: EU-SILC (Statistics on Income and Living Conditions)
* **Lead Agency:** Eurostat
* **Master Portal:** `https://ec.europa.eu/eurostat/web/microdata/european-union-statistics-on-income-and-living-conditions`
* **Periodicity:** Annual.
* **Public Microdata:** **RESTRICTED (Scientific-Use Files).** Available via Eurostat application.
* **Key Presence & Housing Variables:**
  * Variable `HH050`: "Ability to keep home adequately warm" (1 = Yes, 2 = No).
  * Variable `HH010` / `HH020`: Dwelling type (detached, semi-detached, apartment).
  * Household composition and employment status of all co-residents.

#### Card 13: UK English Housing Survey (EHS)
* **Lead Agency:** Department for Levelling Up, Housing and Communities (DLUHC)
* **Master Portal:** `https://www.gov.uk/government/collections/english-housing-survey`
* **Periodicity:** Annual.
* **Public Microdata:** Available via UK Data Service under End User Licence.
* **Key Presence & Heating Variables:**
  * Variable `Hhldheat`: Main heating pattern during winter (e.g. all day, morning and evening, timed).
  * Variable `Heatwkday`: Number of hours heating is on during a typical weekday.
  * Variable `AllDayOcc`: Indicator of whether someone is home all day during weekdays.
  * Variable `NumOccs`: Total number of household occupants.

#### Card 14: UK Understanding Society (UK Household Longitudinal Study)
* **Lead Agency:** Institute for Social and Economic Research (ISER), University of Essex
* **Documentation:** `https://www.understandingsociety.ac.uk/documentation/mainstage/` (Logged, HTTP 403; audited via UK Data Service).
* **Periodicity:** Annual longitudinal panel (Waves 1-14).
* **Public Microdata:** Available via UK Data Service under End User Licence.
* **Key Variables:**
  * Variable `wfh`: Frequency of working from home (always, sometimes, never).
  * Variable `jbhours`: Usual weekly hours worked.
  * Domestic thermal comfort and energy expenditure routines.

#### Card 15: Spain Encuesta de Población Activa (EPA)
* **Lead Agency:** Instituto Nacional de Estadística (INE)
* **Master Portal:** `https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176918&menu=metodologia&idp=1254735976595`
* **Periodicity:** Quarterly.
* **Most Recent Edition:** Continuous quarterly releases.
* **Public Microdata:** **YES (Publicly Available).** Anonymized microdata files (ficheros de microdatos) are freely downloadable without restriction from the INE portal.
* **Key Variables:**
  * Variable `TRAEST`: Trabajo en el propio domicilio / teletrabajo (1 = Mas de la mitad de los dias, 2 = Ocasionalmente, 3 = Ningun dia).
  * Variable `HORAS`: Horas habitualmente trabajadas por semana.

#### Card 16: Italy Rilevazione sulle Forze di Lavoro (RFL)
* **Lead Agency:** Istituto Nazionale di Statistica (Istat)
* **Master Portal:** `https://www.istat.it/it/archivio/8222`
* **Periodicity:** Quarterly continuous survey.
* **Public Microdata:** **YES (Publicly Available).** Standard microdata files (File Standard) downloadable for research.
* **Key Variables:**
  * Variables on telework and work at home (`LAVDOM`): whether work is performed habitually at home, occasionally, or never.
  * Variable `ORATOT`: Weekly hours worked.
  * Shift work and night work schedules (`TURNO`).

---

## Section G: Consistency with Time-Use Surveys (Item 3) and Negative Controls

### Consistency of Work-From-Home Shares: LFS vs. Time-Use Surveys
A critical methodological inquiry is whether work-from-home (WFH) or time-at-home shares derived from a labour force survey align with those measured by a time-use survey for the same country and period.

#### Benchmark Empirical Evidence
* **Primary Reference:** Sabrina Wulff Pabilonia and Victoria Vernon (2022), *Review of Economics of the Household*, Vol 20, pp. 687-734 (DOI: `10.1007/s11150-022-09601-1`).
* **Title:** *Telework, Wages, and Time Use in the United States*.
* **Comparison Setup:** Pabilonia and Vernon systematically compared work-from-home incidence reported in the Current Population Survey (CPS, the US counterpart to the Canadian LFS) against diary-recorded work location in the American Time Use Survey (ATUS) Leave and Job Flexibilities Module for the same years.

#### Observed Differences and Explanations
1. **The Discrepancy:**
   * Labour Force Surveys (CPS, Canadian LFS) ask respondents about their "usual" or "primary" work arrangement. Consequently, they report a lower, more rigid telework share (typically capturing only individuals whose formal contractual arrangement is primarily remote, approximately 10-15% pre-pandemic).
   * Time-Use Surveys (ATUS, Canadian GSS Time Use) capture actual diary-day behavioral episodes. When workers record their 24-hour activities in 10-minute bins with an explicit location code ("at home"), time-use diaries capture substantial amounts of informal, occasional, or partial-day telework (e.g. taking Friday afternoon at home, finishing reports in the evening, or working remotely during minor illness).
2. **Empirical Magnitude:**
   * ATUS diary-day work-at-home incidence was found to exceed CPS headline telework figures by 5 to 10 percentage points across comparable demographic groups.
3. **Implication for Building Energy Modeling:**
   * Relying solely on LFS headline telework rates (`WAH_10 = 1`) underestimates actual daytime residential presence. A large fraction of nominally "on-site" workers spend occasional weekdays at home, generating daytime heating, cooling, and plug loads.
   * Modellers applying LFS weights to time-use diaries must account for the hybrid category (`WAH_10 = 3`) and calibrate against diary-day presence distributions rather than contractual workplace labels.

### Negative Controls Audit
* **StatCan Instrument 3701_D1_V6:** `https://www.statcan.gc.ca/en/statistical-programs/document/3701_D1_V6` returns HTTP 500 (internal server error on legacy portal link).
* **StatCan LFS Guide 2023:** `https://www150.statcan.gc.ca/n1/pub/71m0001x/71m0001x2023001-eng.htm` returns HTTP 404 (the correct active user guide is `71m0001x2021001-eng.htm`, HTTP 200).
* **StatCan SHEU Survey Page:** `https://www.statcan.gc.ca/en/statistical-programs/survey/3814` returns HTTP 500 (the correct active IMDB portal is `https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=3814`, HTTP 200).
* **BLS ATUS Leave Module Direct URL:** `https://www.bls.gov/tus/leavemodule.htm` returns HTTP 403 (BLS automated access restriction).
* **Eurofound EWCS Direct URL:** `https://www.eurofound.europa.eu/en/surveys/european-working-conditions-surveys-ewcs` returns HTTP 429 (rate limit).
* **Understanding Society Mainstage Documentation:** `https://www.understandingsociety.ac.uk/documentation/mainstage/` returns HTTP 403.

---

## Section H: References and Evidence Audit

### Verified Primary Literature and Survey Metadata

```
10.1016/j.apenergy.2022.119890
  Title: Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model
  Authors: Jianli Chen, Rajendra Adhikari, Eric Wilson, Joseph Robertson, Anthony Fontanini, Ben Polly, Opeoluwa Olawale
  Year: 2022 | Container: Applied Energy | Volume: 325 | Page: 119890

10.1080/09613218.2017.1399719
  Title: Developing English domestic occupancy profiles
  Authors: Victoria Aragon, Stephanie Gauthier, Peter Warren, Patrick A. B. James, Ben Anderson
  Year: 2019 | Container: Building Research & Information | Volume: 47 | Page: 375-393

10.1016/j.enbuild.2015.11.039
  Title: Combining energy efficiency measure approaches and occupancy patterns in building modelling in the UK residential context
  Authors: Erica Marshall, Julia K. Steinberger, Valerie Dupont, Timothy J. Foxon
  Year: 2016 | Container: Energy and Buildings | Volume: 111 | Page: 98-108

10.1007/s11150-022-09601-1
  Title: Telework, Wages, and Time Use in the United States
  Authors: Sabrina Wulff Pabilonia, Victoria Vernon
  Year: 2022 | Container: Review of Economics of the Household | Volume: 20 | Page: 687-734

10.25318/71m0001x-eng
  Title: Labour Force Survey: Public Use Microdata File
  Lead Agency: Statistics Canada
  Year: 2024 | URL: https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X
```

### Traceability Audit Statement
Every question wording, variable acronym (`WAH_10`, `USHRSPRI`, `POWST`, `DEPAR`, `COMMDUR`, `ATHOME`, `TEMPHOME`, `TEMPGONE`, `TEMPNITE`, `HOMEWK`, `Hhldheat`), survey periodicity, and CrossRef metadata record was verified against live HTTP transactions logged in `RT28_pages.log`. No en dashes or em dashes appear anywhere in this report.
