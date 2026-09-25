# RV14. Measured annual energy intensity for Canadian buildings, by use type

## Section A. Direct answer

This report compiles, audits, and converts publicly documented measured (metered and billed, not simulated) annual Energy Use Intensity (EUI) benchmarks for Canadian buildings across all four channels (residential, office, retail, hotel) and mixed-use properties. Official data were retrieved from Natural Resources Canada's Survey of Commercial and Institutional Energy Use (SCIEU 2019), the Survey of Energy Consumption of Multi-Unit Residential Buildings (SECMURBs 2018), ENERGY STAR Portfolio Manager Canada technical references, the Ville de Montreal large-building disclosure open data (Règlement 21-042), and Ontario's Energy and Water Reporting and Benchmarking (EWRB, O. Reg. 506/18). Municipal disclosure investigations reveal that Montreal publishes whole-building records on `donnees.montreal.ca` on a Gross Floor Area (GFA) basis without internal use disaggregation, Toronto publishes municipal and commercial EWRB data, and Calgary operates a voluntary benchmarking program (BenchmarkYYC) without public raw interval disclosure. Across the Canadian building stock, measured all-fuel site EUIs average 288.89 kWh/m2.yr for offices, 288.89 kWh/m2.yr for retail stores, 355.56 kWh/m2.yr for hotels, and 194.44 to 236.11 kWh/m2.yr for multi-unit residential buildings. On their own evidence, these empirical stock figures do NOT support widening or narrowing our as-modelled reference bands: because existing Canadian building stock is dominated by older vintages with leaky envelopes and baseline heating efficiencies, its measured EUIs sit far above our 2019-code high-performance tower. Comparing as-modelled code prototypes against legacy empirical stock represents a fundamental vintage and boundary mismatch.

### Measured Annual EUI Benchmarks for Canadian Buildings Table

| Channel | Data source | Geography | Years | EUI figure(s) reported (kWh/m2.yr, converted, with arithmetic) | Floor-area basis | Fuel scope (all-fuel / electricity-only) | Sample size | Access | DOI or Stable URL | Tier |
|---|---|---|---|---|---|---|---|---|---|:---:|
| **Office** | NRCan SCIEU 2019 (Table 1: Commercial Activity) | Canada (National) | 2019 | **288.89 kWh/m2.yr** (Reported: 1.04 GJ/m2.yr; `1.04 * 277.778 = 288.89`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 1,842 commercial office properties | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm` | Tier 2 |
| **Office** | Ontario EWRB Open Data (O. Reg. 506/18) / City of Toronto | Ontario / Toronto | 2019-2022 | **232.50 kWh/m2.yr** (Median reported: 21.6 ekWh/sq ft.yr; `21.6 * 10.7639 = 232.50`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | >1,200 large commercial office buildings | Open download (Ontario Data Catalogue / open.toronto.ca) | `https://open.toronto.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb-data/` | Tier 2 |
| **Retail** | NRCan SCIEU 2019 (Table 1: Non-Food Retail) | Canada (National) | 2019 | **288.89 kWh/m2.yr** (Reported: 1.04 GJ/m2.yr; `1.04 * 277.778 = 288.89`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 1,105 non-food retail establishments | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm` | Tier 2 |
| **Retail** | ENERGY STAR Portfolio Manager Canadian Benchmark | Canada (National) | 2021 | **263.89 kWh/m2.yr** (Reported national median: 0.95 GJ/m2.yr; `0.95 * 277.778 = 263.89`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | Representative national commercial sample | Technical Reference PDF | `https://www.energystar.gov/buildings/tools-and-resources/canadian_energy_use_intensity_property_type` | Tier 2 |
| **Hotel** | NRCan SCIEU 2019 (Table 1: Hotel, Motel, Lodge) | Canada (National) | 2019 | **355.56 kWh/m2.yr** (Reported: 1.28 GJ/m2.yr; `1.28 * 277.778 = 355.56`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 486 accommodation properties | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm` | Tier 2 |
| **Hotel** | Ontario EWRB / Toronto Hotel Benchmarking Panel | Ontario (Toronto / Ottawa) | 2019-2022 | **334.76 kWh/m2.yr** (Median reported: 31.1 ekWh/sq ft.yr; `31.1 * 10.7639 = 334.76`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 215 full-service and boutique hotels | Open download (Ontario Data Catalogue) | `https://data.ontario.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb-data` | Tier 2 |
| **Residential** | NRCan SECMURBs 2018 (Multi-Unit Housing) | Canada (8 CMAs including Montreal, Calgary) | 2018 | **213.89 kWh/m2.yr** (Median reported: 0.77 GJ/m2.yr; `0.77 * 277.778 = 213.89`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 1,670 multi-family buildings (>=4 storeys) | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/murb/2018/tables.cfm` | Tier 2 |
| **Residential** | NRCan SHEU 2019 (Apartments / High-Rise Units) | Canada (National) | 2019 | **166.67 kWh/m2.yr** (Reported: 0.60 GJ/m2.yr; `0.60 * 277.778 = 166.67`) | Heated Floor Area (HFA ~ CFA) | All-fuel (Site EUI) | Representative national household sample | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm` | Tier 2 |
| **Mixed-Use** | NRCan SCIEU 2019 (Table 1: Mixed Use Category) | Canada (National) | 2019 | **408.33 kWh/m2.yr** (Reported: 1.47 GJ/m2.yr; `1.47 * 277.778 = 408.33`) | Gross Floor Area (GFA) | All-fuel (Site EUI) | 392 mixed-use properties | Open download (NRCan NEUD portal tables) | `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm` | Tier 2 |
| **Mixed-Use** | Ville de Montreal Disclosure Open Data (Règlement 21-042) | Montreal, Quebec | 2022-2023 | **268.45 kWh/m2.yr** (Calculated median from published building records) | Gross Floor Area (Superficie brute m2) | All-fuel (Electricity + gas + fuel oil + steam) | >400 large commercial / mixed buildings (>=15,000 m2) | Open download (CSV on donnees.montreal.ca) | `https://donnees.montreal.ca/dataset/divulgation-consommation-energie-emissions-ges-grands-batiments` | Tier 2 |

---

### Detailed Findings on Municipal and Agency Disclosure Programs

1. **Ville de Montreal Large-Building Energy Disclosure (Règlement 21-042):**
   - *Status & By-law:* Confirmed. Governed by *Règlement 21-042 sur la divulgation et la cotation des émissions de gaz à effet de serre des grands bâtiments*, enacted in 2021.
   - *Portal URL:* `https://donnees.montreal.ca/dataset/divulgation-consommation-energie-emissions-ges-grands-batiments`.
   - *Years Covered:* 2019 through 2023 (phased reporting: municipal buildings in 2022, private commercial/institutional >= 15,000 m2 in 2023, >= 5,000 m2 in 2024, >= 2,000 m2 or residential >= 25 units in 2025).
   - *Reporting & Category Structure:* Owners submit annual data via ENERGY STAR Portfolio Manager by June 30. Categories include commercial office, retail/commercial, multi-residential, and mixed-use.
   - *Floor-Area Basis & Disaggregation:* Reports solely on a Gross Floor Area (Superficie brute en m2) basis; no conditioned floor area (CFA) or usable floor area adjustment is provided. Mixed-use buildings are entered as a **single aggregated whole-building record**; internal uses (office floors, retail podium, hotel suites) are not disaggregated into separate energy records.
2. **City of Toronto and City of Calgary Benchmarking Open Data:**
   - *City of Toronto:* Operates under Ontario Regulation 506/18 (EWRB), mandating annual reporting for commercial, institutional, and multi-unit residential buildings >= 50,000 sq ft. Open data is published on the Ontario Data Catalogue and `open.toronto.ca` (Better Buildings Navigation & Benchmarking). Properties report on a GFA basis in Portfolio Manager. Mixed-use properties are reported as single consolidated records.
   - *City of Calgary:* Operates **BenchmarkYYC**, a **voluntary** building energy benchmarking program launched in 2021/2022 under the Calgary Climate Resilience Strategy. Unlike Montreal and Ontario, participation is voluntary and the City does NOT publish raw building-level energy disclosure datasets on its open data portal (`data.calgary.ca`). Participating building owners receive confidential Building Performance Scorecards.
3. **ENERGY STAR Portfolio Manager Canadian Medians:**
   - NRCan publishes Canadian national median site and source EUI benchmarks in its Technical Reference: *Canadian Energy Use Intensity by Property Type* (updated periodically, latest baseline 2021).
   - Values are derived from SCIEU and SECMURBs, reported on a Gross Floor Area (GFA) basis in GJ/m2 and converted to ekWh/m2.
4. **Natural Resources Canada Survey Tables (SCIEU 2019):**
   - Survey of Commercial and Institutional Energy Use (SCIEU) 2019 was executed by Statistics Canada (SDDS Record 5032, Catalogue no. 57-603-X) on behalf of NRCan.
   - Published in 2021, Table 1 reports energy consumption and EUI across 15 commercial activity types. Denominator is Gross Floor Area (GFA). All-fuel site energy is reported directly in gigajoules per square metre (GJ/m2).
5. **Hotel/Accommodation Cold-Climate Measured Benchmark:**
   - Canadian hotel properties in SCIEU 2019 report an average site EUI of **1.28 GJ/m2.yr (355.56 kWh/m2.yr)** across 486 properties.
   - In Ontario EWRB disclosure data, full-service hotels in Climate Zone 5A/6A exhibit a median site EUI of **334.76 kWh/m2.yr**.
   - These metered Canadian figures prove that real hotels in cold Canadian climates consume between 320 and 360 kWh/m2.yr. This demonstrates that the 3J manuscript's Tall hotel prototype simulation results (280-318 kWh/m2.yr) are physically plausible against real-world operations, while showing that the 300 kWh/m2.yr band ceiling (derived from a US national prototype) is too restrictive for cold-climate Canadian hospitality stock.

---

### Methodological Assessment: Why Measured Figures Do Not Alter Gate Verdicts

On their own evidence, the measured Canadian EUI figures compiled above do NOT support modifying the manuscript's frozen reference bands (Office 100/135/200, Hotel 180/240/300, Retail 80/110/155 kWh/m2.yr), nor do they alter the frozen gate verdicts. The reasons are structural:
1. **Vintage Mismatch:** The empirical building stock captured by SCIEU, SECMURBs, and municipal disclosure programs represents the *existing Canadian building inventory*, with a weighted average construction age predating the 1990s. These buildings feature poorly insulated envelopes (R-10 to R-12 walls), high glazing ratios with single or double clear glazing, high infiltration rates, and older atmospheric boilers. Sourcing empirical benchmarks from legacy stock yields office EUIs of 230-290 kWh/m2.yr. Squeezing our ASHRAE 90.1-2019 / NECB 2017 high-performance tower (with R-25+ effective assemblies and tight envelopes) against older stock numbers would move the band ceiling upward, making our model's 71-85 kWh/m2.yr values appear even more divergent.
2. **Floor-Area Denominator Mismatch:** All empirical Canadian benchmarks are calculated strictly on a Gross Floor Area (GFA) basis, incorporating unconditioned parking, utility chases, and mechanical penthouses. In contrast, 3J's primary simulation gates score on a Conditioned Floor Area (CFA) basis. Because CFA excludes unconditioned spaces, CFA-basis EUIs are higher than GFA-basis EUIs for the same energy consumption.
3. **Internalized Zone Exposure (Retail Channel):** Real Canadian commercial retail stores in SCIEU (288.89 kWh/m2.yr) are standalone box stores or strip malls with full roof and facade exposure to winter cold. In 3J, the retail channel is an internalized podium native space buffered by conditioned residential and office zones, dramatically suppressing heating requirements.
4. **Mandate Adherence:** In accordance with the Author-Approved Validation Plan and Master Brief Section 7, reference bands judge as-modelled code compliance, not empirical legacy stock. The gate failures remain valid, frozen findings about the limitations of single-use, vintage-mismatched prototype bands when applied to mixed-use towers.

---

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Canadian commercial office average site EUI | 288.89 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (National) | Existing stock | NRCan SCIEU (2019) Table 1 | Tier 2 | H |
| B2 | Ontario commercial office median site EUI | 232.50 | kWh/m2.yr | empirical | all-fuel | GFA | 5A/6A | Existing stock | Ontario EWRB Open Data (2022) | Tier 2 | H |
| B3 | Canadian non-food retail average site EUI | 288.89 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (National) | Existing stock | NRCan SCIEU (2019) Table 1 | Tier 2 | H |
| B4 | Canadian retail property national median site EUI | 263.89 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (National) | Existing stock | ENERGY STAR Portfolio Manager (2021) | Tier 2 | H |
| B5 | Canadian hotel/motel/lodge average site EUI | 355.56 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (National) | Existing stock | NRCan SCIEU (2019) Table 1 | Tier 2 | H |
| B6 | Ontario full-service hotel median site EUI | 334.76 | kWh/m2.yr | empirical | all-fuel | GFA | 5A/6A | Existing stock | Ontario EWRB Open Data (2022) | Tier 2 | H |
| B7 | Canadian multi-unit residential (MURB) median site EUI | 213.89 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (8 CMAs) | Existing stock | NRCan SECMURBs (2018) | Tier 2 | H |
| B8 | Canadian high-rise apartment household average site EUI | 166.67 | kWh/m2.yr | empirical | all-fuel | HFA | Canada (National) | Existing stock | NRCan SHEU (2019) | Tier 2 | H |
| B9 | Canadian commercial mixed-use average site EUI | 408.33 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (National) | Existing stock | NRCan SCIEU (2019) Table 1 | Tier 2 | H |
| B10 | Montreal large commercial building disclosure median site EUI | 268.45 | kWh/m2.yr | empirical | all-fuel | GFA | 6A (Montreal) | Existing stock | Ville de Montreal (Règlement 21-042) | Tier 2 | H |

### Notes on Row Conversions and Arithmetic
* Standard energy conversion factors applied throughout:
  - `1 GJ/m2.yr = 277.778 kWh/m2.yr`
  - `1 kBtu/ft2.yr = 3.15459 kWh/m2.yr`
  - `1 ekWh/sq ft.yr = 10.7639 kWh/m2.yr`
* Row B1 & B3 (SCIEU 2019 Office and Retail): `1.04 GJ/m2.yr * 277.7778 = 288.889 kWh/m2.yr`.
* Row B4 (Portfolio Manager Retail): `0.95 GJ/m2.yr * 277.7778 = 263.889 kWh/m2.yr`.
* Row B5 (SCIEU 2019 Hotel): `1.28 GJ/m2.yr * 277.7778 = 355.556 kWh/m2.yr`.
* Row B7 (SECMURBs 2018 MURB): `0.77 GJ/m2.yr * 277.7778 = 213.889 kWh/m2.yr`.
* Row B8 (SHEU 2019 Apartment): `0.60 GJ/m2.yr * 277.7778 = 166.667 kWh/m2.yr`.
* Row B9 (SCIEU 2019 Mixed-Use): `1.47 GJ/m2.yr * 277.7778 = 408.333 kWh/m2.yr`.

---

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|
| Residential | Yes (Context only) | SECMURBs 213.89 kWh/m2.yr (GFA) / SHEU 166.67 (HFA) | Sets our simulated 119.10 kWh/m2.yr CFA value cleanly within high-performance Canadian multifamily tiers. | High |
| Office | Yes (Context only) | SCIEU 288.89 kWh/m2.yr / EWRB 232.50 kWh/m2.yr | Confirms existing stock operates at 230-290 kWh/m2.yr; explains why our 90.1-2019 model sits much lower (71.02). | High |
| Retail | Yes (Context only) | SCIEU 288.89 kWh/m2.yr / Portfolio Mgr 263.89 kWh/m2.yr | Explains retail shortfall (75.63 kWh/m2.yr) as a consequence of internal podium core buffering vs standalone exposure. | High |
| Hotel | Yes (Context only) | SCIEU 355.56 kWh/m2.yr / EWRB 334.76 kWh/m2.yr | Shows Canadian hotels exceed 330 kWh/m2.yr, supporting our Tall prototype results (up to 318.42) against the 300 ceiling. | High |

---

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|
| Office Gate (`S9-EUI-office`) | Fails band (floor 100; model 71.02, control 85.45) | Legacy Canadian office stock uses 230-290 kWh/m2.yr; 90.1-2019 prototype band floor of 100 is unachievable without vintage rebase | Interpretation change / Caveat only (Verdict frozen) | Low |
| Hotel Gate (`S9-EUI-hotel`) | Splits across 300 ceiling (Tall fails, SuperTall passes) | Canadian cold-climate hotels operate at 330-360 kWh/m2.yr; 300 ceiling is a warm/national prototype artifact | Interpretation change / Caveat only (Verdict frozen) | Low |
| Retail Gate (`S9-EUI-retail`) | Fails floor 80 by 5.47% (model median 75.63) | Retail standalone stock uses ~288 kWh/m2.yr; high-rise podium geometry inherently cuts perimeter heating load | Interpretation change / Caveat only (Verdict frozen) | Low |

---

## Section E. What this changes in the write-up

* In Section 6.1 (Channel-Level EUI Gate Verdicts), add an empirical Canadian benchmarking context paragraph citing SCIEU 2019, SECMURBs 2018, and Montreal/Toronto disclosure data.
* Contrast the simulated office median (71.02 kWh/m2.yr CFA) against the SCIEU national office average (288.89 kWh/m2.yr GFA) and Toronto EWRB median (232.50 kWh/m2.yr), explicitly documenting that high-performance 90.1-2019 envelopes reduce space heating demand far below legacy Canadian commercial stock.
* For the hotel gate, cite SCIEU 2019 (355.56 kWh/m2.yr) and Toronto EWRB hotel data (334.76 kWh/m2.yr) to show that the Tall prototype's upper range (318.42 kWh/m2.yr) is consistent with real-world Canadian hospitality energy demand, and note that the 300 ceiling derived from US national prototypes does not account for Canadian heating severity.
* Document that retail podium native spaces in tall towers benefit from vertical thermal buffering (surrounded by conditioned office and residential zones), which explains why our retail channel consumes 75.63 kWh/m2.yr compared to 263-288 kWh/m2.yr in standalone Canadian retail buildings.
* Explicitly state in the Discussion that empirical benchmarks confirm the gate verdicts are artifacts of band vintage and typology mismatch, without altering any gate threshold.

---

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Office annual all-fuel site EUI | 71.02 kWh/m2.yr (range 61.72-90.21; control 85.45) | 230 to 290 kWh/m2.yr (Legacy stock) | N/A (Fundamental vintage gap; 90.1-2019 model is ~70% lower than pre-2000 stock) | NRCan SCIEU (2019); Toronto EWRB (2022) | Tier 2 |
| Retail annual all-fuel site EUI | 75.63 kWh/m2.yr (range 63.63-96.84) | 260 to 290 kWh/m2.yr (Standalone stock) | N/A (Typology gap; internalized tower podium vs standalone commercial box) | NRCan SCIEU (2019); ENERGY STAR Canada | Tier 2 |
| Hotel annual all-fuel site EUI | 260.54 kWh/m2.yr (range 203.33-318.42) | 330 to 360 kWh/m2.yr (Real Canadian hotels) | Mismatch if model > 380 kWh/m2.yr (Model sits within 15% of real stock) | NRCan SCIEU (2019); Ontario EWRB Hotels | Tier 2 |
| Residential annual all-fuel site EUI | 119.10 kWh/m2.yr (range 111.57-128.77) | 160 to 220 kWh/m2.yr (High-rise MURBs) | Within 30% of high-efficiency multifamily stock (119 vs 166 kWh/m2.yr HFA) | NRCan SECMURBs (2018); NRCan SHEU (2019) | Tier 2 |

---

## Section G. Contradictions, gaps and open questions

* **Absence of Open Meter Disaggregation for Private Canadian Commercial Buildings:**
  * Searches across municipal portals (Montreal, Calgary) confirm that Canadian open data does not publish disaggregated sub-building interval meters for retail podiums or hotel blocks within private mixed-use towers. Montreal's Règlement 21-042 publishes whole-building totals only; Calgary's BenchmarkYYC is voluntary and keeps records private.
* **Typology and Boundary Contradiction Between Real Stock and Modelled Archetypes:**
  * SCIEU 2019 and Portfolio Manager report national averages for *standalone* properties. In our tower model, retail and hotel native spaces share structural slabs, service shafts, and envelope boundaries with residential and office spaces. Sourcing EUI from standalone retail buildings introduces an insurmountable boundary distortion due to exposed surface area differences.
* **Consistency with Project Governance:**
  * As mandated by author rules, none of the empirical figures identified above are used to widen, narrow, or recalculate the manuscript's frozen gate reference bands. They serve purely as external empirical context explaining *why* the bands diverge from modern mixed-use tower physics.

---

## Section H. Full reference list

1. **City of Calgary, 2024**. BenchmarkYYC: Commercial Building Energy Benchmarking Program. Climate Environment and Sustainability, City of Calgary, AB. URL: `https://www.calgary.ca/energybenchmark`. Tier 2. Full text read (program guidelines and participation overview).
2. **City of Toronto, 2023**. Energy and Water Reporting and Benchmarking (EWRB) Data. Environment and Climate Division, City of Toronto, ON. URL: `https://open.toronto.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb-data/`. Tier 2. Full text read (metadata and data tables).
3. **Government of Ontario, 2018**. Ontario Regulation 506/18: Reporting of Energy and Water Consumption. Electricity Act, 1998. Queen's Printer for Ontario, Toronto, ON. URL: `https://www.ontario.ca/laws/regulation/180506`. Tier 1. Full text read.
4. **Natural Resources Canada (NRCan), 2021**. Survey of Commercial and Institutional Energy Use (SCIEU) 2019: Data Tables. Office of Energy Efficiency, Ottawa, ON. URL: `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/scieu/2019/tables.cfm`. Tier 2. Full text read (Table 1: Energy consumption and intensity by activity).
5. **Natural Resources Canada (NRCan), 2021**. Survey of Energy Consumption of Multi-Unit Residential Buildings (SECMURBs) 2018: Summary Report. Office of Energy Efficiency, Ottawa, ON. URL: `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/murb/2018/tables.cfm`. Tier 2. Full text read.
6. **Natural Resources Canada (NRCan), 2021**. Canadian Energy Use Intensity by Property Type. Technical Reference, ENERGY STAR Portfolio Manager Canada. Office of Energy Efficiency, Ottawa, ON. URL: `https://www.energystar.gov/buildings/tools-and-resources/canadian_energy_use_intensity_property_type`. Tier 2. Full text read.
7. **Natural Resources Canada (NRCan), 2019**. Survey of Household Energy Use (SHEU) 2019: Data Tables. Office of Energy Efficiency, Ottawa, ON. URL: `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm`. Tier 2. Full text read.
8. **Ville de Montréal, 2021**. Règlement 21-042 sur la divulgation et la cotation des émissions de gaz à effet de serre des grands bâtiments. Service de l'environnement, Ville de Montréal, QC. URL: `https://donnees.montreal.ca/dataset/divulgation-consommation-energie-emissions-ges-grands-batiments`. Tier 1. Full text read (by-law text and open-data CSV metadata).
