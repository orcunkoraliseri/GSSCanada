# Step 6 — Longitudinal Forecasting: Validation Plan

## Goal

Validate the outputs of `06_longitudinalForecasting.py` by verifying training convergence,
True Future Test generalization, DRIFT_MATRIX plausibility (including the COVID-19 AT_HOME
signal in DRIFT_MATRIX_1522), 2022 backcasting reconstruction quality, 2030 schedule
plausibility, and BEM output format readiness. Produce an HTML report
(`outputs_step6/step6_validation_report.html`) with embedded charts.

**Input**: `0_Occupancy/Outputs_21CEN22GSS/forecast_2030/` (outputs of Sub-stages A–D)
**Reference**: `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/augmented_diaries.csv` (observed 2022 baseline)
**Output**: `outputs_step6/step6_validation_report.html`

---

## Script Structure: `06_longitudinalForecastingGSS_val.py`

```python
"""Step 6 — Longitudinal Forecasting: Validation & Report Generation.

Validates forecast_2030/ outputs against observed 2022 baseline and
internal consistency checks. Generates an HTML report with embedded charts.
"""

class LongitudinalForecastingValidator:
    def __init__(self, forecast_dir, step4_dir, outputs_dir):
        # Load 2030 synthetic diaries, reconstructed 2022, drift matrices
        # Load observed 2022 from augmented_diaries.csv (CYCLE_YEAR==2022)
        ...

    # ── Section 1 ────────────────────────────────────────────
    def validate_training_convergence(self) -> results_dict

    # ── Section 2 ────────────────────────────────────────────
    def validate_true_future_test(self) -> results_dict

    # ── Section 3 ────────────────────────────────────────────
    def validate_drift_matrices(self) -> results_dict

    # ── Section 4 ────────────────────────────────────────────
    def validate_backcasting_2022(self) -> results_dict

    # ── Section 5 ────────────────────────────────────────────
    def validate_2030_schedule_plausibility(self) -> results_dict

    # ── Section 6 ────────────────────────────────────────────
    def validate_bem_readiness(self) -> results_dict

    # ── Section 7 ────────────────────────────────────────────
    def generate_summary_table(self) -> results_dict

    # ── Report ───────────────────────────────────────────────
    def build_html_report(self) -> str
    def run_all(self)

if __name__ == "__main__":
    LongitudinalForecastingValidator(
        forecast_dir="0_Occupancy/Outputs_21CEN22GSS/forecast_2030",
        step4_dir="0_Occupancy/Outputs_21CEN22GSS/aug_pipeline",
        outputs_dir="outputs_step6",
    ).run_all()
```

---

## Section 1 — Training Convergence

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 1.1 Sub-stage A convergence | Final val JS vs. epoch 1 val JS: `(val_js_epoch1 - val_js_final) / val_js_epoch1` | Reduction ≥ 30% (model actually learned) |
| 1.2 Sub-stage A val JS gate | Final val JS per DDAY_STRATA (W_2005) | < 0.15 per stratum (hard gate) |
| 1.3 No divergence in fine-tuning | Max val JS across all phases vs. Sub-stage A final JS | Max < 1.5 × Sub-stage A final JS (no catastrophic forgetting) |
| 1.4 Sub-stage C pooled convergence | Final pooled val JS (W_pooled_2030) | < 0.18 per stratum |

### Charts
- 4-panel training/val JS loss curves: Sub-stage A + 3 fine-tuning phases
- Horizontal dashed lines: gate thresholds (0.15 for A, 0.20 for fine-tune phases, 0.18 for pooled)

---

## Section 2 — True Future Test (per phase)

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 2.1 W_2005 on 2010 (True Future Test) | JS divergence: W_2005 predicted activity distribution vs. 2010 observed, per DDAY_STRATA | < 0.20 per stratum |
| 2.2 W_2010_ft on 2015 | JS divergence: W_2010_ft predicted vs. 2015 observed, per DDAY_STRATA | < 0.20 per stratum |
| 2.3 W_2015_ft on 2022 | JS divergence: W_2015_ft predicted vs. 2022 observed, per DDAY_STRATA | < 0.20 per stratum |
| 2.4 Improvement over uniform baseline | True Future Test JS vs. uniform activity distribution (JS ≈ 0.5) | All 3 phases < 0.40 (well below uniform — model is generalizing) |

> **Interpretation note:** True Future Test JS will be higher than within-cycle validation
> JS (0.15 vs 0.20 threshold) because the test cycle was never seen during training. This is
> by design — the test directly simulates the forecasting task. A result of 0.18 on 2022
> held-out is publishable evidence of generalization, even if it exceeds the Sub-stage A val gate.

### Charts
- Bar chart: JS per phase × DDAY_STRATA (3 groups × 3 strata = 9 bars per chart)
- Baseline comparison line: uniform distribution JS ≈ 0.5
- Table: phase | True Future Test JS WD | Sat | Sun | vs. baseline improvement %

---

## Section 3 — DRIFT_MATRIX Plausibility

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 3.1 DRIFT_MATRIX_0510 non-trivial | Count activities where JS drift > 0.01 | ≥ 3 activities (behavioral change is real) |
| 3.2 DRIFT_MATRIX_1015 non-trivial | Count activities where JS drift > 0.01 | ≥ 3 activities |
| 3.3 DRIFT_MATRIX_1522 COVID signal | Mean WD AT_HOME drift in DRIFT_MATRIX_1522 vs. mean WD AT_HOME drift in DRIFT_MATRIX_1015 | DRIFT_1522 WD signal ≥ +5 pp larger than DRIFT_1015 WD signal (COVID break is the largest single transition) |
| 3.4 All matrices complete | NaN / Inf count across all 3 matrices | 0 NaN, 0 Inf |
| 3.5 Matrix dimensions | Shape of each matrix: 14 activities × 3 strata × N archetypes | Consistent across all 3 matrices (same N) |

> **DRIFT_MATRIX_1522 is the primary research finding.** The COVID-19 AT_HOME shift
> (2022 WD AT_HOME ≈ 70.6% vs. 2015 ≈ 64.5%) should appear as a large positive drift
> on AT_HOME-correlated activities (Sleep, Personal Care, Leisure at Home) and a negative
> drift on Paid Work outside home and Commute. If check 3.3 fails (< +5 pp COVID signal
> in the WD stratum), the Trend Encoder will underweight this structural break and the
> 2030 WFH projection will be incorrect. Investigate W_2015_ft training convergence and
> 2022 cycle recency weight before proceeding.

### Charts
- Three side-by-side heatmaps: DRIFT_MATRIX_0510 / DRIFT_MATRIX_1015 / DRIFT_MATRIX_1522
  (14 activity categories × 3 DDAY_STRATA; color = JS drift magnitude)
- COVID signal annotated on DRIFT_MATRIX_1522 with a dashed box around AT_HOME-correlated rows
- Bar chart: aggregate cycle shift index per transition (single scalar per matrix)

---

## Section 4 — 2022 Backcasting Reconstruction

This section is the primary publishable validation evidence for the paper. Model 2
reconstructs observed 2022 patterns by conditioning on actual 2022 scenario features.
A tight reconstruction JS gate confirms that the model captures inter-cycle behavioral
drift before the 2030 projection claim is made.

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 4.1 Reconstruction JS WD | JS divergence: reconstructed 2022 vs. observed 2022, DDAY_STRATA=1 | < 0.10 (hard gate) |
| 4.2 Reconstruction JS Saturday | Same, DDAY_STRATA=2 | < 0.10 (hard gate) |
| 4.3 Reconstruction JS Sunday | Same, DDAY_STRATA=3 | < 0.10 (hard gate) |
| 4.4 AT_HOME reconstruction | `|reconstructed WD AT_HOME mean - observed 2022 WD AT_HOME mean|` | ≤ 2 pp |
| 4.5 Top-5 activity reconstruction | For top-5 activities (by time share) in observed 2022: `|reconstructed share - observed share|` per activity | ≤ 2 pp each |
| 4.6 Night sleep reconstruction | `|reconstructed slots 1–8 sleep rate - observed 2022 sleep rate|` | ≤ 2 pp |

> **Paper framing for Section 4:** Results from checks 4.1–4.3 form the backcasting
> validation table in the paper: *"Model 2 reconstructed 2022 occupancy patterns with
> JS divergence WD=X, Sat=Y, Sun=Z (Table X), confirming the model's ability to capture
> the COVID-19 behavioral shift before projecting to 2030."*

### Charts
- **AT_HOME overlay**: 48-slot line plot — reconstructed 2022 vs. observed 2022 vs. 2030 forecast
  (three curves on one plot; primary diagnostic chart)
- Activity diff bar chart: reconstructed 2022 − observed 2022 signed difference (top-5 activities)
- Table: reconstruction JS per stratum (WD / Sat / Sun) with gate threshold and PASS/FAIL

---

## Section 5 — 2030 Schedule Plausibility

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 5.1 2030 AT_HOME plausibility | Overall mean AT_HOME across all 2030 rows | ∈ [55%, 90%] (plausibility bounds) |
| 5.2 WD < WE AT_HOME (structural) | Mean WD AT_HOME < mean WE AT_HOME in 2030 | WD < WE (weekday = more time away from home) |
| 5.3 Night sleep (slots 1–8) | Proportion where act30 == 5 (Sleep & Naps) in slots 1–8 | ≥ 70% |
| 5.4 Activity distribution non-degenerate | Max single activity time-share across 2030 rows | < 60% (model has not collapsed to one output) |
| 5.5 WFH signal present | Work-at-home rate in 2030: rows where act=Work AND hom30=1 across WD slots | > 2022 observed WFH rate (scenario-driven increase) |
| 5.6 2030 WD AT_HOME continuity | `|2030 WD AT_HOME mean - 2022 WD AT_HOME mean|` | ≤ 15 pp (gross continuity — no wild extrapolation) |

### Charts
- **AT_HOME overlay**: 48-slot line plot — 2030 forecast vs. 2022 observed (primary plausibility chart)
- Signed difference bar chart (2030 − 2022) for top-5 activities per DDAY_STRATA
- Night AT_HOME check line (same 48-slot view, highlighting slots 1–8)

---

## Section 6 — BEM Output Readiness

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 6.1 Schema: act30 columns | act30_001–048 all present in 2030 output | 100% present |
| 6.2 Schema: hom30 columns | hom30_001–048 all present in 2030 output | 100% present |
| 6.3 act30 range | All act30_* values ∈ {1..14} | 0 invalid codes |
| 6.4 hom30 range | All hom30_* values ∈ {0, 1} | 0 invalid values |
| 6.5 Row count | Total rows in `2030_synthetic_diaries.csv` | ≥ 37,000 (at minimum 2022-cohort-sized) |
| 6.6 DDAY_STRATA completeness | DDAY_STRATA values ∈ {1, 2, 3} only; all 3 strata represented | 0 unexpected values; all 3 strata present |

> **Step 7 note:** Census archetype linkage (DTYPE, BUILTH, BEDRM, etc.) is NOT done in
> Step 6. The `2030_synthetic_diaries.csv` contains occupancy schedules and demographics
> only. Building variable linkage follows the same Step 5 probabilistic matching logic and
> is executed as part of Step 7 BEM integration.

### Charts
- Table: column completeness rates for act30 and hom30 columns
- Bar chart: DDAY_STRATA distribution in 2030 output vs. observed 2022 distribution

---

## Section 7 — Summary Table

One row per hard gate and per validation section:

| Gate / Check | Threshold | Observed | Status |
|---|---|---|---|
| Sub-stage A val JS (WD) | < 0.15 | — | — |
| Sub-stage A val JS (Sat) | < 0.15 | — | — |
| Sub-stage A val JS (Sun) | < 0.15 | — | — |
| True Future Test JS: W_2005 on 2010 | < 0.20 per stratum | — | — |
| True Future Test JS: W_2010_ft on 2015 | < 0.20 per stratum | — | — |
| True Future Test JS: W_2015_ft on 2022 | < 0.20 per stratum | — | — |
| DRIFT_MATRIX_1522 COVID signal | ≥ +5 pp vs DRIFT_1015 WD | — | — |
| Backcasting reconstruction JS WD | < 0.10 | — | — |
| Backcasting reconstruction JS Sat | < 0.10 | — | — |
| Backcasting reconstruction JS Sun | < 0.10 | — | — |
| 2030 AT_HOME range | [55%, 90%] | — | — |
| 2030 WD < WE AT_HOME | WD < WE | — | — |
| 2030 night sleep (slots 1–8) | ≥ 70% | — | — |
| 2030 output row count | ≥ 37,000 | — | — |

---

## HTML Report Format

Following the same style as `step4_validation_report.html` and `step5_validation_report.html`:

1. **Header**: Step 6 — Longitudinal Forecasting Validation Report
2. **Summary pass/fail table** with severity indicators
3. **7 sections** with embedded base64 PNG charts
4. **Footer**: generation timestamp, input/output file paths

### Pass/Fail Severity Levels

| Level | Meaning |
|-------|---------|
| PASS | Check passes within expected bounds |
| WARN | Check passes but borderline (e.g., True Future Test JS = 0.19) |
| FAIL | Check fails — requires investigation before proceeding to Step 7 |

> **FAIL triage priority:** Section 4 FAILs (backcasting reconstruction JS ≥ 0.10) are
> blockers — they indicate the model has not captured inter-cycle drift and the 2030
> projection cannot be trusted. Section 5 FAILs on check 5.5 (WFH signal absent) are
> soft blockers — investigate scenario feature inputs. Section 1–2 FAILs on convergence
> should be investigated before running Sub-stage D inference.

---

## Checklist (for progress tracking)

- [ ] Create `06_longitudinalForecastingGSS_val.py` with `LongitudinalForecastingValidator` class
- [ ] Section 1: Training convergence + loss curve charts
- [ ] Section 2: True Future Test per phase + JS bar chart
- [ ] Section 3: DRIFT_MATRIX plausibility + heatmaps + COVID signal annotation
- [ ] Section 4: 2022 backcasting reconstruction + AT_HOME overlay + activity diff chart
- [ ] Section 5: 2030 schedule plausibility + AT_HOME overlay + signed diff chart
- [ ] Section 6: BEM output readiness + schema table
- [ ] Section 7: Summary table
- [ ] HTML report builder with base64 embedded PNGs
- [ ] End-to-end run: `py 06_longitudinalForecastingGSS_val.py` → `outputs_step6/step6_validation_report.html`

---

## Progress Log

| Date | Check | Result | Notes |
|---|---|---|---|
