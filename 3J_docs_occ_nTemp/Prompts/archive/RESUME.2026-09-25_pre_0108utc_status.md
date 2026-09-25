# RESUME - THE 3J director prompt. Start every session here.

**Last updated: 2026-09-24 (evening), "P10R runs LOCALLY at 10 workers, author ruling reversed" round.**
Predecessor: `archive/RESUME.2026-09-24_pre_local_relaunch.md` (older: `archive/RESUME.2026-09-23_pre_cancel.md`, `archive/RESUME.2026-09-23_pre_hold_return.md`).

> 🟢 **NEW 2026-09-24 ~20:03 local (00:03 UTC 09-25), AUTHOR RULING: Speed was full, so the P10R campaign runs
> LOCALLY on half the CPUs ("lets go").** This REPLACES the 2026-09-23 "Speed only" ruling below for P10R.
> The whole arm (56 cells) is now LOCAL: 9 cells already ok from 09-23 + 47 running now, one platform, so
> nothing is mixed with Speed. Command (background, from `writing/implementation/IMP/scripts/`):
> `PYTHONIOENCODING=utf-8 py -3 p10r_local_campaign.py --workers 10`; stdout
> `Leg3_4-split/Step8_docs/campaign_local_P10R/_logs/driver_stdout_relaunch2.txt`, per-cell log `driver.log`.
> RAM guard `IMP/scripts/p10r_mem_watchdog.ps1 -Threshold 80` (seen firing at threshold 1 in dry and real
> mode on a dummy process, quiet at 99; kills ONLY processes whose command line has `campaign_local_P10R`
> or `p10r_local_campaign`, driver first; log `_logs/watchdog.log`, exit 2 = fired). At launch: C: 599 GB free,
> RAM 49.6% used with 10 EnergyPlus running. Expect about 1 h. Relaunch after any stop = same command (ok
> cells are skipped). On return: tail `driver.log` / `driver_stdout_relaunch2.txt` for `DRIVER DONE ok=<n>
> failed=<m>`, then read `watchdog.log`. The driver aggregates into `outputs_step8/agg_P10R/` at the end; the
> known gap (`B_central__Tall__MTL` has no `run/eplusout.sql`) still needs its one-cell re-run before the
> aggregate counts 56. Then step 4 below (scorer, gates, P3) - locally is fine for those now too, same guard idea.
> Nothing was submitted on Speed; `/speed-scratch/o_iseri/3J_P10R/` stays as it was.

> 🔴 **CANCELLED 2026-09-23 (evening), by the author: P10R test 1346544 and array 1346545 are CANCELLED** (verified with `sacct`; nothing of
> ours left in the queue under `3J_P10R`). The author will return when Speed CPUs are free. To restart: run `p10r_submit.sh`
> (`/speed-scratch/o_iseri/3J_P10R/`), hold or wait so the non-histnu total never passes 32 CPUs (sum `squeue -u o_iseri -t R`), then
> follow step 0 below with the NEW job IDs. The mirror on Speed is intact and `mirror_md5.txt` is current (64 lines). The 1J draws
> (1342400/1342401) were NOT touched.
>
> 🔴 **RESUME HERE - 2026-09-23. The critical path is the 56 rebuilt-arm (P10R) runs on Speed.**
> Everything that needs the new numbers waits for them; work that does not need them was started in
> parallel (see "Parallel work" below). Live state = bottom of the progress log in
> `writing/implementation/3J_IMP_execution_2026-09-22.md`. Author board (update after EVERY step):
> https://claude.ai/artifact/Fr1S2GUncWa3bC5QptgoKN - state is the db doc `board/progress`
> (`checks`, `sims` bars, `log`); change it with `ArtifactData update`, republish the page
> (`writing/implementation/IMP/board/3J_improvement_board.html`) only for layout changes.
>
> **Author ruling 2026-09-23: simulations run on Speed ONLY, never on the local machine** (the local
> box is busy with the author's own work; a busy queue is not a reason to go local). The local
> `Leg3_4-split/Step8_docs/campaign_local_P10R/` (8 ok cells, killed mid-run) is kept only as a
> Speed-vs-local cross-check (`IMP/scripts/p10r_speed_vs_local.py`, tolerances from V3b).
>
> 🔴 **UPDATE 2026-09-23 (later): 1342535 FAILED at exit 1 after 15 s** - `sched_NECB2011.json` was missing from the
> P10R mirror (it was only in the V3 mirror). Fixed: uploaded to `3J_P10R/repo/3J_docs_occ_nTemp/improvements/v2/f8_necb_schedule_evidence/`
> (md5 e5386a1f, identical to local), added to both `mirror_md5.txt` (now 64 lines), old array 1342536 cancelled.
> 🔴 **HELD 2026-09-23 (author: never pass 32 CPUs):** 1346544 is on `scontrol hold` (verified JobHeldUser); other jobs use exactly 32. Release with `scontrol release 1346544` only when the sum of non-histnu CPUs in `squeue -u o_iseri -t R` is 31 or less.
> **RESUBMITTED: test cell 0 = 1346544, cells 1-55 = array 1346545** (`%26`, afterok on 1346544). At submit time the
> test was PENDING (AssocGrpCpuLimit; non-histnu CPUs were exactly 32). If the test fails again, read
> `3J_P10R/logs/p10r_1346544_0.out`; the code may need more files than the mirror holds. V3b (1342426) and V3c
> (1342434) are all COMPLETED; V3b checker 1342427 = overall NOT_EVALUABLE (noise floor) - SuperTall_MTL noise
> above TOL/10, other 3 towers PASS, control FIRED on all 4; next = write the tolerance into `IMP/V3_design_and_runs.md`
> and post-process V3c. Ignore the 1342535/1342536 IDs below.
>
> **3J jobs on Speed** (user `o_iseri`, cap cpu=64, histnu owns its half - never touch it):
> - P10R test cell 0 = **1342535**; cells 1-55 = array **1342536** (`%26`, `afterok:1342535`,
>   `--nice=10000` so histnu/1J win freed CPUs). Script `Step8_docs/3rdJ_08D_campaign_P10R_speed.sh`
>   (backup `.bak_pre_slim`), submitter `/speed-scratch/o_iseri/3J_P10R/p10r_submit.sh`. Output
>   `/speed-scratch/o_iseri/3J_P10R/campaign_P10R/<tag>/`, logs `.../3J_P10R/logs/p10r_<job>_<idx>.out`.
>   An ok cell = manifest `P10R_STATUS=ok` + `run/eplusout.sql` slimmed to ~1 MB (exit 5/6 = slim failed).
>   At 00:40 UTC the test was RUNNING and the 55 were PENDING on it (see history in step 1 below).
> - V3b plumbing check **1342426** (20 tasks, 9 done at 01:10) + checker **1342427** (afterany).
> - V3c fair code control **1342434** (4 tasks, 1 done). Details: `IMP/V3_design_and_runs.md`, `IMP/V3c_fair_control.md`.
>
> **First actions on return, in order (rewritten 2026-09-23, author away):**
> 0. **NO P10R JOBS ARE LIVE (1346544 and 1346545 were CANCELLED, see the box above).** First action on return: sum the CPUS of
>    `squeue -u o_iseri -t R` excluding `histnu`; if it is 31 or less, resubmit with `p10r_submit.sh` (test cell first), else wait.
>    The text below about 1346544/1346545 is the history of the held state; use the new job IDs after resubmitting.
>    (old) test cell 1346544 (HELD) + array 1346545 (waits on it). Old IDs 1342535/1342536 are dead.
>    `sacct -j 1346544,1346545 -X`, then sum the CPUS of `squeue -u o_iseri -t R` EXCLUDING `histnu`.
>    If that sum is <= 31: `scontrol release 1346544` (ssh, no python on login). If 32, leave it held and
>    re-check later; never pass 32 (author, 2026-09-23). When the test finishes, `sacct` it; ok cell = manifest
>    `P10R_STATUS=ok` + slimmed sql. If it FAILED, read `3J_P10R/logs/p10r_1346544_0.out`, fix (any new mirrored
>    file also goes into BOTH `mirror_md5.txt`), `scancel 1346545`, resubmit with `p10r_submit.sh`, hold again if at cap.
>    Board (db `board/progress`) was last updated at version 9 with the hold; update it after each step.
>    Done and NOT to redo: V3b (20/20) and V3c (4/4) finished; V3b checker overall NOT_EVALUABLE (SuperTall_MTL
>    noise floor above TOL/10; Tall_MTL, Tall_CLG, SuperTall_CLG PASS; control fired on all 4). Next for those
>    two, needing no CPUs: write the tolerance into `IMP/V3_design_and_runs.md`, then `IMP/V4_design.md`, and
>    post-process V3c per `IMP/V3c_fair_control.md` (any Python there = sbatch, not login node).
>    Lesson: a shell command with backticks in a double-quoted string ran locally and garbled a line of this file
>    (fixed); use the Edit tool for this file.
> 1. (old, kept for the history) `sacct -j 1342535,1342536,1342426,1342427,1342434 -X` (never infer "finished" from empty output).
>    If 1342535 FAILED: read its log, fix, `scancel 1342536`, re-upload, re-run `p10r_submit.sh`.
>    History: 1342523 and 1342533 FAILED in 7 s at the mirror check (exit 3) because the edited speed
>    script's md5 was stale in `repo/mirror_md5.txt` (the file the checker reads; a copy also sits at
>    `3J_P10R/mirror_md5.txt`). Fixed: list now 63 lines (script 556bebd8 + slimmer 51d6487d). Any
>    future edit of a mirrored file must update `repo/mirror_md5.txt` in the same step.
>    1342535 started 00:39 UTC on speed-30: `[mirror] OK`, `preserve_load_standby_floor=True`.
> 2. Update the board bars + log.
> 3. V3b done -> read the checker, write the cross-platform tolerance into `IMP/V3_design_and_runs.md`,
>    then the V4 design note (`IMP/V4_design.md`). V3c done -> post-process per `IMP/V3c_fair_control.md`.
> 4. All 56 P10R cells ok -> phase C **as sbatch jobs on Speed** (not locally): aggregate
>    (`--idf-name injected_resized.idf`, `PYTHONPATH=<repo>/eSim`) -> Step-9 scorer -> gates (d)+(e)
>    over 56 cells (`IMP/scripts/p10r_gates.py`) -> old-vs-new table for `IMP/P10_2030_level_check.md` §6
>    -> P3 re-run on the new arm. Pull only the small outputs back to `Leg3_4-split/outputs_step8/agg_P10R/`
>    and `Step9_docs/outputs_step9_P10R/`. Speed-vs-local check on the 8 local cells.
> 5. Then: V3a seed repeats on the P10R products; REWRITE stage 2 numbers pass (substitute the 143
>    ⟦P10R⟧ markers in `writing/chapters_v2/`); P9 second pass; rebuild both docx (verify installed media
>    md5s); P14 finish; closure ritual (Progress Log, this file, board, memory).
> Never touch the frozen arm (`campaign_local_deliverable/`, `agg_deliverable/`, `outputs_step9_deliverable/`).
>
> **Parallel work started 2026-09-23 (does not need the new numbers):** prose fixes in `chapters_v2`
> ("fails" -> "does not meet", leftover HTML author comments removed); P14 journal-package draft
> (cover letter, highlights, declarations, audit prompt) with ⟦P10R⟧ markers where numbers go.
> Their status is logged in the execution doc. **Both DONE and checked 2026-09-23:** wording pass
> (11 sentences, 14 comments out, 143 markers intact, backup `chapters_v2/_archive_pre_stage2a/`;
> 11 open questions in `IMP/rewrite_log.md` "Stage 2a"); P14 draft `IMP/P14_package.md` (no dashes,
> no "fail" in prose; author must confirm NSERC wording + AI declaration and fill reviewers).

> 🔴 **NEW 2026-09-22 - READ FIRST. Do NOT submit 3J as it stands.** 2J was rejected by Building
> Simulation (report-like writing, no simpler-schedule comparison, calibration called validation,
> "forecast" wording, missing statistics). A side-by-side read found 3J carries almost all of it, plus
> two problems of its own: the "coincidence factor below 1" headline is true of any building by
> arithmetic, and the uninjected code-schedule case is never compared for peak timing. Plan:
> `writing/submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md` (P1-P14, decisions D1-D7).
> First checks, in order: P10 (does 3J's 2030 raking share 2J's pre-relink defect? Table 6's
> "10.51 pp below observed 2022") then P3 (code-schedule comparison from the frozen deliverable).
> **D1-D7 ANSWERED 2026-09-22** (plan Section 7): fix first; "forecast" out of the text, title kept;
> lead with timing vs code schedules (only if P3 shows a difference); read-only work on frozen
> aggregates approved; short Limitations (~250 words) in the main text; stay with B&E after P3 + P7.
> Validation tracks V1-V4 all approved (plan Section 7a): V1 measured building energy, V2 measured
> occupancy (both reading only), V3 seed repeats + plumbing check, V4 second tower model. The
> no-simulation rule is lifted for V3/V4 only; runs stay inside the 32 allocated Speed CPUs, never
> touch `histnu`, and are sequenced with live 1J jobs (same cap). Start: P10, then P3, then V3b.
> The work list further down predates this and is now secondary. Predecessor: `Prompts/archive/RESUME.2026-09-22_pre_2J_lessons_plan.md`.
> **EXECUTING since 2026-09-22 (author: "do not wait my confirmation, go to the end").** Live state:
> `writing/implementation/3J_IMP_execution_2026-09-22.md` (work-package table + progress log); each
> package writes its result to `writing/implementation/IMP/`. V3 runs go to Speed under
> `/speed-scratch/o_iseri/3J_V3/`; job IDs are in `IMP/V3_design_and_runs.md`.

> 🔴 **THIS FILE IS THE FIXED ADDRESS OF THE 3J HANDOFF. There is no second one.**
> Instruction from the author, 2026-08-09: *"je veux seulement cet prompt RESUME.md, comme un prompt
> de directeur"* - one file, this path, updated in place every round.
>
> - **Never create a successor file beside it.** Copy the predecessor into `archive/` under a
>   `.<date>_pre_<round>.md` name, then **edit this file**. The address never moves.
> - **Never leave it lagging.** It is updated in the same response as the state change it describes,
>   like the Progress Log. A handoff that lags is worse than none, because it is trusted.
> - **History.** Until 2026-08-09 the handoff lived at
>   `3rdJ_employee_N6_figure_renumbering_2026-08-08.md`, and this file was a short pointer at it. The
>   author consolidated the two. That file is now
>   `archive/3rdJ_manager_prompt_2026-08-09_generated_images.MERGED_INTO_RESUME.md`; every earlier
>   handoff is in `archive/` beside it, most recent first:
>   `3rdJ_manager_prompt_2026-08-09_ledger.SUPERSEDED_by_generated_images_round.md`,
>   `3rdJ_manager_prompt_2026-08-09_round2.SUPERSEDED_by_full_ledger_round.md`,
>   `3rdJ_manager_prompt_2026-08-09.SUPERSEDED_by_docx_cleanup_round.md`,
>   `3rdJ_manager_prompt_2026-08-08.SUPERSEDED_by_2026-08-09_decisions_and_docx_round.md`,
>   `3rdJ_manager_prompt_2026-08-08_submission_round.SUPERSEDED_by_figure_dpi_round.md`,
>   `3rdJ_manager_prompt_2026-08-08.SUPERSEDED_pre_RV09_RV10.md`,
>   `3rdJ_paper_manager_prompt_2026-08-07_review_round.md`.
> - The old contents of this file - the Leg-2 two-channel simulation runbook, with the v24.2
>   `Zone_or_ZoneList_Name` office-WFH bug write-up - are at
>   `archive/RESUME.2026-08-09_pre_rewrite_leg2_runbook.md`. That campaign is finished and superseded
>   by Leg-3. **Nothing in it should be executed.**

---

## Contents

1. [Your role](#your-role)
2. [Where the paper stands, 2026-08-11](#where-the-paper-stands-2026-08-11)
3. [The document, and how to rebuild it](#the-document-and-how-to-rebuild-it)
4. [The figures, and how the trees are kept honest](#the-figures-and-how-the-trees-are-kept-honest)
5. [Everything completed, round by round](#everything-completed-round-by-round)
6. [The three BUILD NOTES that used to be open, and how each closed](#the-three-build-notes-that-used-to-be-open-and-how-each-closed)
7. [What is settled, so nobody reopens it](#what-is-settled-so-nobody-reopens-it)
8. [The work that is left, in the order I would do it](#the-work-that-is-left-in-the-order-i-would-do-it)
9. [Refusals still standing](#-refusals-still-standing-the-first-one-costs-money-if-it-is-forgotten)
10. [Standing hazards](#standing-hazards-and-every-one-of-them-has-already-bitten-this-project)
11. [Hard rules for this phase](#hard-rules-for-this-phase)
12. [The closure ritual, every round, unprompted](#the-closure-ritual-every-round-unprompted)

---

## Your role

You are the **director / manager (Opus)** for the 3rd journal paper. You plan, decide, write employee
prompts, and review. You do not normally execute multi-step implementation yourself, but the author
has overridden that six times now and will probably again; when they do, do the work and log it.

Reply in English. The author writes in French. Keep replies short unless detail is asked for.

**In five lines, for the impatient:**

- The 3J paper is **written, built, rendered and gate-clean**. It is **not submitted**.
- It now ships as **TWO documents**: the manuscript and `Supplementary material.docx`. Build both,
  every time.
- Venue: **Building and Environment (Elsevier)**, reconfirmed 2026-08-09, which made three
  commitments binding.
- **This is a WRITING phase. Zero simulation.** No `sbatch`, no cells, no re-runs.
- **Zero open BUILD NOTES**, all eleven resolved, and **zero known defects** in the shipped files.
  The stale-figure problem found earlier on 2026-08-11 is fixed and verified inside both `.docx`.
- 2J was submitted to Building Simulation on 2026-08-07 and is frozen pending its decision letter.

---

## Where the paper stands, 2026-08-11

**Target venue: Building and Environment (Elsevier). RECONFIRMED by the authors 2026-08-09.** The
sheet `writing/submission/02_journal_options.md` is **green again**. Reopen trigger (b) fired on
2026-08-08 (0J was rejected at B&E for insufficient quality, not scope); the trigger was put back in
front of the authors with the bar restated and the venue was chosen again, recorded in a
`RECONFIRMED BY THE AUTHORS - 2026-08-09` block under Option D.

> **What reconfirmation cost, and it is binding now, not advisory.** The amber block said that if the
> venue were reconfirmed the three commitments under "My recommendation" become more load-bearing.
> They are therefore fixed: (1) the **uninjected-control** result leads the cover letter's first
> paragraph - it is what separates "three of four EUI gates failed" from a desk reject, because the
> office band fails on a model with no occupancy injection at all; (2) the **abstract** opens on the
> behavioural claim, not the pipeline; (3) the **§1 and §6.1 pass** under Option D stands.
>
> Still cheap and still never done: read the 0J decision letter if it exists. "Quality" can mean thin
> contribution, weak validation, or unclear writing, and those point at different fixes. Reconfirming
> the venue decided that the answer is not needed *before* submitting, not that it does not matter.

**Numbers, all re-derived at the last build:**

| | |
|---|---|
| `readySubmission.md` | **873 lines**, 18 exhibit captions. The supplementary half is now a separate file |
| `readySubmission_SI.md` | **171 lines**, 5 exhibit captions (Tables 4, 7, A1, A2 and Figure S3) |
| `3J_manuscript_submission.docx` | **4,261,337 bytes** · **14 images** · 5 tables · **11,935 words** · **single** spaced |
| `Supplementary material.docx` | **138,764 bytes** · 1 image · 9 tables · **1,515 words**, built by the same recipe |
| figures inside those two files | **15 of 15** md5-identical to `writing/figures/`, checked 2026-08-11 |
| equations | **6 native Word (OMML)**, 3 of them displayed. Formulas are no longer code blocks |
| lists in the document | **5**, and all five are the Highlights. Everything else is prose |
| `f3` asset provenance | **3 PASS / 2 FAIL** - the figure registry is stale since the 2026-08-11 replot, see below. **Do not modify `f3` itself** |
| `f4` prose rules | 7 PASS / 0 FAIL (31 files, 22 exhibits) |
| `f5` figures | not run this round - it is NOT read-only, see below |
| `f6` replot equivalence | 5 PASS / 0 FAIL as of 2026-08-09 |
| open BUILD NOTES | **0** |

🔴 **`f3`'s two FAILs are asset bookkeeping, not a manuscript defect, and they are real.** C2 lists
figures present in the submission tree that are not in the registry, and C4 reports
`figures_hires/fig_diurnal_4ch.png` disagreeing with its registered hash. Both date from the
2026-08-11 figure replot, which did not update the registry. Fix the REGISTRY, never the gate.

**House rules for exhibits, set by the author 2026-08-11 and now enforced by the build:**
a figure caption goes **below** the figure, a table caption goes **above** the table, every caption is
**about five words** on **one line**, and **bold is not used inside a paragraph** - the only bold left
in the document is the `**Figure N.**` / `**Table N.**` labels - **23 of them, 18 in the manuscript
and 5 in the supplementary document** - which the assembler, the loss check and `f4`'s C7 all key on. The build prints `captions that wrapped onto a second line`; it must stay 0,
because a wrapped caption used to be split in half by its own figure.

**House rules for the PROSE, set by the author 2026-08-11 in the same day's second message. It is a
paper, not a report, and every one of these is countable in the built file:**

- **One serif font.** Times New Roman everywhere. `ref_submit_single.docx` pins the four heading styles
  and `VerbatimChar`; the sources carry **no inline code spans at all**. An identifier in backticks
  reads as code however it is typeset, so both halves are needed. Installed file: 0 explicit non-Times
  runs, 0 Consolas.
- **Formulas are Word equations.** Written as TeX in the sources, converted by pandoc to native OMML.
  Count `<m:oMath>` in the installed file; a formula that shipped as text or as a picture counts zero.
- **No build dates, no repository paths, no "Footnotes" sections** in reader-facing text. Currently
  0 / 0 / 0.
- **No bullets and no numbered lists**, except the five Highlights, which Elsevier requires as a list.
- **The supplementary material is a SEPARATE DOCUMENT**, `submission/Supplementary material.docx`,
  built from `fullSet/readySubmission_SI.md`. `assemble_3J.py` splits it off with
  `split_supplementary()`, which runs **after** `strip_for_submission()` so the residue, caption and
  image checks still see the whole document, and which asserts the split is a partition: every caption
  and every image lands in exactly one half. Both docx come from the same two pandoc runs; never build
  one and not the other.
- **No exhibit inside Discussion or Conclusion.** Table 4 and Table 7 live in the supplementary
  document and are cited from the body.
- **There is no Limitations chapter.** It was merged into Chapter 6 on 2026-08-11 and the chapter was
  then cut twice on the same day, 2,656 to 1,367 to **697 words**, a total 74 % cut. The Conclusion is
  Chapter 7. Continuous prose, no subsections, no L-numbers. Numbers dropped from the prose in the
  second cut (the 24.97 / 29.97 m2/person pair, the 7.5028 W/m2 blanket, the retail 0.95 peak, the DHW
  -0.98 slope) all still stand in **Table 7**; check there before calling one of them missing.
- **Table numbering is not in first-citation order** (main text 1, 2, 6, 3, 5; appendix 4, 7, A1, A2).
  Pre-existing, flagged to the author, renumbering not done unasked.
- **The appendix carries tables, not essays.** No explanatory blocks around an SI table.

🔴 **Before cutting any block, find the surviving home of every number in it.** The disclosures that
were deleted from the SI model card this round are all stated in Chapter 3 prose; that was checked
disclosure by disclosure, not assumed. A cut that loses a measurement is a defect, not a shortening.

⚠ **The `f5` paragraph below describes the state as of 2026-08-09, when the shipped art was
author-generated. The 2026-08-11 replot put the script-drawn figures back, which may have changed both
arms; `f5` has not been run since, so its current verdict is UNKNOWN rather than 5 PASS / 2 FAIL.
Snapshot the figure tree's md5s before running it - see the read-only warning underneath.**

🔴 **`f5`'s two FAILs are the correct answer and must not be "fixed".** C1 fails because the vector
PDFs for the swapped figures were deliberately removed rather than left disagreeing with the new
PNGs. C2 fails because the plotting scripts no longer reproduce the shipped artwork - they cannot,
the artwork is no longer theirs. Both are true statements about a decision the authors took.

🔴 **`f5` is also NOT read-only. Its C2 arm re-runs every figure script, and those scripts write to
the real output paths.** Running it after installing an image silently reverts the install in
`writing/figures/` and regenerates the deleted PDFs. Its `md5 changed on re-run (b3eea0a9 ->
d09d7b8d)` line was the gate reporting **its own write**, not a determinism finding. Re-install and
re-verify after running it. `f6` was checked the same way, snapshotting the figure tree's md5s before
and after, and is genuinely read-only.

---

## The document, and how to rebuild it

`writing/fullSet/` holds **two** files since 2026-08-11: `readySubmission.md`, the manuscript, and
`readySubmission_SI.md`, the supplementary material. The working draft, which still holds both halves
and every apparatus block, lives in `writing/fullSet/previous/`.

All three come from **one** in-memory string built by `assemble_3J.py`. The draft is that string
verbatim; the two submission files are that string put through `strip_for_submission()` and then
**partitioned** by `split_supplementary()`. 🔴 **The split runs AFTER the strip, and the order is
load-bearing:** the strip's residue check, caption loss check and image loss check all reason over the
whole document, and splitting first would halve what each of them can see. The split then asserts it is
a partition - every caption and every image lands in exactly one half, and a missing, duplicated or
surviving `# Supplementary material` heading raises. Both the strip's manifest and the split's counts
are printed on every build.

```
writing/submission/
  3J_manuscript_submission.md     <- readySubmission.md, figure paths rebased ../figures/ -> figures/
  3J_manuscript_submission.docx   <- 5.59 MB, 18 captions, 14 images, 5 tables, SINGLE spaced
  3J_supplementary_material.md    <- readySubmission_SI.md, same rebase
  Supplementary material.docx     <- 163 kB, 5 captions, 1 image, 9 tables. The author named this file
  figures/  figures/SI/           <- the 15 shipped PNG, each with its vector PDF. Re-synced 2026-08-11
  figures/Prompts_Images_v3/      <- the image-generation prompts (note the _v3 suffix)
  figures/archive/                <- superseded matplotlib art · jpg duplicates · the 3 refused figures
  tables/   tables/SI/
  extra/build_scripts/            <- ref_submit.docx, ref_submit_single.docx, post.py, submit_check.py
```

Rebuild it with, from `3J_docs_occ_nTemp/`:

```
py -3 writing/fullSet/assemble_3J.py
cd writing/submission
sed 's|\.\./figures/|figures/|g' ../fullSet/readySubmission.md    > 3J_manuscript_submission.md
sed 's|\.\./figures/|figures/|g' ../fullSet/readySubmission_SI.md > 3J_supplementary_material.md
pandoc 3J_manuscript_submission.md -o raw.docx    --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
pandoc 3J_supplementary_material.md -o raw_si.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx    3J_manuscript_submission.docx
py -3 extra/build_scripts/post.py raw_si.docx "Supplementary material.docx"
```

Both halves are built every time. The supplementary document is not optional apparatus: it carries
Tables 4, 7, A1 and A2 and Figure S3, all five of which the body cites by number.

🔴 **The reference doc changed on 2026-08-09 and the old one still exists.** `ref_submit.docx` is 2J's,
untouched, **double** spaced (`w:line="480"`). `ref_submit_single.docx` is the derived copy at
`w:line="240"`, **single**, which is what the authors asked for and what the recipe above uses. Both
carry 12 pt Times, black headings, justified body, centred 10 pt captions; `post.py` sets table text to
10 pt single-spaced. Note that **Elsevier asks for double-spaced manuscripts at submission**, so if the
desk check bounces it, the fix is swapping one filename on the pandoc line.

**Verify the INSTALLED docx, never the build output** - in the 2J round a table column had silently
vanished from the shipped file. The check that matters is md5 of every part in `word/media/` against
the files on disk. **No blinded build is needed**: review is single-anonymized (RV10 item 14).

**The build tells you whether the paper is ready:**

```
UNRESOLVED BUILD NOTES -- each one blocks submission:
  none. Nothing in the manuscript is waiting on an external answer.
```

An answered note is rewritten in place as `BUILD NOTE RESOLVED <date> by <what>`. It keeps the words
"BUILD NOTE" on purpose, so the strip and the residue check still catch it, and it stops counting as
blocking. **Deleting the note would delete the reason.** **Clean is not ready.**

---

## The figures, and how the trees are kept honest

**All 15 figures in both documents are the corrected 2026-08-11 set, verified inside the installed
files.** md5 of every PNG in `writing/figures/` against the `word/media/` parts of the two `.docx`
returns **15 of 15**. Each also has a vector PDF beside it in the submission tree.

| | px | about, at the 190 mm page width |
|---|---|---|
| Figures 1 to 6, graphical abstract, S2, S3 | 4500 to 6600 wide | 600 to 880 dpi |
| Figures 7 to 11, the measured results | 4622 to 6597 wide | 620 to 880 dpi |
| Figure S1 | 3744 x 3016 | about 500 dpi, the smallest in the paper |

Elsevier asks **500 dpi** for combination art, so the whole set clears it, S1 by the narrowest margin.

🔴 **THE HAZARD THIS SECTION EXISTS FOR, because it already bit once.** There are **two figure trees**:
`writing/figures/` is the source that the plotting scripts and every gate read, and
`writing/submission/figures/` is what `pandoc` actually reads at build time. They hold the **same
fifteen filenames**. On 2026-08-11 the nine schematics were corrected and re-rendered into the source
tree, the BUILD NOTE was marked RESOLVED, the build printed zero open notes - and **the copy into the
submission tree never happened**, so three further rounds shipped `.docx` files carrying the superseded
1376 x 768 artwork at about 184 dpi. Nothing failed: every gate reads the source tree where the fix was
real, every path resolved because both trees carry the filename, and the build's image count asks how
many images survive the strip, not which version each one is.

**After touching any figure, do both of these:**

```
cp writing/figures/<name>.png writing/submission/figures/<name>.png      # SI figures -> figures/SI/
cp writing/figures/<name>.pdf writing/submission/figures/<name>.pdf
```

then rebuild and **md5 every part in `word/media/` of the INSTALLED files against the source tree**.
That comparison is the only check that can tell the two trees apart. The superseded generated art is
kept at `writing/submission/figures/archive/generated_1376x768_replaced_2026-08-11/`.

**Figures 7 to 11 are the measured results and must not be replaced** absent an explicit decision. All
15 have a prompt at `writing/submission/figures/Prompts_Images_v3/`; the six that carry measured
numbers - 7, 8, 9, 10, 11, S1 - have prompts that **embed the actual series in a table** from the frozen
deliverable, with file, column and source line named. S1's prompt is marked **DO NOT GENERATE**: two
separate generation rounds returned invented shares, so it is plotted by
`writing/figures/SI/figS01_shares.py` instead. Figure 9's series needs `metric == "energy_W"` (Step-9
script `:331`); without that filter every channel returns 48 rows and the plotting code's
`len(y) != 24` guard silently skips it.

---

## Everything completed, round by round

The full detail is in `writing/implementation/3rdJ_paper_TASKS.md`, one Progress Log entry per line
below. This table exists so a fresh session knows what is **done and closed** without reading 2,198
lines. The third column is what the round found that was not what it was sent to do - that column is
the reason the ledger is worth keeping.

### Build phase - 2026-08-06, tasks T1 to T12

| # | What was delivered | What it also found |
|---|---|---|
| T1 | Step-1 asset verification: every figure, table and number traced to a frozen artefact | - |
| T2 | Bucket C - the 7 existing figures relocated into the paper tree | one C2 mismatch, explained not patched |
| T3 | Bucket B - Tables 2, 3, 6 | 🔴 **Table 6 changed what the paper is allowed to claim** |
| T4 | Bucket B - Tables 4, 5 | an arithmetic error, caught at review |
| T5 | Bucket B - Tables 1, 7 | the limitations count is a known ID collision |
| T6 | Bucket B - SI tables A1-A2, B1, Appendix C | B1 is clean |
| T7 | Bucket A - the 8 schematic prompts | - |
| T8 | Bucket D - Chapters 2, 3, 4 | a new check, plus a Methods disclosure that had to be added |
| T9 | Bucket D - Chapter 5, Results | §5.1 gained a caveat it needed |
| T10 | Bucket D - Chapters 1, 6, 7, 8 + Front Matter | two manager corrections |
| T11 | Assembly | **the 2J divergence is now structurally impossible**, not merely avoided |
| T12 | Final build report and closure | - |

### Round 2 - 2026-08-06 night into 2026-08-07

| # | What was delivered | What it also found |
|---|---|---|
| R3 | the submission strip, `strip_for_submission()` | 🔴 **the transform's own guard caught it lying** |
| R2 | schematics - direction decided, build delegated | - |
| R4 | the first deep-research prompt | - |
| R1 | the first end-to-end read of the whole paper | it justified itself immediately |
| #17 | - | 🔴 **the strip deleted real content and no check noticed** - this is why the loss check exists |
| #18 | RV07 and RV08 returned, vetted offline | - |
| #19 | schematics built | 🔴 **one schematic contradicted Table 6** |

### Submission phase - 2026-08-08

| # | What was delivered | What it also found |
|---|---|---|
| #1 | N6 figure renumbering + the `fullSet/` single-document layout | - |
| #2 | SI Tables B1 and C1 cut from the paper (kept on disk - `f5` reads them) | - |
| #3 | **target journal decided: Building and Environment** | - |
| #4 | 13 uncited figures cited, apparatus out of the paper, the B&E framing pass | 🔴 **a Manager-notes block was partly INSIDE the submitted paper**; the DOI banner removed without hiding the problem; Table 6 restructured; **an identifier sweep that had to be reverted** |
| #5 | figures re-rendered at 600 dpi + vector PDF; the B&E requirements prompt | 🔴 **`DEFAULT_AGG` pointed at the superseded arm** - 1 of 5 figures reproduced, 16 `verdict_asmodelled` cells moved. A reopen trigger fired, and it had been written before the fact |
| #6 | RV09 and RV10 returned, vetted, applied | **BUILD NOTES 5 open to 1 open**; a second compliance failure found by checking rather than by being told; one finding **reversed work done two hours earlier** |

### Decision and rendering phase - 2026-08-09

| # | What was delivered | What it also found |
|---|---|---|
| #1 | the three authorial decisions taken; last RV09/RV10 note closed; **the submission `.docx` built** | 🔴 the calibration dispute was settled by a fact **inside RV09 all along**; **Table A2 ships unlabelled** - back to 1 open |
| #2 | the `.docx` made to read like a paper: no thematic breaks, no report notes, single spacing, one bulleted `# References` chapter, 2J cross-cited, image prompts collected | 🔴 **2J was missing from its own successor**; **nine sources were cited with no entry anywhere**; **two of them had never been opened** - back to 2 open |
| #3 | the handoff rebuilt as a full ledger with a table of contents | a dash check reported **281 matches on a file containing zero**, and exited 0 |
| #4 | author-generated images installed; the never-create-images rule written into `CLAUDE.md` and `README.md`; prompts written for all six remaining figures | 🔴 **`f5` reverted the install while checking it**; **C6 passed on a figure whose shipped PNG reads `4.0.1`**; **three generated results figures came back fabricated and were refused** - 3 open |
| #5 | the handoff and this file merged into one director prompt at this path; the 15 installed images re-verified inside the shipped `.docx` | - |

### The paper-not-a-report phase - 2026-08-11

| # | What was delivered | What it also found |
|---|---|---|
| #1 | figures corrected and re-rendered from their scripts; BUILD NOTE 3 answered in the sources | 🔴 the correction **never reached `submission/figures/`** - not noticed until 2026-08-11 #6 |
| #2 | the exhibit house rules: five-word captions, figure captions below, table captions above, no bold in paragraphs | 🔴 **five of fifteen figures shipped INSIDE their own caption** - the assembler matched only the placeholder line |
| #3 | *"ceci n'est pas un rapport, c'est une papier"*: one serif font, native Word equations, no dates or paths, lists 51 to 5, Table 7 to the SI, 20,025 to 15,398 words | 🔴 **the strip deleted a figure and the loss check was blind**, because it counts captions and the caption survived |
| #4 | Table 4 to the appendix, Limitations merged into Discussion, that chapter cut 2,656 to 1,367 words | table numbering is no longer in first-citation order; flagged, not fixed |
| #5 | the Discussion cut again to **697 words**; **the supplementary material split into its own `.docx`** | - |
| #6 | this file brought up to date for the next session | 🔴 **the stale submission figure tree** - nine superseded images were in the shipped manuscript |
| #7 | the nine figures re-synced and both `.docx` rebuilt; **15 of 15 verified inside the installed files** | - |

### What the 2026-08-09 round 2 changed, in detail

**No thematic breaks in the submission copy.** Word was showing 60 objects named "Horizontal Line";
they are markdown `---` rules, which pandoc emits as **VML rectangles** (`<v:rect>`). No style setting
could remove them - they are drawings, not text. `strip_for_submission()` now drops every rule, **last,
after the residue and loss checks**, because the section-drop loop uses `---` as a terminator and the
residue check tests for two rules in a row. Built file: 0 `<v:rect>`.

**No report-style notes in the paper.** Six went: the `n/r` legend, `(5 bullets, each <=85
characters.)`, the front-matter note, the Table 1 differentiation note, and two "verify against the
master bibliography" asides. Three became `<!-- APPARATUS NOTE ... -->` comments and the strip grew one
new named rule that removes **every** HTML comment that is not already a BUILD NOTE. Deleting them
would have deleted the reason.

**`MARK_SUB` is now `not reported`, not `n/r`.** The legend was solved by making the legend
unnecessary. The marker is still fully visible; only the blockquote that declared the symbol went.

**One `# References` chapter at the end**, bulleted, alphabetised, after the Conclusion and before the
Supplementary material. Chapter 08 was split into `Chapter_08_Conclusion.md` /
`Chapter_09_References.md` / `Chapter_10_Supplementary.md`. Nine sources that were cited with no entry
anywhere are now entered, and the Statistics Canada / NECB / EnergyPlus entries were replaced with 2J's
already-vetted forms so the two papers agree.

**2J is cross-cited.** §1.4 describes 2J's abstract almost word for word while citing the JBPS paper
and the eSim companion instead. 2J is now `Iseri and Hachem-Vermette (under review b)` and is cited at
§1.4, §2.1, §3.6, §7.F and the reference list; the JBPS entry became `under review a`.

---

## The three BUILD NOTES that used to be open, and how each closed

**All eleven BUILD NOTES are RESOLVED and the build prints `none`.** These three were the blocking ones
for most of the paper's life, and each is kept here with the reason it closed, because the reason is
what stops it being reopened by accident.

**1. Table A2 shipped unlabelled and uncited. CLOSED 2026-08-11.**
`Table_A1_A2.md` carries two tables, `inline_table()` strips every `^# ` line, and A2's `# ` heading was
its only label - so the AT_RETAIL codebook shipped as an unnumbered tail of the model card. Closed by
replacing that heading with a **bold caption line**, which the assembler does not strip. 🔴 **Keep the
lesson:** `f4`'s C7 reported 22/22 the whole time, because C7 checks that every caption it FINDS is
cited, and this caption had been destroyed before C7 ever saw the document. A check that enumerates
from the artefact cannot see what was deleted upstream.

**2. Kurin et al. 2022 and Menon et al. 2020 had never been opened. CLOSED 2026-08-11 BY REMOVAL.**
Both came from the deep-research report family in which roughly half of all citations have been found
fabricated, and the Kurin entry was `dr_L3-13` reference 5 minus two fields that were self-evidently
placeholders. Neither was load-bearing, so they were **removed rather than verified**. 🔴 **Do not
re-add either from a report.** If one is wanted back, it is a `V<NN>` prompt for the author to run
externally - never a search from this session.

**3. The generated-image defects. CLOSED 2026-08-11 in the sources, and this is the one that is only
half-true.** The nine author-generated schematics were reverted to a corrected script-drawn set:
Figure 1 draws nine boxes on one row (the generated replacement drew twelve, with STEP 5, 6 and 7 each
twice), Figures 4 and 6 carry their previously blank labels, S2 carries all nine scenario-lever values,
and the graphical abstract places the four channel peaks at 12.1, 11.9, 12.3 and 18.9 h with the whole
building near 15 h, which is what §5.3 and Figure 10 report. **S1 was taken out of the
generate-from-a-prompt route entirely** after a second generated version repeated the defect with
different digits. 🔴 **But that correction never reached the submission tree - see the figures section
above. The BUILD NOTE is marked resolved and the shipped `.docx` still carries the old artwork.**
*Generalises:* a note is resolved when the SHIPPED artefact changes, not when the source does.

---

## What is settled, so nobody reopens it

**The calibrated-behavioural-model dispute is CLOSED, and the fact that closed it was inside RV09.**
RV09 marked THIS STUDY "No" on that axis against Table 1's tick. Reading the **column** instead of the
cell settles it: **RV09 marks all TEN rows of its own matrix "No"**, including Widén and Wäckelgård
and Yamaguchi, which it separately certifies as time-use-survey-driven, and its parenthetical for this
study is "gate-tested control" - validation, not a denial that the model is fit to microdata. A column
with zero variance across ten studies cannot un-tick this study specifically. Recorded, not adopted.

Two things fell out of that, and the second is the one worth remembering:

- The novelty claim **never rested on that axis**. It rests on four: time-use-survey-driven,
  multi-channel, forecast to a future year, mixed-use single building.
- 🔴 **One of those four was not a column in Table 1.** *Time-use-survey-driven* was missing from a
  seven-axis matrix, so the table did not score the axis the claim most depends on. **Added.** The
  matrix is now eight axes; §1.2's "six positioning axes" and the caption's "Seven-column" are
  corrected to eight.

Also closed: **Table A1's `Confirmed against` column** is retitled **`Source in the project
repository`** in all three sub-tables, with a paragraph above declaring the convention (internal
paths, not expected to resolve, printed so every number is attributable to a place in the build).
The five `⚠ check source` cells in Table 1 are settled from RV09 full-text readings; markers went
22 to 14. **Not adopted from RV09**, and named in Table 1's Sources so nobody re-imports them: its
calibration column, and its *activity/end-use* verdict for Doma, which contradicts `dr_L3-10` on a
cell `dr_L3-10` does state.

Closed in earlier rounds, do not redo: figure resolution (600 dpi + vector PDF; combination art needs
**500**, and the 300 dpi intermediate was itself wrong), keywords 13 to 6, **no abstract cap** (272
stays), single-anonymized review, both disputed DOIs, the SI cuts of B1 and C1, the target venue, the
figure renumbering, and the whole 2026-08-09 docx cleanup listed in the ledger above.

---

## The work that is left, in the order I would do it

| # | Item | Whose call | Blocking? |
|---|---|---|---|
| 0 | **Re-run `f3` and update the figure REGISTRY**, never the gate. Its 2 FAILs are the 2026-08-11 replot, which the registry never recorded. Now that both trees agree, this is bookkeeping with nothing else in the way | mine | yes, for submission |
| 2 | **Renumber the tables into first-citation order** if wanted. Main text runs 1, 2, 6, 3, 5 and the supplementary 4, 7, A1, A2. Table 6 was already out of place before the SI moves. Offered twice, not done unasked | authors | no |
| 3 | **Fill the cover letter's placeholders** - handling editor's name, submission date - in `writing/submission/Title_Page_and_Cover_Letter.md`, then render it the same way. 2J shipped the title page and cover letter as **one** document | authors supply, I render | yes, for submission |
| 4 | **Check the three binding commitments are actually in the cover letter and abstract.** Reconfirming B&E is what made them binding. Check, do not assume | mine | yes, for submission |
| 5 | **The generative-AI declaration.** RV10 item 18 gives Elsevier's prescribed wording; it goes in a dedicated section before the references, required only if such a tool assisted drafting. Whether one did is the authors' statement to make, so nothing was written | authors | yes, for submission |
| 6 | **Decide whether the supplementary material needs its own title block** - author list, corresponding author, a "Supplementary material for:" line with the manuscript title. It currently opens straight on `# Supplementary material`. Most Elsevier journals accept that; some ask for the pairing to be explicit | authors | no |
| 7 | **§1.4's "Leg-1, published as the second journal in this line (2J)"** reads as though Leg-1 and 2J are the same paper. The citations are right either way, so this is wording, not correctness | authors | no |
| 8 | **Table A1's `Source in the project repository` column** is the last report-like element left in the paper. Kept because the authors chose it. It goes on one word | authors | no |
| 9 | **Deferred and still deferred:** N7 (`f3`'s C2 failure list - **do not relax C2**) and N8 (`f5`'s C4 converse gap) | mine, when asked | no |
| 10 | **Read the 0J decision letter** if it exists. Cheap, never done, and it tells you which kind of "insufficient quality" B&E meant | authors | no |

---

### 🔴 Refusals still standing. The first one costs money if it is forgotten.

1. **Do NOT tick Gold open access** on RV10's CRKN claim that B&E carries a 100 percent APC waiver for
   Concordia authors. **Same shape as the claim that was wrong for 2J and Springer.** It blocks
   nothing (subscription publishing is free either way) but the list APC is **$3,690 USD** and the tick
   is irreversible. Confirm on Concordia Library's own page first.
2. **The Concordia editor conflict is UNANSWERED, not cleared.** RV10 item 29 named two
   Editors-in-Chief and never listed the subject editors, which is what was asked. An unlisted board
   is not an empty board, and this author line already found such a conflict at another venue.
3. **RV09 reference 5 (Yamaguchi 2017)** states one title and reports a different one as its Crossref
   return. It does not enter Table 1 and fails the cell on two axes under either title, so it blocks
   nothing, but the row is unverified. If exactly one row of RV09 Part B is opened by hand, open it.

Read `deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md` before using either report.

---

## Standing hazards, and every one of them has already bitten this project

- **A gate must be seen failing before it is trusted.** C7 was watched failing on 13 exhibits before a
  single citation was added. `f6`'s C1 was watched failing on 4 of 5 figures before it was believed.
  Write the check first, always.
- 🔴 **A check that REGENERATES its input is not read-only.** `f5`'s C2 arm re-runs the figure scripts,
  which write to the real paths, and it silently reverted a figure install. Snapshot md5s before and
  after any gate whose write behaviour is unaudited.
- 🔴 **A check that validates the GENERATOR is blind to a substituted artefact.** `f5`'s C6 certified
  Figure S1's arithmetic - from the plotting script - while the shipped PNG said `4.0.1`. Ask of every
  check: if someone swapped the output file, would this notice?
- 🔴 **A pattern that does not compile as intended does not error, it matches something else.** A dash
  check written as `grep -c [—–]'` reported **281 matches on a file containing zero**, and exited 0.
- 🔴 **Two signals removed in one edit are not two decisions.** `CONTENT_RESUMES` was narrowed on
  2026-08-08 because a bare table row let an apparatus section leak; `![` was dropped in the same edit,
  though a figure never appears inside an apparatus block. On 2026-08-11 that cost a figure: the
  section drop ran past Figure S3's image and stopped at its caption, and the submission copy shipped
  a caption with nothing above it. **The loss check counts CAPTIONS, so it was structurally blind** -
  the caption is exactly what survived. The assembler now counts IMAGES too, and the build prints
  `captions N, images M`. When you narrow a pattern, narrow one thing.
- 🔴 **A check that counts what it FINDS cannot see what was destroyed before it looked.** `f4`'s C7
  verifies every caption is cited and passed 22/22 while Table A2 shipped with no caption at all. When
  a check enumerates from the artefact, ask what the artefact would look like if an item had been
  deleted upstream - and get the count from an independent source.
- 🔴 **Read the whole COLUMN before believing a cell.** RV09's "No" on our calibration axis looked like
  a finding about us; it was a column that reads No for all ten studies. One cell is an assertion, the
  distribution is the evidence.
- 🔴 **A default inside a pipeline script is not provenance.**
  `3rdJ_09_activityDrivenLoads_4split.py:63` `DEFAULT_AGG` points at `outputs_step8/agg`, the
  **superseded** arm; the canonical deliverable came from `outputs_step8/agg_deliverable`. Rendering on
  the default reproduced 1 of 5 figures and moved **16 `verdict_asmodelled` cells**. Check defaults
  against `V2-G1_FROZEN_DELIVERABLE.md` before re-running anything.
- 🔴 **A similarity check on a plot is nearly blind.** Downsample-and-compare passed on figures built
  from the wrong arm: layout, palette and axis labels are identical no matter what the bars say.
  Re-render at the ORIGINAL resolution and demand byte-identity.
- **Verify the INSTALLED file, not the build output.** In 2J a table column had silently vanished from
  the shipped docx.
- 🔴 **A file existing at the path the build reads is not evidence that it is the file this round
  produced.** The 2026-08-11 replot corrected nine figures in `writing/figures/` and the submission tree
  was never re-synced, so the shipped `.docx` kept the superseded artwork for three further rounds while
  a BUILD NOTE recorded the defect as resolved. **Fixed the same day it was found**, but it survived
  three rounds of verification first. Every figure gate reads the source tree; the build's
  image count asks how many images survive, not which version each one is. **When two trees hold the
  same filenames, the only check that means anything is md5 against `word/media/` of the installed
  file.** A note is resolved when the SHIPPED artefact changes.
- 🔴 **Something the reader sees may not be text at all.** Sixty "Horizontal Line" objects in Word were
  markdown `---` rules rendered as VML rectangles. Every attempt to fix that in a style or a font would
  have failed, because the thing on the page was a drawing. Before treating a rendering complaint as a
  formatting problem, find the object in `word/document.xml` and see what it actually is.
- 🔴 **Write the justification, then test it before it hardens.** A comment in `assemble_3J.py` claimed
  a second bug - a paragraph rendering as a setext H2 - on a correct reading of CommonMark and a wrong
  reading of *pandoc*, which takes setext only from a single-line header. Running the fragment through
  pandoc killed it in one command. A plausible mechanism written into a code comment becomes fact for
  the next reader.
- **Removing the pointer does not remove the thing** when the list is built by DIFFING. Deleting a
  table's placeholder relocates it, in full, into the leftovers appendix. Cutting from the submission
  is `EXCLUDED_TABLES` in `assemble_3J.py`, by name, printed on build. And **cutting from the
  submission is not deleting the artefact**: `Appendix_C_corrections.md` stays on disk because `f5`'s
  C4 and C6 arms read it.
- **A cross-reference that names a SECTION must be re-derived, never remapped.**
- **Dropping a section's heading is not dropping the section**, and the converse also holds - see the
  Table A2 note above. A residue check that looks for the heading is blind both ways.
- **A blind token map across files will corrupt something.** The identifier sweep rewrote 58
  occurrences, garbled prose, and broke file paths inside Sources blocks. Reverted, redone site by site.
- **A check whose meaning flips with its own mode is not a check.** Pin the arm, not the mode.
- **Verify a logged number against the artefact's own columns**, even one that hits a target exactly.
  Do not trust a Progress Log claim, including mine.
- **Residue check and loss check are different checks.** Keep both.
- **Read the gate's own doc before proposing any threshold change.** A basis change that turns FAIL
  into WARN is a band change in disguise. Prefer purely additive fixes.
- **Never count lines with PowerShell** `Measure-Object -Line`; use `wc -l`. `py -3` is the only
  working Python invocation, and prefix it with `PYTHONIOENCODING=utf-8` when a script prints anything
  outside cp1252. **Do not use a bash heredoc for prose containing apostrophes** - it broke a round;
  write the text to a file and `cat` it. `py -3 -c "..."` one-liners have returned empty output in Git
  Bash: write the probe to the scratchpad and run the file.

---

## Hard rules for this phase

- **This is a writing phase. Zero simulation.** No `sbatch`, no cells, no re-runs. Re-rendering a
  figure from frozen aggregates is not simulation, but it is authorisation-gated: say so first.
- **NEVER** run a blocking `srun`, or any Python, on the Speed login node `speed-submit2`. Always
  `sbatch`, always `-t 7-00:00:00`. Flagged three times; one more is account suspension. Irrelevant
  during a writing phase, and that is exactly when it gets forgotten.
- **No band moves, no gate verdict changes, no measured number changes.** The three failing EUI gates
  stay failing; that is the paper's contribution.
- **Archive the predecessor before editing.** Corrections are additive. Guard the copy with
  `[ -s "$BK" ]` in the same command before truncating anything.
- **A reported grep result is not a check.** Read exit codes, and check the pattern compiled.
- **Do not modify `f3`.** Its verdict is the correct answer, whatever it currently reads. It was
  4 PASS / 1 FAIL until the 2026-08-11 replot left the registry stale; it is **3 PASS / 2 FAIL**
  now. Fix the REGISTRY, never the gate.
- **The assistant NEVER creates images.** Author instruction 2026-08-09, now a hard-rule section in
  `GSSCanada-main/CLAUDE.md` and a bullet in `README.md`. Write the prompt; the author generates; you
  install, verify against the INSTALLED file, and report every defect. **Plotting is not drawing** - a
  matplotlib figure rendered from a frozen aggregate is computation and stays yours. 🔴 **A prompt for
  a figure that carries measured numbers must carry those numbers**, in a table, from the frozen
  deliverable, with file, column and source line named.
- **Deep research is external.** Author the prompt; never run the search. Roughly half the citations
  in the returned reports have been fabricated.
- **Never edit a built artefact by hand.** Every change goes into the sources or the build, and is then
  verified against the installed file.
- **Reply in English.** The author writes in French.

---

## The closure ritual, every round, unprompted

Three artefacts plus memory, in the same response, without being asked:

1. **Progress Log** appended to `writing/implementation/3rdJ_paper_TASKS.md`.
2. **THIS file**, at this exact path - `3J_docs_occ_nTemp/Prompts/RESUME.md` - **edited in place**,
   with the predecessor copied to `archive/` first. Not a new file beside it.
3. **The board republished** at its fixed URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>
4. **Memory** updated (`project_3j_paper_writing.md`, and `feedback_gates_must_be_seen_failing.md` if
   a new failure class was found).
