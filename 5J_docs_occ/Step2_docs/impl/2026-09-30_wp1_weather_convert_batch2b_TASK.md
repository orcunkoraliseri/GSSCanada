# TASK (employee, Sonnet): 5J weather batch 2b: convert, check and score Manchester 2014 + Milan 2014, then refresh climates.csv

Written 2026-09-30 ~15:15 by the 5J manager. Same method as batch 2a: read
`2026-09-29_wp1_weather_convert_TASK.md` and `2026-09-29_wp1_weather_convert_seville_TASK.md` (same folder) in
full; this task is batch 2a with TWO sites, **uk_manchester (2014)** and **it_milan (2014)**, plus one design-table
refresh. The download is finished (78 of 78 zips at 15:09; PID 19328 has exited).
State file: append a new section `## Convert batch 2b: Manchester + Milan (<date time>)` to
`2026-09-29_wp1_weather.md` (Ledger / Verified / Decisions / WHAT I DID NOT VERIFY). Do not edit sections above it.
Run `date` before writing any time stamp.

## Hard rules
* Local only. Python: `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`.
* Never call CDS or start a download. Never edit OpenUBEM or `4J_docs_occ`. Do not edit
  `tools\5thJ_check_epw.py`, the converter or `tools\5thJ_design_tables.py`; if one fails, record verbatim and stop.
* 🔴 UK licence: UK **weather** and UK TABULA are fine. Never open any UK diary, UK episode, UK manifest, any pooled
  4J file (e.g. `4J_step3_corpus.jsonl`) or anything built from UK diaries. **No repo-wide or folder-wide search and
  no wildcard over csv/json/parquet**; open only the files this doc names. Never wait or poll.

## Steps
1. Re-count `raw\era5_uk_manchester_2014\*.zip` = 13 and `raw\era5_it_milan_2014\*.zip` = 13, else stop.
2. Convert: `<python> <tools>\convert_era5_5J_to_epw.py --site uk_manchester --site it_milan --all-years`, log to
   `logs\convert_batch2b_2026-09-30.log`. Expected `epw\uk_manchester_2014.epw` and `epw\it_milan_2014.epw`.
3. Checker: re-run only the row-count gate seen failing (copy in `%TEMP%`, delete the last data row → FAIL, record
   the line and exit code, delete the copy), then the checker on both real EPWs. Add both to
   `epw\epw_check_batch2.json` (keep the Seville entry unchanged).
4. Score like batch 2a (RMSE of monthly means vs TABULA `targets.<country>.theta_month`; TMYx difference if a
   Manchester / Milan station exists in `candidates.uk` / `candidates.it`, else "no TMYx reference"). **Add** both
   to `epw\weather_score_5J.json`; show the existing seven entries' rmse before/after unchanged.
5. md5 of both EPWs into the state file.
6. Refresh the design: record md5 of every file in `Step2_docs\outputs_step2\` (top level only, by name) BEFORE;
   run `<python> <tools>\5thJ_design_tables.py` (defaults); md5 AFTER. Expected: only `climates.csv` and
   `design_md5.txt` change, climates rows uk_manchester and it_milan now have md5 + status ok. **If any other file
   changes, restore it from your BEFORE copy, record the diff summary and stop.** Then
   `<python> <tools>\5thJ_check_design.py` → record its SUMMARY line and exit code.

## Report back (short)
Converter result; gate line + exit code; two real SUMMARY lines; RMSE + July/January means per city; two md5s;
which outputs_step2 files changed; checker SUMMARY + exit code.

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
* **Speed folder:** `/speed-scratch/o_iseri/5J/weather_batch2b/`.
* **Where the stopped employee left it (manager, 15:25):** step 2 (converter) already ran locally before the stop:
  `epw/uk_manchester_2014.epw` and `epw/it_milan_2014.epw` exist (15:14), log `logs/convert_batch2b_2026-09-30.log`
  ends with EPW_SHA256 lines for both; `epw/epw_check_batch2.json` was rewritten at 15:14 (read it: does it hold
  Manchester and Milan entries, and is Seville unchanged?). `weather_score_5J.json` is unchanged (21:24 yesterday).
  Do NOT rerun the converter. Start at step 3, all on Speed. Step 6 (design tables) also runs on Speed: stage the
  script, `tools/5thJ_check_design.py`, and exactly the inputs the script opens (read its source for the paths and
  the md5 guard; the Spain+Italy corpus copy `_5J_data/surrogate/inputs/4J_step3_corpus_es_it.jsonl` is allowed;
  NEVER the pooled 4J corpus or any UK file). If the script cannot be pointed at the Speed copies without editing
  it, stop and write "manager: step 6 needs a path option".
