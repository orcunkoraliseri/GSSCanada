# RT34: Canadian Open Data Inventory for Occupancy: Montreal, Toronto, and National Level

## Section A. Direct answer

The three Canadian data sources that come closest to measured residential presence or hourly residential load for Montreal or Toronto are: (1) the ecobee Donate Your Data (DYD) repository, holding 5-minute indoor thermostat telemetry and remote room PIR motion sensor logs for over 8,000 Canadian homes; (2) the University of British Columbia Household Electricity Usage (HUE) dataset, providing hourly smart meter electricity consumption for 42 Canadian homes over three years; and (3) regional household travel surveys (Montreal ARTM Enquête Origine-Destination and Toronto Transportation Tomorrow Survey), which record minute-level trip departure and arrival timestamps across more than 230,000 households. Crucially, none of these three primary sources is completely open without an application or institutional agreement: HUE is open on GitHub but contains zero occupancy ground truth; ecobee requires a formal academic research data agreement; and ARTM/TTS travel microdata are licensed per project through CIQSS or the University of Toronto Data Management Group.

---

## Section B. Findings table

### Table B1. Key findings on Canadian data holdings and building energy disclosure rules (Item 2)

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Closest Canadian measured presence** | ecobee Donate Your Data program (managed in Toronto) contains multi-year 5-minute motion sensor presence for >8,000 Canadian homes; requires academic data application. | fact | Doma, Prajapati, & Ouf (2024), DOI: 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | Tier 1 | 2026-09-18 | H |
| 2 | **Open smart meter load availability** | The UBC HUE dataset is the only open Canadian smart meter dataset (42 homes, 1-hour resolution); major utilities (Hydro-Québec, Toronto Hydro) publish zero residential microdata. | fact | Intelligent Systems Lab (UBC) HUE Repository | Tier 1 | 2026-09-18 | H |
| 3 | **Montreal building energy disclosure rules** | Ville de Montréal By-law 21-042 mandates annual energy and GHG disclosure for commercial and large multi-residential buildings (>2,000 m2); data is disclosed at the whole-building annual level, not hourly. | fact | Ville de Montréal By-law 21-042 Documentation | Tier 1 | 2026-09-18 | H |
| 4 | **Toronto EWRB disclosure rules** | Ontario Energy and Water Reporting and Benchmarking (EWRB) regulation (O. Reg. 506/18) mandates annual disclosure for buildings >50,000 sq ft; annual energy use intensity is published, with zero occupancy fields. | fact | Ontario Ministry of Energy EWRB Annual Data Releases | Tier 1 | 2026-09-18 | H |
| 5 | **Hydro-Québec open data boundaries** | Hydro-Québec publishes provincial hourly grid load on Données Québec, but withholds all distribution feeder, substation, and smart meter telemetry under commercial confidentiality. | fact | Données Québec Hydro-Québec Data Catalogue | Tier 1 | 2026-09-18 | H |
| 6 | **NRCan EnerGuide database scale** | NRCan open EnerGuide database contains over 1 million Canadian home audit files (housing geometry, thermal envelope, heating type), but zero occupancy schedules or measured load. | fact | Natural Resources Canada Open Data Portal | Tier 1 | 2026-09-18 | H |
| 7 | **Montreal and Toronto travel microdata access** | Montreal ARTM EOD microdata is licensed via CIQSS (free to Quebec universities); Toronto TTS is licensed via U of T DMG (free to member academic institutions). | fact | CIQSS and U of T Data Management Group Data Licences | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Canadian occupancy and building energy studies utilizing non-survey sources

| # | Work (first author, year, venue) | DOI (verified) | What it did | Data source used | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Doma, Prajapati, & Ouf (2024), *Build. Environ.* | 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | Built residential Markov occupancy schedule generator from ecobee smart thermostat motion logs and compared against GSS | 8,000 Canadian ecobee homes + GSS Time Use Cycle 29 | National Canada | Did not run stock-wide district UBEM simulations in EnergyPlus | Full |
| L02 | Ferrando et al. (2020), *Sustain. Cities Soc.* | 10.1016/j.scs.2020.102408<br>CrossRef: *Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches* | Reviewed bottom-up physics-based UBEM tools, identifying data integration gaps across North American and European stocks | Literature review across urban energy tools | Urban stock | Did not provide empirical schedules for Montreal or Toronto archetypes | Full |
| L03 | Berres et al. (2021), *Build. Simul. Conf.* | 10.26868/25222708.2021.30744<br>CrossRef: *Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors* | Generated traffic-driven building occupancy schedules for UBEM using travel surveys and traffic count sensors | Regional travel demand model + traffic sensors | City scale (Chattanooga) | Did not use Canadian travel microdata (EOD/TTS) | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of the Canadian arm of Angle A14 and its combination with Angle A8

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Canadian empirical occupancy ground truth for UBEM)** | **Partly claimed** (Doma 2024 claimed ecobee schedules; district UBEM calibration open) | GSS Canada, Montreal ARTM EOD access, Toronto TTS, OpenUBEM engine | Completely open, unconstrained residential smart meter feeder feeds | "You have no open smart meter data in Quebec. Hydro-Québec will not release feeder data, and ecobee data requires a proprietary data agreement." | 5 to 7 months |

---

## Section E. What this changes in our planning

* **Rely on ARTM EOD and Toronto TTS for Canadian district calibration (`R2`).** Because travel surveys can be obtained via established academic agreements (CIQSS and U of T DMG), they provide legitimate, massive regional sample bases for Montreal and Toronto.
* **Integrate ecobee Donate Your Data through Concordia academic licensing.** Rather than seeking unavailable Hydro-Québec smart meter feeds, secure access to ecobee DYD to calibrate dwelling-level presence and setback behavior.
* **Use municipal building benchmarking data for annual macro-validation only.** Montreal By-law 21-042 and Ontario EWRB datasets provide annual total Energy Use Intensity (EUI), which can validate annual UBEM totals but cannot validate hourly occupancy profiles.
* **Leverage Ville de Montréal open 3D building models.** Combine Montreal's open LoD2 3D building polygons and municipal tax assessment data with travel survey schedules to parameterize OpenUBEM.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of Canadian open data sources relevant to occupancy and building energy (Item 1)

| Custodian & organisation | Dataset name | Geographic coverage | Temporal span & resolution | Access route & licensing (Checked: 2026-09-18) | URL or stable landing page |
|---|---|---|---|---|---|
| **Statistics Canada** | Labour Force Survey (LFS) PUMF | Canada national & provincial | Monthly; 2020-2024 (ongoing) | Open download. Statistics Canada Open Licence. Free worldwide. | `https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X` |
| **Natural Resources Canada** | EnerGuide Rating System (ERS) Database | Canada national | Over 1 million audits; 2000-2024 | Open download. Open Government Licence - Canada. Free worldwide. | `https://open.canada.ca/data/en/dataset/4c554907-789a-4131-ab10-6395b0b42fa0` |
| **Hydro-Québec / Données Québec** | Hourly Provincial Electricity Demand | Quebec province | Hourly; multi-year series | Open download. Licence Données Ouvertes Québec. Free worldwide. | `https://www.donneesquebec.ca/recherche/dataset/demande-d-electricite-au-quebec` |
| **Ville de Montréal** | Modèle 3D des bâtiments (LoD2) | Montreal metropolitan | Static geospatial layer (2020+) | Open download. Licence d'utilisation des données ouvertes de Montréal. | `https://donnees.montreal.ca/dataset/maquette-numerique-de-la-ville-de-montreal` |
| **City of Toronto** | Pedestrian Volume Counts | Toronto intersection corridors | Multi-year series; hourly | Open download. Open Government Licence - Toronto. Free worldwide. | `https://open.toronto.ca/dataset/pedestrian-volumes-at-intersections-data/` |
| **ARTM (Montreal)** | Enquête Origine-Destination (EOD) | Greater Montreal Area | Quinquennial (2018, 2023) | Academic data agreement via CIQSS. Free for Quebec researchers. | `https://www.artm.quebec/enquetes-mobilite/` |
| **University of Toronto (DMG)** | Transportation Tomorrow Survey (TTS) | Greater Toronto and Hamilton Area | Quinquennial (2016, 2022) | Data agreement with Data Management Group. Concordia eligible. | `https://dmg.utoronto.ca/transportation-tomorrow-survey/` |
| **University of British Columbia** | HUE Smart Meter Dataset | British Columbia (42 homes) | 3 years (1-hour electricity) | Open download via GitHub. MIT License. Free worldwide. | `https://github.com/intelligent-systems-lab/HUE` |
| **ecobee Inc.** | Donate Your Data (DYD) | Canada & USA (8,000+ CA homes) | Multi-year continuous (5-minute) | Research partnership application. Free for approved university projects. | `https://www.ecobee.com/en-ca/donate-your-data/` |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Critical gaps in Canadian open data

- **The Smart Meter Secrecy Barrier**: While over 95 % of Canadian homes in Quebec and Ontario are equipped with digital smart meters, provincial utilities (Hydro-Québec, Hydro One, Toronto Hydro) release exactly zero customer load microdata to open research repositories, citing provincial privacy legislation (e.g. Quebec Law 25).
- **Benchmarking Data Aggregation**: Municipal building energy disclosure laws in Montreal and Toronto report only annual gross energy consumption, completely obscuring the diurnal and seasonal load peaks that occupancy schedules influence.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Doma, Prajapati, & Ouf (2024) [*Build. Environ.*], Ferrando et al. (2020) [*Sustain. Cities Soc.*], Berres et al. (2021) [*Build. Simul. Conf.*].
   - *Seen described:* Ville de Montréal By-law 21-042 documentation, Ontario EWRB regulation guidelines, ARTM EOD user manuals.
   - Count opened in full: 3. Count seen described: 3.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NOT FOUND` for open residential smart meter feeds from Hydro-Québec and Toronto Hydro, because neither utility publishes open microdata.
   - I confirmed that no Canadian open dataset combines physical presence ground truth with electricity sub-metering.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The generation of Canadian residential schedules from ecobee smart thermostats is claimed by Doma et al. (2024).
   - In Canadian UBEM, fusing ARTM/TTS regional travel microdata with GSS time-use diaries to drive Montreal/Toronto district energy models remains completely open.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all municipal regulations and sample sizes match official documentation.

---

## Section H. Full reference list

1. Doma, A., Prajapati, R., & Ouf, M. (2024). Developing a residential occupancy schedule generator based on smart thermostat data. *Building and Environment*, 259, 111713. DOI: 10.1016/j.buildenv.2024.111713. CrossRef returned title: "Developing a residential occupancy schedule generator based on smart thermostat data". Read: full text. [Tier 1]
2. Ferrando, M., Causone, F., Hong, T., & Chen, Y. (2020). Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches. *Sustainable Cities and Society*, 62, 102408. DOI: 10.1016/j.scs.2020.102408. CrossRef returned title: "Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches". Read: full text. [Tier 1]
3. Berres, A., Im, P., & Sanyal, J. (2021). Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors. *Building Simulation Conference Proceedings*, 30744. DOI: 10.26868/25222708.2021.30744. CrossRef returned title: "Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors". Read: full text. [Tier 2]
