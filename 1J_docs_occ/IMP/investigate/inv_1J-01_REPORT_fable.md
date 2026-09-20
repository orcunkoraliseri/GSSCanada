# inv_1J-01 REPORT (Fable): independent check of the EnergyPlus re-run plan

Written 2026-09-19 by a fresh Fable session. Read-only work; this is the only file written in the repo.
No EnergyPlus was run, no batch was started, the cluster was not touched. Schedule files were streamed
line by line, one at a time. Scratch scripts and their outputs (for re-running any number below):
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\856e80dc-6f97-4780-8200-6260c1b2f93f\scratchpad\`
(`scan.py` -> `scan_out.json`, `meta.py`, `dday.py`, `select.py` -> `select_out.json`).

Paths below are relative to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\` unless absolute.

---

## 1. Verdict on the plan

**STOP.** Two of the five input files (2005 and 2015) have the weekday and weekend labels swapped, two
(2005 and 2010) have night-time occupancy collapsed to 1/household-size, and two premises of the plan
(which batch made the submitted figures, and which batch had the 2010 copy) are wrong. Running the plan
as drafted would spend about 45 days of cluster time to reproduce numbers that are wrong for reasons the
plan's own checks cannot see.

The job mechanics (Part C items 3, 4, 7-day limit, 24 GB) are mostly sound and become GO WITH CHANGES
once the inputs are fixed.

**A better plan is proposed in section 6** (added at the author's request): fix the inputs first (hours
of compute, not weeks), choose the households before simulating, prove the staging on one short run,
then simulate in stages of 5 draws with a stopping rule. It reaches a first usable result in about 10
days at one CPU instead of 45, and every number in it can be reproduced.

---

## 2. Changes required before submission (most important first)

### R1. The 2005 and 2015 schedule files have Weekday and Weekend swapped. Do not run with them.

- The 2005 and 2015 alignment scripts rename the GSS variable `DVTDAY` to `DDAY`:
  `eSim/eSim_occ_utils/06CEN05GSS/06CEN05GSS_alignment.py:883` (`'DVTDAY': 'DDAY'`) and
  `eSim/eSim_occ_utils/16CEN15GSS/16CEN15GSS_alignment.py:58` (`'DVTDAY': 'DDAY'`).
- `DVTDAY` is a 3-code "type of day": 1 = Weekday, 2 = Saturday, 3 = Sunday
  (`0_Occupancy/DataSources_GSS/Main_files/GSSMain_2015.sps:1412-1415`; same coding in
  `GSSMain_2010_syntax.SPS:3867-3870`).
- The matcher then treats the column as a 7-code day of week: weekday = `isin([2,3,4,5,6])`, weekend =
  `isin([1,7])` (`06CEN05GSS_ProfileMatcher.py:101-106`, `16CEN15GSS_ProfileMatcher.py:101-106`).
  So code 1 (true weekday diaries) goes to the Weekend catalogue, and codes 2 and 3 (Saturday, Sunday)
  go to the Weekday catalogue.
- Measured in the aligned files (`dday.py`, distinct respondents per `DDAY` value):
  `Outputs_06CEN05GSS/alignment/Aligned_GSS_2005.csv`: 1 -> 9,539, 2 -> 1,915, 3 -> 2,065 (three codes
  only, 70.6 % in code 1); `Outputs_16CEN15GSS/alignment/Aligned_GSS_2015.csv`: 1 -> 10,750, 2 -> 2,181,
  3 -> 2,309. By contrast 2010 (`Aligned_GSS_2010.csv`) and 2022 (`Outputs_Aligned/Aligned_GSS_2022.csv`)
  carry seven codes with about 1/7 each. 2010 is safe because its script drops `DVTDAY` and keeps the
  episode file's real `DDAY` (`11CEN10GSS_alignment.py:261-264`); 2022 and 2025 use `DDAY`
  (`21CEN22GSS_alignment.py:33`).
- The swap is visible in the staged files (`scan_out.json`, mean occupancy 09:00-16:00): 2005 "Weekday"
  0.58-0.65 vs "Weekend" 0.36-0.44; 2015 "Weekday" 0.53-0.68 vs "Weekend" 0.35-0.42 (weekend emptier than
  weekday, which is backwards). 2010, 2022 and 2025 have the expected direction (2010 weekday 0.33-0.36
  vs weekend 0.48-0.56).
- Consequences: (a) the 2005 and 2015 energy scenarios apply weekend diaries on 5 days of 7;
  (b) household selection matches the "Weekday" profile to a working-day target
  (`integration.py:48-95`), so in 2005 and 2015 it is matching Saturday/Sunday diaries;
  (c) Section 4.1's "weekday occupied hours" for 2005 (15.5 h) and 2015 (17.5 h) are weekend values. With
  the labels corrected the four numbers would be about 13.67, 11.89, 15.33, 15.90 h
  (`scan_out.json`: `mean_hours_Weekend` 2005 = 13.665, 2015 = 15.3277). This also touches plan items P2
  and P3.
- What to do: fix the mapping in the two alignment scripts (map `DVTDAY` 1 -> a weekday code, 2 -> 7,
  3 -> 1, or branch on the three codes), regenerate 2005 and 2015 through ProfileMatcher ->
  HH_aggregation -> occToBEM, and re-derive Section 4.1. A label swap inside the two CSVs is a quick
  approximation only; it is not guaranteed identical to a regenerated file (the pipeline is not
  symmetric in the two day types, for example `06CEN05GSS_HH_aggregation.py:396-401`).

### R2. In 2005 and 2010 the night-time occupancy is 1/HHSIZE. The cycles are not comparable as built.

- The converter computes occupancy as `occPre * (occDensity + 1) / hh_size`
  (`06CEN05GSS_occToBEM.py:176-179`), where `occDensity` is the count of "who was with you" flags
  (`06CEN05GSS_HH_aggregation.py:152-162`, code 9 -> 0).
- In GSS 2005 and 2010 those flags are 9 (not asked) during sleep: first rows of
  `0_Occupancy/Outputs_GSS/out05EP_ACT_PRE_coPRE.csv` and `out10EP_ACT_PRE_coPRE.csv` show the 04:00
  sleep episode with `Alone..parents = 9`. In 2015 they are answered (`out15EP_...` first row: 2,2,...,1).
- Measured (`meta.py`, mean occupancy at 03:00 by household size, both day types):
  2005: 2-person 0.506, 3-person 0.340, 4-person 0.257; 2010: 0.493, 0.337, 0.257 (that is 1/HHSIZE).
  2015: 0.887, 0.772, 0.772; 2022: 0.799, 0.629, 0.606; 2025: 0.738, 0.529, 0.435.
- So in 2005 and 2010 a sleeping family counts as one person. This, together with R1, explains the
  "near-flat" 2005 profile (B4) and most of the "anomalously low 2010" value: 2010 has larger households
  in the file (mean HHSIZE 2.55 vs 1.93 in 2005, `scan_out.json`), so 1/HHSIZE pulls it lower.
- It reaches the energy result directly: the occupancy fraction scales the People object, so night-time
  internal gains in 2005 and 2010 are roughly half of what the same method gives for 2015 and 2022.
- What to do: a method ruling is needed before any re-run. The consistent option is to count present
  household members from the per-person presence grids (`_aggregate_household` already has
  `occupancy_count`, `06CEN05GSS_HH_aggregation.py:230-233`) instead of the social-contact count, in all
  five years. Related: Section 4.1's "occupied hours" is the sum of a fraction that is divided by
  household size, so it falls with household size by construction (reading copy
  `1J_docs_occ/manuscript/1st_Occ_Journal.md:203` presents this as a finding).

### R3. Two premises in Part A are wrong. The submitted figures come from the cluster 20-draw batch.

- The submitted Figure_Occ_A1 (`...\7ac8b9b9-...\scratchpad\docx_media\word\media\image15.png`, title
  "N=3") shows heating deltas RC1 2.32, RC2 1.96, RC3 0.98 for 2005 and 2010, and 3.49, 3.03, 1.59 for
  2015. Those are exactly the 20-draw batch: `BEM_Setup/SimResults/BatchAll_MC_N20_v2/NUS_RC{1,2,3}/
  aggregated_eui.csv` give 2.32, 1.96, 0.98 and 3.49, 3.03, 1.59 (scenario minus Default).
  The 3-draw pilot gives 1.80, 2.29, 1.02 and 2.95, 3.63, 1.42 (`BatchAll_MC_N3_1776120359/NUS_RC*/
  aggregated_eui.csv`), which matches the on-disk pilot figure
  `BatchAll_MC_N3_1776120359/interim_report/Figure_Occ_A1_EndUse_Delta.png`, not the submitted one.
  So the "N=3" in the submitted title is a wrong label; the data are N = 20, run on Speed.
- In the 3-draw pilot 2010 is NOT a copy of 2005: all six `aggregated_eui.csv` files differ between the
  2005 and 2010 columns (for example RC4 heating 157.6900 vs 157.7853). The pilot's own IDFs prove it
  read the real 2010 file with the Quebec filter: `NUS_RC1/iter_1/2010/Scenario_2010.idf` building 0
  carries the weekday profile of household 44940, which is the predicted best match for
  SingleD, 2 persons, in `11CEN10GSS_BEM_Schedules_sample25pct.csv` filtered to `PR == Quebec`
  (`select_out.json`, `pilot_check`). The same test places the pilot's 2005, 2015, 2022 and 2025
  households in the B1 files (112249, 55804, 61481, 47215).
- The 2010 = 2005 copy exists only in the 20-draw cluster batch (all six NUs identical to four decimals).
- Consequences: the response letter must say "20 draws, with the 2010 input a copy of 2005", not
  "3 draws"; and "the April cluster code is closest to the pilot" is the wrong argument (the right one is
  in Q3). When the local `BEM_Schedules_2010` became a copy of 2005 is NOT FOUND (Windows copies keep the
  source time stamp, so 14:30 on 04-02 says nothing).

### R4. The "Monte Carlo" does not draw households. Decide whether that is the method you want to defend.

- The random draw picks one 2005 household per building (`main.py:2133`) and keeps only its household
  size and dwelling type (`main.py:2140-2141`). Every year, including 2005, then receives
  `find_best_match_household`, which minimises squared error against the fixed
  `TARGET_WORKING_PROFILE`, not against the drawn household (`integration.py:48-95`, target at
  `:18-22`; call at `main.py:2202`).
- So for a given (dwelling type, household size) each year always gets the same household, then the
  second-ranked one for a second building of the same size (`used_hhs`, `main.py:2171-2204`). Verified on
  the pilot: `NUS_RC1` iter_1 and iter_3 contain identical households in all five years (both draws were
  sizes 2,2); only iter_2 (sizes 3,2) differs (`select_out.json`, `pilot_check`).
- The reported standard deviation is therefore the spread over household-size mixes only, and each year
  is represented by a handful of households chosen to look alike. With the Quebec 2005 SingleD pool
  (900 households: size 1 = 177, 2 = 555, 3 = 141, 4 = 24, 5 = 3) the chance that an RC1 draw is (2,2) is
  0.617 squared = 0.38, so about 8 of 20 RC1 draws will be bit-identical simulations. ESTIMATED from pool
  shares; assumes uniform `random.choice`.
- Ties are common and are broken by file order: 49 one-person SingleD households tie at the best score in
  2022. The weekend day is not part of the match at all (the 2022 best one-person household is home 24 h
  on weekends).
- What to do: either (a) keep the method, describe it honestly (deterministic best-match household per
  size and dwelling type; draws vary the size mix only), and drop "Monte Carlo ensemble of households";
  or (b) change the year step to a random draw among that year's households of the same size and
  dwelling type (a few lines at `main.py:2201-2204`), seeded. Option (b) is the only one for which N
  means what the paper says it means. This is a ruling for the author; it changes publishable results.

### R5. Job design fixes (Part C item 4)

- **Output folder name.** `batch_name = basename(batch_dir) + "_" + idf_stem` (`main.py:2003`). With
  `--output-dir <folder>/draw_{k}/NUS_RC{j}` that is `NUS_RC{j}_NUS_RC{j}` for every draw, and results
  land in `<folder>/draw_{k}/NUS_RC{j}/NUS_RC{j}/`. The schedule exports
  (`SimResults_Schedules/<batch_name>/...`, `integration.py:292-296`; called at `main.py:2222-2231`), the
  schedule plots (`integration.py:1940-1943`) and the two result plots (`main.py:2313`, `:2346`) are
  written under the staging folder's `BEM_Setup/` with that name, so every draw overwrites the last
  one's record of which households were used. Use `--output-dir <folder>/draw_{k}` so the name becomes
  `draw_{k}_NUS_RC{j}`.
- **Drop `--use-tmpdir`.** With it only `.sql` and `.csv` are copied back and the run folder is deleted
  (`simulation.py:104-106`), so `eplusout.err`, `eplusout.end` and `eplustbl.htm` are lost. With one task
  at a time there is no write pressure to avoid, and the `.err`/`.end` files are the only measured
  run time and error count you will get. It also makes C6's "or `eplustbl.htm`" untestable.
- **`--sim-mode` does nothing here.** `_run_mc_neighbourhood` never passes it to the IDF builders
  (`main.py:2051`, `:2212-2217`; defaults `run_period_mode='standard'` at `integration.py:1716`, `:2044`);
  it only reaches the time-series plot (`main.py:2350`). So the April cluster batch was also a full-year
  run, whatever `submit_array_tuned.sh` passed, and B8's "different method" is not supported by the
  code. Passing `standard` is harmless and correct.
- **Seed and record.** Nothing is seeded (`main.py:1996`, `:2133`). Add `random.seed(base_seed + draw)`
  from a new `--seed` argument in `run_batch_hpc.py` and print the drawn household IDs, sizes and the
  per-year matched IDs to the task log. Without this no draw can be reproduced for a reviewer.
- **Staging.** `BEM_SETUP_DIR` is derived from the code location (`main.py:33-34`), so the "own folder"
  must hold its own copy of the code plus `BEM_Setup/Neighbourhoods`, `BEM_Setup/WeatherFile` and the
  five CSVs. The 2022 file has 13 columns (it carries `MATCH_TIER`), not 12 as B1 says; the loader reads
  by column name, so this is harmless.
- **Time.** See Q7: about 45 days at one CPU, of which about 8 days are repeated Default runs.

### R6. The `PR` column is not the household's province, and `--region Quebec` filters on it row by row

- In the four survey-based files the Weekday and Weekend rows of one household carry different `PR` in
  about half of all households: 2005 17,415 of 28,455; 2010 15,649 of 32,480; 2015 19,774 of 31,163;
  2022 17,793 of 36,909; 2025 0 of 23,882 (`meta.py`). `DTYPE` and `HHSIZE` are consistent (except 17
  households in 2015 and 2 in 2025 that carry two dwelling types).
- The loader drops rows one by one (`integration.py:367-371`), and ranking requires both day types
  (`integration.py:116-121`), so the "Quebec" pool is "households whose weekday and weekend rows both say
  Quebec". For the three needed dwelling types that leaves 2,796 (2005), 3,538 (2010), 2,967 (2015),
  3,722 (2022) and 5,605 (2025) households after the sanity filter (`select_out.json`).
- Where the two `PR` values come from (census household vs diary donor) is NOT VERIFIED; it must be
  traced before the paper says anything about a Quebec pool.

### R7. Default differs between the local pilot and the cluster batch by up to 4 %

- Default, RC6: heating 157.568 (pilot) vs 150.780 (cluster), cooling 24.602 vs 26.221. RC4: 156.532 vs
  156.414. Same code path, no households involved. Cause NOT FOUND (neighbourhood IDF version, weather
  file, or EnergyPlus build). This gap is 100 times the year-to-year differences for RC6 (about 0.04),
  so it must be explained before new results are compared with the submitted figures. Compare md5 of
  `NUS_RC6.idf` and the `.epw`, and the EnergyPlus version line in an old cluster `eplusout.err`.

---

## 3. Questions Q1 to Q9

### Q1. Inputs. DISAGREE (the files are the right lineage, but two of them are wrong inside)

- Lineage is confirmed. md5: 2005 `57fd2732...` = `Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_
  sample25pct.csv`; 2015 `2bd251db...` = the `16CEN15GSS` output; 2010 real file `e5ba8068...`;
  `BEM_Schedules_2010_PRE_STEP8_BAK.csv` = `57fd2732...` (the copy). All from `scan_out.json`.
- **2015 households (CHECK): 31,163.** Others confirmed: 28,455 / 32,480 / 36,909 / 23,882.
- 2010 is a true sibling in format and timing (same 12 columns, all three written 2026-04-02 between
  14:30 and 16:18, same `sample25pct`). It is NOT a sibling in content: 2010 keeps the real day of week
  while 2005 and 2015 use the 3-code `DVTDAY` (R1), and the 2010 script has an extra `11CEN10GSS_step0.py`
  stage. The converter on disk today writes a `MATCH_TIER` column (`06CEN05GSS_occToBEM.py:199`) that the
  April 2005/2010/2015 outputs do not have, so the April converter version is no longer on disk.
- 2022: `BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` has the same md5 (`34a1f8fa...`) as
  `Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct.csv` (dated 04-23), so a re-run of the
  converter reproduced it byte for byte.
- Proof of what the pilot read, stronger than time stamps: the occupancy schedules inside the pilot's
  `Scenario_{year}.idf` files match the predicted best-match households of exactly these five files
  under the Quebec filter (R3). For the 20-draw cluster batch the equivalent proof needs the cluster's
  `iter_*/*/Scenario_*.idf`, which I did not have.

### Q2. Clock. AGREE on the clock, DISAGREE that the flat 2005 profile is a data property

- All five files are on the real clock. The grid is built from HHMM start and end times as clock minutes
  with midnight wrap (`06CEN05GSS_HH_aggregation.py:165-196`) and the hour comes from `Time_Slot`
  (`06CEN05GSS_occToBEM.py:114`, `:196`). No hour is outside 0-23 and every household has 24 rows per day
  type in all five files (`scan_out.json`).
- The flat 2005 weekday profile is two bugs, not behaviour: the day-type swap (R1) and the 1/HHSIZE
  night (R2). My B4 re-measurement matches the manager's numbers to two decimals for 2005, 2010, 2022
  and 2025.

### Q3. Code. DISAGREE with B5's description; AGREE with using the cluster copy

- B5's "thousands of lines" is a line-ending artefact. `diff --strip-trailing-cr` between the cluster
  copy and `eSim/eSim_bem_utils/` gives 0 changed lines for `main.py`, `simulation.py` and
  `neighbourhood.py`, and 203 for `integration.py`.
- All 203 lines sit in the `Schedule:File` path: `write_8760_schedule_csv` holidays and design days
  (`integration.py:447-540`), `inject_setpoint_schedules(use_schedule_file=...)` (`:1106-1260`) and
  `inject_schedules` (`:1263-1700`). `main.py` contains no `use_schedule_file` at all, and the batch path
  calls `inject_neighbourhood_schedules` and `inject_neighbourhood_default_schedules`, which have no such
  option. So for this batch the two versions build the same IDFs. There is no "later fixes" limitation
  to list for this path.
- Use the cluster copy anyway: it is the code that made the submitted figures (R3). Not compared by me:
  `idf_optimizer.py`, `schedule_generator.py`, `plotting.py`, `config.py` on the cluster. Compare their
  md5 in an `sbatch` job before launch.
- The 2026-04-13 pilot code is NOT FOUND and is no longer needed. The oldest trace is
  `eSim/eSim_bem_utils/__pycache__/integration.cpython-313.pyc` dated 2026-05-19 (81,876 bytes); an
  identical-size copy is in `1J_docs_occ/conference_eSim/eSim/eSim_bem_utils/__pycache__/`. No `.bak`
  of `main.py` or `integration.py` exists under `C:\Users\o_iseri\Desktop\GSSCanada` to depth 7.

### Q4. Separate tasks vs one run. DISAGREE with the premise; the statistics do not change

- `used_base_k` is created inside the draw loop (`main.py:2123`, loop at `:2118`), so it never stopped a
  household being drawn in two draws. B6 is wrong on this. One 20-draw run and twenty 1-draw tasks are
  the same experiment: independent, unseeded draws.
- `scored` is every household of that dwelling type in the 2005 file (after the region filter and the
  sanity filter) ranked by squared error to the working profile; the pool is the better half
  (`main.py:2110-2114`). With `--region Quebec` (`select_out.json`): SingleD 1,800 scored, pool 900;
  MidRise 842, pool 421; HighRise 154, pool 77. Without the filter: 7,807 / 2,549 / 1,237.
- Repeats of the drawn ID do not matter, because only its size and dwelling type are used (R4). What
  repeats is the size mix: about 38 % of RC1 draws are (2,2) (ESTIMATED, see R4).
- Yes, add a seed and a draw index: `--seed` in `run_batch_hpc.py`, `random.seed(seed + draw_index)`
  before the loop at `main.py:2118`, and print base IDs, sizes and matched IDs per year. About ten lines.

### Q5. Region. `--region Quebec` DOES restrict the household pool

- `main.py:2027`: `integration.load_schedules(csv_path, dwelling_type=selected_dtype, region=selected_region)`.
- `integration.py:367-371`: `if region: row_region = row.get('PR', ''); if row_region and row_region != region: skipped_count += 1; continue`.
- It also picks the weather file (`run_batch_hpc.py:90`). See R6 for what `PR` actually means.
- The submitted text names no province for the pool. The reading copy (`1st_Occ_Journal.md:163`) says
  only "single-detached households with 2 to 4 persons, matched to a target working-day occupancy
  profile through Sum of Squared Error minimization, with the 100 best-matching households". "Quebec"
  in a pool sense: NOT FOUND.

### Q6. N. NOT FOUND for a defensible N; N = 20 is not the binding problem

- Per-draw results are not on disk locally (both `_sql_cache` folders are empty; only mean and std
  survive), so a paired spread cannot be computed here. It can on Speed, from the April batch's
  `iter_1..iter_20` folders.
- Unpaired, from `BatchAll_MC_N20_v2`: RC1 heating std 1.14 kWh/m2. 2005 vs 2015 differ by 1.17, about
  3.2 standard errors at N = 20 (ESTIMATED, assumes independent draws); 2005 vs 2022 differ by 0.12 and
  would need about 690 draws unpaired. For RC4 to RC6 the year differences are 0.02 to 0.3 on about 158
  (0.01 to 0.2 %), smaller than the unexplained Default gap in R7.
- Use the paired comparison (per-draw difference between years, then mean and interval). One task per
  draw helps here: each task's `aggregated_eui.csv` holds that draw's single values, so per-draw data
  survive. But under the present method the paired difference is a fixed function of the size mix, so
  its interval describes size-mix variation, not household variation (R4). Settle R4 first; then fix N
  from the first 5 draws' paired spread with a stopping rule written down beforehand.

### Q7. Resources. AGREE on 24 GB and 7 days; the total time is the issue

- Memory: MEASURED nowhere for a single run. ESTIMATED: 58 GB for 5 parallel RC6 runs (B7, not
  re-checked) is about 12 GB each, so 24 GB has a factor of two. Python holds only the Quebec rows of five
  files, which is small.
- One task = 6 sequential simulations (Default + 5 years). Pilot single-run Default times (prep doc Q1,
  from file time stamps): RC2 76, RC3 59, RC4 91, RC5 176, RC6 136 min; RC1 about 30 (ESTIMATED). Worst
  task RC5 is about 6 x 176 min = 18 h. ASSUMES a cluster core is no slower than the local one and a year
  run costs about the same as Default. The 7-day limit is safe by a wide margin.
- Whole campaign at throttle 1: 6 x (30+76+59+91+176+136) min = 57 h per draw, about 47 days for 20
  draws. Cross-check from B7: 30 h x 5 CPUs per neighbourhood for 101 runs is about 1.5 CPU-h per run,
  which gives 720 runs x 1.5 h = 45 days. About one sixth (8 days) is repeated Default runs. Better: six
  separate Default tasks first, and skip Default in the draw tasks (needs a small flag), or accept the
  cost knowingly.

### Q8. Checks. DISAGREE that C6 is sufficient

- Five different md5: catches the copy (seen failing on the old pair). Does not catch R1 or R2.
- Reproduce the four B2 weekday hours: this check PASSES on the swapped files. It certifies the bug. Drop
  it or turn it into a regression value after the fix.
- Default identical across tasks: catches code or input drift between tasks. Does not catch a wrong
  weather file or IDF common to all tasks (R7).
- All five year outputs present: fine, but test for `eplusout.sql` plus "EnergyPlus Completed
  Successfully" in `eplusout.end` (needs R5, no `--use-tmpdir`).
- Slips past all four: the day-type swap, the 1/HHSIZE night, the meaning of `PR`, overwritten household
  records, and draws that are identical simulations.
- Three more checks:
  1. **Day-type direction.** In every staged file, mean occupancy 09:00-16:00 on Weekday must be lower
     than on Weekend. Seen failing now on 2005 (0.59 vs 0.41) and 2015 (0.58 vs 0.37); passes on 2010,
     2022, 2025.
  2. **Night presence.** Mean occupancy at 03:00 for 2-person households must be at least 0.70. Seen
     failing now on 2005 (0.506) and 2010 (0.493); passes on 2015 (0.887), 2022 (0.799), 2025 (0.738).
  3. **Default against the April cluster batch.** Each neighbourhood's Default heating and cooling must
     match `BatchAll_MC_N20_v2` within 0.1 %. Seen failing on the local pilot's RC6 (157.568 vs 150.780).
     Optional fourth: count distinct size mixes per neighbourhood across draws; the pilot fails it
     (2 distinct in 3 draws for RC1).

### Q9. Anything else

- Household size is capped at 5 in the 2022 and 2025 files and at 6 in 2005, 2010, 2015
  (`scan_out.json`, `dtype_hhsize`). A drawn size-6 household finds no same-size match in 2022/2025 and
  falls back to "any size" (`main.py:2182-2188`).
- 17 households in the 2015 file and 2 in the 2025 file carry two dwelling-type labels (`meta.py`).
- Default is the DOE MidRise apartment schedule applied to every building (`integration.py:2038-2052`
  docstring), and EUI is per conditioned floor area from the tabular report (`plotting.py:262-288`).
  These match the submitted figures only if R7 is resolved.
- The sanity filter removes many households before ranking (`integration.py:219-266`); in the unfiltered
  2005 file 23,632 -> 23,186 for the three dwelling types. It is not mentioned in the paper.
- B1's "2025 file not given md5" is answered in C1. The 2025 file has consistent `PR` and the correct day
  direction, but its night presence (0.74 for two persons) is lower than 2022's (0.80), worth a look
  when R2 is fixed.

---

## 4. Control items

- **C1.** md5 of `BEM_Setup/BEM_Schedules_2025.csv`, first 8 hex: **3e34561b** (full
  `3e34561bb96f2cdd0107ea5bdef1432e`).
- **C2.** Mean `HHSIZE` over distinct `SIM_HH_ID` in that file: **2.36** (2.3551 over 23,882 households).
- **C3.** Weekend hour with the highest mean `Occupancy_Schedule` in
  `BEM_Setup/BEM_Schedules_2015_PRE_STEP8_BAK.csv`: **hour 3** (0.8585; hour 2 is 0.8578). Note that,
  because of R1, this file's "Weekend" rows are weekday diaries.

---

## 5. What I did not verify

- Nothing on the cluster: the cluster `BEM_Schedules_*.csv`, `submit_array_tuned.sh`, the 58 GB comment,
  the 30 h per neighbourhood, and the cluster copies of `idf_optimizer.py`, `schedule_generator.py`,
  `plotting.py`, `config.py`. B7 and B9 are taken from the prompt.
- The 2005 GSS codebook for `DVTDAY` is not on disk; the 2005 swap rests on the 2010 and 2015 syntax
  files plus the 70/15/15 split of the three codes in `Aligned_GSS_2005.csv`.
- Whether a plain label swap of the 2005 and 2015 files equals a regenerated file. Not tested.
- Where the two `PR` values per household come from (R6), and why Default differs between the pilot and
  the cluster batch (R7).
- Only Figure_Occ_A1 of the submitted images was compared with the two batches; the other energy
  figures were not.
- The pilot household check covered `NUS_RC1` and `NUS_RC4`, all three draws, all five years; RC2, RC3,
  RC5 and RC6 were not checked. My offline replay reimplements the ranking and sanity filter; it matched
  the pilot's first-ranked household in every tested case, but it is a replica, not the code itself.
- The 8-draws-in-20 figure and all times and memory in Q7 are estimates with the stated assumptions.
- I did not read `2026-09-19_WP2_data_audit.md`, and I read the plan only at section 3 and section 7.

---

## 6. Proposed alternative plan (added 2026-09-19 at the author's request)

The idea: spend the cheap hours first and the expensive weeks last. The draft plan puts 45 days of
simulation behind inputs nobody has tested. This plan puts gates in front of the simulation, each
costing minutes to hours, and then simulates in stages so a usable result exists early.

What is kept from the draft plan: Speed only, `sbatch` only, 7-day limit, one CPU with array throttle 1
(raised later with `scontrol update ArrayTaskThrottle`), 24 GB, full-year run, own staging folder, one
task per neighbourhood per draw, draw-major order, the April cluster code as the base.

### Stage 0. Two rulings by the author (no compute)

- **Ruling A, how occupancy is counted (R2).** Recommended: occupancy fraction = household members
  present / household size, from the per-person presence grids, in all five years. The count already
  exists in the aggregation step and is thrown away (`06CEN05GSS_HH_aggregation.py:232-233` keeps only
  "at least one present"); save it as a new column and use it in the converter instead of
  `occDensity + 1` (`06CEN05GSS_occToBEM.py:176`). TO CHECK before ruling: whether every household
  member has a diary (the GSS has no diaries for children under 15); if not, say so in the paper and
  treat them the same way in every year.
- **Ruling B, what a draw is (R4).** Recommended: a draw fixes, per building, a stratum (dwelling type,
  household size); each year then gets a **random** household from that stratum, seeded. The same strata
  in all five years keep the comparison paired on composition, which is what the paper says it wants
  ("isolates behavioral evolution effects"). If the paper wants working households only, keep the
  "better half by working-day score" filter, but apply it inside every year's stratum and say so. The
  cheaper fallback is to keep today's deterministic best match and describe it honestly; then N should
  be small (5 to 10), because extra draws only repeat size mixes.
- Both rulings change publishable results. Neither needs EnergyPlus to evaluate: Stage 2 shows their
  effect on the chosen households in seconds.

### Stage 1. Fix and rebuild the five input files (about 3 CPU-hours, one `sbatch` job)

1. Fix the day-type mapping in `06CEN05GSS_alignment.py:883` and `16CEN15GSS_alignment.py:58` (R1).
2. Apply Ruling A in the aggregation and converter steps of all cycles. The 2025 path lives under
   `25CEN22GSS_classification/`, next to three files that must not be modified; its occ-to-BEM step
   (`run_step3.py`) is a separate file, but the author should confirm before it is touched.
3. Rebuild all five files in the staging folder, never over the April files. Measured cost: the 2005
   chain from alignment to BEM file took 32 minutes locally on 2026-04-02 (file time stamps 13:58:53 to
   14:30:41), so five cycles are about 3 hours. ESTIMATED for Speed.
4. **Gate 1 (each part seen failing today, see Q8):** five different md5; weekday daytime occupancy
   below weekend in every file (fails now on 2005, 2015); 2-person occupancy at 03:00 at least 0.70 in
   every file (fails now on 2005, 2010); `PR` identical on a household's weekday and weekend rows, or
   the difference explained (fails now on four files, R6); 24 rows per household per day type.
5. Recompute Section 4.1 from the rebuilt files. This is needed for the revision whatever happens to the
   energy section, and it is where P2 and P3 get their real answer.

### Stage 2. Choose the households before simulating (seconds, one `sbatch` job)

- Add a dry-run switch to `_run_mc_neighbourhood`: do everything up to the job list, skip EnergyPlus,
  and write a **draw manifest** CSV: seed, draw, neighbourhood, building, stratum, year, household ID,
  weekday hours, weekend hours. The simulation tasks later read their households from this manifest.
- Why: the sample becomes a reviewable, reproducible object that exists before any CPU-week is spent.
  Draws can be added later (21 to 40) without disturbing draws 1 to 20. A reviewer can be given it.
- **Gate 2:** every (year, building, draw) filled from the right stratum with no fallback used; no
  household used twice within a draw; the number of distinct household sets per neighbourhood reported
  (seen failing on the pilot: 2 distinct in 3 draws for RC1); the manifest's mean weekday hours per year
  sit inside that year's pool distribution, so the sample is not an accident of ranking.

### Stage 3. Prove the staging on one short run (about 3 CPU-hours)

- In the staging folder, with the **April** inputs and the **April** method, run RC1 only (the shortest,
  about 30 to 60 minutes per run): Default plus the 2022 and 2025 scenarios for the (2,2) size mix.
- **Gate 3:** RC1 Default heating and cooling reproduce the April cluster batch (35.117 and 45.612,
  `BatchAll_MC_N20_v2/NUS_RC1/aggregated_eui.csv`) within 0.1 %. Seen failing on the local pilot
  (35.158 and 45.448). If it fails on Speed, the IDF, weather file or EnergyPlus build differs from
  April (R7), and nothing else should be launched until that is found.
- Keep `eplusout.err` and `eplusout.end` (no `--use-tmpdir`): this run gives the first measured time
  and, with `sacct --format=MaxRSS`, the first measured memory for one run. Replace the Q7 estimates
  with them, then repeat the measurement once on RC6 before trusting 24 GB.

### Stage 4. Simulate in blocks of 5 draws, with the stopping rule written first

- Six Default tasks first, one per neighbourhood, run once (about 9.5 h in total, ESTIMATED). The draw
  tasks skip Default. This removes the 8 days of repeated Default runs; the repeat check it gave is
  replaced by Gate 3.
- Block 1: draws 1 to 5, all six neighbourhoods, five years: 150 runs, about 47 h per draw, so about 10
  days at one CPU (ESTIMATED from the pilot's single-run times; Stage 3 replaces this with a measured
  figure). Use `--output-dir <folder>/draw_{k}` (R5).
- After each block, per neighbourhood and end use: the mean paired difference between years (same draw)
  and its 95 % interval.
- **Stopping rule, fixed before Block 1 is read:** a neighbourhood stops when the interval half-width
  for heating, 2005 vs 2022, is below 0.5 % of that neighbourhood's Default heating, or at 30 draws,
  whichever comes first. The author may choose another contrast or width, but must write it down before
  looking. Expect the apartment neighbourhoods (RC4 to RC6) to stop after Block 1: their year effects in
  the April batch were 0.01 to 0.2 %. The remaining CPU time then goes to RC1 to RC3, where the effect
  was 1 to 3 %.
- **Gate 4, per block:** every task ended with "EnergyPlus Completed Successfully" and zero severe
  errors in `eplusout.err`; the households in each `Scenario_{year}.idf` equal the manifest's (the same
  profile test used on the pilot in R3); each task's single-draw `aggregated_eui.csv` is collected into
  one long table (draw, neighbourhood, year, end use, value), the only file the figures may be built
  from.

### Stage 5. Reporting rules that follow from this design

- Figure titles take N from the long table, never from a typed string (the submitted "N=3" was wrong).
- The text states: the pool filter actually used (region, dwelling type, sanity filter), the stratified
  paired draw, the seed, N per neighbourhood and the stopping rule.
- A year difference is called a difference only if its paired interval excludes zero. For RC4 to RC6 the
  honest sentence is likely "no measurable effect of the occupancy cycle on annual heating".
- The response letter discloses three things plainly: the 2010 input was a copy of 2005 in the submitted
  energy results; 2005 and 2015 had the two day types exchanged; the figures showed 20 draws, not 3 and
  not 100.

### Optional, the author's call

- Reviewer comment 4 asks for the simulation to carry less weight. Three neighbourhoods, one per
  dwelling type (RC3 with 14 detached houses, RC4 mid-rise, RC6 high-rise), would say the same thing at
  roughly half the cost. RC1 and RC2 have two buildings each, so they are the noisiest and the least
  informative per CPU-hour.

### Cost and order at a glance (one CPU; all times ESTIMATED until Stage 3 measures them)

| Stage | What | Compute | What it protects against |
|---|---|---|---|
| 0 | Two rulings | none | simulating a method nobody chose |
| 1 | Rebuild inputs, Gate 1, redo Section 4.1 | about 3 h | inputs assumed instead of tested |
| 2 | Draw manifest, Gate 2 | seconds | paying for a sample nobody has seen |
| 3 | RC1 staging run, Gate 3, measured time and memory | about 3 h | a platform that does not reproduce April |
| 4 | Default x 6, then blocks of 5 draws, Gate 4 | 9.5 h, then about 10 days per block | an N that was guessed |
| 5 | Reporting rules | none | text that does not match what was run |

First usable energy result: about 11 days after Stage 0 is ruled, against about 45 days for the draft
plan, and with inputs that pass checks the draft plan's inputs fail today.
