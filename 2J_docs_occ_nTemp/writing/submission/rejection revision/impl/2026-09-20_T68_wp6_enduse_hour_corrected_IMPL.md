# T68 -- WP6 Part A: end use x hour on the CORRECTED rebuild -- implementation state

Task doc: `impl/2026-09-20_T68_wp6_enduse_hour_corrected.md`
Status:   DONE -- collected by the manager 2026-09-21, all controls fired, see Verified below.

## Ledger

- **JobID `1340956`** -- `enduse_hour_corrected.py` (this task's real run + all four controls,
  same job). Submitted from `speed-submit2` via:
  `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00 --wrap '/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T68/T68_scripts/enduse_hour_corrected.py > /speed-scratch/o_iseri/2J_revision/T68/logs/t68_run.out'`
  Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python` (symlink to `python3.10`, confirmed
  present via `ls -la` before submission, not executed on the login node).
  Single `squeue -j 1340956` check immediately after submission: `R` (running), node `speed-07`,
  0:02 elapsed -- not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T68/`):
  - `logs/t68_run.out` -- stdout/stderr of the whole job (progress lines + traceback if it fails)
  - `out/enduse_annual.csv` -- one row per household x year, raw + per-dwelling + divisor/status columns
  - `out/enduse_hourly_profile.csv` -- mean load by hour x meter x season x daytype, per household x year
  - `out/grid_metrics.csv` -- peak/load_factor/midday_share/ramp/p90 per household x year
  - `out/closure.csv` -- lights+equip+fan+remainder = Facility identity, per household x year
  - `out/enduse_change_2022_2030.csv` -- the reviewer-facing deliverable (see task doc item 4)
  - `out/controls.json` -- C1-C4, each with `outcome` in
    `{ran_and_fired, ran_not_fired, not_evaluable_crashed}`
  - `out/run_meta.json` -- households read/skipped, divisor tables used, WaterSystems absence
    counts, zero-2022-denominator counts, the `undelivered.csv` sweep, and a `controls_all_fired`
    boolean the manager should read FIRST.

  **No number in these files has been read yet by this employee.** A failed run stays in this
  ledger with the line that supersedes it -- it is never dropped.

## Verified (numbers actually read, with source)

- CPU budget check before submission: `squeue -u o_iseri --format='%i %j %t %C' | grep -v histnu`
  on `speed-submit2` returned zero non-`histnu` rows (exit 1 from `grep -v`, meaning no lines
  matched, i.e. every running row belonged to the `histnu` project) -- confirmed 0 of the 2J
  project's 32-CPU ceiling was in use before this job's 8 CPUs were requested.
- The T21 rebuild's raw CSV format, read directly via a single `head`/`sed` on the login node
  (allowed, single-file): `hourly_meters.csv` has a literal `hour` column running 0..8759 (row
  index, NOT hour-of-day 0..23) -- confirmed via
  `SingleD__Montreal_6A/sample_001_HH130228/2022/hourly_meters.csv`, rows 1-3 and 8760-8762. This
  is what C1's "roll every column except hour forward by 3" control actually manipulates: the
  script rolls the METER VALUES by 3 row-positions while the (irrelevant-to-reshape) `hour` column
  values are left untouched, matching the task doc's exact wording.
- The two divisor dictionaries (`T66_CELL_EQUIP_DIVISOR`, `T66_CELL_LIGHT_DIVISOR`) were read
  verbatim out of
  `/speed-scratch/o_iseri/2J_revision/T66/scripts/step9_validate_full_corrected.py` via
  `scp` + local `grep -n -A30`, never re-derived: SingleD=1, OtherDwelling=7 (both meters),
  MidRise=33 (equip)/36 (light), HighRise=81 (equip)/90 (light), uniform across all six cities --
  matches ruling 3 exactly.
- `T67`'s `agg_annual.csv` schema (`arch,city,sim_hh_id,year,midday_share,load_factor`, 2400 rows,
  confirmed via `head -3` + `wc -l` on the login node) does NOT carry an annual
  `Electricity:Facility` total -- confirmed this is why C2 splits into two independent checks
  (reproduce midday_share/load_factor against this file; reproduce the annual kWh/peak kW
  separately against the one hand-verified household).
- `T67`'s `real_correcteddata/ci_reproduction_t67.csv` was read in full (8 data rows): the
  `cell_cluster_bootstrap_GENUINE` rows for `midday_share` (point 0.0073235, CI
  [0.0061604, 0.0085934]) and `load_factor` (point 0.0049432, CI [0.0041285, 0.0057432]) are the
  exact numbers this task's script reads and copies verbatim into
  `enduse_change_2022_2030.csv`'s stock-weighted rows for those two metrics, per ruling 6 -- not
  recomputed.
- **Local functional test, run against a small synthetic tree shaped exactly like T21's
  (2 cells x 2 households x 2 years, 8 household-years total)** using the real Python 3.13
  interpreter available on this machine via the `py` launcher (no interpreter was assumed missing
  without checking -- `python`/`python3` are Microsoft Store stub aliases that do not run, but
  `py -3.13` is a genuine working interpreter with numpy 2.3.5 / pandas 2.3.3 / scipy 1.17.0
  installed):
  - `py -3.13 -m py_compile enduse_hour_corrected.py` -- clean, twice (before and after the
    bugfix below).
  - `discover_runs()`: found exactly 8 runs (4 households x 2 years), 0 skipped -- matches the
    synthetic tree's construction.
  - `process_one()` (run sequentially, not via `Pool`, to avoid a Windows-only
    multiprocessing-spawn/module-import artifact of this local test method -- irrelevant on the
    cluster, which uses POSIX `fork`): all 8 household-years processed OK.
  - Divisor logic: SingleD's `equip_kWh_per_dwelling == equip_kWh` (divisor 1, confirmed
    numerically equal) and SingleD's `fan_kWh_status == "QUOTABLE"` (ruling 4's "SingleD
    quotable everywhere" bullet). HighRise's `equip_kWh_divisor == 81.0`,
    `lights_kWh_divisor == 90.0`, and `fan_kWh_status == "NOT_EVALUABLE"` with
    `fan_kWh_per_dwelling == "NOT_EVALUABLE"` -- all confirmed by assertion, not eyeballing.
  - Closure identity: `identity_residual_kWh` (Facility - (components + remainder)) is exactly 0
    on all 8 synthetic rows (this residual is 0 by construction of the formula, so this checks the
    arithmetic wiring, not the physics).
  - `build_change_table()`: ran without exception, produced 30 rows; `water_ET_kWh` correctly
    shows 2 zero-2022-denominator exclusions (the synthetic HighRise household's water meter was
    deliberately set to 0 in both years, mimicking ruling 8's real MidRise finding) -- confirms
    the zero-denominator guard fires on exactly the households it should, not more, not fewer
    (fixed a bug here -- see Decisions).
  - **C1 fired**: synthetic peak hour moved from 23 to 2 after a +3 roll -- 23+3 mod 24 = 2,
    exactly as predicted; midday_share changed. **C3 fired**: raw-series and per-dwelling-series
    percent change for HighRise equipment agreed to 7.5e-15 (floating-point noise). **C4 fired**:
    per-dwelling equip/light means for SingleD and HighRise landed within the same order of
    magnitude (printed pairs: SingleD equip 979 kWh vs HighRise equip-per-dwelling 722 kWh;
    SingleD light 857 kWh vs HighRise light-per-dwelling 568 kWh -- all quotable-looking numbers,
    not the raw whole-building hundreds-of-thousands). **C2 ran without crashing** (outcome
    `ran_not_fired`, expected on synthetic data since the dummy hand-check constants and dummy
    T67 numbers used for this local-only test do not match the synthetic tree's arithmetic by
    construction -- this only proves the comparison logic executes cleanly, not that the real
    numbers will match; that is unverified until the real job's `controls.json` is read).
  - This is the strongest verification available without a full cluster run: every control except
    C2 was proven to fire correctly on a case engineered to make it fire, and C2 was proven not to
    crash. The real C1-C4 outcomes on the actual T21 data are unread (see WHAT I DID NOT VERIFY).

## Decisions (things the task doc left to this employee, and what was assumed)

1. **Per-cell change rows get a paired household t-interval (T67's "Method A" formula, reused);
   the stock-weighted row gets the cell cluster bootstrap.** The task doc's ruling 5/6 text is
   compatible with more than one reading of where an "interval" applies at the per-cell level.
   Read literally, T67's `cell_cluster_bootstrap` resamples WHICH of the 24 cells appear -- that
   resampling unit is undefined for a single cell in isolation. So per-cell rows use the simpler,
   already-existing paired t-interval (`stats.t.interval` on within-cell household deltas, the
   exact formula T67 calls `method_a_t_interval`), which needs no cell-resampling and is a
   legitimate reuse, not a new statistic. Only the stock-weighted (all-24-cells) row uses the
   cell-level cluster bootstrap. This reading is also the only one consistent with ruling 5's own
   premise -- that per-cell changes "are not resolved at 50 or 200" households -- since that
   finding implies someone already looked at a per-cell interval and found it too wide, which is
   exactly what the per-cell t-interval in this task's output will show.
2. **A new function, `stock_weighted_cluster_bootstrap`, was written for the non-shape end-use
   metrics** rather than calling T67's `cell_cluster_bootstrap` unmodified, because T67's function
   computes a flat pooled mean across all resampled households, which is NOT the stock-weighted
   quantity (`STOCK_WEIGHTS`-weighted archetype mean) this project's own conventions use
   everywhere else (T06's `stock_row`, `08_simulation_plots.py`'s STOCK_WEIGHTS split). The new
   function uses the IDENTICAL resampling unit T67 specifies (draw `n_cells` cell indices with
   replacement from the `n_cells` available, keep each drawn cell's household array intact) --
   only the per-replicate statistic changes, from a flat mean to a stock-weighted mean of
   archetype means. This is a genuinely new function (never existed before), but its resampling
   mechanics are a direct, literal copy of T67's, satisfying "use the same resampling unit" while
   not reusing a formula (flat pooled mean) that this project does not otherwise use for
   stock-level numbers. **For `midday_share`/`load_factor` specifically, this new function is
   NEVER called** -- those two metrics' stock-weighted numbers are read verbatim from T67's own
   output file instead, per ruling 6's explicit instruction not to write "a third bootstrap" for
   metrics T67 already scored.
3. **Percent change, not absolute kWh change, carries the bootstrap interval for every end-use
   meter** (facility, lights, equipment, fan, the three thermal `*:EnergyTransfer` meters, and the
   HVACDHW remainder). Percent change is divisor-invariant (proven by control C3) and is the one
   quantity that is well-defined and comparable across ALL meters, including the three meters
   (fan, facility, thermal) that have NO derived per-dwelling divisor. Reporting the interval on
   an absolute-kWh basis would have forced a choice between raw whole-building units (physically
   misleading for multi-unit archetypes) or per-dwelling units (undefined for fan/facility/thermal
   per ruling 4) for every row. Raw 2022/2030 absolute values and their raw absolute change are
   still reported as separate columns for every row (never suppressed), so no information is lost
   -- only the CI itself is denominated in percent.
4. **Household-level percent change is defined per household as
   `100*(v2030-v2022)/v2022`, using RAW whole-building annual kWh** (not the per-dwelling series),
   then bootstrapped/t-interval'd on that household-level array. Ruling 4/C3 guarantees this is
   numerically identical to doing the same thing on the per-dwelling series wherever a divisor
   exists, so using the raw series uniformly avoids ever needing a per-dwelling value for
   fan/facility/thermal meters just to compute a percent change.
5. **Households with a zero 2022 baseline for a given meter are excluded from that meter's
   percent-change statistics (both per-cell and stock-weighted), not treated as an infinite or
   undefined change.** This directly implements ruling 8 (WaterSystems:EnergyTransfer absent for
   every MidRise household in T06's old-campaign read) generalized to any meter/archetype
   combination that behaves the same way on the rebuild. The exclusion count is tracked BOTH
   globally per meter (`run_meta.json` `zero_2022_denominator_counts_by_meter`) and per cell
   (`enduse_change_2022_2030.csv` `n_zero_2022_denominator_excluded` column, fixed to be
   cell-specific during the local functional test -- see the bug note below) so a reader can see
   exactly which cells lost data to this rule, never a silent `NaN`.
6. **`OLD_CAMPAIGN_DO_NOT_QUOTE` shape-plausibility comparisons against T06's old-campaign output
   were NOT produced.** Ruling 1 makes this comparison permissive ("you may use them"), not a
   required deliverable, and it is absent from the task doc's numbered list of things to produce
   (section 3, items 1-7). Left out to keep scope to exactly what was asked; flagged here so the
   manager can request it explicitly if wanted.
7. **A local functional test against a synthetic tree was run before upload**, in addition to
   `py_compile`, because a real Python 3.13 interpreter was available locally via the `py`
   launcher (the plain `python`/`python3` commands on this machine are non-functional Microsoft
   Store stubs, confirmed by their actual error output, not assumed). This exceeds the task doc's
   minimum bar ("py_compile if available; otherwise a careful line-by-line re-read") but was
   judged worthwhile given the script's complexity (887 lines, four independent control functions,
   a new bootstrap variant) -- a syntax-only check would not have caught the per-cell
   zero-denominator bug found and fixed below.
8. **Bug found and fixed before upload**: the first draft's per-cell
   `n_zero_2022_denominator_excluded` column used a broken boolean-arithmetic expression
   (`int((arr.size == 0) and n_zero_denom or 0)`) that attributed the GLOBAL (all-cells) zero-
   denominator count to whichever cell happened to have an empty percent-change array, rather than
   that cell's own count. Fixed by tracking a per-`(arch,city)` dictionary
   (`n_zero_denom_by_cell`) alongside the existing global counter. Re-ran the full local
   functional test after the fix; all assertions still pass. This bug would only have been visible
   on the real data for a meter/cell combination with a genuine partial (not all-or-nothing)
   zero-denominator pattern -- the synthetic test's all-or-nothing HighRise-water case happened not
   to expose it numerically (both the buggy and fixed versions print a nonzero count for that one
   cell), so this was caught by code inspection during the fix, not by a failing assertion. Worth
   flagging in case the manager wants to spot-check this column specifically once real numbers
   land.

## Manager collection (2026-09-21) -- all owed checks done, see plan log (de) for full text

- `sacct -j 1340956`: `COMPLETED`, exit `0:0`, elapsed 00:01:59 (log confirms 84.8s real work --
  this is a post-processing job over already-simulated files, not a new simulation campaign, so a
  fast runtime is expected, not suspicious).
- `run_meta.json`: `controls_all_fired = true`. `n_households_year_read_ok = 2400`, `skipped = 0`
  -- matches the expected 1,200 households x 2 years exactly. `undelivered_csv_sweep.n_found = 0`
  -- T21 is one of the trees that never writes this file (item 31's standing rule), so this is
  UNINFORMATIVE, not reassuring, and is recorded as such rather than read as a clean bill.
- `controls.json`: all four of C1-C4 read `ran_and_fired`, not just the summary boolean. C2's hand
  check matches to `~3e-7` on annual kWh and `~2.4e-7` on peak kW (relative), so the reproduction
  is trustworthy, not a coincidence.
- **Divisor key coverage checked key-by-key** (this employee had flagged it as assumed, not
  checked): `ls .../T21/out/step8/` lists exactly the 24 `<Arch>__<City>` cell directories (plus
  one non-cell `SimResults_Plotting_Schedules`, correctly excluded, `discover_skipped=0`), and
  every one of those 24 names is a key in both `T66_CELL_EQUIP_DIVISOR` and
  `T66_CELL_LIGHT_DIVISOR` in `run_meta.json`. No missing key, no silent skip.
- **`stock_weighted_cluster_bootstrap` read line by line on the cluster** (item 39's standing
  rule for anything named "cluster bootstrap"): it draws `n_cells` cell indices WITH REPLACEMENT
  from the `n_cells` available cells per replicate (identical resampling unit to T67's genuine
  cluster bootstrap), and only the per-replicate statistic changed, to a stock-weighted mean
  across archetypes. **This is a genuine cluster bootstrap, not stratified** -- decision 2 is
  accepted as described. `STOCK_WEIGHTS` itself is confirmed unchanged from T06 v2 (docstring
  states this and the constant's derivation from `_RAW_STOCK` was read, not just trusted).
- Decision 1 (per-cell rows get a paired t-interval, only the stock-weighted row gets the cluster
  bootstrap) is **accepted** -- the reasoning is sound and the alternative (a cluster bootstrap on
  a single cell) is genuinely undefined.
- `zero_2022_denominator_counts_by_meter`: all 8 meters show 0 exclusions on this run (differs
  from T06's old-campaign MidRise-water finding, but that comparison is
  `OLD_CAMPAIGN_DO_NOT_QUOTE` per ruling 1 and the two trees are not required to match). The
  per-cell zero-denominator bug this employee found and fixed pre-upload could not be
  re-exercised here since no cell hit a partial zero-denominator pattern on this run; the fix
  itself was read in the script and is correct.
- `enduse_change_2022_2030.csv`: 250 rows as expected. Spot count of `change_quotable`: 154
  `True`, 82 `False`, ~14 `NOT_EVALUABLE` (naive `awk -F,` split, a handful of rows likely
  mis-split by a comma inside the free-text reason column -- exact count not load-bearing, the
  QUOTABLE/not-QUOTABLE gate itself is read per-row in the file, not from this tally). **Only
  rows marked `QUOTABLE` may be described as a change in manuscript text (ruling 5).**

**Verdict: T68 / WP6 Part A is ACCEPTED. All four controls fired, all four employee decisions are
sound, the divisor coverage gap flagged as unverified is now closed clean, no red flag found.**

## Next

- This was Part A only. WP6 Part B (T29/T32 scenario arms, item 30's common-household rule and
  item 33's reproducible reversion exclusion) and WP11 (figures) are both unblocked; neither
  dispatched yet as of this collection. See plan log (de) for the manager's recommendation.

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1340956`) on the real T21 data.** Everything
  in `## Verified` above about the script's correctness comes from a synthetic local test and a
  `py_compile` pass, not from the real run's output -- `controls.json`, `run_meta.json`, and all
  five CSVs are unread as of writing this doc.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue --
  2,400 files x ~8760 rows x 10 columns via pandas across 8 workers is expected to be fast
  (T06 processed 1,200 files in well under a minute per its own `run_meta.json` `elapsed_sec`,
  by inference from the v2 script's own timing print, though that exact number was not re-read
  here), but this is an expectation, not a measurement of the new job.
- Whether every one of the 24 T21 cells actually has a matching entry in both
  `T66_CELL_EQUIP_DIVISOR` and `T66_CELL_LIGHT_DIVISOR` (they should, since T66's dictionaries were
  built for the same 4-archetype x 6-city grid) -- not cross-checked key-by-key against T21's
  actual 24 cell directory names on the cluster, only assumed to match by construction (both were
  built for the same `<Arch>__<City>` naming convention).
- Whether `paired_t_interval`'s minimum-`n=2` guard, or `safe_pct_change`'s zero-denominator
  guard, ever fires in some unexpected way on the real 1,200-household-pair data that the small
  synthetic test (4 household pairs) could not exercise -- e.g. a cell where MOST but not all
  households have a zero 2022 baseline for some meter, leaving very few valid pairs for that
  cell's t-interval. `run_meta.json`'s per-meter zero-denominator counts should be read for this
  before trusting any single cell's interval.
- The exact wall-clock/CPU cost of the job was not estimated in advance beyond copying T06's own
  `-c 8 --mem=32G` resource shape; if this proves insufficient (e.g. OOM under the full
  1,200-household x 8-worker `Pool`), a resubmission would be needed and this ledger's line for
  `1340956` would stay, with the resubmission's JobID added below it, not replacing it.
