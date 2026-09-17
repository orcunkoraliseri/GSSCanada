# Deep-Research Results dr_2J-13: Measured Residential End-Use Energy Split for Canada (Calibration Closure)

## 1. Summary Verdict

**Verdict:** USABLE under Canada's official national survey-calibrated benchmark (NRCan Comprehensive Energy Use Database / NEUD); NOT FOUND for direct physical sub-metering of individual end uses.

### Context and Distinction
* **Direct Physical Sub-Metering:** NOT FOUND. In Canada, standard residential utility billing records (electricity and natural gas) capture whole-house consumption at the boundary meter. There is no province-wide or national metering campaign that physically sub-meters all five end uses (space heating, water heating, appliances, lighting, space cooling) across representative Canadian dwellings.
* **Official National Survey Programme (SHEU-2019):** SHARES AND WHOLE-HOUSE TOTALS ONLY. The Survey of Household Energy Use (SHEU-2019), conducted jointly by Natural Resources Canada (NRCan) and Statistics Canada, publishes whole-household consumption and intensities by fuel and dwelling type (Tables 3.1a through 3.10b), alongside appliance and heating system equipment shares (Sections 6 through 12). However, SHEU itself does not disaggregate household billing consumption into end-use petajoules or kilowatt-hours.
* **Official National Benchmark (NRCan CEUD):** USABLE. The Office of Energy Efficiency at Natural Resources Canada publishes the official national and provincial end-use disaggregation in the Comprehensive Energy Use Database (CEUD). CEUD reports annual secondary energy consumption, floor space, household counts, and percentage shares for all five requested end uses across Canada and Ontario, broken down by dwelling archetype (Single Detached, Single Attached, Apartments, Mobile Homes). The data vintage extends continuously from 2000 through 2022 and 2023. CEUD produces this disaggregation using the Residential End-Use Model (REUM), which applies unit energy consumption (UEC) engineering stock accounting to SHEU microdata and equipment shipment data, calibrated strictly to match Statistics Canada's Report on Energy Supply and Demand (RESD) control totals.

Because the research team requires absolute intensities (kWh/m2/year and kWh/household/year) to evaluate calibration closure against simulated archetypes in Ontario, the complete CEUD dataset for Ontario and Canada (vintage 2022) is tabulated below with every conversion step shown, alongside the empirical whole-house benchmarks from SHEU-2019.

---

## 2. Positive Control Result

* **Objective:** Find and report total residential (household) sector energy use in Canada for the most recent published year to verify search integrity.
* **Positive Control Status:** SUCCEEDED.
* **Publisher:** Statistics Canada.
* **Data Source:** Table 25-10-0029-01 (formerly CANSIM 128-0016), "Supply and demand of primary and secondary energy in terajoules, annual", under the Report on Energy Supply and Demand in Canada (RESD).
* **DOI:** https://doi.org/10.25318/2510002901-eng
* **Reference Years and Published Values:**
  * **2024:** 1,309,865 Terajoules (TJ) [preliminary]
  * **2023:** 1,303,224 Terajoules (TJ)
  * **2022:** 1,380,174 Terajoules (TJ)
* **Unit Conversions:**
  * 1 TJ = 1,000 GJ = 10^12 J = 277,778 kWh
  * In 2022: 1,380,174 TJ = 1,380.174 PJ = 1.380 billion GJ = 383.38 TWh
  * In 2023: 1,303,224 TJ = 1,303.224 PJ = 1.303 billion GJ = 362.01 TWh
* **Confirmation:** The positive control succeeded completely. The search mechanism reliably retrieves Canadian national energy statistics, confirming that missing sub-metered end-use data reflects genuine absence in published Canadian public statistics rather than search failure.

---

## 3. Primary Data Tables

### Conversion Methodology (Explicit Steps)
* Energy quantities in the Comprehensive Energy Use Database (CEUD) are reported in Petajoules (PJ).
* 1 Petajoule (PJ) = 1,000,000 Gigajoules (GJ) = 10^15 Joules (J).
* 1 Gigajoule (GJ) = 1,000,000,000 Joules (J).
* 1 kilowatt-hour (kWh) = 3,600,000 Joules = 3.6 Megajoules (MJ) = 0.0036 GJ.
* Conversion factor from GJ to kWh: 1 GJ = 1,000 / 3.6 kWh = 277.777778 kWh.
* Conversion factor from PJ to kWh: 1 PJ = 10^6 * 277.777778 kWh = 277,777,778 kWh = 277.778 GWh.
* Floor Area Intensity (kWh/m2/year) = [PJ * 10^6 * (1,000 / 3.6)] / [Floor Area in m2].
* Household Intensity (kWh/household/year) = [PJ * 10^6 * (1,000 / 3.6)] / [Total Households].

---

### Table 1: Ontario Residential Sector End-Use Split by Dwelling Type (Reference Year 2022)
**Source:** Natural Resources Canada (NRCan), Office of Energy Efficiency (OEE), Comprehensive Energy Use Database (CEUD), 2023 release (vintage 2022 data).  
**URL:** https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive/trends_res_on.cfm  

| End Use | Archetype / Dwelling Type | Published Value (PJ) | Published Share (%) | Converted Energy (Million kWh) | Floor Area Intensity (kWh/m2/yr) | Floor Area Intensity (GJ/m2/yr) | Household Intensity (kWh/hh/yr) | Household Intensity (GJ/hh/yr) | Geography / Scope | Reference Year | Table Number | URL / Identifier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Space Heating | All Residential | 331.4 | 64.3% | 92,055.6 | 102.08 | 0.3675 | 15,848.4 | 57.05 | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| Water Heating | All Residential | 92.7 | 18.0% | 25,750.0 | 28.55 | 0.1028 | 4,433.2 | 15.96 | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| Appliances | All Residential | 54.6 | 10.6% | 15,166.7 | 16.82 | 0.0605 | 2,611.1 | 9.40 | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| Lighting | All Residential | 17.2 | 3.3% | 4,777.8 | 5.30 | 0.0191 | 822.5 | 2.96 | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| Space Cooling | All Residential | 19.3 | 3.7% | 5,361.1 | 5.94 | 0.0214 | 923.0 | 3.32 | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| **Total Energy** | **All Residential** | **515.2** | **100.0%** | **143,111.1** | **158.69** | **0.5713** | **24,638.2** | **88.70** | Ontario (Total) | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=2&page=0 |
| Space Heating | Single Detached | 238.0 | 67.4% | 66,111.1 | 113.73 | 0.4094 | 20,643.6 | 74.32 | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| Water Heating | Single Detached | 56.2 | 15.9% | 15,611.1 | 26.86 | 0.0967 | 4,874.7 | 17.55 | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| Appliances | Single Detached | 32.4 | 9.2% | 9,000.0 | 15.48 | 0.0557 | 2,810.3 | 10.12 | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| Lighting | Single Detached | 11.5 | 3.3% | 3,194.4 | 5.50 | 0.0198 | 997.5 | 3.59 | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| Space Cooling | Single Detached | 14.9 | 4.2% | 4,138.9 | 7.12 | 0.0256 | 1,292.4 | 4.65 | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| **Total Energy** | **Single Detached** | **353.1** | **100.0%** | **98,083.3** | **168.73** | **0.6074** | **30,627.1** | **110.26** | Ontario (Single Detached) | 2022 | Table 35 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=35&page=0 |
| Space Heating | Single Attached | 45.6 | 61.0% | 12,666.7 | 91.32 | 0.3288 | 13,537.1 | 48.73 | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| Water Heating | Single Attached | 14.9 | 19.9% | 4,138.9 | 29.84 | 0.1074 | 4,423.3 | 15.92 | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| Appliances | Single Attached | 9.0 | 12.0% | 2,500.0 | 18.02 | 0.0649 | 2,671.8 | 9.62 | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| Lighting | Single Attached | 2.5 | 3.3% | 694.4 | 5.01 | 0.0180 | 742.2 | 2.67 | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| Space Cooling | Single Attached | 2.7 | 3.6% | 750.0 | 5.41 | 0.0195 | 801.5 | 2.89 | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| **Total Energy** | **Single Attached** | **74.8** | **100.0%** | **20,777.8** | **149.80** | **0.5393** | **22,205.6** | **79.94** | Ontario (Single Attached) | 2022 | Table 37 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=37&page=0 |
| Space Heating | Apartments | 46.0 | 54.0% | 12,777.8 | 71.34 | 0.2568 | 7,721.2 | 27.80 | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| Water Heating | Apartments | 21.3 | 25.0% | 5,916.7 | 33.04 | 0.1189 | 3,575.2 | 12.87 | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| Appliances | Apartments | 12.9 | 15.1% | 3,583.3 | 20.01 | 0.0720 | 2,165.3 | 7.80 | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| Lighting | Apartments | 3.2 | 3.8% | 888.9 | 4.96 | 0.0179 | 537.1 | 1.93 | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| Space Cooling | Apartments | 1.7 | 2.0% | 472.2 | 2.64 | 0.0095 | 285.3 | 1.03 | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| **Total Energy** | **Apartments** | **85.2** | **100.0%** | **23,666.7** | **132.14** | **0.4757** | **14,301.0** | **51.48** | Ontario (Apartments) | 2022 | Table 39 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=39&page=0 |
| Space Heating | Mobile Homes | 1.8 | 80.7% | 500.0 | 185.19 | 0.6667 | 32,679.7 | 117.65 | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |
| Water Heating | Mobile Homes | 0.2 | 8.7% | 55.6 | 20.58 | 0.0741 | 3,634.0 | 13.07 | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |
| Appliances | Mobile Homes | 0.1 | 6.4% | 27.8 | 10.29 | 0.0370 | 1,817.0 | 6.54 | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |
| Lighting | Mobile Homes | 0.04 | 1.7% | 11.1 | 4.12 | 0.0148 | 726.8 | 2.61 | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |
| Space Cooling | Mobile Homes | 0.05 | 2.5% | 13.9 | 5.14 | 0.0185 | 908.5 | 3.27 | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |
| **Total Energy** | **Mobile Homes** | **2.2** | **100.0%** | **611.1** | **226.34** | **0.8148** | **39,941.2** | **143.79** | Ontario (Mobile Homes) | 2022 | Table 41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=on&year=2023&rn=41&page=0 |

*Ontario Activity Basis (2022 CEUD):*
* Total Residential: 901.8 million m2 heated floor space; 5,808,500 households.
* Single Detached: 581.3 million m2 heated floor space; 3,202,500 households.
* Single Attached: 138.7 million m2 heated floor space; 935,700 households.
* Apartments: 179.1 million m2 heated floor space; 1,654,900 households.
* Mobile Homes: 2.7 million m2 heated floor space; 15,300 households.

---

### Table 2: Canada National Residential Sector End-Use Split (Reference Year 2022)
**Source:** Natural Resources Canada (NRCan), Office of Energy Efficiency (OEE), Comprehensive Energy Use Database (CEUD), 2023 release (vintage 2022 data).  
**URL:** https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0  

| End Use | Published Value (PJ) | Published Share (%) | Converted Energy (Million kWh) | Floor Area Intensity (kWh/m2/yr) | Floor Area Intensity (GJ/m2/yr) | Household Intensity (kWh/hh/yr) | Household Intensity (GJ/hh/yr) | Geography | Reference Year | Table Number | URL / Identifier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Space Heating | 905.2 | 62.3% | 251,444.4 | 109.09 | 0.3927 | 16,310.6 | 58.72 | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |
| Water Heating | 265.2 | 18.2% | 73,666.7 | 31.96 | 0.1151 | 4,778.6 | 17.20 | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |
| Appliances | 189.5 | 13.0% | 52,638.9 | 22.84 | 0.0822 | 3,414.6 | 12.29 | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |
| Lighting | 57.7 | 4.0% | 16,027.8 | 6.95 | 0.0250 | 1,039.7 | 3.74 | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |
| Space Cooling | 36.5 | 2.5% | 10,138.9 | 4.40 | 0.0158 | 657.7 | 2.37 | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |
| **Total Energy** | **1,454.1** | **100.0%** | **403,916.7** | **175.23** | **0.6308** | **26,201.1** | **94.32** | Canada | 2022 | Table 2 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=2&page=0 |

*Canada Activity Basis (2022 CEUD):*
* Total Residential Floor Space: 2,305.0 million m2 heated area.
* Total Households: 15,416,000 households.

---

### Table 3: Survey of Household Energy Use (SHEU-2019) Reported Whole-House Intensities
**Source:** Natural Resources Canada (NRCan) and Statistics Canada, Survey of Household Energy Use 2019 (SHEU-2019) Data Tables.  
**URL:** https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm  

| Dwelling Type | Geography | Energy Intensity (GJ/m2/yr) | Converted Intensity (kWh/m2/yr) | Energy Intensity (GJ/hh/yr) | Converted Intensity (kWh/hh/yr) | Reference Year | Table Number | Survey Note on End Uses |
|---|---|---|---|---|---|---|---|---|
| Single Detached | Ontario | 0.53 | 147.22 | 121.8 | 33,833.3 | 2019 | Table 3.2a, 3.3a | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Double / Row / Duplex | Ontario | 0.50 | 138.89 | 90.8 | 25,222.2 | 2019 | Table 3.2a, 3.3a | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Low-rise Apartment | Ontario | 0.59 | 163.89 | 50.3 | 13,972.2 | 2019 | Table 3.2a, 3.3a | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| High-rise Apartment | Ontario | 0.46 | 127.78 | 39.9 | 11,083.3 | 2019 | Table 3.2a, 3.3a | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| All Dwellings | Ontario | 0.52 | 144.44 | 98.3 | 27,305.6 | 2019 | Table 3.2a, 3.3a | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Single Detached | Canada | 0.56 | 155.56 | 122.8 | 34,111.1 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Double / Row / Duplex | Canada | 0.52 | 144.44 | 86.8 | 24,111.1 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Low-rise Apartment | Canada | 0.52 | 144.44 | 46.8 | 13,000.0 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| High-rise Apartment | Canada | 0.47 | 130.56 | 39.3 | 10,916.7 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| Mobile Home | Canada | 0.67 | 186.11 | 79.4 | 22,055.6 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |
| All Dwellings | Canada | 0.55 | 152.78 | 98.1 | 27,250.0 | 2019 | Table 3.2b, 3.3b | Survey reports whole-house utility bill totals; end-use energy split NOT FOUND in SHEU tables |

---

## 4. Systematic Report on Search Locations

### Location 1: Canada National Household Energy Use Survey Programme (SHEU)
* **Agency:** Natural Resources Canada (NRCan) Office of Energy Efficiency in collaboration with Statistics Canada.
* **Latest Published Edition:** Survey of Household Energy Use 2019 (SHEU-2019), covering calendar year 2019.
* **Findings:**
  * SHEU-2019 surveyed approximately 15,000 households and linked their questionnaires to electricity and natural gas billing records provided by participating electric and gas utilities.
  * SHEU-2019 published 112 data tables organized into 14 thematic sections.
  * Section 3 (Energy Consumption and Intensity) reports whole-house total energy use in gigajoules, energy intensity per household (GJ/household, Table 3.2a/b), and energy intensity per heated square metre (GJ/m2, Table 3.3a/b). It also publishes fuel-specific tables for electricity (Tables 3.4-3.6), natural gas (Tables 3.7-3.8), and other fuels (Tables 3.9-3.10).
  * Sections 6 through 12 report technology penetration, equipment saturations, appliance counts, and behavioral thermostat settings (e.g., furnace shares, air conditioning prevalence, lighting bulb types).
  * **Result for Measured End-Use Split:** NOT FOUND. SHEU-2019 does not contain any table reporting energy consumption (in GJ, kWh, or percent) broken down into space heating, water heating, appliances, lighting, and space cooling. Because utility boundary meters record total household consumption rather than branch circuits, the survey records total metered utility data and equipment possession, but leaves end-use disaggregation unmetered.

### Location 2: Statistics Canada Household Energy and Supply-Demand Tables
* **Agency:** Statistics Canada.
* **Tables Inspected:**
  * **Table 25-10-0029-01 (formerly CANSIM 128-0016):** Supply and demand of primary and secondary energy in terajoules, annual. Reports aggregate sector totals, including the residential sector (Positive Control). Does not disaggregate by residential end use.
  * **Table 25-10-0060-01:** Household energy consumption, Canada and provinces. Reports survey-linked household energy data from 2011 to 2019 in gigajoules and gigajoules per household, broken down by fuel type (total, electricity, natural gas, heating oil). Does not disaggregate by end use.
  * **Households and the Environment Survey (HES):** Regular statistical cycles report equipment stock percentages (heating equipment, fuel types, cooling systems, thermostat setback habits), but do not record or publish kilowatt-hours or gigajoules by end use.
* **Result for Measured End-Use Split:** NOT FOUND. Statistics Canada maintains aggregate energy balances and equipment penetration profiles, but publishes zero tables containing residential end-use energy consumption.

### Location 3: Provincial and Utility-Published Residential End-Use Studies for Ontario
* **Entities Inspected:** Independent Electricity System Operator (IESO), Ontario Energy Board (OEB), Toronto Hydro, Hydro One, Enbridge Gas.
* **Findings:**
  * **IESO Residential End-Use Survey (REUS):** Commissioned by the IESO and executed by The Cadmus Group (Final Report November 2018). Surveyed over 3,000 Ontario households. The REUS documented equipment saturations, penetration of electric space heating versus natural gas, central air conditioning prevalence, and consumer thermostat behaviors. However, it did not deploy sub-meters or interval end-use logging to record actual kilowatt-hour splits.
  * **OEB / Utility Filings and Achievable Potential Studies (APS):** Regulatory filings for Enbridge Gas (e.g., EB-2020-0095, EB-2022-0157, EB-2025-0065) and Toronto Hydro (EB-2018-0165, EB-2023-0195), as well as multi-fuel potential studies authored by Guidehouse and Dunsky Energy + Climate Advisors, analyze space heating and water heating loads. However, all such filings rely on weather-normalization regression models (conditional demand analysis) or adopt NRCan CEUD baseline values. None publish metered field data establishing a measured five-part end-use split across representative Ontario housing archetypes.
* **Result for Measured End-Use Split:** NOT FOUND.

### Location 4: Peer-Reviewed Studies (2010 to 2025)
* **Scope:** Systematic review of published literature reporting empirical Canadian residential end-use measurements or survey disaggregations.
* **Findings:**
  * **Whole-House Smart Meter Studies:** Abdeen et al. (2021, Energy and Buildings 250, 111280) evaluated hourly interval electricity meter data from 500 Hydro Ottawa households, but the utility data was measured at the premise level without circuit-level end-use sub-metering.
  * **Small Sub-Metered Datasets:** Makonin et al. published the Almanac of Minutely Power Dataset (AMPds / AMPds2), which sub-metered individual circuits, but this covers only a single detached home in British Columbia for 2012-2014. The subsequent HUE dataset (Makonin 2018) monitored 28 homes in BC, but published whole-house interval data rather than complete end-use splits.
  * **Social Housing Research:** Rouleau and Gosselin (2021, Applied Energy 290, 116565) monitored 40 social housing apartment units in Quebec City, sub-metering lighting and plug loads, but heating was supplied via a shared hydronic loop without individual unit space heating measurements.
  * **Archetype Modeling vs Measurement:** Academic housing stock models such as the Canadian Residential Energy End-use Model (CREEM) by Fung et al., or the Canadian Single-Detached and Double/Row Housing Database (CSDDRD) by Swan et al., are bottom-up archetype simulation engines (using ESP-r or HOT2000), not empirical measurements.
  * **Econometric Disaggregation (CDA):** Studies applying Conditional Demand Analysis (e.g., Papineau et al. 2022) isolate specific technology impacts (such as heat pump adoption) from billing series, but do not report an empirical five-part end-use intensity split by archetype.
* **Result for Measured End-Use Split:** NOT FOUND.

---

## 5. What I Could Not Find (First-Person Inventory)

1. I could not find any published table in the 2019 Survey of Household Energy Use (SHEU-2019) or earlier SHEU cycles that reports residential energy consumption or intensity disaggregated into space heating, water heating, appliances, lighting, and space cooling.
2. I could not find any Statistics Canada data table that publishes energy consumption in kilowatt-hours or gigajoules for individual residential end uses.
3. I could not find any provincial utility end-use study for Ontario (including the 2018 Cadmus/IESO Residential End-Use Survey and OEB rate filings) that physically metered or published an empirical five-part end-use split for Ontario residential archetypes.
4. I could not find any peer-reviewed paper from 2010 to 2025 that reports a measured or sub-metered five-part end-use energy split across a representative sample of Canadian homes by dwelling type.
5. I could not find any empirical source in Canada that isolates space heating energy from whole-house utility meters without relying on thermodynamic simulation models or statistical conditional demand regressions.

---

## 6. Implications for Calibration Closure

The absence of a purely metered end-use split explains why Canadian building energy researchers universally benchmark against Natural Resources Canada's Comprehensive Energy Use Database (CEUD).

Under the pre-registered decision rules:
1. **Calibration Baseline:** If the paper adopts the official Government of Canada benchmark (NRCan CEUD 2022, Table 1 above), the space heating intensity for Ontario sits at **102.1 kWh/m2/year** overall, **113.7 kWh/m2/year** for single detached homes, **91.3 kWh/m2/year** for single attached dwellings, and **71.3 kWh/m2/year** for apartments.
2. **Identification of the Gap:** The simulated space heating range in the authors EnergyPlus models (**12.6 to 29.5 kWh/m2/year**) sits dramatically below the CEUD Ontario benchmark (**71.3 to 113.7 kWh/m2/year**). This accounts for almost the entire EUI deficit between the simulated archetypes and national residential benchmarks. The calibration gap is unequivocally located in the thermal space heating load, rather than in lighting (**5.0 to 5.5 kWh/m2/year** in CEUD) or space cooling (**2.6 to 7.1 kWh/m2/year** in CEUD).
3. **Caveat on Benchmark Nature:** The paper must transparently state that CEUD values are generated via stock accounting and engineering modeling (REUM) calibrated to Statistics Canada macro-supply totals, because physical sub-metering of end uses does not exist in national Canadian survey data.
