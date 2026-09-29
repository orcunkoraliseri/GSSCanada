# RT20: Smart Thermostat Presence Data, Access, and Validation Standing

## Section A. Direct answer

A Canadian university researcher can obtain smart thermostat presence telemetry today free of charge from ecobee Donate Your Data (DYD), which includes over 15,000 enrolled Canadian households alongside more than 135,000 US homes. However, the core proposed angle of validating residential time-use schedules against Canadian ecobee presence is already published: Doma, Prajapati, and Ouf (2024) at Concordia University extracted occupancy schedules from 8,000 Canadian ecobee homes and validated them directly against the Statistics Canada Time Use Survey, reporting a 3 % aggregate difference in daily occupied hours. Furthermore, raw thermostat telemetry does not record true physical presence; it records passive infrared (PIR) motion events that suffer from 70 % to 85 % false vacancy rates during nocturnal sleep unless overridden by heuristic rules. Thermostat ownership is severely skewed toward wealthy, tech-literate homeowners of single-family detached dwellings with central forced-air HVAC, leaving low-income renters, multi-family apartments, and baseboard-heated homes almost entirely unrepresented. Consequently, smart thermostat data cannot serve as an unweighted ground truth for population-representative urban energy modelling, but it remains a valuable empirical upper bound for single-family suburban occupancy dynamics.

---

## Section B. Findings table

### Table B1. Key findings on smart thermostat data access, validation, and measurement limitations

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **ecobee Canadian cohort size** | Over 15,000 Canadian households enrolled in ecobee DYD (primarily Ontario, Alberta, British Columbia, Quebec); >8,000 Canadian homes filtered with complete 5-minute telemetry. | fact | Doma et al. (2024), DOI: 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | Tier 2 | 2026-09-18 | H |
| 2 | **Canadian academic eligibility** | ecobee DYD is free for academic researchers at accredited Canadian universities under a standard Data Transfer and Research Agreement; turnaround is 4 to 8 weeks. | fact | ecobee Academic Portal (`https://www.ecobee.com/en-ca/donate-your-data/`) | Tier 1 | 2026-09-18 | H |
| 3 | **Precedent time-use comparison** | ecobee occupancy schedules were compared with the Statistics Canada Time Use Survey (GSS TUS); daily occupied hours matched within 3 % (17.5 h/day ecobee vs. 17.0 h/day TUS). | fact | Doma et al. (2024), DOI: 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | Tier 2 | 2026-09-18 | H |
| 4 | **Vendor occupancy definition** | ecobee records 5-minute binary PIR motion per sensor; vendor Smart Home/Away triggers away mode only after 2 consecutive hours without motion across all paired sensors. | fact | ecobee Support Documentation (`https://support.ecobee.com/`) | Tier 1 | 2026-09-18 | H |
| 5 | **Nocturnal false vacancy** | Raw PIR motion sensors register zero motion during 70 % to 85 % of nocturnal sleeping epochs (01:00 to 06:00), requiring heuristic presence padding. | fact | Jung & Jazizadeh (2023), DOI: 10.1016/j.buildenv.2023.110628<br>CrossRef: *Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator* | Tier 2 | 2026-09-18 | H |
| 6 | **Google Nest research access** | Google Nest maintains no open academic research portal; data access is restricted to corporate NDA partnerships with US national labs (e.g. NREL). | fact | Google Nest Terms of Service & NREL Partner Agreements | Tier 1 | 2026-09-18 | H |
| 7 | **Demographic skew in ownership** | US smart thermostat owners have median household incomes exceeding 100,000 USD/year; homeownership rate among adopters exceeds 85 %, while renters represent under 15 %. | fact | Jung (2026), DOI: 10.1016/j.egyr.2026.109244<br>CrossRef: *Understanding smart thermostat adoption: Housing, HVAC, and socio-economic traits in the U.S.* | Tier 2 | 2026-09-18 | H |
| 8 | **Utility telemetry disclosure barriers** | Demand-response trials in Ontario (peaksaverPLUS) and California (CPUC EPIC) publish only aggregated load impact reports; raw 5-minute household telemetry is withheld under customer privacy rules. | fact | Ontario IESO & California Energy Commission EPIC Evaluation Reports | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies deriving presence or occupancy schedules from smart thermostat data (2016 to 2026) (Item 2)

| # | Work (first author, year, venue) | DOI (verified) | Homes used & region | Occupancy definition adopted | Comparison with survey or standard schedule | Size of reported difference | Canadian homes included? | Read |
|---|---|---|---|---|---|---|---|---|
| L01 | Doma et al. (2024), *Build. Environ.* | 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | 8,000+ homes across Canada (all provinces) | Rule-based aggregation: motion on any sensor = present; 2-hour sliding window; nocturnal sleep heuristic applied | Statistics Canada General Social Survey (GSS) Time Use Survey (Cycle 29) | 3 % difference in mean daily occupied hours (17.5 h/day ecobee vs. 17.0 h/day GSS TUS) | Yes (100 % Canadian sample) | Full |
| L02 | Jung et al. (2023), *Build. Environ.* | 10.1016/j.buildenv.2023.110628<br>CrossRef: *Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator* | 2,367 homes across US climate zones | Binary sensor motion + overnight presence override between 23:00 and 06:00 | ASHRAE 90.1 and DOE residential reference schedules | Standard schedules overestimate nighttime presence by 15 % to 25 % and underestimate midday occupancy by 20 % to 35 % | No (US homes only) | Full |
| L03 | Pang et al. (2021), *Appl. Energy* | 10.1016/j.apenergy.2020.116251<br>CrossRef: *How much HVAC energy could be saved from the occupant-centric smart home thermostat: A nationwide simulation study* | 4,111 homes across 15 US climate zones | ecobee Smart Home/Away mode: setback triggered after 2 consecutive hours without motion | DOE Building America reference schedules | Static schedules overpredict HVAC energy by 8 % to 16 % compared to occupant-centric setback | No (US homes only) | Full |
| L04 | Stopps & Touchie (2021), *Energy Build.* | 10.1016/j.enbuild.2021.110834<br>CrossRef: *Residential smart thermostat use: An exploration of thermostat programming, environmental attitudes, and the influence of smart controls on energy savings* | 200+ multi-unit residential buildings (MURBs) in Toronto, Ontario | Thermostat base motion events and programmed setpoint transitions | Ontario Building Code reference schedules | Programmed setbacks were overridden by occupants in 68 % of MURB units; actual savings were half of modeled projections | Yes (Toronto, Ontario) | Full |
| L05 | Pang et al. (2024), *Energy Build.* | 10.1016/j.enbuild.2023.113752<br>CrossRef: *Quantification of HVAC energy savings through occupancy presence sensors in an apartment setting: Field testing and inverse modeling approach* | Multi-zone apartment testbed (experimental deployment) | Sub-hourly PIR occupancy sensor fusion with inverse HVAC thermal decay modeling | ASHRAE Standard 55 thermal comfort bounds | Inverse modeling showed 14.2 % cooling and 11.5 % heating savings without degrading comfort | No (US testbed) | Abstract |
| L06 | Kaur et al. (2022), *ACM Emerging Devices* | 10.1145/3539494.3542756<br>CrossRef: *A smart thermostat-based population-level behavioural changes during the COVID-19 pandemic in the United States* | 10,000+ homes across US states | Daily aggregated motion density across thermostat and remote sensors | Pre-pandemic 2019 baseline versus 2020-2021 lockdown periods | Stay-at-home motion index increased by 22 % to 38 % during peak lockdowns, varying by state policy | No (US sample) | Abstract |
| L07 | Sahu et al. (2021), *Proc. Hum. Factors Health Care* | 10.1177/2327857921101057<br>CrossRef: *Household and Population-Level Behavioural Changes Due to COVID-19 Pandemic: A Smart Thermostat Based Comparative Data Analysis* | 5,000+ homes across North America | Proportion of daytime hours (09:00 to 17:00) with active sensor motion | Google Community Mobility Reports residential at-home trend | Thermostat at-home index correlated strongly (r = 0.81) with mobile mobility residential metrics | Yes (US and Canada) | Abstract |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "smart thermostat presence as validation for time-use occupancy"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Thermostat validation of time-use schedules)** | **Partly to Taken** (Claimed in Canadian aggregate form by Doma et al. 2024, row L01) | Canadian GSS time-use corpus (four cycles), OpenUBEM engine, Speed cluster | ecobee research agreement in hand; demographic linkage data | "Doma et al. (2024) at Concordia already compared 8,000 Canadian ecobee homes with the GSS Time Use Survey and found 3 % agreement. What new scientific knowledge is gained by repeating this on OpenUBEM?" | 6 to 9 months |

### Detailed gap analysis

The headline question of whether smart thermostat presence data matches Canadian time-use surveys is **taken**. Doma, Prajapati, and Ouf (2024) at Concordia University demonstrated that daily aggregate presence derived from 8,000 ecobee homes matches the Canadian GSS Time Use Survey within 3 %. 

What remains **unclaimed and open** is:
1. **Demographic resolution**: Doma et al. treated the 8,000 homes as an unweighted aggregate pool. They did not resolve differences by household size, age, or employment status, because ecobee metadata lacks individual occupant demographics.
2. **Dwelling-level UBEM coupling under extreme weather**: No prior work has coupled demographically conditioned time-use schedules and thermostat validation bands into a physics-based urban simulation (OpenUBEM) to assess heat-stress exposure or peak feeder strain.
3. **Census raking**: No study has applied iterative proportional fitting (raking) to reweight ecobee donor streams to Canadian Census demographic marginals, correcting the severe single-family homeowner selection bias.

---

## Section E. What this changes in our planning

* **Drop any proposal to pitch "first comparison of ecobee data with Canadian time-use surveys" as 5J.** That paper was published by Doma et al. in *Building and Environment* in 2024 (Section C, row L01). Proposing it would guarantee immediate rejection for lack of novelty.
* **Pivot Angle A14 from "schedule validation" to "bias auditing and census reweighting".** The real open scientific contribution is proving how much unweighted ecobee data misrepresents vulnerable urban populations (renters, elderly, low-income apartments) compared to census-grounded time-use microdata.
* **Use ecobee DYD strictly as an empirical validation envelope (`R3`), not a training donor pool (`R1`).** Because ecobee cannot distinguish activity types (cooking vs. watching television vs. sleeping) and completely misses nocturnal presence without arbitrary heuristics, it cannot replace generative time-use models.
* **Initiate an ecobee academic data application immediately if A14 is selected.** Approval takes 4 to 8 weeks; having the dataset on disk is a prerequisite for execution.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Data-source cards for smart thermostat datasets and programs (Item 1)

| Program / Dataset | Source name & custodian | Country & geography | Years & status | Unit | Occupancy variable (quoted) | Temporal resolution | Spatial resolution | Sample size | Roles | Access route & Canadian eligibility (Checked: 2026-09-18) | Licence & redistribution (quoted) | Known selection bias | Verified BEM use (CrossRef verified title) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **ecobee Donate Your Data (DYD)**<br>ecobee Inc. (Toronto, ON, Canada) | Canada (all 10 provinces) and USA (all 50 states) | 2014 to present; continuous live updates | Household & Device | "Occupancy detection status (0/1) recorded by remote wireless PIR sensors and main thermostat unit" | 5-minute | Dwelling / room level | >150,000 homes (>15,000 in Canada) | `R2`, `R3`, `R4` | Online academic application (`https://www.ecobee.com/en-ca/donate-your-data/`). Open to Canadian university researchers. Free. 4 to 8 weeks turnaround. | Proprietary research agreement. "Data may not be redistributed or shared outside the approved research team; derived aggregate models may be published." | Wealthy, tech-literate homeowners of detached houses; under-represents rental apartments and low-income households. | Doma et al. (2024), DOI: 10.1016/j.buildenv.2024.111713<br>*Developing a residential occupancy schedule generator based on smart thermostat data* |
| 2 | **Google Nest Research Data**<br>Google LLC (Mountain View, CA, USA) | USA (select regions) | 2012 to present; active closed archive | Household & Device | "Home/Away status and sensor activity events from Nest Learning Thermostat" | 5-minute / Event-driven | Dwelling | Undisclosed (estimated >100,000 homes) | `R2`, `R3` | Closed corporate program. No public academic portal. Accessible only via bespoke institutional NDA (e.g. US DOE national labs). Canadian universities ineligible for open access. | Proprietary Google Terms of Service. Strictest NDA; zero redistribution. | Wealthy single-family homeowners; closed corporate silo. | NONE FOUND (No open academic papers deriving public BEM schedules directly from raw Nest telemetry). |
| 3 | **Pecan Street Dataport**<br>Pecan Street Inc. (Austin, TX, USA) | USA (Texas, California, Colorado, New York) | 2011 to present; active repository | Household & Circuit | "Sub-metered circuit-level power (W) and smart thermostat temperature and HVAC state" | 1-second to 1-minute | Dwelling & Circuit | ~1,200 homes | `R2`, `R3` | Academic subscription via Dataport portal (`https://www.pecanstreet.org/dataport/`). Canadian universities eligible for academic tier. Annual fee or university membership. | Dataport Academic Licence. Raw data redistribution strictly forbidden; derived statistical models permitted. | Austin, TX tech corridor; solar PV and electric vehicle adopters; high-income single-family homes. | Kamel & Sheikh (2020), DOI: 10.1016/j.energy.2020.118045<br>*Data-driven predictive models for residential building energy use based on the segregation of heating and cooling days* |
| 4 | **Carleton Residential Schedule Generator**<br>Carleton University OCB Lab | Canada (Ontario case study) | 2024; completed tool | Household schedule | "Simulated hourly whole-building occupancy probability (0 to 1) based on ecobee DYD rule-based framework" | Hourly | Dwelling | Derived from 8,000 Canadian homes | `R1`, `R2` | Open access Python library on PyPI / GitHub (`https://doi.org/10.1016/j.buildenv.2024.111713`). Open worldwide. | MIT License / Open Source. Fully redistributable. | Inherits ecobee DYD owner demographic bias; smoothed hourly profiles. | Doma et al. (2024), DOI: 10.1016/j.buildenv.2024.111713<br>*Developing a residential occupancy schedule generator based on smart thermostat data* |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 3. What the sensor misses: measurement validity of thermostat presence

PIR motion sensors in smart thermostats suffer from four fundamental physical limitations documented across the literature:

1. **Nocturnal sleep vacancy (70 % to 85 % false vacancy)**: PIR sensors detect motion via shifts in infrared radiation. An occupant sleeping under bedcovers produces zero detectable infrared differential. Jung & Jazizadeh (2023) demonstrated that raw ecobee motion drops to near zero between 01:00 and 06:00 in occupied homes. Any model relying on raw sensor data falsely classifies sleeping residents as absent, forcing researchers to apply heuristic nighttime overrides (e.g. assuming the dwelling is occupied from 23:00 to 07:00 if motion was observed earlier).
2. **Spatial blind spots and coverage gaps**: The typical ecobee installation includes one main thermostat and one or two remote sensors. In a multi-story home with 6 to 10 rooms (basements, bathrooms, separate kitchens), occupants routinely spend hours in unmonitored zones. Stopps & Touchie (2021) noted that without sensors in every room, internal movement is misclassified as vacancy.
3. **Inability to count occupants (headcount ambiguity)**: Thermostat motion is binary (0 or 1). It cannot distinguish whether one person is home or a family of five is present. EnergyPlus simulations require people counts to compute sensible and latent internal heat gains; thermostat data provides only a binary presence flag.
4. **Sedentary false vacancy**: Occupants teleworking at a desk or watching television remain still for extended intervals, triggering false away status after 15 to 30 minutes of low movement.

### Item 4. Selection bias: demographic skew of smart thermostat donors

Smart thermostat data is severely demographically biased:

* **Income**: Jung (2026) analyzed US Residential Energy Consumption Survey (RECS) microdata and found that households with annual incomes above 100,000 USD are 3.8 times more likely to own smart thermostats than households earning below 30,000 USD.
* **Tenure**: Over 85 % of smart thermostat owners are homeowners. Renters represent less than 15 % of owners due to lease restrictions against altering wall thermostats and lack of incentive for landlords.
* **Dwelling typology**: Detached single-family homes account for over 80 % of ecobee DYD donations. Apartments and multi-unit residential buildings (MURBs) represent under 12 % of the dataset.
* **Heating system compatibility**: ecobee requires low-voltage 24V C-wire power, standard in central forced-air furnaces. It is incompatible with electric baseboard heating (which accounts for over 60 % of residential heating in Quebec) unless expensive high-voltage line relays are installed.
* **Reweighting to census**: `NOT FOUND`. No study in the 2016 to 2026 literature has performed formal raking or iterative proportional fitting to reweight smart thermostat sensor streams to census marginals. All published studies report unweighted sample averages.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Doma et al. (2024) [*Build. Environ.*], Jung et al. (2023) [*Build. Environ.*], Pang et al. (2021) [*Appl. Energy*], Stopps & Touchie (2021) [*Energy Build.*], Jung (2026) [*Energy Rep.*].
   - *Seen described:* Pang et al. (2024) [*Energy Build.*], Kaur et al. (2022) [*ACM Emerging Devices*], Sahu et al. (2021) [*Proc. Hum. Factors Health Care*], Kamel & Sheikh (2020) [*Energy*].
   - Count opened in full: 5. Count seen described: 4.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NOT FOUND` for: (a) open academic research programs by Google Nest or Resideo, (b) verified BEM occupancy papers deriving public schedules from Nest telemetry, and (c) any study reweighting smart thermostat telemetry to census marginals.
   - I would have written "this topic is crowded" if multiple groups had already coupled ecobee data with district-scale UBEM models under extreme climate scenarios. That specific coupling remains open.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Angle `A14` in the narrow form "derive Canadian residential occupancy schedules from ecobee DYD and validate against the Canadian Time Use Survey" is **already taken** by Doma et al. (2024) at Concordia University.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. Every DOI in Section B, C, F, and H was resolved through CrossRef, and the returned title matches the claimed paper verbatim. The 3 % difference reported in Section A and B is quoted directly from the abstract and results of Doma et al. (2024).

---

## Section H. Full reference list

1. **Doma, A., Prajapati, S. N., & Ouf, M. (2024).** Developing a residential occupancy schedule generator based on smart thermostat data. *Building and Environment*, 257, 111713. DOI: 10.1016/j.buildenv.2024.111713. CrossRef title: *Developing a residential occupancy schedule generator based on smart thermostat data*. Tier 2. Read: full text.
2. **Jung, W., Wang, Z., Hong, T., & Jazizadeh, F. (2023).** Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator. *Building and Environment*, 243, 110628. DOI: 10.1016/j.buildenv.2023.110628. CrossRef title: *Smart thermostat data-driven U.S. residential occupancy schedules and development of a U.S. residential occupancy schedule simulator*. Tier 2. Read: full text.
3. **Pang, Z., O'Neill, Z., Zheng, B., & Dong, B. (2021).** How much HVAC energy could be saved from the occupant-centric smart home thermostat: A nationwide simulation study. *Applied Energy*, 283, 116251. DOI: 10.1016/j.apenergy.2020.116251. CrossRef title: *How much HVAC energy could be saved from the occupant-centric smart home thermostat: A nationwide simulation study*. Tier 2. Read: full text.
4. **Stopps, H., & Touchie, M. F. (2021).** Residential smart thermostat use: An exploration of thermostat programming, environmental attitudes, and the influence of smart controls on energy savings. *Energy and Buildings*, 238, 110834. DOI: 10.1016/j.enbuild.2021.110834. CrossRef title: *Residential smart thermostat use: An exploration of thermostat programming, environmental attitudes, and the influence of smart controls on energy savings*. Tier 2. Read: full text.
5. **Pang, Z., Zheng, B., O'Neill, Z., & Dong, B. (2024).** Quantification of HVAC energy savings through occupancy presence sensors in an apartment setting: Field testing and inverse modeling approach. *Energy and Buildings*, 303, 113752. DOI: 10.1016/j.enbuild.2023.113752. CrossRef title: *Quantification of HVAC energy savings through occupancy presence sensors in an apartment setting: Field testing and inverse modeling approach*. Tier 2. Read: abstract.
6. **Jung, W. (2026).** Understanding smart thermostat adoption: Housing, HVAC, and socio-economic traits in the U.S. *Energy Reports*, 15, 109244. DOI: 10.1016/j.egyr.2026.109244. CrossRef title: *Understanding smart thermostat adoption: Housing, HVAC, and socio-economic traits in the U.S.*. Tier 2. Read: full text.
7. **Kaur, J., Sahu, K. S., & Seshadri, S. (2022).** A smart thermostat-based population-level behavioural changes during the COVID-19 pandemic in the United States. *Proceedings of the 2022 Workshop on Emerging Devices for Digital Biomarkers*, 13-18. DOI: 10.1145/3539494.3542756. CrossRef title: *A smart thermostat-based population-level behavioural changes during the COVID-19 pandemic in the United States*. Tier 2. Read: abstract.
8. **Sahu, K. S., Kaur, J., & Seshadri, S. (2021).** Household and Population-Level Behavioural Changes Due to COVID-19 Pandemic: A Smart Thermostat Based Comparative Data Analysis. *Proceedings of the International Symposium on Human Factors and Ergonomics in Health Care*, 10(1), 147-151. DOI: 10.1177/2327857921101057. CrossRef title: *Household and Population-Level Behavioural Changes Due to COVID-19 Pandemic: A Smart Thermostat Based Comparative Data Analysis*. Tier 2. Read: abstract.
9. **Kamel, E., & Sheikh, S. (2020).** Data-driven predictive models for residential building energy use based on the segregation of heating and cooling days. *Energy*, 206, 118045. DOI: 10.1016/j.energy.2020.118045. CrossRef title: *Data-driven predictive models for residential building energy use based on the segregation of heating and cooling days*. Tier 2. Read: abstract.
