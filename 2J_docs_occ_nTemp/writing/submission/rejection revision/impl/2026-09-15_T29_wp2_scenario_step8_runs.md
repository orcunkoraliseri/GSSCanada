# T29 — WP2: Step-8 runs for the two extra 2030 scenarios (half-reverted and fully reverted work from home) — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP2, §7 D1, §10 Wave 3. Spec: `2026-09-15_WP2_scenario_spec.md`.
Inputs built by: `2026-09-15_T26_wp2_scenario_builds.md` (λ = 0.5 and λ = 0 schedule files).
Facts used: `2026-09-15_T27_wave3_prep_reading.md` Q1b (same-ID files give the same draw), T21 (engine, paths).
Status:     SUBMITTED -- phase B (fixed-manifest wrapper) submitted 2026-09-15: staging 1328431, smoke
            1328432, arrays 1328433 (S-Partial)/1328434 (S-Revert); not yet collected.

## Design (manager, fixed before any result)
- **Runs.** 2030 only, both scenarios: S-Partial (λ = 0.5) and S-Revert (λ = 0). 24 cells × 50 × 1 year × 2 =
  **2,400 runs**. S-Persist (λ = 1) is T21's Step-8 2030 arm, because T26's SC0 requires the λ = 1 build to equal
  T20 `main`; it is not rerun. The 2022 arm is T21's, shared by all three scenarios.
- **Command.** `run_paired_mc.py --n 50 --seed 42 --sim-mode standard --years 2030 --sched-dir T29/sched_lambda_<v>`
  from the copy inside `T22/code/repo`, one array per scenario, task id → cell in the fixed ARCHS × CITIES order
  (T27 Q2). Output root `T29/out/lambda_<v>/<cell>/`.
- **Why `--years 2030` alone gives the T21 households.** T27 Q1b: pool and per-cell seed do not depend on the
  years list when the file's household IDs equal the 2022 file's. T26's builds keep the 2022 IDs (they reweight
  targets on the same stock). Checked, not assumed: acceptance P1.
- **Staging.** An sbatch job copies `T26/out/lambda_<v>/BEM_Setup/BEM_Schedules_2030.csv` into
  `T29/sched_lambda_<v>/BEM_Schedules_2030.csv` (plain filename, which `--sched-dir` expects) and writes md5s before
  the arrays start. Step 9 is not rerun per scenario (plan WP2).
- **Compute.** `-c 4 --mem=16G`, `--array=0-23%2` per scenario, `--nice=100` so T21's arrays run first. About
  120 CPU-hours per scenario from T27 Q6.

## Acceptance (collector)
- **P0 completeness.** 1,200 per scenario, per cell; 8,760 rows per `hourly_meters.csv`; warm-up retry as T21;
  undelivered runs listed, never filled.
- **P1 pairing.** Each cell's `(sample, hh_id)` equals T21's Step-8 manifest for that cell (24/24, both
  scenarios). A mismatch in any cell stops the scenario comparison for that cell.
- **P2 target reached (plan WP2 test).** Injected weekday at-home mean of the sampled households, per scenario,
  against the T26 target for the same households' strata, within 0.5 pp; reported per archetype and stock-weighted.
- **P3 the chain responds (plan WP2 test).** Stock-weighted 2022→2030 deltas of midday share, load factor, peak
  hour and annual kWh, per scenario, next to T21's S-Persist deltas. Expected order S-Revert ≤ S-Partial ≤
  S-Persist on midday share and the reverse sign for S-Revert if its at-home level sits below 2022. Report the
  numbers; a broken order is a finding for the manager, not a rerun trigger.
- **P4 inputs unchanged.** md5 of both staged files before and after.
- **P5 no fallback.** Zero "schedule.json not found" and zero "invalid" lines in all task logs.

## Phase A brief (employee, Sonnet) — prepare and stage; nothing submitted
Rules: login node = `sbatch squeue sacct scancel scontrol cd ls scp module load` plus single-file
`tail/head/grep/wc -l/cat` only. Never python, `find`, `du`, `md5sum`, `cp`, `mkdir` or blocking `srun` there.
ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`; tcsh, no `2>&1`, no `2>/dev/null`.
Python `/speed-scratch/o_iseri/envs/step4/bin/python`. Every job `-p ps -t 7-00:00:00`. Never write into another
task's directory. No edits to repo files; local `py -3 -m py_compile` and `bash -n` only. Write state here as you go.
1. Read the WP2 spec, T26 (Design, Ledgers, Decisions), T21 (Design, Decisions) and `impl/T21_scripts/t21_array.sh`.
   Record under Decisions the exact staged-file paths and the command per cell.
2. Write `impl/T29_scripts/`: `t29_stage.sh` (`-c 1 --mem=4G`: copy the two λ files, md5 before);
   `t29_array.sh` (env `LAMBDA` ∈ {0.5, 0.0}; same warm-up retry as `t21_array.sh`); `t29_check.py` (P0–P5, sbatch
   `-c 4 --mem=32G`, writes `T29/out/t29_check.json` and the P2/P3 CSVs; metric definitions from T27 Q5 with
   `file:line`; stock weighting as `08_simulation_plots.py:74-77,300-321`). Test the P1 and P2 logic locally on a
   tiny fake tree in the scratchpad so each is seen failing once.
3. `scp -r` the scripts to `/speed-scratch/o_iseri/2J_revision/T29/`. Status READY (phase A). End turn.

## Phase B (fresh employee, only after manager go)
Go: T26 collector SC0–SC5 pass (SC0 nesting is required), T21 smoke collected PASS. Submit `t29_stage.sh`, then
the two arrays with `afterok` on it. JobIDs to Ledger, Status SUBMITTED, end turn. Collector: `t29_check.py` as an
sbatch job with `afterok` on both arrays and on T21's Step-8 array.

## Ledger
- **Step 1 (reading).** Read the WP2 spec (`2026-09-15_WP2_scenario_spec.md`, design + acceptance
  SC0-SC5), T26 doc in full (Design, Ledger, Decisions, Next), T21 doc in full (Design, Ledger,
  Decisions, Next), `impl/T21_scripts/t21_array.sh` in full, `impl/T21_scripts/t21_check.py` in full,
  `impl/T21_scripts/t21_smoke.sh` in full (for the warm-up-retry-NOT-wired precedent and the
  cd-into-DRIVER_DIR pattern, since `run_paired_mc.py` has no `--code-root` flag -- T21 Decisions),
  `impl/T26_scripts/t26_scenario.py` in full (targets CSV schema: `stratum,slot,lam,stock_rate,
  pre_slope,jump,target`; person table schema `HH_ID,DDAY_STRATA,DTYPE,BEDRM,act30_*,hom30_*`,
  `t20_d1.py:227-231`) and `impl/T26_scripts/t26_metrics.py` in full (confirms the FINAL staged
  `BEM_Schedules_2030.csv` -- the file actually fed to `--sched-dir` and to E+ -- has columns
  `SIM_HH_ID,Day_Type,Hour,DTYPE,Occupancy_Schedule`, `t26_metrics.py:45-46`; this is what P2 reads,
  not the intermediate person table, so P2 measures the literally-injected value). Read
  `2026-09-15_T27_wave3_prep_reading.md` Q1 (pool/seed), Q2 (cell order), Q5 (metric definitions +
  file:line, stock weighting) in full. Read `08_simulation_plots.py:60-115,270-397` directly
  (`STOCK_WEIGHTS` `:74-77`, `_circular_mean_hour` `:278-285`, `_stock_weighted_circular_mean`
  `:300-321`, `summarize_run` metric computations `:324-393`).
- **Wrote `impl/T29_scripts/`**: `t29_stage.sh`, `t29_array.sh`, `t29_check.py`. Local
  `py -3 -m py_compile t29_check.py` -> exit 0; `bash -n t29_stage.sh` / `bash -n t29_array.sh` ->
  exit 0 (all three, this session).
- **P1/P2 logic smoke-tested on a fake tree** (scratchpad `t29_faketest/`, never on Speed): built one
  fake cell (`SingleD__Toronto_5A`) with a T29 `cell_manifest.csv` (sample 1->HH111, sample 2->HH222)
  and a deliberately-mismatched T21 reference manifest (sample 1->HH999, sample 2->HH222), plus a fake
  `t26_targets_lambda_0.5.csv` (stratum=1 `target`=0.20 constant across 48 slots) and a fake staged
  `BEM_Schedules_2030.csv` (households 111/222, `Day_Type=Weekday`, `Occupancy_Schedule`=0.5 constant).
  - **P1 seen failing once**: `p1_pairing()` on the mismatched pair returned `FAIL:1_mismatch`
    (`got={1:'111',2:'222'}` vs `ref={1:'999',2:'222'}`) -- confirmed via direct function call.
  - **P1 seen passing once** (extra check, not required by the brief but done for confidence):
    same function against the matching (T29-vs-itself) manifest returned `PASS`.
  - **P2 seen failing once**: full `t29_check.py --t29-root ... --t26-root ... --t21-step8-dir ...`
    run against the fake tree reported `P2.0.5 = {"status":"OK","target_wd_pp":20.0,
    "injected_stock_weighted_wd_pp":26.45,"diff_pp":6.45,"flag_over_0.5pp":true,
    "per_archetype_wd_pp":{"SingleD":50.0}}` -- correctly flagged (0.5 injected vs 0.20 target is far
    outside the 0.5pp band); exit code 1 (fail), confirmed. `injected_stock_weighted_wd_pp`=26.45 (not
    50.0) because the fake tree only populates the `SingleD` archetype -- the stock-weighted formula
    still multiplies by the full `STOCK_WEIGHTS[SingleD]`=0.529-ish share, not renormalized to the
    populated archetypes only, which is correct behaviour once all 4 archetypes are real (each cell
    contributes its own archetype) but means a single-archetype fake tree understates the
    stock-weighted number by construction -- expected, not a bug, noted here so a future reader is not
    confused by the arithmetic.
  - P0/P3/P4/P5 exercised incidentally by the same full run (all cells but one have no data, so P0
    reports the fake tree's true incompleteness; P3 correctly returned `NO_PAIRED_HOUSEHOLDS` since no
    fake `hourly_meters.csv` files were built; P4 correctly returned `NO_BEFORE_FILE` since no fake
    `sched_md5_before.txt` was written) -- none of these three were separately fake-failure-tested
    beyond this, since the brief only asked for P1 and P2.
- **Staged to Speed** by `scp -r` of a local `T29/` folder (never `ssh ... mkdir`, per the rule and
  per T21's own recorded rule-violation/correction) containing `T29_scripts/` (3 files) plus empty
  placeholder subdirs `logs/`, `out/lambda_0.5/`, `out/lambda_0.0/`, `sched_lambda_0.5/`,
  `sched_lambda_0.0/` (each holding a 0-byte `.keep` so SLURM's `--output=.../T29/logs/...` path and
  the stage/array jobs' output dirs exist before Phase B ever submits anything -- `#SBATCH --output`
  paths must pre-exist at submission time, they are not created by the job itself). Remote
  `ls -la /speed-scratch/o_iseri/2J_revision/T29/T29_scripts`: `t29_array.sh` 5,342 B, `t29_check.py`
  22,770 B, `t29_stage.sh` 3,057 B -- all three match local byte sizes exactly (checked before and
  after transfer). `T21`, `T26` sibling dirs confirmed present read-only on Speed (login-node `ls`,
  allowed) -- not written to.

## Verified
- `run_paired_mc.py`'s only CLI args are `--archetype --city --n --seed --sim-mode --years
  --output-dir --sched-dir` (T21 Decisions, `Step8_docs/run_paired_mc.py:35-47`) -- no `--code-root`;
  `t29_array.sh` reuses T21's own already-verified cd-into-`T22/code/repo` invocation method rather
  than inventing a flag.
- Per T27 Q1b: for a lone `--years 2030` call, the per-cell pool is `sorted(keys(schedules['2030']))`
  and the per-cell RNG seed (`_step8_cell_seed`, `main.py:1952-1962`) does not depend on `--years` --
  so if the 2030 file's household-ID set equals the 2022 file's (true for T26's builds, which keep the
  2022 IDs), the draw is identical to T21's own 2022+2030 draw for that cell. This is exactly what
  P1 checks; it is not assumed at run time by `t29_array.sh`.
- Cell order (T27 Q2, `t21_array.sh` header): archetype outer loop
  (SingleD, OtherDwelling, MidRise, HighRise), city inner loop (Toronto_5A, Kelowna_5B, Vancouver_5C,
  Montreal_6A, Calgary_6B, Winnipeg_7A) -- copied verbatim into `t29_array.sh` so task index N is the
  SAME cell in both T21's and T29's arrays.
- Metric definitions used in `t29_check.py`'s P3, with file:line (T27 Q5): annual kWh =
  `Electricity:Facility` meter summed (`08_simulation_plots.py:79,361`); load factor = mean24/max24
  (`:385`); midday share = hours 9-17 sum / annual sum, `MIDDAY=(9,17)` (`:114,387`); mean peak hour =
  circular mean of the 365 daily-peak hours (`_circular_mean_hour`, `:278-285,372,378,388`). Stock
  weighting = `STOCK_WEIGHTS` archetype-only (`{SingleD:.529,MidRise:.213,OtherDwelling:.130,
  HighRise:.128}` renormalized, `:74-77`), each archetype's share split equally across its (up to 6)
  cities (`_stock_weighted_circular_mean`, `:300-321`) -- `t29_check.py`'s `_stock_weighted_scalar()`
  and `_stock_weighted_hour()` reimplement this same split for T29's own per-cell deltas.
- T26's final staged `BEM_Schedules_2030.csv` (the file this task copies under `--sched-dir` and the
  one E+ actually reads occupancy from) has columns `SIM_HH_ID,Day_Type,Hour,DTYPE,
  Occupancy_Schedule` (`t26_metrics.py:45-46`, confirmed by reading the script, not by reading the
  actual CSV -- T26 has not produced real output yet). P2 reads exactly this file/these columns.
- T26's `t26_targets_lambda_<v>.csv` has columns `stratum,slot,lam,stock_rate,pre_slope,jump,target`
  (`t26_scenario.py:104-114`), one row per (stratum in {1=WD,2=Sat,3=Sun}, slot 1-48). P2's
  `target_wd_pp` = mean of the `target` column where `stratum==1`, matching how `t26_metrics.py`'s own
  `sc1_intended_step`/`sc5_rake` read the same file.

## Decisions
- **P2 reads the FINAL staged `BEM_Schedules_2030.csv`, not the intermediate person table.** The
  task doc's own acceptance line says "injected ... at-home mean" -- the final staged file (columns
  `SIM_HH_ID,Day_Type,Hour,DTYPE,Occupancy_Schedule`) is literally what is injected into every
  household's IDF (T27 Q4, `integration.inject_schedules()`), whereas the person table
  (`hom30_*`/`act30_*` at the pre-conversion 48-slot granularity) is one step upstream of the
  raking-to-injection pipeline. Reading the staged file also means P2 is checking the SAME bytes P4's
  md5 check guards, end to end.
- **P2's "same households' strata" is read as "the day-type stratum" (weekday, `stratum==1` in T26's
  own STRATA encoding), not a demographic stratum.** T26's `STRATA = {1:WD, 2:Sat, 3:Sun}`
  (`t26_scenario.py:75-76`) is the only stratification the target CSV carries; there is no
  per-household demographic target to match against (the rake target is a population-level 3x48
  grid, `t26_scenario.py:104-113`), so "target for the same households' strata" can only mean the
  weekday-stratum target level, compared against the sampled households' own weekday mean.
- **P2 is banded at the stock-weighted (national) level; per-archetype numbers are reported, not
  separately gated**, matching the task doc's own SC1 precedent in `t26_metrics.py` ("Sat/Sun and per
  archetype reported" alongside one banded national number). `t29_check.py`'s overall FAIL/PASS uses
  `flag_over_0.5pp` on the stock-weighted number only.
- **P3's circular (peak-hour) delta is computed as a wrap-aware difference of two stock-weighted
  circular means** (`((h2030 - h2022 + 12) % 24) - 12`, range `(-12,12]`), not a linear subtraction of
  two mean-hour scalars, and not a circular mean of per-household hour-deltas -- this keeps the 2022
  and 2030 stock-weighted means individually reportable (both are written to the P3 CSV) while giving
  a delta that handles the 23->0 wrap correctly, consistent with why `08_simulation_plots.py` uses a
  circular (not linear) definition for the mean peak hour itself.
- **P3's 2022 side always comes from T21's own Step-8 output** (`--t21-step8-dir`, default
  `T21/out/step8`), never re-derived or re-run -- task doc Design line 11: "The 2022 arm is T21's,
  shared by all three scenarios." `t29_check.py` pairs by the `HH<id>` suffix of the `sample_N_HH<id>`
  directory name (same naming both T21's and T29's `run_paired_mc.py` output use), not by sample
  index, since a household can land on a different sample index in T21's `--years 2022,2030` draw vs
  T29's `--years 2030` draw even though (per P1) the SET of sampled households is identical -- pairing
  on directory-name hh_id is index-independent and correct either way.
- **P1's reference manifest prefers T21's own re-run Step-8 output** (`--t21-step8-dir`) over the
  published pre-rebuild manifest (`--step8-published-ref-dir`, optional fallback, same tree
  `t21_check.py` already wires for A2), because T21's own re-run is the thing this task's own draw
  must match (same rebuilt-stock code path, same seed) -- the published manifest is only a fallback if
  T21's Phase B has not yet produced its own manifest when the collector runs.
- **`t29_check.py` does not implement the warm-up retry** (same as `t21_array.sh`) -- on the published
  campaign and on T21 this was always a separate post-hoc pass after the array completes; P0's own
  undelivered-runs list is the mechanism for a human/collector to identify what needs the retry pass,
  per the task doc's own "undelivered runs listed, never filled."
- **Pre-created `T29/logs/`, `T29/out/lambda_{0.5,0.0}/`, `T29/sched_lambda_{0.5,0.0}/` on Speed now**
  (via `scp -r` of local placeholder dirs with a `.keep` file each), even though Phase A submits
  nothing, because every Phase-B `sbatch` job's `#SBATCH --output=.../T29/logs/...` path must already
  exist at submission time (SLURM does not create the output directory itself) -- without this, the
  very first Phase-B `sbatch` call would fail before running a single line of the script. This is
  staging, not submission -- no job was run, no compute used.
- **Driver-path fix (2026-09-15, T21 employee, cross-task pointer).** `t29_array.sh:69`'s `CODE_ROOT`
  was re-pointed from `T22/code/repo` (missing `run_paired_mc.py`) to a new shared tree
  `/speed-scratch/o_iseri/2J_revision/code_step8/repo` built to hold exactly what the driver needs.
  Edited, `bash -n` clean, restaged; T29's array is still Phase B (not submitted), so no new JobID.
  Full reasoning in `2026-09-15_T21_wp1_step8_step9_rerun.md`, "Ledger (2026-09-15, driver path fix)".

## Next
Phase A employee: done. `t29_stage.sh`, `t29_array.sh`, `t29_check.py` written, syntax-checked, P1/P2
logic smoke-tested on a fake tree (both seen failing once, and, as an extra check, seen passing once),
staged to `/speed-scratch/o_iseri/2J_revision/T29/` (scripts + empty `logs`/`out`/`sched_lambda_*`
dirs). Status READY (phase A). Nothing submitted.
Phase B (fresh employee, only after manager go per this doc's own gate: T26 collector SC0-SC5 pass
with SC0 nesting required, T21 smoke collected PASS): submit `t29_stage.sh`, then
`sbatch --job-name=t29_partial --export=ALL,LAMBDA=0.5 --nice=100 --dependency=afterok:<stage jobid>
t29_array.sh` and the same for `LAMBDA=0.0` (`t29_revert`); JobIDs to Ledger, Status SUBMITTED. Then
the collector runs `t29_check.py` as its own sbatch job with `--dependency=afterok:<both arrays>:<T21
step8 array>` (T21's own Step-8 array must also be complete, since P1/P3 both read its output).

## WHAT I DID NOT VERIFY
- Did not run any script against real Speed data -- T26's own scenario builds (1328377/1328379) and
  T21's own Step-8 array have not completed as of this task (both docs' own Next sections say so); no
  real `BEM_Schedules_2030.csv`, `t26_targets_lambda_<v>.csv`, `cell_manifest.csv`, or
  `hourly_meters.csv` exists yet to check the scripts against.
- Did not confirm the exact `--output-dir` layout `run_paired_mc.py` writes (`cell_manifest.csv` at
  the output-dir root, `sample_N_HH<id>/<year>/hourly_meters.csv` per household-year) against a real
  T29 run -- this is T21's own already-verified layout (T21 Verified/Ledger, and `t21_smoke.sh`'s own
  working pattern), reused here on the assumption `run_paired_mc.py`'s output layout does not change
  with `--years` being a 1-item vs 2-item list. Not independently re-derived from the driver's source
  in this task (T21/T27 already did that reading).
- Did not verify that `SIM_HH_ID` in the staged `BEM_Schedules_2030.csv` and the `HH<id>` suffix in
  `sample_N_HH<id>` directory names are the same value in the same string/int representation on real
  data -- `t29_check.py`'s P2 casts `SIM_HH_ID` to `str()` before matching against the manifest's
  `sim_hh_id` (also read as `str()`), which should be robust to int-vs-string CSV quirks, but this was
  only exercised on the fake tree's own consistent values, not on a real file with possibly
  zero-padded or `HH`-prefixed IDs.
- Did not test P0, P3, P4, or P5 against a deliberately-failing fake case (only P1 and P2, per the
  brief) -- P3/P4/P5 were only exercised incidentally (see Ledger) via their "no data yet" paths, not
  via a case built to make them fail for a real (non-missing-input) reason.
- Did not verify `pandas`/`numpy` import successfully under
  `/speed-scratch/o_iseri/envs/step4/bin/python` on Speed itself (confirmed only under the local `py -3`
  environment, which reports pandas 2.3.3 / numpy 2.3.5) -- every other T2x collector script
  (`t20_metrics.py`, `t26_metrics.py`) has the same unstated dependency, so this is treated as an
  already-accepted precedent, not newly re-verified.
- Did not check Speed disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T29/` before
  staging -- same gap T17/T18/T20/T21/T22/T26 all recorded; 2,400 new E+ runs' `hourly_meters.csv`
  outputs will add non-trivial space on top of everything already on disk.
- `--nice=100` and the `--dependency=afterok:...` flags are documented in the scripts' own header
  comments as submit-time flags (same precedent as T21/T26's `--dependency`, T18's `t18_chain.sh`) but
  were not tested here since Phase A submits nothing.

## Manager addendum (2026-09-15, after phase A)
- Phase A accepted. Decisions accepted as written (P2 on the final staged file, weekday stratum, national band;
  wrap-aware peak-hour delta; pairing on household id).
- P1 uses T21's re-run Step-8 manifests only. The published-manifest fallback is not used for a verdict: the
  collector runs `afterok` T21's Step-8 array, so the re-run manifests exist.
- P3, P4 and P5 were not seen failing. The phase-B collector must make each fail once on a copied fake case
  (wrong sign, changed schedule md5, injected "invalid" line) before trusting their PASS.
- The collector also confirms the id representation matches on real data (`SIM_HH_ID` vs the `HH<id>` suffix)
  on one cell before the full check runs.

## Manager addendum 2 (2026-09-15, after T21 diagnosis 1328414 and T26 collector) — sampling changed, phase B go
- **The phase-A premise "`--years 2030` alone gives the T21 households" is FALSE on the rebuilt files.** The
  engine's pool is the set of households that pass `validate_household_schedule` on the schedule file(s) loaded,
  so it depends on schedule CONTENT, not only on the stock (T21 doc, diagnosis ledger: SingleD Montreal 2022 alone
  16,327, 2030 alone 16,326, paired 16,326; one household of difference changes the seed-42 draw). Each scenario
  file changes schedules, so its sanity-passed pool can differ from T21's 2022-and-2030 pool, and `--years 2030`
  on it would draw other households. P1 would fail by construction.
- **Decision (spec §4 says "on the same 1,200 households as T21's 2030 runs").** Phase B does not draw. A new
  wrapper `impl/T29_scripts/run_fixed_manifest.py`, built from a copy of `run_paired_mc.py` (no repo edits),
  takes `--manifest <T21 Step-8 cell_manifest.csv>` and simulates exactly those `(sample, hh_id)` rows for year
  2030 on the scenario file, same sim mode, same output layout. Everything else (loading, injection, IDF, EPW,
  run_bem) is the driver's own path. If a manifest household is absent from, or fails the sanity check in, a
  scenario file, it is written to `undelivered.csv` with the reason and NOT replaced. P1 stays as written
  (equality with T21's manifest) and now also counts undelivered households per cell.
- **Go conditions met** (T21 smoke PASS; T26 accepted, addendum). The array must wait for T21's manifests:
  `--dependency=afterok:1328422` (T21 Step-8 array), `--nice=100`. Staging job first (md5 of both scenario files
  inside sbatch), array `afterok` on staging too.
- **Smoke first, same turn:** one cell (SingleD__Montreal_6A, S-Revert) on a two-row manifest built from the T21
  smoke's draw (`130228`, `79252`) — this smoke needs no T21 output — then the 48-task array
  `afterok:<smoke>:<staging>:1328422`.
- **S-Revert-std** (T32) gets the same wrapper and 1,200 more runs only after the T32 collector passes; not part of
  this submission.

## Ledger (2026-09-15, phase B submitted -- fixed-manifest wrapper)
- **Wrote `impl/T29_scripts/run_fixed_manifest.py`** (new file, 12,496 B, built from a COPY of
  `Step8_docs/run_paired_mc.py` -- no repo edits). Takes `--manifest <T21 Step-8 cell_manifest.csv>` instead of
  `--n/--seed`; loads the scenario `BEM_Schedules_2030.csv` via `integration.load_schedules()` (same sanity-check
  filtering path the real driver relies on, `integration.py:432-438`), then iterates the manifest's `(sample,
  sim_hh_id)` rows IN ORDER (not `rng.sample`); each row present in the loaded pool gets `integration.
  inject_schedules()` (`run_fixed_manifest.py:180-188`, same call signature as `main.py:2064-2070`) + an E+ job;
  `_run_simulations_with_fallback()` and `_step8_job_succeeded()` (`main.py`) and `plotting.get_hourly_meter_data()`
  are called verbatim, unedited -- no engine/pipeline logic reimplemented, only the sampling top-level loop
  differs. A manifest row absent from the pool, or whose `inject_schedules` call raises, is written to
  `undelivered.csv` (`sample,sim_hh_id,reason`) and popped out of the delivered `cell_manifest.csv` -- never
  replaced with another household (`run_fixed_manifest.py:190-207`).
  - **Import path (no chdir, no co-location with the driver)**: `_import_step8(code_root)` (`:73-95`) mirrors
    `T30_scripts/run_avg_arm.py`'s own `_import_step8()` exactly -- `sys.path.insert(0, <code_root>/
    2J_docs_occ_nTemp/Step8_docs)`, then `from eSim_bem_utils_2J import integration, plotting` /
    `from eSim_bem_utils_2J.main import _run_simulations_with_fallback, _step8_job_succeeded, ENERGYPLUS_EXE` /
    `from run_bem import resolve_cell`. Confirmed against `eSim_bem_utils_2J/main.py:38`
    (`BASE_DIR = dirname(dirname(dirname(dirname(abspath(__file__)))))`, the 4th-dirname rule): BASE_DIR resolves
    from `main.py`'s OWN file location once `<code_root>/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py`
    exists on disk -- independent of where `run_fixed_manifest.py` itself is staged or the process cwd. This
    script is staged in `T29/T29_scripts/`, NOT inside `code_step8/repo` (a shared tree other tasks also read;
    left untouched, read-only use only), and takes `--code-root` pointing at it, same as `run_avg_arm.py`'s own
    precedent (that script's own JobID 1328399 COMPLETED using this exact mechanism, no chdir).
  - Local `py -3 -m py_compile run_fixed_manifest.py t29_check.py` -> exit 0 (both, this session).
- **Edited `t29_array.sh`** (lines noted against the version last staged in Phase A): replaced the
  `run_paired_mc.py` + `cd "$DRIVER_DIR"` invocation with a call to the new wrapper. Line-level:
  `t29_array.sh:69-71` (`WRAPPER=$T29_ROOT/T29_scripts/run_fixed_manifest.py`, `T21_ROOT=` added, `CODE_ROOT=`
  kept), `t29_array.sh:86-88` (`MANIFEST=$T21_ROOT/out/step8/$CELL/cell_manifest.csv` added), `t29_array.sh:95-99`
  (new guard: exit 1 if `$MANIFEST` missing), `t29_array.sh:101-106` (driver call now `"$PYTHON" "$WRAPPER"
  --archetype ... --manifest "$MANIFEST" --sim-mode standard --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
  --code-root "$CODE_ROOT"`, no `cd`). Header comment block rewritten to record the addendum-2 reasoning (schedule
  CONTENT, not stock, drives the pool -- T21 diagnosis 1328414). `bash -n` clean. Cell order (ARCHS/CITIES arrays,
  task-index mapping) UNCHANGED, so task N here is still the same cell as T21's Step-8 array task N.
- **Wrote `t29_smoke.sh`** (new, 4,018 B): one cell (SingleD__Montreal_6A), LAMBDA=0.0 (S-Revert), calls the new
  wrapper with a hardcoded 2-row manifest (see below), output to a DEDICATED `T29/smoke_out/lambda_0.0/
  SingleD__Montreal_6A/` (not the real array's own output dir for the same cell). Checks: exit code, output
  `cell_manifest.csv` pairing == `130228,79252` in order, `undelivered.csv` has 0 data rows, both households'
  `2030/hourly_meters.csv` have 8,760 data rows. `bash -n` clean.
- **Wrote `t29_smoke_manifest.csv`** (new, 82 B): header `sample,sim_hh_id,hhsize,dtype,pr` (same columns
  `run_fixed_manifest.py:read_fixed_manifest`/`main.py:2055-2058` use), two rows: `1,130228,,SingleD,Quebec` and
  `2,79252,,SingleD,Quebec` -- sample 1 -> 130228, sample 2 -> 79252 per the task instruction (T21's own smoke
  draw, T21 doc diagnosis 1328414 Q3a). `hhsize` left blank (not read by the wrapper; re-derived from the loaded
  pool for delivered rows).
- **Edited `t29_check.py`'s P1** (`t29_check.py:150-192` in the file as now staged): added `read_undelivered_
  samples()` (reads a cell's own `undelivered.csv`, returns the set of `sample` ints listed) and rewrote
  `p1_pairing()` to return a 4-tuple `(status, got, ref, n_undelivered_this_cell)`: a sample present only in
  `ref` because `undelivered.csv` explains it (household absent from, or dropped by the sanity check in, this
  scenario's file) is no longer counted as a P1 pairing mismatch -- only an unexplained mismatch (different
  hh_id for the same sample, or an unexplained gap) fails P1. Call site in `main()` updated to unpack 4 items and
  accumulate `n_undelivered_manifest` (+ `undelivered_manifest_by_cell`) into `report["P1"][lam]`. Local
  `py -3 -m py_compile t29_check.py` -> exit 0 (see above, same run as the wrapper).
- **File sizes, local `wc -c` vs remote `ls -la` (all byte-identical after `scp`, no directory-header flag
  needed since `T29/T29_scripts/` already existed from Phase A staging):**
  - `run_fixed_manifest.py`: 12,496 B (both).
  - `t29_check.py`: 24,995 B (both).
  - `t29_array.sh`: 6,116 B (both).
  - `t29_smoke.sh`: 4,018 B (both).
  - `t29_smoke_manifest.csv`: 82 B (both).
  - `t29_stage.sh`: unchanged this session (3,057 B), not restaged, present from Phase A.
- **No new directories were created by `scp -r`/`.keep`** -- `T29/T29_scripts/`, `T29/logs/`, `T29/sched_lambda_
  {0.5,0.0}/`, `T29/out/lambda_{0.5,0.0}/` all already existed from Phase A staging (confirmed by plain `ls`
  before this session's `scp`, read-only, allowed).
- **Pre-submission read-only checks (`ls`, login node, allowed):** `T29/sched_lambda_{0.5,0.0}/` both empty
  (staging had not yet run) -- confirms the staging job genuinely had work to do. `T21/out/step8/` has only 2 of
  24 cells so far (`SingleD__Kelowna_5B`, `SingleD__Toronto_5A`); `SingleD__Toronto_5A/cell_manifest.csv` has 50
  rows, header-less-confirmed columns `sample,sim_hh_id,...` (read via the smoke's own directory listing, not by
  opening the file's header line) -- confirms T21's Step-8 array (1328422) is genuinely still running (tasks 0/1
  `R`, 2-23 `PD AssocGrpCpuLimit` per `squeue`), so this array's `--dependency=afterok:...:1328422` has real work
  to wait for, not a no-op.
- **Submitted, in order:**
  - **JobID 1328431** -- `sbatch -p ps -t 7-00:00:00 t29_stage.sh` (staging: copies `T26/out/lambda_{0.5,0.0}/
    BEM_Setup/BEM_Schedules_2030.csv` into `T29/sched_lambda_{0.5,0.0}/BEM_Schedules_2030.csv`, md5 before+after
    each copy, inside the sbatch job -- `t29_stage.sh`, unedited, already satisfied "md5 of the two scenario
    files inside sbatch"). `squeue` immediately after: `PD (AssocGrpCpuLimit)`.
  - **JobID 1328432** -- `sbatch -p ps -t 7-00:00:00 --dependency=afterok:1328431 t29_smoke.sh`. `squeue`
    immediately after: `PD (Dependency)`.
  - **JobID 1328433** -- `sbatch --job-name=t29_partial --export=ALL,LAMBDA=0.5 -p ps -t 7-00:00:00 --nice=100
    --dependency=afterok:1328432:1328431:1328422 t29_array.sh` (S-Partial, `--array=0-23%2` from the script's own
    header). `squeue` immediately after: `PD (Dependency)`.
  - **JobID 1328434** -- same command, `--job-name=t29_revert --export=ALL,LAMBDA=0.0` (S-Revert). `squeue`
    immediately after: `PD (Dependency)`.
  - None of 1328431/1328432/1328433/1328434 were waited on or polled beyond the single immediate `squeue`
    snapshot above (no-parking rule).
- **T21's Step-8 array (1328422) is an array job**; `--dependency=afterok:1328422` on it (SLURM semantics) does
  not fire until EVERY task of that array exits 0 -- confirmed this is the intended "the array must wait for
  T21's manifests" reading from addendum 2 (all 24 cells' manifests, not just some).

## Verified (2026-09-17, smoke re-verified retrospectively, read-only login-node checks)
- **Check 1 -- both households simulated.** Two result sets present under the smoke's dedicated output
  dir: `sample_001_HH130228/2030/` and `sample_002_HH79252/2030/`, each with its own `hourly_meters.csv`
  and full E+ output set (`eplusout.*`, `Scenario_2030.idf`, etc.). `cell_manifest.csv` in that dir
  reads `1,130228,...` / `2,79252,...` and `undelivered.csv` has 0 data rows (header only). **PASS.**
  Evidence: `T29/smoke_out/lambda_0.0/SingleD__Montreal_6A/{cell_manifest.csv,undelivered.csv,
  sample_001_HH130228/2030/,sample_002_HH79252/2030/}`.
- **Check 2 -- 8,760 rows each.** `wc -l` run separately on each file: HH130228's
  `hourly_meters.csv` = **8761 lines**; HH79252's `hourly_meters.csv` = **8761 lines**. Both counts
  INCLUDE the header row (`head -1` on HH130228's file confirmed the first line is the column header
  `hour,Electricity:Facility,...`, not a data row) -- so both files have exactly 8,760 data rows.
  **PASS.** Evidence: `T29/smoke_out/lambda_0.0/SingleD__Montreal_6A/sample_001_HH130228/2030/
  hourly_meters.csv` (8761 lines), `.../sample_002_HH79252/2030/hourly_meters.csv` (8761 lines).
- **Check 3 -- household IDs are the REBUILT seed-42 draw (130228, 79252), not the published pair
  (130322, 80058).** Confirmed both from the directory names (`sample_001_HH130228`,
  `sample_002_HH79252`) and from `cell_manifest.csv`'s own rows (`1,130228,1,SingleD,Quebec` /
  `2,79252,2,SingleD,Quebec`). Neither `130322` nor `80058` appears anywhere in this output. **PASS.**
  Evidence: `T29/smoke_out/lambda_0.0/SingleD__Montreal_6A/cell_manifest.csv`.
- **Ledger check (SLURM state, read this session, not carried from the task doc's own prior claim).**
  `sacct -j 1328433 --format=JobID,JobName,State,ExitCode -X`: all 24 tasks (`1328433_0`..`1328433_23`)
  `COMPLETED`, `ExitCode 0:0` -- confirms 24/24. `squeue -u o_iseri` at the same time shows `1328434`
  (`t29_revert`) still active: tasks `1328434_20`/`1328434_21` running (`R`), `1328434_[22-23%2]`
  pending on `JobArrayTaskLimit` -- i.e. tasks 0-19 already finished, 20-21 in flight, 22-23 queued.
  Not yet complete.

## Next
The T29 revert-array collector fires when 1328434 (`t29_revert`) finishes (all 24 tasks reach a
terminal state). At that point, per the "Next (phase B submitted...)" section below: read
`T29/logs/t29_stage_1328431.out` for md5 before/after PASS lines (if not already read), then each
array's per-task logs (`T29/logs/t29_partial_*_*.out`, `T29/logs/t29_revert_*_*.out`) for `DONE`/
`FAILED` and undelivered counts, then run `t29_check.py` (P0-P5, restated P1) as its own sbatch job
with `--dependency=afterok:1328433:1328434:1328422` (T21's Step-8 array 1328422 must also be complete)
and read `T29/out/t29_check.json` plus the P2/P3 CSVs. P3/P4/P5 still have not been seen failing on a
copied fake case (manager addendum) -- do that before trusting their PASS on real output. This task
did NOT collect 1328433's own array output or run `t29_check.py` -- it only re-verified the smoke.

## WHAT I DID NOT VERIFY (2026-09-17, smoke re-verification)
- Did not read 1328433's (`t29_partial`) own per-cell output or manifests -- only confirmed via
  `sacct` that all 24 of its tasks exited 0:0. Whether its 24 cells' own household draws also match
  T21's manifests (P1, across all cells) is the collector's job, not checked here.
- Did not read any of 1328434's completed-so-far task output (tasks 0-19) -- only confirmed via
  `squeue` that it is still mid-flight, not that its finished tasks succeeded.
- Did not read `T29/logs/t29_stage_1328431.out` (md5 before/after) or `T29/logs/t29_smoke_1328432.out`
  (the smoke's own stdout log) this session -- verification here was done directly against the smoke's
  output directory on disk, not its log file.
- Did not run `t29_check.py` -- per the manager's ruling this task only verifies and reports; the
  collector run is a separate, later task once 1328434 completes.
- Per the manager's 2026-09-17 ruling, no `scancel` was issued and none was warranted (all three
  checks passed).

## Next (phase B submitted, fixed-manifest wrapper)
Collector (fresh agent, once 1328431/1328432/1328433/1328434 all complete, in that dependency order): **first
read the smoke** (`T29/logs/t29_smoke_1328432.out`) -- confirm both households (130228, 79252) were simulated,
their `2030/hourly_meters.csv` each have 8,760 data rows, and the output `cell_manifest.csv` IDs match the input
manifest in order, 0 rows in `undelivered.csv`. **If the smoke does not pass cleanly, `scancel` the two arrays
(1328433, 1328434) before they burn compute** -- they are already queued behind the smoke via `--dependency`, but
will fire automatically once T21's 1328422 also completes, so do not assume the dependency chain alone is a safe
gate if the smoke's own log shows a problem. If the smoke passes: read `T29/logs/t29_stage_1328431.out` for the
md5-before/after PASS lines, then each array's per-task logs (`T29/logs/t29_partial_*_*.out`,
`T29/logs/t29_revert_*_*.out`) for `DONE`/`FAILED` and undelivered counts, then run `t29_check.py` (P0-P5,
restated P1) as its own sbatch job with `--dependency=afterok:1328433:1328434:1328422` and read `T29/out/
t29_check.json` plus the P2/P3 CSVs. Per addendum 2, P3/P4/P5 still have not been seen failing on a copied fake
case (per the earlier manager addendum) -- do that before trusting their PASS on real output.
Manager: nothing new to decide until the smoke and arrays complete.

## WHAT I DID NOT VERIFY (phase B submitted, fixed-manifest wrapper, 2026-09-15)
- Did not wait for or poll 1328431/1328432/1328433/1328434 -- submitted and moved on, per the no-parking rule.
  Whether the smoke actually delivers both households with 8,760-row output, and whether the two 48-task arrays
  deliver valid output for any cell, are unread.
- Did not run `run_fixed_manifest.py` or the updated `t29_check.py` against real Speed data this session -- only
  `py -3 -m py_compile`'d locally and `bash -n`'d the shell scripts. The manifest-read/undelivered/pop-on-failure
  logic in `run_fixed_manifest.py`, and the explained-vs-unexplained mismatch logic in `t29_check.py`'s rewritten
  `p1_pairing()`, are reasoned through, not exercised against a known-answer fixture (the task doc's own P1/P2
  fake-tree smoke-tests from Phase A predate this wrapper and do not cover it).
- Did not verify that `eSim_bem_utils_2J.integration`/`eSim_bem_utils_2J.main`/`run_bem` import cleanly via
  `run_fixed_manifest.py`'s `--code-root` mechanism on Speed itself -- reasoned by direct analogy to
  `run_avg_arm.py`'s own already-COMPLETED JobID 1328399 (same import function, same shared `code_step8/repo`
  tree), not independently re-run here.
- Did not check Speed disk quota/free space under `T29/` before this submission -- same gap recorded in every
  prior T-series doc; two more 1,200-run E+ campaigns' `hourly_meters.csv` outputs add non-trivial space.
- Did not verify `t29_stage.sh`'s own md5-before/after check actually still passes on the CURRENT `T26/out/
  lambda_*/BEM_Setup/BEM_Schedules_2030.csv` files (T26 is DONE per its own doc, but this employee did not
  re-open those files or their md5s this session -- relying on T26's own collector pass).
- `--nice=100` and the three-way `--dependency=afterok:...` chain are SLURM's own submit-time mechanisms
  (T21/T26/T29-Phase-A precedent); not independently tested beyond the immediate `squeue` snapshots above.
