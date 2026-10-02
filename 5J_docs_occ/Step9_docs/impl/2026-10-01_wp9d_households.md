# Step 9d Model A households: implementation state
Task doc:   `Step9_docs/impl/2026-10-01_wp9d_households_TASK.md`
Status:     IN PROGRESS (script written, test job submitted 2026-10-01; result not read; nothing sealed)
Script:     `5J_docs_occ/tools/5thJ_modelA_households.py` (local md5 bee14cda3ccc47f17fddbc3087613008, same md5 on Speed)

## Ledger
* 1407122 · wp9d test job (splits, pools, calibration, 6 runs, P1) · SUBMITTED, state not read · exit unknown · log `/speed-scratch/o_iseri/5J/modelA/households/wp9d_1407122.out` · sbatch file `.../households/code/wp9d.sbatch` (2 CPUs, 32 G, -t 7-00:00:00, --exclude=antenna1)
* First `scp` attempt failed ("Connection closed"); `scp -O` worked. No job was affected.

## Files on Speed (all under `/speed-scratch/o_iseri/5J/modelA/households/`)
* `code/` copies of `5thJ_modelA_households.py`, `5thJ_design_tables.py` (md5 b293a4b1a2b0da2f6fab163eedfb196d, same as local), `wp9d.sbatch`
* `inputs/zone_map_win.csv` = `Step9_docs/impl/2026-10-01_wp9c_zone_map_win.csv` (WINDOWED zone map, md5 1c48d2e5240962a88ca16279dd089d50)
* The job writes: `splits/hids_<c>_<dev|val|test>.csv`, `splits/respondents_<c>.csv`, `hazards_<c>.json`,
  `test/series/<run_id>/{presence,elec}_HH_<c>_<hid>.csv`, `test/placement_<run_id>.csv`, `test/draws_<run_id>.csv`, `test/det/`, `test/p1/`

## Reused functions (file:line, local copies)
* `tools/5thJ_design_tables.py`: `read_household_sizes` :145, `read_household_weights` :185, `rng_for` :89 (weighted key `log(1-u)/w` as `draw_households` :198, re-written in `assign_flats`/`split_hids`, not imported, because `draw_households` is fixed to 60 households); `alloc` :160 not used.
* `tools/5thJ_step9_trigger_act2.py` (5J copy of 4J trigger, act2 rule): `check_corpus_guard` :656, `_import_step7` :578, `Mapping` :145, `build_act2_map` :104 (rule `prefix2_major`), `sample_ownership` :828, `count_eligible` :852, `count_eligible_dhw` :928, `calibrate_all` :870, `calibrate_to_published` :1004, `simulate_dwelling` :1074, `rotate_to_midnight` :957, `write_series_csv` :1350. This file is the one the pilot household build ran (`tools/speed/hh_run_fold.sbatch`). Its Speed copy is `repo/5J_docs_occ/tools/5thJ_step9_trigger_act2.py` (md5 not compared with local).
* 4J `tools/4thJ_step7_schedules.py` (loaded by `_import_step7` from `repo/4J_docs_occ/tools`): `year_day_types` :153, `draw` :245 (the back-off), `assemble_person_year` :266 (used only as an equivalence check), `household_year` :321, `write_schedule_csv` :359, `_stratum_key` :180; plus `dec.decode_record`, `dec.decode_prefix`, `indoor.presence_minutes`, `indoor.load_outdoor_at_home`, `load_bit_positions`.
* Not reused: `tools/speed/hh_build.py` and `s7_hh_build.py` (they copy pilot / trigger output files made from the generated pool; forbidden here).

## Design as built (decisions the task doc did not fix)
* Corpus: only `/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl` (md5 checked 1a5163445291b54114832e192b0d9a05, guard `check_corpus_guard`); the script stops if any row has a country other than es / it, and `assert_not_uk` refuses any path or argument naming the UK. Weights: `/speed-scratch/o_iseri/4J/outputs_step1/episodes_spain.parquet` and `episodes_italy.parquet`, columns hid, pid, weight_ind only (the path the Step 7 job `s7_hh_draw.py` used).
* Split: per country, households with weight > 0, strata size 1, 2, 3, 4, 5+ (distinct pid per hid); within a stratum sorted hids shuffled with `rng_for(9101, "split", country, bucket)`; dev = round(0.70 n), val = round(0.15 n), test = rest (Python round). Expected counts by that rule from the inventory sizes (arithmetic only, checked against inventory totals): Spain dev 6,678 / val 1,431 / test 1,432 (by size 2,101/450/451, 3,081/660/660, 969/208/208, 437/94/93, 90/19/20); Italy 12,905 / 2,765 / 2,765 (4,553/976/975, 4,677/1,002/1,002, 2,176/466/466, 1,222/262/262, 277/59/60). The job prints the real lists and md5; read those.
* A respondent (= one corpus row, one pid) and its single diary day follow the household: each day is in exactly one split pool (gate in the job).
* Day draw: as 4J `independent` rule (fresh draw each calendar day), bucket = age band, sex, household type, economic status, day type, back-off `draw`; seed string `A9d|<run seed>|<country>|<hid>|m<member index>`; run seed = first 8 hex of md5(run_id) mod 2147483647. Calendar year Madrid 2010, Bologna 2014 (non-leap).
* Appliances: the trigger's own state machine (`simulate_dwelling`) with act2 rule `prefix2_major`, standby + cycles, ownership per household from its own seeded stream (CREST default-dwelling set, as the pilot). DHW is simulated by that function and discarded. People level = number of members (distinct pid), appliance level = max hourly mean W of the household-year (written with 4 decimals, as the pilot read it from the IDF); fractions = W / peak. Presence = share of members at home, rotated to midnight (04:00 diary origin), 8,760 values.
* **Hazards (calibration) are fixed per country once, from DEV only:** 100 dev households drawn by weight (`rng_for(9103, "calib", c)`), years drawn from the dev pool (seed 9104), hazards calibrated to CREST cycles per year with `calibrate_all` + `calibrate_to_published` (max 6 passes, as the pilot); the act2 map takes its ambiguous-prefix minutes from the dev pool only. Saved as `hazards_<c>.json`. This is my choice (the pilot calibrated on its 60 households); the manager may rule otherwise.
* Flats: `assign_flats` = distinct households of the run's split, key `log(1-u)/w` (largest keys first) with `rng_for(9105, "flats", run_id)`, weight = lowest-pid person (`read_household_weights`), no size matching; optional `exclude` per flat for later runs in the same pool (not exercised by the test: one run per split).
* Zone map used: the WINDOWED one (`2026-10-01_wp9c_zone_map_win.csv`, present). Test buildings: per district the building with 5 to 25 flats whose flat count is closest to 15 (ties: lowest stem); the job prints the stems.
* Placement CSV written per run in the writer's format (`dwelling_zone, hid, presence_csv, appliance_csv, n_members, appliance_peak_w`), absolute Speed paths; `n_members` is an integer, `appliance_peak_w` has 4 decimals. The IDF writer was NOT run on these files (not in this task).
* P1: for the Madrid dev run, the plant is a test respondent whose exact bucket equals a dev-run member's (smallest dev bucket first, up to 5 tries); all three Madrid runs are re-drawn (draws only, no appliance step) with the planted dev pool; the check reads the written draw files; the gate compares the failing runs with an independent count of the planted respondent's id in the draw records. If no try is drawn the job prints `P1 NOT_EVALUABLE` and records `P1_not_evaluable` as a failure so it cannot pass silently.

## Verified
* `py -3 -m py_compile` on the script: OK (local, syntax only). Nothing run yet: no numbers read from the job.

* 2026-10-01 15:58 manager read the script (code only): split, pools, draw records, read-back purity, P1, selfchecks and determinism as the task doc asks. Calibration on dev only RULED by the manager (keep). Job 1407122 PENDING; nothing from the job read yet.

## Next
Cold agent (or manager): after `sacct -j 1407122 -X` shows COMPLETED, `cat /speed-scratch/o_iseri/5J/modelA/households/wp9d_1407122.out` (login node, single file; it is long, use `grep "^GATE\|^SPLIT\|^POOL\|^DEPTH\|^RUN\|^P1\|^TIMING\|^SUMMARY\|^CALIB\|^COUNTRY"`). Fill from it: (1) the split counts (`SPLIT_COUNTS`, `SPLIT_LIST` md5) against the expected counts above; (2) the `POOL` lines (respondents, days by day type, buckets, buckets >= 5 days per split); (3) the `DEPTH` table (back-off per country and split); (4) the gates (purity per run, series length, determinism, `P1_...`); (5) `TIMING` (seconds and bytes per household-year). If it FAILED, read the last 40 lines of the log and fix the script on the Speed copy and the local one, then resubmit `code/wp9d.sbatch`. The manager seals the split md5 only after checking.

## WHAT I DID NOT VERIFY
* Everything the job computes: split counts as run, pools, calibration convergence (worst deviation, saturated appliances), draws, purity, P1, determinism, timing, disk. The job was not waited for.
* That the Speed copy of the trigger file equals the local one (only the local was read), and that `/speed-scratch/o_iseri/4J/outputs_step1/episodes_*.parquet` hold the same weights as the local parquets (same path as the Step 7 job; not compared).
* That Python on the `step4` environment accepts the script (only a local Python 3.13 syntax check).
* The placement files against the IDF writer (not run); the windowed zone map building choice (stems unknown until the job prints them).
* Nothing UK was opened, listed, copied or passed; no pilot generated-day pool, schedule file or pilot household folder was read. I read (code only, local) `tools/speed/hh_build.py`, `s7_hh_draw.py`, `s7_hh_build.py` and the trigger/step 7 sources; `tools/` was not listed beyond the file names shown by one `ls | grep -v -i uk` (UK-named entries filtered out of the display, never opened). `tools/5thJ_design_tables.py` and the trigger file contain UK entries in their own code (country list, climates); they were read as code, none is used or passed.
