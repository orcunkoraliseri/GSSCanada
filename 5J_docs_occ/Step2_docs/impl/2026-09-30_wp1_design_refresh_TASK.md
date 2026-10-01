# TASK (employee, Sonnet): 5J design refresh on Speed (climates.csv: Manchester + Milan become ok)

Written 2026-09-30 ~15:45 by the 5J manager. This is step 6 of `2026-09-30_wp1_weather_convert_batch2b_TASK.md`,
which stopped because the script needed a path option. The manager has now edited `tools/5thJ_design_tables.py`
(backup `tools/5thJ_design_tables.py.v1_2026-09-30`, old md5 ce1feb64e599f9421617d418b49d73d2):
* the hard-coded `pending` for uk_manchester / it_milan is removed;
* new options `--data DIR` (read root for `_5J_data/surrogate`) and `--openubem DIR` (read root for the three
  OpenUBEM EPWs). The Windows paths written INTO climates.csv are unchanged (ntpath); the options only say where to
  read. The script prints `PATCH read_roots OK ...`: check it is PRESENT in the job output.
* 4J inputs are found relative to the script: `<root>/4J_docs_occ/...` next to `<root>/5J_docs_occ/tools/`.

State file: append `## Design refresh on Speed (<date time>)` to `2026-09-29_wp1_weather.md` (Ledger / Verified /
Decisions / WHAT I DID NOT VERIFY). Run `date` before any time stamp.

## Hard rules
* ALL compute on Speed (author's rule). Locally: edit/write files, `ssh`/`scp`, `ls`, read small files. No local
  python, no local md5 loops. Never touch a process you did not start.
* Speed: `ssh o_iseri@speed.encs.concordia.ca`, tcsh login, wrap as `ssh ... "bash -c '...'"`. Login node:
  `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`wc -l`. Python only inside sbatch:
  `#SBATCH -p ps`, `-t 7-00:00:00`, `--exclude=antenna1`, `-c 1`, `--mem=4G`,
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`. Print python + pandas + pyarrow versions first.
  After `sbatch`: at most 6 `sacct -j <id> -X` checks, 30 s apart, each `sleep 30; sacct ...` in one ssh call.
* 🔴 UK licence: never open or copy any UK diary, UK episode, UK manifest, or the POOLED 4J corpus
  (`4J_step3_corpus.jsonl`). Only the files named below. No wildcard, no folder-wide copy or search.
* Do not edit any script. If the script fails, record verbatim and stop.

## Steps
1. Speed root `R=/speed-scratch/o_iseri/5J/design_refresh`. Stage with `scp`, one named file at a time, keeping
   this layout (G = `C:\Users\o_iseri\Desktop\GSSCanada`):
   * `G\GSSCanada-main\5J_docs_occ\tools\5thJ_design_tables.py` and `...\tools\5thJ_check_design.py`
     -> `R/repo/5J_docs_occ/tools/`
   * `G\GSSCanada-main\4J_docs_occ\Step8_docs\outputs_step8\archetype_idf_manifest.csv`
     -> `R/repo/4J_docs_occ/Step8_docs/outputs_step8/`
   * `G\GSSCanada-main\4J_docs_occ\Step1_docs\outputs_step1\episodes_spain.parquet` and `episodes_italy.parquet`
     -> `R/repo/4J_docs_occ/Step1_docs/outputs_step1/`
   * `G\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl` -> `R/data/inputs/`
   * `G\_5J_data\surrogate\weather\epw\weather_score_5J.json` and the six EPWs `es_valencia_2010.epw`,
     `es_seville_2010.epw`, `uk_birmingham_2014.epw`, `uk_manchester_2014.epw`, `it_turin_2014.epw`,
     `it_milan_2014.epw` -> `R/data/weather/epw/`
   * `C:\Users\o_iseri\Desktop\OpenUBEM\openubem\data\weather\es_madrid_2009_2010_y2010.epw`,
     `uk_london_2014_2015_y2014.epw`, `it_bologna_2013_2014_y2014.epw` -> `R/openubem/`
   * the CURRENT tables `G\GSSCanada-main\5J_docs_occ\Step2_docs\outputs_step2\buildings.csv`, `households.csv`,
     `climates.csv`, `pilot_runs.csv`, `design_md5.txt` -> `R/before/`
2. One sbatch job: `md5sum` of every staged file (compare the script's md5 with the local one you record by
   `certutil -hashfile <file> MD5` for that ONE file); then
   `python -u R/repo/5J_docs_occ/tools/5thJ_design_tables.py --out R/after --data R/data --openubem R/openubem`;
   then `cmp` each of the 4 csv in `R/after` against `R/before` and `diff R/before/climates.csv R/after/climates.csv`
   and `diff R/before/design_md5.txt R/after/design_md5.txt`; then
   `python -u R/repo/5J_docs_occ/tools/5thJ_check_design.py --dir R/after --manifest R/repo/4J_docs_occ/Step8_docs/outputs_step8/archetype_idf_manifest.csv; echo EXIT=$?`.
3. Seen failing (second job, or same job after the real run): copy `R/data` to `R/bad_data`, append one byte to
   `R/bad_data/weather/epw/it_milan_2014.epw`, run the script with `--data R/bad_data --out R/bad_out`: it must stop
   with `md5 of ... differs from the score json`. Record the line and exit code.
4. Expected: buildings.csv, households.csv, pilot_runs.csv IDENTICAL (cmp silent); climates.csv differs ONLY in the
   uk_manchester_2014 and it_milan_2014 rows, which now carry md5 feb4aca1a755516b025653bf066112d4 /
   ae285a50b2fa50d7af5b0dfeec040170, rmse 1.138 / 3.166, ghi 984 / 1326, status ok; the path column is still the
   Windows path; design_md5.txt differs ONLY in the climates.csv and 5thJ_design_tables.py lines; checker SUMMARY
   FAIL=0 NOT_EVALUABLE=0, exit 0. **If anything else differs: do not copy anything back; record and stop.**
5. Only if step 4 holds: `scp` `R/after/climates.csv` and `R/after/design_md5.txt` back over the two files in
   `Step2_docs\outputs_step2\` (first copy the two old files to `Step2_docs\outputs_step2\v2_pre_refresh_2026-09-30\`).
   Nothing else is copied back.

## Report back (short)
PATCH line present y/n; cmp results; the climates diff lines; design_md5 diff; checker SUMMARY + exit code;
the seen-failing line + exit code; JobIDs.
