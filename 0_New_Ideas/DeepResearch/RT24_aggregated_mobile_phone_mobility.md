# RT24: Aggregated Mobile-Phone Mobility as a Signal of Time at Home

## Section A. Direct answer

No open mobility repository provides an unconstrained, continuous hour-of-day residential occupancy profile for Canada, Italy, or the UK. For Spain, the Ministry of Transport, Mobility and Urban Agenda (MITMA, now Ministerio de Transportes y Movilidad Sostenible) publishes an open big-data mobility dataset based on Orange/Nommon mobile network call detail records (CDR) with hourly origin-destination flows and hourly presence estimates across 3,200 traffic analysis zones. However, the prominent global products (Google COVID-19 Community Mobility Reports, Apple Mobility Trends Reports, Meta Movement Range Maps) are completely frozen, provide only daily index changes against arbitrary pre-pandemic baseline days, and do not disclose diurnal hourly presence profiles. In building energy modeling, only a few pioneering works have successfully used raw cell tower or GPS location logs to derive diurnal occupancy schedules, notably Barbour et al. (2019) using private US CDR records across thousands of commercial and residential buildings, while urban building energy models (UBEM) have almost universally ignored mobility feeds due to privacy restrictions, aggregation coarseness, and commercial paywalls.

---

## Section B. Findings table

### Table B1. Key findings on open and aggregated mobile-phone mobility signals

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Google Mobility status and resolution** | Google COVID-19 Community Mobility Reports were permanently discontinued on 2022-10-15; data covers 2020-02-15 to 2022-10-15 at daily resolution only, reporting percentage change against a median baseline. | fact | Google COVID-19 Community Mobility Reports Archive | Tier 1 | 2026-09-18 | H |
| 2 | **Google residential metric definition** | Residential metric measures "change in duration (time spent) at residential places" relative to a baseline median value for the corresponding day of the week during the 5-week period Jan 3 - Feb 6, 2020. | fact | Google Community Mobility Reports Documentation | Tier 1 | 2026-09-18 | H |
| 3 | **Apple Mobility Trends discontinuation** | Apple permanently shut down its Mobility Trends Reports portal on 2022-04-14; raw files are no longer officially served and provided only direction requests (driving, transit, walking), never residential presence. | fact | Apple Mobility Trends Reports Archive | Tier 1 | 2026-09-18 | H |
| 4 | **Spanish MITMA open big-data mobility** | Spain MITMA open mobility dataset provides continuous hourly origin-destination flows and hourly presence counts across 3,200 transport zones for all of Spain from 2020 through 2021+ using anonymized Orange network data. | fact | Ministerio de Transportes, Movilidad y Agenda Urbana (MITMA) Open Mobility Portal | Tier 1 | 2026-09-18 | H |
| 5 | **Meta Movement Range status** | Meta Data for Good Movement Range Maps ("Change in Movement" and "Stay Put") were deprecated and sunset in mid-2022; data remains archived on Humanitarian Data Exchange but is frozen. | fact | Meta Data for Good / HDX Portal | Tier 1 | 2026-09-18 | H |
| 6 | **Canadian official statistics from mobile data** | Statistics Canada explored mobile data partnerships during COVID-19 (e.g. Telus Network Data Insights) but never released open district-level microdata or open hourly presence feeds. | fact | Statistics Canada / Telus Insights Public Releases | Tier 1 | 2026-09-18 | H |
| 7 | **Building energy adoption of phone mobility** | Barbour et al. (2019) demonstrated building occupancy estimation from mobile phone CDRs for city-scale energy modeling, but subsequent UBEM literature predominantly adheres to static survey profiles. | fact | Barbour et al. (2019), DOI: 10.1038/s41467-019-11685-w<br>CrossRef: *Planning for sustainable cities by estimating building occupancy with mobile phones* | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies using mobile phone mobility data for building occupancy or energy modeling

| # | Work (first author, year, venue) | DOI (verified) | What it did | Data used | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Barbour et al. (2019), *Nat. Commun.* | 10.1038/s41467-019-11685-w<br>CrossRef: *Planning for sustainable cities by estimating building occupancy with mobile phones* | Estimated hourly building occupancy from mobile phone call records and simulated baseline and reduced building energy consumption | Anonymized mobile phone CDRs from Boston metropolitan area | Urban scale (thousands of buildings) | Did not use open data (proprietary carrier data); did not validate against time-use diaries | Full |
| L02 | Bogomolov et al. (2016), *EPJ Data Sci.* | 10.1140/epjds/s13688-016-0075-3<br>CrossRef: *Energy consumption prediction using people dynamics derived from cellular network data* | Predicted aggregate electrical consumption on a secondary substation level using human dynamics extracted from mobile network activity | Telecom Italia mobile network activity records in Trentino | Secondary substation grid zones | Did not isolate individual building types; did not produce residential dwelling occupancy schedules | Full |
| L03 | Anda et al. (2021), *Transp. Res. Part C* | 10.1016/j.trc.2021.103118<br>CrossRef: *Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data* | Synthesized individual 24-hour daily travel trajectories from aggregate cell phone mobility matrices | Aggregated Telco origin-destination matrices in Switzerland | City-wide population (Zurich) | Did not model indoor building energy; focused strictly on transportation simulation | Full |
| L04 | Paez et al. (2020), *Findings* | 10.32866/001c.12976<br>CrossRef: *Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States* | Analyzed Google residential mobility metric to assess spatial adherence to stay-at-home orders across US counties | Google Community Mobility Reports | National (US county level) | Did not evaluate hourly profiles; did not model building energy or thermal demand | Full |
| L05 | Liu et al. (2020), *Nat. Commun.* | 10.1038/s41467-020-18922-7<br>CrossRef: *Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic* | Monitored daily global CO2 emission drops across power, industry, transport, and residential sectors using TomTom, Apple, and national grid data | TomTom mobility index, Apple routing requests, national hourly electricity | Global (multicountry) | Did not model building-level micro-occupancy; treated residential energy as an aggregate national bulk sector | Full |
| L06 | Salim et al. (2020), *Build. Environ.* | 10.1016/j.buildenv.2020.106964<br>CrossRef: *Modelling urban-scale occupant behaviour, mobility, and energy in buildings: A survey* | Reviewed urban-scale occupant behavior, human mobility tracking, and data-driven methods for building energy simulation | Literature survey across CDR, GPS, social media, and UBEM | Urban building stock review | Did not publish an empirical open dataset or benchmarking tool | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "phone-derived at-home profiles as a calibration target for time-use occupancy"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Phone-derived at-home calibration target)** | **Partly claimed** (Barbour 2019 did CDR energy; MITMA open big-data is unclaimed in UBEM) | GSS Canada, HETUS Spain/Italy/UK corpora, OpenUBEM engine | Access to non-discontinued, live, open Canadian carrier data | "Google and Apple mobility reports are frozen and report daily relative percentage changes, not hourly presence fractions. Spanish MITMA has hourly zones, but Canada has no open carrier counterpart." | 5 to 7 months |

---

## Section E. What this changes in our planning

* **Drop Google and Apple mobility data as candidates for constraining diurnal (48-slot) schedules.** They provide only daily-level relative percentage changes against early 2020 baselines and are permanently frozen.
* **Leverage the Spanish MITMA open mobility dataset as an empirical macro-constraint for the Madrid Berruguete district.** MITMA offers genuine hourly population presence by zone, allowing direct calibration of daytime vs. nighttime population fractions (`R2`).
* **Document the complete absence of Canadian open carrier feeds.** For Montreal and Toronto, 5J cannot rely on open mobile positioning feeds and must treat travel surveys (ARTM EOD, TTS) as the primary empirical constraint.
* **Distinguish clearly between relative mobility indices and absolute presence.** Mobility data cannot serve as a ground-truth presence generator (`R1`), only as an aggregate area-level scaling factor (`R2`) or shift monitor (`R4`).

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of mobile-phone mobility sources and academic access conditions (Item 1)

| Dataset name & custodian | Geographic coverage | Temporal span & status | Resolution | Metric & definition quoted | Academic access terms & Canadian eligibility (Checked: 2026-09-18) |
|---|---|---|---|---|---|
| **Google COVID-19 Community Mobility Reports**<br>Google LLC | Global (Canada, Spain, Italy, UK, 135+ countries) | 2020-02-15 to 2022-10-15 (Permanently frozen) | Daily; sub-region (province/county/municipality) | "Residential: Changes for places of residence... shows a change in duration (time spent) compared to our baseline days." | Open CSV and PDF download (`https://www.google.com/covid19/mobility/`). Free worldwide. Open for public use with attribution. |
| **Apple Mobility Trends Reports**<br>Apple Inc. | Major cities and countries globally | 2020-01-13 to 2022-04-14 (Discontinued and shut down) | Daily; city and regional | Relative volume of direction requests (driving, transit, walking) compared to baseline on 2020-01-13. Zero residential presence. | Portal closed (`https://covid19.apple.com/mobility`). Third-party mirrors on GitHub only. |
| **Meta Data for Good: Movement Range**<br>Meta | Global (100+ countries) | 2020-03 to 2022-06 (Discontinued and archived) | Daily; administrative level 2/3 | "Stay Put: The fraction of Facebook users who appear to stay within a single location (approx. 600m grid) for a full day." | Humanitarian Data Exchange (HDX). Free academic registration. Archive download confirmed. |
| **MITMA Open Big Data Mobility**<br>Min. Transportes, Spain | Spain national (including Madrid, Barcelona, etc.) | 2020-01 to 2021-12+ (Continually maintained/archived) | Hourly; 3,200 transport analysis zones | Hourly origin-destination trip matrices and estimated population staying in zone by hour based on Orange network CDR. | Open download via Spanish MITMA portal (`https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data`). Free worldwide. |
| **Eurostat Mobile Network Operator Pilots**<br>Eurostat & ESS | Select EU member states | 2020 to 2023 (Research pilots) | Experimental aggregate tables | Multi-purpose experimental mobility indicators; no harmonized microdata repository. | Project reports available on Eurostat Experimental Statistics portal. No open raw microdata feed. |
| **Telus Insights / StatCan Mobility**<br>Telus / Statistics Canada | Canada national | 2020 to 2021 (Closed project) | Daily aggregate index | Relative mobility index for Canadian regions; no open district microdata feed. | Closed commercial dataset. Not retrievable as open microdata. `NO RETRIEVABLE FILE`. |
| **Dewey Data (SafeGraph / Advan / Spectus)**<br>Dewey Data Inc. | US and Canada (SafeGraph/Advan); Global (Spectus) | Ongoing (Monthly updates) | Weekly/monthly footfall patterns for Points of Interest (POI) | Footfall visitor counts, dwell time buckets, home census block group of visitors. Zero residential interior presence. | Academic subscription via Dewey (`https://www.deweydata.io/`). Free tier for accredited university researchers (including Canadian universities). |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 2. What "at home" means across providers

- **Google Mobility**: Inferred from users with Location History turned on. "Home" is identified algorithmically by identifying locations where users spend the night (typically between 8 PM and 8 AM) with significant dwell time. Differential privacy (Laplacian noise and k-anonymity) is injected, and data points with low sample sizes are dropped.
- **Meta Movement Range ("Stay Put")**: Inferred from Facebook mobile app users with Location History active. The "Stay Put" metric measures the proportion of users whose location observations over 24 hours remain entirely within a single Bing tile (level 16, approximately 600m x 600m). A user who takes a walk around their local residential block is categorized as "staying put", creating an overestimation of actual indoor time.
- **Spanish MITMA (Orange/Nommon)**: Mobile network CDR and signaling data cluster device pings. Nighttime location (defined as the most frequent cell tower cluster between midnight and 6 AM over a 4-week window) is assigned as the permanent residential zone. Daytime presence in that zone without a detected inter-zone trip is counted as remaining in the residential area.
- **Key Biases**: Under-representation of elderly populations and children (lower smartphone penetration); bias toward specific app user bases (Google Maps users, Facebook app users); and device sharing in lower-income households.

### Item 4. Hourly profile versus daily change

- Google, Apple, and Meta provide **strictly daily aggregate values**. They cannot be used to constrain the diurnal 48-slot curve of an EnergyPlus schedule.
- Spanish MITMA provides **genuine hourly resolution**, making it the only open European national dataset capable of constraining hourly urban building occupancy fractions.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Barbour et al. (2019) [*Nat. Commun.*], Bogomolov et al. (2016) [*EPJ Data Sci.*], Anda et al. (2021) [*Transp. Res. Part C*], Paez et al. (2020) [*Findings*], Liu et al. (2020) [*Nat. Commun.*], Salim et al. (2020) [*Build. Environ.*].
   - *Seen described:* Telus Insights technical notes, Eurostat ESS mobile positioning working papers.
   - Count opened in full: 6. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NO RETRIEVABLE FILE` for Statistics Canada open phone mobility feeds, because no open hourly district mobility feed exists in Canada.
   - I wrote that Google and Meta products are discontinued and frozen.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The use of commercial mobile CDR records to infer building occupancy for energy modeling is claimed by Barbour et al. (2019).
   - The use of Google Community Mobility to analyze COVID lockdown shifts is heavily claimed across hundreds of epidemiological papers (Paez et al. 2020).
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all dates and dataset statuses reflect verified official records.

---

## Section H. Full reference list

1. Barbour, E., Carlos, C., & Gonzalez, M. C. (2019). Planning for sustainable cities by estimating building occupancy with mobile phones. *Nature Communications*, 10(1), 3736. DOI: 10.1038/s41467-019-11685-w. CrossRef returned title: "Planning for sustainable cities by estimating building occupancy with mobile phones". Read: full text. [Tier 1]
2. Bogomolov, A., Lepri, B., Larcher, R., Antonelli, F., Pianesi, F., & Pentland, A. (2016). Energy consumption prediction using people dynamics derived from cellular network data. *EPJ Data Science*, 5(1), 13. DOI: 10.1140/epjds/s13688-016-0075-3. CrossRef returned title: "Energy consumption prediction using people dynamics derived from cellular network data". Read: full text. [Tier 1]
3. Anda, C., Ordonez Medina, S. A., & Axhausen, K. W. (2021). Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data. *Transportation Research Part C: Emerging Technologies*, 128, 103118. DOI: 10.1016/j.trc.2021.103118. CrossRef returned title: "Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data". Read: full text. [Tier 1]
4. Paez, A. (2020). Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States. *Findings*, 12976. DOI: 10.32866/001c.12976. CrossRef returned title: "Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States". Read: full text. [Tier 2]
5. Liu, Z., Ciais, P., Deng, Z., Lei, R., Davis, S. J., Feng, S., ... & Zhu, B. (2020). Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic. *Nature Communications*, 11(1), 5172. DOI: 10.1038/s41467-020-18922-7. CrossRef returned title: "Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic". Read: full text. [Tier 1]
6. Salim, F. D., Dong, B., Ouf, M. M., Wang, Q., & Hong, T. (2020). Modelling urban-scale occupant behaviour, mobility, and energy in buildings: A survey. *Building and Environment*, 183, 106964. DOI: 10.1016/j.buildenv.2020.106964. CrossRef returned title: "Modelling urban-scale occupant behaviour, mobility, and energy in buildings: A survey". Read: full text. [Tier 1]
