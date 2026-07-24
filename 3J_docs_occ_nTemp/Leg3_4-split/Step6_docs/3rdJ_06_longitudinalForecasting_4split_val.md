# Step 6 — Four-Channel Longitudinal Forecasting: Validation Plan (4-Split)
### Leg-2 Sections 1–7 ported (3-channel) + NEW Section 8: hotel SARIMA gates

---

## Goal

Validate: training convergence on three GSS heads, TFT generalization per fine-tune phase, DRIFT_MATRIX plausibility including the **COVID triple signal** (home ↑, work ↓, retail ↓), the joint 2022 backcast (profile metric), 2030 three-band plausibility per channel (office WFH bands + retail lever + hotel bands), BEM readiness — **plus the entirely new hotel SARIMA section**, which uses time-series forecast metrics, not diary-distribution metrics (none of the JS/DRIFT machinery applies to a non-GSS aggregate series).

## Threshold Provenance Note (Leg-2 discipline kept)

(1) **ASHRAE Guideline 14** — cite the standard (NMBE/CV(RMSE), same-period-only). (2) Literature-confirmed (C2ST ≈ 0.50, dwell-KS). (3) **Project-chosen** — KL < 0.05, EMD < 0.05, presence-RMS ≤ 5 pp, MAD < 0.10, hotel MAE < 0.05, band bars: never cite to literature. Model selection on the Pareto frontier / gate-first — never a single composite.

## Script: `3rdJ_06_longitudinalForecasting_4split_val.py` — class `LongitudinalForecastingValidator4Split`

## Sections

### Section 1 — Training convergence (ported, + retail)

Leg-2 checks 1.1–1.10 with: fixed-α sanity (α logged constant — no dynamic weighter drift by construction), retail head convergence (val PR-AUC trend rising; loss non-degenerate), PCGrad conflict stats across 3+ tasks, no catastrophic forgetting (< 1.5× stage-A JS on old heads).

### Section 2 — True Future Test per phase (ported, + retail)

Per-phase gates: home < 0.20, work < 0.25 (asymmetric — work structurally harder), **retail: profile-MAD < 0.10 + PR-AUC ≥ 0.10 on the future cycle** (raw JS not used — saturates on a ~2 %-positive channel).

### Section 3 — DRIFT_MATRIX plausibility (ported, + retail axis)

3.1–3.4 ported; 3.5 home COVID ≥ +5 pp (1522); 3.6 work directional decrease; **3.7 NEW: retail directional decrease in 1522** (COVID in-store collapse); 3.8 non-trivial retail activity count (≥ 1 axis entry per matrix). Triple-signal failure = soft blocker (TrendEncoder would underweight the COVID break).

### Section 4 — 2022 backcast (joint gate, ported metric lessons)

- Profile metric only (shape-JS + level-MAD) — **never raw flattened-binary JS** (Leg-2 saturation artifact; retail is the worst case).
- Backcast generated at deliverable decode settings (T 0.7/nucleus/min-dwell) — **never greedy** (sticky-attractor artifact).
- Gates: home MAD < 0.10 & ±2 pp level (3 strata); work MAD < 0.10 & ±3 pp; **retail MAD < 0.10 & ±1.5 pp**; WFH_RATE ±5 pp; Tier-1/2 battery (KL/EMD/RMS/Frobenius/dwell-KS/ACF/C2ST) per channel, retail thresholds provisional (project-chosen, record at first run).

### Section 5 — 2030 schedule plausibility (ported + retail block; retail windows are NOT office copies)

- Residential 5.1–5.6 and office 5.7–5.15 ported verbatim (peaks slots 12–16/22–26, lunch dip, night floor 0.02–0.05, WD > WE, band targets 5.17–5.19).
- **Retail 5.20–5.27 (NEW):** 5.20 weekday midday 12–14h in 0.06–0.10 × lever; 5.21 Saturday peak 13–16h 0.09–0.12 × lever, **Sat > weekday** (reverse of office); 5.22 Sunday QC 0.04–0.07 / AB 0.06–0.10 (respondent-PR subset); 5.23 night 0.000–0.003; 5.24 lever exactness: band ratios of all-day retail mass = 0.90/0.97/1.05 ± 0.01 (post-hoc lever is exact by construction — deviation means the lever leaked through normalization); 5.25 QC-Sunday sub-axis file: restricted default 0.60–0.75 × Sat peak; 5.26 continuity vs 2022 ±10 pp shape; 5.27 no retail–WFH cross-contamination (office band choice leaves retail mass unchanged ± float tolerance).

### Section 6 — BEM output readiness (ported, 3-way)

Schema/range checks with `ret30`; **6.7 mutex hard gate generalized 3-way** (0 violations across home/work/retail post-6H); row counts per band; peak magnitude/timing (project-chosen ±15 %/≤1h). **G14 same-period-only restriction unchanged** (cross-year application invalid for every channel — the WFH/e-commerce shifts ARE the signal).

### Section 8 — Hotel SARIMA (⚠️ NEW, Leg 3, non-GSS — time-series metrics)

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 8.1 | Orders frozen on pre-COVID 2005–2019 segment by BIC/AICc; recorded | documented | FAIL if selected on full series |
| 8.2 | Ljung-Box residual whiteness (full-series refit, with interventions) | p > 0.05 | WARN |
| 8.3 | Backcast 2015–2019 reconstruction, QC + AB | **MAE < 0.05** | FAIL |
| 8.4 | COVID 2020-04 dip recovered | no overshoot below the historical low | FAIL |
| 8.5 | Intervention spec: pulse (2020-03…2022-06) **+ permanent level-shift** present; AB splice dummy if applicable | as dr_L3-09 | FAIL |
| 8.6 | 2030 central path vs 2023–2025 anchors (QC ~0.635, AB ~0.615) | ± 0.05 | WARN |
| 8.7 | Band monotonicity + tilts: low < central < high; AB low 0.90, QC high 1.07 applied | exact | FAIL |
| 8.8 | Seasonality preserved in the 2030 path (12-month profile correlation vs pre-COVID mean profile r ≥ 0.8) | r ≥ 0.8 | WARN |
| 8.9 | Output schemas: `hotel_multiplier_2030.csv` (12 × 2 PR × 3 bands), `hotel_multiplier_lookup.csv` (historical); rates ∈ (0,1] | exact | FAIL |
| 8.10 | s(t) table integrity: 48 slots × 2 day-types, max = 1.000, plateau/trough values match dr_L3-05 (0.200 / 0.308) | exact | FAIL |

### Section 7 — Summary table

Full roll-up: gate | channel (home/work/retail/hotel) | band | result. FAIL triage priorities inherited: §4 backcast = blocker; §5 band-monotonicity/lever-exactness = hard blocker; §3 triple-signal = soft blocker; §6.7 mutex = hard blocker (6H re-run); **§8.3/8.4 hotel backcast = blocker for the hotel channel only** (GSS channels may proceed — the fall-back guarantee routes hotel Spaces to NECB baseline).

## PASS / WARN / FAIL Convention

Canonical definitions. The hotel channel's failure domain is isolated by design: a hotel FAIL never blocks GSS-channel sign-off (additive-safety principle), but it does block Step-7 hotel injection.

## Expected Result

0 FAIL; report `outputs_step6/step6_validation_report.html`. Defer always to the live HTML + the canonical `_C` deliverable — this plan doc will not track result numbers (Leg-2 staleness lesson; use ⚠️ ADDENDUM blocks if headline numbers are ever quoted here).

## Test Method

Cluster GSS stages via sbatch; hotel + validator locally: `py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split_val.py`.

## Progress Log

*(append entries below — `| Date | Check | Result | Notes |`)*

| Date | Check | Result | Notes |
|---|---|---|---|
| 2026-07-23 | Full validator run (Sections 1-8) | GSS(1-6): 66P/15W/**5F**/19I; Hotel(8): 17P/3W/2F | `3rdJ_06_longitudinalForecasting_4split_val.py` built + run. Full scorecard, both discovered validator bugs (Section-5 scenario-loop `lev` binding; hotel status normalization), and per-gate disposition recorded in `3rdJ_06_longitudinalForecasting_4split.md`'s 2026-07-23 Progress Log entry (this doc intentionally does not track result numbers beyond this summary row, per the "defer to the live HTML + this doc won't track result numbers" convention above). Report: `outputs_step6/step6_validation_report.html`. Canonical `_C` deliverable MD5 `7c105ef331b37107d5b605c95028c3ba`. **Step 6 NOT declared done** (5 FAIL on GSS channels, both real evidence-characterized findings, not relaxed). |
