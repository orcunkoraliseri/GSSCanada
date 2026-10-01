# TASK (employee, Sonnet): 5J Step 5 part E: blind control C, seeds 1-3, one-country trainings (rules R8, R9)

Written 2026-09-30 by the 5J manager (stamp = file time; `date` before every stamp you write). Launch only after part D's winner
is verified by the manager. Read first, in full: `Step5_docs/outputs_step5/step5_rules.md` (THE RULES incl. AMENDMENT 1; esp. R8,
R9, R6 budget, R11; never change them), `Step5_docs/impl/2026-09-30_wp3_store_TASK.md` (hard rules, they bind you unchanged), the
state files `Step5_docs/impl/2026-09-30_wp3_s.md`, `..._wp3_b1.md`, `..._wp3_winner.md`, `Step5_docs/outputs_step5/models.md`,
`tools/speed/s5_data.py`, `s5_train.py`, `s5_predict.py`, `s5_b1.py`, and `/speed-scratch/o_iseri/5J/train/winner/winner.json`
(`cat`). State file: create `Step5_docs/impl/2026-09-30_wp3_control.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules (short)
As part D. GPU jobs `-p ps --gres=gpu:nvidia_a100_2g.20gb:1 -c 3 --mem=48G -t 7-00:00:00 --exclude=antenna1`. All 5J jobs together
at most 30 CPUs: GPU trainings at most 7 at once (21 CPUs) and the B1 one-country jobs one at a time (6 CPUs). Never wait.

## Parts
A. Code (additive; the winner's code path must stay byte-identical when the new flags are off: print the md5 of each s5_*.py before
   and after and run the winner's reload check again with the new code, flags off, equal to 4 decimals):
   * `--blind` (R8): for every (run, flat) row of a split, donor = a random row of ANOTHER run of the same country in the same split,
     drawn with `random.Random(int(md5("<run_id>|<flat>|blind|20260930").hexdigest(), 16))`; the row's household drivers (hh_index)
     AND neighbour drivers (nb_same, nb_above, nb_below and their flags) are replaced by the donor's; building, static vector,
     weather, calendar and targets unchanged. Applied to development (training) and to validation (early stopping and prediction).
     Print the share of rows whose donor hid equals the own hid (INFO) and FAIL if any donor is from the same run.
   * `--seed N` (torch, numpy, python; default 1).
   * `--country es|it` and `--no-climate` (R9): rows of one country only in training and in validation; climate one-hot columns
     dropped from the static vector (print the static column count before/after).
     (Manager note 2026-10-01 00:32 EDT, rules AMENDMENT 3: the country-out B1 outputs are clipped at 0 kWh, total
     recomputed, as S and C; the winner is S3, `train/winner/winner.json`, pinned copy `train/winner/pinned/best.pt`.)
     (Manager note 2026-09-30 21:21 EDT, rules AMENDMENT 2: the static mean, sd, zmin and zmax come from the TRAINING
     country's development rows only; filter rows BEFORE `Data` computes `stats`, and print the `STATIC_CLIP` lines.)
   * Same flags for `s5_b1.py` where they apply (`--country`, `--no-climate`; B1 uses its chosen configuration per target from
     part B, no re-tuning).
   * Config diff check (val 3.2): print the JSON diff between the winner's config and C's config; PASS only if the one difference is
     `blind: true` (seeds aside).
B. GPU training array (`%7`): winner config with seed 2, seed 3 (S); `--blind` with seeds 1, 2, 3 (C); `--country es --no-climate`
   and `--country it --no-climate` (seed 1, S one-country) = 7 trainings into `train/ckpt/S_seed2`, `S_seed3`, `C_seed1..3`,
   `S_loco_es`, `S_loco_it`.
C. CPU: `s5_b1.py --country es --no-climate` then `--country it --no-climate` (chained, one at a time) into `train/ckpt/B1_loco_es`,
   `B1_loco_it`. No predictions of the other country here (Step 6 scores them on its test lists).
D. Predict validation (afterok B, GPU array `%5`) for S_seed2, S_seed3, C_seed1..3 into `train/pred/<name>`; score each with the
   FROZEN scorer (6 CPUs, at most 4 at once): `--b1 train/pred/B1 --control train/pred/B0 --tag <name>`. Then ONE more scorer run
   of the pinned winner with the control line filled: `--pred train/pred/S<winner> --b1 train/pred/B1 --control train/pred/C_seed1
   --tag S<winner>_vsC`.
E. `tools/speed/s5_seeds.py` (CPU, afterok D): G5J.3 PASS count and median heating/cooling R² for S seeds 1-3 and C seeds 1-3;
   G5J.4 = C seed 1 FAILS G5J.3 (print the cells; "C passes" is a result to report, never tuned away); the spread (min, max) of
   the median R² over the 3 seeds (INFO, val 2.4). Write `train/winner/seeds.json`.
F. Write the chain JobIDs into the state file and sections "Control and seeds" and "One-country trainings" into
   `Step5_docs/outputs_step5/models.md` ("running, manager reads" until done). End.

## Report back (short, plain)
JobIDs; the config diff line; status; Next = "manager verifies control; Step 5 closes".

## What the manager will re-derive
With own code: 3 donor rows of the shuffle from the md5 rule; C's config diff; one G5J.3 cell of C; the seed spread.

## Manager note before launch (2026-10-01 01:00 EDT)
* Winner verified by the manager: S3 (TCN 64 large λ1), `Step5_docs/outputs_step5/winner.md`, pinned copy read-only. Rules now
  include AMENDMENTS 2 and 3 (`step5_rules.md` md5 5e937d09f02f21ee9c0b5444ad4bfd80 = `train/step5_rules_amend3.md5`).
* GPU arrays: the account runs at most 4 A100 slices at once (AssocGrpGRES), so use `%4` (not `%7` / `%5`); CPUs 4 x 3 = 12 +
  B1 one-country 6 + scorers: keep the total <= 30 (scorers at most 2 at once while GPU jobs run).
* Part D scoring: use `--b1 train/pred/B1_clip0` (B1 clipped at 0, AMENDMENT 3; written by the manager, job 1404988) for every
  call, incl. `S3_vsC`; the winner's own unclipped-B1 score stays in `train/score/score_S3.txt`, never overwritten.
  `train/pred/S3` is the winner's validation prediction (kept by the cleanup job 1405037; never re-predict it).
* `s5_b1.py --country`: clip outputs at 0 kWh before writing and recompute total (AMENDMENT 3); print the count clipped.
