# 3J Leg-3 — manager handoff, 2026-08-06 (v2 closed; **v3 opened**)

**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v2_R5_closed.md`.** That prompt closed the v2 board
at 49/49 and ended with **three items owed by the user**, carried as a bullet list.

**A bullet list is not a task.** It has no aim, no test method and nothing that fails if it is
ignored — which is how §0.23's deliverable item 2 (*"add a person-level retail gate"*) left the
ledger between 08-05 and 08-06 with nobody deciding to drop it. **v3 converts the list into tasks.**

🔴 **Nothing was executed. No threshold moved, no band touched, Speed never contacted, zero
simulation cells.** What changed is that all three decisions now have evidence behind them — and
**all three descriptions on the v2 board turned out to be incomplete, one of them wrong.**

---

## 0. Read first, in this order

1. **`improvements/v3/3rdJ_L3_v3_implementation.md`** — the v3 plan. §0 carries the three
   corrections; **appendix A gives a reproduction command for every number in it.** Run one of them
   before trusting the rest.
2. **`improvements/v3/e4_seed_logs/`** — the five seeds' joint training logs, **rescued today**.
   They existed **only** in a session scratchpad and are the entire evidence base for the
   `val_score` decision.
3. `improvements/v2/3rdJ_L3_v2_implementation.md` §0.23 / §0.24 / §0.31 — the source entries for
   the three decisions, if you want the long form.
4. The board, republished at its existing URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> ·
   **source now kept in the repo** at `improvements/v3/board_v3.html`, for the same reason as the
   logs above.

**Machine state, unchanged from last night's note:** 16 unrelated `energyplus.exe` processes
(~35 GB, `ubem_e02_five_mode`, EnergyPlus 23-1-0). Not ours, not touched. **V3-J1 reads a 418 MB
pool — check memory before starting it.**

---

## 1. The three corrections, shortest form

| | v2 board said | what the artefacts say |
|---|---|---|
| **`val_score`** | *"the second means a re-run"* | The re-run is **not five retrainings**. The documented rule's winner is **seed 0, epoch 15 = the final epoch**, and `3rdJ_04D_train_4split.py:876` saves the final epoch every run — those weights exist. 🔴 **But the documented rule was never implementable as written**: two of its five hard gates (midday error, transitions) are pool-level, so evaluating its own first clause needed **75 inference+rake cascades**. And **both** rules select on the teacher-forced columns V2-E1 showed are blind to person-level retail skill. |
| **X-3** | *"whether one **office** check should fail rather than warn"* | 🔴 **Not an office check** — it is Step-4 pairwise exclusivity over `hom30`/`wrk30`/`ret30`. And `X-3 > 0` **iff** `ISR-final > 0`, which is a hard FAIL above `1e-9`. **X-3 cannot fire while ISR-final passes.** FAIL-vs-WARN changes no detection outcome; it double-counts one event. |
| **hotel rule** | *"under the shop rule the hotel check would pass"* | True. Also true and not said: **retail FAILs under both rules** (median **75.63** against an 80 floor) and so does office. **A uniform `median` rule changes exactly one status in the whole scorecard — the hotel FAIL.** And V2-B3's own stated rationale (*"an all-cells rule on a spread smaller than its own uncertainty reports noise"*) measures **hotel at 96 % of its band** against office 28 % / retail 44 % ⇒ **the principle on file argues for keeping `all_cells` on hotel**, and doing so **changes nothing**. |

**None of these clears a FAIL. None moves a band.** Two of the three cut *against* the convenient
answer, which is the only reason to trust the third.

---

## 1b. 🔴 V3-J1 CLOSED the same day — and the finding is larger than the task

**6P / 4F / 1 N-A.** Plan **§1.1**; pre-registration `improvements/v3/V3-J1_PREREGISTRATION.md`,
written before a single agreement statistic existed. Local win32, ~4 min, **pool md5 `ebb1dfe8…`
identical before and after every arm.**

**The gate (RW9)** asks whether a generated retail day belongs to the *person* it was generated for,
against a **within-cell shuffle null**. **Falsifier 8/8**, and the row that makes the rest readable
is the **positive control**: set the synthetic vector to the person's own observed vector and the
gate reads **+2.3778** (z 375). It can see person-level structure.

**On the shipped pool it reads +0.0179 — FAIL against a pre-registered 0.10 bar**, i.e. **0.75 % of
what a perfect copy scores**.

🔴 **Then the two pre-registered diagnostics changed what the finding is.**

| channel | null = cell | null = cell × AGEGRP × SEX × LFTAG |
|---|---|---|
| `ret30` | **+0.0179** FAIL | **−0.0002** |
| `wrk30` | **+0.5540** PASS (z 79.6) | **+0.0122** |

Work looked strongly person-specific — until the null also matched labour-force status. **So this is
not a retail defect. The generator reproduces STRATA, not individuals.** V2-E1 showed the *gates*
were blind to a person shuffle; this shows the *model* has little for them to see.

⚖️ **The counterargument, and it was written down before the diagnostics ran:** each respondent has
**one** observed diary day, so the true cross-day-type persistence is **unmeasurable from this
data**. The gate scores retention against **zero**, not against truth. If retail behaviour really is
near-independent across day types for an individual, ≈ 0 is correct and the 0.10 bar is wrong.
**The bar was not moved**; the limitation is published beside the verdict.

**Two defects caught in my own work before either shipped:** my first wiring scored the coverage
line as **PASS**, putting a non-gate into the pass count — the exact thing V2-E7 forbade, committed
by me an hour after quoting it; and the **Step-4 validator carries the same latent INFO defect V2-E7
fixed in Step 5** (`_rec("info", …)` → `KeyError` at `:458`), recorded and deliberately **not**
fixed, because fixing it is a scorecard change.

**Not done, and stated rather than skipped:** the shipped Step-4 report was **not regenerated** — it
is a cluster artefact and a local rerun would stamp it `win32`. **RW9 is in the code and not yet in
the shipped report.**

**What it does to V3-H2:** the decision is unchanged in form, but its option C (*leave X-3 a WARN,
document it as a decomposition of ISR-final, and build the gate that was meant*) now has its second
half already built — and that gate FAILs. **You can take H2 with the number in hand.**

---

## 1c. 🔴 V3-J2 and V3-J3 also closed — and J2 corrected a v2 finding

**V3-J2 (plan §1.2), 5 of 6 conditions, P12–P19 7P/1F.** Rebuilt the V2-E1 falsifier that no longer
existed anywhere, as `Step4_docs/falsify_rw_battery_blindness.py`: six pools, six runs of the **real**
validator, text-level rewrites so no number is reformatted.

- **E1 reproduced exactly:** under a within-cell retail shuffle the **RW/RETM battery is
  byte-identical**, all 40 lines.
- 🔴 **E1 also CORRECTED.** E1 read `ISR-final` and `X-3` firing under that shuffle as those gates
  *catching* the scrambled person. **They were catching simultaneity** — permuting retail alone puts
  a stranger's shopping episode into a slot where the person was AT_HOME (`ISR-final`
  **0.000000 % → 1.421611 %**). *A perturbation that changes more than one thing cannot attribute
  what it breaks* — E1's own lesson, applied to E1's own arms.
- 🔴 **Arm F, pre-registered, is an inventory of the whole validator.** Move the **entire day** — all
  thirteen channel blocks — to another person in the same cell, and **exactly 4 of 150 validator
  lines change**: `OW5`, `OW5-REG`, and RW9's two. **The Step-4 validator contains exactly two
  checks that can see the person at all**, and one of them is one day old.
- **One condition left FAILING and not relaxed** (exit 1): I required RW9's number to drop ≥ 3×
  under the A→B shuffle; it dropped 2.2×. The criterion assumed the control had signal to lose, and
  V3-J1 had already shown it does not.

**Rescued into the repo:** the 5-seed training logs, the **board's own HTML** (it was being
published from a scratchpad), the R5 additions-only run diff, `e6/val_final.log` (which §0.33 names
as the reference for checking a re-implementation), and the 26 `MIN_POOL` sweep logs. The 24 GB of
E5 run output was deliberately **not** kept — V2-G1 already decided regenerable output is not
archived.

**V3-J3 (plan §1.3), 7/7 arms.** `improvements/v3/j3_ledger_check.py` fails when the plan, this
prompt and the board disagree about what is owed. Control passes; six perturbations detected;
**all four conditions seen firing** — the sixth arm exists only because after five, condition C4 had
never once been the one that fired, and a condition that has never fired has not been shown to work.
🔴 **A claim in J3's own task spec was wrong**: its F3 fixture is *not* the literal 08-05 tree (that
tree is v2-era and this parser reads the v3 vocabulary) but the 08-05 **defect pattern** reproduced
on today's files. Corrected in §1.3 rather than quietly satisfied.

**Run it before trusting this prompt:** `python improvements/v3/j3_ledger_check.py` — it passes on
the current tree.

---

## 2. The v3 board — 6 tasks

| ID | | |
|---|---|---|
| **V3-H1** | 🟣 your call | `val_score`: fix the doc, fix the code, or fix the doc **with a written trigger** that reopens it if V3-J1 ranks the seeds differently |
| **V3-H2** | 🟣 your call | X-3: leave WARN and document the relation, raise to FAIL, or leave WARN **and build the gate that was meant** (V3-J1) |
| **V3-H3** | 🟣 your call | The rule, all three channels at once. **Decidable today** — the evidence is complete |
| **V3-J1** | ✅ **CLOSED 08-06** | RW9 built and wired. Falsifier **8/8** incl. the positive control. 🔴 **It produced the new FAIL it was warned about — see §1b** |
| **V3-J2** | ✅ **CLOSED 08-06** | Five artefact sets rescued; the lost falsifier rebuilt. 🔴 **It corrects V2-E1** — see §1c |
| **V3-J3** | ✅ **CLOSED 08-06** | Ledger check, **7/7 arms**, all four conditions seen firing. One claim in its own spec was wrong and is corrected in plan §1.3 |

**Order.** All three J tasks are closed. **Every remaining item is a decision, and all three are yours.** H3 is decidable today on evidence already in the plan; H1 and H2 now have the numbers they were missing.

---

## 3. Standing constraints — unchanged, restated because they are load-bearing

| | |
|---|---|
| **Speed** | 🔴 Not contacted. No `ssh` / `scp` / `sbatch` / `squeue`. Cluster-only artefacts are stated as limitations, not worked around. |
| **Simulation** | Zero cells in v3. |
| **Frozen deliverable** | Not reopened. Only **V3-H3 option B** would touch the headline scorecard, and that is a re-publication decision, called out as one. |
| **Bands** | 🔴 **No band value moves in v3.** A rule change is not a band change — and the difference is the whole subject of H3. |
| **Gate-shopping** | 🔴 The 2026-07-21 R1 decision and §0.27's reversion bind. Choosing a rule after seeing which one clears a gate is gate-shopping whatever the write-up calls it. |

---

## 4. Closure ritual — the user's standing instruction

The moment a task closes, **all three artefacts are updated in the same response, unprompted**: the
**Progress Log** in the v3 plan with its successor promoted, **this prompt**, and the **board
republished at its fixed URL**. Plus memory. A task reported done without all three is not done.

**v3 adds one clause:** every WP-H task closes with its **recorded reason**, not just its choice.
A decision without a reason is a decision that gets re-litigated in four weeks — which is what
happened to R1 between 2026-07-21 and 2026-08-05.
