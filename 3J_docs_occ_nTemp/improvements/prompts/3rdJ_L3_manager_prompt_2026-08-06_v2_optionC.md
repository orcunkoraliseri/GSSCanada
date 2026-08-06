# 3J Leg-3 — manager handoff, 2026-08-06 (option C adopted)

> 🔴 **SUPERSEDED 2026-08-06 by `3rdJ_L3_manager_prompt_2026-08-06_v2_R5_closed.md`.**
> All three tasks below are **closed**: R5 added at **1.615 pp WARN**, R1 byte-identical at 4.796 pp
> FAIL, scorecard **31P/5W/3F → 31P/6W/3F**. Board **49 done / 0 ready / 0 decisions of 49**.
>
> 🔴 **And one instruction in this file is WRONG.** It says V2-E7 is a *prerequisite* for
> V2-E6 — that option C keeps the old R1-POOL statistic as an INFO line. **It does not.** That is
> a leftover from the **reverted** design, where R1 was *re-specified* and the displaced statistic had
> to be demoted. **Option C demotes nothing:** R1 keeps the pool basis as a gate, R5 is added on the
> sibling basis as a gate. **E6 never depended on E7.** E7 was still worth doing — it is what
> lets the paper's caveat be *computed* rather than asserted (see R1-XCH) — but not as a blocker.
> Struck here rather than deleted: the numbers and the guards in this file are all still correct.


**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v2_close.md`.** That prompt was correct when written
and is stale in exactly one respect: it reports **one decision outstanding**. The user answered it on
2026-08-06 and chose **option C**. The board is now **46 done · 3 ready · 0 decisions · 49 total**.

---

## 0. Read first, in this order

1. **`improvements/v2/3rdJ_L3_v2_implementation.md`** — the plan, now **5,608 lines**. Read the
   status panel (near line 175), then **§0.33** at the very end — that is the decision record and it
   is short. Then **§0.27**, which is the attempt that was reverted and the source of every number
   you are about to reproduce.
2. **`Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.md`** — 🔴 **the validator's own
   document, including its CLOSURE entry.** Read it before touching the validator. Skipping it is
   the single most expensive mistake made this week.
3. The board: <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>

🔴 **`3rdJ_L3_employee_prompt_V2-E6_R1_respec.md` is DEAD. Do not execute it.** It implements the
change that was reverted. It has been banner-marked, but if you are skimming filenames, that is the
one to skip.

---

## 1. What was decided, in one paragraph

**R1 is not touched.** It keeps its **FAIL at 4.796 pp**, its basis, and its 2026-07-21 disposition.
A **new gate R5** is *added* beside it: retail generation fidelity, synthetic vs observed within day
type. **The scorecard gains a WARN. It does not lose a FAIL.** If at the end of this work Step 5
reports anything other than **three FAILs including R1**, something has gone wrong and you should
stop rather than reconcile it.

**Why additive rather than a re-specification:** replacing R1's basis so its FAIL becomes a WARN was
implemented, verified and **reverted** on 2026-08-05 — it had already been refused in July as
gate-shopping (§0.27). Adding a second gate on the sibling basis does the opposite: it puts a number
on the wall for the one channel that had no such check, and leaves the uncomfortable one standing.

**Declined, deliberately:** the scale-relative bar (the shared absolute 3.0 pp bar is 3 % of
`hom30`'s signal and 66 % of retail's). True, but rebasing it would retroactively re-evaluate **W1
and 2.2**, which currently pass on the absolute bar. **A change that moves existing verdicts is a
band change however it is motivated.** Separate decision, not part of this work.

---

## 2. The three tasks, in strict order

### V2-E7 — first, and it is a prerequisite, not a companion

Option C keeps the old R1-POOL statistic as an **INFO** line, and INFO is precisely what the
validator cannot currently express. Two defects, both **observed** on §0.27's first run, not
inferred:

- `self.results` holds only `pass` / `fail` / `warn`, so `_rec("info", …)` raises **`KeyError`** at
  `3rdJ_05_censusLinkage_4split_val.py:220`.
- The summary-table renderer at **`:1271`** falls through to `[FAIL]` for any status it does not
  recognise, so an INFO row prints **as a failure**.

**Test method:** add an INFO row; assert it neither raises nor renders as `[FAIL]`; assert the 49
existing gate lines are **byte-identical** to the shipped baseline.

### V2-E6 — implement R5

🔴 **Re-implement from the specification. Do not go looking for the reverted code.** The archive at
`Step5_docs/archive/3rdJ_05_censusLinkage_4split_val.2026-08-05_pre_r1respec.py` is the **pre-edit
baseline** — its md5 is `46b0eb222f88f802e149647c82c1b726`, byte-identical to the shipped file. The
re-specified code was overwritten by the revert and no diff was kept. (§0.27's housekeeping said
otherwise; that line is struck and corrected.)

**What survives is the attempt's output, and it is enough to check yourself against** —
`scratchpad/e6/val_final.log`:

| | synthetic | observed | max slot deviation |
|---|---|---|---|
| **weekday** | `syn=6052` | `obs=15506` | **1.567 pp** |
| **weekend** | `syn=7448` | `obs=1267` | **1.615 pp** |

Gate reads **1.615 pp**, `FAIL > 3` / `WARN 1–3` ⇒ **WARN**. Channel peak 4.57 %, so state in the
gate's own text that the 3.0 pp bar is 66 % of the signal and the headroom is 1.385 pp = **0.9×** the
observed value.

🔴 **A falsifier is required before this counts as closed.** The gate must be *seen* failing —
perturb the synthetic retail rows until R5 crosses 3.0 pp and confirm it says FAIL. The standing rule
in this project is that a gate nobody has watched fail is not evidence.

**Guard, non-negotiable:** every other gate line must be **byte-identical** after your change. §0.27
achieved zero diff across all 49; anything less means R5 is not additive.

### V2-E8 — cascade

- Step-5 scorecard **31P/5W/3F → 31P/6W/3F**. **A WARN is gained; no FAIL is cleared.**
- The shipped validator md5 moves off `46b0eb22`. Every document citing it moves with it.
- The **paper caveat** switches to §0.27 finding 1: R1's own basis gives `hom30` **22.969 pp** and
  `wrk30` **27.263 pp** while both those gates PASS. That is simpler and stronger than the
  re-weighting argument currently in the text.
- READER_GUIDE gate list and the Step-5 step doc updated in the same pass.

---

## 3. Constraints that apply to all three

| | |
|---|---|
| **Speed** | 🔴 **Not available. No `ssh`, no `scp`, no `sbatch`, no `squeue` — not even a cheap `ls`.** None of this needs it: three tasks, one Python file, and the documents around it. |
| **Simulation** | **None.** Zero cells. Step 9 is not re-scored — R5 is a Step-5 gate and nothing downstream reads it. |
| **The frozen deliverable** | **Not reopened.** `V2-G1_FROZEN_DELIVERABLE.md` contains no reference to Step 5, the validator, or its md5 — checked by `grep`, not assumed. |
| **Backups** | Verify non-empty **in the same command**: `cp X "$BK" && [ -s "$BK" ] && …`. A failed `cp` in a `;`-chain once silently truncated 7,646 lines of log. |
| **Line counts** | `wc -l`. **Never PowerShell `Measure-Object -Line`** — it counts blank lines as zero. |

---

## 4. Traps, ranked by what they would cost

1. **Treating R5 as a replacement.** If R1's line changes at all, stop. The whole justification for
   this work is that R1 is untouched.
2. **Hunting for the reverted patch.** It does not exist. See §2.
3. **Adopting the scale-relative bar because it is "obviously right."** It is defensible and it was
   declined. It moves W1 and 2.2.
4. **Closing V2-E6 without a falsifier.** A WARN that has never been seen become a FAIL is not
   evidence of anything.
5. **Reconciling a surprise.** If Step 5 ends with two FAILs, that is not success — it means
   something cleared a FAIL that was not supposed to move.
6. **Editing the checker to match the document.** `scratchpad/verify_plan_optionC.py` parses the
   panel, the table and the bar chart and compares them to each other; it has two falsifiers and both
   hold. If it fails, the document is wrong.

---

## 5. Still owed by the user — not tasks, and not mine to take

1. **The `val_score` selection rule (V2-E4).** The doc mandates *argmax retail F1, never a single
   composite*; the code selects on a composite containing neither `pr_auc` nor `f1`. **Fix the doc or
   fix the code** — the latter means re-running selection.
2. **X-3 — should it FAIL rather than WARN?**
3. **The hotel gate's `all_cells`-vs-`median` rule (§0.31).** 🔴 The scorer itself discloses that
   under `median`, `S9-EUI-hotel` would **pass**. **Do not resolve this by picking the rule that
   passes.** If it changes, it changes for retail too, or on a stated principle.

---

## 6. Closure ritual — the user's standing instruction

The moment a task closes, **all three artefacts are updated in the same response, unprompted**:

1. the **Progress Log** in the plan, with the successor promoted into the ready queue;
2. this **directeur prompt**;
3. the **board HTML, republished at its fixed URL** — not rebuilt at a new one.

Plus the memory files. A task reported as done without all three is not done.
