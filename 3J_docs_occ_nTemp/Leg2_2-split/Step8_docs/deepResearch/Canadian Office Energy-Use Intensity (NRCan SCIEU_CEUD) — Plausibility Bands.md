# Canadian Office Energy-Use Intensity (NRCan SCIEU_CEUD) — Plausibility Bands

## TL;DR
- **Use these NRCan SCIEU-2019 national office intensities as central plausibility bands:** Non-medical offices **1.05 GJ/m² (291.7 kWh/m²)**; medical offices **0.91 GJ/m² (252.8 kWh/m²)** — total all-fuels (Table 1).
- **Large and high-rise offices exhibit lower intensities:** SCIEU buildings over 200,000 sq. ft. average **0.83 GJ/m² (230.6 kWh/m²)** (Table 17.1), and buildings with 10 or more floors average **0.82 GJ/m² (227.8 kWh/m²)** (Table 19).
- **Electricity-only intensities (calculated from Table 7.1 fuel shares):** Non-medical offices average **0.51 GJ/m² (141.4 kWh/m²)** (46.3% of total energy); medical offices average **0.27 GJ/m² (75.0 kWh/m²)** (29.7% of total energy).
- **NRCan CEUD 2023 provincial tables show wide regional spreads:** Total office EUI ranges from **0.86 to 1.86 GJ/m² (238.9 to 516.7 kWh/m²)**, while electricity-only EUI ranges from **0.48 to 0.84 GJ/m² (133.6 to 232.6 kWh/m²)**. This is driven by Quebec's high electricity fraction (77.0% electric heating) vs. Alberta's low electricity fraction (29.9% electric, relying heavily on natural gas at 1.06 GJ/m²).

## Key Findings

Natural Resources Canada (NRCan) provides two independent and complementary datasets to benchmark office and commercial building energy use:

1. **Survey of Commercial and Institutional Energy Use (SCIEU) 2019** — Primary survey-measured dataset based on a sample of 2019 building energy consumption. It provides detailed breakouts by building size class, floor count, year of construction (vintage), and primary fuel types. This is the primary source for building-level EUI bands.
2. **Comprehensive Energy Use Database (CEUD), reference year 2023** — Modeled stock-level dataset that accounts for annual energy consumption and floor space projections. It provides provincial and regional breakdowns of total energy, floor space, and end-uses for the "Offices" activity type.

### Floor-Area Basis
Unlike the residential SHEU database (which reports EUI per heated area excluding basements and garages), both commercial SCIEU and CEUD report energy intensities based on **gross floor space** (the total area enclosed by exterior walls including basements, common areas, mechanical rooms, and hallways, but typically excluding unheated indoor parking).

## Details

### 1. SCIEU 2019 primary building-level statistics (national)

#### Table 1.1 — Overall Office Intensities by Primary Activity (SCIEU Table 1)
| Primary Activity | Floor Space (M m²) | Energy Use (PJ) | Total EUI (GJ/m²) | Total EUI (kWh/m²) | Implied Electric EUI (GJ/m² → kWh/m²) |
|---|---|---|---|---|---|
| Office space – excluding medical | 101.5 | 111.7 | 1.05 [A] | 291.7 | 0.51 → 141.4 |
| Office space – medical | 15.2 | 8.9 | 0.91 [A] | 252.8 | 0.27 → 75.0 |

**Conversions & Derivations** (1 GJ = 277.78 kWh): 
- Non-medical total: 1.05 × 277.78 = 291.67 kWh/m². 
- Medical total: 0.91 × 277.78 = 252.78 kWh/m².
- Implied Electric EUI (Non-medical): Derived from Table 7.1 fuel consumption (51.7 PJ electricity ÷ 101.5 M m² floor space) = 0.509 GJ/m² × 277.78 = 141.49 kWh/m².
- Implied Electric EUI (Medical): Derived from Table 7.1 fuel consumption (4.1 PJ electricity ÷ 15.2 M m² floor space) = 0.270 GJ/m² × 277.78 = 74.91 kWh/m².

#### Table 1.2 — EUI by Building Size Class for Non-Medical Offices (SCIEU Table 17.1)
| Building Size Class | Building Count | Floor Space (M m²) | Energy Use (PJ) | EUI (GJ/m²) | EUI (kWh/m²) |
|---|---|---|---|---|---|
| 5,000 sq. ft. or less (≤465 m²) | 49,330 [A] | 10.7 [A] | 10.6 [A] | 1.03 | 286.1 |
| 5,001 to 10,000 sq. ft. (466 to 929 m²) | 11,239 [A] | 7.4 [A] | 7.1 [A] | 0.97 | 269.4 |
| 10,001 to 50,000 sq. ft. (930 to 4,645 m²) | 14,028 [A] | 29.4 [A] | 32.4 [A] | 1.05 | 291.7 |
| 50,001 to 200,000 sq. ft. (4,646 to 18,580 m²) | 3,463 [B] | 26.3 [A] | 38.4 [F] | 1.71 | 475.0 |
| Over 200,000 sq. ft. (>18,580 m²) | 694 [B] | 27.8 [C] | 23.1 [C] | 0.83 | 230.6 |

**Conversions:** 1.03 × 277.78 = 286.11; 0.97 × 277.78 = 269.45; 1.05 × 277.78 = 291.67; 1.71 × 277.78 = 474.99; 0.83 × 277.78 = 230.56.
*Note: The EUI for the 50,001 to 200,000 sq. ft. class is anomalously high (1.71 GJ/m²), which is driven by a data-quality flag of **F** (unreliable) on its underlying energy consumption; it should be treated as soft.*

#### Table 1.3 — EUI by Number of Floors for Non-Medical Offices (SCIEU Table 19)
| Number of Floors | Building Count | Floor Space (M m²) | Energy Use (PJ) | EUI (GJ/m²) | EUI (kWh/m²) |
|---|---|---|---|---|---|
| 1 floor | 25,670 [A] | 10.4 [A] | 12.0 [A] | 1.24 | 344.4 |
| 2 floors | 25,674 [A] | 21.3 [A] | 22.0 [B] | 0.92 | 255.6 |
| 3 floors | 5,494 [A] | 12.4 [B] | 28.5 [F] | 1.82 | 505.6 |
| 4 to 9 floors | 2,770 [B] | 12.9 [B] | 14.3 [B] | 1.08 | 300.0 |
| 10 or more floors | 587 [B] | 13.0 [F] | 13.3 [F] | 0.82 | 227.8 |
| Not available / Unclassified | 18,558 [A] | 31.5 [B] | 21.7 [B] | 0.75 | 208.3 |

**Conversions:** 1.24 × 277.78 = 344.45; 0.92 × 277.78 = 255.56; 1.82 × 277.78 = 505.56; 1.08 × 277.78 = 300.00; 0.82 × 277.78 = 227.78; 0.75 × 277.78 = 208.34.
*Note: The "10 or more floors" category EUI of 0.82 GJ/m² (227.8 kWh/m²) is a key reference for high-rise prototypes, but is flagged **F** for both floor space and energy use; it must be treated as soft.*

#### Table 1.4 — EUI by Year of Construction/Vintage for Non-Medical Offices (SCIEU Table 18.1)
| Construction Vintage | Building Count | Floor Space (M m²) | Energy Use (PJ) | EUI (GJ/m²) | EUI (kWh/m²) |
|---|---|---|---|---|---|
| Before 1920 | 5,223 [B] | 3.5 [A] | 3.0 [B] | 0.87 | 241.7 |
| 1920 to 1959 | 8,537 [A] | 8.1 [B] | 6.4 [A] | 1.02 | 283.3 |
| 1960 to 1969 | 7,616 [C] | 8.4 [C] | 25.0 [F] | 1.34 | 372.2 |
| 1970 to 1979 | 11,220 [A] | 10.7 [A] | 16.1 [C] | 1.78 | 494.5 |
| 1980 to 1989 | 11,611 [B] | 17.0 [C] | 18.8 [C] | 1.10 | 305.6 |
| 1990 to 1999 | 5,609 [A] | 6.7 [C] | 4.9 [B] | 0.85 | 236.1 |
| 2000 to 2009 | 5,667 [C] | 7.8 [B] | 6.6 [B] | 0.79 | 219.4 |
| 2010 or later | 4,335 [A] | 8.5 [B] | 9.6 [C] | 0.84 | 233.3 |
| Not available | 18,937 [A] | 30.8 [B] | 21.1 [B] | 0.73 | 202.8 |

**Conversions:** 0.87 × 277.78 = 241.67; 1.02 × 277.78 = 283.34; 1.34 × 277.78 = 372.23; 1.78 × 277.78 = 494.45; 1.10 × 277.78 = 305.56; 0.85 × 277.78 = 236.11; 0.79 × 277.78 = 219.45; 0.84 × 277.78 = 233.34; 0.73 × 277.78 = 202.78.

---

### 2. CEUD 2023 Commercial Sector regional cross-check

#### Table 2.1 — Office Energy Intensity and Fuel Breakdown by Region (Reference Year 2023)
The following provincial and national indicators are extracted from CEUD Commercial Table 19 (Canada) and Table 12 (Provinces/Regions).

| Region / Province | Floor Space (M m²) | Energy Use (PJ) | Total EUI (GJ/m²) | Total EUI (kWh/m²) | Electricity Use (PJ) | Electricity EUI (GJ/m²) | Electricity EUI (kWh/m²) | Electricity Fraction |
|---|---|---|---|---|---|---|---|---|
| **Canada** | 313.48 | 387.7 | 1.24 | 344.4 | 189.8 | 0.61 | 168.2 | 49.0% |
| **Atlantic** | 18.38 | 15.8 | 0.86 | 238.9 | 9.0 | 0.49 | 136.0 | 57.0% |
| **Quebec** | 62.58 | 68.0 | 1.09 | 302.8 | 52.4 | 0.84 | 232.6 | 77.0% |
| **Ontario** | 129.49 | 164.9 | 1.27 | 352.8 | 73.7 | 0.57 | 158.1 | 44.7% |
| **Manitoba** | 10.89 | 16.3 | 1.50 | 416.7 | 7.2 | 0.66 | 183.6 | 44.4% |
| **Saskatchewan** | 8.25 | 15.4 | 1.86 | 516.7 | 6.2 | 0.75 | 208.8 | 40.2% |
| **Alberta** | 43.25 | 69.4 | 1.61 | 447.2 | 20.8 | 0.48 | 133.6 | 29.9% |
| **BC & Territories** | 40.65 | 37.9 | 0.93 | 258.3 | 20.5 | 0.50 | 140.1 | 54.1% |

**Conversions & Arithmetic Checks (Reference Year 2023):**
- **Canada:** 387.7 PJ ÷ 313.48 M m² = 1.2367 ≈ 1.24 GJ/m²; 1.24 × 277.78 = 344.45 kWh/m². Electric EUI: 189.8 PJ ÷ 313.48 M m² = 0.6054 GJ/m² × 277.78 = 168.18 kWh/m².
- **Atlantic:** 15.8 PJ ÷ 18.38 M m² = 0.8596 ≈ 0.86 GJ/m²; 0.86 × 277.78 = 238.89 kWh/m². Electric EUI: 9.0 PJ ÷ 18.38 M m² = 0.4897 GJ/m² × 277.78 = 136.02 kWh/m².
- **Quebec:** 68.0 PJ ÷ 62.58 M m² = 1.0866 ≈ 1.09 GJ/m²; 1.09 × 277.78 = 302.78 kWh/m². Electric EUI: 52.4 PJ ÷ 62.58 M m² = 0.8373 GJ/m² × 277.78 = 232.59 kWh/m².
- **Ontario:** 164.9 PJ ÷ 129.49 M m² = 1.2734 ≈ 1.27 GJ/m²; 1.27 × 277.78 = 352.78 kWh/m². Electric EUI: 73.7 PJ ÷ 129.49 M m² = 0.5691 GJ/m² × 277.78 = 158.10 kWh/m².
- **Manitoba:** 16.3 PJ ÷ 10.89 M m² = 1.4968 ≈ 1.50 GJ/m²; 1.50 × 277.78 = 416.67 kWh/m². Electric EUI: 7.2 PJ ÷ 10.89 M m² = 0.6611 GJ/m² × 277.78 = 183.65 kWh/m².
- **Saskatchewan:** 15.4 PJ ÷ 8.25 M m² = 1.8667 ≈ 1.86 GJ/m²; 1.86 × 277.78 = 516.67 kWh/m². Electric EUI: 6.2 PJ ÷ 8.25 M m² = 0.7515 GJ/m² × 277.78 = 208.75 kWh/m².
- **Alberta:** 69.4 PJ ÷ 43.25 M m² = 1.6046 ≈ 1.61 GJ/m²; 1.61 × 277.78 = 447.23 kWh/m². Electric EUI: 20.8 PJ ÷ 43.25 M m² = 0.4809 GJ/m² × 277.78 = 133.59 kWh/m².
- **BC & Territories:** 37.9 PJ ÷ 40.65 M m² = 0.9323 ≈ 0.93 GJ/m²; 0.93 × 277.78 = 258.34 kWh/m². Electric EUI: 20.5 PJ ÷ 40.65 M m² = 0.5043 GJ/m² × 277.78 = 140.08 kWh/m².

- **SCIEU 2019 Regional Data: `NOT FOUND`**  
SCIEU 2019 reports regional statistics only at highly aggregated levels or does not publish them for specific commercial building subcategories due to pandemic-related non-response and sample size limitations. Therefore, CEUD provincial tables are used as the primary source for regional spreads.

---

## Interpretation for simulation plausibility bands

- **Central Expectation:** An average Canadian office building has an empirical all-fuels EUI of **290 to 345 kWh/m²·yr** on a gross floor-space basis. However, because simulation models are evaluated on **conditioned floor area**, simulated EUI will scale higher if the model includes significant unconditioned/unheated basements or parking structures that are excluded from the denominator.
- **Large and High-Rise Scaling:** Large high-rise office models (similar to the DOE/PNNL Tall and SuperTall models with 10+ floors and >200,000 sq. ft.) should benchmark against the lower bins in SCIEU. The measured EUI for high-rise office stock drops to **0.82–0.83 GJ/m² (227.8–230.6 kWh/m²·yr)**. This reflects greater volume-to-envelope ratios and more centralized HVAC systems.
- **Fuel and Technology Spreads:** The electricity-only EUI is highly dependent on region:
  - In **Quebec**, offices average **77.0% electricity** (resulting in an electric EUI of **232.6 kWh/m²·yr**) due to widespread electric resistance or heat-pump space heating.
  - In **Alberta**, offices average only **29.9% electricity** (an electric EUI of **133.6 kWh/m²·yr**) because they rely heavily on natural gas for space heating, which accounts for **1.06 GJ/m² (294.2 kWh/m²·yr)** of gas EUI.
  - In **Ontario**, offices sit in the middle with a **44.7% electricity share** (electric EUI of **158.1 kWh/m²·yr**) and **52.1% natural gas share** (gas EUI of **184.3 kWh/m²·yr**).

---

## Recommendations

1. **Adopt size-adjusted thresholds for high-rise prototypes:** Rather than using the overall commercial stock average (~290–345 kWh/m²·yr), set the baseline central EUI gate for Tall and SuperTall prototypes to **230 kWh/m²·yr** to match the SCIEU large-building and 10+ floors bins.
2. **Implement climate-zone/provincial matching for the electricity gate:** Do not apply a single national electricity EUI gate.
   - For Quebec (Montréal), use a high electric EUI gate centered around **230 kWh/m²·yr**.
   - For Alberta (Calgary) and BC (Kelowna/Vancouver), use a lower electric EUI gate centered around **130–140 kWh/m²·yr**.
   - For Ontario (Toronto) and Manitoba (Winnipeg), use a medium electric EUI gate centered around **160–180 kWh/m²·yr**.
3. **Map the Plausibility Gate thresholds:**
   
   #### Recommended Total Site EUI Band (All-Fuels)
   - **Central Baseline:** **230 kWh/m²·yr**
   - **Plausibility Gate Range (Pass/Fail):** **170 to 360 kWh/m²·yr** (allows for a -25% to +55% buffer to accommodate different envelope and occupancy schedule combinations).

   #### Recommended Electricity-Only EUI Band
   - **Quebec (Montréal):** Central **230 kWh/m²·yr** | Gate Range: **170 to 300 kWh/m²·yr**
   - **Ontario & Prairies (Toronto, Winnipeg, Regina):** Central **170 kWh/m²·yr** | Gate Range: **120 to 230 kWh/m²·yr**
   - **Alberta (Calgary):** Central **130 kWh/m²·yr** | Gate Range: **90 to 180 kWh/m²·yr**
   - **British Columbia (Vancouver, Kelowna):** Central **140 kWh/m²·yr** | Gate Range: **100 to 200 kWh/m²·yr**

4. **Reconcile Denominators:** If the EnergyPlus model includes unconditioned basements in the floor area calculation, simulated intensities will appear artificially lower. Standardize simulated EUI using conditioned floor area and apply a +5% to +10% adjustment when comparing to these gross-area-based stock averages.

---

## Caveats

- **Measured vs. Modeled:** SCIEU is based on empirical billing data and building surveys, which capture real operational anomalies, plug loads, and system degradation. Simulation models represent idealized design schedules and may underpredict actual energy consumption unless plug loads and infiltration are fully calibrated.
- **Data-Quality Flags:** Several critical categories in SCIEU (such as energy consumption in offices of 10+ floors and offices of 50k–200k sq. ft.) carry quality flags of **F** (unreliable). While they are the best available public data, they should be treated as guidelines rather than rigid physical constraints.
- **Vintage Bias:** The stock average includes a large proportion of older, uninsulated commercial buildings. Newer offices constructed to NECB 2011/2015/2020 or ASHRAE 90.1-2013/2016/2019 codes are expected to sit near or below the lower bound of the plausibility range.
- **Site vs. Source:** All intensities in this document represent **site (secondary) energy** delivered to the building boundary. Do not compare these numbers to ENERGY STAR Portfolio Manager source EUI metrics, which scale electric consumption by a factor of 1.96 to account for generation and transmission losses.

---

## Sources

### 1. SCIEU 2019 (NRCan Office of Energy Efficiency, National Energy Use Database; tables released/modified 2022-08-05)
- **Data Tables Index:** [SCIEU 2019 Buildings Index](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm)
- **Table 1 — Building and Establishment characteristics by primary activity:** [SCIEU 2019 Table 1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=1&page=1)
- **Table 7.1 — Buildings – Share of fuel types by primary activity:** [SCIEU 2019 Table 7.1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=11&page=1)
- **Table 17.1 — Buildings – Characteristics by primary activity and building size:** [SCIEU 2019 Table 17.1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=31&page=1)
- **Table 18.1 — Buildings – Characteristics by primary activity and year of construction:** [SCIEU 2019 Table 18.1](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=33&page=1)
- **Table 19 — Buildings – Characteristics by primary activity and number of floors:** [SCIEU 2019 Table 19](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SC&sector=aaa&juris=ca&year=2019&rn=35&page=1)

### 2. CEUD 2023 (NRCan Comprehensive Energy Use Database, Commercial/Institutional Sector – Reference Year 2023)
- **Database Menu:** [CEUD Commercial Sector Index](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive/trends_com_ca.cfm)
- **Table 19 (Canada) — Offices Secondary Energy Use and GHG Emissions by Energy Source:** [CEUD 2023 Table 19 (Canada)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=ca&year=2023&rn=19&page=0)
- **Table 20 (Canada) — Offices Secondary Energy Use and GHG Emissions by End Use:** [CEUD 2023 Table 20 (Canada)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=ca&year=2023&rn=20&page=0)
- **Table 21 (Canada) — Offices Secondary Energy Use and GHG Emissions by Region – Excluding Electricity-Related Emissions:** [CEUD 2023 Table 21 (Canada)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=ca&year=2023&rn=21&page=0)
- **Table 12 (Provinces) — Offices Secondary Energy Use and GHG Emissions by Energy Source:**
  - **Atlantic:** [CEUD 2023 Table 12 (Atlantic)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=atl&year=2023&rn=12&page=0)
  - **Quebec:** [CEUD 2023 Table 12 (Quebec)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=qc&year=2023&rn=12&page=0)
  - **Ontario:** [CEUD 2023 Table 12 (Ontario)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=on&year=2023&rn=12&page=0)
  - **Manitoba:** [CEUD 2023 Table 12 (Manitoba)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=mb&year=2023&rn=12&page=0)
  - **Saskatchewan:** [CEUD 2023 Table 12 (Saskatchewan)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=sk&year=2023&rn=12&page=0)
  - **Alberta:** [CEUD 2023 Table 12 (Alberta)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=ab&year=2023&rn=12&page=0)
  - **BC & Territories:** [CEUD 2023 Table 12 (BC & Territories)](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=com&juris=bct&year=2023&rn=12&page=0)
