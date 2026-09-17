# T32 — WP2 S-Revert-std schedule build on Speed — implementation state
Task doc:   this file. Spec: `2026-09-15_WP2_scenario_spec.md` §5 (definition and acceptance, fixed).
Code base:  `2026-09-15_T26_wp2_scenario_builds.md`, `T26_scripts/t26_scenario.py`, `t26_metrics.py`, `t26_job.sh`.
Status:     Build DONE (scored 2026-09-17, all three jobs COMPLETED, all criteria PASS). Step-8 energy
            campaign SUBMITTED 2026-09-17: JobID 1329220 (24-task array, S-Revert-std, T21's households),
            PENDING on --dependency=afterany:1328434; not yet collected.

## Design (manager)
- New `impl/T32_scripts/t32_scenario.py` that **imports** `t26_scenario.py` (no edits to T26 files) and adds
  `--jump-basis {primary,std}`; with `std` it uses `compute_standardized_jump` (`t26_scenario.py:146-183`) per slot
  for both slope and jump, λ fixed at 0. Everything else (stock, rake, clamp, writing, validator) is T26's path.
- `t32_job.sh`: array `0-1` (0 = `--jump-basis primary` regression guard, 1 = `--jump-basis std`), same resources
  as `t26_job.sh` (`-c 8 --mem=64G`, `-p ps -t 7-00:00:00`), `%2`. Output `T32/out/guard_primary/`, `T32/out/std/`.
  Inside the job: md5 of the output `BEM_Schedules_2030.csv` and of the T26 λ = 0 file.
- Metrics: G0 guard = share of equal occupancy cells between task 0 and `T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv`
  (must be 1.0; if not, task 1 output is not used). SC1, SC4, SC5 on task 1 as spec §5; reported: weekday at-home
  change and difference from S-Revert (-3.2081 pp, T26 collector). A final dependent job (`afterok`) computes G0
  and the comparison.

## Verified
- Local `py -3 -m py_compile t32_scenario.py t32_metrics.py`: exit 0 each. `bash -n t32_job.sh`,
  `bash -n t32_compare.sh`: exit 0 each.
- Remote byte sizes match local exactly for all 6 staged paths (4 scripts + 2 `.keep`), confirmed via `ls -la`
  before and after `scp -r`.
- Remote `ls -la` confirmed `T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv` (667,043,823 B) and the
  three `T26_scripts/` files this task imports exist with sizes matching T26's own Ledger, before submitting.
- `squeue -u o_iseri` immediately after submission: `1328429_[0-1%2]` PD (AssocGrpCpuLimit — queue full, not
  a dependency problem), `1328430` PD (Dependency on 1328429). Neither job depends on any currently-failing
  chain (unlike T26's own original submission, which sat behind T18/T20).

## Decisions
- **`t32_scenario.py` imports `t26_scenario.py` for the jump/pre_slope computations and `t20_d1.py` directly
  for the stock-rate/write/validate/loader helpers**, both via the same importlib pattern `t26_scenario.py`
  itself uses on `t20_d1.py` — per the task doc's "imports t26_scenario.py ... no edits to T26 files".
  `--scripts-dir` is passed `T26/T26_scripts` at run time (read-only), so no pipeline file is duplicated into
  `T32/`.
- **`lambda` is not exposed as a CLI flag** (task doc: "λ fixed at 0") — `t32_scenario.py`'s target formula
  hardcodes the λ=0 case (`stock_rate + 8*pre_slope - jump`, no `(1-λ)` term), for both `--jump-basis` values.
- **Added `t32_metrics.py`** beyond the task doc's three-file list (`t32_scenario.py`, `t32_job.sh`,
  `t32_compare.sh`) to reuse `t26_metrics.py`'s `sc0_nesting`/`sc1_intended_step`/`sc3_jump_sanity`/
  `sc5_rake`/`rows`/`load_bem` via import rather than re-deriving the same acceptance logic — same "import,
  never edit" principle the task doc applies to `t26_scenario.py`, extended to the metrics half.
- **G0 relabeling**: `t26_metrics.sc0_nesting()` is called unmodified (same function T26 used for its own
  SC0); `t32_metrics.py` only renames the resulting row's `measure` field to `G0_regression_guard` after the
  call, matching the task doc's own name for this check, without touching `t26_metrics.py`.
- **S-Revert comparator value (-3.2081pp) is a literal constant** in `t32_metrics.py`
  (`S_REVERT_WEEKDAY_ATHOME_CHANGE_PP`), taken from T26's own collector table (spec §5's own number), not
  recomputed from T26's output file in this task — matches the task doc's own phrasing ("difference from
  S-Revert (-3.2081 pp, T26 collector)").
- **md5 scope**: `t32_job.sh` records md5 of (a) T26's λ=0.0 comparator file before/after this task's own run
  (read-only leakage guard, since T26 is off-limits to write) and (b) this task's own output
  `BEM_Schedules_2030.csv` once, after it is built (no "before" state exists for a newly written file). This
  is the literal task-doc instruction ("md5 of the output ... and of the T26 λ=0 file"), not T26's fuller
  three-file SC4 pattern (stock/2022-BEM/T20-main-BEM), since this task's own G0 check already re-derives the
  occupancy-cell comparison directly from the CSVs.
- **Resource sizing**: array tasks `-c 8 --mem=64G` (identical to `t26_job.sh`, per task doc Design); compare
  job `-c 2 --mem=32G` (identical to `t26_compare.sh`). `--nice=50` passed on both `sbatch` calls per the
  task doc's own instruction.

## Next
Collector (fresh agent, once 1328429 and 1328430 show COMPLETED in `sacct`): read G0 first
(`t32_metrics_primary.csv` / the compare job's `t32_compare_metrics.csv` `G0_regression_guard` row) — if G0's
share is not 1.0 (100%), the std task's output (task 1) is not used, per the task doc's own rule, and this
becomes a BLOCKED finding for the manager, not a routine reading. If G0 passes: read SC1/SC5 for the std
task (`t32_metrics_std.csv`), and the compare job's own `SC_athome_change_2022_2030` row (S-Revert-std vs
S-Revert -3.2081pp) and its SC5 readout. Tail `slurm_1328429_0.out`, `slurm_1328429_1.out`,
`slurm_compare_1328430.out` for `--- STEP START/OK/FAILED ---` and `[LEAK-GUARD]` lines first. Manager: once
scored, decide whether S-Revert-std feeds a Step-8 energy run (spec §5: "Energy runs: 1,200 Step-8 runs of
2030 on T21's households (T29 addendum)" — already anticipated, not re-decided here).

## WHAT I DID NOT VERIFY
- Did not run any step of `t32_scenario.py`/`t32_metrics.py` on real data — jobs were only just submitted and
  are `PD` (queue-full / dependency) at the time of writing; no evidence yet that `compute_standardized_jump`
  (called here with a full stock read, same as T26's own `--std-jump` path) or the reused `rake_2030`/
  `_joint_act30_rake_2030`/validator calls succeed end-to-end when driven from this new entry point — reasoned
  through every function signature and call site while reading `t26_scenario.py`/`t20_d1.py`, same caveat
  T26's own doc carries, not a measurement.
- Did not verify G0 will actually reach share=1.0 — reasoned that `stock_rate` comes from the same imported
  `t20.compute_stock_rate` call on the same stock file, and `compute_pre_slope_and_jump` is the same function
  T26's own λ=0.0 task called (unedited), so the target arrays should be identical; did not trace the
  `rake_2030` RNG call sequence (`np.random.default_rng(42)`) instruction-by-instruction against T26's own
  call order to rule out any divergence from a different number of preceding random draws — same open risk
  T26's own doc flagged before its run, not newly closed here.
- Did not check Speed disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T32/` before staging —
  two builds each write a full `BEM_Schedules_2030.csv` (T26-scale, ~650+ MB each) plus a person table, on
  top of everything T17-T30 already have on disk.
- Did not confirm whether `1328429`'s array will start promptly given other jobs (T21/T22/T28/T30) already
  running/queued for the same 32-CPU pool — not pollable now since this is a queue-fullness state, not a
  resolvable dependency.
- Did not independently re-verify T26's own λ=0.0 BEM file's content (only confirmed its existence and size
  via `ls -la`) — trusted T26's own doc (collector-scored, ACCEPTED by manager) as the reference.

## Brief (employee, Sonnet)
Login node = `sbatch squeue sacct scancel scontrol cd ls scp module load` + single-file `tail head grep wc -l cat`
ONLY. Never python, never `mkdir`, never `find`, `du`, `md5sum`, `cp`, never blocking `srun`. tcsh: no `2>&1`, no
`2>/dev/null`. ssh `-o BatchMode=yes -o ConnectTimeout=60`. Python on nodes `/speed-scratch/o_iseri/envs/step4/bin/python`.
Remote dirs only by `scp -r` of a local folder with `.keep`. Never write into T17–T31 dirs. Local `py -3 -m py_compile`
only. **Submit and end your turn — never wait.**
1. Read spec §2 and §5, the T26 doc (Decisions, Ledger, collector, addendum), `t26_scenario.py`, `t26_metrics.py`,
   `t26_job.sh`, `t26_compare.sh`.
2. Write `T32_scripts/` (scenario wrapper, job array, compare job); compile.
3. Stage to `/speed-scratch/o_iseri/2J_revision/T32/`; submit the array (`--nice=50`) and the compare job `afterok`.
4. Write Ledger (JobIDs, sbatch lines, paths), Decisions, Next (collector), WHAT I DID NOT VERIFY.

## Ledger
- **Reading (step 1).** Read spec §2 (design rule and trigger) and §5 (S-Revert-std definition and
  acceptance, T26's measured jumps 4.7316pp primary / 7.6673pp standardized), `2026-09-15_T26_wp2_scenario_builds.md`
  in full (Design, Ledger incl. the Nb-f re-point, Decisions, Collector table, Manager addendum that opens T32),
  and `T26_scripts/t26_scenario.py`, `t26_metrics.py`, `t26_job.sh`, `t26_compare.sh` in full (functions reused:
  `compute_pre_slope_and_jump`, `compute_standardized_jump`, `write_targets_csv`, `SCEN_LABEL`/`STRATA`/
  `STRATA_LBL`/`N_SLOTS`/`HOM_COLS` from `t26_scenario.py`; `sc0_nesting`, `sc1_intended_step`, `sc3_jump_sanity`,
  `sc5_rake`, `rows`, `load_bem` from `t26_metrics.py`). Confirmed T26's own `lambda_0.0` output (S-Revert) and
  `T26_scripts/` (`t26_scenario.py` 16,420B, `t20_d1.py` 15,614B, `t26_metrics.py` 9,966B — byte sizes match
  T26's own Ledger exactly) exist on Speed via remote `ls -la` before writing any code (see below).
- **Plug-in decision.** `t32_scenario.py` loads BOTH `t26_scenario.py` and `t20_d1.py` itself via the same
  importlib house pattern (so neither script's own `if __name__=="__main__":` fires), then calls
  `t26.compute_pre_slope_and_jump` (basis=primary) or `t26.compute_standardized_jump` (basis=std) for
  `pre_slope`/`jump`, and `t20.compute_stock_rate`/`write_person_table_csv`/`run_validator`/`_step`/`log`/
  `_require`/`_load_module` exactly as `t26_scenario.py`'s own `main()` does. `--scripts-dir` points directly
  at `T26/T26_scripts` (read-only; T26 is a T17-T31 dir, never written to) — no files copied into `T32/`, so
  `T32_scripts/` holds only the three new files (`t32_scenario.py`, `t32_metrics.py`, `t32_job.sh`,
  `t32_compare.sh` — four, `t32_metrics.py` added beyond the task doc's three-file list to reuse
  `t26_metrics.py`'s functions rather than re-deriving SC0/SC1/SC5 logic; imported, not copied, same pattern).
  `target = clip(stock_rate + 8*pre_slope - jump, 0, 1)` with `lambda` fixed at 0 (no `--lambda` flag): for
  `--jump-basis primary` this is byte-for-byte T26's own λ=0.0 formula (same `compute_stock_rate` function,
  same stock/diaries files) — the mechanical basis for the G0 regression guard; for `--jump-basis std`,
  `pre_slope`/`jump` come from `t26.compute_standardized_jump` instead (spec §5: standardized slope AND jump,
  unlike T26's own `--std-jump` flag which only ever reported these, never fed them into a target).
- **Local compile.** `py -3 -m py_compile t32_scenario.py t32_metrics.py` — exit 0 each. `bash -n t32_job.sh`,
  `bash -n t32_compare.sh` — exit 0 each. None run locally on real data.
- **Staging (scp, foreground, no login-node python/find/du/md5sum).** Local staging folder built in
  scratchpad (`T32_stage/T32/T32_scripts/`: the four new files; `T32/logs/.keep`, `T32/out/.keep` so the
  SLURM `--output` dir and the job's own `out/` tree exist before submit). `scp -r` to
  `/speed-scratch/o_iseri/2J_revision/T32/` (exit 0). Remote `ls -la` confirmed byte-for-byte matches: local
  vs remote — `t32_scenario.py` 8,103B, `t32_metrics.py` 5,749B, `t32_job.sh` 5,366B, `t32_compare.sh` 2,172B,
  both `.keep` files 0B. No T17-T31 directory written to (T26 read via absolute paths only; only `T32/` was
  staged into).
- **Pre-submission check.** Remote `ls -la` confirmed `T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv`
  exists (667,043,823 B, the G0 comparator) and `T26/T26_scripts/{t26_scenario.py,t20_d1.py,t26_metrics.py}`
  exist with sizes matching T26's own Ledger — both needed before submitting, both present, no dependency
  needed on any earlier job (T26 is DONE per its own doc).
- **JobID 1328429** — `t32_scenario` array (`--array=0-1%2`, `-c 8 --mem=64G`, from `t32_job.sh`'s own
  `#SBATCH` header), submitted `sbatch --nice=50 -p ps -t 7-00:00:00 T32_scripts/t32_job.sh` from
  `/speed-scratch/o_iseri/2J_revision/T32/`. Task 0 = `--jump-basis primary` (G0 regression guard vs T26
  λ=0.0), task 1 = `--jump-basis std` (S-Revert-std); both run `--validate`. Output:
  `T32/logs/slurm_1328429_<task>.out`; per-task artifacts under `T32/out/guard_primary/` and `T32/out/std/`
  (`t32_targets_<basis>.csv`, `t32_person_table_<basis>.csv`, `BEM_Setup/BEM_Schedules_2030.csv`,
  `t32_metrics_<basis>.csv`, `md5_t26_revert_{before,after}.txt`, `md5_own_output.txt`,
  `outputs_step7/step7_validation_report_2030_v2.html`). `squeue` immediately after submit:
  `1328429_[0-1%2]` `PD (AssocGrpCpuLimit)` — queue is full from other running jobs (T21/T22/T28/T30), not a
  dependency block; this array has no `--dependency` (T26 is already DONE, unlike T26's own chain which
  waited on T20).
- **JobID 1328430** — `t32_compare` (single job, `-c 2 --mem=32G`, from `t32_compare.sh`'s own `#SBATCH`
  header), submitted `sbatch --dependency=afterok:1328429 --nice=50 -p ps -t 7-00:00:00
  T32_scripts/t32_compare.sh`. Computes G0 (task 0 vs T26 λ=0.0), the S-Revert-std weekday at-home change and
  its difference from S-Revert (-3.2081pp, T26 collector, not recomputed), and SC5 readout on the std targets/
  person-table. `squeue` immediately after: `1328430` `PD (Dependency)`. Output:
  `T32/logs/slurm_compare_1328430.out`, `T32/out/t32_compare_metrics.csv`.
- **CPU-cap check** (`squeue -u o_iseri` immediately after both submissions): running = `1328422_[0-1]`(2x8=16
  via T21) + `1328310_[12-13]`(2x2=4, T22) + `1328419_[0-1]`(2, T30) + `1328415_0`(1, T28) — this task's own
  jobs (`1328429`, `1328430`) both sat `PD` (queue-full / dependency), none of ours exceeded 32 running CPUs
  at submission time. T17-T31 dirs untouched by this task (T26 read-only via absolute paths in `t32_job.sh`/
  `t32_compare.sh`; only `T32/` written).
- **1328429_0** (`t32_scenario`, `--jump-basis primary`, guard) — `sacct`: COMPLETED, exit 0:0, elapsed
  00:29:18. Output: `T32/out/guard_primary/` (`BEM_Setup/BEM_Schedules_2030.csv` 6,934,320 rows / 144,465 HH,
  `t32_metrics_primary.csv`, `t32_person_table_primary.csv`, `t32_targets_primary.csv`, both md5 files,
  `outputs_step7/`). Log `T32/logs/slurm_1328429_0.out` (203 lines).
- **1328429_1** (`t32_scenario`, `--jump-basis std`, S-Revert-std) — `sacct`: COMPLETED, exit 0:0, elapsed
  00:16:01. Output: `T32/out/std/` (`BEM_Setup/BEM_Schedules_2030.csv` 6,934,320 rows / 144,465 HH,
  `t32_metrics_std.csv`, `t32_person_table_std.csv`, `t32_targets_std.csv`, both md5 files,
  `outputs_step7/`). Log `T32/logs/slurm_1328429_1.out` (198 lines).
- **1328430** (`t32_compare`) — `sacct`: COMPLETED, exit 0:0, elapsed 00:00:36. Output:
  `T32/out/t32_compare_metrics.csv` (5 rows). Log `T32/logs/slurm_compare_1328430.out` (22 lines).

## Verified (collector pass, 2026-09-17)
- **G0, the guard — PASS.** Two independent lines of evidence, both from files actually on disk:
  1. md5 of `T32/out/guard_primary/BEM_Setup/BEM_Schedules_2030.csv` = `2606a9f830ec927d36464e8033834ab0`
     (`out/guard_primary/md5_own_output.txt`), identical to md5 of
     `T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv` = `2606a9f830ec927d36464e8033834ab0`, taken both
     before (`md5_t26_revert_before.txt`) and after (`md5_t26_revert_after.txt`) the run for both tasks 0 and
     1 — full-file byte-for-byte match, and confirms T26's file was never touched (`[LEAK-GUARD] PASS: T26
     lambda=0.0 reference unchanged`, `slurm_1328429_0.out:177`, `slurm_1328429_1.out:173`).
  2. `t32_compare_metrics.csv` row `G0_regression_guard,both,share_pct,100.0`: "6,934,320/6,934,320 cells
     exactly equal" from a cell-by-cell join on `SIM_HH_ID+Day_Type+Hour` between `T32/out/guard_primary/...`
     and `T26/out/lambda_0.0/...` (`slurm_compare_1328430.out` input-check steps confirm these are the two
     files actually diffed).
  - **Caveat, not a fault:** the row's own text note reads "lambda=1.0 vs T20 main" — that is `t26_metrics.
    sc0_nesting()`'s original hardcoded label (written for T26's own SC0 check), reused unmodified per the
    Decisions above and never restated for G0's actual comparison. The label is stale/misleading; the file
    paths in the log and the two independent md5s confirm the comparison itself is the correct one
    (guard_primary vs T26 lambda_0.0). Recorded here so no one re-reads this note and thinks the wrong files
    were compared.
- **SC1 — PASS (both tasks).** `t32_metrics_std.csv`: design target (mean of `target_std - stock_2022` over
  the 48 weekday slots) = -8.3274 pp; measured national weekday at-home change 2022->2030 = -8.3154 pp
  (`SC1_national,weekday,S-Revert-std`) → |diff| = 0.012 pp, inside the 0.5 pp band. `t32_metrics_primary.csv`
  (guard task, not required by spec but consistent): target -3.225 pp vs measured -3.2081 pp → |diff| =
  0.017 pp, also inside band.
- **SC4 — PASS (both tasks), on the established reading.** Validator: `30 PASS / 1 WARN / 0 FAIL` for both
  tasks (`slurm_1328429_0.out:165`, `slurm_1328429_1.out:161`); the one WARN is `[WARN] 6.x | classic backup
  absent — regression skipped` in both, not a data problem. Row count 6,934,320 and unique households
  144,465 match the expected counts in both tasks' validator output (`_0.out:90-95`, `_1.out:90-95` block).
  Spec text literally says "Validator 28/28" — the validator has grown to 31 checks; T26's own doc already
  raised and closed this exact mismatch (`2026-09-15_T26_wp2_scenario_builds.md:332-333`: "28/28 is a stale
  count... the intent is no FAIL"), and T32 reproduces the identical 30/1/0 pattern, so this is not a new
  finding, just confirmation the same reading applies. Household-ID identity with Arm N 2022 is not
  independently re-derived in this task; it rests on the G0 join (which fixes guard_primary's `SIM_HH_ID` set
  equal to T26's, itself validated against Arm N by T26/T20) — see gap below.
- **SC5 — PASS (both tasks).** `t32_compare_metrics.csv` / both per-task metrics files agree: WD max abs
  diff 0.0002 pp, Sat 0.0012 pp, Sun 0.0012 pp — all far under the 0.5 pp flag, "0/48 slots > 0.5 pp" in
  every stratum for both tasks.
- **Reported numbers (compare job, `t32_compare_metrics.csv`):** S-Revert-std weekday at-home change
  2022->2030 = -8.3154 pp; difference from S-Revert (-3.2081 pp, T26 collector, not recomputed) = -5.1073 pp
  (S-Revert-std falls much further than S-Revert, as expected since the standardized jump, 7.6673 pp, is
  larger than the primary jump, 4.7316 pp — `t32_metrics_std.csv` / `t32_metrics_primary.csv` SC3 rows).

## Next (collector pass, 2026-09-17)
All four criteria (G0, SC1, SC4, SC5) PASS on the numbers above. Manager to brief the 1,200 S-Revert-std
Step-8 energy runs for 2030, using T29's fixed-manifest wrapper on the same households as T21 (spec §5,
"Energy runs: 1,200 Step-8 runs of 2030 on T21's households (T29 addendum)"). No job submitted in this task.

## Ledger (2026-09-17, S-Revert-std Step-8 campaign submitted)
- **Read** this doc's Ledger/Verified/Next (above) and `2026-09-15_T29_wp2_scenario_step8_runs.md` in full
  (Design, Manager addendum 2, Ledger "phase B submitted -- fixed-manifest wrapper", "Verified (2026-09-17,
  smoke re-verified)"). Identified `impl/T29_scripts/run_fixed_manifest.py` as T29's fixed-manifest wrapper:
  built from a copy of `run_paired_mc.py`, takes `--manifest <T21 Step-8 cell_manifest.csv>` and simulates
  exactly those `(sample, sim_hh_id)` rows, in order, for year 2030 only, on whatever `--sched-dir` schedule
  file is given -- never draws a fresh sample. Reused verbatim (byte-identical copy, no edits): local
  `wc -c` = 12,496 B for both `T29_scripts/run_fixed_manifest.py` and the new staged copy.
- **Wrote `impl/T32_scripts_step8/` (local staging only; remote path `T32/step8_std/scripts/`)**:
  `t32_step8_array.sh`, new 24-task array script, adapted line-for-line from `T29_scripts/t29_array.sh`'s
  own invocation pattern (same `ARCHS`/`CITIES`/cell-order arrays, same wrapper call shape), plus a
  byte-identical copy of `run_fixed_manifest.py`. `bash -n t32_step8_array.sh` -> exit 0;
  `py -3 -m py_compile run_fixed_manifest.py` -> exit 0 (both local, this session).
- **Staged** via `scp -r` of a local folder (`T32/step8_std/{logs/.keep, out/.keep, scripts/{run_fixed_manifest.py,
  t32_step8_array.sh}}`) to `/speed-scratch/o_iseri/2J_revision/T32/step8_std/` (new subdirectory under this
  task's own `T32/` root -- not another task's directory). Remote `ls -la` confirmed byte-for-byte match:
  `run_fixed_manifest.py` 12,496 B, `t32_step8_array.sh` 6,753 B (both local vs remote). A stray
  `scripts/__pycache__/run_fixed_manifest.cpython-313.pyc` (16,170 B) rode along from the local
  `py -3 -m py_compile` run (it lives next to the source file); harmless leftover bytecode, not used by the
  cluster's own `/speed-scratch/o_iseri/envs/step4/bin/python`, could not be removed (no `rm` on the login
  node) -- noted here so it is not mistaken for a real artifact.
- **Pre-submission checks (all read-only, login node, allowed):**
  - `T32/out/std/BEM_Setup/BEM_Schedules_2030.csv` exists, 667,351,503 B (this task's own S-Revert-std build,
    G0/SC1/SC4/SC5 all PASS per the collector pass above).
  - `T21/out/step8/SingleD__Montreal_6A/cell_manifest.csv` exists, 1,387 B, and its row
    `1,130228,1,SingleD,Quebec` is present -- confirms this file is T21's REBUILT seed-42 draw (household
    130228 at sample 1), the same file T29's own 2026-09-17 smoke re-verification confirmed, NOT the stale
    published pair (130322/80058). This is the exact manifest path `t32_step8_array.sh`'s `$MANIFEST` points
    at for every cell.
  - `T21/out/step8/` lists 25 entries (24 cell directories; T21's Step-8 array 1328422 finished after this
    task's own G0/SC1/SC4/SC5 collector pass).
  - `/speed-scratch/o_iseri/2J_revision/code_step8/repo/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py`
    exists (120,117 B) -- the shared Step-8 code tree `run_fixed_manifest.py`'s `--code-root` resolves
    against.
- **Job script confirmed by eye before submitting** (`cat` of the staged `t32_step8_array.sh` from Speed):
  `#SBATCH --partition=ps`, `--time=7-00:00:00`, `--array=0-23%2`, `--cpus-per-task=4`, `--mem=16G`,
  `--output=.../T32/step8_std/logs/t32_step8_%x_%A_%a.out` (directory just staged and confirmed to exist).
  `--dependency` is a submit-time flag (same pattern as every other array in this project), confirmed via
  `squeue` immediately after submission (below), not embedded in the header.
- **JobID 1329220** -- `t32_step8_std`, submitted from `/speed-scratch/o_iseri/2J_revision/T32/step8_std/scripts`:
  `sbatch -p ps -t 7-00:00:00 --dependency=afterany:1328434 t32_step8_array.sh`. `squeue -j 1329220`
  immediately after: `1329220_[0-23%2]` `PD (Dependency)` -- correct and expected, not a problem. At
  submission, `1328434` (`t29_revert`) showed tasks 20/21 `R` (running) and `22-23%2` `PD
  (JobArrayTaskLimit)`, i.e. genuinely still in flight, so the dependency has real work to wait for.
  Output: `T32/step8_std/logs/t32_step8_std_1329220_<task>.out`; per-cell artifacts under
  `T32/step8_std/out/<cell>/` (`cell_manifest.csv`, `undelivered.csv`,
  `sample_NNN_HH<id>/2030/hourly_meters.csv` per delivered household, per `run_fixed_manifest.py`'s own
  output layout).
- No job was waited on or polled beyond the single immediate `squeue` snapshot above (no-parking rule).

## Verified (2026-09-17, S-Revert-std campaign submission)
- **Fixed-manifest wrapper identity confirmed two ways**: (a) the staged `run_fixed_manifest.py` is a
  byte-identical copy of T29's own already-run, already-verified wrapper (12,496 B both sides, `wc -c`);
  (b) `$MANIFEST` in `t32_step8_array.sh` points at the exact same path (`T21/out/step8/<cell>/
  cell_manifest.csv`) T29's own array used, and a direct read of one such file
  (`SingleD__Montreal_6A/cell_manifest.csv`) shows household 130228 at sample 1 -- the rebuilt seed-42 draw
  T29's smoke re-verification (2026-09-17, this doc's sibling `2026-09-15_T29_wp2_scenario_step8_runs.md`,
  "Verified" section) confirmed by name, not the stale published pair (130322/80058). No fresh sampling path
  was written; the wrapper's own top-level loop (`read_fixed_manifest` -> iterate in order -> `inject_schedules`)
  is unedited from T29's copy.
- **SBATCH settings confirmed by eye** from the `cat`-back of the staged script on Speed: `--partition=ps`,
  `--time=7-00:00:00`, `--cpus-per-task=4`, `--array=0-23%2`, output directory pre-staged. `--dependency=
  afterany:1328434` confirmed via the `sbatch` command line used and the immediate `squeue -j 1329220`
  showing `PD (Dependency)`.
- **Input files confirmed present on Speed before submitting** (read-only `ls`/`grep`): T32's own
  S-Revert-std schedule file, T21's Step-8 manifest for the test cell (with the expected household ID), and
  the shared `code_step8/repo` tree's `main.py` (see Ledger above for exact paths/sizes).

## Decisions (2026-09-17, S-Revert-std campaign submission)
- **CPU ceiling (manager decision, restated here for the record).** The account's 32 CPUs newly freed by the
  64-CPU raise are reserved for a different project and are off-limits to 2J. The four live 2J arrays already
  summed to exactly 32 CPUs (T22 2x4, T28 1x8, T29-revert 2x4, T30 2x4). This array (`--cpus-per-task=4`,
  `--array=...%2` = max 8 CPUs in flight) was therefore submitted with `--dependency=afterany:1328434` (the
  T29 revert array, which frees exactly 8 CPUs on completion) so the 32-CPU ceiling holds without babysitting.
  `%2` and `--cpus-per-task=4` were not raised, per the manager's explicit instruction that this is not the
  employee's call to optimise.
- **`--sched-dir` points directly at T32's own `out/std/BEM_Setup/` output, no copy made** (departs from
  T29's own pattern of staging a copy of T26's files into `T29/sched_lambda_<v>/`). T32's build output
  directory already contains only the plain-named `BEM_Schedules_2030.csv` the wrapper's `--sched-dir`
  expects, T32 is this task's own directory (not another task's, so read-only use is not a rule violation),
  and the wrapper never writes into `--sched-dir` -- so a ~650MB duplicate copy job was judged unnecessary.
  Recorded here as a deviation from precedent, not an unstated shortcut.
- **`afterany`, not `afterok`, was used on 1328434.** The manager's instruction named `afterany:1328434`
  explicitly (not `afterok`); followed as given. This means the array will fire once 1328434 reaches ANY
  terminal state, including a failure -- unlike T29's own internal chain, which used `afterok` throughout.
  This is the manager's stated choice (CPU-freeing dependency, not a correctness dependency on 1328434's own
  exit code), not re-litigated here.
- **No new collector script was written in this task.** The task brief asked only for staging, submission,
  and the doc updates below; scoring the campaign (P0-P5-style checks, reusing `t29_check.py`'s logic
  adapted for a single "std" scenario and compared against S-Revert per spec §5) is left to the collector
  named in Next below.

## Next (2026-09-17, for the collector)
Fresh agent, once `sacct -j 1329220` shows all 24 tasks in a terminal state: first check `1328434`'s own
final state (`sacct -j 1328434`) -- since the dependency was `afterany` not `afterok`, confirm 1328434
actually finished cleanly (24/24 COMPLETED, exit 0:0) before trusting this array's own CPU-budget premise
was sound (it does not gate correctness of 1329220's own runs, only the CPU-ceiling reasoning above). Then
read each cell's own log (`T32/step8_std/logs/t32_step8_std_1329220_<task>.out`) for `DONE .../ E+ <n>/50 ok`
and any `undelivered.csv` rows; read each cell's `T32/step8_std/out/<cell>/cell_manifest.csv` (should list
the same 50 `(sample, sim_hh_id)` pairs as `T21/out/step8/<cell>/cell_manifest.csv`, order-preserving, per
P1 in T29's own acceptance) and `undelivered.csv` (expected empty or near-empty). Once P0/P1 read clean,
compute P2/P3-style comparisons against this doc's own S-Revert-std targets (`t32_metrics_std.csv`,
`t32_compare_metrics.csv`) and against T29's own S-Revert (lambda=0.0) Step-8 output
(`T29/out/lambda_0.0/<cell>/`) per spec §5's own comparison intent -- reusing `t29_check.py`'s metric
definitions (file:line already recorded in the T29 doc's own Verified section) rather than rederiving them.
Manager: decide the exact collector script (new `t32_step8_check.py` vs. a parameterised rerun of
`t29_check.py`) once the array actually completes.

## WHAT I DID NOT VERIFY (2026-09-17, S-Revert-std campaign submission)
- Did not wait for or poll 1329220 -- submitted and moved on, per the no-parking rule. Whether any of the 24
  cells actually deliver valid `hourly_meters.csv` output is unread.
- Did not run `run_fixed_manifest.py` against T32's S-Revert-std schedule file this session -- reused it
  unedited on the strength of T29's own already-COMPLETED runs (1328433/1328434, 24/24 each, exit 0:0) using
  the identical code path against T26's schedule files; T32's file has a different byte size (667,351,503 B
  vs T26's per-lambda files) and has not itself been run through this wrapper before.
- Did not check the other 23 cells' `T21/out/step8/<cell>/cell_manifest.csv` for the correct rebuilt
  household draw -- only `SingleD__Montreal_6A` was read directly; the other 23 are trusted on the strength
  of T21's Step-8 array (1328422) and T29's own two 24-task arrays (1328433/1328434, both 24/24 COMPLETED)
  having already consumed all 24 of these same manifest files successfully.
- Did not check Speed disk quota/free space before this submission -- same gap every T2x/T3x doc in this
  project has recorded; 1,200 more `hourly_meters.csv`/E+ output sets add non-trivial space on top of
  everything already on disk.
- Could not remove the stray `__pycache__/run_fixed_manifest.cpython-313.pyc` that rode along in the `scp -r`
  (no `rm` allowed on the login node) -- left in place; it is inert (Python only reads a `.pyc` for the exact
  source path/mtime it was built from locally, which does not match the remote layout, so it will not be
  used, only ever silently ignored or regenerated).
- Did not verify `1328434`'s own final exit state before submitting (it was still 20/24 complete, 2 running,
  2 queued, per the manager's own briefing and the `squeue` snapshot at submission time) -- the
  `--dependency=afterany:1328434` mechanism itself, not this task, is what makes 1329220 wait for it.

## WHAT I DID NOT VERIFY (collector pass, 2026-09-17)
- **Seen-failing gap.** Neither this doc nor T26's own doc records any run of `sc0_nesting`/G0,
  `sc1_intended_step`, `sc5_rake`, or `BEMIntegrationValidator` against a deliberately broken/fake input to
  confirm the check can actually catch a real problem. Every PASS above rests on functions never demonstrated
  to fail on a bad case — flagging per project rule, not treating any of the PASSes above as unconditional.
- Did not independently md5-snapshot Arm N 2022's own output file or T20 `main`'s own output file
  before/after this task's run (only T26's `lambda_0.0` file was leak-guarded, per this doc's own Decisions
  section) — "Arm N and T20 outputs md5 unchanged" (spec SC4) is inferred from T32's scripts only ever
  reading those paths (input-check steps only, no write calls to those directories), not from a direct
  before/after hash.
- Did not re-derive the G0 100%/6,934,320-cell figure from the raw CSVs myself — forbidden tools on the
  login node (no python, no md5sum invocation beyond reading the job's own pre-written md5 text files).
  Relied on the job's own printed cell-join count plus two independently-taken, agreeing md5s of the full
  667 MB files.
- Did not open either `outputs_step7/step7_validation_report_2030_v2.html` file (Step-7 validation report)
  — relied on the SLURM log's own validator printout, not the HTML report content.
- SC2 (order Revert < Partial < Persist) does not apply here: spec §5 explicitly builds no S-Partial-std, so
  there is nothing to order-check for the standardized family.
