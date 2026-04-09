# Task 2 — W3: SEASON Coverage Gap Decision

**Date:** 2026-04-09  
**Input:** `outputs_step3/merged_episodes.csv` (read-only) +
`outputs_step2/main_2015.csv` / `main_2022.csv` for `SURVMNTH` join  
**Output:** Decision on how Model 1 (Step 4) should handle `SEASON`

---

## Setup

`SURVMNTH` is present in the Step 2 main files for 2015 and 2022,
and entirely absent (all NaN) for 2005 and 2010 — as confirmed in the
Step 3 validation pass. SEASON is derived from SURVMNTH using:

| Months | SEASON |
|--------|--------|
| Dec, Jan, Feb | Winter |
| Mar, Apr, May | Spring |
| Jun, Jul, Aug | Summer |
| Sep, Oct, Nov | Fall |

**Episode counts per season (pooled 2015 + 2022):**

| Season | Episodes |
|--------|----------|
| Winter | 150,152 |
| Fall | 136,667 |
| Spring | 128,925 |
| Summer | 124,993 |
| **Total** | **540,737** |

All episodes in 2015/2022 have a valid SEASON. No imputation needed.

---

## (1) AT_HOME Marginals by SEASON × DDAY_STRATA

### AT_HOME (%) by season — pooled 2015 + 2022

| Season | AT_HOME % |
|--------|-----------|
| Winter | 68.79% |
| Fall | 68.74% |
| Spring | 68.14% |
| Summer | 67.98% |
| **Max spread** | **0.81 pp** |

### Per cycle

| Cycle | Winter | Spring | Summer | Fall | Spread |
|-------|--------|--------|--------|------|--------|
| 2015 | 66.50% | 65.59% | 66.06% | 65.62% | 0.92 pp |
| 2022 | 72.68% | 72.34% | 71.30% | 72.33% | 1.38 pp |

### AT_HOME (%) by SEASON × DDAY_STRATA (pooled 2015 + 2022)

| Day type | Winter | Spring | Summer | Fall | Spread |
|----------|--------|--------|--------|------|--------|
| Weekday | 68.29% | 67.70% | 68.08% | 68.48% | **0.78 pp** |
| Saturday | 68.29% | 67.99% | 65.96% | 67.51% | **2.34 pp** |
| Sunday | 71.66% | 70.47% | 69.29% | 71.26% | **2.37 pp** |

**Interpretation:** Weekday AT_HOME is essentially flat across seasons
(0.78 pp). The weekend spread reaches ~2.4 pp driven mainly by the
Winter/Sunday peak, consistent with Canadians staying in on cold
winter weekends, but the effect is small in absolute terms.

---

## (2) Per-Activity Shares and JS Divergence Across Seasons

### Activity shares (%) by season — pooled 2015 + 2022

| Activity | Winter | Spring | Summer | Fall | Max diff (pp) |
|----------|--------|--------|--------|------|---------------|
| Sleep & Naps & Resting | 36.78 | 36.53 | 36.60 | 36.57 | **0.24** |
| Passive Leisure | 15.85 | 15.58 | 14.83 | 14.69 | **1.16** |
| Work & Related | 12.68 | 12.72 | 12.53 | 12.98 | **0.45** |
| Household Work & Maintenance | 9.40 | 9.69 | 10.32 | 10.05 | **0.92** |
| Eating & Drinking | 5.39 | 5.43 | 5.46 | 5.37 | **0.08** |
| Travel | 4.23 | 4.31 | 4.56 | 4.13 | **0.43** |
| Socializing | 3.59 | 3.73 | 4.09 | 3.63 | **0.50** |
| Personal Care | 3.56 | 3.51 | 3.56 | 3.65 | **0.14** |
| Active Leisure | 1.76 | 1.85 | 2.12 | 1.94 | **0.36** |
| Purchasing Goods & Services | 1.91 | 1.81 | 1.72 | 1.82 | **0.19** |
| Caregiving & Help | 2.14 | 2.00 | 1.92 | 2.04 | **0.22** |
| Community & Volunteer | 0.85 | 0.94 | 0.83 | 0.91 | **0.12** |
| Education | 1.16 | 1.23 | 0.74 | 1.37 | **0.62** |
| Miscellaneous / Idle | 0.70 | 0.68 | 0.73 | 0.85 | **0.17** |

The two largest movers are:
1. **Passive Leisure:** 14.69% (Fall) → 15.85% (Winter), +1.16 pp.
   Classic indoor-leisure amplification in cold months.
2. **Household Work & Maintenance:** 9.40% (Winter) → 10.32% (Summer),
   +0.92 pp. Consistent with outdoor maintenance shifting to warm months.
3. **Education:** 0.74% (Summer) → 1.37% (Fall), +0.62 pp.
   School-year effect.

No activity shifts by more than 1.2 pp across seasons.

### JS divergence between season pairs — binary (activity vs rest)

Ranked by mean JS across all season pairs:

| Activity | Mean JS (×10⁻⁴) | Max JS (×10⁻⁴) |
|----------|----------------|----------------|
| Education | 2.60 | 6.84 |
| Passive Leisure | 0.90 | 1.88 |
| Household Work & Maintenance | 0.65 | 1.70 |
| Socializing | 0.51 | 1.23 |
| Active Leisure | 0.45 | 1.25 |
| Travel | 0.29 | 0.79 |
| Miscellaneous / Idle | 0.27 | 0.69 |
| Caregiving & Help | 0.15 | 0.44 |
| Purchasing Goods & Services | 0.12 | 0.37 |
| Community & Volunteer | 0.12 | 0.28 |
| Work & Related | 0.11 | 0.33 |
| Personal Care | 0.04 | 0.11 |
| Sleep & Naps & Resting | 0.02 | 0.05 |
| Eating & Drinking | 0.01 | 0.02 |

Education leads by a factor of 3×, but even its max JS (6.84 × 10⁻⁴)
is two orders of magnitude below a threshold that would typically
warrant a separate conditioning variable (~0.01–0.05 in practice).

### Full 14-activity distribution JS between season pairs

| Season pair | JS (full dist) |
|-------------|----------------|
| Summer vs Fall | 0.001004 |
| Winter vs Summer | 0.000987 |
| Spring vs Summer | 0.000780 |
| Winter vs Fall | 0.000424 |
| Spring vs Fall | 0.000262 |
| Winter vs Spring | 0.000105 |

**All values < 0.001.** The seasonal structure in these diaries is
extremely weak by the JS divergence measure. Weekday-only JS is
comparable (max 0.001094), confirming the signal is not concentrated
in any single day-type stratum.

---

## (3) Summary of Findings

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AT_HOME spread (Weekday) | 0.78 pp | < 2 pp = safe to drop | ✅ well below |
| AT_HOME spread (Weekend) | 2.34–2.37 pp | > 5 pp = must keep | ✅ well below |
| Max per-activity spread | 1.16 pp (Passive Leisure) | < 2 pp = safe to drop | ✅ below |
| Max full-distribution JS | 0.001004 | — | Noise-floor level |
| Max per-activity JS | 6.84 × 10⁻⁴ (Education) | — | Noise-floor level |

---

## Decision

**Recommendation: (a) Drop SEASON from the conditioning vector entirely.**

### Rationale

1. **The seasonal lift is negligible at the BEM-relevant stratum.**
   Weekday AT_HOME varies by only 0.78 pp across seasons. This is far
   below 2 pp, which was the threshold specified in the SWOT analysis
   for "drop is fine." BEM is primarily driven by weekday schedules;
   seasonal fine-structure on weekends at <2.4 pp will not materially
   affect EUI calculations.

2. **The JS divergence is at the noise floor.**
   The highest full-distribution JS between any two season pair is
   0.001004. For context, a difference of 0.01 is generally considered
   perceptible in distributional terms; values in the 0.05–0.20 range
   are what typically motivate separate conditioning dimensions in
   generative models. These season-pair JS values are 10–50× below that
   threshold.

3. **Including SEASON creates a structural asymmetry with no payoff.**
   For 2005/2010 strata, SEASON would have to be masked or imputed —
   which means the conditioning vector is uninformative for half the
   training corpus. The model would need to learn to condition on
   something that is absent 50% of the time, for a signal that is too
   small to matter even when it is present. This is complexity without
   return.

4. **The signal is demographically correlated anyway.**
   The Education summer drop is real but it is captured indirectly by
   demographic strata: students are concentrated in specific AGEGRP
   bands, and their summer activity shift is co-linear with school
   term, which is predictable from age × cycle year. Adding SEASON
   would duplicate what the demographic conditioning already encodes.

5. **The weekend spreads (2.34 pp, 2.37 pp) are border-line but do not
   change the verdict.** They land between the "safe to drop" (<2 pp)
   and "must keep" (>5 pp) thresholds. Given the considerations in
   points 2–4, the tie-break favors dropping: the 0.001 JS tells us
   the distributional effect is real but practically undetectable after
   training.

### Proxy check for 2005/2010

The question in Task 2 asked whether any proxy for survey month
exists for 2005/2010. Answer: **no.** The Step 2 main file shows
`SURVMNTH = NaN` for 100% of 2005 and 2010 respondents. Statistics
Canada did not include interview month in the PUMF release for those
cycles. No imputation is feasible.

### Implementation note for Step 4

- Remove `SEASON` / `SURVMNTH` from the Model 1 conditioning vector.
- The existing `DDAY_STRATA` (3-category: Weekday / Saturday / Sunday)
  is sufficient as the temporal conditioning dimension for all four cycles.
- `SURVMNTH` can be retained in `merged_episodes.csv` as a diagnostic
  column for future analysis (e.g., a reviewer asks for it), but it
  does not enter the model.
- The Step 4 conditioning vector spec should note:
  "SEASON omitted: seasonal AT_HOME lift <2 pp on Weekdays, full-dist
  JS <0.001 across all season pairs — below the signal threshold for a
  conditioning dimension."

---

## Consistency check

After this decision, the Step 4 schema should show:

| Element | State |
|---------|-------|
| `SEASON` in conditioning vector | **No** |
| `SURVMNTH` in conditioning vector | **No** |
| `DDAY_STRATA` (3-category) as temporal condition | Yes |
| 2005/2010 and 2015/2022 treated symmetrically on temporal conditioning | Yes |
| Annual forecast output stratified by season | **No** — stratified by DDAY_STRATA only |
| BEM schedules: seasonal variants | Not generated (single annual profile per DDAY_STRATA) |

If SEASON is required downstream (e.g., a reviewer insists), the least-cost
path is to re-run Step 4 with SEASON appended as a soft condition only for
2015/2022, masked for 2005/2010. Given the signal levels above, this is
unlikely to change any BEM result meaningfully.

---

## Progress Log

**2026-04-09 — Review of Sonnet's Task 2 execution**

Numbers are conclusive — SEASON has no useful signal.
- Weekday AT_HOME spread of 0.78 pp is essentially noise. For comparison,
  the COVID 2015→2022 jump was ~6 pp — an order of magnitude larger.
  SEASON is not in the same league.
- Max JS divergence of 0.001004 across all 14 activities is two orders of
  magnitude below where conditioning normally pays for itself. This is not
  a "small but real" effect; it is a "below the floor" non-effect.
- The most season-sensitive activity (Passive Leisure, 1.16 pp) still does
  not break 1.2 pp. There is no hidden activity where SEASON matters that
  the AT_HOME aggregate is masking.

Recommendation (drop SEASON entirely) is the right call.
- Weekend spread of 2.34 pp is the only number that even gets close to the
  threshold, but the JS=0.001 number kills any argument that the model
  could actually learn it. Two metrics agreeing rules out a single-metric
  artifact.
- Confirming that no SURVMNTH proxy exists for 2005/2010 closes Option (c)
  cleanly — imputation was the only escape hatch and it is not available.
- The unblock is bigger than just removing one column: it means **Step 4's
  conditioning vector is identical for all 4 cycles**, no masking required,
  no half-trained dimension. That simplifies both training and the methods
  section.

Knock-on effect:
- W3 was the only weakness asking the model to handle a half-observed
  *conditioning* variable. With SEASON dropped, `colleagues` (Task 1,
  half-observed *output*) becomes the only remaining "half" in the design.
  That is a much cleaner story for the paper — missing-data handling can
  be described in one paragraph instead of two.

**Status:** Task 2 closed cleanly. Follow-up implementation work tracked
as **Task 2a** in `00_SWOT_pipeline.md` — drop SEASON from
`03_mergingGSS.py`, regenerate `merged_episodes.csv` and `hetus_30min.csv`,
re-confirm Step 3 validation 81/82, update Step 4 / Step 6 / Step 7 docs.
Authorized 2026-04-09 by user.
