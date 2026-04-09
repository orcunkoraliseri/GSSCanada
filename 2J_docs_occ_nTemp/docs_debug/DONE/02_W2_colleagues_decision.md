# Task 1 — W2: `colleagues` Half-Observed Decision

**Date:** 2026-04-09  
**Input:** `outputs_step3/merged_episodes.csv` (Step 3 output, read-only)  
**Output:** Decision on how Model 1 (Step 4) should handle `colleagues` (TUI_06I)

---

## Data Overview

`merged_episodes.csv` has 1,049,480 rows across 4 cycles.

| Cycle year | Total episodes | `colleagues == 1` | `colleagues == 2` | NaN |
|-----------|---------------|-------------------|-------------------|-----|
| 2005 | 328,143 | 0 | 0 | 328,143 (100%) |
| 2010 | 279,151 | 0 | 0 | 279,151 (100%) |
| 2015 | 274,108 | 12,680 | 261,088 | 340 (0.1%) |
| 2022 | 168,078 | 4,774 | 151,944 | 11,360 (6.8%) |

`colleagues` is entirely absent for 2005 and 2010. The 2022 NaN rate (6.8%)
reflects instrument/design gaps but is not a coding problem.

*Re-baselined 2026-04-09: 2005/2010 row counts updated against Step 3 outputs
regenerated during Task 2a (original counts were 303,703 / 303,591). The
2015/2022 numbers and all decision conclusions are unchanged.*

---

## (a) Episode-Level Share of `colleagues == 1`

Computed over observed (non-NaN) episodes only.

| Cycle year | Observed episodes | `colleagues == 1` share |
|-----------|------------------|------------------------|
| 2015 | 273,768 | **4.63%** |
| 2022 | 156,718 | **3.05%** |

The drop from 4.63% to 3.05% is consistent with the WFH increase
documented in the COVID drift analysis (AT_HOME: 63.5% → 72.3%).
Fewer episodes occur in the physical presence of colleagues when more
people work from home.

---

## (b) Respondent-Level Share (≥1 `colleagues == 1` episode in diary)

| Cycle year | Respondents | Share with ≥1 colleagues episode |
|-----------|-------------|----------------------------------|
| 2015 | 17,390 | **27.4%** |
| 2022 | 12,336 | **20.9%** |

More than one in four respondents in 2015 spent some time with
colleagues during their diary day. This is not a rare edge-case signal.

---

## (c) Cross-Tab Against `LFTAG` and `DDAY_STRATA`

### 2015 — Episode-level share of `colleagues == 1`

| LFTAG \ DDAY_STRATA | Weekday | Saturday | Sunday |
|---------------------|---------|----------|--------|
| Employed (n~92K) | **10.49%** | 2.59% | 2.10% |
| Unemployed (n~8.5K) | **11.68%** | 4.21% | 2.76% |
| Not-in-LF (n~92K) | 0.60% | 0.33% | 0.32% |

### 2022 — Episode-level share of `colleagues == 1`

| LFTAG \ DDAY_STRATA | Weekday | Saturday | Sunday |
|---------------------|---------|----------|--------|
| Employed (n~53K) | **6.66%** | 2.51% | 2.51% |
| Unemployed (n~2K) | **8.67%** | 4.36% | 3.72% |
| Not-in-LF (n~55K) | 0.40% | 0.50% | 0.20% |

**Key observations:**

1. The signal is almost entirely concentrated in **Employed × Weekday**
   (10.5% in 2015, 6.7% in 2022). Outside this cell, rates fall to
   0.3–2.6%.

2. The Employed × Weekday drop (10.5% → 6.7%, −3.8 pp) directly mirrors
   the WFH shift. This is a real, interpretable behavioral signal.

3. Not-in-LF rates are negligible (<0.6%) across all day types — these
   respondents rarely encounter colleagues regardless of day.

4. The signal is **structured**: it varies by labor force status × day
   type in a way that is demographically sensible and internally
   consistent across cycles.

---

## Decision

**Recommendation: Option 2 — predict `colleagues` only when the
conditioning cycle is 2015 or 2022; emit NaN (and apply masked loss)
for 2005/2010 strata.**

### Rationale

**For keeping `colleagues` in the output (vs. Option 3 — drop entirely):**

- 27% respondent prevalence in 2015 is too high to ignore. At roughly
  one-in-four diary respondents, this is a mainstream behavioral signal,
  not a niche co-presence category.
- The 2015 → 2022 decline is interpretable and publishable as part of
  the COVID drift story. Dropping it throws away one of the cleanest
  cross-cycle behavioral trends in the data.
- For BEM: if `colleagues` is present, multiple people are co-located
  during working hours, which affects metabolic gain estimates. Keeping
  the column preserves this downstream option.

**For restricting to 2015/2022 strata (vs. Option 1 — predict for all
cycles):**

- Ground truth is fully absent for 2005/2010. There is no validation
  lever whatsoever for those cycles.
- The 2005/2010 social context (commuting norms, remote-work rates)
  was materially different from 2015/2022. Any learned `colleagues`
  pattern is extrapolation without a demographic bridge.
- The calibration risk is bounded: for 2005/2010-anchored BEM runs,
  `colleagues` simply contributes nothing (NaN). That is conservative,
  not wrong.
- Masked-loss training on 2015/2022 is already planned for Step 4.
  Option 2 just extends the same mechanism: the model learns the
  colleagues signal from 2015/2022 and does not emit it for cycle
  conditions where it was never observed.

### Implementation note for Step 4

- `colleagues` remains a decoder output (9th co-presence column, 48
  slots).
- Loss is masked for all 2005/2010 episodes (as currently planned).
- For inference: when the conditioning cycle indicator is 2005 or 2010,
  emit NaN rather than a predicted binary. This requires a one-line
  post-processing mask applied after the decoder output.
- The Step 4 output schema should document: "colleagues: predicted for
  cycle ∈ {2015, 2022}; NaN for cycle ∈ {2005, 2010}."

### Estimated calibration risk

Employed × Weekday episodes represent ~35% of the 2015 corpus and ~33%
of 2022. Within this cell, a ~10% `colleagues` rate means that for every
10 employed-weekday episodes, 1 involves co-worker co-presence. Dropping
or mis-predicting this signal would slightly underestimate internal
gains during daytime work hours, but the effect is bounded by the cell
frequency and is not load-critical at the whole-building EUI level.

---

## Consistency check (as specified in SWOT Task 1)

After this decision, the Step 4 schema should show:

| Element | State |
|---------|-------|
| `colleagues` in decoder output | Yes (9th co-presence col) |
| Loss masked for 2005/2010 | Yes |
| Inference output for 2005/2010 | NaN (post-decoder mask) |
| Inference output for 2015/2022 | Binary predicted value |
| Step 6 progressive fine-tuning target | 2015/2022 `colleagues` signal included |
| Step 7 BEM use | Optional; safe to include for 2015/2022 archetypes |

If any of these are inconsistent after writing the Step 4 spec, the
decision needs revisiting.

---

## Progress Log

**2026-04-09 — Review of Sonnet's Task 1 execution**

Numbers look healthy.
- Episode-level 4.63% / 3.05% is in the expected range — `colleagues` is a
  sparse but real signal, not a phantom column.
- 27.4% / 20.9% respondent-level prevalence confirms it touches roughly
  1 in 4–5 diaries. Definitely too much to drop.
- The Employed × Weekday cell (10.5% → 6.7%) is the cleanest possible
  signature of the WFH shift. That's a real, interpretable result on its own.

Recommendation (Option 2) is the right call.
- It matches the existing masked-loss design in Step 4 — extends the same
  mask from training time to inference time. One-line change in the decoder
  post-processing, no architectural rework.
- It preserves the publishable 2015→2022 drop for the COVID-drift story
  (Artifact 3 in Task 6 / O1).
- It avoids fabricating predictions on a column that has no ground truth
  for half the corpus, which would be the weakest part of the methods
  section under reviewer scrutiny.

One thing to make sure lands in the Step 4 spec when it gets written:
- The NaN mask at inference must be conditioned on
  `CYCLE_YEAR ∈ {2005, 2010}`, not on whether the *input* `colleagues` was
  observed. Otherwise a 2015/2022 respondent who happens to have all-zero
  colleagues episodes will be wrongly NaN'd.

Optional sanity check (only if extra confidence is wanted before closing):
- Cross-tab `colleagues == 1` against `AT_HOME == 0` for the
  Employed × Weekday cell. Expected pattern: vast majority of
  `colleagues == 1` episodes have `AT_HOME == 0` in 2015 (in-office) and a
  noticeably higher share with `AT_HOME == 1` in 2022 (Zoom calls / hybrid).
  If that pattern shows, it is a second independent confirmation that the
  encoding is correct *and* a bonus figure for the COVID-drift artifact.

**Status:** Task 1 closed cleanly. Safe to move on to Task 2 (W3 SEASON).
