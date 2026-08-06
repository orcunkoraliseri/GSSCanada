# V2-E7 / V2-E6 / V2-E8 — pre-registration

**Written 2026-08-06, BEFORE any line of the validator was touched.** Predictions first, so that a
result which disagrees with me is visible as a disagreement rather than quietly absorbed. Every
number below is either a target to reproduce or a claim that can be shown false.

**Scope:** implement option C — R1 untouched, a **new gate R5** added beside it. No simulation, no
cluster, Step 9 not re-scored.

---

## 🔴 A correction I owe before I start, and it changes the *justification* for V2-E7

In the plan (§0.33), the new directeur prompt, the board and memory I wrote that **V2-E7 is a hard
prerequisite for V2-E6** — that option C keeps the old R1-POOL statistic as an INFO line, and INFO is
what the validator cannot express.

**That is wrong, and I noticed it while reading the code rather than while writing the documents.**
It is a leftover from the *reverted* design. In §0.27's implementation R1 was **re-specified** onto
the sibling basis, so the old pool statistic had to be demoted to a non-scoring INFO line. **Option C
demotes nothing.** R1 keeps the pool basis *as a gate*; R5 is added on the sibling basis *as a gate*.
Two gates, no INFO required. **V2-E6 does not depend on V2-E7 at all.**

**V2-E7 is still worth doing, for two reasons that survive:**

1. **The two defects are real and were observed, not theorised.** They will bite the next person who
   adds any non-scoring row, and they are three lines to fix.
2. **It gives V2-E8's paper argument a better home.** §0.27 finding 1 — R1's own basis gives `hom30`
   **22.969 pp** and `wrk30` **27.263 pp** while both those gates PASS — is currently a claim in
   prose. Emitted by the validator as an INFO line it becomes a number the reader can watch being
   computed. **A caveat the tool prints is worth more than a caveat the author asserts.**

So the order **E7 → E6 → E8** stands, but for ordering convenience, **not** because E6 is blocked.
Corrected in all four artefacts; the original claim is struck, not deleted.

---

## V2-E7 — predictions

| | prediction | how it is decided |
|---|---|---|
| **P1** | `_rec("info", …)` on the **current** file raises `KeyError: 'info'` | run it before fixing; a probe that does not raise falsifies me |
| **P2** | a summary row with `Status="INFO"` on the **current** file renders with CSS class **`fail-row`** and prints **`[FAIL]`** | inspect `generate_summary_table` output + the emitted HTML |
| **P3** | after the fix, **all existing gate lines are byte-identical** and the scorecard is still **31 PASS / 5 WARN / 3 FAIL** | full diff of the PASS/WARN/FAIL line sets against the pre-change run |
| **P4** | the fix is **≤ 15 changed lines** | `diff` line count |

## V2-E6 — predictions

| | prediction | how it is decided |
|---|---|---|
| **P5** | R5 weekday = **1.567 pp**, weekend = **1.615 pp**, gate value **1.615 pp** ⇒ **WARN** | must match `scratchpad/e6/val_final.log` to 3 dp |
| **P6** | the row counts behind it are **`syn=6052` / `obs=15506`** (WD) and **`syn=7448` / `obs=1267`** (WE) | printed by the new gate |
| **P7** | **R1 is completely unmoved: 4.796 pp, FAIL** | diff of R1's line |
| **P8** | **no existing gate changes status**; the scorecard goes **31P/5W/3F → 31P/6W/3F** | full line diff |
| **P9** | the falsifier works: perturbing synthetic retail rows drives R5 **over 3.0 pp** and it reports **FAIL** | deliberate corruption, run, observe |
| **P10** | summary-table gate count **49 → 50** | count rows |

🔴 **P8 is the whole decision.** If a FAIL clears, this was not the additive option and I stop rather
than reconcile it.

## V2-E8 — predictions

| | prediction | how it is decided |
|---|---|---|
| **P11** | the cross-channel INFO numbers reproduce §0.27 exactly: `hom30` **22.969 pp**, `wrk30` **27.263 pp** | computed by the new INFO line |
| **P12** | the shipped validator md5 moves off `46b0eb222f88f802e149647c82c1b726`, and **every** document citing that hash is updated in the same pass | `grep` for the old hash returns only struck/historical mentions |

---

## What would make me stop

- Any existing gate changing status (**P8**).
- R5 landing outside **1.5–1.7 pp** — that would mean I have not reproduced the same statistic, and
  the right response is to find the difference, **not** to publish the number I got.
- The falsifier failing to fail (**P9**). A gate nobody has seen fail is not evidence, and on
  2026-08-05 one of my own falsifiers passed when it should have failed.

## What I am explicitly NOT doing

- Not touching R1's basis, threshold or verdict.
- Not adopting the scale-relative bar — it would retroactively re-judge W1 and 2.2.
- Not re-running Step 8 or Step 9.
- Not resolving the hotel gate's rule question, which is the user's.
