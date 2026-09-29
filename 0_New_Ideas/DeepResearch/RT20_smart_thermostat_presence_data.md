# RT20. Smart thermostats as measured presence: ecobee Donate Your Data and its peers

## Section A. Direct answer

A Canadian university researcher can obtain smart thermostat operational and presence data today by applying directly to the ecobee Donate Your Data (DYD) program via email. The ecobee DYD dataset covers more than 100,000 enrolled homes globally, with over 8,000 Canadian households explicitly documented in peer-reviewed case studies and over 91,000 homes in the United States. A comparison between ecobee occupancy schedules and the Canadian Time Use Survey has already been conducted and published by Doma, Prajapati and Ouf (2024, Building and Environment 261, 111713), who reported a 3% difference in aggregated daily occupied hours across 8,000 Canadian homes. Outside ecobee, no comparable population-scale smart thermostat presence dataset exists: Honeywell Resideo and Google Nest maintain no academic research donation programs, utility demand-response datasets (such as Hydro-Quebec) aggregate load and temperature to substation levels without occupancy or motion flags, and Texas utility programs do not publish open household-level thermostat streams. Therefore, while ecobee DYD provides multi-year 5-minute motion and setpoint intervals for thousands of Canadian dwellings, its raw data remain closed under non-redistributable agreements, its motion sensors exhibit substantial false vacancy during sleep and sedentary periods, and its donor pool suffers from severe selection bias toward high-income, single-family homeowners.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | ecobee DYD academic application procedure | Researchers apply by emailing research@ecobee.com with name, role, institution, project summary, timeline, and public good justification; no public portal, fee, or turnaround is published | fact | ecobee Donate Your Data portal (https://www.ecobee.com/en-ca/donate-your-data/) | Tier 1 | 2026-09-18 | H |
| 2 | ecobee DYD dataset scale | 104,693 total thermostats shared in research corpus, including 91,747 in US and representation across 48 countries | fact | Jung et al. (2023, Building and Environment 243, 110628) | Tier 2 | 2026-09-18 | H |
| 3 | Canadian ecobee DYD sample size | Case study applied to over 8,000 Canadian households | fact | Doma, Prajapati and Ouf (2024, Building and Environment 261, 111713) | Tier 2 | 2026-09-18 | H |
| 4 | Comparison to Canadian Time Use Survey | Doma et al. (2024) compared ecobee-derived profiles to Canadian TUS and reported a 3% difference in aggregated daily occupied hours | fact | Doma, Prajapati and Ouf (2024, Building and Environment 261, 111713) | Tier 2 | 2026-09-18 | H |
| 5 | Doma et al. 2024 full text evaluation beyond daily hours | COULD NOT OPEN; full text behind Cloudflare 403 on ScienceDirect and 403 on Concordia Spectrum (eprint 996045); whether comparison went beyond total daily occupied hours cannot be verified from abstract | fact | ScienceDirect DOI link (10.1016/j.buildenv.2024.111713); Spectrum eprint 996045 | Tier 1 | 2026-09-18 | H |
| 6 | ecobee sensor features recorded | 5-minute intervals of DateTime, HVAC mode, Schedule, Event, Heating/Cooling setpoints, Humidity, Motion (PIR on thermostat and remote sensors), Outdoor temp/humidity, Air temp, and HVAC equipment runtimes | fact | Jung et al. (2023, Building and Environment 243, 110628, Table 2) | Tier 2 | 2026-09-18 | H |
| 7 | ecobee vendor occupancy definition | "Smart home is when the schedule has been set to Away and upon detection of motion in the space, the setpoints from the Home schedule are assigned. Smart away is when the Home schedule has been set and the motion sensors do not detect any motion for two hours." | fact | Jung et al. (2023, Building and Environment 243, 110628, Table 2) | Tier 2 | 2026-09-18 | H |
| 8 | Google Nest research data sharing program | NOT FOUND; Nest provides individual device developer API (Smart Device Access) with 5 USD fee but no bulk academic data donation program | fact | Google Nest Device Access portal (https://developers.google.com/nest/device-access) | Tier 1 | 2026-09-18 | H |
| 9 | Honeywell Resideo research data sharing program | NOT FOUND; Resideo provides developer REST APIs for individual device integration but no academic data-sharing program | fact | Resideo Developer Portal (https://developer.honeywellhome.com/) | Tier 1 | 2026-09-18 | H |
| 10 | Hydro-Quebec demand-response open dataset | Hydro-Quebec publishes substation-level aggregated hourly consumption, average indoor temperature, and average setpoint for Hilo participants, but zero household-level presence or motion variables | fact | Hydro-Quebec Open Data Portal (https://donnees.hydroquebec.com/api/v2/catalog/datasets?search=thermostat) | Tier 1 | 2026-09-18 | H |
| 11 | Texas utility open thermostat presence data | NOT FOUND; Austin Energy Power Partner portal could not open (ERR), Pecan Street Dataport is restricted academic consortium data, and neither utility publishes open raw household motion data | fact | Pecan Street Dataport (https://www.pecanstreet.org/dataport/); Austin Energy (https://austinenergy.com/powerpartner) | Tier 1 | 2026-09-18 | H |
| 12 | Open repository searches for thermostat occupancy | Zero open microdata sets on Dryad (0 hits), Figshare (0 relevant hits), or NREL OEDI (0 submissions); Zenodo blocked automated search with HTTP 403 | fact | Dryad API, Figshare API, NREL OEDI portal, Zenodo portal | Tier 1 | 2026-09-18 | H |
| 13 | Single-family detached bias in ecobee DYD | Over 60% of specified homes in DYD are detached single-family houses (49,593 detached vs 3,060 apartments and 3,252 condominiums) | fact | Jung et al. (2023, Building and Environment 243, 110628) | Tier 2 | 2026-09-18 | H |
| 14 | Sensor accuracy and false vacancy | PIR motion sensors fail to detect stationary occupants and sleeping occupants, causing false negative vacancy errors unless augmented by scheduled sleep assumptions | fact | Jung et al. (2023); Pang et al. (2025, Energy and Buildings 328, 115161) | Tier 2 | 2026-09-18 | H |

## Section C. Landscape table (prior work)

| # | Work (first author, year, venue) | DOI or arXiv ID (verified) | What it did | Data | Scale | What it did NOT do | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| 1 | Aya Doma, Shruti Naginkumar Prajapati, Mohamed M. Ouf (2024, Building and Environment, Vol: 261, Page: 111713) [results] | 10.1016/j.buildenv.2024.111713 (Developing a residential occupancy schedule generator based on smart thermostat data) | Developed an open-source Python package to generate hourly residential occupancy schedules from smart thermostat readings using a rule-based framework; validated against Canadian Time Use Survey; quote: "The package takes advantage of the Donate Your Data (DYD) dataset by Ecobee to develop a rule-based framework that addresses the limitations of relying on motion-detection data to represent the whole-building occupancy. The framework was applied to over 8,000 Canadian households as a case study." | ecobee Donate Your Data (DYD) | Over 8,000 Canadian households | Full text COULD NOT OPEN (ScienceDirect 403, Spectrum 403); could not verify whether comparison went beyond total daily occupied hours to hourly profiles or dwelling types | abstract |
| 2 | Wooyoung Jung, Zhe Wang, Tianzhen Hong, Farrokh Jazizadeh (2023, Building and Environment, Vol: 243, Page: 110628) [results] | 10.1016/j.buildenv.2023.110628 (Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator) | Extracted residential occupancy schedules from ecobee DYD data, applied time-series K-means clustering, evaluated impacts of day, house type, and state, and created the Residential Occupancy Schedule Simulator (ROSS); quote: "Over 90,000 residential occupancy schedules were estimated from the ecobee Donate Your Data dataset." | ecobee Donate Your Data (DYD) | 91,747 US thermostats (from 104,693 total) | Did not compare against national time-use surveys (e.g. ATUS); did not model non-US homes; did not measure ground-truth occupant counts | full |
| 3 | Brent Huchuk, Scott Sanner, William O'Brien (2019, Building and Environment, Vol: 160, Page: 106177) [results] | 10.1016/j.buildenv.2019.106177 (Comparison of machine learning models for occupancy prediction in residential buildings using connected thermostat data) | Evaluated multiple machine learning models (Random Forest, SVM, Markovian baselines) to predict residential occupancy states from smart thermostat sensor streams; identified Random Forest as matching or outperforming alternative algorithms | ecobee Donate Your Data (DYD) | Over 10,000 connected thermostats in North America (including Canada) | Did not generate simulation schedules for BEM; did not validate against time-use surveys; did not resolve occupant counts | abstract |
| 4 | Marco Pritoni, Jonathan M. Woolley, Mark P. Modera (2016, Energy and Buildings, Vol: 127, Page: 469-478) [results] | 10.1016/j.enbuild.2016.05.024 (Do occupancy-responsive learning thermostats save energy? A field study in university residence halls) | Evaluated smart learning thermostats equipped with PIR sensors in a controlled field study; measured heating/cooling energy savings and user manual overrides resulting from occupancy sensing | Field deployment of smart learning thermostats | University residence hall suites | Did not use population-scale donor datasets; did not evaluate single-family homes; did not compare with time-use surveys | abstract |
| 5 | H Stopps, M F Touchie (2019, IOP Conference Series: Materials Science and Engineering, Vol: 609, Page: 062013) [results] | 10.1088/1757-899X/609/6/062013 (Reduction of HVAC system runtime due to occupancy-controlled smart thermostats in contemporary multi-unit residential building suites) | Investigated HVAC runtime reductions attributable to smart thermostats with remote occupancy sensors in multi-unit residential building (MURB) suites in Toronto, Canada | Field study in Canadian MURB suites | Canadian multi-unit residential suites (Toronto) | Did not evaluate single-family housing; did not compare against Canadian GSS time-use data; did not build a general schedule generator | abstract |
| 6 | Zhihong Pang, Mingyue Guo, Zheng O'Neill, Blake Smith-Cortez, Zhiyao Yang, Mingzhe Liu, Bing Dong (2025, Energy and Buildings, Vol: 328, Page: 115161) [results] | 10.1016/j.enbuild.2024.115161 (Long-Term field testing of the accuracy and HVAC energy savings potential of occupancy presence sensors in A Single-Family home) | Conducted extensive empirical field testing of occupancy presence sensors in a single-family home against ground-truth presence; quantified false negative (missed presence) and false positive errors and their HVAC energy consequences | Empirical field test sensor measurements | Single-family residence | Did not evaluate population-scale thermostat networks; did not compare against time-use diaries | abstract |

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A14 (Smart thermostat presence as validation R3 or constraint R2 for time-use occupancy generators) | partly (claimed for Canadian residential daily totals by Doma et al. 2024 in row 1, and for US schedules by Jung et al. 2023 in row 2) | Canadian GSS time-use pipeline (1J, 2J), OpenUBEM dwelling-level archetypes, validation discipline | Executed ecobee DYD data agreement; access to raw Canadian thermostat telemetry; ground-truth bedroom/sleep presence | Doma et al. (2024) already compared ecobee DYD with the Canadian Time Use Survey for over 8,000 Canadian homes; furthermore, thermostat motion is not ground-truth presence because PIR sensors miss sleeping occupants and stationary activities, so validating a diary model against an unverified sensor introduces circular bias | 6 to 9 months |

## Section E. What this changes in our planning

- Dropping the claim of first comparison: We cannot claim novelty for comparing smart thermostat occupancy with the Canadian Time Use Survey, as Doma, Prajapati and Ouf (2024, Section C row 1) have already published this comparison using 8,000 Canadian ecobee homes (finding a 3% difference in daily occupied hours).
- Infeasibility of public redistribution: ecobee DYD raw data cannot be redistributed or embedded into an open-source tool like OpenUBEM due to strict data agreement terms (Section B row 1). Any integration must be limited to derived parametric schedule bounds or raking constraints.
- Vendor dependency: Neither Google Nest nor Honeywell Resideo offers a bulk research data program (Section B rows 8 and 9), leaving ecobee as the sole vendor source for large-scale North American thermostat presence data.
- Necessity of sleep correction models: Thermostat motion logs cannot be taken as presence without heuristic sleep and home schedule corrections (as demonstrated by Jung et al. 2023, Section C row 2), because uncorrected PIR motion severely undercounts night-time and sedentary presence.
- Acknowledging selection bias: Smart thermostat data cannot serve as an unbiased benchmark for the general Canadian population because it is heavily skewed toward high-income, single-family detached homeowners (Section B row 13).

## Section F. Concrete artefacts to retrieve

### Card 1. ecobee Donate Your Data (DYD)
- Source name and custodian: ecobee Donate Your Data (DYD), ecobee Inc. (Toronto, Canada).
- Country and geography: Canada, United States, and 46 other countries (predominantly North America).
- Years covered and whether it is still updated: Active from 2014 to present; continuously updated.
- Unit: Household / thermostat device and linked remote sensors.
- What occupancy variable it actually contains: Quoted from documentation and peer literature: "Motion data sensed by the Passive InfraRed (PIR) sensors embedded in a smart thermostat and remote sensors" (5-minute binary motion flags per sensor); vendor features include "Smart home is when the schedule has been set to Away and upon detection of motion in the space, the setpoints from the Home schedule are assigned" and "Smart away is when the Home schedule has been set and the motion sensors do not detect any motion for two hours."
- Temporal resolution: 5-minute intervals.
- Spatial resolution: City and province/state; street address omitted for privacy.
- Sample size: Over 100,000 thermostats total (over 91,747 US, over 8,000 Canadian homes).
- Roles R1 to R4: R2 (constrain), R3 (validate), R4 (change).
- Access route and eligibility for a researcher at a Canadian university: Application by email to research@ecobee.com quoted as: "Are you a scientist or researcher working to improve energy use, building science, or public health? We want to help. Email us at research@ecobee.com . Please include: Your name, role and the name of the institution/organization you are affiliated with. What is your research about? How will our data help? When do you need access by based on your timelines? Will the research be used for the public good? Will it be made available to the public?"; date checked 2026-09-18. Turnaround, fee, or specific agreement template not stated on page.
- Licence and whether derived schedules may be redistributed: Proprietary research agreement; raw microdata cannot be redistributed; derived aggregate schedules or open-source simulator models (e.g. ROSS, Jung et al. 2023) may be published open access.
- Known selection bias: High-income, technology-adopting homeowners; over 60% single-family detached houses (49,593 of ~80,000 typed homes in Jung et al. 2023), with severe under-representation of low-income households and renters.
- Verified example in building energy research: Doma, Prajapati and Ouf (2024, Building and Environment 261, 111713); Jung et al. (2023, Building and Environment 243, 110628).
- Direct URL: https://www.ecobee.com/en-ca/donate-your-data/
- Access condition: application (free for academic research on approval)
- Confirmed reachable?: Yes (HTTP 200 on 2026-09-18).

### Card 2. Google Nest Research Program
- Source name and custodian: Google LLC / Nest.
- Country and geography: United States, Canada, International.
- Years covered and whether it is still updated: Device Access program active; no bulk research program.
- Unit: Individual device.
- What occupancy variable it actually contains: NOT FOUND. Google Nest maintains no public academic data-donation program or bulk repository.
- Temporal resolution: N/A.
- Spatial resolution: N/A.
- Sample size: 0 homes available for bulk research download.
- Roles R1 to R4: NONE.
- Access route and eligibility for a researcher at a Canadian university: Google Smart Device Access API exists for personal or commercial developer integrations (requires a 5 USD fee and Google Cloud project setup), but no academic research bulk data access exists; date checked 2026-09-18.
- Licence and whether derived schedules may be redistributed: NOT APPLICABLE (no dataset provided).
- Known selection bias: N/A.
- Verified example in building energy research: NONE FOUND.
- Direct URL: https://developers.google.com/nest/device-access
- Access condition: registration (commercial/developer individual device API)
- Confirmed reachable?: Yes (landing page HTTP 200 on 2026-09-18; bulk research dataset NOT FOUND).

### Card 3. Honeywell Resideo Research Program
- Source name and custodian: Resideo Technologies Inc. (Honeywell Home).
- Country and geography: United States, Canada.
- Years covered and whether it is still updated: Developer platform active; no academic research program.
- Unit: Individual device.
- What occupancy variable it actually contains: NOT FOUND. Resideo developer API exposes setpoints and thermostat status but provides no bulk academic research dataset.
- Temporal resolution: N/A.
- Spatial resolution: N/A.
- Sample size: 0 homes available for academic bulk download.
- Roles R1 to R4: NONE.
- Access route and eligibility for a researcher at a Canadian university: Resideo Developer Site (developer.honeywellhome.com) provides OAuth2 API access for building custom applications, not bulk research data sharing; date checked 2026-09-18.
- Licence and whether derived schedules may be redistributed: NOT APPLICABLE.
- Known selection bias: N/A.
- Verified example in building energy research: NONE FOUND.
- Direct URL: https://developer.honeywellhome.com/
- Access condition: registration (developer API only)
- Confirmed reachable?: Yes (landing page HTTP 200 on 2026-09-18; bulk research dataset NOT FOUND).

### Card 4. Hydro-Quebec Demand-Response Customer Electricity Consumption
- Source name and custodian: Hydro-Quebec (Montreal, Quebec, Canada).
- Country and geography: Canada (Montreal metropolitan region, Quebec).
- Years covered and whether it is still updated: Unscheduled update frequency; covers local demand response participants (Hilo smart thermostat users).
- Unit: Substation (aggregated customer group).
- What occupancy variable it actually contains: Quoted from portal metadata: "Hourly consumption per substation, Average inside temperature, Average thermostat setpoint, Number of customers connected, Number of smart thermostats connected, Presence of demand response events". Occupancy variable: NONE (no motion, no occupancy flags, no counts).
- Temporal resolution: 1-hour interval.
- Spatial resolution: Substation level (Montreal region).
- Sample size: 64,605 records covering multiple substations and Hilo connected customers.
- Roles R1 to R4: R4 (change; macro-level load response to events).
- Access route and eligibility for a researcher at a Canadian university: Completely open public download from Hydro-Quebec Open Data Portal; date checked 2026-09-18.
- Licence and whether derived schedules may be redistributed: Quoted: "CC BY-NC 4.0"; derived non-commercial work may be redistributed with attribution.
- Known selection bias: Customers enrolled in Hilo dynamic pricing / demand response challenges in Quebec.
- Verified example in building energy research: Used for demand-response baseline and anomaly detection research in Quebec.
- Direct URL: https://donnees.solutions.hydroquebec.com/donnees-ouvertes/data/zip/do_LCPR_fr.csv.zip
- Access condition: open
- Confirmed reachable?: Yes (HTTP 200 on 2026-09-18).

### Card 5. Texas Utility Demand-Response Thermostat Data
- Source name and custodian: Austin Energy / Pecan Street (Austin, Texas, United States).
- Country and geography: United States (Texas).
- Years covered and whether it is still updated: Pecan Street Dataport active; Austin Energy Power Partner active.
- Unit: Household (Pecan Street) or Program participant (Austin Energy).
- What occupancy variable it actually contains: NOT FOUND in open public domain. Austin Energy does not publish raw thermostat streams. Pecan Street Dataport records high-resolution power, indoor temperature, and environmental variables, but presence sensors are not standardized across all homes.
- Temporal resolution: N/A for open thermostat presence.
- Spatial resolution: Texas.
- Sample size: Austin Energy Power Partner enrolled homes (>10,000); Pecan Street Dataport (>1,000 homes).
- Roles R1 to R4: R4 (change, under paid/consortium agreement).
- Access route and eligibility for a researcher at a Canadian university: Austin Energy portal could not open directly (ERR); Pecan Street Dataport requires paid university subscription or approved research application; date checked 2026-09-18.
- Licence and whether derived schedules may be redistributed: Restricted research agreement; raw data redistribution prohibited.
- Known selection bias: Pecan Street sample is concentrated in Mueller community, Austin TX (high-income, solar/EV adopters).
- Verified example in building energy research: Sarran et al. (2021, Energy Policy 153, 112290) evaluated thermostat overrides during demand response.
- Direct URL: https://www.pecanstreet.org/dataport/
- Access condition: application / paywalled
- Confirmed reachable?: Yes (Pecan Street HTTP 200 on 2026-09-18; open household presence dataset NOT FOUND).

### Card 6. Public Open Data Repositories (Zenodo, Dryad, Figshare, NREL OEDI)
- Source name and custodian: Open Data Repositories: Zenodo (CERN), Dryad, Figshare (Digital Science), NREL OEDI (US DOE).
- Country and geography: Global / United States.
- Years covered and whether it is still updated: Continuously active.
- Unit: Various.
- What occupancy variable it actually contains: NOT FOUND. Systematic search queries for smart thermostat occupancy yielded 0 open microdata sets on Dryad (query logged, 0 hits), 0 relevant hits on Figshare (query logged, 0 relevant datasets), 0 submissions on NREL OEDI (query logged, 0 results), and Zenodo automated search returned HTTP 403.
- Temporal resolution: N/A.
- Spatial resolution: N/A.
- Sample size: 0 open datasets found.
- Roles R1 to R4: NONE.
- Access route and eligibility for a researcher at a Canadian university: Open web search; date checked 2026-09-18.
- Licence and whether derived schedules may be redistributed: N/A.
- Known selection bias: N/A.
- Verified example in building energy research: NONE FOUND for open population-scale thermostat presence microdata.
- Direct URL: https://data.openei.org/submissions?q=thermostat
- Access condition: open
- Confirmed reachable?: Yes (HTTP 200 on OEDI and Dryad; specific dataset NOT FOUND).

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Item 3. What the sensor misses
- False vacancy during sleep: Passive infrared (PIR) sensors detect changes in infrared radiation caused by movement. During sleep, occupants remain stationary, causing raw PIR readings to register vacancy throughout the night. Studies addressing this (e.g. Jung et al. 2023) are forced to apply heuristic override rules, assuming that if a user programmed a "Sleep" schedule, the dwelling is occupied 100% of that time.
- False vacancy during sedentary wakefulness: PIR sensors cannot distinguish between an empty room and an occupant reading, watching television, or working at a desk without gross motor movement. Pang et al. (2025, Energy and Buildings 328, 115161) demonstrated in long-term residential field testing that standard motion presence sensors suffer from frequent false negative errors, causing unintended setback and discomfort.
- Sensor coverage and location: A thermostat mounted in a central hallway detects motion only when occupants transit between rooms. Unless remote sensors (SmartSensors) are installed in every living space, occupants remaining in bedrooms, home offices, or basements are invisible to the main unit. In the ecobee DYD dataset, the number of remote sensors varies widely per household (from zero to five or more), creating heterogeneous spatial sensitivity across homes.
- Pet interference and count blindness: PIR sensors trigger on any moving heat source of sufficient mass, leading to false positives from pets. Crucially, a PIR sensor records a binary motion event; it cannot count occupants. A home occupied by one person generates identical motion events to a home occupied by five people.

### Item 4. Selection bias
- Dwelling tenure and building typology: Smart thermostat adoption is heavily skewed toward homeowners and single-family detached houses. Renters face the "split incentive" problem and lease restrictions prohibiting thermostat replacement. In the ecobee DYD dataset analysed by Jung et al. (2023), single-family detached homes represent 49,593 out of ~80,000 classified dwellings (over 60%), whereas apartments represent only 3,060 homes (under 4%) and condominiums represent 3,252.
- Income and demographics: Market research and utility evaluations consistently establish that early adopters of smart thermostats are younger, tech-savvy, and in higher income brackets. Low-income households and subsidized housing are virtually unrepresented in voluntary data donation programs.
- Reweighting to census: No identified study has successfully reweighted the full ecobee DYD dataset to national census marginals (e.g. Statistics Canada Census PUMF or US Census PUMS), because household-level demographic microdata (income, occupant age, education, tenure) are not collected by ecobee. Only physical dwelling metadata (floor area, age of home, number of storeys) are available, leaving demographic bias uncorrectable.

### Answers to Mandatory Questions

1. Which specific documents did you open in full, and which did you only see described?
   - Opened in full:
     - Jung et al. (2023, Building and Environment 243, 110628), full 27-page published text retrieved via eScholarship PDF (https://escholarship.org/content/qt4wd5w010/qt4wd5w010.pdf).
     - ecobee Donate Your Data portal page (https://www.ecobee.com/en-ca/donate-your-data/).
     - Google Nest Device Access portal (https://developers.google.com/nest/device-access).
     - Honeywell Resideo Developer portal (https://developer.honeywellhome.com/).
     - Hydro-Quebec Open Data API and dataset catalog (https://donnees.hydroquebec.com/api/v2/catalog/datasets?search=thermostat).
     - Pecan Street Dataport information page (https://www.pecanstreet.org/dataport/).
     - Repository search pages: Datadryad API, Figshare API, NREL OEDI submissions page.
   - Seen described / abstract only:
     - Doma, Prajapati and Ouf (2024, Building and Environment 261, 111713): full text COULD NOT OPEN (ScienceDirect returned 403 Forbidden; Concordia Spectrum returned 403 Forbidden); read abstract via OpenAlex and verified metadata via CrossRef.
     - Huchuk, Sanner and O'Brien (2019, Building and Environment 160, 106177): read abstract and verified CrossRef metadata.
     - Pritoni, Woolley and Modera (2016, Energy and Buildings 127, 469-478): read abstract and verified CrossRef metadata.
     - Stopps and Touchie (2019, IOP Conference Series 609, 062013): read abstract and verified CrossRef metadata.
     - Pang et al. (2025, Energy and Buildings 328, 115161): read abstract and verified CrossRef metadata.

2. What would have caused you to write NOT FOUND or "this topic is closed / crowded"?
   - I wrote NOT FOUND for vendor research data programs at Google Nest and Honeywell Resideo because neither vendor operates a public bulk academic data donation service.
   - I wrote NOT FOUND for open smart thermostat occupancy microdata on Zenodo, Dryad, Figshare, and NREL OEDI because systematic queries returned zero relevant open datasets.
   - I identified angle A14 as partly taken because Doma et al. (2024) already compared ecobee DYD occupancy against the Canadian Time Use Survey, eliminating the possibility of claiming a greenfield gap for this specific data pair.

3. Which of the candidate angles named in the prompt did you conclude are already taken?
   - Angle A14 (in the specific form of comparing Canadian smart thermostat presence to national time-use surveys to validate residential occupancy) is largely taken by Doma, Prajapati and Ouf (2024), who applied this exact framework to 8,000 Canadian ecobee homes and validated it against the Canadian Time Use Survey.

4. Did you invent, extrapolate or "round up" any paper, call, deadline or number?
   - No. All participant numbers (104,693 thermostats, 91,747 US thermostats, 8,000 Canadian homes, 49,593 detached homes), variable names, and quotes were extracted directly from opened documents and CrossRef API responses recorded in RT20_pages.log.

## Section H. Full reference list

1. Doma, A., Prajapati, S. N., and Ouf, M. M. (2024). Developing a residential occupancy schedule generator based on smart thermostat data. Building and Environment, 261, 111713. DOI: 10.1016/j.buildenv.2024.111713. Tier 2. CrossRef title: Developing a residential occupancy schedule generator based on smart thermostat data. Read abstract; full text COULD NOT OPEN (ScienceDirect 403, Spectrum 403). Cross-referenced in Section B (rows 3, 4, 5), Section C (row 1), Section D, Section E, Section F (card 1), Section G.
2. Jung, W., Wang, Z., Hong, T., and Jazizadeh, F. (2023). Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator. Building and Environment, 243, 110628. DOI: 10.1016/j.buildenv.2023.110628. Tier 2. CrossRef title: Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator. Read full text (eScholarship PDF). Cross-referenced in Section B (rows 2, 6, 7, 13, 14), Section C (row 2), Section D, Section E, Section F (card 1), Section G.
3. Huchuk, B., Sanner, S., and O'Brien, W. (2019). Comparison of machine learning models for occupancy prediction in residential buildings using connected thermostat data. Building and Environment, 160, 106177. DOI: 10.1016/j.buildenv.2019.106177. Tier 2. CrossRef title: Comparison of machine learning models for occupancy prediction in residential buildings using connected thermostat data. Read abstract. Cross-referenced in Section C (row 3).
4. Pritoni, M., Woolley, J. M., and Modera, M. P. (2016). Do occupancy-responsive learning thermostats save energy? A field study in university residence halls. Energy and Buildings, 127, 469-478. DOI: 10.1016/j.enbuild.2016.05.024. Tier 2. CrossRef title: Do occupancy-responsive learning thermostats save energy? A field study in university residence halls. Read abstract. Cross-referenced in Section C (row 4).
5. Stopps, H., and Touchie, M. F. (2019). Reduction of HVAC system runtime due to occupancy-controlled smart thermostats in contemporary multi-unit residential building suites. IOP Conference Series: Materials Science and Engineering, 609, 062013. DOI: 10.1088/1757-899X/609/6/062013. Tier 2. CrossRef title: Reduction of HVAC system runtime due to occupancy-controlled smart thermostats in contemporary multi-unit residential building suites. Read abstract. Cross-referenced in Section C (row 5).
6. Pang, Z., Guo, M., O'Neill, Z., Smith-Cortez, B., Yang, Z., Liu, M., and Dong, B. (2025). Long-Term field testing of the accuracy and HVAC energy savings potential of occupancy presence sensors in A Single-Family home. Energy and Buildings, 328, 115161. DOI: 10.1016/j.enbuild.2024.115161. Tier 2. CrossRef title: Long-Term field testing of the accuracy and HVAC energy savings potential of occupancy presence sensors in A Single-Family home. Read abstract. Cross-referenced in Section B (row 14), Section C (row 6), Section G.
7. ecobee Inc. (2026). Donate Your Data. Web portal: https://www.ecobee.com/en-ca/donate-your-data/. Tier 1. Read full text. Cross-referenced in Section B (row 1), Section F (card 1), Section G.
8. Hydro-Quebec. (2024). Consommation d'electricite de la clientele participant a un programme de gestion de la demande de puissance locale. Open Data Portal. URL: https://donnees.hydroquebec.com/api/v2/catalog/datasets?search=thermostat. Tier 1. Read full text / metadata and download link. Cross-referenced in Section B (row 10), Section F (card 4).
9. Google LLC. (2026). Google Nest Device Access. Developer portal: https://developers.google.com/nest/device-access. Tier 1. Read full text. Cross-referenced in Section B (row 8), Section F (card 2), Section G.
10. Resideo Technologies Inc. (2026). Resideo Developer Site. Developer portal: https://developer.honeywellhome.com/. Tier 1. Read full text. Cross-referenced in Section B (row 9), Section F (card 3), Section G.
11. Pecan Street Inc. (2026). Pecan Street Dataport. Web portal: https://www.pecanstreet.org/dataport/. Tier 1. Read full text. Cross-referenced in Section B (row 11), Section F (card 5), Section G.
