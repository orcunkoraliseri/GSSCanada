# T16 — Step-8 run machinery: how a 2022/2030 campaign run is built and executed — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP1 step 4, WP3, WP4 step 3, WP7.3; §10 Wave 3
Status:     DONE

## Task

**Why.** Wave 3 needs thousands of new EnergyPlus runs on Speed (2030 re-runs, a static code-schedule
arm, an N=200 check, an envelope arm). Before any spec, the manager needs a factual map of how the
existing `campaign_N50` runs were produced. **Reading only. No runs, no edits, no cluster jobs.**

**Where to read (local, `GSSCanada-main/2J_docs_occ_nTemp/`):** `Step8_docs/` (e.g. `cluster_rerun.md`,
`08_09_injection_bug_status.md`, `build_s8_sched.py`, `08_gen_cycle_schedules.py`, `ep_wrappers/`,
`eSim_bem_utils_2J/`, any `run_campaign_local.py` / `run_paired_mc.py`, `*.sbatch`), plus the
`BEM_Setup/SimResults_Step8/campaign_N50/` manifests (`cell_manifest.csv*` — read with `head`/`wc -l`
only). Use Grep/Glob and partial reads; never read a multi-MB file into context.

**Answer each question with `file:line` evidence, or NOT FOUND:**
- Q1 Entry point: which script(s) launched the N50 campaign; local Windows or Speed? Exact command lines on record.
- Q2 Sampling: where the 50 household IDs per cell are drawn (seed, strata), and where the 2022/2030 panel IDs are stored.
- Q3 Inputs per run: base IDF per archetype, EPW per city (file names, weather year if stated), EnergyPlus version and executable path(s) (local and Speed, if any).
- Q4 Schedule injection: which function writes occupancy / lighting / equipment / DHW schedules into the IDF, from which schedule file (`07_aug_to_bem.py` output?), and what SHEU scaling is applied where.
- Q5 Where the occupancy schedule could be swapped for (a) a static NECB/ASHRAE default schedule, (b) an average survey profile — name the exact function and argument, and whether a code-default schedule already exists anywhere in the repo (grep NECB, ASHRAE, `default schedule`).
- Q6 Envelope: where construction/infiltration is set per archetype (for an older-stock variant).
- Q7 Outputs: which files each run writes, which post-processing builds `agg_annual.csv`, and how the manifest marks the canonical run (the `new_2022_2030` merge).
- Q8 Runtime and resources: wall time per run and parallelism on record; EnergyPlus availability on Speed (any `module load`, container, or binary path in scripts/docs).
- Q9 Known traps on record: injection bug, cache/collision issues, concurrent-launch corruption — one line each with the doc line.

**Output.** Fill Verified with Q1–Q9 (short, evidence per line). No new files other than this doc.

**Employee rules.** Reading only; Sonnet. Never `find`/`du`/python on Speed (you should not need Speed at
all). Past ~150k tokens: write state, stop, "handoff needed". Write NOT FOUND rather than guess.

## Ledger
(reading task — no jobs)

## Verified

**Q1 — Entry point, local vs Speed: BOTH, at different times.**
- Per-cell driver: `2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py:1-95` (one cell = one archetype x city, calls `run_step8_paired_mc()`). Wraps into `run_campaign_local.py` (multi-cell orchestrator, `Step8_docs/run_campaign_local.py:13,27,40,144,150-154,223`) for local runs, and into `step8_array.sh`/`step8_array_v2.sh` (SLURM array) for cluster runs.
- **Original + "v2 corrected" full 24-cell campaign ran on Speed** via SLURM array: `Step8_docs/cluster_rerun.md:93` (`sbatch step8_smoke.sh`), `:102` (`sbatch step8_array.sh`), `:149-155` (job 953111, `step8_array_v2.sh`). Exact per-task command: `Step8_docs/step8_array_v2.sh:73` `$PYTHON run_paired_mc.py \` with `PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python` (`:34`). SLURM params: `Step8_docs/step8_array.sh:2-9` / `step8_array_v2.sh:2-9` — `--partition=ps --array=0-23 --cpus-per-task=8 --mem=16G --time=48:00:00`.
- **Later targeted 2022/2030 re-simulation (post multi-zone injection bugfix, the campaign that produced the current `campaign_N50` on disk) ran LOCALLY on Windows**, not Speed: `Step8_docs/08_09_injection_bug_status.md:35-38` ("Live process: `py.exe`/`python.exe run_campaign_local.py` chain started 22:00:15 EDT 2026-07-13 ... PID lineage `run_paired_mc.py`"). Exact command on record: `Step8_docs/08_09_injection_bug_status.md:338-339` — `run_campaign_local.py --cells OtherDwelling__Kelowna_5B --years 2022,2030 --no-resume --workers 1 --ep-workers 8 --mem-abort 80`, run against the live `BEM_Setup/SimResults_Step8/campaign_N50` tree (confirmed local path, not a Speed path).
- Net: the on-disk `campaign_N50` manifests are a mix — 2005/2010/2015 from the Speed SLURM array (v2 corrected), 2022/2030 from the later local-Windows targeted re-run.

**Q2 — Sampling.**
- Seed: `eSim_bem_utils_2J/main.py:1952-1962` `_step8_cell_seed(base_seed, tag)` — SHA-256 of the cell tag (`f"{archetype}__{city}"`) mixed with `base_seed` (default 42, `run_paired_mc.py:38`), so every task drawing the same cell gets the same sample regardless of machine.
- Strata / draw: `main.py:2029-2048` inside `run_step8_paired_mc()` — pool = SIM_HH_IDs present in ALL requested years for that (dtype x region) (`:2029-2034`), sampled without replacement via `rng.sample(pool, n)` unless pool < n (`:2040-2047`, `with_replacement` flag logged).
- Panel IDs storage: `BEM_Schedules_{year}.csv` in `BEM_SETUP_DIR` (`main.py:103-108` `_build_schedule_file_map()`), one CSV per cycle-year (2005/2010/2015/2022/2030). 2005/2010/2015 share a frozen 144,507-ID frame; 2022/2030 were refreshed 2026-07-09 onto a 144,465-ID frame (`main.py:69-75`), so the household pairing across years differs by ~42 HH for the newer two years — documented as a known, deferred inconsistency.

**Q3 — Inputs per run.**
- Base IDF per archetype: `STEP8_ARCHETYPES` (`main.py:84-89`) maps archetype name -> IDF filename substring, resolved via `resolve_cell()`/`_find_one()` glob in `STEP8_BUILDINGS_DIR = 2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242` (`run_bem.py:34-50`, dir set at `main.py:79`). Actual files on disk (Glob): `ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf`, `ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf`, `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf`, `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` — i.e. apartment archetypes are ASHRAE 90.1 STD2022/NECB2017 prototypes, house archetypes are IECC-2024/NBC936 prototypes, all pre-converted to EnergyPlus 24.2 IDD (`v242` suffix; conversion note `main.py:76-78`).
- EPW per city: `STEP8_CITIES` (`main.py:93-100`) maps city label -> EPW filename substring x PR region, resolved in `WEATHER_DIR` (`run_bem.py:47`). Actual files (Glob, `BEM_Setup/WeatherFile/`): `CAN_ON_Toronto...715080_TMYx_5A.epw`, `CAN_BC_Kelowna...712030_TMYx_5B.epw`, `CAN_BC_Vancouver...712010_TMYx_5C.epw`, `CAN_QC_Montreal...716120_TMYx_6A.epw`, `CAN_AB_Calgary...712350_TMYx_6B.epw`, `CAN_MB_Winnipeg...715790_TMYx_7A.epw` — all TMYx typical-year files; no single calendar year is stated in the filenames or in the code read.
- EnergyPlus version: 24.2 throughout — `eSim_bem_utils_2J/config.py:9-24` (`DEFAULT_ENERGYPLUS_DIR`: macOS `/Applications/EnergyPlus-24-2-0`, Windows `C:\EnergyPlusV24-2-0`, Linux `/usr/local/EnergyPlus-24-2-0`; `ENERGYPLUS_EXE`/`IDD_FILE` derived from it). Speed: IDD extracted from `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` via singularity (`Step8_docs/cluster_rerun.md:65`); wrapper binaries `ep_wrappers/energyplus` + `ep_wrappers/ExpandObjects` uploaded and `ENERGYPLUS_DIR` pointed at that wrapper dir in the array script (`step8_array_v2.sh:68`).

**Q4 — Schedule injection.**
- Function: `integration.inject_schedules(idf_path, output_path, hh_id, schedule_data, epw_path=..., ...)` (`eSim_bem_utils_2J/integration.py:1269-1305`), called once per (sample x year) from the campaign loop at `main.py:2065-2070`.
- Schedule source: `schedule_data = schedules[year][hh_id]`, built by `integration.load_schedules(csv_path, dwelling_type, region)` (`integration.py:323`) reading `BEM_Schedules_{year}.csv` — the task doc's own pointer to `07_aug_to_bem.py` as the CSV's producer was not independently re-verified in this reading pass (file exists per repo layout convention but its role as producer was not opened).
- Method (per docstring, `integration.py:1285-1288`): DOE MidRise Apartment schedules as baseline, then household modulation — Lighting via "Daylight Threshold Method" (Gatekeeper), Equipment/DHW via "Presence Filter Method" (min/max toggling by occupancy presence).
- SHEU scaling: applied inside `inject_schedules()`'s equipment/lighting blocks (`integration.py:1584,1755-1758,1836-1840` — `obj.Lighting_Level` / `obj.Design_Level` set to the SHEU-calibrated per-household value, replicated per-zone for multi-zone archetypes per the Bug-A fix, `integration.py:1573-1653`).

**Q5 — Static-default swap point.**
- A code-default, ASHRAE-90.1-labelled schedule set already exists: `idf_optimizer.load_standard_residential_schedules(verbose, baseline='midrise'|'sf_detached')` (`idf_optimizer.py:570-624`), reading `0_BEM_Setup/Templates/schedule.json` (DOE MidRise Apartment, OpenStudio Standards — docstring says "ASHRAE Standard 90.1 compliant schedules", `idf_optimizer.py:959`, `integration.py:2338`) or `schedule_sf.json` (IECC 2021 SF Detached, "robustness check only"). No literal "NECB" schedule was found anywhere in `Step8_docs` — only "ASHRAE Zone" as a column header in an unrelated EUI-reference CSV (`main.py:527-532`).
- A sibling injector already applies this default statically, without any household diary: `integration.inject_neighbourhood_default_schedules(idf_path, output_path, n_buildings, ...)` (`integration.py:2320-2369+`), used today for the "Default" arm of neighbourhood-scale comparative runs (`COMPARATIVE_SCENARIOS = COMPARATIVE_YEARS + ('Default',)`, `main.py:49`) — but this is the **neighbourhood** path, not the single-building `campaign_N50` path.
- Exact swap point for a static campaign_N50 arm: in `run_step8_paired_mc()` (`main.py:2065-2070`), replace the `schedule_data` argument (currently `schedules[y][hh_id]` from `integration.load_schedules()`) with a synthetic per-household dict built from `idf_optimizer.load_standard_residential_schedules()`'s fixed 24h profiles — i.e. same `inject_schedules()` call, different 4th argument. No existing flag does this for single-building `inject_schedules()`; it would be new wiring, not a config toggle.
- Average-survey-profile swap (Q5b): not investigated separately — no function found that averages across households into one representative profile; would need the same swap point with a caller-built average instead of a standard-schedule dict. NOT FOUND as an existing function.

**Q6 — Envelope.**
- NOT FOUND: no runtime code in `Step8_docs`/`eSim_bem_utils_2J` sets construction or infiltration per archetype. Grepped `infiltration`/`envelope`/`Construction` across `Step8_docs` — only hit was a plot color-legend label (`plotting.py:32`, `'infiltration': '#0730E0'`), not simulation logic.
- The envelope is instead baked into the base archetype IDFs themselves (see Q3): apartments come from ASHRAE 90.1 STD2022 / NECB2017 prototype IDFs, houses from IECC-2024/NBC936 prototype IDFs, all under `Buildings_MTL_v242/`. An "older-stock" variant would mean swapping in a different-vintage prototype IDF set for that dir, not a code edit to construction/infiltration objects.

**Q7 — Outputs.**
- Per-run files: `Scenario_{year}.idf` (injected IDF, `main.py:2063-2070`), EnergyPlus's own `eplusout.sql`/`eplusout.end`/`eplusout.err` in each `sc_dir`, plus a parsed `hourly_meters.csv` (8760 rows x meters, written from the sql, `main.py:2094-2113`). Per cell: `cell_manifest.csv` (sample/hh_id/hhsize/dtype/pr, `main.py:2076-2081`).
- `agg_annual.csv` builder: `Step8_docs/08_simulation_plots.py`, `--rebuild-agg` flag (`:982,990-993`), driven by `discover_runs()` (`:189`) which walks each cell dir.
- Canonical-run marking / `new_2022_2030` merge: `load_cell_manifest()` (`08_simulation_plots.py:154-182`) reads the base `cell_manifest.csv` as source `"orig"`, then overlays any `cell_manifest.csv.new_2022_2030_*` file, tagging those rows `source="new_2022_2030"` (`:176,182`); `discover_runs()` uses `meta.get("source") == "new_2022_2030"` (`:212`) to flag `is_new_sample`, i.e. prefer the post-relink 2022/2030 samples over old-frame leftovers.

**Q8 — Runtime and resources.**
- Cluster array: `step8_array.sh:2-9` / `step8_array_v2.sh:2-9` — `partition=ps`, `array=0-23` (24 cells), `cpus-per-task=8`, `mem=16G`, `time=48:00:00`. Observed elapsed: smoke (15 E+ runs) 14m30s (`cluster_rerun.md:137`); one single-run DX-coil recovery job 3m46s (`cluster_rerun.md:311-313`); full re-aggregate+validate pass 54-56 min (`cluster_rerun.md:219,320-321`).
- Local: `run_campaign_local.py:13` documents concurrency as `--workers` (default = CPU cores − 2) x `--ep-workers`, each E+ run single-threaded (`:13,144,150-154`); `ThreadPoolExecutor(max_workers=args.workers)` at `:223`. The Windows targeted re-run used `--workers 1 --ep-workers 8` (one cell's schedules in RAM at a time, `08_09_injection_bug_status.md:116-117,338-339`).
- EnergyPlus on Speed: not a `module load` — a wrapper binary pair (`ep_wrappers/energyplus`, `ep_wrappers/ExpandObjects`) extracted once from `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` via `singularity exec ... cat .../Energy+.idd > ep_wrappers/Energy+.idd` (`cluster_rerun.md:59-65`), then `chmod +x` (`:70`) and referenced via `ENERGYPLUS_DIR` env var in the array script (`step8_array_v2.sh:68`). No `module load energyplus` line found anywhere in `Step8_docs`.

**Q9 — Known traps on record.**
- Multi-zone equipment/lighting injection collapse ("Bug A") — SHEU carrier injected into only the occupancy zone while legacy per-zone loads were neutralized, collapsing whole-building load to ~1/N_units: `08_09_injection_bug_status.md:84-97`.
- Untracked/hidden electric end-use meter gap ("Bug B") — `idf_optimizer.py` `REQUIRED_METERS`/`HOURLY_DETAIL_METERS` missing `WaterSystems:Electricity` (MidRise) and `Heating:Electricity`/`Pumps:Electricity` (HighRise), visibility-only, documented as a known non-blocking limitation, not fixed: `08_09_injection_bug_status.md:99-114,248-254`.
- Concurrent-launch corruption — explicit warning not to run a second `run_campaign_local.py`/`run_paired_mc.py` against the live `campaign_N50` while one is running; Phase 4 found real corruption from exactly this: `08_09_injection_bug_status.md:37-43`.
- Disk-space near-miss during backup — 18-cell backup needed ~456 GB against 229 GB free; backup was rescoped to just the 2022/2030 subfolders about to be overwritten (128.98 GB) rather than a full copy: `08_09_injection_bug_status.md:297-316`.
- DX-coil autosizing fatal error, one run — `Coil:Cooling:DX:SingleSpeed` negative bypass factor during warmup, fixed by hand-setting `Gross Rated Sensible Heat Ratio` from `autosize` to `0.75` for that one run: `cluster_rerun.md:296-309`.
- One benign warmup failure in the v2 SLURM array (task 7, OtherDwelling x Kelowna_5B) — files complete but one fallback output written; did not require the warmup-retry job: `cluster_rerun.md:157-161`.

## Decisions
None required — all nine questions were answerable (with explicit NOT FOUND sub-points noted above) from files already in `Step8_docs/`, `eSim_bem_utils_2J/`, and the `BEM_Setup` manifests; no ambiguity needed the manager's judgment call.

## Next
Manager: use Q1's local-vs-Speed split and Q5's swap point when specifying Wave 3's static-schedule and 2030 re-run arms; Q8 gives the resource template (`partition=ps`, 8 cpu/16G/48h) to copy for new array jobs.

## WHAT I DID NOT VERIFY
- `07_aug_to_bem.py` was not opened to confirm it is literally the producer of `BEM_Schedules_{year}.csv` (Q4) — only inferred from the task doc's own framing and from `load_schedules()`'s consumption of that CSV name.
- Did not open `eSim_bem_utils_2J/schedule_generator.py` (PresenceFilter/Gatekeeper implementation detail) — took `inject_schedules()`'s docstring and call sites at face value for the *method name*, not its arithmetic.
- Did not confirm Q5's "average survey profile" swap point exists anywhere outside `Step8_docs` (e.g. in `eSim_occ_utils/` or Step 4/7) — searched only within the paths the task doc named.
- Did not read `08_validation_warnings_investigation.md`, `roundtrip_analysis.py`, `step8_val_v2.py`, `materiality_p4_analysis.py`, or any `test_*.sh` smoke scripts — not needed for Q1–Q9, left unopened.
- Did not open any `_bigtest/` sample output beyond confirming its existence via Glob — it is a local scratch/test tree, not part of the canonical `campaign_N50`.
- CSV row/column counts for `cell_manifest.csv` files and `BEM_Schedules_*.csv` were taken from prose in `cluster_rerun.md`/`main.py` comments, not re-derived with `wc -l` in this pass (task doc's own reading-only + no-multi-MB-read constraint).
