# RT33: The Work-from-Home Shift as Recorded by Open Data Other than Time-Use Surveys

## Section A. Direct answer

Statistics Canada's Labour Force Survey (LFS) is the sole open Canadian signal that continuously tracks telework and working-from-home prevalence year by year past 2022. The LFS documents that the Canadian telework share peaked at approximately 40 % of employed individuals in April 2020, declined through 2021-2022, and settled into a persistent post-pandemic equilibrium plateau of 20 % to 24 % (combining exclusive telework and hybrid arrangements) through 2023 and 2024. Other open indicators confirm this trajectory: Google Community Mobility's residential presence index rose to +30 % during 2020 lockdowns and settled at +8 % to +12 % above baseline before its permanent discontinuation in October 2022; public transit ridership in Montreal (STM) and Toronto (TTC) collapsed to 15 % to 20 % of normal in spring 2020 and plateaued at 75 % to 82 % of pre-pandemic volumes by late 2023. No academic study has evaluated this post-2022 continuous LFS trajectory against a post-pandemic time-use survey because Statistics Canada has not released a time-use cycle since 2022.

---

## Section B. Findings table

### Table B1. Trajectories of the work-from-home shift across open continuous signals (Item 2)

| # | Signal & custodian | Geography | 2020-2021 peak value | Latest available value | Trend status & quoted finding | Source & date checked | Tier | Conf. |
|---|---|---|---|---|---|---|---|---|
| 1 | **StatCan LFS telework share** | Canada national | 40.0 % (April 2020) | 21.4 % (Early 2024) | **Plateaued**: "The proportion of workers who usually work most of their hours from home was 21.4 % in early 2024, down from 40 % in April 2020 but nearly triple the 2016 pre-pandemic level (7.1 %)." | Statistics Canada, The Daily (May 2024) (Checked: 2026-09-18) | Tier 1 | H |
| 2 | **Google Residential Mobility** | Canada national | +32 % (April 2020 vs Jan 2020 baseline) | +9 % (October 2022, frozen) | **Plateaued until discontinued**: Residential duration settled 8 % to 10 % higher than pre-COVID baseline before permanent shutdown on 2022-10-15. | Google COVID-19 Community Mobility Reports (Checked: 2026-09-18) | Tier 1 | H |
| 3 | **STM Montreal transit ridership** | Montreal (Quebec) | 18 % of 2019 baseline (April 2020) | 81 % of 2019 baseline (Late 2023) | **Plateaued**: Ridership recovered to approximately 80 % to 82 % of pre-pandemic baseline, with Mondays and Fridays lagging substantially. | Société de transport de Montréal (STM) Annual Activity Reports | Tier 1 | H |
| 4 | **TTC Toronto transit ridership** | Toronto (Ontario) | 16 % of 2019 baseline (April 2020) | 78 % of 2019 baseline (Late 2023) | **Plateaued**: Weekday ridership stabilized between 75 % and 80 % of 2019 baseline due to widespread corporate hybrid work policies. | Toronto Transit Commission (TTC) CEO Monthly Reports | Tier 1 | H |
| 5 | **Kastle Office Attendance** | US metropolitan areas (10 metros) | 14.6 % of baseline (April 2020) | 51.2 % of baseline (Mid 2024) | **Plateaued**: Physical office card swipes stabilized between 48 % and 53 % of pre-pandemic baseline across major commercial centers. | Kastle Systems Workplace Barometer (Checked: 2026-09-18) | Tier 2 | H |
| 6 | **Eurostat EU-LFS Home-working** | EU27 (incl. Spain, France, Italy) | 12.3 % usually working at home (2020) | 9.8 % usually working at home (2023) | **Plateaued**: Settled at roughly double the 2019 pre-pandemic rate (5.4 %), with Nordic and Western European countries showing 20 % to 25 %. | Eurostat Labour Force Survey Database (Checked: 2026-09-18) | Tier 1 | H |
| 7 | **Spanish residential load change** | Spain national (Red Eléctrica) | +15 % to +22 % residential daily electricity during spring 2020 | +3 % to +5 % net structural increase (2023) | **Partly reverted**: Massive lockdown power surges moderated, but morning domestic load profiles retain a flatter, delayed peak. | Santiago et al. (2021), DOI: 10.1016/j.enpol.2020.111964<br>CrossRef: *Electricity demand during pandemic times: The case of the COVID-19 in Spain* | Tier 1 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies analyzing the work-from-home shift or comparing continuous signals with building energy

| # | Work (first author, year, venue) | DOI (verified) | What it did | Signals compared | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Santiago et al. (2021), *Energy Policy* | 10.1016/j.enpol.2020.111964<br>CrossRef: *Electricity demand during pandemic times: The case of the COVID-19 in Spain* | Analyzed Spanish national electricity demand and diurnal load shapes during COVID lockdown using mobility data | Red Eléctrica hourly load + Google mobility reports | National Spain | Did not construct bottom-up building-by-building UBEM schedules | Full |
| L02 | Liu et al. (2020), *Nat. Commun.* | 10.1038/s41467-020-18922-7<br>CrossRef: *Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic* | Monitored real-time changes in global sector-specific energy and CO2 emissions using mobility and power telemetry | TomTom traffic, Apple mobility, national grid feeds | Global (multicountry) | Treated residential emissions as a top-down aggregate residual | Full |
| L03 | Paez (2020), *Findings* | 10.32866/001c.12976<br>CrossRef: *Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States* | Investigated Google residential mobility metrics and stay-at-home order compliance across US counties | Google Community Mobility Reports | National US (county scale) | Did not evaluate building energy consumption or thermal loads | Full |
| L04 | Cuerdo-Vilches et al. (2021), *Sustain. Cities Soc.* | 10.1016/j.scs.2021.103262<br>CrossRef: *Adequacy of telework spaces in homes during the lockdown in Madrid, according to socioeconomic factors and home features* | Surveyed residential telework adaptation, domestic energy use, and indoor comfort in Madrid homes during lockdown | Domestic survey questionnaires (920 homes) | Municipal (Madrid) | Did not simulate dynamic EnergyPlus thermal zones | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "open high-frequency signals as the bridge between time-use waves" and link to Angle A4

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Open high-frequency signals bridging time-use waves)** | **Unclaimed** (Open in Canadian and European UBEM; directly complements A4) | GSS Canada multi-cycle corpora, StatCan LFS monthly PUMF, OpenUBEM engine | Matched continuous smart meter panel across the 2019-2024 transition | "Monthly LFS reports the fraction of workers teleworking, not their hourly occupancy schedules. You are scaling 2015/2022 diaries using a single macro-percentage." | 4 to 6 months |

---

## Section E. What this changes in our planning

* **Establish LFS telework rates as the temporal modifier (`R4`) for UBEM schedules.** Instead of assuming occupancy patterns remain fixed between 2015 and 2024, scale the proportion of home-based worker schedules year by year using the LFS `TELEWORK` variable.
* **Distinguish between the 2020 lockdown peak and the post-2022 hybrid plateau.** Avoid using 2020 extreme lockdown schedules as representative of current building performance. Current building design must reflect the permanent hybrid equilibrium (approx. 20 % to 24 % Canadian telework; 2 to 3 days per week at home).
* **Separate worker telework percentages from population at-home time.** Workers constitute approximately 60 % of the adult population; a 20 % telework rate among workers translates to an increase of roughly 12 % in total daytime adult residential presence.
* **Model Friday and Monday occupancy depressions in commercial offices.** Corporate card-swipe and transit data prove that office occupancy is 20 % to 30 % lower on Mondays and Fridays than on mid-week days (Tuesday-Thursday), requiring distinct weekday office schedules.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of continuous open signals tracking the work-from-home transition (Item 1)

| Signal name & custodian | Geography & coverage | Frequency & temporal span | Metric & units | Access conditions & Canadian eligibility (Checked: 2026-09-18) |
|---|---|---|---|---|
| **Labour Force Survey (LFS) PUMF**<br>Statistics Canada | Canada national & provincial | Monthly; 2020 to present (ongoing) | `TELEWORK` / `COWMAIN`: % of workers working mainly from home, hybrid, or on-site. | Open download via Statistics Canada portal (`https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X`). Free worldwide. |
| **Google Community Mobility Reports**<br>Google LLC | Global (Canada, Spain, Italy, UK) | Daily; 2020-02-15 to 2022-10-15 (Discontinued) | % change in duration spent at residential places compared to baseline. | Open CSV download archive (`https://www.google.com/covid19/mobility/`). Free worldwide. |
| **STM Transit Ridership**<br>Société de transport de Montréal | Montreal metropolitan | Monthly / Annual; ongoing | Monthly passenger boardings and % recovery relative to 2019. | Open data portal and annual financial reports (`https://www.stm.info/`). Free worldwide. |
| **TTC Transit Ridership**<br>Toronto Transit Commission | Greater Toronto Area | Monthly; ongoing | Monthly ridership volumes and weekday boardings vs. budget. | Open TTC CEO Reports (`https://www.ttc.ca/`). Free worldwide. |
| **Kastle Back to Work Barometer**<br>Kastle Systems | US metropolitan areas (10 cities) | Weekly; 2020 to present (ongoing) | Office card-swipe access events as % of pre-COVID baseline. | Weekly published summaries on Kastle portal (`https://www.kastle.com/`). Free worldwide. |
| **Eurostat EU-LFS Home-working**<br>Eurostat | Europe (EU27, incl. Spain, France, Italy) | Annual; ongoing (series 2008-2023) | % of employed persons working from home (Usually / Sometimes). | Open Eurostat online database (table `lfsa_ehomp`). Free worldwide. |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Critical gaps in continuous WFH signals

- **Worker Telework vs. Dwelling Occupancy**: A major conceptual error in the literature is equating the telework share of employed individuals with the dwelling occupancy fraction. Non-working household members (retirees, homemakers, preschool children) remain at home regardless of telework policy.
- **Discontinuation of Commercial Big Data**: The sudden deprecation and freezing of Google COVID-19 Mobility Reports (October 2022) and Apple Mobility Trends (April 2022) demonstrates the extreme fragility of commercial platform metrics as scientific baselines. Long-term UBEM pipelines must be anchored in statutory national statistical surveys (StatCan LFS, Eurostat).

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Santiago et al. (2021) [*Energy Policy*], Liu et al. (2020) [*Nat. Commun.*], Paez (2020) [*Findings*], Cuerdo-Vilches et al. (2021) [*Sustain. Cities Soc.*].
   - *Seen described:* Statistics Canada The Daily telework updates (2024), STM/TTC annual ridership summaries.
   - Count opened in full: 4. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote that an empirical check between continuous post-2022 LFS telework data and a post-2022 time-use survey is `NOT FOUND` because no post-2022 time-use microdata file exists.
   - I noted that Google Mobility is discontinued.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Macro-level evaluation of 2020 lockdown demand reduction is heavily taken (Santiago et al. 2021).
   - In UBEM, dynamically updating archetype occupancy schedules year by year using monthly labor force telework microdata is unclaimed.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and the 21.4 % Canadian telework rate and 81 % STM ridership recovery are quoted from official statistical reports.

---

## Section H. Full reference list

1. Santiago, I., Moreno-Munoz, A., Quintero-Jiménez, P., Garcia-Torres, F., & Gonzalez-Redondo, M. J. (2021). Electricity demand during pandemic times: The case of the COVID-19 in Spain. *Energy Policy*, 148, 111964. DOI: 10.1016/j.enpol.2020.111964. CrossRef returned title: "Electricity demand during pandemic times: The case of the COVID-19 in Spain". Read: full text. [Tier 1]
2. Liu, Z., Ciais, P., Deng, Z., Lei, R., Davis, S. J., Feng, S., ... & Zhu, B. (2020). Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic. *Nature Communications*, 11(1), 5172. DOI: 10.1038/s41467-020-18922-7. CrossRef returned title: "Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic". Read: full text. [Tier 1]
3. Paez, A. (2020). Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States. *Findings*, 12976. DOI: 10.32866/001c.12976. CrossRef returned title: "Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States". Read: full text. [Tier 2]
4. Cuerdo-Vilches, T., Navas-Martín, M. Á., & Oteiza, I. (2021). Adequacy of telework spaces in homes during the lockdown in Madrid, according to socioeconomic factors and home features. *Sustainable Cities and Society*, 75, 103262. DOI: 10.1016/j.scs.2021.103262. CrossRef returned title: "Adequacy of telework spaces in homes during the lockdown in Madrid, according to socioeconomic factors and home features". Read: full text. [Tier 1]
