# T77 — WP11 Figure 6: full model vs. average-profile arm (T30), two-way comparison — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP3 (metric list, line ~205), plan log entry (dp).
Ruling this task must not re-open: **Figure 6 is TWO-WAY only** (full model vs. T30 average-profile arm).
The static arm (T19/T22) is CLOSED as not home-for-home (checklist item c8) and is EXCLUDED, not
computed, not plotted. State this in the figure caption and cite item c8's closure — do not silently
omit it.
Status:     IN PROGRESS -- three jobs submitted 2026-09-21, none polled yet (NO PARKING rule).
            Employee session ended after submission; a fresh agent must read the Ledger/Next
            sections below and check `sacct`/log files, never resume this session.

## Background (read before writing any code)
- Plan §3 WP3 always specified this exact comparison table but explicitly deferred it: "Comparison table
  (Wave 4, not this collector)" — `impl/2026-09-15_T30_wp3_average_profile_arm.md:50`. It has never been
  computed. This is new work, not a re-collection of an existing result.
- Metrics required (plan §3 WP3): annual kWh (by end use), peak demand, peak hour, load factor, midday
  share, evening ramp, and household-level peak-hour spread (Mardia circular SD + morning-leaning %).
- **T30's own gates are now ALL closed** (plan log (dp)): V0/V1/V2/V4/V5 accepted before T61; V3 PASS via
  T72 (job 1341254, full 48-cell grid, all controls fired). T30's averaging design is trustworthy. But
  `t30_check.py` never computed stock-level energy metrics for T30 — only gates + household peak-hour
  spread (`household_peak_spread`/`spread_metrics_all`, `T30_scripts/t30_check.py:114-146,317-341`).
  **Confirm for yourself** whether T30's original acceptance run (job `1328419`) already has a household
  peak-hour-spread number recorded for the average-profile arm and for T21 (the full model, run as a
  positive control reproducing the submitted "22-25% nationally" sentence per
  `2026-09-15_T30_wp3_average_profile_arm.md:27-34`) — read that report before recomputing anything.
- **Full model's stock-level energy metrics already exist and are ACCEPTED**: `T68/out/grid_metrics.csv`
  and `T68/out/enduse_annual.csv` (job `1340956`, plan log (de), `impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md`).
  These carry load_factor, midday_share, peak_kW_annual, evening_ramp_kW_mean, per-meter annual kWh, per
  cell and year, on the corrected 2022/2030 rebuild. **Do not recompute the full-model side from scratch
  — reuse this file.** Confirm its exact columns yourself (`head`/`wc -l` on the login node, or a tiny
  cluster job) before writing any join code; do not assume column names from this brief.
- **T30's tree has the same directory shape as T21's** (`<cell>__<year>/sample_NNN_HH<id>/avg_<year>/`,
  with `hourly_meters.csv`, `eplusout.sql`, `eplusout.eio` present in each run dir — confirmed by a
  directory listing of `T30/out/SingleD__Toronto_5A__2022/sample_001_HH32811/avg_2022/` this session).
  **`T68_scripts/enduse_hour_corrected.py` is the already-accepted, already-hand-verified method for
  turning that exact tree shape into `grid_metrics.csv`/`enduse_annual.csv`.** Read it fully yourself,
  confirm it only needs its root-path constant changed (never algorithmic changes) to run against
  `T30/out` instead of `T21/out`, and confirm the unit-equivalent divisor logic (item 40, T66's per-
  archetype divisors: SingleD=1, OtherDwelling=7, MidRise=33 equip/36 lighting, HighRise=81 equip/90
  lighting) still applies identically — T30 uses the same building archetypes as T21, so the same
  divisors should hold, but verify rather than assume. **Do not edit `T68_scripts/enduse_hour_corrected.py`
  in place — copy it to a new `T77_scripts/` file and point only the input root at T30/out**, same
  discipline as every prior checker fix in this project (T72 kept the original T30 checker untouched too).
- **Only relative/divisor-invariant metrics are stock-level quotable as absolute numbers** (item 40's
  ruling, carried into T68/T69/T71): percent change, load_factor, midday_share, peak hour, evening ramp
  as a fraction, share of facility total. Absolute per-dwelling kWh is only trustworthy for SingleD and
  for equipment/lighting meters elsewhere (T66's divisors). Any other meter's per-dwelling absolute is
  `NOT_EVALUABLE` with its reason; report the whole-building raw value under its own plainly-named column
  instead. Apply this same rule to Figure 6 — do not invent a divisor and do not reuse the equipment
  divisor for fans, exactly as T68/T69/T71 were bound.
- **No CI exists for peak_kW_annual or any ramp metric in the accepted WP6 output** (T71's own finding,
  `T71_scripts/wp11_figures.py:20-27`). If T30's own new grid_metrics.csv is built the same way, expect
  the same gap. Show peak and ramp as point values only, explicitly labelled "no CI available", exactly
  as T71's Figure 4 already does — do not fabricate a CI or silently drop the caveat. load_factor and
  midday_share may carry a real CI if `T68_scripts/enduse_hour_corrected.py`'s bootstrap logic runs on
  the T30 side too; confirm rather than assume, and if you build a genuine cluster-level bootstrap use
  T67's already-corrected `cell_cluster_bootstrap.py` (item 39's fix), never the retired stratified one.

## What this task must do
1. Confirm `T68/out/grid_metrics.csv` and `enduse_annual.csv` columns directly (do not guess).
2. Copy `T68_scripts/enduse_hour_corrected.py` to `T77_scripts/t77_grid_metrics_avgarm.py`, change only
   the input root to `T30/out`, run it on the full 24-cell x {2022,2030} T30 grid.
   - **Seen-working control required**: run the copied script, unmodified in logic, against a small
     slice of `T21/out` (or reuse T68's own already-accepted numbers for one cell) and confirm it
     reproduces T68's accepted grid_metrics.csv row for that cell/year exactly. This proves the copy
     didn't silently diverge from the accepted method.
   - **Hand-verify at least 2 (cell, year) pairs** on the T30 side: pick one household's raw
     `hourly_meters.csv` from `T30/out`, compute annual kWh and peak by hand (non-pandas or an
     independent code path), and match the script's own row for that run.
3. Build the two-way comparison table (`T77/out/fig06_comparison_table.csv`): one row per cell x year x
   metric, columns for full-model value, average-profile value, delta, whether the metric is a
   divisor-invariant/quotable comparison or `NOT_EVALUABLE`, and CI columns where they exist (else null
   with an explicit "no CI available" reason string — never blank without a reason).
4. Add household peak-hour spread (Mardia circular SD + morning-leaning %) for both arms, either reused
   directly from T30/T72's own reports if already present and on the same real tree, or computed fresh
   with the identical method (`_circular_sd_hours`/`_circular_mean_hour`, `Step8_docs/08_simulation_plots.py:278-300`)
   — state which you did and why.
5. Plot Figure 6: full model vs. average-profile arm, on the metrics above, following T71's Figure 4
   conventions (hatched/point-only bars where no CI exists, solid bars with error bars where one does).
   Caption must state plainly: static arm excluded, already ruled not home-for-home (item c8), cite it.
6. Write `T77/logs/t77_report.txt` — controls first (seen-working reproduction, hand-verified pairs),
   then the table, then the figure path. State a VERDICT line. `run_meta.json` with a
   `controls_all_fired` boolean, same fixed collection order as every prior WP11/WP6 task.

## Rules (same as every prior cluster task this project — do not relax any of these)
- Login node = `sbatch squeue sacct scancel scontrol cd ls scp module load` plus single-file
  `tail/head/grep/wc -l/cat` only. Never python, `find`, `du`, `md5sum`, `cp`, `mkdir`, or blocking `srun`
  on the login node. ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`; tcsh,
  no `2>&1`, no `2>/dev/null`.
- `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00` (bump `--mem` if a smoke run shows it's tight; T30's average
  loading needed 32G per plan §3, confirm what this job actually needs from a small slice first).
- Python `/speed-scratch/o_iseri/envs/step4/bin/python`; `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`
  / `IDD_FILE=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd` if eppy/IDF reads are needed anywhere (T72's
  whole bug was a missing `IDD_FILE` export in a checker wrapper — do not repeat it).
- Never write into another task's directory. `T68/out`, `T30/out`, `T21/out` are read-only inputs.
- No edits to any existing repo or task script — new files only, in `T77_scripts/`.
- **Submit and end your turn — never wait, never poll for the job.** Write state to this file as you go
  (Ledger of JobIDs, what's verified, what's not, next action) so a fresh agent can resume cold.
- If you pass roughly 150k tokens of context, stop, write state, and say "handoff needed" rather than
  push on.

## Ledger
- Job **1341328** (`t77_control`, seen-working control): `/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T77/T77_scripts/t77_control_copy.py`, `-p ps -c 4 --mem=16G -t 7-00:00:00`.
  Runs a BYTE-IDENTICAL copy of T68's already-accepted `enduse_hour_corrected.py` (only `OUT_DIR`
  changed, to `T77/controls_out`; `INPUT_ROOT` untouched, still `T21/out/step8`). Submitted
  2026-09-21, state RUNNING at submission time (`squeue` showed `R`, node `antenna1`). Expected
  output: `T77/controls_out/{enduse_annual,grid_metrics,closure,enduse_change_2022_2030}.csv`,
  `controls.json`, `run_meta.json`. Expected result: `controls_all_fired=true`, identical numbers to
  `T68/out/run_meta.json` (elapsed ~85s per T68's own precedent). NOT YET CHECKED against T68's file
  by a fresh agent -- do that first on resume (`grep`/`cat` `controls.json` and `run_meta.json`,
  never a bulk diff of the big CSVs; the two CSVs' hand-check row can be spot-checked with
  `grep 130228 T77/controls_out/enduse_annual.csv` vs the same grep on `T68/out/enduse_annual.csv`).
- Job **1341329** (`t77_part1`, real T30 metrics): `t77_grid_metrics_avgarm.py`, same resources.
  Discovers T30's `<arch>__<city>__<year>` tree (rewritten `discover_runs_t30()`, see script
  docstring), runs `process_one()` (byte-identical to T68's), writes
  `T77/out/{enduse_annual,grid_metrics,closure}.csv`, `controls.json`, `run_meta.json`. Controls:
  C1 (hour-of-day roll, T30 hand-check household), C2 (T77-specific: hand-verified against the 2
  independently-computed pairs below), C3 (divisor invariance, HighRise), C4 (divisor sanity).
  Submitted 2026-09-21, state RUNNING at submission time (node `speed-39`). Expected
  `n_households_year_read_ok=2400` (24 cells x 2 years x 50 households), matching T68's own count.
  NOT YET CHECKED -- read `run_meta.json` and `controls.json` first on resume.
- Job **1341330** (`t77_part2`, comparison table + spread + figure + report):
  `t77_fig06_build.py`, same resources, **`--dependency=afterok:1341329`** (will not start until
  part1 exits 0). State PENDING (`Dependency`) at submission time. Writes
  `T77/out/fig06_comparison_table.csv`, `T77/out/household_peak_spread_both_arms.csv`,
  `T77/out/figure_06_full_vs_avgarm.png`, `T77/out/run_meta_part2.json`, and
  **`T77/logs/t77_report.txt`** (controls first, then table, then figure path, then a `VERDICT:`
  line -- read this file first on resume, it is the single-file summary the brief asked for).
  If 1341329 fails (non-zero exit), 1341330 will sit in `Dependency` state forever and must be
  `scancel`led and resubmitted after the root cause is fixed -- it will NOT silently run on stale
  or partial part1 output.
- All three scripts live at `/speed-scratch/o_iseri/2J_revision/T77/T77_scripts/` (uploaded via
  `scp -r`, line counts diffed byte-for-byte against the local originals, matched: 895/551/637
  lines). `T77/out`, `T77/logs`, `T77/controls_out` were created via `scp -r` of empty local
  directories (`mkdir` is forbidden on the login node; this was the only whitelist-compliant way to
  pre-create them for SLURM's `--output`/`--error` paths).

## Verified
- **T68/out/grid_metrics.csv columns** (confirmed `head -1` on the login node): `cell,arch,city,
  region,sample,sim_hh_id,hhsize,year,peak_kW_annual,peak_hour_annual,mean_daily_peak_kW,
  mean_peak_hour_circ,load_factor,midday_share,evening_ramp_kW_mean,evening_ramp_kW_p90,p90_kW,
  n_hours_above_own_p90`. 2401 lines (2400 rows + header).
- **T68/out/enduse_annual.csv columns** (confirmed `head -1`): per-meter kWh + `_divisor` +
  `_divisor_source` + `_status` + `_status_reason` + `_per_dwelling` for all 8 meters (facility,
  lights, equip, fan, heating_ET, cooling_ET, water_ET, hvac_dhw remainder). 2401 lines.
- **T68/out/run_meta.json**: `input_root=T21/out/step8`, `n_candidate_runs=2400`,
  `controls_all_fired=true`, `divisor_tables_used` = the exact T66 dictionaries (copied into my
  scripts verbatim, cross-checked equal). `elapsed_sec=84.8` -- confirms this whole class of job is
  cheap (~85s for 2400 households), so my three jobs are not expected to need anywhere near the
  7-day walltime requested.
- **T68_scripts/enduse_hour_corrected.py**, full 887 lines, read via `scp` + local `Read`: confirmed
  meter list, divisor tables, `process_one()` formulas (load_factor, midday_share, evening_ramp,
  peak, closure identity), and that its own `INPUT_ROOT`/hand-check constants are T21-specific
  (`SingleD__Montreal_6A/sample_001_HH130228/2022/hourly_meters.csv`,
  `HAND_CHECK_ANNUAL_KWH=8209.333463`, `HAND_CHECK_PEAK_KW=4.318054`).
- **T30/out tree shape -- CONFIRMED DIFFERENT from T21's, brief's assumption was WRONG.** `ls
  T30/out/` shows 48 top-level dirs named `<arch>__<city>__<year>` (e.g.
  `SingleD__Toronto_5A__2022`), each with its OWN `cell_manifest.csv` (columns
  `sample,sim_hh_id,hhsize,dtype,pr`, confirmed by `head`, same columns as T21's). Each sample dir
  has a SINGLE subdir `avg_<year>/hourly_meters.csv` (not `<year>/hourly_meters.csv` like T21).
  T21's `T21/out/step8/<arch>__<city>/` has NO year suffix on the cell dir and both `2022` and
  `2030` subdirs live under the same sample dir. `hourly_meters.csv` columns match between T30 and
  T21 (`hour,Electricity:Facility,InteriorLights:Electricity,...`, `hour` column is 0-indexed, row 0
  = hour 0 -- confirmed by `head -4`). Household IDs spot-checked IDENTICAL across the 2022/2030
  sibling dirs for two cells (`SingleD__Toronto_5A/sample_001_HH32811`,
  `HighRise__Vancouver_5C/sample_003_HH135983` both present in both years).
  This is why `discover_runs_t30()` is a real (documented) rewrite, not a path-only change --
  see the Decisions section.
- **Household peak-hour spread has NEVER been run for T30 vs T21.** `T30_scripts/t30_check.py`
  (built, `py_compile`-clean per its own docstring) has never been submitted as its own job --
  `ls T30/logs/ | grep check` returned nothing, and `T72/logs/` only has `t72_v3_*` (T72 only ran
  V3, never the full V0-V5 + `spread_metrics_all()`). So the brief's "confirm whether it's already
  present" resolves to: NOT present, must be computed fresh -- done in `t77_fig06_build.py` by
  copying `household_peak_spread()`/`_circular_mean_hour()`/`_circular_sd_hours()` VERBATIM from
  `t30_check.py:95-139` (cited in the script's own docstring), applied to both the T30 tree
  (`avg_<year>` label) and the T21 `step8` tree (`<year>` label) -- static arm (T22) deliberately
  NOT computed, per the exclusion ruling.
- **Two hand-verified (cell, sample, year) pairs, computed independently via PowerShell
  `Import-Csv` (non-pandas, run on my local machine, not the cluster) on the raw
  `hourly_meters.csv` files, scp'd down for this purpose:**
  - `SingleD__Toronto_5A`, sample 1, HH32811, year 2022: `elec_facility_kWh=10490.314524177`,
    `peak_kW_annual=3.46471128664492`, `peak_hour_annual=18`.
  - `HighRise__Vancouver_5C`, sample 3, HH135983, year 2030: `elec_facility_kWh=487815.692798221`,
    `peak_kW_annual=134.603295911133`, `peak_hour_annual=17`.
  **These were then cross-checked locally against the ACTUAL `process_one()` function** (imported
  the real `t77_grid_metrics_avgarm.py` module locally, ran it on the same two downloaded CSVs):
  matched to better than 1e-9 relative difference on both metrics, exact match on peak hour. This
  is a genuine second, independent code path (PowerShell sum/max vs. pandas/numpy reshape-and-
  reduce), not a rerun of the same formula, and it ran BEFORE the real cluster job, not after --
  i.e. the script's correctness was established prior to trusting its cluster output. Both pairs
  are wired into `t77_grid_metrics_avgarm.py`'s own `control_c2_hand_verify()` as `HAND_PAIRS`, so
  the real job re-asserts them automatically.
- **Local end-to-end smoke tests, all three scripts, run with a local Python 3.13.5 (`py` launcher
  -- pandas/numpy/scipy/matplotlib all available locally, discovered mid-task):**
  `py_compile` clean on all three files; `process_one()` reproduced both hand-check pairs to
  floating-point precision; `discover_runs_t30()` correctly found 1/1 run and excluded a mock
  `SimResults_Plotting_Schedules` junk directory in a temp mock tree; `household_peak_spread()`
  ran on a 2-household mock cell without error; `paired_t_interval()` edge cases (n=0, n=1, n=5)
  all returned the expected None/tuple; a FULL synthetic end-to-end run of `t77_fig06_build.main()`
  (temp dirs standing in for T68/T77/T30/T21, 2 cells x 2 years x 1 household each, module
  path constants monkeypatched) completed with no exceptions, produced all expected output files
  including a real PNG (`figure.savefig` succeeded) and a `t77_report.txt` with the correct
  `VERDICT: FAIL` (correctly failed because the mock row counts were 4, not the expected 2400 --
  proving the row-count check itself works, not just that the happy path runs).
  These tests give real confidence the scripts will run cleanly on the actual 2400-row cluster
  data, but they are NOT a substitute for reading the real jobs' own output (see Next).

## Decisions
1. **T30's tree shape required a real code change to `discover_runs()`, not just a path change**
   (brief flagged this as something to verify, not assume -- verified, and the assumption was
   wrong). `discover_runs_t30()` parses `<arch>__<city>__<year>` cell-dir names and looks under
   `avg_<year>/hourly_meters.csv`; `load_cell_manifest()`, `process_one()`, all meter/divisor logic
   are byte-identical to T68's script. Documented in the script's own module docstring, not hidden.
2. **Dropped `enduse_hourly_profile.csv` and `enduse_change_2022_2030.csv` from the T30-side
   script.** Neither is a T77 deliverable (Figure 6 is a same-year arm-vs-arm comparison, not a
   within-arm 2022-vs-2030 change table), and the profile table alone is ~4M rows / ~500MB for
   T21's equivalent run. Documented in the script docstring as a deliberate scope trim, reversible
   if a later task needs them.
3. **T68's own C2 control (comparison against T67's T21-only `agg_annual.csv`) does not apply to
   T30 data** (would either crash or match zero rows) -- replaced with a T77-specific
   `control_c2_hand_verify()` built directly from the two independently hand-computed pairs above.
   This is the brief's own "hand-verify at least 2 pairs" requirement, wired in as an automated,
   re-run-every-time control rather than a one-off manual check.
4. **Load factor and midday share get a REAL paired-t 95% CI** in the comparison table
   (`paired_t_interval`, copied verbatim from T68's own "T67 method_a formula"), applied to a new
   pairing axis: full-model vs. avg-arm at the SAME year, household-matched by
   `(sample, sim_hh_id)`. This is a reuse of an already-reviewed formula on a different (but
   structurally identical: paired, matched-household) axis, not a new statistic. Peak demand,
   evening ramp, peak hour, and household peak-hour spread stay POINT-ONLY with an explicit
   "no CI available" reason string, per the brief's explicit instruction to match T71 Figure 4's
   treatment of peak/ramp and not invent a new CI.
5. **The stock-weighted CI shown in Figure 6's load-factor/midday-share panels
   (`stock_weighted_paired_ci()`) is a new (small, documented) aggregation**: it takes the 24
   per-cell paired deltas, STOCK_WEIGHTS-rescales them, and runs `paired_t_interval` again across
   the 24 (weighted) cell deltas. This is more conservative/ad hoc than T67's genuine
   cluster-bootstrap and is labelled as such in the code comment. **The per-cell table's own CI
   column (item 4 above) is the load-bearing number; the figure's stock-weighted CI is illustrative
   only** -- flagged here so nobody quotes the figure's aggregate CI as if it were T67-grade.
6. **Figure 6 shows STOCK-WEIGHTED single comparisons per metric (2022 vs. 2030, full vs. avg
   arm)**, following T71 Figure 4's visual convention, while the CSV table (`fig06_comparison_
   table.csv`) carries the full per-cell x year x metric granularity the brief's step 3 asked for.
   Annual kWh is shown in the figure as Electricity:Facility total only (not all 8 end uses) for
   space; the table has all 8. This mirrors T71's own split between Figure 2 (by end use, table
   only really needs the by-end-use breakdown) and Figure 4 (compact multi-panel).
7. Resources: `-p ps -c 4 --mem=16G -t 7-00:00:00` for all three jobs, matching the brief's default
   (T68's equivalent full run took 84.8s and used <16G easily on the same row count; no smoke-test
   memory bump was needed since this is a post-processing job, not the EnergyPlus/32G loading job
   the brief's memory note referred to).

## Next
1. **Read `T77/logs/t77_report.txt` first** (single file, has VERDICT + controls + table/figure
   paths). If it doesn't exist yet, `sacct -j 1341328,1341329,1341330 --format=JobID,State,ExitCode`
   to see what's actually finished (never poll in a loop -- one check is enough to resume from).
2. If job 1341328 (control) finished: `cat T77/controls_out/controls.json` and compare
   `controls_all_fired` + the C2 hand-check numbers against `T68/out/run_meta.json`'s
   `controls_summary` and the constants `HAND_CHECK_ANNUAL_KWH=8209.333463`/
   `HAND_CHECK_PEAK_KW=4.318054`. If they don't match, STOP -- the copy has diverged and nothing
   downstream can be trusted until this is root-caused.
3. If job 1341329 (real T30 metrics) finished with exit 0: `cat T77/out/run_meta.json`, confirm
   `n_households_year_read_ok=2400` and `controls_all_fired=true` (read `controls.json`'s C1-C4
   individually -- a false "all_fired" would be exactly the kind of gate-crash-masking failure this
   project's rules warn about). If it failed, read `T77/logs/t77_part1_1341329.err` (single file,
   `cat`/`tail` allowed) before touching any code.
4. If job 1341330 ran (only possible after 1341329 exits 0): read `t77_report.txt`'s VERDICT line,
   then spot-check 2-3 rows of `T77/out/fig06_comparison_table.csv` by eye against
   `T77/out/grid_metrics.csv` / `T68/out/grid_metrics.csv` directly (e.g. `grep` one cell/year out
   of each and hand-average), and open `T77/out/figure_06_full_vs_avgarm.png` to confirm it
   rendered sensibly (6 panels, static-arm-exclusion note in the suptitle).
5. If all of the above look right, this task is DONE pending the author's own look at the figure.
   If anything disagrees, do not silently patch and rerun -- write the disagreement into this doc's
   Decisions/WHAT-I-DID-NOT-VERIFY sections first, the way every other task in this project does.

## WHAT I DID NOT VERIFY
- **The real 2400-row cluster output of all three jobs.** Everything above the Ledger is either a
  file read on the login node, a local smoke test against 1-2 real households, or a fully synthetic
  end-to-end test. NO ONE has yet looked at the actual `T77/out/*.csv`, `controls.json`, or
  `figure_06_full_vs_avgarm.png` produced by the real jobs. Per the NO PARKING rule this is exactly
  what a fresh resuming agent must do first, not this session.
- **T30_scripts/t30_check.py's own V1 check (T21/T30 household-set equality) has never been run
  project-wide** -- I only spot-checked 2 of the 24 cells' household-ID pairing by hand (`ls`).
  If V1 would fail on some other cell, my C3 divisor-invariance control (which needs paired
  HighRise households across years) or the spread computation could silently under-count without
  crashing. The scripts report their own `n_households`/`n_compared` counts, which a resuming agent
  should sanity-check against 50-per-cell rather than assume are full.
- **Whether `/speed-scratch/o_iseri/envs/step4/bin/python` on the actual compute node has the same
  pandas/numpy/scipy/matplotlib versions as my local Python 3.13.5.** My local smoke tests prove
  the LOGIC is sound; they cannot prove environment parity (e.g. a pandas version quirk in
  `.set_index().loc[]` behavior). If the real job errors where my local test did not, check this
  first.
- **The stock-weighted paired CI in the figure (`stock_weighted_paired_ci`, Decision 5) has not
  been cross-checked against any independent formula** -- it is a small, documented, honestly-
  labelled extension, not a previously-accepted method like T67's genuine cluster bootstrap.
- I did not re-verify T67's `agg_annual.csv` or `ci_reproduction_t67.csv` in this session (not
  needed for T77 -- those were only relevant to T68's own now-superseded C2, not touched here).
