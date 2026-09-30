# WP13 — Section 4.1 occupancy metrics and figures from the rebuilt files, Canada vs Quebec (WP3), matching-tier shares — task + state
Task doc:   this file (manager-written 2026-09-29, plan log (bi))
Status:     SUBMITTED (job 1401447, 2026-09-29; not polled)
Model:      Sonnet employee. One agent, one task, one turn. Submit, write state here, stop. Never wait or poll.

## Why
Every Section 4.1 number and Figures 8, 11, 12, 13, 14, C1, C2 in the submitted paper came from the OLD faulty
schedule files (2005/2015 weekday-weekend swapped; 2010 a copy of 2005 in places; wrong occupancy denominator).
The five REBUILT grid files are now the inputs (plan log (x)-(ad), (ap)). Reviewer comment 2 also asks whether
national data represent Quebec/Montreal: the audit (plan log (h)) found national data, no weights, so the
paper owes a Canada-vs-Quebec comparison (WP3). And the paper gives only 2 of the 4 matching-tier shares.

## Inputs (Speed; confirm each with `ls -l` on the login node first)
Grid files (header `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate`):
- 2005 `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv`
- 2010 `.../Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv`
- 2015 `.../Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv`
- 2022 `.../Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv`
- 2025 `/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv`
Matched-keys files (tier shares; F-1J-9: the grid's MATCH_TIER column is NOT the source):
`<Outputs_TAG>/.../<TAG>_Matched_Keys_sample25pct.csv` for the four census years (find exact paths with `ls`),
and the 2025 matcher keys output (see `impl/2026-09-19_WP9_stage1c_2025.md` for its path).
Existing plot code to reuse (read, copy, re-point; never edit in place): `eSim/eSim_occ_utils/plotting/`
(`generate_occupancy_metrics_table.py`, `plot_presence_evolution*.py`, `plot_activity_metabolic_comparison.py`,
`plot_default_class_v2.py`, `plot_hhsize_occupancy.py`, `plot_nontemporal_comparison.py`, `plot_temporal_comparison.py`,
`cross_cycle_plot_utils.py`). Figure numbers ↔ scripts: find which script made each paper figure from its output
PNG name (e.g. `Fig_4_1_4_HHSize_Occupancy.png` = Figure 14) and record the mapping under Decisions.

## Definitions (FIXED; they are the paper's own, from `generate_occupancy_metrics_table.py`)
- Hourly profile = mean `Occupancy_Schedule` by Hour, per Day_Type, over all household rows.
- Occupied hours (h/day) = sum of the 24 hourly means (the Default profile gives 16.39 h, the paper's "16.4").
- Daytime occupancy fraction = mean of hours 9-16 inclusive (09:00-17:00); daytime vacancy % = 100*(1 - that).
- Morning departure / evening return = the script's steepest-drop / steepest-rise hour (same windows).
- Mean occupancy (0-1) = mean over all 24 h; mean metabolic rate = mean `Metabolic_Rate` over rows with
  `Occupancy_Schedule` > 0 AND over all rows (print both; say which the old Figure 13 used).
- Default profile: the 24 values in `generate_occupancy_metrics_table.py` (DEFAULT_PROFILE_WEEKDAY, same weekend).
- Quebec subset = `PR == 24` (all cycles share the harmonised 6-value PR scheme, plan log (h)); Canada = all rows.

## What to compute (one sbatch job, 1 CPU, `--mem=32G`)
1. Per year (5) x Day_Type x region {Canada, Quebec}: the 24-hour profile, occupied hours, daytime fraction,
   departure/return hour, mean occupancy, mean metabolic rate, household count. -> `metrics_by_year_region.csv`,
   `profiles_by_year_region.csv`.
2. Quebec minus Canada, per year and day type, for occupied hours and daytime fraction; ALSO a 95 % bootstrap
   interval of that difference (resample households, 1,000 reps, seed 20260929). -> `quebec_vs_canada.csv`.
   (The decision rule "small -> one sentence; large -> re-run with Quebec" is the manager's, not yours.)
3. Per year: the same metrics by HHSIZE bucket (1,2,3,4,5+), Canada. -> `metrics_by_hhsize.csv`.
4. Matching-tier shares per year from the keys files: share of persons (and of weekday / weekend assignments if the
   keys file separates them) in Tier 1, 2, 3, 4 (and any other label, e.g. NaN, reported as is). -> `tier_shares.csv`.
   The paper currently says Tier 2 = 84.6 % and Tier 4 = 0.3 % for 2025 (weekday); print the new 2025 values beside them.
5. Figures: re-run the copied plot scripts on the rebuilt files to regenerate paper Figures 8, 11, 12, 13, 14, C1, C2
   (same style, same panel layout; only the input paths change). If a figure needs data the grid file lacks (e.g. the
   activity categories of Figure 12), find the rebuilt source file in the same `Outputs_TAG` folder, say which, and
   use it; if none exists, SKIP that figure and write why under Decisions (do not invent a source).
   PNG at 300 dpi -> `figs/`.
6. Old-vs-new table for the manager: each Section 4.1 number the paper states (lines 173, 179, 183, 189, 193, 199,
   203 of `1J_docs_occ/manuscript/1st_Occ_Journal.md`) beside its new value computed here, same definition.
   -> `old_vs_new_section41.md`.

## Seen failing first (required)
Locally, on a tiny synthetic grid (3 households, 2 provinces, both day types, all 24 hours): hand-compute occupied
hours, daytime fraction, Quebec-minus-Canada; the script must match; then break the synthetic file (swap Day_Type
labels) and show the check fails. Write both under Verified.
Also: the Default profile must give 16.39 occupied hours for the script to be trusted (the paper's 16.4).

## Rules
- Speed: `sbatch` only; login node allows only sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp/module load and single-file
  tail/head/grep/wc -l/cat. NO python, NO find, NO du, NO md5sum there. tcsh login shell. `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`.
  Every job: `-t 7-00:00:00 -A chachemv -p ps`. Python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (read only).
  Work folder `/speed-scratch/o_iseri/1J_rerun/wp13/` (create via `scp -r` of a local folder); logs in `/speed-scratch/o_iseri/1J_rerun/logs/`.
  At most 4 CPUs for this WP.
- Local: `py`, never `python`. Local folder `1J_docs_occ/IMP/impl/wp13/`. Never open a multi-MB CSV in context.
- Never edit pipeline code. Never write under `/speed-scratch/o_iseri/GSSCanada/`.
- Submit, write job id + log path under Ledger, stop. Do not wait. The manager reads the log and copies outputs back.

## Ledger
- Job **1401447** - `wp13.sh` (one job, 1 CPU, --mem=32G, -A chachemv -p ps -t 7-00:00:00) - submitted 2026-09-29, PENDING at submission, not polled.
  Steps inside (each prints `STEPn exit <code>`; the job continues past a failed step): 1 metrics, Quebec, HHSIZE, tiers; 2 Fig 8 + C2; 3 Fig C1; 4 Fig 11; 5 Fig 13; 6 Fig 14; 7 Fig 12 (slow: reads five 4.6-9 GB aggregated files + the 2.6 GB 2025 file); 8 old-vs-new table. Last line `JOB DONE`.
  Log: `/speed-scratch/o_iseri/1J_rerun/logs/wp13_1401447.out`.
  Outputs: `/speed-scratch/o_iseri/1J_rerun/wp13/out/` (`metrics_by_year_region.csv`, `profiles_by_year_region.csv`, `quebec_vs_canada.csv`, `metrics_by_hhsize.csv`, `tier_shares.csv`, `old_vs_new_section41.md`) and `.../out/figs/` (PNGs at 300 dpi, `fig13_summary.csv`, `activity_hours_by_year.csv`, `metabolic_hourly_by_year.csv`, `BEM_Presence_Evolution_v2.csv`).
  Scripts on Speed: `/speed-scratch/o_iseri/1J_rerun/wp13/` (uploaded by `scp -r`); local copy `1J_docs_occ/IMP/impl/wp13/`. Plot copies in `wp13/plot/` were built by `make_plot_copies.py`; the originals in `eSim/eSim_occ_utils/plotting/` are untouched.

## Verified
**Inputs (`ls -l` on the login node, 2026-09-29).** All five grid files exist. Headers read with `head -3`: 2005 to 2022 have `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate`; the 2025 grid is the same without `MATCH_TIER`. Sizes now: 2005 91,215,596 (Sep 19); 2010 102,305,892 (Sep 21); 2015 101,017,776 (Sep 19); 2022 118,411,103 (Sep 21); 2025 62,816,947 (Sep 19). **The 2010 and 2022 sizes differ from what WP9 recorded (102,507,148 and 118,809,877): those two grids were rebuilt on Sep 21, so the WP9 numbers for 2010 and 2022 are stale.** Keys files exist for all five years (2005 8,529,279 B; 2010 10,034,374; 2015 8,718,847; 2022 10,782,857; 2025 `Outputs_Aligned/Matched_Population_Keys.csv` 4,973,611). `head -3` on 2005, 2010 and 2025 shows `MATCH_TIER_WD` and `MATCH_TIER_WE`; 2015 and 2022 were not head-checked (the script warns if a column is absent).

**Seen failing first (local, `py check_synthetic.py`; 3 households, Quebec + Ontario, both day types, 24 h).** Hand values worked out on paper: Canada weekday 15.3333 h and daytime 0.3333; Quebec weekday 14 and 0; Canada weekend 14 and 0.58333; Quebec weekend 24 and 1; Quebec minus Canada weekday -1.3333 h and -0.3333, weekend +10 h and +0.41667; HHSIZE 5+ 12 h weekday, 6 h weekend. The script matched all 18 comparisons (including the bootstrap point estimate). After swapping the Day_Type labels in the file, all 18 comparisons failed and the check printed `check works (passes good, fails broken)`. Tier code tested on a 4-row fake keys file (an empty tier is reported as its own label `nan`; pooled counts add up). The Figure 13 runner on the synthetic file gave weekday mean 0.6389, daytime 33.33 %, night +20 %, all equal to hand values. All seven plot copies were smoke-run on the synthetic file and each wrote a PNG.

**Default profile gate.** The task doc says the Default gives 16.39 h. The script's own 24 values (`generate_occupancy_metrics_table.DEFAULT_PROFILE_WEEKDAY`, read with `py`) sum to **16.42**, which rounds to the paper's 16.4; 16.42/24 = 0.684 is the paper's mean occupancy and vacancy 74.4 % matches. The gate in `wp13_metrics.py` checks 16.4 / 0.684 / 74.4 instead of 16.39.

**Figure to script map.** Fig 8 = `plot_temporal_comparison.py` (BEM_Temporal_CrossCycle_Comparison.png); C2 = the same script's spaghetti PNG; C1 = `plot_nontemporal_comparison.py`; Fig 11 = `plot_presence_evolution_v2.py` (its 3-row by 5-column layout matches the paper image decoded from the manuscript, compared by eye, saved in `wp13/oldfigs/`); Fig 12 = `plot_activity_metabolic_comparison.py`; Fig 13 = `plot_default_class_v2.py`; Fig 14 = `plot_hhsize_occupancy.py`. Figs 8, C1, C2 are matched by caption and PNG name only.

No real result number has been read yet (the job has not run).

## Decisions
1. **Quebec is `PR == "Quebec"` (text), not 24.** Every grid file stores PR as a name (Ontario, Quebec, Prairies, Atlantic, BC), seen in each `head`. The job prints household counts per PR value per year, so Quebec being non-empty can be seen in the log.
2. **Default gives 16.42 h, not 16.39** (see Verified). The task doc number was wrong; nothing else changes.
3. **Two departure/return rules exist in the repo.** The task doc says steepest drop/rise (table script); the Figure 11 script uses the first hour below/above 0.5. The job writes both (`dep_steepest`, `ret_steepest`, `dep_cross50`, `ret_cross50`); -1 means no hour qualified.
4. **Metabolic mean.** Three versions are written: rows with Occupancy > 0, all rows, rows with Metabolic_Rate > 1. The old Figure 13 panel (b) line used ALL weekday rows by hour; the Figure 12 script uses Metabolic_Rate > 1. The old Figure 13 panel (e) value (72.7 W) was typed into the script with no recorded source (the paper text says 72.1). New Figure 13 uses the mean of the 24 hourly all-row weekday means; `fig13_summary.csv` lists the alternatives.
5. **Figure 13 panels (c) to (e) and two annotation percentages were hard-coded from the OLD files** (the `SUMMARY` dict, "+39%", "+60%"). Re-running the unchanged script would have redrawn stale numbers. `run_fig13.py` computes them from the rebuilt 2025 grid and sets them before the unchanged plotting code runs. The definitions are inferred (nothing documents them): night overestimate = Default mean of hours 1-5 / 2025 weekday mean of hours 1-5 - 1; midday = 95 W / 2025 weekday mean metabolic rate of hours 10-14 - 1, with the label saying Over or Under by sign. The manager should check these against the paper's intent.
6. **Fig 13 Default source.** `run_fig13.py` tries the pipeline loader (`eSim_bem_utils.idf_optimizer` from `/speed-scratch/o_iseri/1J_rerun/code`) and accepts it only if its weekday occupancy sums to 16.42; otherwise it uses the script's own 24-value constant. The log line `WP13 default source:` says which was used. Not tested on Speed.
7. **Fig 14.** The copied script draws one line per distinct HHSIZE; I clip HHSIZE at 5 (the 5-person line then means 5 or more) and print the HHSIZE distribution to the log. The old file's HHSIZE range is unknown.
8. **Fig 12 inputs.** The aggregated activity files exist in each `Outputs_TAG/HH_aggregation/*_Full_Aggregated_sample25pct.csv` (4.7 to 8.9 GB) and 2025 `Full_data.csv` (2.6 GB); dates (Sep 19 or Sep 21) precede each year's grid file, so they appear to come from the same rebuild. Contents not verified. The metabolic panels use the rebuilt GRID files.
9. **Tier shares.** Unit = persons (one keys row per person), reported separately for the weekday assignment and the weekend assignment, plus a pooled row. 2005 to 2022 keys use labels like `2_Core`, `3_Constraints`; the 2025 keys use `2_Drivers`, `4_FailSafe`. Reported as they are, an empty value as `nan`. The paper's 2025 "Tier 2 = 84.6 %, Tier 4 = 0.3 %" is printed beside the new 2025 weekday shares at the end of step 1. The manager should read the whole table, not only the digits.
10. **Bootstrap.** Resamples all households of a year with replacement (multinomial weights, 1,000 reps, seed 20260929, `numpy.random.default_rng`), recomputes Quebec and Canada profiles on the same resample, and reports the 2.5 and 97.5 percentiles of the Quebec-minus-Canada difference in occupied hours and in daytime fraction. The number of Quebec households varies per resample (natural design).
11. **`old_vs_new_section41.md`** has about 65 rows. Where the paper states a range, the Old column holds the range as text and every year's new value gets its own row. The "~58 pp" of line 179 has no stated definition; I used Default vacancy 74.4 minus the cycle's weekday vacancy and say so in the table.
12. One sbatch, 1 CPU; the job continues past a failed step, so check each `STEPn exit`.

## Next
Manager: read `/speed-scratch/o_iseri/1J_rerun/logs/wp13_1401447.out` (grep for `STEP`, `Traceback`, `FAIL`, `WP13 default source`, `PR values`, `2025 weekday tier shares NEW`, `JOB DONE`). If a step failed, spawn a fresh employee to fix only that step and re-run only that step (scripts are in `/speed-scratch/o_iseri/1J_rerun/wp13/`). Then `scp` `out/` back to `1J_docs_occ/IMP/impl/wp13/out/`, compare the seven PNGs with the old figures, and apply the Quebec-vs-Canada rule using `quebec_vs_canada.csv`. Read Decision 5 before quoting any Figure 13 number.

## WHAT I DID NOT VERIFY
- No real result was read; the job had not started. Nothing was checked on the real grid files beyond headers and sizes.
- That Quebec is present in every year (heads showed Ontario, Quebec, Prairies, Ontario, Atlantic for the five files; the job prints counts).
- That every household has 48 rows (the job prints rows per household and the count of incomplete households).
- That `idf_optimizer` imports on Speed (fallback in place), and that 2025 `Full_data.csv` has an `occActivity` or `occACT` column (the script handles both; if neither, the 2025 activity panel shows No Data and the log says so).
- That the 2015 and 2022 keys have both tier columns.
- The inferred definitions in Decision 5 and the source of the old 72.7 W.
- Runtime and memory (32 GB requested; the Fig 8 script holds all five grids in memory).
- Layouts of Figs 8, C1, C2, 12, 13, 14 against the old paper images (only Fig 11 was compared).
