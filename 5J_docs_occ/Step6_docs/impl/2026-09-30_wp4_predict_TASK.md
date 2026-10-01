# TASK (employee, Sonnet): 5J Step 6 part A: scorer test mode (dated amendment), test drivers, test predictions

Written 2026-09-30 by the 5J manager (stamp = file time; `date` before every stamp you write). Launch ONLY after Step 5 is closed
by the manager (winner, C and seeds pinned; Step 5 Progress Log says CLOSED). Nothing is trained or tuned in Step 6.
Read first, in full: `Step6_docs/5thJ_06_sealedScoring.md`, `Step6_docs/5thJ_06_sealedScoring_val.md`,
`Step4_docs/outputs_step4/gates_frozen.md` (esp. §8 Amendments), `Step5_docs/outputs_step5/step5_rules.md` (incl. amendments),
`Step5_docs/outputs_step5/models.md`, `Step5_docs/outputs_step5/winner.md`, `Step5_docs/impl/2026-09-30_wp3_store_TASK.md` (hard
rules; they bind you, EXCEPT the test-list rule, replaced below), `tools/speed/5thJ_04_scorer.py`, `tools/speed/s5_common.py`,
`tools/speed/s5_store.py`, `tools/speed/s5_predict.py`, `tools/speed/s5_b1.py`, `tools/speed/s5_b0.py`, `tools/speed/frz_freeze.sbatch`.
State file: create `Step6_docs/impl/2026-09-30_wp4_predict.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* Speed sbatch only; nothing on the local CPU; login node as in the part A task. All 5J jobs together at most 30 CPUs; GPU
  `-p ps --gres=gpu:nvidia_a100_2g.20gb:1 -c 3 --mem=48G -t 7-00:00:00 --exclude=antenna1`. Spain + Italy only; never a UK file;
  no folder-wide search or wildcard. Never wait; at most 6 sacct checks per job; past ~150k tokens hand off.
* 🔴 TEST TRUTH IS NEVER READ IN THIS PART. Predictors read only DRIVERS of test runs (household files, weather, building table,
  run table). The extracted EnergyPlus files of test runs are read ONLY by the frozen scorer in part B. Every driver read of a test
  run goes through a guarded reader that logs it to `/speed-scratch/o_iseri/5J/test/openlog_drivers.tsv` with kind `driver`; a
  check at the end FAILS if any line of any open log under `test/` has a kind other than `driver` or a path under
  `campaign/extracted/`.
* Test lists allowed now: `test_new_households`, `test_new_buildings`, `test_both_new`, `b0_test` (+ `b0_dev` for test runs on
  development buildings). Never `unused`, never `loco_es`/`loco_it`. Write only under `/speed-scratch/o_iseri/5J/test/` (new
  folder) and, for the amendment, the files named in A.
* Additive only: never overwrite anything under `freeze/`, `train/`, `campaign/`, `splits/`.

## Parts
A. **Scorer test mode = a dated AMENDMENT of the freeze (written BEFORE any test prediction exists).** The frozen scorer refuses
   test lists (`ALLOWED_SPLITS`, line ~46; `assert a.split in ("development","validation")`, line ~364). Write
   `tools/speed/5thJ_04_scorer_t.py` = the frozen scorer with ONLY these changes: a `--test` flag; with it, the allowed lists are
   the three test lists + `b0_test` + `b0_dev`, `--split` may be one of the three test lists, the B0 ids used inside are
   `b0_dev + b0_test`, and it refuses to start unless `/speed-scratch/o_iseri/5J/gates_frozen.md5` exists. Without `--test` it must
   behave byte for byte like the frozen scorer: run both on the validation B0 scoring (same args as job 1404521) and diff the score
   files (equal except the start-time line; print the diff). Print `diff -u` of the two scorer files (only the intended lines).
   Append to `Step4_docs/outputs_step4/gates_frozen.md` §8 a dated amendment (what, why, the diff summary, old and new md5s,
   "no test result existed when this was written"); lock on Speed: copy to `/speed-scratch/o_iseri/5J/freeze/5thJ_04_scorer_t.py`
   chmod 444 and write `/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5` (md5 of the amended gates_frozen.md, the new scorer,
   split_loader) chmod 444, with the same prefix-unchanged check as job 1404523 (the old gates_frozen.md bytes must be an
   unchanged prefix of the new one). The original lock file is never touched.
B. **Test drivers store** `/speed-scratch/o_iseri/5J/test/store/`: `flats_<list>.parquet` for the three test lists, same columns
   and code path as the Step 5 store (`s5_store.py` functions reused, NO targets file), households of the test pools added to
   `hh_<cc>.npz` copies under `test/store/` (the train store is never modified), `norm.json` and `static_cols.json` COPIED from
   the train store (never recomputed). Checks: rows per list, every hid found, no NaN, static columns identical to
   `static_cols.json`, open log kinds = `driver` only.
C. **Predictions** (scorer layout, `test/pred/<model>/<climate>/<run_id>.csv.gz`) for every run of the three test lists:
   `B0` (the b0 run of the same building and climate: `b0_dev` for development buildings, `b0_test` for test buildings; these are
   B0 RUNS, their own extracted files are allowed because they are B0 inputs, log kind `b0`), `B1` (the 3 saved models, unchanged),
   `S` (pinned winner, `train/winner/pinned/`, md5 checked against `winner.json` before use), `C` (C seed 1, md5 printed).
   For G5J.6 (leave one country out): `S_loco_es` and `B1_loco_es` predict the ITALIAN runs of the three test lists, `S_loco_it` and
   `B1_loco_it` the SPANISH ones (`test/pred/<model>/...`). Every checkpoint md5 printed and compared to the Step 5 records
   (val 1.2 of Step 6).
   🔴 (manager note 2026-09-30 21:20 EDT, rules AMENDMENT 2): S, C and S_loco_* static vectors are z-scored AND clipped with the
   checkpoint's own `static_stats` (mean, sd, zmin, zmax); a checkpoint without zmin/zmax is refused. Use the `s5_data.py` code
   path (same function), never a re-implementation. Print `STATIC_CLIP` per list (values clipped, columns) and record it.
   🔴 (manager note 2026-10-01 00:32 EDT, rules AMENDMENT 3, md5 5e937d09...): B1, B1_loco_es and B1_loco_it outputs are
   clipped at 0 kWh (heating, cooling, equipment) and total electricity is recomputed from the clipped values, exactly as S
   and C. Print per model the count of values clipped. The pinned winner is S3 (`train/winner/winner.json`).
   🔴 (manager note 2026-10-01 02:05 EDT, spec 6D "seed spread"): also predict `S_seed2` and `S_seed3`
   (`train/ckpt/S_seed2/best.pt`, `train/ckpt/S_seed3/best.pt`; md5 from `train/winner/seeds.json`) on the three test lists
   into `test/pred/S_seed2`, `test/pred/S_seed3`. Reported only.
D. Write JobIDs and the prediction counts in the state file; Next = "manager verifies predictions; part B = ONE scoring job".

## Report back (short, plain)
JobIDs; the amendment md5s; the byte-for-byte diff result; prediction counts per model and list; status.

## What the manager will re-derive
The amendment diff (only intended lines); one test flat's S prediction recomputed from the pinned checkpoint and the test drivers;
open logs: no test truth read.

## Manager note before launch (2026-10-01 02:06 EDT)
* Step 5 is verified except the Italy-only B1 (job 1405050, running; `train/ckpt/B1_loco_it`). Launch now; the ONE prediction task
  that needs `B1_loco_it` (it predicts the SPANISH test runs) gets `--dependency=afterok:1405050`; everything else may run now.
  If 1405050 fails, stop that task, write it in the state file, and end.
* Records to check checkpoints against: `train/winner/winner.json` (S3, md5 78271da9...), `train/winner/seeds.json` (S seeds 2-3,
  C seeds 1-3), `Step5_docs/impl/2026-09-30_wp3_control.md` (S_loco_es/it, B1_loco_es/it md5s), `ckpt/B1/*.joblib` md5s in
  `Step5_docs/impl/2026-09-30_wp3_b1.md`.
* C on test = the blind control exactly as trained: household and neighbour drivers replaced by the donor row drawn with the
  SAME md5 rule (`s5_data.blind_donors`) inside the same test list table. Print the donor checks (0 same-run, 0 other-country).
* `s5_data.Data` and `s5_b1.Ctx` refuse test splits by design. Add a store-directory argument (default = the train store, so
  every Step 5 path is unchanged; prove it with the same flags-off equality check part E used) and point it at `test/store/`.
  No re-implementation of windows, features, clipping or the total rule.
* CPU/GPU: at most 4 GPU slices at once; all 5J jobs together <= 30 CPUs (Step 6 part B0 job 1405073 uses 4 CPUs until done).
