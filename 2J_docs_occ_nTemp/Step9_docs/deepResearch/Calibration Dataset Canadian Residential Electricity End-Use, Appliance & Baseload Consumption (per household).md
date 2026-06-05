# Calibration Dataset: Canadian Residential Electricity End-Use, Appliance & Baseload Consumption (per household)

*Sources: NRCan Survey of Household Energy Use 2019 (SHEU-2019); NRCan Comprehensive Energy Use Database (CEUD) / Energy Use Data Handbook, Residential Sector (2023 data release); Hydro-Québec; Ferguson/Fung/Ugursal Canadian standby study. Conversion: 1 GJ = 277.78 kWh. Access date: 2 June 2026.*

## TL;DR
- **Quebec households consume the most residential electricity in Canada at 63.9 GJ/hh (≈17,750 kWh/yr), "more than double the consumption in Alberta (24.2 GJ per household) and Ontario (29.8 GJ per household)"** (SHEU-2019); the spread is driven almost entirely by electric space heating, not by appliances or lighting.
- A behavioural model's **"always-on" baseload (refrigerator + freezer + standby/networking) totals roughly 1,000–1,200 kWh/hh/yr** — fridge stock-average UEC 448 kWh (≈51 W continuous), freezer 343 kWh (≈39 W), networking/standby ≈400–430 kWh (≈45–49 W) — about **30% of the appliance block**.
- **Appliances + lighting equal ≈18.6% of total residential energy** and constitute essentially the entire non-thermal electricity load (within it, appliances ≈77%, lighting ≈23%); national lighting is ≈1,053 kWh/hh/yr and is falling with LED adoption.

## Key Findings
- **Provincial electricity intensity (SHEU-2019 Table 3.5a) [Published]**: Quebec 63.9 GJ, Atlantic 48.0, Manitoba/Saskatchewan 39.9, British Columbia 31.9, Ontario 29.8, Alberta 24.2; Canada 39.8 GJ/hh. Converting at 277.78 kWh/GJ: Quebec 17,750; Atlantic 13,333; MB/SK 11,083; BC 8,861; Ontario 8,278; Alberta 6,722; Canada 11,055 kWh/hh/yr. Statistics Canada's parallel Households and the Environment Survey (2019) corroborates this spread, reporting Quebec highest (63.6 GJ/hh) "followed closely by those in Newfoundland and Labrador (60.4 gigajoules per household)," with Alberta (24.3) and Ontario (29.7) lowest.
- **The provincial spread is a heating-fuel story.** Quebec, Atlantic and BC have high electric-heat penetration, so electricity carries space heating; Ontario, Alberta and the Prairies heat mostly with natural gas, so their electricity is dominated by the non-thermal block (appliances + lighting + water heating + cooling).
- **Appliance UEC (CEUD Handbook Table 16, 2023) [Published]** has fallen sharply: stock-average refrigerator 448 kWh, freezer 343, dishwasher 73, clothes washer 35, electric dryer 790, electric range 546. New units: refrigerator 458, freezer 307, dishwasher 69, washer 27, dryer 582, range 548.
- **Baseload/standby**: the Canadian benchmark is the NRCan-funded Halifax field study (Ferguson/Fung/Ugursal), which found "the annual average standby energy consumption per household in the sample was estimated to be 427 kWh, which is equivalent to a constant load of 49 W," reducible by 59% to 177 kWh if all >1 W devices were capped at 1 W. Hydro-Québec, citing NRCan, states "In Canada, phantom power use totals about 5.4 TWh, the equivalent of the annual power consumption of 300,000 households," from "between 20 and 40 consumer electronic devices" per home, "responsible for 5 to 20% of your electricity bills."
- **Hydro-Québec cross-check (electric-heat homes) [Published]**: "54% Heating and air-conditioning · 20% Hot water · 18% Appliances and electronics · 5% Lighting · 3% Other."

## Details

### Conversion and base data
All energy converted at **1 GJ = 277.78 kWh** (task-specified). Provincial and dwelling-type totals are from SHEU-2019; end-use and appliance breakdowns are from the CEUD Energy Use Data Handbook (2023 release, data series 2000 + 2013–2023) and CEUD provincial/analysis tables. SHEU national electricity intensity (39.8 GJ) and CEUD national (40.6 GJ) corroborate to within 2%.

**National per-household electricity by end-use, 2023** (CEUD Handbook Table 1; total residential electricity 636.8 PJ ÷ 15,668,100 households = 40.64 GJ = 11,290 kWh) [Derived]:
- Lighting (100% electric): 59.4 PJ ÷ 15,668.1k = 3.79 GJ = **1,053 kWh** [Published end-use total; per-hh Derived]
- Space cooling (100% electric): 37.3 PJ ÷ 15,668.1k = 2.38 GJ = **661 kWh**
- Appliances (≈all electric): ~180 PJ ÷ 15,668.1k ≈ 11.5 GJ ≈ **3,200 kWh**
- Space + water heating (electric remainder): 11,290 − 1,053 − 661 − 3,200 = **≈6,380 kWh**

### Table A — Province × End-Use (annual kWh/household)
**Total electricity intensity is [Published]** (SHEU-2019 Table 3.5a, "Electricity Intensity Per Household (excluding Garage) By Region," converted at 277.78 kWh/GJ). URL: `oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=15&page=1`. **End-use columns are [Derived]**: lighting and appliances anchored to national CEUD values; Quebec uses its province-specific CEUD values (higher, because Quebec has essentially no gas appliances and near-universal electric ranges/dryers); space cooling from national CEUD; space + water heating electricity computed as the residual (total − appliances − lighting − cooling).

| Province | Space + water heating (elec) | Space cooling | Appliances | Lighting | TOTAL electricity intensity |
|---|---|---|---|---|---|
| **Quebec** | ≈11,250 [Derived: 17,750 − 4,583 − 1,250 − 681] | 681 [Pub CEUD-QC: 2.45 GJ] | 4,583 [Pub CEUD-QC: 16.5 GJ] | 1,250 [Pub CEUD-QC: 4.5 GJ] | **17,750** [Pub: 63.9 GJ] |
| **Atlantic** | ≈8,100 [Derived: 13,333 − 3,500 − 1,050 − 683] | ~683 [Derived] | ~3,500 [Derived] | ~1,050 [Derived] | **13,333** [Pub: 48.0 GJ] |
| **Manitoba/Saskatchewan** | ≈6,500 [Derived: 11,083 − 3,200 − 1,050 − 333] | ~333 [Derived] | ~3,200 [Derived] | ~1,050 [Derived] | **11,083** [Pub: 39.9 GJ] |
| **British Columbia** | ≈4,200 [Derived: 8,861 − 3,300 − 1,050 − 311] | ~311 [Derived] | ~3,300 [Derived] | ~1,050 [Derived] | **8,861** [Pub: 31.9 GJ] |
| **Ontario** | ≈3,180 [Derived: 8,278 − 3,100 − 1,050 − 950] | ~950 [Derived] | ~3,100 [Derived] | ~1,050 [Derived] | **8,278** [Pub: 29.8 GJ] |
| **Alberta** | ≈1,520 [Derived: 6,722 − 3,200 − 1,050 − 950] | ~950 [Derived] | ~3,200 [Derived] | ~1,050 [Derived] | **6,722** [Pub: 24.2 GJ] |
| **Canada** | ≈6,380 [Derived] | 661 [Pub: 2.38 GJ] | ~3,200 [Derived] | 1,053 [Pub: 3.79 GJ] | **11,055** [Pub: 39.8 GJ] |

*Caveat: SHEU does not publish electricity-by-end-use per province; only the totals are [Published]. The end-use columns are model-grade derivations. For all-electric Quebec homes the Hydro-Québec split (below) is the better calibration anchor.*

**Quebec Hydro-Québec cross-check [Published]** (applies to homes heating both space and water with electricity), applied to the 17,750 kWh total [Derived products]:
- Heating + AC 54% = 9,585 kWh; Water heating 20% = 3,550 kWh; Appliances + electronics 18% = 3,195 kWh; Lighting 5% = 888 kWh; Other 3% = 533 kWh.
- HQ's appliance share (3,195 kWh) is lower than CEUD's 4,583 kWh because CEUD's "appliances" bucket folds in a large "other appliances & electronics" category that HQ reports partly under "Other." HQ further breaks appliances/electronics as: refrigerator 33%, dryer 18%, other 16%, range 15%, freezer 13%, dishwasher 3%, washer 2%.

**Quebec CEUD per-household electricity by end-use [Published, CEUD-QC tables, 2021/2023]:** Lighting 4.5 GJ = 1,250 kWh (Table 3, "Lighting consumes only electricity"); Appliances 16.5 GJ = 4,583 kWh (Table 13, ≈100% electric in QC); Space cooling 2.45 GJ = 681 kWh (2021). Space and water heating electricity are not isolated in the retrieved tables (Table 2 reports total all-fuel space heating 54.5 GJ/hh and water heating 12.8 GJ/hh; in Quebec both are predominantly electric).

### Table B — Dwelling Type × End-Use (annual kWh/household)
**Electricity totals are [Published]** from SHEU-2019 Table 3.5a (dwelling-type rows). **End-use splits are [Published/Derived]** from CEUD Residential Energy-Use Analysis tables (full fuel split, 2023): apartments and mobile homes have published CEUD electricity-by-end-use; single detached and attached use CEUD single-detached end-use totals with electric-share derivation.

| Dwelling type | Space heating (elec) | Water heating (elec) | Space cooling | Appliances | Lighting | TOTAL electricity |
|---|---|---|---|---|---|---|
| **Single detached** | ≈5,600 [Derived residual] | ≈1,300 [Derived] | ~920 [Derived: 28.3 PJ÷8,515.8k] | ~3,700 [Derived: 114.1 PJ÷8,515.8k×elec] | 1,262 [Pub: 36.4 PJ÷8,515.8k = 4.54 GJ] | **12,694** [Pub: 45.7 GJ] |
| **Attached/row/duplex/semi** | ≈4,500 [Derived residual] | ≈1,200 [Derived] | ~800 [Derived] | ~3,200 [Derived] | ~1,050 [Derived] | **10,750** [Pub: 38.7 GJ] |
| **Low-rise apartment** | ≈3,180 [Derived: apt elec shares × total] | ≈1,080 [Derived] | ~180 [Derived] | ~2,400 [Derived] | ~600 [Derived] | **7,417** [Pub: 26.7 GJ] |
| **High-rise apartment** | ≈2,800 [Derived: apt elec shares × total] | ≈960 [Derived] | ~160 [Derived] | ~2,130 [Derived] | ~530 [Derived] | **6,583** [Pub: 23.7 GJ] |
| **Mobile** | ≈6,620 [Pub CEUD: ~23.8 GJ space-heat total] | ≈1,080 [Pub CEUD: 0.9 PJ÷230.9k] | ~720 [Pub CEUD: 0.6 PJ÷230.9k] | ≈3,610 [Pub CEUD: 3.1 PJ÷230.9k = 13.6 GJ] | ≈960 [Pub CEUD: 0.8 PJ÷230.9k] | **11,250** [Pub: 40.5 GJ] |

**Apartment electricity end-use anchors (CEUD Analysis, 2023; total apartment electricity 162.3 PJ ÷ 4,944,900 = 32.8 GJ = 9,116 kWh):** space heating-elec 69.5 PJ = 3,904 kWh; water heating-elec 23.6 PJ = 1,326 kWh; appliances-elec 52.2 PJ = 2,932 kWh; lighting 13.1 PJ = 736 kWh; cooling 3.9 PJ = 219 kWh. Low-rise/high-rise rows apply these apartment electricity shares to each SHEU-published total. *Note: SHEU mobile-home and some apartment cells outside Quebec/Ontario carry "use with caution" (M) flags.*

### Table C — Appliance Unit Energy Consumption (annual kWh/yr) + saturation
Stock-average and new UEC from **CEUD Handbook Table 16 (2023) [Published**; "Unit energy consumption is based on rated efficiency"; dishwasher/washer "exclude hot water requirements"]. URL: `oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=HB&sector=res&juris=00&year=2023&rn=16&page=0`.

| Appliance | Stock-average UEC | New UEC | Ownership / saturation |
|---|---|---|---|
| Refrigerator | 448 [Pub] | 458 [Pub] | Near-universal: 9.08M households one, 5.14M two or more (SHEU-2019 Table 10.1a) |
| Second refrigerator | ~450–1,000 [Derived/Pub fallback: use ≥ stock UEC; pre-1990 units exceed 1,000 kWh per US EIA] | n/a | ≈36% of households have ≥2 fridges (SHEU-2019 Table 10.1a) |
| Freezer | 343 [Pub] | 307 [Pub] | ≈60%: 8.59M of ~14.3M households own a standalone freezer (SHEU-2019 Table 10.2a) |
| Dishwasher | 73 [Pub] | 69 [Pub] | Majority (~55–62% historically; BC highest) |
| Clothes washer | 35 [Pub] | 27 [Pub] | ≈88% |
| Clothes dryer (electric) | 790 [Pub] | 582 [Pub] | ≈88% |
| Electric range/oven | 546 [Pub] | 548 [Pub] | Majority electric (gas common in AB/ON) |
| Other appliances & electronics | ≈1,400 [Derived: CEUD "Other Appliances" 78.9 PJ ÷ 15,668.1k = 5.04 GJ] | n/a | Near-universal: TVs 14.6M, computers/tablets 13.8M, cellphones 13.7M households (SHEU-2019); network devices "typically always turned on" |

Gas appliance UEC-equivalents (Handbook T16, kWh-equivalent) [Published]: gas dryer 880, gas range 1,226.

**Provincial freezer saturation (SHEU-2019 Table 10.2a, households with freezer ÷ regional households) [Derived from Published counts]:** Atlantic ≈76% (645k+71k of ~939k), Manitoba/Saskatchewan high (~70%), Quebec ≈55%, Ontario ≈54%, Alberta and BC moderate. **Household-size note:** SHEU Tables 10.x-b give appliance counts by household size (1, 2, 3, 4+ members); ownership of second fridges and freezers rises with household size.

### Table D — Always-On / Baseload Components (hold flat in a behavioural model)
| Component | Continuous wattage (W) | Annual kWh | % of appliance block |
|---|---|---|---|
| Refrigerator (stock) | ≈51 W [Derived: 448,000 Wh ÷ 8,760 h] | 448 [Pub] | ~14% |
| Freezer (stock, if owned) | ≈39 W [Derived: 343,000 ÷ 8,760] | 343 [Pub] | ~11% (×0.60 saturation ≈ 206 kWh fleet-average) |
| Networking/standby (phantom) | ≈45–49 W [Pub: 427 kWh ÷ 8,760 = 48.7 W] | ~400–430 [Pub] | ~12% |
| **Total always-on** | **≈135–140 W** | **≈1,000–1,200** | **~30% of the appliance block** |

Baseload notes:
- The refrigerator continuous figure (51 W) is the duty-cycle average implied by the 448 kWh stock UEC; nameplate compressor draw is higher (typically 100–200 W cycling, "divide by 3" rule of thumb).
- **Standby (Canadian primary source):** Ferguson/Fung/Ugursal, "Standby power requirements of household appliances in Canada" (75 houses, Halifax; NRCan-funded): **427 kWh/household/yr ≈ 49 W continuous**, reducible by 59% to 177 kWh if all >1 W devices were capped at 1 W. The authors note this excludes major and hard-wired appliances, so the true figure is likely slightly higher.
- **Standby (national scale):** Hydro-Québec / NRCan "Standby power: When 'off' means on" (2014): "In Canada, phantom power use totals about 5.4 TWh, the equivalent of the annual power consumption of 300,000 households"; "between 20 and 40 consumer electronic devices" per home; phantom power "could be responsible for 5 to 20% of your electricity bills." NRCan brochure separately: standby "amounts to at least 5 percent of the electricity used in the average Canadian home."
- **US/IEA/LBNL fallbacks:** LBNL — standby is 5–10% of residential use; Meier & Huber — average US home ≈50 W / 440 kWh/yr; rule of thumb — each 1 W of continuous draw ≈ 9 kWh/yr.

### Lighting
- **National 2023: 1,053 kWh/hh/yr** (CEUD Handbook T1, 59.4 PJ ÷ 15,668.1k = 3.79 GJ) [Published end-use total; per-hh Derived].
- By segment: Quebec 1,250 kWh (4.5 GJ); single detached 1,262 kWh (4.54 GJ); apartment 736 kWh; mobile ≈960 kWh.
- **Trend:** per-household lighting fell ≈25% (from 4.7 GJ to 3.5 GJ, 2000→2020) as LEDs displaced incandescents. SHEU-2019: "Light-emitting diodes (LED) were the most used lightbulbs across Canada, with almost 9.9 million households using them, followed closely by incandescent with 9.7 million households. The number of households using LEDs increased by 68% since 2015 (5.9 million households)." Average home ≈40 bulbs (Hydro-Québec).

### Appliances + Lighting shares
- **(a) Of total residential energy (2023, Handbook T1):** Appliances 195.8 PJ + Lighting 59.4 PJ = 255.2 PJ ÷ 1,372.4 PJ total = **18.6%** [Derived].
- **(b) Of the non-thermal electricity remainder** (excluding space heating, space cooling, water heating): appliances + lighting constitute essentially the entire remainder; within it, **appliances ≈77% and lighting ≈23%** [Derived: 195.8 ÷ 255.2].

## Recommendations
1. **Anchor each province to the SHEU-2019 Table 3.5a total electricity intensity** — the only fully published per-household electricity numbers: Quebec 17,750, Atlantic 13,333, MB/SK 11,083, BC 8,861, Ontario 8,278, Alberta 6,722 kWh/hh/yr. Treat these as hard calibration targets and reconcile your model's annual electricity to within ±10%.
2. **Disaggregate end-uses with province-specific heating-fuel logic, not one national split.** In Quebec/Atlantic/BC, electric space heating dominates the remainder; in Ontario/Alberta/Prairies, treat the electricity load as predominantly non-thermal (appliances + lighting + water heating + cooling). For all-electric Quebec homes, use the Hydro-Québec 54/20/18/5/3 split directly.
3. **Hold the baseload flat at ≈1,000–1,200 kWh/hh/yr** (fridge 448 + freezer ≈206 fleet-average + standby ≈400). Set continuous wattages: fridge 51 W, freezer 39 W, standby 45–49 W. This is the floor a behavioural intervention cannot move.
4. **Use stock-average UEC for the installed fleet and new UEC for retrofit/new-build scenarios** (Handbook T16). The stock/new gap is largest for clothes washers (35 vs 27) and dryers (790 vs 582); refrigerators have essentially converged (448 vs 458).
5. **Triggers to revisit the calibration:** if a province's modelled electricity diverges >10% from its SHEU total, re-examine the electric-heating share first (the largest and most variable component). If migrating to a newer CEUD release (2024+), refresh UEC and lighting (both trending down) before re-running.

## Caveats
- SHEU-2019 publishes per-household electricity *totals* by province and dwelling type but **not** an electricity-by-end-use matrix; the end-use columns in Tables A and B are derived and should be treated as model-grade, not published.
- CEUD's "appliances" category includes a large "other appliances & electronics" bucket (≈1,400 kWh/hh), which inflates appliance totals relative to utility splits like Hydro-Québec's. Decide which definition your model uses and apply consistently.
- The Canadian standby figure (427 kWh) is from an early-2000s Halifax study; modern per-device standby is lower (<1 W for many devices) but device counts are far higher, so total household standby today is plausibly similar — use with the noted uncertainty and treat 400–430 kWh as a central estimate within a 200–500 kWh range.
- SHEU-2019 reliability flags: several provincial dwelling-type cells are "use with caution" (M) or "too unreliable to publish" (U), especially mobile homes and apartments outside Quebec/Ontario (e.g., Atlantic high-rise, Prairie duplex).
- The CEUD has been updated to a 2023 data year (2000 + 2013–2023 series); some provincial appliance-type tables still display a 2021 vintage, and the appliance-bucket definition differs slightly between the Handbook end-use table and the provincial Table 13 (e.g., Quebec appliances 55.3 PJ in the by-end-use table vs 61.1 PJ in the dedicated appliance-type table for 2021) — reconcile before fine calibration.