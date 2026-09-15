# T26 — WP2 scenario schedule builds (S-Persist nesting, S-Partial, S-Revert) on Speed — implementation state

Task doc:   this file. Spec: `2026-09-15_WP2_scenario_spec.md` (design, acceptance SC0–SC5, fixed). Code base:
`2026-09-15_T20_wp1_d1_2030_build.md` + `T20_scripts/t20_d1.py`, `t20_metrics.py`, `t20_job.sh`. Stock and 2022
reference: T18 Arm N (T18 doc Ledger/Decisions).
Status:     DONE (Nb-f stock) — 1328377/1328379 COMPLETED 0:0, SC0-SC5 scored 2026-09-15

## Design (manager)
- New script `impl/T26_scripts/t26_scenario.py` that **imports** `t20_d1.py` functions (no copy-paste
  drift) and adds only: computing `jump[s,t]` as in `06_forecast_rake.py:130,150-161` (`obs_2022 − trend(2022)`,
  same polyfit), `--lambda` (1.0, 0.5, 0.0), and the target formula of spec §2. If `t20_d1.py` is not
  importable as is, record why and copy the minimum with a citation; do not edit T20's staged files.
- Standardized-jump sensitivity (spec §2), printed and written as JSON, not used in the target.
- `t26_metrics.py`: SC0 (λ = 1 vs T20 `main` 2030 file, share of equal occupancy cells), SC1, SC2 (after all
  three tasks, so run it in a final dependent job), SC3, SC5, SC4 md5 of the Arm N and T20 outputs before/after.
- `t26_job.sh`: array `0-2` (0 = λ 1.0, 1 = λ 0.5, 2 = λ 0.0), `-c 8 --mem=64G %2`, validator
  `07_bemIntegrationGSS_val.py` on each output (as T20 task 1 does). Output `T26/out/lambda_<v>/`.
  Then `t26_compare.sh` (`-c 2 --mem=32G`) with `--dependency=afterok:<array>` for SC1/SC2/SC3 across tasks.
- Submit the array with `--dependency=afterok:1328311` (T20 array). If T20 fails, nothing runs.

## Brief (employee, Sonnet)
Rules identical to T20 (login node = submit/inspect only, never python/find/du/md5sum there; `-p ps
-t 7-00:00:00`; ssh `-o BatchMode=yes -o ConnectTimeout=60`; tcsh, no `2>&1`; remote dirs by `scp -r`;
python `/speed-scratch/o_iseri/envs/step4/bin/python`; our jobs ≤ 32 CPUs, let the queue hold the rest;
never write into T17/T18/T19/T20/T22 dirs; no edits to existing repo files; local `py -3 -m py_compile` only).
**Submit and end your turn — never wait.**
1. Read the spec, the T20 doc (all of it), `t20_d1.py`, `t20_metrics.py`, `t20_job.sh`, `06_forecast_rake.py:100-183`.
   Record under Decisions how `t26_scenario.py` plugs into `t20_d1.py` and every path.
2. Write `impl/T26_scripts/` files above; compile locally.
3. Stage to `/speed-scratch/o_iseri/2J_revision/T26/` by `scp -r`; submit array (dependency on 1328311) and the
   compare job (dependency on the array). Ledger: JobIDs. Status SUBMITTED. End turn.

## Ledger
- **Reading (step 1).** Read the spec (design/§2 target formula, §3 acceptance SC0-SC5, §4 order), the T20
  doc in full (Design, Ledger, Decisions, Next, WHAT I DID NOT VERIFY), `t20_d1.py` in full (`compute_stock_rate`
  `:136-148`, `compute_pre_slope` `:151-159`, `build_2030_table` `:162-212` — the rake + `_joint_act30_rake_2030`
  call this task's own rake step mirrors, `write_person_table_csv` `:227-231`, `run_validator` `:234-258`,
  `main()` `:261-330` — the monkeypatch-`assemble_2030` pattern reused as-is), `t20_metrics.py` in full (the
  `rows()`/`load_bem()` helpers and `r_rake()` `:146-166` this task's `SC5_rake` copies), `t20_job.sh` in full
  (array/mode mapping, input-check + SC4-precedent md5-before/after pattern, `--validate` only on task 1 there —
  T26 differs: validator runs on every task, per this task doc's own design line), and
  `06_forecast_rake.py:100-183` (`compute_observed_marginals` `:100-123`, `project_to_2030` `:138-183` — noted
  its 3rd return value is a literal `None`, not an intercept, `:183`, which is why `t26_scenario.py` reruns the
  polyfit itself rather than calling `project_to_2030`). Read `06_forecast_rake.py:228-294` (`rake_2030`) and
  `:533-603` (`_load_postlink_rake_module`, `_load_2022_obs_reference`, `_joint_act30_rake_2030`) since T26 calls
  these directly (same as `t20_d1.build_2030_table` does), not through a copy. Confirmed via local `head`
  (never on Speed) that `outputs_step4/augmented_diaries.csv` carries `AGEGRP,SEX,LFTAG` columns (needed for the
  standardized-jump sensitivity) and that the Arm N stock schema
  (`0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`, same schema T18's Arm N
  output uses) carries `AGEGRP,SEX,LFTAG,DTYPE,BEDRM` too — both needed for the reweighting. Read the T18 doc
  (Ledger + Decisions) for the Arm N Speed paths T26 reads: stock =
  `T18/arm_N/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`, diaries (full) =
  `T18/input/augmented_diaries.csv`, Arm N 2022 BEM = `T18/arm_N/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv`.
- **Plug-in decision (Decisions has the full text).** `t26_scenario.py` loads `t20_d1.py` itself as a module via
  the same importlib house pattern `t20_d1.py` uses on the pipeline scripts (so `t20_d1.py`'s own
  `if __name__=="__main__":` never fires), then calls `t20.compute_stock_rate`, `t20.write_person_table_csv`,
  `t20.run_validator`, `t20._step`, `t20.log`, `t20._require`, `t20._load_module` directly — no copy-paste. The
  ONE piece it could not reuse from `t20_d1.py` is the rake+act30 sequence, because that logic is inlined inside
  `t20_d1.build_2030_table()` (which always derives `target` internally from mode `null`/`main`, not from an
  external target array) — so `t26_scenario.py` calls `06_forecast_rake.py`'s own `rake_2030()` and
  `_joint_act30_rake_2030()` directly (imported, unedited, same as `t20_d1.py` itself does), passing this task's
  own `target_lambda` array. This is not a copy of `t20_d1.py`'s code, it is the same two library calls
  `t20_d1.py` also makes, called independently with a different target.
- **Staging (scp, foreground, no login-node python/find/du/md5sum).** Local staging folder built in scratchpad
  (`T26_stage/T26/T26_scripts/`): `t26_scenario.py`, `t26_metrics.py`, `t26_job.sh`, `t26_compare.sh` (new, this
  task) plus copies of `t20_d1.py` (from `T20_scripts/`, needed because `t26_scenario.py` imports it) and
  `06_forecast_rake.py`, `05_postlink_rake.py`, `07_aug_to_bem.py`, `07_bemIntegrationGSS_val.py`,
  `activity_loads.py` (from the live repo, same source paths T20 used). Byte sizes verified equal to the live
  repo/T20 staging before transfer (`ls -la`): the 5 shared pipeline files are byte-identical to T20's own
  staged copies (`05_postlink_rake.py` 44,456 B; `06_forecast_rake.py` 34,438 B; `07_aug_to_bem.py` 13,246 B;
  `07_bemIntegrationGSS_val.py` 53,721 B; `activity_loads.py` 11,530 B; `t20_d1.py` 15,614 B — all match T20's
  Ledger exactly). New files: `t26_scenario.py` 16,420 B; `t26_metrics.py` 9,966 B; `t26_job.sh` 5,352 B;
  `t26_compare.sh` 1,511 B. `scp -r` to `/speed-scratch/o_iseri/2J_revision/T26/` (exit 0); remote `ls -la`
  confirmed every size matches exactly. No T17/T18/T19/T20/T22 directory written to (only read, and only via
  paths the sbatch script resolves at run time — the staging itself touched only the new `T26/` tree).
- 🔴 **Pre-submission `squeue` check found T18's own chain array (`1328301_0`/`1328301_1`) in state
  `FAILED` (`sacct -j 1328300,1328301`: `1328300` `t18_filter` COMPLETED 0:0; `1328301_0` and `1328301_1`
  `t18_chain` **FAILED 1:0** both). Consequently T20's array (`1328311_[0-1]`) already sat in `squeue` as
  `PD` with reason `DependencyNeverSatisfied` (its own `--dependency=afterok:1328301` can never be met) —
  T20 has not run and will not run as currently queued. This task's own instruction is to submit T26's array
  with `--dependency=afterok:1328311` regardless (spec §4/design: "If T20 fails, nothing runs" is the
  explicitly anticipated outcome), so T26 was submitted exactly as briefed; it will sit `PD`/`Dependency`
  behind `1328311` indefinitely unless the manager re-runs or fixes T18/T20 (not this task's scope, and T18/T20
  dirs are off-limits per the rules). Not investigated further (T18/T20 failure root cause is outside T26's
  brief) — flagged here for the collector/manager, not fixed.**
- **JobID 1328326** — `t26_job` array (`--array=0-2%2`, `-c 8 --mem=64G`, from `t26_job.sh`'s own `#SBATCH`
  header), submitted `sbatch --dependency=afterok:1328311 -p ps -t 7-00:00:00 T26_scripts/t26_job.sh` from
  `/speed-scratch/o_iseri/2J_revision/T26/`. Task 0 = λ 1.0 (S-Persist, runs `--std-jump` + SC0 vs T20 main),
  task 1 = λ 0.5 (S-Partial), task 2 = λ 0.0 (S-Revert); all three tasks run `--validate` (validator on each
  output, per this task doc's design line, unlike T20 where only the `main` task validated). State at
  submission: **PENDING**, `squeue` reason `Dependency` (immediately after submit, before checking again —
  its true blocking state inherits from `1328311`'s own `DependencyNeverSatisfied`, see finding above).
  Output: `T26/logs/slurm_1328326_<task>.out`; per-λ artifacts under `T26/out/lambda_<v>/`
  (`t26_targets_lambda_<v>.csv`, `t26_person_table_lambda_<v>.csv`, `BEM_Setup/BEM_Schedules_2030.csv`,
  `t26_metrics_lambda_<v>.csv`, `sc4_md5_*_{before,after}.txt`, `outputs_step7/step7_validation_report_2030_v2.html`,
  and for task 0 only `t26_std_jump_sensitivity.json`).
- **JobID 1328327** — `t26_compare` (single job, `-c 2 --mem=32G`, from `t26_compare.sh`'s own `#SBATCH`
  header), submitted `sbatch --dependency=afterok:1328326 -p ps -t 7-00:00:00 T26_scripts/t26_compare.sh`.
  Runs SC2 (order check) across all three λ outputs, after the array. State at submission: **PENDING**,
  `squeue` reason `Dependency`. Output: `T26/logs/slurm_compare_<jobid>.out`, `T26/out/t26_compare_metrics.csv`.
- CPU-cap check (`squeue -u o_iseri`) immediately after both submissions: running = `1328310_2`(2) +
  `1328310_3`(2) + `1328286_2`(8, T17 array) = 12 CPUs running; `1328326_[0-2%2]` (this job, throttled to 2
  concurrent tasks x 8 CPUs = 16 max), `1328327`, `1328311_[0-1]`, `1328290`, `1328310_[4-23%2]` all PENDING
  behind dependencies or the array-task limit — none of ours exceeded 32 running CPUs at submission time.
  T17/T18/T19/T20/T22 dirs untouched by this task (read-only references in `t26_job.sh`/`t26_compare.sh`, all
  under `T26/` written).

## Verified
- `t26_scenario.py` and `t26_metrics.py` pass `py -3 -m py_compile` locally (exit 0 each); `t26_job.sh` and
  `t26_compare.sh` pass `bash -n` (exit 0 each). None run locally on big files.
- Confirmed via local `head -c ... | head -1` (never a full read, never on Speed) that
  `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv`'s header carries `AGEGRP,SEX,LFTAG` (needed for the
  standardized-jump sensitivity's reweighting) and that
  `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`'s header (same schema
  as the Arm N stock T26 reads on Speed) carries `AGEGRP,SEX,LFTAG,DTYPE,BEDRM` at columns 542-550 — both
  confirmed present before the standardization code was written, not assumed.
- Confirmed local vs remote byte sizes match exactly for all 10 staged files (see Ledger) — no
  truncation/corruption in transfer.
- Confirmed via `sacct -j 1328300,1328301` (read-only, allowed on login node) that T18's chain array failed
  (see 🔴 finding above) — this is a measurement, not an assumption, and is why T20/T26 will not progress as
  currently queued.

## Decisions
- **`t26_scenario.py` imports `t20_d1.py` as a module (importlib house pattern) rather than copying any of
  its code**, per the task doc's own instruction. `compute_stock_rate`, `write_person_table_csv`,
  `run_validator`, `_step`, `log`, `_require`, `_load_module` are called from the loaded module unmodified.
  This guarantees `stock_rate[s,t]` at λ=1.0 is byte-identical to T20 main's own `stock_rate` (same function,
  same stock file) — the mechanical basis for SC0 nesting, not just a design intention.
- **`jump[s,t]` is NOT obtained by calling `06_forecast_rake.py`'s `project_to_2030()`.** That function's own
  3rd return value (the slot t20_d1.py's own comment calls "intercepts") is a literal `None`
  (`06_forecast_rake.py:183`), so the intercept needed for `trend(2022) = slope*2022+intercept` is not
  recoverable from it. `t26_scenario.py.compute_pre_slope_and_jump()` reruns the identical
  `np.polyfit(pre_years, ..., 1)` loop itself (same inputs, same per-slot call as `:150-161`), keeping both
  the slope (pre_slope — same value `project_to_2030` would give) and the intercept, in one pass. This is a
  new computation the design brief asked for ("adds only: computing jump[s,t]..."), not a second, divergent
  reimplementation of the slope already in `t20_d1.py`/`06_forecast_rake.py`.
- **Rake step calls `06_forecast_rake.py`'s `rake_2030()` and `_joint_act30_rake_2030()` directly** (imported
  unedited, exactly as `t20_d1.py` itself calls them), rather than reusing `t20_d1.build_2030_table()` whole —
  that function always derives `target` internally from mode, so it cannot take T26's externally-computed
  `target_lambda`. See Ledger's "Plug-in decision" for the full reasoning.
- **Standardized-jump sensitivity computed once, task 0 only** (`--std-jump` flag, set only for λ=1.0 in
  `t26_job.sh`), since jump/pre_slope do not depend on λ — recomputing it identically in all three tasks would
  be pure redundant compute (~another full `augmented_diaries.csv` read + reweighting per task) for a number
  that does not change with λ. Written as `T26/out/lambda_1.0/t26_std_jump_sensitivity.json`; the >1.0 pp
  S-Revert-std trigger (spec §2) is a manager decision, not evaluated here beyond computing and flagging the
  diff.
- **Standardized-jump reweighting method:** post-stratification weights on real respondents (`IS_SYNTHETIC==0`,
  all 4 cycles) to the rebuilt stock's `AGEGRP x SEX x LFTAG` cell counts; a respondent's weight falls back to
  the `AGEGRP x SEX` cell's ratio, then the `AGEGRP`-only ratio, when its own cycle/stratum sample cell is
  empty (spec's "collapse LFTAG, then SEX, for empty cells"); rows with no matching stock cell at any level get
  weight 1.0 (unweighted) and are counted as `no_stock_match` in the written JSON's `collapse_report`, since
  the spec does not specify a further fallback. `AGEGRP`/`SEX`/`LFTAG` are used as pandas groupby keys in their
  on-disk numeric-code form (not remapped to labels) — matches `05_census_linkage.py`'s own `MATCH_KEYS` use of
  these same columns.
- **SC0 requires `--t20-main-bem`, only wired for the λ=1.0 task** (`t26_job.sh` passes it only when
  `SLURM_ARRAY_TASK_ID=0`); the other two tasks' `t26_metrics.py --action report` calls omit it (SC0 is only
  meaningful for the nesting scenario).
- **SC2 (order check) is a separate `--action compare` mode in `t26_metrics.py`**, run only by
  `t26_compare.sh` after the array, per the design's own "after all three tasks, so run it in a final
  dependent job."
- **SC4 (md5 before/after) done as bash `md5sum` inside `t26_job.sh`**, not python — matches T18/T20
  precedent. md5 is taken of all three upstream files T26 reads (Arm N stock, Arm N 2022 BEM, T20 main 2030
  BEM), not just two, since T26 (unlike T20) also reads T20's own output file for SC0.
- **Resource sizing:** array tasks `-c 8 --mem=64G` (T18/T20/T12 precedent for a similarly-scaled CSV job),
  throttled `%2` so at most 16 of our CPUs run from this array at once; compare job `-c 2 --mem=32G` per the
  design's own sizing line. Did not shrink further given other jobs (T17, T22) were already running/queued at
  submission time — per precedent, "or let the job queue" is explicitly allowed, and in any case this whole
  chain is currently blocked on T18/T20 (see 🔴 finding), so no queue contention was actually observed for
  T26's own tasks.

## Ledger (2026-09-15, re-point to Nb-f stock)
- **Old JobIDs 1328326 (array) and 1328327 (compare): CANCELLED by manager 2026-09-15 (log (z));
  superseded by 1328377 (array) and 1328379 (compare) on Nb-f stock.** Both had been stuck
  `PD`/`DependencyNeverSatisfied` behind T20's own old array (1328311), which never ran (T18 Arm N's
  chain array 1328301 FAILED).
- **Stock chosen 2026-09-15** — same Nb-f decision and column check as T20's doc
  (`2026-09-15_T20_wp1_d1_2030_build.md` Ledger): `run_exclusion()`
  (`05_census_linkage.py:674`) and `frame_filter()` (`t18b_pipeline.py:193`) are both pure row filters,
  so the Nb-f `_framev2.csv` stock has the same columns as the old `_excl` stock — no schema gap.
- **`t26_job.sh` edited** (only file changed; `t26_scenario.py`/`t26_metrics.py`/`t26_compare.sh` take
  paths as CLI args or read this job's own `T26/out/` tree, no hardcoded T18 paths, confirmed by grep):
  - `t26_job.sh:36` — added `T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf`.
  - `t26_job.sh:50` (`STOCK=`) — now `$T18C_ROOT/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv`
    (was `$T18_ROOT/arm_N/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`).
  - `t26_job.sh:52` (`ARM_N_2022_BEM=`) — now `$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv`
    (was the Arm N path); variable name kept unchanged (matches `t26_metrics.py --arm-n-2022-bem`).
  - `DIARIES=$T18_ROOT/input/augmented_diaries.csv` left as is; `T20_MAIN_BEM` unchanged (it is this
    task's own new-T20-output reference, path shape identical either way).
  - Comments and the `[SC4]` PASS/FAIL log line updated from "Arm N" to "Nb-f" for clarity; no logic
    changed. `bash -n` clean.
- **Staged** by `scp` over the existing remote copy at
  `/speed-scratch/o_iseri/2J_revision/T26/T26_scripts/t26_job.sh`. Remote `ls -la`: 5,701 B, matches
  local exactly. Single-file `grep -n arm_N` on the staged remote file: zero hits (grep exit 1).
- **New JobID 1328377** — `t26_scenario` array (`--array=0-2%2`, unchanged), submitted
  `sbatch --dependency=afterok:1328375 -p ps -t 7-00:00:00 T26_scripts/t26_job.sh` from
  `/speed-scratch/o_iseri/2J_revision/T26/` (same directory as the original submission). 1328375 is
  T20's new JobID on the Nb-f stock. `squeue` immediately after: `1328377_[0-2%2]` `PD (Dependency)`.
- **New JobID 1328379** — `t26_compare`, submitted
  `sbatch --dependency=afterok:1328377 -p ps -t 7-00:00:00 T26_scripts/t26_compare.sh` (`t26_compare.sh`
  itself unedited — no T18/arm_N references in it). `squeue` immediately after: `1328379` `PD (Dependency)`.

## Next
Employee (Nb-f re-point): done — jobs 1328377 (array) and 1328379 (compare) submitted, state written
here, turn ending (no waiting/polling). Collector (fresh agent, once T20's 1328375 and this chain
complete): same acceptance procedure as originally written below (SC0-SC5). 🔴 Note for the collector:
T18c's own validator on the Nb-f 2022 build showed 30 pass / 1 fail / 1 warn (32 checks total) — a
different total than any "28/28"-style target inherited from the old chain; do not change any
acceptance count yourself, this is flagged for the manager.

## Next (original, pre-re-point, superseded by the Ledger entry above)
Employee: steps 1-3 done, jobs submitted (`1328326` array, `1328327` compare), turn ending here (no
waiting/polling per the no-parking rule). 🔴 **Before any collector work on T26 itself: T18's chain array
(`1328301`) FAILED both tasks, so T20 (`1328311`) and T26 (`1328326`/`1328327`) are all stuck behind a
`DependencyNeverSatisfied`/`Dependency` chain and will not produce output until T18 is fixed and re-run (or
T20/T26 are resubmitted against a working T18 build) — this is a manager decision, out of this task's scope
and outside the directories this task may touch.** Once T18→T20 are healthy and `1328326`/`1328327` actually
run: collector (fresh agent) runs `sacct -j 1328326` and `sacct -j 1328327` for exit codes, scp back
`T26/out/lambda_*/t26_metrics_lambda_*.csv`, `T26/out/lambda_1.0/t26_std_jump_sensitivity.json`,
`T26/out/t26_compare_metrics.csv`, and the three `outputs_step7/step7_validation_report_2030_v2.html`
summaries; tail the four slurm logs for `--- STEP START/OK/FAILED ---` and `[SC4]`/`[SC*]` lines. Fill
Verified against SC0 (share of exactly-equal cells, λ=1.0 vs T20 main — must be 1.0 or scenario builds are
not used), SC1 (per λ, weekday change within 0.5pp of `t26_targets_lambda_<v>.csv`'s own design target), SC2
(`t26_compare_metrics.csv`'s `SC2_national`/`SC2_archetype` PASS/FAIL notes), SC3 (reported jump numbers,
sign check on S-Revert), SC5 (max abs diff per stratum, flag >0.5pp), SC4 (diff the `sc4_md5_*` files).
Manager: per spec §4/Next — SC0 fail → scenario builds not used; standardized jump differs from primary by
> 1.0 pp (national weekday mean, in the JSON) → add S-Revert-std; else brief Step-8 runs for S-Partial and
S-Revert on the same 1,200 households as T21's 2030 runs.

## WHAT I DID NOT VERIFY
- Did not run any step of `t26_scenario.py` on real data (T18/T20 have not produced output for it to read —
  see the 🔴 finding), so no evidence yet that `compute_pre_slope_and_jump`, `rake_2030`,
  `_joint_act30_rake_2030`, the standardized-jump reweighting, or the Step-7 validator actually succeed
  end-to-end against the Arm N stock — reasoned through every function signature and every hard assert while
  reading the source, but this is reasoning, not a measurement, same caveat T20's own doc carries.
- Did not verify that SC0 actually reaches share=1.0 at λ=1.0 — reasoned that `stock_rate` comes from the
  same imported function and `pre_slope`/target formula collapse to T20 main's own formula when
  `(1-lambda)=0`, but the rake step's RNG draw (`np.random.default_rng(42)`, called once per script
  invocation) could in principle diverge in call order/state from T20's own single call to `rake_2030` if
  any other randomness precedes it differently between the two scripts — not traced instruction-by-instruction
  against T20's RNG call sequence, only against the target arrays being equal.
- Did not independently verify the standardized-jump reweighting's fallback logic (`AGEGRP x SEX x LFTAG` ->
  `AGEGRP x SEX` -> `AGEGRP`) against a known-answer fixture — logic was reasoned through but not exercised on
  real data; also did not check whether `AGEGRP`/`SEX`/`LFTAG` can carry `NaN` in either the stock or the
  diaries (pandas `groupby` silently drops `NaN` keys by default, which could under-count a stock or sample
  cell without raising) — not confirmed either way.
- Did not check Speed disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T26/` before staging —
  three λ builds each write a full `BEM_Schedules_2030.csv` (T20-scale, ~600+ MB each) plus a person table,
  on top of everything T17/T18/T19/T20/T22 already have on disk.
- Did not confirm whether `1328326`'s array will actually start promptly once `1328311` (and, transitively,
  `1328301`) are healthy, given other jobs (`1328310` T22, `1328286` T17) may still be running/queued for the
  same 32-CPU pool at that future time — not pollable now since the blocking dependency has not resolved.

## WHAT I DID NOT VERIFY (Nb-f re-point, 2026-09-15)
- Did not run `t26_scenario.py`/`t26_metrics.py` against the Nb-f stock — submitted 1328377/1328379 and
  ended the turn per the no-parking rule; same column-equivalence reasoning as T20's doc, not exercised
  on the real Nb-f file.
- Did not resolve the 30/1/1/32-vs-"28/28" acceptance-count question — flagged for the manager.
- Did not re-verify SC0 nesting logic against the Nb-f stock beyond what was already reasoned for the
  old chain (unchanged formula, only the input file differs).

## Collector (2026-09-15, 1328377/1328379)
`sacct -j 1328377,1328379`: array `1328377_[0-2]` and compare `1328379` all **COMPLETED 0:0**
(task 0 32:53, task 1 29:51, task 2 30:14, compare 0:43). Every task log (`slurm_1328377_0/1/2.out`) shows
an unbroken `STEP START`->`STEP OK` chain, no `STEP FAILED` anywhere; compare log shows the same for its
one step.

| SC | value read | where | band | verdict |
|---|---|---|---|---|
| SC0 nesting | 6,934,320/6,934,320 cells exactly equal = 100.0% (λ=1.0 vs T20 main) | `slurm_1328377_0.out:199` | share = 1.0 (100%) required, or scenario builds unused | **PASS** |
| SC1 intended step | λ1.0: 1.4850pp vs design 1.5066pp (diff 0.0216pp); λ0.5: -0.8547 vs -0.8592 (diff 0.0045pp); λ0.0: -3.2081 vs -3.2250 (diff 0.0169pp) | `slurm_1328377_0.out:179,191`; `_1.out:176,188`; `_2.out:176,188` | within 0.5pp of `target_λ − stock_2022` mean | **PASS** (all 3) |
| SC2 order | Weekday at-home: Revert 71.2168% < Partial 73.5702% < Persist 75.9099% (national); same strict order in all 5 archetypes | `slurm_compare_1328379.out` (`t26_compare_metrics.csv` rows) | strict Revert<Partial<Persist | **PASS** (national + 5/5 archetypes) |
| SC3 jump sanity | WD jump 4.7316pp / Sat 1.8166 / Sun 1.354 (same all λ, as expected); S-Revert WD at-home change 2022->2030 = -3.2081pp (negative) | `slurm_1328377_0.out:192-195` (jump also in `_1.out`/`_2.out`, identical) | reported only, not banded; sign check: negative expected since jump>8yr trend | **INFO — consistent with expectation** |
| SC4 integrity | Each task's own validator: `30 PASS / 1 WARN / 0 FAIL` (WARN = "classic backup absent, regression skipped"); row count 6,934,320 / HH 144,465 match expected in all 3; `[SC4] PASS: ... unchanged` (md5 before=after) in all 3 | `_0.out:84,205`; `_1.out:167,201`; `_2.out:167,201` | spec text says "Validator 28/28"; same-rows/HH-IDs as Arm N 2022; upstream md5 unchanged | **PASS on 0-FAIL + md5-unchanged**, but band text ("28/28") does not match this validator's own total (30+1=31) — pre-existing mismatch, already flagged in this doc's Ledger for the manager, not resolved here |
| SC5 rake | max abs diff/stratum: λ1.0 WD 0.0002 / Sat 0.0012 / Sun 0.0012pp; λ0.5 0.0002/0.0011/0.0011; λ0.0 0.0002/0.0012/0.0012 — 0/48 slots flagged >0.5pp in every case | `_0.out:196-198`; `_1.out:193-195`; `_2.out:193-195` | flag any slot >0.5pp | **PASS** (9/9 stratum-task cells, 0 flagged) |

How each check could fail (one sentence each): SC0 fails if the imported rake call diverges in RNG
call order from T20's own call (flagged as an open risk in this doc's own "WHAT I DID NOT VERIFY" before
this run; not observed here — result was exactly 100%). SC1 fails if the binary-flip rake cannot
converge exactly to a discrete target, drifting the achieved change away from the intended one by
>0.5pp. SC2 fails if a small/high-variance archetype's ordering flips even while the national mean
still respects Revert<Partial<Persist. SC3 has no failure band by design — a "surprising" result would
be S-Revert's at-home change coming out positive despite a jump larger than the 8-year trend. SC4 fails
if the validator's numeric checks (row/HH counts, ranges, calibration deltas) miss a genuine schema or
population drift, or if the md5-before/after diff silently passes because a re-run overwrote the "before"
file first. SC5 fails if the rake leaves any stratum x slot more than 0.5pp off target, e.g. from an
under-determined joint constraint.

**Not-trusted-yet note (validator):** one of the validator's own checks — "6.x classic backup absent,
regression skipped" (WARN, all 3 tasks) — never actually ran; it was never seen catching a bad case in
this task, so its 0-FAIL claim rests on 30 checks with hard numeric bands, not 31. Treating SC4 as PASS
on those 30, not claiming the skipped one adds any evidence either way.

**New finding, not an acceptance item:** task 0's standardized-jump sensitivity (spec §2) shows WD
primary jump 4.7316pp vs standardized 7.6673pp, diff +2.9357pp — **over the spec's 1.0pp trigger** for
adding S-Revert-std (`slurm_1328377_0.out:173`, JSON at
`/speed-scratch/o_iseri/2J_revision/T26/out/lambda_1.0/t26_std_jump_sensitivity.json`). This is a
manager decision per spec §2, not made here.

Three `BEM_Schedules_2030.csv` files that feed T29 (all confirmed present — compare job's own input
checks passed on all three):
- `/speed-scratch/o_iseri/2J_revision/T26/out/lambda_1.0/BEM_Setup/BEM_Schedules_2030.csv` (S-Persist)
- `/speed-scratch/o_iseri/2J_revision/T26/out/lambda_0.5/BEM_Setup/BEM_Schedules_2030.csv` (S-Partial)
- `/speed-scratch/o_iseri/2J_revision/T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv` (S-Revert)

md5 of these three scenario output files: **not recorded** — the compare job never computed or printed
them (it only re-uses the before/after md5 of the three *upstream* files, `STOCK`/`ARM_N_2022_BEM`/
`T20_MAIN_BEM`, inside `t26_job.sh`), and `md5sum` is forbidden on the login node, so this collector
could not compute them either.

**WHAT I DID NOT VERIFY (collector pass):**
- Did not open/recompute any value from the underlying CSVs (`t26_targets_lambda_*.csv`,
  `t26_metrics_lambda_*.csv`, `t26_compare_metrics.csv`, `t26_std_jump_sensitivity.json`) — all numbers
  above are read from the SLURM log `print()` lines only (no python allowed on the login node).
- Did not compute md5 of the three scenario `BEM_Schedules_2030.csv` files (see above — never printed,
  and forbidden to compute here).
- Did not resolve the SC4 "28/28" vs actual "30 PASS/1 WARN/0 FAIL" band mismatch — inherited, flagged
  for the manager, not changed.
- Did not confirm the skipped validator regression check (6.x) against any known-bad fixture — marked
  NOT TRUSTED YET above, scoped to that one sub-check only.
- Did not check Step-8/T29 consumption of these three files — out of this task's scope.
- Did not check Speed disk usage/quota under `T26/` after these three ~600+MB-scale BEM builds landed.

## Next
Manager: SC0-SC5 all read and scored (SC0/SC1/SC2/SC4/SC5 PASS, SC3 informational/consistent) —
per spec §4, T26 output is accepted for use. Decide on the standardized-jump trigger (+2.9357pp, over
the 1.0pp band) — add S-Revert-std or not. Once decided: brief Step-8 runs for S-Partial and S-Revert
(and S-Revert-std if added) on the same 1,200 households as T21's 2030 runs (spec §4/Next, original).

## Manager addendum (2026-09-15, after collector)
- **T26 ACCEPTED for use.** SC0 exact nesting, SC1 all three within 0.022 pp, SC2 strict order nationally and in
  every archetype, SC5 max 0.0012 pp, SC3 consistent (S-Revert weekday change -3.21 pp, negative as expected).
- **SC4 reading (not a band change).** "Validator 28/28" in the spec is a stale count from the old chain; the
  validator now has 31 checks. The intent is "no FAIL". 30 PASS / 1 WARN (regression skipped, no backup) / 0 FAIL,
  row and household counts equal, upstream md5s unchanged = PASS, the same reading T20 N2 used. The skipped
  regression check adds no evidence and is not claimed.
- **Standardized-jump trigger FIRED by the rule fixed in the spec before any data** (spec §2): national weekday
  standardized jump 7.6673 pp vs primary 4.7316 pp, +2.94 pp > 1.0 pp. S-Revert-std is added as task **T32**
  (definition: spec addendum). Not re-litigated.
- Scenario file md5s were never printed; T29's staging job and T32's job record them inside sbatch.
- T29 phase B go for S-Partial and S-Revert (go conditions met: T21 smoke PASS, T26 SC0-SC5).
