# wp9n store from campaign results - implementation state
Task doc:   Step9_docs/impl/2026-10-01_wp9n_store_campaign_TASK.md
Status:     DONE (desktop test PASS; Speed build waits for the manager)
Started:    2026-10-01 (fresh employee; a previous helper was stopped mid-task)

## Ledger
(no Speed jobs; desktop only; array 1409235 untouched, only read-only scp of named files)

## Files
- tools/speed/a9_store_pre9n.py : backup of a9_store.py taken before any 9n edit (created by me; it did not exist; md5-identical copy of the 18:51 file)
- tools/speed/a9_store.py : the builder (9n additions: `campaign` mode, exact supply-air heating rule)
- Step9_docs/impl/wp9n/smoke_copy/ : local test copy of the 36 smoke runs of Madrid (completed by me). results/ (36 json + 21 npz of the CLEAN ones), runs/<rid>/ (placement.csv, series.tar.gz, summary.json for the 21 CLEAN ones; b0/def runs have no series.tar.gz by design), b0/es (3 files the b0 placements point to), inputs/static (= Step9_docs/impl/static_win3, byte-equal to the ES files on Speed in store_test3/in/static), inputs/zone_map_win3.csv (from campaign/inputs), smoke_ES-MAD-BERRUGUETE.csv, clean_ids.txt.

## STEP 1: inputs the store needs and where the campaign keeps them
| store input | used at (a9_store.py) | source in a campaign result | kept? (a9_campaign_task.py) |
|---|---|---|---|
| status clean (completed, 0 Severe) | extract_run reads eplusout.end (a9_extract.py:71-78, :111-114) | results/<rid>.json `status == CLEAN` and `complete` | yes, json :520, :440 (eplusout.end also kept, KEEP :49) |
| hourly targets heating, cooling, equipment per flat (kWh) | extract_run from eplusout.csv (a9_extract.py:115-176) | results/<rid>.npz keys heating, cooling, equipment, total_elec, zones (float32) | yes :433-435; csv deleted :484-491 but extraction ran first :427-430 |
| zone order of the arrays | zone map rows (a9_store.py:172) | npz `zones`; checked equal to zone map order :431 | yes |
| zone map | c.zone_map (a9_common.py:63) | campaign/inputs/zone_map_win3.csv (md5 1c48d2e5240962a88ca16279dd089d50, a9_campaign_task.py:39-40) | yes (input) |
| static tables | c.static_tables (a9_common.py:73) | flats_<D>.csv, buildings_<D>.csv: Step9_docs/impl/static_win3 (local); on Speed the same ES files sit in store_test3/in/static (byte-equal, checked by scp+cmp); IT copy not compared | NOT in campaign folder: manager must name a Speed folder |
| household placement per flat | a9_store.py:120 (placement_csv) | runs/<rid>/placement.csv (dwelling_zone, hid, presence_csv, appliance_csv, n_members, appliance_peak_w) | yes :385, :392; for def runs none (mode default) |
| household series (presence, appliance fraction) 8,760 values | read_series a9_store.py:137-138 via the csv paths in the placement | runs/<rid>/series.tar.gz (members presence_HH_<cc>_<hid>.csv, elec_HH_<cc>_<hid>.csv, same names as in the placement paths) :474-477; b0 runs: campaign/b0/<cc>/presence_HH_<cc>_avg.csv, elec_HH_<cc>_avg.csv (absolute paths in the placement) | yes. The placement paths point at runs/<rid>/series/ which is DELETED :488-489, so the builder must read the tar |
| EPW weather | read_epw a9_store.py:156 | EPW[d] = step9c/epw/es_madrid_2009_2010_y2010.epw (a9_campaign_task.py:36-37) | yes (input, not a result) |
| split of the run, mode, building | manifest `building_split`, `pool`, `mode` (occupancy/default) | plan row + result json | yes |
| G-c3 / purity flags | store check | result json gc3_fail, purity_violations | yes :461-465, :381-383 |
| src IDF md5 | R1(d) | result json src_idf_md5 vs plan | yes :334 |
Blocker check: everything the store needs is kept (only the static folder on Speed is an input to name, not a runner defect). NO BLOCKER.
Notes: hid is NOT a unique household key across runs (each run draws its own series for the same hid, seed per run), so the 9g rule "one hid = one spec" cannot be reused; a household INSTANCE = (country, hid, md5 presence file, md5 appliance file, members, design W).

## Verified (read from the test logs in Step9_docs/impl/wp9n/)
Test = `py tools/speed/a9_store.py campaign-test Step9_docs/impl/wp9n/smoke_copy 4` (4 worker processes, desktop). Final logs: `campaign_test_run5.log` (parquet) and `campaign_test_run6_csv_fallback.log` (A9_FORCE_CSV=1), both `SUMMARY PASS=120 FAIL=0 NOT_EVALUABLE=0`, exit 0. a9_store.py md5 069ec42a506bcdb31286f3da8c75d4f8 (1,544 lines); a9_store_pre9n.py md5 ff9ab2f32d5beb47c8ae358d2f2b21c2 (the 9k version).

| check (as printed) | result | seen failing (where) |
|---|---|---|
| stored runs = clean non-test smoke runs: 13 stored of 36 (36 = 10 test + 13 not clean + 13 clean) | PASS | run1 log: the build failed to load the npz (key names heating, not heating_kwh) -> stored 0 vs expected 13 printed FAIL; fixed |
| not-clean runs refused by name (13, listed in refused_<tag>.tsv with the status text) | PASS | planted copies of result jsons: src md5 changed, G-c3 flag, NOT_CLEAN, missing result, each refused (`classifier_seen_refusing_planted_...`) |
| every test-pool run and every run of test building 4a1eb42e7c488fc0 refused (10 runs, 6 of the test building) and absent from the open log | PASS | `planted_call_for_a_test_id_refused_and_not_logged`; the old 9g guard OPENS a wrongly allowed test id, the new one refuses it (`old_guard_seen_opening...`); `openlog_check_seen_failing_planted_test_id_in_log` |
| G-c3 in the store (equipment = design x series, 42 flats, max rel dev 1.5e-7) | PASS | planted x1.02 on the equipment rows: worst rel dev 2.0e-2 > 5e-3 |
| one flat's heating re-derived from the kept npz (own read), total_elec identity, run annual heating vs result json 10832.012 = 10832.012 | PASS | planted +1 % on the stored row: False |
| incremental: second build adds 0 (targets and flats files byte-equal); deleting one stored run (ledger line) -> exactly 1 added, rows 50 -> 50, no duplicate; changed result md5 -> that run re-added (added 1, removed 1); final build adds 0 | PASS | the md5 case: the same-md5 skip does not hold when the md5 differs |
| targets rows = flats rows, every split | PASS | planted extra-row file -> False |
| heating column unique by position, exact supply-air label | PASS on the 9k case (the old substring rule found [1, 3]) | planted header list with two exact supply-air columns -> candidates [1, 6] (`py a9_store.py heatrule`) |
| input list = spec (67 inputs), check_features, no NaN, pairs two methods agree | PASS | (9g controls unchanged) |

SIZE line (smoke, 50 flat-years): `store_total_bytes=10867724 MB_per_flat_year_total=0.2174 targets_only=0.1051 hh_files=0.0982` against R9 0.229. At campaign scale the household part may grow (one household instance per run draw, see Decisions).
Static tables: the four files in Speed `store_test3/in/static` are byte-equal (cmp) to local `Step9_docs/impl/static_win3` (ES and IT).
Defect found in the 9g code and fixed: `chk()` stored a numpy bool (np.True_ is not `True`), so `summary()` counted it as pass, fail and not-evaluable at once = nothing (the first full run printed PASS=117 and crashed in the SUMMARY_NOT_PASS line). `chk` now converts to bool.

## Decisions
- Split names from (building_split, pool): development = dev building x dev households; validation = val building x val households; xdev_hval (dev bldg x val hh) and xval_hdev (val bldg x dev hh) kept apart, never merged; b0_<bs>; default_<bs>; test pool or test building = refused. Manager may rename; one function (`store_split`).
- A result is stored only if json `complete` and status CLEAN, src_idf_md5 equals the plan row (R1 d), gc3_fail is not true and purity_violations = 0 (R3); anything else is refused by name with its reason (also MISSING_RESULT). A test run is not even status-read.
- Household rows are per household INSTANCE (country, hid, md5 of the two series, members, design W): the same hid has a different series in every run (per-run seed), so the 9g one-hid-one-spec rule cannot apply. Identical files (the b0 average) share one instance. Expect hh_<cc>.npz to dominate the size (140 KB per instance is the floor per distinct household draw).
- Incremental design: ledger.tsv (run, split, md5 of the result json, flats) + work/ (raw flats, hh arrays); changed or removed runs are purged, new runs appended; z-scoring, pairs, norm.json and the final flats tables are rewritten every build; hh instance numbers are append-only (unused instances stay).
- The heating-by-position check compares the exact supply-air label, which equals the label the 9g builder uses; independence of that check comes from reading by header position.
- b0 placements point at absolute Speed b0 paths: the loader uses the path if it exists, else re-roots `.../b0/...` under the campaign root given on the command line (that is how the desktop copy works).
- Safe to run while the array runs: a result json is written LAST and by rename (a9_campaign_task.py:525-527), so a CLEAN json implies its npz and run folder are final. Not done here (CPU rule); the manager decides.
- The smoke copy contains the test runs' npz because the task asked for all 36 results; the guard refuses them (open log shows 0 test ids).

## Next
Manager, after reading campaign check 1409266, builds the store on Speed (nothing but ssh/scp/sbatch on the login node):
1. Locally: create the folder and copy the code (a9_common imports s5_common; a9_store imports a9_extract): `ssh o_iseri@speed.encs.concordia.ca "mkdir -p /speed-scratch/o_iseri/5J/modelA/store_code"` then `scp tools/speed/a9_store.py tools/speed/a9_common.py tools/speed/a9_extract.py tools/speed/s5_common.py o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/5J/modelA/store_code/` (name the four files in full).
2. On the cluster, one line: `sbatch -p ps --mem=32G -c 8 -t 7-00:00:00 --exclude=antenna1 --wrap "cd /speed-scratch/o_iseri/5J/modelA/store_code && /speed-scratch/o_iseri/envs/step4/bin/python a9_store.py campaign /speed-scratch/o_iseri/5J/modelA/campaign/manifests/plan_ES-MAD-BERRUGUETE.csv /speed-scratch/o_iseri/5J/modelA/campaign /speed-scratch/o_iseri/5J/modelA/campaign/inputs/zone_map_win3.csv /speed-scratch/o_iseri/5J/modelA/store_test3/in/static /speed-scratch/o_iseri/5J/step9c/epw /speed-scratch/o_iseri/5J/modelA/store campaign_madrid 8 > /speed-scratch/o_iseri/5J/modelA/store_build_madrid.out 2>&1"`
3. Read the single file `store_build_madrid.out` with tail first, then grep for CHECK, CAMPAIGN_INCREMENT, SIZE, STORE_DONE (stdout lists at most 40 REFUSED lines; the full list is `store/refused_campaign_madrid.tsv`). Exit code 0 = every check PASS, 1 = a FAIL, 2 = crash. Running the same command later adds only new clean runs (for example the 585 degenerate-building runs after 10-04).
Bologna: same command with its plan once its lists are amended (R1 c); the code already knows the IT static tables and EPW name.
Open for the manager: (a) the split names; (b) the real store size with real households; (c) whether to build on partial results while the array runs.

## WHAT I DID NOT VERIFY
- Not run on Speed (no job submitted, by rule). Local python 3.13, numpy 2.3, pandas 2.3; the Speed env `step4` versions are unread (the code avoids new syntax; `np.lib.format.dtype_to_descr` and `write_array_header_1_0` exist in numpy 1 and 2). The csv fallback (no pyarrow) was tested; whether Speed has pyarrow is unknown.
- Scale: 13 runs / 50 flats only. Memory and time at about 9,000 runs are estimates (32 G requested, not measured).
- Test rows were identified from the plan columns pool and building_split; those columns were taken as correct (not re-derived from the sealed split lists).
- The multi-process pool was exercised with 4 workers on Windows only.
- The Bologna plan columns were not read.
- A second employee worked on the same task at the same time and stopped (`wp9n/employee_B_NOTE.md`, unused `wp9n/employee_B_unused_test_block.py.txt`); I did not read its code.

state written to Step9_docs/impl/2026-10-01_wp9n_store_campaign.md
