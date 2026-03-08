# Step 3 — Merge & Temporal Feature Derivation: Validation Plan

## Goal

Validate the outputs of `03_mergingGSS.py` by verifying merge integrity, derived feature correctness, and HETUS 144-slot conversion quality. Produce an HTML report (`step3_validation_report.html`) with embedded charts.

**Input**: `outputs_step3/merged_episodes.csv`, `outputs_step3/hetus_wide.csv`
**Reference**: `outputs_step2/main_*.csv`, `outputs_step2/episode_*.csv`
**Output**: `outputs_step3/step3_validation_report.html`

---

## Script Structure: `03_mergingGSS_val.py`

```python
"""Step 3 — Validation & Report Generation.

Validates merged dataset and HETUS wide format against Step 2 inputs.
Generates an HTML report with embedded charts.
"""

class GSSMergeValidator:
    def __init__(self, step2_dir, step3_dir):
        # Load Step 2 CSVs (reference) and Step 3 outputs
        ...

    # ── Section 1 ────────────────────────────────────────────
    def validate_row_counts(self) → results_dict

    # ── Section 2 ────────────────────────────────────────────
    def validate_merge_integrity(self) → results_dict

    # ── Section 3 ────────────────────────────────────────────
    def validate_derived_features(self) → results_dict

    # ── Section 4 ────────────────────────────────────────────
    def validate_hetus_slots(self) → results_dict

    # ── Section 5 ────────────────────────────────────────────
    def validate_cross_cycle_consistency(self) → results_dict

    # ── Section 6 ────────────────────────────────────────────
    def generate_summary_table(self) → results_dict

    # ── Report ───────────────────────────────────────────────
    def build_html_report(self) → str
    def run_all(self)

if __name__ == "__main__":
    GSSMergeValidator("outputs_step2", "outputs_step3").run_all()
```

---

## Section 1 — Row Count Preservation

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 1.1 Main row counts | Compare `unified_main` per-cycle counts vs. Step 2 `main_*.csv` row counts | Exact match per cycle |
| 1.2 Episode row counts (pre-filter) | Compare `unified_episode` per-cycle counts vs. Step 2 `episode_*.csv` row counts | Exact match per cycle |
| 1.3 Merge row count | `len(merged) == len(unified_episode)` | LEFT JOIN preserves all episode rows |
| 1.4 DIARY_VALID exclusions | Count respondents removed per cycle | Exclusion rate < 5% per cycle |
| 1.5 Post-filter totals | Total respondents and episodes after DIARY_VALID filtering | Log for reference |

### Charts
- Grouped bar chart: respondents per cycle (Step 2 vs. Step 3 pre-filter vs. Step 3 post-filter)
- Table: per-cycle exclusion counts and rates

---

## Section 2 — Merge Key Integrity

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 2.1 No orphan episodes | All `(occID, CYCLE_YEAR)` in episodes exist in Main | 0 orphan episodes |
| 2.2 No duplicate respondents | `(occID, CYCLE_YEAR)` unique in unified Main | 0 duplicates |
| 2.3 Weight propagation | `WGHT_PER` is not NaN for all merged rows | 100% non-null |
| 2.4 CYCLE_YEAR consistency | `CYCLE_YEAR` from episode matches `CYCLE_YEAR` from Main after merge | 100% match |

### Charts
- Orphan episode count table (should be all zeros)
- Weight column null-rate bar chart

---

## Section 3 — Derived Feature Verification

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 3.1 DAYTYPE values | `DAYTYPE ∈ {"Weekday", "Weekend"}` | No other values |
| 3.2 DAYTYPE ratio | Weekday ~71%, Weekend ~29% (5:2 ratio) | Within 65–77% weekday |
| 3.3 HOUR_OF_DAY range | `HOUR_OF_DAY ∈ {0, 1, ..., 23}` | All 24 hours represented |
| 3.4 TIMESLOT_10 range | `TIMESLOT_10 ∈ {1, 2, ..., 144}` | All 144 slots represented |
| 3.5 startMin range | `startMin ∈ [0, 1439]` | No out-of-range values |
| 3.6 DDAY_STRATA range | `DDAY_STRATA ∈ {1, 2, ..., 7}` | All 7 days represented |
| 3.7 DAYTYPE ↔ DDAY consistency | Weekday = DDAY ∈ {2,3,4,5,6}, Weekend = DDAY ∈ {1,7} | 100% consistent |

### Charts
- DAYTYPE distribution bar chart (overall + per cycle)
- HOUR_OF_DAY histogram (episode start times)
- TIMESLOT_10 distribution histogram
- DDAY_STRATA bar chart per cycle

---

## Section 4 — HETUS 144-Slot Integrity

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 4.1 Slot completeness | All `slot_001`–`slot_144` non-null per respondent | 100% complete |
| 4.2 Activity code validity | All slot values ∈ {1, 2, ..., 14} | No invalid codes |
| 4.3 AT_HOME completeness | All `home_001`–`home_144` non-null per respondent | 100% complete |
| 4.4 AT_HOME validity | All home slot values ∈ {0, 1} | Binary only |
| 4.5 Respondent count | `hetus_wide` row count == unique `(occID, CYCLE_YEAR)` in merged (post-filter) | Exact match |
| 4.6 Sleep dominance in night slots | Slots covering ~22:00–06:00 should have Sleep (occACT=1) as modal activity | Sleep > 50% in night slots |
| 4.7 AT_HOME night rate | `home_*` slots covering ~22:00–06:00 should average > 80% | Home rate > 80% at night |

### Charts
- **Activity heatmap**: 14 activity categories × 144 time slots (rows=activities, cols=slots, color=proportion). This is the key visual — it should show clear diurnal patterns (sleep at night, work during day, meals at mealtimes).
- **AT_HOME curve**: Line plot of mean AT_HOME rate across 144 slots (should show high home rate at night, dip during work hours, return in evening).
- Slot completeness summary (% respondents with all 144 filled).

---

## Section 5 — Cross-Cycle Consistency

### Checks

| Check | Logic | Pass Criterion |
|-------|-------|----------------|
| 5.1 Weighted activity distribution | Per-cycle weighted `occACT` proportions (using `WGHT_EPI`) | Broadly consistent; known shifts acceptable |
| 5.2 Weighted AT_HOME rate | Per-cycle weighted mean AT_HOME | Within 55–75% range per cycle |
| 5.3 Demographic preservation | AGEGRP, SEX, HHSIZE distributions per cycle | Must match Step 2 marginals exactly |
| 5.4 Episode count per respondent | Mean/median episodes per respondent per cycle | Reasonable range (10–30) |

### Charts
- Stacked bar chart: weighted activity proportions per cycle (14 categories)
- Line chart: weighted AT_HOME rate per cycle
- Demographic bar charts per cycle (AGEGRP, SEX, HHSIZE) — side-by-side with Step 2 values
- Box plot: episodes per respondent, grouped by cycle

---

## Section 6 — Dataset Statistics Summary Table

A single summary table aggregating key statistics from all sections:

| Statistic | 2005 | 2010 | 2015 | 2022 | Total |
|-----------|------|------|------|------|-------|
| Respondents (Step 2) | | | | | |
| Respondents (Step 3 pre-filter) | | | | | |
| Respondents (Step 3 post-filter) | | | | | |
| DIARY_VALID exclusion rate | | | | | |
| Total episodes (post-filter) | | | | | |
| Mean episodes per respondent | | | | | |
| Median episodes per respondent | | | | | |
| HETUS wide rows | | | | | |
| Slots with valid activity (%) | | | | | |
| Weighted AT_HOME rate (%) | | | | | |
| Weekday % | | | | | |
| Weekend % | | | | | |

---

## HTML Report Format

Following the same style as `step2_validation_report.html`:

1. **Header**: Step 3 — Merge & Temporal Feature Derivation Validation Report
2. **Summary pass/fail table** with severity indicators (PASS / WARN / FAIL)
3. **6 sections** with embedded base64 PNG charts
4. **Footer**: generation timestamp, input/output file paths

### Pass/Fail Severity Levels

| Level | Meaning |
|-------|---------|
| PASS | Check passes within expected bounds |
| WARN | Check passes but with unexpected values (e.g., exclusion rate 3–5%) |
| FAIL | Check fails — requires investigation before proceeding to Step 4 |

---

## Checklist (for progress tracking)

- [ ] Create `03_mergingGSS_val.py` with `GSSMergeValidator` class
- [ ] Section 1: Row count preservation checks + grouped bar chart
- [ ] Section 2: Merge key integrity checks + orphan table
- [ ] Section 3: Derived feature verification + distribution charts
- [ ] Section 4: HETUS slot integrity + activity heatmap + AT_HOME curve
- [ ] Section 5: Cross-cycle consistency + weighted distribution charts
- [ ] Section 6: Summary statistics table
- [ ] HTML report builder with base64 embedded PNGs
- [ ] End-to-end run: `python 03_mergingGSS_val.py` → `step3_validation_report.html`
