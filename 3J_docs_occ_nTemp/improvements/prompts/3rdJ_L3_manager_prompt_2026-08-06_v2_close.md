# 3J Leg-3 — manager handoff, 2026-08-06

> 🔴 **SUPERSEDED 2026-08-06 by `3rdJ_L3_manager_prompt_2026-08-06_v2_optionC.md`.**
> This prompt is accurate except in one respect: it reports **one decision outstanding (V2-E6)**.
> **The user answered it on 2026-08-06 and chose option C** — R1 keeps its FAIL, and a new gate
> **R5** (retail generation fidelity, 1.615 pp) is *added* beside it. That created three ready tasks
> (**V2-E7 → V2-E6 → V2-E8**, in that order) and took the board to **46 done / 3 ready / 0 decisions
> of 49**. See plan **§0.33**. Everything this prompt says about the four tasks closed overnight stands.

**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v2_E6.md`.** That prompt was written before the
overnight session; its state section is stale in one respect only — the four tasks it lists as
blocked on compute are **closed**.

---

## 0. Read first, in this order

1. **`improvements/v2/3rdJ_L3_v2_implementation.md`** — the plan. **5,512 lines.** Go to the status
   panel (§ near line 175), then the Progress Log entries **§0.29 – §0.32** at the end. Those four
   entries are the whole of last night.
2. **`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`** — what the paper reports, and its provenance.
3. **`improvements/v2/V2-E5_PREREGISTRATION.md`** — the predictions, written *before* the arm was
   built. Read this **before** §0.31 if you want to judge the scoring honestly.
4. The board: <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>

🔴 **And the rule that cost the most this week:** before proposing any change to a gate or a
threshold, **open that gate's own step document and its closure entry first.** On 2026-08-05 I
implemented an R1 re-specification that a **2026-07-21 manager decision had explicitly refused as
gate-shopping**, and had to revert it. See `feedback_read_the_gates_own_doc` and §0.27.

---

## 1. Standing conventions — unchanged, and none of them were relaxed

- 🔴 **Speed is NOT available.** No `ssh`, `scp`, `sbatch`, `squeue` — not even a cheap `ls`.
  Reachability ≠ availability; the **user** decides availability. Everything below ran on local
  win32. If a task needs the cluster, do the local part and say what could not be done.
- 🔴 **Never widen a band, move a threshold or re-specify a gate to erase a FAIL.** The mirror also
  holds (V2-D9): **a correct input is never withheld because it deepens one.**
- **Pre-register predictions, with numbers, before the run.** Then score them without amendment.
- **A gate must be seen failing** on a deliberately broken input before it is trusted. Applies to
  your own checkers — see §3, where a falsifier was caught not falsifying.
- **Struck, not deleted.** Corrections are `~~strikethrough~~` plus the correction.
- **A citation is not evidence until it has been opened.**
- Verify a backup is non-empty **in the same command** (`[ -s "$BK" ]`). Never count lines with
  PowerShell `Measure-Object -Line` — use `wc -l`. Don't append to the Progress Log with
  `Add-Content`; write a scratchpad file and `cat >>`.
- **The three-artefact closure ritual**, every completed task, same response, unprompted: Progress
  Log + successor promoted · this prompt · the board **republished at its fixed URL**. Plus memory.

---

## 2. Where the project stands

**46 done · 0 in progress · 1 decision · 0 blocked · 47 total.**

**Nothing is blocked. Nothing is waiting on the cluster. One thing is waiting on the user.**

The plan's summary table, status panel and ASCII bar chart are checked against each other by
`scratchpad/verify_plan_final.py` — **5 PASS / 0 FAIL**. It parses all three rather than hard-coding
the counts, so it keeps working as they change. (Its predecessor hard-coded "42 … 47" and would have
had to be hand-edited, which is a checker that has stopped checking.)

---

## 3. What closed overnight, 2026-08-05 21:55 → 2026-08-06 00:05

All four on **local win32**. Speed never touched.

### V2-G2 — the master docs said "PLANNED" about work that shipped months ago (§0.29, 3P/0F)

**22 tags** across both master documents, each now **naming the artefact that proves it**, because
`PLANNED` → `DONE` on its own swaps one unfalsifiable claim for another. New
`improvements/v2/g2_status_tag_check.py` stats every named path; **falsifier seen failing 3/3**.

🔴 **Its first real run failed twice and only one was the document's fault.** One "missing" file
**exists** — in `Leg2_2-split/`, and my checker walked only the Leg-3 tree. *A checker that cannot
see half the repository reports true statements as false.* The other failure was real, and **the
document was changed to satisfy the check rather than the check loosened to excuse the document.**

### V2-G5 — the audit closed (§0.30, 4P/0F)

**24/24 terminal statuses**: **12 FIXED** (each naming its task), **8 ACCEPTED-AS-DOCUMENTED**
(true, unrepaired, and that is a *decision* — each names where the limitation is written),
**4 WITHDRAWN** (each names its falsifier). B/C/G **never merged** — `C-4 ≡ B-3` and `G-1 ≡ B-8` stay
separate rows because *found twice, blind* is the evidence.

🔴 **The falsifier did not falsify, and running it is what showed that.** It dropped `B-9` and then
re-added it with a bad status, so the "is anything missing?" check still saw a `B-9` row and
**passed**. It was two minutes from being recorded as 4/4. **A falsifier that cannot fail is the same
defect as a gate that cannot fail.**

**Catalogue reconciled to 16 classes** across four documents; 1–12 unchanged; the `#13` collision
settled (severity-vacuous = **#14**; #15 selection-never-implemented; #16 sensitivity-with-n=1).

### V2-E5 — the deliverable arm, scored (§0.31, 7P/3F) 🔴 read this one properly

56/56 cells, **126 minutes**, 0 failures. Deliverable = base + **V2-D9** (retail `NECB-C`) +
**V2-D10** (`Laundry Service Water Use 30.6gpm 180F=8.5`, every other burner K = 1).
Attribution residual **0.000000 %** on every cell. **Scorecard 17P/0W/3F/10I — identical counts to
base.**

> **The base arm had to be re-scored to say that.** The scorecard on file was **31 July**, predating
> V2-D1/D2/D4/D6, all of which changed gate code. Diffing against it would have credited *scorer*
> changes to the *arm*.

**🔴 THE RESULT — vacuous-gate class #12 fired, pre-registered.** `S9-EUI-hotel` reads **28/56 in
both arms**, and **all 28 turned over**: base **28 below** the floor / 0 above → deliverable **0
below / 28 ABOVE** the ceiling, median **178.29 → 260.54**. *The failing end inverted while the count
held still.* Second time this same gate has done it — the first is what created class #12.

**🔴 And the scorer discloses the verdict rests on a rule choice:** under the `median` rule (adopted
for retail by V2-B3) the hotel gate would **PASS**. **Not proposed — recorded.** Choosing the rule
after seeing which one passes is exactly what §0.27 reverted. The honest reading runs against us:
half the cells now overshoot the ceiling.

**Also:** hotel DHW **+120.09 %** (predicted +112). **All three blocking gates still FAIL** — the
prediction that keeps this from being another gate-chasing arm. **0 gates changed status.**

**Three predictions failed, and two for one reason: the per-object resize is NOT channel-confined.**
Residential DHW **−2.76 %**, office −0.66 %, retail −0.27 % — the pinned burner was being
**cross-subsidised** by its neighbours on the loop. Reported, **not scored**: inventing a criterion
after seeing the number is how a test gets built to pass. **Pre-register it properly next time.**

**P6 could not be run, and it is my defect.** It was the surgical-edit control. The base IDF never
requests `Water Use Equipment Total Volume`, so there is no reference and none is recoverable from
the base SQL either. **N/A with the reason, not quietly replaced.** `C2′` was run instead — it was
pre-registered in the campaign header, not invented afterwards — **56/56**, exactly one burner ×8.5,
held burners drift `6.139e-11`.

### V2-G1 — frozen (§0.32)

`V2-G1_FROZEN_DELIVERABLE.md`, 88 lines. **No SLURM ids, and the absence is stated** — a placeholder
job id would be a fabricated provenance field. **Test method executed:** hotel EUI median
**re-derived from the artefact's own columns = 260.5411** against the scorer's independent 260.5.
Surfaced a real difference: `OUTPUT_SCHEMA_HASH` **`db4e729f` → `93dd5129`** (two extra per-cell
tables). Predecessor intact, pointer moved; **847 MB kept**, 23 GB of regenerable `run/` output not.

### Also cleared

The RW1/RW2 relabel owed from V2-E1: `3rdJ_04_augmentationGSS_4split_val.md` now states on the gate
rows themselves that both are **teacher-forced reads of `step4_training_log.csv`**, that they are
byte-identical on an all-zeros pool, and that all 10 RW/RETM gates are blind to a within-cell person
shuffle.

---

## 4. ✋ Owed by the user — three decisions, unchanged by last night

1. 🔴 **V2-E6 / gate R1** (§0.27). **A** leave it (upgrade the paper caveat to the cross-channel
   demonstration) · **B** redefine it — *reverses the 2026-07-21 decision, not recommended* ·
   **C, recommended** keep R1 failing and **ADD** a retail generation-fidelity gate (1.615 pp,
   ~8× worse than its siblings as a share of channel peak). Purely additive: clears no FAIL,
   reverses no decision. **Nothing in Step 5 changes until this is answered.**
2. **The `val_score` selection rule** (V2-E4): the checkpoint is selected by a composite the method
   document forbids in as many words. Fix the document to describe the code, or the code to match
   the document — the latter means a re-run. *Not urgent; the five seeds are statistically
   indistinguishable.*
3. Whether **X-3** should FAIL rather than WARN.

**A fourth is now worth raising, and it is not mine to take either:** the hotel gate's verdict
depends on the `all_cells`-vs-`median` rule choice (§0.31). **Do not resolve it by picking the rule
that passes.** If it is revisited at all, it should be on the same grounds V2-B3 used for retail —
*whether the spread is smaller than its own uncertainty* — decided against a written argument, not
against this arm's result.

---

## 5. Remaining work, such as it is

Nothing is blocked and nothing needs the cluster. What is left is genuinely optional:

- **Promote the stratified-shuffle null into a real person-level gate** (owed from V2-E1/B-3). The
  perturbation harness exists (`_e1_perturb.py`); no gate reads it yet. This is the one substantive
  code item still outstanding, and it was deliberately **not** done last night — adding a gate to a
  just-frozen deliverable is the user's call.
- **Two latent validator defects**, recorded and not fixed: `_rec("info", …)` raises `KeyError`
  (`3rdJ_05_censusLinkage_4split_val.py:220` lacks the bucket) and the summary renderer falls
  through to `[FAIL]` for any unrecognised status (`:1271`). Neither fires today; both would the
  moment an INFO row is added — which is what recommendation **C** in §4 would do.
- **`LargeHotel Retail` is never injected** (owed from V2-D9) — 368 m², 11.7 % of the `Tall` retail
  channel, still on a stock NECB schedule. A Step-7 injector change, out of scope where it was found.
- The paper itself: V2-G3's 16 limitations are written; §0.31's cross-channel finding and the
  class-#12 event should both reach it.

---

## 6. Artefacts

| what | where |
|---|---|
| plan (5,512 lines) | `improvements/v2/3rdJ_L3_v2_implementation.md` |
| frozen deliverable | `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` |
| pre-registration | `improvements/v2/V2-E5_PREREGISTRATION.md` |
| deliverable cells (847 MB) | `Leg3_4-split/Step8_docs/campaign_local_deliverable/` |
| deliverable aggregate | `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/` |
| deliverable scorecard | `Leg3_4-split/Step9_docs/outputs_step9_deliverable/` |
| base arm (untouched) | `campaign_local_v2/campaign_cf69d508/`, `outputs_step8/agg/`, `outputs_step9/` |
| audit + closure (2,447 lines) | `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md` |
| checkers | `improvements/v2/g2_status_tag_check.py`, `g5_audit_closure_check.py`, `g3_limitations_check.py` |
| backups | `improvements/v2/v2plan_backup_pre_{g2g5,e5g1}.md`, `audit_preG5.md`, `READER_GUIDE_preG5.md`, `3rdJ_00_4split_Occupancy_Pipeline{,_Overview}_preG2.md` |

---

## 7. The traps, in the order they have actually bitten

1. A logged number is not evidence — re-derive from the artefact's own columns.
2. A citation is not evidence until opened. Five external rounds contained fabricated numbers.
3. A gate that cannot fail tells you nothing. **16 catalogued classes.**
4. Check **membership**, not just counts (class #12) — **it fired again last night**.
5. Read the **untreated control** before blaming the model.
6. **Silence** — a reader returning 0.0 for what it cannot parse describes its own gap. It has now
   caught me twice: the "missing" checkpoint, and the "missing" Leg-2 document.
7. Never widen a band to erase a FAIL — **and never withhold a correct input because it deepens one.**
8. A basis change that turns FAIL into WARN is a band change in disguise.
9. Don't rank warnings by frequency — the fatal lines appear once each.
10. Verify a backup is non-empty in the same command.
11. `Measure-Object -Line` counts blank lines as zero. Use `wc -l`.
12. A perturbation that changes more than one thing cannot attribute what it breaks.
13. Re-selecting on the same gate with better statistics is still selecting on that gate.
14. **Read the gate's own document before proposing to change it.**
15. **After a revert, re-read the prose, not just the counts.** A count-agreement check cannot fail
    on a false English sentence.
16. **Your own falsifier can fail to falsify.** Each mutation must break exactly one check — §0.30.
17. **Re-score the baseline with the current code before diffing against it.** An old scorecard
    turns your code changes into apparent data changes — §0.31.
18. **Don't assume an intervention is confined to the channel it targets.** The hotel-loop resize
    moved residential, office and retail DHW — §0.31.
