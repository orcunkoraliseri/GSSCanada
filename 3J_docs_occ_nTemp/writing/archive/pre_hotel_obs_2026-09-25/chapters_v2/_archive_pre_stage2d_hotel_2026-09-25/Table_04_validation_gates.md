# Table 4 - Validation gate set

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

---

## Provenance key (do not cite a project-chosen threshold to the literature)

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

---

## Sources

- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, section `## VALIDATION GATES`,
  lines 179-214 (tiered + channel-specific gate tables and the threshold-provenance blockquote) and
  section `## KEY DESIGN DECISIONS SUMMARY`, lines 218-234 (wiring + differentiation gates rationale,
  row "Wiring + differentiation gates mandatory").
- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`, section `## VALIDATION PLAN`, lines 522-561
  (identical gate tables, full pipeline doc) and section `## KEY DESIGN DECISIONS`, lines 564-581, row
  "Wiring + differentiation gates are mandatory, not advisory".
- Heuristic and project-novel classifications cross-checked against
  `Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md` (± 2 pp EUI-share gate
  confirmed project-novel, Part C §2) and the provenance blockquote's citations to dr_L3-11 / dr_L3-13
  for the PR-AUC / F1 heuristic flag.

No em dashes or en dashes.
