# Table 4 - Validation gate set

Gates applied across Steps 4-9 of the Leg-3 (4-split) pipeline. The **Provenance** column classifies
every threshold as exactly one of three kinds. This distinction is load-bearing for the paper's
honesty: a **project-chosen** threshold is not literature, and must never be cited as if it were.

## (a) Tiered gates - Tier 1 distributional / Tier 2 structural / Tier 3 ASHRAE G14

Applied per day-type, to AT_RETAIL exactly as to AT_WORK in Leg-2.

| Tier | Metric | Threshold | Provenance |
|---|---|---|---|
| 1 Distributional | KL divergence (arrival / departure) | < 0.05 | project-chosen (set before tuning) |
| 1 Distributional | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 | project-chosen (set before tuning) |
| 1 Distributional | Presence-rate RMS error | ≤ 5 pp per day-type | project-chosen (set before tuning) |
| 2 Structural | Transition-matrix Frobenius / MAE | < 0.05 | project-chosen (set before tuning) |
| 2 Structural | Dwell-time KS test | p > 0.05 (fail to reject H₀) | project-chosen (set before tuning) |
| 2 Structural | Autocorrelation MAE, lags 1-24 h | < 0.05 | project-chosen (set before tuning) |
| 3 Downstream | NMBE | monthly ±5 %, hourly ±10 % | **ASHRAE Guideline 14** |
| 3 Downstream | CV(RMSE) | monthly 15 %, hourly 30 % | **ASHRAE Guideline 14** |
| 3 Downstream | Peak demand magnitude + timing | magnitude ±15 %; timing ≤ 1 h | project-chosen (set before tuning) |

## (b) Channel-specific gates

| Layer | Check | Target | Provenance |
|---|---|---|---|
| LOCATION mapping | AT_RETAIL rate, weekday 12:00-14:00, per cycle | 0.06-0.10 (confirmed by dr_L3-06, central ≈ 0.079) | project-chosen (set before tuning) |
| LOCATION mapping | Saturday peak rate, 13:00-16:00 | 0.09-0.12 | project-chosen (set before tuning) |
| LOCATION mapping | Sunday peak rate, per city | Calgary 0.06-0.10 / Montreal 0.04-0.07 | project-chosen (set before tuning) |
| LOCATION mapping | Night slots 00:00-05:00, all day-types | 0.000-0.003 | project-chosen (set before tuning) |
| OR-rule leak | `occACT==4 & occPRE==1` (online-shopping) share per cycle, excluded from AT_RETAIL | rule FROZEN (OD-1, 2026-07-02); cross-tab still reported as verification | project-chosen (set before tuning) |
| Transformer (JS) | JS(AT_WORK), JS(AT_RETAIL) per stratum | < 0.02 each (JS alone is toothless for AT_RETAIL; paired with PR-AUC / F1 below) | project-chosen (set before tuning) |
| Transformer (Resolution) | PR-AUC and F1 on positive slots, AT_RETAIL | PR-AUC ≥ 0.15, F1 ≥ 0.25 (catches all-zeros failure) | **heuristic** |
| Transformer (Dynamics) | Midday (11-14 h) rate error + transitions/day, AT_RETAIL | Midday error ≤ 3.0 pp, transitions ≥ 0.05/day | project-chosen (set before tuning) |
| Transformer (Regression) | Old-head (Head 1, Head 2) JS drift | ΔJS ≤ 0.002 bits vs Leg-2 validation baseline | project-chosen (set before tuning) |
| Transformer (Exclusivity) | Impossible-State Rate: slots with > 1 of {AT_HOME, AT_WORK, AT_RETAIL} active | ISR ≤ 0.5 % raw; = 0 % after decode-time projection (dr_L3-12) | project-chosen (set before tuning) |
| Hotel backcast | QC + AB monthly 2015-2019 vs reconstruction | MAE < 0.05 | project-chosen (set before tuning) |
| Hotel COVID dip | 2020-04 reconstruction | recovered without overshoot | project-chosen (set before tuning) |
| BEM end-to-end | Default vs 2022, Montreal SuperTall | EUI delta positive; Office + Hotel dominant | project-chosen (set before tuning) |
| Floor-area sanity | Per-channel EUI share vs parsed occupiable share | ± 2 pp | project-chosen (set before tuning) |

## (c) Wiring + differentiation gates (the Leg-2 lesson gates)

Made mandatory because the Leg-2 People-field wiring bug (`Number_of_People_Schedule_Name`, not
`Schedule_Name`) passed every input-side check and was caught only output-side.

| Layer | Check | Target | Provenance |
|---|---|---|---|
| Wiring | Post-injection field-reference assertion | 100 % of modulated Spaces pass | project-chosen (set before tuning) |
| Simulation | Scenario-differentiation probe | Outputs differ per channel across ≥ 2 scenarios (byte-identical results = automatic FAIL) | project-chosen (set before tuning) |

---

## Provenance key (do not cite a project-chosen threshold to the literature)

- **ASHRAE Guideline 14** - NMBE (±5 % monthly / ±10 % hourly) and CV(RMSE) (15 % monthly / 30 %
  hourly) only. Cite the standard.
- **project-chosen (set before tuning)** - every `< 0.05` gate (KL, EMD, transition-matrix
  Frobenius/MAE, autocorrelation MAE), the presence-rate RMS ≤ 5 pp, the dwell-time KS p > 0.05, the
  peak ±15 % / ≤ 1 h gate, the 0.06-0.10 retail rate family (weekday/Saturday/Sunday/night), the OR-rule
  freeze, the JS < 0.02 pairing, the midday-dynamics and JS-drift gates, the ISR ≤ 0.5 % bar, the
  hotel MAE < 0.05 and COVID-recovery checks, the decode thresholds (0.50 / 0.40 / 0.15), the wiring
  and scenario-differentiation gates, and the ± 2 pp EUI-share gate. All were set before tuning and
  are project acceptance bars, not literature values.
- **heuristic** - PR-AUC ≥ 0.15 and F1 ≥ 0.25, adopted to catch an all-zeros failure mode, flagged by
  dr_L3-11/dr_L3-13 as heuristic rather than literature-derived.

⚠ check source - the decode-time thresholds (0.50 / 0.40 / 0.15) named in the pipeline overview's
provenance blockquote are not broken out as individual gate rows in the VALIDATION GATES / VALIDATION
PLAN tables of either source document; they are recorded here only inside the provenance key, per the
source text itself.

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
