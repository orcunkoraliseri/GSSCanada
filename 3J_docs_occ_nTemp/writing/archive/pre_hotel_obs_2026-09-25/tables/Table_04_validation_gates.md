# Table 4 - Validation gate set

Gates applied across Steps 4-9 of the four-channel pipeline reported here. The Provenance column classifies
every threshold as exactly one of three kinds. This distinction is load-bearing for the paper's
honesty: a project-chosen threshold is not literature, and must never be cited as if it were.

## (a) Tiered checks - Tier 1 distributional / Tier 2 structural / Tier 3 downstream

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

## (b) Channel-specific checks

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

## (c) Wiring and differentiation checks

Made mandatory because the two-channel version's occupancy-field wiring defect passed every input-side
check and was caught only on the output side (§3.5).

| Layer | Check | Target | Provenance |
|---|---|---|---|
| Wiring | Post-injection field-reference assertion | 100 % of modulated spaces pass | project-chosen |
| Simulation | Scenario-differentiation probe | Outputs differ across ≥ 2 scenarios; byte-identical outputs do not pass | project-chosen |

---

## Provenance key (do not cite a project-chosen threshold to the literature)

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
