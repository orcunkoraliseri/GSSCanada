# TASK (employee, Sonnet): 5J Step 5 part A: guarded reader, feature store, B0 predictions and B0 score

Written 2026-09-30 20:08 EDT (from `date`) by the 5J manager. Read first, in full: `Step5_docs/outputs_step5/step5_rules.md`
(THE RULES; do not change them), `Step5_docs/5thJ_05_surrogateTraining.md`, `Step5_docs/5thJ_05_surrogateTraining_val.md`,
`tools/speed/5thJ_04_scorer.py` lines 1-60 and its `read_run`/`load_runs` functions, `tools/speed/frz_standins.py` (the
`write_pred` layout you must copy), `tools/speed/split_loader.py`, `tools/5thJ_idf_mz.py` (builder: flat order, floor index,
floor areas). State file: create `Step5_docs/impl/2026-09-30_wp3_store.md` (sections Ledger / Verified / Decisions / Next /
WHAT I DID NOT VERIFY); `date` before every stamp.

## Hard rules
* 🔴 ALL compute on Speed via sbatch (`-p ps -t 7-00:00:00 --exclude=antenna1`, python `/speed-scratch/o_iseri/envs/step4/bin/python -u`;
  at most 30 CPUs for all your jobs together). Locally ONLY edit/write files, ssh/scp, ls, read small files. Login node (tcsh: wrap
  as `ssh o_iseri@speed.encs.concordia.ca "bash -c '...'"`): sbatch/squeue/sacct/scancel/scp/ls and single-file
  cat/tail/grep/wc -l only (no `du`, no loops, no python, no `find`).
* 🔴 NO TEST DATA (rules R1): only `development`, `validation`, `b0_dev`, `b0_val` through `load_split`; never `test_*`, `b0_test`,
  `unused`, `loco_es`, `loco_it` (the loco lists contain test runs).
* 🔴 UK licence: Spain and Italy only; never open a UK file; no folder-wide search, no wildcard that could match a UK file; name
  every file in full. Household folders: only `/speed-scratch/o_iseri/5J/households/inputs/es_*` and `it_*` that a Spain/Italy
  run's placement names, plus `es_avg`, `it_avg`.
* Additive only: never overwrite anything under `/speed-scratch/o_iseri/5J/campaign/`, `freeze/`, `splits/`, `households/`.
  Write only under `/speed-scratch/o_iseri/5J/train/`.
* You never wait: submit, write the JobID in the state file, end. At most 6 sacct checks of 30 s per job, then "manager to read".
* Past ~150k tokens: stop, write state, "handoff needed".

## Facts the manager checked (2026-09-30)
* Env has torch 2.5.1+cu121, sklearn 1.7.2, pyarrow, numpy 2.2.6, pandas 2.3.3; NO lightgbm/xgboost.
* Household folder `inputs/<cc>_<hid>/` = `presence_HH_<cc>_<hid>.csv` (line 1 = a name, then 8,760 values), `elec_HH_<cc>_<hid>.csv`
  (same, appliance fraction), `household.json` (read it for member count and appliance design level; name the keys you use).
* Run table: `/speed-scratch/o_iseri/5J/campaign/in/campaign_runs_<cc>.csv` (columns run_id, country, climate_id, building_id,
  class, k, n_floors, n_dwellings, pool, building_split, replicate, seed, placement = `flat:hid;...`, flat 0..n-1 in builder order,
  floor = flat // k). Buildings `campaign/in/buildings_es_it.csv`, archetypes `campaign/in/archetype_parameters_<cc>.csv`, climates
  `campaign/in/climates_es_it.csv`, weather folder `campaign/epw/`. Truth = `campaign/extracted/<climate_id>/<run_id>.csv.gz`
  (comment line(s) `#`, columns dwelling, hour 1..8760, heating_kwh, cooling_kwh, equipment_kwh, total_elec_kwh).
* Validation: 1,980 runs, 7,617 flat series (scorer). Development 4,335 runs. b0_val 30, b0_dev 180.

## Parts
A. `tools/speed/s5_common.py`: `allowed_ids()` = development ∪ validation ∪ b0_dev ∪ b0_val via `load_split`;
   `open_run(run_id, kind, log)` refuses (raises) any other id and appends `kind\trun_id\tpath` to
   `/speed-scratch/o_iseri/5J/train/openlog_<tag>.tsv`; `FEATURE_FORBIDDEN` = the EnergyPlus output names (the 4 target names and
   any name containing heating/cooling/equipment_kwh/total_elec/temperature/zone/load) and `check_features(names)` that FAILS when a
   name matches (val 1.2). Seen failing (in a job): (1) `open_run` on one id of `test_new_households` -> refused, printed;
   (2) `check_features` on the real list -> PASS, on the list plus `heating_kwh_lag24` -> FAIL.
B. `tools/speed/s5_store.py` + `s5_store.sbatch` (8 CPUs, 64G) writes `/speed-scratch/o_iseri/5J/train/store/` (THE CONTRACT; the
   training tasks code against it, so keep names exactly):
   * `hh_<cc>.npz`: `hid` (str, incl. `avg`), `presence`, `appl_frac`, `people`, `appl_w` (n_hh × 8760 float32), `members`,
     `design_w` (n_hh).
   * `weather_<climate_id>.npy` (8760 × 7 float32: dry-bulb, dew point, RH, GHI, DNI, DHI, wind; name the EPW columns used) and
     `calendar_<cc>.npy` (8760 × 5: hour sin, hour cos, day-of-year sin, day-of-year cos, day of week 0-6 of the diary year es 2010 /
     it 2014; check the 4J calendar convention used for the schedules and write it down).
   * `flats_<split>.parquet` for split in development, validation, b0_dev, b0_val: one row per (run, flat), sorted by run_id then
     flat: run_id, country, climate_id, building_id, class, flat, floor, hid, hh_index (row in hh_<cc>), nb_same, nb_above,
     nb_below (';'-joined hh_index of those flats, '' if none), then static columns `s_*` (rules R2 static vector; floor area from
     the builder geometry; class one-hot; climate one-hot `c_*` kept separate so R9 can drop it).
   * `targets_<split>.npy`: float32 (n_rows × 8760 × 3: heating, cooling, equipment), same row order as the parquet.
   * `pairs_development.parquet`, `pairs_validation.parquet`: row_a, row_b (indices into the flats table) for every pair = same
     building, climate and flat index, different runs, different hid (the scorer's definition). Validation count must equal the
     scorer's 33,474.
   * `norm.json`: mean and SD from development for each target and each dynamic channel; `static_cols.json`; `README.md` (one line
     per file).
   Checks printed by the job (each a line `CHECK <name> PASS|FAIL ...`): rows per split (validation must be 7,617); R3 total-electricity
   rule on 3 runs (max abs difference; FAIL stops the job); households in development ∩ validation = 0 (val 1.3, FAIL if > 0);
   building overlap dev/val counted (INFO); `check_features` on the full input list; every hid of a placement found; no NaN;
   open log lines outside the allowed ids = 0.
C. B0 (rules R4): `tools/speed/s5_b0.py` + sbatch: for each of the 1,980 validation runs, write `train/pred/B0/<climate>/<run_id>.csv.gz`
   from the `b0_val` run of the same building and climate (flat by flat; total_elec = equipment + (heating + cooling)/3.0 as in R3, or
   copy the B0 run's own total if equal to file precision; say which). Then a scorer job (6 CPUs, `--afterok` the B0 job):
   `5thJ_04_scorer.py --pred /speed-scratch/o_iseri/5J/train/pred/B0 --split validation --out /speed-scratch/o_iseri/5J/train/score
   --tag B0 --b1 /speed-scratch/o_iseri/5J/freeze/out/standins/weakb1 --control /speed-scratch/o_iseri/5J/train/pred/B0` (scorer
   from the freeze folder, never a copy). Expected: G5J.3 FAIL on every cell (B0's effect is 0); report SUMMARY and the 32 G5J.2 lines.
D. Chain B -> C with `--dependency=afterok`; the seen-failing job of A can run at once. Write all JobIDs, end your turn.

## Report back (short, plain)
JobIDs; store file list with sizes if read; the CHECK lines if the jobs finished; else "manager to read". Status "DONE (jobs
submitted)" or "DONE"; Next = "manager verifies; parts B1 and S start".

## What the manager will re-derive
With its own code: 3 random validation rows of the store against the extracted file and the household csv; the pair count; B0's
G5J.2 for one cell; 0 locked runs in the open log.
