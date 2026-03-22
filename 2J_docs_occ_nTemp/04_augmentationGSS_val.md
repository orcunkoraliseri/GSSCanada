# Step 4 — Conditional Transformer Augmentation: Validation Plan

## Goal

Validate the outputs of the Step 4 augmentation pipeline by verifying that synthetic diary schedules are statistically faithful to observed data, temporally plausible, and properly conditioned on demographic profiles. Produce an HTML report (`step4_validation_report.html`) with embedded charts.

**Input**: `outputs_step4/augmented_diaries.csv`, `outputs_step4/step4_training_log.csv`, `outputs_step4/best_model.pt`
**Reference**: `outputs_step3/hetus_30min.csv`, `outputs_step3/copresence_30min.csv`
**Output**: `outputs_step4/step4_validation_report.html`

---

## Script Structure: `04F_validation.py`

```python
"""Step 4 — Conditional Transformer Augmentation: Validation & Report Generation.

Validates augmented_diaries.csv against observed hetus_30min.csv and
copresence_30min.csv. Generates an HTML report with embedded charts.
"""

class AugmentationValidator:
    def __init__(self, step3_dir, step4_dir):
        # Load Step 3 CSVs (reference) and Step 4 outputs
        ...

    # ── Section 1 ────────────────────────────────────────────
    def validate_training_curves(self) → results_dict

    # ── Section 2 ────────────────────────────────────────────
    def validate_activity_distribution(self) → results_dict

    # ── Section 3 ────────────────────────────────────────────
    def validate_at_home_rate(self) → results_dict

    # ── Section 4 ────────────────────────────────────────────
    def validate_temporal_structure(self) → results_dict

    # ── Section 5 ────────────────────────────────────────────
    def validate_copresence_prevalence(self) → results_dict

    # ── Section 6 ────────────────────────────────────────────
    def validate_demographic_conditioning(self) → results_dict

    # ── Section 7 ────────────────────────────────────────────
    def validate_cross_stratum_consistency(self) → results_dict

    # ── Section 8 ────────────────────────────────────────────
    def generate_summary_table(self) → results_dict

    # ── Report ───────────────────────────────────────────────
    def build_html_report(self) → str
    def run_all(self)

if __name__ == "__main__":
    AugmentationValidator("outputs_step3", "outputs_step4").run_all()
```

---

## Section 1 — Training Curves

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 1.1 Loss convergence | Training loss curve is monotonically decreasing over first 10 epochs | No upward spike in first 10 epochs |
| 1.2 Validation JS improves | Val JS divergence improves for ≥20 epochs before plateau | At least 20 epochs of improvement |
| 1.3 No NaN/Inf | All loss values in training log are finite | 0 NaN or Inf entries |
| 1.4 Early stopping triggered | Training stopped before max epochs (100) | Patience triggered (indicates convergence) |
| 1.5 Component loss balance | Activity, AT_HOME, and co-presence losses are all decreasing | No single component diverging |

### Charts
- **1a — Training loss curve**: total loss + per-component (activity CE, AT_HOME BCE, co-presence BCE) vs. epoch
- **1b — Validation JS divergence**: per-stratum JS divergence vs. epoch (3 lines: Weekday / Saturday / Sunday)
- **1c — Gradient norm**: max gradient norm per epoch (should stay below clipping threshold 1.0 after warm-up)

---

## Section 2 — Activity Distribution Fidelity (Primary Metric)

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 2.1 Per-stratum JS divergence | For each CYCLE_YEAR × DDAY_STRATA: JS(P_obs ‖ P_syn) across 14 activity categories | JS < 0.05 for all 12 cells (4 cycles × 3 strata) |
| 2.2 Overall JS divergence | JS across all respondents (ignoring strata) | JS < 0.03 |
| 2.3 No missing categories | All 14 activity categories appear in synthetic diaries per stratum | 0 missing categories |
| 2.4 Dominant activity preserved | Most frequent activity per (cycle × stratum) is same in observed and synthetic | 100% match |

### Charts
- **2a — Activity distribution grouped bars**: for each DDAY_STRATA (3 panels), 14 grouped bar pairs (observed vs. synthetic), colored by cycle
- **2b — JS divergence heatmap**: 4 cycles × 3 strata matrix, colored by JS value (green < 0.03, yellow 0.03–0.05, red > 0.05)
- **2c — Per-activity delta**: bar chart of `P_syn(a) − P_obs(a)` for each of 14 categories, faceted by stratum

---

## Section 3 — AT_HOME Rate Consistency

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 3.1 Per-stratum AT_HOME rate | For each CYCLE_YEAR × DDAY_STRATA: \|rate_obs − rate_syn\| | < 2 percentage points |
| 3.2 Cross-cycle AT_HOME ordering | 2022 synthetic AT_HOME > 2015 > 2010 ≈ 2005 | Ordering preserved |
| 3.3 IS_SYNTHETIC flag integrity | Observed rows (IS_SYNTHETIC=0) have identical AT_HOME values to source | 100% exact match |

Expected baseline rates (from Step 3):
- 2005: ~62.7% | 2010: ~62.3% | 2015: ~64.5% | 2022: ~70.6%

### Charts
- **3a — AT_HOME rate table**: observed vs. synthetic per cycle × stratum (12 cells + totals)
- **3b — AT_HOME daily rhythm**: 48-slot line plot of mean AT_HOME rate, observed vs. synthetic overlaid, one panel per stratum
- **3c — AT_HOME delta by cycle**: bar chart of `rate_syn − rate_obs` per cycle

---

## Section 4 — Temporal Structure Plausibility

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 4.1 Sleep continuity | Count sleep-wake-sleep transitions in night slots (37–48, 1–8) per synthetic diary | ≤ 3 transitions for ≥ 95% of diaries |
| 4.2 Activity transition rate | Mean transitions per 48-slot diary, observed vs. synthetic | Synthetic within ±20% of observed |
| 4.3 Work peak hours | Paid work (category 1) proportion in slots 9–20 (08:00–14:00) | Synthetic within ±3 pp of observed |
| 4.4 Sleep onset time | Modal slot for sleep start, observed vs. synthetic | Within ±1 slot (30 min) |
| 4.5 No impossible sequences | No paid work at 3–5 AM for non-shift workers (LFTAG = standard employment) | < 1% violation rate |

### Charts
- **4a — Activity heatmap (observed vs. synthetic)**: 14 categories × 48 slots, two side-by-side panels per stratum (6 panels total)
- **4b — Transition count distribution**: histogram of transitions per diary, observed vs. synthetic overlaid
- **4c — Sleep onset distribution**: histogram of first sleep slot, observed vs. synthetic

---

## Section 5 — Co-Presence Prevalence Match

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 5.1 Per-column prevalence | For each co-presence column × CYCLE_YEAR × DDAY_STRATA: \|P_obs − P_syn\| (computed over non-NaN observed slots only) | < 3 percentage points per column |
| 5.2 Colleagues masking | `colleagues30_*` = 0 for all 2005/2010 synthetic diaries | 100% zero |
| 5.3 Alone–Spouse anti-correlation | If Alone=1 then Spouse should be 0 in same slot (logical consistency) | < 2% violation rate |
| 5.4 Co-presence value range | All synthetic co-presence values ∈ {0, 1} | No values outside range |
| 5.5 NaN-aware prevalence | Observed prevalence computed only from non-NaN source slots; NaN rates match expected: 2005 ~20%, 2010 ~19.3%, 2015 ~0.1%, 2022 ~6.8% for primary 8 cols | NaN rates within ±2 pp of expected |

### Charts
- **5a — Co-presence prevalence grouped bars**: 9 columns × 4 cycles, observed vs. synthetic side-by-side
- **5b — Co-presence delta heatmap**: 9 columns × (4 cycles × 3 strata) matrix, colored by `P_syn − P_obs`
- **5c — Alone rate daily rhythm**: 48-slot line plot, observed vs. synthetic, per stratum

---

## Section 6 — Demographic Conditioning Fidelity

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 6.1 AGEGRP activity correlation | Per age group: Pearson correlation of 14-category activity distribution (observed vs. synthetic) | r ≥ 0.9 per group |
| 6.2 LFTAG work hour separation | Employed respondents have higher paid-work proportion than not-in-labour-force | Directional difference preserved |
| 6.3 HHSIZE co-presence scaling | Larger HHSIZE → more co-presence (Spouse + Children + otherInFAMs) in synthetic diaries | Monotonic trend preserved |
| 6.4 SEX schedule differentiation | Activity distributions differ by SEX in same direction as observed | Correlation ≥ 0.85 per group |

### Charts
- **6a — Activity distribution by AGEGRP**: faceted bar chart (observed vs. synthetic) for 3 selected age groups (young / mid / senior)
- **6b — Work proportion by LFTAG**: grouped bar chart, observed vs. synthetic
- **6c — Co-presence by HHSIZE**: line plot of mean co-presence rate vs. HHSIZE, observed vs. synthetic

---

## Section 7 — Cross-Stratum Consistency

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 7.1 Weekday vs. weekend work | Weekday paid-work proportion > Saturday > Sunday | Ordering holds for ≥ 90% of respondents |
| 7.2 Weekend leisure increase | Saturday/Sunday leisure proportion > Weekday | Holds for ≥ 85% of respondents |
| 7.3 Weekend sleep shift | Weekend sleep-end (first non-sleep slot) ≥ Weekday | Mean shift ≥ 0 slots |
| 7.4 Weekend AT_HOME increase | Saturday/Sunday AT_HOME rate ≥ Weekday | Holds for ≥ 80% of respondents |
| 7.5 Demographic consistency | All 3 DDAY_STRATA diaries for a respondent share identical demographics | 100% match (trivially true from conditioning) |

### Charts
- **7a — Per-stratum activity radar**: radar/polar chart of 14 activity proportions for Weekday / Saturday / Sunday (observed vs. synthetic overlaid)
- **7b — Work proportion by stratum**: grouped bar chart per cycle
- **7c — AT_HOME by stratum**: grouped bar chart per cycle

---

## Section 8 — Dataset Statistics Summary Table

A single summary table aggregating key statistics:

| Statistic | 2005 | 2010 | 2015 | 2022 | Total |
|-----------|------|------|------|------|-------|
| Observed diary-days | | | | | |
| Synthetic diary-days | | | | | |
| Total augmented diary-days (×3 strata) | | | | | |
| Mean JS divergence (activity) | | | | | |
| Mean \|Δ AT_HOME\| (pp) | | | | | |
| Mean \|Δ co-presence\| (pp) | | | | | |
| Sleep continuity pass rate (%) | | | | | |
| Activity transition rate ratio (syn/obs) | | | | | |
| Demographic conditioning r (mean) | | | | | |
| Weekday>Weekend work ordering (%) | | | | | |

---

## HTML Report Format

Following the same style as `step3_validation_report.html`:

1. **Header**: Step 4 — Conditional Transformer Augmentation Validation Report
2. **Summary pass/fail table** with severity indicators (PASS / WARN / FAIL)
3. **8 sections** with embedded base64 PNG charts
4. **Footer**: generation timestamp, model checkpoint path, training epochs completed

### Pass/Fail Severity Levels

| Level | Meaning |
|-------|---------|
| PASS | Check passes within expected bounds |
| WARN | Check passes but with marginal values (e.g., JS between 0.03 and 0.05) |
| FAIL | Check fails — requires investigation before proceeding to Step 5/6 |

---

## Checklist (for progress tracking)

- [ ] Create `04F_validation.py` with `AugmentationValidator` class
- [ ] Section 1: Training curves + loss component charts
- [ ] Section 2: Activity distribution fidelity + JS heatmap
- [ ] Section 3: AT_HOME rate consistency + daily rhythm comparison
- [ ] Section 4: Temporal structure plausibility + activity heatmaps
- [ ] Section 5: Co-presence prevalence match + delta heatmap
- [ ] Section 6: Demographic conditioning fidelity + per-group charts
- [ ] Section 7: Cross-stratum consistency + radar charts
- [ ] Section 8: Summary statistics table
- [ ] HTML report builder with base64 embedded PNGs
- [ ] End-to-end run: `python 04F_validation.py` → `step4_validation_report.html`
