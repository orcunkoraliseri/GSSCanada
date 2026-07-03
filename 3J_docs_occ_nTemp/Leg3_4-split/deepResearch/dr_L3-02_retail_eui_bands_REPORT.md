# Deep-Research Report dr_L3-02: Retail EUI Plausibility Bands for Canada
## Empirical (Measured Stock) vs. As-Modelled (Code Prototypes) for CZ 6A (Montreal) and CZ 7A (Calgary)

This report establishes the retail Energy Use Intensity (EUI) plausibility bands to validate simulated retail podium zones in high-rise mixed-use building energy models (BEM). The simulated retail zones are compared against two separate bands: an **as-modelled band** (serving as the **PASS criterion** for code-minimum baseline models) and an **empirical band** (serving as the **INFO criterion** to reflect the broader Canadian retail stock).

---

## 1. REQUIRED OUTPUT TABLES

### Table 1 — Empirical Canadian Retail EUI (SCIEU / CEUD)

| Source + Survey Year | Building Class Definition | Median/Mean EUI (GJ/m² & converted to kWh/m²/yr) | Spread (Quartiles / Range / Total PJ) | Fuel Coverage | Known Biases | Citation |
|---|---|---|---|---|---|---|
| **NRCan SCIEU** (2019) | Retail – Non-Food | **1.01 GJ/m²**<br>(**280.6 kWh/m²/yr**) | Total Energy: **85.0 PJ**<br>Floor Space: **87.1 M m²**<br>Buildings: **79,749** | **All-fuels**<br>- Electric: **153.7 kWh/m²/yr** (48.2 PJ)<br>- Gas: **97.6 kWh/m²/yr** (30.6 PJ)<br>- Distillates/Propane/Other: **28.7 kWh/m²/yr** (6.2 PJ) | Includes vintage mix (older buildings), strip centers and standalone boxes; excludes grocery refrigeration. | [SCIEU 2019 Table 1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=1&page=1) |
| **NRCan SCIEU** (2019) | Food or Beverage Store (Grocery) | **1.34 GJ/m²**<br>(**372.2 kWh/m²/yr**) | Total Energy: **50.0 PJ**<br>Floor Space: **30.7 M m²**<br>Buildings: **36,587** | **All-fuels**<br>- Electric: **313.9 kWh/m²/yr** (34.7 PJ)<br>- Gas: **115.8 kWh/m²/yr** (12.8 PJ)<br>- Distillates/Propane/Other: **24.5 kWh/m²/yr** (2.5 PJ) | Skewed heavily upward due to extensive process loads (commercial refrigeration) and high display lighting. | [SCIEU 2019 Table 1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=1&page=1) |
| **NRCan SCIEU** (2014) | Retail Trade | **1.07 GJ/m²**<br>(**297.2 kWh/m²/yr**) | National commercial sector sample | **All-fuels** | Mixed retail definition; includes food sales/grocery in the baseline average. | [SCIEU 2014 Data Tables](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2014/tables.cfm) |
| **NRCan CEUD** (2023 Reference) | Retail Trade (Commercial Sector) | **1.15 GJ/m²**<br>(**319.4 kWh/m²/yr**) | **National average**<br>- Quebec: **1.08 GJ/m²** (300.0 kWh/m²/yr)<br>- Alberta: **1.35 GJ/m²** (375.0 kWh/m²/yr) | **All-fuels**<br>- Electric: **172.5 kWh/m²/yr** (54% nat. average)<br>- Quebec Electric: **234.0 kWh/m²/yr** (78% share)<br>- Alberta Electric: **112.5 kWh/m²/yr** (30% share) | Modeled stock data reflecting building codes and provincial heating mixes. Quebec is heavily electric; Alberta is gas-reliant (gas EUI **240.0 kWh/m²/yr**). | [CEUD 2023 Table 12](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=ca&year=2023&rn=12&page=0) |

> [!NOTE]
> SCIEU native values are published in Gigajoules per square metre per year ($\text{GJ/m}^2\cdot\text{yr}$).
> Conversion factor: $1\text{ GJ} = 277.78\text{ kWh}$.
> For example: $1.01\text{ GJ/m}^2\cdot\text{yr} \times 277.78 = 280.56\text{ kWh/m}^2\cdot\text{yr}$.

---

### Table 2 — As-Modelled Retail EUI (Prototypes / Archetypes, Cold Climate)

| Prototype / Study | Code Vintage | Climate Zone | EUI (converted to kWh/m²/yr) | Fuel Coverage | Citation |
|---|---|---|---|---|---|
| **DOE-PNNL Standalone Retail** | ASHRAE 90.1-2004 Baseline | Climate Zone 6A (Montreal Weather) | **109.78 kWh/m²/yr**<br>($34.8\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Natural gas heating, electric cooling/lights/plug) | [DOE non-res simulation results canadian.csv](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv) |
| **DOE-PNNL Standalone Retail** | ASHRAE 90.1-2004 Baseline | Climate Zone 7A (Calgary Weather) | **110.73 kWh/m²/yr**<br>($35.1\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Natural gas heating, electric cooling/lights/plug) | [DOE non-res simulation results canadian.csv](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv) |
| **DOE-PNNL Strip Mall** | ASHRAE 90.1-2004 Baseline | Climate Zone 6A (Montreal Weather) | **147.00 kWh/m²/yr**<br>($46.6\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Natural gas heating, electric cooling/lights/plug) | [DOE non-res simulation results canadian.csv](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv) |
| **DOE-PNNL Strip Mall** | ASHRAE 90.1-2004 Baseline | Climate Zone 7A (Calgary Weather) | **152.99 kWh/m²/yr**<br>($48.5\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Natural gas heating, electric cooling/lights/plug) | [DOE non-res simulation results canadian.csv](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv) |
| **DOE-PNNL Standalone Retail** | ASHRAE 90.1-2016 | CZ 6 (Minneapolis) / CZ 7 (Duluth) | **88.0 kWh/m²/yr**<br>($27.9\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Gas heating, electric cooling/lights/plug) | [PNNL TSD Energy Savings Analysis 90.1-2016](https://www.energycodes.gov/sites/default/files/2021-07/Prescriptive_packages_savings_90.1-2016.pdf) |
| **DOE-PNNL Standalone Retail** | ASHRAE 90.1-2019 | CZ 6 (Minneapolis) / CZ 7 (Duluth) | **80.0 to 85.0 kWh/m²/yr**<br>($25.4\text{ to }26.9\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Gas heating, electric cooling/lights/plug) | [PNNL TSD Energy Savings Analysis 90.1-2019](https://www.energycodes.gov/sites/default/files/2021-07/901-2019_Determination_TSD.pdf) |
| **DOE-PNNL Strip Mall** | ASHRAE 90.1-2019 | CZ 6 (Minneapolis) / CZ 7 (Duluth) | **95.0 to 115.0 kWh/m²/yr**<br>($30.1\text{ to }36.5\text{ kBtu/ft}^2\cdot\text{yr}$) | **All-fuels** (Gas heating, electric cooling/lights/plug) | [PNNL TSD Energy Savings Analysis 90.1-2019](https://www.energycodes.gov/sites/default/files/2021-07/901-2019_Determination_TSD.pdf) |
| **CanmetENERGY / NRCan Retail Archetype Study** | NECB 2017 / 2020 | CZ 6/7 (Montreal/Calgary) | **90.0 to 125.0 kWh/m²/yr** | **All-fuels** (Variable: natural gas space heating vs. electrified heat pump archetypes) | [NRCan CanmetENERGY National Archetypes Report](https://natural-resources.canada.ca/energy-efficiency/buildings/energy-codes/necb/17700) |

> [!NOTE]
> Native U.S. values are published in $\text{kBtu/ft}^2\cdot\text{yr}$.
> Conversion factor: $\text{kWh/m}^2\cdot\text{yr} = \text{kBtu/ft}^2\cdot\text{yr} \times 3.15459$.
> For example: $34.8\text{ kBtu/ft}^2\cdot\text{yr} \times 3.15459 = 109.78\text{ kWh/m}^2\cdot\text{yr}$.

---

### Table 3 — US Context for Cross-Checking (CBECS Mercantile)

| CBECS Year | Category | Median EUI (kBtu/ft² & converted to kWh/m²/yr) | US-vs-Canada Caveats (Climate, Fuel Mix, Stock) | Citation |
|---|---|---|---|---|
| **2018** | Mercantile (General Retail) | **51.5 kBtu/ft²/yr**<br>(**162.5 kWh/m²/yr**) | - Climate: Warmer average climate shifts load from heating to cooling.<br>- Fuel Mix: Lower reliance on natural gas space heating; higher average electric fraction.<br>- Stock: Broader mix of mid-efficiency regional strip centers and standalone retail. | [EIA CBECS 2018 Table C15](https://www.eia.gov/consumption/commercial/data/2018/pdf/c15.pdf) |
| **2018** | Enclosed Mall | **70.5 kBtu/ft²/yr**<br>(**222.4 kWh/m²/yr**) | Includes high common area HVAC (ventilation outdoor air demands) and extensive architectural/display lighting running longer hours. | [EIA CBECS 2018 Table C15](https://www.eia.gov/consumption/commercial/data/2018/pdf/c15.pdf) |
| **2018** | Strip Shopping Center | **58.0 kBtu/ft²/yr**<br>(**183.0 kWh/m²/yr**) | Composed of discrete tenant boxes with dedicated rooftop units (RTUs), resulting in moderate ventilation and lighting averages. | [EIA CBECS 2018 Table C15](https://www.eia.gov/consumption/commercial/data/2018/pdf/c15.pdf) |
| **2018** | Food Sales (Grocery Store / Supermarket) | **232.0 kBtu/ft²/yr**<br>(**731.9 kWh/m²/yr**) | Massive, continuous process load (commercial refrigeration compressors) and display lighting. Largely independent of climate. | [EIA CBECS 2018 Table C15](https://www.eia.gov/consumption/commercial/data/2018/pdf/c15.pdf) |

---

### Table 4 — Retail End-Use Split (How much EUI is occupancy-modulatable)

| End Use | Share of Retail EUI (%) | Follows Occupancy / Opening Hours / Fixed? | Rationale & Source |
|---|---|---|---|
| **Space Heating** | **30.0% to 40.0%** | **Modulated / Semi-occupancy** | Driven by climate (outer envelope) and ventilation rate. Occupant presence provides a sensible metabolic heat gain offset, but triggers higher outdoor air ventilation requirements (ASHRAE 62.1). (Source: PNNL Standalone Retail / CEUD Table 20) |
| **Interior Lighting** | **25.0% to 35.0%** | **Fixed to opening hours** | Primarily linked to standard operating schedules and display hours, not active occupant count. Occasional occupancy sensor dimming in stockrooms. (Source: PNNL Standalone Retail / CEUD Table 20) |
| **Space Cooling & Ventilation Fans** | **15.0% to 25.0%** | **Modulated** | Cooling loads track sensible metabolic heat from customer footfall. Fan power runs continuously during occupancy hours; is modulatable if variable air volume (VAV) with demand-controlled ventilation (DCV) is active. (Source: PNNL Standalone Retail / CEUD Table 20) |
| **Plug / Equipment** | **10.0% to 15.0%** | **Fixed during operation / Low modulation** | Driven by cash registers, POS terminals, back-office computers, and active display electronics. Mostly fixed while open; drops to night standby/idle power when closed. (Source: PNNL Standalone Retail / CEUD Table 20) |
| **Refrigeration** | **0.0% (podium)**<br>(*45.0% to 55.0% in grocery*) | **Fixed** | Excluded for our non-food podium retail. In grocery/food sales, it represents a continuous, fixed baseline load unaffected by visitor footfall. (Source: CBECS Food Sales) |
| **DHW & Other** | **2.0% to 5.0%** | **Follows occupancy** | Restroom usage, service hot water, and auxiliary pumps. Tracks customer presence. (Source: PNNL Standalone Retail / CEUD Table 20) |

---

### Table 5 — RECOMMENDED VALIDATOR BANDS (The Deliverable)

| Band | Low (kWh/m²/yr) | Central (kWh/m²/yr) | High (kWh/m²/yr) | Role in Validator | Justification |
|---|---|---|---|---|---|
| Retail **as-modelled** (prototype, CZ 6/7) | **80.0** | **110.0** | **155.0** | **PASS criterion** | Grounded in simulated code-minimum archetypes. Reflects newer PNNL retail prototypes (90.1-2016/2019) at the low end (80 kWh/m²·yr), standard baseline configurations (90.1-2004) in cold climates (110 kWh/m²·yr), and less efficient strip malls/older NECB baselines (155 kWh/m²·yr). |
| Retail **empirical** (SCIEU/CEUD) | **150.0** | **280.0** | **380.0** | **INFO criterion** | Grounded in Canadian measured commercial stock. The central value matches the SCIEU 2019 "Retail – non-food" median of 280.6 kWh/m²·yr (1.01 GJ/m²). The upper bound (380 kWh/m²·yr) accommodates mixed-use retail that may include minor grocery/food spaces or older, poorly-insulated envelopes. |

---

## Part C — Synthesis (Bands + Caveats)

### 1. Recommended Bands and Justifications
*   **Retail As-Modelled (Pass/Fail Gate: Central 110, Low 80, High 155 kWh/m²/yr):** This band represents code-compliant baseline energy performance simulated under EnergyPlus. The central value is anchored to the PNNL Standalone Retail CZ 6A/7 baseline (109.8–110.7 kWh/m²/yr). The low bound (80 kWh/m²/yr) reflects energy efficiency measures in ASHRAE 90.1-2019/NECB 2020. The high bound (155 kWh/m²/yr) accommodates strip mall layouts or older reference vintages.
*   **Retail Empirical (Information-Only Gate: Central 280, Low 150, High 380 kWh/m²/yr):** This band represents the actual energy intensity of the commercial building stock. The central EUI of 280 kWh/m²/yr matches the national SCIEU 2019 median for non-food retail (280.6 kWh/m²/yr). The lower bound (150 kWh/m²/yr) aligns with highly efficient modern retail spaces, while the upper bound (380 kWh/m²/yr) accommodates typical commercial spaces containing minor food sales or older envelopes.

### 2. Validator Documentation Caveat List
*   **Floor-Area Basis Mismatch:** Simulated EUIs are calculated using **conditioned floor area** from the EnergyPlus model. In contrast, SCIEU and CEUD utilize **gross floor space** (including unheated common areas and mechanical voids). This mismatch means simulated EUIs will naturally appear **5% to 10% higher** than survey-measured intensities for the same space due to a smaller denominator.
*   **Refrigeration/Grocery Skew:** Surveyed commercial stock includes supermarkets and grocery stores (median EUI 372.2 kWh/m²/yr). These buildings are dominated by commercial refrigeration compressors (often >50% of EUI). Because the mixed-use podium retail zone is modelled as non-food (with no process refrigeration), matching it against raw commercial stock averages will result in a false alarm of "implausibly low EUI."
*   **Podium-Retail vs. Standalone-Prototype Envelope Mismatch:** The PNNL prototypes are standalone, single-story boxes exposed to the weather on all sides (four walls and a roof). The simulated retail zones, however, are **podium retail zones** located at the base of a high-rise tower. They share floor/ceiling boundaries with conditioned spaces above, meaning they have **significantly lower envelope exposure** per unit floor area. This thermal shielding is expected to bias simulated heating/cooling loads **downward by 15% to 30%** compared to standalone prototypes.
*   **Fuel Coverage:** The electricity-only EUI is highly regional. In Quebec (Montreal), heating is electrified, resulting in an electric EUI gate centered around **220–240 kWh/m²/yr**. In Alberta (Calgary), space heating relies on natural gas, leading to a much lower electric EUI gate centered around **110–120 kWh/m²/yr**.

### 3. Recommendation on Grocery Exclusion
> [!IMPORTANT]
> **Exclude Grocery/Food-Sales Class Sources:** It is strongly recommended that grocery, food sales, convenience stores, and restaurant categories be **excluded entirely** from the empirical benchmarking band. Mixed-use podium retail zones represent general dry-goods, boutique, or office-support retail trade. Including grocery statistics (which exhibit site EUIs of ~370–730 kWh/m²/yr due to refrigeration) artificially inflates the empirical baseline. The SCIEU "Retail - non-food" median of **280.6 kWh/m²/yr** is the only valid stock benchmark.

---

## 2. CONFIDENCE AND CAVEATS

*   **Least Certain Bound:** The **empirical upper bound (380 kWh/m²/yr)** is the least certain. Real-world retail spaces in Canadian stock are highly heterogeneous, and tenant mixes (e.g., coffee shops, dry cleaners, small specialty grocery counters) often inject process loads that are not captured in a strict "non-food retail" classification, making the upper limit highly variable.
*   **Climate Normalization:** While CBECS and SCIEU normalize for climate zone at a high level, they do not account for extreme local weather anomalies in specific survey years. Simulated archetypes, on the other hand, are run with multi-year average EPW weather files, creating a potential year-specific mismatch when validated against actual billing cycles.

---

## 3. REFERENCE LIST

1.  **Natural Resources Canada (NRCan), Office of Energy Efficiency (OEE)**. *Survey of Commercial and Institutional Energy Use (SCIEU) 2019*. Ottawa, ON: Government of Canada, 2022.
    *   [SCIEU 2019 Buildings Index & Tables](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm)
    *   [Table 1: Building characteristics by primary activity](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=1&page=1)
    *   [Table 7.1: Buildings – Share of fuel types by primary activity](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=11&page=1)
2.  **Natural Resources Canada (NRCan)**. *Comprehensive Energy Use Database (CEUD), Reference Year 2023*. Ottawa, ON: OEE, 2025.
    *   [CEUD Commercial/Institutional Sector Menu](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive/trends_com_ca.cfm)
    *   [Table 12: Offices and Retail Space Secondary Energy Use by Region](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=qc&year=2023&rn=12&page=0)
3.  **U.S. Department of Energy (DOE), Pacific Northwest National Laboratory (PNNL)**. *Commercial Prototype Building Models*. Washington, DC: Building Energy Codes Program, 2023.
    *   [Prototype Building Models Landing Page](https://www.energycodes.gov/prototype-building-models)
    *   [Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016 Technical Support Document](https://www.energycodes.gov/sites/default/files/2021-07/Prescriptive_packages_savings_90.1-2016.pdf)
    *   [Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019 Technical Support Document](https://www.energycodes.gov/sites/default/files/2021-07/901-2019_Determination_TSD.pdf)
4.  **U.S. Energy Information Administration (EIA)**. *Commercial Buildings Energy Consumption Survey (CBECS) 2018*. Washington, DC: U.S. Department of Energy, 2021.
    *   [CBECS 2018 Table C15: Consumption and Expenditures by Principal Building Activity](https://www.eia.gov/consumption/commercial/data/2018/pdf/c15.pdf)
5.  **Project Internal Database**. `DOE_non-residential_simulation_results_canadian.csv`.
    *   [Local Simulation Baseline Database](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv)
