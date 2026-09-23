# Sentence length baseline — 3J manuscript chapters

BASELINE (before the rewrite). Rerun the same script after the rewrite and diff against this file.

Rerun command:

```
PYTHONIOENCODING=utf-8 py -3 writing/implementation/IMP/scripts/sentence_length_count.py
```

Script: `writing/implementation/IMP/scripts/sentence_length_count.py` (stripping rules and
sentence-splitting method are documented in its module docstring).

## Summary by chapter

| Chapter file | Total sentences | Sentences >30 words | % >30 words |
|---|---:|---:|---:|
| Chapter_00_FrontMatter.md | 47 | 8 | 17.0% |
| Chapter_01_Introduction.md | 46 | 27 | 58.7% |
| Chapter_02_Datasets.md | 42 | 13 | 31.0% |
| Chapter_03_Methods.md | 95 | 44 | 46.3% |
| Chapter_04_ExperimentalDesign.md | 67 | 24 | 35.8% |
| Chapter_05_Results.md | 68 | 37 | 54.4% |
| Chapter_06_Discussion.md | 28 | 10 | 35.7% |
| Chapter_08_Conclusion.md | 14 | 10 | 71.4% |
| Chapter_09_References.md | 38 | 6 | 15.8% |
| Chapter_10_Supplementary.md | 4 | 0 | 0.0% |
| **TOTAL** | **449** | **179** | **39.9%** |

Worst chapter by share over 30 words: **Chapter_08_Conclusion.md (71.4%)**. Highest raw count of
long sentences: Chapter_03_Methods.md (44). Note Chapter_08_Conclusion.md's high % is on a small
base (14 sentences total).

## 20 longest sentences (overall, across all chapters)

Text is verbatim from the source file (list markers/emphasis markers kept as-is except where the
splitter's own stripping applies). Truncated only where noted, at the 80-word mark.

**#1 — 206 words — `writing/chapters/Chapter_00_FrontMatter.md:7`**

> *Context.* Tall buildings increasingly stack residential, office, retail and hospitality uses inside one structure, yet the occupancy schedules driving their energy models remain single-channel, borrowed from one use and held at code default everywhere else. *Gap.* No published occupancy generator produces multiple independent, jointly-trained presence channels for one mixed-use building, and the energy-use-intensity references used to judge such channels were built for single-use stock, not stacked towers. *Aim.* This study jointly trains one model to generate four independent time-use presence [truncated]

**#2 — 164 words — `writing/chapters/Chapter_05_Results.md:174`**

> `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_longitudinal.csv` - 64 rows (4 channels x 4 cycles x 4 building-city cells); `eui_CFA_kWh_m2`, `energy_pct_vs_2005`, `energy_share_pct`, `area_share_pct`, `share_delta_pp` columns; medians and ranges in Section 5.1 computed in this task across the four building-city cells per channel/cycle from this file. `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv` and `writing/tables/Table_05_eui_bands.md` - Section 5.2, all band values, measured ranges, and the three failing-gate numbers. `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_loadshape_peaks.csv` - 392 rows; Section 5.3 figures computed in this task, `B_central` scenario, `peak_hour_circular`/`wd_peak_hour_circular`, `wd_midday_kW`, `wd_night_kW`, `coincidence_factor` columns, medians and ranges across the four building-city [truncated]

**#3 — 135 words — `writing/chapters/Chapter_03_Methods.md:244`**

> `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`: STEP 1-2 box (AT_RETAIL derivation, no-new-GSS-variable statement), STEP 3 box (list-driven tiler, separate retail CSV), STEP 4 box (three-head Transformer design, loss weights, PCGrad, pos_weight, decode thresholds), STEP 5 box (linkage reuse, retail/hotel population-level fallbacks), STEP 6 box (2030 forecast chain, retail lever bands, hotel SARIMA side-track and `hotel_multiplier` formula), STEP 7 box (Tag-2 dispatch, REPLACE/MODULATE assignment, the wiring gate), STEP 9 box (retail/hotel end-use rules, SCIEU calibration); `## VALIDATION GATES` and `## KEY DESIGN DECISIONS SUMMARY` sections (gate [truncated]

**#4 — 116 words — `writing/chapters/Chapter_04_ExperimentalDesign.md:105`**

> `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py`, lines 1-70 (14-scenario list, the `sens_office_*` shared residential/office axis and its code-level justification, `Default_NECB` tag) and lines 350-367 (hotel deliberately absent from 2005/2010/2015). `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md`: "Etat verrouille au 2026-07-28" table (IDF reuse, 36-byte MTL/CLG delta, channel-isolation), residential-channel correction note (4 channels on Y2022/B_*/sens_*, 3 on historicals, 0 on Default_NECB), "Defaut 3" section (stale output guard, injector-only fingerprint and its Step-7-product blind spot, corrected 2026-07-28), "Defaut 7" section (parsed occupiable-share and total-area figures for both towers). `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, STEP 8 box (two [truncated]

**#5 — 104 words — `writing/chapters/Chapter_04_ExperimentalDesign.md:29`**

> Figure 1 now draws nine boxes on one row (the generated replacement drew twelve, with STEP 5, 6 and 7 each twice and one box with no title); Figure 4's before/after panels and Figure 6's wiring-gate card carry their text; Figure S2 carries all nine scenario-lever values instead of "low / default / high"; the graphical abstract's peak-hour panel now places the four channel peaks at 12.1, 11.9, 12.3 and 18.9 h with the whole building at ~15 h, which [truncated]

**#6 — 93 words — `writing/chapters/Chapter_08_Conclusion.md:5`**

> First, the four populations do not behave as one occupant inside one envelope, and the difference reaches the building rather than stopping at the occupancy model: the four channels peak at four different hours, with the hotel channel roughly seven hours after the midday cluster formed by the other three and the whole-building peak coincident with none of them; their weekday day-to-night structure differs by an order of magnitude across channels and inverts outright for hotel; and they move in [truncated]

**#7 — 90 words — `writing/chapters/Chapter_08_Conclusion.md:7`**

> The limitations set out above, an occupancy frame that cannot see hotel guests or retail staff, internal-gain parameters carried over unchanged from a single office reference, and a domestic-hot-water plant whose capacity pinning defeats a global correction, bound how far the present results generalise, and several of them point directly at what a following study would need to build: reference bands constructed for, and validated against, buildings that stack more than one use, rather than borrowed from single-use stock and [truncated]

**#8 — 88 words — `writing/chapters/Chapter_00_FrontMatter.md:7`**

> Three of four channel EUI gates fail: the uninjected office control alone scores 85.45 kWh/m2/yr against a floor of 100; the hotel gate splits into two prototype clusters 84.64 kWh/m2/yr apart, 70.5% of the band width, with the 300 ceiling inside that gap; the retail median sits 5.47% below its floor. *Impact.* These failures are findings about reference-band applicability to mixed-use towers, not model error, reported at full strength with no band widened to pass them.<!-- BUILD NOTE RESOLVED 2026-08-08 [truncated]

**#9 — 81 words — `writing/chapters/Chapter_05_Results.md:84`**

> This 5.47 % median-to-floor gap must not be confused with a different, smaller quantity: the retired all-cells rule was itself replaced because it was turning on a margin of only 0.15 % of its floor (a -0.05 % shift in the median, from a separate improvement round, flipped one cell's individual verdict) - that 0.15 % is the decision margin that justified changing the rule, not the distance between the median and the floor, which is the 5.47 % reported [truncated]

**#10 — 75 words — `writing/chapters/Chapter_03_Methods.md:112`**

> And the specified rule was never implementable as written on this data, since two of its five hard-gate families are pool-level quantities computable only after inference and raking; on the observed range its gate clause is inert in any case, the worst epoch clearing PR-AUC 0.518 against a bar of 0.15, F1 0.282 against 0.25, and a raw impossible-state rate of 0.014 % against 0.5 %, so gate-first then argmax reduces to global argmax F1.

**#11 — 74 words — `writing/chapters/Chapter_01_Introduction.md:42`**

> The aim of the study follows directly. *This paper asks what four functionally distinct occupant populations do to a single stacked building when each is carried on its own behavioural signal rather than blended into one, whether a single jointly-trained occupancy model can generate all four, and where the energy-use-intensity references built for single-use stock do, and do not, still apply to the result.* Figure 1 summarises the full pipeline that operationalises the question.

**#12 — 73 words — `writing/chapters/Chapter_01_Introduction.md:5`**

> A mixed-use tower carries households on some floors, an office workforce on others, retail customers at grade, and hotel guests in a separate tower, all sharing one envelope, one central plant, and often one energy meter, yet the occupancy signal driving such a model is still, in current practice, a single channel: one schedule is chosen (most often residential or office), applied uniformly, and the remaining uses are left on their code-default densities.

**#13 — 71 words — `writing/chapters/Chapter_01_Introduction.md:34`**

> Households, a workforce, customers and overnight guests are carried as four independent presence channels through one stacked tower, and the campaign shows they do not behave as one occupant: they peak at different hours of the day, hotel roughly seven hours after the midday cluster of the other three, and they move in different directions across the four survey cycles, retail reversing its own trend while residential stays close to flat.

**#14 — 69 words — `writing/chapters/Chapter_01_Introduction.md:19`**

> Retail presence is pulled down by a longer-running structural shift toward e-commerce: the measured weighted episode-time share of shopping locations in the General Social Survey declines by roughly 25% across the four cycles used in this pipeline (Table 7, L14), a decline this study's own deep-research check found to be internationally normal in direction and comparable in magnitude to the United States, the United Kingdom and the European Union.

**#15 — 69 words — `writing/chapters/Chapter_05_Results.md:3`**

> The four subsections below move from the raw behavioural driver behind each channel (Section 5.1), to its annual energy consequence measured against reference bands, including where that consequence fails the bands (Section 5.2), to its reshaping of the load curve inside a single stacked building (Section 5.3), and finally to how each channel responds when its own 2030 scenario lever, and only its own lever, is moved (Section 5.4).

**#16 — 68 words — `writing/chapters/Chapter_05_Results.md:75`**

> The band ceiling rests on the first-party DOE/PNNL Large Hotel, ASHRAE 90.1-2019 (ASHRAE, 2019) prototype value (284.44 kWh/m2/yr at CZ 6A, 299.28 at CZ 7), which is 1.0 % from the ceiling's original 90.1-2004-lineage anchor of 302.21, so a vintage-mismatch objection does not hold; what remains is that the reference archetype's own city set (Rochester / International Falls) does not match this study's NECB-2017 Montreal / Calgary towers.

**#17 — 68 words — `writing/chapters/Chapter_08_Conclusion.md:3`**

> Answering the first two parts of that question required building a shared-encoder Transformer with three time-use-survey decoder heads and a separate, non-survey side-track for the one use the source survey cannot see, then dispatching all four resulting channels into the same tower geometry through a per-space, exact-match routing key so that a missing channel falls back safely to the untouched code baseline rather than to an undefined state.

**#18 — 67 words — `writing/chapters/Chapter_01_Introduction.md:25`**

> The first stage, published separately, established a single-channel, residential-only occupancy pipeline: General Social Survey time-use cycles harmonized and augmented by a calibrated conditional generator, linked to the Census dwelling stock, and forecast to 2030 through the COVID/work-from-home break, together with the paired stock-scale simulation design used to isolate the behavioural signal (Iseri and Hachem-Vermette, under review a; Iseri and Hachem-Vermette, under review b; Iseri and Hachem-Vermette, 2026).

**#19 — 67 words — `writing/chapters/Chapter_03_Methods.md:226`**

> For Retail, lighting and HVAC-relevant schedules follow the Space's opening hours rather than the customer-presence signal itself, plug load follows the staff schedule (and therefore stays on the NECB baseline, consistent with §3.5), and customer presence modulates only the occupant-driven internal gain; minimum lighting and baseline plug floors are enforced so that an empty-of-customers slot during opening hours is not modelled as a fully unlit, unpowered space.

**#20 — 67 words — `writing/chapters/Chapter_05_Results.md:41`**

> Aggregated across all four cycles and all four building-city cells, Hotel's median share of building energy (44.47 %) runs 24.22 percentage points above its median share of building floor area (20.25 %), while Office's median energy share (21.42 %) runs 13.72 points below its area share (35.14 %); Residential (energy 18.27 % vs area 17.73 %) and Retail (2.56 % vs 3.92 %) sit close to proportional.
