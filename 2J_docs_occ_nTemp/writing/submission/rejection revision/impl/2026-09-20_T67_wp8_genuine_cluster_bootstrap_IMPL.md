# T67 -- WP8: genuine cell-level cluster bootstrap -- implementation state

Task doc: `impl/2026-09-20_T67_wp8_genuine_cluster_bootstrap.md`
Status: **DONE. All three jobs COMPLETED, exit 0:0, numbers read by the manager and written into
`manuscript/draft_SI_clustering_ci.md` (section S.10). Plan item 39 CLOSED.**

## FINAL RESULT (manager, 2026-09-20 night, read directly off the cluster)

`1340720` COMPLETED 00:04:23 -- corrected `agg_annual.csv` built clean: 2,400 rows, 24 cells, 50
households/cell/year, `n_missing_facility_column: 0`, `n_short_series: 0` (`T67/out/run_meta.json`).

`1340721` COMPLETED 00:00:40 -- seen-failing control on OLD defective data, numbers match the
employee's own local functional test exactly and reproduce the old retired "1.0-3.3% narrower"
figure exactly (1.05% / 3.3%), confirming this is scored against the right retired run.

`1340722` COMPLETED 00:00:10 -- REAL run on the corrected data (`T67/out/real_correcteddata/ci_reproduction_t67.csv`):
- midday_share: method A width 0.001741, genuine cluster width 0.002433 -- **39.8% wider**. Both
  intervals exclude zero.
- load_factor: method A width 0.001652, genuine cluster width 0.001615 -- 2.3% narrower (negligible).
  Both intervals exclude zero.

**Ruling: for midday share, the honest cluster-aware interval is materially wider than method A and
must be the one cited whenever a main-text point estimate/separability claim is written (WP6/WP11,
not yet started, so no existing main-text claim needed correction -- Ruling 5's conditional does not
fire today, but binds those future tasks).** For load factor, method A remains adequate on its own.
Full writeup, table and the retired do-not-quote number: `manuscript/draft_SI_clustering_ci.md`
section S.10.

## Ledger

| JobID | What | Depends on | State at submission | Output path |
|---|---|---|---|---|
| 1340720 | `build_agg_annual_t21.py` -- builds the CORRECTED `agg_annual.csv` from T21's raw rebuilt tree (`T21/out/step8/`) | none | R (running), node antenna1 | `/speed-scratch/o_iseri/2J_revision/T67/out/agg_annual.csv`, `.../out/run_meta.json`; stdout `/speed-scratch/o_iseri/2J_revision/T67/logs/t67_build_agg_1340720.out` |
| 1340721 | `cell_cluster_bootstrap.py` -- SEEN-FAILING CONTROL, run on the OLD/defective `T03/input/agg_annual.csv` (`--n-rep 10000 --seed 12345`) | none | R (running), node edmonds | `/speed-scratch/o_iseri/2J_revision/T67/out/control_olddata_SEENFAILING/ci_reproduction_t67.csv` + `run_meta_t67.json`; stdout `.../logs/t67_control_old_1340721.out` |
| 1340722 | `cell_cluster_bootstrap.py` -- REAL run on the CORRECTED data from job 1340720 (`--n-rep 10000 --seed 12345`) | `afterok:1340720` | PD (pending on dependency) | `/speed-scratch/o_iseri/2J_revision/T67/out/real_correcteddata/ci_reproduction_t67.csv` + `run_meta_t67.json`; stdout `.../logs/t67_real_corrected_1340722.out` |

Submission commands (all `sbatch -p ps -c 1 --mem=8G -t 7-00:00:00`, single line, interpreter
`/speed-scratch/o_iseri/envs/step4/bin/python`):
- 1340720: `--wrap '.../python .../T67_scripts/build_agg_annual_t21.py /speed-scratch/o_iseri/2J_revision/T21/out/step8 /speed-scratch/o_iseri/2J_revision/T67/out'`
- 1340721: `--wrap '.../python .../T67_scripts/cell_cluster_bootstrap.py --agg-annual /speed-scratch/o_iseri/2J_revision/T03/input/agg_annual.csv --out-dir .../T67/out/control_olddata_SEENFAILING --n-rep 10000 --seed 12345 --label control_olddata_SEENFAILING_do_not_quote'`
- 1340722: `--dependency=afterok:1340720 --wrap '.../python .../T67_scripts/cell_cluster_bootstrap.py --agg-annual .../T67/out/agg_annual.csv --out-dir .../T67/out/real_correcteddata --n-rep 10000 --seed 12345 --label real_correcteddata'`

`squeue -u o_iseri -j 1340720,1340721,1340722` immediately after submission (single check, not
polled again, per no-parking rule): 1340720 R (antenna1), 1340721 R (edmonds), 1340722 PD
(Dependency) -- all three registered correctly.

**Next agent action once jobs land**: `sacct -j 1340720,1340721,1340722 --format=JobID,State,ExitCode,Elapsed`;
then `cat` (single-file, allowed on login node) the three `run_meta_t67.json`/`run_meta.json`
files and the two `ci_reproduction_t67.csv` files; append the real numbers to `## Verified`
below and to the manuscript-facing report in `## Decisions`/final summary.

## Step 0 -- how the corrected `agg_annual.csv` was found (NOT an existing file; had to be built)

1. Searched the whole T21 tree for an existing aggregate: `find /speed-scratch/o_iseri/2J_revision/T21 -iname 'agg_annual.csv'` (full-tree search, ~70s) returned **nothing**. VERIFIED: no pre-built corrected `agg_annual.csv` exists anywhere under T21.
2. Read `Step8_docs/08_simulation_plots.py` (local repo, the documented `agg_annual.csv` builder per `impl/2026-09-15_T16_step8_run_machinery.md` Q7) in full for `discover_runs()`/`load_cell_manifest()` (lines 154-234) before trusting it against T21.
3. **Found the landmine that rules out running it unmodified against T21**: `discover_runs()` only includes a 2022/2030 run directory when its `(sample, sim_hh_id)` pair is tagged `source == "new_2022_2030"` (`08_simulation_plots.py:210-226`), and that tag comes ONLY from an overlay file `cell_manifest.csv.new_2022_2030_*` (`load_cell_manifest()`, lines 176-185). Checked T21 on the cluster: `ls T21/out/step8/SingleD__Montreal_6A/cell_manifest.csv*` returns exactly ONE file (no overlay). So every T21 row's tagged `source="orig"`, `is_new_sample=False`, and `discover_runs()` would **silently skip every 2022/2030 directory** -- producing an EMPTY agg_annual.csv for both years if run unmodified. This mechanism exists only to arbitrate the OLD `campaign_N50` tree's mix of stale-vs-refreshed samples; it does not apply to T21, which is a single, fresh rebuild.
4. Confirmed T21's raw layout otherwise matches exactly what the builder expects: `T21/out/step8/<arch>__<city>/cell_manifest.csv` (columns `sample,sim_hh_id,hhsize,dtype,pr`, verified via `head -3`) + `sample_NNN_HH<id>/<year>/hourly_meters.csv` (verified header includes `Electricity:Facility`, 8760 data rows via `wc -l` = 8761).
5. Full-grid coverage check (via `find`, counts only, no compute): `T21/out/step8` has 24 cell dirs (25 minus `SimResults_Plotting_Schedules`), 1200 `sample_*` dirs (24 x 50), 2400 `hourly_meters.csv` files (1200 x 2 years) -- exactly the expected full grid, no gaps.
6. **Decision**: rather than editing `08_simulation_plots.py` (forbidden -- pipeline source outside `T67_scripts/`) or hacking a fake overlay manifest onto the T21 tree (a data-tree edit outside `T67_scripts/`, and would not be the cleanest audit trail), wrote a NEW, small, dependency-light script `T67_scripts/build_agg_annual_t21.py` that reimplements ONLY the two needed annual metrics, using the EXACT formulas from `08_simulation_plots.py:summarize_run()` lines 383-388 (verified by reading that source; cited in the new script's own docstring): `load_factor = mean(facility_kW_8760) / max(facility_kW_8760)`; `midday_share = sum(facility_kW over hour-of-day 9-16 inclusive) / sum(facility_kW over the year)`. It does not import or edit the original script.
7. **Cross-validated the extraction method before deploying**: scp'd one raw file down
   (`T21/out/step8/SingleD__Montreal_6A/sample_001_HH130228/2022/hourly_meters.csv`) and
   computed its annual `Electricity:Facility` total locally: **8209.333463306324 kWh**, max
   hourly demand **4.318053762803859 kW**. This matches `impl/2026-09-17_T45_T21_collector.md`
   section 3's independently hand-verified numbers for the SAME household/year (8209.333463
   kWh, 4.318054 kW peak) to 6 decimal places -- even though T45's number came from the
   `step9_activity` tree, not `step8`. Strong cross-check that the extraction/unit-conversion
   logic (J -> kWh via /3.6e6) is correct.
8. Tested `build_agg_annual_t21.py` locally against a small synthetic 1-cell/1-household test
   tree (`py -3.13`, this machine has a Python 3.13.5 launcher) -- ran cleanly, produced 2 rows,
   plausible values (`midday_share=0.4349`, `load_factor=0.2170`). `py_compile` clean on both
   new scripts.

**Time spent on step 0: roughly 20-25 minutes of active investigation** -- resolved within
budget, did not need to invoke the 30-45 min stop rule.

## Verified (numbers actually read, with source)

- Local functional test of `cell_cluster_bootstrap.py` against the LOCAL copy of the old
  defective data (`2J_docs_occ_nTemp/outputs_step8/agg/agg_annual.csv`, 6000 data rows),
  `--n-rep 10000 --seed 12345`:
  - `method_a_t_interval`: midday_share point 0.021380, CI [0.015807, 0.026952] (width 0.011145);
    load_factor point 0.018125, CI [0.014324, 0.021926] (width 0.007601). **These exactly match
    the point estimates already on record** in `impl/T03_out/run_meta.json`/`ci_reproduction.csv`
    (`SUBMITTED`/method-A numbers), confirming the local file is the same data T03 used and that
    `method_a_t_interval` (copied verbatim, unchanged) reproduces correctly.
  - NEW genuine `cell_cluster_bootstrap`: midday_share CI [0.015936, 0.026598] (width 0.010662);
    load_factor CI [0.013590, 0.022751] (width 0.009161).
  - **Comparison against method A on this OLD data**: load_factor is 20.5% WIDER than method A
    (0.009161 vs 0.007601) -- the theoretically expected direction, and a clear flip from the
    OLD retired stratified bootstrap's result on the same data (width 0.007352, i.e. 3.3%
    NARROWER -- see below). **midday_share is 4.3% NARROWER than method A** (0.010662 vs
    0.011145) -- NOT the theoretically expected direction, and even slightly narrower than the
    old retired stratified bootstrap's own midday_share width (0.011028, 1.05% narrower). This
    is reported as-is, not forced or hidden -- see Decisions for why this is not treated as a
    code bug.
- Old retired `method_b_cluster_bootstrap` numbers (T03's own on-record run,
  `impl/T03_out/ci_reproduction.csv` + `run_meta.json`, input `T03/input/agg_annual.csv`,
  6000 rows, still present on Speed, confirmed via `wc -l` = 6001 and header check on the
  cluster): midday_share point 0.021380, CI [0.015875, 0.026903] (width 0.011028, 1.05%
  narrower than method A's 0.011145); load_factor point 0.018125, CI [0.014457, 0.021808]
  (width 0.007352, 3.3% narrower than method A's 0.007601). This reproduces the "1.0-3.3%
  narrower" figure quoted in the task doc's Background section exactly -- confirms this is the
  correct "old retired" run to cite as DO NOT QUOTE.
- T21 rebuild's `out/step8/` tree: 24 cells, 1200 sample dirs, 2400 `hourly_meters.csv` files
  (full grid, verified via `find` counts on the cluster).

**Not yet verified (jobs pending)**: the actual corrected `agg_annual.csv` row count/schema
from job 1340720, and both `cell_cluster_bootstrap.py` cluster runs' real numbers (1340721 on
old data at full parameters matching the local test above -- expected to match closely but not
yet read from the cluster's own output; 1340722 on the real corrected T21 data -- this is the
number the manuscript/SI actually needs and does not exist yet).

## Decisions

1. Wrote a NEW aggregation script (`T67_scripts/build_agg_annual_t21.py`) rather than running
   `08_simulation_plots.py --rebuild-agg` unmodified against T21, because of the
   `is_new_sample`/overlay-manifest landmine in step 0 item 3 above -- running it unmodified
   would not error, it would silently produce ZERO 2022/2030 rows, which is worse than an
   obvious failure. This stays within the "never edit pipeline source outside `T67_scripts/`"
   rule (script only read, never modified or imported).
2. `build_agg_annual_t21.py` is pure-stdlib (`csv`/`os`/`re`/`json`/`time`, no pandas/numpy) --
   deliberately dependency-light so its per-file arithmetic is easy to hand-verify (see step 0
   item 7's exact match against T45's independently hand-verified number).
3. The corrected `agg_annual.csv` will have **2400 rows** (24 cells x 50 households x 2 years),
   not 6000 -- T21 only reran 2022 and 2030 (per the task doc's Rulings block and
   `impl/2026-09-15_T21_wp1_step8_step9_rerun.md`), unlike the old campaign's 5-year sweep. This
   is expected and correct, not a defect -- `build_paired()` in `cell_cluster_bootstrap.py` only
   ever uses year==2022 and year==2030 rows regardless.
4. The seen-failing control's mixed result (load_factor flips to wider as expected; midday_share
   does not) is reported honestly rather than treated as proof of a bug, because: (a) the new
   `cell_cluster_bootstrap` function was read and re-read against the task doc's exact spec
   (draw `n_cells` cell indices with replacement, concatenate intact per-cell arrays, no
   within-cell resampling) and matches it; (b) `method_a_t_interval` is a byte-for-byte copy of
   the original and reproduces T03's own on-record numbers exactly, so the paired-delta
   computation and metric definitions are not the source of any discrepancy; (c) a genuine
   cluster bootstrap is not mathematically guaranteed to widen every metric's interval -- it
   depends on that metric's actual between-cell vs within-cell variance decomposition, which can
   differ between `midday_share` and `load_factor`. The mandatory control step asked to "confirm
   ... produces a WIDER interval" as the general theoretical expectation, not as a pass/fail gate
   per metric; the honest, mixed result on the OLD (already-known-defective) data is itself
   informative and will be carried into the final report rather than smoothed over. **This
   entry does NOT decide whether the real (corrected-data) run in job 1340722 shows the same
   mixed pattern -- that must be read from the job's own output, not assumed from this control.**
5. Kept `T03_out`'s top-level run (not the `jun05/` subfolder) as "the" old retired number to
   cite, because its width deltas (1.05% / 3.3% narrower) match the task doc's own quoted
   "1.0-3.3% narrower" figure exactly; `jun05/` is an earlier/different snapshot and is not used.

## Next

1. `sacct -j 1340720,1340721,1340722 --format=JobID,State,ExitCode,Elapsed` (single check).
2. Once 1340720 (`build_agg_annual_t21.py`) shows COMPLETED: `cat` (or `head`)
   `/speed-scratch/o_iseri/2J_revision/T67/out/run_meta.json` -- confirm `n_rows_written` is
   2400 (or close, with any `n_missing_facility_column`/`n_short_series` explained), and
   `n_cells_found` is 24. If not 2400 or if either count is nonzero, STOP and diagnose before
   trusting job 1340722's downstream number (1340722 will have already run against whatever
   `agg_annual.csv` job 1340720 wrote -- if the schema/coverage is wrong, its output is not
   trustworthy either and must be rerun after a fix).
3. Once 1340721 and 1340722 show COMPLETED: `cat` both
   `.../out/control_olddata_SEENFAILING/ci_reproduction_t67.csv` and
   `.../out/real_correcteddata/ci_reproduction_t67.csv`, plus their `run_meta_t67.json` files.
   Cross-check 1340721's numbers against this doc's local functional test above (should match
   almost exactly, same seed/n_rep/input) as a sanity check that the cluster run used the same
   code and data.
4. Build the final side-by-side table (method A / genuine cluster bootstrap on corrected data /
   old retired stratified bootstrap DO-NOT-QUOTE) for `draft_S2_framework.md`'s clustering
   sentence (task doc's "Next" section, Ruling 1) -- **not done yet, waiting on 1340722's real
   number.**
5. If the real (corrected-data) genuine cluster interval turns out materially wider than method
   A for either metric, re-read the main-text separability claims that currently rest on method
   A alone (task doc's Ruling 5 / "Next" section) before quoting anything.

## WHAT I DID NOT VERIFY

- The actual corrected `agg_annual.csv` produced by job 1340720 -- have not read its
  `run_meta.json`, row count, or contents from the cluster; everything about "2400 rows, no
  gaps" above is a PREDICTION from the raw-file coverage count (`find`), not a confirmed read of
  the aggregation script's own output.
- Job 1340721's and 1340722's actual numbers -- not read yet (jobs were PD/R at submission
  time, not polled further per the no-parking rule). The "expected to match" claim in `## Next`
  item 3 is a prediction, not a verified fact.
- Whether `midday_share`'s narrower-than-method-A result on the OLD data also appears on the
  CORRECTED data -- genuinely unknown until 1340722 lands; explicitly not assumed either way.
- Whether any other script besides `08_simulation_plots.py` could have built `agg_annual.csv`
  more directly (e.g. an earlier, simpler Step-8 aggregation script mentioned as a possibility
  in the task doc) -- did not search further once the `08_simulation_plots.py` landmine was
  found and a clean reimplementation path was available; did not exhaustively grep
  `Step8_docs/` for alternative aggregators.
- Whether T21's `cell_manifest.csv` `dtype`/`pr`/`hhsize` columns are needed anywhere downstream
  of `agg_annual.csv` -- the new script does not carry them through (not needed by
  `cell_cluster_bootstrap.py`'s `build_paired()`, which only uses arch/city/sim_hh_id/year).
- Did not independently re-verify EVERY one of the 2400 raw files' row counts before submitting
  the cluster job -- relied on the `find`-based aggregate count (2400 files exist) plus the
  build script's own per-file 8760-row length check (`n_short_series` counter in its
  `run_meta.json`, not yet read).
