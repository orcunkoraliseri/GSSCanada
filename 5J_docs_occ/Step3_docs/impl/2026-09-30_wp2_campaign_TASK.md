# TASK (employee, Sonnet): 5J Step 3, part 1: campaign tool, smoke job, disk preflight, Spain + Italy arrays

Written 2026-09-30 16:39 EDT (from `date`) by the 5J manager. Read first: `Step3_docs/5thJ_03_fullCampaign.md` (the spec),
`Step3_docs/5thJ_03_fullCampaign_val.md`, the FROZEN design `Step2_docs/outputs_step2/campaign_design.md` (md5
2594867b0fe6cf24191c00e0c83d91a7: check it inside your first job; if it differs, stop, BLOCKED), and the scripts it
names: `tools/5thJ_idf_mz.py` (build_mz), `tools/speed/mzp_build.py`, `tools/speed/mzp_array.sh`,
`tools/speed/mzp_extract.py`, `tools/5thJ_mz_pilot_check.py` (the re-pilot checks), `tools/speed/cd_timing_build.py`.
State file: create `Step3_docs/impl/2026-09-30_wp2_campaign.md` (Task doc / Status / Ledger / Verified / Decisions /
Next / WHAT I DID NOT VERIFY), write as you go; `date` before every stamp. G = `C:\Users\o_iseri\Desktop\GSSCanada`.
Part 2 (G5J.1 over everything, resume check, splits sealed) is a separate task after the arrays finish.

## Hard rules
* 🔴 ALL compute on Speed via sbatch. Locally ONLY edit/write files, ssh/scp, ls, read small files. Login node:
  sbatch/squeue/sacct/scancel/scp/ls and single-file cat/tail/wc -l; hashes only inside a job. Every job
  `#SBATCH -p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G`, python `/speed-scratch/o_iseri/envs/step4/bin/python -u`,
  EnergyPlus 23.1 as in `mzp_array.sh` (never name the input `in.idf` in the run dir). CPU share 30 (O-5): 6 arrays
  at `%5` each, never more than 30 tasks running. At most 6 sacct checks of 30 s per job; then "manager to read", stop.
* 🔴 UK licence: Spain and Italy only. Never open or copy any UK household, diary, schedule, IDF or output; no
  folder-wide search or wildcard that could match a UK file. Stage only es/it rows of `buildings.csv` and only the
  six es/it EPWs of `climates.csv` (md5 each against climates.csv inside a job).
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor `tools/5thJ_idf.py`, `tools/5thJ_idf_mz.py`, the frozen
  design files. New scripts go in `tools/speed/` (local copy = the record) and `R/`.
* Speed folder `R=/speed-scratch/o_iseri/5J/campaign/` (create). Household inputs (read-only):
  `/speed-scratch/o_iseri/5J/households/inputs/<cc>_<hid>/` and `<cc>_avg/`. Read-only: every other `5J/` folder.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: the campaign tool (`tools/speed/camp_*.py`)
1. `camp_plan.py`: reads the two frozen run tables; per country x climate (6 arrays) cuts the runs into blocks of
   about 40 min estimated time (per-run estimate from design section 7: class medians, and 1.0 s per zone above 18
   zones), keeping each run's position fixed; writes `R/plan/<array>/block_<n>.csv` and `R/plan/plan.csv`. A run
   counts as DONE only if its `R/done/<run_id>.json` exists with `status: pass` AND its `cache_key` equals the key
   recomputed from the current inputs (md5 of: building row, k, placement, every household file, EPW, builder file,
   `4thJ_step8_idf.py`, EnergyPlus version). Prints `PLAN total=.. done=.. todo=..`.
2. `camp_task.py <array> <block>`: for each run not DONE: build the IDF with `build_mz` (household dicts from the
   input folders; B0 runs use `<cc>_avg` in every flat); run EnergyPlus in `R/runs/<run_id>/`; extract exactly as
   `mzp_extract.py` (one `<run_id>.csv.gz` + `<run_id>.dwellings.csv` in `R/extracted/<array>/`); check: "Completed
   Successfully", 0 Severe, every PATCH line PRESENT, 8,760 rows per dwelling per target, facility annual = hourly
   sum (as gate 2.4), each dwelling's annual = its zone columns (as gate 2.4b); record size and md5 of both
   extracted files; write `R/done/<run_id>.json` (run_id, status, seconds, MaxRSS, cache_key, idf_md5, epw_md5,
   household md5s, extracted md5 + bytes, EnergyPlus version, clock origin); delete the raw run folder ONLY when
   status is pass (a failed run keeps it). Ends with one line
   `SUMMARY array=.. block=.. planned=.. not_run=.. ran_failed=.. ran_passed=..` (three outcomes kept apart; a
   crash inside a run counts as ran_failed with the traceback saved, never as passed).
3. `camp_array.sh`: `sbatch --array=1-<nblocks>%5`, one per country x climate; replicates as planned in the design.

## Part B: smoke job (ONE job, before any array; each item must PASS)
On 4 runs taken from the real tables: one SFH run, one MFH run, one B0 run (average household), one replicate:
`camp_task.py` end to end. Then: rerun `camp_plan.py`: these 4 must count as DONE; change one byte in a scratch copy
of one household file referenced by one of them (copy the input folder, point a scratch plan at it): that run must
count as NOT done (cache key seen failing). Plant a Severe line into a scratch copy of one err file and feed it to
the check: must FAIL. Print each line PASS/FAIL.

## Part C: disk preflight (ONE job) and submission
`df -B1 /speed-scratch/o_iseri` raw line + `du -sb /speed-scratch/o_iseri/5J` + `PREFLIGHT_DISK free_bytes=..
used_5J=.. plan_peak_bytes=..`; PASS if free > 10 x plan peak (27.5 GB from the design). Then submit the 6 arrays
(`%5` each). Write every JobID in the Ledger. Do NOT wait for them: at most 6 sacct checks, then stop with
"arrays running, manager to read".

## Report back (short)
Smoke lines; preflight line; plan counts; the 6 array JobIDs and blocks per array; state of the first sacct read.
Status "RUNNING (arrays submitted)", Next = "manager reads arrays; Step 3 part 2 task (G5J.1, resume check, splits)".

## What the manager will re-derive
One finished run's extracted heating for one dwelling against its done.json md5 and a recount inside a job; the plan
count after the arrays; one task's SUMMARY line against its done files.
