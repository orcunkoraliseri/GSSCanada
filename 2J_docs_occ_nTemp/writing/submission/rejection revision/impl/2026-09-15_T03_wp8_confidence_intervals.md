# T03 — WP8: how the two confidence intervals were built — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP8, §10
Status:     DONE -- collected; Test criterion (a) FAILED (see Verified), stopped at the finding per
            task instructions, both sets of numbers recorded

## Task

**Why.** A reviewer asked how the intervals were built and whether the city × dwelling-type structure
was respected. Submitted values: change in midday share **+0.367 pp, CI [+0.208, +0.526]**; change in
load factor **+0.0117, CI [+0.0085, +0.0150]** (2022 → 2030).

**Steps.**
1. Find the code that produced those two intervals. Start from `2J_docs_occ_nTemp/Step8_docs/
   08_simulation_plots.py`, `interim_report_gen.py`, `replot_existing_montecarlo.py`, and the
   aggregate tables in `outputs_step8/agg/`. `grep -n` for `ci`, `bootstrap`, `t.ppf`, `percentile`,
   `0.367`, `0.0117`. Also check the archived manuscript for the sentence that states the method:
   `writing/submission/archive/2J_manuscript_submission.md` (read-only, grep only).
2. Write down the method exactly: unit of resampling (household? cell?), paired or not, how the 24
   cells are pooled or weighted, number of replicates, seed, percentile or t-interval. Cite `file:line`.
3. Script in `T03_scripts/`, run **on Speed** (`sbatch -p ps -c 32 --mem=64G -t 7-00:00:00`), that
   (a) reproduces both submitted intervals with the documented method from the same input data, and
   (b) computes a **cell-stratified cluster bootstrap** beside it: resample households with
   replacement within each archetype × city cell, keep the pairing of each household's 2022 and 2030
   runs, pool with the same weights as (a); 10,000 replicates, fixed seed; percentile interval.
   Outputs: `ci_reproduction.csv` (method, metric, point, low, high), `run_meta.json`.
4. Upload only the script and the input tables it needs to `/speed-scratch/o_iseri/2J_revision/T03/`.
   Write the JobID in the Ledger. **End your turn.**

**Important.** These inputs contain the defective 2030 (WP1). The numbers here only prove we found
the right code and show whether the method changes the width. They are **not for the paper**.

**Test.** (a) must match the submitted values to the reported precision. If it does not, stop at
the finding and record both sets of numbers.

**Employee rules.** Plan §10 rules 1–6 apply. Python on Speed:
`/speed-scratch/o_iseri/envs/step4/bin/python`.

## Ledger
- JobID **1328238** · sbatch on Speed, partition `ps`, `-c 32 --mem=64G -t 7-00:00:00` ·
  runs `ci_reproduction.py` on `agg_annual.csv` · Status **COMPLETED**, elapsed 33 s, exit 0:0
  (`sacct -j 1328238`, MaxRSS 164376K) · output dir
  `/speed-scratch/o_iseri/2J_revision/T03/out/` (`ci_reproduction.csv`, `run_meta.json`,
  `slurm_1328238.out`) · collected 2026-09-15, scp'd to local
  `impl/T03_out/` (all three files) · `slurm_1328238.out` reads only
  `done: /speed-scratch/o_iseri/2J_revision/T03/out/ci_reproduction.csv` -- no error, no traceback,
  short elapsed is genuine (6,000-row CSV, 10,000-replicate bootstrap, `elapsed_s: 2.86` per
  `run_meta.json`), not a truncated/failed run.
- JobID **1328252** · manager, 2026-09-15 · same script on the ARCHIVED input
  `outputs_step8/archive/agg/agg_annual.csv` (dated 2026-06-05, i.e. BEFORE job 954135 on 2026-06-10,
  6,001 lines), uploaded to `T03/input_jun05/` · **CANCELLED by manager before start** — wrong script
  path (`ci_reproduction.py` lives in `T03/scripts/`). Superseded by 1328253.
- JobID **1328253** · manager · `sbatch -p ps -c 1 --mem=8G -t 7-00:00:00` · `scripts/ci_reproduction.py
  --agg-annual input_jun05/agg_annual.csv --out-dir out_jun05` · PENDING (account CPU cap) · output
  `/speed-scratch/o_iseri/2J_revision/T03/out_jun05/` (`ci_reproduction.csv`, `run_meta.json`,
  `slurm_1328253.out`). Test: does method (a) on the June copy give 0.367 pp / 0.0117?
- 2026-09-15 (manager) · JobID **1328253** → **COMPLETED**, exit 0:0, elapsed 00:00:32, 1 CPU ·
  outputs scp'd to `impl/T03_out/jun05/` (`ci_reproduction.csv`, `run_meta.json` with
  `input_rows 6000`, `paired_n_total 1200`, `n_cells_with_pairs 24`; `slurm_1328253.out` reads only
  `done: out_jun05/ci_reproduction.csv`).

## Verified
- Code that produced the two submitted CIs found: `2J_docs_occ_nTemp/08_simulation_val.py:951-1027`
  (`SimulationValidator.validate_shift_effect`, Section 6 of the Step-8 validator, "2022->2030 shift
  effect"). Confirmed by matching the manuscript sentence in
  `writing/submission/archive/2J_manuscript_submission.md:407` ("midday energy share increases by
  +0.367 percentage points (95% CI [+0.208, +0.526])... load factor... increases by +0.0117 (95% CI
  [+0.0085, +0.0150])") and by the Progress Log entry `08_simulation_val.md:180`
  (Cluster job 954135, 2026-06-10) which records the identical numbers.
- Metric definitions: `load_factor = mean24/max24`, `midday_share = sum(hours MIDDAY)/sum(all
  hours)` (a fraction, 0-1; manuscript reports it x100 as pp) -- both at
  `2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py:385-387`.
- Method, read from `08_simulation_val.py:951-1027`:
  - Unit of resampling/pairing: **household** (`sim_hh_id`) matched by index
    `(arch, city, sim_hh_id)` between the 2022 and 2030 rows of `agg_annual.csv`
    (`08_simulation_val.py:957-961`), inner join -> a household missing either year is dropped.
  - Paired: **yes** -- delta = value_2030 - value_2022 per matched household
    (`08_simulation_val.py:963-967`).
  - How the 24 cells are pooled/weighted: **flat, unweighted pool.** The join is built once over
    the whole `annual` table (all 24 (arch,city) cells together, all up to 50 households each), so
    every paired household counts once with equal weight; there is no per-cell averaging first and
    no stock-weighting anywhere in this function.
  - Replicates / seed: **none** -- this is not a resampling method. It is a parametric one-sample
    Student-t interval: `scipy.stats.t.interval(0.95, len(d)-1, loc=d.mean(), scale=stats.sem(d))`
    (`08_simulation_val.py:973-975`), i.e. mean +/- t_(0.975,df)*SEM over the pooled paired deltas.
    A paired one-sample t-test p-value is also reported alongside (`ttest_1samp`, line 969-971).
  - Underlying MC sample (not the CI step itself, the input to it): N=50 households/cell x 24
    cells, seed=42 default, one EnergyPlus run per household-year (`Step8_docs/run_paired_mc.py:37-38`).
  - Input data used here: `outputs_step8/agg/agg_annual.csv` (6,001 lines = header + 6,000 rows =
    24 cells x 50 households x 5 years). Note: an earlier Progress-Log entry (`08_simulation_val.md:180`,
    job 954135, 2026-06-10) references a separately downloaded `outputs_step8_v2/` that no longer
    exists on disk; the current `outputs_step8/agg/agg_annual.csv` is dated 2026-07-15, i.e. later
    than that entry, and is the only `agg_annual.csv` present in the working tree (also one archived
    copy at `outputs_step8/archive/agg/agg_annual.csv`, dated 2026-06-05, not used). **NOT VERIFIED
    that this exact file is byte-identical to whatever produced the submitted numbers** -- this is
    exactly what job 1328238's part (a) tests: if it does not reproduce the submitted values to the
    reported precision, the script stops at the finding and records both sets (per Test criterion).
- **Job 1328238 result -- TEST FAILED, does NOT match the submitted values.** Read from
  `impl/T03_out/ci_reproduction.csv` and `run_meta.json` (both collected, 5-row CSV + JSON, no
  errors in `slurm_1328238.out`), `n_paired: 1200` = 24 cells x 50 households, matching the expected
  input shape exactly.
  - `midday_share`, method (a) (submitted method, t-interval): point **0.021380** (fraction) =
    **2.138 pp** x100, CI **[1.581, 2.695] pp**. Submitted: **0.367 pp, CI [0.208, 0.526]**. The
    computed point is **~5.8x the submitted point**; the two CIs do not overlap at all.
  - `load_factor`, method (a): point **0.018125**, CI **[0.014324, 0.021926]**. Submitted:
    **0.0117, CI [0.0085, 0.0150]**. The computed point is **~1.55x the submitted point**; the CIs
    barely touch at one edge (submitted high 0.0150 vs computed low 0.014324) and do not agree to
    the reported 3-4 decimals.
  - Neither metric reproduces the submitted numbers to the reported precision. This confirms the
    provenance gap flagged above: `outputs_step8/agg/agg_annual.csv` (dated 2026-07-15, currently on
    disk) is **not** the file that produced the submitted manuscript numbers. The
    `outputs_step8_v2/` copy referenced by the 2026-06-10 Progress Log entry (job 954135) is the
    more likely source and is no longer present on disk -- unresolved, needs the author/manager to
    locate or regenerate it.
  - Method (b) (cell-stratified cluster bootstrap, `n_rep=10000`, `seed=12345`) vs (a), width
    comparison on the same (non-matching) input: `midday_share` width 0.011028 (b) vs 0.011145 (a),
    **(b) ~1.0% narrower**. `load_factor` width 0.007352 (b) vs 0.007601 (a), **(b) ~3.3%
    narrower**. So on this input, respecting the household-cluster/pairing structure via bootstrap
    gives a slightly tighter interval than the parametric paired t-interval, not a wider one --
    order of a few percent, not a qualitative change.
- **Job 1328253 result (June-5 archived copy) -- CLOSE BUT DOES NOT MATCH.** Read by manager from
  `impl/T03_out/jun05/ci_reproduction.csv`, method (a):
  - `midday_share`: point 0.0038873 = **0.389 pp**, CI **[0.267, 0.511] pp** (width 0.244).
    Submitted 0.367 pp [0.208, 0.526] (width 0.318). Point off by +0.022 pp; interval ~23% narrower.
  - `load_factor`: point **0.011299**, CI **[0.008663, 0.013935]** (width 0.00527). Submitted 0.0117
    [0.0085, 0.0150] (width 0.0065). Point off by -0.0004; interval ~19% narrower.
  - Method (b) widths vs (a): midday 0.244 vs 0.244 (b ~0.2% narrower), load factor 0.00530 vs 0.00527
    (b ~0.6% wider). The bootstrap again changes nothing material.
  - **Reading:** the June copy is the right order of magnitude (the July file is ~5.5x larger on
    midday), but a different width at identical n=1200 means a different set of deltas, not rounding.
    The submitted numbers therefore came from a THIRD file, most likely `outputs_step8_v2/` (job
    954135, 2026-06-10), which is not on disk. Neither surviving copy reproduces them.
  - **Consequence (manager finding):** between the June data and the July 15 regeneration the
    2022->2030 midday shift grew from ~0.39 pp to ~2.14 pp and load factor from ~0.011 to ~0.018.
    Any manuscript number computed before 2026-07-15 may describe data that no longer exists. Both
    copies also contain the defective 2030 rows (WP1 finding), so neither is paper-grade.

## Decisions
- Script computes both `midday_share` and `load_factor` deltas (task's two target metrics); did not
  additionally reproduce the EUI paired-delta CI (Section 6.1's third metric) since the task doc only
  asked for the two submitted intervals -- easy to add if the collector/manager wants it, the
  `METRICS` list in `ci_reproduction.py` is a one-line change.
- Cell-stratified cluster bootstrap (b) pools its 24 cells' bootstrap draws the same **unweighted**
  way (a) pools the real data, per the task instruction "pool with the same weights as (a)" -- (a)
  has no explicit weights, so (b) uses a flat concatenation across cells, matching that.
- `--n-rep 10000 --seed 12345` used exactly as specified in the task's step 3(b).
- Job sized per task doc (`-c 32 --mem=64G`) even though the computation itself is small (6,000-row
  CSV); did not downsize since sizing is not this employee's call.

## Next
**Manager update 2026-09-15 (after 1328253):** T03 DONE as a method check. The source file of the
submitted intervals is lost; the code and method are confirmed; the bootstrap changes widths by
under 4%, so WP8 keeps the paired t-interval and reports the bootstrap as a robustness line. WP8
recomputes on rebuilt data. Open follow-up (Wave 2, separate task doc): list every manuscript number
and which `outputs_step8*` generation it came from (before or after 2026-07-15).
Earlier manager note: collect job 1328253 (June-5 archived input). If (a) matches the
submitted values → the paper's interval numbers came from the June data, and the July regeneration
changed results after they were written: check which other manuscript numbers predate 2026-07-15.
If it does not match → the source file is lost; WP8 recomputes the intervals on the rebuilt data anyway.
Earlier collector note follows.
Collected and recorded (2026-09-15). Test (a) FAILED to reproduce the submitted numbers on the
current on-disk `agg_annual.csv` (2026-07-15) -- computed intervals are ~1.5-6x the submitted point
values and the CIs mostly do not overlap. This is a manager/author decision now, not mechanical:
locate or regenerate `outputs_step8_v2/` (the file behind the 2026-06-10 / job-954135 entry) and
re-run against it, or determine some other cause of the mismatch. Do not re-run method (b) until (a)
reproduces, since (b)'s width comparison is only informative once (a) is confirmed correct.

## WHAT I DID NOT VERIFY
- Did not run anything locally (no local Python available in this shell) -- did not syntax-check
  `ci_reproduction.py` with `python -m py_compile`; reviewed it by hand instead. If job 1328238 fails
  with a Python error, that is the first thing to check.
- Did not confirm that `outputs_step8/agg/agg_annual.csv` (dated 2026-07-15, currently on disk) is
  the exact file that produced the submitted manuscript numbers, vs. the `outputs_step8_v2/` copy
  referenced in the 2026-06-10 Progress Log entry that is no longer present. Job 1328238's part (a)
  result is the test of this, not yet read.
- Did not poll the job or read any output file yet -- ended turn immediately after `sacct` confirmed
  PENDING, per the no-waiting rule.
- Did not check whether `/speed-scratch/o_iseri/envs/step4/bin/python` on Speed has `scipy`/`pandas`/
  `numpy` importable -- assumed yes per task doc's stated env; if job exits non-zero early, this is
  the second thing to check (see `slurm_1328238.out`).
