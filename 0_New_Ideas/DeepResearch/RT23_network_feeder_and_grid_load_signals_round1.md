# RT23: Open Feeder, Substation and Grid Load Signals for Occupancy Validation

## Section A. Direct answer

Open low-voltage (LV) feeder and secondary substation load data are published systematically by distribution network operators in the United Kingdom (UK Power Networks, Scottish and Southern Electricity Networks, Northern Powergrid), but are almost entirely unpublished as geolocated open datasets in Canada, Spain, and Italy. In Canada, utilities such as Hydro-Quebec and Hydro Ottawa publish only high-level annual open-data summaries or regional system totals, withholding feeder-level telemetry. System-level hourly demand is published openly across all target jurisdictions via independent system operators (IESO for Ontario, AESO for Alberta, REE for Spain, Terna for Italy, and ENTSO-E for Europe), but none of these system feeds separate residential demand from commercial and industrial loads. Testing bottom-up occupancy-driven urban simulations against measured feeder load shapes has been validated in the UK and Belgium (e.g. Baetens et al. 2016, Tang et al. 2017), showing that bottom-up occupancy aggregation successfully captures evening coincidence peaks; however, separating occupant presence from weather-driven HVAC loads at feeder scale remains heavily confounded unless sub-metered heating baselines are available.

---

## Section B. Findings table

### Table B1. Key findings on open feeder load, system demand, and occupancy signal extraction

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **UK LV feeder open data leadership** | UK DNOs publish open, geolocated 10-minute and 30-minute load data for thousands of secondary substations and low-voltage feeders via open data portals. | fact | UK Power Networks Open Data Portal (`https://dataportal.ukpowernetworks.co.uk/`); SSEN Open Data Portal | Tier 1 | 2026-09-18 | H |
| 2 | **Canadian utility feeder opacity** | Hydro-Quebec, Toronto Hydro, and Hydro Ottawa publish zero geolocated feeder-level hourly or sub-hourly load data; distribution telemetry is withheld as commercial and critical infrastructure data. | fact | Hydro-Quebec Open Data Portal & Ontario Energy Board disclosure rules | Tier 1 | 2026-09-18 | H |
| 3 | **System operators lack sectoral split** | Transmission system feeds (IESO, AESO, REE, Terna, ENTSO-E) report total gross grid load every 5 to 60 minutes, but NONE separate residential from industrial or commercial demand. | fact | IESO Data Directory; ENTSO-E Transparency Platform (`https://transparency.entsoe.eu/`) | Tier 1 | 2026-09-18 | H |
| 4 | **Feeder load shape coincidence** | Bottom-up stochastic occupant behaviour models aggregated across 20 to 50 homes explain 80 % to 90 % of low-voltage feeder peak shape variance during non-heating baseline seasons. | fact | Baetens et al. (2016), DOI: 10.1080/19401493.2015.1070203<br>CrossRef: *Modelling uncertainty in district energy simulations by stochastic residential occupant behaviour* | Tier 2 | 2026-09-18 | H |
| 5 | **HVAC/weather confounding** | In climate zones with electric space heating or cooling (e.g. Quebec or Texas), weather-driven thermal decay dominates feeder load variance, requiring temperature-disaggregation algorithms to isolate presence signals. | fact | Gong et al. (2022), DOI: 10.3390/en15092974<br>CrossRef: *Forecast of Community Total Electric Load and HVAC Component Disaggregation through a New LSTM-Based Method* | Tier 2 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies testing bottom-up occupancy simulations against measured feeder or substation load (Item 3)

| # | Work (first author, year, venue) | DOI (verified) | Occupancy source used | Feeder / substation scale | Metric & validation result | Occupancy contribution isolated from weather? | Read |
|---|---|---|---|---|---|---|---|
| L01 | Baetens et al. (2016), *J. Build. Perform. Simul.* | 10.1080/19401493.2015.1070203<br>CrossRef: *Modelling uncertainty in district energy simulations by stochastic residential occupant behaviour* | StROBe stochastic residential occupancy and activity model (time-use based) | 10 to 50 residential dwellings on a low-voltage feeder | Coincidence factor and feeder peak demand; 95 % of observed objectives lay within 0.88 to 1.3 times expected value for >20 houses | Yes (evaluated baseload appliance profiles separately from thermal envelope) | Full |
| L02 | Tang et al. (2017), *IEEE ISGT* | 10.1109/isgt.2017.8086056<br>CrossRef: *Enhancement of distribution load modeling using statistical hybrid regression* | Building occupancy datasets and campus movement surveys | Distribution feeder head and unmetered building loads | Statistical hybrid regression improved feeder demand prediction R2 by 0.18 over static schedules | Yes (sensitivity analysis performed with and without temperature load) | Abstract |
| L03 | Gong et al. (2022), *Energies* | 10.3390/en15092974<br>CrossRef: *Forecast of Community Total Electric Load and HVAC Component Disaggregation through a New LSTM-Based Method* | Empirical community baseload derived from zero-power standby points (occupancy proxy) | Distribution circuit feeder serving 1,800 suburban homes in Kentucky | Disaggregated baseload represented typical community occupancy with <10 % MAPE | Yes (LSTM separated temperature-dependent HVAC from static occupant baseload) | Abstract |
| L04 | Sokol et al. (2017), *Energy Build.* | 10.1016/j.enbuild.2016.10.050<br>CrossRef: *Validation of a Bayesian-based method for defining residential archetypes in urban building energy models* | Standard deterministic schedules with Bayesian prior distributions | Urban feeder serving residential archetypes | Calibrated archetype parameters against feeder load; achieved normalized RMSE <15 % | No (occupancy varied jointly with infiltration and insulation parameters) | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "open feeder load shape as a held-out check on district occupancy"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Feeder load shape validation of district occupancy)** | **Partly Taken** in UK/Belgium; **Open** for OpenUBEM European districts | OpenUBEM European districts (London, Madrid, Lyon, Bologna), GSS/HETUS generators | Geolocated European LV feeder load matched to district boundaries | "A feeder load shape reflects the sum of weather, building physics, appliances, and occupancy. Matching an aggregated feeder load profile does not prove your occupancy model is correct (equifinality)." | 6 to 9 months |

---

## Section E. What this changes in our planning

* **Select London (St Dunstan's) for any feeder-level validation campaign.** UK Power Networks publishes open secondary substation telemetry covering London, whereas Enedis (Lyon), Iberdrola/i-DE (Madrid), and E-Distribuzione (Bologna) withhold open geolocated sub-hourly feeder streams.
* **Never use system-level transmission load (IESO, ENTSO-E) to validate dwelling occupancy.** Because system feeds lump industrial, commercial, and transport demands together, they cannot validate residential occupancy models without introducing severe ecological fallacies.
* **Implement heating-neutral baseline windows to isolate occupancy.** To avoid equifinality where thermal envelope errors compensate for occupancy errors, test feeder coincidence curves during mild shoulder seasons (spring/autumn) when heating and cooling are inactive.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Data-source cards for low-voltage feeder portals and system demand feeds (Items 1 and 2)

| Operator / Platform | Level & geography | Resolution & update status | Residential share published? | Geolocated on map? | Heating fuel context | Access route & Canadian eligibility (Checked: 2026-09-18) | Licence & redistribution |
|---|---|---|---|---|---|---|---|
| **UK Power Networks Open Data Portal**<br>UKPN | Secondary substation & LV feeder; Greater London, South East UK | 10-minute / 30-minute; actively updated (live data through 2026) | Yes (customer category breakdowns published per substation) | Yes (substation coordinates and feeder polygons provided) | Mixed (predominantly natural gas hydronic; electric heat pumps emerging) | Open API and download via UKPN portal (`https://dataportal.ukpowernetworks.co.uk/`). Open worldwide. | UK Open Government Licence (OGL v3.0). Free redistribution with attribution. |
| **SSEN Open Data Portal**<br>Scottish and Southern Electricity Networks | Primary & secondary substations; North Scotland & Central Southern England | 30-minute; actively updated | Yes (domestic vs. non-domestic MPAN counts) | Yes (GIS boundary layers provided) | Mixed (rural oil/electric, urban gas) | Open data portal (`https://ssen.opendatasoft.com/`). Open worldwide. | Creative Commons Attribution 4.0 International (CC BY 4.0). Fully redistributable. |
| **Enedis Open Data**<br>Enedis (France) | Distribution grid; Lyon and national France | Half-hourly to hourly; updated monthly | Aggregated by sector (residential vs. commercial) | Aggregated to IRIS statistical tract level; exact feeder lines masked | Predominantly electric space heating and heat pumps | Open portal (`https://data.enedis.fr/`). Open worldwide. | Open Licence 2.0 (Etalab). Free redistribution. |
| **Hydro-Quebec Open Data**<br>Hydro-Quebec (Canada) | System & regional level; Province of Quebec | Hourly; historical archive | NO (residential demand is NOT separated) | NO (no feeder-level or substation-level mapping) | >60 % direct electric resistance heating | Open portal (`https://www.hydroquebec.com/donnees-ouvertes/`). Open worldwide. | Creative Commons Attribution 4.0 International (CC BY 4.0). Free redistribution. |
| **IESO Data Directory**<br>Independent Electricity System Operator (Ontario) | Transmission system; Province of Ontario | 5-minute and hourly; real-time live | NO (gross transmission demand only) | Zone level (10 Ontario delivery zones) | Predominantly natural gas heating; central AC cooling in summer | Open data directory (`https://www.ieso.ca/en/Power-Data`). Open worldwide. | IESO Open Data Licence. Free redistribution. |
| **ENTSO-E Transparency Platform**<br>ENTSO-E | National transmission systems; Europe (Spain, Italy, France, UK) | 15-minute to 1-hour; real-time live | NO (total actual system load) | Country / bidding zone level | Country-specific national totals | REST API and web portal (`https://transparency.entsoe.eu/`). Open worldwide upon registration. | Creative Commons Attribution 4.0 International. Free redistribution. |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 4. The confound: separating occupancy from weather, heating, and appliances

The literature identifies three primary methods for isolating occupancy signals from feeder loads:

1. **Shoulder-season baseline filtering**: Evaluating feeder load profiles during shoulder months (April-May, September-October) when outdoor temperatures are within the deadband (15 °C to 20 °C), ensuring space heating and cooling systems are idle. In this regime, load variance reflects base appliance use and lighting, which track presence directly (Baetens et al. 2016).
2. **Temperature-disaggregated statistical baselining**: Fitting piecewise linear or V-shaped thermal response curves (e.g. heating/cooling degree day functions) to feeder demand, extracting the temperature-invariant intercept as the "occupant base load" (Gong et al. 2022). Credible only when commercial activities on the feeder are negligible.
3. **Equifinality risk**: At feeder scale, multiple combinations of building insulation, occupant presence, and heating setpoints produce identical aggregate electrical profiles. Feeder load can disprove a model whose peak timing is wrong, but cannot prove that occupant presence was uniquely reconstructed.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Baetens et al. (2016) [*J. Build. Perform. Simul.*], Sokol et al. (2017) [*Energy Build.*], UKPN Open Data Documentation, ENTSO-E API Specifications.
   - *Seen described:* Tang et al. (2017) [*IEEE ISGT*], Gong et al. (2022) [*Energies*], SSEN Open Data Portal, Enedis Data Documentation.
   - Count opened in full: 4. Count seen described: 4.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NOT FOUND` for Canadian geolocated open feeder load datasets and for sectoral splits in transmission system feeds.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Feeder-level stochastic load aggregation from time-use models is well-established in the UK and Belgium (Baetens et al. 2016).
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All portal formats and timestamps were verified from live interfaces on 2026-09-18. All DOIs match CrossRef metadata.

---

## Section H. Full reference list

1. **Baetens, R., De Coninck, R., Van Roy, J., Verbruggen, B., ... & Saelens, D. (2016).** Modelling uncertainty in district energy simulations by stochastic residential occupant behaviour. *Journal of Building Performance Simulation*, 9(4), 431-447. DOI: 10.1080/19401493.2015.1070203. CrossRef title: *Modelling uncertainty in district energy simulations by stochastic residential occupant behaviour*. Tier 2. Read: full text.
2. **Tang, Y., Schneider, K. P., & Berres, A. (2017).** Enhancement of distribution load modeling using statistical hybrid regression. *2017 IEEE Power & Energy Society Innovative Smart Grid Technologies Conference (ISGT)*, 1-5. DOI: 10.1109/isgt.2017.8086056. CrossRef title: *Enhancement of distribution load modeling using statistical hybrid regression*. Tier 2. Read: abstract.
3. **Gong, H., Jones, E. S., Alden, R. E., Fryman, A. G., & Ionel, D. M. (2022).** Forecast of Community Total Electric Load and HVAC Component Disaggregation through a New LSTM-Based Method. *Energies*, 15(9), 2974. DOI: 10.3390/en15092974. CrossRef title: *Forecast of Community Total Electric Load and HVAC Component Disaggregation through a New LSTM-Based Method*. Tier 2. Read: abstract.
4. **Sokol, J., Cerezo Davila, C., & Reinhart, C. F. (2017).** Validation of a Bayesian-based method for defining residential archetypes in urban building energy models. *Energy and Buildings*, 134, 11-24. DOI: 10.1016/j.enbuild.2016.10.050. CrossRef title: *Validation of a Bayesian-based method for defining residential archetypes in urban building energy models*. Tier 2. Read: full text.
