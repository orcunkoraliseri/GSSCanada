# 3J Leg-3 — manager handoff, 2026-08-06 (option C executed; board 49/49)

**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v2_optionC.md`.** That prompt was the instruction
set for three tasks. All three are closed. **The V2 board is 49 done / 0 ready / 0 decisions of 49.**

🔴 **And one claim in it was wrong — corrected below before anything else, because it is the kind of
error that propagates into the next person's plan.**

---

## 0. Read first, in this order

1. **`improvements/v2/V2-E7E6E8_PREREGISTRATION.md`** (83 lines) — the predictions, written
   **before** the validator was opened. 🔴 **Read it before §0.34, not after.** Scoring read after
   the fact is not scoring; 9 of 12 held and you should be able to see which 3 did not without
   taking my word for it.
2. **`improvements/v2/3rdJ_L3_v2_implementation.md`** — the plan, **5,751 lines**. Status panel near
   line 175, then **§0.34** at the end (this work) and **§0.33** (the decision it implements).
3. **`Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.md`** — 🔴 **the validator's own
   document.** Its 2026-07-21 CLOSURE entry is what the reverted change on 08-05 violated. The new
   Progress Log entry at the end (2026-08-06) records R5 in full. **Read this file before touching
   any Step-5 gate, ever.**
4. **`outputs_step5/3rdJ_step5_validation_report.html`** — the regenerated report. Scorecard
   **31 / 6 / 3**, with R5 and the R1-XCH informational line visible in it.
5. The board: <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>

**The two tests are now IN the repo, beside the validator** — they were written in a temp
directory and a test that lives in a temp directory is a test nobody will run again:

- **`Step5_docs/falsify_r5.py`** — corrupts synthetic retail rows in memory (nothing on disk) and
  reads R5 back. **4/4**, control included. Re-run it; it takes about a minute.
- **`Step5_docs/probe_defects.py`** — takes an optional path argument. Point it at the shipped
  validator and it reports **0 of 2 defects**; point it at
  `archive/3rdJ_05_censusLinkage_4split_val.2026-08-06_pre_R5.py` and it reports **2 of 2**. **Both
  directions were run.** A probe that only ever reports "clean" has not been shown to detect
  anything.

🔴 **`probe_defects.py` was rewritten before being committed, and the reason is worth reading.** Its
first version decided one of the two checks by regex-matching the ternary in the source. The fix
replaced that ternary with a dict, so the scraper silently stopped matching and printed `?` — while a
hardcoded summary line underneath still announced the old verdict. **It reported a result it had not
measured.** Both checks now read captured output.

Still scratchpad-only: `e78/base_gates.txt` vs `e78/e8_gates.txt`, the additions-only run diff.

---

## 0b. Machine state, because this prompt keeps saying "run it locally"

⚠️ **As of 2026-08-06 01:54 this machine is carrying an unrelated load: 16 `energyplus.exe`
processes, ~35 GB resident, from a `ubem_e02_five_mode/nyc_centre` job on EnergyPlus **23-1-0** (this
project uses 24.2.0).** Not ours, not touched, and it did not interfere with the Step-5 runs — but
"just run it here" is advice about a machine, and the machine is not idle. **Check before starting
anything memory-hungry.**

---

## 1. The correction

The superseded prompt (and plan §0.33, the board, and memory) said **V2-E7 is a hard prerequisite for
V2-E6** — that option C keeps the old R1-POOL statistic as an INFO line, so the INFO channel had to
exist first.

**False.** It is a leftover from the *reverted* design. In §0.27 R1 was **re-specified** onto the
sibling basis, so the displaced pool statistic had to be demoted to INFO. **Option C demotes
nothing:** R1 keeps the pool basis *as a gate*, R5 is added on the sibling basis *as a gate*. Two
gates, no INFO needed. **E6 never depended on E7.**

E7 was still worth doing, and it did earn its keep — but for a different reason (R1-XCH, §4 below).
The dependency claim is **struck in all four artefacts, not deleted**. Found by reading the code, not
by re-reading my own prose, which is the uncomfortable part.

---

## 2. What is now true

**Step-5 scorecard: 31 PASS / 6 WARN / 3 FAIL (+1 INFO, not scored).** Was 31/5/3.
**A WARN was gained. No FAIL was cleared.** That was the pre-registered falsifiable test of whether
option C was genuinely additive, and it is met.

- **R1 is byte-identical**: 4.796 pp, FAIL, same basis, July disposition intact.
- **R5 is new**: AT_RETAIL generation fidelity, synthetic vs observed within day type,
  **1.615 pp ⇒ WARN** (WD 1.567 / WE 1.615).
- **R1-XCH is new and is not a gate**: an INFO line, excluded from the scorecard and the pass rate.
- All **49** pre-existing gate lines are byte-identical; the run diff has additions only.

**Validator md5 `46b0eb222f88f802e149647c82c1b726` → `f71a97142e9f420f73a6f874bc11d496`.**
Pre-change copy: `Step5_docs/archive/3rdJ_05_censusLinkage_4split_val.2026-08-06_pre_R5.py`.
Shipped report regenerated; the 2026-07-21 original kept as
`outputs_step5/3rdJ_step5_validation_report.2026-07-21_pre_R5.html` (md5 `b261d5d5`).

---

## 3. R5, and the band choice you should know about

| | synthetic | observed | max slot deviation | slots > 3 pp |
|---|---|---|---|---|
| weekday | 6,052 | 15,506 | **1.567 pp** | 0 |
| weekend | 7,448 | 1,267 | **1.615 pp** | 0 |

🔴 **Disclosed, not buried:** R5 uses **R1's** banding (PASS ≤ 1 / WARN 1–3 / FAIL > 3). Its siblings
W1 and 2.2 gate on the **count of slots over 3 pp** — and under *that* rule **R5 would read PASS**.
The stricter band was chosen deliberately: retail's channel peak is 4.57 %, so 1.615 pp is roughly a
third of the whole signal and headroom is **0.9×** the observed value. **The looser rule was
available and was not taken.** It is written into the gate's own text.

**Seen failing, 4/4** — control 1.615 WARN · +2 pp → 2.200 WARN · **+5 pp → 4.933 FAIL** · +20 pp →
19.032 FAIL. The control row is the load-bearing one.

---

## 4. R1-XCH — the paper change, and what E7 was actually for

The manuscript's R1 caveat is now **computed on every run** instead of asserted:

> R1's own basis applied to the **PASSING** channels: `hom30` **22.969 pp**, `wrk30` **27.263 pp** —
> against AT_RETAIL's **4.796 pp**.

The worst channel by R1's own measure is one whose gate passes, so R1's FAIL is not evidence of a
retail-specific defect. **A caveat the tool prints beats a caveat the author asserts** — if it stops
being true, the report says so instead of the manuscript quietly staying wrong.

⚖️ **The honest other half, retained:** normalised by its own peak, retail's R1 deviation is
**105 %** — the *worst* of the three. R1-XCH disqualifies the **basis**; it does not exonerate
retail. Both halves belong in the write-up.

**Action still open for the paper:** replace the current re-weighting argument with this one. The
numbers are now printed by the validator, so the manuscript should cite the report rather than
restate them.

---

## 5. Predictions, scored — 9 PASS / 2 FAIL / 1 ill-posed

Full table in plan §0.34. The two that went against me:

- **P4 FAIL** — I estimated the INFO fix at ≤ 15 lines; it took **41**. Teaching a fourth outcome
  means five status expressions, two CSS rules and a render block, not one dictionary.
- **P10 ill-posed, which is worse than wrong** — I predicted "49 → 50" while conflating console gate
  *lines* with summary-table *rows*. Recorded **N/A**, not matched retroactively to whichever count
  happened to land on 50.

---

## 6. Constraints that held throughout

| | |
|---|---|
| **Speed** | Never contacted. No `ssh`, `scp`, `sbatch`, `squeue`. |
| **Simulation** | Zero cells. Step 9 not re-scored — R5 is a Step-5 gate and nothing downstream reads it. |
| **Frozen deliverable** | Not reopened. `V2-G1_FROZEN_DELIVERABLE.md` references Step 5 nowhere. |
| **Scale-relative bar** | Still declined. It would retroactively re-judge W1 and 2.2. |

---

## 7. Still owed by the user — none of it mine

1. **The `val_score` selection rule (V2-E4).** The doc mandates *argmax retail F1, never a single
   composite*; the code selects on a composite containing neither `pr_auc` nor `f1`. Fix the doc or
   fix the code — the latter means re-running selection.
2. **X-3 — should it FAIL rather than WARN?**
3. **The hotel gate's `all_cells`-vs-`median` rule (§0.31).** 🔴 The scorer discloses that under
   `median`, `S9-EUI-hotel` would **pass**. **Do not resolve it by picking the rule that passes.**

🔴 **An empty board is not proof the work is finished, and that lesson is 24 hours old.** On
2026-08-05 the panel read *"nothing left for a local session"* and lasted **forty minutes** — one
question about a failing gate produced a task, a reverted change, four findings and eventually the
decision in §0.33. None of the three items above will surface by itself.

---

## 8. Closure ritual — the user's standing instruction

The moment a task closes, **all three artefacts are updated in the same response, unprompted**: the
**Progress Log** with its successor promoted, this **directeur prompt**, and the **board HTML
republished at its fixed URL**. Plus memory. A task reported done without all three is not done.
