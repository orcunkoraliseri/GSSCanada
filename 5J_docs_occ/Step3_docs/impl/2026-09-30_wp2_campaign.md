# 5J Step 3 part 1: campaign tool, smoke job, disk preflight, Spain + Italy arrays - implementation state
Task doc:   `Step3_docs/impl/2026-09-30_wp2_campaign_TASK.md`
Status:     RUNNING (arrays submitted 16:49 EDT); part 1 done by the employee, manager reads the arrays next
Speed folder R = `/speed-scratch/o_iseri/5J/campaign/`; local scripts (the record) in `tools/speed/camp_*.py|sh|sbatch`
(camp_common.py, camp_plan.py, camp_task.py, camp_array.sh, camp_smoke.py, camp_smoke.sbatch, camp_preflight.sbatch).

## Ledger (append-only)
* 1404149 · smoke job (5 runs in scratch tree R/smoke/) · COMPLETED 16:48, exit 0 · `logs/smoke_1404149.out`
* 1404152 · preflight job (df, du, PREFLIGHT_DISK, real plan) · COMPLETED 16:48, exit 0 · `logs/preflight_1404152.out`
* Arrays (each `--array=1-N%5`, -p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G), submitted 16:48:56 to 16:49:07 by `bash camp_array.sh <climate>`; logs `R/logs/<climate>_<JobID>_<task>.out`:
  * 1404153 · es_madrid_2010 · blocks 1-6 (6) · RUNNING (tasks 1-5 running, 6 pending)
  * 1404159 · es_valencia_2010 · 1-5 (5) · RUNNING
  * 1404164 · es_seville_2010 · 1-5 (5) · RUNNING
  * 1404165 · it_bologna_2014 · 1-5 (5) · RUNNING
  * 1404174 · it_turin_2014 · 1-5 (5) · RUNNING
  * 1404179 · it_milan_2014 · 1-5 (5) · RUNNING
  Total 31 tasks; at most 30 run at once (6 x %5).
* First sacct read 16:50: 30 tasks RUNNING (1 min 30 s), 1 pending (1404153_6, throttle), 0 failed. About 211 done json files 1 minute in, first Madrid SFH runs PASS at about 7 s each.

## Verified (read from the job logs)
* Smoke job 1404149, 16 items, `SMOKE SUMMARY pass=16 fail=0`: frozen design md5 2594867b0fe6cf24191c00e0c83d91a7 equal; run tables es b4d5b42e... and it e9ddcf10... equal; six EPW md5 equal climates.csv; staged buildings 80 rows (es+it only) and climates 6 rows; smoke plan before runs `PLAN total=5 done=0 todo=5`; `camp_task es_madrid_2010 1` SUMMARY planned=4 not_run=0 ran_failed=0 ran_passed=4; `camp_task it_bologna_2014 1` planned=1 ran_passed=1; done json of all 5 (status pass, all 6 checks ok, all required fields, extracted md5+bytes equal a recount inside the job, raw folder deleted); plan after runs `done=5 todo=0`; control (unchanged scratch copy of household folders) `done=5`; one byte changed in es_02288 elec file -> `done=4 todo=1`, todo = es_madrid_B21_dev_1 (cache miss seen); check_err: real err file passes, planted Severe line FAILS, removed "Completed Successfully" FAILS. The MFH run checks (12 dwellings, 105,120 rows): patch lines 9 of 9, area gates, Completed + 0 Severe, rows, facility annual (heating 237.5142 GJ hourly vs 237.51 table), dwelling annual all true.
* Preflight 1404152: `PREFLIGHT_DISK free_bytes=46083191013376 used_5J=2712561484 plan_peak_bytes=27500000000`, verdict PASS (free > 10 x plan peak); raw df line `filer-speed:/userdata/speed_scratch 133040906960896 86957715947520 46083191013376  66% /nfs/speed-scratch`.
* Real plan (inside 1404152): `PLAN total=9269 done=0 todo=9269` (= 4,768 Spain + 4,501 Italy). Per array runs/blocks: es_madrid 1656/6, es_valencia 1556/5, es_seville 1556/5, it_bologna 1567/5, it_turin 1467/5, it_milan 1467/5 (31 blocks).

## Decisions
* (16:44) Household folder for a placement token: a token that already starts with `<cc>_` (B0: `es_avg`) is used as is, any other token is `<cc>_<token>`. Builder household dict `fold` = country code.
* (16:44) Smoke job uses 4 runs from the real tables (SFH es_madrid_B01_dev_1, MFH es_madrid_B21_dev_1, B0 es_madrid_B01_b0_1, replicate es_madrid_B01_dev_1_rep1) plus ONE extra Italian run (it_bologna_B01_dev_1) so the Italian path is also exercised.
* (16:44) gzip written with mtime 0; content of the extracted files identical to `mzp_extract.py`, except the first header line names the campaign and the run (so two runs with the same inputs have different file md5; compare contents without the `#` lines, part 2).
* (16:44) Each passed run also keeps its small `eplusout.err` as `R/done/<run_id>.err`; raw folder deleted on pass only.
* (16:44) SUMMARY line: `planned = not_run + ran_failed + ran_passed`; runs already DONE at task start count in not_run and are also listed as `skipped_done=..` appended at the end of the line.
* (16:44) Cache key = md5 of JSON of: buildings.csv row, TABULA parameter row, k, n_floors, placement string, md5 of every file in each used household folder (presence, elec, household.json), EPW md5, md5 of 5thJ_idf_mz.py + 5thJ_idf.py + 4thJ_step8_idf.py (R/repo copies), EnergyPlus version string.
* (16:44) Block cutting: run positions fixed by table order, replicate runs last in the climate-1 array; run estimate = class median (SFH/TH 4 s, MFH 14 s, AB 19 s, 1.0 s per zone above 18 zones), greedy cut at 2,400 s. Gives 31 blocks, not the 40 the design guessed (design section 6 counted about 220 runs per task; its own per-class seconds give about 5 blocks per array). Real runs are slower than the estimate (smoke: SFH 7 s, 12-flat MFH 29 s), so a block will take more than 40 min.
* (16:44) Area gates (check_area_gates) are part of the per-run checks, in addition to the checks the task listed.
* Throttle: the preflight and smoke jobs ran before the arrays; arrays 6 x %5 = 30 tasks.

## Next
Manager reads the arrays (sacct, SUMMARY lines per task: `grep SUMMARY R/logs/<climate>_<job>_<task>.out`, one line per task; there must be 31), then the Step 3 part 2 task: G5J.1 over everything, resume check (failure class 61), splits sealed. A failed run stays in `R/done/<run_id>.json` (status fail) with its raw folder in `R/runs/<run_id>/`; `python camp_plan.py` (inside a job) shows todo; resubmit the climate with `bash camp_array.sh <climate>` only after the plan job is re-run (the plan rewrites block files).

## WHAT I DID NOT VERIFY
* No array task has finished as of 16:50; none of the 9,269 runs is confirmed beyond the 5 smoke runs and about 200 early Madrid SFH lines seen as PASS in a log.
* Italy: only one Italian run (Bologna SFH) was exercised end to end; no Italian MFH/AB run (TABULA k from the Italian dwelling counts) has run yet; Turin and Milan climate files only md5-checked, not run.
* The 77- and 48-dwelling runs have not run under this tool (memory with 4 GB: reading an eplusout.csv of about 2,300 columns plus the facility and dwelling checks was not tested at that size; the timing job measured EnergyPlus alone at 266 MB).
* Replicate outputs equal their originals: not tested (the file header differs by run id, so the md5 differs; content comparison belongs to part 2).
* Gate 1.5 (empty extracted file) and 1.6 (missing SUMMARY line) seen-failing were not part of this task and were not run.
* The disk line is one moment; free space during the campaign was not watched.
* Smoke used scratch copies; the done folder of the real campaign was empty before the arrays started (not listed separately).
* Lighting is not modelled; COP 3.0 assumed (design open items), not touched.

## Manager read 2026-09-30 16:51 EDT (from `date`)
sacct: all 30 first tasks RUNNING (6 arrays x 5, throttle holds at 30 CPUs), 0 failed; `done/` 1158 files,
`failed/` 0. Smoke 16/16, preflight PASS, PLAN total 9269 accepted as reported (re-derivation after the arrays, in
part 2's verification). Part 2 task written: `Step3_docs/impl/2026-09-30_wp2_campaign_part2_TASK.md`, launched
when the arrays finish (manager watcher polls squeue every 5 min).
- Manager 2026-09-30 18:33 EDT: all 31 array tasks COMPLETED 0:0; done/ 18,538 files, failed/ 0. Part 2 employee launched.
