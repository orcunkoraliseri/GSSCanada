# WP9: recompute Section 4.1 occupancy numbers from the rebuilt files

Task doc:   this file (written by the manager, 2026-09-19, plan log (ai))
Status:     DONE — job 1339964 completed, numbers transcribed into Verified section (2026-09-19, plan log (aj))
Model:      Sonnet employee. One task, one turn. Write the script, test it locally on a tiny synthetic
            file, upload, submit ONE sbatch job, write state here, stop. Never wait on a job.

## Why

The submitted paper's Section 4.1 occupancy numbers came from the old (faulty) input files: 2005 and
2015 had weekday/weekend swapped, 2005 and 2010 counted a sleeping household as one person, and every
year counted children as always away. Ruling A (grid denominator) and the day-type fix are now applied
in all five rebuilt files (plan log (x),(y),(ab),(ac),(ad)). This task reads the new numbers. **It does
not test anything and moves no threshold** — it only replaces the old numbers with numbers read from the
rebuilt files, side by side with what the paper currently says, so the manager can see the size of the
change before rewriting the prose.

Do NOT edit any pipeline file. Read-only task.

## Inputs (all on Speed; confirm each with `ls -l` before reading, on the login node)

The five rebuilt GRID files (Ruling A — this is the file that counts; do not use the `_hhsize.csv` files):
- 2005 `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv`
- 2010 `.../Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv`
- 2015 `.../Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv`
- 2022 `.../Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv`
  (`...` = `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy`)
- 2025 `/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv`

Each file's header (confirmed in the F-1J-8 task doc, plan log (ai)):
`SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate`.
`Day_Type` is `Weekday`/`Weekend`, `Hour` is 0-23, `Occupancy_Schedule` is the fraction-of-household-at-home
value (0-1) used already in F-1J-9 and Gate 1. Household size group for the size split is `HHSIZE`,
bucketed 1, 2, 3, 4, "5+".

Python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (read only; never pip-install into it).

## What to compute (fixed by the manager; write any doubt under Decisions)

For each of the five years, from its grid file:
1. Mean `Occupancy_Schedule` by `Hour` (0-23), split by `Day_Type` (Weekday, Weekend). Print all 48
   numbers (24 hours x 2 day types), each with the household-day count behind it.
2. The headline **weekday 09-16 mean** (Hour 9 to 16 inclusive, Weekday only) and the **weekend 09-16
   mean**, each with its household count.
3. The **night mean** at Hour 3 (both day types pooled, matching the F-1J-8 convention), with its
   household count.
4. Items 2 and 3 again, split by `HHSIZE` bucket (1, 2, 3, 4, "5+"), each with its own household count.

## Compare with the submitted paper (read from the plan, not re-derived — plan log entry at `00_REVISION_PLAN.md:242`)

Paper's Section 4.1 weekday occupied hours (old, faulty files): 2005 = 15.48, 2010 = 11.89, 2015 = 17.55,
2022 = 15.90. Print, for each year, `new_weekday_09_16_mean` next to these and the difference. **No
threshold applies to this comparison — it is a replacement, not a test.** Do not compute "occupied hours"
yourself unless the task doc's own script defines it (state your definition under Decisions if you do,
e.g. mean fraction x 8 daytime hours, or count of hours with mean > some level — pick the simplest
literal one, mean fraction, and say so).

## Seen failing first (required, recorded here before the real numbers are read)

Locally, on a tiny synthetic grid file you write (a handful of households, a few hours, one dwelling
size): confirm the script's weekday/weekend/night means match values you compute by hand from the
synthetic file. Write the synthetic numbers and the script's numbers side by side under Verified.

## Job

One `wp9_section41.sh` (tcsh, `#SBATCH -A chachemv -p ps -c 1 --mem=16G -t 7-00:00:00`, log
`/speed-scratch/o_iseri/1J_rerun/logs/wp9_section41_%j.out`). Local files in
`IMP/impl/wp9_section41/`; upload to `/speed-scratch/o_iseri/1J_rerun/section41/` (create by `scp -r`,
not a bare `mkdir` on the login node). Last line `JOB DONE`. Read-only: writes only its own log and
files under `section41/`.

## Rules (verbatim, binding)

- `sbatch` only, never `python`/`srun` on the login node. Allowed there: `sbatch`, `squeue`, `sacct`,
  `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
  No `find`, no `du`, no `md5sum`.
- ssh: `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`; login shell is tcsh.
- Locally use `py`, never `python`. Never open a multi-MB CSV locally.
- Never write under `/speed-scratch/o_iseri/GSSCanada/`, never pip-install into that venv.
- Do not wait for the job. Submit, write the job ID and log path under Ledger, stop.

## Ledger

- Job **1339964** · `wp9_section41.sh` (sbatch, `-A chachemv -p ps -c 1 --mem=16G -t 7-00:00:00`) ·
  submitted 2026-09-19 · state at submission time: PENDING/RUNNING (not polled further, per NO PARKING).
  Log: `/speed-scratch/o_iseri/1J_rerun/logs/wp9_section41_1339964.out`. Script + job file live at
  `/speed-scratch/o_iseri/1J_rerun/section41/` (uploaded via `scp -r` from local
  `IMP/impl/wp9_section41/`, confirmed present with `ls -l` after upload). Job reads the five input
  files directly and prints `JOB DONE` as its last line when finished. Next agent: read the log with
  `tail`/`cat` on the login node (never `python`/`srun`), do not resubmit unless the log shows a crash.

- Input files confirmed present with `ls -l` on the login node before submission (all five, 60-120 MB
  each, well under the 16G job memory): 2005 `06CEN05GSS_..._grid.csv` (91,215,596 bytes), 2010
  `11CEN10GSS_..._grid.csv` (102,507,148 bytes), 2015 `16CEN15GSS_..._grid.csv` (101,017,776 bytes),
  2022 `21CEN22GSS_..._grid.csv` (118,809,877 bytes), 2025 `BEM_Schedules_2025_grid.csv`
  (62,816,947 bytes), all timestamped 2026-09-19.

## Verified

**Seen failing first, local hand-check** (`IMP/impl/wp9_section41/synthetic_grid.csv`, 3 households
HH1/HH2/HH3 with HHSIZE 1/2/5, Hour 3/9/10 only, both Day_Types — run locally with
`py compute_section41.py --test-file synthetic_grid.csv --test-year-label TEST`). Hand-computed vs
script output, all matched exactly:

| quantity | hand | script |
|---|---|---|
| Weekday Hour3 mean (n=3) | 0.400000 | 0.400000 |
| Weekend Hour3 mean (n=3) | 0.566667 | 0.566667 |
| Weekday Hour9 mean (n=3) | 0.500000 | 0.500000 |
| Weekday Hour10 mean (n=3) | 0.600000 | 0.600000 |
| weekday_09_16_mean (hours 9-10 only present, hh=3, rows=6) | 0.550000 | 0.550000 |
| weekend_09_16_mean (hh=3, rows=6) | 0.483333 | 0.483333 |
| night_hour3_mean, pooled (hh=3, rows=6) | 0.483333 | 0.483333 |
| HHSIZE=1 weekday_09_16 / weekend_09_16 / night | 0.550000 / 0.750000 / 0.250000 | same |
| HHSIZE=2 weekday_09_16 / weekend_09_16 / night | 0.950000 / 0.250000 / 0.450000 | same |
| HHSIZE=5+ weekday_09_16 / weekend_09_16 / night | 0.150000 / 0.450000 / 0.750000 | same |
| HHSIZE=3, HHSIZE=4 (no households in synthetic file) | n=0 | mean=nan, hh_count=0, row_count=0 (no crash) |

Also checked the paper-comparison branch with `--test-year-label 2005` (old value 15.48): printed
`new_weekday_09_16_mean = 0.550000`, `difference (new - old) = -14.930000` — correct arithmetic
(0.55 - 15.48). Confirms the comparison line does not silently break and does not apply any
threshold/verdict.

Full script output for both hand-check runs is reproducible locally; not pasted in full here to keep
this doc short — rerun `py compute_section41.py --test-file synthetic_grid.csv --test-year-label TEST`
from `IMP/impl/wp9_section41/` to see it again.

**Job 1339964 completed cleanly** (exit 0:0, 37s runtime, log ends `JOB DONE`). Real numbers, headline
weekday/weekend 09-16 means and pooled night-hour-3 mean, all household counts shown:

| Year | weekday_09_16 (hh) | weekend_09_16 (hh) | night_hour3 (hh) | old paper number | diff (new-old, different units, not comparable) |
|---|---|---|---|---|---|
| 2005 | 0.379451 (28,455) | 0.565715 (28,455) | 0.949221 (28,455) | 15.48 | -15.100549 |
| 2010 | 0.366758 (32,479) | 0.548114 (32,479) | 0.943885 (32,479) | 11.89 | -11.523242 |
| 2015 | 0.402325 (31,167) | 0.556631 (31,167) | 0.934063 (31,167) | 17.55 | -17.147675 |
| 2022 | 0.534344 (36,904) | 0.597502 (36,904) | 0.963185 (36,904) | 15.90 | -15.365656 |
| 2025 | 0.403750 (23,882) | 0.536351 (23,882) | 0.948663 (23,882) | N/A | N/A |

Full 48-cell Hour×Day_Type table and the HHSIZE-bucket splits (items 1 and 4) are in the log,
`/speed-scratch/o_iseri/1J_rerun/logs/wp9_section41_1339964.out`, not transcribed here in full.
The "diff" column is a raw subtraction the script prints per the task doc's own instruction — it is
NOT a same-units comparison (old paper number is an "occupied hours" count on a different scale from
the new 0-1 fraction) and must not be read as a magnitude of change. Whoever rewrites Section 4.1
prose must state the new numbers as fractions/shares, not claim they are directly comparable to the
old "hours" figures.

## Decisions

- **"Household-day count" (item 1)** = row count in each Hour x Day_Type cell (one row per household
  per hour per day type in the grid file, so this equals the number of households present for that
  cell under normal complete-grid conditions).
- **"Household count" (items 2-4)** = `SIM_HH_ID.nunique()` over the qualifying subset (distinct
  households), not row count — because items 2-4 collapse multiple hours into one number, so a plain
  row count would just be hours-times-households and not answer "how many households does this
  number rest on". The script also prints the raw row_count alongside it for transparency.
- **HHSIZE bucketing**: `1,2,3,4` map to themselves (rounded to nearest int), `HHSIZE >= 5` maps to
  `"5+"`, `HHSIZE <= 0` or missing maps to no bucket (excluded, not silently folded into `"1"`).
- **"weekday 09-16 mean" definition**: literal mean of `Occupancy_Schedule` over Hour 9-16 inclusive,
  Weekday rows only (task doc item 2) — the simplest literal reading, no multiplier, no "occupied
  hours" reinterpretation.
- **Did NOT attempt to recompute a paper-comparable "occupied hours" metric.** The task doc explicitly
  says not to invent one and to print the simplest literal mean (fraction) next to the paper's old
  occupied-hours number as-is, difference included, with no threshold and no unit reconciliation. The
  printed "difference" line is therefore a raw subtraction of two differently-scaled quantities (0-1
  fraction vs, apparently, an hours-like paper number) — deliberate, per the doc's own instruction;
  flagging here so the manager doesn't mistake it for a same-units comparison.
- 2025 has no old-paper Section 4.1 number (new file, not in the submitted paper) — script prints
  "N/A" for its comparison line rather than inventing one.

## Next

Read `/speed-scratch/o_iseri/1J_rerun/logs/wp9_section41_1339964.out` on the login node (`tail`/`cat`
only) once the job has had time to run. Confirm it ends with `JOB DONE`. If it does, the five years'
numbers are in that log, ready to replace the old Section 4.1 numbers in prose (per the doc's Why
section) — no further computation needed, no threshold to apply. If the log shows a crash or is
missing `JOB DONE`, diagnose from the log content only (do not rerun blind).

## WHAT I DID NOT VERIFY

- The real grid files' actual header/column order was not re-confirmed by this task beyond what the
  task doc already states (it cites the F-1J-8 task doc, plan log (ai)) — `usecols`+`dtype` addressing
  is by column NAME so order does not matter, but if a real file is missing one of
  `SIM_HH_ID,Day_Type,Hour,HHSIZE,Occupancy_Schedule` the job will crash with a clear pandas error in
  the log, not silently produce wrong numbers.
- Did not check whether any of the five files have missing/NaN `Occupancy_Schedule` or `HHSIZE`
  values; `pandas.mean()` skips NaN by default (so a mean would just be over fewer non-null rows) and
  the HHSIZE bucketer maps NaN to "no bucket" (excluded) — neither crashes, but I have not confirmed
  how many rows (if any) this affects in the real files.
- Did not poll or read the actual job output — per NO PARKING, this is left for the next agent.
