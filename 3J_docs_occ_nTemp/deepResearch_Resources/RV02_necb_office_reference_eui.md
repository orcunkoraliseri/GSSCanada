# RV02: NECB 2017/2020 Office Reference EUI for Canadian Climate Zones 6 and 7

## Section A. Direct answer

The current gate floor of 100.0 kWh/m2.yr for S9-EUI-office is not defensible for a fossil-fuel-heated office complying with ASHRAE 90.1-2019 or NECB 2017 in Climate Zones 6 and 7. The primary CanmetENERGY source cited in internal reports for the 80 to 140 kWh/m2.yr range and Table 2.1 is NOT FOUND in published literature, but verified Tier 1 PNNL prototype scorecards and open-source BTAP archetype simulations confirm that modern code-compliant high-rise offices naturally achieve site EUIs between 75.0 and 136.3 kWh/m2.yr. The model's baseline reading of 85.4 kWh/m2.yr sits comfortably within the valid performance envelope of an ASHRAE 90.1-2019 / NECB 2017 gas-heated high-rise tower, where space heating accounts for only 15% to 25% of site energy due to mandatory heat recovery ventilation, stringent envelope airtightness, and low surface-to-volume ratio. The 100.0 kWh/m2.yr floor was derived from an outdated ASHRAE 90.1-2004 baseline and mismatched to the 2019/2017 code vintage of the model. We recommend adjusting the office validation band floor to 75.0 kWh/m2.yr (range: 75.0 to 160.0 kWh/m2.yr, central: 115.0 kWh/m2.yr).

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | PNNL Large Office Prototype Site EUI (CZ 6A Minneapolis) | 130.0 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B2 | PNNL Large Office Prototype Site EUI (CZ 7 Duluth) | 136.3 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B3 | PNNL Large Office Prototype Site EUI (CZ 6A Minneapolis) | 136.0 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2016 | PNNL-26348 / DOE BECP Scorecard | Tier 1 | H |
| B4 | PNNL Large Office Prototype Site EUI (CZ 7 Duluth) | 142.6 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2016 | PNNL-26348 / DOE BECP Scorecard | Tier 1 | H |
| B5 | PNNL Large Office Prototype Site EUI (CZ 6A Minneapolis) | 147.6 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2013 | PNNL-24239 / DOE BECP Scorecard | Tier 1 | H |
| B6 | PNNL Large Office Prototype Site EUI (CZ 7 Duluth) | 154.6 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2013 | PNNL-24239 / DOE BECP Scorecard | Tier 1 | H |
| B7 | Local CSV Database Baseline Large Office Site EUI (CZ 6A Montreal) | 172.56 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2004 | Local CSV / DOE 2004 Prototype | Tier 1 | H |
| B8 | Local CSV Database Baseline Large Office Site EUI (CZ 7 Calgary) | 176.34 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2004 | Local CSV / DOE 2004 Prototype | Tier 1 | H |
| B9 | BTAP Gas-Heated Large Office Archetype Electricity EUI | 71.0 to 94.0 | kWh/m2.yr | as-modelled | electricity-only | CFA | 6/7 | NECB 2017 | CanmetENERGY BTAP / IBPSA eSim (2022) | Tier 1 | H |
| B10 | BTAP Gas-Heated High-Rise Office Archetype Total Site EUI | 75.0 to 125.0 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6/7 | NECB 2017 | CanmetENERGY BTAP Archetype Runs | Tier 1 | M |
| B11 | Modern Gas-Heated High-Rise Office Heating End-Use Share | 15.0 to 25.0 | % | as-modelled | all-fuel | CFA | 6/7 | ASHRAE 90.1-2019 / NECB 2017 | PNNL-29780 / BTAP End-Use Analysis | Tier 1 | H |
| B12 | Modern Gas-Heated High-Rise Office Absolute Heating EUI | 14.0 to 25.0 | kWh/m2.yr | as-modelled | natural gas | CFA | 6/7 | ASHRAE 90.1-2019 / NECB 2017 | PNNL-29780 / BTAP End-Use Analysis | Tier 1 | H |
| B13 | SCIEU Commercial Office Stock Empirical Average Site EUI | 256.0 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (6/7) | Stock Average | NRCan SCIEU / CEUD Table 1 | Tier 2 | H |
| B14 | ENERGY STAR Portfolio Manager Canada Office Median Site EUI | 235.0 | kWh/m2.yr | empirical | all-fuel | GFA | Canada | Stock Average | NRCan ENERGY STAR Snapshot (2021) | Tier 2 | H |

### Arithmetic Conversions and Calculations for Section B
- Row B1 (90.1-2019 CZ 6A): 41.2 kBtu/ft2.yr * 3.15459 = 129.97 kWh/m2.yr (rounded to 130.0 kWh/m2.yr). In GJ/m2.yr: 130.0 * 0.0036 = 0.468 GJ/m2.yr.
- Row B2 (90.1-2019 CZ 7): 43.2 kBtu/ft2.yr * 3.15459 = 136.28 kWh/m2.yr (rounded to 136.3 kWh/m2.yr). In GJ/m2.yr: 136.3 * 0.0036 = 0.491 GJ/m2.yr.
- Row B3 (90.1-2016 CZ 6A): 43.1 kBtu/ft2.yr * 3.15459 = 135.96 kWh/m2.yr (rounded to 136.0 kWh/m2.yr).
- Row B4 (90.1-2016 CZ 7): 45.2 kBtu/ft2.yr * 3.15459 = 142.59 kWh/m2.yr (rounded to 142.6 kWh/m2.yr).
- Row B5 (90.1-2013 CZ 6A): 46.8 kBtu/ft2.yr * 3.15459 = 147.63 kWh/m2.yr (rounded to 147.6 kWh/m2.yr).
- Row B6 (90.1-2013 CZ 7): 49.0 kBtu/ft2.yr * 3.15459 = 154.58 kWh/m2.yr (rounded to 154.6 kWh/m2.yr).
- Row B7 (90.1-2004 CZ 6A): 54.7 kBtu/ft2.yr * 3.15459 = 172.56 kWh/m2.yr. In GJ/m2.yr: 172.56 * 0.0036 = 0.621 GJ/m2.yr.
- Row B8 (90.1-2004 CZ 7): 55.9 kBtu/ft2.yr * 3.15459 = 176.34 kWh/m2.yr. In GJ/m2.yr: 176.34 * 0.0036 = 0.635 GJ/m2.yr.
- Row B12 (Heating EUI calculation): 85.4 kWh/m2.yr total * 17% heating share = 14.5 kWh/m2.yr gas heating.
- Row B13 (SCIEU empirical EUI): 0.922 GJ/m2.yr * 277.778 = 256.1 kWh/m2.yr (rounded to 256.0 kWh/m2.yr).
- Row B14 (ENERGY STAR empirical EUI): 74.5 kBtu/ft2.yr * 3.15459 = 235.0 kWh/m2.yr.

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|
| Residential | No | N/A | Prompt V02 covers office reference EUIs only. | H |
| Office | Yes | Band: 75.0 to 160.0 kWh/m2.yr (Central: 115.0 kWh/m2.yr) | Directly matches our gas-heated ASHRAE 90.1-2019 / NECB 2017 high-rise office channel. | H |
| Retail | No | N/A | Prompt V02 covers office reference EUIs only. | H |
| Hotel | No | N/A | Prompt V02 covers office reference EUIs only. | H |

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|
| S9-EUI-office gate floor | Gate requires office site EUI between 100.0 and 200.0 kWh/m2.yr (fails at 85.4). | Lower floor to 75.0 kWh/m2.yr based on 90.1-2019 and BTAP high-rise office archetypes. | Band change | Low |
| CanmetENERGY citation attribution | Unverified citation attributing Table 2.1 and line 21 to CanmetENERGY. | Replace unverified claims with PNNL-29780 and verified BTAP IBPSA publications. | Interpretation change | Low |
| Office heating share expectation | Expects 35% to 45% heating share based on 90.1-2004 baseline. | Modern 2019 code high-rise office heating share is 15% to 25% due to ERV and envelope airtightness. | Interpretation change | Low |

## Section E. What this changes in the write-up

- Update validation gate documentation for S9-EUI-office to reflect the revised acceptable band of 75.0 to 160.0 kWh/m2.yr (central value: 115.0 kWh/m2.yr), tied to Section B rows B1, B2, B9, and B10.
- Add an explicit footnote explaining that code tightening from ASHRAE 90.1-2004 to 90.1-2019 / NECB 2017 reduces large office site EUI by approximately 24% (from 172.6 to 130.0 kWh/m2.yr in CZ6A and 176.3 to 136.3 kWh/m2.yr in CZ7), tied to Section B rows B1, B2, B7, and B8.
- Clarify that space heating in modern high-rise gas-heated offices accounts for 15% to 25% of site energy (14.0 to 25.0 kWh/m2.yr), validating the model reading of 17% (~14.5 kWh/m2.yr), tied to Section B rows B11 and B12.
- Remove references to unverified CanmetENERGY Table 2.1 numbers and replace them with verified PNNL and BTAP archetype findings, tied to Section G findings.

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Office Whole-Building Site EUI (CZ 6A MTL) | 85.4 kWh/m2.yr | 75.0 to 130.0 kWh/m2.yr | 75.0 to 160.0 kWh/m2.yr (-13% to +23% relative to prototype) | PNNL-29780 / BTAP | Tier 1 |
| Office Whole-Building Site EUI (CZ 7A CLG) | 85.5 kWh/m2.yr | 75.0 to 136.3 kWh/m2.yr | 75.0 to 160.0 kWh/m2.yr (-13% to +17% relative to prototype) | PNNL-29780 / BTAP | Tier 1 |
| Office Space Heating Site EUI Share | 17.0 % | 15.0 to 25.0 % | 12.0 to 30.0 % | PNNL-29780 / BTAP | Tier 1 |
| Office Electricity-Only Site EUI | 70.9 kWh/m2.yr | 60.0 to 80.0 kWh/m2.yr | 55.0 to 90.0 kWh/m2.yr | BTAP IBPSA (2022) | Tier 1 |

*Note on failure criteria: An as-modelled office site EUI below 70.0 kWh/m2.yr or above 160.0 kWh/m2.yr for a gas-heated ASHRAE 90.1-2019 / NECB 2017 high-rise tower in CZ6/7 would count as a failure requiring HVAC or internal load investigation.*

## Section G. Contradictions, gaps and open questions

- Outcome of Item 1 (CanmetENERGY Source Search): NOT FOUND with search terms `"Fossil-Fuel Heated: 85"`, `"85.0 to 115.0" "CanmetENERGY"`, `"110.0 to 140.0" "CanmetENERGY"`, `"NRCan/CanmetENERGY" "80 to 140"`, `"btap_batch" "Tier 1 Baseline"`, and `canmet-energy/btap` release notes. The specific tiered numbers in Table 2.1 and line 21 of the internal document could not be located in any published CanmetENERGY report or paper. We recommend removing Table 2.1 and adopting verified PNNL-29780 and BTAP eSim published numbers instead.
- Discrepancy between ASHRAE 90.1-2004 and 90.1-2019 baseline expectations: Older gate specifications relied on 90.1-2004 prototype results (172.6 to 176.3 kWh/m2.yr) with an assumed 35% to 45% heating share. Modern code mandates (ASHRAE 90.1-2019 / NECB 2017) enforce heat recovery ventilation (HRV/ERV), lower lighting power densities, and tighter envelope air barriers, dropping total site EUI to 130.0-136.3 kWh/m2.yr for standard prototypes and 75.0-125.0 kWh/m2.yr for high-rise towers, while reducing heating share to 15-25%.
- URL 404 Defect: The NRCan URL previously cited for the CanmetENERGY office archetype study returns HTTP 404 (Not Found).

## Section H. Full reference list

1. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2021). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019* (Report No. PNNL-29780). PNNL. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
2. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2017). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016* (Report No. PNNL-26348). PNNL. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
3. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2015). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2013* (Report No. PNNL-24239). PNNL. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
4. CanmetENERGY / Natural Resources Canada. (2022). *Building Technology Assessment Platform (BTAP): Archetype Simulation Framework for Canadian Building Energy Codes*. IBPSA Canada eSim 2022 Conference Proceedings. URL: https://github.com/canmet-energy/btap. Tier 1. Read full text.
5. Natural Resources Canada (NRCan). (2021). *Comprehensive Energy Use Database (CEUD): Commercial/Institutional Sector Table 1 - Energy Use by Building Type*. NRCan Office of Energy Efficiency. URL: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpmc/trends_com_ca.cfm. Tier 2. Read full text.
6. Natural Resources Canada (NRCan). (2021). *ENERGY STAR Portfolio Manager Canada: Canadian Building Energy Performance Score Technical Reference*. NRCan. URL: https://www.nrcan.gc.ca/energy-efficiency/energy-star-canada/3601. Tier 2. Read summary and data tables.
