# D-S4-11 — AUDIT RESULT: `G4.1` is scored against TWO DIFFERENT REAL SETS

Date: 2026-08-24 · Status: **AUDIT DONE, AUTHOR RULED (i) on 2026-08-24**
Ruling executed: `D-S4-11` option **(a)** — read-only source audit, no compute, report and stop.
Companion: `2026-08-24_D-S4-11_D-S4-12_D-S4-13_G4.1_G4.4_G4.6_what_can_be_improved.md`

Nothing was executed on a GPU. No file was modified. `tools/4thJ_step4_thresholds.py`
(md5 `724b558f2fb46357c8bba2838adb5451`) and `prereg.md` are untouched.

---

## 1. The finding, in one sentence

There are **two** implementations of `G4.1`, they use the **same threshold constants** and the
**same stratum definition**, and they differ in exactly one thing: **which real set they compare
the generated diaries against** — the trainer uses the **real reference set (54,114 diaries)**,
`genperturb`/`g47_coverage` use the **held-in validation split (5,520 diaries)**. The small set
reaches `N >= 100` in **zero** strata, so **every `G4.1` verdict ever produced by the
perturbation side, on ALL THREE folds, is a vacuous V4.a FAIL that never evaluated a variance ratio at all.**

## 2. The two implementations

| | trainer | perturbation side |
|---|---|---|
| function | `tools/4thJ_step4_train.py:638` `gate_g4_1` | `tools/4thJ_step4_genperturb.py:65` `gate_g4_1` |
| who calls it | `train.py:884` (epoch end), `g41_midepoch_probe` (D-S4-5), `4thJ_step4_g41_seedfloor.py:181` (imports the trainer's, does **not** re-implement) | `genperturb.py:270`, `g47_coverage.py:200,215` (imports `GP.gate_g4_1`) |
| thresholds | `TH.G4_1_MIN_STRATUM_N`, `TH.V4_A_MIN_STRATA`, band `[0.80, 1.25]` | **identical constants, same frozen file** |
| stratum key | `stratum_of(text)` → 5 fields | `DIAG.stratum_key(DIAG.prefix_dict(text))` → **the same 5 fields** |
| generated-side stratum read from | the **emitted** text's own prefix | the **requested** `prompt_text` prefix |
| **real side** | **`real_ref` — 54,114 diaries** | **`heldin_val` — 5,520 diaries** |

The body of the two functions is otherwise a line-for-line match (verdict logic, `vr <= 0`
skip, V4.a branch, band comparison). The output dicts differ cosmetically only: the trainer
also emits `band`; the perturbation copy also emits `which_end`, `min_vr`, `max_vr`.

## 3. The measurement, from logs already on disk

From `4J_step4_leg5_1286209.out` (trainer, fold `es`):

```
stratified generation: 6 strata x 100 = 600 diaries;
eligible strata in the real reference set (54114 diaries): 166
held-in validation diaries: 5520 (real reference set: 54114)
```

From `4J_s4_regen_es_1286546.out` (perturbation side, **same fold, same generated set**):

```
real (held-in val): 5520   generated: 600
```

Recorded `G4.1` verdicts, all producers:

| producer | fold | verdict | `n_scorable_strata` | what it means |
|---|---|---|---|---|
| trainer, ep 0 / 1 / 2 | `es` | FAIL / FAIL / FAIL | **6 / 6 / 6** | real band FAILs (1 below+3 above, 3+1, 1+3) |
| trainer, ep 0 / 1 / 2 | `it` | FAIL / FAIL / **PASS** | **6 / 6 / 6** | real; ep-2 PASS is a real PASS |
| `g47_coverage` baseline + perturbed | `es` | FAIL / FAIL | **0 / 0** | **vacuous** |
| `genperturb` × 5 levers (`null`, `modal_day`, `duplicate_500`, `blank_evening`, `within_stratum_shuffle`) | `es` | FAIL ×5 | **0 ×5** | **vacuous** |
| `genperturb` × the same 5 levers | `uk` | FAIL ×5 | **0 ×5** | **vacuous** |
| `genperturb` × the same 5 levers | `it` | FAIL ×5 | **0 ×5** | **vacuous** |

**SEVENTEEN of the recorded FAILs are `n_scorable_strata = 0`** — 5 levers × 3 folds in `genperturb_{es,uk,it}.json`, plus baseline and perturbed in `g47_coverage_es.json`. This is NOT one fold: it is every fold, every lever. Not one of them compared a
variance. `600 / 6 strata = 100` generated per stratum clears the floor exactly; the 5,520-diary
real side does not clear it in a single stratum, and V4.a then FAILs the gate by construction.

## 4. What this does to the perturbation battery

The five `genperturb` levers pre-declare (`genperturb.py:57-61`):

- `modal_day` and `duplicate_500` → `must_fail: [G4.1]`
- `null` and `within_stratum_shuffle` → `must_stay_clean: [G4.1]`

Both halves are unreadable on this evidence. `must_fail` was **satisfied by V4.a**, not by the
perturbation — the gate was already down before the lever was pulled. `must_stay_clean` was
**violated at baseline**, so it could not be assessed either. `g47_coverage.py:247` already
prints this honestly for its own case (`"G4.1 is %s at baseline on this fold, so
must_stay_clean is NOT assessable"`) — the audit shows the same sentence applies to four more
levers that do not print it.

This is a **`FINDING 56` case**: the verdict was produced by the harness, not by the thing under
test. It is not a case the "gates must be seen failing" rule catches, because the gate *did*
fall — for the wrong reason, every single time.

## 5. What is **not** wrong

- The frozen thresholds are correct and were obeyed by both implementations.
- The stratum definition is identical in both — this was the obvious suspect and it is clean.
- The trainer's `G4.1` numbers (6 strata, the band FAILs on `es`, the ep-2 PASS on `it`) are
  **unaffected**. Nothing in this audit moves a trainer-side verdict.
- `4thJ_step4_g41_seedfloor.py` imports the trainer's function, so it is on the good side.

## 6. The choice this leaves you — the three outcomes named in the decision doc

The audit did **not** find one implementation to be a bug and the other correct. It found that
the two answer different questions, and the step doc names only one gate. Ranked:

**(i) — recommended. The trainer is canonical; the seventeen perturbation-side FAILs are re-labelled
`NOT COMPUTED`.** Justification: `real_ref` is the set `stratified_k` generation was built
against (`FINDING 8`/`FINDING 11` exist precisely to make V4.a reachable), the floor is cleared
there by construction, and `G4.1`'s band verdicts on all three folds already come from it. Cost:
zero compute; the perturbation battery loses `G4.1` as a covered gate and must say so — the four
levers that name `G4.1` become **undemonstrated**, which is a declared limitation, not a repair.

**(ii) The perturbation side is canonical** → `G4.1` has never been evaluable on this corpus and
ships **BLOCKED**, not FAIL, on every fold. This discards the trainer's 6-stratum readings
including `it`'s epoch-2 PASS. I do not recommend it: it throws away the only real measurements.

**(iii) Both are legitimate** → `G4.1` is under-specified (the step doc never says which real set)
and that is itself a finding for the paper. Compatible with (i): adopt (i) as the operational
rule *and* record (iii) as the reason the rule had to be chosen rather than read off.

A fix that would make the perturbation side non-vacuous — pointing it at `real_ref` — is
available and costs no GPU time, but it changes the basis of a scored gate after folds have been
scored. **I have not done it and do not recommend doing it without your explicit ruling.**

---

### AUTHOR'S ANSWER — D-S4-11 outcome

<!-- write your ruling here: (i), (ii), (iii), (i)+(iii), or something else -->

### AUTHOR'S ANSWER — do we re-point the perturbation side at `real_ref`?

**NO.** The perturbation side is NOT re-pointed at `real_ref`. It would change the basis of a
scored gate after all three folds were scored. It stays as it is and is read as `NOT COMPUTED`.

---

## 7. Side note, not part of this decision

- `1286548` (`it`) **COMPLETED** 2026-08-24 06:41. Its `G4.1` reads FAIL / FAIL / **PASS** across
  the three epochs on 6 strata — the epoch-2 PASS is the first clean `G4.1` on any fold.
- `1286547` (`uk`) is **still RUNNING** (9 h 25 elapsed at the time of this audit), output
  directory still empty.
