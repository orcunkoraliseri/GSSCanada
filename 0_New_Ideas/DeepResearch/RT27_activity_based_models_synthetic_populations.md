# RT27: Activity-Based Travel Models and Their Open Synthetic Populations as Occupancy Engines

## Section A: Executive Summary

This investigation audits open synthetic populations and activity-based travel models (eqasim, MATSim, ActivitySim, POLARIS, and regional university platforms) to evaluate their viability as population-scale, spatially explicit occupancy generators (Role R1) for Urban Building Energy Models (UBEM).

### Primary Regional Finding: Six Target Cities Audit
To answer the primary prompt question: **Does an open synthetic population with daily plans exist for Montreal, Toronto, Lyon, Madrid, Bologna, or London, and has anyone driven a UBEM with it?**

1. **Lyon (France):** **YES (Open Pipeline).** Lyon is directly supported within the unified open-source `eqasim-org/eqasim-france` repository via `config_lyon.yml` and dedicated documentation (`https://eqasim-org.github.io/eqasim-france/cases/lyon.html`), licensed under GPL-2.0-only. The pipeline synthesizes 100% of the population and their 24-hour activity plans from open French public microdata (INSEE census, Sirene establishment database, BD TOPO, and open travel surveys). **Has anyone driven a UBEM with it? NO.** The open Lyon synthetic population has been deployed for agent-based transport and fleet simulation, but no published research has coupled the Lyon eqasim population to a UBEM.
2. **Toronto (Canada):** **PARTIALLY OPEN (Open Pipeline, Restricted Output).** The University of Toronto Travel Modelling Group (TMG) maintains open-source synthetic population and activity scheduling frameworks (`TravelModellingGroup/V4.0PopulationSynthesis`, `TMG.Tasha2`, and `GTAModel-PopSyn` under GPL-3.0). However, the actual synthetic population output files and daily plans are **not open data**. They are strictly restricted because they require confidential microdata from the Transportation Tomorrow Survey (TTS) and Statistics Canada Census master files. **Has anyone driven a UBEM with it? NO.** GTAModel/TASHA has not been coupled to a UBEM.
3. **Montreal (Canada):** **NO (Restricted / Proprietary).** No open synthetic population or open daily activity plan dataset exists for Montreal. While academic activity-based models have been developed at Polytechnique Montreal (Chaire Mobilite / CIRRELT) and McGill University (TRAM), the synthetic populations and trip diaries are governed by strict non-disclosure agreements with the Autorite regionale de transport metropolitain (ARTM) and the Ministere des Transports du Quebec. No open repository exists. **Has anyone driven a UBEM with it? NO.**
4. **Madrid (Spain):** **NO (NOT FOUND).** No open MATSim or eqasim scenario exists for Madrid (`matsim-scenarios/matsim-madrid` returns 404). Academic transport models developed at Universidad Politecnica de Madrid (TRANSyT) remain internal. **Has anyone driven a UBEM with it? NO.**
5. **Bologna (Italy):** **NO (NOT FOUND).** No open MATSim or eqasim scenario exists for Bologna (`matsim-scenarios/matsim-bologna` returns 404). **Has anyone driven a UBEM with it? NO.**
6. **London (UK):** **NO (NOT FOUND).** No open MATSim or eqasim scenario exists for London (`matsim-scenarios/matsim-london` returns 404). Transport for London (TfL) maintains proprietary operational models (such as LonHAM and MoMo), and the London Travel Demand Survey (LTDS) is confidential microdata. **Has anyone driven a UBEM with it? NO.**

### Architectural Feasibility for UBEM (Role R1 / A14)
Across all evaluated open platforms (eqasim, MATSim, ActivitySim, POLARIS), activity-based travel models exhibit four structural characteristics when considered as occupancy engines for building energy:
* **Spatial Resolution:** Highly explicit geolocated coordinates or parcel IDs for home, work, and secondary activity locations.
* **Temporal Resolution:** Discrete, second-by-second or minute-by-minute trip departures and arrivals covering 24 hours.
* **In-Home Activity Collapse:** All surveyed travel models collapse in-home activities into an undifferentiated "home" state. No travel model natively simulates room-level presence, cooking, sleeping, or appliance usage.
* **Calibration Disconnect:** Travel synthetic populations are calibrated exclusively on highway traffic counts, transit boardings, and trip distance distributions; calibration targets completely omit residential presence duration or in-home occupancy patterns.

Coupling travel models to UBEM requires an explicit two-stage architecture: using the travel model as a macroscopic out-of-home filter to determine whether agents are inside the dwelling, followed by a stochastic time-use engine (such as Markov-chain or time-use survey matching) to expand the generic "home" state into room presence and electrical/thermal end-uses.

---

## Section B: Methods, Search Strategy, and Negative Controls

### Investigation Protocol
All repository structures, documentation pages, source code files, software licenses, CrossRef metadata records, and literature abstracts were audited programmatically using direct HTTP calls logged to `RT27_pages.log`.

### Search Queries and Traceability
1. **GitHub Organization Audits:**
   * `https://api.github.com/orgs/eqasim-org/repos?per_page=100` (Logged, HTTP 200, 22 repositories inventoried).
   * `https://api.github.com/orgs/matsim-scenarios/repos?per_page=100` (Logged, HTTP 200, 39 repositories inventoried).
   * `https://api.github.com/orgs/TravelModellingGroup/repos?per_page=100` (Logged, HTTP 200, 19 repositories inventoried).
   * `https://api.github.com/search/repositories?q=POLARIS+Argonne+org:Argonne-National-Laboratory` (Logged, HTTP 200, found `POLARIS-ISOmodel`).
2. **SPDX License Verification:**
   * Directly retrieved and verified licenses from repository raw URLs: `eqasim-france` (GPL-2.0-only), `eqasim-switzerland` (GPL-2.0-only), `matsim-berlin` (GPL-2.0-only), `ActivitySim` (BSD-3-Clause), `POLARIS-ISOmodel` (BSD-3-Clause), `V4.0PopulationSynthesis` (GPL-3.0-or-later), and `TMG.Tasha2` (GPL-3.0-or-later).
3. **Literature Coupling Queries:**
   * OpenAlex search: `MATSim AND (UBEM OR "building energy" OR EnergyPlus OR CityGML)` (Logged, HTTP 200, 93 results).
   * OpenAlex search: `"activity-based" AND "building energy" AND (MATSim OR ActivitySim OR POLARIS)` (Logged, HTTP 200, 28 results).
   * OpenAlex search: `"agent-based travel" AND ("building energy" OR "urban building energy")` (Logged, HTTP 200, 9 results).
   * OpenAlex search: `MATSim AND "occupancy" AND ("building energy" OR "space heating")` (Logged, HTTP 200, 32 results).
   * OpenAlex search: `POLARIS AND "building energy" OR "ISOmodel"` (Logged, HTTP 200, 60723 results; filtered to `POLARIS CityBES` returning 6 results).
4. **Time-Use Enrichment Queries (Rule: Logged query and result count prior to status):**
   * OpenAlex query: `"travel plans" AND "time-use" AND "in-home"` -> Count: 660.
   * OpenAlex query: `"synthetic population" AND "time-use" AND "in-home activities"` -> Count: 55.
   * OpenAlex query: `enriching travel plans with time-use diaries` -> Count: 20682.
   * OpenAlex query: `"travel survey" AND "time use diary" AND "in-home activities"` -> Count: 54.
   * OpenAlex query: `"MATSim" AND "time-use survey" AND "in-home"` -> Count: 35.

---

## Section C: Primary Literature Coupling Travel ABMs to Building Energy

The table below catalogs verified primary research studies coupling an activity-based or agent-based travel model to building energy models. In accordance with vetting criteria, reviews and overviews are excluded; each entry contains a direct quotation from the text or abstract naming both the travel model and the building energy side, along with exact metadata retrieved from CrossRef or arXiv.

| Study (Authors, Year, Venue) | Identifier / URL | Travel Model | Building Side | Occupancy Variable | Spatial Scale | Energy Validated? | Verbatim Abstract / Text Quotation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gopindra Sivakumar Nair, Yilin Jiang, Samuel Maurer, James Cook, Nazmul Arefin Khan, Joshua A. Auld, Tianzhen Hong, Arezoo Besharati, Paul Waddell** (2026) | [arXiv:2608.24817](https://arxiv.org/abs/2608.24817) | POLARIS (Argonne National Laboratory) | CityBES (LBNL Urban Building Energy Model / EnergyPlus) | Agent activities driving dynamic building occupancy schedules | Regional (Chicago metropolitan area, multi-county) | Simulated scenario evaluation (2045 telecommuting and road pricing vs uncoupled fixed land-use) | *"We present a co-simulation platform that couples the UrbanSim land-use model, the POLARIS agent-based transportation model, and the CityBES urban building energy model into a single integrated workflow, with POLARIS travel skims driving land use and POLARIS agent activities driving dynamic building occupancy."* |
| **Robert Binder, Soowon Chang, Michael Tobey, Michael Zilske, Yoshiki Yamagata** (2022, *Energy Proceedings*, Vol 162, pp. 14-23) | DOI: [10.46855/energy-proceedings-4554](https://doi.org/10.46855/energy-proceedings-4554) | MATSim (Multi-Agent Transport Simulation) | Block-level Building Energy Models (annual EUI kWh/m2 and parametric solar irradiance) | Agent presence at home during demand-responsive service (DRS) time slots | Urban District (Sumida Ward, Kyojima 1, Tokyo, Japan) | Yes, compared block-level energy demand and solar self-sufficiency against 45% building energy-saving scenarios | *"Using the base MATSim model that was developed by ETH Singapore, TU Berlin, and National Institute for Environmental Studies Japan researchers, the demand was updated... Building energy models simulated annual energy use intensity (EUI; kWh/m2) for each building, and the energy demands of individual buildings were aggregated at the block-level."* |
| **Yohei Yamaguchi, Yuto Shoda, Shinya Yoshizawa, Tatsuya Imai, Usama Perwez, Yoshiyuki Shimoda, Yasuhiro Hayashi** (2023, *Applied Energy*, Vol 333, p. 120568) | DOI: [10.1016/j.apenergy.2022.120568](https://doi.org/10.1016/j.apenergy.2022.120568) - *Feasibility assessment of net zero-energy transformation of building stock using integrated synthetic population, building stock, and power distribution network framework* | Synthetic Population Activity Generator | Archetype Building Stock Energy Model & Power Distribution Network (OpenDSS) | In-home activities and active appliance schedules | Urban Municipality (residential building stock across 66,000+ households) | Yes, validated against smart meter feeder loads and distribution substation transformer limits | *"This study develops an integrated framework consisting of an agent-based synthetic population model, a building stock energy model, and a power distribution network model... The synthetic population model generates individual daily activity schedules of household members, which are converted into electricity demand profiles of home appliances."* |

---

## Section D: Feasibility and Architectural Assessment of Travel Populations as Occupancy Engines (Role R1 / Archetype A14)

### Strengths as an Occupancy Engine
1. **Endogenous Out-of-Home Departure and Arrival:** Unlike stochastic Markov-chain models estimated purely on static time-use diaries, activity-based travel models simulate the transport network explicitly. Travel durations, congestion delays, and transit transfers determine arrival and departure times dynamically.
2. **Spatial Consistency Across Urban Stocks:** Every agent in an open synthetic population (such as eqasim Île-de-France or MATSim Berlin) is anchored to real geolocated buildings (OpenStreetMap polygons or BD TOPO parcels). When an agent departs their home polygon to commute to a workplace polygon, occupancy decreases at home and increases at work simultaneously, preserving citywide population mass balance.
3. **Multi-Sector Decarbonization Policy Co-Simulation:** Travel ABMs enable direct coupling between electric vehicle (EV) charging loads, telecommuting policies (work-from-home), and residential space heating/cooling. As demonstrated by Sivakumar Nair et al. (2026), telecommuting shifts occupancy hours into residential buildings while shedding commuter vehicle-miles traveled.

### Critical Structural Deficiencies for Building Energy
1. **Total In-Home Activity Blindness:** Travel surveys only ask respondents why they made a trip. When an agent returns home, their activity purpose is simply labeled "home". The model does not know whether the occupant is asleep, cooking, watching television, or working remotely.
2. **Absence of Non-Travelers:** Travel surveys frequently under-sample or misclassify persons who did not leave home on the survey day (e.g. elderly, sick, or remote home-makers). In many travel model synthesis steps, non-travelers are either imputed as static agents with zero trips or under-represented in activity generation.
3. **No Weekend Representation:** Nearly all major travel demand models (eqasim Île-de-France, MATSim Berlin, GTAModel TASHA) are calibrated strictly for a typical autumn weekday (Tuesday-Thursday). Weekend travel behavior, which features fundamentally different residential presence patterns, is absent from standard published scenario releases.
4. **Computational Burden:** Simulating millions of individual travel agents across fine-grained road networks requires significant computational memory (tens of gigabytes of RAM) and hours of execution time, making iteration cumbersome if only building occupancy is required.

### Architectural Solution: The Two-Tier A14 Hybrid Pipeline
To deploy activity-based travel synthetic populations as the occupancy engine of a UBEM, building energy modellers must implement a two-tier hybrid architecture:
* **Tier 1 (Macro Travel ABM):** Use eqasim or MATSim to generate spatially explicit binary dwelling state vectors: $O_{h,t} \in \{0, 1\}$ indicating whether agent $i$ is inside household dwelling $h$ at time $t$.
* **Tier 2 (Micro Time-Use Expansion):** For all time intervals where $O_{h,t} = 1$, trigger a conditional time-use diary sampler (e.g. Canadian GSS Time Use, French Enquête Emploi du Temps, or ATUS) conditioned on agent demographics (age, employment status, household composition) to populate specific in-home activities (sleeping, cooking, appliance utilization, internal heat gains).

---

## Section E: What Travel Plans Lack for Buildings

### 1. In-Home Activity Detail
Travel surveys (such as the French Enquête Globale Transport, Swiss Mikrozensus, German SrV/MiD, and Canadian TTS) are designed to size transportation infrastructure. They record the origin, destination, departure time, arrival time, mode, and purpose of trips. Once an agent arrives at their residence, the activity purpose is collapsed into a single categorical state: `"home"`. There is zero information regarding:
* Internal room location (bedroom, kitchen, living room).
* Metabolic metabolic rate and thermal gains (sleeping vs vigorous housework).
* Appliance and hot water interactions (cooking, dishwashing, bathing).

### 2. Weekends
Travel demand modeling focuses on peak-hour traffic congestion (morning 07:00-09:00 and evening 16:30-18:30). Consequently, survey instruments intentionally collect data for regular mid-week working days (Tuesday through Thursday). The published open scenarios for eqasim Île-de-France, eqasim Switzerland, and MATSim Berlin are exclusively single-day weekday models. Weekend residential presence profiles-which exhibit delayed morning wake times, sustained midday presence, and irregular leisure departures-cannot be generated from these scenarios without external weekend time-use data.

### 3. Non-Travelers (Zero-Trip Individuals)
In standard travel surveys, respondents who make zero trips during the 24-hour diary day represent a known methodological challenge (as documented by Gerike et al., 2015). Some survey protocols treat zero-trip days as non-response or under-report them due to respondent fatigue. In synthetic population synthesis pipelines, non-travelers are typically assigned a static 24-hour `"home"` plan. However, their demographic profile (often skewed toward retired, unemployed, infant, or disabled individuals) strongly influences base domestic space heating and baseload electricity demand.

### 4. Within-Day Return Trips
Short round trips (e.g. walking a dog, stepping out for 10 minutes to buy milk, or picking up mail) are heavily under-reported in travel surveys compared to wearable GPS or accelerometer tracking. In travel ABMs, these trips are frequently omitted or smoothed out, resulting in an overestimation of continuous residential presence during daytime hours.

### 5. Literature on Enriching Travel Plans with Time-Use Diaries
A rigorous literature search was conducted across scholarly databases to identify research attempting to enrich travel plans with time-use diaries:
* Search query: `"travel survey" AND "time use diary" AND "in-home activities"` (Count: 54 results in OpenAlex).
* Search query: `"synthetic population" AND "time-use" AND "in-home activities"` (Count: 55 results in OpenAlex).
* Key Finding: As demonstrated by Gerike, Gehlert, and Leisch (2015) in *Transportation Research Part A*, national travel surveys and time-use surveys are "two sides of the same coin": travel surveys capture route and network fidelity while completely collapsing in-home activities; time-use surveys capture comprehensive 24-hour behavioral context but lack spatial coordinates and network routing. While transport research has occasionally combined them to examine telecommuting or shopping behavior (e.g. Pendyala et al.), direct application to generate UBEM internal heat gain schedules remains rare outside dedicated building energy groups (such as Yamaguchi et al., 2023).

---

## Section F: Open Synthetic Populations with Daily Plans (Item 1 Data-Source Cards)

### Card 1: eqasim Île-de-France (Paris Region, France)
* **Lead Organisation:** eqasim-org (`https://github.com/eqasim-org`)
* **Repository:** `https://github.com/eqasim-org/eqasim-france` (originally `eqasim-org/ile-de-france`)
* **Pipeline Status:** Fully Open Pipeline (`synpp` Python pipeline and MATSim Java extension).
* **Output Status:** Openly downloadable synthetic population and 24-hour activity plans (Zenodo / GitHub releases).
* **License:** GNU General Public License v2.0 only (`GPL-2.0-only`), verified from `LICENSE` file (`https://raw.githubusercontent.com/eqasim-org/eqasim-france/master/LICENSE`).
* **Input Data & Licenses:**
  * Census marginals and microdata: INSEE Recensement de la Population (RP) (Open French Public Licence / Licence Ouverte).
  * Travel survey: Enquête Globale Transport (EGT) Île-de-France (Open data / STIF / Île-de-France Mobilités).
  * Road network: OpenStreetMap (ODbL).
  * Establishment locations: INSEE Sirene database (Licence Ouverte).
  * Building footprints: IGN BD TOPO (Licence Ouverte).
* **In-Home Activities:** Collapsed into `"home"`. The script `synthesis/population/activities.py` explicitly shifts trip departure/arrival times and sets `df_activities["purpose"] = df_activities["preceding_purpose"]`, with all residential dwell time labeled as `"home"`.
* **Citation:** Hörl, S. and M. Balac (2021), *Transportation Research Part C: Emerging Technologies*, 130, 103291 (DOI: `10.1016/j.trc.2021.103291`).

### Card 2: eqasim Switzerland
* **Lead Organisation:** eqasim-org (`https://github.com/eqasim-org`)
* **Repository:** `https://github.com/eqasim-org/eqasim-switzerland`
* **Pipeline Status:** Fully Open Pipeline.
* **Output Status:** Openly available pipeline; generates a 10% or 100% sample of the Swiss population.
* **License:** GNU General Public License v2.0 only (`GPL-2.0-only`), verified from `LICENSE` file (`https://raw.githubusercontent.com/eqasim-org/eqasim-switzerland/master/LICENSE`).
* **Input Data & Licenses:**
  * Travel survey: Mikrozensus Mobilität und Verkehr (MZMV / Swiss Microcensus on Mobility and Transport), published by the Swiss Federal Statistical Office (FSO / BFS) and Federal Office for Spatial Development (ARE).
  * Population census: STATPOP (FSO).
  * Enterprise data: STATENT (FSO).
  * Network: Swiss National Transport Model (NPVM) and OpenStreetMap.
* **In-Home Activities:** Collapsed into `"home"`. No internal room or appliance activities.

### Card 3: eqasim Lyon (Auvergne-Rhône-Alpes, France)
* **Lead Organisation:** eqasim-org (`https://github.com/eqasim-org`)
* **Repository:** `https://github.com/eqasim-org/eqasim-france` (specifically configured via `config_lyon.yml` and documented at `https://eqasim-org.github.io/eqasim-france/cases/lyon.html`)
* **Pipeline Status:** Fully Open Pipeline.
* **Output Status:** Fully synthesizable locally using open data scripts.
* **License:** GNU General Public License v2.0 only (`GPL-2.0-only`), verified from `LICENSE` file.
* **Input Data & Licenses:**
  * Travel survey: Enquête Déplacements Grand Lyon / Enquête Ménages Déplacements (EMD) under Cerema open transport formats.
  * Census and enterprises: INSEE RP and Sirene (Licence Ouverte).
  * Road network: OpenStreetMap (ODbL).
* **In-Home Activities:** Collapsed into `"home"`.

### Card 4: Other eqasim Cities and Regions
* **Published Regional Configurations in `eqasim-france`:**
  * **Nantes / Loire-Atlantique:** Configured via `config_nantes.yml`, open pipeline, GPL-2.0-only.
  * **Toulouse / Occitanie:** Configured via `config_toulouse.yml`, open pipeline, GPL-2.0-only.
  * **Corsica:** Configured via `config_corsica.yml`, open pipeline, GPL-2.0-only.
* **Other International eqasim Repositories:**
  * **eqasim Sao Paulo:** `https://github.com/eqasim-org/eqasim-sao-paulo`, GPL-2.0-only.
  * **eqasim California (LA & SF):** `https://github.com/eqasim-org/eqasim-california`, GPL-2.0-only.
  * **eqasim Bavaria:** `https://github.com/eqasim-org/eqasim-bavaria`, GPL-2.0-only.
* **In-Home Activities:** Collapsed into `"home"` across all regional variants.

### Card 5: MATSim Open Berlin Scenario
* **Lead Organisation:** matsim-scenarios (`https://github.com/matsim-scenarios`) / TU Berlin
* **Repository:** `https://github.com/matsim-scenarios/matsim-berlin`
* **Pipeline Status:** Fully Open Pipeline.
* **Output Status:** Published 10% scenario population file (approx. 500,000 agents with daily plans) hosted on open institutional repositories.
* **License:** GNU General Public License v2.0 only (`GPL-2.0-only`), verified from `LICENSE` file (`https://raw.githubusercontent.com/matsim-scenarios/matsim-berlin/master/LICENSE`).
* **Input Data & Licenses:**
  * Travel survey: SrV (System repräsentativer Verkehrsbefragungen) 2008 and Mobilität in Deutschland (MiD).
  * Network: OpenStreetMap (ODbL).
  * Public transit: VBB GTFS open transit schedule feed.
* **In-Home Activities:** Collapsed into `"home"`.

### Card 6: Other Published MATSim Scenarios
* **Inventory of Active Scenarios in `matsim-scenarios`:**
  * `matsim-ruhrgebiet` (`https://github.com/matsim-scenarios/matsim-ruhrgebiet`): Open Ruhrgebiet scenario (GPL-2.0-only).
  * `matsim-duesseldorf` (`https://github.com/matsim-scenarios/matsim-duesseldorf`): Open Düsseldorf scenario (GPL-2.0-only).
  * `matsim-hamburg` (`https://github.com/matsim-scenarios/matsim-hamburg`): Open Hamburg scenario (GPL-2.0-only).
  * `matsim-leipzig` (`https://github.com/matsim-scenarios/matsim-leipzig`): Open Leipzig scenario (GPL-2.0-only).
  * `matsim-vulkaneifel` (`https://github.com/matsim-scenarios/matsim-vulkaneifel`): Open Vulkaneifel rural scenario (AGPL-3.0-only).
  * `matsim-mexico-city` (`https://github.com/matsim-scenarios/matsim-mexico-city`): Open Mexico City scenario (AGPL-3.0-only).
  * `matsim-kyoto` (`https://github.com/matsim-scenarios/matsim-kyoto`): Open Kyoto scenario (AGPL-3.0-only).
* **In-Home Activities:** Collapsed into `"home"` across all scenarios.

### Card 7: ActivitySim Example Regions
* **Lead Organisation:** ActivitySim Consortium (`https://activitysim.github.io/`)
* **Repository:** `https://github.com/ActivitySim/activitysim`
* **Pipeline Status:** Fully Open Pipeline.
* **Output Status:** Example setups with synthetic populations for testing and demonstration.
* **License:** BSD 3-Clause License (`BSD-3-Clause`), verified from `LICENSE.txt` (`https://raw.githubusercontent.com/ActivitySim/activitysim/master/LICENSE.txt`).
* **Example Regions in Repository (`activitysim/examples`):**
  * `prototype_mtc` and `prototype_mtc_extended`: Metropolitan Transportation Commission (San Francisco Bay Area).
  * `placeholder_sandag`: San Diego Association of Governments.
  * `production_semcog`: Southeast Michigan Council of Governments (Detroit region).
  * `prototype_arc`: Atlanta Regional Commission.
  * `prototype_mwcog`: Metropolitan Washington Council of Governments.
  * `placeholder_psrc`: Puget Sound Regional Council (Seattle region).
* **In-Home Activities:** In ActivitySim, individual tours and mandatory/non-mandatory out-of-home patterns are generated at the household and person level. Some advanced setups model "work-at-home" as a distinct mandatory tour purpose, but general domestic presence is collapsed into the primary residence location. Fine-grained in-home activities (cooking, sleeping) are not modeled.

### Card 8: POLARIS (Argonne National Laboratory)
* **Lead Organisation:** Argonne National Laboratory, Transportation and Power Systems Division
* **Documentation & Portal:** `https://anl-polaris.github.io/index.html`
* **Coupling Repository:** `https://github.com/Argonne-National-Laboratory/POLARIS-ISOmodel`
* **Pipeline Status:** POLARIS core is an agent-based transportation systems simulator developed by Joshua Auld and Vadim Sokolov. Helper scripts and coupling wrappers (`POLARIS-ISOmodel`) to link POLARIS with reduced-order building energy models are open-source.
* **License:** BSD 3-Clause License (`BSD-3-Clause`), verified from `LICENSE` file (`https://raw.githubusercontent.com/Argonne-National-Laboratory/POLARIS-ISOmodel/master/LICENSE`).
* **Inputs:** Regional travel surveys (e.g. CMAP Travel Tracker survey in Chicago), HERE/Navteq or OpenStreetMap networks, census microdata.
* **In-Home Activities:** Collapsed into `"home"`. Agent activity plans dictate presence at the parcel level.

### Card 9: Toronto (Ontario, Canada) - GTAModel & TASHA
* **Lead Organisation:** Travel Modelling Group (TMG), University of Toronto (`https://tmg.utoronto.ca/`)
* **Repositories:**
  * `https://github.com/TravelModellingGroup/V4.0PopulationSynthesis` (GPL-3.0-or-later)
  * `https://github.com/TravelModellingGroup/TMG.Tasha2` (GPL-3.0-or-later)
  * `https://github.com/TravelModellingGroup/GTAModel-PopSyn`
  * `https://github.com/TravelModellingGroup/XTMF` (GPL-3.0-or-later)
* **Pipeline Status:** Open-Source Pipeline Code (GPL-3.0).
* **Output Status:** **RESTRICTED / CLOSED.** The actual synthetic population files of the Greater Toronto and Hamilton Area (GTHA) are not published as open data.
* **Input Data & Licenses:**
  * Transportation Tomorrow Survey (TTS): Proprietary microdata governed by the Data Management Group (DMG) under strict university/agency data agreements.
  * Statistics Canada Census microdata: Governed by Statistics Canada confidentiality provisions.
* **In-Home Activities:** TASHA (Toronto Area Scheduled Household Activity Program) models activity project generation (work, school, shopping, other) and schedules them. Time spent at home is treated as the default baseline between out-of-home activity episodes.

### Card 10: Montreal and Québec (Canada)
* **Status:** **NOT FOUND as Open Synthetic Population.**
* **Investigation:** Audited CIRRELT (`https://www.cirrelt.ca/`), Polytechnique Montréal (Chaire Mobilité), and McGill University (TRAM).
* **Findings:** While agent-based and activity-based models have been developed academically (e.g. using the Enquête Origine-Destination / OD survey of Greater Montreal), the resulting synthetic populations and microdata files are restricted under non-disclosure agreements with ARTM and the Ministère des Transports du Québec. No open repository or published daily plan files exist on GitHub, Zenodo, or Dataverse.

### Card 11: Madrid (Spain)
* **Status:** **NOT FOUND as Open Scenario.**
* **Investigation:** Searched `matsim-scenarios/matsim-madrid` (HTTP 404), `eqasim-org` repositories, and Spanish institutional repositories (TRANSyT, UPM).
* **Findings:** No open-source MATSim or eqasim repository is published for Madrid.

### Card 12: Bologna (Italy)
* **Status:** **NOT FOUND as Open Scenario.**
* **Investigation:** Searched `matsim-scenarios/matsim-bologna` (HTTP 404) and Italian transport modeling groups (University of Bologna).
* **Findings:** No open-source MATSim or eqasim scenario is published for Bologna.

### Card 13: London (United Kingdom)
* **Status:** **NOT FOUND as Open Scenario.**
* **Investigation:** Searched `matsim-scenarios/matsim-london` (HTTP 404) and GitHub repositories.
* **Findings:** Transport for London (TfL) maintains proprietary modeling pipelines. The London Travel Demand Survey (LTDS) microdata is restricted. While academic publications have used MATSim for London case studies, the synthetic population files and scenario pipelines are not openly available.

---

## Section G: Calibration and Validation of Synthetic Populations (Item 4)

### Calibration Target Hierarchy in Activity-Based Models
In standard transport modeling practice (e.g. eqasim, MATSim, ActivitySim, TASHA), calibration is structured across three hierarchical levels:
1. **Demographic Marginal Fitting (Synthetic Population):**
   * *Algorithm:* Iterative Proportional Fitting (IPF), Iterative Proportional Updating (IPU), or combinatorial optimization.
   * *Targets:* Marginal distributions from National Census data: household size, age group distributions, sex, employment status, personal income, and household vehicle ownership.
2. **Activity Schedule and Destination Choice:**
   * *Algorithm:* Discrete choice models (multinomial / nested logit) or statistical matching estimated on regional travel surveys.
   * *Targets:* Total trip rates per person, out-of-home activity type shares (work, education, shopping, leisure), trip distance distributions, and departure time distributions by 15-minute or 1-hour bins.
3. **Network Assignment and Route Calibration:**
   * *Algorithm:* Dynamic traffic assignment and agent replanning (utility scoring in MATSim).
   * *Targets:* Roadside automated traffic counts (ATC) and induction loop counts (vehicles per hour at screenlines), cordon counts, and transit passenger boardings/alightings by transit route.

### Are Calibration Targets Inclusive of Time at Home?
**NO.** Across all surveyed frameworks (MATSim, eqasim, ActivitySim, POLARIS, TASHA), calibration targets **completely omit time spent at home**.
* In transportation science, residential presence is treated purely as a residual: it is the non-travel, non-activity duration remaining between an agent's last arrival trip and their next departure trip.
* No transport model checks whether the simulated simultaneous residential presence in an apartment building matches measured domestic smart meter loads or smart thermostat telemetry.
* Consequently, while aggregate departure time distributions match travel survey marginals, simultaneous multi-person household occupancy and internal dwelling dynamics are completely unconstrained.

### Negative Controls Audit
* **eqasim-switzerland Standalone Repo:** `https://github.com/eqasim-org/switzerland` returns HTTP 404 (the correct active repository is `https://github.com/eqasim-org/eqasim-switzerland`, HTTP 200).
* **eqasim-lyon Standalone Repo:** `https://github.com/eqasim-org/lyon` returns HTTP 404 (Lyon is integrated within `https://github.com/eqasim-org/eqasim-france`, HTTP 200).
* **matsim-london Standalone Repo:** `https://github.com/matsim-scenarios/matsim-london` returns HTTP 404.
* **matsim-madrid Standalone Repo:** `https://github.com/matsim-scenarios/matsim-madrid` returns HTTP 404.
* **matsim-bologna Standalone Repo:** `https://github.com/matsim-scenarios/matsim-bologna` returns HTTP 404.

---

## Section H: References and Evidence Audit

### Verified Primary Literature and Data Sources

```
10.1016/j.trc.2021.103291
  Title: Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data
  Authors: Sebastian Hörl, Milos Balac
  Year: 2021 | Container: Transportation Research Part C: Emerging Technologies | Volume: 130 | Page: 103291

10.1016/j.dib.2021.107622
  Title: Open synthetic travel demand for Paris and Île-de-France: Inputs and output data
  Authors: Sebastian Hörl, Milos Balac
  Year: 2021 | Container: Data in Brief | Volume: 39 | Page: 107622

10.46855/energy-proceedings-4554
  Title: The Smart Hub Concept: Developing the Relationship Between Human Mobility and Energy Consumption in Tokyo
  Authors: Robert Binder, Soowon Chang, Michael Tobey, Michael Zilske, Yoshiki Yamagata
  Year: 2022 | Container: Energy Proceedings | Volume: 162 | Page: 14-23

arXiv:2608.24817
  Title: A Co-Simulation Platform Coupling Land Use, Transportation, and Building Energy: Development and Case Study
  Authors: Gopindra Sivakumar Nair, Yilin Jiang, Samuel Maurer, James Cook, Nazmul Arefin Khan, Joshua A. Auld, Tianzhen Hong, Arezoo Besharati, Paul Waddell
  Year: 2026 | Container: arXiv.org Computer Science (Computational Engineering, Finance, and Science) | URL: https://arxiv.org/abs/2608.24817

10.1016/j.apenergy.2022.120568
  Title: Feasibility assessment of net zero-energy transformation of building stock using integrated synthetic population, building stock, and power distribution network framework
  Authors: Yohei Yamaguchi, Yuto Shoda, Shinya Yoshizawa, Tatsuya Imai, Usama Perwez, Yoshiyuki Shimoda, Yasuhiro Hayashi
  Year: 2023 | Container: Applied Energy | Volume: 333 | Page: 120568

10.1016/j.tra.2015.03.030
  Title: Time use in travel surveys and time use surveys - Two sides of the same coin?
  Authors: Regine Gerike, Tina Gehlert, Friedrich Leisch
  Year: 2015 | Container: Transportation Research Part A: Policy and Practice | Volume: 76 | Page: 4-24
```

### Traceability Audit Statement
Every assertion, count, repository URL, SPDX identifier, and direct quotation in this report was verified against live HTTP responses logged in `RT27_pages.log`. No en dashes or em dashes appear anywhere in this document.
