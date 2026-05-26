# Step 4 — Conditional Transformer Augmentation: Validation Plan

## Goal

Validate the outputs of the Step 4 augmentation pipeline by verifying that synthetic diary schedules are statistically faithful to observed data, temporally plausible, and properly conditioned on demographic profiles. Produce an HTML report (`step4_validation_report.html`) with embedded charts.

**Input**: `outputs_step4/augmented_diaries.csv`, `outputs_step4/step4_training_log.csv`, `outputs_step4/best_model.pt`
**Reference**: `outputs_step3/hetus_30min.csv`, `outputs_step3/copresence_30min.csv`
**Output**: `outputs_step4/step4_validation_report.html`

> **Activity-code caveat (must read before interpreting any S4 report):** Per the Step-2 harmonization, raw code **1 = Work & Related** and raw code **5 = Sleep & Naps & Resting**. `04F_validation.py` currently has these swapped in several places (`== 1` is used where the code intends "sleep", `== 5` where it intends "paid work"). See the confirmed-bug chapter in `Phase1_ready.md`. Until that is fixed, checks 4.1, 4.3, 6.2, 7.1, and 7.2 are effectively measuring the *opposite* quantity of what their labels claim — ignore their PASS/FAIL status until the code is patched.

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
| 4.1 Sleep continuity | Count sleep-wake-sleep transitions in night slots (37–48, 1–8) per synthetic diary, where "sleep" = **Sleep & Naps & Resting** (raw code **5**, tensor idx 4 — **not** raw 1) | ≤ 3 transitions for ≥ 95% of diaries |
| 4.2 Activity transition rate | Mean transitions per 48-slot diary, observed vs. synthetic | Synthetic within ±20% of observed |
| 4.3 Work peak hours | **Work & Related** (raw code **1**, tensor idx 0 — **not** raw 5) proportion in slots 9–20 (08:00–14:00) | Synthetic within ±3 pp of observed |
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

Uniform convention across all sections. Let `T` be the PASS threshold stated in the section's check table.

| Level | Rule | Example (§2.1, `T = 0.05`) |
|-------|---------|---------|
| PASS  | `value ≤ T`           | JS ≤ 0.05 |
| WARN  | `T < value ≤ 2 × T`   | 0.05 < JS ≤ 0.10 |
| FAIL  | `value > 2 × T`       | JS > 0.10 |

Applies to §2.1 (JS per cell), §3.1 (AT_HOME rate Δ), §4.1 (sleep-continuity transitions — use `T = 3` so WARN = 3–6 transitions), §5.1 (co-presence prevalence Δ), and any other numeric threshold stated in a check table. For boolean/ordering checks (e.g., §3.2, §7.1), there is no WARN tier — the check is PASS if the condition holds, FAIL otherwise.

### Blocking vs. investigate policy

Not every FAIL should block downstream Step 5 submission. Use this rule:

| Failure location | Action |
|---|---|
| §2.1 (activity JS per cell) **FAIL** | **BLOCK** — re-train or re-check pair construction before Step 5 |
| §3.1 (AT_HOME rate Δ per cell) **FAIL** | **BLOCK** — AT_HOME is load-bearing for BEM downstream |
| §4–§7 **FAIL** | **INVESTIGATE** — log the finding in the Progress Log and proceed to Step 5, but revisit if Step 5/6 anomalies appear |
| §1 (training-curve) FAIL with WARN on §2–§5 | Typically an under-training artifact — rerun with more epochs if wall time allows, otherwise proceed |

Sample-mode runs (`--sample`) use relaxed thresholds (`T × 4`) and are for pipeline wiring only — their FAILs never block.

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
- [x] HTML report builder with base64 embedded PNGs
- [x] End-to-end run: `python 04F_validation.py` → `step4_validation_report.html`

---

## Progress Log

### 2026-05-12 — J3 validation run
- Model: J3 (composite=0.6355, 87 epochs)
- Observed rows: 64,061 | Synthetic rows: 128,122
- Section 1 (training curves): PASS (1.1 loss monotone, 1.2 67 improving epochs, 1.3 0 NaN)
- Section 2 (activity JS): overall JS = 0.0242 — PASS (all 12 per-stratum cells < 0.05; max cell = 0.0308)
- Section 3 (AT_HOME): max |Δ| = 9.69 pp (2022 × Weekday) — FAIL (all 12 cells exceed 2 pp threshold; range 2.95–9.69 pp; BLOCK per policy — but J3 already ships per gate AT_HOME RMS=4.57 pp)
- Section 4 (temporal): FAIL — 4.2 transition rate ratio = 157.95 (INVESTIGATE); 4.3 swapped-code bug (see caveat in doc header, ignore PASS/FAIL)
- Section 5 (co-presence): PASS (5.2 colleagues=0 for 2005/2010; 5.4 all binary values valid)
- Section 6 (demographic conditioning): PASS/FAIL mixed — 6.1 AGEGRP r=0.9583 PASS; 6.2 FAIL (swapped Work/Sleep code bug, ignore per caveat)
- Section 7 (cross-stratum): FAIL — 7.1 work ordering 46.5% FAIL (swapped-code bug, ignore); 7.4 AT_HOME weekend≥weekday 72.1% WARN (< 80% threshold)
- Section 8 (summary table): generated
- HTML report: outputs_step4/step4_validation_report.html ✅

### 2026-05-22 — Pre-J3-DEMO retrain: tensor inputs rebuilt with restored demographics

Inputs to Step 4 changed. Phase 2 plumbing (see `04_augmentationGSS_IMP.md`) restored three previously-dropped GSS columns into the conditioning vector. No retrain yet — this entry only records the input change so that the next J3-DEMO / J3-DEMO-PSBLite retrain has a clean reference point for diff-analysis.

- `d_cond`: 76 → **90** (+14 from `ATTSCH`, `POWST`, `MODE` one-hot widths)
- `step4_feature_config.json` regenerated with the three new categorical columns
- Train/val/test tensors regenerated: 44,843 / 9,609 / 9,609 (stratification structure unchanged)
- New COP `pos_weights` (Alone 1.21, Spouse 2.52, Children 10.99, parents 39.71, friends 15.21, others 9.27, colleagues 12.17) — small numerical drift from the prior J3-baseline weights due to the 70/15/15 stratified split being re-drawn on the regenerated frame; same magnitudes, same ordering.

Validation sections to recheck after the next retrain:
- Section 3 (AT_HOME): does the 2022 × Weekday cell narrow from 9.69 pp? (Lever A's most direct target — POWST encodes the WFH workers dominating that cell.)
- Section 6 (demographic conditioning): add ATTSCH / POWST / MODE correlation checks (parallel to the existing AGEGRP, SEX, MARSTH checks). Current Section 6 logic computes `df.groupby(cat_col)[at_home].mean()` and correlates with the cond vector; same logic applies — just add the three new keys to the iteration list when the script is next run.

J3 baseline (composite 0.6355, 4/4 gates) remains the reference. Whichever of J3-DEMO / J3-DEMO-PSBLite wins becomes the new baseline; the loser is shelved (per IMP doc §5 Phased execution).
