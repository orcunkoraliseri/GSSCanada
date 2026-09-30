# TASK (employee, Sonnet): 5J pilot, part 1: build the 50 pilot inputs, copy them to Speed, submit

Written 2026-09-29 ~21:50 by the 5J manager. **Start only when `2026-09-29_wp1_households_v2.md` has a
"Verified (manager)" section** (it provides `wp1_hids/es_60/` with a `presence/` folder, and
`outputs_step2/pilot_runs.csv` built from the weighted households). Spec: `Step2_docs/5thJ_02_campaignDesignPilot.md`
§2A "Inputs recorded per run", §2C, §2D. State file: create `Step2_docs/impl/2026-09-30_wp1_pilot.md`
(Task doc / Status / Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), write as you go.

## Hard rules
* Spain only. UK licence: never open any UK file or the pooled 4J corpus; no repo-wide or folder-wide search, no
  wildcard that could match a UK file (FINDING 5J-2); name files in full.
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`; do not edit `tools/5thJ_idf.py` or the trigger (import them).
  New script `tools/5thJ_pilot_build.py` and Speed scripts under `tools/speed/` (new folder).
* 🔴 Speed: `sbatch` only; every job `-p ps -t 7-00:00:00 --exclude=antenna1`; never python, EnergyPlus, loops or
  md5 over many files on the login node (single-file `ls`/`cat`/`tail`/`wc -l` only). Host
  `o_iseri@speed.encs.concordia.ca`, login shell tcsh. Do not touch any job that is not yours (1J, openubem arrays).
* **You never wait or poll.** Submit, write the JobIDs in the Ledger, end the turn: "jobs N submitted, state written
  to <path>". A later employee reads the results and writes `outputs_step2/pilot_report.md`.

## Part A (local)
1. `5thJ_pilot_build.py`: for each row of `outputs_step2/pilot_runs.csv`: building = the 4J archetype row
   (`_s8.load_rows(<4J Step8 outputs>, "es")`, match `archetype_code`) with `infiltration_ach` and `north_axis_deg`
   from `buildings.csv`, passed to `5thJ_idf.build(row, household, infiltration_ach=..., north_axis_deg=...)`.
   Household dict built by YOUR script the way `5thJ_idf._household` does (5thJ_idf.py:317-334) but with presence
   from `wp1_hids/es_60/presence/` and appliance csv + peak W from `wp1_hids/es_60/` (not from `wp1_test`).
2. Portable inputs: one folder per UNIQUE input (42) `_5J_data/surrogate/pilot/inputs/<input_id>/` holding
   `in.idf` + the schedule csvs it names; rewrite the absolute `File Name` paths in the IDF to bare basenames
   (text post-process in your script, printed as `PATCH relative_paths OK n=<count>`). Replicates point at the same
   input folder.
3. Gate "relative = absolute" (seen failing, then passing): run EnergyPlus locally
   (`C:/EnergyPlusV23-1-0/energyplus.exe -w <epw> -d <run> -x -r in.idf`, cwd = the input copy) on ONE input with
   absolute paths and with relative paths; hourly heating, cooling, appliance columns must be identical. Seen
   failing: point one schedule name at a missing file → EnergyPlus must stop with a severe error (record it).
4. Run manifest `pilot/run_manifest.csv`, one row per run (50): `run_id, country, climate, building_id,
   household_id, replicate, input_id, schedule_md5 (presence;appliance), idf_md5, epw_md5, energyplus_version
   (23.1.0-87ed9199d4), clock_origin (midnight)`. EPW = `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/
   es_madrid_2009_2010_y2010.epw` (md5 110b364912226ee4d2a5b5411eab81da; check it). Local md5 list
   `pilot/md5_local.txt` of every file under `pilot/inputs/` + the EPW.

## Part B (Speed; D2-5/D2-6)
5. Copy `pilot/` (inputs, manifest, md5 list) and the EPW to `/speed-scratch/o_iseri/5J/pilot/` (scp or rsync,
   run locally). EnergyPlus on Speed: `/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64`
   (from `Step1_docs/outputs_step1/wp0_inventory.md:144`; `ls -l` it, do not run it on the login node).
6. Job 1 `tools/speed/5J_pilot_check.sh` (1 CPU): md5 every file on the Speed side and diff against
   `md5_local.txt` (write `md5_speed.txt` and one line `MD5 equal=<n> differ=<n> missing=<n>`); disk preflight:
   `df -h /speed-scratch/o_iseri` and `quota` or `lfs`/`du -sh /speed-scratch/o_iseri` as available, written to
   `preflight.txt`; `energyplus --version` on the compute node. Exit non-zero if any md5 differs or is missing.
7. Job 2 `tools/speed/5J_pilot_array.sh`: `--array=1-50%8`, 1 CPU, 4G, `--dependency=afterok:<job1>`. Each task:
   its manifest row → copy the input folder to a fresh run dir `/speed-scratch/o_iseri/5J/pilot/runs/<run_id>/`
   (one working directory per run), run EnergyPlus with `/usr/bin/time -v` (or `date +%s` before/after), then write
   `runs/<run_id>/status.txt`: rc, seconds, max RSS if available, `du -sb` of the run dir, "Completed Successfully"
   yes/no, severe count; extract the 4 hourly columns (the ones `5thJ_idf.summarise_run` reads) to
   `extracted/<run_id>.csv` and write its size. Keep the raw folder (the pilot measures it).
8. Submit job 1 then job 2; `squeue -u o_iseri` once to show both queued; Ledger lines; end the turn.
   (Queue note: the account is at its 64-CPU cap tonight, so the array may wait; that is expected.)

## What the manager will re-derive
One idf_md5 on both sides; the relative = absolute gate output; the 50 manifest rows; the two JobIDs in squeue.
