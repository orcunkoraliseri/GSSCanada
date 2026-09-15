# T25 — Reading: Step-9 run machinery (the 4,800 activity/baseline runs) — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP1 step 4. Step-8 counterpart: `2026-09-15_T16_step8_run_machinery.md`
(read it first; answer in the same shape). Purpose: the manager must brief T21 (rerun Step 8 and Step 9 for
2022 and 2030 on the rebuilt schedules) on Speed.
Status:     DONE

## Questions (file:line evidence, or NOT FOUND)
- Q1 Entry point for the Step-9 campaign: script(s), local or Speed, exact command lines, array layout.
- Q2 Arms and grid: what "baseline" and "activity" arms are (which injector, which schedule columns), cells
  (archetype × city), years, households per cell; confirm the 4,800 count from a manifest or doc.
- Q3 Sampling: same seed-42 households as Step 8, or its own draw? Where stored.
- Q4 Inputs beyond Step 8: activity-to-end-use tables, SHEU calibration scalars (`f_e`), any file tied to a
  schedule year that must be regenerated if `BEM_Schedules_2022/2030.csv` change.
- Q5 Outputs and post-processing: per-run files, aggregate tables, which script builds the Step-9 numbers the
  paper quotes (SHEU cells, EUI table, end-use by hour).
- Q6 Resources and runtime on record; known traps (one line each, doc line).
- Q7 Can the same staged Speed tree pattern as T17/T22 (`code/repo` + `sched/`) run Step 9, or does it need
  extra assets? List them with sizes from `Glob`/doc prose only.

## Brief (employee, Sonnet)
Local read-only. No edits except this doc. No cluster. No script runs. `Grep` before `Read`; ranges only;
never open multi-MB files. Look in `GSSCanada-main/2J_docs_occ_nTemp/Step9_docs/`, `Step8_docs/`
(`eSim_bem_utils_2J/main.py`, `integration.py`), `BEM_Setup/SimResults_Step9*` manifests (head only).
Write answers under Verified as you go; Status DONE.

## Ledger
(reading task — no jobs)

## Verified

**Q1 — Entry point: BOTH cluster and local, at different times — same pattern as Step 8 (T16 Q1).**
- **Original full 24-cell x n=50 grid ran on Speed** via a 3-stage sbatch pipeline: Stage A (IDF gen) `Step9_docs/step9_cluster/step9_a_generate_full.sh`, Stage B (E+ array) `step9_b_array_full.sh`, Stage C (validate) `step9_c_validate_full.sh` — architecture table `Step9_docs/cluster_run.md:10-22`; exact "Corrected Re-Run" sbatch command sequence (0-11) `cluster_run.md:516-645` (e.g. `:547` `sbatch .../step9_a_generate_full.sh`, `:593` `sbatch .../step9_b_array_full.sh`). Array layout: `Step9_docs/step9_cluster/step9_b_array_full.sh:2-9` (`--partition=ps --array=0-47 --cpus-per-task=4 --mem=16G --time=48:00:00`); task-to-cell mapping `:30-40` (task 0-23 = baseline x 24 cells, task 24-47 = activity x 24 cells; `ARCHS`/`CITIES` arrays list 4 archetypes x 6 cities). Confirmed complete 2026-06-10: `cluster_run.md:792,811-813` "4795/4800 files loaded... All SHEU ±15% gates pass".
- **Later, after the 2026-07-09 schedule relink (same trigger as Step 8's local re-run), Step 9 was re-run LOCALLY on Windows**: driver `Step9_docs/run_step9_local.py` (new, "No local Step-9 driver existed before this", `run_step9_local.py:16-17`), exact command `py run_step9_local.py --n 50 --workers 1 --ep-workers 18 --no-resume`, run from `Step9_docs`, launched 2026-07-11 ~13:08 — `2J_docs_occ_nTemp/outputs_step8/implementation-improvement/step8_2022_2030_resim_implementation.md:465-468`. As of that doc's last entry this local campaign was **IN PROGRESS, not confirmed complete** (`:222-223,479-481`). Post-processing scripts `step9_validate_full.py`/`step9_loadshape_aggregate.py` have archived pre-fix copies dated `20260713_pre_local_paths`/`20260713_pre_utf8fix` (`Step9_docs/step9_cluster/` dir listing), confirming the whole chain was retargeted at the local output tree around 2026-07-13.
- No SLURM array is used for the local path — `run_step9_local.py` runs 48 sequential (cell, treatment) units single-threaded (`--workers 1`) with internal E+ parallelism (`--ep-workers 18`), via a `ThreadPoolExecutor`-based driver identical in spirit to Step 8's local orchestrator.

**Q2 — Arms and grid.**
- Arms: "baseline" = presence-filter-only schedules, no activity injection, drawn from `BEM_Schedules_{year}_baseline.csv` (13-col); "activity" = activity-driven equipment/lighting fractions from `BEM_Schedules_{year}.csv` (17-col) — `Step9_docs/cluster_run.md:24-27`. Both CSVs are derived from the SAME synthetic-population run so HH IDs match (`:25`, D4 `:38`).
- Grid: 24 cells (4 archetypes x 6 cities — same cell set as Step 8, confirmed by `step9_b_array_full.sh:31-38` `ARCHS`/`CITIES` arrays: SingleD/OtherDwelling/MidRise/HighRise x Toronto_5A/Kelowna_5B/Vancouver_5C/Montreal_6A/Calgary_6B/Winnipeg_7A) x 2 years (2022, 2030 only — no 2005/2010/2015 for Step 9) x 2 arms x n=50 HH/cell.
- 4,800 count confirmed independently in two places: `run_step9_local.py:14` "24 cells x 2 treatments... x 50 HH x 2 years... = 4,800 E+ runs total"; `Step9_docs/si_appendix_step9.md:170` "4,800"; and the cluster run's own tally `cluster_run.md:257` "4,800-run campaign", `:807` "4795/4800", `:813` "4795/4800 files loaded".

**Q3 — Sampling: SAME seed-42 households as Step 8, paired by construction, not an independent draw.**
- `Step9_docs/step9_cluster/step9_idf_gen_full.py:9` "n=50 HH/cell, seed=42 + per-cell SHA-256 draw — SAME HH as Step 8 (paired)"; `:12` "so HH selection is identical to [Step 8]"; `:58` `_cell_seed()`, `:143,151,153` `rng = random.Random(_cell_seed(args.seed, cell_label)); sampled = rng.sample(pool, args.n)`. Default `--seed 42` at `:91`.
- Local path confirms explicitly: `run_step9_local.py:9-12` "a fixed --seed draws the SAME households for baseline and activity, and the SAME households Step 8's targeted 2022/2030 re-sim used... -> Step 8/Step 9 stay paired with no extra bookkeeping." Storage: same `BEM_Schedules_{year}.csv` / `BEM_Schedules_{year}_baseline.csv` panel files under `BEM_SETUP_DIR` as Step 8 (T16 Q2), no separate Step-9-only ID store.

**Q4 — Inputs beyond Step 8.**
- Activity-to-end-use table: `2J_docs_occ_nTemp/activity_loads.py` — `WEIGHT` dict (activity->end-use weight matrix, `:33`), `APPLIANCE_W` (`:68`), documented in `Step9_docs/si_appendix_step9.md:56` "Table S4.1 — Activity -> end-use weight matrix".
- SHEU calibration scalars: `activity_loads.py:82-83` `SHEU_EQUIP_KWH = 3700.0`, `SHEU_LIGHT_KWH = 1262.0`, `:103` `SHEU_BY_DTYPE` (per-dwelling-type targets), applied in `:197` `calibrate_schedules()`; documented `si_appendix_step9.md:108` "Table S4.2 — SHEU 2019 calibration targets". **Literal name `f_e` NOT FOUND** anywhere in `Step9_docs` or `activity_loads.py` — the scaling scalars exist under the names above, not that symbol.
- File tied to schedule year that must be regenerated if `BEM_Schedules_2022/2030.csv` change: `07_aug_to_bem.py` (root of `2J_docs_occ_nTemp/`) is the producer of the activity CSV — confirmed here (T16 left this NOT independently verified) by `Step9_docs/cluster_run.md:16` "Stage A: `07_aug_to_bem.py` -> activity CSVs". The baseline CSV is then re-derived from that same run by `Step9_docs/step9_cluster/step9_a2_baseline_extract.py` (`cluster_run.md:38`, D4) — so both the activity and baseline arms must be regenerated together whenever the underlying schedules change, via `07_aug_to_bem.py` then `step9_a2_baseline_extract.py`.

**Q5 — Outputs and post-processing.**
- Per-run: `Scenario_{year}.idf`, E+'s own outputs, and a parsed `hourly_meters.csv` per (cell/arm/sample/year) dir — same layout convention as Step 8 (`run_step9_local.py:22-24`).
- SHEU cell gates (48 cell x year table): `Step9_docs/step9_cluster/step9_validate_full.py` — `SHEU_EQUIP_NET`/`SHEU_EQUIP_GROSS`/`SHEU_LIGHT` dicts (`:38,40-41`), gate logic `:107-161`; console table format `:235-253`.
- Load-shape / end-use-by-hour: `Step9_docs/step9_cluster/step9_loadshape_aggregate.py:7-10` — writes `loadshape_profiles.csv` (mean diurnal W per cell/year/arm/hour), `peak_hours.csv`, `peak_shift_summary.csv`.
- Paper-facing cross-check/scorecard: `2J_docs_occ_nTemp/09_activityDrivenLoads_val.py:3-10` — reads the four Step9_docs CSVs, writes `outputs_step9/figV1_default_vs_step9_equip.png` and `outputs_step9/step9_validation_report.html`. Exact script that assembles the final manuscript EUI table was NOT FOUND in the paths read (SI appendix `si_appendix_step9.md` presents Tables S4.1-S5.2 as prose/values, not a script pointer).

**Q6 — Resources, runtime, traps.**
- Cluster array resources: `step9_b_array_full.sh:2-9` — `partition=ps`, `array=0-47`, `cpus-per-task=4`, `mem=16G`, `time=48:00:00`, up to 4 E+ runs in parallel per task (`:14,28` `MAX_PAR=4`).
- Local resources: `run_step9_local.py --workers 1 --ep-workers 18` (`step8_2022_2030_resim_implementation.md:467`); expected wall-clock "very roughly ~40-45h... estimate pending actual completion data, not a confirmed figure" (`:475-478`).
- Trap 1 — the "-4h injection bug": `07_aug_to_bem.py` wrote GSS diary slots directly to E+ Hours without an offset, shifting the activity peak ~4h from baseline; fixed and reverified as "0 ± 1 h" peak shift, `cluster_run.md:467-469,878`.
- Trap 2 — EPW path invisible in Singularity container (`/nfs/speed-scratch` vs `/speed-scratch` symlink resolution) plus CRLF corrupting the manifest path field, D6 `cluster_run.md:40`.
- Trap 3 — sampling-pool skips: original pool drawn from `baseline/2022` only, causing HH absent-from-2030 skips (238/240 IDFs); fixed by intersecting all 4 CSVs, D5 `cluster_run.md:39`.
- Trap 4 — warmup convergence failures needing a 120-day warmup recovery pass (`step9_warmup120_recovery_v2.sh`), final residual "5 of 4,800 runs (0.1%)" undelivered, SHEU gates still pass at n=49 — `cluster_run.md:610-618,807`, `si_appendix_step9.md:388`.
- Trap 5 — manifest-clobbering risk on the local path: a second treatment's `run_paired_mc.py` cell_manifest.csv write could mislabel the other treatment's households; mitigated by reading `hh_id` back from the directory name instead of the manifest — `run_step9_local.py:25-27`.
- No `module load energyplus` on Speed — same wrapper-binary pattern as Step 8 (`step9_b_array_full.sh:17-24`, singularity SIF at `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`).

**Q7 — Staged Speed tree pattern (T17/T22 `code/repo` + `sched/`): mostly works, needs 3 extra assets.**
- T17/T22 mention no Step 9 material at all (grep for "Step9"/"Step 9"/"step9" in both docs returned no matches) — the pattern was built and proven only for Step 8's `run_paired_mc.py` engine.
- The local Step-9 path is a thin wrapper around that SAME engine: `run_step9_local.py:5,58` `DRIVER = Step8_docs/run_paired_mc.py`, `:53,55-56` `sys.path.insert(0, S8DOCS); from eSim_bem_utils_2J.main import BEM_SETUP_DIR; from run_bem import all_cells, resolve_cell` — i.e. it reuses exactly the staged `code/repo/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J` + `BEM_Setup/WeatherFile` + `Buildings_MTL_v242` tree T17 already proved out (`.../T17_speed_reproduces_local_campaign.md:64-67,156-159`).
- Extra assets needed beyond T17's staged tree (sizes from local `Get-ChildItem`, not Glob — this pass's Glob calls on `BEM_Setup/` returned no results though the dir exists, so file sizes below are read directly, not via Glob per the task's instruction to prefer Glob/doc prose — noted as a deviation):
  1. `Step9_docs/run_step9_local.py` itself (15,123 bytes) — lives outside `Step8_docs`, not part of what T17 staged; must be copied in or its logic re-implemented.
  2. A second, baseline-arm schedule directory: `BEM_Setup/_step9_baseline_sched/BEM_Schedules_{2022,2030}.csv` (474,171,469 and 474,195,321 bytes respectively) — hardlinks that expose the 13-col baseline CSVs under the plain filename `run_paired_mc.py --sched-dir` expects (`run_step9_local.py:6-9,59`); T17 staged only the activity CSVs (`.../T17_speed_reproduces_local_campaign.md:65-67`, `BEM_Schedules_2022.csv` at 673,929,104 bytes for the activity arm).
  3. Post-processing scripts `Step9_docs/step9_cluster/step9_validate_full.py` and `step9_loadshape_aggregate.py` (SHEU gates / load-shape tables) — these live under `Step9_docs`, not `Step8_docs`, so T17's staged tree does not carry them.

## Decisions
None required — all seven questions were answerable (with explicit NOT FOUND sub-points noted above) from `Step9_docs/`, `activity_loads.py`, `09_activityDrivenLoads_val.py`, the T16/T17 docs, and local filesystem size checks; no ambiguity needed the manager's judgment call.

## Next
Manager: write T21 (Step-8 + Step-9 reruns, 2022 and 2030, new schedules) from T16 + T25.

## WHAT I DID NOT VERIFY
- Did not confirm whether the 2026-07-11 local Step-9 re-sim (`run_step9_local.py`) actually reached completion — the only doc that mentions it (`step8_2022_2030_resim_implementation.md`) leaves it "IN PROGRESS" at its last entry; did not search beyond that doc and `Step9_docs/` for a later completion note (e.g. a fresher manifest row count), per the "no multi-MB file reads" and time-budget constraints.
- Did not open `step9_manifest.csv` under `BEM_Setup/SimResults_Step9/campaign_N50_2022_2030/` (head-only was permitted but not attempted — ran out of scoped budget after the sizing checks in Q7).
- Did not verify the exact script that builds the final manuscript EUI table/end-use-by-hour figure beyond `09_activityDrivenLoads_val.py` and `step9_loadshape_aggregate.py` — `si_appendix_step9.md`'s tables are not explicitly script-attributed in the ranges read.
- Did not open `eSim_bem_utils_2J/integration.py`'s activity-arm injection code path in `Step9_docs` context (Q4/Q5 answers rely on `cluster_run.md`/`si_appendix_step9.md` prose plus `activity_loads.py`, not a re-read of `integration.inject_schedules()` itself — already covered from the Step-8 side in T16).
- Q7 asset sizes were obtained via direct PowerShell `Get-ChildItem`, not `Glob`, because `Glob` returned "No files found" for `BEM_Setup/*` patterns in this session even though the directory exists (confirmed via `Test-Path`) — flagged as a possible Glob-tool limitation on this large tree, not a data gap.
