# 2J manager prompt — RESUME the Applied Energy resubmission (paste whole into a new session)

First written 2026-09-15 by the outgoing manager session. **Kept current: the manager rewrites §2 and §3
after every task completion** (author request, 2026-09-15). Last updated: **2026-09-16 morning**, after the
first overnight cluster read. Nothing was collected between (bc) and this update: the outgoing session only
refreshed the progress bars (checklist Version 29) and confirmed that no job has failed. Every step in section 3
is still owed.
Model: Opus (manager). Employees and collectors: Sonnet, named explicitly on every Agent call.

---

## 0. Who you are and the standing instructions

You are the **manager** of the 2J rejection revision. The paper was rejected by Building Simulation on
2026-09-15. Target venue is **Applied Energy** (author decision; fallback Sustainable Cities and Society).

Author instructions that still bind, verbatim where quoted:
- "continue until the end, do not stop the progress anymore for questions". You take design decisions
  yourself and record them in the plan's Progress Log and the task doc. Ask the author only for inputs
  only they hold (the SHEU end-use split; running deep-research prompts; generating Figure 1).
- Use cheaper agents (Sonnet), model named explicitly. **One fresh agent per task, never resume a
  finished one.** Employees submit, write the JobID to the task doc, end the turn. They never wait.
- Use the Speed cluster at full speed (account cap 32 CPUs total), `sbatch` only.
- Option (a) is decided: 2022 is rebuilt from 2022-cycle diaries only; 2030 is built by D1 on the rebuilt
  stock. Do not re-open it.
- **Update this prompt (§2 and §3, plus the "Last updated" line) after every task completion**, in the same
  turn as the Progress Log entry and the checklist republish.
- "udpate artifact everytime" (2026-09-15): republish the checklist page after EVERY step, not only task closures.
- "i am struggling to montior, what is left to do": the checklist page must always answer that question
  without the author asking. One progress bar per cluster job, refreshed from `sacct` on every wake.

**AUTHOR RULINGS (plan log (ay)), binding on every later task:**
- **(a) Weekend ceiling.** The pre-registered diary-distance ceiling is 0.10 for every day type. The weekend
  does not meet it and the manuscript says so plainly. The later widening to 0.20 is disclosed once, in the
  SI, and used nowhere. The evidence carried is the observed-only weekend rows (0.036 Sat / 0.040 Sun) versus
  synthetic-only 0.138 to 0.175, plus the saturated weekend up-weighting (~0.005 movement over two attempts).
  The synthesized weekend days are a stated limitation of the diary completion step.
- **(b) Old numbers.** Every OLD-CAMPAIGN / OLD-BUILD number is re-derived on the rebuilt runs (T20, T21, T28,
  T30) before it may appear anywhere. Any number the rebuilt runs do not produce is **dropped**, never quoted
  from the old campaign. Old and rebuilt numbers never share a table.

Hard rules (read `GSSCanada-main/CLAUDE.md` first; it overrides everything):
- Chat reply shape: one plain headline sentence, 3–5 plain bullets, `Evidence:` line, `Next:` 3–4 words,
  ~80 words, English, no tables, no IDs or jargon in sentences.
- **Speed login node (`speed-submit2`): never python, never blocking `srun`, never `find/du/md5sum/cp/mkdir`.**
  Allowed: `sbatch squeue sacct scancel scontrol cd ls scp module load` + single-file `tail head grep wc -l cat`.
  Every job `-p ps -t 7-00:00:00`. Shell is tcsh: no `2>&1`, no `2>/dev/null`. ssh
  `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Python on nodes:
  `/speed-scratch/o_iseri/envs/step4/bin/python`, `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`.
  Staging: `/speed-scratch/o_iseri/2J_revision/Tnn/`. Create remote dirs by `scp -r` of a local folder with
  `.keep` files (SLURM `--output` dirs must exist at submit time).
- The rejection letter is confidential: no quotes, no manuscript ID on any public page.
- Deep research is external: write prompts, never search literature or check DOIs yourself.
- Never create images (data plots from frozen data excepted).
- Manuscript prose says "limitation", never "failure". Never relax a band to pass.
- Every check must be seen failing once on a fake case before its PASS is trusted.
- Local edit rule: **never use bash heredocs for file edits** (they mangle LaTeX backslashes and tabs). Write a
  `.py` script into the scratchpad with the Write tool, every replacement guarded by
  `assert s.count(a) == 1`, then run `py -3 <file>`. Quote every path containing "rejection revision".

Engine facts (verified, do not re-derive): cell label `f"{archetype}__{city}"`; archetypes SingleD,
OtherDwelling, MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B,
Winnipeg_7A; array task id = arch_idx*6 + city_idx. `run_paired_mc.py` has no `--code-root`: run the copy in the
shared tree `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (T22's tree never had the driver; log (ag)).
`--sched-dir` expects plain `BEM_Schedules_{y}.csv`. **The sampling pool = households passing
`validate_household_schedule` on the loaded file(s), so it depends on schedule CONTENT**: any run meant to reuse
T21's households must use T21's paired pool or T21's manifest, never a fresh draw on another file (log (ak), (am)).
Stock weights are archetype-only, split equally over cities. CI = pooled paired Student-t
(`08_simulation_val.py:951-1027`). Metrics in `08_simulation_plots.py` (annual kWh :340,361; daily peak :377;
circular peak hour :278-285; load factor :385; midday share [9,17) :387; circular SD :290; morning-leaning
share :914-915).

## 1. Read these first, in order

1. `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md` — §2 reviewer triage,
   §3 work packages, §9 closure boxes, §10 waves, and **the Progress Log from entry (aa) to the end**.
   The log is the state.
2. The task docs of everything in flight (§2 below), Ledger and Manager addenda first.
3. `deepResearch/00_README_deepResearch.md` (vetting list, venue decision rule).
4. Memory: `project_2j_paper_writing.md` (update it at the end of your session).

All `impl/` and `deepResearch/` paths are under `2J_docs_occ_nTemp/writing/submission/rejection revision/`.

Progress checklist page for the author: https://claude.ai/artifact/4emZkRdASTDUtvXSRtWPVe (source HTML
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\3104eb58-cbdd-4775-8be0-71261110f8f2\scratchpad\2j_resubmission_tracker.html`;
if it is gone, `Artifact action:read` the URL and rebuild the file from it). **Always read the live page and
diff before republishing; extract the scripts to `scratchpad/t.js` and `node --check` it; never pass `favicon`;
pass `url` to update in place.** The top panel "Right now" holds one progress bar per cluster job (cells done of
total, from `sacct`); refresh its counts on every waiter wake (author asked for it, Version 15).

## 2. State (2026-09-15 late evening, entry (ba))

### 2.1 Done and trusted
- T01–T19, T23–T25, T27 (see log). T17: Speed reproduces the local campaign. T18: control arm reproduces the
  published 2022 files exactly. T23: the schedule fallback path gives identical values; no correction.
- **T18c / choice rule (entry (aa))**: the frozen 2022 stock is **Nb-f**, all 144,465 households, 6,934,320 rows.
  Validator check 3.5 fails on Nb-f (75.04 % vs 72.3 %, band not moved): a stated limitation.
- **T20 CLOSED** (log (ah)): N0–N3 all PASS; household-ID sets of 2030 main and null equal Nb-f 2022 (job 1328408).
- **Shared Step-8 code tree** `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (log (ag)).
- **T21 sample question CLOSED (log (ak)).** Staged files byte-equal to T18c/T20 outputs. The rebuilt schedules
  change which households the engine's sanity check drops, so the paired pool (16,326 for SingleD Montreal)
  differs from the published one (16,208) by 320 households and seed 42 draws a different sample (130228/79252
  vs published 130322/80058, which the engine reproduces on the published files). **Basis change: A2 = equality
  with an independent engine re-draw on the staged files (seen failing first) + info-only overlap with the
  published manifests.** The paper must say the before/after comparison is not household-paired across stocks.
  T21 smoke PASS. T30's and T31's smokes ran on the PUBLISHED schedules: their mechanics results stand, their
  household numbers are not Nb-f numbers.
- **T30 V1 decided (log (ak)):** phase B samples once per cell from the paired pool; V1 = equal to T21's manifest,
  mismatch = stop.
- T31 phase A CLOSED (E0 exact, E1 heating +205–208 %, E2 2.50 ACH50).
- **T26 ACCEPTED** (log (am)): SC0–SC5 pass; SC4 read as 0 FAIL of 31 checks. Standardized-jump trigger fired → T32.
- **T31 CLOSED, NOT RUN (log (aq)):** dr_2J-09b returned; rules 1 to 8 applied. Wall, ceiling and air-tightness
  found, but no source prints a U-value or SHGC for the dominant glazing type, so window is NOT FOUND and rule 8
  fires: WP7.3 is not run, no JSON, no partial variant. The paper states the one-envelope limitation.
- **WP10 prep DONE:** T33 (log (at)) `manuscript/prep/` response_map (42 rows), jargon_inventory, si_move_list.
  T34 (log (au)) `manuscript/draft_S2_framework.md`, 9 corrections. T35 (log (aw)) Figure 1 prompt, corrected:
  raking runs AFTER matching in the code, so WP10 orders matching (2.4) before raking (2.3). T36 (log (ax), (ay))
  `manuscript/draft_SI_model_selection.md`, accepted with 3 manager corrections and both author rulings applied.

### 2.1b Both done, collected 2026-09-15 (logs (bb) and (bc)). Nothing to do here.
- **T37 — DONE, collected and accepted 2026-09-15, log (bb).** `manuscript/draft_S7_limitations.md` is written
  and reviewed: **ten** limitations, four trace rows re-checked at source by the manager, both rulings hold. Two
  manager corrections applied: the opening count was wrong twice (it said six, the section listed nine), and the
  tenth limitation (Saturday and Sunday pooled into one weekend pattern) was added at the T38 collection with its
  own trace row. Use it as the S7 base in step 13. Do not re-run this task.
- **T38 — DONE, collected and accepted 2026-09-15, log (bc).** `manuscript/draft_SI_schedule_completion.md`
  is written and reviewed: S.5 to S.9 plus a 17-row trace table. Four manager corrections applied, three of them
  ruling (b) repairs (the 2022 at-home rates by day type, the 2030 Saturday and Sunday rates, and the 77,313
  weekday-only count were all measured on superseded builds and are now marked PENDING). Do not re-run this task.
**Three PENDING placeholders are now live in the manuscript folder** and must be filled or cut at step 13:
the 2022 at-home rate by day-type stratum, the 2030 Saturday and Sunday rates, and the 24-cell drop-count audit
behind the sampling-pool caveat. The first two come free with any rebuilt schedule file; the third is optional
and only if the reviewer response needs more than the one audited cell.

### 2.2 Cluster snapshot read 2026-09-16 morning (refresh with `sacct` before trusting it)
Everything is queued behind the 32-CPU account cap. **Every completed array task so far exited 0:0; nothing has
failed, nothing needs resubmitting.** Counts are completed array tasks. The T21 arrays are eating the whole
32-CPU allocation, which is why everything else sits in `AssocGrpCpuLimit`; that is expected, not a problem.

| Job | What | Progress 2026-09-16 am |
|---|---|---|
| 1328422 | T21 Step 8 paired runs, 24 tasks `%4` | **20 done, 4 running** |
| 1328425 | T21 Step 9 activity, 24 tasks `%4` | **18 done, 4 running, 2 pending** |
| 1328426 | T21 Step 9 baseline, 24 tasks `%4` | 0 done, queued |
| 1328427 | T21 A4 md5-after, `afterany` | queued (dependency) |
| 1328428 | T21 `t21_check.py` selftest + A2/A2-info | queued (dependency) |
| 1328419 | T30 average-profile array, 48 tasks `%2` | 2 done, queued |
| 1328415 | T28 200-home sample-size array, 4 tasks `%1` | 1 done, queued |
| 1328310 | T22 static-schedule arm, 24 tasks `%2` | **14 done**, 10 queued |
| 1328429 | T32 S-Revert-std build (task 0 guard, task 1 std) | queued |
| 1328430 | T32 compare, `afterok` | queued (dependency) |
| 1328431 | T29 staging | queued |
| 1328432 | T29 smoke (2 households) | queued (dependency) |
| 1328433 / 1328434 | T29 S-Partial / S-Revert, 24 tasks each | queued (dependency, `--nice=100`) |

Longest observed Step-8 task so far: about 5 hours (`1328422_19`, 05:07:26). Four at a time, 4 left at the read,
so T21 Step 8 should finish within a few hours of 2026-09-16 morning and Step 9 baseline (1328426) then starts.

**Waiter.** The outgoing session's waiter (`b0ip5fw2y`) polled every 30 min and fired when any of 1328432,
1328430, 1328310 or 1328428 left the queue. **It dies with that session: start a fresh waiter as your first act**,
on whichever of those IDs are still queued, and restart it (minus finished IDs) after every wake. Watch 1328422
too now — it is the closest to finishing and it unblocks steps 3 and 4.

### 2.3 Owed by the author (never block on these)
- Run `deepResearch/dr_2J-10_novelty_matrix_search_prompt.md` and `dr_2J-11_wfh_trajectory_and_tradeoff_prompt.md`
  (log (ar)). Vet each return with the README 7 steps before any citation; the pre-registered decision rules in
  each prompt then apply mechanically.
- Generate the Figure 1 workflow image from `figures/Prompts_Images/` (log (aw)). Not urgent.
- The SHEU end-use split, asked once during Wave 4.

### 2.4 Process warnings
Three employees broke the login-node ban this session (`mkdir` twice, `find` once). **Every brief must name
`mkdir` and `find` explicitly as forbidden.** Employees must also be told: no `2>&1`, no `2>/dev/null` (tcsh),
no python on the login node, and `-p ps -t 7-00:00:00` on every job.

## 3. Your queue — every remaining step, in order

Nothing local is running. Steps 1 to 6 are cluster collectors and fire as jobs finish; steps 7 onward are the
writing waves and can start at any time in parallel with the cluster.

**Step 0 — first act of the session.** Start a fresh 30-min waiter on the still-queued trigger IDs (1328422,
1328432, 1328430, 1328310, 1328428 — drop any that have already finished). Then `sacct` all live jobs, refresh
the nine progress bars on the checklist page (it is at **Version 29**, read the live page and diff first),
republish, and send the author one short reply on where things stand. Nothing else is owed before the first
collector fires; steps 7 to 13 can be started in parallel at any time and do not need the cluster.

**Step 1 — T29 smoke collector** (fires when 1328432 leaves the queue). Fresh Sonnet. It reads the smoke output
and confirms: both households simulated, **8,760 rows each**, household IDs **130228 and 79252** (T21's rebuilt
draw, not the published 130322/80058). All three true → let arrays 1328433 and 1328434 run. Any one false →
`scancel 1328433 1328434`, write why in the T29 doc, and report. Nothing else is decided here.

**Step 2 — T32 collector** (fires when 1328430 leaves the queue). Fresh Sonnet, spec §5 of the T32 doc.
Score G0 guard, SC1, SC4, SC5 and the reported numbers. **G0 is the load-bearing one: the guard task must
equal T26's λ = 0 output exactly**; if it does not, the standardized build is wrong and nothing downstream runs.
On full PASS, brief the 1,200 S-Revert-std runs using T29's fixed-manifest wrapper (same households as T21).
On any FAIL, stop and write the diagnosis; do not submit.

**Step 3 — T21 collector** (fires when 1328422, 1328425, 1328426, 1328427 and 1328428 have all finished).
Fresh Sonnet. Score A1–A6 with the restated A2 (equality against the independent engine re-draw, plus
info-only overlap with the published manifests — the pre-registered wording is in the T21 doc's ledger).
A5 SHEU gates are report-only. **A6 is a stop rule: a peak shift outside 0 ± 1 h stops all paper numbers** until
the manager rules on it. Hand-check one cell's annual kWh and daily peak against the raw output before accepting.

**Step 4 — T28 collector** (after T21 Step 8 1328422 and its own array 1328415). Fresh Sonnet. B1–B3 plus the
hand-checks in the T28 addendum. T28 answers the 200-home sample-size question; its numbers replace the
OLD-CAMPAIGN sample-size numbers under ruling (b).

**Step 5 — T30 collector** (after 1328419's 48 tasks). Fresh Sonnet. V0–V5. **Make V1 and V2 fail once on a
fake case before trusting their PASS** (V1 = manifest equality with T21; a mismatch stops T30). Hand-check one
cell end to end.

**Step 6 — T22 collector** (fires when 1328310 finishes). Fresh Sonnet. Score the static-schedule arm, and in
the same pass check the Nb-f SHEU design levels and household IDs against the old file. That comparison decides
whether any T22 cell must be re-run; say so explicitly either way.

**Step 7 — deep-research returns** (whenever the author hands them back). For each of dr_2J-10 and dr_2J-11:
apply the README's 7 vetting steps in order, write the vetting file next to the return, then apply that
prompt's pre-registered decision rules. Expect fabricated citations; `NOT FOUND` is a valid and useful result
and is carried into the manuscript as a stated gap, exactly as dr_2J-09b's window value was.

**Step 8 — Wave 4 re-derivations** (plan §10; can start before the cluster finishes, finishes after it).
Re-derive T06, T07 and T09/T15 on the rebuilt runs. **When T09 is re-derived, re-read the scope paragraph of
`manuscript/draft_S7_limitations.md`**: it describes the measured-data check as Toronto and Ontario electricity on
shoulder-season weekdays, sourced from the old T09 doc. No T09 number is quoted there, so ruling (b) is not
breached, but the description must still match the re-derived run (log (bb)). Under ruling (b), every number these produced on the old
campaign is replaced or dropped — check each against the T36 number trace table, which now marks the seven
OLD-CAMPAIGN / OLD-BUILD rows.

**Step 9 — WP6** (2030 and scenarios). WP6 **must deliver the clustering check that `draft_S2_framework.md`
promises in its paired-interval section**, or that sentence is cut from Section 2. Decide and record which.

**Step 10 — WP8**: confidence intervals recomputed on the corrected runs (pooled paired Student-t,
`08_simulation_val.py:951-1027`). **Step 11 — WP3**: the comparison table. **Step 12 — WP11**: figures — write
prompts only for schematic figures; matplotlib plots from frozen data are allowed and preferred.

**Step 13 — WP10, the manuscript rewrite for Applied Energy.** Carry in: the response map (42 rows), the jargon
inventory, the SI move list, `draft_S2_framework.md`, `draft_SI_model_selection.md`, `draft_S7_limitations.md`,
`draft_SI_schedule_completion.md`, the Figure 1 prompt. **Plan §5 item 5 is already settled, do not redo it** (log (bc)): Saturday and Sunday are pooled into one
weekend pattern at the building-model interface, `07_aug_to_bem.py:34`, and the tenth limitation is already in
`draft_S7_limitations.md`. At assembly, confirm the SI appendix order and renumber S.5 to S.9 if this part does
not follow the model-selection part, and name which calendar-expansion path the campaign uses
(`create_compact_schedule` or `write_8760_schedule_csv`); no claim turns on it, but the SI should not be vague.
Order matching (2.4) before raking (2.3). State plainly: the before/after comparison is **not household-paired
across stocks**; the one-envelope limitation; validator check 3.5; and ruling (a)'s weekend limitation. Update
`writing/submission/tables/SI/Table_B1_B2.md` lines 9 and 59 ("sole model" wording). Re-derive or drop the seven
OLD-campaign SI numbers. The internal model label (J3) never appears in prose.

**Step 14 — WP13**: build the submission package, then run `submit_check.py` on the installed files until green.

**Step 15 — Wave 5**: write `deepResearch/dr_2J-08_presubmission_audit_prompt.md` **only after step 14 is green**.
The author runs it in Gemini and Fable 5; vet the return the same way.

After every step: append to the plan Progress Log, tick the plan §9 boxes that closed, republish the checklist
page (read live first, `node --check` the script), and **update §2–§3 of this prompt and its "Last updated" line**.
At session end, update memory `project_2j_paper_writing.md`.

## 4. First reply to the author

One plain headline on where things stand (how many cluster runs finished overnight, and whether anything failed),
3–5 plain bullets, `Evidence:`, `Next:` in 3–4 words. Nothing else.
