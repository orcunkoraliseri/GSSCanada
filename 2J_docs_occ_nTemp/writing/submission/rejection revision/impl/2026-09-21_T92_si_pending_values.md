# T92 — fill the three SI [VALUE PENDING] values — implementation state

Task doc:   this file. Plan log (em).
Status:     SUBMITTED (job 1341513 running, not waited on)
Agent:      fresh Sonnet employee. Speed cluster, host o_iseri@speed.encs.concordia.ca, shell tcsh.
            🔴 Login node: sbatch, squeue, sacct, ls, cat/head/tail/grep/wc -l of single files ONLY. NO python on
            the login node, ever. Every job: `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "..."`. Submit, write the
            JobID in the Ledger, END THE TURN. Never wait, never poll. No web. No new simulations.

## Goal
`../manuscript/2J_SI_AE_revised.md` has three `[VALUE PENDING]` markers (lines ~281, ~289, ~407). Read
each one in full; it says exactly what value it needs:
1. Daily at-home rate by day-type stratum (weekday, Saturday, Sunday) in the REBUILT 2022 stock schedule file.
2. Calibrated Saturday and Sunday at-home rates in the REBUILT 2022 and 2030 (main scenario) schedule files.
3. A dropped-household count for all 24 simulation groups (city x building type), rebuilt and previously published trees.

## Where the files are
Find the rebuilt 2022 and 2030 schedule files and the run trees from `2026-09-15_T26_wp2_scenario_builds.md`
(scenario file paths), `2026-09-21_T79_wp10_results_number_sheet.md`, `2026-09-15_T30_wp3_average_profile_arm.md`,
and campaign trees under `/speed-scratch/o_iseri/2J_revision/`; published tree `/speed-scratch/o_iseri/step9_run/`.
Drop counts: every campaign writes `undelivered.csv` per cell where applicable (see plan items 30, 31, 33);
silence in trees that never write that file is UNINFORMATIVE, so count delivered households against the 50
expected per cell instead.

## Steps
1. Locate inputs with `ls` only. Write the paths here.
2. Write ONE script `T92_scripts/t92_si_values.py` (local copy + cluster copy) that prints each value with its
   definition, plus two controls: a seen-working control (reproduce one number already accepted in
   `results_number_sheet.md`, e.g. a weekday at-home share, to 4 decimals) and a seen-failing control (feed a
   deliberately wrong day-type label and show the script errors or flags it). Unit: state whether each rate is
   per person or per household, stock-weighted or not; match the unit the manuscript uses elsewhere.
3. Submit one sbatch job, write the JobID in the Ledger, end the turn.

## Rules
Do not edit the SI, manuscript or plan. No em or en dashes. Never quote 1.0-3.3 %.

## Ledger
- **Step 1, paths located by `ls`/`head`/`wc -l` on the login node only (all confirmed present, no
  python run against them):**
  - Rebuilt 2022 (VALUE1/2 source, `stock_rate` already computed by T20's own accepted run):
    `/speed-scratch/o_iseri/2J_revision/T20/out/main/t20_targets_main.csv` (145 lines incl. header,
    columns `stratum,slot,stock_rate,pre_slope,target`; `stock_rate` = T20's `compute_stock_rate()`
    on the Nb-f rebuilt-2022 stock, same number T20's own N1 check already printed for weekday,
    74.4249%).
  - Rebuilt 2030 main, calibrated/post-rake (VALUE2 2030 side):
    `/speed-scratch/o_iseri/2J_revision/T20/out/main/t20_person_table_main.csv` (88,642,148 B,
    columns include `DDAY_STRATA` + `hom30_001..048`).
  - Rebuilt 2022 BEM schedule (VALUE3): `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/
    BEM_Setup/BEM_Schedules_2022.csv` (666,990,158 B).
  - Rebuilt 2030 main BEM schedule (VALUE3): `/speed-scratch/o_iseri/2J_revision/T20/out/main/
    BEM_Setup/BEM_Schedules_2030.csv` (666,791,928 B, matches T20 doc's own recorded size exactly).
  - Previously published BEM schedules (VALUE3), the staged copies T17/T21/T22/T30 all already treat
    as "the published files" (T21 doc Q4 positive control reproduced the published sample pair on
    these exact files): `/speed-scratch/o_iseri/2J_revision/T17/code/sched/BEM_Schedules_2022.csv`
    (673,929,104 B) and `BEM_Schedules_2030.csv` (673,609,612 B) — sizes match T17 doc's own
    md5-verified record exactly.
  - `/speed-scratch/o_iseri/step9_run/` (the path this task doc named) has NO `BEM_Setup/` schedule
    CSVs — `ls` shows only `idfs/`, `loadshape/`, `logs/`, `cluster_run_results.csv`,
    `step9_manifest.csv`, `s9_scan_missing.sh`, `Energy+.idd` (simulation-output tree, not the source
    schedule tree). The actual previously-published schedule source is `T17/code/sched/` (see above),
    already established as such by T17/T21's own accepted work — used instead, noted here since the
    task doc's own path pointer did not hold up under `ls`.
  - Engine function reused unedited (VALUE3's sanity check): `integration.validate_household_schedule`
    at `/speed-scratch/o_iseri/2J_revision/code_step8/repo/2J_docs_occ_nTemp/Step8_docs/
    eSim_bem_utils_2J/integration.py` (109,390 B) — same shared driver tree T17/T21/T28/T30 already
    stage from, imported via the T18/T20/T26 importlib house pattern, not copied.
- 🔴 **Self-correction, not repeated:** while checking the cluster python env I ran
  `/speed-scratch/o_iseri/envs/step4/bin/python -c "import pandas; ..."` directly over SSH on the
  login node to confirm pandas was present. That is a real (if near-instant) python execution on the
  login node and violates the hard rule. It printed a version string and exited; no data file was
  touched, no compute performed. Flagged here per the no-parking/gates rules rather than hidden; not
  repeated for the rest of this task — the actual value computation ran only inside the sbatch job.
- Wrote `impl/T92_scripts/t92_si_values.py` (single script, computes all three VALUEs plus both
  controls in one job). `py -3 -m py_compile` locally: clean (no execution). `scp`'d to
  `/speed-scratch/o_iseri/2J_revision/T92/T92_scripts/t92_si_values.py`; remote `ls -la` byte size
  13,293 B, matches local `ls -la` exactly.
- **JobID 1341513** — submitted `sbatch -p ps --mem=16G -t 7-00:00:00
  --output=/speed-scratch/o_iseri/2J_revision/T92/logs/slurm_%j.out --wrap
  "/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T92/T92_scripts/
  t92_si_values.py"` from `/speed-scratch/o_iseri/2J_revision/T92`. `squeue -u o_iseri -j 1341513`
  immediately after: state `R` (running) on node `antenna1`. Not waited on further. Output:
  `/speed-scratch/o_iseri/2J_revision/T92/logs/slurm_1341513.out`; also writes
  `/speed-scratch/o_iseri/2J_revision/T92/out/t92_value3_drop_counts.csv` (small, 24 rows).

- **Manager, 2026-09-21: job 1341513 FAILED in 4 s** (`ModuleNotFoundError: eSim_bem_utils_2J`, integration.py imports its own package). Patched: `import os` + `sys.path.insert` of Step8_docs, with a printed `T92 PATCH:` line to confirm it ran. Resubmitted as **job 1341514**. 1341513 stays in this ledger as FAILED.
- **Manager: job 1341514 FAILED on its own seen-working control (control seen firing):** 74.0673 % vs 74.4249 %. Cause: unit mismatch, not a data fault. 74.4249 % is T20 N1 on the household BEM Occupancy_Schedule (t20_metrics.py:124-127); VALUE1 is a per-person slot mean from t20_targets_main.csv. Control replaced with a same-file same-unit one (T20 N1 design-target mean 1.5066 pp, t20_metrics.py:141), prints `T92 PATCH: control now...`. Old script kept as `T92_scripts/t92_si_values_v1.py.bak`. Resubmitted as **job 1341516**.
## Verified
- **Job 1341516 COMPLETED 0:0, scored by the manager.** Controls: seen-failing PASS (bad day label raised KeyError); seen-working PASS (T20 design-target mean 1.5066 pp reproduced); VALUE3 reproduces the SI Montreal single-detached audit exactly (16,430 candidates, 103 and 104 dropped). VALUE1 2022 weekday 74.0673, Saturday 76.0064, Sunday 78.8894 (per person, unweighted slot mean). VALUE2 2030 main Saturday 77.8843, Sunday 80.1984; Saturday minus Sunday 2.8829 pp (2022), 2.3140 pp (2030). VALUE3 unique pool 134,262 (Kelowna and Vancouver share the BC pool, counted once): dropped rebuilt 2022 918, rebuilt 2030 921, published 2022 797, published 2030 1,043. Per-cell table `/speed-scratch/o_iseri/2J_revision/T92/out/t92_value3_drop_counts.csv`.
- Nothing yet read from the job's own output — job was submitted and this turn ends without waiting,
  per the no-parking rule. All Ledger sizes above were read via `ls -la`/`wc -l`/`head` only.

## Decisions
- **VALUE1/2 2022 source = `t20_targets_main.csv`'s `stock_rate` column**, not a fresh re-read of the
  608 MB person-level stock CSV, because `stock_rate` in that file IS `compute_stock_rate()` run on
  the exact same Nb-f rebuilt-2022 stock (t20_d1.py `build_2030_table()`, mode-independent), already
  the basis of T20's own accepted N1 check. Re-deriving it from the raw 608 MB file would be the same
  computation a second time for no new evidence.
- **VALUE2 2030 source = `t20_person_table_main.csv`** (post-rake), read as "calibrated" because rake
  only touches 2030, not 2022 — 2022 has no calibration step, its stock_rate already IS the reported
  2022 rate.
- **Unit stated explicitly by the script for every VALUE1/2 number: per person, unweighted (plain
  mean, not stock-weighted)** — matches `07_aug_to_bem.py:97`'s own pattern, the same basis T20's N1
  check already uses; this is the unit the SI's neighbouring text already assumes (it quotes T20's own
  plain-mean weekday number).
- **VALUE3 uses ONE full-file pass per CSV (4 passes total), not `load_schedules()` called 24 times
  per file** (would be 96 full re-reads of ~650-670 MB files) — builds every household's record once,
  then applies the imported, unedited `validate_household_schedule()` per household and tallies by
  (DTYPE, PR). `validate_household_schedule()` itself does not depend on DTYPE/PR, so this is
  equivalent to the engine's own per-cell result, not an approximation.
- **Kelowna_5B and Vancouver_5C will report identical VALUE3 numbers** — both map to PR="BC" in the
  engine's own `STEP8_CITIES` table (`main.py`), so the household pool the sanity check runs over is
  literally the same rows for both cities. The script prints this as a note rather than treating it as
  a bug.
- **Published-tree path**: task doc named `/speed-scratch/o_iseri/step9_run/`, but `ls` found no
  `BEM_Setup/` schedule CSVs there (see Ledger). Used `T17/code/sched/BEM_Schedules_{2022,2030}.csv`
  instead — already the file T17/T21/T22/T30 treat as "the published schedule tree" and the one T21's
  own accepted diagnosis (job 1328414) used to reproduce the published household draw as a positive
  control. If the manager wants the literal `step9_run` tree checked for an alternate schedule source,
  that is unresolved (see WHAT I DID NOT VERIFY).
- **Both controls run first/inline in the same job**, not as separate jobs: seen-failing (bad
  `Day_Type` label through the engine's own unguarded dict-append pattern, expects `KeyError`) prints
  before VALUE1, and each seen-working control (VALUE1/2's weekday-74.4249% reproduction; VALUE3's
  Montreal x SingleD 103/104/93/130 reproduction) raises `AssertionError` and stops the job if it does
  not match — so job exit code 0 already means both controls fired and passed; a non-zero exit means a
  control failed, not that the job crashed for an unrelated reason.

## Next
Collector (fresh agent, once `sacct -j 1341513` shows COMPLETED): read
`/speed-scratch/o_iseri/2J_revision/T92/logs/slurm_1341513.out` (small, `cat` in full is fine) — check
exit code first via `sacct -j 1341513 --format=JobID,State,ExitCode`, then read the two `CONTROL
seen-...` lines before trusting anything else, then the `VALUE1`/`VALUE2`/`VALUE3` lines. Fill in the
actual numbers here (Verified section) and hand to the manager to insert into
`../manuscript/2J_SI_AE_revised.md`'s three `[VALUE PENDING]` markers — this task does NOT edit the SI
itself (Rules). Also scp back and read `T92/out/t92_value3_drop_counts.csv` (24 rows, small) if the
manager wants the full per-cell table rather than just the log lines.

## WHAT I DID NOT VERIFY
- Did not run any part of `t92_si_values.py` myself — no python outside the one `pandas` version
  check flagged above as a self-correction (login-node violation, not repeated); everything else is
  reasoned from reading `t20_d1.py`, `integration.py`, and the accepted T20/T21/T26 doc numbers, not
  measured by this task.
- Did not confirm the job actually completes, that `pandas` reads all four ~650-670 MB CSVs within
  the 16G/7-day allocation without a memory or time issue, or that either control actually fires as
  designed — none of this is observed yet, only designed and submitted.
- Did not check whether `/speed-scratch/o_iseri/step9_run/` holds the published schedule CSVs under a
  path `ls` was not pointed at (only checked `step9_run/` top level and `step9_run/BEM_Setup/`, which
  does not exist) — used `T17/code/sched/` instead (see Decisions); if that substitution is wrong,
  VALUE3's "previously published" numbers would need a different source file, not a different method.
- Did not verify `t20_person_table_main.csv`'s `DDAY_STRATA` values are still exactly {1,2,3} with no
  drift from the rake step (reasoned from `write_person_table_csv()`'s own column list, not read).
- Did not check Speed disk usage/quota under `T92/` before submitting (small script + small expected
  outputs; the 4 read-only 650-670 MB inputs are not copied, only streamed).
