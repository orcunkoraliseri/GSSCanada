# WP9 Stage 3: stage the April setup on Speed and prove it reproduces April (1J JBPS revision), task and implementation state

Task doc:   this file (sections "Why" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7 log (m) and (n)
Source:     `1J_docs_occ/IMP/investigate/inv_1J-01_REPORT_fable.md` R5, R7, Q3, Q8, section 6 Stage 3
Status:     IN PROGRESS

## Why

Before any new energy result is paid for, the staging folder on Speed must reproduce the April 20-draw cluster
batch (the one behind the submitted figures). The local pilot does NOT: Default RC6 heating 157.568 locally vs
150.780 in `BEM_Setup/SimResults/BatchAll_MC_N20_v2/NUS_RC6/aggregated_eui.csv`, a 4 % gap of unknown cause
(neighbourhood IDF, weather file or EnergyPlus build). This task also gives the first MEASURED time and memory of
one simulation. It uses the April code and the April method; the input fixes (Stage 1) come later and do not
affect the Default building.

## Task

Cluster: `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`. Login shell is tcsh.

**Step 1. Staging folder.** Create `/speed-scratch/o_iseri/1J_rerun/` (new; never write into
`/speed-scratch/o_iseri/GSSCanada/`). Inside it:
- `code/`: a copy of the April cluster code tree that `submit_array_tuned.sh` ran
  (`/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/`; read that script first to see the exact entry point, the
  code folder and `BEM_Setup` layout it expects; copy with `cp -rp` inside an `sbatch` job if the tree is large,
  plain `cp -rp` on the login node is allowed only for a few files). `BEM_SETUP_DIR` is derived from the code
  location (`main.py:33-34`), so the copy must carry its own `BEM_Setup/Neighbourhoods`, `BEM_Setup/WeatherFile`.
- Record the md5 of every `.py` in the staged `eSim_bem_utils/` (inside an `sbatch` job) and compare with the
  cluster originals; they must be identical.

**Step 2. Find the cause of the Default gap (R7), read-only.** In an `sbatch` job, compute md5 of: each
`BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf` and each `.epw` in `BEM_Setup/WeatherFile/` on the cluster tree; locally,
the same files under `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\` (local md5 with `certutil` or
`py hashlib`). Read the EnergyPlus version line and the weather file line from one old cluster `eplusout.err` or
`eplusout.eio` of the April N20 batch (find where its outputs sit on Speed; `ls` only) and from one local pilot
Default run in `BEM_Setup/SimResults/BatchAll_MC_N3_1776120359/NUS_RC6/Default/`. Report what differs.

**Step 3. One test run (Gate 3).** In the staging folder, submit ONE `sbatch` job:
`-p ps -A chachemv -c 1 --mem 24G -t 7-00:00:00`, running `run_batch_hpc.py` for `NUS_RC1` only, `--iter-count 1`,
`--workers 1`, `--sim-mode standard`, **no `--use-tmpdir`**, `--output-dir /speed-scratch/o_iseri/1J_rerun/stage3/draw_1`
(so the batch name becomes `draw_1_NUS_RC1`, R5), with the region and IDF arguments exactly as
`submit_array_tuned.sh` passed them. Use the venv `/speed-scratch/o_iseri/GSSCanada/venv` and EnergyPlus
`/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64`.
Schedule inputs for this test: stage the April files, renamed to the names the code reads
(`BEM_SETUP_DIR/BEM_Schedules_{year}.csv`), from local copies via `scp`:
- 2005 `0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct.csv` (md5 57fd2732...)
- 2010 `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv` (md5 e5ba8068...)
- 2015 `0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct.csv` (md5 2bd251db...)
- 2022 `BEM_Setup/BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` (md5 34a1f8fa...)
- 2025 `BEM_Setup/BEM_Schedules_2025.csv` (md5 3e34561b...)
Check the five md5 on Speed inside the job before the run starts, and have the job stop if any two are equal.
Then submit a SECOND job, same settings, for `NUS_RC6`, `--iter-count 1`, output `.../stage3/draw_1` (memory check).
Write both JobIDs into the Ledger below, then END YOUR TURN. Do not wait for the jobs.

## Rules

- 🔴 Login node: only `sbatch squeue sacct scancel scontrol cd ls scp module load` and single-file
  `tail/head/grep/wc -l/cat`. NEVER python, never `srun`, never a loop over folders, never md5 on the login node.
  Every job asks for `-t 7-00:00:00`. tcsh: avoid `2>/dev/null` and awk `$` inside ssh strings; write job scripts
  as files locally and `scp` them over.
- Never touch `/speed-scratch/o_iseri/GSSCanada/` except to read and copy from it.
- Nothing runs locally except md5 of the local files.
- Write state into this file as it happens. End with the JobIDs, Status IN PROGRESS, and a `Next` line.

---

## Ledger

(JobID · what · state · exit · output path)

- 1339754 · Step1+2 job: staged `eSim_bem_utils/` + `BEM_Setup/{Neighbourhoods,WeatherFile}` into
  `/speed-scratch/o_iseri/1J_rerun/code/` with `cp -rp`; md5 of staged vs cluster-original
  `eSim_bem_utils/*.py` (16 files); md5 of cluster `NUS_RC{1..6}.idf` and all 6 `.epw` · COMPLETED ·
  exit 0 · log `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage1_2_1339754.out`
- 1339756 · Step3 test run: `run_batch_hpc.py --idf NUS_RC1.idf --region Quebec --sim-mode standard
  --iter-count 1 --workers 1` (no `--use-tmpdir`), staged code/venv/EnergyPlus · submitted, RUNNING at
  submit time (confirmed via `squeue`, not waited on) · output
  `/speed-scratch/o_iseri/1J_rerun/stage3/draw_1` · log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage3_RC1_1339756.out`
- 1339757 · Step3 test run: same settings, `NUS_RC6.idf` (memory check) · submitted, RUNNING at submit
  time (confirmed via `squeue`, not waited on) · output `/speed-scratch/o_iseri/1J_rerun/stage3/draw_1`
  · log `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage3_RC6_1339757.out`

## Verified

- All 16 staged `eSim_bem_utils/*.py` files are byte-identical to the cluster originals (md5 MATCH on
  every file) — job 1339754 log.
- The 6 `NUS_RC{1..6}.idf` files are byte-identical between the cluster tree and the local repo (same
  md5 on both sides, e.g. `NUS_RC6.idf` = `30050f32cd53393d2e068827f838fd2f`).
- All 6 `.epw` weather files are byte-identical between the cluster tree and the local repo, including
  `CAN_QC_Montreal...716120_TMYx_6A.epw` (the one RC1-RC6 actually use), md5
  `06b938811fc706a399bbe37d8c259327` on both sides.
- EnergyPlus build is identical on both sides: `24.2.0-94a887817b`. Cluster value read from the April
  N20 batch's own job stdout log header (`/speed-scratch/o_iseri/GSSCanada/logs/eSim_900550_6.out`,
  identified as the RC6 array task by its printed `Output dir: .../BatchAll_MC_N20_v2/NUS_RC6` line);
  local value read from `eplustbl.htm`'s "Program Version" line in
  `BEM_Setup/SimResults/BatchAll_MC_N3_1776120359/NUS_RC6/Default/eplustbl.htm`.
- **R7 finding: neither side has an `eplusout.err`/`eplusout.eio`.** The April cluster batch was run
  with `--use-tmpdir`, which (per `run_batch_hpc.py` help text) only copies `eplusout.sql` and the CSVs
  back out of `$TMPDIR`, discarding `.err`/`.eio`; checked both `.../NUS_RC6/Default/` and
  `.../iter_1/2022/` on the cluster, neither has them. The local pilot's `Default/` folder also has no
  `.err`/`.eio`, only `eplustbl.htm`. So the version/weather line came from the job log (cluster) and
  `eplustbl.htm` (local) instead — both agree, so **IDF, weather file, and EnergyPlus build are ruled
  out as the cause of the 4% Default-RC6 gap**; the cause is still open and must be elsewhere
  (sim-mode, worker count, MC draw count N3 vs N20, or something not checked here).
- The 5 staged April schedule CSVs: local md5 before upload matched the task doc's quoted prefixes
  exactly (2005 `57fd2732...`, 2010 `e5ba8068...`, 2015 `2bd251db...`, 2022 `34a1f8fa...`, 2025
  `3e34561b...`); post-`scp` file sizes on Speed match the local files byte-for-byte (77037650,
  88032159, 84606105, 103368174, 63963284 bytes). The dedupe-and-stop check runs again inside jobs
  1339756/1339757 before each simulation starts.

## Decisions

- **`code/` copy scope narrowed.** `submit_array_tuned.sh`'s entry point (`run_batch_hpc.py`) only
  imports from `eSim_bem_utils` (`grep` confirmed no cross-package imports out of it), so only
  `eSim_bem_utils/` (whole dir) + `BEM_Setup/Neighbourhoods/` + `BEM_Setup/WeatherFile/` were copied,
  not the full 72 GB repo (`0_Occupancy/`, `.git`, doc trees, other schedule CSV snapshots under
  `BEM_Setup/` are all unused by this entry point and were left out). This satisfies the task doc's own
  parenthetical ("must carry its own `BEM_Setup/Neighbourhoods`, `BEM_Setup/WeatherFile`") without
  copying data this run never reads.
- **April reference batch identified as job 900550** (array 1-6, task 6 = NUS_RC6), matched by its
  printed `Output dir: .../BatchAll_MC_N20_v2/NUS_RC6` header line — used as the "old cluster
  `eplusout.err`/`.eio`" source required by Step 2 (neither file exists, see Verified).
- **Step 3 `--region` set to `Quebec`** for both NUS_RC1 and NUS_RC6, matching
  `submit_array_tuned.sh`'s `REGIONS` array (all six neighbourhoods use `Quebec`).

## Next

- Poll `sacct -j 1339756,1339757` (not a long sleep loop) once, then read
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage3_RC{1,6}_*.out` and the
  `/speed-scratch/o_iseri/1J_rerun/stage3/draw_1/` output tree for exit codes, wall time, peak memory,
  and the Default RC1/RC6 heating numbers to compare against the April 150.780 figure.
- R7 is still open (IDF/weather/EnergyPlus build ruled out) — next candidate checks: `--sim-mode`
  (weekly vs standard), `--workers` count, and N3-vs-N20 Monte Carlo draw noise.

## WHAT I DID NOT VERIFY

- Whether the Step 3 test runs actually reproduce the April Default RC6 number — jobs were still
  running at end of turn, not checked.
- The Python venv / package versions were not compared between April and now (reused
  `/speed-scratch/o_iseri/GSSCanada/venv` as-is, per task doc; no independent check that its packages
  are unchanged since April).
- No content comparison of `BEM_Schedules_2022.csv` against what was live on the cluster in April —
  task doc asked for the local `BAK` snapshot specifically, not a match to the cluster's current file,
  so none was owed.
- Did not read `eplusout.sql` or the rest of `eplustbl.htm` beyond the version/weather lines (e.g. no
  check of run period or ground-temperature settings that could also affect Default RC6 heating).
