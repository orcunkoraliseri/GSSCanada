# TASK (employee, Sonnet): fix the 5J campaign placement so each household gets 3 DISTINCT flats

Written 2026-09-30 16:30 EDT (from `date`) by the 5J manager. Read first: the task
`Step2_docs/impl/2026-09-30_wp1_campaign_design_TASK.md` (Part C) and its state file
`Step2_docs/impl/2026-09-30_wp1_campaign_design.md`, INCLUDING "Verified (manager)" (the defect).
State file: create `Step2_docs/impl/2026-09-30_wp1_campaign_design_fix.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY); `date` before every stamp.

## The defect
The ruling is "each household in at least 3 flats of every MFH/AB building" (P = 3 positions). The run tables give
each household 3 placements, but on es_B21 10 of 60 households land twice on the same flat index, so they have only
2 distinct flats. Gate C1 counted placements, not distinct flats, and passed.

## Hard rules (same as the parent task)
* 🔴 ALL compute on Speed via sbatch (`-p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`). Locally ONLY edit/write files, ssh/scp, ls, read small files.
  Login node: sbatch/squeue/sacct/scancel/scp/ls and single-file cat/tail/wc -l. Hashes (md5) only inside a job.
  At most 6 sacct checks of 30 s per job, then "manager to read" and stop.
* 🔴 UK licence: Spain and Italy only; no UK household/diary/schedule/output; no folder-wide search or wildcard that
  could match a UK file.
* Speed folder `R=/speed-scratch/o_iseri/5J/campaign_prep/`. Changes to `cd_design.py` / `cd_gates.py` are ADDITIVE:
  back up first (`<name>.v1_2026-09-30`), the old behaviour stays reachable by a flag, each change prints a
  `PATCH <name> OK` line that must be PRESENT in the job output.

## Steps
1. Copy the Speed scripts of the parent task (`cp_partA_tabula.py`, `cd_design.py`, `cd_gates.py`,
   `cd_timing_build.py`, `cd_arith.py`, `cd_extract_timing.py`, the `.sbatch` files) into `tools/speed/` (backups
   first on Speed; the local copies are the record).
2. **Gate first (seen failing on the CURRENT tables):** add `C1_distinct` to `cd_gates.py`: for every MFH/AB
   building, pool and climate, every household of the pool sits in at least `min(3, n_dwellings)` DISTINCT dwelling
   indices. Run it on the current tables: it MUST FAIL (es_B21 among the failures). Print the number of
   (building, household) pairs below the bar per country. Keep old C1 as `C1_slots`.
3. **Placement repair** in `cd_design.py` (flag `--distinct-flats`, default on): after the slots of one building and
   pool are filled, repair deterministically: while some household has fewer than `min(3, n)` distinct flats, find
   the first such household h with a repeated flat f in run a; swap h's slot (a, f) with the slot (b, g) of another
   household h2 in the same building and pool (scan runs b and slots g in order) such that after the swap: h gains a
   distinct flat, h2 does not drop below `min(3, n)` distinct flats, and no household appears twice in run a or run
   b when `n <= |pool|`. Count swaps; if no swap exists, print `REPAIR_STUCK <building> <pool> <hid>` (do not loop).
   Placement stays identical in the 3 climates of a country (repair once per building and pool, then copy).
4. Rewrite `campaign_runs_es.csv` and `campaign_runs_it.csv` (keep the old ones as `*.v1_2026-09-30.csv`). Run
   counts must NOT change (same runs, only who sits where): print old vs new counts per country, class and pool.
5. Rerun all gates (C1_slots, C1_distinct, C2-C7) on the new tables: all PASS, `REPAIR_STUCK` count 0. INFO: per
   class, the distribution of distinct floors and of end/middle flats per household (position variety).
6. Update `outputs_step2/campaign_design.md` (placement rule text, gate list, new md5s) and copy the new tables to
   `outputs_step2/`. Do NOT touch splits, counts, timing or disk sections except to confirm them unchanged.

## Report back (short)
C1_distinct on old tables (FAIL + counts), swaps made, REPAIR_STUCK count, gates on new tables, run counts old vs new,
new md5s, JobIDs. Status DONE, Next = "manager verifies; manager freezes the design".

## What the manager will re-derive
Distinct flats per household on es_B21 and one more building (own job); run counts unchanged; md5 of the new tables.
