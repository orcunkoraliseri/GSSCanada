# Manager prompt — 3J Leg-3 **v2 finalisation**, 2026-08-05 (LIVING HANDOFF)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **This file is a LIVING HANDOFF, updated at every step of the work, not once at end of day.**
> The user opens a fresh manager session at any moment; whatever state the work is in, this file must
> already describe it. 🔴 **If you change the state of the work — a job lands, a gate flips, a
> decision is taken — update this file in the SAME response.** A handoff that lags the work is worse
> than none, because it is trusted.
>
> **Predecessors** (do not re-read unless a question below sends you there):
> `3rdJ_L3_manager_prompt_2026-08-04_v2_kickoff.md` — the previous living handoff for **this**
> thread; superseded by this file, kept for provenance. ·
> `3rdJ_L3_manager_prompt_2026-08-05.md` — the Step-9 living handoff for the *simulation* thread
> (arm R, the K sweep, the H1–H11 gates). Still authoritative for anything about arms and the
> cluster. · `..._2026-08-04_progress.md` (the resize thread, §§0.1–0.17) ·
> `..._2026-08-03.md` (arm H closure) · `..._2026-08-03_PRE-ARMH.md` · `..._2026-08-02.md` ·
> `..._2026-08-01.md`.

---

You are the **manager** on the 3J Leg-3 four-channel mixed-use tower BEM pipeline (residential /
office / retail / hotel). Work in `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

Reply in **English** even though the user writes French. Casual, short — under ~100 words unless the
user asks for depth. Act first; skip the "before you launch" caveat lists and fold caveats into one
line afterwards.

---

## 0. Read this first — the one thing that changed

The project is no longer a simulation problem. It is a **decision-and-writing** problem, and the plan
for that is a document:

**`improvements/v2/3rdJ_L3_v2_implementation.md`** — the v2 implementation & finalisation plan.
**45 tasks in 7 work packages, with a table of contents, a traceability matrix and a Progress Log.
It is your task list. Read its `WHERE WE ARE RIGHT NOW` block before anything else** — not the
summary table, which is the index, not the state.

It is the *implementation* counterpart to
**`improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md`** — the *investigation* (13
findings B-1…B-13 with falsifiers). The audit says what is wrong and how to prove it; the v2 plan
says what to change, where, in what order, and how you will know it worked. **Both stay. Do not
merge them.**

**The board.** `scratchpad/v2board.html`, published as an Artifact at
**`https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213`**. 🔴 **Editing the local
HTML is not the update — republishing the Artifact is, and you must pass that exact URL so the link
never changes.** The user asked for this explicitly, twice.

---

## 1. Standing conventions — these are not suggestions

**Closure ritual.** One task at a time. The moment a task closes you do **all** of the following in
the same response, or the closure is not done:

1. Append a dated Progress Log entry to `3rdJ_L3_v2_implementation.md`.
2. Flip the task's row to ✅ in the summary table.
3. **Promote its successor into `🔄 IN PROGRESS`** in the `WHERE WE ARE RIGHT NOW` block.
4. Update `scratchpad/v2board.html` **and republish it at the URL above**.

> If `IN PROGRESS` is ever empty while `READY` is not, the board is **stale** — the last closure
> failed to promote its successor.

**Pre-registration.** Write the predictions, with their FAIL conditions, into the Progress Log
**before** looking at the number. A prediction written afterwards is a description.

**Never widen a band to erase a FAIL.** The mirror of that rule, established by V2-D9: a **correct**
input is never withheld because it deepens one.

**Gates must be seen failing.** Every guard ships with a falsifier that was actually run and actually
failed. The vacuous-gate catalogue is at **fourteen** classes and every one of them was found in this
project's own code.

**Cluster.** 🔴 `sbatch` only, never a blocking `srun`, never bare `python` on the login node,
always `-t 7-00:00:00`, always single-line, always labelled "locally" or "on the cluster".
**Speed was unavailable on 2026-08-05 and everything that day ran on local win32.**

**Deep research is external.** You author a `V<NN>_*.md` prompt in `deepResearch_Resources/`; the
user runs it in Gemini Antigravity. You never search the web yourself. You **do** read and vet what
comes back — six rounds so far, five of which contained fabricated numbers, all caught offline by
arithmetic.

**PowerShell cannot count lines.** `Measure-Object -Line` reports blank lines as zero. Use `wc -l`.

**Corrections are struck, not deleted.** Rule 6 of the plan.

---

## 2. Where the work actually stands

**40 of 45 done · 1 in progress (V2-E4) · 0 ready · 4 blocked.** *(Plan and board verified
programmatically against the summary table — they agree.)* **The entire desk-work critical path is
closed and every decision in the project is taken.** Four tasks closed on the night of 2026-08-05:
**D10, D9, E2, E1**. What remains is one compute job needing an allocation call, the re-score, and
the closing bookkeeping.

**Counting note:** V2-E1 counts as **done** even though half of it is unreachable — the artefact that
half needed no longer exists, so it converted into a V2-G3 **limitation** rather than staying an open
task. A permanently unreachable item does not belong in the queue.

> 🔴 **Correct a standing assumption before you act on it: Speed is NOT down.** It has been reachable
> throughout. The queue is saturated by the **user's own** array jobs (~670 tasks at
> `AssocGrpCpuLimit`). Running locally all week was still right — for that reason, not the one
> previously recorded.

### The three blocking gates, and why none of them is an occupancy problem

This is the single most important finding of the last week, and it is what redirected the project:

| gate | status | why occupancy cannot fix it |
|---|---|---|
| `S9-EUI-office` | **FAIL**, 0/56 in band | The band floor is **100**; the **uninjected** `Default_NECB` control reads **85.45**. A floor no untreated control can clear is measuring the band, not the model. Floor published as **contested and unsourced** (V2-B1). |
| `S9-EUI-retail` | **FAIL**, median 75.4 vs floor 80 | 44/56 cells under. V2-E3 moved the median by **0.05 %** and that alone flipped a cell — the gate is decided at **0.15 %** of its floor. V2-D9 then measured the last untried lever; see §3. |
| `S9-EUI-hotel` | **FAIL**, 21/56 out | Resizing the DHW plant moved the **uninjected** control from 178 → 261. Ceiling re-cited first-party to 90.1-2019 (284.44 / 299.28) by V2-F6; **no band value moved**. |

> 🔴 **Do not propose another simulation arm to move an `S9-EUI-*` gate.** Two weeks and ~10 re-sims
> produced zero gate movement. The user challenged this on 2026-08-04 and was right. The remaining
> honest moves are a published limitation (V2-G3, written) and the re-score (V2-E5).

### Decisions taken, with their numbers

- **V2-B4 / V2-D10 — the hotel DHW plant.** A **global** K was refuted: it changed the *shares*, not
  the physics. At K=6 every heater except `LAUNDRY` had slope exactly 0.000. The deliverable is a
  **per-object** resize: **`Laundry Service Water Use 30.6gpm 180F = 8.5`, all other heaters at
  K = 1.** `LAUNDRY`'s own slope of ln E against ln V went **0.0182 → 0.9848**. K ≈ 7 (V2-B4's text)
  clears only 28 of 56 cells and is **superseded**.
- **V2-B3 — the retail rule** is **median-in-band**, replacing 56-of-56, because an all-cells rule on
  a spread smaller than its own uncertainty reports noise as a verdict.
- **V2-B1 / B2** — office floor contested; hotel ceiling re-cited. **No band widened.**
- **B-1 was falsified by its own falsifier**; **B-13 withdrawn** (no 2J erratum owed); **B-11
  retired** (it was a unit-label error). Three of thirteen audit findings are gone — **V2-G5 owes the
  reconciliation.**

---

## 3. V2-D9 — the last lever on `S9-EUI-retail`, and it pushed the wrong way

**Closed 2026-08-05 night. 2 PASS / 2 FAIL, and the two failures are the finding.**
**Answer: load `NECB-C-*`. It is the correct input, and it makes the gate worse. Both clauses ship.**

| # | prediction | verdict | measured |
|---|---|---|---|
| **P1** | retail EUI **falls** in every cell | 🔴 **FAIL** | falls in **1 of 4**; **−0.2758 … +0.0952** kWh/m² |
| **P2** | \|Δ EUI\| ≤ 1.5 kWh/m² | ✅ PASS | largest **0.2758** |
| **P3** | the median moves **down** | 🔴 **FAIL** | **93.4948 → 93.5880**, **+0.093 kWh/m² — UP** |
| **P4** | other channels move < 0.05 % | ✅ PASS | largest **0.0258 %** |

**🔴 The predicted sign was wrong, and the cause is a lesson worth carrying.** The pre-registration
argued retail is cooling-dominated, "heating is 10.3 % of conditioning". That figure came from
`channel_hourly.csv`. **The gate reads `agg_annual.csv`, and the two bases disagree by 26.5 % — not
just in size but in which term is larger.** On the gate's basis retail is **heating-dominated,
61–64 %**. Occupants are a heat source, so removing **16.6 %** of them costs **+3.2…+3.6 GJ** of
heating and saves only **−0.8…−1.0 GJ** of cooling. The penalty is **3.5–4×** the saving.

**The two halves of D9 pull in opposite directions**, and the uninjected control was in the probe to
separate them:

| arm | schedule swaps | net retail Δ |
|---|---|---|
| 3 injected cells | **1 of 4** ZoneLists | **+1.05 GJ** |
| `Default_NECB` control | **4 of 4** | **−3.14 GJ** |

Same density edit in both, so the difference **is** the schedule effect (≈ −4.2 GJ). But the injector
overwrites three of the four retail ZoneLists, so **in production `NECB-C` reaches only
`LargeHotel Retail` — 11.7 % of the `Tall` retail channel.** The net production effect is the density
correction alone, pointing up.

**Why it ships anyway.** A band is never widened to erase a FAIL; **the mirror is that a correct
input is never withheld because it deepens one.** Retail was running the *office* density. D9 is the
first task to test that mirror, and it holds.

**Strategically this is the closing argument.** The lever is **2.0 %** of the 4.6 kWh/m² the gate
needs, pointing the wrong way. With V2-E3 (median moved 0.05 %, flipping a cell) and the uninjected
control failing the office floor at 85.45, that is the **third independent measurement** that
**`S9-EUI-retail` is not an occupancy problem.** It is a published limitation (V2-G3), not a gate to
chase. **Do not propose another arm for it.**

**Open item D9 created but did not fix:** `LargeHotel Retail` is a retail zone the occupancy injector
never touches. Fixing that is a **Step-7 injector** change, currently unowned.

---

## 3b. V2-E2 — the regression gates were never row-matched, and one is blind to its own signal

**Closed 2026-08-05 night. 3 PASS / 1 FAIL.** Artefact:
`Leg3_4-split/Step4_docs/3rdJ_04E_rowmatched_reg.py`, run locally.

**🔴 The frozen validation split is unrecoverable, and V2-D5 did not change that.** Leg-3's split is
persisted (9,609 rows). **Leg-2's never was** — the only Leg-2 `step4_val_meta.csv` in the repo has
**192 rows**, its `step4_all_meta.csv` has **1,280** against Leg-3's **64,061**: that directory is a
development run. The two val splits intersect on **26 keys, 0.27 %**, which is exactly what E2's own
test method calls disqualifying. **C-2's infrastructure half is confirmed, not repaired. Do not
re-attempt it.**

Rescued at **pool** level, where the match is total: both legs' synthetic pools carry the same
**64,061 `(occID, CYCLE_YEAR)` keys, intersection 1.0000 of both**.

| gate | proxy | row-matched | ratio |
|---|---|---|---|
| **REG-1** activity | 0.00003 bits | **0.043461** | **1,448.7×** |
| **REG-2** AT_WORK | 0.00008 bits | **0.471734** | **5,896.7×** |

Both breach the 0.002 bar — **but that bar was calibrated for aggregated distributions and means
nothing per row. No threshold was moved and no gate status edited.**

**The finding: REG-2 cannot see its own largest disagreement.** JS is *undefined* when either side
has zero mass, so a respondent one leg gives a working day and the other gives none is **dropped**
rather than counted as maximal disagreement — and that is where the legs differ. **18,192 of 64,061
keys (28.40 %) disagree on work/no-work while the net marginal difference is 5.08 %: aggregation
cancels 82.1 % of it.** REG-2's mean is computed on **19.9 %** of rows.

> **The control that keeps this from being an accusation:** two *independent* samples with these
> marginals would disagree at **45.09 %**; observed is **28.40 %**, **κ = 0.3702**. The legs agree
> well above chance. **This is a gate defect, not a model defect.**

**P3 split:** REG-1's cross/within ratio is **7.28×** (bound 5×) — **real Head-1 drift**. REG-2's is
reported **N/A**: the only same-leg control shares seed 3 and differs on **1 key in 64,061**
(κ = 1.0000), so dividing by it yields a meaningless 13,881× — **catalogue class #7**. **Head 2
cannot be judged until independent seeds exist, which is V2-E4.**

---

## 3c. V2-E1 — B-3 answered without compute; the other half is permanently gone

**Closed 2026-08-05 night. 2 PASS / 2 FAIL.**

**🔴 The shipped Leg-3 seed-3 Step-4 checkpoint does not exist on either machine.** Speed holds
`warmup_checkpoint.pt` (19 Jul) alone; all six `sweep/seed_3_*` dirs are outputs-only; Leg-2 by
contrast has both `best_model.pt` and `last_checkpoint.pt`. **Free-running PR-AUC is not
recomputable, permanently.** Retraining is forbidden here and would answer a different question.
**This is the answer to V2-D5's open "ckpt hash needs cluster" — there is no checkpoint to hash.**
→ **V2-G3 limitation. Do not re-attempt.**

**B-3 was settled anyway, with no checkpoint and no GPU**, by perturbing the pool the validator reads
and re-running the real gate code via `--step4_dir` on copies:

| gate | baseline | zero | shuffle | **shuffle-strat** |
|---|---|---|---|---|
| **RW1, RW2** | PASS | **PASS** | PASS | **PASS** |
| RW3, RW8, RETM, ISR-raw | PASS | PASS | PASS | **PASS** |
| RW4, RW5 | PASS | FAIL | PASS | **PASS** |
| RW6 | FAIL | FAIL | FAIL | **FAIL** |
| RW7 | WARN | FAIL | FAIL | **WARN** |
| RW-TRIPWIRE | PASS | **FAIL** | PASS | **PASS** |
| **ISR-final** | PASS | PASS | FAIL | **FAIL** ← catches it |
| **X-3** | PASS | PASS | WARN | **WARN** ← catches it, WARN only |

`shuffle-strat` permutes the retail block **within (cycle × day-type × province)**, 105 cells —
marginal drift **0.000e+00**, 40.6 % of rows changed. **All 10 RW/RETM gates are blind to it.** The
named retail battery measures **marginals, not skill**. The only two gates that fire are **not retail
gates**.

**And RW1/RW2 are byte-identical even on the all-zeros pool** — they read
`step4_training_log.csv` (`pr_auc` 0.519045, `f1` 0.37941), which no pool edit reaches. **B-3's wiring
claim is confirmed exactly; its literal "a dead head passes" form is refuted, because the tripwire
does catch all-zeros.**

**Method note worth keeping:** my *global* shuffle was a bad falsifier — it also destroyed the
day-type and province conditioning RW6/RW7 legitimately read, so it moved 7 lines I had predicted
would not move. **A perturbation that changes more than one thing cannot attribute what it breaks.**

**Owed:** relabel RW1/RW2 in the report text as teacher-forced log reads; add the stratified-shuffle
null as a real person-level gate; decide whether `X-3` should FAIL rather than WARN. **No threshold
was moved.**

---

## 4. What to do next

**🔄 IN PROGRESS — V2-E4, and it needs YOU, not more of my time**

| ID | What it is | The two things to weigh |
|---|---|---|
| **V2-E4** | Validator across seeds 0–4; publish mean ± sd | **(1)** 🔴 **Speed is NOT down** — it is reachable, but saturated by **your own** arrays 1172484 / 1172485, ~670 tasks pending at `AssocGrpCpuLimit`. Submitting behind that is an allocation call, so nothing was submitted while you were out. **(2)** E1 just found the **previous run's checkpoint was never preserved** — worth fixing artefact retention *before* spending five more training runs. E4 also supplies the independent-seed control **V2-E2** needs for Head-2 drift. |

**⛔ BLOCKED, and by what**

| ID | Waiting on |
|---|---|
| **V2-E5** | WP-C + WP-D landing first (it re-scores them) |
| **V2-G1** | WP-E finishing |
| **V2-G2** | WP-C finishing |
| **V2-G5** | everything above — including the vacuous-gate renumbering, now with **3 new classes** from tonight |

**✋ Waiting on the user: the V2-E4 submission decision above. That is the only one.**

---

## 5. Traps this project has already fallen into

Read these before writing a guard. Each cost real time.

1. **The gate whose reference comes from the source it audits.** The `PLATFORM` guard read a value
   inherited wholesale from the arm it was checking. It was accidentally correct on Speed and only
   visible as wrong on a second OS. Every pre-08-04 arm still carries arm H's execution stamp.
2. **The gate declared but never coded.** 53.5 % of site energy was read as zero.
3. **The gate whose count is stable while its membership turns over.** `S9-EUI-hotel` read 28/56 in
   both arms — a *different* 28.
4. **The verifier that under-counts.** Worse than one that over-counts: it condemns correct output
   and invites you to "fix" what was never broken. D9's diff verifier did this and was caught.
5. **The silent reader.** A parser returning 0.0 for what it cannot parse blames the system for its
   own gap.
6. **Two copies of a band.** D9's scorer carried its own retail band (80/140, all-cells) while the
   shipped band is 80/155 with a median rule. It now **imports `BENCH` from the gate module.**
7. **Two definitions of "channel energy".** `agg_annual.csv` (9 end uses) and `channel_hourly.csv`
   (5 columns) differ by **26.5 %** on the same cell. The gate uses the aggregator. Anything scored
   on the other basis answers a question no gate asks.
8. **An area from the wrong geometry.** `Tall` retail is **3,158.98 m²**; `SuperTall` is
   **4,738.47 m²**. They differ by exactly 1.5×, which makes a mix-up look plausible.
9. **The gate that reads a training log, not the artefact it claims to score.** RW1/RW2 are
   byte-identical on a pool whose retail channel is entirely zero. Nothing you do to the output can
   move them.
10. **The gate blind to a permutation of its own subject.** All 10 RW/RETM gates report identically
    when retail vectors are randomly reassigned among people within their own cell. Marginals, not
    skill. **Ask of any gate: what would a shuffled input do to it?**
11. **A falsifier that perturbs more than one thing.** My global shuffle destroyed person-level
    association *and* the day-type/province conditioning, so the gates it moved could not be
    attributed. Stratify the perturbation to the single factor you mean to test.
12. **A control with no variance in the dimension you are dividing by.** V2-E2's within-leg control
    differs on **1 key in 64,061** for AT_WORK (κ = 1.0000); a cross/within ratio there yields a
    meaningless 13,881×. Check the control moves before quoting a ratio against it.

---

## 6. Artefacts you will need

| what | where |
|---|---|
| the plan / task list | `improvements/v2/3rdJ_L3_v2_implementation.md` |
| the audit (13 findings) | `improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md` |
| the board | `scratchpad/v2board.html` → the Artifact URL in §0 |
| Step-9 gate + bands | `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` (`BENCH`) |
| §8E aggregator | `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` (`--idf-name`, `--jobs`) |
| per-cell runner | `Leg3_4-split/Step9_docs/3rdJ_09H_resize_campaign_cell.py` |
| DHW resize tooling | `3rdJ_09H_{dhw_plant_topology,resize_spec_check,laundry_slope,peak_draw_sizing}.py` |
| D9 converter + scorer | `3rdJ_09J_retail_necb_c.py`, `3rdJ_09J_necb_c_score.py` |
| NECB schedule evidence | `improvements/v2/f8_necb_schedule_evidence/sched_NECB2011.json` |
| local arm outputs | `_local_armH_cells/`, `_local_K16/{K1,K6,agg_K1,agg_K6}/`, `_local_D9_necbC/` |
