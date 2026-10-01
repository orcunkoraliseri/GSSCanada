# TASK (employee, Sonnet): 5J Step 6 part B: the ONE scoring job on the sealed test lists

Written 2026-09-30 by the 5J manager (stamp = file time; `date` before every stamp you write). Launch ONLY after the manager has
verified Step 6 part A (state file `Step6_docs/impl/2026-09-30_wp4_predict.md` has a "MANAGER VERIFIED" section). Nothing is
trained, tuned or re-predicted in this part. Read first, in full: `Step6_docs/5thJ_06_sealedScoring.md`,
`Step6_docs/5thJ_06_sealedScoring_val.md`, `Step4_docs/outputs_step4/gates_frozen.md` (incl. §8 amendments),
`Step5_docs/outputs_step5/winner.md`, `Step5_docs/outputs_step5/models.md`, the part A task and state file, the hard rules of
`Step6_docs/impl/2026-09-30_wp4_predict_TASK.md` (they bind you, except that the frozen test-mode scorer may now read test truth).
State file: create `Step6_docs/impl/2026-09-30_wp4_scoring.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* Speed sbatch only; nothing on the local CPU; login node: sbatch/squeue/sacct/scancel/scontrol/scp/ls and single-file
  cat/tail/grep/wc only. All 5J jobs together at most 30 CPUs (this job: `-c 16 --mem=96G`, scorer `--workers 16`;
  `-p ps -t 7-00:00:00 --exclude=antenna1`). Spain + Italy only; never a UK file; no folder-wide search or wildcard.
* 🔴 Test truth is read ONLY by the locked test-mode scorer `/speed-scratch/o_iseri/5J/freeze/5thJ_04_scorer_t.py --test`, inside
  the ONE scoring job. You never open, list the contents of, or summarise a test truth file yourself.
* 🔴 The scoring job is submitted ONCE. If it crashes, its crashed sections are NOT_EVALUABLE; a rerun of the same frozen code on
  the same inputs is allowed only with the crash line copied into the ledger; any code change = a new dated amendment of
  `gates_frozen.md` §8 written BEFORE the rerun (stop and hand back to the manager instead of writing it yourself).
* A verdict is copied as the scorer printed it. No rewording, no rounding of a verdict, no dropping of a line.

## Parts
A. **Start-up checks script** `tools/speed/s6_startup.sh` (bash, no python; md5sum + grep only), used by both B and C:
   (1) md5 of `freeze/5thJ_04_scorer_t.py`, the amended `gates_frozen.md` copy and `split_loader.py` equal the lines of
   `/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5` (val 1.1); (2) md5 of every checkpoint used in part A predictions
   (B1 x3, pinned S, C seed 1, S_loco_es/it, B1_loco_es/it) equals the Step 5 records (`winner.json`, `seeds.json`, models.md)
   (val 1.2); (3) md5 of `test_new_households`, `test_new_buildings`, `test_both_new`, `b0_test`, `b0_dev` lists equal
   `splits/splits.md5` AND the Step 3 Progress Log line of 2026-09-30 18:50 (val 1.3). Each check prints
   `STARTUP <name> PASS|FAIL <expected> <found>`; any FAIL -> `exit 9` BEFORE any scorer call. Prints `STARTUP_ALL PASS` last.
B. **Seen failing (val section 4), on VALIDATION, no test truth:** a job that copies the scorer, the md5 file and one checkpoint
   to a scratch folder under `/speed-scratch/o_iseri/5J/test/seenfail/`, changes one byte in each copy in turn (3 runs, one per
   check 1-3; for check 3 a copy of `b0_test.txt` with one changed byte), runs `s6_startup.sh` pointed at the scratch copies
   (a `ROOT=` variable; the real paths are the default), and must print FAIL + exit 9 each time, and PASS + exit 0 on the
   untouched copies. No scorer call happens in this job. Record the 4 exit codes.
C. **THE scoring job** `tools/speed/s6_score.sbatch` (one job, submitted once, afterok B): runs `s6_startup.sh` (real paths; exit 9
   stops everything), prints `SCORER_MD5 ... PRESENT`, then calls the test-mode scorer in this order, one `--tag` each, all
   outputs under `/speed-scratch/o_iseri/5J/test/score/`:
   * for each LIST in test_new_households, test_new_buildings, test_both_new:
     `S_<LIST>`  : `--pred test/pred/S  --b1 test/pred/B1 --control test/pred/C --secondary`
     `C_<LIST>`  : `--pred test/pred/C  --b1 test/pred/B1 --control test/pred/C`
     `B1_<LIST>` : `--pred test/pred/B1 --b1 test/pred/B1 --control test/pred/C`
     `B0_<LIST>` : `--pred test/pred/B0 --b1 test/pred/B1 --control test/pred/C`   (val 3.1: B0's G5J.3 R² about 0)
     `SloES_<LIST>`: `--pred test/pred/S_loco_es --b1 test/pred/B1_loco_es --control test/pred/B0` (Spanish runs have no
       prediction and fall out of the scored set; only the ITALIAN lines count for G5J.6, the Spanish ones are listed as such)
     `SloIT_<LIST>`: same with `_loco_it` (only the SPANISH lines count)
   * `--split <LIST> --test --floors <the same floors.json as job 1404521> --nboot <frozen default> --workers 16`.
   * every call's exit code printed as `CALL <tag> EXIT <n>`; a call that exits 1 does not stop the next call.
   The job ends with `S6_DONE`. 18 scorer calls, one job.
   (Manager additions 2026-10-01 02:05 EDT, spec 6D:) per LIST also `Sseed2_<LIST>` and `Sseed3_<LIST>` (`--pred
   test/pred/S_seed2` / `S_seed3`, same `--b1 test/pred/B1 --control test/pred/C`), REPORTED only = 6 more calls (24 in all);
   then the LOCKED `freeze/s6_reported_v2.py --test` (md5 checked in `s6_startup.sh` against `freeze/s6_reported_v2.md5`;
   NEVER the v1 file `freeze/s6_reported.py`, VOID since 2026-10-01 02:21: its lag took the most positive correlation) on S for
   each LIST (3 calls). The startup script (part A) also checks the md5 of `S_seed2`/`S_seed3` checkpoints against
   `seeds.json`. The collect job's line-count check covers the 24 scorer calls.
D. **Collect (separate CPU job, afterany C, reads only the score_*.txt files):** `tools/speed/s6_collect.py` -> 
   `Step6_docs/outputs_step6/scores.parquet` (one row per printed GATE line: tag, model, list, gate, country, class, target,
   verdict, the printed numbers, the printed interval if any) and `SUMMARY.txt` (the SUMMARY_GATE and SCORER_EXIT lines of every
   call, verbatim, plus one line per call: tag, exit code); `bootstrap_intervals.csv` (the interval columns only). Checks
   (val 2.1-2.3): per call, GATE line count equals the count of the same model on validation (job 1404521 layout: 8 G5J.1,
   32 G5J.2, 32 G5J.3, 32 G5J.4, 8 G5J.5 lines); every verdict in {PASS, FAIL, NOT_EVALUABLE}; every NOT_EVALUABLE has a reason;
   exit code consistent with the lines (scorer docstring lines 12-14). Plant one missing line in a COPY of one score file and
   show the count check FAIL (seen failing). scp the three outputs back to `Step6_docs/outputs_step6/`.
   (Manager addition 2026-09-30 21:26 EDT, spec 6D:) also print `TEST_OPENS <tag> <n files> <job ids>` per call from the
   scorer's `openlog_<tag>.tsv` (must equal the runs of the list, all from the ONE scoring job; FAIL otherwise), and write
   `claims.txt`: per target and list, S's G5J.3 PASS count of 8 and per country of 4, the NOT_EVALUABLE cell names, the G5J.4
   FLAGGED count, and the 6D verdict word (holds / partly / does not hold / withdrawn), computed by code from `scores.parquet`.
E. Write JobIDs, exit codes, the SUMMARY_GATE lines (verbatim) and the val 3.1 / 3.2 numbers into the state file. Next =
   "manager re-derives 3 numbers (val section 5); then part C (reported analyses: thermal-mass lag, mild-climate cooling)".

## Report back (short, plain)
JobIDs; start-up and seen-failing exit codes; per call the exit code; the SUMMARY_GATE lines of S on the three lists; status.

## What the manager will re-derive (val section 5)
One run's hourly CV(RMSE) of total electricity from the saved S prediction and the EnergyPlus file; one pair's annual difference
sign for S and for EnergyPlus; one class's G5J.3 R² from `scores.parquet` rows. All inside a Speed job, Spain or Italy only.

## Manager note before launch (2026-10-01 04:01 EDT)
* Part A is MANAGER VERIFIED (`Step6_docs/impl/2026-09-30_wp4_predict.md`, section at the end). Launch now.
* Records for the start-up checks (part A of this task): scorer `freeze/5thJ_04_scorer_t.py` and amended gates doc against
  `/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5`; `freeze/s6_reported_v2.py` against `freeze/s6_reported_v2.md5` (NEVER
  `freeze/s6_reported.py`, VOID); every checkpoint used in part A (S, C, S_seed2, S_seed3, S_loco_es, S_loco_it, B1 x3,
  B1_loco_es x3, B1_loco_it x3) against `/speed-scratch/o_iseri/5J/test/ckpt_md5_snapshot.tsv` AND, for S, `train/winner/winner.json`;
  split lists against `splits/splits.md5`. The startup script's own seen-failing job (part B) must flip one byte in a copy of
  each kind of record, including the s6_reported_v2 copy.
* Predictions: `test/pred/<model>/` for B0, B1 (already clipped at 0, AMENDMENT 3), S, C, S_seed2, S_seed3, S_loco_es, S_loco_it,
  B1_loco_es, B1_loco_it. `--floors`: the floors file used by job 1404521 (read its SCORER start line / the freeze record).
* `s6_reported_v2.py --test` calls (one per LIST, after that LIST's scorer calls): `--pred test/pred/S --split <LIST> --out
  test/score/ --tag reported_S_<LIST> --pairs-ref test/score/score_S_<LIST>.txt --workers 16`; their exit codes are printed as
  `CALL reported_S_<LIST> EXIT <n>` like the scorer calls.
* CPU: nothing else of 5J is running; the scoring job takes `-c 16 --mem=96G`, the collect job 2 CPUs.
