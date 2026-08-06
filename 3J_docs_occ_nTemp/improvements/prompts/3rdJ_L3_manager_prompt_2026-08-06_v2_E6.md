> 🔴 **SUPERSEDED 2026-08-06 by `3rdJ_L3_manager_prompt_2026-08-06_v2_close.md`.** Kept intact, per the archive-predecessor rule.
> Its state section is stale in one respect: the **four tasks it lists as blocked on compute (V2-E5, V2-G1,
> V2-G2, V2-G5) all CLOSED overnight on local win32**, 2026-08-05 21:55 → 2026-08-06 00:05. The project is now
> **46 done / 1 decision / 0 blocked of 47**. Its §4 (the V2-E6 decision) and its traps list remain correct.

---

# Manager prompt — 3J Leg-3 **v2 finalisation**, 2026-08-06 (LIVING HANDOFF)

> **You are the manager (Agent1).** You plan, debug, and write the prompts that spawn employee
> sessions. You do not normally execute multi-step implementation yourself.
>
> **Predecessor:** `3rdJ_L3_manager_prompt_2026-08-05_v2_close.md` — superseded by this file. Read it
> only for the detail of tasks closed on 08-05 (§3, §3b, §3c, §3d); everything still live is here.

---

## 0. Read this first

The project is a **decision-and-writing** problem, not a simulation problem. The plan is a document:

**`improvements/v2/3rdJ_L3_v2_implementation.md`** — 47 tasks, 7 work packages, ToC, traceability
matrix, Progress Log. **It is your task list. Read its `WHERE WE ARE RIGHT NOW` block first** — not
the summary table, which is an index, not a state.

Its investigation counterpart is
**`improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md`** (13 findings B-1…B-13 with
falsifiers). The audit says what is wrong and how to prove it; the plan says what to change and how
you will know it worked. **Both stay. Do not merge them.**

**The board.** `scratchpad/v2board.html`, published at
**`https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213`**.
🔴 **Editing the local HTML is not the update — republishing the Artifact is, and you must pass that
exact URL so the link never changes.** The user has asked for this explicitly, more than once.

---

## 1. Standing conventions — these are not suggestions

**🔴🔴 THE CLUSTER: THE FIRST RULE IS THAT YOU DO NOT USE IT.** The user's standing instruction,
restated firmly on 2026-08-05 after it was violated twice in one session: **Speed is NOT available.
Stay local. Use local CPU.** No `ssh`, no `scp`, no `sbatch`, no `squeue` — not even a "cheap" `ls`.
**An `ssh` that answers is not availability**; the user decides that, and you do not re-derive it from
a successful connection. If a task appears to need the cluster, do the local part and **say plainly
what could not be done** — never work around it, never "just check".
*If and only if the user re-opens Speed:* `sbatch` only, never a blocking `srun`, never bare `python`
on the login node, always `-t 7-00:00:00`, single-line, labelled "locally" or "on the cluster".

**🔴 THE THREE-ARTEFACT CLOSURE RITUAL.** The user's standing instruction, 2026-08-05: **the moment a
task completes, update all three in the same response, unprompted** —
1. the **Progress Log** in the plan, *and promote the successor into the NOW panel*;
2. the **directeur prompt** for the next session (this file, or its successor);
3. the **board HTML**, *republished at the fixed URL above*.
Plus **memory**. Updating two of three is the failure mode that has already happened.

**Pre-register predictions before looking at numbers.** Write them to a file first, score them after,
and **report failures as results**. Every substantial task on this project since 08-03 has done this,
and the predictions that failed have been the most informative part of the output.

**🚫 Never widen a band to erase a FAIL.** This is absolute. If a gate fails, either fix the thing or
document the failure — you do not move the bar. *(V2-E6 below has an explicit, recorded refusal of
exactly this move; do not let a later session "tidy it up".)*

**Never re-tune a parameter on the gate that selected it.** V2-E4c established that Step-5's
`MIN_POOL` was chosen on a gate crossing smaller than its own noise. **The response is not to pick a
better value with better statistics** — that is the same defect performed more carefully. Report the
band.

**Other house rules.** A citation is not evidence until opened. Corrections are **struck, not
deleted** (`~~like this~~`). Verify a backup is non-empty **in the same command** before overwriting
(`[ -s "$BK" ]`). **Never count lines with PowerShell `Measure-Object -Line`** — it miscounts; use
`wc -l`. Do not append to the Progress Log with `Add-Content`; write a scratchpad file and `cat >>`.
Reply in English even though the user writes French. Keep replies short unless detail is asked for.

---

## 2. Where the work stands

**42 of 47 done · 0 in progress · 1 user decision (V2-E6) · 4 blocked.** *(Plan and board verified
programmatically against the summary table — they agree.)*

~~**Every decision in the project is taken** and the desk-work critical path is closed.~~ 🔴 **Struck
2026-08-05: it is no longer true.** The desk-work path is closed, but **a decision is owed on V2-E6**
(§4) and it is the most consequential one open. Six tasks closed on 2026-08-05: **D10, D9, E2, E1,
E4, E4c**. A seventh, **E6**, was opened, implemented and **reverted** the same night; it is now a
**user decision**, not a task.

> 🔴 **A correction worth carrying, because it is a pattern and not an accident.** Late on 08-05 the
> plan said *"every task that can be done without the cluster is now done."* Forty minutes later the
> user asked one question — *does R1's failure have a solution?* — and the answer produced a diagnosis,
> a new task and four findings. **"No work left" meant "no question asked."**
>
> 🔴🔴 **And then the opposite failure, one hour later.** That new task (V2-E6) was implemented, run,
> verified — **and reverted.** The change was **already decided against on 2026-07-21**, in the Step-5
> closure entry, on the grounds that *"redefining a gate to clear a FAIL immediately before publication
> reads as gate-shopping"*. I had opened the task off my own diagnosis **without reading the validator
> doc — the primary record for the gate I was changing.** See §4. **Both lessons are the same lesson:
> the document you did not open is the one that decides whether your work is new or already refused.**

**The four blocked tasks** — V2-E5 (re-score after WP-B/WP-D), V2-G1 (freeze the deliverable),
V2-G2 (flip PLANNED → DONE), V2-G5 (close the audit) — are blocked on **WP-C / WP-D / WP-E compute**.
None is blocked on desk work, a decision, or anything local.

**✋ Owed by the user — three decisions, the first of which gates a paper caveat:**
- 🔴 **V2-E6 / gate R1** (§4). **A** leave it · **B** redefine it (reverses a 2026-07-21 decision — not
  recommended) · **C, recommended** keep R1 failing and *add* a retail generation-fidelity gate.
  **Nothing in Step 5 changes until this is answered**, and the paper caveat text should be upgraded
  either way (finding 1 in §4 is clearer than the caveat currently on file).
- **The `val_score` decision** (from V2-E4): the model checkpoint is selected by a composite the
  method document forbids in as many words. Fix the document to describe the code, or fix the code to
  match the document — the latter means a re-run. *Neither is urgent; the seeds are statistically
  indistinguishable.*
- Whether **X-3** should FAIL rather than WARN.

---

## 3. What closed on 2026-08-05, in one paragraph each

*(**V2-E6 is not here** — it did not close. It was implemented and reverted; see §4.)*

**V2-E4 — the selector the method document forbids.** `best_model.pt` is chosen by
`val_score = mean_js + 0.5·(home+work+retail)/3` (`3rdJ_04D_train_4split.py:499,881`) — a composite
containing **neither** `pr_auc` **nor** `f1`, while the doc (`:157`) mandates *"gate survivors →
argmax retail F1, **never a single composite score**"*. The docstring defers to a *"separate
checkpoint-selection step"* that **does not exist** (0 grep hits for `seed_0`/`range(5)`/`for SEED`).
The two rules disagree in **4 of 5 seeds**, costing **+0.0218 F1** (5.6 % rel). **Seed 3 is 4th/5 on
retail F1 and 1st/5 on `val_score`** — the retrospective rationale is *it was picked by the forbidden
composite*. Spread threatens **no** gate (margins 9.5/51/165 sd), so B-7 is a *reporting* omission at
gate level and a *selection* defect at checkpoint level. New vacuous class **#15**.
**Not answered:** W3/midday/transitions spread for seeds 0,1,2,4 — needs 4×418 MB pools that exist
only on Speed. **Transfer constraint, not compute. 5 of 8 metrics have their spread; 3 do not.**

**V2-E4c — the `MIN_POOL` sweep is a curve through one draw.** 26 local runs, ~20 min, 4P/2F. The
sweep moved off `MIN_POOL=10` on a **0.16 pp** crossing; across-seed sd of that statistic is
**0.363 pp — 2.27×** the margin. `MIN_POOL=10` exceeds the gate in **1 of 5 draws, and that one is the
shipped draw** (seed 42 is worst-of-five at `MIN_POOL` 10 *and* 11). **F(4,20) = 0.692** (crit 2.87),
**η² = 0.122**; within-level MS **0.143 > 0.099** between-level. **But `MIN_POOL=15` never fails** —
0/5, band [1.97, 2.41], **+0.59 pp** headroom, lowest mean and smallest sd in the grid. **B-2 splits:
upheld on procedure, refuted on consequence — nothing downstream is at risk.** New vacuous class
**#16** (*the sensitivity analysis with n=1 per level*). One code change is now in the tree:
`3rdJ_05_censusLinkage_4split.py:387` reads `STEP5_MATCH_SEED`, **default 42**, so every pre-08-05 run
reproduces byte-identically.

**§0.26 — R1 diagnosed.** See §4; it is the ready task.

---

## 4. V2-E6 — attempted, reverted, and now a USER DECISION

**Do not implement anything here until the user chooses.** Full record in plan **§0.27**.

### What happened

The re-specification of gate R1 (matched-vs-pool → synthetic-vs-observed, the basis its siblings use)
was written, run and verified: **R1 4.796 pp FAIL → 1.615 pp WARN, every other gate byte-identical.**
Then `Step5_docs/3rdJ_05_censusLinkage_4split_val.md` was opened and it contains, from the Step-5
**CLOSURE** entry of 2026-07-21:

> **"R1 reference NOT redefined (decision (b)): although the reweighted reference is arguably the more
> correct comparison, redefining a gate to clear a FAIL immediately before publication reads as
> gate-shopping and weakens the audit's credibility. The FAIL stays visible."**

**Reverted.** Validator restored from `archive/3rdJ_05_censusLinkage_4split_val.2026-08-05_pre_r1respec.py`,
md5 `46b0eb222f88f802e149647c82c1b726`, **zero diff on all 49 gate lines**, scorecard back to
**31 PASS / 5 WARN / 3 FAIL**. Step-5 outputs were never touched.

**July had also gone further than §0.26 did:** the mechanism, a bootstrap null (P(max ≥ 3.0) ≤ 0.012
in all 12 groups), and the re-weighted reference *actually computed* — all 12 groups collapse below
3 pp, 2005-d2 going **4.796 → 2.268**. That is §0.26's "option 2", already run and already declined.

### What survives the revert — genuinely new, and none of it changes a gate

1. **The cross-channel test.** R1's own statistic on the two channels whose gates **pass**: `hom30`
   **22.969 pp**, `wrk30` **27.263 pp**, vs retail's 4.796. **That basis condemns all three.** Simpler
   and stronger than July's re-weighting argument — **it should replace the paper caveat text.**
2. **Retail is still the worst channel.** Normalised by own peak (95.02 / 46.92 / **4.57 %**):
   24.2 % / 58.1 % / **105.1 %**. Retail's gap exceeds its whole signal. **Carry both halves.**
3. **The bar is not comparable across channels.** An absolute 3.0 pp is **3 %** of `hom30`'s signal
   and **66 %** of retail's.
4. **Retail generation fidelity is unmeasured.** No gate asks retail the sibling question. The number
   is **1.615 pp = 35.3 %** of its peak, vs 3.9 % / 4.4 % for its siblings — **~8× worse.** Real gap.
5. **Two latent validator defects.** `self.results` is `{"pass","fail","warn"}` (`:220`) so any
   `_rec("info", …)` raises `KeyError`; and the summary renderer (`:1271`) falls through to `[FAIL]`
   for unrecognised statuses — an INFO row printed as a failure. **Not fixed** (out of scope after the
   revert); recorded so the next attempt does not re-find them.

### 🔴 The decision to put to the user

- **A — leave it.** R1 stays FAIL/documented; upgrade the paper caveat to use finding 1.
- **B — redefine R1.** Reverses the 2026-07-21 decision. **Not recommended.**
- **C — RECOMMENDED. Keep R1 untouched and ADD a new gate** (`R5`, retail generation fidelity,
  1.615 pp). **Purely additive: clears no FAIL, reverses no decision, closes the real gap.** Scorecard
  gains a WARN rather than losing a FAIL.

**Pre-registration scored honestly** (`scratchpad/e6_prereg.md`): **P1, P5, P6 PASS; P2, P4 FAIL.**
P4 predicted the re-specified gate would be vacuous-because-green; it would **not** have been
(headroom 0.9× the observed value — it keeps real power). **The change was better than I predicted,
which is exactly why adopting it quietly would have been worse.**

---

## 5. Traps this project has already fallen into

Read these before writing a guard. Each cost real time.

1. **The gate whose reference comes from the source it audits.** The `PLATFORM` guard read a value
   inherited wholesale from the arm it was checking — accidentally correct on Speed, visible as wrong
   only on a second OS. **R1 is the same defect at the other end of the pipeline** (§4).
2. **The gate declared but never coded.** 53.5 % of site energy read as zero.
3. **The gate whose count is stable while its membership turns over.** `S9-EUI-hotel` read 28/56 in
   both arms — a *different* 28.
4. **The verifier that under-counts.** Worse than one that over-counts: it condemns correct output and
   invites you to "fix" what was never broken.
5. **The silent reader.** A parser returning 0.0 for what it cannot parse blames the system for its own
   gap. *(E4c's sweep parser refuses instead — it returns `PARSE_FAIL_<k>`.)*
6. **Two copies of a band.** D9's scorer carried its own retail band while the shipped band differed.
7. **Two definitions of "channel energy"** differing by 26.5 % on the same cell.
8. **An area from the wrong geometry.** `Tall` retail 3,158.98 m² vs `SuperTall` 4,738.47 m² — exactly
   1.5×, which makes a mix-up look plausible.
9. **The gate that reads a training log, not the artefact it claims to score.**
10. **The gate blind to a permutation of its own subject.** All 10 RW/RETM gates report identically
    under a person-level shuffle. **Ask of any gate: what would a shuffled input do to it?**
11. **A falsifier that perturbs more than one thing.** Stratify to the single factor you mean to test.
12. **A control with no variance in the dimension you are dividing by.**
13. **The sweep with one draw per level.** The `MIN_POOL` curve was read as structure when its
    step-to-step differences (0.16 pp, and 0.01 pp between two levels) were smaller than the scatter
    from re-running a single point (0.363 pp). **Before believing a swept curve, ask what one point
    would do if you re-ran it.**
14. **The absolute bar on channels of different size.** 3.0 pp is 3 % of `hom30`'s signal and 66 % of
    `ret30`'s. **A shared threshold is not a shared standard.**
15. 🔴 **Proposing a change without reading the primary record for the thing you are changing.** V2-E6
    re-specified gate R1 and turned its FAIL into a WARN — a change **already refused by a recorded
    manager decision** in the very document that defines the gate. The diagnosis that licensed it was
    also not new. **Before opening a task against any gate, read that gate's own doc and its closure
    entry.** A citation is not evidence until opened — and neither is a gate's history.
16. 🔴 **After a revert, re-read the prose — not just the counts.** V2-E6's revert restored the code
    perfectly and every programmatic check passed (table vs panel, row counts, no duplicates) because
    those checks read the *status column*. Meanwhile the manager prompt still said *"every decision in
    the project is taken"* and the board headline still said *"nothing is waiting on you"* — both
    false, both left by the revert. **A count-agreement check cannot fail on a false English
    sentence.** (§0.28.)

---

## 6. Artefacts you will need

| what | where |
|---|---|
| the plan / task list | `improvements/v2/3rdJ_L3_v2_implementation.md` |
| the audit (13 findings) | `improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md` |
| the board | `scratchpad/v2board.html` → the Artifact URL in §0 |
| **Step-5 linkage + validator** | `Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split{,_val}.py` (`STEP5_MIN_POOL`, `STEP5_MATCH_SEED`) |
| Step-4 trainer (the `val_score` finding) | `Leg3_4-split/Step4_docs/3rdJ_04D_train_4split.py:499,881` |
| Step-9 gate + bands | `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` (`BENCH`) |
| §8E aggregator | `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` (`--idf-name`, `--jobs`) |
| per-cell runner | `Leg3_4-split/Step9_docs/3rdJ_09H_resize_campaign_cell.py` |
| DHW resize tooling | `3rdJ_09H_{dhw_plant_topology,resize_spec_check,laundry_slope,peak_draw_sizing}.py` |
| D9 converter + scorer | `3rdJ_09J_retail_necb_c.py`, `3rdJ_09J_necb_c_score.py` |
| NECB schedule evidence | `improvements/v2/f8_necb_schedule_evidence/sched_NECB2011.json` |
