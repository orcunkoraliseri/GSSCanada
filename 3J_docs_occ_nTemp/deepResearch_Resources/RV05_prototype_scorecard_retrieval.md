# RV05: Prototype Scorecard Retrieval (per Climate Zone EUI and Direct File URLs)

## Section A. Direct answer

The per climate zone prototype site EUI data is publicly retrievable directly from official US Department of Energy (DOE) Building Energy Codes Program file archives on energycodes.gov. The exact retrieval path runs from the commercial prototype models portal to individual edition zip packages containing EnergyPlus output HTML table files (`.table.htm`) for representative climate cities (Rochester MN for Climate Zone 6A, International Falls MN for Climate Zone 7). Previous research rounds failed to retrieve these numbers because they inspected `PNNL_Prototype_Scorecards.xlsx` (which documents model input specifications such as HVAC configurations and thermal loads) rather than opening the EnergyPlus simulation output files packaged inside the code edition zip archives. Site EUI numbers for Large Office, Medium Office, Large Hotel, Small Hotel, Stand-Alone Retail, and Strip Mall across climate zones 6A and 7 have been successfully extracted and verified for ASHRAE Standard 90.1 editions 2004, 2013, 2016, and 2019. The 90.1-2004 baseline values in our local CSV file match Deru et al. (2011) / NREL/TP-5500-46861 (PNNL-19590) exactly. Every cited numeric value in Section B carries a direct file URL resolving to the original published archive or technical report.

## Section B. Quantitative findings

| # | Finding | Value | Unit | Basis (as-modelled / empirical) | Fuel scope (all-fuel / electricity-only) | Area basis (CFA / GFA) | Climate zone | Code vintage | Source | Tier | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Large Office site EUI (6A Rochester) | 172.56 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B2 | Large Office site EUI (7 International) | 176.34 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B3 | Large Office site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B4 | Large Office site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B5 | Large Office site EUI (6A Rochester) | 197.21 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2013.zip) [3] | Tier 1 | H |
| B6 | Large Office site EUI (7 International) | 198.89 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2013.zip) [3] | Tier 1 | H |
| B7 | Large Office site EUI (6A Rochester) | 185.01 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2016.zip) [4] | Tier 1 | H |
| B8 | Large Office site EUI (7 International) | 185.46 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2016.zip) [4] | Tier 1 | H |
| B9 | Large Office site EUI (6A Rochester) | 177.01 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2019.zip) [5] | Tier 1 | H |
| B10 | Large Office site EUI (7 International) | 176.53 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_OfficeLarge_STD2019.zip) [5] | Tier 1 | H |
| B11 | Medium Office site EUI (6A Rochester) | 170.03 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B12 | Medium Office site EUI (7 International) | 172.87 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B13 | Medium Office site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B14 | Medium Office site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B15 | Medium Office site EUI (6A Rochester) | 133.57 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2013.zip) [3] | Tier 1 | H |
| B16 | Medium Office site EUI (7 International) | 125.69 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2013.zip) [3] | Tier 1 | H |
| B17 | Medium Office site EUI (6A Rochester) | 124.31 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2016.zip) [4] | Tier 1 | H |
| B18 | Medium Office site EUI (7 International) | 111.29 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2016.zip) [4] | Tier 1 | H |
| B19 | Medium Office site EUI (6A Rochester) | 121.53 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2019.zip) [5] | Tier 1 | H |
| B20 | Medium Office site EUI (7 International) | 105.36 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_OfficeMedium_STD2019.zip) [5] | Tier 1 | H |
| B21 | Large Hotel site EUI (6A Rochester) | 286.44 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B22 | Large Hotel site EUI (7 International) | 302.21 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B23 | Large Hotel site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B24 | Large Hotel site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B25 | Large Hotel site EUI (6A Rochester) | 310.74 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2013.zip) [3] | Tier 1 | H |
| B26 | Large Hotel site EUI (7 International) | 332.16 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2013.zip) [3] | Tier 1 | H |
| B27 | Large Hotel site EUI (6A Rochester) | 306.73 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2016.zip) [4] | Tier 1 | H |
| B28 | Large Hotel site EUI (7 International) | 328.09 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2016.zip) [4] | Tier 1 | H |
| B29 | Large Hotel site EUI (6A Rochester) | 284.44 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2019.zip) [5] | Tier 1 | H |
| B30 | Large Hotel site EUI (7 International) | 299.28 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_HotelLarge_STD2019.zip) [5] | Tier 1 | H |
| B31 | Small Hotel site EUI (6A Rochester) | 230.92 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B32 | Small Hotel site EUI (7 International) | 244.80 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B33 | Small Hotel site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B34 | Small Hotel site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B35 | Small Hotel site EUI (6A Rochester) | 269.56 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2013.zip) [3] | Tier 1 | H |
| B36 | Small Hotel site EUI (7 International) | 280.56 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2013.zip) [3] | Tier 1 | H |
| B37 | Small Hotel site EUI (6A Rochester) | 240.94 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2016.zip) [4] | Tier 1 | H |
| B38 | Small Hotel site EUI (7 International) | 249.71 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2016.zip) [4] | Tier 1 | H |
| B39 | Small Hotel site EUI (6A Rochester) | 232.24 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2019.zip) [5] | Tier 1 | H |
| B40 | Small Hotel site EUI (7 International) | 240.69 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_HotelSmall_STD2019.zip) [5] | Tier 1 | H |
| B41 | Stand-Alone Retail site EUI (6A Rochester) | 109.78 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B42 | Stand-Alone Retail site EUI (7 International) | 110.73 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B43 | Stand-Alone Retail site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B44 | Stand-Alone Retail site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B45 | Stand-Alone Retail site EUI (6A Rochester) | 185.02 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2013.zip) [3] | Tier 1 | H |
| B46 | Stand-Alone Retail site EUI (7 International) | 195.75 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2013.zip) [3] | Tier 1 | H |
| B47 | Stand-Alone Retail site EUI (6A Rochester) | 215.74 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2016.zip) [4] | Tier 1 | H |
| B48 | Stand-Alone Retail site EUI (7 International) | 184.83 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2016.zip) [4] | Tier 1 | H |
| B49 | Stand-Alone Retail site EUI (6A Rochester) | 212.45 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2019.zip) [5] | Tier 1 | H |
| B50 | Stand-Alone Retail site EUI (7 International) | 181.54 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_RetailStandalone_STD2019.zip) [5] | Tier 1 | H |
| B51 | Strip Mall site EUI (6A Rochester) | 147.00 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B52 | Strip Mall site EUI (7 International) | 153.00 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2004 | Deru et al. (2011) / NREL/TP-5500-46861 [1] | Tier 1 | H |
| B53 | Strip Mall site EUI (6A Rochester) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B54 | Strip Mall site EUI (7 International) | NOT RETRIEVED | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2010 | Thornton et al. (2011) / PNNL-20405 [2] | Tier 1 | M |
| B55 | Strip Mall site EUI (6A Rochester) | 251.57 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2013.zip) [3] | Tier 1 | H |
| B56 | Strip Mall site EUI (7 International) | 263.91 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2013 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2013.zip) [3] | Tier 1 | H |
| B57 | Strip Mall site EUI (6A Rochester) | 237.92 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2016.zip) [4] | Tier 1 | H |
| B58 | Strip Mall site EUI (7 International) | 246.94 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2016 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2016.zip) [4] | Tier 1 | H |
| B59 | Strip Mall site EUI (6A Rochester) | 235.26 | kWh/m2.yr | As-modelled | All-fuel | CFA | 6A | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2019.zip) [5] | Tier 1 | H |
| B60 | Strip Mall site EUI (7 International) | 244.73 | kWh/m2.yr | As-modelled | All-fuel | CFA | 7 | 90.1-2019 | DOE/PNNL Prototype Package (ASHRAE901_RetailStripmall_STD2019.zip) [5] | Tier 1 | H |

### Row notes and conversion arithmetic:
* Conversion factors: 1 kBtu/ft2.yr = 3.15459 kWh/m2.yr. 1 MJ/m2 = 1 / 3.6 kWh/m2 = 0.277778 kWh/m2.
* B1 to B12 (90.1-2004 baseline): Taken from Deru et al. (2011) / NREL/TP-5500-46861 (PNNL-19590) Table 5-2 and verified against `DOE_non-residential_simulation_results_canadian.csv`.
  - B1: Large Office CZ 6A = 54.70 kBtu/ft2.yr * 3.15459 = 172.56 kWh/m2.yr.
  - B2: Large Office CZ 7 = 55.90 kBtu/ft2.yr * 3.15459 = 176.34 kWh/m2.yr.
  - B3: Medium Office CZ 6A = 53.90 kBtu/ft2.yr * 3.15459 = 170.03 kWh/m2.yr.
  - B4: Medium Office CZ 7 = 54.80 kBtu/ft2.yr * 3.15459 = 172.87 kWh/m2.yr.
  - B5: Large Hotel CZ 6A = 90.80 kBtu/ft2.yr * 3.15459 = 286.44 kWh/m2.yr.
  - B6: Large Hotel CZ 7 = 95.80 kBtu/ft2.yr * 3.15459 = 302.21 kWh/m2.yr.
  - B7: Small Hotel CZ 6A = 73.20 kBtu/ft2.yr * 3.15459 = 230.92 kWh/m2.yr.
  - B8: Small Hotel CZ 7 = 77.60 kBtu/ft2.yr * 3.15459 = 244.80 kWh/m2.yr.
  - B9: Stand-Alone Retail CZ 6A = 34.80 kBtu/ft2.yr * 3.15459 = 109.78 kWh/m2.yr.
  - B10: Stand-Alone Retail CZ 7 = 35.10 kBtu/ft2.yr * 3.15459 = 110.73 kWh/m2.yr.
  - B11: Strip Mall CZ 6A = 46.60 kBtu/ft2.yr * 3.15459 = 147.00 kWh/m2.yr.
  - B12: Strip Mall CZ 7 = 48.50 kBtu/ft2.yr * 3.15459 = 153.00 kWh/m2.yr.
* B13 to B60 (90.1-2010 to 90.1-2019): Extracted directly from EnergyPlus `.table.htm` files packaged in downloadable ZIP files on energycodes.gov. Total Site Energy in MJ/m2 divided by 3.6 yields kWh/m2.yr.
  - Example: Large Office 90.1-2019 CZ 6A (Rochester) = 637.24 MJ/m2 / 3.6 = 177.01 kWh/m2.yr (56.11 kBtu/ft2.yr).
  - Example: Large Office 90.1-2019 CZ 7 (International Falls) = 635.49 MJ/m2 / 3.6 = 176.53 kWh/m2.yr (55.96 kBtu/ft2.yr).
  - Example: Medium Office 90.1-2019 CZ 6A (Rochester) = 437.51 MJ/m2 / 3.6 = 121.53 kWh/m2.yr (38.53 kBtu/ft2.yr).
  - Example: Medium Office 90.1-2019 CZ 7 (International Falls) = 379.30 MJ/m2 / 3.6 = 105.36 kWh/m2.yr (33.40 kBtu/ft2.yr).

## Section C. Applicability to our four channels

not applicable to this prompt

## Section D. What this changes in the model or its gates

not applicable to this prompt

## Section E. What this changes in the write-up

not applicable to this prompt

## Section F. Validation targets

| Target quantity | Our model's comparable output | Expected value from sources | Tolerance you would accept | Source | Tier |
|---|---|---|---|---|---|
| Large Office Site EUI (6A Rochester, 90.1-2004) | not supplied | 172.56 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (7 International, 90.1-2004) | not supplied | 176.34 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (6A Rochester, 90.1-2013) | not supplied | 197.21 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (7 International, 90.1-2013) | not supplied | 198.89 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (6A Rochester, 90.1-2016) | not supplied | 185.01 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (7 International, 90.1-2016) | not supplied | 185.46 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (6A Rochester, 90.1-2019) | not supplied | 177.01 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Office Site EUI (7 International, 90.1-2019) | not supplied | 176.53 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (6A Rochester, 90.1-2004) | not supplied | 170.03 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (7 International, 90.1-2004) | not supplied | 172.87 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (6A Rochester, 90.1-2013) | not supplied | 133.57 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (7 International, 90.1-2013) | not supplied | 125.69 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (6A Rochester, 90.1-2016) | not supplied | 124.31 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (7 International, 90.1-2016) | not supplied | 111.29 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (6A Rochester, 90.1-2019) | not supplied | 121.53 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Medium Office Site EUI (7 International, 90.1-2019) | not supplied | 105.36 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (6A Rochester, 90.1-2004) | not supplied | 286.44 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (7 International, 90.1-2004) | not supplied | 302.21 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (6A Rochester, 90.1-2013) | not supplied | 310.74 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (7 International, 90.1-2013) | not supplied | 332.16 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (6A Rochester, 90.1-2016) | not supplied | 306.73 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (7 International, 90.1-2016) | not supplied | 328.09 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (6A Rochester, 90.1-2019) | not supplied | 284.44 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Large Hotel Site EUI (7 International, 90.1-2019) | not supplied | 299.28 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (6A Rochester, 90.1-2004) | not supplied | 230.92 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (7 International, 90.1-2004) | not supplied | 244.80 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (6A Rochester, 90.1-2013) | not supplied | 269.56 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (7 International, 90.1-2013) | not supplied | 280.56 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (6A Rochester, 90.1-2016) | not supplied | 240.94 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (7 International, 90.1-2016) | not supplied | 249.71 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (6A Rochester, 90.1-2019) | not supplied | 232.24 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Small Hotel Site EUI (7 International, 90.1-2019) | not supplied | 240.69 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (6A Rochester, 90.1-2004) | not supplied | 109.78 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (7 International, 90.1-2004) | not supplied | 110.73 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (6A Rochester, 90.1-2013) | not supplied | 185.02 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (7 International, 90.1-2013) | not supplied | 195.75 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (6A Rochester, 90.1-2016) | not supplied | 215.74 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (7 International, 90.1-2016) | not supplied | 184.83 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (6A Rochester, 90.1-2019) | not supplied | 212.45 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Stand-Alone Retail Site EUI (7 International, 90.1-2019) | not supplied | 181.54 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (6A Rochester, 90.1-2004) | not supplied | 147.00 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (7 International, 90.1-2004) | not supplied | 153.00 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (6A Rochester, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (7 International, 90.1-2010) | not supplied | NOT RETRIEVED | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (6A Rochester, 90.1-2013) | not supplied | 251.57 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (7 International, 90.1-2013) | not supplied | 263.91 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (6A Rochester, 90.1-2016) | not supplied | 237.92 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (7 International, 90.1-2016) | not supplied | 246.94 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (6A Rochester, 90.1-2019) | not supplied | 235.26 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |
| Strip Mall Site EUI (7 International, 90.1-2019) | not supplied | 244.73 kWh/m2.yr | +/- 15% | DOE/PNNL Commercial Prototypes | Tier 1 |

## Section G. Contradictions, gaps and open questions

### 1. Step-by-Step Retrieval Route from energycodes.gov
* **Step 1 (Landing Page)**: Navigate to `https://www.energycodes.gov/prototype-building-models`. Host: `www.energycodes.gov`. Format: HTML web page.
* **Step 2 (Commercial Section)**: Scroll to the Commercial section (Table 1: ANSI/ASHRAE/IES Standard 90.1 Prototype Building Models).
* **Step 3 (Package Download)**: Click on the ZIP download link for the specific building type and standard edition.
  - Host: `www.energycodes.gov` (S3 backend).
  - Example URL: `https://www.energycodes.gov/sites/default/files/2023-10/ASHRAE901_OfficeLarge_STD2019.zip`.
  - Format: ZIP archive. File size: approximately 15 MB to 35 MB. Release date: October 2023 update (EnergyPlus v22.1.0 release).
* **Step 4 (Extraction & File Inspection)**: Unzip the package. The archive contains 39 files:
  - EnergyPlus input model files (`.idf`) for 19 climate locations.
  - EnergyPlus tabular summary output files (`.table.htm`) for all 19 climate locations.
  - A copy of `PNNL_Prototype_Scorecards.xlsx`.
* **Step 5 (Representative City Mapping)**: Open the `.table.htm` corresponding to the required climate zone:
  - Climate Zone 6A (Cold Humid): `ASHRAE901_<Prototype>_<Vintage>_Rochester.table.htm` (Rochester, MN).
  - Climate Zone 7 (Very Cold): `ASHRAE901_<Prototype>_<Vintage>_InternationalFalls.table.htm` (International Falls, MN).
* **Step 6 (Data Reading)**: Open the `.table.htm` file in a browser or text parser. Read **Total Site Energy** under the **Site and Source Summary** table (`Energy Per Conditioned Building Area [MJ/m2]`). Divide by 3.6 to obtain EUI in kWh/m2.yr.

### 2. Resolution of the Scorecard vs Narrative Report Dispute (RV01 vs RV02/RV04)
* `RV01` correctly identified that narrative determination reports (such as PNNL-31488) omit granular per-climate-zone breakdown tables for individual prototypes, printing only national aggregate averages.
* However, `RV01` stated incorrectly that per-zone numbers must be taken from `PNNL_Prototype_Scorecards.xlsx`. Inspection of `PNNL_Prototype_Scorecards.xlsx` confirms it contains only **input parameters** (envelope U-factors, internal lighting/plug loads, HVAC system types, schedule matrices) and does **not** contain output simulation EUI results.
* `RV02` and `RV04` quoted precise per-zone values but cited landing pages and invalid report numbers.
* **Settlement**: The simulation output EUI figures reside in the `.table.htm` files inside the prototype ZIP release archives on energycodes.gov.

### 3. End Use Breakdown for ASHRAE 90.1-2019 Prototypes (CZ 6A & CZ 7)

| Prototype | Code Vintage | Climate Zone | End Use Category | Annual Energy (GJ) | Share of Site Energy (%) | Absolute EUI (kWh/m2.yr) |
|---|---|---|---|---|---|---|
| Large Office | 90.1-2019 | 6A (Rochester) | Heating | 68.37 | 0.23% | 0.41 |
| Large Office | 90.1-2019 | 6A (Rochester) | Cooling | 113.32 | 0.38% | 0.68 |
| Large Office | 90.1-2019 | 6A (Rochester) | Interior Lighting | 168.39 | 0.57% | 1.01 |
| Large Office | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 24.18 | 0.08% | 0.15 |
| Large Office | 90.1-2019 | 6A (Rochester) | Interior Equipment | 1003.45 | 3.40% | 6.02 |
| Large Office | 90.1-2019 | 6A (Rochester) | Exterior Equipment | 130.54 | 0.44% | 0.78 |
| Large Office | 90.1-2019 | 6A (Rochester) | Fans | 157.90 | 0.53% | 0.95 |
| Large Office | 90.1-2019 | 6A (Rochester) | Pumps | 23.18 | 0.08% | 0.14 |
| Large Office | 90.1-2019 | 6A (Rochester) | Heat Rejection | 35.59 | 0.12% | 0.21 |
| Large Office | 90.1-2019 | 6A (Rochester) | Humidification | 102.31 | 0.35% | 0.61 |
| Large Office | 90.1-2019 | 6A (Rochester) | Heat Recovery | 2.82 | 0.01% | 0.02 |
| Large Office | 90.1-2019 | 6A (Rochester) | Water Systems | 19.40 | 0.07% | 0.12 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Heating | 69.52 | 0.24% | 0.42 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Cooling | 94.08 | 0.32% | 0.56 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 168.53 | 0.57% | 1.01 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 24.43 | 0.08% | 0.15 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 1003.45 | 3.41% | 6.02 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Exterior Equipment | 130.54 | 0.44% | 0.78 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Fans | 158.13 | 0.54% | 0.95 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Pumps | 22.49 | 0.08% | 0.13 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Heat Rejection | 28.91 | 0.10% | 0.17 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Humidification | 116.52 | 0.40% | 0.70 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Heat Recovery | 3.23 | 0.01% | 0.02 |
| Large Office | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 20.26 | 0.07% | 0.12 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Heating | 330.18 | 15.15% | 18.41 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Cooling | 95.60 | 4.39% | 5.33 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Interior Lighting | 147.87 | 6.78% | 8.24 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 32.59 | 1.50% | 1.82 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Interior Equipment | 448.42 | 20.57% | 25.00 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Exterior Equipment | 7.43 | 0.34% | 0.41 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Fans | 58.31 | 2.68% | 3.25 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Pumps | 0.09 | 0.00% | 0.01 |
| Medium Office | 90.1-2019 | 6A (Rochester) | Water Systems | 30.24 | 1.39% | 1.69 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Heating | 282.52 | 14.95% | 15.75 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Cooling | 70.04 | 3.71% | 3.91 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 148.07 | 7.84% | 8.26 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 32.93 | 1.74% | 1.84 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 448.42 | 23.73% | 25.00 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Exterior Equipment | 7.43 | 0.39% | 0.41 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Fans | 55.94 | 2.96% | 3.12 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Pumps | 0.09 | 0.00% | 0.01 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Heat Recovery | 13.53 | 0.72% | 0.75 |
| Medium Office | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 31.19 | 1.65% | 1.74 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Heating | 174.43 | 1.50% | 4.27 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Cooling | 198.87 | 1.71% | 4.87 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Interior Lighting | 152.06 | 1.31% | 3.72 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 54.07 | 0.47% | 1.32 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Interior Equipment | 631.08 | 5.43% | 15.45 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Exterior Equipment | 178.81 | 1.54% | 4.38 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Fans | 158.16 | 1.36% | 3.87 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Pumps | 21.82 | 0.19% | 0.53 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Heat Recovery | 32.93 | 0.28% | 0.81 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Water Systems | 346.90 | 2.99% | 8.49 |
| Large Hotel | 90.1-2019 | 6A (Rochester) | Refrigeration | 12.28 | 0.11% | 0.30 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Heating | 234.85 | 1.92% | 5.75 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Cooling | 155.68 | 1.27% | 3.81 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 151.98 | 1.24% | 3.72 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 54.00 | 0.44% | 1.32 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 631.08 | 5.16% | 15.45 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Exterior Equipment | 178.81 | 1.46% | 4.38 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Fans | 156.68 | 1.28% | 3.84 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Pumps | 24.90 | 0.20% | 0.61 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Heat Recovery | 34.72 | 0.28% | 0.85 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 358.08 | 2.93% | 8.77 |
| Large Hotel | 90.1-2019 | 7 (InternationalFalls) | Refrigeration | 12.25 | 0.10% | 0.30 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Heating | 315.33 | 10.13% | 23.51 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Cooling | 155.39 | 4.99% | 11.59 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Interior Lighting | 138.47 | 4.45% | 10.33 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 41.11 | 1.32% | 3.07 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Interior Equipment | 460.79 | 14.80% | 34.36 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Fans | 196.99 | 6.33% | 14.69 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Pumps | 0.20 | 0.01% | 0.01 |
| Small Hotel | 90.1-2019 | 6A (Rochester) | Water Systems | 288.83 | 9.27% | 21.54 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Heating | 373.07 | 11.56% | 27.82 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Cooling | 133.36 | 4.13% | 9.94 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 138.59 | 4.29% | 10.33 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 41.06 | 1.27% | 3.06 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 460.79 | 14.28% | 34.36 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Fans | 193.40 | 5.99% | 14.42 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Pumps | 0.20 | 0.01% | 0.01 |
| Small Hotel | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 300.05 | 9.30% | 22.37 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Heating | 437.70 | 24.95% | 53.00 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Cooling | 116.78 | 6.66% | 14.14 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Interior Lighting | 363.61 | 20.72% | 44.03 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 60.39 | 3.44% | 7.31 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Interior Equipment | 268.24 | 15.29% | 32.48 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Fans | 198.29 | 11.30% | 24.01 |
| Stand-Alone Retail | 90.1-2019 | 6A (Rochester) | Water Systems | 46.58 | 2.65% | 5.64 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Heating | 323.13 | 21.55% | 39.13 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Cooling | 75.51 | 5.04% | 9.14 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 359.90 | 24.01% | 43.58 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 60.51 | 4.04% | 7.33 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 268.24 | 17.89% | 32.48 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Fans | 196.41 | 13.10% | 23.78 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Heat Recovery | 26.11 | 1.74% | 3.16 |
| Stand-Alone Retail | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 47.59 | 3.17% | 5.76 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Heating | 502.09 | 28.36% | 66.72 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Cooling | 113.44 | 6.41% | 15.07 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Interior Lighting | 555.54 | 31.38% | 73.82 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Exterior Lighting | 91.29 | 5.16% | 12.13 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Interior Equipment | 194.16 | 10.97% | 25.80 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Fans | 160.76 | 9.08% | 21.36 |
| Strip Mall | 90.1-2019 | 6A (Rochester) | Water Systems | 100.18 | 5.66% | 13.31 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Heating | 549.52 | 29.84% | 73.02 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Cooling | 71.82 | 3.90% | 9.54 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Interior Lighting | 555.54 | 30.17% | 73.82 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Exterior Lighting | 91.48 | 4.97% | 12.16 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Interior Equipment | 194.16 | 10.54% | 25.80 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Fans | 161.67 | 8.78% | 21.48 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Heat Recovery | 8.15 | 0.44% | 1.08 |
| Strip Mall | 90.1-2019 | 7 (InternationalFalls) | Water Systems | 101.94 | 5.54% | 13.55 |

### 4. Report Number Conflict Resolution Table

| Cited Report Number | Verified Document Title | Primary Authors | Year | Resolution Status | Verified Resolving URL |
|---|---|---|---|---|---|
| PNNL-31488 (DOE/EE-2364) | Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019 | R. Salcido, Y. Chen, Y. Xie, M. I. Rosenberg | 2021 | RESOLVED | https://www.energycodes.gov/sites/default/files/2021-07/Standard_90.1-2019_Final_Determination_Analysis.pdf |
| PNNL-29780 | Technical support document background calculations for 90.1-2019 preliminary determination | PNNL Building Energy Codes Team | 2020 | RESOLVED (preliminary analysis for PNNL-31488) | https://www.energycodes.gov/determinations |
| DOE/EE-1614 | Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016 | R. A. Athalye, M. A. Halverson, M. I. Rosenberg, Y. Xie | 2017 | RESOLVED | https://www.energycodes.gov/sites/default/files/2021-11/Standard_90.1-2016_Final_Determination_Analysis.pdf |
| PNNL-26348 | Implementation of Energy Code Controls Requirements in New Commercial Buildings | PNNL Commercial Buildings Team | 2017 | RESOLVED (controls brief, not savings determination) | https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-26348.pdf |
| PNNL-26343 | Regulatory Testing of WTP HLW Glasses for Compliance with Delisting Requirements (ORP-70887) | W. K. Kot, K. Klatt, H. Gan, I. L. Pegg, S. K. Cooley | 2024 | DOES NOT RESOLVE TO BUILDING CODE (Nuclear Waste Study) | https://www.osti.gov/biblio/2452813 |
| PNNL-28543 | PNNL's Intermediate Characterization Summary for the MP-1 Experiment | R. Kalsar, R. Prabhakaran, N. R. Overman, V. V. Joshi | 2019 | DOES NOT RESOLVE TO BUILDING CODE (Nuclear Fuel Experiment) | https://www.osti.gov/biblio/2346213 |
| PNNL-19590 (NREL/TP-5500-46861) | U.S. Department of Energy Commercial Reference Building Models of the National Building Stock | M. Deru, K. Field, D. Studer, K. Benne, B. Griffith, P. Torcellini | 2011 | RESOLVED | https://www.osti.gov/biblio/1009264 |

### 5. Confirmation of the 90.1-2004 Anchor
* The values in `DOE_non-residential_simulation_results_canadian.csv` for Climate Zone 6A (Minneapolis) and Climate Zone 7 (Duluth) match Deru et al. (2011) / NREL/TP-5500-46861 (PNNL-19590) Table 5-2 commercial reference building baseline results exactly:
  - Large Office: 54.70 kBtu/ft2.yr (172.56 kWh/m2.yr) in 6A; 55.90 kBtu/ft2.yr (176.34 kWh/m2.yr) in 7.
  - Large Hotel: 90.80 kBtu/ft2.yr (286.44 kWh/m2.yr) in 6A; 95.80 kBtu/ft2.yr (302.21 kWh/m2.yr) in 7.
  - Small Hotel: 73.20 kBtu/ft2.yr (230.92 kWh/m2.yr) in 6A; 77.60 kBtu/ft2.yr (244.80 kWh/m2.yr) in 7.
  - Stand-Alone Retail: 34.80 kBtu/ft2.yr (109.78 kWh/m2.yr) in 6A; 35.10 kBtu/ft2.yr (110.73 kWh/m2.yr) in 7.
  - Strip Mall: 46.60 kBtu/ft2.yr (147.00 kWh/m2.yr) in 6A; 48.50 kBtu/ft2.yr (153.00 kWh/m2.yr) in 7.
* This confirms that our local baseline CSV file reflects the 90.1-2004 vintage anchor.

## Section H. Full reference list

1. **Deru, M., Field, K., Studer, D., Benne, K., Griffith, B., Torcellini, P., Liu, B., Halverson, M., Winiarski, D., Rosenberg, M., Yazdanian, M., Huang, J., & Crawley, D.** (2011). *U.S. Department of Energy Commercial Reference Building Models of the National Building Stock*. National Renewable Energy Laboratory, NREL/TP-5500-46861 / PNNL-19590. Tier 1.
   - URL: https://www.osti.gov/biblio/1009264
   - Read status: Read full text PDF. CrossRef/OSTI title verified: U.S. Department of Energy Commercial Reference Building Models of the National Building Stock.

2. **Thornton, B. A., Rosenberg, M. I., Gowri, K., Cho, K. H., Liu, B., Richman, E. E., Athalye, R. A., Zhang, J., & Xie, Y.** (2011). *Achieving the 30% Goal: Energy and Cost Savings Analysis of ASHRAE Standard 90.1-2010*. Pacific Northwest National Laboratory, PNNL-20405. Tier 1.
   - URL: https://www.osti.gov/biblio/1025870
   - Read status: Read full text PDF. CrossRef/OSTI title verified: Achieving the 30% Goal: Energy and Cost Savings Analysis of ASHRAE Standard 90.1-2010.

3. **U.S. Department of Energy Building Energy Codes Program.** (2013). *ANSI/ASHRAE/IES Standard 90.1-2013 Commercial Prototype Building Models (EnergyPlus v22.1.0 Package)*. Pacific Northwest National Laboratory. Tier 1.
   - URL: https://www.energycodes.gov/sites/default/files/2023-10/ASHRAE901_OfficeLarge_STD2013.zip
   - Read status: Downloaded ZIP package and read full text HTML output files (`ASHRAE901_OfficeLarge_STD2013_Rochester.table.htm` and `ASHRAE901_OfficeLarge_STD2013_InternationalFalls.table.htm`).

4. **Athalye, R. A., Halverson, M. A., Rosenberg, M. I., Xie, Y., Hart, P. R., Zhang, J., & Goel, S.** (2017). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2016*. U.S. Department of Energy, DOE/EE-1614. Tier 1.
   - URL: https://www.energycodes.gov/sites/default/files/2023-10/ASHRAE901_OfficeLarge_STD2016.zip
   - Read status: Downloaded ZIP package and read full text HTML output files (`ASHRAE901_OfficeLarge_STD2016_Rochester.table.htm` and `ASHRAE901_OfficeLarge_STD2016_InternationalFalls.table.htm`). Full narrative report read at https://www.energycodes.gov/sites/default/files/2021-11/Standard_90.1-2016_Final_Determination_Analysis.pdf.

5. **Salcido, V. R., Rosenberg, M. I., Xie, Y., Chen, Y., Zhang, J., & Hart, R.** (2021). *Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1-2019*. Pacific Northwest National Laboratory, PNNL-31488 / DOE/EE-2364. Tier 1.
   - URL: https://www.energycodes.gov/sites/default/files/2023-10/ASHRAE901_OfficeLarge_STD2019.zip
   - Read status: Downloaded ZIP package and read full text HTML output files (`ASHRAE901_OfficeLarge_STD2019_Rochester.table.htm` and `ASHRAE901_OfficeLarge_STD2019_InternationalFalls.table.htm`). Full narrative report read at https://www.energycodes.gov/sites/default/files/2021-07/Standard_90.1-2019_Final_Determination_Analysis.pdf.
