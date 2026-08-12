# Supplementary material

**Table 4.** - Validation gate set.

Gates applied across Steps 4-9 of the four-channel pipeline reported here. The Provenance column classifies
every threshold as exactly one of three kinds. This distinction is load-bearing for the paper's
honesty: a project-chosen threshold is not literature, and must never be cited as if it were.

## (a) Tiered gates - Tier 1 distributional / Tier 2 structural / Tier 3 ASHRAE G14

Applied per day-type, to AT_RETAIL exactly as to AT_WORK in the two-channel stage.

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

## (b) Channel-specific gates

| Layer | Check | Target | Provenance |
|---|---|---|---|
| LOCATION mapping | AT_RETAIL rate, weekday 12:00-14:00, per cycle | 0.06-0.10 (central ≈ 0.079) | project-chosen |
| LOCATION mapping | Saturday peak rate, 13:00-16:00 | 0.09-0.12 | project-chosen |
| LOCATION mapping | Sunday peak rate, per city | Calgary 0.06-0.10 / Montreal 0.04-0.07 | project-chosen |
| LOCATION mapping | Night slots 00:00-05:00, all day-types | 0.000-0.003 | project-chosen |
| OR-rule leak | Online shopping, excluded from AT_RETAIL | rule fixed before training; cross-tab still reported | project-chosen |
| Transformer (JS) | JS(AT_WORK), JS(AT_RETAIL) per stratum | < 0.02 each, paired with PR-AUC / F1 below | project-chosen |
| Transformer (Resolution) | PR-AUC and F1 on positive slots, AT_RETAIL | PR-AUC ≥ 0.15; F1 ≥ 0.25 | heuristic |
| Transformer (Dynamics) | Midday (11-14 h) rate error and transitions/day | error ≤ 3.0 pp; transitions ≥ 0.05/day | project-chosen |
| Transformer (Regression) | Head 1 and Head 2 JS drift | $\Delta\mathrm{JS} \leq 0.002$ bits vs the two-channel baseline | project-chosen |
| Transformer (Exclusivity) | Impossible-State Rate (ISR), slots with more than one channel active | ≤ 0.5 % raw; 0 % after projection | project-chosen |
| Hotel backcast | QC and AB monthly 2015-2019 vs reconstruction | MAE < 0.05 | project-chosen |
| Hotel COVID dip | 2020-04 reconstruction | recovered without overshoot | project-chosen |
| BEM end-to-end | Default vs 2022, Montreal SuperTall | EUI delta positive; office and hotel dominant | project-chosen |
| Floor-area sanity | Per-channel EUI share vs parsed occupiable share | ± 2 pp | project-chosen |

## (c) Wiring and differentiation gates

Made mandatory because the two-channel stage's occupancy-field wiring defect passed every input-side
check and was caught only on the output side (§3.5).

| Layer | Check | Target | Provenance |
|---|---|---|---|
| Wiring | Post-injection field-reference assertion | 100 % of modulated Spaces pass | project-chosen |
| Simulation | Scenario-differentiation probe | Outputs differ across ≥ 2 scenarios; byte-identical = FAIL | project-chosen |

## Threshold provenance

Only two thresholds in this set are literature values, and only they may be cited as such: the NMBE
limits of 5 % monthly and 10 % hourly, and the CV(RMSE) limits of 15 % monthly and 30 % hourly, both
from ASHRAE Guideline 14. Two more are heuristic, the PR-AUC bar of 0.15 and the F1 bar of 0.25, adopted
to catch an all-zeros failure mode and flagged as heuristic rather than literature-derived by this
project's own architecture and training reviews. Every other threshold above is project-chosen and was
set before any tuning: the family of 0.05 tolerances on divergence, transition-matrix and
autocorrelation error, the presence-rate limit of 5 percentage points, the dwell-time test level, the
peak magnitude and timing gate, the retail rate family, the OR-rule freeze, the Jensen-Shannon pairing
and drift gates, the midday-dynamics gate, the impossible-state bar, the hotel backcast and
COVID-recovery checks, the decode thresholds of 0.50, 0.40 and 0.15, the wiring and differentiation
gates, and the EUI-share gate of 2 percentage points. These are project acceptance bars, not literature
values.

**Table 7.** - Sixteen limitations and bounding measurements.

The Discussion carries the deciding statements in full; the wording here is condensed to fit a cell.
No verdict is paraphrased and every number is the source's own.

| ID | Group | Statement | Bounding measurement |
|---|---|---|---|
| L1 | Frame | Hotel guests are outside the survey frame; the channel is driven by a tourism series. | The survey observes 0 % of hotel occupancy: 3 of 4 channels time-use-driven, 1 series-driven. |
| L2 | Frame | Retail sees customers only; staff are logged as at work. | 0 % of retail staff presence enters the signal, and 0 % of retail plug load is modulated by it. |
| L3 | Frame | Residential intra-household diversity is partial; the stronger claim of exactly zero is falsified. | 3,499 of 16,367 multi-person households, 21.38 %, carry a slot value outside 0, 0.5 and 1. |
| L4 | Reference bands | The office floor is contested and unsourced; the gate is a band-applicability finding. | The uninjected control scores 85.45 against a floor of 100. Two mechanisms refuted; the source gives three floors for itself. |
| L5 | Reference bands | The hotel band is archetype- and city-mismatched. | Reference 284.44 and 299.28 kWh/m2/yr. FAIL on 28 of 56 cells, all Tall, all over the 300 ceiling; range 203.33-318.42. |
| L6 | Reference bands | The stacked-channel explanation for low hotel EUI was tested and refuted; it is cited nowhere. | Wrong in sign and order in 56 of 56 cells. Exposure takes 2 values across the campaign, not 56. |
| L7 | Reference bands | Retail is validated on shape, not level; no time-of-day in-store reference exists. | Median 75.63 against a floor of 80, 5.47 % below, 44 of 56 cells under. The rate gate is informational. |
| L8 | Reference bands | Residential has no as-modelled band; the survey high-rise figure is context only. | 130.6 kWh/m2/yr over 113.9-147.2, never a pass criterion. |
| L9 | Internal gains | Retail runs on the code's office occupant density, not its retail figure. | 24.97 against 29.97 m2/person, so retail is roughly 20 % over-crowded. |
| L10 | Internal gains | Equipment power density is one blanket value; lighting is differentiated. | 7.5028 W/m2 on every space type in both towers. |
| L11 | Internal gains | The retail peak of 0.95 has no source, and the code's retail schedule was never loaded. | The tower carries the office curve, peak 0.90 with a 0.50 lunch dip, times 0.95: 18.75 % hot on the wrong shape. |
| L12 | Method conventions | The minimum pool size of 15 is an analyst judgement, presented as one. | The anchor previously cited gives 5. The gate is non-monotonic: fails at 10, passes at 11-20, fails at 30. |
| L13 | Method conventions | Household aggregation is the mean, a decision rather than an inheritance. | Three construction stages, three implementations; this one verified against its own code. |
| L14 | Method conventions | The retail episode-time share declines across cycles; the earlier stable claim was a documentation defect. | 2.00 %, 2.14 %, 1.66 %, 1.50 %, a 25 % decline that three other national series confirm as normal. |
| L15 | Physical model | Ground-level weather on a supertall tower; the one item with no bounding measurement. | Not quantified. No altitudinal temperature or wind-speed gradient is represented. |
| L16 | Physical model | The hotel hot-water plant is capacity-pinned on one object, and a global fix does not correct it. | Slope -0.98 against draw volume. A global factor of 6 moved that object's share from 26.7 % to 65.4 % by reweighting alone. |

**Table A1.** - Model card, three-head Transformer.

### A1.1 Architecture

| Component | Specification |
|---|---|
| Backbone | Shared multi-head Transformer encoder-decoder, kept from the two-channel stage with targeted upgrades rather than replaced |
| Encoder | 6 layers, model width 256, 8 attention heads, approximately 29M parameters |
| Activity arm | Autoregressive decoder, 14 activity classes, 48 half-hour slots per day |
| Head 1 | Residential presence, unchanged from the earlier stages |
| Head 2 | Office presence, unchanged from the two-channel stage |
| Head 3 | Retail presence, new in this study; mirrors Head 2 off the same fused representation, with the activity arm's gradient barrier untouched |
| Co-presence head | 9-channel co-presence, unmodified by the retail addition |

### A1.2 Conditioning vector (width 120)

| Covariate group | Encoding |
|---|---|
| Demographics | One embedding per categorical field, concatenated and projected; 14 census fields plus the occupation, telework and work-schedule set |
| Day-type stratum | Embedding over three strata; drives diurnal shape |
| Cycle year | Continuous projection, never categorical, so the model extrapolates to an unseen 2030 |
| Collection mode | Low-capacity embedding, deliberately too small to leak physical signal |
| Retail | No retail-specific conditioning is added: retail presence is population-behavioural, not occupation-gated |

The width grew from 119 to 120 between the two stages because one demographic field gained a
missing-value category, an independent data-pipeline fix rather than part of the retail addition.

### A1.3 Training regimen

| Item | Value |
|---|---|
| Loss weights, residential : office : retail | 1.0 : 0.5 : 0.3 |
| Scalarization | Fixed-weight; dynamic weighters rejected as unstable on a task with about 2 % positives |
| Gradient surgery | PCGrad, pairwise across the three tasks, joint phase only |
| Class imbalance, retail | Positive-class weight 49 |
| Inference logit shift | $-\ln 49 \approx -3.89$, applied at decode only, never during training |
| Warmup phase | 5 epochs, Head 3 only trainable, learning rate 1e-3 |
| Joint phase | 15 epochs, all parameters trainable, learning rate 1e-4, PCGrad on, early stopping on the gate set |
| Dropout | 0.1, attention and residual only, never on output projections |
| Weight decay | 1e-4 |
| Label smoothing | Disabled; it distorts calibration on this task |
| Diary augmentation | None |
| Batch composition | Stratified 50 % weekday, 25 % Saturday, 25 % Sunday, inverse-cycle-frequency weighted |
| Survey weights | Applied inside the loss, clipped at the 99th percentile |
| Selection rule | Gate-first, then maximize retail F1 among survivors; no composite score. The shipped checkpoint deviates from this rule, as disclosed in §3.2 |
| Shipped scorecard | 147 PASS / 18 WARN / 1 FAIL; the single FAIL is a day-type ordering check pre-existing in the two-channel baseline, with no new failure introduced |

The design value of the positive-class weight is 49; the training split's measured positive rate implies
50.1056. The shipped model trains on 49.

### A1.4 Decoding

| Item | Value |
|---|---|
| Sampling | Temperature 0.7 with nucleus sampling at 0.9; the two-channel stage used 0.8 with no nucleus |
| Minimum dwell | At least 2 slots, 60 minutes, for work and retail events, applied after the exclusivity projection |
| Decision thresholds | 0.50 residential, 0.40 office, 0.15 retail, derived on validation |
| Exclusivity | Threshold-normalized argmax: a slot over threshold on more than one channel keeps only the channel with the largest threshold-normalized probability |
| Impossible-state rate | At most 0.5 % on raw output; 0 % on the injected schedules by construction |
| Rejected alternative | A categorical location head, which crushes the 2 % retail class and couples calibration |

**Table A2.** - AT_RETAIL codebook per GSS cycle.

| GSS cycle | Raw variable | Codes mapped to the unified shopping location | Status |
|---|---|---|---|
| 2005 (C19) | PLACE | 06 grocery and 07 other store or mall | confirmed |
| 2010 (C24) | PLACE | 06 and 07 | confirmed |
| 2015 (C29) | LOCATION | 306 | confirmed |
| 2022 (GSSP) | LOCATION | 3306 | confirmed |

In 2005 and 2010 two source codes are combined into one unified value; in 2015 and 2022 the single code
is already a merged grocery and general-merchandise bucket at the source. Grocery and general
merchandise are therefore not separable in the two later cycles, which is why the retail channel uses a
single retail archetype.

![Figure S3](../figures/SI/Figure_S03_leg2_pipeline.png)

**Figure S3.** - Two-channel construction-stage pipeline.
