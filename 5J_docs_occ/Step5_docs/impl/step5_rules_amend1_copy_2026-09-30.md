# 5J Step 5 rules (written BEFORE any training; val 4.1)

Ruled by the manager 2026-09-30 20:10 EDT (from `date`), under the author's go-ahead of 2026-09-30 evening ("continue to the end
based on your recommendations, no need my confirmation"). Spec: `Step5_docs/5thJ_05_surrogateTraining.md`. Gates are frozen
(`/speed-scratch/o_iseri/5J/gates_frozen.md5`, Step 4). The md5 of this file is written by a Speed job into
`/speed-scratch/o_iseri/5J/train/step5_rules.md5` before the first training job; any later change is a dated AMENDMENT at the
end, never an edit, and must say whether any training result had been seen.

Spain and Italy only. 🔴 No UK file, no folder-wide search, no wildcard that could match a UK file.

## R1. Which runs (no test data)
* Training: the `development` list. Early stopping, tuning and model choice: the `validation` list. B0: `b0_dev`, `b0_val`.
  Lists are read ONLY through `split_loader.load_split` (copy `/speed-scratch/o_iseri/5J/freeze/split_loader.py`).
* 🔴 Never call `load_split` on `test_*`, `b0_test`, `unused`, `loco_es`, `loco_it` in Step 5. The loco lists hold every run of a
  country INCLUDING test runs, and they load without the lock; the leave-one-country-out training (R9) is built as
  "development (+ validation for early stopping) runs of one country", never from a loco list.
* Every Step 5 reader of campaign files goes through one function that refuses a run id outside
  development ∪ validation ∪ b0_dev ∪ b0_val and appends (kind, run_id, path) to an open log; val 1.1 = 0 lines naming a run of
  the five locked lists or of a loco list outside those four lists.

## R2. Inputs (O-4 RULED)
The surrogate gets what EnergyPlus gets from the household, the building and the weather; nothing EnergyPlus computes.
* **Household drivers per flat and hour** (from `/speed-scratch/o_iseri/5J/households/inputs/<cc>_<hid>/`, the files the
  campaign IDF used): presence fraction (`presence_HH_*.csv`), appliance fraction (`elec_HH_*.csv`), and from
  `household.json` the member count and the appliance design level; derived: people at home = members × presence, appliance
  power = design level × appliance fraction.
* **Neighbour drivers** (multi-zone, flats exchange heat): for the flats on the same floor, the floor above and the floor below
  (flat j is on floor j // k, builder order), the mean of people at home and of appliance power, 0 and a 0/1 flag when there is
  no such flat. SFH/TH: all 0, flags 0.
* **Weather per hour** from the run's EPW (`/speed-scratch/o_iseri/5J/campaign/epw/` or the climates table path on Speed): dry-bulb,
  dew point, relative humidity, global horizontal, direct normal, diffuse horizontal radiation, wind speed.
* **Calendar:** hour of day (sin, cos), day of year (sin, cos), day of week of the diary calendar year (es 2010, it 2014).
* **Static vector:** class (one-hot), every numeric field of the building row (`campaign/in/buildings_es_it.csv`) and of its
  archetype row (`archetype_parameters_<cc>.csv`), north axis as sin/cos, n_floors, k, n_dwellings, the flat's floor index,
  top-floor and ground-floor flags, the flat's conditioned floor area (from the builder geometry, `tools/5thJ_idf_mz.py`, NOT from
  an EnergyPlus output), climate one-hot (dropped in R9). No household id, building id or run id is ever an input.
* **Not used:** activity shares from the diaries (EnergyPlus never sees them; they would need diary rows). Any EnergyPlus output
  (loads, temperatures, past hours) is NEVER an input (val 1.2).
* **Window:** 168 h of drivers before + the 24 h predicted (192 h in), 24 h out, stride 24 h, per flat. The first 7 days take
  their history from the end of the same year (wrap); the error of days 1-7 is reported separately (INFO).

## R3. Targets
Heating, cooling and equipment electricity (kWh per hour per flat), standardised per target on development. Total electricity is
NOT learned: it is computed as equipment + (heating + cooling) / 3.0 (COP 3.0, the campaign's rule); the data task checks on 3
runs that the extracted `total_elec_kwh` equals this to file precision, else stops and reports.

## R4. B0 (average schedule)
For each validation run, B0's prediction = the `b0_val` run of the same building and climate, flat by flat. Its occupancy effect
is zero by construction.

## R5. B1 (boosted trees, CPU)
`sklearn.ensemble.HistGradientBoostingRegressor` (lightgbm/xgboost are not in the env), one model per target, hourly rows:
current drivers, lags 1, 2, 3, 6, 12, 24, 48, 168 h of people at home, appliance power and dry-bulb, rolling 24 h and 168 h means
of people at home and dry-bulb, neighbour drivers, calendar, static vector. Training rows: a fixed random sample of at most 6
million development flat-hours (seed 20260930). Tuning: 20 random configurations (learning rate, max_leaf_nodes, min_samples_leaf,
l2), chosen by validation hourly MSE on a fixed sample of 2 million validation flat-hours. B1 is the skill reference (`--b1`) for
S in G5J.3.

## R6. S (sequence model, GPU) and the fixed budget
Two families on the same windows: (1) temporal convolution network (dilated causal convolutions, receptive field >= 192 h);
(2) Transformer encoder over the 192 hours (static vector as one extra token). Grid fixed now, 8 configurations per family:
width {64, 128} × depth {small, large} × pair-loss weight λ {0, 1}. Loss = MSE on standardised targets over the 24 h (summed
over the 3 targets) + λ × MSE of the paired difference: each batch holds pairs (two development runs, same building, climate and
flat index, different households, same day), and the pair term compares (ŷA − ŷB) with (yA − yB). AdamW, lr 1e-3 with cosine
decay, at most 30 epochs of 400,000 windows, early stopping patience 4 on the validation loss (level + pair term, both reported
for every configuration whatever λ), at most 4 GPU-hours per configuration. One GPU slice per configuration
(`--gres=gpu:nvidia_a100_2g.20gb:1`, 3 CPUs, `-p ps`), at most 8 jobs at once (24 CPUs; with other 5J jobs never above 30).
Seed 1 for all 16.

## R7. Winner (val 4.1)
1. Shortlist: the 3 configurations per family with the lowest validation loss (level + pair) = 6.
2. Each of the 6 writes predictions for all 1,980 validation runs (scorer layout) and is scored by the FROZEN scorer
   (`5thJ_04_scorer.py`, md5 84d1dafa...) with `--b1 <B1 predictions> --control <B0 predictions>` (C does not exist yet; the
   control line is ignored for the choice).
3. Winner = most G5J.3 PASS cells (of 32); tie -> highest median G5J.3 R² over the 16 heating and cooling cells; tie -> most
   G5J.2 PASS cells; tie -> lowest validation loss. Written result: `outputs_step5/winner.md`.
4. Pinned: md5 of the training code, seed, checkpoint md5, config. Reload check: the reloaded checkpoint reproduces the
   validation loss to 4 decimals (val 4.3).
5. If S does not beat B1 (G5J.3 skill interval excluding 0), that is reported, not tuned away (Overview). No threshold changes.
6. Prediction files of non-winning configurations are deleted after scoring (score files kept).

## R8. C (blind control) and seeds
C = the winner's configuration retrained from scratch where, for every (run, flat) of development, the household drivers AND the
neighbour drivers are taken from a random other development run of the same country (per (run, flat) a random (run', flat'),
seed = md5("<run_id>|<flat>|blind|20260930")); building, weather and targets unchanged. Config diff S vs C = the shuffle flag
only (val 3.2). Validation predictions of C use the same shuffle rule on validation runs. G5J.4: C must FAIL G5J.3.
Seeds: winner S and C at seeds 1, 2, 3; the pinned models are seed 1; the spread of validation G5J.3 R² is reported (INFO, val 2.4).

## R9. Leave-one-country-out (for G5J.6, scored in Step 6)
The pinned configuration (no re-tuning) and B1's chosen configuration, trained on one country's development runs (early stopping
on that country's validation runs), climate one-hot dropped; two trainings each (Spain only, Italy only). No field only one
country records (val 1.4).

## R10. Val 1.3 as applied
No household id in both the training and the validation windows (FAIL if any). Buildings ARE shared by design (validation = new
households in development buildings, Step 2 split design; new buildings are scored in Step 6 on `test_new_buildings`): the
building overlap is counted and reported (INFO), not a failure.

## R11. Where things go
Speed `/speed-scratch/o_iseri/5J/train/` (`store/` feature store, `pred/<model>/<climate>/<run_id>.csv.gz`, `ckpt/`, `logs/`,
`openlog_*.tsv`); ledger `Step5_docs/impl/<date>_wp3_*.md`; results `outputs_step5/models.md`, `winner.md`.
Checkpoints are copied to `GSSCanada\_5J_data\surrogate\checkpoints\` only after pinning (Spain + Italy weights only).

## AMENDMENTS (dated; none at writing)

### AMENDMENT 1 (2026-09-30 20:18 EDT, from `date`; manager, under the author's go-ahead)
Seen before writing: the store job's check lines and the B0 group counts (job logs 1404516, 1404519, 1404520). NO training
result, NO model output and NO B0 or B1 score had been seen (the B0 scorer job had not run).
* **R10 (val 1.3) as applied, amended.** The validation list sealed in Step 3 holds three blocks per country: new households in
  development buildings (es 564 / it 543 runs), new households in new buildings (102 / 78), and DEVELOPMENT households in new
  buildings (396 / 297; Step 2 design line 62: every household runs on every SFH/TH building with pool = its own split). So every
  development household also appears in validation by design, and "no household id in both" cannot pass on the frozen list.
  Val 1.3 is now: (a) 0 (country, household, building) combinations in both development and validation; (b) 0 development
  households in the new-household blocks; (c) 0 development buildings in the development-household block. Each validation run
  is then new in its household, its building or both. All three are FAIL if > 0 and are shown failing on a planted run. The
  validation list itself is NOT changed (the frozen scorer reads it); the share of each block is reported with every score.
* **R4 (B0) amended.** B0 = the average-household run of the same building and climate from `b0_val` for new buildings and from
  `b0_dev` for development buildings (`b0_val` holds only the 5 new buildings per country). Both lists are allowed (R1).
