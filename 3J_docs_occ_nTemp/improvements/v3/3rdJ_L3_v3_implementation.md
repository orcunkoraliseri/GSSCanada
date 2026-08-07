# 3J Leg-3 — v3 Implementation Plan: the three open decisions, and what makes them decidable

**Opened 2026-08-06, after the v2 board closed at 49 / 49.**
**Predecessor:** `improvements/v2/3rdJ_L3_v2_implementation.md` (5,751 lines, all 49 tasks closed).
**Predecessor handoff:** `improvements/prompts/3rdJ_L3_manager_prompt_2026-08-06_v2_R5_closed.md`.
**Board (shared with v2, same URL):** <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>

---

## 0. Why this plan exists

The v2 plan closed with **three items owed by the user and nothing owed by me**. That is the exact
state the v2 panel warned about twice: *"an empty board is not proof the work is finished"* — on
2026-08-05 an empty board lasted forty minutes.

The three items were carried on the v2 board as a bullet list under a heading. **A bullet list is
not a task.** It has no aim, no test method, no artefact, and nothing that fails if it is ignored —
which is how §0.23's deliverable item 2 (*"add a person-level retail gate"*) fell off the ledger
between 08-05 and 08-06 without anyone deciding to drop it. **This plan converts the list into
tasks.**

**Scope discipline, stated up front.** The user asked for a plan covering *the last open options*.
Three of the six tasks below (**WP-H**) are exactly those. The other three (**WP-J**) exist because
each of the three decisions is currently **not decidable on the evidence on file** — they supply
the missing evidence and nothing more. WP-J is derived scope; it is labelled as such and can be cut
without touching WP-H's structure.

### 🔴 What I did before writing this plan, and what it changed

I read the code and the artefacts behind all three decisions rather than restating the v2 summary of
them. **All three descriptions on the v2 board were incomplete, and one was wrong.** Every claim
below is reproducible with a command given in the appendix.

| # | Decision as carried on the v2 board | What the artefacts actually say |
|---|---|---|
| 1 | `val_score` — *"the second means a re-run"* | **The re-run is not five retrainings.** The documented rule's global winner is **seed 0, epoch 15** — the *final* epoch, whose weights survive in `last_checkpoint.pt`. The cost is one inference + rake cascade and a full Step 5→9 re-cascade. **But the documented rule was never implementable as written** (below), and both rules select on **teacher-forced** numbers that V2-E1 showed are blind to person-level retail skill. |
| 2 | X-3 — *"whether one **office** check should fail rather than warn"* | 🔴 **X-3 is not an office check.** It is the Step-4 pairwise-exclusivity check over `hom30`/`wrk30`/`ret30`. And it is **arithmetically incapable of firing alone**: `X-3 > 0` if and only if `ISR-final > 0`, and `ISR-final` is a hard FAIL at anything above `1e-9`. Raising X-3 to FAIL changes **no detection outcome whatsoever**. |
| 3 | hotel rule — *"under the shop rule the hotel check would pass"* | True, and the trap is real. What the board does not say: **retail FAILs under BOTH rules** (median 75.63 against an 80 floor), and so does office. **A uniform `median` rule would change exactly one status in the whole scorecard: hotel FAIL → PASS.** Meanwhile the *stated rationale* for retail's median rule (V2-B3), applied honestly, **argues against** median for hotel. |

**None of these three findings clears a FAIL, and none of them is a licence to move a band.**

> 🔴 **A FOURTH correction arrived later the same day, from outside this leg** — the user asked that
> the decisions be taken *"en regardant les projets avant pour être compatible avec eux"*, so 2J's
> and Leg-2's pipeline documents were read, and then the Leg-2 scorers those documents describe.
> **The office EUI band's rule citation is false in code and doc alike**: the band VALUES are
> inherited from Leg-2, the **rule and severity are not** — Leg-2 scored the median and graded a miss
> **WARN** (`Leg2_2-split/Step9_docs/…_2split.py:462-470`, `Leg2_2-split/Step8_docs/…_2split_val.py:1420-1431`).
> **No gate here could have caught it**, and the closest one says so on every run: *"agreement is not
> correctness. This gate cannot fail on a band that is wrong in both places."* **Vacuous-reading
> class #17 — the consistency check whose two inputs share an ancestor.** Details in §2.3; the
> citation is corrected, the rule is not changed.

---

## 1. Status panel

*Opened **2026-08-06**. Updated **2026-08-06 (later)** — the three decisions were taken against the
earlier legs, on the user's instruction to make them **compatible with 2J and Leg-2**.
**6 done · 0 in progress · 0 ready · 0 decision of 6.***

```
DONE        6 / 6   ← V3-J1 (§1.1) · V3-J2 (§1.2) · V3-J3 (§1.3)
                      V3-H1 (§2.1, option C) · V3-H2 (§2.2, option C) · V3-H3 (§2.3, option A)
IN PROGRESS 0
READY       0
DECISION    0   ← all three taken, each with its reason AND a written reopen trigger
BLOCKED     0
```

> 🔴 **The three decisions were taken by recommendation, not by delegation — and every one of them
> is revocable.** Each carries a **reopen trigger** in the artefact it changed, because a decision
> without a trigger is one that gets re-litigated in four weeks (R1, 2026-07-21 → 2026-08-05).
> **Nothing here moved a band, a threshold, a rule value, a checkpoint or a published status.**
> The two that could have — H1 option B and H3 option B — are the two that were declined.

> 🔴 **Reading the earlier legs changed two of the three answers.** `val_score`: option A would have
> deleted a **Leg-1 lesson promoted to a Leg-2 design principle** (*"Pareto model selection, never
> composite"*, `Leg2 pipeline:262`), so the rule stays and the deviation is recorded under it.
> X-3: Leg-2's `OW6` grades pairwise exclusivity **by rate, thresholds 1.0/5.0 %** — identical to
> Leg-3's — and never as a zero-tolerance gate, so WARN is the Leg-2-compatible answer.
> 🔴 **And the office EUI rule's provenance turned out to be FALSE in both code and doc**: Leg-2
> scored the same band on the **median** and graded a miss **WARN**. See §2.3.

> 🔴 **V3-J1 produced a new FAIL, as its own plan said it might.** The generated retail day is
> **1.79 %** more like the person it was generated for than like a same-cell stranger's — against a
> pre-registered 10 % bar and a positive control that reads **238 %**. **Under a null that also
> matches age, sex and labour-force status the lift is −0.02 %: nothing at all.** And the same
> statistic on `wrk30` collapses the same way (+55.4 % → +1.2 %), so **this is not a retail defect,
> it is the generator reproducing strata rather than individuals.** V3-H2 changes character
> because of it — see §1.1.

> **Nothing here is blocked, nothing needs the cluster, and nothing needs a simulation cell.**
> Every artefact each task reads is on this machine. Where a task *would* benefit from a cluster
> artefact, that is written into the task as a stated limitation, not worked around.

**Standing constraints, inherited and unchanged:**

| | |
|---|---|
| **Speed** | 🔴 **Not contacted.** No `ssh` / `scp` / `sbatch` / `squeue`. If a task needs a cluster artefact, do the local part and say what could not be done. |
| **Simulation** | Zero cells. Nothing in v3 re-runs EnergyPlus. |
| **Frozen deliverable** | `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` is **not** reopened. V3-H3 can change a *reported status*; if it ever would, that is a re-publication decision, called out in the task. |
| **Bands** | 🔴 **No band value moves in v3.** Not one. A rule change is not a band change, and the difference is the whole subject of V3-H3. |
| **Gate-shopping** | 🔴 The 2026-07-21 R1 decision and §0.27's reversion are binding precedent: **a rule or basis chosen after seeing which choice clears a gate is gate-shopping**, whatever it is called in the write-up. |
| **Machine** | ⚠️ As of 2026-08-06 this box was carrying 16 unrelated `energyplus.exe` processes (~35 GB, a `ubem_e02_five_mode` job on EnergyPlus 23-1-0). Check before starting anything memory-hungry — V3-J1 reads a 418 MB pool. |

---

## 2. Summary table

**Legend: ✅ done · 🔄 in progress · ⬜ ready · 🟣 user decision · ⛔ blocked**

| ✔ | ID | Task | Cost | Depends on | Status |
|---|---|---|---|---|---|
| ✅ | **V3-H1** | The `val_score` selection rule: fix the doc or fix the code | decision | V3-J2, V3-J1 | **DECIDED 2026-08-06 · option C · §2.1** — the rule is **kept** as the specification and the shipped deviation is recorded under it, with a 3-condition reopen trigger. 🔴 Option A was ruled out by **Leg-2 precedent**, not by cost. 🔴 The code's own docstring was **lying** about where selection happens and is corrected |
| ✅ | **V3-H2** | X-3: FAIL or WARN | decision | ~~V3-J1~~ **done** | **DECIDED 2026-08-06 · option C · §2.2** — stays WARN, documented as a decomposition of `ISR-final`. **Impossibility claim attacked with 6 real validator runs and it held (6/7 conditions, 1 left failing, exit 1).** 🔴 Sharper than the plan said: X-3 grades **PASS at 1 000 conflicts** — it cannot reach WARN below 61,499 slots. Matches Leg-2 `OW6` thresholds exactly |
| ✅ | **V3-H3** | The `all_cells` vs `median` rule, all three channels | decision | none | **DECIDED 2026-08-06 · option A, made into a principle · §2.3** — rule values unchanged, criterion now written down, **0 statuses moved**. 🔴 **The office rule's provenance was FALSE in code and doc**: Leg-2 scored the median and graded WARN. The case for restoring it is written up **against** my own recommendation and the trigger is the user's to pull |
| ✅ | **V3-J1** | Build the person-level retail gate (§0.23 deliverable item 2, silently dropped) | local CPU, 418 MB pool, ~1 h | none | **CLOSED 2026-08-06 · 6P/4F/1 N-A · §1.1** — RW9 shipped, falsifier **8/8** incl. the positive control. 🔴 **New FAIL: lift +0.0179 vs a 0.10 bar; −0.0002 under the demographic null.** Not retail-specific — `wrk30` collapses the same way |
| ✅ | **V3-J2** | Rescue the v2 evidence that exists only in temp directories | 6 validator runs, ~8 min | none | **CLOSED 2026-08-06 · 5 of 6 conditions · 7P/1F on P12–P19 · §1.2** — five artefact sets rescued; falsifier rebuilt. 🔴 **It reproduces V2-E1 and CORRECTS it**: E1's `ISR-final`/`X-3` firing was an exclusivity confound, not person detection. **Arm F: only 4 of 150 validator lines move when every day is reassigned to another person** |
| ✅ | **V3-J3** | A decision-ledger check that fails when an owed item is missing from an artefact | ~230 lines + falsifier | none | **CLOSED 2026-08-06 · 7/7 arms · §1.3** — control passes, 6 perturbations detected across all four conditions. 🔴 One claim in this row's own task section was **wrong and is corrected** in §1.3 |

---

# WP-H — the three decisions

## V3-H1 — the `val_score` selection rule

> ✅ **DECIDED 2026-08-06 — option C. Closure in §2.1; spec kept as written below.**
> 🔴 **Option A's description below is the one the earlier legs ruled out**: *"rewrite `:157` to
> describe `val_score` selection"* would delete *"never a single composite score"* — a Leg-1 finding
> promoted to a Leg-2 design principle (`Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md:262`) —
> from the only place a Leg-3 reader looks. **The option table is left standing** rather than edited,
> because a plan rewritten to match its own outcome cannot be checked against it.

**The defect (V2-E4, §0.24, unchanged).** `3rdJ_04D_train_4split.py:881` saves `best_model.pt` on
`score < best_val_score` where (`:499`)

```
val_score = mean_js + 0.5 * (home_gap + work_gap + retail_gap) / 3.0
```

a composite containing **neither `pr_auc` nor `f1`**, while
`3rdJ_04_augmentationGSS_4split.md:157` mandates *"keep only checkpoints passing every hard gate,
then **maximize retail F1** among survivors … **Never a single composite score**"*. The two rules
pick different epochs in **4 of 5 seeds**, worth **+0.0218 retail F1** (5.6 % relative), and seed 3
ships because it is the **argmin of the forbidden composite** (1st of 5 on `val_score`, 4th of 5 on
the metric the doc names).

### 🔴 What v2 got wrong about the cost, and it points the decision the other way

**Claim A — the documented rule was never implementable as written.** Its first clause requires
*"passing every hard gate"*, and the gate set is *ΔJS ≤ 0.002 on Heads 1–2, ISR ≤ 0.5 %,
PR-AUC ≥ 0.15 ∧ F1 ≥ 0.25, **midday error ≤ 3.0 pp**, **transitions ≥ 0.05/day***. The training log
carries 21 columns and **two of those five gate families are not among them** — midday error and
transitions are **pool-level**, computable only after inference + rake + validator. There is no
per-epoch pool and never was. So evaluating the documented rule's own first clause would have cost
**75 inference-plus-rake cascades** (5 seeds × 15 epochs). *The docstring's promise of a "separate
checkpoint-selection step" was not merely unwritten — it was unaffordable.*

The clause is also **inert on this data**: over all 75 epochs the log-visible gates are never
threatened (min `pr_auc` **0.518213** against a 0.15 bar; min `f1` **0.282362** against 0.25; max
`isr_raw` **0.014245 %** against 0.5 %). Every epoch survives, so *survivors → argmax F1* reduces to
**global argmax F1**.

**Claim B — the documented rule's winner is recoverable without retraining.** Global argmax retail
F1 over all 75 epochs is **seed 0, epoch 15 = 0.41685**. Epoch 15 is the **final** epoch, and
`3rdJ_04D_train_4split.py:876` writes `last_checkpoint.pt` **every joint epoch** — so seed 0's
`last_checkpoint.pt` holds exactly those weights. **"Fix the code" therefore costs one inference +
rake cascade, not five retrainings** — followed by the full Step 5 → 9 re-cascade, which is the
expensive part and which reopens the frozen deliverable.

**Claim C — and this is the one that should decide it.** Both rules select on the **teacher-forced**
`pr_auc` / `f1` columns of the training log. **V2-E1 established that those numbers are blind to
person-level retail skill**: all 10 RW/RETM gates report identical statuses on a pool whose retail
vectors have been shuffled between people, and RW1/RW2 pass an all-zeros pool. So switching to the
documented rule buys **+0.0218 of a teacher-forced statistic that the audit showed does not measure
what the retail channel exists to model**, at the price of a full re-cascade — while the cross-seed
F1 margin is **0.16 sd**, i.e. no seed is distinguishable from any other.

> **What I am not doing.** I am not recommending "fix the doc" because it is cheaper. I am recording
> that **the metric the expensive option optimises has already been shown not to measure the thing**,
> and that this is a stronger argument than cost. If V3-J1's person-level gate is built and the
> ranking under *it* disagrees with the shipped seed, this decision changes character completely —
> which is why J1 is listed as a dependency.

### The decision

| option | what it means | cost | consequence |
|---|---|---|---|
| **A — fix the doc** | Rewrite `:157` to describe `val_score` selection, record the Leg-1 "never a composite" lesson as **violated, knowingly, with the reason**, and carry the F1 gap as a limitation | writing | Shipped pool unchanged; the paper gains an honest limitation |
| **B — fix the code** | Implement gate-first → argmax F1, re-select seed 0 ep 15 from `last_checkpoint.pt`, re-run 04E + rake + validator, then Steps 5→9 | cluster inference + full re-cascade + **reopening the frozen deliverable** | Buys +0.0218 teacher-forced F1 on a metric E1 showed is person-blind |
| **C — fix the doc now, revisit after J1** | A, plus a written trigger: *if the person-level gate ranks seeds differently, B is reopened* | writing | The only option that does not commit before the evidence exists |

**Aim.** Get one of A / B / C recorded, with its reason, in the plan, the Step-4 doc and the board.
**Test method.** Whichever is chosen, `grep` proves it landed: option A ⇒ `:157` no longer says
*"never a single composite score"* unqualified; option B ⇒ a script exists that reads more than one
seed directory (today `grep` for `seed_0` / `range(5)` / `for SEED` across `Step4_docs/*.py|*.sh`
returns **0 hits**).
**Expected result.** No band moves; no gate status changes under A or C.

---

## V3-H2 — X-3: FAIL or WARN

> ✅ **DECIDED 2026-08-06 — option C. Closure in §2.2; spec kept as written below.**
> 🔴 **One claim below is weaker than what the runs showed.** This section says X-3's *"WARN band
> lies entirely inside the region where a hard gate has already failed"*. True, and understated:
> **X-3 grades PASS at one conflict and still grades PASS at one thousand** — it cannot reach WARN
> below **61,499** conflicting slots. Corrected in §2.2, not here. The test method below was executed
> exactly as written: **6 arms, the real validator, and the impossibility claim held.**

**The question as inherited** (§0.23 deliverable item 3): *"Raise X-3 from WARN to FAIL for the
retail pair, or record why WARN is right. It is currently the only retail-touching person-level
discriminator and it cannot fail."*

### 🔴 The premise is false, and the arithmetic is three lines

`3rdJ_04_augmentationGSS_4split_val.py:1395-1423`:

```
n_any_gt1  = count of slots with (hom + wrk + ret) > 1        → ISR-final
n_hw, n_hr, n_wr = the three pairwise counts                  → X-3
```

`n_any_gt1 = 0` **if and only if** `n_hw = n_hr = n_wr = 0` — a slot with two channels active is a
pairwise conflict, and a pairwise conflict is a slot with two channels active. And
`_grade_isr_final` (`:491`) returns `fail` for any value above `1e-9`.

**Therefore: X-3 can be non-zero only when ISR-final is already FAILing.** Its WARN band (0, 5 %]
lies entirely inside the region where a hard gate has already failed. On the shipped pool both read
zero — `0/6,149,856` slots, X-3 `0.0000 %` on all three pairs.

This also explains the V2-E1 shuffle result without any appeal to X-3 being a discriminator:
under SHUFFLE-STRAT, `ISR-final` went **FAIL** and X-3 went **WARN** — *the same event, reported
twice, at two severities*.

**So the decision as posed — FAIL or WARN — has no detection consequence.** It is a choice about
how loudly a already-failing condition is echoed. **Neither answer makes X-3 catch anything
ISR-final misses.**

### The decision, re-posed

| option | what it means |
|---|---|
| **A — leave WARN, document why** | Record in the validator doc that X-3 is a *decomposition* of ISR-final, not an independent gate: it says *which pair* conflicted. WARN is right precisely because the FAIL is already carried by ISR-final; two FAILs for one event double-counts the scorecard |
| **B — raise to FAIL** | Costs nothing, catches nothing, and makes the Step-4 scorecard report one event as two failures |
| **C — leave WARN, and build the gate that was actually meant** | A, plus **V3-J1** — the person-level retail gate. §0.23's item 2 asked for exactly this and it was dropped. This is the only option that changes what the validator can detect |

**Recommendation: C.** A is the honest label; the detection gap is real and J1 is what closes it.
**Aim.** A recorded decision plus, under A or C, a docstring and report-text change stating the
X-3 / ISR-final relation.
**Test method.** 🔴 **Seen failing, both directions, before the write-up is believed**: perturb the
pool to introduce exactly *k* pairwise conflicts, re-run the real validator, and confirm
(i) ISR-final FAILs at k=1, (ii) X-3 is non-zero for exactly the perturbed pair, (iii) no
perturbation exists that makes X-3 non-zero while ISR-final passes. The third is the claim; a claim
about an impossibility must be attacked, not asserted.
**Expected result.** No threshold moves. On the shipped pool no status changes under any option.

---

## V3-H3 — the `all_cells` vs `median` rule

> ✅ **DECIDED 2026-08-06 — option A, written up as a principle rather than as inertia.
> Closure in §2.3; spec kept as written below.**
> 🔴 **This section's account of where `all_cells` came from is FALSE, and it is left standing so
> the correction has something to point at.** It treats `all_cells` as the inherited default. It is
> not: **Leg-2 scored the same office band on the CHANNEL MEDIAN and graded a miss WARN** — twice
> (`Leg2 Step9:462-470`, `Leg2 Step8:1420-1431`). Leg-3 inherited the **values** and tightened the
> **rule and the severity** without recording either. §2.3 carries the correction, the case *for*
> restoring Leg-2's rule written against my own recommendation, and why it is the user's trigger to
> pull: Leg-2's convention is *median **and** WARN*, and adopting it whole turns the EUI block from
> **3 FAILs into 1 PASS + 2 WARNs**.

**Where it stands.** `3rdJ_09_activityDrivenLoads_4split.py:116-156`: `rule` is a per-channel field
of `BENCH` — `all_cells` for office and hotel, `median` for retail (V2-B3). The gate publishes both
readings every run, and says so out loud when they disagree.

### The full picture, which the v2 board did not carry

Computed from the **shipped deliverable** `outputs_step9_deliverable/step9_eui_by_channel.csv`
(56 cells per channel, no simulation, appendix A3):

| channel | min | median | max | band | in band | **`all_cells`** | **`median`** | rules agree? |
|---|---|---|---|---|---|---|---|---|
| office | 61.72 | **71.02** | 90.21 | [100, 200] | 0/56 | **FAIL** | **FAIL** | ✔ agree |
| retail | 63.63 | **75.63** | 96.84 | [80, 155] | 12/56 | **FAIL** | **FAIL** | ✔ agree |
| hotel | 203.33 | **260.54** | 318.42 | [180, 300] | 28/56 | **FAIL** | **PASS** | 🔴 **disagree** |

🔴 **Retail FAILs under both rules.** The v2 board's framing — *"the hotel check requires every
building to fall in range; the shop check requires only the middle one to"* — is correct about the
rules and misleading about the stakes: **switching every channel to `median` would change exactly
one status in the entire scorecard, and it is the hotel FAIL.** A "uniform principled rule" whose
only effect is to clear the one gate under discussion is gate-shopping with better paperwork.

### 🔴 The principle is already on file, and it points the other way

V2-B3's recorded rationale for retail's median rule (`BENCH["retail"]["src"]`, verbatim):

> *"V2-E3 moved the median by −0.05 % and that alone flipped a cell, so **an all-cells rule on a
> spread smaller than its own uncertainty reports noise as a verdict**."*

That is a statement about **spread relative to the band**. Measured:

| channel | across-cell range | band width | **range / width** |
|---|---|---|---|
| office | 28.50 | 100.0 | **0.285** |
| retail | 33.22 | 75.0 | **0.443** |
| hotel | **115.09** | 120.0 | **0.959** |

**Hotel's cells span 96 % of its own band.** Under V2-B3's own rationale, hotel is the channel
*least* eligible for a median rule: its cells are not clustered inside their uncertainty, they
genuinely differ, and an all-cells rule on them reports signal rather than noise.

**A boundary placed anywhere between 0.443 and 0.959 yields: median for office, median for retail,
`all_cells` for hotel — and changes ZERO gate statuses** (office and retail FAIL under both rules
anyway). *A principled rule that changes no status is what a non-gate-shopped rule looks like.*

> ⚖️ **Disclosure, because it is load-bearing.** I computed these spreads **after** knowing which
> rule clears hotel. A threshold I now propose is **not blind**, and I am not proposing one. The
> deliverable is the *statistic and the principle*; the boundary is the user's to set, and the
> honest reason to trust this particular construction is not my judgement — it is that **the
> resulting rule changes nothing**, which is the one property gate-shopping cannot produce.

### The decision

| option | rule set | scorecard effect |
|---|---|---|
| **A — status quo** | office `all_cells`, retail `median`, hotel `all_cells` | none (current) |
| **B — uniform `median`** | all three | 🔴 **hotel FAIL → PASS**, and nothing else |
| **C — uniform `all_cells`** | all three | none (retail already FAILs under both) |
| **D — spread-based principle** | `median` where range/width < boundary, else `all_cells` | **none**, for any boundary in [0.443, 0.959) |

**Aim.** A rule *principle* written into `BENCH`'s `src` strings and the master doc, applied to all
three channels at once, with the statuses computed **after** the principle is fixed.
**Test method.** `3rdJ_09_bench_doc_sync_check.py` already enforces doc↔code agreement on the rule
field and is **seen failing 5/5** (F3 and F4 are the rule cases, bidirectional). Re-run it. Then
re-score Step 9 from the existing CSVs and diff all 30 gates — **expected: 0 status changes under
A, C and D; exactly 1 under B.**
**Expected result.** No band value moves under any option. Option B reopens the frozen deliverable's
headline scorecard and must be treated as a re-publication, not an edit.

---

# WP-J — what makes those decidable (derived scope)

## V3-J1 — the person-level retail gate

> ✅ **CLOSED 2026-08-06 — read §1.1 for what happened.** The spec below is kept as written so the
> outcome can be read against the intent rather than against a spec edited to match it.

**Why it exists.** §0.23's deliverable had four items. Item 1 (relabel RW1/RW2 as teacher-forced) is
**done** — the strings are in the validator at `:1150` and `:1156`. Item 4 was **withdrawn** (the
checkpoints exist). Item 3 is **V3-H2**. **Item 2 — "add a person-level retail gate" — was never
built and never appeared on the owed list.** It is the only one of the four that changes what the
validator can detect, and it is the thing X-3 was mistakenly credited with being.

**Aim.** A gate that FAILs on a pool whose retail vectors have been permuted **within**
(cycle × day-type × province) — the permutation under which all 10 RW/RETM gates, and every
marginal, are unchanged.

**Steps.**
1. Statistic: per respondent, agreement between their synthetic `ret30_001..048` vector and their
   own observed one (matched on the pool's respondent key), aggregated across the pool.
2. Null: the **within-cell shuffle** distribution of that same statistic, so the bar is *"above
   what random person-assignment achieves"*, not an invented constant.
3. Band: derived from the null (e.g. distance from the null mean in null sd), **written before the
   observed value is computed**, and recorded in the pre-registration file.
4. Wire it into `3rdJ_04_augmentationGSS_4split_val.py` beside the RW battery; publish both the
   observed statistic and the null.

**Test method.** 🔴 **Seen failing, 4 arms, and the control is load-bearing**: `baseline` (must
PASS), `shuffle-strat` (must FAIL), `zero` (must FAIL), and a **half-shuffle** (50 % of rows
permuted) to show the gate is graded rather than binary. The v2 falsifier that produced exactly
these arms **no longer exists** (V3-J2) and must be rewritten — it lives in the repo this time,
next to the validator, per the `falsify_r5.py` precedent.

**Expected result.** 🔴 **A new FAIL is a live possibility and is not a reason to weaken the gate.**
If the shipped pool cannot beat its own shuffle null, that is the finding V2-E1 pointed at, and it
is reported at whatever severity the pre-registered band gives.

**Cost.** Local CPU. Reads `outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv`
(418,622,540 B, **present on this machine**). Chunked read — check the machine's memory first.

**Constraint.** The observed retail vector must come from the **GSS side**, not from the pool's own
synthetic columns. If no per-respondent observed retail vector exists for every pool row, say so and
scope the gate to the rows where it does — **do not** substitute a marginal and call it person-level.
*That check is the first thing to run, before any gate design.*

---

## V3-J2 — rescue the evidence that lives in temp directories

> ✅ **CLOSED 2026-08-06 — read §1.2.** The rebuilt falsifier did more than restore E1: it **corrected**
> it. Spec kept as written.

**The defect.** The v2 closure moved `falsify_r5.py` and `probe_defects.py` into the repo on the
principle that *"a test that lives in a temp directory is a test nobody will run again"*. **The
principle was applied to two files and not to the rest.**

| artefact | status 2026-08-06 | consequence |
|---|---|---|
| 5-seed joint training logs (`log_joint_seed{0..4}.csv`, ISR + G3 JSONs) | **were** in a session scratchpad only | **the entire evidence base for V3-H1** |
| `_e1_perturb.py` / `_e1_score.py` / `_e1_summary.py` (the E1 falsifier) | 🔴 **gone — not in the repo, not in any surviving scratchpad** | the *only* demonstration that 10 RW/RETM gates are blind; **V3-J1's test method** |
| `e78/base_gates.txt`, `e78/e8_gates.txt` (the additions-only run diff) | scratchpad only | the audit trail for R5 being additive |
| **the board's own HTML** (`v2board.html`) | scratchpad only, across every republish since it was created | the board is a *published deliverable* whose source lived nowhere |

**Done 2026-08-06, in the same response as this plan:**

- the 15 seed-log files copied to `improvements/v3/e4_seed_logs/` (49 KB) — appendix A1/A2
  reproduce from that copy;
- **the board source itself** into `improvements/v3/board_v3.html`, with the patch that produced it
  (`board_patch_v3.py`). The board had been republished at its URL for days from a file that
  existed only in session scratchpads. *This task's own defect, found while writing the task.*

**Still owed.** The E1 falsifier must be **rewritten**, not recovered — and it is subsumed by
V3-J1's test method, so it lands there. The `e78` diff should be copied beside the Step-5 tests.

**Test method.** A one-line check that each artefact cited by a plan section resolves to a path
under the repo — folded into **V3-J3**.

---

## V3-J3 — the decision-ledger check

> ✅ **CLOSED 2026-08-06 — read §1.3.** 🔴 **One claim in the spec below is wrong** (the F3 fixture is
> not the literal 08-05 tree). It is left standing here and corrected in §1.3, because editing a spec
> to match what was built is how a prediction stops being one.

**The defect it catches has happened twice.** (1) The v2 *"waiting on the user"* line read
**"Nothing"** while three decisions were owed. (2) §0.23's deliverable item 2 left the ledger with
nobody deciding to drop it.

**Aim.** A script that FAILs when the plan, the manager prompt and the board disagree about what is
owed.

**Steps.** Parse the owed-items list from the plan's status panel; parse the manager prompt's
*"Still owed"* section; parse the board's decisions block. Require the **same set of IDs** in all
three. Require every ID to have a task section in the plan. **A missing section is a hard FAILURE,
never a skip** — a checker that skipped absent IDs would have passed on 08-05, and that is the
vacuous-gate pattern this project already catalogues 16 kinds of.

**Test method.** 🔴 **Seen failing on a fixture, ≥ 4 ways**, the real tree never mutated:
F0 control PASS · F1 remove an ID from the prompt · F2 remove it from the board ·
F3 **the 08-05 tree exactly as it stood** (plan lists three, prompt says "nothing") · F4 an ID
present everywhere but with no task section.
**F3 is the one that matters** — it is not synthetic, it is a state this repository was really in.

**Expected result.** PASS on today's tree, once WP-H's three IDs are in all three artefacts.

---

## 3. Order of work

```
V3-J2 (part done)  ──►  V3-H1 decidable
V3-J1              ──►  V3-H2 decidable (option C) ──►  V3-H1 revisit trigger (option C)
(nothing)          ──►  V3-H3 decidable now
V3-J3              ──►  keeps all three from being lost again
```

**V3-H3 can be decided today** — its evidence is complete and in the table above.
**V3-J1 is the long pole** and is the only task with a real chance of producing a new FAIL.

## 4. What must be true at closure

Per the user's standing three-artefact ritual, every closed task updates **in the same response**:
the Progress Log here (with its successor promoted), the manager prompt in `improvements/prompts/`,
and the board **republished at its existing URL** — plus memory. A task reported done without all
three is not done.

**And the v3-specific one:** every task in WP-H closes with a *recorded reason*, not just a choice.
A decision without its reason is a decision that gets re-litigated in four weeks.

---

## Appendix A — reproducing every number in this plan

All commands are local, read-only, and run from the repo root
(`3J_docs_occ_nTemp/`). Python used: `AppData/Local/Programs/Python/Python313/python.exe`.

**A1 — shipped vs documented epoch, per seed** (reproduces §0.24's table exactly):

```bash
cd improvements/v3/e4_seed_logs
for s in 0 1 2 3 4; do awk -F, -v S=$s 'NR>1{n++;
  if($18<bv||n==1){bv=$18;be=$1;bf=$17} if($17>mf||n==1){mf=$17;me=$1}}
  END{printf "seed %s | shipped ep=%s f1=%.5f | doc-rule ep=%s f1=%.5f | gap=%.5f\n",
  S,be,bf,me,mf,mf-bf}' log_joint_seed$s.csv; done
```

```
seed 0 | shipped ep=14 f1=0.38250 | doc-rule ep=15 f1=0.41685 | gap=0.03436
seed 1 | shipped ep=11 f1=0.39922 | doc-rule ep=11 f1=0.39922 | gap=0.00000
seed 2 | shipped ep=14 f1=0.36731 | doc-rule ep= 9 f1=0.41135 | gap=0.04404
seed 3 | shipped ep=15 f1=0.37941 | doc-rule ep= 7 f1=0.39831 | gap=0.01890
seed 4 | shipped ep=15 f1=0.40151 | doc-rule ep= 6 f1=0.41320 | gap=0.01169
```

Global argmax F1 = **seed 0, epoch 15** = the final epoch ⇒ its weights are what
`seed_0/checkpoints/last_checkpoint.pt` holds (`3rdJ_04D_train_4split.py:876`, written every joint
epoch). 🔴 **To verify before acting on Claim B:** that the file exists for seed 0 (it is on Speed,
which v3 does not touch), and that the payload's 0-based `"epoch"` field corresponds to the log's
1-based epoch 15.

**A2 — the log-visible hard gates are never threatened** (75 epochs):

```bash
awk -F, 'FNR>1{n++; if($16<p||n==1)p=$16; if($17<f||n==1)f=$17; if($15>i||n==1)i=$15}
  END{printf "epochs=%d min pr_auc=%.6f min f1=%.6f max isr_raw=%.6f\n",n,p,f,i}' log_joint_seed*.csv
# epochs=75 min pr_auc=0.518213 min f1=0.282362 max isr_raw=0.014245
```

Bars: PR-AUC ≥ 0.15, F1 ≥ 0.25, ISR ≤ 0.5 %. **Column mapping matters** — the header is
`epoch,phase,train_loss,act_loss,home_loss,work_loss,retail_loss,cop_loss,div_loss,excl_loss,val_js,home_gap,work_gap,retail_gap,isr_raw,pr_auc,f1,val_score,lr,grad_norm,elapsed_s`,
so `$16=pr_auc`, `$17=f1`, `$18=val_score`. Cross-check: seed 3 epoch 15 reads
`pr_auc 0.519045 / f1 0.379410`, the exact pair RW1/RW2 report.

**A3 — per-channel spread and both rules** (Step 9, shipped deliverable):

```bash
python - <<'EOF'
import csv, statistics as st
rows=list(csv.DictReader(open('Leg3_4-split/Step9_docs/outputs_step9_deliverable/'
                             'step9_eui_by_channel.csv',encoding='utf-8')))
for ch in ['office','retail','hotel']:
    v=[float(r['eui_CFA_kWh_m2']) for r in rows if r['channel']==ch]
    lo,hi=[float([r[k] for r in rows if r['channel']==ch][0]) for k in ('band_lo','band_hi')]
    print(ch, len(v), round(min(v),2), round(st.median(v),2), round(max(v),2),
          'in_band', sum(lo<=x<=hi for x in v), 'median_in_band', lo<=st.median(v)<=hi,
          'range/width', round((max(v)-min(v))/(hi-lo),3))
EOF
```

**A4 — X-3 on the shipped pool** (`outputs_step4/sweep/seed_3_raked3_mindwell_actv/step4_validation_report.txt:126-130`):

```
[PASS] ISR-final | ... 0.000000% (0/6,149,856 slots with >1 active channel; hard gate, must be exactly 0%)
[PASS] X-3 | Pairwise exclusivity (hom AND wrk): 0 cells (0.0000%)
[PASS] X-3 | Pairwise exclusivity (hom AND ret): 0 cells (0.0000%)
[PASS] X-3 | Pairwise exclusivity (wrk AND ret): 0 cells (0.0000%)
```

Thresholds: production profile `x3_pass_pct 1.0 / x3_warn_pct 5.0` (`:368`); the smoke profile at
`:325` is 5.0 / 15.0 and does not apply to the shipped run.

**A5 — the rule counterfactuals, quoted from the gate's own output**
(`outputs_step9_deliverable/step9_gates.json`):

- office: *"COUNTERFACTUAL: the median-in-band rule would return **FAIL** on this same data."*
- retail: *"COUNTERFACTUAL: the all-cells rule would return **FAIL** on this same data."*
- hotel: *"COUNTERFACTUAL: the median-in-band rule would return **PASS** on this same data — ***
  THE TWO RULES DISAGREE HERE, so this gate's status is set by the RULE CHOICE and not by the
  model."*

---

## Progress Log

*(Entries are appended here as tasks close. Every entry states its pre-registration file, its
predictions **written before the data was opened**, and the scorecard against them.)*

### 2026-08-06 — plan opened

**Not a task closure.** The v2 board closed 49/49 with three items owed by the user carried as a
bullet list. This plan converts them into tasks and adds the three that make them decidable.

**Work actually done in this response:**

1. Read the code behind all three decisions rather than the v2 summary of them. **Three corrections
   resulted** (table in §0, appendix A1–A5 reproduces each): the `val_score` re-run is not five
   retrainings and the documented rule was never implementable as written; X-3 is not an office
   check and cannot fire while ISR-final passes; retail FAILs under *both* rules, so uniform
   `median` would move exactly one status in the scorecard.
2. **Rescued the evidence base.** The 5-seed joint training logs existed **only** in a session
   scratchpad. Copied to `improvements/v3/e4_seed_logs/` (15 files, 49 KB) so appendix A1/A2 are
   reproducible from the repo. 🔴 **The E1 falsifier scripts were already gone** — not in the repo,
   not in any surviving scratchpad. They are the only demonstration that 10 RW/RETM gates are blind
   to a person-level shuffle, and they must be rewritten inside V3-J1.
3. **Board updated at its existing URL**, v2's 49 rows and its full decisions block kept verbatim
   below the new v3 material — *most of that block is closed work that had accumulated under a
   "waiting on you" heading, which is part of why three real decisions were easy to lose.* Verified
   before publishing: the task array parses, **55 rows** (43 done + 6 decided + 3 your-call +
   3 ready), all HTML tags balanced, the render script runs without error, and the 16 pre-existing
   list items are all still present.
4. 🔴 **The board's own source was the defect V3-J2 describes.** It has been republished for days
   from a file living only in session scratchpads. `board_v3.html` and `board_patch_v3.py` are now
   in the repo.
5. **Nothing was executed, no threshold moved, no band touched, Speed never contacted, zero
   simulation cells.**

**Owed by the user — the same three, now with the evidence to decide them:**
V3-H1 (`val_score`), V3-H2 (X-3), V3-H3 (the hotel rule).
🔴 **H3 is decidable today and carries the trap**: the tempting uniform rule clears exactly the one
gate under discussion, and the principle already on file argues against it.

---

### §1.1 — V3-J1 CLOSED: the gate exists, it is seen failing AND seen passing, and the pool fails it

**Status: DONE, 2026-08-06.** Local win32, ~4 minutes of compute in total. **Speed never contacted,
zero simulation cells, the shipped pool never written to** (md5 `ebb1dfe8…` verified identical
before and after every arm).

**Pre-registration:** `improvements/v3/V3-J1_PREREGISTRATION.md`, written before a single agreement
statistic was computed, with an addendum written after the five arms and **before** the two
diagnostics. **Scorecard: 6 PASS / 4 FAIL / 1 N-A.**

#### The result

| arm | J1a participation | J1b timing |
|---|---|---|
| **F0 control (the shipped pool)** | lift **+0.0179**, z 2.2 ⇒ 🔴 **FAIL** | lift **+0.0202**, z 1.1 ⇒ **WARN** |
| F1 within-cell shuffle | +0.0027 ⇒ FAIL | −0.0051 ⇒ FAIL |
| F2 retail deleted | undefined ⇒ FAIL *with the reason printed* | undefined ⇒ FAIL |
| F3 half-shuffle | +0.0055 ⇒ FAIL | +0.0003 ⇒ FAIL |
| **F4 copy (positive control)** | **+2.3778**, z 374.7 ⇒ **PASS** | **+5.0389**, z 245.1 ⇒ PASS |

**8 of 8 required conditions met**, exit 0. **F4 is the row that makes the rest readable**: without
a positive control, a gate reading ≈ 0 on the shipped pool is indistinguishable from a broken gate.
The gate can see person-level structure — it sees **238 %** of it when the structure is there. On
the shipped pool it sees **1.8 %**, which is **0.75 % of what a perfect copy scores.**

#### 🔴 The finding is bigger than retail, and the diagnostic that showed it was pre-registered

| channel | null = cell | null = cell × AGEGRP × SEX × LFTAG |
|---|---|---|
| `ret30` | **+0.0179** (FAIL) | **−0.0002** |
| `wrk30` | **+0.5540** (PASS, z 79.6) | **+0.0122** |
| `hom30` | +0.0000 — *statistic degenerate*, P(any home) = 0.9991 | not run |

**D1 was meant to be the exoneration test and it started out as one:** `wrk30` clears the bar at
**+0.554**, 31× retail's, so the near-zero retail reading could not be blamed on the day-type
mismatch, on sparsity, or on the statistic. **Then D2 dissolved it.** Once the null also matches
age, sex and labour-force status, **work's lift collapses from +0.554 to +0.012 and retail's to
−0.0002.**

**So the honest reading is not "the retail head is broken".** It is: **the generator reproduces
strata, not individuals.** Work only *looked* person-specific because `LFTAG` — whether the person
works at all — was free information outside the null. This is V2-E1's finding about the *gates*,
now demonstrated about the *model*: **a person's generated day is, to measurement, a draw from
their stratum.**

⚖️ **The counterargument, recorded before the diagnostics rather than after them.** Each respondent
has **exactly one observed diary day**, so the true cross-day-type persistence of retail behaviour
— how much a person's Tuesday *should* predict their Saturday — **is not measurable from this data
at all.** The gate measures retention against **zero**, not against the truth. If real retail
behaviour is near-independent across day types for an individual, a lift of ≈ 0 is correct
behaviour and the 0.10 bar is wrong. **The bar was not moved.** The limitation is published beside
the verdict, and it is the first thing a reader should be told.

#### Predictions vs outcome — 6P / 4F / 1 N-A

| # | prediction | outcome |
|---|---|---|
| **P1** | F0 J1a lift ≥ 0.10 ⇒ PASS | 🔴 **FAIL** — **+0.0179**, below even the WARN floor. I assumed that because the model is *handed* the person's own retail vector it would retain it |
| **P2** | F0 J1b lift ≥ 0.10 | 🔴 **FAIL** — +0.0202, WARN. Flagged in advance as the one I was least sure of |
| **P3** | F1 within ±0.02 of 0, both FAIL | ✅ **PASS** — +0.0027 / −0.0051 |
| **P4** | F2 runs clean, FAILs, says why | ✅ **PASS** — *"statistic UNDEFINED … reported as FAIL rather than as 0.0"* |
| **P5** | F3 lift is 0.35–0.65× F0 | 🔴 **FAIL** — **0.31×**, just outside. Also flagged in advance; the half-shuffle is not linear in the fraction shuffled |
| **P6** | F4 J1a lift ≥ 2.0 | ✅ **PASS** — +2.3778 |
| **P7** | the demographic null cuts F0's lift by < half | 🔴 **FAIL — and this is the finding.** It cuts it to **zero** (−0.0002) |
| **P8** | wiring changes no existing gate line | ✅ **PASS** — diff is `98a99,100`, **additions only**; pass count unchanged, +1 WARN +1 FAIL |
| **P9** | J1a and J1b do not return the same verdict class on F0 | ✅ **PASS** — FAIL vs WARN |
| **P10** | `wrk30` lift ≥ 3× retail's and clears 0.10 | ✅ **PASS** — 31×, +0.554 |
| **P11** | if home *and* work also read < 0.02, the finding is generator-wide | ⚪ **N-A** — its condition was written against the **cell** null, where work reads +0.554. **Not retro-matched to the demographic null**, which would have satisfied it; that result is reported on its own terms above |

**Four failures, and three of them are mine in the direction that costs something:** I predicted the
model retains the individual, and it does not.

#### Two defects caught in my own work, before either shipped

1. 🔴 **My first wiring recorded the coverage line at PASS** — putting a **non-gate into the
   scorecard's pass count**. That is exactly what V2-E7 forbade for INFO lines in the Step-5
   validator, committed by me in Step 4 forty minutes after quoting the rule. Coverage is now folded
   into the participation line's detail and **RW9 adds exactly two scored lines.** Caught by reading
   the before/after diff, which showed `+1 PASS` that no gate had earned.
2. 🔴 **The Step-4 validator carries the same latent INFO defect V2-E7 fixed in Step 5.**
   `self.results` holds only `pass`/`warn`/`fail` (`:288`) and the icon map (`:459`) has no
   fallback, so `_rec("info", …)` raises `KeyError`. **Recorded, deliberately not fixed** — fixing
   it changes the scorecard's rendering, and this task is not a scorecard change. It is written into
   `validate_person_retail`'s docstring so the next person meets it before they trip on it.

Also worth keeping: **`hom30` exposes a real limit of the J1a statistic.** When a channel's marginal
sits at 0.9991 the conditional probability is at its ceiling and the lift is structurally ≈ 0 — the
statistic is *degenerate*, not passing and not failing. For retail (0.20) and work (0.32) it is
fine. A future channel would need J1b, or a different statistic.

#### What shipped

| | |
|---|---|
| `Step4_docs/person_retail_gate.py` | the statistic, the null, the pre-registered bands. `--channel` and `--demo-null` make the two diagnostics reproducible |
| `Step4_docs/falsify_person_retail_gate.py` | the five arms, **in memory**; exit 1 if any required verdict is unmet |
| `Step4_docs/3rdJ_04_augmentationGSS_4split_val.py` | **RW9 wired in**, md5 `50c9b389…` → `02ae34c8…`; predecessor archived as `archive/…_val.2026-08-06_pre_RW9.py` |
| `improvements/v3/j1_evidence/` | the diagnostics, both gate-line dumps, the additions-only diff, the falsifier transcript, the pool md5 |

🔴 **The shipped Step-4 report was NOT regenerated, and that is a stated gap, not an oversight.**
`sweep/seed_3_raked3_mindwell_actv/step4_validation_report.{html,txt}` is a **cluster artefact**;
regenerating it locally would stamp it `win32` and silently replace a cluster provenance record with
a local one — the same reasoning that kept `outputs_step9/` untouched in V2-D4. **So RW9 is in the
code and is not yet in the shipped report.** The before/after runs used for P8 ran in a scratch
directory against a hardlink of the pool, and are a **degraded harness** (126P/14W/8F, because the
training log, `isr_summary.json` and the thresholds file live only on Speed) — they are a valid
before/after comparison and **are not the shipped scorecard**.

#### What this does to V3-H2

**H2 asked whether X-3 should FAIL rather than WARN.** §0 already showed the choice has no detection
consequence. **Now the gate that does have one exists, and it reads FAIL.** Option C in H2 — *leave
X-3 as a WARN, document that it is a decomposition of ISR-final, and build the gate that was
actually meant* — is now the only option whose second half is already done. **The decision is still
the user's; what changed is that it can now be taken with the number in hand rather than in
principle.**

---

### §1.2 — V3-J2 CLOSED: the lost falsifier is rebuilt, it reproduces E1 — and it corrects it

**Status: DONE, 2026-08-06.** Six runs of the **real** validator on six pools, local win32,
~8 minutes. **5 of 6 required conditions met**; the one failure is mine and is kept failing (below).
Evidence: `improvements/v3/j2_evidence/` (six gate dumps + four diffs + the score).

#### Part 1 — the rescue

| artefact | before | now |
|---|---|---|
| 5-seed joint training logs | session scratchpad only | `improvements/v3/e4_seed_logs/` (15 files) |
| the board's own HTML | session scratchpad only, **while being published for days** | `improvements/v3/board_v3.html` + its patch scripts |
| R5 additions-only run diff (`e78/`) | scratchpad only | `improvements/v3/rescued/e78_r5_rundiff/` |
| the reverted R1 re-spec's output (`e6/val_final.log`) — **§0.33 cites this as the reference for checking a re-implementation** | scratchpad only | `improvements/v3/rescued/e6_reverted_attempt/` |
| the 26 `MIN_POOL` sweep run logs | scratchpad only | `improvements/v3/rescued/e4c_minpool_sweep/` |

**Not rescued, deliberately:** the 24 GB of E5 campaign run output. V2-G1 already decided that
regenerable simulation output is not kept; this is the same call, made the same way.

#### Part 2 — the rebuilt falsifier, and what it says

`Step4_docs/falsify_rw_battery_blindness.py`. Six pools, each a **text-level** rewrite of the
shipped file — only the named 48-column blocks are replaced and every other byte is carried through,
because round-tripping 644 columns through a dataframe would reformat numbers and then a gate that
moved could not be attributed.

| arm | what moves | result |
|---|---|---|
| **A** control | — | the shipped pool |
| **B** retail-only shuffle | `ret30` between people, within cell | **RW/RETM battery byte-identical (40 lines)** — E1 reproduced |
| **C** copy | synthetic := own observed | RW9 **PASS** +2.3778 |
| **D** shuffle(copy) | C, then permuted | battery identical to C; **RW9 flips PASS → FAIL** (−0.0035) |
| **E** joint shuffle | `hom30`+`wrk30`+`ret30` together | exclusivity confound gone; activity confound appears |
| **F** full-day shuffle | **all 13 channel blocks** — the whole day | 🔴 **4 of 150 lines move** |

**C vs D is the demonstration the task existed to produce:** two pools with identical marginals and
an identical RW battery, one of which has person-level structure and one of which does not — and
**RW9 is the only thing that can tell them apart.**

#### 🔴 And it corrects V2-E1, which is the part I did not expect

E1 concluded that under its person shuffle *"only `ISR-final` and `X-3` fire, and neither is a
retail gate"* — reported as evidence that those two gates catch person-level scrambling. **They do
not.** Arm B reproduces exactly that signature, and the run diff shows why:

```
ISR-final   0.000000 % PASS  ->  1.421611 % FAIL   (87,427 / 6,149,856 slots)
X-3         0 cells    PASS  ->  73,448 cells WARN (hom AND ret)
S9 semantic 10.8 %           ->  93.6 %
```

**Permuting the retail block alone puts two channels in the same slot.** A person who was AT_HOME at
14:00 inherits a stranger's 14:00 shopping episode. `ISR-final` fired because the perturbation
**introduced simultaneity**, not because it detected a scrambled person. *A perturbation that
changes more than one thing cannot attribute what it breaks* — the lesson E1 itself wrote down,
now applied to E1's own arms. **E1's surviving claim is untouched and is reproduced here exactly:
all ten RW/RETM gates are byte-identical.** What is withdrawn is the reading that ISR-final and X-3
are person-level discriminators. *This also independently confirms §0's X-3 analysis: X-3 fired only
where ISR-final fired, never alone.*

#### 🔴 Arm F: an inventory of the whole validator, pre-registered and it held

Arm E fixed the exclusivity confound (`ISR-final` and `X-3` never move) but created another —
moving the presence channels while leaving `act30` behind sends `S9` to 93.6 % and `GA-3` to
+17.40 pp FAIL. **There is no perturbation that destroys only the person→retail link.** So arm F
moves the **entire day**: all thirteen channel blocks to another person in the same cell. Every row
stays an internally consistent day; every marginal is preserved; only *whose day it is* is
destroyed.

**Out of 150 validator lines, exactly 4 move:**

```
OW5      day-type ordering wkdy>=Sat>=Sun   58.2 %  ->  55.0 %
OW5-REG  regression vs the Leg-2 baseline   PASS    ->  WARN
RW9      participation                      +0.0179 ->  +0.0083
RW9      timing                             +0.0202 ->  -0.0116
```

**Everything else is byte-identical** — the RW battery, RETM, ISR-final, X-3, S9, GA-3, the REG
gates, G1–G4, OW1, OW4. **P19 predicted "at most 6 lines, all RW9 or OW5-family" and it held.**

**So the Step-4 validator contains exactly two checks that can see the person at all** — `OW5`,
which reads one respondent's three day-types for ordering, and `RW9`, which is one day old. Every
other check in the file is a statement about a population. That is a much sharper statement of
V2-E1's finding than V2-E1 made, and it is now demonstrated rather than argued.

#### Predictions — P12–P19, 7 PASS / 1 FAIL

| # | prediction | outcome |
|---|---|---|
| **P12** | arm E: `ISR-final` and `X-3` stay PASS | ✅ **PASS** — neither line moves |
| **P13** | arm E: RW/RETM battery byte-identical | ✅ **PASS** |
| **P14** | arm E: RW9 participation below +0.010 | ✅ **PASS** — +0.0083 |
| **P15** | arm E: `S9` semantic within 2 pp of A | 🔴 **FAIL** — 10.8 % → **93.6 %**. Flagged as the risk before the run; it is what forced arm F |
| **P16** | arm F: `ISR-final` and `X-3` unchanged | ✅ **PASS** |
| **P17** | arm F: RW/RETM battery unchanged | ✅ **PASS** |
| **P18** | arm F: RW9 participation below +0.010 | ✅ **PASS** — +0.0083 |
| **P19** | arm F: ≤ 6 lines move, all RW9 or OW5-family | ✅ **PASS** — exactly **4**, all of them |

#### The condition I left failing

**`RW9's number moves under the A→B shuffle` requires a ≥ 3× drop; it dropped 2.2×** (+0.0179 →
+0.0083). **The criterion is not relaxed to 2×.** It was written on the assumption that the control
pool has person-level signal to destroy, and V3-J1 had already shown it has almost none — a pool
sitting at the null cannot fall far from it. **The criterion was mis-specified, the arm behaved
correctly, and the honest record is a red line in the transcript rather than a threshold edited
after the fact.** The C→D pair is where a large drop can exist, and there it is +2.3778 → −0.0035.

**Exit code 1**, deliberately: 5/6. A falsifier that exits 0 while one of its own conditions failed
would be the defect this project spends its time hunting.

#### Housekeeping

**No shipped artefact was touched.** All six pools were written into a scratch directory and deleted
at the end; the control arm was a **hard link**, so the shipped pool was never copied and never
written. Only the six gate dumps and four diffs are kept — 11 small text files.

---

### §1.3 — V3-J3 CLOSED: a check that fails when an owed item goes missing, seen failing 6 ways

**Status: DONE, 2026-08-06.** `improvements/v3/j3_ledger_check.py`, ~230 lines, no dependencies
outside the standard library. **Control passes on the real tree; 6 of 6 perturbations detected;
7/7 arms behaved as required.** Transcript: `improvements/v3/j3_falsify_run.txt`.

**What it enforces.** The plan, the manager prompt and the board must agree — *in their own
vocabularies* — about what is owed by the user:

| | how each artefact declares it |
|---|---|
| plan | summary-table rows carrying the decision glyph |
| prompt | task-table rows marked *"your call"* |
| board | task entries in state `waiting` **and** the reader-facing decisions block |

- **C1** the three sets are identical
- **C2** every owed ID has its own task section in the plan — **a missing section is a hard
  FAILURE, never a skip**
- **C3** the plan's status-panel `DECISION n` equals the number of decision rows in its table
- **C4** every owed ID is *named in the board's prose*, not only in its data array

#### Seen failing

| arm | perturbation | detected by |
|---|---|---|
| **F0** | control, unmodified | — *passes*, as it must |
| **F1** | owed item removed from the prompt | C1 |
| **F2** | owed item's board state flipped `waiting` → `open` | C1 |
| **F3** | **the 08-05 defect**: prompt's owed rows deleted and replaced with *"Waiting on the user: nothing blocking"* | C1 |
| **F4** | owed item's task section renamed out of existence | C2 |
| **F5** | status panel drifts from the table (`DECISION 3` → `2`) | C3 |
| **F6** | still `waiting` in the data, but the **prose** no longer names it | C4 |

**F6 exists because of a gap in my own first falsifier.** After five arms, **C4 had never once been
the check that fired** — every failure was caught by C1, C2 or C3. A condition that has never fired
has not been shown to work; by this project's own standard C4 was decoration. F6 exercises it, and
it is the arm that reproduces the 08-05 defect *most* exactly: the machine-readable field was never
wrong, the sentence a human reads was.

#### 🔴 A claim in this plan's own J3 description was wrong, and it is corrected rather than quietly met

The task section said F3 would be *"the repository exactly as it stood on 5 August, which is not
synthetic"*. **It is not that.** The real 08-05 triple is v2-era: its IDs are `V2-*`, its prompt
uses different section headings, and this checker parses the v3 vocabulary. Running it against
those files would report a mismatch for the trivial reason that it cannot read them. **So F3
reproduces the 08-05 *defect pattern* on today's artefacts** — the owed rows deleted, the sentence
*"Waiting on the user: nothing blocking"* put in their place, which is the wording the 08-05 prompt
actually used at its line 422. That is a weaker claim than the one I wrote, and it is the true one.

**Known limitation, stated rather than discovered later:** this check reads the **v3 generation's**
artefacts. Pointed at the v2 files it would fail for the wrong reason. A future generation must
either keep the same three markers or update the three parsers — and the parsers are 4 short
functions at the top of the file for exactly that reason.

**One more thing it does not do:** it checks that the three artefacts *agree*, not that they are
*right*. If all three lose the same item on the same day, the check passes. That is why C2 and C3
exist — they anchor the owed set to structures (task sections, the panel count) that a careless edit
does not touch — but the residual risk is real and is not papered over.

---

## 🔴 2026-08-06 (later) — the three decisions, taken against the earlier legs

**Why this section exists.** The user's instruction was to proceed *"en regardant les projets
avant pour être compatible avec eux"* — decide these three against 2J and Leg-2, not against Leg-3
alone. **That instruction changed two of the three answers**, and it produced a finding that no gate
in this project could have caught.

The four documents read: `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` (+ its Overview) and
`2J_docs_occ_nTemp/00_GSS_Occupancy_Pipeline.md` (+ its Overview), then — because two of them
pointed at code — the Leg-2 scorers those docs describe.

### §2.1 — V3-H1 DECIDED: **option C**, and the precedent is why it is not option A

**Decision: fix the doc — WITHOUT deleting the rule — and write the trigger.** Landed
2026-08-06 in `Step4_docs/3rdJ_04_augmentationGSS_4split.md` (the "Checkpoint selection" section)
and `Step4_docs/3rdJ_04D_train_4split.py` (docstring only, predecessor archived
`archive/3rdJ_04D_train_4split.2026-08-06_pre_H1_docstring.py`, md5 `cd7167ca`).

🔴 **The precedent is what ruled out option A.** Option A as written in this plan was *"rewrite
`:157` to describe `val_score` selection"* — i.e. make the doc match the code. The earlier legs say
do not:

> `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md:262`, in the design-decisions table:
> **"Pareto model selection, never composite | The Leg-1 composite chose a 2/4-gate model;
> per-objective frontier is the lesson learned."** Repeated verbatim in the Overview at `:153`.

So *"never a single composite score"* is not a Leg-3 preference that Leg-3 may rescind. It is a
**Leg-1 finding, promoted to a Leg-2 design principle, then frozen into Leg-3 by dr_L3-13** — three
documents deep. Rewriting `:157` would delete it from the only place a Leg-3 reader would look, and
would do it in the week it became inconvenient. **That is the J3 move — editing a spec to match what
was built — which I refused for my own task three hours earlier.**

**So the rule stays as the specification and the deviation is recorded under it**, with: what
actually selected the shipped weights (`:881` on the composite at `:499`), the cost (+0.0218 retail
F1, 5.6 % relative, **0.16 sd** of cross-seed spread), the reason it was not re-selected, and the
second reason that constrains any future attempt (the documented rule needs **75 inference+rake
cascades** to evaluate its own first clause, and that clause is **inert** on this data).

**The reason on record is not cost.** Both rules rank epochs on the **teacher-forced** `pr_auc`/`f1`
columns that V2-E1 and V3-J1 showed are blind to person-level retail skill. The expensive option
buys +0.0218 of a statistic already demonstrated not to measure the thing. *Cost is the weaker
argument;* it is stated and then set aside — and it is smaller than the v2 board claimed (one
inference + rake cascade, not five retrainings, because the documented winner is the **final** epoch
and `:876` writes `last_checkpoint.pt` every joint epoch).

**The trigger — the operative half of C.** Recorded in the doc, three conditions, any one of which
reopens the code fix:
**T1** a person-level gate (RW9 or successor) ranks the five seeds and disagrees with `val_score`;
**T2** the retail-F1 gap between the two rules exceeds **1 sd** of cross-seed spread (today 0.16 sd);
**T3** Steps 5→9 are reopened for any other reason, at which point the re-cascade is not a cost this
decision has to carry.

🔴 **And a second defect, found while landing the decision: the code's own docstring was lying.**
`3rdJ_04D_train_4split.py:361-364` asserts that `val_score` *"is NOT the gate-first → lexicographic
selection criterion (that happens later, across the 5-seed sweep, in a separate checkpoint-selection
step)"*. **Twenty lines below, at `:881`, it is exactly that criterion** — and the "separate
checkpoint-selection step" **does not exist**: `grep` for `seed_0` / `range(5)` / `for SEED` across
`Step4_docs/*.py|*.sh` returns **zero hits**. Nothing ever compared the five seeds under the
documented rule. The docstring is now corrected **in place, with the wrong paragraph kept above the
correction** so the correction has something to point at. Comment-only: no behaviour change, no
checkpoint moves, nothing regenerated.

**Landing test (as specified in the task).** `grep` proves it:

```bash
grep -c "SHIPPED ARTEFACT WAS NOT SELECTED\|REOPEN TRIGGER" \
  Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md      # 2
grep -c "Never a single composite score" \
  Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md      # 1  <- the principle is still there
```

**What did NOT change:** no checkpoint, no pool, no band, no gate status, no scorecard. `best_model.pt`
is still what `04E` loads and the shipped pool is byte-identical (md5 `ebb1dfe8`, re-verified).

**Known gap, stated:** the local `3rdJ_04D_train_4split.py` now differs from Speed's copy by this
comment block. v3 does not contact Speed, so the two are out of sync until the user syncs them; the
difference is comments only and cannot change a result.

### §2.2 — V3-H2 DECIDED: **option C**, and the impossibility claim survived being attacked

**Decision: X-3 stays a WARN, the relation to `ISR-final` is documented, and the gate that was
actually meant is `RW9` — built yesterday, and it FAILs.** The severity is not raised. Six runs of
the **real** validator, local win32, ~10 min. **6 of 7 conditions met; the seventh is mine and is
left failing.** Falsifier: `Step4_docs/falsify_x3_isr_relation.py`; evidence
`improvements/v3/h2_evidence/` (6 gate dumps + the score). Pool md5 `ebb1dfe8` unchanged; the control
arm was **hard-linked**, so the shipped pool was never copied and never written.

#### The claim, and how it was attacked rather than asserted

The task said: *"a claim about an impossibility must be attacked, not asserted."* Reading
`:1448-1452` is how the claim was **formed**; it cannot also be the evidence for it. So six pools:

| arm | perturbation | ISR-final | X-3 census |
|---|---|---|---|
| **A** control | — (hard link) | **PASS** 0.000000 % | `0 · 0 · 0` |
| **B** | one slot forced hom=1 **wrk=1** ret=0 | **FAIL** 0.000016 % | `hom∧wrk = 1`, others 0 |
| **C** | one slot forced hom=1 **ret=1** wrk=0 | **FAIL** 0.000016 % | `hom∧ret = 1`, others 0 |
| **D** | one slot forced wrk=1 **ret=1** hom=0 | **FAIL** 0.000016 % | `wrk∧ret = 1`, others 0 |
| **E** | one slot forced hom=1 **ret=2** — outside {0,1} | **FAIL** *refused* | *(no lines)* |
| **F** | **1 000** hom∧wrk conflicts | **FAIL** 0.016261 % | `hom∧wrk = 1000` |

**B/C/D are the positive controls, and the census was known before the run**: the control pool has
zero conflicts, so forcing *k* slots to a chosen pair with the third channel explicitly zeroed
injects exactly *k* conflicts of exactly that pair. All three landed on the cell. Without them,
"X-3 read zero" would be indistinguishable from "X-3 is broken" — the lesson V3-J1's arm F4 taught
the day before.

🔴 **The claim held: no arm produced X-3 > 0 while ISR-final PASSed.** Not because no attack was
tried — E and F were the attacks.

#### 🔴 It is sharper than the plan said, and the sharper version is the one that decides it

The plan argued that X-3's WARN band *"lies entirely inside the region where a hard gate has already
failed"*. The runs say something stronger. **X-3 grades `PASS` at one conflict — and still grades
`PASS` at one thousand.** Its thresholds are `x3_pass_pct = 1.0 %` / `x3_warn_pct = 5.0 %` of *all*
slots, so it cannot even reach WARN until **61,499 slots** conflict, a state in which `ISR-final`
(hard FAIL above `1e-9`) has been failing by **five orders of magnitude**.

**So raising X-3 to FAIL does not change when the scorecard fails. It changes the printed severity of
a line that is only reachable deep inside an already-hard-failed pool.** Option B is not a stricter
validator; it is a second FAIL for one event.

#### Cross-leg compatibility — this is Leg-2's rule, unchanged

Leg-2 has the same check, one pair narrower:
`Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS_2split_val.py:781-796`, gate **`OW6`**, *"channel
exclusivity hom30=1 AND wrk30=1"*, graded `self._grade(pct_both, ow6_pass, ow6_warn)` with
**`ow6_pass = 1.0, ow6_warn = 5.0`** (`:242`, the production dict). **Leg-3's X-3 carries the
identical thresholds** (`:368`) applied to three pairs instead of one.

**Leg-2 never made pairwise exclusivity a zero-tolerance gate**; it graded it by rate. The
zero-tolerance role in Leg-3 is played by **`ISR-final`, which is Leg-3-new**. So *leave X-3 a WARN*
is the answer that keeps the two legs comparable, and raising it would break a correspondence that
costs nothing to keep and buys no detection.

#### Arm E: the blind spot I predicted does not exist — and the condition stays failing

**P: a value outside {0,1} would be invisible to both counters** — `(x == 1)` is False for 2, so
neither `n_hw` nor `n_any_gt1` would count it, and the pool would pass a gate it should fail.
**Wrong.** The domain violation is caught one section earlier and **quarantines** the whole chain:

```
[FAIL] RET-PRESENCE | Non-{0,1} values in synthetic ret30_*: 1
[WARN] RETM      | retail presence gate failed -- Section 5b skipped
[FAIL] RW1       | retail presence gate failed -- RW battery skipped
[WARN] RW9       | retail presence gate failed -- person-level gate skipped
[FAIL] ISR-final | cannot recompute -- hom30/wrk30/ret30 columns not all present
[WARN] GA-3      | retail presence gate failed -- 4-way decomposition skipped
```

`_retail_ok` is set at `:988` and read at `:1439`. **`ISR-final` refuses with a reason instead of
returning a clean zero** — the opposite of the *silence* failure mode this project catalogues (a
reader that returns 0.0 for what it cannot parse, blaming the system for its own gap). Here the
reader says it cannot read.

**The condition is left FAILING (6/7, exit 1) and is not rewritten to match.** A prediction edited
after the run stops being one — the same call as V3-J2's 3× criterion. What is recorded is that the
prediction was wrong in the *safe* direction.

**One inconsistency noted and deliberately NOT fixed:** the same quarantine grades **FAIL** on `RW1`
and **WARN** on `RETM` and `RW9`. One cause, two severities. Fixing it is a scorecard change and
belongs to whoever reopens Step 4.

#### 🔴 Two defects in my own harness, both caught here

1. **The impossibility condition was satisfiable by a parse miss.** In the first scoring run arm E's
   ISR-final line is the *"cannot recompute"* variant, which the reader did not match — so E scored
   `level = None`, and *"no arm has ISR-final PASS while X-3 > 0"* held for E **because nothing was
   read**, not because the claim did. That is the vacuous reading this project spends its time
   hunting, sitting inside the one condition carrying the argument. Hardened: the refusal variant is
   parsed, and an **unreadable arm now fails the condition** rather than satisfying it.
2. **`| tee` swallowed the exit code.** The first run printed `EXIT=0` while the script returned
   **1**. Re-scored without the pipe: `TRUE EXIT=1`. A falsifier whose non-zero exit is invisible is
   a falsifier that cannot fail a pipeline.

#### What this decides, and what it does not

**Decided:** X-3 stays WARN; its docstring and the val doc record that it is a **decomposition** of
`ISR-final` — it says *which pair* conflicted — not an independent detector. **Not decided by this:**
whether Step 4 can see a person at all. It cannot, much: V3-J2's arm F moved an entire generated day
to another person and **4 of 150 lines** moved. **The detection gap H2 was really about is real, it
is now measured, and the gate that closes it (`RW9`) FAILs at +0.0179 against a 0.10 bar.** That is
the part of option C that matters, and it was built before this decision was taken.

### §2.3 — V3-H3 DECIDED: **option A**, made into a principle — and the citation for the rule was false

**Decision: keep `all_cells` for office and hotel, `median` for retail — and write down the
criterion that produces that assignment**, so it stops being an unexplained per-channel value.
Landed in `Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` (the `BENCH` comment block) and
`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md:402`. **No `rule` value changed. No band moved.
No status changed. No artefact regenerated.** `3rdJ_09_bench_doc_sync_check.py` re-run: **PASS**.

#### 🔴 The finding: the office rule's provenance claim was false, in both places at once

The scorer said `all_cells` was *"the original rule"* and the master doc said the office band was
*"inherited from Leg-2 … Table 7.1"* with **`rule: all-cells`**. The band **values** are inherited —
`(low 100, central 135, high 200)` is `OFFICE_EUI_BAND = (135.0, 100.0, 200.0)` exactly. **The rule
is not, and neither is the severity.** Leg-2 scored those same values on the **channel median** and
graded a miss **WARN**, in both scorers that carry it:

```
Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:462-470   gate G2o
    med = float(o["eui_kWh_m2"].median()); okb = lo_b <= med <= hi_b
    status = "PASS" if okb else "WARN"
Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.py:1420-1431      gate 4.3-office
    omed = float(allo.median())  ->  WARN, and the message itself says "non-blocking"
```

**Leg-3 took the numbers, tightened the rule AND the severity, and recorded neither.** A reader
checking the office gate against its citation would have found the band and never learned that the
criterion had been changed under it.

🔴 **No gate in this project could have caught that** — and the gate that comes closest says so
itself. `3rdJ_09_bench_doc_sync_check.py` prints, every run: *"REMINDER: agreement is not
correctness. This gate cannot fail on a band that is wrong in both places."* The rule was wrong in
both places. **That line was written as a caveat and turned out to be a description.** It is the
V3-J3 limitation — *the three artefacts agree, they are not thereby right* — hit on a different
artefact the same day. **New vacuous-reading class #17: the consistency check whose two inputs share
an ancestor.** Cross-leg reading is the only thing that finds it, which is exactly what this session
was asked to do.

#### The strongest case against my own recommendation, written before the recommendation

**Restoring Leg-2's rule would not obviously be gate-shopping.** The argument: Leg-3 tightened a
criterion without recording it; correcting an unrecorded drift is housekeeping, not shopping; that it
happens to clear a gate is a consequence, not a motive. It is a serious argument and the user should
have it whole.

**Two things defeat it, and neither is "because hotel would pass".**

1. **Leg-2's convention is a package: median AND WARN.** Adopting the median half alone gives a rule
   that is neither leg's — Leg-2 never had median-with-FAIL. Adopting the whole package changes
   **three** statuses, not one: office **FAIL → WARN**, retail **FAIL → WARN**, hotel **FAIL →
   PASS**. The entire EUI block goes from 3 FAILs to 1 PASS + 2 WARNs on a documentation correction.
   **A basis change that turns FAIL into WARN is a band change in disguise** — the 2026-08-05 R1
   reversion, verbatim, and it binds here.
2. **The spread principle already on file points the other way.** V2-B3 put retail on `median`
   because *"an all-cells rule on a spread smaller than its own uncertainty reports noise as a
   verdict"*. Across-cell range / band width: **office 0.285 · retail 0.443 · hotel 0.959.** Hotel's
   cells span **96 % of its own band** — they genuinely differ; they are not sitting inside their own
   noise. **Hotel is the channel least eligible for the rule that would clear it.**

#### What was actually written into the code

The principle, not a boundary: **default `all_cells`; `median` only where a channel's across-cell
spread is small enough that a re-run's own noise can flip the verdict** — V2-B3's condition, quoted.
Today that is retail alone, on the evidence V2-E3 produced (a −0.05 % median move flipped one cell).

⚖️ **Disclosure kept in the code, not just in this log:** the spreads were measured *after* it was
known which rule clears hotel, so **no numeric boundary is written** — a threshold chosen with the
answer in hand is not blind. The arithmetic is published so a reader can verify that applying the
principle **changes nothing**, which is the one property gate-shopping cannot produce.

**Reopen trigger:** **T1** the user accepts the precedent-restoration argument above (it is theirs to
accept — this decision is a recommendation acted on, not a foreclosure); **T2** any channel's
across-cell spread falls below the demonstrated re-run noise of its own median; **T3** the frozen
deliverable is reopened for another reason, at which point re-publication costs nothing extra.

**What is NOT claimed:** that `all_cells` is the better criterion in general, or that the hotel gate
is right. `S9-EUI-hotel` still FAILs, its floor/ceiling are still contested where V2-B1/B2 said they
were, and the band-applicability limitation for office still stands. **This decision only settles
which rule is applied and why — and it settles it in the direction that leaves every failing gate
failing.**

### §2.4 — closing the three decisions BROKE the ledger check, and that is the day's cheapest finding

**Not planned. Found by running the closure ritual.** The moment V3-H1/H2/H3 stopped being owed,
`j3_ledger_check.py --falsify` died:

```
File "improvements/v3/j3_ledger_check.py", line 172, in falsify
    line = next(l for l in t.splitlines() if "your call" in l and "V3-H2" in l)
StopIteration
```

**Its perturbation arms were built by copying the LIVE artefacts and deleting things out of them.**
That works only while the live tree happens to contain an owed item. **So the falsifier stopped
working at exactly the moment the ledger went empty — the state in which a reader most needs to know
whether the check still does anything.** A test whose fixtures *are* the thing under observation is
not independent of it. Closed 8 hours after the check was written, by the check's own author, on the
first day it was exercised in a state it had not been written in.

**Three repairs, all landed:**

1. **The fixture is now synthetic** — a minimal three-artefact ledger written from scratch carrying
   one owed item (`V3-X1`) in each artefact's own vocabulary (plan glyph row + section + panel
   count · prompt *"your call"* row · board `"waiting"` state + prose mention). It exercises the same
   four parsers and is independent of what the repo happens to contain.
2. **The live tree is still checked — as its own arm (`F0L`).** The fixture proves the *check* works;
   `F0L` proves the *repository* currently agrees with itself. Conflating those two was the original
   design error.
3. **`PROMPT` now points at `…_v3_closed.md`**, the current handoff. A ledger check reading a
   superseded prompt would agree with itself about a document nobody is following.

**Result: 8/8 arms — 2 controls + 6 perturbations, exit 0.** Transcript:
`improvements/v3/j3_falsify_run_2026-08-06_evening.txt`.

🔴 **And the summary line was quietly wrong again.** It printed *"1 control + 7 perturbations"* after
the second control was added, because the split was **hard-coded** as `len(results) - 1`. This is the
third time in two days a count has been inflated by a constant that stopped being true — the same
class as scoring the RW9 coverage line as a PASS. **It is now counted, not asserted.**

#### The limitation this leaves, stated plainly

🔴 **With zero owed items the live check is vacuous.** All four conditions are satisfied by an empty
set: nothing is owed, so nothing can be missing from anywhere. **It passes today for the right reason
and it cannot fail here any more.** Its evidence is the 8-arm falsifier, not its green run — which is
this project's standard position (a gate is trusted because it has been seen failing, not because it
is green), and it applies to my own gate. **The moment one owed item exists, the check is live
again**; that is the whole point of the synthetic fixture.

---

### §2.5 — the BOARD claimed more than it counted, and the user caught it, not a gate

**Reported by the user, 2026-08-06, reading the published board:** *"il disent que tout est fini, mais
tu m'as dit que Leg-3 n'est pas fini, comment ça passe?"* **The board was wrong and the reading was
right.**

Its header pairs the title **`3J Leg-3 — four-split occupancy to BEM`** and the headline
**`v2 closed · v3 closed`** with the counters **`49 v2 tasks done`** and
**`6 v3 tasks: 6 done, 0 waiting on you`**. Those counters cover the **improvement rounds only** —
documents, gates, falsifiers, decisions. **Leg-3's own scorecards have never been on that board.**
`S9-EUI-office`, `S9-EUI-retail` and `S9-EUI-hotel` — three FAILs, verified in
`Step9_docs/outputs_step9/step9_gates.json` this session at **17 PASS / 0 WARN / 3 FAIL / 10 INFO** —
have no row, no pill and no counter anywhere on it.

🔴 **So the page put "Leg-3" in the heading and a denominator from somewhere else beside it, and never
stated the difference.** Nothing on it was false in isolation; the composition was. **This is the
project's own recurring finding — a green display whose scope is implicit — occurring in my own
artefact**, and it is a near-relative of the v2 *"waiting on the user"* line that read "nothing" while
three decisions were open (the defect `V3-J3` was built for). **The ledger check cannot catch it**: it
verifies that every *owed item* is visible in all three artefacts, and there were no owed items — the
vacuity recorded in §2.4 one entry above. **A reader caught what the checker structurally could not.**

**Fix, additive, no counter moved and no task datum touched:**

1. A **scope band** in the header stating what the counters cover, naming the three Step-9 FAILs, and
   listing the three open user decisions (`LAUNDRY` per-object resize; the Leg-2 `ReportName` defect
   inflating its published office EUI ~1.7×; the audit finding that reaches the submitted 2J paper).
   It also carries the hotel **bimodality** — Tall 195–212 vs SuperTall 149–165, **no cell in
   [170,182)** — because that is what makes "the hotel median" describe no building in the set.
2. The `EMPTY.partial` blurb was **stale in the other direction**: it still read *"three v3 tasks are
   ready and three are your call"* after all six closed. Rewritten, and it now points at the scope
   band rather than asserting completeness on its own.

Board 114,542 → **116,980 bytes**, republished at the same URL.

**The lesson, and it is not a new one:** *"v2 closed · v3 closed"* is a true statement about a list of
things I was asked to fix. **It was displayed under a heading that names the leg.** A scope is not
implied by a title — and an unstated denominator is how a green board tells the truth and misleads
anyway.

#### 🔴 The fix above was itself incomplete, and the user caught that too — v4 exists because of it

The scope band listed the open items **as prose**. The user's next question was *"où sont les tâches
ouvertes ?"* and the answer was **nowhere**: `B-13` appeared in eight files and was a task in none;
`LAUNDRY` likewise. **That is this document's own founding complaint — *a bullet list is not a task* —
committed by me, one level up, on the day this round closed.**

**`improvements/v4/3rdJ_L3_v4_implementation.md` opened the same evening**, carrying all ten as rows
with states: five owed decisions (`V4-A1` hotel rule · `V4-B1` `LAUNDRY` · `V4-B2` the Leg-2 1.706×
defect · `V4-B3` the submitted-manuscript finding · `V4-C1` the severity mismatch), two ready, three
blocked. `improvements/v4/j4_ledger_check.py` reuses this round's falsifier against v4's vocabulary —
**8/8 arms, and the v3 check still 8/8 after the refactor.** **The v3 check stays vacuous and that is
now correct**: v3 owes nothing, v4 owes five, and each round is checked against its own ledger.

**Two defects in my own wrapper, both caught by running it rather than reading it:** the return value
was inverted (`check()` returns the *failure list*, so the wrapper exited 1 on a healthy tree — worse
than no check, and visible only because `[PASS]` printed beside a non-zero status); and retargeting
the fixture *templates* was not enough, because `falsify()` names the fixture id itself in four more
places, so the first v4 run died on `StopIteration` instead of reporting arms. **`FIX_ID` is a
constant now.**
