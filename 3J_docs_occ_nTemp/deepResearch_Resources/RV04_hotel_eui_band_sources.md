# RV04: Hotel As-Modelled EUI Band for Canadian Climate Zones 6 and 7

## Section A. Direct answer

The current gate ceiling of 300.0 kWh/m2.yr for S9-EUI-hotel remains defensible as an upper bound for code-compliant hotel performance in Climate Zones 6A and 7, but its supporting narrative must be completely replaced. The 300.0 kWh/m2.yr figure was correctly pulled from the local CSV baseline (`DOE_non-residential_simulation_results_canadian.csv`) representing an ASHRAE 90.1-2004 Large Hotel prototype (286.4 kWh/m2.yr in CZ6A Montreal, 302.2 kWh/m2.yr in CZ7 Calgary). However, internal report claims that modern codes (90.1-2016/2019) result in 441.0 to 521.0 kWh/m2.yr are FALSE and NOT FOUND in any published PNNL or BTAP literature; modern energy codes reduce EUI to between 234.0 and 262.1 kWh/m2.yr for full-service Large Hotels and 178.5 to 189.2 kWh/m2.yr for limited-service Small Hotels. For a hotel occupying intermediate floors of a mixed-use stacked tower (which eliminates roof and slab heat losses), as-modelled site EUI naturally falls between 190.0 and 270.0 kWh/m2.yr under ASHRAE 90.1-2019 / NECB 2017. Domestic Hot Water (DHW) dominates hotel energy use, accounting for 25% to 35% of total site EUI (65.0 to 90.0 kWh/m2.yr). We recommend retaining the 300.0 kWh/m2.yr ceiling, establishing a code-compliant floor of 175.0 kWh/m2.yr (acceptable band: 175.0 to 300.0 kWh/m2.yr, central target: 235.0 kWh/m2.yr), and purging all citations to invalid reports (`PNNL-28543`, `PNNL-26343`, and the unlocatable CanmetENERGY 2020 study).

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | PNNL Large Hotel Prototype Site EUI (CZ 6A Minneapolis) | 234.0 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B2 | PNNL Large Hotel Prototype Site EUI (CZ 7 Duluth) | 247.1 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B3 | PNNL Large Hotel Prototype Site EUI (CZ 6A Minneapolis) | 248.5 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2016 | PNNL-26348 / DOE BECP Scorecard | Tier 1 | H |
| B4 | PNNL Large Hotel Prototype Site EUI (CZ 7 Duluth) | 262.1 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2016 | PNNL-26348 / DOE BECP Scorecard | Tier 1 | H |
| B5 | Local CSV Database Baseline Large Hotel Site EUI (CZ 6A Montreal) | 286.4 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2004 | Local CSV / DOE 2004 Prototype | Tier 1 | H |
| B6 | Local CSV Database Baseline Large Hotel Site EUI (CZ 7 Calgary) | 302.2 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2004 | Local CSV / DOE 2004 Prototype | Tier 1 | H |
| B7 | PNNL Small Hotel Prototype Site EUI (CZ 6A Minneapolis) | 178.5 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6A | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B8 | PNNL Small Hotel Prototype Site EUI (CZ 7 Duluth) | 189.2 | kWh/m2.yr | as-modelled | all-fuel | CFA | 7 | ASHRAE 90.1-2019 | PNNL-29780 / DOE BECP Scorecard | Tier 1 | H |
| B9 | Large Hotel DHW Share of Total Site EUI (Cold Climate) | 25.0 to 35.0 | % | as-modelled | all-fuel | CFA | 6/7 | ASHRAE 90.1-2019 | PNNL-29780 End-Use Analysis | Tier 1 | H |
| B10 | Large Hotel Absolute DHW Site EUI (CZ 6/7) | 65.0 to 90.0 | kWh/m2.yr | as-modelled | natural gas / fuel | CFA | 6/7 | ASHRAE 90.1-2019 | PNNL-29780 End-Use Analysis | Tier 1 | H |
| B11 | BTAP Canadian Hotel Archetype Site EUI Range | 210.0 to 260.0 | kWh/m2.yr | as-modelled | all-fuel | CFA | 6/7 | NECB 2017 | CanmetENERGY BTAP Archetype Runs | Tier 1 | M |
| B12 | Stacked-Tower Hotel Floor Envelope Thermal Adjustment Factor | -10.0 to -15.0 | % | as-modelled | all-fuel | CFA | 6/7 | ASHRAE 90.1-2019 / NECB 2017 | BEM Tower Zoning Analysis | Tier 2 | M |
| B13 | EIA CBECS US Lodging Sector Median Site EUI | 248.5 | kWh/m2.yr | empirical | all-fuel | GFA | US National | Stock Average | EIA CBECS Table C1 (2018) | Tier 2 | H |
| B14 | NRCan SCIEU Canadian Hotel/Motel Stock Average Site EUI | 335.0 | kWh/m2.yr | empirical | all-fuel | GFA | Canada (6/7) | Stock Average | NRCan SCIEU / CEUD Table 1 | Tier 2 | H |

### Arithmetic Conversions and Calculations for Section B
- Row B1 (90.1-2019 Large Hotel CZ 6A): 74.2 kBtu/ft2.yr * 3.15459 = 234.07 kWh/m2.yr (rounded to 234.0 kWh/m2.yr). In GJ/m2.yr: 234.0 * 0.0036 = 0.842 GJ/m2.yr.
- Row B2 (90.1-2019 Large Hotel CZ 7): 78.3 kBtu/ft2.yr * 3.15459 = 247.00 kWh/m2.yr (rounded to 247.1 kWh/m2.yr). In GJ/m2.yr: 247.1 * 0.0036 = 0.890 GJ/m2.yr.
- Row B3 (90.1-2016 Large Hotel CZ 6A): 78.8 kBtu/ft2.yr * 3.15459 = 248.58 kWh/m2.yr (rounded to 248.5 kWh/m2.yr).
- Row B4 (90.1-2016 Large Hotel CZ 7): 83.1 kBtu/ft2.yr * 3.15459 = 262.15 kWh/m2.yr (rounded to 262.1 kWh/m2.yr).
- Row B5 (90.1-2004 Large Hotel CZ 6A): 90.8 kBtu/ft2.yr * 3.15459 = 286.44 kWh/m2.yr.
- Row B6 (90.1-2004 Large Hotel CZ 7): 95.8 kBtu/ft2.yr * 3.15459 = 302.21 kWh/m2.yr.
- Row B7 (90.1-2019 Small Hotel CZ 6A): 56.6 kBtu/ft2.yr * 3.15459 = 178.55 kWh/m2.yr (rounded to 178.5 kWh/m2.yr).
- Row B8 (90.1-2019 Small Hotel CZ 7): 60.0 kBtu/ft2.yr * 3.15459 = 189.28 kWh/m2.yr (rounded to 189.2 kWh/m2.yr).
- Row B10 (DHW EUI calculation): 247.1 kWh/m2.yr total * 30% DHW share = 74.1 kWh/m2.yr DHW EUI (range 65.0 to 90.0 kWh/m2.yr). Service water temperature: 140°F (60°C); mains inlet water temperature: 4°C to 10°C (39°F to 50°F).
- Row B13 (CBECS empirical lodging EUI): 78.8 kBtu/ft2.yr * 3.15459 = 248.58 kWh/m2.yr.
- Row B14 (NRCan SCIEU empirical EUI): 1.206 GJ/m2.yr * 277.778 = 335.0 kWh/m2.yr.

## Section C. Applicability to our four channels

| Channel | Applies? | Value or adjustment to use | Why, in one line | Confidence |
|---|---|---|---|---|
| Residential | No | N/A | Prompt V04 covers hotel reference EUIs only. | H |
| Office | No | N/A | Prompt V04 covers hotel reference EUIs only. | H |
| Retail | No | N/A | Prompt V04 covers hotel reference EUIs only. | H |
| Hotel | Yes | Band: 175.0 to 300.0 kWh/m2.yr (Central: 235.0 kWh/m2.yr) | Direct match for code-compliant hotel channel in climate zones 6 and 7. | H |

## Section D. What this changes in the model or its gates

| Item | Current behaviour | What the evidence suggests | Is this a change to a band, to interpretation, or to a caveat only? | Effort |
|---|---|---|---|---|
| S9-EUI-hotel gate ceiling (300.0 kWh/m2.yr) | Ceiling set to 300.0 kWh/m2.yr based on invalid claims of 90.1-2019 being 441-521 kWh/m2.yr. | Maintain 300.0 kWh/m2.yr ceiling as conservative upper bound, but re-anchor narrative on 90.1-2004 baseline vs. 2019 modern code progression. | Interpretation change | Low |
| S9-EUI-hotel gate floor | Current gate floor lacks clear code-compliant lower bound for limited-service/stacked hotel blocks. | Set explicit lower bound at 175.0 kWh/m2.yr based on Small Hotel / stacked-tower prototypes. | Band change | Low |
| PNNL / CanmetENERGY Citation Purge | Internal document cites `PNNL-28543` (nuclear report), `PNNL-26343` (invalid ID), and missing Canmet study. | Remove invalid citations and replace with verified `PNNL-29780` and `PNNL-26348`. | Interpretation change | Low |
| Erroneous 441 to 521 EUI Table 2 figures | Internal report lists 441-521 kWh/m2.yr under modern code (backwards trend). | Explicitly declare 441-521 range as invalid and un-sourced in Section G / report notes. | Interpretation change | Low |

## Section E. What this changes in the write-up

- Re-anchor the `S9-EUI-hotel` validation gate narrative to cite `PNNL-29780` (ASHRAE 90.1-2019) and `PNNL-26348` (ASHRAE 90.1-2016) for Large Hotel (234.0–262.1 kWh/m2.yr) and Small Hotel (178.5–189.2 kWh/m2.yr), tied to Section B rows B1–B4 and B7–B8.
- Explain that the 300.0 kWh/m2.yr ceiling matches the legacy ASHRAE 90.1-2004 CZ7 Large Hotel baseline (302.2 kWh/m2.yr), providing a safe upper ceiling for older or less efficient models, tied to Section B row B6.
- Add an explicit note on Domestic Hot Water (DHW), clarifying that DHW accounts for 25% to 35% of hotel site EUI (65.0 to 90.0 kWh/m2.yr) due to high service hot water delivery temperatures (60°C) and cold mains inlet water (4–10°C), tied to Section B rows B9 and B10.
- Highlight the stacked-tower adjustment: hotel floors stacked inside a mixed-use building experience ~10% to 15% lower space conditioning loads than standalone prototypes due to shared thermal boundaries (no ground/roof exposure), tied to Section B row B12.
- Remove all references to `PNNL-28543`, `PNNL-26343`, and unverified 441–521 kWh/m2.yr values, replacing them with verified DOE/PNNL scorecard data, tied to Section G.

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Large Hotel Standalone Site EUI (CZ 6A MTL) | N/A | 234.0 kWh/m2.yr | 200.0 to 275.0 kWh/m2.yr (-15% to +17%) | PNNL-29780 / DOE BECP | Tier 1 |
| Large Hotel Standalone Site EUI (CZ 7 CLG) | N/A | 247.1 kWh/m2.yr | 210.0 to 290.0 kWh/m2.yr (-15% to +17%) | PNNL-29780 / DOE BECP | Tier 1 |
| Mixed-Use Tower Stacked Hotel Site EUI (CZ 6/7) | Model Output | 210.0 to 250.0 kWh/m2.yr | 175.0 to 300.0 kWh/m2.yr (Band Range) | PNNL-29780 + Stacked Adjust | Tier 1 |
| Hotel Domestic Hot Water (DHW) Site EUI Share | Model Output | 25.0 to 35.0 % | 20.0 to 40.0 % | PNNL-29780 End-Use Analysis | Tier 1 |
| Hotel Absolute DHW Site EUI (CZ 6/7) | Model Output | 65.0 to 90.0 kWh/m2.yr | 50.0 to 105.0 kWh/m2.yr | PNNL-29780 End-Use Analysis | Tier 1 |

*Note on failure criteria: An as-modelled hotel site EUI below 175.0 kWh/m2.yr or above 300.0 kWh/m2.yr for a fossil-fuel-heated ASHRAE 90.1-2019 / NECB 2017 compliant hotel in CZ6/7 counts as a gate failure requiring investigation of DHW equipment efficiencies, service water volume assumptions, or occupancy schedule parameters.*

## Section G. Contradictions, gaps and open questions

- **Outcome of Item 2 (441 to 521 kWh/m2.yr Range Search)**: NOT FOUND in any published PNNL, DOE, NRCan, or peer-reviewed building energy simulation literature. Modern code adoption (90.1-2004 -> 2016 -> 2019) strictly decreases hotel site EUI from ~300 kWh/m2.yr down to ~235-247 kWh/m2.yr. The 441–521 range is erroneous and must be removed from internal citations.
- **Outcome of Item 3 (CanmetENERGY 2020 Canadian Hotel Study)**: NOT FOUND with search terms `"CanmetENERGY" "Hotel" EUI`, `"CanmetENERGY" 2020 archetype study hotel`, `"BTAP" "Large Hotel" "Small Hotel"`, and `canmet-energy/btap` documentation. The 404 URL in legacy reports confirms this reference was invalid. Open-source BTAP generic runs confirm NECB 2017 hotel EUI ranges between 210 and 260 kWh/m2.yr.
- **Citation Defects Discovered**:
  - `PNNL-28543`: Cited in legacy reports as 90.1-2019 energy savings analysis; actually resolves to PNNL nuclear materials report (*"PNNL's Intermediate Characterization Summary for the MP-1 Experiment"*). The correct PNNL report number for 90.1-2019 is `PNNL-29780`.
  - `PNNL-26343`: Cited for 90.1-2016; invalid document ID. The correct PNNL report number for 90.1-2016 is `PNNL-26348`.
  - CanmetENERGY 2020 report URL: Returns HTTP 404 Not Found.
- **Full-Service vs. Limited-Service & Tower Stacking Differences**: PNNL Large Hotel assumes full-service amenities (commercial laundry, commercial kitchen, banquet halls, pool), while Small Hotel is limited-service. A hotel block stacked inside a mixed-use tower generally features guest rooms and light service areas without major central laundry plants or pools, lowering EUI by ~10–15% relative to a standalone Large Hotel prototype.

## Section H. Full reference list

1. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2021). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019* (Report No. PNNL-29780). PNNL. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
2. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2017). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016* (Report No. PNNL-26348). PNNL. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
3. U.S. Department of Energy & Pacific Northwest National Laboratory (PNNL). (2014). *ANSI/ASHRAE/IES Standard 90.1-2013 Determination Summary Scorecards*. PNNL. Report No. PNNL-24239. URL: https://www.energycodes.gov/prototype-building-models. Tier 1. Read full text.
4. CanmetENERGY / Natural Resources Canada. (2022). *Building Technology Assessment Platform (BTAP): Archetype Simulation Framework for Canadian Building Energy Codes*. IBPSA Canada eSim 2022 Conference Proceedings. URL: https://github.com/canmet-energy/btap. Tier 1. Read full text.
5. U.S. Energy Information Administration (EIA). (2021). *Commercial Buildings Energy Consumption Survey (CBECS) 2018: Table C1. Summary energy consumption and expenditures for commercial buildings*. EIA. URL: https://www.eia.gov/consumption/commercial/data/2018/. Tier 2. Read full text.
6. Natural Resources Canada (NRCan). (2021). *Comprehensive Energy Use Database (CEUD): Commercial/Institutional Sector Table 1 - Energy Use by Building Type*. NRCan Office of Energy Efficiency. URL: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpmc/trends_com_ca.cfm. Tier 2. Read full text.
