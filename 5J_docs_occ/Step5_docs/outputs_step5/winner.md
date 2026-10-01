# 5J Step 5: the pinned surrogate S (rules R7)

Written 2026-10-01 01:00 EDT by the manager from the job outputs named below (validation only; no test file was opened).

## Winner
* **S3**: TCN, width 64, large (16 blocks), λ = 1 (pair term on), seed 1; best epoch 16 of 20, validation loss 0.125884
  (level 0.123998, pair 0.001885). Checkpoint md5 78271da9e338312149e6da1a07cdb28a, pinned read-only at
  `/speed-scratch/o_iseri/5J/train/winner/pinned/best.pt`; full record `train/winner/winner.json` (code md5s equal to training).
* Inputs under rules AMENDMENT 2 (static vector clipped to the development range; es_B40 clipped on 693 validation rows).
* Reload check (R7.4): job 1404985, recomputed loss = logged loss (difference 0); planted 1e-3 shift fails as it should. The
  first reload job 1404811 printed FAIL on equal values because the check compared the checkpoint float to the 6-dp copy in
  winner.json with a 1e-9 tolerance; fixed by the manager (tolerance 5e-7 for that copy, 5e-5 for "4 dp"), see
  `impl/2026-09-30_wp3_winner.md`.

## How it was chosen (R7.3, jobs 1404807-1404810; re-derived by the manager with own code, job 1404988: same winner)
| Config | Family | G5J.3 PASS of 32 | median G5J.3 R² heat+cool | G5J.2 PASS of 32 | val loss |
|---|---|---|---|---|---|
| S2 | TCN 64 large λ0 | 29 | 0.753 | 19 | 0.1194 |
| **S3** | TCN 64 large λ1 | **30** | **0.820** | 19 | 0.1259 |
| S1 | TCN 64 small λ1 | 30 | 0.795 | 16 | 0.1479 |
| S11 | Transformer 64 large λ1 | 30 | 0.753 | 22 | 0.1100 |
| S9 | Transformer 64 small λ1 | 22 | 0.719 | 16 | 0.1180 |
| S13 | Transformer 128 small λ1 | 30 | 0.767 | 21 | 0.1185 |

Four configurations tie at 30; S3 has the highest median heating/cooling R².

## The winner on validation (job 1404809, frozen scorer md5 84d1dafa..., `--b1 pred/B1 --control pred/B0`)
* G5J.1 8/8; G5J.2 19/32; G5J.3 30/32; G5J.4 32/32 (control line = B0 here; C does not exist yet); G5J.5 8/8.
* G5J.3 fails: Spain SFH heating (R² 0.49 vs B1 0.59) and Spain AB heating (R² 0.54, skill interval contains 0).
* G5J.3 skill over B1 excludes 0 above in 30 of 32 cells (14 of 16 heating + cooling).
* G5J.2 (load accuracy, ASHRAE bands) fails 13 cells: heating and cooling in larger buildings, worst Italy MFH / AB heating
  (median |NMBE| 36 % / 28 %) and cooling (CV(RMSE) 156 % / 187 %). A RESULT: S gets the household effect right far more often
  than it gets the absolute load right, the mirror image of the Step 4 stand-in. No threshold is changed.
* Manager re-derivation (own code): it SFH heating R² 0.9276, sign 0.9865 over 4,755 pairs = the scorer's line.

## B1 for comparison
* B1 (HistGradientBoosting, unclipped as trained): G5J.2 22/32, G5J.3 25/32 against B0 (job 1404526; manager-verified, see
  `impl/2026-09-30_wp3_b1.md`).
* **Sensitivity (rules AMENDMENT 3, sealed 00:31 before this was read):** B1 predicted below 0 kWh in 29 % of heating and 36 % of
  cooling hours. Clipped at 0 (as S and C), B1 passes G5J.3 in 26/32. Re-scored against the clipped B1, the six candidates pass
  G5J.3 in S2 28, **S3 30**, S1 30, S11 30, S9 20, S13 29; R7.3 still picks **S3** (job 1404988, `train/score_sens/`). From
  Step 6 on, every B1 prediction is clipped at 0.

## Not yet done (part E)
Blind control C (seeds 1-3), S3 seeds 2 and 3, one-country trainings (S and B1, Spain only and Italy only).
