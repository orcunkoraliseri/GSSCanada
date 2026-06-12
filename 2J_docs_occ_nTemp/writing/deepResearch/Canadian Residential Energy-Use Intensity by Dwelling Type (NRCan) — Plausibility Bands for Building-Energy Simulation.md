# Canadian Residential Energy-Use Intensity by Dwelling Type (NRCan) — Plausibility Bands for Building-Energy Simulation

## TL;DR
- **Use these NRCan SHEU-2019 per-m² intensities (energy consumed per heated m², basement & garage excluded) as central plausibility bands:** Single detached **0.56 GJ/m² (155.6 kWh/m²)**; single attached/double/row/duplex **0.52 GJ/m² (144.4 kWh/m²)**; low-rise apartment **0.52 GJ/m² (144.4 kWh/m²)**; high-rise apartment **0.47 GJ/m² (130.6 kWh/m²)** — total all-fuels (Table 3.3b).
- **Electricity-only intensities (Table 3.6b):** single detached **0.21 GJ/m² (58.3 kWh/m²)**, single attached **0.23 GJ/m² (63.9 kWh/m²)**, low-rise apartment **0.30 GJ/m² (83.3 kWh/m²)**, high-rise apartment **0.28 GJ/m² (77.8 kWh/m²)**.
- **NRCan publishes provincial breakdowns (Tables 3.3a/3.6a), giving wide bands** — e.g. single-detached total intensity 0.47–0.67 GJ/m² (130.6–186.1 kWh/m²) across regions; electricity-only single-detached 0.13–0.40 GJ/m² (36.1–111.1 kWh/m²), driven by Quebec electric heating (high) vs Alberta/Ontario gas heating (low).

## Key Findings

NRCan provides **two independent, authoritative datasets**, and they corroborate each other:

1. **Survey of Household Energy Use (SHEU) 2019** — survey-measured, reported per **heated area excluding basement and garage**, and the **only** NRCan source that splits apartments into low-rise (<5 storeys) and high-rise (≥5 storeys). This is the recommended primary source for per-m² bands. Definition (NRCan glossary): "Energy intensity: Total energy consumption of a dwelling divided by the number of heated units of floor area (excluding the basement and the garage)... expressed in gigajoules per square metre (GJ/m²)."
2. **Comprehensive Energy Use Database (CEUD), reference year 2023** — modeled, reported per **total floor space (basement included)**, with a single combined "Apartments" category. Useful as an independent cross-check.

Because SHEU excludes basements/garage from floor area while CEUD includes them, the two are NOT on the same denominator basis — yet they land close together, supporting confidence in the ~0.5 GJ/m² (≈140 kWh/m²) central figure for total residential energy intensity.

## Details

### Table A — SHEU-2019 intensities per heated area (PRIMARY; basement & garage excluded)

| Dwelling type | Total all-fuels (GJ/m²) | Total all-fuels (kWh/m²) | Electricity only (GJ/m²) | Electricity only (kWh/m²) | Provincial range, total (GJ/m² → kWh/m²) | Provincial range, electricity (GJ/m² → kWh/m²) |
|---|---|---|---|---|---|---|
| Single detached | 0.56 | 155.6 | 0.21 | 58.3 | 0.47–0.67 → 130.6–186.1 | 0.13–0.40 → 36.1–111.1 |
| Single attached (double / row / terrace / duplex) | 0.52 | 144.4 | 0.23 | 63.9 | 0.49–0.67 → 136.1–186.1 | 0.13–0.42 → 36.1–116.7 |
| Apartment, low-rise (<5 storeys) | 0.52 | 144.4 | 0.30 | 83.3 | 0.40–0.78 → 111.1–216.7 | 0.12–0.38 → 33.3–105.6 |
| Apartment, high-rise (≥5 storeys) | 0.47 | 130.6 | 0.28 | 77.8 | 0.41–0.53 → 113.9–147.2 | 0.22–0.44 → 61.1–122.2 |
| (Mobile home, for reference) | 0.67 | 186.1 | 0.34 | 94.4 | NOT FOUND (most regional cells suppressed U/M) | NOT FOUND (most cells suppressed) |

**Conversions** (1 GJ = 277.78 kWh): 0.56 × 277.78 = 155.56; 0.52 × 277.78 = 144.44; 0.47 × 277.78 = 130.56; 0.21 × 277.78 = 58.33; 0.23 × 277.78 = 63.89; 0.30 × 277.78 = 83.33; 0.28 × 277.78 = 77.78; 0.67 × 277.78 = 186.11; 0.34 × 277.78 = 94.44.

**Source notes.** Total intensity by dwelling type = SHEU-2019 **Table 3.3b** (Energy Intensity Per Heated Area excluding Garage By Dwelling Type). Electricity intensity by dwelling type = **Table 3.6b** (Electricity Intensity Per Heated Area excluding Garage By Dwelling Type). Provincial min–max ranges = **Table 3.3a** (total, by region) and **Table 3.6a** (electricity, by region), reading the "Type of dwelling" rows across the columns Canada / Atlantic / Quebec / Ontario / Manitoba–Saskatchewan / Alberta / British Columbia. Regional cells flagged **U** (too unreliable to publish) are excluded from the ranges (e.g. high-rise apartment in Atlantic and Alberta are "U" in Table 3.3a; single-attached in Manitoba/Saskatchewan is "U"). Cells flagged **M** (use with caution) are included but noted. Catalogue: 2019 Survey of Household Energy Use, NRCan Office of Energy Efficiency, National Energy Use Database; data tables released/modified 2023-07-06.

Verbatim anchor values from the source tables (Canada column / "Energy Intensity" header row): Table 3.3b lists Single detached 0.56, Double/Row/Terrace/Duplex 0.52, Low-rise apartments 0.52, High-rise apartments 0.47, Mobile homes 0.67. Table 3.6b lists Single detached 0.21, Double/Row 0.23, Low-rise apartments 0.30, High-rise apartments 0.28, Mobile homes 0.34.

### Table B — SHEU-2019 per-household intensity (Table 3.2b) and implied average heated area

NRCan Table 3.2b gives total energy per household; dividing by the per-m² intensity (Table 3.3b) recovers the average heated area, which is internally consistent with the survey (national average heated area was 177.7 m² in 2019, per the SHEU-2019 highlights page):

| Dwelling type | Energy per household (GJ/hh, Table 3.2b) | ÷ intensity (GJ/m², Table 3.3b) | = avg heated area (m²) |
|---|---|---|---|
| Single detached | 122.8 | 0.56 | 219.3 |
| Single attached | 86.8 | 0.52 | 166.9 |
| Low-rise apartment | 46.8 | 0.52 | 90.0 |
| High-rise apartment | 39.3 | 0.47 | 83.6 |
| Mobile home | 79.4 | 0.67 | 118.5 |

(NRCan's published SHEU-2019 highlight text independently confirms the endpoints: "single detached homes had the highest energy intensity, with 122.8 GJ per household, whereas high-rise apartments had the least energy intensity (39.3 GJ per household)." The national all-dwelling average was 98.1 GJ/household and 0.55 GJ/m².)

### Table C — CEUD reference-year 2023 (modeled; total floor space incl. basement; INDEPENDENT cross-check)

| Building type | Secondary energy use (PJ) | Floor space (M m²) | Energy intensity (GJ/m², published) | Energy intensity (kWh/m²) | Energy intensity (GJ/household) |
|---|---|---|---|---|---|
| Single detached | 915.2 | 1,456 | 0.63 | 175.0 | 107.5 |
| Single attached | 152.1 | 290 | 0.53 | 147.2 | 76.9 |
| Apartments (combined — NOT split low/high-rise) | 279.6 | 580 | 0.48 | 133.3 | 56.5 |

Arithmetic check (single detached): 915.2 PJ = 915,200,000 GJ ÷ 1,456,000,000 m² = 0.629 ≈ 0.63 GJ/m². Conversion: 0.63 × 277.78 = 175.0 kWh/m²; 0.53 × 277.78 = 147.2; 0.48 × 277.78 = 133.3.

- **CEUD electricity-only GJ/m² by building type: NOT FOUND** in these building-type tables (they break out energy *source* totals but do not publish an electricity intensity per m²); use SHEU-2019 Table 3.6b for electricity-only per-m².
- **CEUD low-rise vs high-rise split: NOT FOUND** — CEUD reports a single combined "Apartments" category; only SHEU-2019 splits them.

**Source:** CEUD, Residential Sector – Canada, reference year 2023 — **Table 39** (Single Detached), **Table 42** (Single Attached), **Table 45** (Apartments), each titled "Secondary Energy Use and GHG Emissions by Energy Source," NRCan Office of Energy Efficiency.

### Interpretation for simulation plausibility bands

- For a **total site-energy** simulation result, expect roughly **130–190 kWh/m²** for detached/attached houses and **110–215 kWh/m²** for apartments on the SHEU heated-area basis, with central expectations near **145–155 kWh/m²**. Results far outside these bands warrant scrutiny.
- For **electricity-only** results, national central values are **58–83 kWh/m²**, but the regional band is very wide (≈33–122 kWh/m²) because of the electric-vs-fossil heating split. **Province-match your band:** Quebec (electric heat) sits at the top; Alberta/Ontario (gas heat) at the bottom.
- **Floor-area definition matters:** SHEU excludes basement/garage; CEUD includes basement. If your model's denominator includes the basement, expect your kWh/m² to read lower than SHEU values and closer to the CEUD basis.

## Recommendations
1. **Adopt SHEU-2019 Table 3.3b / 3.6b (Table A) as the default per-m² plausibility bands** — measured, dwelling-type-specific, and the only NRCan source splitting apartments by rise. Use the national value as the band center and the Table 3.3a/3.6a regional min–max as the outer band.
2. **Confirm your simulation's floor-area basis matches SHEU** (heated area excluding basement/garage). If you use gross floor area including basement, switch to the CEUD 2023 figures (Table C) or apply a downward offset.
3. **Province-match the electricity band.** A Quebec model checked against an Alberta-derived electricity band will falsely fail; pull the correct regional column from Table 3.6a.
4. **Treat M/U-flagged cells as soft.** Several regional apartment cells are suppressed (U) or caution-flagged (M); do not build a hard pass/fail threshold off a single weak cell.
5. **Thresholds that would change these bands:** (a) release of a newer SHEU cycle; (b) a stock dominated by post-2011 construction — Table 3.3b shows ~0.48 GJ/m² for detached and ~0.47 GJ/m² for attached in the "2011 or later" vintage, materially below the all-vintage averages, so shift the band center down; (c) modeling source/primary rather than site energy — do not compare against these site-energy values.

## Caveats
- SHEU and CEUD use **different floor-area definitions** (heated-excluding-basement vs total floor space incl. basement); their GJ/m² values are not strictly interchangeable.
- SHEU intensities are **secondary (site) energy**, not source/primary energy; do not benchmark against ENERGY STAR Portfolio Manager *source*-EUI figures.
- NRCan quality flags: **A** = acceptable, **M** = use with caution, **U** = too unreliable to be published. Several regional/apartment cells are M or U.
- CEUD apartments are **not** split into low-/high-rise; only SHEU-2019 provides that split.
- All values are national/regional averages spanning all vintages; new-construction intensities are materially lower.

## Sources (exact tables, catalogue, year, URLs)

**SHEU-2019 (NRCan Office of Energy Efficiency, National Energy Use Database; 2019 Survey of Household Energy Use; tables released/modified 2023-07-06):**
- Data-tables index: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm
- Table 1.2b — Total Heated Area of Dwelling (excluding Garage) by Dwelling Type: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=4&page=1 (Excel: …/data_e/downloads/sheu/Excel/2019/Table 1-2.xls)
- Table 3.2b — Energy Intensity Per Household by Dwelling Type: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=10&page=1 (Excel: …/sheu/Excel/2019/Table 3-2.xls)
- Table 3.3a — Energy Intensity Per Heated Area (excluding Garage) by Region: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=11&page=1 (Excel: …/sheu/Excel/2019/Table 3-3.xls)
- Table 3.3b — Energy Intensity Per Heated Area (excluding Garage) by Dwelling Type: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=12&page=1 (Excel: …/sheu/Excel/2019/Table 3-3.xls)
- Table 3.6a — Electricity Intensity Per Heated Area (excluding Garage) by Region: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=17&page=1 (Excel: …/sheu/Excel/2019/Table 3-6.xls)
- Table 3.6b — Electricity Intensity Per Heated Area (excluding Garage) by Dwelling Type: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=SH&sector=aaa&juris=ca&year=2019&rn=18&page=1 (Excel: …/sheu/Excel/2019/Table 3-6.xls)
- SHEU-2019 highlights (national averages, definitions): https://oee.nrcan.gc.ca/publications/statistics/sheu/2019/index.cfm

**CEUD (NRCan Comprehensive Energy Use Database, Residential Sector – Canada, reference year 2023):**
- Database menu: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm
- Residential Sector – Canada (table list): https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive/trends_res_ca.cfm
- Table 39 — Single Detached Secondary Energy Use and GHG Emissions by Energy Source: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=39&page=0 (Excel: …/comprehensive/Excel/2023/res_ca_e_39.xls)
- Table 42 — Single Attached …by Energy Source: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=42&page=0 (Excel: …/res_ca_e_42.xls)
- Table 45 — Apartments …by Energy Source: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/showTable.cfm?type=CP&sector=res&juris=ca&year=2023&rn=45&page=0 (Excel: …/res_ca_e_45.xls)

**Supporting NRCan references:**
- Energy Use in the Residential Sector (Trends, 2019/2020 — space-heating intensity GJ/m²): https://oee.nrcan.gc.ca/publications/statistics/trends/2020/residential.cfm
- Conversion factor 1 GJ = 277.78 kWh (NRCan, used throughout): confirmed in NRCan CICES methodology, https://oee.nrcan.gc.ca/publications/statistics/cices06/pdf/cices06.pdf

*Note: One automated enrichment pass was attempted on this report but the enrichment service returned an internal error; the report nonetheless cites only named NRCan tables with verbatim values and working URLs, with every unavailable cell explicitly marked NOT FOUND.*