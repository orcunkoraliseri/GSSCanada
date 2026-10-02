# 5J Step 9g: Model A extractor + training-data store builder (task doc for a fresh employee)

Written 2026-10-01 16:42 EDT by the 5J manager (author: "go on, prepare the training data builder"). Parent:
`Step9_docs/5thJ_09_modelA.md`, blocks "9D FINAL DRAFT", "9E detail" (E2, E3, E4, E5, E6, E10, E11) and the progress-log entries of
16:10 and 16:13 (FINDING 5J-5: the current windowed base has walls facing inward; OpenUBEM will rebuild it). Read those first.
State file you keep: `Step9_docs/impl/2026-10-01_wp9g_store.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
Training must start the day the Model A simulations finish (GPU access ends about late October 2026). This task writes the code
that turns Model A runs into the training store, exactly as the pilot's Step 5 store did, and tests it on the writer's test runs.
Nothing is final: the store is rebuilt on the real campaign after the fixed base arrives.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Only `ES-MAD-BERRUGUETE` and `IT-BOL-GALVANI2`. No pilot generated-day pool, pilot schedule or pilot household folder.
* **No folder-wide or repo-wide search, no recursive listing, and no wildcard of any kind** (FINDING 5J-2, 5J-4). Open files by full
  name; list only your own folders and `/speed-scratch/o_iseri/5J/step9c/` (one level).
* **No EnergyPlus output may become an input column.** Outputs are targets only (Step 5 `check_features` and its forbidden list).
* **Compute:** Speed via `sbatch` only (`-t 7-00:00:00`, `--exclude=antenna1`, at most 4 CPUs; the cap is shared and busy). Never
  python on the login node. Never wait for a job: submit with a dependency, write the id, end the turn.
* Write only: `5J_docs_occ/tools/speed/a9_common.py`, `a9_extract.py`, `a9_store.py`, their sbatch files, your state file, and
  `/speed-scratch/o_iseri/5J/modelA/store_test/`.

## Code to reuse (import, never copy-edit; name each function with file:line in the state file)
* Pilot store: `tools/speed/s5_common.py` (`open_run`-style guard, `read_truth`, `FEATURE_FORBIDDEN`, `check_features`, input names),
  `tools/speed/s5_store.py` (layout of the store, `norm.json`, the 168 + 24 h windows, neighbour channels, weather channels), state
  `Step5_docs/impl/2026-09-30_wp3_store.md` (its Decisions 4-8 are the pilot conventions; keep them unless 9E says otherwise).
* Pilot extractor: `tools/speed/mzp_extract.py` (hourly per-zone output names and units).
* Model A inputs: zone map `Step9_docs/impl/2026-10-01_wp9c_zone_map_win.csv`, static tables `Step9_docs/impl/static/flats_<D>.csv`
  and `buildings_<D>.csv` (orientation bins will change after the fix; the store must read them as given, never hard-code them),
  placement CSVs in the writer's format (`dwelling_zone, hid, presence_csv, appliance_csv, n_members, appliance_peak_w`).

## What to write
1. **`a9_extract.py`:** for one Model A run folder, per flat zone (`<stem>_F<k>_dwelling_<n>`), 8,760 hourly heating, cooling and
   equipment electricity in kWh, total electricity = equipment + (heating + cooling) / 3.0 (E6), plus the pilot's extra outputs
   where present. Checks: every zone of the zone map found; 8,760 rows; annual equals the sum of hourly; run status read from
   `eplusout.end` (Completed Successfully, 0 Severe).
2. **`a9_store.py`:** builds the store from a manifest (run id, split, district, stem, mode, run folder, placement csv, EPW) through
   a guard that refuses any run whose id is not in the allowed lists it is given (and logs every open, as Step 5). Inputs per flat-
   hour as E3-E5: household drivers from the placement series (people at home = presence x members, appliance W = fraction x
   peak), neighbour channels = flats on the same storey, the storey above and the storey below by `floor_k` (same storey excludes
   the flat itself), weather 7 EPW columns + calendar of the district year (Madrid 2010, Bologna 2014), static vector joined from
   the two static tables (class and age band one-hot, numeric columns z-scored on development and clipped to the development
   range, E5); targets from item 1. Average-household (B0) and default runs are kept apart, as Step 5 kept b0 runs.
3. **Test (one sbatch job, afterany on the writer aggregator 1407093):** on the writer test runs in `/speed-scratch/o_iseri/5J/step9c/`
   (read its `manifest.csv` and the writer state `Step9_docs/impl/2026-10-01_wp9c_idf_writer.md` for folder names): extract every
   D and O run; build a test store from the O runs with a made-up allowed list (all O runs = development, no validation). Report:
   * extraction checks per run; G-c3-style check: hourly equipment of one O flat equals design level x the placement series within
     0.5 % (your code, not the writer's);
   * manager-style re-derivation: one O flat's heating and one hour of its inputs re-read straight from `eplusout` / the series files
     and compared with the store row (equal within 1e-6);
   * neighbour channels of one flat recomputed by hand from the zone map (equal);
   * `check_features` passes on the real input list and FAILS when one target name (for example `heating_kwh_lag24`) is added (seen
     failing);
   * the guard refuses a run id not in the allowed list and logs nothing for it (seen failing);
   * no NaN; store size per flat-year in MB (feeds D9-4).
   If the writer runs failed or are missing, report what is missing, keep your code, and say NOT_EVALUABLE; do not invent data.

## Done means
Code written; test job submitted with its dependency and id written; the state file names every reused function with file:line,
the input column list with its source for each column, and a `Next` naming the log and the table a cold agent fills. Nothing UK
opened or passed. End your turn with "job N submitted, state written to <path>".
