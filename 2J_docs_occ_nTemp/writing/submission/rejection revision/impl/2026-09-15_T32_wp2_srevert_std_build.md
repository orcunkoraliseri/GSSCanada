# T32 — WP2 S-Revert-std schedule build on Speed — implementation state
Task doc:   this file. Spec: `2026-09-15_WP2_scenario_spec.md` §5 (definition and acceptance, fixed).
Code base:  `2026-09-15_T26_wp2_scenario_builds.md`, `T26_scripts/t26_scenario.py`, `t26_metrics.py`, `t26_job.sh`.
Status:     SUBMITTED

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
