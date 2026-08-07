# 3J Leg-3 — manager handoff, 2026-08-06 (v3 **CLOSED**, 6/6)

**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v3_open.md`** (kept intact as the predecessor).
That prompt ended with **three decisions owed by the user**. All three are now **taken**, against the
earlier legs, on the user's instruction to make them *compatible with 2J and Leg-2*.

🔴 **Nothing moved.** No band value, no threshold, no `rule` value, no checkpoint, no published
status, no scorecard line, no simulation cell. Speed was never contacted. The shipped pool is
byte-identical (md5 `ebb1dfe8`). **The two options that could have moved something — H1 option B and
H3 option B — are the two that were declined**, and the argument for the one I declined most firmly
is written up *against* my own recommendation, in §3.

---

## 0. Read first, in this order

1. **`improvements/v3/3rdJ_L3_v3_implementation.md`** — §2.1 / §2.2 / §2.3 are the three closures.
   §0's fourth correction is the cross-leg finding. Appendix A reproduces every number.
2. **`improvements/v3/h2_evidence/`** — six gate dumps from six real validator runs, plus the score.
3. The four documents this session was told to read, in case you want to re-derive the precedent:
   `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` (+ Overview) and
   `2J_docs_occ_nTemp/00_GSS_Occupancy_Pipeline.md` (+ Overview) — then the **Leg-2 scorers** those
   documents describe, which is where the finding actually is.
4. The board, republished at its existing URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> ·
   source in the repo at `improvements/v3/board_v3.html`.

---

## 1. The three decisions, with their reasons

| ID | decision | the reason on record | reopens if |
|---|---|---|---|
| **V3-H1** | **option C** — the documented rule is **kept** as the specification; the shipped deviation is recorded under it | 🔴 **Not cost.** Both rules rank epochs on **teacher-forced** columns V2-E1 and V3-J1 showed are blind to person-level retail skill, so the re-cascade buys +0.0218 of a statistic that does not measure the thing. Option A was ruled out by **precedent**: rewriting the rule would delete *"never a single composite score"* — a Leg-1 finding promoted to a Leg-2 design principle (`Leg2 pipeline:262`) | **T1** a person-level gate ranks the seeds differently · **T2** the F1 gap exceeds 1 sd (today **0.16 sd**) · **T3** Steps 5→9 reopen for any other reason |
| **V3-H2** | **option C** — X-3 stays **WARN**, documented as a decomposition of `ISR-final`; the gate that was actually meant is `RW9`, built 08-06 and **FAILing** | The impossibility claim was **attacked, not asserted**: 6 pools, 6 runs of the real validator, **no arm produced X-3 > 0 while `ISR-final` passed**. Sharper than the plan said — **X-3 grades PASS at 1 000 conflicts**; it cannot reach WARN below **61,499** slots. And Leg-2's `OW6` uses the **identical** 1.0/5.0 % thresholds and was never a zero-tolerance gate | a perturbation is found that makes X-3 fire while `ISR-final` passes — the falsifier is in the repo and takes one argument |
| **V3-H3** | **option A** — `all_cells` for office and hotel, `median` for retail, with the **criterion now written down** instead of left as three unexplained values | V2-B3's own condition, applied: `median` only where a channel's spread is small enough that re-run noise can flip the verdict. Range/band-width: **office 0.285 · retail 0.443 · hotel 0.959** — hotel's cells span 96 % of its band, so they differ genuinely. **Applying the principle changes zero statuses** | **T1** you accept the precedent argument in §3 · **T2** a channel's spread falls below its own re-run noise · **T3** the frozen deliverable reopens anyway |

---

## 2. 🔴 The finding this session was not looking for

**The office EUI band's rule citation is false — in the code and in the master doc, identically.**

The scorer called `all_cells` *"the original rule"*; the master doc said the band was *"inherited
from Leg-2 … Table 7.1"* with **`rule: all-cells`**. The **values** are inherited exactly
(`OFFICE_EUI_BAND = (135.0, 100.0, 200.0)`). **The rule and the severity are not.** Leg-2 scored
those same values on the **channel median** and graded a miss **WARN**, in both scorers that carry
it:

```
Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:462-470   G2o          median, WARN
Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py:1420-1431      4.3-office   median, WARN,
                                                                                     "non-blocking"
```

Leg-3 tightened both and recorded neither. **No gate in this project could have caught it** — and
the closest one prints its own epitaph every run:

> `3rdJ_09_bench_doc_sync_check.py`: *"REMINDER: agreement is not correctness. This gate cannot fail
> on a band that is wrong in both places."*

**The rule was wrong in both places.** That line was written as a caveat and turned out to be a
description. **New vacuous-reading class #17: the consistency check whose two inputs share an
ancestor.** Only cross-leg reading finds it.

**The citation is corrected in both files. The rule is not changed by the correction.**

---

## 3. The argument against my own H3 recommendation — read this before accepting it

**"Restoring Leg-2's rule is not gate-shopping, it is correcting an unrecorded drift."** That is a
serious argument. It says: Leg-3 tightened a criterion silently; undoing a silent tightening is
housekeeping; the fact that it clears a gate is a consequence, not a motive.

**Two things defeat it, and neither is "because hotel would pass".**

1. **Leg-2's convention is a package — median AND WARN.** Median-with-FAIL is neither leg's rule.
   Adopting the package whole changes **three** statuses: office **FAIL → WARN**, retail **FAIL →
   WARN**, hotel **FAIL → PASS**. The whole EUI block goes from **3 FAILs to 1 PASS + 2 WARNs** on a
   documentation correction. **A basis change that turns FAIL into WARN is a band change in
   disguise** — the R1 decision of 2026-07-21, re-affirmed 2026-08-05, and it binds.
2. **The spread principle already on file points the other way.** Hotel is the channel *least*
   eligible for the rule that would clear it.

**If you disagree, T1 is yours to pull and nothing has been foreclosed** — no artefact was
regenerated and no status was republished.

---

## 4. What is in the repo that was not there this morning

| | |
|---|---|
| `Leg3_4-split/Step4_docs/falsify_x3_isr_relation.py` | 6 arms, 3 positive controls with the conflict census known in advance, **6/7 conditions, exit 1** |
| `improvements/v3/h2_evidence/` | the six gate dumps + `SCORE.txt` |
| `Step4_docs/3rdJ_04_augmentationGSS_4split.md` | the H1 deviation record + reopen trigger, **under** the unchanged rule |
| `Step4_docs/3rdJ_04D_train_4split.py` | docstring corrected (comment only; predecessor archived) |
| `Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` | provenance correction + the rule principle, in `BENCH` |
| `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` | the same two, for the reader |
| `improvements/v3/j3_ledger_check.py` | fixture rebuilt **synthetic**; live tree kept as its own arm; `PROMPT` repointed here |
| `improvements/v3/j3_falsify_run_2026-08-06_evening.txt` | the 8/8 transcript |

---

## 5. Stated openly, because none of it is finished

- **RW9 is in the validator code and not in the shipped Step-4 report.** Regenerating it locally
  would stamp a cluster artefact `win32`. Unchanged since 08-06 morning.
- **`3rdJ_04D_train_4split.py` now differs from Speed's copy** by a comment block. Comments only; it
  cannot change a result. Sync when convenient.
- **The condition left failing in H2's falsifier is mine, not the validator's** — I predicted a blind
  spot for out-of-range values and there isn't one; `RET-PRESENCE` catches it and quarantines the
  chain. The prediction was **not** rewritten to match.
- 🔴 **Closing the three decisions BROKE `j3_ledger_check.py --falsify`, and that is §2.4.** Its
  perturbation arms were built by deleting things out of the **live** artefacts, so it died with a
  `StopIteration` the moment nothing was owed — *the falsifier stopped working exactly when the
  ledger went empty.* Repaired the same hour: the fixture is now a **synthetic** three-artefact
  ledger, the live tree is checked as its own arm, and `PROMPT` points at *this* file rather than the
  superseded one. **8/8 arms, 2 controls + 6 perturbations, exit 0.** The summary line was also
  hard-coded and printed *"1 control + 7"*; it is counted now.
- 🔴 **With zero owed items the live check is vacuous.** Four conditions satisfied by an empty set.
  **It passes today for the right reason and cannot fail here any more** — its evidence is the 8-arm
  falsifier, not its green run. One owed item makes it live again.
- **Same cause, two severities, not fixed:** the retail quarantine grades `RW1` **FAIL** and `RETM` /
  `RW9` **WARN**. Fixing it is a scorecard change.

---

## 5b. 🔴 "v3 closed" is NOT "Leg-3 closed" — the board implied it was

**Caught by the user reading the published board, not by any check** (plan §2.5). The board's title
names the leg; its counters count the **improvement rounds**. Leg-3's own scorecards were never on
it. **Verified from the artefact this session:** `Step9_docs/outputs_step9/step9_gates.json` =
**17 PASS / 0 WARN / 3 FAIL / 10 INFO**, the three FAILs being `S9-EUI-{office,retail,hotel}` — every
channel **below** its floor, never above.

**Leg-3's actual state:** Steps 1–7 closed · Step 8 probes 32P/0W/0F · **Step 9 3 FAIL, blocking** ·
v2 49/49 · v3 6/6. Open beyond that, all user decisions: `LAUNDRY` per-object resize (a global K is
the wrong instrument); the Leg-2 `calculate_eui()` `ReportName` defect inflating its **published**
office EUI ~1.706× (fixing it reopens a paper-ready leg); the backward-audit finding that reaches the
**submitted** 2J paper; plus the retail quarantine severity mismatch and RW9's absence from the
shipped Step-4 report.

**The ledger check could not have caught this** — it verifies owed items are visible everywhere, and
there were none (§2.4's vacuity). Scope band added to the board, additively; no counter moved.

🔴 **Note for the H3 decision, which is the next thing on the desk:** the trigger in §3 would move
**office → WARN, retail → WARN, hotel → PASS**. That is precisely the blocking set above, cleared by
a documentation correction rather than by the diagnosis. Hotel's own **bimodality** (Tall 195–212 vs
SuperTall 149–165, **no cell in [170,182)**) is a genuine argument that *neither* rule is right there
— the median describes no building in the set, and `all_cells` scores two populations as one.

---

## 6. Closure ritual — unchanged

The moment a task closes, **all three artefacts are updated in the same response, unprompted**:
the **Progress Log** in the v3 plan, **this prompt**, and the **board republished at its fixed URL**.
Plus memory. **v3's added clause held**: every WP-H task closed with its **recorded reason** and,
beyond what the clause required, a **written reopen trigger**.
