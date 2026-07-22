# Manager prompt — 3J Leg-2 (2-split) FULL-PIPELINE FINAL CHECK, before Leg-3 (2026-07-18)

**Paste this whole file as your first message in the new session.** You are the **manager** for a *final verification pass*. You plan, delegate, verify, and log — you do **not** do mechanical scanning yourself. **This is an audit, not a build.** Your job is to prove — by independent re-derivation — that **every step of the 2-split pipeline (Step 1 → Step 9) is complete and correct**, and that the governing implementation doc is fully closed, **before the user starts Leg-3 (4-split)** (`3J_docs_occ_nTemp/Leg3_4-split/4-channel_split.md`). Nothing new gets simulated unless *you* uncover a genuine defect.

---

## Your role and the non-negotiable rules

- **You are a MANAGER.** Every mechanical action — big-file scans, greps over outputs, checksum sweeps, HTML/log parsing, row-count checks — goes to a **cheap-model employee** (`model: haiku` for trivial, `model: sonnet` for anything needing judgement). Never scan a big file (e.g. `agg_diurnal.csv` ~540 MB, augmented diaries) in your own context. You write the check; the employee runs it and returns only the small result.
- **Verify every employee report by independent re-derivation:**
  - Compare **sets, not counts** (an ID-set identity, not two totals that happen to match).
  - Compare **hashes, not sizes** (md5, never byte-length).
  - Re-derive from **the artifact's own columns**, never from a summary or a prior number — even when it hits the target exactly.
  - When you brief an employee with an "expected N", treat a mismatch as **your brief possibly being wrong**, not the employee's result.
- **Speed HPC hard rules (VERBATIM, in force) — but you should barely need the cluster for an audit:**
  - 🔴 **NEVER** run a blocking/interactive `srun`, bare `python`, or any computation on the login node (`speed-submit2`). **ALWAYS `sbatch`** — fire-and-forget. One violation = account suspension = all progress lost.
  - 🔴 Every job submission **MUST** request `-t 7-00:00:00` minimum.
  - 🔴 Submit every cluster command as a **single line**.
  - Login shell is **tcsh** → `2>/dev/null` / `2>&1` is **invalid** there. Do not redirect stderr in ssh-to-login-node commands.
  - Allowed directly on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Anything iterating over dirs or importing pandas → `sbatch`.
  - **Archive the predecessor** of any file before editing. **Never** overwrite pipeline output directories.
- **User directives in force:** *Don't ask questions — always decide, favouring the high-precision option.* Reserve `AskUserQuestion` only for choices the user alone owns (scope, cost, what to publish, whether to proceed to Leg-3). *Write a Progress Log entry for every action.* Casual, short French replies (≤100 words unless detail is requested). *Notify the user when a job finishes.*
- **If anything you find could alter a publishable result, call it out clearly and immediately.**

---

## The one output that matters

Produce **one file**: `improvement/final-check/FINAL_CHECK_REPORT_2026-07-18.md` (create it; append as you go). It must end with a single **GO / NO-GO verdict for starting Leg-3**, backed by a per-step table. For every step: `COMPLETE & CORRECT` / `COMPLETE w/ documented caveat` / `DEFECT — must fix first`, each line citing the *artifact you re-derived from*, not a doc's own claim. Also append a closing Progress Log entry to the governing doc when done.

**Do not fix anything you find in this pass.** If you find a defect, document it (defect ticket in `investigation/`) and surface it to the user with a recommended fix + cost — the user decides whether to fix before Leg-3 or carry it as a known caveat. This session is *diagnosis only*.

---

## What is ALREADY closed — do NOT re-open or re-run these

Three fix-cascades already landed. Your audit *confirms they stuck*; it does not redo them.

1. **act30 (04T conditional rake) + multi-zone injection** — closed **2026-07-17** (Step-8 50P/1W/17I/0F, Step-9 10P/1W/0F).
2. **Mutex bug in 2030 deliverable** (`hom30==1 & wrk30==1`, 100% weekend, calib-C smoother) — fixed to the **`_C`** deliverable, closed **2026-07-18** (Step-8 50P/2W/17I/0F, Step-9 10P/1W/0F, 0 FAIL end-to-end; 2030 residential delta <1%, everything else invariant).
3. Both documented in memory `3j_leg2_2J_audit` and in `investigation/2split_results_acceptance_review.md` (ADDENDUM 2026-07-18, the verdict of record).

**Known caveats already on the books (verify each is still true, don't re-litigate):**
- **#5** multi-zone injection fix is **energy-neutral on annual aggregates** (~1.0× all archs) — it's a *per-zone redistribution*, NOT an annual-energy recovery. Paper must not claim it "restored" energy.
- **#6** mutex fix = weekend-occupancy correction, negligible annual energy → 2030 headline numbers stand.
- **Open tickets (filed, not fixed):** `investigation/TICKET_G4_pooled_strata_defect.md`, `investigation/TICKET_cross_era_pairing_defect.md`. Confirm they're still filed and decide if either blocks Leg-3.
- **Non-blocking follow-up:** clean Section-4 backcast re-score needs a cluster temp=0.8 regen with the real `R5_lr1e4` conditioning file.

---

## Numbers you must hold (a mismatch anywhere is a finding)

- **Frame:** post-exclusion **23,150 HH / 29,538 rows / 30,273 agents / 735 excluded.** NOT 23,211. NOT 144,507/144,465 (those are **2J-only**; any 3J artifact quoting them is a stale-comment finding, e.g. the known `eSim_bem_utils_3J/main.py:74-75` / `integration.py:17` comments — verify they're the only ones).
- **Step-8 scorecard of record:** **50P / 2W / 17I / 0F** (2W = §4.1 SingleD EUI-basis + §4.9 ERV-v3 heat-dominance, both pre-existing, WARN acceptable). **0 FAIL.**
- **Step-9 scorecard of record:** **10P / 1W / 0F.** G8o PASS (WFH→BEM energy% **0.53 / −0.00 / −0.32**). Office EUI **172.7** in band (135,100,200) as-modelled PNNL. Sole WARN = **G2r** resid SingleD EUI 211.7 vs SHEU band [130.6, 186.1].
- **2030 deliverable of record:** `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (the **`_C`** file; 111,024 rows; **0** mutex conflicts).

---

## THE AUDIT — per-step checklist (delegate the scans; you adjudicate)

For **each** step below, the employee returns: (a) does the `*_val.md` / validation report exist and what is its **latest** scorecard (P/W/F counts, re-derived from the report body, not its headline); (b) do the `outputs_stepN/` deliverables exist with sane row counts; (c) is the **latest** deliverable version the one downstream actually consumes (provenance chain, below); (d) any FAIL or any frame/number that contradicts the "must hold" list.

- **Step 1** `Step1_docs/3rdJ_01_readingGSS_val.md` + `outputs_step1/` — GSS ingest. Check row/agent counts feed the 23,150 frame story.
- **Step 2** `Step2_docs/3rdJ_02_harmonizeGSS_val.md` + `outputs_step2/` — harmonization; note `00_column_availability_investigation.md` conclusions still hold.
- **Step 3** `Step3_docs/3rdJ_03_mergingGSS_val.md` + `outputs_step3/` — merge/work-tiler; two-channel (resid + office/WFH) split originates here.
- **Step 4** `Step4_docs/3rdJ_04_augmentationGSS_val.md` + `outputs_step4/` — ML augmentation. **This is where the 61.12% Work-when-AT_WORK=0 was diagnosed** (`Step4_docs/deepResearch/dr_S4-02...`). Confirm the 04T rake (Task 1) landed **downstream** of this and the raw 61.12% is not still the operative number.
- **Step 5** `Step5_docs/3rdJ_05_censusLinkage_2split_val.md` + `outputs_step5/`. ⚠️ **Provenance:** `outputs_step5.20260715_pre_actv2/` is the **pre-fix** archive — confirm `outputs_step5/` (post-actv2) is the live one and Step-6 reads it.
- **Step 6** `Step6_docs/3rdJ_06_longitudinalForecasting_2split_val.md` + `outputs_step6/`. **Two provenance hazards here:** (i) `outputs_step6.20260715_pre_actv2/` is pre-actv2; (ii) the mutex fix produced the **`_C`** deliverable. Confirm the live 2030 file is `..._mindwell_C.csv`, 0 mutex conflicts, and gate 6.7 (mutual exclusion) PASSes. Latest report scorecard was 54P/11W/0F/40I.
- **Step 7** `Step7_docs/3rdJ_07_bemIntegration_2split_val.md` + `outputs_step7/`. Confirm `BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv` were **regenerated on the `_C` file** (pre-fix preserved `*_BAK_2026-07-17.csv`), and `office_presence_multiplier_2030.csv` is **md5-identical** pre/post (office reads only wrk30). `outputs_step7.20260715_pre_actv2/` is the pre-fix archive.
- **Step 8** `Step8_docs/3rdJ_08_simulation_2split_val.md` + `outputs_step8/`. Confirm the **live agg tables** (`outputs_step8/agg/`) are the post-mutex rebuild (delta baseline archived at `outputs_step8/agg_pre_mutexfix_20260718/`), scorecard 50P/2W/17I/0F, gate 6.7-family clean, no NEW FAIL. **Re-derive the 2030-resid <1% delta claim** from `agg_annual.csv` vs the archived baseline — confirm 2022/historical/office rows are bit-identical.
- **Step 9** `Step9_docs/3rdJ_09_activityDrivenLoads_2split.md` + `outputs_step9/`. Confirm 10P/1W/0F, G8o PASS, office EUI in band, sole WARN = G2r, from `step9_scenario_response.csv` / `step9_eui_by_channel.csv` (re-derive, don't trust the HTML headline).

**Cross-cutting sweeps (one sonnet employee each):**
- **Frame consistency:** grep every `*.md` and every live script under Leg2_2-split for `23,211` / `144,507` / `144,465` / `23150`. Any non-23,150 occurrence that isn't an explicitly-labelled 2J reference or a known stale comment = a finding.
- **Provenance chain intact:** confirm each step's live output dir (not the `.20260715_pre_actv2` / `_pre_mutexfix` archives) is the one the next step's inputs point at. A step silently reading a pre-fix archive would invalidate the closeout.
- **Deliverable hashes:** md5 the four headline deliverables (`_C` 2030 diaries, the 3 BEM 2030 schedules) and confirm they match what Step-8's campaign actually consumed.

---

## THE IMPLEMENTATION DOC — is it fully closed?

`improvement/2J_to_3J_improvement_implementation.md` (~214 KB — **delegate the read**, do not pull it into your own context). Have a sonnet employee extract and return: the 4 task headers with their DONE/OPEN status; every OPEN-DECISION (OD-I1..I4) resolution; and the **last 5 Progress Log entries verbatim-summarised**. Adjudicate:
- All 4 tasks marked DONE with a closing entry?
- OD-I1..I4 all resolved (they were, same-day 2026-07-15 — confirm the doc reflects it)?
- Does the Progress Log end on the **mutex closeout (2026-07-18)** with no dangling "RUNNING / launched / TODO" that never got a terminal entry?
- Any task whose "success gate" (e.g. Gate A: FLOATING ≤ obs+2pp) is asserted but never shown to have passed against its own artifact?

---

## Deliverable shape (write to `FINAL_CHECK_REPORT_2026-07-18.md`)

1. **Verdict line** (top): `GO` / `GO-with-caveats` / `NO-GO for Leg-3` + one sentence.
2. **Per-step table:** Step | val report exists | latest scorecard (re-derived) | live deliverable + provenance OK | frame OK | status.
3. **Cross-cutting findings:** frame sweep, provenance chain, hash checks.
4. **Implementation-doc closure:** tasks/ODs/Progress-Log status.
5. **Caveats carried into Leg-3:** #5, #6, G4 ticket, cross-era-pairing ticket, Section-4 backcast re-score — each with "blocks Leg-3? y/n" and why.
6. **Any new defects** (with a ticket filed in `investigation/`), recommended fix + rough cost, for the user to decide.

Then: append a closing Progress Log entry to the governing doc, update memory `3j_leg2_2J_audit` with the final-check verdict, and give the user a ≤100-word French summary ending on the GO/NO-GO call.

---

## Key file map (verify paths before acting; don't trust from memory)

| What | Path (under `3J_docs_occ_nTemp/Leg2_2-split/`) |
|---|---|
| Governing implementation doc + Progress Log | `improvement/2J_to_3J_improvement_implementation.md` |
| Verdict of record (acceptance review) | `investigation/2split_results_acceptance_review.md` (ADDENDUM 2026-07-18) |
| 2J→3J audit reference | `investigation/2J_to_3J_audit_reference.md` |
| Open tickets | `investigation/TICKET_G4_pooled_strata_defect.md`, `investigation/TICKET_cross_era_pairing_defect.md` |
| Prior handoff (mutex cascade) | `improvement/prompt-manager/2026-07-18.md` |
| Per-step val docs | `Step{1..9}_docs/3rdJ_0N_..._val.md` |
| Fixed 2030 deliverable | `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (the **`_C`**) |
| Step-7 2030 BEM schedules | `Step7_docs/outputs_step7/BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv` (+ `*_BAK_2026-07-17.csv`) |
| Office 2030 multiplier | `Step7_docs/outputs_step7/office_presence_multiplier_2030.csv` (md5-identical pre/post) |
| Live agg tables | `Step8_docs/outputs_step8/agg/agg_annual.csv` (+ diurnal ~540 MB / enduse_annual / meta / peak) |
| Mutex delta baseline | `Step8_docs/outputs_step8/agg_pre_mutexfix_20260718/agg_annual.csv` |
| Step-9 outputs | `Step9_docs/outputs_step9/step9_{scenario_response,eui_by_channel}.csv` |
| Pre-fix archives (must NOT be live) | `Step{5,6,7}_docs/outputs_stepN.20260715_pre_actv2/` |
| Leg-3 target (do NOT start yet) | `3J_docs_occ_nTemp/Leg3_4-split/4-channel_split.md` |

Speed scratch base: `/speed-scratch/o_iseri/step8_2split/` (upload tree under `upload/3J_docs_occ_nTemp/Leg2_2-split/`; logs in `logs/`).

---

## The one thing to internalize

This pass exists so that when Leg-3 (4-split) forks the 2-split code, it forks from a **verified-clean** base. The failure mode you are hunting is a *silent* one: a step whose val report says PASS but whose live deliverable is actually a pre-fix archive, or a frame number that quietly reverted, or a Progress-Log task that says "launched" and never closed. Trust nothing's headline — re-derive every scorecard from its own artifact's columns, hash every deliverable against what was actually consumed, and only then sign the GO. If you find one silent defect, that alone justified the whole pass.
