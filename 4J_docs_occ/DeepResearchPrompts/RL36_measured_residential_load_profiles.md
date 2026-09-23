# Deep-Research Report RL36: Measured Residential Electricity Load Profiles for Spain, Italy and the United Kingdom

## 1. Direct answer

The best usable measured source for Spain is IDAE's SPAHOUSEC study (2011), with REE's e-sios tariff 2.0TD profiles providing the official settlement benchmark.
For Italy, the best measured source is the RSE smart-meter monitoring panel published by Besagni et al. (2020) in Buildings, complemented by e-distribuzione's domestic settlement profiles.
For the United Kingdom, the premier source is the Household Electricity Survey (HES 2010-11, UK Data Service 7591), which provides physically sub-metered appliance demand, alongside Elexon's Profile Class 1 settlement profile.
No single, open-access, continuous measured hourly dataset covers all three countries on a unified basis today; the pan-European REMODECE project (2008) surveyed all three but its public archives lack complete, standardized hourly time-series files.
Crucially, SPAHOUSEC (Spain) and HES (UK) allow full empirical separation of appliance and lighting demand from space heating and water heating, whereas standard settlement profiles represent unseparated total meter demand.

## 2. Country-by-country load profile tables

### 2.1 Spain

| Feature | Source 1 (Best: Measured survey with sub-metering) | Source 2 (Regulated settlement profile) | Source 3 (Aggregated smart-meter portal) |
| :--- | :--- | :--- | :--- |
| **Source name** | IDAE SECH-SPAHOUSEC (2011) | Red Electrica de Espana (REE) / CNMC Perfiles de consumo iniciales (Tarifa 2.0TD / 2.0A) | Datadis (Plataforma de datos de las distribuidoras electricas de Espana) |
| **Type** | Survey with metering (in-situ appliance sub-metering) | Standard load profile used for settlement (regulatory profile) | Measured smart-meter data (aggregated provincial portal) |
| **Population** | Households only (600 metered households with physical sub-meters + 6,000 surveyed households across Atlantic-North, Continental, and Mediterranean zones) | Low-voltage customers under 15 kW (predominantly domestic households on default PVPC supply, but legally mixed with small businesses on tariff 2.0TD) | Domestic households on tariff 2.0TD (over 28 million smart-metered supply points aggregated by province and postal code) |
| **Period covered** | 2010 to 2011 | 2014 to present (updated annually and dynamically for each settlement year; 2.0TD since June 2021) | 2019 to present |
| **Day types separated** | Weekday and weekend separated; seasonal profiles (winter, summer, intermediate) | All 365 days of the year (differentiated by weekday, Saturday, Sunday/holiday, and seasonal day-types) | Continuous daily time series across all days of the week |
| **Resolution** | Hourly | Hourly (and 15-minute on recent ESIOS updates) | Hourly |
| **Heating included or separable** | SEPARABLE (physical sub-metering of appliance circuits, lighting, cooking, and refrigeration separate from electric space heating and ACS) | INCLUDED (NOT separable; gross electricity delivered at the delivery point / border meter) | INCLUDED (NOT separable at the whole-house smart meter level) |
| **Weekday peak hour** | Evening peak at 21:00-22:00; secondary midday lunch peak at 14:00-15:00 (read from figure) | Hour 21:00-22:00 (Hour 22, settlement period 21-22); secondary midday peak at Hour 14:00-15:00 (read from table) | Evening peak at 21:00-22:00; secondary midday peak at 14:00-15:00 (read from figure) |
| **Where seen in source** | IDAE Informe Final SPAHOUSEC (2011), Chapter 4, Grafico 4.12 ('Curva de carga media diaria de electrodomesticos') and Grafico 4.14 (pp. 54-58) | REE ESIOS portal, Indicator 522 ('Coeficientes de perdidas y perfiles de consumo iniciales'), downloadable settlement profile table | Datadis public web analytics portal, 'Curva de carga media horaria por provincia y tarifa 2.0TD' |
| **Access URL** | `https://www.idae.es/uploads/documentos/documentos_Informe_SPAHOUSEC_ACC_f68291a3.pdf` | `https://www.esios.ree.es/es/mercados-y-precios/perfiles-de-consumo` | `https://datadis.es` |
| **Licence** | Public domain / Open Government Data (Government of Spain / IDAE) | Open data (REE Terms of Service for ESIOS, free download with attribution) | Free access upon registration / public aggregated statistics under Spanish Open Data regulations |

### 2.2 Italy

| Feature | Source 1 (Best: Measured smart-meter research panel) | Source 2 (Regulated settlement profile) | Source 3 (Appliance end-use monitoring survey) |
| :--- | :--- | :--- | :--- |
| **Source name** | Besagni, Premoli Vila, and Borgarello (2020), RSE S.p.A. Monitoring Campaign | e-distribuzione / ARERA Profili di prelievo standardizzati per punti non orari (Clienti domestici DOM) | MICENE project / Pagliano et al. (Politecnico di Milano, eERG) |
| **Type** | Measured smart-meter and sensor panel data | Standard load profile used for settlement (regulatory profile) | Survey with metering (in-situ appliance sub-metering) |
| **Population** | 50 Italian households across Italy monitored with high-resolution power transmitters (classified into demographic clusters including energy-poor and families with children) | Domestic low-voltage customers (DOM / residenti D2, non residenti D3) on e-distribuzione grid | 110 Italian households in Lombardy and other regions monitored at appliance circuits |
| **Period covered** | 2018 to 2019 | Defined under ARERA Delibera 237/04 and ARG/elt 107/09, updated annually (2010 to 2022) | 2003 to 2005 |
| **Day types separated** | Weekday and weekend separated; seasonal breakdowns (winter, spring, summer, autumn) | Weekday (feriale), Saturday (prefestivo), and Sunday/holiday (festivo); broken down by season | Weekday and weekend separated; seasonal profiles |
| **Resolution** | 1-minute to hourly (reported in hourly mean load curves) | 15-minute and hourly | Hourly and 15-minute |
| **Heating included or separable** | CAN BE EXCLUDED / SEPARABLE (appliance baselines isolated; space heating is predominantly gas-fired in Italy, with electric auxiliary loads distinguished) | INCLUDED (NOT separable; total customer withdrawal from the low-voltage grid) | SEPARABLE (dedicated monitoring of appliances, lighting, and cooking; electric heating excluded) |
| **Weekday peak hour** | Evening peak between 19:30 and 22:30 (specifically 20:30-21:30); secondary midday peak at 12:30-13:30 (read from figure) | Hour 20:00-21:00; secondary midday peak at 12:00-13:00 (read from table) | Evening peak at 20:00-21:30; secondary midday peak at 12:30-13:30 (read from figure) |
| **Where seen in source** | Besagni et al. (2020), Buildings 10(12), 217, Figure 6 ('Average daily load profiles for weekdays across clusters') and Figure 8 (pp. 8-11) | e-distribuzione technical table 'Tabella coefficienti profilo di prelievo convenzionale BT domestico', Table 1; ARERA Delibera ARG/elt 107/09, Allegato A | Pagliano et al. (2006), 'Analisi dei consumi elettrici nel settore domestico: i risultati del progetto MICENE', Figure 3 and Table 2 |
| **Access URL** | `https://doi.org/10.3390/buildings10120217` | `https://www.e-distribuzione.it` and `https://www.arera.it/atti-e-provvedimenti/dettaglio/09/107-09` | `http://www.eerg.polimi.it` |
| **Licence** | Open Access (Creative Commons Attribution CC BY 4.0) | Public regulatory document / free download | Academic research report / open access |

### 2.3 United Kingdom

| Feature | Source 1 (Best: Physical sub-metering panel) | Source 2 (Regulated settlement profile) | Source 3 (Smart-meter trial panel) |
| :--- | :--- | :--- | :--- |
| **Source name** | Household Electricity Survey 2010-11 (HES) (DECC / Defra / EST / Intertek) | Elexon Profile Class 1 (PC1: Domestic Unrestricted Customers) | Low Carbon London (LCL) / UK Power Networks |
| **Type** | Survey with metering (comprehensive appliance and circuit sub-metering) | Standard load profile used for settlement (regulatory profile) | Measured smart-meter data (trial panel) |
| **Population** | 250 owner-occupier domestic households in England (26 monitored for 1 year, 224 monitored for 1 month) | Statistically representative panel of ~2,500 domestic unrestricted customers in Great Britain (Load Research Programme) | 5,567 domestic customer households across the Greater London area |
| **Period covered** | May 2010 to July 2011 | Continuously maintained since 1998, updated annually (including 2014-2015 HETUS period) | November 2011 to February 2014 |
| **Day types separated** | Weekday and weekend separated; monthly and seasonal breakdowns | 5 Day Types (Winter Weekday, Winter Saturday, etc.) across 5 distinct BSC settlement seasons | Continuous daily time series across all days of the week, weekends, and seasons |
| **Resolution** | 2-minute and 10-minute raw data (aggregated to hourly and half-hourly) | Half-hourly (48 settlement periods per day) | Half-hourly (30-minute) |
| **Heating included or separable** | FULLY SEPARABLE (physical sub-meters attached to every appliance plug, cooker, shower, immersion heater, and space heater) | INCLUDED (NOT separable; measures total whole-house active power at the supply boundary) | INCLUDED (NOT separable at the whole-house smart meter level) |
| **Weekday peak hour** | Evening peak at 18:00-19:00 (specifically peaking 18:30-19:30); secondary morning peak at 08:00-09:00 (read from figure) | Half-hour 36-37 (18:00-18:30, extending across 18:00-19:00; read from table) | Half-hour 37 (18:00-18:30, extending to 19:00; read from figure) |
| **Where seen in source** | Zimmermann et al. (2012), Intertek Report R66141 for DECC/Defra, Figure 4 (p. 22) and Figure 9 ('Mean daily profile across 250 households', p. 31) | Elexon BSC Guidance Note 'Load Profiles and their use in Electricity Settlement', Figure 1 ('Profile Class 1 Average Load Profile') and SVG profile table | UK Power Networks Low Carbon London Report 'Residential consumer responses to time-of-use tariffs', Figure 3.2 |
| **Access URL** | `https://doi.org/10.5255/UKDA-SN-7591-1` | `https://bscdocs.elexon.co.uk/guidance-note/load-profiles-and-their-use-in-electricity-settlement` | `https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households` |
| **Licence** | Open Government Licence v3.0 / UK Data Service End User Licence | Free public access under Elexon BSC open data terms | UK Open Government Licence (OGL v2.0, freely downloadable CSV files) |

## 3. Answers to specific questions

### Question A: Is there ONE source that gives household hourly profiles for all three countries on a comparable basis?

Candidate evaluated: The European Commission Intelligent Energy Europe project REMODECE (Residential Monitoring to Decrease Energy Use and Carbon Emissions in Europe, 2006-2008, coordinated by ISR-University of Coimbra).

Finding:
No single, harmonized, open-access hourly load profile dataset covering Spain, Italy, and the United Kingdom on a strictly comparable basis exists today.
While REMODECE surveyed and monitored households across several European countries, it does not serve as a ready-to-use common source for the following reasons:
1. The UK monitoring was not conducted under the same in-situ instrumentation campaign as continental partners, but was instead retrofitted from existing Energy Saving Trust data collections.
2. In-situ monitoring in REMODECE focused on two-week sample campaigns for individual appliances rather than continuous, annualized 8760-hour whole-house logging.
3. The public web database hosted by ISR-Coimbra (`http://remodece.isr.uc.pt/`) is currently largely archival and provides static annual consumption averages by appliance category rather than downloadable, high-resolution hourly time-series load curves for each country.
Consequently, combining three authoritative national empirical sources (SPAHOUSEC for Spain, Besagni/RSE for Italy, and HES for the UK) is substantially superior, more rigorous, and provides direct access to verified appliance-level measurements.

### Question B: For the standard settlement profiles (REE/CNMC, ARERA, Elexon): do they reflect measured household demand, and from which year's sample? Are they appliance-only or total household demand?

1. Spain (REE / CNMC Tariff 2.0TD, formerly 2.0A):
   - Sample basis: Derived originally from historical low-voltage customer load research panels established by UNESA and the system operator under Royal Decree 2017/1997 in the late 1990s and 2000s. REE updates the profile coefficients dynamically using calendar patterns, daylight hours, and temperature regression models, but the underlying customer classification was not continuously re-metered until the recent integration of smart meters.
   - Demand type: TOTAL household demand (gross electricity consumption measured at the meter). It includes all domestic appliances, lighting, electric cooking, electric water heaters, and electric space heating / air conditioning present in tariff 2.0TD dwellings. It is NOT appliance-only.

2. Italy (ARERA / e-distribuzione Profilo DOM):
   - Sample basis: Defined under ARERA Delibera 237/04 and ARG/elt 107/09 based on sample metering campaigns carried out by distribution network operators in the early 2000s prior to the nationwide Telegestore smart meter rollout.
   - Demand type: TOTAL household demand measured at the low-voltage delivery point. Because Italy achieved near 100 percent smart meter coverage by 2008, settlement for most customers is performed using actual multi-rate time bands (F1, F2, F3) or hourly readings, leaving synthetic profile curves primarily as a regulatory standard for residual non-hourly points. It is NOT appliance-only.

3. United Kingdom (Elexon Profile Class 1):
   - Sample basis: Derived from the national Load Research Programme (LRP), a statistically stratified sample of approximately 2,500 domestic unrestricted customers across Great Britain equipped with half-hourly recorders by Distribution Network Operators (DNOs). The profile is updated and reviewed annually by Elexon's Supplier Volume Allocation Group (SVG).
   - Demand type: TOTAL household demand measured at the whole-house fiscal meter. It captures all electricity imported by the dwelling, including space heating, water heating, and lighting alongside domestic appliances. It is NOT appliance-only.

### Question C: Which of these sources lets us separate appliance and lighting demand from space heating and water heating? If none does, say so.

1. United Kingdom: The Household Electricity Survey (HES 2010-11) permits COMPLETE SEPARATION.
   HES deployed dedicated physical sub-meters on every individual socket and hard-wired circuit across all 250 dwellings. Appliance loads (refrigeration, washing, cooking, audiovisual, computing) and lighting are logged independently from electric space heaters, electric immersion water heaters, and instantaneous electric showers. In contrast, Elexon PC1, Low Carbon London, and SERL record whole-house total demand where heating cannot be separated without unverified non-intrusive load monitoring (NILM) algorithms.

2. Spain: The IDAE SPAHOUSEC project (2011) permits COMPLETE SEPARATION.
   The 600 metered dwellings in SPAHOUSEC were equipped with physical multi-channel data loggers that monitored specific end-uses. The published study explicitly isolates annual and hourly load curves for domestic appliances ('Electrodomesticos'), lighting ('Iluminacion'), and cooking ('Cocina') from electric heating ('Calefaccion') and sanitary hot water ('ACS'). In contrast, REE settlement profiles and Datadis report only gross aggregate meter consumption.

3. Italy: The Besagni et al. (2020) RSE dataset and the MICENE project (eERG Politecnico di Milano) permit PARTIAL TO FULL SEPARATION.
   Besagni et al. (2020) and MICENE analyzed disaggregated end-use circuits and isolated baseline appliance consumption profiles. Furthermore, in Italian residential buildings, space heating and sanitary hot water are overwhelmingly fueled by natural gas (over 85 percent of Italian homes), meaning that measured whole-house electricity profiles in Italy are naturally dominated by appliances and lighting, with space heating contributing only minor electricity for water circulation pumps.

## 4. Full reference list of sources

- ARERA, 2009. Testo integrato delle disposizioni dell'Autorita per l'energia elettrica e il gas per l'erogazione dei servizi di trasmissione, distribuzione e misura dell'energia elettrica (TIT) e disposizioni per la perequazione dei costi di trasmissione e distribuzione. Deliberazione ARG/elt 107/09. Autorita di Regolazione per Energia Reti e Ambiente, Milan, Italy.
- Besagni, G., Premoli Vila, L., Borgarello, M., 2020. Italian Household Load Profiles: A Monitoring Campaign. Buildings 10 (12), 217. DOI: 10.3390/buildings10120217.
- Elexon, 2021. Load Profiles and their use in Electricity Settlement. BSC Guidance Note, Elexon Ltd., London, UK. URL: https://bscdocs.elexon.co.uk/guidance-note/load-profiles-and-their-use-in-electricity-settlement.
- Greater London Authority, 2015. SmartMeter Energy Use Data in London Households (Low Carbon London project). London Datastore. URL: https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households.
- IDAE, 2011. Proyecto SECH-SPAHOUSEC: Analisis del consumo energetico del sector residencial en Espana. Informe Final. Instituto para la Diversificacion y Ahorro de la Energia (IDAE), Ministerio de Industria, Turismo y Comercio, Madrid, Spain. URL: https://www.idae.es/uploads/documentos/documentos_Informe_SPAHOUSEC_ACC_f68291a3.pdf.
- Pagliano, L., Ruggieri, G., Zangheri, P., 2006. Analisi dei consumi elettrici nel settore domestico: i risultati del progetto MICENE. Technical Report, end-Use Efficiency Research Group (eERG), Politecnico di Milano, Milan, Italy.
- Red Electrica de Espana (REE), 2021. Perfiles de consumo y coeficientes de perdidas para el calculo de la energia en puntos de frontera. Plataforma e-sios, Red Electrica de Espana, Madrid, Spain. URL: https://www.esios.ree.es/es/mercados-y-precios/perfiles-de-consumo.
- Zimmermann, J.-P., Evans, M., Griggs, J., King, N., Morrison, L., Forest, V., 2012. Household Electricity Survey: A study of domestic electrical product usage. Intertek Testing & Certification Ltd and Energy Saving Trust for the Department of Energy and Climate Change (DECC) and Department for Environment, Food and Rural Affairs (Defra), London, UK. UK Data Service Study Number 7591. DOI: 10.5255/UKDA-SN-7591-1.

## 5. Positive control result

- Definition of Elexon Profile Class 1:
  Elexon's Profile Class 1 (PC1) represents the standard electricity load profile for 'Domestic Unrestricted Customers' on single-rate tariffs without switched off-peak loads, used in Great Britain's Balancing and Settlement Code (BSC) arrangements to convert non-half-hourly meter readings into half-hourly settlement consumption estimates.
- Exact URL of Elexon's page describing the standard load profiles:
  `https://www.elexon.co.uk/knowledgebase/profiling/`
  (with the primary operational guidance note located at `https://bscdocs.elexon.co.uk/guidance-note/load-profiles-and-their-use-in-electricity-settlement`).

## 6. What I could not find

- I could not find any single, centralized, downloadable hourly time-series dataset that provides synchronized, measured appliance-only electricity profiles across Spain, Italy, and the United Kingdom simultaneously.
- I could not find any public, open-access repository from Red Electrica de Espana or Datadis that isolates domestic appliance-only electricity consumption from space heating and domestic hot water.
- I could not find a publicly downloadable, 8760-hour raw csv dataset for the REMODECE project on the University of Coimbra website, which currently hosts only summarized deliverable PDFs and static aggregate appliance tables.
