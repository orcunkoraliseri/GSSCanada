
## S grid (written 2026-09-30 20:25 EDT by the part C employee; timing to be added from the smoke log)
Jobs: smoke 1404529; grid array 1404530 (indices 0-15, `%8`, afterok 1404529). Code: tools/speed/s5_*.py (md5 in each run's run_info.json). Seed 1, AdamW lr 1e-3, wd 1e-4, cosine, 30 epochs x 400,000 windows (781 steps of 512 windows), bf16, patience 4, cap 4 GPU-hours.
| index | family | width | depth (blocks / layers) | lambda |
|---|---|---|---|---|
| 0 | TCN | 64 | small (8) | 0 |
| 1 | TCN | 64 | small (8) | 1 |
| 2 | TCN | 64 | large (16) | 0 |
| 3 | TCN | 64 | large (16) | 1 |
| 4 | TCN | 128 | small (8) | 0 |
| 5 | TCN | 128 | small (8) | 1 |
| 6 | TCN | 128 | large (16) | 0 |
| 7 | TCN | 128 | large (16) | 1 |
| 8 | Transformer | 64 | small (3) | 0 |
| 9 | Transformer | 64 | small (3) | 1 |
| 10 | Transformer | 64 | large (6) | 0 |
| 11 | Transformer | 64 | large (6) | 1 |
| 12 | Transformer | 128 | small (3) | 0 |
| 13 | Transformer | 128 | small (3) | 1 |
| 14 | Transformer | 128 | large (6) | 0 |
| 15 | Transformer | 128 | large (6) | 1 |
Expected grid time: pending the smoke timing (train/ckpt/smoke/smoke_timing.json, TIMING lines in train/logs/s5_smoke_1404529.out). Predictions are NOT written for the grid (part D, shortlist only).

## S grid (re-run under AMENDMENT 2) (written 2026-09-30 21:21 EDT by the clip employee)
VOID: every earlier S grid result (array 1404570, smoke 1404569, and the older 1404529/1404530 runs); no 1404570 row existed in this file, none was deleted; outputs moved to train/ckpt/S_void_1404570 and ckpt/smoke_void_1404569, never pinned.
Jobs: void-move 1404629 (done), smoke 1404630 (afterok 1404629), grid array 1404631 (indices 0-15, %4, afterok 1404630). Same 16 configurations and s5_grid.json (md5 d69b81761daecd2b3caa3731ad37533f) as above; only change: static inputs clipped to the development range (rules AMENDMENT 2). Results to be added by the manager after the smoke CHECK lines are read.

## Winner (part D, written 2026-09-30 23:24 EDT by the winner employee; running, manager reads)
Jobs: shortlist 1404807 (done), predictions array 1404808, scorer array 1404809 (afterok 1404808 and the B1 scorer 1404526), winner 1404810, reload + pin 1404811, cleanup 1404812. State: `Step5_docs/impl/2026-09-30_wp3_winner.md`.
Shortlist from the valid grid (array 1404631; best validation sum = level + pair): TCN S2 0.11943, S3 0.12588, S1 0.14793; Transformer S11 0.10998, S9 0.11803, S13 0.11846.
Winner, G5J.3 / G5J.2 counts, reload check: pending (running, manager reads).

## Control and seeds (part E, written 2026-10-01 01:08 EDT by the control employee; running, manager reads)
Jobs: code checks 1405047 (done, all CHECK lines PASS), flags-off reload of pinned S3 1405048, S and C trainings array 1405051 (0 S_seed2, 1 S_seed3, 2-4 C_seed1-3, blind control, config differs from the winner only by `blind: true` plus the seed), predictions 1405053, frozen scorer array 1405054 (`--b1 pred/B1_clip0 --control pred/B0`), pinned S3 vs C seed 1 scorer 1405055 (`score_S3_vsC.txt`), seeds summary 1405056 (`train/winner/seeds.json`). State: `Step5_docs/impl/2026-09-30_wp3_control.md`. Results (G5J.3 PASS cells, median R2, G5J.4, seed spread): pending (running, manager reads).

## One-country trainings (part E, written 2026-10-01 01:08 EDT by the control employee; running, manager reads)
S one-country (winner configuration S3, seed 1, climate one-hot dropped, 47 static columns, static mean/SD/range from that country's development rows): array 1405052 (5 Spain, 6 Italy) into `train/ckpt/S_loco_es`, `S_loco_it`. B1 one-country (chosen configuration per target reused, no re-tuning, climate dropped): jobs 1405049 (Spain), 1405050 (Italy) into `train/ckpt/B1_loco_es`, `B1_loco_it`; outputs clipped at 0 kWh with the total recomputed (AMENDMENT 3). No prediction of the other country here (Step 6 scores them on its test lists). Results: pending (running, manager reads).

## Manager results (2026-10-01 02:52 EDT; fills the "pending" lines above, which stay as written)
* Winner (part D): S3, TCN 64 large λ1, seed 1; validation G5J.3 30/32, G5J.2 19/32; reload equal; pinned md5 78271da9...;
  full record `winner.md`. Manager re-derived.
* Control and seeds (part E): C seeds 1-3 G5J.3 0/32 each (median heat+cool R² -0.10 / -0.10 / -0.13) -> G5J.4 PASS (32/32
  lines with C seed 1 as control of S3). S seeds 1 / 2 / 3: G5J.3 30 / 22 / 13 of 32, median R² 0.82 / 0.73 / 0.67, G5J.2
  19 / 17 / 17 (seeds 2 and 3 early-stopped at epochs 4 and 2). All against B1 clipped at 0 (AMENDMENT 3). Manager re-derived.
* One-country: S_loco_es best val 0.188 (epoch 5), S_loco_it 0.122 (epoch 10); B1_loco_es / B1_loco_it COMPLETED (jobs
  1405049 / 1405050, exit 0; refit val_mse_std heating 0.024 / 0.040, cooling 0.192 / 0.059, equipment 0.0016 / 0.0154;
  20.5 % / 21.8 % of values clipped at 0; model md5s in the job logs). Scored on test in Step 6 (G5J.6, reported).
