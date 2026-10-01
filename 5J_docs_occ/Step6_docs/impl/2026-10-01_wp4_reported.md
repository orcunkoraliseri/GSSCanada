# Step 6 part B0 (reported analyses) - implementation state
Task doc:   Step6_docs/impl/2026-10-01_wp4_reported_TASK.md
Status:     IN PROGRESS (job submitted 2026-10-01 01:12 EDT, waiting on Step 5 scorer 1405055)

## Ledger
* 1405073 · s6_reported.sbatch (-c 4 --mem=32G -p ps -t 7-00:00:00 --exclude=antenna1) · submitted 01:12 EDT with `--dependency=afterok:1405055` · state: PENDING (not checked after submit) · exit: n/a
  log `/speed-scratch/o_iseri/5J/train/reported/logs/s6_reported_1405073.out`; outputs `train/reported/reported_S3_val.{txt,parquet}`, `reported_S3_val_flats.parquet`, `openlog_S3_val.tsv`.
* Files (local `tools/speed/`, copied to Speed `train/reported/`): `s6_reported.py` md5 32fb7bfbf3647992ef40937073c4a6e5 (as submitted; same md5 on Speed); `s6_reported.sbatch` md5 a70e97dee5dba08f30784d5cf924080d.
* The job does: compile; planted `--test` call on a scratch copy (ROOT = empty folder; must exit 9); main run on validation S3; if main exit 0, refusal exit 9 and no failed CHECK line: copy to `freeze/s6_reported.py` (444) and write `freeze/s6_reported.md5` (444). Otherwise prints NOT_LOCKED (manager decides).

## Verified
Nothing run yet. Read: task, spec 6A/6B/6D, wp4 scoring task, gates_frozen sections 0-3, scorer lines 1-330 (readers, pair rule), winner.md, Speed `split_loader.py`, `train/store/README.md`, `train/score/score_S3.txt` PAIRS lines (es SFH 4755, TH 8160, MFH 3570, AB 1497; it SFH 4755, TH 4620, MFH 5085, AB 1032).

## Decisions (task doc did not fix them)
1. Lag: for lag L the pairs are presence p(t) and heating h(t+L) over hours where EP heating at t+L > 0; the same hour mask (from EP) is used for S and EP. Peak = argmax of Pearson r over L = 0..24. Flat skipped if fewer than 500 such hours. Presence = `people` (members x presence) of the flat's household.
2. Pairs rebuilt from `flats_validation.parquet` (same climate, building, flat index; different run; different `hid`), only for runs where the S prediction file is usable; compared with the scorer's `pairs=` per country x class.
3. Cooling: relative error = (S - EP)/EP of annual cooling over flats with EP cooling > 0.001 kWh/year (signed and absolute medians both printed); pair R2 is on ANNUAL pair effects (a different level from the scorer's hourly R2); pairs are per climate x class.
4. Level vs timing: x1 = difference of annual `people` hours, x2 = difference of annual `appl_w` sum / 1000 (assumes appl_w is in watts; the unit is not stated in the store README, it only affects the coefficient, not R2).
5. Seen-failing is done inside the one job without extra file reads: lag check uses a +6 h roll of EP heating of the first run (computed in the worker from the already-read file), the planted defect is the same lag code on the unshifted series (delta 0, must fire); cooling check planted S = EP (R2 = 1, must fire); pair-count check against a reference changed by one pair (must fire). Planted lines print `CHECK_PLANTED`; real ones `CHECK`.
6. Open log has a fourth column (job id) beyond the scorer's three. Extra output: `reported_<tag>_flats.parquet` (one row per flat, for the manager's re-derivation).
7. `--test` is refused (exit 9) first thing unless `gates_frozen_amend1.md5` exists and the list is one of the three test lists; without `--test` only `validation` is accepted. In test mode the self-checks add no extra file open (so opens = runs of the list).

## Next
Manager (or a fresh employee) reads the log after 1405055 and 1405073 finish: copy every REPORTED and CHECK line and the LOCKED md5 into this file; confirm the three planted lines say "expected". If NOT_LOCKED, find the failing CHECK line and fix by a new dated copy (do not edit a locked file).

## WHAT I DID NOT VERIFY
* Nothing has run: not even that the script compiles (compile happens in the job) or that the store columns are named as assumed (`run_id, country, climate_id, building_id, class, flat, hid, hh_index`, taken from `s5_store.py` lines 224-225; `flat` assumed equal to the dwelling index in the EnergyPlus file as in the scorer).
* That `hid` equality gives the scorer's pair counts (the job's first CHECK tests it).
* That the shifted-lag check finds a flat of the first run with lag <= 18 h and at least 500 heating hours.
* The test path with real test data (written, never run, by design); `test/store/` layout assumed equal to `train/store/`.

## MANAGER (2026-10-01 02:22 EDT): v1 read; lag definition fixed (v2); v1 lock VOID
* Job 1405073 (v1, md5 32fb7bfb...): all real CHECKs PASS, planted checks fired, refusal exit 9, locked as
  `freeze/s6_reported.py` + `.md5` at 02:05. Results read by the manager (validation only).
* Defect: `lag_peak` took the lag of the MOST POSITIVE correlation (nanargmax). Presence adds internal gains at a constant
  setpoint, so it LOWERS heating; the response is the most negative correlation. v1's Italian medians (EP 15-17 h, S 6 h, while
  80-95 % of flats agreed within 1 h) show daily-cycle artefacts. Fixed by the manager in `tools/speed/s6_reported.py` (v2,
  md5 3a0749b1..., one line: nanargmin, docstring); v1 archived in `tools/speed/archive_s6_reported_v1/`.
* v2 job 1405166 (`s6_reported_v2.sbatch`: same steps; the refusal guard no longer requires the amend1 lock to be absent, since
  part A has created it, the scratch ROOT is still empty; locks as `freeze/s6_reported_v2.py` + `.md5`, never touching v1).
  The v1 lock files stay on disk, VOID, and the scoring task now names v2 only. Manager re-derivation job 1405167 (afterok).
* Validation results already seen from v1 that do not depend on the lag (kept): level explains most of the ANNUAL pair effect
  (R² 0.75-0.97 EP, 0.79-0.98 S); mild-climate cooling pair R² 0.84-0.997, worst Turin MFH/AB, annual cooling level error up
  to 106 % (Turin AB).

## MANAGER VERIFIED v2 (2026-10-01 02:24 EDT)
* Job 1405166: refusal exit 9, every real CHECK PASS, planted checks fired, LOCKED `freeze/s6_reported_v2.py` md5
  3a0749b12ee1ad8b208404fb84a57c0c. Lags now 12-16 h (median), S = EP median in 7 of 8 cells, within 1 h for 73-99 % of flats.
* Own code (job 1405167, `mgr/mgr_reported_check.py` md5 49d49e2f...): lag of 3 flats (es SFH, it TH, it MFH) for EP and S =
  the script's (13/13, 14/14, 16/16; peak correlations -0.19 to -0.27); level-vs-timing es SFH heating R² 0.9321 (EP),
  0.9374 (S) over 4,755 pairs = the script's line.
* Interpretation limit (for the paper): the peak correlations are weak (about -0.2) and the 12-16 h lag mostly reflects the daily
  cycle of presence against heating, not a building time constant. The analysis is a like-for-like check that S reproduces
  EnergyPlus's presence-heating timing, and is reported as such (never as a thermal-mass constant).
