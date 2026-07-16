# TICKET — G4 "Work peak-slot delta" gate is defective: it pools day-type strata (Simpson's paradox)

**Status:** OPEN · **Severity:** 🟡 MEDIUM (validator-only; no pipeline data is affected) · **Filed:** 2026-07-15
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
