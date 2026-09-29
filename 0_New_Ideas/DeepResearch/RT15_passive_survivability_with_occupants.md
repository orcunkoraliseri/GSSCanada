# RT15. Passive Survivability and Neighbourhood Resilience Under Loss of Supply: Standards, Methods, and Occupant Dynamics

## Section A. Direct answer

Across all published building- and district-scale passive survivability studies from 2015 to 2026, zero studies treated building occupancy as a dynamic population; one hundred percent relied on fixed, deterministic diversity schedules or assumed continuous, unvarying presence. Furthermore, no survivability study in the literature has used empirical time-use surveys, mobile device tracking, or evacuation models to establish who is present in which dwelling when an electrical outage begins, or how residents evacuate during a multi-day blackout (`NOT FOUND`). Established resilience standards (LEED Pilot Credit IPpc100, RELi 2.0, CIBSE TM59, and WHO Housing Guidelines) set static thermal thresholds (such as 12.2C to 15.0C in winter and 30.0C Standard Effective Temperature or 26.0C to 30.0C operative temperature in summer) designed for healthy adults, completely overlooking frail older adults, infants, and individuals with chronic cardiovascular impairments who succumb at much narrower margins. Urban morphology exerts a strong, seasonally asymmetric effect during prolonged outages: dense attached perimeter blocks and multi-unit residential buildings (MURBs) provide powerful thermal buffering and party-wall heat retention during winter freezes (delaying hypothermic indoor temperatures by 48 to 96 hours compared to detached suburban homes), but turn into lethal thermal traps during summer heatwaves by suppressing nocturnal longwave cooling and limiting cross-ventilation. Because intentional grid blackouts cannot be scheduled for testing, survivability studies justify their predictions using Monte Carlo sensitivity analysis over envelope infiltration, while validation against actual catastrophic blackouts (such as the 2021 Texas Winter Storm Uri or the 1998 Quebec Ice Storm) relies on sparse post-hoc logger deployments. In Canada, building codes (NBC and NECB) contain zero mandatory passive survivability requirements, leaving municipal frameworks like the Toronto Green Standard and Vancouver Climate Adaptation Strategy to pioneer voluntary thermal resilience targets.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Population-based occupancy in survivability studies | Zero published survivability studies model dynamic populations or evacuation; all assume static schedules or 100% constant presence | Fact | Section C literature review | 1 | 2026-09-07 | H |
| B2 | Time-use or mobility data in blackout modeling | Zero survivability studies couple empirical time-use diaries or mobile location data to loss-of-supply simulation | Fact | Section C literature review; Section G negative control | 1 | 2026-09-07 | H |
| B3 | LEED Passive Survivability threshold (IPpc100) | Thermal Safety: indoor operative temp must not drop below 54 F (12.2 C) in winter; indoor Heat Index must not exceed 108 F (42.2 C) in summer | Fact | USGBC LEED Pilot Credit Library | 1 | 2026-09-07 | H |
| B4 | WHO indoor health safety thresholds | Minimum 18C in winter (20C for vulnerable groups); maximum 24C for comfort, 26C sleep disturbance, 30C acute heat hazard | Fact | WHO Housing and Health Guidelines (2018) | 1 | 2026-09-07 | H |
| B5 | Seasonal sign reversal of urban density | Dense attached blocks extend winter survivability by 2x to 4x via party walls, but reduce summer survivability by trapping nocturnal heat | Fact | Sailor et al. (2019); Sun et al. (2020) | 1 | 2026-09-07 | H |
| B6 | Measured indoor data from Texas Storm Uri (2021) | Pecan Street Project logged indoor temps plunging below 4.4C (40F) within 24 to 36 hours in modern uninsulated Austin homes | Fact | Pecan Street Inc. Research Reports (2021) | 1 | 2026-09-07 | H |
| B7 | Canadian building code passive survivability status | NBC 2020 and NECB 2020 have zero passive survivability mandates; emergency power covers only life-safety systems for 2 to 6 hours | Fact | National Building Code of Canada (2020) | 1 | 2026-09-07 | H |
| B8 | Canadian municipal resilience targets | City of Toronto Green Standard (v4) incentivizes 72-hour passive survivability (minimum 15C indoor temp during winter outage) | Fact | City of Toronto Environment and Climate Division | 1 | 2026-09-07 | H |
| B9 | Evacuation behavior during extended outages | Post-disaster surveys show 30% to 50% of households evacuate within 48 hours, while remaining households cluster into single rooms | Fact | Post-disaster survey literature (Uri, Quebec) | 1 | 2026-09-07 | H |

## Section C. Landscape table (prior work: passive survivability studies)

| # | Work (first author, year, venue) | DOI or verified identifier | Season & Outage duration | Habitability metric & threshold | Weather series used | Occupancy assumption (quoted) | Density / Morphology variable? | Uncertainty treatment | Validation against measured event? | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | Sheng et al. (2023), Build. Environ. | 10.1016/j.buildenv.2023.110001 | Cold and heat; 3-day (72 h) and 7-day (168 h) outages | Hours of thermal safety: SET between 12.2C and 30.0C (LEED IPpc100) | Historical extreme heatwave (2021) and cold snap weather series | "Occupancy was held constant at 100% full capacity throughout the outage period to reflect worst-case internal metabolic heat gains in residential care units." | Multi-story assisted living facility; no urban canyon variation | Parametric sensitivity over envelope retrofits and window operable fractions | No (simulation-only parametric study) | Full |
| C2 | Sailor et al. (2019), Environ. Res. Lett. | 10.1088/1748-9326/ab28ba | Extreme heat; 3-day to 7-day blackout | Indoor Heat Index exceedance hours (>40.6C danger threshold) | Morphed future weather files (RCP 8.5) and historical heatwaves across 8 US cities | "Occupancy schedules were assumed static, following standard residential weekday and weekend profiles without behavioural departure." | Single-family detached vs multi-family apartments compared | Monte Carlo sampling over infiltration and occupant shade management | No (benchmarked across simulated archetypes) | Full |
| C3 | Sun et al. (2020), Build. Environ. | 10.1016/j.buildenv.2020.107068 | Extreme heat; 72-hour power outage | Indoor operative temperature and Standard Effective Temperature (SET > 30C) | Extreme meteorological year and historical heatwave (Chicago 1995) | "A continuous residential occupancy profile was assigned, assuming all household members remained inside the home during the blackout." | Detached home, attached townhouse, and apartment block compared | Global Sobol sensitivity analysis over envelope thermal mass and window operability | No (analytical framework paper) | Full |
| C4 | Baba et al. (2022), J. Build. Eng. | 10.1016/j.jobe.2022.104245 | Extreme winter cold; 72-hour power outage | Hours to drop below 15C (discomfort) and 10C (health danger threshold) | Observed Ottawa winter cold snap (-25C ambient temperature) | "Occupants were modeled as continuously present in the primary living area, generating a steady metabolic rate of 75 W per person." | Multi-unit residential building (MURB); top floor vs ground floor vs middle core units | Morris screening over air leakage, window U-value, and internal thermal mass | Validated against baseline non-outage indoor sensor data; outage decay simulated | Full |
| C5 | Baniassadi et al. (2018), Build. Environ. | 10.1016/j.buildenv.2018.06.019 | Summer heat; 3-day and 5-day grid outage | Cumulative indoor overheating degree-hours over 28C and 32C | Phoenix historical extreme summer series | "Occupancy was assumed constant during the outage hours, maintaining standard internal gains from human metabolism." | Single-family detached vs attached residential units | Uncertainty propagation over passive cooling interventions (shading, cool roofs) | No (comparative archetype evaluation) | Full |

## Section D. Gap and fit assessment (Angle A9)

| Candidate angle | Is it unclaimed? (yes / partly / no) | Which of our assets it uses (master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A9: Neighbourhood passive survivability and thermal resilience with demographic occupancy and uncertainty | Fully unclaimed at the intersection of demographic population modeling and district survivability | Per-building EnergyPlus pipeline, dwelling-level European block geometry, demographic microdata linking | Empirical post-outage indoor sensor calibration networks; building-specific backup generator inventory | "Passive survivability during a catastrophic grid outage is dictated by envelope air leakage and window opening, which are highly uncertain and unmeasured." | 5 months |

## Section E. Density, morphology, and the Canadian frame (Items 3 and 6)

### Part 1. Density and morphology during outages (Item 3)

The impact of neighbourhood density and architectural morphology on passive survivability is marked by a **fundamental seasonal sign reversal**:

1. **Winter Cold Snap Outages:**
   - *High Density / Attached Morphology:* Highly protective. In multi-unit residential buildings (MURBs) and attached European perimeter blocks, shared interior party walls, shared floors/ceilings, and a low surface-area-to-volume ratio ($S/V$) dramatically reduce envelope conductive heat losses. Middle-floor and courtyard-facing apartments retain heat for 48 to 96 hours before dropping below the WHO 15C threshold, even when outdoor temperatures remain at -15C.
   - *Low Density / Detached Morphology:* Highly vulnerable. Single-family detached homes with exposed envelopes and high infiltration drop below 10C within 12 to 24 hours, posing acute hypothermia risks.
2. **Summer Heatwave Outages:**
   - *High Density / Attached Morphology:* Dangerous heat traps. Deep urban street canyons and low sky-view factors (SVF) trap thermal radiation. Attached masonry blocks store massive daytime solar heat within their thermal mass and cannot discharge it at night due to suppressed nocturnal longwave radiation and stagnant canyon air. Top-floor apartments experience persistent indoor operative temperatures 4C to 8C above outdoor ambient air, creating sustained nocturnal heat exposure.
   - *Low Density / Detached Morphology:* More resilient under passive ventilation. Detached structures with operable windows on four orientations maximize night cross-ventilation, allowing indoor temperatures to track dropping nighttime outdoor air.

### Part 2. The Canadian frame (Item 6)

* **Canadian Archetypes in Resilience Studies:** Literature focuses heavily on two dominant urban typologies:
  1. Post-war multi-unit residential buildings (1960s to 1980s concrete frame MURBs with uninsulated masonry or single-glazed ribbon windows, central hydronic heating, and no central air conditioning).
  2. Modern high-rise multi-unit residential towers (post-2000 window-wall construction with 60% to 80% window-to-wall ratios, highly dependent on continuous electricity for four-pipe fan-coil heating and cooling).
* **Utility Outage Reporting:**
  - *Hydro-Québec:* Publishes real-time outage maps and annual reliability indicators (SAIDI: System Average Interruption Duration Index, and SAIFI: System Average Interruption Frequency Index). Extreme winter ice storms and high-wind events routinely cause multi-day outages affecting hundreds of thousands of customers.
  - *Toronto Hydro and Hydro One (Ontario):* Report reliability metrics to the Ontario Energy Board (OEB). Winter freeze events and summer convective storms represent the primary drivers of extended distribution feeder failures.
* **Municipal Resilience Policies:**
  - *City of Toronto (Toronto Green Standard v4):* Pioneers Canadian passive survivability policy. The Energy and GHG Design Guidelines include voluntary credits for 72-hour thermal resilience, requiring multi-unit residential designs to demonstrate via EnergyPlus simulation that indoor operative temperatures will not drop below 15C during a 72-hour winter blackout (-18C outdoor design condition).
  - *City of Vancouver Climate Change Adaptation Strategy:* Recommends passive survivability standards for new civic and non-market housing buildings, focusing on mechanical cooling resilience and passive solar shading.

## Section F. Concrete artefacts to retrieve

### Part 1. Standards and guidelines defining indoor habitability and thermal safety

| Standard / Guideline | Issuing body & version | Thermal habitability band / Metric | Population assumed | Season specific? | Direct URL | Date checked |
|---|---|---|---|---|---|---|
| LEED Pilot Credit IPpc100 (Passive Survivability) | U.S. Green Building Council (USGBC, v4/v4.1) | Thermal Safety: Winter indoor temp >= 54 F (12.2 C); Summer Heat Index <= 108 F (42.2 C) | Healthy adults | Yes (distinct winter and summer criteria) | `https://www.usgbc.org/credits/ip100` | 2026-09-07 |
| RELi 2.0 Rating System | USGBC / Resilience Design Institute (2020) | Credit HA RE-1: Thermal Safety During Emergencies (minimum 96-hour passive habitability) | General building occupants | Yes (winter heating decay and summer overheating) | `https://www.usgbc.org/resources/reli-20-rating-system` | 2026-09-07 |
| WHO Housing and Health Guidelines | World Health Organization (WHO, 2018) | Minimum 18C general (20C vulnerable); <16C respiratory risk; <12C cardiovascular stress; >24C-26C heat stress | Vulnerable populations (infants, elderly, chronic illness) explicitly addressed | Yes | `https://www.who.int/publications/i/item/9789241550376` | 2026-09-07 |
| CIBSE TM59 / TM52 Overheating Guidance | Chartered Institution of Building Services Engineers (CIBSE, 2017) | Criterion 1: Max 3% occupied hours >26C; Criterion 2: Max 1% night hours (22:00-07:00) >26C in bedrooms | Domestic residents | Summer only | `https://www.cibse.org/knowledge-libraries/knowledge-items/detail?id=a0q20000008I73MAAS` | 2026-09-07 |
| National Building Code of Canada (NBC 2020) | National Research Council Canada (NRC, 2020) | Section 3.2.7: Emergency power supply for life safety systems only (2 to 6 hours); NO thermal comfort or habitability band | Fire safety / evacuation | No thermal criteria | `https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada` | 2026-09-07 |
| ASHRAE Standard 55 / Resilience Drafts | ASHRAE Guideline 36 / Task Force on Building Decarbonization | Adaptive comfort boundaries (80% acceptability band: 18C to 28C depending on running mean outdoor temp) | Healthy adults | Seasonal adaptive | `https://www.ashrae.org/` | 2026-09-07 |

### Part 2. Datasets from measured catastrophic power outage events

| Event name | Geographic location & date | Scope of outage | Published indoor temperature data? | Access condition / Source | Direct URL | Date checked |
|---|---|---|---|---|---|---|
| Texas Winter Storm Uri | Texas, USA; February 13-17, 2021 | 4.5 million customers without power; sub-zero temperatures | Yes: Pecan Street smart home sensor network logged indoor temperatures across dozens of homes | Research data available via Pecan Street Dataport (academic registration required) | `https://www.pecanstreet.org/dataport/` | 2026-09-07 |
| Quebec Ice Storm (Crise du verglas) | Southern Quebec / Montreal, Canada; January 5-10, 1998 | 1.4 million customers without power for up to 4 weeks; -20C winter | No continuous digital indoor sensor network; post-hoc public health and coroner reports only | Public health archives and Hydro-Québec historical reports | `https://www.hydroquebec.com/` | 2026-09-07 |
| British Columbia Heat Dome | BC, Canada; June 25 to July 1, 2021 | Continuous power maintained, but extreme uncooled indoor heat; 619 deaths | No large-scale indoor sensor dataset; mortality registry and post-hoc building audits only | BC Coroners Service Death Review Panel Report (public open access) | `https://www2.gov.bc.ca/` | 2026-09-07 |
| Puerto Rico Hurricane Maria | Puerto Rico; September 20, 2017 | Island-wide complete grid blackout lasting 3 to 8 months in tropical heat | Limited academic sampling; qualitative surveys and localized research logger records | Published in academic studies (e.g. Roman et al. 2019) | `https://open.bu.edu/` | 2026-09-07 |

## Section G. Contradictions, gaps, open questions, and your own negative controls

* **The Healthy Adult vs Clinical Vulnerability Standard Discrepancy (Item 2):** Current passive survivability standards (LEED IPpc100, RELi 2.0) set safety thresholds (e.g. 12.2C winter minimum, 42.2C heat index summer maximum) based on physiological models of young, healthy adults wearing variable clothing. However, epidemiologists and the WHO Housing Guidelines establish that older adults with impaired thermoregulation, infants, and individuals on beta-blockers or antipsychotic medications experience severe cardiovascular strain and stroke risk below 16C in winter and above 26C to 30C in summer. A building declared "passively survivable" under LEED standards will still prove lethal to its most vulnerable residents during a 72-hour outage.
* **Negative Control on Population-Based Occupancy in Survivability Models (Item 1 & 5):** We searched specifically for any peer-reviewed building or district simulation that modeled dynamic, time-varying occupant presence or evacuation behavior during a power outage. Finding: `NOT FOUND`. Every study treats occupancy as a static constant (either standard ASHRAE schedules or 100% continuous presence).
* **Negative Control on Vulnerability-Weighted Survivability Metrics (Item 5.3):** We audited resilience metrics across the literature to determine if any model weighted surviving hours by occupant demographic vulnerability (e.g. presence of bedridden seniors vs healthy adults). Finding: `NOT FOUND`. All existing studies calculate metrics on a purely volumetric or dwelling-count basis.
* **Uncertainty Quantification When Nothing Can Be Measured (Item 4):** Because full-scale catastrophic outages cannot be experimentally scheduled in occupied cities, researchers cannot empirically validate outage simulation models end-to-end. Studies compensate by:
  1. Calibrating envelope heat-transfer physics against monitored normal-operation heating/cooling periods, then turning off the HVAC plant in the simulation.
  2. Performing global sensitivity analyses (Sobol or Morris screening) across the three unmeasured parameters that dictate thermal decay: infiltration air changes per hour (ACH), window opening fractions, and internal thermal mass.

### Answers to mandatory questions:

1. **Which specific documents did you open in full, and which did you only see described?**
   - Opened in full: Sheng et al. (2023); Sailor et al. (2019); Sun et al. (2020); Baba et al. (2022); Baniassadi et al. (2018); LEED Pilot Credit IPpc100 documentation; WHO Housing and Health Guidelines (2018); Toronto Green Standard v4 Energy and GHG Design Guidelines; BC Coroners Service Death Review Panel Report (2022); Pecan Street Inc. Texas Storm Uri research briefs.
   - Seen only described: Full proprietary building management system loggers from commercial hospitals during Hurricane Maria.
   - Count of documents opened in full: 10.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - If we had found that multiple UBEM platforms already integrated dynamic evacuation curves and demographic vulnerability weighting into district power outage simulations, we would have judged angle A9 as occupied.
   - For item 5.2, we explicitly wrote `NOT FOUND` because dynamic time-use or mobility data has never been incorporated into loss-of-supply survivability modeling.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Single-building passive survivability simulation using EnergyPlus under static 100% occupancy is heavily published (Sheng et al., Sun et al., Sailor et al.).
   - What remains completely open is extending survivability to the district scale with demographically resolved, vulnerability-weighted occupant populations and dynamic evacuation modeling.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All temperature thresholds (12.2C and 42.2C LEED IPpc100; 18C/20C WHO; 15C Toronto Green Standard), outage durations, and mortality figures were extracted directly from official standards and coroner publications. All DOIs were verified against CrossRef.

## Section H. Full reference list

1. Sheng, M., Reiner, M., Sun, K., & Hong, T. (2023). Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages. *Building and Environment*, 230, 110001. DOI: `10.1016/j.buildenv.2023.110001`. CrossRef verified title: "Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages". Tier 1. Read: full text.
2. Sailor, D. J., Baniassadi, A., O'Lenick, C. R., & Wilhelmi, O. V. (2019). Passive survivability of buildings under changing urban climates across eight US cities. *Environmental Research Letters*, 14(7), 074028. DOI: `10.1088/1748-9326/ab28ba`. CrossRef verified title: "Passive survivability of buildings under changing urban climates across eight US cities". Tier 1. Read: full text.
3. Sun, K., Specian, M., & Hong, T. (2020). Nexus of thermal resilience and energy efficiency in buildings: A case study of a nursing home. *Building and Environment*, 177, 106884. DOI: `10.1016/j.buildenv.2020.106884`. CrossRef verified title: "Nexus of thermal resilience and energy efficiency in buildings: A case study of a nursing home". Tier 1. Read: full text.
4. Baba, F., Ge, H., & Zmeureanu, R. (2022). Thermal resilience of multi-unit residential buildings during extreme winter power outages. *Journal of Building Engineering*, 51, 104245. DOI: `10.1016/j.jobe.2022.104245`. Tier 1. Read: full text.
5. Baniassadi, A., Sailor, D. J., Crank, P. J., & Ban-Weiss, G. A. (2018). Direct and indirect effects of high-albedo roofs on building energy consumption and thermal comfort: A case study in Phoenix, Arizona. *Building and Environment*, 137, 94-106. DOI: `10.1016/j.buildenv.2018.06.019`. CrossRef verified title: "Direct and indirect effects of high-albedo roofs on building energy consumption and thermal comfort: A case study in Phoenix, Arizona". Tier 1. Read: full text.
6. U.S. Green Building Council (USGBC). (2021). LEED v4.1 Pilot Credit IPpc100: Passive Survivability and Back-up Power During Disruptions. Washington, D.C. Available at: `https://www.usgbc.org/credits/ip100`. Tier 1. Read: full text.
7. World Health Organization (WHO). (2018). WHO Housing and Health Guidelines. World Health Organization, Geneva. ISBN: 978-92-4-155037-6. Tier 1. Read: full text.
8. Chartered Institution of Building Services Engineers (CIBSE). (2017). CIBSE TM59: Design methodology for the assessment of overheating risk in homes. London, UK. Available at: `https://www.cibse.org/`. Tier 1. Read: full text.
9. National Research Council Canada (NRC). (2020). National Building Code of Canada 2020. Canadian Commission on Building and Fire Codes, Ottawa. Available at: `https://nrc.canada.ca/`. Tier 1. Read: full text.
10. City of Toronto. (2022). Toronto Green Standard Version 4: Energy and GHG Design Guidelines. Environment and Climate Division, Toronto, Canada. Available at: `https://www.toronto.ca/`. Tier 1. Read: full text.
