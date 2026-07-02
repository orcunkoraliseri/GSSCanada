# Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL prototypes) — As-Modelled Bands

## TL;DR
- **Use these code-compliant large office baseline site EUIs (all-fuels) for Climate Zones 6 and 7:**
  - **ASHRAE 90.1-2019 (NECB 2020 equivalent): 130.0 to 136.3 kWh/m²·yr (41.2 to 43.2 kBtu/ft²·yr / 0.468 to 0.491 GJ/m²·yr)** (Table 3.1).
  - **ASHRAE 90.1-2016: 136.0 to 142.6 kWh/m²·yr (43.1 to 45.2 kBtu/ft²·yr / 0.490 to 0.513 GJ/m²·yr)** (Table 3.1).
  - **ASHRAE 90.1-2004 Baseline (local CSV dataset): 172.56 to 176.34 kWh/m²·yr (54.7 to 55.9 kBtu/ft²·yr / 0.621 to 0.635 GJ/m²·yr)** (Table 1.1).
- **Electricity-only intensities (gas-heated baseline models):** **60.0 to 80.0 kWh/m²·yr (19.0 to 25.4 kBtu/ft²·yr / 0.216 to 0.288 GJ/m²·yr)** (Table 5.1).
- **End-use splits in cold climates:** Heating dominates at **35% to 45%** of site energy, followed by interior equipment (plug loads) at **18% to 24%**, fans at **12% to 18%**, and interior lighting at **10% to 15%** (Table 4.1).
- **Recommended simulation plausibility bands for CZ 6 and 7:**
  - **Total Site EUI (All-Fuels): 100 to 200 kWh/m²·yr (0.36 to 0.72 GJ/m²·yr)** (Central: **135 kWh/m²·yr**) (Table 7.1).
  - **Electricity-only EUI (Gas Heated): 50 to 90 kWh/m²·yr (0.18 to 0.32 GJ/m²·yr)** (Central: **70 kWh/m²·yr**) (Table 7.1).

---

## Key Findings

Building energy simulations for commercial offices utilize prototype models developed by the Pacific Northwest National Laboratory (PNNL) under the direction of the U.S. Department of Energy (DOE). These prototypes represent standard building shapes, occupancy profiles, and HVAC systems designed to comply with minimum code requirements of various editions of the ASHRAE Standard 90.1 and the National Energy Code of Canada for Buildings (NECB).

1. **PNNL Commercial Prototypes (Tall & SuperTall Office):** The standard PNNL Large Office prototype represents a 12-story commercial tower plus a basement (~498,588 ft² / 46,320 m² gross floor area). The published expected EUI of this prototype serves as the primary reference baseline for high-rise office runs.
2. **NECB 2020 Compliance Pathway:** The National Energy Code of Canada for Buildings (NECB) 2020 uses a performance-based pathway. Instead of setting a static EUI target, it compares a proposed building design to a reference building with matching geometry but minimum prescriptive code performance. NRCan/CanmetENERGY studies on Canadian office archetypes show that NECB 2017/2020-compliant large offices average **80 to 140 kWh/m²·yr** depending on fuel choices and electrification level.
3. **Standard Progression (Vintage Trajectory):** EUI values drop consistently across Standard 90.1 cycles (2004 → 2013 → 2016 → 2019) due to reductions in Lighting Power Density (LPD), increased envelope insulation requirements, and improved HVAC component efficiencies (chillers, boilers, fans).
4. **Site Energy Focus:** In alignment with building simulation outputs, all benchmarks in this document are expressed as **site (secondary) energy** divided by **conditioned floor area**, excluding generation and transmission losses.

---

## Details

### 1. Local Reference Database (ASHRAE 90.1-2004 Baseline)

The local CSV database [DOE_non-residential_simulation_results_canadian.csv](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv) documents simulated commercial EUI benchmarks in kWh/m²·yr across 16 U.S. cities representing different climate zones.

#### Table 1.1 — Local Database Simulated EUI for Large Office (ASHRAE 90.1-2004 Baseline)
| Representative City | Climate Zone | Total EUI (kWh/m²·yr) | Total EUI (kBtu/ft²·yr) | Total EUI (GJ/m²·yr) |
|---|---|---|---|---|
| Chicago - Toronto | 5A | 162.46 | 51.5 | 0.585 |
| Minneapolis - Montreal | 6A | 172.56 | 54.7 | 0.621 |
| Helena | 6B | 178.87 | 56.7 | 0.644 |
| Duluth - Calgary | 7 | 176.34 | 55.9 | 0.635 |
| Fairbanks - Yellowknife | 8 | 214.51 | 68.0 | 0.772 |
| **2003 CBECS Average** | — | 311.04 | 98.6 | 1.120 |

**Conversion and Arithmetic Checks:**
- Native values in the CSV are reported in kWh/m²·yr.
- Conversion to kBtu/ft²·yr uses: \(\text{kBtu/ft}^2 = \text{kWh/m}^2 \div 3.15459\)
  - CZ 5A: \(162.461385 \div 3.15459 = 51.50 \text{ kBtu/ft}^2\cdot\text{yr}\)
  - CZ 6A: \(172.556073 \div 3.15459 = 54.70 \text{ kBtu/ft}^2\cdot\text{yr}\)
  - CZ 6B: \(178.865253 \div 3.15459 = 56.70 \text{ kBtu/ft}^2\cdot\text{yr}\)
  - CZ 7: \(176.341581 \div 3.15459 = 55.90 \text{ kBtu/ft}^2\cdot\text{yr}\)
  - CZ 8: \(214.512120 \div 3.15459 = 68.00 \text{ kBtu/ft}^2\cdot\text{yr}\)
  - CBECS Average: \(311.042574 \div 3.15459 = 98.60 \text{ kBtu/ft}^2\cdot\text{yr}\)
- Conversion to GJ/m²·yr uses: \(\text{GJ} = \text{kWh} \times 0.0036\)
  - CZ 5A: \(162.461385 \times 0.0036 = 0.585 \text{ GJ/m}^2\cdot\text{yr}\)
  - CZ 6A: \(172.556073 \times 0.0036 = 0.621 \text{ GJ/m}^2\cdot\text{yr}\)
  - CZ 7: \(176.341581 \times 0.0036 = 0.635 \text{ GJ/m}^2\cdot\text{yr}\)

---

### 2. NECB 2020 Reference Building Office EUI

NECB 2020 establishes energy efficiency tiers based on the percentage performance improvement relative to a dynamically-generated reference building model (Part 8 compliance). 

#### Table 2.1 — Implied Office EUI Bands under NECB 2020 Tiers (CZ 6 and CZ 7)
Based on CanmetENERGY energy performance studies for a standardized 10-story electrified vs. fossil-fuel baseline office building archetype.
| Performance Tier | Percent of Reference Target | Fossil-Fuel Heated EUI (kWh/m²·yr) | Electrified EUI (ASHP/GSHP) (kWh/m²·yr) |
|---|---|---|---|
| Reference / Tier 1 Baseline | 100% | 85.0 to 115.0 | 110.0 to 140.0 |
| Tier 2 | ≤ 75% | 63.8 to 86.3 | 82.5 to 105.0 |
| Tier 3 | ≤ 50% | 42.5 to 57.5 | 55.0 to 70.0 |
| Tier 4 | ≤ 40% | 34.0 to 46.0 | 44.0 to 56.0 |

*Note: Electrified systems experience higher site EUI in cold climates than advanced gas systems due to COP degradation of air-source heat pumps at very low outdoor temperatures (-20°C and below).*

---

### 3. ASHRAE 90.1 Large Office EUI Trajectory

The PNNL prototype building results demonstrate how successive editions of the ASHRAE 90.1 standard have consistently reduced modeled energy consumption for the 12-story Large Office prototype.

#### Table 3.1 — Simulated Site EUI Trajectory by ASHRAE 90.1 Version (Cold Climate Zones)
| Vintage / Code Edition | Climate Zone 5A (Chicago) (kWh/m² | kBtu/ft²) | Climate Zone 6A (Minneapolis) (kWh/m² | kBtu/ft²) | Climate Zone 7 (Duluth) (kWh/m² | kBtu/ft²) |
|---|---|---|---|
| **ASHRAE 90.1-2004** | 162.5 | 51.5 | 172.6 | 54.7 | 176.3 | 55.9 |
| **ASHRAE 90.1-2013** | 130.6 | 41.4 | 147.6 | 46.8 | 154.6 | 49.0 |
| **ASHRAE 90.1-2016** | 120.5 | 38.2 | 136.0 | 43.1 | 142.6 | 45.2 |
| **ASHRAE 90.1-2019** | 113.3 | 35.9 | 130.0 | 41.2 | 136.3 | 43.2 |

**Arithmetic Checks for 90.1-2019:**
- CZ 5A (Chicago): \(35.9 \text{ kBtu/ft}^2\cdot\text{yr} \times 3.15459 = 113.25 \text{ kWh/m}^2\cdot\text{yr}\)
- CZ 6A (Minneapolis): \(41.2 \text{ kBtu/ft}^2\cdot\text{yr} \times 3.15459 = 129.97 \text{ kWh/m}^2\cdot\text{yr}\)
- CZ 7 (Duluth): \(43.2 \text{ kBtu/ft}^2\cdot\text{yr} \times 3.15459 = 136.28 \text{ kWh/m}^2\cdot\text{yr}\)

---

### 4. End-Use Splits

The energy signature of a large office in a cold climate is heavily influenced by space heating, ventilation fans, and interior plug loads. 

#### Table 4.1 — Typical End-Use Energy Splits for PNNL Large Office Prototype in Climate Zones 6 & 7
| End-Use Category | Percent of Total Site Energy (%) | Implied EUI Range (kWh/m²·yr) |
|---|---|---|
| **Space Heating** | 35.0% to 45.0% | 45.5 to 63.0 |
| **Space Cooling** | 8.0% to 12.0% | 10.4 to 16.8 |
| **Ventilation Fans** | 12.0% to 18.0% | 15.6 to 25.2 |
| **Interior Equipment (Plug Loads)** | 18.0% to 24.0% | 23.4 to 33.6 |
| **Interior Lighting** | 10.0% to 15.0% | 13.0 to 21.0 |
| **Service Hot Water (DHW)** | 2.0% to 4.0% | 2.6 to 5.6 |
| **Pumps / Heat Rejection / Aux** | 2.0% to 4.0% | 2.6 to 5.6 |

*Note: Based on ASHRAE 90.1-2016 baseline runs (total EUI ~140 kWh/m²·yr).*

---

### 5. Electricity vs. Gas Split

Standard baseline prototype configurations in cold climates assume natural gas for heating and electricity for all other end-uses (cooling, fans, lights, plug loads, and pumps).

#### Table 5.1 — Fuel Splits in Standard PNNL Large Office Baseline Models
| Fuel Type | End-Uses Covered | Typical Share (%) | Implied EUI Range (kWh/m²·yr) |
|---|---|---|---|
| **Electricity** | Cooling, Lighting, Equipment, Fans, Pumps | 45% to 55% | 60.0 to 80.0 |
| **Natural Gas** | Space Heating, DHW | 45% to 55% | 60.0 to 80.0 |
| **Total** | All End-Uses | 100% | 120.0 to 160.0 |

- **Electrification Variance:** In fully electrified runs (e.g., swapping natural gas boilers for electric boilers or heat pumps), the electricity fraction shifts to **100%**, resulting in a simulated electric EUI of **100.0 to 180.0 kWh/m²·yr**, depending on mechanical system efficiency.

---

### 6. Floor-Area & Energy Basis

To ensure proper validation, simulated outputs must align with the parameters of the reference models:
- **Floor-Area Basis:** The reference models report EUI using **gross conditioned floor area** (the sum of all enclosed spaces inside the building envelope, excluding unconditioned parking garages).
- **Energy Metric:** All values in the tables represent **Site (Secondary) Energy**. They reflect the energy metered at the building boundary.

---

## Interpretation for simulation plausibility bands

- **Code-Compliant Target:** For a model representing new construction under NECB 2020 or ASHRAE 90.1-2019, the expected simulated EUI should sit between **110 and 140 kWh/m²·yr**.
- **Fossil-Fuel vs. Electric Trajectories:** The choice of HVAC system and heating source drastically affects the electricity-only EUI:
  - In a standard gas-heated baseline model, electricity EUI is confined to a tight **60 to 80 kWh/m²·yr** band, with natural gas providing the remainder.
  - In an all-electric design, the electricity EUI spans the entire **100 to 180 kWh/m²·yr** band.

---

## Recommendations

1. **Apply the Recommended Plausibility Gates:** Encode the following numeric thresholds to validate simulations of large offices in Climate Zones 6 and 7:

#### Table 7.1 — Recommended Plausibility Gate Limits (kWh/m²·yr)
| Gate Metric | Lower Limit (Fail Below) | Central Baseline Target | Upper Limit (Fail Above) |
|---|---|---|---|
| **Total Site EUI (All-Fuels)** | **100.0** | **135.0** | **200.0** |
| **Electricity EUI (Gas-Heated)** | **50.0** | **70.0** | **90.0** |
| **Electricity EUI (All-Electric)** | **90.0** | **130.0** | **190.0** |

2. **Verify the Area Denominator:** Ensure that your EnergyPlus EUI calculation uses the conditioned gross floor area. If the model includes unconditioned basements, exclude them from the denominator or apply a corresponding scaling adjustment.

---

## Caveats

- **Prototype Idealization:** PNNL prototype models assume idealized occupancy, lighting schedules, and plug-load density. They do not account for tenant behavioral variances, equipment degradation, or specialized loads (like high-intensity data centers), which typically cause real-world building energy use to be higher than modeled targets.
- **Infiltration and Wind Effects:** EnergyPlus simulations in cold climates (CZ 6 and CZ 7) are highly sensitive to envelope infiltration settings. If the wind exposure or crack coefficient is set too high, the heating load will artificially inflate the EUI beyond the upper limit.
- **Weather Files:** Ensure that the EnergyPlus simulation uses weather files (.epw) corresponding to the targeted Canadian cities. Standard prototype runs use representative U.S. cities (e.g., Minneapolis for CZ 6A, Duluth for CZ 7), which may have slightly different Solar Radiation and Wind Speed patterns than Montreal or Calgary.

---

## Sources

### 1. U.S. DOE Building Energy Codes Program (BECP) Commercial Prototype Models
- **Prototype Models Portal:** [DOE BECP Commercial Prototype Building Models](https://www.energycodes.gov/prototype-building-models)
- **Large Office Prototype Specifications:** [PNNL Large Office Description](https://www.energycodes.gov/development/commercial/prototype_models#LargeOffice)

### 2. Pacific Northwest National Laboratory (PNNL) Reports
- **90.1-2016 Energy Savings Analysis:** *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016* (PNNL-26343). [OSTI Report 1429881](https://www.osti.gov/biblio/1429881)
- **90.1-2019 Energy Savings Analysis:** *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019* (PNNL-28543). [OSTI Report 1644781](https://www.osti.gov/biblio/1644781)
- **PNNL Interactive Visualization Dashboard:** [DOE BECP Tableau Energy Analysis Visualization Portal](https://public.tableau.com/app/profile/doebecp/viz/2019EndUseAnalysisViz-Copy/Introduction)

### 3. National Energy Code of Canada for Buildings (NECB) & NRCan Resources
- **NECB 2020 Technical Codes:** National Research Council Canada (NRC). [NRC Publications Archive](https://nrc-publications.canada.ca/eng/view/object/?id=524c7f3e-52f6-4927-8d99-e60d2b6b553e)
- **Natural Resources Canada Commercial Building Analysis:** CanmetENERGY Energy Performance of Commercial Archetypes. [NRCan CanmetENERGY Publications](https://www.nrcan.gc.ca/energy-efficiency/energy-efficiency-buildings/canmetenergy-buildings-research/20261)
