# TICKET — G4 "Work peak-slot delta" gate is defective: it pools day-type strata (Simpson's paradox)

**Status:** CLOSED (fixed 2026-07-18) · **Severity:** 🟡 MEDIUM (validator-only; no pipeline data is affected) · **Filed:** 2026-07-15
**Filed by:** manager, during the 2J→3J improvement cascade (`../improvement/2J_to_3J_improvement_implementation.md`)
**Explicitly OUT OF SCOPE of that plan** — filed separately so it isn't silently carried as a Task-1 regression.

---

## Aim

Fix the Step-4 validator's **G4 "Work peak-slot delta"** gate, which reports **FAIL after the 04T activity rake even though 04T sharply *improves* the thing G4 claims to measure.** As written, the gate is a composition artifact, not a fit measure — so it will keep failing (or passing) for the wrong reasons, and it currently misrepresents a good result as a bad one.

## The defect

`Step4_docs/3rdJ_04_augmentationGSS_2split_val.py:538-541`:

```python
d_work = abs(slot_rate(obs_arr, WORK_PEAK_SLOTS, RAW_WORK_CAT)
             - slot_rate(syn_arr, WORK_PEAK_SLOTS, RAW_WORK_CAT))
lvl = self._grade(d_work, self.thr["g4_slot_pp_pass"], self.thr["g4_slot_pp_warn"])
self._rec(lvl, "G4", f"Work peak-slot delta: {d_work:.2f} pp")
```

`obs_arr` / `syn_arr` are **pooled across all `DDAY_STRATA`** (weekday / Saturday / Sunday). Work rates differ enormously by day type, and the observed and synthetic pools do not share the same day-type composition. So `d_work` mixes two different quantities:

- the thing we want: **per-stratum fit** (does synthetic weekday work look like observed weekday work?)
- the thing that dominates: **composition weighting** (what fraction of each pool is weekday?)

This is a textbook **Simpson's paradox** setup: every stratum can improve while the pooled statistic worsens. That is exactly what happened.

**Note the inconsistency:** the sibling gate **G2 stratifies** by `DDAY_STRATA`. The night-sleep half of G4 (`:533-536`) has the same pooling issue but is less exposed, because sleep rates vary far less across day types than work rates do.

## Evidence (measured 2026-07-15, on the 04T rake)

Per-stratum fit **improves dramatically**, and the peak slot is **identical pre/post in every stratum** (argmax 14 / 15 / 20, matching observed):

| stratum | pre-04T delta | post-04T delta |
|---|---|---|
| weekday | 14.5 pp | **0.3 pp** |
| Saturday | 8.0 pp | **0.02 pp** |
| Sunday | 7.0 pp | **0.00 pp** |

Yet the **pooled** G4 delta worsens → gate flips to FAIL. Nothing about the synthetic diaries got worse; the pooled number simply stopped being a fit measure.

## Why this matters

1. **It misreports a success as a failure.** 04T's whole purpose is to make synthetic activity match observed activity per cell. G4 says it made it worse. Any reader of the Step-4 report — including a reviewer — would draw the opposite of the true conclusion.
2. **It is not a regression, and must not be recorded as one.** The FAIL is pre-existing behaviour of the gate, newly *triggered* by 04T changing the composition balance. The plan's Task-1 acceptance (scorecard 64P/3W/4F → 66P/3W/2F, post-FAIL a strict subset of pre-FAIL) already accounts for this.
3. **A pooled gate is untrustworthy in both directions.** It can also *pass* while per-stratum fit is bad, if composition happens to cancel the error out. So this isn't only about one inconvenient FAIL.

## Proposed fix

Stratify G4 the way G2 already does: compute the delta **per `DDAY_STRATA`**, grade each, and report either the worst stratum or one row per stratum. Do **not** simply reweight the pooled statistic — per-stratum reporting is more informative and matches the validator's existing idiom.

Optionally apply the same treatment to the night-sleep delta (`:533-536`) for consistency, even though it is less sensitive.

## Steps

1. Read `_gate_G2`'s stratification idiom in the same file and mirror it.
2. Split `:538-541` into a per-stratum loop over `DDAY_STRATA ∈ {1, 2, 3}`.
3. Grade per stratum against the existing `g4_slot_pp_pass` / `g4_slot_pp_warn` thresholds (do **not** retune thresholds as part of this fix — changing the gate's shape and its thresholds at once would make the result uninterpretable).
4. Decide the roll-up: worst-stratum grade, or three rows. Prefer three rows plus a worst-stratum summary.
5. Do the same for the sleep delta if it is cheap.
6. **Archive the predecessor** before editing (repo hard rule).

## Expected result

- G4 reports weekday 0.3 pp / Sat 0.02 pp / Sun 0.00 pp on the current actv2 pool → **PASS**, correctly reflecting the measured per-stratum fit.
- The Step-4 scorecard's remaining FAILs drop by one, on the merits rather than by tuning.

## Test method

- Re-run `3rdJ_04_augmentationGSS_2split_val.py` against **both** `R5_raked_mindwell/` (pre-04T) and `R5_raked_mindwell_actv2/` (post-04T).
- The fixed gate must show **pre-04T worse than post-04T in every stratum** — i.e. it must now rank the two pools in the direction the underlying data actually moved. That, not "does it pass", is the real acceptance criterion: a gate that passes the good pool but can't tell the two apart is still broken.
- Confirm no other gate's numbers move (this edit must touch only G4's computation).

## Notes

- **Do not** "fix" this by relaxing thresholds or by excluding strata. The bug is the pooling, not the bar.
- The peak *slot* itself (argmax) was never wrong — only the *rate delta* is affected. Any narrative that says the peak shifted is mistaken.
- Related: `../improvement/2J_to_3J_improvement_implementation.md` Task-1 Progress Log (the 04T decomposition and scorecard), and this ticket's sibling correction on the superseded 61.12% figure in `2J_to_3J_audit_reference.md`.

## Progress Log

*(append below)*

### 2026-07-15 — filed
Filed by the manager during the Task-4 cascade. Not actioned: the plan's §0.2 scope covers the act30 rake and the multi-zone injection fix only, and changing a validator gate mid-cascade would have made the campaign's before/after scorecards incomparable. Deferred deliberately, with the evidence recorded above so the next session doesn't have to re-derive it.

### 2026-07-18 — FIXED (employee)

**Predecessor archived first** (hard repo rule): `Step4_docs/3rdJ_04_augmentationGSS_2split_val.py.20260718_preG4fix`. Pre-fix reports also saved alongside each pool before re-run: `outputs_step4/sweep/R5_raked_mindwell_actv2/step4_validation_report.{txt,html}.20260718_preG4fix` and the `R5_raked_mindwell/` equivalents.

**Change:** in `validate_temporal` (Section 4 / G4), the pooled `d_sleep` / `d_work` block (`:533-541` pre-fix) was replaced with a loop over `DDAY_STRATA ∈ {1,2,3}`, mirroring `validate_at_home`'s (G2) per-stratum idiom. For each of the two metrics (night sleep-slot delta, work peak-slot delta) it now computes the delta on stratum-filtered `obs`/`syn` subsets, grades each of the 3 strata against the **unchanged** `g4_slot_pp_pass`/`g4_slot_pp_warn` thresholds, and records a 4th "worst stratum" roll-up row (max delta, graded the same way) — three rows + a worst-stratum summary per metric, per ticket step 4's preference. Applied the same treatment to the sleep delta too (ticket step 5), since it was cheap and the pre-04T pool turned out to need it (see below). The pooled `obs_arr`/`syn_arr` and the transition-rate gate above them were left untouched.

**Per-stratum results:**

| metric | stratum | pre-04T (`R5_raked_mindwell`) | post-04T (`R5_raked_mindwell_actv2`) |
|---|---|---|---|
| Work peak-slot delta | Weekday | 14.53 pp **FAIL** | 0.33 pp **PASS** |
| Work peak-slot delta | Saturday | 7.97 pp **FAIL** | 0.03 pp **PASS** |
| Work peak-slot delta | Sunday | 7.00 pp **FAIL** | 0.01 pp **PASS** |
| Work peak-slot delta | worst (Weekday both) | 14.53 pp **FAIL** | 0.33 pp **PASS** |
| Night sleep-slot delta | Weekday | 16.41 pp **FAIL** | 0.00 pp **PASS** |
| Night sleep-slot delta | Saturday | 5.19 pp **WARN** | 0.04 pp **PASS** |
| Night sleep-slot delta | Sunday | 4.62 pp **WARN** | 0.00 pp **PASS** |
| Night sleep-slot delta | worst (Weekday both) | 16.41 pp **FAIL** | 0.00 pp **PASS** |

Matches the ticket's evidence table closely (weekday/Sat/Sun 14.5/8.0/7.0 → 0.3/0.02/0.00 pp, argmax unchanged). **Direction test passed**: pre-04T ranks worse than post-04T in every one of the 6 strata (both metrics), not merely "fails while the other passes."

**Scorecards** (both re-run locally against the actual pools):
- post-04T (`R5_raked_mindwell_actv2`, the live pool): **66P/3W/2F → 73P/3W/1F**. FAIL count dropped by exactly one (the pooled work-peak FAIL is gone; the sole remaining FAIL is OW5, unrelated). Total row count rose from 71→77 because the fix intentionally reports 3 strata + 1 worst-stratum roll-up per metric (8 rows) instead of 1 pooled row per metric (2 rows) — the ticket's "expected 67P/3W/1F" assumed a single roll-up row; the actual design (ticket step 4's stated preference) adds diagnostic rows, so the total-count is higher than that rough guess even though the FAIL-count-drops-by-one criterion holds exactly.
- pre-04T (`R5_raked_mindwell`): 64P/3W/4F → 64P/5W/8F. This pool got *worse* under the fix, which is correct and expected — its pooled sleep/work deltas (6.25/6.38 pp) happened to land in a similar range to the true per-stratum badness by coincidence; stratifying reveals the real weekday delta is far worse (14.5-16.4 pp) and Sat/Sun are WARN/FAIL too. This is exactly the "untrustworthy in both directions" risk the ticket flagged (§ "Why this matters", point 3).
- **No other gate's line moved on either pool** — confirmed by diffing each new `step4_validation_report.txt` against its `.20260718_preG4fix` backup; the only lines that differ are the `G4` sleep/work lines and the summary counts they roll into.

**Files touched:** `Step4_docs/3rdJ_04_augmentationGSS_2split_val.py` (G4 block only); both sweep pools' `step4_validation_report.{html,txt}` regenerated in place (pre-fix copies preserved as `.20260718_preG4fix`).

**Status: CLOSED.**
