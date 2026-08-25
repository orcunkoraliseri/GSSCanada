# 2026-08-26 — "PERTURBATION BATTERY COVERAGE" IS CLOSED AS A DECLARED LIMITATION, NOT REPAIRED

The Step 4 checklist carried this item as IN PROGRESS with the note:

> "Four of fifteen perturbations still owed, and the four `genperturb` levers naming `G4.1` stay
> UNDEMONSTRATED per `D-S4-11` (i) — seventeen recorded `G4.1` FAILs had `n_scorable_strata = 0`
> and are NOT COMPUTED, never FAIL. The coverage clause also FAILs on `es` and `uk`: `G4.7` passes
> at baseline and no lever fells it — a defect of the probe."

It is now closed, and it is closed **as a limitation**. 🔴 Closing is not passing. Step 4's own
standing instruction — *"Closing is not passing: never write Step 4 up as clean"* — applies here
with full force.

⚪ No threshold moved. No checker edited. No lever added. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` unchanged.

---

## Why "still owed" cannot be discharged by running anything

The four levers are `null`, `modal_day`, `duplicate_500` and `within_stratum_shuffle` — the
`genperturb` levers that name `G4.1`. They are not un-run. They **ran**, and every verdict they
produced is vacuous.

Re-derived today from the artefacts themselves rather than quoted from the log:

| artefact | `G4.1` verdicts | of which `n_scorable_strata = 0` |
|---|---|---|
| `4J_step4/genperturb/genperturb_es.json` | 5 | **5** |
| `4J_step4/genperturb/genperturb_it.json` | 5 | **5** |
| `4J_step4/genperturb/genperturb_uk.json` | 5 | **5** |
| `4J_step4/genperturb_f29/genperturb_es.json` | 5 | **5** |
| **total** | **20** | **20** |

Every `G4.1` verdict this project has ever recorded on the perturbation side was computed over
**zero scorable strata**. `D-S4-11` established why: the trainer scores `G4.1` against `real_ref`
(54,114 diaries, which reaches N ≥ 100 per stratum), while `genperturb` scores it against
`heldin_val` (5,520 diaries, which never reaches N ≥ 100 anywhere). Same threshold, same stratum
key, different denominator.

**The author ruled option (i) on 2026-08-24:** the trainer is canonical; the perturbation-side
verdicts are re-labelled `NOT COMPUTED`, never FAIL; and *"the four levers that name `G4.1` become
undemonstrated, which is a declared limitation, not a repair."*

**The one change that would make them non-vacuous was separately and explicitly declined**, in the
author's own words: *"NO. The perturbation side is NOT re-pointed at `real_ref`. It would change
the basis of a scored gate after all three folds were scored."*

So re-running the battery reproduces exactly the twenty vacuous verdicts above. There is no
compute, no GPU and no environment standing between this item and completion — there is a ruling.
🔴 **The item is closed because running it again is the one thing that could not change it.**

---

## The `G4.7` half, measured, and a correction to the note

The checklist note says the coverage clause "also FAILs on `es` and `uk`". Read off the artefacts:

| fold | `coverage_clause` | `G4.7` under `null` / `modal_day` / `duplicate_500` / `within_stratum_shuffle` / `blank_evening` |
|---|---|---|
| es | **FAIL** | PASS / PASS / PASS / PASS / PASS |
| uk | **FAIL** | PASS / PASS / PASS / PASS / PASS |
| it | **FAIL** | PASS / PASS / PASS / PASS / PASS |

🔴 **The coverage clause FAILs on all three folds, not two,** and `G4.7` survives every one of the
five levers in every fold. The note understated it. Corrected here.

This is a **defect of the probe, not of the gate**: `G4.7` passes at baseline and the battery
contains nothing that fells it, so `G4.7` sits in the "never made to fall" list the coverage
clause exists to catch. The clause is doing its job by failing.

🔴 **No new lever was written to fell it, and that is deliberate.** Adding a perturbation now,
after all three folds are scored, is the same act the author declined for `G4.1` — changing what a
scored gate is measured against once its verdicts are on the record. Doing it for `G4.7` while it
was refused for `G4.1` would be inconsistent in the direction that flatters the result. `G4.7` is
therefore recorded as **PASSING AT BASELINE AND NEVER DEMONSTRATED FALLING**, in the same class of
declared limitation as the four `G4.1` levers.

---

## What the write-up must say

* Four of fifteen perturbations are **undemonstrated**, by ruling `D-S4-11` (i), and their `G4.1`
  readings are **NOT COMPUTED** — never FAIL, never PASS. All twenty recorded perturbation-side
  `G4.1` verdicts are vacuous, re-verified 2026-08-26.
* The generation-side **coverage clause FAILs on all three folds**, because `G4.7` has no lever
  that fells it.
* The canonical `G4.1` reading is the **trainer's**, taken against `real_ref`, and it is the only
  one that may be quoted.
* Step 4 remains closed with four failing gates — `G4.1`, `G4.3`, `G4.6`, `G4.12` — each explained
  and empirically grounded. **Never written up as clean.**
