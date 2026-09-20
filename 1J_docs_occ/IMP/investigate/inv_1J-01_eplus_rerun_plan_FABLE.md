# inv_1J-01: independent check of the EnergyPlus re-run plan (for Fable)

Written 2026-09-19 by the 1J manager session. Paste this whole file into a fresh Fable session opened in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`. It carries all the context you need; you do not need
any earlier conversation.

**Your job:** try to break the re-run plan in Part C before any simulation starts. You are a reviewer, not
an executor. For every item, check it against the files on disk and give a verdict. Where the plan is
wrong, say what to do instead. The author will not start the simulations until your report is vetted.

**Write exactly one file:** `1J_docs_occ/IMP/investigate/inv_1J-01_REPORT_fable.md`. Change, move or
delete nothing else. Do not write into `00_REVISION_PLAN.md` or any impl doc (an earlier outside session
did that, and it had to be corrected).

---

## Part A. The paper and why a re-run is needed

- **Paper:** *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials*, Journal of
  Building Performance Simulation, manuscript 266775447. Rejected in its current form; resubmission after
  major revision invited, deadline 2027-09-19.
- **What it does:** GSS time-use cycles 2005, 2010, 2015 and 2022 are matched to Census PUMF 2006, 2011,
  2016 and 2021 to build household occupancy schedules; a C-VAE projects a 2025 cohort. EnergyPlus then
  runs six Montreal neighbourhood units (`NUS_RC1` to `NUS_RC6`, climate zone 6A) with households drawn
  from each year's schedules. Section 4.1 reports occupancy; Section 4.2 reports the energy results
  (Figure 15 and related panels).
- **Submitted text:** `1J_docs_occ/IMP/86e336cb-ac8c-4230-946f-20ff060f5bc4.pdf` (PDF page N = manuscript
  page N-1). Editable copy: `1J_docs_occ/manuscript/submission_Occ_NUsJournal.docx`. Reading copy:
  `1J_docs_occ/manuscript/1st_Occ_Journal.md`.
- **Working plan (read section 3 P1 to P15 and section 7, entries (h) to (l)):**
  `1J_docs_occ/IMP/00_REVISION_PLAN.md`.

**What we found (plan log (j) and (l)):**

1. **2010 energy = 2005 energy.** In every energy result, the 2010 scenario is an exact copy of 2005. The
   cause: `BEM_Setup/BEM_Schedules_2010_PRE_STEP8_BAK.csv` is a byte copy of
   `BEM_Setup/BEM_Schedules_2005_PRE_STEP8_BAK.csv` (same md5, same size, same 14:30 time stamp on
   2026-04-02). The copy is visible in the submitted figures.
2. **The energy figures come from a 3-draw pilot**, not the "100 households per pairing" the text states.
   The submitted figure titles say "N=3". The pilot is
   `BEM_Setup/SimResults/BatchAll_MC_N3_1776120359/` (run locally, 2026-04-13; its `batch_log.txt` shows
   the six neighbourhoods run one after another, about 51 hours in total).
3. **The paper's text describes a filter the code does not have** ("single-detached, 2 to 4 persons").
   Households are drawn per building, from a pool of the building's own dwelling type.
4. **Section 4.2 must therefore be re-run** with a correct 2010 input and a stated number of draws. The
   author approved the re-run on the Speed cluster.

**Earlier implementation notes you may read (they are state files, not truth; check what matters):**
- `1J_docs_occ/IMP/impl/2026-09-19_WP2_data_audit.md` (data audit)
- `1J_docs_occ/IMP/impl/2026-09-19_WP2b_find_simulations.md` (search for the runs, plus "Manager vetting")
- `1J_docs_occ/IMP/impl/2026-09-19_WP9_eplus_rerun_prep.md` (re-run prep: timings, dwelling types, the June
  files, the 2010 file, seeding, launch command). Its Q3 statement that Section 4.1 does not match any
  file is out of date: it read the June files. See Part B.

---

## Part B. Facts the manager measured (re-check the ones marked CHECK)

**B1. Candidate input files (the "April set").**

| Year | File | Households | md5 (first 8) |
|---|---|---|---|
| 2005 | `BEM_Setup/BEM_Schedules_2005_PRE_STEP8_BAK.csv` = `0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct.csv` | 28,455 | 57fd2732 |
| 2010 | `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv` (the real 2010 converter output) | 32,480 | e5ba8068 |
| 2015 | `BEM_Setup/BEM_Schedules_2015_PRE_STEP8_BAK.csv` = `0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct.csv` | (CHECK: report it) | 2bd251db |
| 2022 | `BEM_Setup/BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` (local time stamp 2026-04-10) | 36,909 | 34a1f8fa |
| 2025 | `BEM_Setup/BEM_Schedules_2025.csv` (local time stamp 2026-04-08) | 23,882 | (not given; see control C1) |

The files have 12 columns: `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,
Occupancy_Schedule,Metabolic_Rate`, with 24 rows per household per `Day_Type` (Weekday, Weekend).
The 2022 file uses a different dwelling-type label set (`OtherDwelling` and a bare `8`), but the six
neighbourhoods only need `SingleD` (RC1 to RC3), `MidRise` (RC4, RC5) and `HighRise` (RC6), which exist in
all five files.

**B2. Section 4.1 is reproduced by these files.** Mean over households of the summed hourly
`Occupancy_Schedule` on **weekdays**: 2005 15.48 h, 2010 (real file) 11.89 h, 2015 17.55 h, 2022 15.90 h;
2025 gives 12.63 h. The paper's Section 4.1 says 15.5, 11.9, 17.5 and 15.9 h. Weekend and 5/2-mixed means
do not match. So the occupancy section used the right 2010 file; only the energy runs used the copy.
(CHECK one year yourself, streamed.)

**B3. The "June set" is a different lineage and is not used.** `BEM_Setup/BEM_Schedules_2005.csv`,
`_2010.csv`, `_2015.csv` (13 columns, adds `MATCH_TIER`, 144,507 households each, written 2026-06-08 after
submission) were built for another paper (2J) and then relabelled by
`2J_docs_occ_nTemp/Step9_docs/investigation/fix_old_years_clock.py`, which shifts `Hour` by +4 to fix a
"4-hour-early" clock bug in that lineage. Their weekday hours (about 16.3 to 16.9) do not reproduce the
paper.

**B4. Clock of the April set.** The April converter builds its hour from the diary `Time_Slot` parsed as
clock time (`eSim/eSim_occ_utils/06CEN05GSS/06CEN05GSS_occToBEM.py:114` and `:196`). Weekday hourly means
(hour 0 to 23) measured by the manager:
- 2005: 0.62 0.61 0.61 0.61 0.61 0.60 0.62 0.64 0.68 0.65 0.58 0.57 0.59 0.58 0.59 0.61 0.63 0.70 0.73 0.72 0.75 0.76 0.73 0.67
- 2010: 0.52 0.52 0.52 0.52 0.53 0.52 0.53 0.53 0.42 0.36 0.33 0.33 0.36 0.33 0.33 0.34 0.44 0.58 0.67 0.66 0.69 0.69 0.62 0.54
- 2022: 0.79 0.80 0.80 0.80 0.85 0.83 0.76 0.69 0.59 0.54 0.49 0.48 0.45 0.42 0.42 0.45 0.52 0.62 0.74 0.75 0.76 0.78 0.77 0.78
- 2025: 0.69 0.70 0.70 0.70 0.76 0.73 0.66 0.54 0.41 0.34 0.30 0.29 0.28 0.27 0.27 0.30 0.37 0.50 0.58 0.61 0.64 0.66 0.66 0.68
- June 2005 (after the +4 fix, for comparison): 0.95 0.96 0.97 0.97 0.96 0.93 0.85 0.69 0.51 0.44 0.40 0.39 0.40 0.37 0.37 0.41 0.51 0.64 0.70 0.72 0.78 0.84 0.89 0.93

The manager's reading: the April files are on the real clock (the 4 am diary seam sits at hour 4 in 2022
and 2025, daytime absence sits at 9 to 16). The 2005 profile is almost flat, which is odd. Is the April
set on the real clock, and is the flat 2005 profile a data property or a bug?

**B5. Code.** `eSim/eSim_bem_utils/` locally (all files dated 2026-08-13, a bulk copy) differs from the
cluster copy `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/eSim_bem_utils/` (dated 2026-04-16 to 04-18)
by thousands of lines. The four cluster files are copied for you to
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\7ac8b9b9-c77e-419c-ad41-0aaeaf7638da\scratchpad\cluster_code\`
(`main.py`, `simulation.py`, `integration.py`, `neighbourhood.py`). Known differences in `integration.py`:
the cluster copy treats five fixed Canadian holidays as weekend days; the local copy drops holidays, forces
design-day dates to the weekday pattern, and can write setpoints through `Schedule:File`. The cluster
`config.py` and `run_batch_hpc.py` are identical to the local ones. The pilot itself was run from the local
code as it stood on 2026-04-13, which no longer exists as a copy (the manager found none; CHECK
`_local_runs\`, `.bak` files, or anything else that could hold it).

**B6. How the batch draws households** (cluster and local `main.py`, `_run_mc_neighbourhood`, near lines
1970 to 2240 locally):
- A `Default` run (the neighbourhood's own schedules) runs once per invocation, before the draws.
- Per draw: one base household per building is drawn with plain `random.choice` from the **first year's**
  (2005) pool of the building's dwelling type; `used_base_k` stops a base household being drawn twice in
  one invocation. Each other year then gets its best-matching household (same size and dwelling type,
  smallest squared schedule difference, `integration.find_best_match_household`). Nothing is seeded.
- The five years of one draw run as five EnergyPlus jobs; `--workers` (env `ESIM_WORKERS`,
  `simulation.py:156-162`) caps how many run at once.
- No resume: an interrupted invocation restarts at `Default`.

**B7. Timings.** Local pilot, wall-clock per group of five simultaneous runs: 37 to 250 minutes per
neighbourhood (RC5 slowest). Cluster April 20-draw batch (`/speed-scratch/o_iseri/GSSCanada/results/
BatchAll_MC_N20_v2/`, script `.../GSSCanada-main/submit_array_tuned.sh`): 5 CPUs, 64 GB, sim mode
**weekly**, about 30 hours per neighbourhood, and "RC6 peaked at 58 GB" (comment in that script). No log
records peak memory for one single run.

**B8. Run period.** The pilot's `prepared.idf` files have `RunPeriod` 1 January to 31 December (sim mode
"standard", full year). The cluster 20-draw batch used "weekly" (24 representative weeks, scaled to a year,
`eSim/eSim_bem_utils/idf_optimizer.py:449`), so it is a different method from the submitted figures.

**B9. Cluster rules (binding).** Speed cluster, `sbatch` only, never Python on the login node, every job
asks for 7 days (`-t 7-00:00:00`). The author allows **one CPU** for this work for now, because their other
jobs fill their share; it may be raised later. The local machine is busy with another heavy run and cannot
be rebooted remotely, so nothing runs locally.

---

## Part C. The draft plan (what you are checking)

1. **Inputs:** the five files in B1, staged into a new folder of their own on Speed, renamed
   `BEM_Schedules_{2005,2010,2015,2022,2025}.csv` inside that folder's `BEM_Setup/` (the code reads
   `BEM_SETUP_DIR/BEM_Schedules_{year}.csv`). The shared cluster `BEM_Setup/` is not touched.
2. **Code:** the April cluster copy (B5), unchanged, because it is closest to the pilot. The later fixes are
   listed as a limitation in the paper.
3. **Run period:** "standard" (full year), as in the pilot.
4. **Job design:** one SLURM array of 6 x N tasks. Task i runs neighbourhood ((i-1) mod 6)+1 for draw
   ((i-1) div 6)+1, as `run_batch_hpc.py --idf .../NUS_RC{j}.idf --region Quebec --sim-mode standard
   --iter-count 1 --workers 1 --output-dir <folder>/draw_{k}/NUS_RC{j} --use-tmpdir`; `--cpus-per-task=1`,
   `--mem=24G`, `-t 7-00:00:00`, array throttle `%1` (one CPU in use at any time; can be raised later with
   `scontrol update JobId=<id> ArrayTaskThrottle=<n>`). Draw-major order, so each 6 finished tasks give one
   full draw of all six neighbourhoods. Each task re-runs `Default` (wasted time, but a free repeat check).
5. **N = 20** draws.
6. **Checks before any number is used:** the five staged files have five different md5 values (this check
   was seen failing on the old 2005/2010 pair); the staged files reproduce the four weekday hours in B2;
   `Default` results are identical in every task of the same neighbourhood; every task has all five year
   outputs (`eplusout.sql` or `eplustbl.htm`).

---

## Part D. Questions (answer every one; NOT FOUND is a valid answer)

Q1. **Inputs.** Are the five B1 files the right inputs for a corrected Section 4.2? Is the 2010 file a true
sibling of the 2005 and 2015 files (same converter version, same sampling, same filters)? Compare
`06CEN05GSS_occToBEM.py`, `11CEN10GSS_occToBEM.py` and `16CEN15GSS_occToBEM.py` and their upstream steps.
Is the 2022 `CLASSIC_BAK` file (and the 2025 file) what the pilot actually read on 2026-04-13? Its
time stamps must be earlier than the pilot; say what else could prove it.

Q2. **Clock (B4).** Is every one of the five files on the real clock? Is the near-flat 2005 weekday profile
plausible, or a sign of a different bug (for example household-size normalisation)?

Q3. **Code (B5).** List the differences between the cluster April code and the local code in anything that
changes an energy result (schedules, setpoints, day types, holidays, run period, matching, the pool). Which
code should the re-run use, and why? Can the 2026-04-13 pilot code be recovered?

Q4. **Separate tasks vs one run (C4).** With `--iter-count 1` per task, `used_base_k` no longer stops the
same base household being drawn twice across draws, and every task builds its pools afresh. Does this
change the statistics compared with one 20-draw run? How large is each pool per dwelling type (read the
pool-building code: `pool_size = max(n_buildings*2, len(scored)//2)` and what `scored` is), and so how
likely are repeats? Would you rather add a seed and a draw index (a small code change), and if so, what
exactly?

Q5. **Region.** Does `--region Quebec` restrict the household pool to `PR == Quebec`, or only pick the
weather file? Quote the lines. What does the submitted paper say the pool is?

Q6. **N.** Is N = 20 enough to tell the year scenarios apart, given the pilot's spread? Use the pilot's
per-draw results in `BatchAll_MC_N3_1776120359` (and, if readable, the local 20-draw batch that WP2b
found) to estimate the draw-to-draw spread, and say what N gives a confidence interval narrow enough for the
differences the paper claims. Paired or unpaired comparison?

Q7. **Resources.** Is 24 GB enough for one run of the largest neighbourhood (RC6, 9 high-rise buildings)?
Is the 7-day limit safe for one task on one CPU in "standard" mode? Estimate from B7 and say what is
measured and what is assumed.

Q8. **Checks (C6).** Would each check catch the fault it is meant for? What fault would slip past all of
them? Propose at most three more checks, each with how it can be seen failing first.

Q9. **Anything else** that would make the re-run's numbers wrong or not comparable with the submitted
figures (for example weather file, `Default` definition, the 2025 cohort, output extraction, the meter or
EUI definition used in the figures).

---

## Part E. Rules

- Read-only, apart from your one report file. Run **no** EnergyPlus and start no batch. Do not touch the
  cluster; the cluster facts you need are in Part B and the scratchpad copy.
- The schedule files are 60 to 475 MB. **Never load a whole one into memory.** Stream them line by line
  (Python `csv` module or `awk`), one file at a time. Python: `py` (3.13, with pandas). Bare `python` is a
  broken stub.
- Cite every claim as `file:line` or a file path plus the value you read. A claim without a citation is
  treated as a guess.
- NOT FOUND beats a guess. Mark each estimate as ESTIMATED and state its assumptions.
- Do not relax a check because the plan would fail it.
- Plain hyphens only; no em or en dashes.

## Part F. Control items (they tell us whether the report can be trusted)

Answer these three exactly, from the files (stream them):
- C1. The first 8 hex characters of the md5 of `BEM_Setup/BEM_Schedules_2025.csv`.
- C2. The mean `HHSIZE` over distinct `SIM_HH_ID` in `BEM_Setup/BEM_Schedules_2025.csv`, to 2 decimals.
- C3. The **weekend** hour (0 to 23) with the highest mean `Occupancy_Schedule` in
  `BEM_Setup/BEM_Schedules_2015_PRE_STEP8_BAK.csv`.

## Part G. Report format (`inv_1J-01_REPORT_fable.md`)

1. **Verdict on the plan** in one line: GO, GO WITH CHANGES, or STOP.
2. **Changes required before submission**, most important first, each with the evidence.
3. **Q1 to Q9**, each with: verdict (AGREE / DISAGREE / NOT FOUND), the answer, and citations.
4. **Control items C1 to C3.**
5. **What I did not verify.**
