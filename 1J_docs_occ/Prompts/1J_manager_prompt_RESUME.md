# 1J manager prompt: RESUME the JBPS revision (paste the whole file into a new session)

First written 2026-09-19 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6,
§7 and §8 change only when a rule or a design changes.
Last updated: **2026-09-24 ~07:10 EDT (status check only: 6/36 draws done, 55/56 CPUs in use, nothing else moved; see first bullet). Before that 2026-09-23 ~19:15 (CPU budget raised to 56, throttles changed); last plan log entry (az), next (ba). Gate 4 PASS (all six baselines equal April,
diff 0), workers check PASS (5 workers = 1 worker, 3.3x faster), swap+probe PASS. Step 4d draws SUBMITTED and
RUNNING. Session closed after this; nobody is polling — the next session starts from the "first action" list below.**
- **Status check 2026-09-24 06:52 EDT (no new plan-log entry): 6 of 36 draw tasks DONE, exit 0:0; 11 RUNNING = 55 CPUs (cap 56, full).**
  Done: LIGHT `_0`,`_1`,`_2`,`_4`; HEAVY `_1`,`_3`. Running: LIGHT `_3`,`_5`-`_8` (throttle 5 full), HEAVY `_0`,`_2`,`_4`-`_7`
  (throttle 6 full). HEAVY `_8`-`_11` still PENDING, so no throttle shift yet (step 0). Block 1 waits on LIGHT `_3`
  (RC4 b1, 19:15 h) and HEAVY `_0` (RC5 b1, 36:57 h); all scorers PENDING (Dependency). `histnu` = 4 x 1 CPU; account
  59/64. Newly done logs LIGHT `_2`,`_4`, HEAVY `_1`,`_3` grepped: all `WP11 EXTRACT VERDICT: VERIFIED` and E5 PASS
  (DRAW START 1/6/1/6). Progress page db **53 -> 54** (sim 6/36 + log line 2026-09-24).
- **CPU budget change 2026-09-23 ~19:00 EDT (author, plan log (az)): 1J now gets 56 CPUs on Speed; `histnu` cut to 8 (its 4 arrays `%2`).**
  Progress at ~19:00: 3 of 36 draw tasks done and VERIFIED (LIGHT `_0`, `_1`; `_2` = RC3 block 1 log shows VERIFIED,
  was still finishing in `squeue`); LIGHT `_3` (RC4 b1) and HEAVY `_0`-`_3` RUNNING. Block 1 expected ~2026-09-24 midday.
  Done by `scontrol update`: LIGHT 1342400 `ArrayTaskThrottle=5` (was 2), HEAVY 1342401 `ArrayTaskThrottle=6` (was 4)
  = 11 tasks x 5 CPUs = 55 CPUs; read back with `scontrol show job`. New tasks start only as the 32 running `histnu`
  tasks finish (account cap `cpu=64`), not instantly.
  - Measured round length (one simulated year, 5 draws in parallel, minutes, from the logs): RC1 ~45, RC2 ~146,
    RC3 ~171, RC4 ~167, RC6 ~308, RC5 ~368. Parallel costs little (single default run: RC1 40, RC5 331). A task =
    1 default run + 5 years: RC1 ~6 h, RC2 ~18 h, RC3/RC4 ~19 h, RC6 ~32 h, RC5 ~38 h. ~640 task-hours left at 19:00.
  - Estimate (not a result): all 30 draws done about **2026-09-26** (vs ~09-30 at the old `%2`/`%4` split). When HEAVY
    has no pending tasks left, raise LIGHT's throttle so freed HEAVY slots go to LIGHT (1J total stays <= 11 tasks).
  - Offered, NOT taken: skipping each task's default re-run (the E4 check; author's call); local CPUs (Windows vs
    Linux numbers; RC5/RC6 need 90G).
- *(Older; its "cap stays 32" line is superseded by the 56-CPU bullet above)* **Status check 2026-09-23 ~14:45 EDT (no new plan-log entry): 2 of 36 draw tasks DONE and VERIFIED; STILL WAITING FOR BLOCK 1.**
  Read by `sacct` (about 21 h after submission at ~18:00 on 09-22) and by grepping the logs:
  - LIGHT 1342400: `_0` (RC1 block 1) COMPLETED 05:57:55, exit 0:0; `_1` (RC2 block 1) COMPLETED 17:42:15, exit 0:0.
    Both logs show `WP11 EXTRACT VERDICT: VERIFIED`; `_0` also shows `WP11 DRAW START` (E5 PRESENT).
    `_2` (RC3 block 1) RUNNING 14:49 h, `_3` (RC4 block 1) RUNNING 3:05 h (started when `_0`/`_1` finished, `%2`).
  - HEAVY 1342401 `_0`..`_3` RUNNING 20:47 h each. **E5 now PASS on all four:** `WP11 DRAW START: 1` in `_0`/`_1`,
    `WP11 DRAW START: 6` in `_2`/`_3` (RC5/RC6 blocks 1 and 2). Each is inside a repeated `[SIM] Running... [0/5 complete]`
    round of about 2.5 h or more (RC5/RC6 sims are slow); a task ends only after all its draws.
  - Draw tasks 4+ of each array PENDING (JobArrayTaskLimit); scorers 1342408-1342413 all PENDING (Dependency).
    Nothing FAILED or CANCELLED. Block 1 completes only when LIGHT `_2`/`_3` and HEAVY `_0`/`_1` all finish.
  - **Not slower than planned:** plan said ~1.5 days for block 1 and ~4.5 days for all 30 draws. Do not read the
    wait as a fault; the 32-CPU cap (6 tasks at once) is the limit. **More CPUs would cut total time (~2x for 64)
    but NOT block 1 (all its tasks already run), and later blocks may be cancelled by a STOP.** The author was
    told this and did not raise the cap; it stays 32 (author's rule, `histnu` shares the rest).
  - One `ssh` call dropped ("Connection closed by 132.205.2.12 port 22", empty output); a retry worked. An empty result
    is a failed query, never "no jobs" (see cluster memory §14).
  - **Progress page updated: db version 51 -> 52** (sim tracker now 2 of 36, new log line dated 2026-09-23; backup of
    v51 was in the session scratchpad only). Plan log and REVISION_STEPS.txt were NOT touched this check.
  - **Author is away; next session: run the "first action" sacct below (not before ~30 min after 14:45), then follow steps 1-3.**
- *(Older, superseded by the bullet above)* **Status check 2026-09-22 ~20:30 EDT (no new plan-log entry; nothing finished yet): WAITING FOR BLOCK 1.**
  Six tasks RUNNING 2:32 h, 30 CPUs (read from each log's first line): LIGHT _0 = RC1 block 1, _1 = RC2 block 1;
  HEAVY _0 = RC5 block 1, _1 = RC6 block 1, _2 = RC5 block 2 (draws 6-10), _3 = RC6 block 2. Block 1 is complete
  only after LIGHT _2/_3 (RC3/RC4 block 1) also run; they start when LIGHT _0/_1 finish (`%2`). Rest PENDING
  (JobArrayTaskLimit), scorers PENDING (Dependency); nothing FAILED/CANCELLED.
  - Log path is `/speed-scratch/o_iseri/1J_rerun/logs/wp11_draw_<array>_<i>.out` (NOT `stage4/wp11/logs/`;
    that folder holds only `quota_*.txt`). Scorer logs: same folder, `wp11_scorer_<jobid>.out`.
  - **E5 half-seen:** `WP11 DRAW START: 1` is PRESENT in both LIGHT logs (after the one-worker default sim,
    "Default EUI: 145.3" for RC1). The four HEAVY logs do not show it yet because each task first re-runs its
    one-worker default sim (`[SIM] Running... [0/1 complete] Elapsed: 151:30` at 20:30); the START line prints
    only after that. Re-grep the HEAVY logs at the next check; absent once iterations begin = E5 FAIL.
  - The watcher that polled sacct every 30 min lived in the old chat session; it dies when that session
    closes. A returning session re-runs the "first action" sacct below by hand (or re-arms its own watcher).
- **Author ruling (ao): remove only the code-88 person, keep the home; state it as a limitation.** WRITTEN
  in the manuscript at the sampled-population share (2.8 % 2010, 5.4 % 2022), never the raw-census 4.1 % /
  10.0 % (see §7.3).
- **G2.0: kept and disclosed (an).** Stays a recorded FAIL, no longer blocks anything.
- **Live now (submitted 2026-09-22 ~18:00 EDT, plan log (ay)):**
  - LIGHT array **1342400** (RC1-RC4, 24 tasks, `%2`, `-c 5`, 56G) and HEAVY array **1342401** (RC5-RC6, 12 tasks,
    `%4`, `-c 5`, 90G): 6 tasks RUNNING at submission = 30 CPUs (cap 32). **Since 2026-09-23 ~19:00 (az): LIGHT
    `%5`, HEAVY `%6` = 11 tasks = 55 CPUs, cap 56.**
  - Scorers **1342408-1342413** = blocks 1-6, each `afterany` on all tasks of blocks 1..b. On STOP a scorer
    `scancel`s later tasks and scorers itself (IDs from `stage4/draws/job_ids.txt`).
  - Rough time (estimate, not a result): block 1 ~2026-09-24 midday; all 30 draws ~2026-09-26 at 11 tasks (az).
- (Unrelated `histnu` arrays under `/nfs/speed-scratch/rhlab/hist_nu_z7a` are not 1J — they belong to the
  author's idf_reader project, now held to 8 CPUs; never scancel or change them.)
- Progress page db version **54** (2026-09-24 ~07:00: `sim` tracker 6/36; v53 = 3/36 + CPU-change line; v52 = 2/36).
- **Author instruction in force:** "continue until the end" — carry Stage 4 through on your own (score blocks),
  closure ritual after every step; ask the author only if a fix is itself a design choice.

**A fresh session's first action:** `sacct -j 1342400,1342401,1342408,1342409,1342410,1342411,1342412,1342413 -X
--format=JobID,JobName%24,State,Elapsed,ExitCode` on Speed (no more than once every 30 min). A draw task's exit
code IS its verdict (0 = VERIFIED, 1 = not, 3 = disk/md5 pre-flight stop); the runner inside it still hits the
harmless plotting crash, printed as `RUNNER EXIT: 1`. Also run `squeue -u o_iseri -h -n wp11_draw_task -t R` and
count: it should have risen from 6 toward 11 as `histnu`'s old tasks ended (if still 6 after ~12 h, check
`scontrol show job 1342400` / `1342401` still read `ArrayTaskThrottle=5` / `=6`). Then, as each lands:
  0. **Throttle shift (az):** once `squeue` shows HEAVY 1342401 with no PENDING tasks left, raise LIGHT with
     `scontrol update JobId=1342400 ArrayTaskThrottle=<11 - running HEAVY tasks>` so 1J keeps 11 tasks (55 CPUs);
     never above 11. Log it in the plan.
  1. **First draw task done** -> `grep` its log (`logs/wp11_draw_<array>_<i>.out`) for `WP11 DRAW START: <D>` (must be
     PRESENT, E5) and `WP11 EXTRACT VERDICT: VERIFIED`; any task not VERIFIED -> read why, rerun that one task only.
  2. **Scorer b done** (`logs/wp11_scorer_<id>.out`) -> read `STOPRULE SUMMARY: block=b ... VERDICT=...` and
     `stage4/draws/stoprule_block_<b>.csv`. STOP -> Stage 4 done at n = 5b (check the scancels it printed);
     CONTINUE -> wait for next block; NOT_EVALUABLE -> diagnose, rerun the missing task, rescore; block 1 also
     carries the C1 control (draw 1 = `default/draw_1`), NOT_EVALUABLE there means nondeterminism: stop and
     write it up. CAP_REACHED_TARGET_UNMET at b = 6 -> report the achieved intervals (§7.1).
  3. Plan log entry per scorer read, closure ritual.
---

## 0. Cold start: do these five things, in this order, before anything else

1. Read the **last three entries of §7 (Progress log)** in `1J_docs_occ/IMP/00_REVISION_PLAN.md`
   (`tail -60 00_REVISION_PLAN.md`). **The log is the state. This file is only a pointer; where the two
   disagree, the plan wins.** The last entry written is **(az)**; the next letter you write is **(ba)**.
2. Read the progress page's database (`ArtifactData` `get`, url `https://claude.ai/artifact/JfzUauqeSBpwpkR5MZdVQn`,
   collection `revision`, doc `progress`) and note its `version`. It was **53** when this file was last updated (2026-09-23 ~19:00, CPU-budget log line + sim 3/36; 51 at first writing)
   (the document now also carries a `sim` field: `{done, total, label, note, updated}`, read by the page's
   new tracker box — keep it when you next write the whole document, or update `done`/`total`/`note` if a
   different job's simulation count becomes the one worth showing).
3. **Live jobs:** see the "Live now" block and "first action" list at the top of this file (Stage 4d
   draw arrays and the six block scorers). Poll with `sacct` no more than once every 30 minutes. The
   (ao) F-1J-8 chain is DONE and scored. (Unrelated `histnu` array under `/nfs/speed-scratch/rhlab/hist_nu_z7a`
   is not 1J; confirm by `WorkDir`, then ignore.)
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
- **R7: DONE** (plan log (am)). Job 1339757's `aggregated_eui.csv` gives RC6 Default heating **150.7800**
  and cooling **26.2210** — heating matches the 150.780 threshold exactly, so **the cluster reproduces
  April; the pilot ran older code**, not an environment cause. Same FAILED-exit-but-numbers-are-good pattern
  as Gate 3 (5/5 sims succeeded, CSV written, crash was the same unrelated plotting-folder issue). Wall
  time/memory read: RC1 04:03:38 / 11,028,788K, RC6 1-04:12:44 / 38,758,716K.

**RULED (plan log (an)) — read this before touching Stage 2 or Stage 4:**
- **G2.0 (70,281 multi-dwelling-type households, 2005=17,362, 2010=15,100, 2015=19,757, 2022=18,061,
  2025=1): author says KEEP and DISCLOSE.** No exclusion. `G2.0` stays a recorded FAIL (gate verdicts keep
  FAIL; the paper's prose says "limitation"). This no longer blocks Stage 4 by itself — `G2.1-G2.5` still
  need to PASS, which they already did on the current manifest (plan log (ai)).
- **F-1J-8 (age code 88 mapped into 75+, d=0.007813 in the in-between band): author says FIX AND REBUILD,
  2010 and 2022 only** (2005/2015 unaffected by construction; 2025 different pipeline, unaffected).

**RULED (ao): age code 88 -> remove the person, keep the home, disclose as a limitation.** Fix = P6
(staged copies only): P6a maps 88 -> 95 at alignment without dropping; P6b reuses the existing
`<year>_LINKED.csv` (assembly is unseeded, so re-assembling would reshuffle every home); P6c drops
`AGEGRP == 95` right after the seeded 25 % sample. Same sampled homes; only homes whose every sampled
member is code 88 vanish, and they are counted. Old outputs are backed up as `*.preF1J8`.

**DONE (ap):** the F-1J-8 fix-and-rebuild chain (`impl/2026-09-21_WP9_f1j8_fix_rebuild.md`) completed and
was verified: T0 `1341248` -> rebuilds `1341249` (2010), `1341250` (2022) -> age check `1341251` (T3
PASS both years, M2=0, home-set diff matches P6c exactly) -> Stage 2 `1341252` (Gate 2 real manifest
`G2.0` FAIL accepted, `G2.1`-`G2.5` PASS). Gate 1 checked, all PASS both years both files. Persons
dropped 1,885 (2010) / 3,844 (2022), homes emptied 39 / 119. **Sampled-person totals read directly from
the matched-keys files (`wc -l` on `11CEN10GSS_Matched_Keys_sample25pct.csv` = 66,170 lines / 66,169
persons after drop, and `21CEN22GSS_Matched_Keys_sample25pct.csv` = 67,724 / 67,723 after drop): total
sampled persons before drop = 68,054 (2010), 71,567 (2022); limitation share = 1,885/68,054 = 2.8 %
(2010), 3,844/71,567 = 5.4 % (2022) — never the raw-census 4.1 % / 10.0 %.** The 2022 "+4 persons" gap
noted at the (ao) addendum was never chased further; it is immaterial to the limitation share and does
not block anything.
**Limitation sentence WRITTEN** in `manuscript/1st_Occ_Journal.md`, Section 5 Discussion, folded into the
existing "Limitations include..." sentence: cites 2.8 %/5.4 % of the sampled population and 39/119
emptied households, states 2005/2015 unaffected.

**Stage 4 STARTED (ar), blocker found and fixed (as/at):** stopping rule (§7.1) pasted into plan log (ar)
before any result is read. First employee found the manifest (built from Stage-1 rebuilt grid files)
disagreed on `PR`/region with the still-April-staged schedule files (0/6 neighbourhoods would succeed) and
correctly stopped rather than guessing which file generation was right. **Manager ruled (as): re-stage from
the rebuilt grid files** (they carry this revision's own occupancy fixes; Default numbers are unaffected
either way; Gate 3's April `aggregated_eui.csv` stays a valid frozen comparison target). A second employee
did the re-stage (archive-first), re-ran the cheap probe and got **6/6** (job 1341383), then submitted the
real chain: **1341388** selftest (COMPLETED) -> **1341389-1341394** six Default jobs RC1-RC6 (RUNNING,
~1h20m in as of this check) -> **1341395** Gate 4 real scoring (PENDING on Dependency, will start itself).
**Superseded (ay):** 1341395 was replaced by 1342160; Gate 4 scored all PASS; step 4d submitted and running
(see the top of this file and §5.5). Still waiting on the author, not blocking:
deep-research prompts `IMP/deepResearch/dr_1J-07` and `dr_1J-08` (missing-age handling); vet any returned
report before quoting it.

**Done, closed out (aj, ak, am):**
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
- The 2005 outlier: 98.4 % of 2005 households have a grid for every member, against 64 to 70 % elsewhere.
- R6: where the two `PR` values per household came from (Gate 2's first check answers it for the rebuilt files).
- The cause of the April Default gap (R7 decides it).
- The `21CEN22GSS_occToBEM.py` mirror mismatch on Speed (local 517 lines, mirror 459). Local was used.

---

## 5. Do this next, in this order

Each item says what to run, what to read, and what each outcome means. After every finished item, do the
closure ritual in §6 **in the same turn**.

### 5.1 Score Stage 2 when job 1339951 ends — DONE (plan log (ai)); ruling applied (an)
Scored: real manifest G2.0=FAIL, G2.1=PASS, G2.2=PASS, G2.3=PASS, G2.4=PASS, G2.5=PASS. Author ruled (an):
**keep the multi-dwelling-type households, disclose as a limitation.** `G2.0`'s FAIL is now accepted and
expected, not a blocker. This manifest is nonetheless stale for Stage 4 once 2010/2022 are rebuilt under
F-1J-8's fix (5.5) — it will need rebuilding and re-scoring at that point, same six checks, same expected
pattern (G2.0 FAIL, G2.1-G2.5 PASS).

### 5.2 Gate 3 and R7 — both DONE (plan log (ai), (am))
- Gate 3: **DONE, PASS** (plan log (ai)) — RC1 Default heating 35.1170 / cooling 45.6120, exact match,
  read from `aggregated_eui.csv` (job 1339756's own exit code was FAILED from an unrelated plotting-folder
  crash after the numbers were already written; ignore the exit code). Checkbox 6 already ticked.
- R7: **DONE** (plan log (am)) — RC6 Default heating 150.7800 / cooling 26.2210, exact match to the
  150.780 threshold: **the cluster reproduces April; the pilot ran older code.** Same ignore-the-exit-code
  pattern as Gate 3. Wall time/memory read: RC1 04:03:38 / 11,028,788K, RC6 1-04:12:44 / 38,758,716K —
  kept for Stage 4 job sizing. Nothing further to do here.

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

### 5.5 Stage 4: the simulations — 4a/4b/4c DONE (Gate 4 PASS, (ay)), 4d RUNNING (ay)
1. **Age-88 rule: ANSWERED (ao), fixed and rebuilt (ap).** Remove the person, keep the home. Done.
2. **Rebuild chain scored (ap), all conditions met:** P6a/P6b/P6c/P5 lines PRESENT both years; Gate 1 PASS
   on both files; age-88 re-measurement gives 0 affected households in 2010 and 2022 (seen failing at
   1,782 / 3,502 pre-fix); old-minus-new sampled homes equals P6c's "homes emptied" count exactly (39 /
   119), no new home appeared.
3. **Gate 2 on the rebuilt manifest: matches the expected pattern exactly** — `G2.0` FAIL (accepted, (an)),
   `G2.1`-`G2.5` PASS.
4. **4a (manifest patch) and 4b (Gate 4, seen failing first) DONE.** A schedule-file mismatch was found
   (manifest vs still-April schedules disagreed on `PR`/region, 0/6 neighbourhoods would succeed), ruled on
   by the manager (as: re-stage from the rebuilt grid files, not April), fixed and verified 6/6 (at).
   **4c DONE (ay): Gate 4 `G4.0-G4.3` all PASS**, all 12 Default numbers equal April (diff 0). Workers check
   PASS (5 workers = 1 worker). Swap+probe PASS.
   d. **4d RUNNING (ay).** LIGHT 1342400, HEAVY 1342401, scorers 1342408-1342413; `--mem` 56G/90G derived in plan
      log (ay). Throttles raised to `%5`/`%6` (55 CPUs, cap 56) in (az). Design: plan log (aw), binding notes (ax), task doc `impl/2026-09-22_WP11_stage4d_draws.md`.
      Read each scorer's `STOPRULE SUMMARY` as it lands (see the "first action" list at the top). Draws after
      the stopping block never enter any reported number. When a STOP (or CAP) verdict is read, Stage 4 is
      done: go to 5.6.
Detail and job shapes: Fable report §6 Stage 4.

### 5.6 Stage 5: what may be written in the paper
Fixed rules, already decided (see §7.2). Apply them; do not add to them.

### 5.7 Then Steps 7 to 9 of `REVISION_STEPS.txt`
Rewrite the paper, response letter, upload. The wording still owed is listed in §7.3.

---

## 6. The closure ritual: four records, every single step, same turn

1. **Plan log** `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7: append one entry, next letter in sequence
   (last written: **(ao)**, so next is **(ap)**). Say what was read, what it means, and what is next.
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
- **Age code 88 (ruling (ao)), a limitation: WRITTEN (ap).** `manuscript/1st_Occ_Journal.md`, Section 5
  Discussion, folded into the "Limitations include..." sentence. Quotes the share of the SAMPLED persons
  removed — 2.8 % (2010, 1,885/68,054) and 5.4 % (2022, 3,844/71,567) — never the raw-census 4.1 % /
  10.0 %; states homes emptied 39 (2010) and 119 (2022); states 2005 and 2015 are unaffected.
- **Multi-dwelling-type households (ruling (an)), a limitation:** 70,281 households carry more than one
  dwelling type across their records; they are kept in the drawing pool.
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
- **CPU budget (author, 2026-09-22): 1J uses at most 32 CPUs at once**, counting running and pending 1J
  jobs; the rest of the allocation belongs to `histnu`. Size every 4d block to fit (e.g. 5-worker jobs:
  at most 6 at a time).
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
