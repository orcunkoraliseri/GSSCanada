# TASK (employee, Sonnet): 5J pilot, part 2: read the 50 pilot runs, check them, write the pilot report

Written 2026-09-29 ~21:50 by the 5J manager. **Start only when (a) `2026-09-30_wp1_pilot.md` has a "Verified
(manager)" section, and (b) the pilot array has finished**: `sacct -j <array JobID from that Ledger> -X
--format=JobID,State,ExitCode,Elapsed` shows no PENDING or RUNNING task. If either is not true, write one line
in the state file and stop. Spec: `Step2_docs/5thJ_02_campaignDesignPilot.md` §2C, §2D, §2E; gates:
`Step2_docs/5thJ_02_campaignDesignPilot_val.md` Sections 2, 3, 4, 5, 6. State file: create
`Step2_docs/impl/2026-09-30_wp1_pilot_report.md` (Task doc / Status / Ledger / Verified / Decisions / Next /
WHAT I DID NOT VERIFY), write as you go.

## Hard rules
* Spain only. UK licence: never open any UK file or the pooled 4J corpus; no repo-wide or folder-wide search, no
  wildcard that could match a UK file (FINDING 5J-2); name files and folders in full.
* 🔴 Speed: login node = `sbatch`, `squeue`, `sacct`, `scp`, single-file `ls`/`cat`/`tail`/`wc -l` only. No python,
  no loops, no md5 over many files there. Copying results back with `scp -r` run LOCALLY is allowed.
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor `tools/5thJ_idf.py`, the trigger or `tools/5thJ_pilot_build.py`.
  New script: `tools/5thJ_pilot_check.py` (local). Local python
  `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`. Do not touch python PID 19328.
* Never wait or poll. Past ~150k tokens: stop, write state, "handoff needed".

## Steps
1. Copy back, LOCALLY: `scp -r` of `/speed-scratch/o_iseri/5J/pilot/extracted/`, and for each run only
   `runs/<run_id>/status.txt` and `runs/<run_id>/eplusout.err` (50 + 50 small files; one `scp` per folder is fine),
   plus `md5_speed.txt` and `preflight.txt`, into `_5J_data/surrogate/pilot/speed_results/`. Do NOT copy the raw
   run folders (the pilot measured their size in `status.txt`). Record file counts.
2. `5thJ_pilot_check.py`: one line per gate, `PASS|FAIL|WARN|INFO|NOT_EVALUABLE <gate> <numbers>`, then
   `SUMMARY PASS=.. FAIL=.. WARN=.. NOT_EVALUABLE=..`; exit 0 only when FAIL=0 and NOT_EVALUABLE=0 among the
   FAIL-severity gates (write this meaning at the top of the script). Gates (val doc numbering):
   * 2.1 50 of 50 extracted files and status files present.
   * 2.2 every `eplusout.err`: "EnergyPlus Completed Successfully" and 0 `** Severe  **` lines (parse the err file
     itself; do not trust `status.txt` alone; report where they disagree).
   * 2.3 8,760 rows per target per run.
   * 2.4 annual sum = hourly sum per target (abs diff < 0.1 %): annual from the EnergyPlus annual table the run
     wrote, if the IDF asks for one (look in ONE run folder on Speed with a single `ls`); if no annual table
     exists, this gate is NOT_EVALUABLE with that reason (do not invent a substitute; the manager decides).
   * 2.5 run manifest (`pilot/run_manifest.csv`) has every field of §2A; clock origin = midnight on all 50 rows.
   * 3.1 on each of the 5 buildings, hourly electricity differs between every pair of different households.
   * 3.2 same for heating (cooling where heating is zero), reported per class (WARN if identical).
   * 3.3 replicates: per target, max absolute and relative spread across the 5 repeats of each of the 2 inputs.
   * 3.4 schedule md5 differs between households and is identical between repeats (from the manifest).
   * 4.1 annual heating and cooling per m² per class (floor area from the building row), next to the 4 Madrid
     wrapper test values in `Step2_docs/impl/2026-09-29_wp1_wrapper.md` (WARN if far; the wrapper found them high).
   * 4.2 cooling zero in Jan-Feb and Dec (heating-only months); heating zero in Jul-Aug.
   * 4.3 electricity mean over hours of presence > over hours of absence, per household (presence files are in
     the local pilot input folders); pass if >= 90 % of households.
   * Patch lines: the build log of part 1 has every `PATCH ...` line for every input (count them).
   * 5.1 median and 90th percentile seconds per run and max RSS (from `status.txt`); CPU-hours for the draft campaign
     = runs x median s / 3600 with the formula written. Draft runs: take the count from §2A "Run count" of the spec.
   * 5.2 disk: (runs in flight x median raw size) + (all runs x median extracted size) vs the free space in
     `preflight.txt`.
   * 5.3 finish date at 8, 16 and 32 CPUs, starting on the day the report is written; mark which meet 11 Oct 2026;
     if none, apply the 2E cut order (climates to 2 per country, then buildings to 30, then households to 50,
     never drop replicates or average-schedule runs) until one does, and show the arithmetic.
3. Seen failing (val doc Section 6), each on a scratch copy in `%TEMP%`, each must print FAIL: 3.1 (copy one
   household's series onto another on the same building), 2.2 (plant `** Severe  **` in a copy of one err file),
   2.4 (scale one hourly series by 1.01; only if 2.4 is evaluable). Record the exact lines.
4. `Step2_docs/outputs_step2/pilot_report.md`: the §2D list, the gate lines, the three seen-failing lines, the size
   arithmetic, and a one-paragraph plain summary. No recommendation on the CPU share (the manager rules O-5 and O-3).
5. State file: Status DONE, checker SUMMARY + exit code, Next = "manager verifies; manager rules campaign size".

## What the manager will re-derive
One run's annual electricity summed from its extracted file; one replicate spread; the median seconds from the
status files; the checker SUMMARY and exit code.

## 🔴 AMENDMENT 2026-09-30 ~15:25 (manager): ALL COMPUTE ON SPEED, NOTHING ON THE LOCAL CPU
The author said: "use speed cluster resources", "do not use local cpu resources". This overrides every "Local only"
and every local-python line above. Rules:
* Locally you may only: edit/write files, `ssh`/`scp`, `ls`, read small files. **No local python, no local
  EnergyPlus, no local md5 loops over many files.** Never touch any process you did not start (the author's own
  python and EnergyPlus jobs run on this machine).
* Speed: `ssh o_iseri@speed.encs.concordia.ca` (key-based; login shell is tcsh, wrap as `ssh ... "bash -c '...'"`).
  Login node = `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`wc -l` only. Every
  python run goes in an sbatch script: `#SBATCH -p ps`, `-t 7-00:00:00`, `--exclude=antenna1`, `-c 1`,
  `--mem=4G`, python `/speed-scratch/o_iseri/envs/step4/bin/python -u`. Check it imports what you need inside the
  job (print versions first); if a package is missing, record verbatim and stop.
* Stage inputs with `scp` into a task folder under `/speed-scratch/o_iseri/5J/` (named below), md5 one file on each
  side inside the job to show the copy is equal, copy outputs back with `scp` and write them where this task says.
* Jobs here take seconds. After `sbatch`, you may check `sacct -j <id> -X` at most 6 times, 30 s apart (one ssh
  call each: `ssh ... "bash -c 'sleep 30; sacct -j <id> -X --format=JobID,State,ExitCode,Elapsed'"`). If still not
  finished after that, write the JobID in the state file with "manager to read" and stop.
* Write every JobID in the Ledger.
* **Speed folder:** work inside `/speed-scratch/o_iseri/5J/pilot/` (read-only for `runs/`, `extracted/`, `inputs/`);
  put your script, seen-failing copies and outputs in `/speed-scratch/o_iseri/5J/pilot/report/`. Run
  `5thJ_pilot_check.py` there via sbatch against the Speed files directly (you need not copy results back first).
* **Where the stopped employee left it (manager, 15:25):** `_5J_data/surrogate/pilot/speed_results/` holds
  `extracted/`, `runs/`, `md5_speed.txt`, `md5_summary.txt`, `preflight.txt` copied back (a download, fine; count
  what is there and record it; finish step 1 with scp if incomplete). No state file yet; create it.
* Current arrays: 1403962 (task 1) and 1403963 (tasks 2-50); err files at `runs/<run_id>/eplus_out/eplusout.err`;
  the IDF there is `model.idf`. Floor areas: `Step2_docs/outputs_step2/buildings.csv` (scp it up).
