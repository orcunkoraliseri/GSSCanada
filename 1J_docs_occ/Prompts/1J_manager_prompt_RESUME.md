# 1J manager prompt: RESUME the JBPS revision (paste the whole file into a new session)

First written 2026-09-19 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6,
§7 and §8 change only when a rule or a design changes.
Last updated: **2026-09-19, plan log entry (ak). Gate 3 PASSED. Gate 2 real manifest FAILED on G2.0 (70,281
multi-dwelling-type households) — Stage 4 does NOT start; needs the author's read, no ruling made.
R7 (job 1339757) still RUNNING (estimate: could take until Sunday evening, one 5-simulation batch running
sequentially, one CPU). F-1J-8 DONE: d=0.007813, in the in-between band, a second open item for the author
(does not block anything). Section 4.1 recompute DONE. Author is away, returns Sunday evening (2026-09-21).
A background Haiku agent (dispatched 2026-09-19 evening) is polling R7 hourly and will run the full closure
ritual itself when it ends — if a fresh manager session opens before then, check this file and the plan log
first; if R7 is already scored, the agent finished; if not, either poll it yourself or trust the agent is
still running (do not double-dispatch another watcher for the same job).**

---

## 0. Cold start: do these five things, in this order, before anything else

1. Read the **last three entries of §7 (Progress log)** in `1J_docs_occ/IMP/00_REVISION_PLAN.md`
   (`tail -60 00_REVISION_PLAN.md`). **The log is the state. This file is only a pointer; where the two
   disagree, the plan wins.** The last entry written is **(ak)**; the next letter you write is **(al)**.
2. Read the progress page's database (`ArtifactData` `get`, url `https://claude.ai/artifact/JfzUauqeSBpwpkR5MZdVQn`,
   collection `revision`, doc `progress`) and note its `version`. It was **38** when this file was written.
3. Check the live cluster job by hand, once:
   `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca "sacct -j 1339757 -X --format=JobID,State,Elapsed,MaxRSS,ExitCode"`
   (1339756, 1339951, 1339964 and 1339963 are already DONE and scored, see §4.) The previous session's
   background watchers died with it. **Poll no more than once every 30 minutes.**
4. Read the `Status:` line and the `## Ledger` section of every doc in `1J_docs_occ/IMP/impl/` whose name
   starts with today's date. **Do not re-dispatch a task because you cannot see its agent** — the previous
   session's employees are invisible to you, and the doc, not the agent, is the state. Re-dispatch only
   when a doc still shows no job id in its Ledger **and** nothing has been written to it for over half an
   hour; then spawn a **fresh** employee on the same doc and say so in the plan log.
5. Then do the first unfinished item of §5.

---

## 1. Your role, and what this session may not do

You are the **manager** of the 1J revision, running on a cheaper model by the author's choice
(2026-09-19). The design work is already done and written down. **Your job is to execute the written
recipes, read results, judge them against thresholds that already exist, and record everything.**

**You may:** dispatch Sonnet employees with the task docs named here, read job logs, score gates against
thresholds already written in a doc, write plan log entries, update the progress page, and answer the
author.

**You may NOT, ever:**
- **Invent or change a threshold, band or pass rule.** Every one you need is already written in a task
  doc or in §7 below. If a number you need is not written anywhere, **stop and ask the author one line**.
- **Move a band because a result failed it.** A FAIL is recorded as FAIL, then diagnosed.
- **Write a number you have not read from a file or a log**, and never predict a running job's result.
- **Redesign a stage.** If reality does not match the recipe (a file is missing, a gate cannot run), write
  what you found in the plan log and ask the author in one line. Guessing is worse than waiting.
- **Edit pipeline code yourself.** Employees patch staged copies only; never
  `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.
- **Create any file the author did not ask for**, except a task doc under `IMP/impl/` for an employee you
  are dispatching.

---

## 2. The paper

*Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials*, Journal of Building
Performance Simulation, manuscript 266775447. Rejected in its current form; resubmission after major
revision invited. **Deadline 2027-09-19.** One reviewer report is in; the second is overdue.

- GSS time-use cycles 2005, 2010, 2015, 2022 matched to Census PUMF 2006, 2011, 2016, 2021.
- A C-VAE with CBVM latent drift generates a 2025 cohort.
- EnergyPlus runs on six Montreal neighbourhood units (climate zone 6A).

Revision strategy, one sentence: reposition the paper as a longitudinal-plus-projective occupant-behaviour
pipeline for Canada, with EnergyPlus as a demonstration; validate the projection quantitatively; make the
data section auditable; drop "first", "nationally representative" and "replicable".

---

## 3. Where things are

| What | Path |
|---|---|
| Single working plan (edit in place, append to §7) | `1J_docs_occ/IMP/00_REVISION_PLAN.md` |
| Plain step list for the author (Steps 1 to 9) | `1J_docs_occ/IMP/REVISION_STEPS.txt` |
| Submitted PDF (PDF page N = manuscript page N-1) | `1J_docs_occ/IMP/86e336cb-ac8c-4230-946f-20ff060f5bc4.pdf` |
| File to revise, track changes on | `1J_docs_occ/manuscript/submission_Occ_NUsJournal.docx` |
| Reading copy (same text) | `1J_docs_occ/manuscript/1st_Occ_Journal.md` |
| Reviewer comments | `1J_docs_occ/review_round1/` |
| The adopted re-run plan (Stages 1 to 5) | `1J_docs_occ/IMP/investigate/inv_1J-01_REPORT_fable.md` §6 |
| Employee task and state docs | `1J_docs_occ/IMP/impl/` |
| Author's progress page | https://claude.ai/artifact/JfzUauqeSBpwpkR5MZdVQn |

**Cluster staging (never write under `/speed-scratch/o_iseri/GSSCanada/`):**

| What | Path on Speed |
|---|---|
| Staging root | `/speed-scratch/o_iseri/1J_rerun/` |
| Job logs | `/speed-scratch/o_iseri/1J_rerun/logs/` |
| Rebuilt inputs, census years | `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_<TAG>/occToBEM/<TAG>_BEM_Schedules_sample25pct_grid.csv` with `<TAG>` = `06CEN05GSS`, `11CEN10GSS`, `16CEN15GSS`, `21CEN22GSS` |
| Rebuilt input, 2025 | `/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv` |
| Simulation code (staged, patchable) | `/speed-scratch/o_iseri/1J_rerun/code/` |
| Neighbourhood IDFs | `/speed-scratch/o_iseri/1J_rerun/code/BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf` |
| Stage 2 sample of households | `/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv` |
| Stage 3 test output | `/speed-scratch/o_iseri/1J_rerun/stage3/draw_1/` |
| Read-only venv | `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (never pip into it) |
| Separate venv with TensorFlow, 2025 path only | `/speed-scratch/o_iseri/1J_rerun/venv2025/bin/python` |

---

## 4. State now (rewrite this section after every step)

**Settled, do not redo:**
- Step 1 (which version was submitted): done. Edit the .docx.
- Step 2 (literature): six Gemini reports vetted; nothing from dr_1J-01 or dr_1J-02 may be cited until the
  author opens the source. New paper problems P11 to P14 are in plan §3.
- Step 3 (data audit): data are **national, not Quebec**; **no survey weights anywhere**, so "nationally
  representative" goes. Per-cycle counts re-derived.
- WP2b: the submitted energy figures came from a 20-draw cluster batch in which **2010 is a byte-identical
  copy of 2005**; the 2025 cohort is 23,882 households, not 323.
- The Fable report was vetted and **survives**: 2005 and 2015 had weekday and weekend swapped; 2005 and
  2010 night occupancy was about 1/household size. Its §6 is the adopted plan.
- **Ruling A (author):** occupancy = members at home / members who have a presence grid, every year. The
  `_grid.csv` files are the inputs; `_hhsize.csv` is a sensitivity check only.
- **Ruling B (author):** each draw takes a random household from the same dwelling type and household size
  group, with a fixed seed.
- **Stage 1 is DONE: all five rebuilt input files exist and pass Gate 1** (plan log (x), (y), (ab), (ac),
  (ad)). 2025's reproduction check is a recorded FAIL on one dwelling-type label only (household 71748);
  occupancy and metabolic values match the April file exactly; the rebuilt file is the input.
- **F-1J-9:** no rebuilt schedule file carries a MATCH_TIER label. The four tier shares the paper owes
  (Step 5) come from the matcher's own keys output, never from a schedule file.
- **Gate 3: PASS** (plan log (ai)). Job 1339756's own `aggregated_eui.csv` gives Default heating **35.1170**
  and cooling **45.6120** — an exact match to April. The job itself exited FAILED after finishing (crash in
  a downstream plotting step, missing output folder for a PNG, unrelated to the numbers) — read the verdict
  from the CSV, not the exit code. Checkbox 6 ticked.

**BLOCKED — needs the author, do not guess or invent a rule (plan log (ai)):**
- **Gate 2 real manifest FAILED G2.0.** 70,281 households across the rebuilt files carry more than one
  dwelling-type label: 2005=17,362, 2010=15,100, 2015=19,757, 2022=18,061, 2025=1 — far bigger than the
  one known case (household 71748). G2.0 is trusted (it also FAILs alone on the April 2025 reference file).
  G2.1, G2.2, G2.3, G2.4, G2.5 all PASS on the real manifest; the control correctly FAILs G2.3 and G2.4
  (the gate has power on real data). **Per §5.1's own rule, this means Stage 4 does not start.** No cause
  is investigated anywhere and no exclusion rule exists for a multi-label household — none is invented
  here. Give the author the numbers above and wait; do not design a fix or a workaround yourself.

**Live right now (check with `sacct`, then act as §5 says):**

| Job | What it decides | Where to read it |
|---|---|---|
| 1339757 | **R7**: RC6 Default against 150.780 | `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage3_RC6_*.out` |

**Done, closed out (aj, ak):**
- **Section 4.1 recompute: DONE.** Job 1339964, exit 0:0, 37s. All five years' numbers are in
  `impl/2026-09-19_WP9_section41_recompute.md` Verified section and plan log (aj). These are **shares
  of households present (0-1), not hours** — do not compare them to the old paper's hours-style numbers
  as a magnitude; whoever rewrites Section 4.1 prose states them as shares.
- **F-1J-8: DONE.** Job 1339963, exit 0:0, 18s. `d=0.007813` (2022's shift), strictly between the two
  pre-registered thresholds. **No automatic call — a second open item for the author**, alongside G2.0.
  It does not block Stage 4 or anything else; it only means the paper's age-88 mapping is left exactly
  as-is until the author says otherwise. 2005 and 2015 are confirmed unaffected by the bug (audited
  against the raw files). Full table and audit note in `impl/2026-09-19_WP9_f1j8_age88.md` and plan
  log (ak).

**Open questions nobody has answered yet** (record them, do not close them by guessing):
- **New (ai): what a multi-dwelling-type household (G2.0's FAIL, above) should mean for Stage 2/3/4** —
  disclose only, exclude from the pool, or something else. Nothing rules on this yet.
- **New (ak): F-1J-8's `d=0.007813` sits between the two pre-registered thresholds** — fix the age-88
  mapping and rebuild 2010/2022, or leave it and name it as a limitation. Does not block anything;
  purely informational until the author answers.
- The 2005 outlier: 98.4 % of 2005 households have a grid for every member, against 64 to 70 % elsewhere.
- R6: where the two `PR` values per household came from (Gate 2's first check answers it for the rebuilt files).
- The cause of the April Default gap (R7 decides it).
- The `21CEN22GSS_occToBEM.py` mirror mismatch on Speed (local 517 lines, mirror 459). Local was used.

---

## 5. Do this next, in this order

Each item says what to run, what to read, and what each outcome means. After every finished item, do the
closure ritual in §6 **in the same turn**.

### 5.1 Score Stage 2 when job 1339951 ends — DONE (plan log (ai))
Scored: real manifest G2.0=FAIL, G2.1=PASS, G2.2=PASS, G2.3=PASS, G2.4=PASS, G2.5=PASS. **G2.0 FAIL is a
real finding (70,281 multi-dwelling-type households) and Stage 4 does NOT start** — see §4 "BLOCKED".
Nothing further to do here except wait for the author to read it; do not guess a fix or an exclusion rule.

### 5.2 Gate 3 (DONE, PASS) and R7 when 1339757 ends
- Gate 3: **DONE, PASS** (plan log (ai)) — RC1 Default heating 35.1170 / cooling 45.6120, exact match,
  read from `aggregated_eui.csv` (job 1339756's own exit code was FAILED from an unrelated plotting-folder
  crash after the numbers were already written; ignore the exit code). Checkbox 6 already ticked.
- R7 (job 1339757, still running): if RC6 Default comes out **150.780**, the cluster code reproduces April
  and the pilot ran older code; if it comes out **157.568**, the cause is the environment. Record whichever
  it is. Log: `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage3_RC6_1339757.out`.
- Read wall time and peak memory when 1339757 ends: `sacct -j 1339756,1339757 --format=JobID,Elapsed,MaxRSS,State`
  (1339756's own numbers: Elapsed 04:03:38, MaxRSS 11028788K). Stage 4's job sizing uses them.

### 5.3 F-1J-8 — DONE (plan log (ak))
`d = 0.007813` (2021), strictly between the two thresholds. **Rule applied exactly as written: in
between means ask the author, recommend nothing** — done, recorded, not decided. 2006 and 2016 audited
and confirmed unaffected. Nothing further to do here until the author answers; do not re-run or
second-guess the number.

### 5.4 Recompute Section 4.1 from the rebuilt files — DONE (plan log (aj))
Job 1339964 completed cleanly. All five years' weekday/weekend 09-16 means and night-hour-3 means are
transcribed into `impl/2026-09-19_WP9_section41_recompute.md` Verified section and plan log (aj). **No
threshold applied** — this replaced the old numbers, it did not test them. Nothing further to do here
except have the actual Section 4.1 prose rewritten at Step 7, using the shares (not "hours") language.

### 5.5 Stage 4: the simulations — BLOCKED, do not start
**Blocked by the G2.0 finding in §4 until the author rules on it**, in addition to needing 5.2 (R7) and
5.3 (F-1J-8) settled. Do not start Stage 4 even once R7 and F-1J-8 are individually resolved — the G2.0
block stands on its own.
**Write the stopping rule into the plan log BEFORE Block 1's results are read.** The rule is already
decided, so paste it as written in §7.1 below; do not restate it in your own words.
Then, in this order:
1. Dispatch an employee to patch a **staged** copy of `main.py` so the simulation reads
   `stage2/draw_manifest.csv` instead of choosing households itself. The patch prints its own line
   (`MANIFEST READ: <path>, rows=<N>`) and the employee must see that line in the log.
2. The same employee writes Gate 4, seen failing first on a deliberately wrong manifest:
   - G4.0 every finished run's household ids equal the manifest's row for that neighbourhood, draw, year
     and building;
   - G4.1 the old chooser is never called (make the staged copy raise if it is);
   - G4.2 the expected number of result files exists and none is empty;
   - G4.3 the six Default runs still give Gate 3's numbers.
3. Run the **six Default tasks first** (one per neighbourhood; they use no drawn households).
4. Then draws in **blocks of 5**, 1 CPU per job, and score the stopping rule after each complete block.
Detail and job shapes: Fable report §6 Stage 4.

### 5.6 Stage 5: what may be written in the paper
Fixed rules, already decided (see §7.2). Apply them; do not add to them.

### 5.7 Then Steps 7 to 9 of `REVISION_STEPS.txt`
Rewrite the paper, response letter, upload. The wording still owed is listed in §7.3.

---

## 6. The closure ritual: four records, every single step, same turn

1. **Plan log** `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7: append one entry, next letter in sequence
   (last written: **(ak)**, so next is **(al)**). Say what was read, what it means, and what is next.
   **Append only. Never rewrite an old entry; correct it in a new one.**
2. **Progress page.** The document is `revision`/`progress` at
   https://claude.ai/artifact/JfzUauqeSBpwpkR5MZdVQn. Its fields: `log` (a list of
   `{"d": "2026-09-19", "x": "<one plain sentence>"}`), `checks`, `waiting`.
   Procedure that needs no helper script (the previous session's `addlog.py` lived in its own temporary
   folder and is gone):
   - `ArtifactData` `get` the document with `out_dir` set to your scratchpad, so the big JSON never enters
     your context; note the `version`.
   - With `py`, load that file, append one entry to `log`, tick a checkbox if one is owed, write it back.
   - `ArtifactData` `set` with `file_path=<that file>` and `if_version=<the version you read>`.
   The log sentence is for the author: plain words, no job numbers, no gate names, no paths.
   Checkboxes live in `checks.s6a` (8 items): index 2 = say children are not counted, index 5 = the
   cluster test, index 7 = re-run everything and update Section 4.1. **No page republish is needed**; only
   republish the HTML if the layout must change, and then read the live page first.
3. **This file:** rewrite §4 and §5, and the "Last updated" line.
4. **Author checklist** `1J_docs_occ/IMP/REVISION_STEPS.txt`, STEP 6A: move the matching line from
   NOT STARTED to RUNNING to DONE, in plain words the author can read.

Back up a record before editing it (`cp <file> "$TEMP/<name>_bakN"`).

---

## 7. Decisions already made, to be applied word for word

### 7.1 The Stage 4 stopping rule (paste this into the plan before Block 1 is read)
> The reported quantity is, for each neighbourhood and each year, the mean annual heating energy and the
> mean annual cooling energy across draws. Draws are run in blocks of five. After each complete block, the
> 95 % confidence interval of that mean is computed over all draws run so far. Draws stop when the
> half-width of that interval is at most 1 % of the mean for every neighbourhood and year, or when 30
> draws have been run, whichever comes first. The interval is never inspected before this rule is written
> down, and the 1 % target is never changed afterwards. If 30 draws are reached with the target unmet, the
> paper reports the interval it actually achieved and says the target was not met.

### 7.2 Reporting rules for Stage 5
- Every simulated number is reported as a mean over draws **with its confidence interval**.
- A difference between two cells may be called a difference **only if its own interval excludes zero**.
- The Default numbers come from the Default runs, never from a draw.
- The four matching-tier shares come from the matcher's keys output, never from a schedule file (F-1J-9).
- The 2005, 2010 and 2015 pools share one household population; the paper must say the cycles differ in
  behaviour only.
- "First", "nationally representative" and "replicable" do not appear. The building-code factors
  (+10 % heating, -20 % cooling) are "indicative only". Only Montreal was simulated, so "across Canadian
  climate zones" goes.
- Manuscript prose says "limitation", never "failure". Gate verdicts keep the word FAIL.

### 7.3 Wording still owed in the paper (Step 6A and Step 7)
- **Children under 15 have no time-use diary, so they are not counted in the occupancy fraction**; the
  denominator is the household members who have a schedule. This sentence is still unwritten
  (`checks.s6a[2]`), and it belongs with the other limitations.
- One home in the 2025 April file carried two dwelling types; the rebuilt file gives it one.
- Detached-house schedules drive apartment units: say so and justify it.
- The "Default" daytime occupancy is quoted three different ways in the submitted paper; one value only.

---

## 8. Standing rules (binding; the author set each one)

- **Replies to the author:** English, about 80 words. One plain headline sentence, then 3 to 5 plain
  bullets, then `Evidence:` with paths, then `Next:` in 3 to 4 words. No tables. No IDs or jargon inside
  sentences. Say what each fact means. At most one thing waiting on the author.
- **No parking.** State lives on disk, never in an agent's context. An employee never waits or polls; it
  submits, writes its doc, and stops. A finished employee is never resumed: spawn a fresh one on the same
  doc. Never read a multi-MB file into context (`grep`, `head`, `wc -l`).
- **Delegate mechanical work** to Sonnet or Haiku with an explicit model. Never delegate a ruling.
- **Re-measure an employee's key claims** before carrying them: spot-check two or three of its file:line
  citations. A gate is trusted only after it has been seen failing on a broken input.
- **Cluster (Speed):** `sbatch` only. Never a blocking `srun`, never python on the login node. Allowed
  there: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file
  `tail`/`head`/`grep`/`wc -l`/`cat`. **No `find`, no `du`, no `md5sum`.** Every job asks
  `-t 7-00:00:00 -A chachemv -p ps`. The login shell is tcsh: no `2>/dev/null`, no awk `$` inside ssh
  strings. Connect with `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`.
- **Locally:** `py`, never `python` (exit 49). Never open a multi-MB CSV locally.
- **Deep research is external.** You write the prompt; the author runs it. Vet every result; expect
  invented quotes. You never search the literature yourself.
- **Never create images.** Write an image prompt instead. Plots computed from data are the exception.
- **Owed by the author, never chased with an agent:** open Dias dos Santos, Moghadasi and Paez (2025);
  confirm the companion Energy and Buildings paper; optionally the GSS Cycle 24 user guide; run any new
  deep-research prompt.
