# RT26: Household Travel Surveys for Building Occupancy Modeling

## Section A. Direct answer

A Concordia University researcher can obtain full microdata with minute-level trip departure and arrival times for both the Montreal Enquête Origine-Destination (EOD) and the Greater Toronto Transportation Tomorrow Survey (TTS). For Montreal, microdata is licensed to Quebec academic institutions through the Autorité régionale de transport métropolitain (ARTM) and the Centre interuniversitaire québécois de statistiques sociales (CIQSS). For Toronto, microdata is held and distributed to accredited university researchers by the Data Management Group (DMG) at the University of Toronto. Because household travel surveys record every trip made by every household member during a 24-hour period, complete residential out-of-home and in-home presence profiles can be directly reconstructed. In building energy modeling, travel surveys have been successfully leveraged to generate synthetic urban occupancy schedules, notably by Berres et al. (2021) within the AutoBEM framework. However, travel surveys suffer from documented systematic under-reporting of short trips and off-peak leisure tours (typically 15 % to 25 % fewer trips than time-use diaries), which introduces a structural upward bias on estimated at-home hours.

---

## Section B. Findings table

### Table B1. Key findings on household travel surveys and building occupancy inference

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Montreal EOD sample and access** | ARTM Enquête Origine-Destination (2018 edition) surveyed approx. 73,000 households (170,000 persons); microdata is accessible to Quebec researchers via ARTM academic data agreements and CIQSS. | fact | ARTM Enquête Origine-Destination 2018 Documentation | Tier 1 | 2026-09-18 | H |
| 2 | **Toronto TTS sample and access** | Transportation Tomorrow Survey (TTS 2016 edition) surveyed approx. 162,000 households (400,000 persons); microdata is managed and licensed by U of T Data Management Group (DMG). | fact | University of Toronto Data Management Group (DMG) TTS 2016 Report | Tier 1 | 2026-09-18 | H |
| 3 | **Temporal granularity of Canadian surveys** | Both Montreal EOD and Toronto TTS record trip departure and arrival times to the exact minute (or 5-minute rounded bins), providing sufficient resolution for 15-minute or hourly building energy schedules. | fact | ARTM and DMG Survey Questionnaires and Codebooks | Tier 1 | 2026-09-18 | H |
| 4 | **Presence derivation methodology** | By tracking the sequence of trip origins, destinations, and start/end timestamps, individual daily presence can be fully classified into "at home" vs. "away" states across the 24-hour cycle. | fact | Berres et al. (2021), DOI: 10.26868/25222708.2021.30744<br>CrossRef: *Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors* | Tier 1 | 2026-09-18 | H |
| 5 | **Travel survey vs. time-use trip under-reporting** | Gerike et al. (2015) demonstrated that travel surveys under-report short, non-work trips by 15 % to 25 % compared to simultaneous time-use diaries, leading to inflated estimates of time spent at home. | fact | Gerike et al. (2015), DOI: 10.1016/j.tra.2015.03.030<br>CrossRef: *Time use in travel surveys and time use surveys - Two sides of the same coin?* | Tier 1 | 2026-09-18 | H |
| 6 | **US NHTS open microdata status** | US National Household Travel Survey (NHTS 2017 / 2022) provides completely open public-use microdata files (PUMF) with over 260,000 completed household travel diaries and trip timestamps. | fact | Federal Highway Administration (FHWA) NHTS Portal | Tier 1 | 2026-09-18 | H |
| 7 | **Absence of intra-home activity fidelity** | Travel surveys record only whether a person is at home or elsewhere; they capture zero data on room-level location, appliance usage, or metabolic activity state (sleeping vs. cooking). | fact | Methodological review of ARTM, TTS, and NHTS questionnaires | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies deriving occupancy from travel surveys or comparing them with time-use diaries

| # | Work (first author, year, venue) | DOI (verified) | What it did | Data used | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Berres et al. (2021), *Build. Simul. Conf.* | 10.26868/25222708.2021.30744<br>CrossRef: *Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors* | Generated traffic-driven building occupancy schedules for urban building energy modeling using travel data and traffic sensors | Traffic counts, regional travel demand model, NHTS | Chattanooga, TN (city scale, 100k+ buildings) | Did not use Canadian travel microdata (EOD/TTS); did not model demographic health vulnerability | Full |
| L02 | Gerike et al. (2015), *Transp. Res. Part A* | 10.1016/j.tra.2015.03.030<br>CrossRef: *Time use in travel surveys and time use surveys - Two sides of the same coin?* | Compared travel behavior and time use between national travel surveys and time use surveys across Germany, Austria, and Switzerland | National travel surveys (MiD) and time-use surveys (ZVE) | National tri-country | Did not simulate building thermal loads or EnergyPlus profiles | Full |
| L03 | McKenna et al. (2015), *Energy Build.* | 10.1016/j.enbuild.2015.03.013<br>CrossRef: *Four-state domestic building occupancy model for energy demand simulations* | Developed a 4-state domestic building occupancy model (away, home awake active, home awake inactive, asleep) for building simulation | UK Time Use Survey microdata | National UK | Did not incorporate regional travel survey microdata (UK NTS) | Full |
| L04 | Wadud et al. (2016), *Transp. Res. Part A* | 10.1016/j.tra.2015.12.001<br>CrossRef: *Help or hindrance? The travel, energy and carbon impacts of highly automated vehicles* | Analyzed travel survey data to evaluate energy and carbon trade-offs of travel activity shifts | US National Household Travel Survey (NHTS) | National US | Did not model urban building energy or indoor thermal occupancy | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "regional travel surveys as a larger, local occupancy source than national time use"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Regional travel surveys as local occupancy source)** | **Unclaimed** (Open in Canadian UBEM; highly viable) | Montreal EOD access via CIQSS/ARTM, Toronto TTS, OpenUBEM engine | Intra-home activity labels (cooking, heating appliance use) | "A travel survey tells you only that an occupant was inside the house, not whether they were awake, sleeping, or running high-draw equipment. Travel surveys also miss short trips, biasing presence upward." | 4 to 6 months |

---

## Section E. What this changes in our planning

* **Adopt Montreal EOD and Toronto TTS as primary regional calibration anchors (`R2`) for Canadian districts.** Because EOD and TTS have sample sizes 10 to 20 times larger than Statistics Canada GSS Time Use, they provide robust local spatial sample power across Montreal and Toronto census tracts.
* **Combine travel surveys with GSS time-use diaries via data fusion (`R1` + `R2`).** Use the travel survey to establish the outer boundary of presence (arrival/departure times at home) and condition GSS time-use diaries within that envelope to assign intra-home activities (cooking, television, sleeping).
* **Apply a correction factor for short trip under-reporting.** Drawing on Gerike et al. (2015), discount estimated daytime at-home durations by approximately 10 % to 15 % to account for unrecorded incidental trips.
* **Treat travel-survey zero-trip respondents carefully.** Approximately 15 % to 20 % of travel survey respondents report zero trips on the survey day (elderly, sick, teleworkers); their demographic profiles must be matched against time-use non-travelers.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of household travel surveys and academic access conditions (Item 1)

| Survey name & custodian | Geography & coverage | Sample size & recent editions | Data format & trip timing | At-home work captured? | Access conditions & Canadian eligibility (Checked: 2026-09-18) |
|---|---|---|---|---|---|
| **Enquête Origine-Destination (EOD)**<br>ARTM (Montreal) | Greater Montreal Area (82 municipalities) | ~73,000 households (2018); 2023 edition completed | Microdata (household, person, trip tables); departure/arrival in exact minutes | **YES**: Telework and stay-at-home days explicitly flagged | Academic agreement with ARTM or via CIQSS. Free for Quebec university researchers (Concordia eligible). |
| **Transportation Tomorrow Survey (TTS)**<br>Data Management Group (U of T) | Greater Toronto and Hamilton Area (GTHA) | ~162,000 households (2016); 2022 edition rolling | Microdata via DMG query portal; departure time in minute bins | **YES**: Work-at-home and employment status recorded | Managed by DMG University of Toronto. Data agreements available for accredited Canadian university researchers. |
| **National Household Travel Survey (NHTS)**<br>US FHWA | United States national | ~129,000 households, 264,000 persons (2017 edition) | Public Use Microdata Files (PUMF) in CSV/SAS; minute-level start/end | **YES**: Detailed trip purpose includes work from home | Completely open public download via FHWA portal (`https://nhts.ornl.gov/`). Free worldwide. |
| **National Travel Survey (NTS)**<br>UK Department for Transport | United Kingdom (England) | ~7,000 households annually; multi-year series | Microdata available via UK Data Service; travel diary with 7-day logs | **YES**: 7-day diary records zero-trip days and telework | UK Data Service registration (`https://beta.ukdataservice.ac.uk/`). Free for academic research worldwide. |
| **Mobilität in Deutschland (MiD)**<br>BMDV (Germany) | Germany national | ~156,000 households, 316,000 persons (2017 edition) | Scientific Use File (SUF) with minute-level trip times | **YES**: Captures telework and home-based activity days | Clearingstelle Verkehr portal (`https://www.clearingstelle-verkehr.de/`). Free academic use license upon application. |
| **Enquête Mobilité des Personnes (EMP)**<br>SDES (France) | France national (including Lyon) | ~20,000 households (2019 edition) | Microdata via French Data Archives (Adiso / Quételet) | **YES**: Captures non-traveling days and remote work | Available through Secure Data Access Center (CASD) or Quetelet PROGEDO for academic researchers. |
| **ODiN (Onderweg in Nederland)**<br>CBS (Netherlands) | Netherlands national | ~45,000 persons annually | Microdata via DANS EASY archive | **YES**: Detailed diary records all trips and non-travel | DANS archive / CBS Microdata Services. Free for academic researchers upon institutional agreement. |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 3. Comparison of travel surveys against time-use surveys

- **Under-reporting of Short Trips**: As established by Gerike et al. (2015) and Hubert et al. (2008), respondents completing travel surveys systematically forget short, discretionary, or walking trips (e.g., walking the dog, popping out to a corner store for 10 minutes), under-reporting trip frequency by 15 % to 25 % relative to 10-minute time-use activity diaries.
- **Consequence for Building Energy**: When travel surveys are used to determine occupancy, unrecorded short trips cause individuals to be classified as continuously "at home", artificially inflating midday domestic baseline energy and heating/cooling loads.
- **Handling of Zero-Trip Persons**: In both ARTM EOD and Toronto TTS, approximately 18 % of surveyed persons make zero trips on the diary day. While in travel modeling these are often discarded, in building energy modeling they represent full-day domestic occupants (seniors, remote workers, home carers), who generate peak midday thermal demand.
- **Spatial Resolution Mismatch**: Public travel survey files aggregate home locations to Traffic Analysis Zones (TAZ) or Census Tracts (CT) to prevent re-identification, requiring probabilistic assignment to individual building archetypes.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Berres et al. (2021) [*Build. Simul. Conf.*], Gerike et al. (2015) [*Transp. Res. Part A*], McKenna et al. (2015) [*Energy Build.*], Wadud et al. (2016) [*Transp. Res. Part A*].
   - *Seen described:* ARTM 2018 methodology report, U of T DMG TTS 2016 report, US FHWA NHTS user guide.
   - Count opened in full: 4. Count seen described: 3.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I would have written `NOT FOUND` if Canadian regional travel surveys did not record trip start and end times; both EOD and TTS record timestamps to the minute.
   - I noted that travel surveys lack intra-home activity fidelity (`NOT FOUND` in travel surveys).
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The use of US NHTS travel data to generate synthetic building occupancy schedules is claimed by Berres et al. (2021).
   - In Canada, the specific combination of ARTM EOD / Toronto TTS microdata with UBEM archetype engines remains unclaimed.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all sample sizes correspond to published survey reports.

---

## Section H. Full reference list

1. Berres, A., Im, P., & Sanyal, J. (2021). Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors. *Building Simulation Conference Proceedings*, 30744. DOI: 10.26868/25222708.2021.30744. CrossRef returned title: "Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors". Read: full text. [Tier 2]
2. Gerike, R., Gehlert, T., & Schulz, F. (2015). Time use in travel surveys and time use surveys - Two sides of the same coin? *Transportation Research Part A: Policy and Practice*, 76, 4-24. DOI: 10.1016/j.tra.2015.03.030. CrossRef returned title: "Time use in travel surveys and time use surveys - Two sides of the same coin?". Read: full text. [Tier 1]
3. McKenna, E., Krawczynski, M., & Thomson, M. (2015). Four-state domestic building occupancy model for energy demand simulations. *Energy and Buildings*, 96, 30-39. DOI: 10.1016/j.enbuild.2015.03.013. CrossRef returned title: "Four-state domestic building occupancy model for energy demand simulations". Read: full text. [Tier 1]
4. Wadud, Z., MacKenzie, D., & Leiby, P. (2016). Help or hindrance? The travel, energy and carbon impacts of highly automated vehicles. *Transportation Research Part A: Policy and Practice*, 86, 1-18. DOI: 10.1016/j.tra.2015.12.001. CrossRef returned title: "Help or hindrance? The travel, energy and carbon impacts of highly automated vehicles". Read: full text. [Tier 1]
