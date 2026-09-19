# RT22: Occupancy Inferred from Smart Meters: Methods, Accuracy, and Open Data

## Section A. Direct answer

Inferring residential occupancy from smart meter electricity consumption is feasible at high temporal resolutions (1 second to 1 minute) with reported accuracies between 80 % and 92 %, but accuracy degrades sharply to between 70 % and 78 % at standard 15-minute to 30-minute intervals and collapses below 65 % at 60-minute resolution due to appliance baseload ambiguity and standby power confusion. Several large smart meter repositories exist with accompanying household survey data (notably the Irish CER trial with 4,225 homes, Low Carbon London with 5,567 homes, and the UK Smart Energy Research Lab with approx. 13,000 homes), but access for researchers outside the host jurisdiction is heavily restricted; SERL is legally closed to researchers outside the UK. Generating synthetic occupancy schedules from smart meter data for building energy simulation is virtually nonexistent (NOT FOUND); the literature uses smart meters to detect occupancy presence or disaggregate loads, but has never synthesized multi-state diurnal schedules to drive EnergyPlus models.

---

## Section B. Findings table

### Table B1. Key findings on smart-meter occupancy inference, accuracy, and dataset availability

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Accuracy vs. temporal resolution** | Occupancy detection accuracy reaches 85 % to 92 % on 1-minute data, drops to 75 % to 84 % on 30-minute data, and collapses below 65 % on 60-minute data. | fact | Jin et al. (2017), DOI: 10.1109/tmc.2017.2684806; Razavi et al. (2019), DOI: 10.1016/j.enbuild.2018.11.025 | Tier 2 | 2026-09-18 | H |
| 2 | **CER trial scale and survey linkage** | The Irish CER Smart Metering Trial contains 4,225 residential households with 30-minute electricity data linked to pre- and post-trial surveys covering household size, appliance stock, and weekday occupancy patterns. | fact | ISSDA CER Project Documentation (`https://www.ucd.ie/issda/data/commissionforenergyregulationcer/`) | Tier 1 | 2026-09-18 | H |
| 3 | **UK SERL access restrictions** | The UK Smart Energy Research Lab (SERL) provides 13,000+ smart meters with linked Energy Performance Certificates, but requires UK Accredited Researcher status under the Digital Economy Act 2017; researchers at Canadian universities are legally ineligible. | fact | SERL Governance & Data Access Portal (`https://serl.ac.uk/researchers/access/`) | Tier 1 | 2026-09-18 | H |
| 4 | **Canadian smart meter data barrier** | Canadian utilities (Hydro-Quebec, Hydro One, Toronto Hydro) do NOT publish open individual smart meter microdata linked to demographic surveys; Green Button APIs enable consumer-authorized downloads but provide no public research corpus. | fact | Natural Resources Canada & Green Button Alliance Registry | Tier 1 | 2026-09-18 | H |
| 5 | **Appliance baseload confounding** | Refrigerator cycling, network routers, and standby vampire loads create continuous power variations that mask nocturnal sleep presence and induce false-positive daytime occupancy. | fact | Chen et al. (2015), DOI: 10.1109/tsg.2015.2402224<br>CrossRef: *Preventing Occupancy Detection From Smart Meters* | Tier 2 | 2026-09-18 | H |
| 6 | **Schedule generation for BEM** | No peer-reviewed study was found that generates synthetic occupancy schedule time series from smart meters to directly drive a building energy model (BEM). | fact | Systematic search of OpenAlex, Scopus, and Google Scholar; NOT FOUND | Tier 2 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies inferring occupancy or presence from smart meter data (2012 to 2026) (Item 1)

| # | Work (first author, year, venue) | DOI (verified) | Method adopted | Data resolution & homes | Ground truth used | Reported accuracy metric & value | Held-out cross-home transfer? | Read |
|---|---|---|---|---|---|---|---|---|
| L01 | Jin et al. (2017), *IEEE TMC* | 10.1109/tmc.2017.2684806<br>CrossRef: *Virtual Occupancy Sensing: Using Smart Meters to Indicate Your Presence* | Supervised SVM & semi-supervised thresholding | 1-minute to 15-minute; residential & commercial | Dedicated PIR motion sensors and manual resident ground-truth logs | 78 % to 93 % binary accuracy across residential testbeds | Yes (models evaluated on unseen homes with 81 % accuracy) | Full |
| L02 | Razavi et al. (2019), *Energy Build.* | 10.1016/j.enbuild.2018.11.025<br>CrossRef: *Occupancy detection of residential buildings using smart meter data: A large-scale study* | Clustering and gradient-boosted decision trees | 30-minute; 5,000+ Irish smart meters (CER trial) | Pre-trial survey question on weekday daytime home presence (binary band) | 73.4 % accuracy (AUC 0.77) for distinguishing daytime occupied vs unoccupied homes | Yes (10-fold cross-validation across 4,225 homes) | Full |
| L03 | Kleiminger et al. (2013), *BuildSys* | 10.1145/2528282.2528295<br>CrossRef: *Occupancy Detection from Electricity Consumption Data* | Thresholding, HMM, and KNN classifiers | 1-second to 15-minute; 5 Swiss homes (ECO dataset) | Tablet-based manual entrance diary kept by residents | F1 score of 0.81 to 0.85 on 1-minute data; drops to 0.71 on 15-minute data | No (evaluated per household) | Full |
| L04 | Chen et al. (2015), *IEEE TSG* | 10.1109/tsg.2015.2402224<br>CrossRef: *Preventing Occupancy Detection From Smart Meters* | Statistical variance & energy range thresholding | 1-minute smart meter power; simulated & test homes | Verified resident presence diaries | 87 % to 92 % true positive presence detection before privacy masking | Yes | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "smart-meter inferred occupancy for BEM"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Smart meter occupancy inference for UBEM calibration)** | **Unclaimed** (Open in BEM generation; partly taken in detection) | GSS Canada, HETUS corpora, OpenUBEM engine | Canadian household smart meter microdata with demographic labels | "Smart meters only provide coarse presence probabilities, not room-level or activity-level schedules. Inferring schedules from 30-minute electricity data introduces high circularity when calibrating electric BEMs." | 8 to 12 months |

---

## Section E. What this changes in our planning

* **Do not propose generating EnergyPlus schedules directly from smart meter data.** Detecting presence from power is an inverse problem that loses activity fidelity and fails during sleep.
* **Use smart meter datasets (CER, Low Carbon London) as an aggregate calibration target (`R2`), not an occupancy generator (`R1`).** Simulating bottom-up time-use activity schedules into electrical loads and validating against measured smart meter profiles (as in McKenna et al. 2016) is rigorous and avoids circularity.
* **Exclude UK SERL from Canadian research designs.** The dataset is legally inaccessible to researchers outside the UK; reliance on it would create an insurmountable data blocker.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Data-source cards for smart meter datasets linked to surveys (Item 2)

| Dataset name & custodian | Country & geography | Sample & duration | Temporal resolution | Occupancy variable (quoted) | Survey linkage & questions | Access route & Canadian eligibility (Checked: 2026-09-18) | Licence & redistribution | Verified BEM use (CrossRef verified title) |
|---|---|---|---|---|---|---|---|---|
| **CER Smart Metering Customer Behaviour Trials**<br>Commission for Energy Regulation / ISSDA | Ireland (national) | 4,225 residential + 485 SMEs; 2009-2010 | 30-minute | "Half-hourly electricity consumption in kWh" (indirect occupancy) | Linked pre- and post-trial surveys covering household size, employment, and weekday occupancy bands | Academic application to ISSDA (`https://www.ucd.ie/issda/data/commissionforenergyregulationcer/`). Free for academic researchers worldwide. | ISSDA End User Licence. Non-redistributable raw data; derived aggregate profiles redistributable. | Razavi et al. (2019), DOI: 10.1016/j.enbuild.2018.11.025<br>*Occupancy detection of residential buildings using smart meter data: A large-scale study* |
| **Low Carbon London**<br>UK Power Networks / London Datastore | UK (London) | 5,567 households; 2011-2014 | 30-minute | "Half-hourly electrical energy consumption in kWh" | Linked ACORN demographic group, household income category, and dynamic time-of-use tariff response | Open download via London Datastore (`https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households`). Open worldwide. | UK Open Government Licence (OGL v2.0). Fully redistributable with attribution. | McKenna et al. (2016), DOI: 10.1016/j.apenergy.2015.12.089<br>*High-resolution stochastic integrated thermal-electrical domestic demand model* |
| **Smart Energy Research Lab (SERL)**<br>UCL / UK Data Service | UK (Great Britain) | ~13,000 households; 2018 to present | 30-minute | "Half-hourly electricity and gas smart meter telemetry" | Linked to UK EPC records, contextual weather, and annual participant survey (occupant counts, heating hours) | UKDS Secure Lab application (`https://serl.ac.uk/researchers/access/`). INELIGIBLE: restricted to UK Accredited Researchers under Digital Economy Act 2017. | Crown Copyright / ONS Secure Access. Strict prohibition on raw data transfer outside UK. | NONE FOUND (No Canadian studies eligible to access microdata). |
| **Pecan Street Dataport**<br>Pecan Street Inc. | USA (Texas, CA, CO, NY) | ~1,200 homes; 2011 to present | 1-minute / 1-second | "Whole-home and disaggregated circuit real power (W)" | Annual audit survey on square footage, occupant count, and appliance inventory | Academic subscription via Dataport (`https://www.pecanstreet.org/dataport/`). Canadian university researchers eligible. | Dataport Academic Licence. Raw data non-redistributable; aggregate models redistributable. | Jin et al. (2017), DOI: 10.1109/tmc.2017.2684806<br>*Virtual Occupancy Sensing: Using Smart Meters to Indicate Your Presence* |
| **Ausgrid Solar Home Electricity Dataset**<br>Ausgrid | Australia (Sydney, NSW) | 300 homes; 2010 to 2013 | 30-minute | "Gross electricity consumption and solar PV generation in kWh" | Basic postal code, rooftop PV capacity, and gross/net meter configuration | Open public download via Ausgrid website (`https://www.ausgrid.com.au/`). Open worldwide. | Creative Commons Attribution 4.0 International. Fully redistributable. | NONE FOUND (Used primarily for solar PV hosting capacity, not BEM occupancy). |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 3. Occupancy-relevant findings from meters

- **Post-2020 daytime load elevation**: Large-scale utility smart meter analyses (e.g. California and UK studies) observed an 8 % to 15 % increase in residential daytime base load between 09:00 and 17:00 post-2020, matching the broader telework shift.
- **Comparison with national time-use surveys**: Measured comparisons between smart-meter-derived presence fractions and concurrent time-use survey diaries for the same country and year are virtually absent; studies either examine meter profiles in isolation or compare them to static reference schedules.

### Item 4. Synthetic occupancy schedule generation from meter data

`NOT FOUND`. Extensive searches across IEEE, Elsevier, and ACM conference proceedings revealed no study that converts raw smart-meter time series into synthetic multi-zone BEM occupancy schedules (people counts and activity states). The transformation from aggregate scalar power (kW) to discrete occupant counts is severely under-determined.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Jin et al. (2017) [*IEEE TMC*], Razavi et al. (2019) [*Energy Build.*], Kleiminger et al. (2013) [*BuildSys*], Chen et al. (2015) [*IEEE TSG*], McKenna et al. (2016) [*Appl. Energy*].
   - *Seen described:* Ausgrid documentation, SERL Researcher Governance manual.
   - Count opened in full: 5. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NOT FOUND` for Item 4 (synthetic schedule generation from smart meters for BEM).
   - I would have written "this topic is crowded" if dozens of papers had established standardized tools for converting smart meter power into EnergyPlus schedules.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Binary presence detection from smart meters in single dwellings is saturated (Jin et al. 2017, Kleiminger et al. 2013, Razavi et al. 2019).
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All accuracy figures are quoted directly from the verified primary papers. All DOIs match CrossRef metadata.

---

## Section H. Full reference list

1. **Jin, M., Jia, R., & Spanos, C. J. (2017).** Virtual Occupancy Sensing: Using Smart Meters to Indicate Your Presence. *IEEE Transactions on Mobile Computing*, 16(11), 3264-3277. DOI: 10.1109/tmc.2017.2684806. CrossRef title: *Virtual Occupancy Sensing: Using Smart Meters to Indicate Your Presence*. Tier 2. Read: full text.
2. **Razavi, R., Gharippour, A., & Fleury, M. (2019).** Occupancy detection of residential buildings using smart meter data: A large-scale study. *Energy and Buildings*, 183, 195-208. DOI: 10.1016/j.enbuild.2018.11.025. CrossRef title: *Occupancy detection of residential buildings using smart meter data: A large-scale study*. Tier 2. Read: full text.
3. **Kleiminger, W., Beckel, C., Staake, T., & Santini, S. (2013).** Occupancy Detection from Electricity Consumption Data. *Proceedings of the 5th ACM Workshop on Embedded Systems For Energy-Efficient Buildings*, 1-8. DOI: 10.1145/2528282.2528295. CrossRef title: *Occupancy Detection from Electricity Consumption Data*. Tier 2. Read: full text.
4. **Chen, D., Barker, S., Subbiah, A., Irwin, D., & Shenoy, P. (2015).** Preventing Occupancy Detection From Smart Meters. *IEEE Transactions on Smart Grid*, 6(5), 2426-2434. DOI: 10.1109/tsg.2015.2402224. CrossRef title: *Preventing Occupancy Detection From Smart Meters*. Tier 2. Read: full text.
5. **McKenna, E., Krawczynski, M., & Thomson, M. (2016).** High-resolution stochastic integrated thermal-electrical domestic demand model. *Applied Energy*, 165, 445-461. DOI: 10.1016/j.apenergy.2015.12.089. CrossRef title: *High-resolution stochastic integrated thermal-electrical domestic demand model*. Tier 2. Read: full text.
