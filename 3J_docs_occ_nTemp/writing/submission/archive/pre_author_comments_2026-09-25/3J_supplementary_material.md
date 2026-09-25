# Supplementary material

*From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005-2030)*

## S.1 Checkpoint selection

The delivered occupancy model was selected by a composite validation score rather than by the rule specified before training. The specified rule was to discard every checkpoint that did not pass a hard check, then to take the highest retail F1 among the rest. The training code instead kept the checkpoint with the lowest composite of the mean Jensen-Shannon divergence and the mean gap in presence rate across the three heads:

$$S = \overline{\mathrm{JS}} + \tfrac{1}{2}\cdot\frac{g_{\mathrm{home}} + g_{\mathrm{work}} + g_{\mathrm{retail}}}{3}$$

The score contains neither the precision-recall area nor F1. The two rules pick different epochs in four of five seeds. The delivered seed ranks first of five on the composite and fourth of five on retail F1. It is 0.0218 retail F1 below the specified rule's choice, 5.6 % in relative terms and 0.16 standard deviations of the spread across seeds.

The model was not re-selected, for an evidential reason. Both rules rank epochs on teacher-forced validation columns. A separate person-level test showed that those columns cannot see person-level retail skill. The hard-check clause of the specified rule could also not be applied as written. Two of its five check families are pool-level quantities that exist only after inference and adjustment. On the observed range the clause would not have removed any epoch. The worst epoch reached a precision-recall area of 0.518 against a bar of 0.15, an F1 of 0.282 against 0.25, and a raw impossible-state rate of 0.014 % against 0.5 %.

## S.2 Injection checks

The field check on occupant objects has its origin in the two-channel version. There, a modulated occupancy schedule was attached to the wrong field of the occupant object. That field still existed and still held a valid schedule. Every input-side check then available passed, including schedule presence, syntax and non-empty fields. The error flattened the office channel's daily signal. It was found only when office output did not differ from an unmodulated run. The check now confirms the correct field on every modulated space.

An input-side check cannot show that outputs carry the scenario signal. Two output-side checks were therefore added. The first requires scenarios that should differ to give different outputs. The second re-runs a simulation whenever the injection code or the schedule files it reads have changed since that output was produced. The first version of this second check tracked only the injection code. It was extended to the schedule files, because their content also decides what is injected.

## S.3 Retail scoring rule

Retail was first scored by counting every simulation against the range. Under that count, the verdict depended on a margin of only 0.15 % of the floor. In an earlier model version, a shift of -0.05 % in the median changed one simulation's verdict. The rule was then changed to require the median of all simulations to lie within the range. The change was made after the numbers of an earlier run had been seen. The rule was then written down before the numbers of the reported runs were read. Retail meets its range under the median rule but not under the count of individual simulations (37 of 56 inside).

## Supplementary tables

**Table S1.** Checks and thresholds, with their provenance.

The Provenance column classifies every threshold as exactly one of three kinds: a literature value, a heuristic, or a project-chosen value.

### (a) Tiered checks - Tier 1 distributional / Tier 2 structural / Tier 3 downstream

Applied per day type, to retail presence exactly as to work presence in the two-channel version.

| Tier | Metric | Threshold | Provenance |
|---|---|---|---|
| 1 Distributional | KL divergence (arrival / departure) | < 0.05 | project-chosen |
| 1 Distributional | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 | project-chosen |
| 1 Distributional | Presence-rate RMS error | ≤ 5 pp per day-type | project-chosen |
| 2 Structural | Transition-matrix Frobenius / MAE | < 0.05 | project-chosen |
| 2 Structural | Dwell-time KS test | p > 0.05 (fail to reject H₀) | project-chosen |
| 2 Structural | Autocorrelation MAE, lags 1-24 h | < 0.05 | project-chosen |
| 3 Downstream | NMBE | monthly ±5 %, hourly ±10 % | ASHRAE Guideline 14 |
| 3 Downstream | CV(RMSE) | monthly 15 %, hourly 30 % | ASHRAE Guideline 14 |
| 3 Downstream | Peak demand magnitude + timing | magnitude ±15 %; timing ≤ 1 h | project-chosen |

### (b) Channel-specific checks

| Layer | Check | Target | Provenance |
|---|---|---|---|
| Location mapping | Retail presence rate, weekday 12:00-14:00, per cycle | 0.06-0.10 (central ≈ 0.079) | project-chosen |
| Location mapping | Saturday peak rate, 13:00-16:00 | 0.09-0.12 | project-chosen |
| Location mapping | Sunday peak rate, per city | Calgary 0.06-0.10 / Montreal 0.04-0.07 | project-chosen |
| Location mapping | Night slots 00:00-05:00, all day-types | 0.000-0.003 | project-chosen |
| Retail rule (Eq. B.1) | Online shopping excluded from retail presence | rule fixed before training; cross-tabulation still reported | project-chosen |
| Transformer (JS) | JS for work presence and for retail presence, per stratum | < 0.02 each, paired with PR-AUC / F1 below | project-chosen |
| Transformer (Resolution) | PR-AUC and F1 on positive slots, retail presence | PR-AUC ≥ 0.15; F1 ≥ 0.25 | heuristic |
| Transformer (Dynamics) | Midday (11-14 h) rate error and transitions/day | error ≤ 3.0 pp; transitions ≥ 0.05/day | project-chosen |
| Transformer (Regression) | Head 1 and Head 2 JS drift | $\Delta\mathrm{JS} \leq 0.002$ bits versus the two-channel version | project-chosen |
| Transformer (Exclusivity) | Impossible-State Rate (ISR), slots with more than one channel active | ≤ 0.5 % raw; 0 % after projection | project-chosen |
| Hotel backcast | Alberta monthly 2015-2019 and Quebec monthly 2019 versus reconstruction | MAE < 0.05 | project-chosen |
| Hotel COVID dip | 2020-04 reconstruction | recovered without overshoot | project-chosen |
| BEM end-to-end | Code-schedule control versus 2022, Montreal SuperTall | EUI delta positive; office and hotel dominant | project-chosen |
| Floor-area sanity | Per-channel EUI share vs parsed occupiable share | ± 2 pp | project-chosen |

### (c) Wiring and differentiation checks

Made mandatory because the two-channel version's occupancy-field wiring defect passed every input-side
check and was caught only on the output side (Section S.2).

| Layer | Check | Target | Provenance |
|---|---|---|---|
| Wiring | Post-injection field-reference assertion | 100 % of modulated spaces pass | project-chosen |
| Simulation | Scenario-differentiation probe | Outputs differ across ≥ 2 scenarios; byte-identical outputs do not pass | project-chosen |

### Threshold provenance

Only two thresholds in this set are literature values, and only they may be cited as such: the NMBE
limits of 5 % monthly and 10 % hourly, and the CV(RMSE) limits of 15 % monthly and 30 % hourly, both
from ASHRAE Guideline 14. Two more are heuristic, the PR-AUC bar of 0.15 and the F1 bar of 0.25. They were adopted
to catch a model that predicts no retail presence at all, and they are treated as heuristic rather
than literature-derived. Every other threshold above is project-chosen and was
set before any tuning: the family of 0.05 tolerances on divergence, transition-matrix and
autocorrelation error, the presence-rate limit of 5 percentage points, the dwell-time test level, the
peak magnitude and timing check, the retail rate family, fixing the retail rule before training, the
Jensen-Shannon pairing and drift checks, the midday-dynamics check, the impossible-state bar, the hotel backcast and
COVID-recovery checks, the decode thresholds of 0.50, 0.40 and 0.15, the wiring and differentiation
checks, and the EUI-share check of 2 percentage points. These are acceptance thresholds chosen for this
study, not literature values.

**Table S2.** Limitations with a bounding measurement for each.

Section 5 of the main text states the limitations in full; the wording here is condensed to fit a cell. Rows L5 and L7 give values from the simulations reported in the main text; the other rows give design values or measurements made during model development.

| ID | Group | Statement | Bounding measurement |
|---|---|---|---|
| L1 | Frame | Hotel guests are outside the survey frame; the channel is driven by a tourism series. | The survey observes 0 % of hotel occupancy: 3 of 4 channels time-use-driven, 1 series-driven. |
| L2 | Frame | Retail sees customers only; staff are logged as at work. | 0 % of retail staff presence enters the signal, and 0 % of retail plug load is modulated by it. |
| L3 | Frame | Residential intra-household diversity is partial; the stronger claim of exactly zero is falsified. | 3,499 of 16,367 multi-person households, 21.38 %, carry a slot value outside 0, 0.5 and 1. |
| L4 | Reference ranges | The office floor is contested and unsourced; the check result reflects the fit of the range to this tower, not a model defect. | The code-schedule control scores 85.36 against a floor of 100. Two candidate explanations were ruled out; the reference source gives three different floors. |
| L5 | Reference ranges | The hotel reference range comes from a different building archetype and different cities. | Reference 284.44 and 299.28 kWh/m2/yr. Outside the range in 28 of 56 simulations, all in the Tall tower and all over the 300 ceiling; simulated values 204.83-321.55. |
| L6 | Reference ranges | The stacked-channel explanation for low hotel EUI is not used in this paper. | Not evaluated in the reported runs. |
| L7 | Reference ranges | Retail is validated on shape, not level; no time-of-day in-store reference exists. | Median 84.82 against a floor of 80, inside the range; 19 of 56 simulations under the floor. The retail rate check is reported for information only. |
| L8 | Reference ranges | Residential has no reference range that matches the modelled building; the survey high-rise figure is context only. | 130.6 kWh/m2/yr over 113.9-147.2, never a pass criterion. |
| L9 | Internal gains | Retail runs on the code's office occupant density, not its retail figure. | 24.97 against 29.97 m2/person, so retail is roughly 20 % over-crowded. |
| L10 | Internal gains | Equipment power density is one blanket value; lighting is differentiated. | 7.5028 W/m2 on every space type in both towers. |
| L11 | Internal gains | The retail peak of 0.95 has no source, and the code's retail schedule was never loaded. | The tower carries the office curve, peak 0.90 with a 0.50 lunch dip, times 0.95: 18.75 % too high, on the wrong shape. |
| L12 | Method conventions | The minimum pool size of 15 is an analyst judgement, presented as one. | The nearest literature value is 5, a study design rather than a recommendation. The check is non-monotonic: it does not pass at 10, passes at 11-20 and does not pass at 30. |
| L13 | Method conventions | Household aggregation is the mean, a decision rather than an inheritance. | The three model versions aggregate households in three different ways; this version was checked against its own code. |
| L14 | Method conventions | The retail episode-time share declines across cycles; it is not stable. | 2.00 %, 2.14 %, 1.66 %, 1.50 %, a 25 % decline that three other national series confirm as normal. |
| L15 | Physical model | Ground-level weather on a supertall tower; the one item with no bounding measurement. | Not quantified. No altitudinal temperature or wind-speed gradient is represented. |
| L16 | Physical model | The hotel hot-water plant is limited by the capacity of one water heater, and a global resize does not correct it. | Slope -0.98 against draw volume. A global factor of 6 moved that heater's share from 26.7 % to 65.4 % by reweighting alone. |

**Table S3.** Model card and per-cycle retail code mapping.

### (a) Architecture

| Component | Specification |
|---|---|
| Backbone | Shared multi-head Transformer encoder-decoder, kept from the two-channel version with targeted upgrades rather than replaced |
| Encoder | 6 layers, model width 256, 8 attention heads, approximately 29M parameters |
| Activity decoder | Autoregressive decoder, 14 activity classes, 48 half-hour slots per day |
| Head 1 | Residential presence, unchanged from the earlier versions |
| Head 2 | Office presence, unchanged from the two-channel version |
| Head 3 | Retail presence, new in this study; mirrors Head 2 off the same fused representation, with the activity decoder's gradient barrier unchanged |
| Co-presence head | 9-channel co-presence, unmodified by the retail addition |

### (b) Conditioning vector (width 120)

| Covariate group | Encoding |
|---|---|
| Demographics | One embedding per categorical field, concatenated and projected; 14 census fields plus the occupation, telework and work-schedule set |
| Day-type stratum | Embedding over three strata; drives diurnal shape |
| Cycle year | Continuous projection, never categorical, so the model extrapolates to an unseen 2030 |
| Collection mode | Low-capacity embedding, deliberately too small to leak physical signal |
| Retail | No retail-specific conditioning is added: retail presence is population-behavioural, not occupation-gated |

The width grew from 119 to 120 between the two versions because one demographic field gained a
missing-value category, a data-preparation correction unrelated to the retail addition.

### (c) Training regimen

| Item | Value |
|---|---|
| Loss weights, residential : office : retail | 1.0 : 0.5 : 0.3 |
| Scalarization | Fixed-weight; dynamic weighters rejected as unstable on a task with about 2 % positives |
| Gradient surgery | PCGrad, pairwise across the three tasks, joint phase only |
| Class imbalance, retail | Positive-class weight 49 |
| Inference logit shift | $-\ln 49 \approx -3.89$, applied at decode only, never during training |
| Warmup phase | 5 epochs, Head 3 only trainable, learning rate 1e-3 |
| Joint phase | 15 epochs, all parameters trainable, learning rate 1e-4, PCGrad on, early stopping on the check set |
| Dropout | 0.1, attention and residual only, never on output projections |
| Weight decay | 1e-4 |
| Label smoothing | Disabled; it distorts calibration on this task |
| Diary augmentation | None |
| Batch composition | Stratified 50 % weekday, 25 % Saturday, 25 % Sunday, inverse-cycle-frequency weighted |
| Survey weights | Applied inside the loss, clipped at the 99th percentile |
| Selection rule | Discard checkpoints that do not pass the hard checks, then maximize retail F1 among the rest; no composite score. The delivered checkpoint deviates from this rule, as described in Section S.1 |
| Automated checks on the generated diaries | 166 checks: 147 pass, 18 give a warning and 1 does not pass. The one that does not pass is a day-type ordering check that also did not pass in the two-channel version; no check that passed there stops passing here |

The design value of the positive-class weight is 49; the training split's measured positive rate implies
50.1056. The delivered model is trained with 49.

### (d) Decoding

| Item | Value |
|---|---|
| Sampling | Temperature 0.7 with nucleus sampling at 0.9; the two-channel version used 0.8 with no nucleus |
| Minimum dwell | At least 2 slots, 60 minutes, for work and retail events, applied after the exclusivity projection |
| Decision thresholds | 0.50 residential, 0.40 office, 0.15 retail, derived on validation |
| Exclusivity | Threshold-normalized argmax: a slot over threshold on more than one channel keeps only the channel with the largest threshold-normalized probability |
| Impossible-state rate | At most 0.5 % on raw output; 0 % on the injected schedules by construction |
| Rejected alternative | A categorical location head, which crushes the 2 % retail class and couples calibration |

### (e) Per-cycle retail code mapping

Each raw code below maps to the harmonised location code 5 (store) used in Eq. B.1.

| GSS cycle | Raw variable | Codes mapped to the unified shopping location | Status |
|---|---|---|---|
| 2005 (C19) | PLACE | 06 grocery and 07 other store or mall | confirmed |
| 2010 (C24) | PLACE | 06 and 07 | confirmed |
| 2015 (C29) | LOCATION | 306 | confirmed |
| 2022 | LOCATION | 3306 | confirmed |

In 2005 and 2010 two source codes are combined into one unified value; in 2015 and 2022 the single code
is already a merged grocery and general-merchandise bucket at the source. Grocery and general
merchandise are therefore not separable in the two later cycles, which is why the retail channel uses a
single retail archetype.

**Table S4.** Components carried over from the two-channel version.

A "Yes" is entered only where the files themselves were compared by checksum. Where nothing was compared, the table says so.

| Component | Two-channel version | Four-channel change | Identical? | Basis |
|---|---|---|---|---|
| Data collection | Survey columns for residential and office | Monthly provincial hotel series added; retail needs no new survey variable | Not compared | No comparison was run |
| Harmonisation | Code mapping for residential and office | Hotel series preparation added, plus the retail rule (Eq. B.1) | Not compared | No comparison was run |
| Half-hour slot tables | Residential and office slot tables | One added retail entry, written to a separate file | Not compared | Design intent only; not tested against the output |
| Occupancy model | Two decoder heads | Third head for retail; shared encoder kept with targeted upgrades | No | The drift tolerance is 0.002 bits, a bounded change rather than identity; the measured drift is not reported |
| Linkage | Household and worker linkage | Retail as one population-level fraction; hotel by provincial multiplier | Not compared | Documented as unchanged; no comparison was run |
| 2030 scenarios and hotel model | Survey-cycle adjustment, demographic drift, office work-from-home bands | Adjustment reused; retail lever and hotel time-series model added | No | Not compared at the level of injected schedules |
| Building-model integration | Two-channel injection by space tag | Four-channel routing; a missing channel keeps the code schedule | Yes, base prototype geometry only | The four prototype files are byte-identical. The injection code exists in three non-matching copies, so the building is shared and the code writing into it is not |
| Building simulation | 72-run residential re-simulation plus the office runs | The 56-simulation campaign with all four channels | Not compared | Channel isolation was shown inside this campaign; the two versions' outputs were not compared |
| End-use loads | Two-channel checks against survey and prototype references | Four-channel checks, two reported outside their ranges (Table 4 of the main text) | No | Different check sets and possibly a different basis; the two cannot be differenced |

## Supplementary figures

![](figures/SI/Figure_S01_occupiable_shares.png){width=16cm}

**Figure S1.** Occupiable-area share per channel.

![](figures/SI/Figure_S02_scenario_levers.png){width=16cm}

**Figure S2.** One scenario lever per channel.

![](figures/SI/Figure_S03_leg2_pipeline.png){width=16cm}

**Figure S3.** Two-channel version of the framework.

![](figures/Figure_02_three_leg_roadmap.png){width=16cm}

**Figure S4.** Three-stage development of the model.

![](figures/Figure_04_exclusivity_projection.png){width=16cm}

**Figure S5.** Exclusivity step across the three decoder heads.

![](figures/Figure_09_diurnal_4ch.png){width=16cm}

**Figure S6.** Diurnal load per channel, SuperTall tower, Calgary, central 2030 scenario.

![](figures/Figure_10_peakhour_4ch.png){width=16cm}

**Figure S7.** Channel and whole-building peak hours, central 2030 scenario.
