# TASK (employee, Sonnet): 5J Step 3, part 2: campaign integrity (G5J.1), resume check, splits sealed (Spain + Italy)

Written 2026-09-30 by the 5J manager (stamp: see the Progress Log entry that launches it). Start ONLY when all 6 arrays
of part 1 are finished (Ledger of `Step3_docs/impl/2026-09-30_wp2_campaign.md`; `sacct` them first; if any task is
still RUNNING/PENDING, write that and stop). Read first: `Step3_docs/5thJ_03_fullCampaign.md` (3C, 3D),
`Step3_docs/5thJ_03_fullCampaign_val.md`, the part 1 task + state file, the frozen design
`Step2_docs/outputs_step2/campaign_design.md`, and `tools/speed/camp_*.py`.
State file: create `Step3_docs/impl/2026-09-30_wp2_campaign_part2.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY), write as you go; `date` before every stamp.

## Hard rules
* 🔴 ALL compute on Speed via sbatch (`-p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=8G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`). Locally ONLY edit/write files, ssh/scp, ls, read small files.
  Login node: sbatch/squeue/sacct/scancel/scp/ls and single-file cat/tail/wc -l; hashes and file counting over
  folders only inside a job. At most 6 sacct checks of 30 s per job, then "manager to read", stop.
* 🔴 UK licence: Spain and Italy only; no UK file of any kind; no folder-wide search or wildcard that could match a UK
  file (the campaign folder holds only es/it runs; name the folders you read).
* Do not edit `camp_*.py` in place: additive changes with a backup and a printed `PATCH <name> OK` line.
* Speed folder `R=/speed-scratch/o_iseri/5J/campaign/`; new outputs under `R/integrity/` and
  `/speed-scratch/o_iseri/5J/splits/`.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: task SUMMARY lines and repairs
Collect the `SUMMARY array=.. block=..` line of every task log (31 expected; a task with no SUMMARY line is
NOT_EVALUABLE, never pass). If any run is `ran_failed` or `not_run`: read its saved traceback / err (Spanish or
Italian run only), write the cause, fix if it is the tool (additive), rerun ONLY those runs via the plan tool (it
must list exactly them as todo), and ledger the rerun JobIDs. A failed run is never dropped.

## Part B: G5J.1 over every planned run (one job, `camp_integrity.py`)
For all 9,269 planned runs: done.json present with status pass; cache key equals the key recomputed now; extracted
files exist, non-empty, and their size + md5 equal done.json (truncated-output check, 1J antenna1 lesson); 8,760
rows per dwelling per target (read every file); dwellings in the file = n_dwellings of the plan; annual heating,
cooling, equipment finite and >= 0; raw run folder deleted for every pass. Outputs differ between households:
per building and climate, no two runs with different households give identical equipment series for any pair of
flats with different households (sample: every SFH/TH building fully, 5 MFH/AB buildings fully). Replicates:
content (not md5; the header holds the run id) equal to their original, report the max spread per target. B0 runs:
every flat has the average household. One line per check, `SUMMARY PASS=.. FAIL=.. NOT_EVALUABLE=..`, exit 0 only
when FAIL = 0 and NOT_EVALUABLE = 0 (write this at the top of the script).
Seen failing (scratch copies, each must FAIL): truncate one extracted file by 100 bytes; delete one done.json; copy
one flat's series onto another flat with a different household; change one byte of one household file (cache key).

## Part C: resume check (failure class 61)
Move one finished task's done files and extracted files to `R/resume_test/` (a real task, not scratch); run
`camp_plan.py`: `done` must drop by exactly that task's run count and `todo` rise by the same; move them back; rerun:
counts restored. Print the three PLAN lines.

## Part D: splits written and sealed
From `splits_households.csv`, `splits_buildings.csv` and the run tables, write run_id lists (one per line, sorted) in
`/speed-scratch/o_iseri/5J/splits/`:
* `development` = dev households on dev buildings; `validation` = val households on dev or val buildings, plus dev
  households on val buildings; `test_new_households` = test households on dev buildings; `test_new_buildings` = dev
  households on test buildings; `test_both_new` = test households on test buildings; `unused` = every other
  household x building combination (val on test, test on val), listed so nothing disappears;
* B0 runs go with their building's split (`b0_dev`, `b0_val`, `b0_test`); replicates in `replicates` (noise set);
* leave-one-country-out: `loco_es` and `loco_it` (all runs of that country), UK added later by its own task.
Gates: every planned run in exactly one of development/validation/test_*/unused/b0_*/replicates; no household id
and no building id appears in two of {development, validation, test_*} except as the rules above allow (print the
overlaps table); counts per list per country. Then `chmod a-w` on the files, md5 of each into the state file and
`Step3_docs/5thJ_03_fullCampaign.md` Progress Log. Write `tools/speed/split_loader.py` with
`load_split(name)` that refuses any `test_*` list unless `/speed-scratch/o_iseri/5J/gates_frozen.md5` exists (seen
failing now: it must refuse; do NOT create gates_frozen.md5, that is Step 4).

## Report back (short)
SUMMARY lines (31), reruns if any, G5J.1 SUMMARY + seen-failing lines, the three resume PLAN lines, split counts and
md5s, total disk of R/extracted, JobIDs. Status DONE, Next = "manager verifies; Step 4 (freeze the gates)".

## What the manager will re-derive
One random run: its extracted md5 against done.json and one flat's annual heating recomputed; the count of runs in
each split list; the resume PLAN lines; the refusal line of the loader.
