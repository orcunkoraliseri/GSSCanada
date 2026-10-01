# TASK (employee, Sonnet): 5J campaign design (Spain + Italy): dwelling counts, splits, run tables, timing check

Written 2026-09-30 16:16 EDT (from `date`) by the 5J manager. Step 2 closure, part 2 of 2 (part 1 =
`2026-09-30_wp1_it_households_TASK.md`, runs in parallel on `5J/households/`; do not touch that folder).
State file: create `Step2_docs/impl/2026-09-30_wp1_campaign_design.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY), write as you go; `date` before every stamp.
G = `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`. Read first: `Step2_docs/5thJ_02_campaignDesignPilot.md`
(2A-2E), `Step3_docs/5thJ_03_fullCampaign.md`, `Step2_docs/impl/2026-09-30_wp1_mz_repilot.md` (incl. "Verified
(manager)"), `Step2_docs/outputs_step2/mz_pilot_runs.csv` (placement format), the Progress Log entry "O-3 RULED"
of `5thJ_00_Occupancy_Surrogate_Pipeline.md` (the rules below are its detail).

## Hard rules
* 🔴 ALL compute on Speed (author). Locally ONLY: edit/write files, `ssh`/`scp`, `ls`, read small files. No local
  python, no local EnergyPlus. Login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file
  `cat`/`tail`/`wc -l`. Every job: `#SBATCH -p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`, EnergyPlus as in `tools/speed/mzp_array.sh` (never name the
  input `in.idf` in the run dir). After `sbatch`: at most 6 checks, each ONE ssh call `sleep 30; sacct -j <id> -X
  --format=JobID,State,ExitCode,Elapsed,MaxRSS`; if not done, JobID in the Ledger with "manager to read" and stop.
* 🔴 UK licence: this task designs Spain and Italy only. UK TABULA rows are public and may be read, but no UK
  household, diary, schedule or output is ever opened. No repo-wide or folder-wide search, no wildcard that could
  match a UK file. Stage only the `es` and `it` rows of `buildings.csv` to Speed (filter locally by reading the
  file; say so).
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor `tools/5thJ_idf.py`, `tools/5thJ_idf_mz.py`. New files only.
* Speed folder: `R=/speed-scratch/o_iseri/5J/campaign_prep/` (create). Read-only: every other `5J/` folder.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: Italian dwelling counts
Run the Part A reader of the builder task (`tools/speed/mz_partA_tabula.py`, a copy with the country as an
argument; do not edit the original) for the 24 `Code_Building` values of
`4J_docs_occ\Step8_docs\outputs_step8\archetype_parameters_it.csv`. Write `outputs_step2/dwelling_count_it.csv`
(same columns as `dwelling_count_es.csv`), and per Italian building of `buildings.csv`:
`k = max(1, round_half_up(n_Apartment / n_Storey))` (manager ruling), n_dwellings = k x n_Storey (SFH/TH k = 1,
one dwelling). Print a table of TABULA n_Apartment vs modelled n_dwellings per code (the difference is recorded,
not fixed). If a code has no value: say so, do not invent one; Status BLOCKED for that code.

## Part B: splits (households and buildings), written once, for Spain and Italy
* Households: `split_draft` of `outputs_step2/households.csv` as is (40 dev / 10 val / 10 test per country).
  Print the counts by household size per split.
* Buildings: per country, per class, shuffle the 10 buildings with `random.Random(7000 + c)` (c = 0 es, 1 it; one
  generator per country, classes in the order SFH, TH, MFH, AB): position 0 -> test, 1 -> val, rest dev. Then,
  with the same generator, pick 1 more test and 1 more val from the dev buildings of all classes (sorted by
  building_id before the draw): 30 dev / 5 val / 5 test, every class in every split.
* Write `outputs_step2/splits_households.csv` (household_id, country, split) and `splits_buildings.csv`
  (building_id, country, class, split); md5 of each in the state file.

## Part C: run tables (the manager's O-3 ruling)
Per country, 3 climates (from `climates.csv`), 40 buildings. Placement is the SAME in the 3 climates of a country
(paired climates); run_ids differ.
* **SFH/TH:** every household of the country (all 60, all splits) one run on every SFH/TH building; placement
  `0:<hid>`.
* **MFH/AB (every flat tested, P = 3):** for each building and each household pool (dev 40, val 10, test 10):
  runs = ceil(|pool| x 3 / n_dwellings); fill the runs' slots (run by run, dwelling 0..n-1) with concatenated
  permutations of the pool, permutation m drawn with `random.Random(100000*c + 1000*b + 10*pool_idx + m)` (b =
  building number, pool_idx 0 dev 1 val 2 test). A run holds households of ONE pool only (households never cross
  splits). If n_dwellings <= |pool|, no household twice in one run: when a clash would occur, swap the later slot
  with the nearest following slot that does not clash (deterministic; count the swaps).
* **B0:** one run per building and climate, every dwelling = the country's average household (`<country>_avg`,
  built by part 1).
* **Replicates:** per country 10 inputs (the first dev household on each SFH and TH building of the first 5
  buildings by id, and run 1 of the dev pool on 5 MFH/AB buildings including the one with most dwellings), climate
  1 only, 10 repeats each (replicate 1..10).
* Columns: `run_id, country, climate_id, building_id, class, k, n_floors, n_dwellings, pool, building_split,
  replicate, seed, placement`. `run_id` = `<cc>_<climate>_<building>_<pool>_<r>` (+ `_rep<n>`). Files
  `outputs_step2/campaign_runs_es.csv`, `campaign_runs_it.csv`; md5 in the state file.
* Gates (each PASS/FAIL line, each seen failing on a scratch copy): (C1) every household sits in >= 3 dwellings of
  every MFH/AB building (seen failing: drop one run); (C2) no run mixes pools (plant a val hid in a dev run);
  (C3) placements identical across the 3 climates (change one slot); (C4) every SFH/TH building x household x
  climate present exactly once (drop one row); (C5) run counts per country, class and pool printed and equal to the
  formula; (C6) no duplicate run_id.

## Part D: timing and disk check job (ONE job, real EnergyPlus)
Stage the builder + 4J `4thJ_step8_idf.py` (layout as in `5J/mz_pilot/repo/`), the es+it building rows, Madrid EPW
and the Italian EPW of climate 1. In ONE sbatch job: build and run (i) the Spanish building with the most dwellings
(AB.06, 77 zones expected) and (ii) the Italian building with the most dwellings, each filled with Spanish pilot
households from `/speed-scratch/o_iseri/5J/pilot/inputs/` round-robin (TIMING ONLY, not a design run; say so).
Record seconds, MaxRSS, `du -sk` of each run folder, 0 Severe + "Completed Successfully". Then `du -sb
/speed-scratch/o_iseri/5J` (the 5J folder ONLY) and `df -B1 /speed-scratch/o_iseri` (print the whole line; the
disk parser is tested on this real line, failure class 59). Print `PREFLIGHT_DISK free_bytes=.. used_5J=..`.
Arithmetic (INFO, printed): per country, runs x seconds (class medians from the re-pilot, and for n_zones > 18 the
seconds per zone of the two timing runs) -> CPU-hours and wall hours at 30 CPUs; peak disk = 30 x largest raw
folder + all runs x extracted size per class (re-pilot 5.2 medians; scale AB by zones for the big buildings).

## Part E: `outputs_step2/campaign_design.md` (the frozen design Step 3 reads)
Sections: counts per country (runs, B0, replicates, total) from the run tables; splits and md5s; the placement
rule; targets (heating, cooling, equipment, total electricity with COP 3.0 ASSUMED) and the output list of the
design doc; extraction format (as `tools/speed/mzp_extract.py`, one file per run) and the rule that the raw folder
is deleted only after that run's checks pass; arrays (one per country x climate, `%30`, block of runs per task sized
so a task lasts 20-60 min: give the number); the timing and disk numbers of Part D; open items (UK arrays wait on
the author's UK household script `tools/5thJ_design_households_uk.py` and the UKDS 5J project line; lighting not
modelled, asked; COP ASSUMED; interior R ASSUMED; TABULA n_Apartment vs modelled count). No recommendation.

## Report back (short)
Italian k table; split counts; run counts per country; gates + seen-failing lines; timing of the two big runs; the
disk line; JobIDs. Status DONE, Next = "manager verifies; manager freezes the design; Step 3 campaign task".

## What the manager will re-derive
One MFH run count from the formula; C1 on one building from the csv (inside a Speed job); one big run's seconds
from sacct; the free-bytes number from the raw df line.
