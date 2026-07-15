# From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)

**Authors:** O. Iseri and C. Hachem-Vermette · Concordia University

---

## Aim of the Study

Energy models for buildings have long assumed that people's daily routines stay fixed over time. In reality, the pandemic changed not just *how much* energy Canadian households use, but *when* they use it — because working from home kept people home through midday hours when they used to be absent. This study asks a concrete question: if we track how occupant behaviour has actually shifted from 2005 to the present and project those shifts forward to 2030, does the daily *shape* of residential electricity demand change in a way that matters for the electricity grid?

To answer that, the study builds a nine-step pipeline that starts with real survey data — four rounds of Statistics Canada's General Social Survey Time-Use program (64,061 household diaries recording what Canadians did in 10-minute slices) — and links them to 2021 Census records to represent the actual housing stock. A machine-learning model trained on those diaries generates realistic daily schedules for 144,507 households. Those schedules are then fed into building energy simulation software (EnergyPlus) for 6,000 paired computer runs. The "paired" design is key: the same fifty households are simulated under each survey cycle, so any difference in the electricity profile is directly attributable to changes in occupant behaviour alone, not to differences in the houses or the weather.

The central finding is that work-from-home adoption fills the midday lull in electricity demand and flattens the daily load curve — but the evening peak, which occurs around 17:30, stays firmly in place. Annual electricity use rises only modestly (+1.4 to +2.6 % across the pandemic break). What changes is *when* during the day that electricity is drawn, and that timing question is precisely what matters for grid planning, demand response, and peak-load management.

---

## The Pipeline at a Glance

**Figure 1.** — **End-to-end occupancy-to-energy pipeline (Steps 1–9).** Block schematic from the four GSS Time-Use cycles and the Census PUMF through harmonization and 30-minute diary construction, generative day-type augmentation, Census linkage, longitudinal forecasting to 2030, BEM schedule conversion, paired Monte-Carlo simulation, and activity-resolved end-use loads; each block labelled with its section number and the key validation gate it passes.

![Figure 1](../figures/Figure_01_pipeline.png)

---

## Results

---

### 5.1 Non-Stationarity in At-Home Occupancy

**Figure 5.** — **Occupancy driver: diurnal at-home shift.** Average fraction of households at home across the hours of the day, weekday and weekend panels, one line per survey/forecast cycle (2005–2030), with the work-from-home midday window shaded; the behavioural starting point traced into electricity demand.

![Figure 5](../figures/Figure_05_occupancy_driver.png)

---

### 5.2 Annual Energy Magnitude and Benchmark Plausibility

**Table 5.** — Stock-weighted annual energy use intensity per archetype against the NRCan SHEU-2019 regional-average intensity ranges (secondary plausibility cross-check), ordered by envelope-to-occupant ratio.

| Archetype | SHEU dwelling type | Simulated EUI (kWh/m²) | SHEU national central (kWh/m²) | SHEU band (regional range, kWh/m²) | Within band? |
|---|---|---|---|---|---|
| SingleDetached | Single detached | 208 | 155.6 | 130.6 – 186.1 | **No — above upper (≈ +12%)** |
| OtherDwelling | Single attached (double / row / terrace / duplex) | 128 | 144.4 | 136.1 – 186.1 | **Marginal — ≈ 6% below lower** |
| MidRise | Apartment, low-rise (< 5 storeys) | 152 | 144.4 | 111.1 – 216.7 | Yes |
| HighRise | Apartment, high-rise (≥ 5 storeys) | 117 | 130.6 | 113.9 – 147.2 | Yes |

**Notes:**
- **Simulated EUI** values are from the Step-8 corrected campaign. Exact recomputed values: SingleDetached 208.13, MidRise 151.79, OtherDwelling 127.80, HighRise 117.01 kWh/m² (rounded to integers above; ordered by envelope-to-occupant ratio).
- **SHEU bands** are sourced from the NRCan 2019 Survey of Household Energy Use — national central from Table 3.3b (Energy Intensity Per Heated Area excluding Garage, by Dwelling Type); regional range from Table 3.3a (same metric, by region). Total all-fuels per heated area excluding basement and garage.
- **Floor-area basis reconciled.** The EUI denominator is the EnergyPlus Net Conditioned Building Area — conditioned zones only, with the unconditioned basement and attic excluded — which coincides with SHEU's heated-area basis. For SingleDetached the simulated and SHEU denominators are the same (approximately 221 m²), so the approximately +12% over-band reading is not a denominator artefact. The elevation is genuine and sits in the space-heating component — a total-energy quantity fixed by the building envelope and climate zone, which (unlike equipment + lighting) was not SHEU-calibrated. For the apartment archetypes the simulated building EUI divides by floor area that includes common corridors; re-normalizing to per-dwelling-unit area (×1.11) raises MidRise to approximately 168 and HighRise to approximately 130 kWh/m², both still inside their SHEU ranges.
- **What actually passed validation.** The hard calibration gate was on per-household end-use kWh/yr: all 48 dwelling-by-year cells within ±2.7% of SHEU, maximum +2.33% equipment / +2.63% lighting. The EUI-per-m² check above is a secondary plausibility cross-check; on it, two of four archetypes fall outside the SHEU regional-average intensity range. Regional averages smooth within-province variance, so a single cold-zone archetype legitimately can exceed them.
- Ordered by envelope-to-occupant ratio (colder zones higher within each archetype type).

---

### 5.3 Diurnal Load-Shape Reshaping and Peak-Hour Stability

**Figure 6.** — **Diurnal load-shape reshaping under work-from-home.** (a) Average hourly electricity demand over a day, most recent observed cycle vs 2030 forecast, each with a shaded uncertainty band; (b) average hour-by-hour paired within-household difference (forecast − recent), with a confidence band read against the zero line and the work-from-home midday window highlighted; (c) stock-weighted ensemble daily load shape (archetypes/cities combined by stock share), recent vs forecast, with the coincidence factor annotated.

![Figure 6](../figures/Figure_06_loadshape.png)

---

### 5.4 End-Use Resolution: Magnitude Correction without Peak Displacement

**Figure 7.** — **Activity-driven equipment: magnitude correction and intraday shape.** (a) Default versus activity-driven equipment demand — one panel per archetype, single-detached in absolute terms with the annual total held to the survey-based energy anchor and the others normalized to daily mean, each overlaying default vs activity-driven with peak-hour markers; (b) activity-driven equipment diurnal load shape — daily shape of equipment demand per archetype, each curve normalized to its own daily mean, baseline vs activity-driven with peak-hour markers, showing a more pronounced morning rise and sharper evening concentration yet both curves peaking at essentially the same evening hour.

![Figure 7](../figures/Figure_07_activity_equipment.png)
