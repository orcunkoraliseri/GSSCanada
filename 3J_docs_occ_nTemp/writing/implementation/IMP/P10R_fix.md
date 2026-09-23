# P10R - fix the frame defect (Option R) - implementation state

Task doc:   `writing/implementation/3J_IMP_execution_2026-09-22.md` §P10R; design `IMP/P10_2030_level_check.md` §7 Option R
Status:     PHASE A DONE (2026-09-22 18:55) - Speed campaign staged, NOT submitted
Scripts:    `IMP/scripts/p10r_*.py` (+ `.out`/`.json`); new pipeline scripts `*_P10R.py` beside the originals

## Ledger
(local runs only; no Speed jobs in this task)
- 2026-09-22 A1 controls: `p10r_gates.py` on frozen products -> `scripts/p10r_gates_control_frozen.out/.json`,
  `scripts/p10r_gates_control_mutex.out/.json`. Exit 0 under `--expect FAIL` (every requested gate failed).

## Verified

### A1 - gates written before any product, each seen failing (`scripts/p10r_gates.py`)
Outcomes per gate: NOT_RUN / PASS / FAIL / NOT_EVALUABLE (a crash; never PASS). Exit codes: 0 all
requested PASS; 1 any FAIL; 2 no FAIL but a NOT_EVALUABLE; 3 under `--expect FAIL`, some gate did NOT
fail. Crash path seen: `--res2022 does_not_exist.csv` -> `(a)=NOT_EVALUABLE exit=2`.

| Gate | Definition | Control (frozen product) | Seen failing? |
|---|---|---|---|
| (a) | Y2022 residential, weekday clock h 9..16 mean of hourly HH-mean `Occupancy_Schedule` = 0.4180 +/- 0.005 | `outputs_step7/BEM_Schedules_4split_2022.csv` (281d96c0): **0.3006** | FAIL, yes |
| (b) | 2030 file, BAND=hybrid, weekend (strata 2,3) day-mean over 48 slots, LFTAG 1 and 2, home and work, minus OBS2022 same LFTAG: all four abs <= 1.4 pp | `_C_v2` (5aa74f44): LFTAG1 home **-8.99**, work **+6.48**; LFTAG2 home -9.06, work -2.67 | FAIL, yes |
| (c) | H8 `check_mutex` = 0 on each file/frame + calibration log shows the post-resolution hard assert at all 6 stages and final conflicts 0 | (i) in-memory copy of `_C_v2` rows with ONE injected home&work slot -> H8 fired; (ii) a log carrying only the post-StageB line -> 5 stages NOT FOUND | FAIL, yes (both). `_C_v2` itself: H8 0 conflicts (clean, as expected) |
| (d) | every cell manifest `INPUTS_HASH_DETAIL` entry: file in `outputs_step7_P10R/`, no frozen md5 on residential/office/retail, md5 == P10R registry == md5 on disk now | frozen `B_central__Tall__MTL`, `Y2022__Tall__MTL` manifests: all 8 entries BAD (old dir; 6 frozen md5s; no registry yet) | FAIL, yes |

**Employed-only SE, recomputed BEFORE the rake** (`p10r_gates_control_frozen.out`, OBS2022 =
AUG `CYCLE_YEAR==2022 & IS_SYNTHETIC==0`, weekend strata 2+3, SE of per-person day-means):
- LFTAG 1, n = 191: home 0.7863, **SE 1.44 pp**; work 0.0731, **SE 1.07 pp**.
- LFTAG 2, n = 17: home 0.8223, SE 4.52 pp; work 0.0931, SE 4.64 pp.
- All (for reference, reproduces the doc's pooled values): n = 208, home SE 1.37 pp, work SE 1.05 pp.
- Note: the gate tolerance 1.4 pp (manager's number) is ~0.97 SE for LFTAG-1 home, ~1.3 SE for work.
  Kept as set. The rake hits its slot targets directly, so the post-rake gap should be near 0 by
  construction; the tolerance is a guard against a rake that did not land, not a sampling test.

### A2 - re-rake -> `_C_v3` (DONE 2026-09-22 18:22, 33 s)
- Script: `Leg3_4-split/Step6_docs/3rdJ_06_calibrate_C_4split_P10R.py` (copy of `3rdJ_06_calibrate_C_4split.py`
  ffce34e6, untouched). Change: C0, C1, RETAIL loop `for lf in LF_STRATA=[1,2]`, target from
  `obs22[LFTAG==lf]`, applied to `out[LFTAG==lf]`; LFTAG 3/NaN not touched by these stages. Command
  (from `Step6_docs/`): `py -3 3rdJ_06_calibrate_C_4split_P10R.py --out_tag v3`; log
  `Step6_docs/run_calibrate_P10R_20260922.log`.
- Output: `Step6_docs/outputs_step6/2030_synthetic_diaries_4split_calibrated_mindwell_C_v3.csv`,
  111,024 rows, **md5 `6ee73094bc076955baef52eec51e8764`**. `_C` and `_C_v2` untouched.
- Targets (log): LFTAG 1 weekend work 0.0731 (n 191), home 0.7863; LFTAG 2 work 0.0931, home 0.8223 (n 17).
  Post-C1 mutex resolution cleared 11,215 home&work slots (local min-dwell re-creates home on work
  slots; resolution sets home=0). All six post-resolution asserts passed; final conflicts 0.
- **Gate (b) PASS** (`scripts/p10r_gates_A2_Cv3.out`): hybrid LFTAG1 home +0.06, work -0.13; LFTAG2 home
  +1.23, work -0.23 pp. INFO: pooled bands LFTAG1 -0.14/-0.11; cons -3.08/+1.06; opt +2.60/-1.25
  (weekend band spread kept, as designed). Control `_C_v2` failed (-8.99/+6.48).
- **Gate (c) PASS**: H8 0 conflicts on `_C_v3`; log shows all 6 stages + final 0.
- Step-6 validator (`3rdJ_06_longitudinalForecasting_4split_val.py --deliverable ..._C_v3.csv --out-suffix
  _P10R_v3`, log `Step6_docs/run_val_P10R_v3_20260922.log`, report `outputs_step6/step6_validation_report_P10R_v3.html`):
  PASS 86 / WARN 18 / FAIL 4 / INFO 20. Same validator on `_C_v2` (`--out-suffix _P10R_ctrl_v2`):
  identical counts and identical per-check verdict list (diff empty). The 4 FAILs are 4.1 home/work
  reconstruction and hotel 8.1/8.3 - pre-existing, not about the 2030 file.
- Retail note: LFTAG 2 Saturday retail could not reach its target (0.0227 vs 0.0404; obs n = 7) -
  too few OUT-state candidates. LFTAG 2 is 0.6 % of the 2030 pool.

### A3 - re-assembled Step-7 products (DONE 2026-09-22 18:25, 67 s for all four builds)
- Script `Step7_docs/3rdJ_07_aug_to_bem_4split_P10R.py` (copy of fa8bb8a8, untouched original). Changes
  listed in its header: D2030 = `_C_v3` (md5 pinned), OUT_DIR = `outputs_step7_P10R/`; `--year 2022`
  assembles `08A.demo_assemble(stock, stock[CYCLE_YEAR==2022 & IS_SYNTHETIC==0])` (3,087-row pool;
  tiers matched 25,487 / 3,406 / 223 / 386) then the unchanged residential/office/retail builders;
  `--year 2030` residential = `demo_assemble_2030(stock, band pool)`; office = `build_office_2030_product`
  and retail = `build_retail_product_2030` (unchanged code, fed `_C_v3`); hotel = byte copy of the
  frozen files with md5 asserted (NOT rebuilt). `--registry` writes the md5 registry.
- Commands (from `Step7_docs/`): `py -3 3rdJ_07_aug_to_bem_4split_P10R.py --year 2022`, then
  `--year 2030 --bundle {cons,central,opt}`, then `--registry`. Logs `Step7_docs/run_P10R_*_20260922.log`.
  The sens_* scenarios read the same files (cons/opt residential + office + retail), so nothing else to build.
- **New md5s** (`outputs_step7_P10R/P10R_products_registry.json`):
  `BEM_Schedules_4split_2022.csv` bdb9b506911922646bca6f06f065b516 · `_2030_cons` 21bbd08b48fce30a7d5a0d6d251ad6b2 ·
  `_2030_central` 65a078b798862f42c4e32f2656d28e48 · `_2030_opt` 6d5681a82fc1cd6c08c50cbfedaf540a ·
  `office_presence_multiplier_2022.csv` d94d86554bd2c3713128dbb074da4265 · `office_presence_multiplier_2030.csv`
  d78650c0922b48978f3ff736adbb0e5b · `retail_presence_multiplier_2022.csv` 33708341dacabf4d32e786a2bdd6d9ee ·
  `_2030_cons` 3f9d038789f9c86171727219c809f034 · `_2030_central` 0ec541ae0d0e9da206db486086df79a2 ·
  `_2030_opt` 756f5bf1fd021d59efbd6caf90173ae7. Hotel (unchanged, copied): 2022 7b62a885, 2030 cons
  d6e834ba / central 4b3d3a46 / opt e0ab6c86. (`office_presence_multiplier_2030_BAK_2026-09-22.csv` is the
  generator's own backup when the 2nd bundle call rewrote the office file; same md5 d78650c0 -> the
  office build is deterministic across calls.)
- **Gate (a) PASS** (`scripts/p10r_gates_A3_a.out`): new Y2022 WD 09-17 h = 0.4180 (|d| 0.0000); frozen 0.3006 failed.
- **Gate (c), Step-7 part**: every H8 check in the four build logs PASS (stock, 2022 real pool, 2022
  assembled, `_C_v3` pre-build, each 2030 assembled frame); an H8 violation aborts the build (assert).
- Levels (`scripts/p10r_levels.out`), weekday clock 09-17 h: residential Y2022 0.3006 -> **0.4180**; 2030
  cons/central/opt 0.4773/0.5186/0.5454 -> **0.2516/0.3402/0.3944** (exactly P10's same-frame values);
  weekend day-mean central 0.7882 -> 0.7959. Office_Knowledge Y2022 0.5634 -> **0.4749**; 2030 (vs the
  stale injected 1536c98c) 0.4947/0.4343/0.3750 -> **0.5283/0.4695/0.3902**; weekend day-mean 2030 central
  0.1353 -> **0.0740** (2022 new 0.0961: weekend office is now BELOW 2022, the old x2 rise is gone).
- Step-7 validator copy `Step7_docs/3rdJ_07_bemIntegration_4split_val_P10R.py` (paths only: OUT_DIR,
  D2030, md5, generator) `--all --out-suffix _P10R`, log `Step7_docs/run_val_P10R_all_20260922.log`.
  Frozen log `run_val_all_20260730.log` had FAIL only E.3 (Office_Sales band order, x3). New run: E.3 x3
  (same, Office_Sales is not the injected archetype) PLUS, in all four scenarios:
  - **B.2 / C.2 (weekday and weekend marginal vs "source diary")**: the validator's source is
    `AUG` all-cycle stock for 2022 and the WHOLE `_C` pool for 2030 (validator :272) - exactly the
    frames P10R replaces. Expected by design; the product-vs-correct-frame check is gate (a) and the
    exact reproduction of P10's same-frame numbers above. Validator reference NOT changed.
  - **M.2 (weekday retail peak outside 11-15 h)**: AB now peaks at 16 h (2022 and all 2030 bundles);
    night max <= 0.0067 so the +4 h roll is intact. Same bimodal late-afternoon shape the validator
    already documents as a real-data exception for QC-2022 (`_val.py:940-946`). Window NOT widened.
    Hourly profile: `scripts/p10r_retail_peak.out`.

### A4 - one cell end to end (IN PROGRESS)
- **How the frozen arm was built** (read from files): base arm `Step8_docs/campaign_local_v2/campaign_cf69d508/`
  (driver md5 04a2a9be, injector `cf69d508` = before the T9-9 standby floor existed), then V2-D9 retail NECB-C
  converter, then V2-D10 per-object resize (`Step9_docs/3rdJ_09H_resize_campaign_cell.py ... 1.0
  "Laundry Service Water Use 30.6gpm 180F=8.5"`), `improvements/v2/V2-E5_PREREGISTRATION.md` "Method";
  frozen manifest `RESIZE_SOURCE_CELL` / `ARMH_outdir`. Diff proof: frozen `injected_resized.idf` differs
  from `campaign_local_v2/.../B_central__Tall__MTL/injected.idf` in 166 lines (retail density/NECB-C
  + heater capacity only) and from the T9-9-era `_local_runs/_local_armH_cells/...` in 9,940 lines.
- **Does the resize need a second EnergyPlus run?** In the frozen chain, yes: the driver ran E+ once on
  `injected.idf` (outputs discarded) and the resize script ran it again on `injected_resized.idf`. Only
  the second run feeds the deliverable, so ONE run per cell is output-equivalent (control below).
- **Runner** `Step8_docs/3rdJ_08D_campaign_cell_P10R.py` (new file; frozen driver not usable as-is: it
  expects `<repo>/eSim_bem_utils/`, now at `<repo>/eSim/eSim_bem_utils/`, and has no product-dir
  option). Same functions, same order: `build_campaign_cells(REPO, step7_out=outputs_step7_P10R)` ->
  `inject_mixed_use(preserve_load_standby_floor=True, lighting_model=None, dhw_model=None)` ->
  `_ensure_output_objects` -> D9 convert+verify -> D10 resize -> ONE E+ 24.2.0 run -> `_do_postprocess`
  + `_write_hotel_dT_by_type` -> manifest (driver fields + resize stamps + `arm` + `P10R_*`). Prints one
  `[arm] preserve_load_standby_floor=...` line per cell. Deletes `injected.idf`, `injected_d9.idf` and
  `run/` on success (keeps what the frozen cells keep). Refuses any frozen outroot.
- **Static reproduction control (seen passing, and its converse)**: frozen B_central products (office
  1536c98c, retail cf8721c6, hotel 4b3d3a46, residential d36388c8, copied under canonical names to the
  scratchpad) + `--no-standby-floor --build-only` -> `injected_resized.idf` equals the frozen one except
  ONE added object (`Output:Variable,*,Water Use Equipment Total Volume,Hourly` - a report request, no
  physics) (`scripts/p10r_idf_compare_ctrl.out`, 4 differing lines of 116,233). Live injector md5 is
  233932d7 (frozen registered cf69d508, no longer on disk), so this is the evidence that the live code
  with the frozen flag reproduces the frozen wiring.
- **Gate (e) added (manager scope change: standby floor ON)** - `p10r_gates.py --idf`: all office
  LIGHTS/ELECTRICEQUIPMENT on `MXU_Office_Load_*` with min value > 0, none on `MXU_Office_People_*`.
  Control: frozen `B_central__Tall__MTL/injected_resized.idf` FAILS (12/12 office objects on
  `MXU_Office_People_B_central__Tall__MTL`, min 0.0031) - `scripts/p10r_gates_control_standby.out`.
- **Test cell DONE**: `Step8_docs/campaign_local_P10R/B_central__Tall__MTL/` (status ok, 8,760 rows,
  closures ok). Run 1 18:33-18:40 (404 s: build 18 s, EnergyPlus 359 s); its `run/` was deleted by the
  first runner version, which broke aggregation (the Step-8E aggregator reads `run/eplusout.sql`), so the
  runner now KEEPS `eplusout.sql` + `.err` (`--drop-sql` to remove) and the cell was re-run: run 2
  18:40-18:47, **398 s (build 17 s, EnergyPlus 354 s)**, runner md5 f8916ef6, injector 233932d7, E+
  24.2.0-94a887817b, INPUTS_HASH b75af528. Run 1 kept as `campaign_local_P10R/_run1_B_central__Tall__MTL/`:
  `channel_hourly.csv` a5814c28, `hourly_meters.csv` 0c23ebe0, `injected_resized.idf` 05046c7e are
  **byte-identical** in both runs (deterministic). After aggregation the test cell's `run/` was deleted
  (manager instruction, only inside `campaign_local_P10R/`). Logs `campaign_local_P10R/_logs/`.
- **Gate (d) PASS** (`scripts/p10r_gates_A4_de.out`): all 4 manifest entries in `outputs_step7_P10R`,
  md5 = registry = disk (office d78650c0, residential 65a078b7, retail 0ec541ae, hotel 4b3d3a46).
  Control: frozen cell manifest vs the registry FAILS (`scripts/p10r_gates_control_d_registry.out`).
- **Gate (e) PASS** (`scripts/p10r_gates_A4_e.out`): 12/12 office lights/equipment on
  `MXU_Office_Load_f*` (lights floor 0.0453), 0 on `MXU_Office_People_*`; retail 7 and hotel 6 objects
  also on `_Load_` schedules. Control (frozen cell) FAILED.
- **Channel intensity, test cell vs frozen cell** (report, not a gate; aggregator
  `3rdJ_08E_aggregate_4split.py --idf-name injected_resized.idf` into a scratch dir, run with
  `PYTHONPATH=<repo>/eSim` because the aggregator also imports `eSim_bem_utils`; tables copied to
  `IMP/data/P10R_testcell_agg/`; `scripts/p10r_testcell_eui.out`), kWh/m2/yr: office 71.64 -> **80.20**
  (+12.0 %), retail 77.14 -> **87.27** (+13.1 %), hotel 317.26 -> 321.08 (+1.2 %), residential 120.48 ->
  121.33 (+0.7 %), residential common 59.24 -> 59.10, service/MEP 62.53 -> 62.34; site energy +3.33 %;
  attribution residual 1e-16. Sanity vs arm A (standby floor alone, Speed, pre-fix products): its office
  median moved 71.08 -> 80.03 (`improvements/v1/3rdJ_L3_improvements_step9.md:1308`); this cell moved
  +8.6 kWh/m2, same size. Arm A's per-cell files are only on Speed (`campaign/agg_A_t99/`), not compared
  cell-to-cell. Office still far below the 100 floor, so its FAIL verdict cannot flip.
- **Disk anomaly**: at ~18:40 C: had **0 bytes free** (a scratchpad copy failed with "No space left");
  20 s later 9.96 GB free. Something else on the machine fills and frees the disk. Not mine (my new
  files total < 1 GB). Manager ruled the campaign moves to Speed.

### A5 - campaign on Speed, all 56 cells (READY, NOT submitted)
Manager scope change 2 replaced the local 39-cell command: the whole arm runs on Speed (one platform).
- **Upload tree (staged locally)**: `C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/P10R_speed_stage/`
  (built by `IMP/scripts/p10r_stage_speed.py`; 62 files, 552 MB + IDD). Contents: `repo/` mirror of every
  file the runner reads at its repo-relative path - `eSim/eSim_bem_utils/*.py`; Step8 `3rdJ_08P_probe_driver.py`,
  `3rdJ_08D_campaign_cells.py`, `3rdJ_08D_campaign_cell_P10R.py`, `3rdJ_08D_campaign_P10R_speed.sh`; Step9
  `3rdJ_09J_retail_necb_c.py`, `3rdJ_09H_plant_resize_probe.py`, `3rdJ_09H_dhw_plant_topology.py`,
  `3rdJ_09H_resize_campaign_cell.py`, `3rdJ_09H_hotel_dT_decompose.py`; `IMP/scripts/p10r_verify_mirror.py`;
  all `outputs_step7_P10R/` products + registry (no `_BAK_`); `outputs_step8/historical_schedules/*.csv`
  (Y2005/10/15, unchanged); the 4 base IDFs (Leg-2 `office_idfs_v242`, Tall/SuperTall x MTL/CLG); the
  2 EPWs; `Energy+.idd` (the local 24.2.0 IDD). **Every md5 is in `P10R_speed_stage/mirror_md5.txt`**
  (re-staged after the sql fix: md5 of the list **1d66697a**; runner f8916ef6 = the one that ran the test
  cell; sbatch 67d14c95; local re-verify 0 problems). Product md5s are the A3 list above.
- Cells keep `run/eplusout.sql` (~160 MB each, ~9 GB for 56) for the phase-C aggregation on Speed or after
  download; aggregate with `PYTHONPATH=<repo>/eSim` and `--idf-name injected_resized.idf`, then remove sql.
- **sbatch script**: `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_P10R_speed.sh` (bash, LF endings,
  `bash -n` OK): `-p ps`, 1 CPU, 8G, `-t 7-00:00:00`, `--array=0-55%26`, log
  `/speed-scratch/o_iseri/3J_P10R/logs/p10r_%A_%a.out`; python `/speed-scratch/o_iseri/envs/step4/bin/python`
  and the SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` (V3's proven setup, build
  94a887817b). Each task first runs `p10r_verify_mirror.py` (exit 3 on any md5 mismatch), then
  `3rdJ_08D_campaign_cell_P10R.py --cell $SLURM_ARRAY_TASK_ID --outroot $ROOT/campaign_P10R`.
- **Per-cell extraction** happens inside the task (the runner): `channel_hourly.csv`, `hourly_meters.csv`,
  `manifest.json`, `injected_resized.idf` (+ `dhw_hourly.csv`, `dhw_volume_hourly.csv`,
  `hotel_dT_by_type.csv`, `injected.idf.provenance.txt`, same set as the frozen cells); `run/` deleted on
  success (kept on failure for diagnosis). Output: `/speed-scratch/o_iseri/3J_P10R/campaign_P10R/<tag>/`.
- **Exact commands** (manager; single lines):
  1. locally, from `C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/` (Git Bash):
     `scp -r P10R_speed_stage o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/3J_P10R`
     (target must not exist yet, so scp creates `3J_P10R/` = the stage root).
  2. on the cluster: `squeue -u o_iseri` (count non-histnu CPUs; 3J may use up to 26 now; edit `%26` if needed
     with `sbatch --array=0-55%N ...`, which overrides the header).
  3. on the cluster: `sbatch /speed-scratch/o_iseri/3J_P10R/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08D_campaign_P10R_speed.sh`
  4. after it ends, on the cluster: `grep -l "status=ok" /speed-scratch/o_iseri/3J_P10R/logs/p10r_<array>_*.out | wc -l` (expect 56),
     then locally: `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/3J_P10R/campaign_P10R <local dest>`
     (56 cells x ~14 MB = ~0.8 GB; check local free space first).
- Expected wall time: frozen local measured 6.6 min/cell alone (V3 measures Speed times); 56 tasks at
  %26 = 3 waves, roughly 30-45 min if Speed matches local speed.
- **Speed-vs-local check** (after the array): `py -3 IMP/scripts/p10r_speed_vs_local.py
  Leg3_4-split/Step8_docs/campaign_local_P10R/B_central__Tall__MTL <downloaded>/B_central__Tall__MTL
  --tol-annual X --tol-hourly Y`, where X/Y = the linux-vs-win32 difference V3b measures ("U vs frozen",
  `IMP/V3_design_and_runs.md`), not yet available -> NOT_EVALUABLE until V3b reports. Control: the same
  script, local test cell vs the FROZEN cell, must FAIL.
- Phase C carry-over: none (all 56 cells run on Speed, incl. Default_NECB; the 16 formerly "unchanged"
  cells - Y2005/10/15 x4 and Default_NECB x4 - are re-run because the wiring changed / one platform).
- Download size warning: `campaign_P10R` with sql is ~10 GB; local C: had 6.0 GB free at 18:50. Aggregate
  on Speed (sbatch) or download without `run/`.

### B-local (2026-09-22, agent task "P10R phase B-local")

Task: make the 56-cell campaign runnable on THIS Windows machine within the tight local C: budget
(Speed has only 2 free CPUs for 3J for days, per A5; local C: was 4.3-5.7 GB free through this task,
same drive the manager saw fluctuate to 0 bytes at A4). Approach: never keep a cell's full
~160 MB `run/eplusout.sql` -- shrink it to only the tables the aggregator reads, right after each
cell finishes. Campaign NOT launched (task scope: build + verify + hand off one command only).

**1. What the aggregator reads from `eplusout.sql`.** Only two functions in
`3rdJ_08E_aggregate_4split.py` touch sql (grepped the whole file and `eSim_bem_utils/` -- nothing
else does): `parse_channel_areas()` (`SELECT ZoneName, FloorArea, Multiplier, IsPartOfTotalArea
FROM Zones`, ~:135) and `read_calendar()` (`Time` JOIN `EnvironmentPeriods`, restricted to
`TimeIndex` values that have an `Electricity:Facility` row in `ReportData`/`ReportDataDictionary`,
~:336). Five tables matter: `Zones`, `Time`, `EnvironmentPeriods`, `ReportDataDictionary` (all
tiny, kept whole) and `ReportData` (the ~99 %-of-the-file table, kept only for rows whose
dictionary entry names `Electricity:Facility` -- a strict superset of what either query can read).

**2. `IMP/scripts/p10r_slim_sql.py`** (new). `ATTACH`es the source db, `CREATE TABLE ... AS SELECT
* FROM src.<table> [WHERE ...]` for the five tables above (no version-specific column list to
maintain), adds the two indices the two queries actually use, `VACUUM`s, then `os.replace()`s the
finished file onto `run/eplusout.sql` -- the original is untouched until that last line succeeds,
so a crash mid-build cannot corrupt a cell. `--self-test FULL_SQL SCRATCH_DIR` builds both a slim
copy and a deliberately-broken copy (drops `ReportDataDictionary`) for the control below, without
touching the source.

**3. Control, seen both ways.** Re-ran `B_central__Tall__MTL` locally (fresh EnergyPlus run,
`3rdJ_08D_campaign_cell_P10R.py`, status ok, 396 s: build 17 s + EnergyPlus 352 s; fuel/channel
closures OK). Its `run/eplusout.sql` was **161.7 MB -> 1.0 MB (99.4 % smaller)** after slimming;
verify query read back `Zones` 164 rows, calendar 8760 rows. Ran the aggregator 3 ways, same
`--idf-name injected_resized.idf`, `PYTHONPATH=<repo>/eSim` (repo = `GSSCanada-main`, i.e. the dir
ABOVE `3J_docs_occ_nTemp` -- `eSim_bem_utils` lives at `GSSCanada-main/eSim/eSim_bem_utils`, not
under `3J_docs_occ_nTemp/eSim/`; the campaign runner already sets this internally, the aggregator
does not, so it needs the env var when called directly): (a) full sql -- ok, site 34,846.6 GJ; (b)
slim sql -- ok, site 34,846.6 GJ; (c) negative control, sql missing `ReportDataDictionary` --
**crashed** (`pandas.errors.DatabaseError: ... no such table: ReportDataDictionary`), i.e. seen
failing as required. Diffed all 5 output tables (`agg_annual.csv`, `agg_annual_by_channel.csv`,
`agg_diurnal.csv`, `agg_peak.csv`, `agg_meta.csv`) between (a) and (b): **byte-identical, all 5**.
Scratch outroot (`_local_runs/P10R_ctrl/`, incl. the 161.7 MB full sql) deleted afterwards.

**4. `IMP/scripts/p10r_local_campaign.py`** (new). Runs the 56 cells `3rdJ_08D_campaign_cells.
build_campaign_cells()` returns, `--workers` at a time (default 4) via
`3rdJ_08D_campaign_cell_P10R.py --tag <tag> --outroot campaign_local_P10R`; `B_central__Tall__MTL`
(already built, `P10R_STATUS=ok`) is kept and only re-slimmed, not re-run. Slims every cell right
after it finishes ok. Before starting ANY cell, waits while C: free space < `--min-free-gb`
(default 3 GB, `ctypes.windll.kernel32.GetDiskFreeSpaceExW`), logging the wait every 60 s. A
failed cell (bad exit code or a manifest that does not read back `P10R_STATUS=ok`) retries once,
then is recorded failed and the driver moves on. One status line per cell (`run`/`retry`/`ok`/
`fail`/`skip`) to `campaign_local_P10R/_logs/driver.log` and stdout. At the end runs the Step-8E
aggregator with an explicit `--outdir outputs_step8/agg_P10R/` (never the default `agg/`) and
prints `DRIVER DONE ok=<n> failed=<m>`. Writes only inside `campaign_local_P10R/`,
`outputs_step8/agg_P10R/` and its own log; never touches a frozen arm or the protected `eSim_*`
scripts.

**5. Dry-run** (`--dry-run`, real run, no work done): correctly lists all 56 tags in
`build_campaign_cells()`'s own building x city x scenario order, marks `B_central__Tall__MTL` as
`KEEP(ok)` and the other 55 as `run`, prints the current free-space reading, the aggregate target
path and the log path -- this is also what `--limit 0` does (same code path).

**Sizing.** Per running cell, `run/` peaks near ~320 MB (eso/mtr/audit/etc, before the runner's own
cleanup drops everything but `eplusout.sql`+`.err`, then slimming drops the sql to ~1 MB); at
`--workers 4` that is a ~1.3 GB transient peak on a drive already seen at 0 bytes free from other
programs. **Recommend `--workers 2`** for this machine given that anomaly (not mine -- see A4's
"disk anomaly" note); `--workers 4` is the coded default and works if the manager confirms headroom.

**Launch command** (ONE line, Git Bash, from `Leg3_4-split/Step8_docs/`):
```
PYTHONIOENCODING=utf-8 py -3 ../../writing/implementation/IMP/scripts/p10r_local_campaign.py --workers 2 --min-free-gb 3
```
(add `--limit N` for a smoke test first, e.g. `--limit 2 --workers 1`.)

**Expected wall time.** One cell measured at 396 s. 55 cells still to run (1 already ok): at
`--workers 2`, ceil(55/2) = 28 waves x ~400 s ~= 3.1 h; at `--workers 4`, 14 waves ~= 1.6 h. Final
aggregation is now cheap (56 x ~1 MB slim sql instead of 56 x ~160 MB) -- a few minutes, not
counted in the estimate above.

**NOT verified:** the driver has not run a real cell end to end (campaign not launched, per task
scope) -- only its `--dry-run` path and the control cell (built by the separate runner call, then
slimmed and aggregated by hand with the same commands the driver issues). The retry-on-failure
path and the 60 s disk-wait loop are unexercised (no failure or low-disk condition occurred during
this task). Concurrent-worker disk behaviour under real EnergyPlus load is unmeasured -- the 1.3 GB
peak above is an arithmetic estimate from the single-cell `run/` size, not a measured 4-way peak.

## Decisions
- 2026-09-22 manager scope change 1: P10R carries the T9-9 standby floor (`preserve_load_standby_floor=True`);
  52 cells re-run (Y2005/10/15 too); only Default_NECB carried over. Then scope change 2: the campaign
  runs on **Speed, all 56 cells** (Default_NECB too, one platform); only this one test cell runs locally.
- Retail 2030 still uses `build_retail_product_2030` (pools all 111,024 `_C_v3` rows incl. the
  uncalibrated LFTAG 3 rows), as ruled. Its level is not injected (the multiplier is peak-normalised
  against its own base), only its shape; the shape still mixes non-workers. Flagged, not changed.
- Manager ruling: NO weekday home target; only LFTAG stratification of C0, C1, RETAIL.
- Gate (b) is scored on the **hybrid band** (the central scenario, and the band the manager's control
  numbers -8.99 / +6.48 come from). C0/C1 rake all three bands together to one target per LFTAG (the
  frozen design pools bands; P10R changes only the LFTAG conditioning), so the cons/opt bands keep
  their weekend band spread. Pooled-over-bands and cons/opt gaps are printed as INFO, not gated.
- Gate (c) "every stage": the calibration script resolves conflicts and then hard-asserts 0 after
  each of the 6 stages (it aborts otherwise); the gate reads the log for all 6 post-resolution lines.

## Next
- Manager (phase B): upload + CPU check + submit, exact commands in A5. Then phase C: aggregate the 56
  Speed cells into `outputs_step8/agg_P10R/` (explicit path, never `DEFAULT_AGG`), Step-9 scorer into
  `outputs_step9_P10R/`, old-vs-new table for P10 §6, gate (d)+(e) over all 56 manifests/IDFs
  (`p10r_gates.py --cells ... --idf ... --registry ...`), Speed-vs-local check once V3b gives the tolerance.

## WHAT I DID NOT VERIFY
- The Speed run itself: the runner's Linux branch (SIF wrapper, version stamp) has not executed; the
  first array task is its test. The mirror layout is checked locally only.
- That the in-job `p10r_verify_mirror.py` works under the Speed python (plain stdlib, not run there).
- The cross-platform tolerance for the Speed-vs-local check (V3b not reported yet).
- The retail 2030 shape effect of the uncalibrated LFTAG-3 rows (not sized).
- Whether Office_Sales' band non-monotonicity (validator E.3, pre-existing) matters: cells inject
  Office_Knowledge only.
- What fills the C: drive to 0 bytes intermittently (not my processes; other EnergyPlus runs were live).
