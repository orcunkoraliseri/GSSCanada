# TASK (employee, Sonnet): 5J multi-zone re-pilot on Speed (every flat tested, per-dwelling targets)

Written 2026-09-30 ~16:00 EDT by the 5J manager. Read first: design `Step2_docs/impl/2026-09-30_d2-8_multizone_design.md`
(all sections incl. the RULED and Outputs sections), builder state `Step2_docs/impl/2026-09-30_wp1_multizone_builder.md`
(incl. "Verified (manager)" rulings), the old pilot task `Step2_docs/impl/2026-09-30_wp1_pilot_report_TASK.md` (gate
list) and `tools/5thJ_pilot_build.py` (how a household's inputs are made from `_5J_data/surrogate/wp1_hids/es_60/`).
State file: create `Step2_docs/impl/2026-09-30_wp1_mz_repilot.md` (Task doc / Status / Ledger / Verified / Decisions /
Next / WHAT I DID NOT VERIFY), write as you go; `date` before every stamp. G = `C:\Users\o_iseri\Desktop\GSSCanada`.

## Hard rules
* 🔴 ALL compute on Speed (author). Locally ONLY: edit/write files, `ssh`/`scp`, `ls`, read small files. No local
  python, no local EnergyPlus. Never touch a process you did not start.
* Speed login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`wc -l`. Every
  job: `#SBATCH -p ps -t 7-00:00:00 --exclude=antenna1`, `-c 1`, `--mem=4G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`; EnergyPlus 23.1 at the path in `tools/speed/5J_pilot_array.sh`
  (never name the input `in.idf` in the run dir). Arrays at most `%30` (O-5 = 30 CPUs). After `sbatch`: at most 6
  checks, each ONE ssh call `sleep 30; sacct -j <id> -X --format=JobID,State,ExitCode,Elapsed,MaxRSS`; if not done,
  JobID in the Ledger with "manager to read" and stop. Every JobID in the Ledger.
* 🔴 UK licence: Spain only. Never open or copy any UK diary, episode, manifest, the POOLED 4J corpus, or anything
  built from UK diaries. No repo-wide or folder-wide search, no wildcard that could match a UK file; name files in
  full. `buildings.csv` holds UK rows: copy only the Spanish rows (filter locally by reading the file, or stage it
  and filter inside the job before anything else reads it; write which).
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor `tools/5thJ_idf.py`. Changes to `tools/5thJ_idf_mz.py`
  are ADDITIVE only, backed up first (`tools/5thJ_idf_mz.py.v1_2026-09-30`), and each prints its `PATCH` line.
* Speed folder: `R=/speed-scratch/o_iseri/5J/mz_pilot/`. Read-only: `5J/pilot/`, `5J/multizone/`.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: builder fixes (additive)
1. **Mass budget (manager ruling):** count EVERY interior surface EnergyPlus sees (both sides of each pair) in the
   capacity budget, so total modelled capacity = c_m x A_C_Ref. Print `PATCH mz_mass OK ... interior_sides=..`.
   Gate: sum over all surfaces of (area x areal capacity) = c_m x A_C_Ref within 0.01 %; seen failing by counting
   pairs once (must FAIL). Collapse runs must stay byte-identical to the builder task's collapse IDFs (cmp).
2. **k from TABULA:** `k = max(1, round_half_up(n_Apartment / n_Storey))` from
   `Step2_docs/outputs_step2/dwelling_count_es.csv` (use one row per code; it has 3 identical rows per code: check
   they are identical and say so).

## Part B: re-pilot design (write `R/design/mz_pilot_runs.csv` + copy to `Step2_docs/outputs_step2/`)
Madrid 2010 (`/speed-scratch/o_iseri/5J/pilot/epw/`), the same 5 pilot buildings (es_B07 SFH, es_B16 TH, es_B21
MFH, es_B33 AB, es_B37 AB; rows from `buildings.csv`, Spanish rows only).
* SFH and TH (1 dwelling): 10 runs each, one per pilot household (`outputs_step2/pilot_hids_es.csv`), as before.
* MFH and AB (n dwellings): 2 runs each; run r fills dwellings 0..n-1 with a seeded permutation (seed = 5000 +
  building number x 10 + r) of the 60 households of `outputs_step2/hids_es60.csv` (first n; if n > 60, continue
  with a second permutation). Different seeds give each household different positions.
* Replicates: es_B07 with its first household and es_B37 run 1, each repeated 5 times (10 runs).
* Columns: `run_id, building_id, class, k, n_floors, n_dwellings, replicate, seed, placement` (placement =
  `j:hid;j:hid;...`). Expected total 20 + 6 + 10 = 36 runs; print the count.
Household inputs for any hid of the 60: build exactly as `tools/5thJ_pilot_build.py` does (same source files, same
n_members and appliance design level); record md5 of every presence and appliance file staged.

## Part C: runs (one build job, one array `%30`, one extraction job)
* Build all 36 IDFs; every `PATCH mz_*` line PRESENT per IDF (count them: 36 x 8 or 9).
* Each run: 0 Severe, "Completed Successfully"; `status.txt` with seconds, MaxRSS, `du -sk` of the run folder.
* **Extraction per run** to `R/extracted/<run_id>.csv.gz` (or one parquet per run): 8,760 rows x dwellings, per
  dwelling (sum of its zones): heating = `Zone Ideal Loads Supply Air Total Heating Energy`, cooling = same for
  Cooling, equipment = `Electric Equipment Electricity Energy`, total electricity = equipment + heating/3.0 +
  cooling/3.0 (COP 3.0 ASSUMED, written in the file header), plus every other variable of the design's output list
  as extra columns. Dwelling floor area and floor index in a side table. Delete nothing raw yet.

## Part D: checker `tools/5thJ_mz_pilot_check.py` (new; runs on Speed via sbatch)
One line per gate `PASS|FAIL|WARN|INFO|NOT_EVALUABLE <gate> <numbers>`, then `SUMMARY PASS=.. FAIL=.. WARN=..
NOT_EVALUABLE=..`; exit 0 only when FAIL=0 and NOT_EVALUABLE=0 among FAIL-severity gates (write this at the top).
* 2.1 36/36 extracted + status; 2.2 err file parsed (0 Severe, completed); 2.3 8,760 rows per dwelling per target;
  2.4 annual = sum of hourly per target (facility level against eplustbl.csv, < 0.1 %).
* 3.1 within each multi-dwelling run: dwellings with different households differ (equipment and heating), per
  class; across the 10 SFH/TH runs: households differ.
* 3.3 replicates: max absolute and relative spread per target over the 5 repeats (expect zero; report).
* 4.1 annual heating and cooling per m2 of DWELLING floor area, per class and per floor position (ground, middle,
  top), INFO.
* 4.3 equipment mean over hours with presence > 0 vs presence == 0 ("absent" = nobody home), per dwelling; PASS if
  >= 90 %.
* 5.1 seconds per run (median, 90th pct, max) by class and zone count; 5.2 disk per run (median, max) raw and
  extracted.
* 5.3 **draft campaign arithmetic (INFO, the manager rules):** per country and climate, 40 buildings (10 per class;
  zones from each class's k x n_Storey), SFH/TH 60 runs each, MFH/AB ceil(60 / n_dwellings) x P runs each for P = 1,
  2, 3 (positions per household); 9 climates, Spain + Italy + UK. Show runs, CPU-hours (runs x class median s),
  and finish time at 30 CPUs, and disk at peak (in flight x raw + all x extracted).
* Seen failing (scratch copies, each must print FAIL): copy one dwelling's series onto another dwelling with a
  different household (3.1); plant a Severe line in one err copy (2.2); scale one hourly series by 1.01 (2.4).

## Part E: report
`Step2_docs/outputs_step2/mz_pilot_report.md`: gate lines, SUMMARY + exit code, the three seen-failing lines, run
seconds and disk, the 5.3 table in words, one plain paragraph. No recommendation on campaign size (manager rules O-3).
State file: Status DONE, Next = "manager verifies; manager rules O-3".

## What the manager will re-derive
One dwelling's annual heating from its extracted file against the zone sums; the B21 dwelling count and area; one
run's seconds; the checker SUMMARY and exit code.
