# T73 — plot WP11 Figure 7 (measured vs. simulated 2022 daily load shape, rebuilt runs)

Task doc:   this file
Status:     IN PROGRESS — job `1341255` submitted, not yet collected (no-parking rule: this
            employee does not poll/wait; a fresh agent collects when `sacct` shows COMPLETED).

## Background

T70 (job `1341184`, ACCEPTED by the manager, `impl/2026-09-21_T70_wp5_measured_vs_rebuilt_IMPL.md`) already
produced the underlying comparison data — it did NOT produce a figure. This task turns that accepted data
into Figure 7, the second reviewer's main requested comparison (measured IESO load shape vs. simulated,
on the REBUILT 2022 runs, not the retired ones).

Inputs (both already accepted, do not recompute anything in them):
- `/speed-scratch/o_iseri/2J_revision/T70/out/sim_vs_measured_toronto_2022_shape_rebuilt.csv` (215,905 bytes,
  join of measured IESO and simulated stock-shape metrics — read its header yourself, do not assume columns)
- `/speed-scratch/o_iseri/2J_revision/T70/out/sim_toronto_2022_shape_metrics_rebuilt.csv` (150,762 bytes)
- `/speed-scratch/o_iseri/2J_revision/T70/out/run_meta.json` (metadata, controls, seen-working-control values)

## What to do

1. **Read the actual CSV headers and a sample of rows yourself first** (`head`/single-file read, allowed on
   login node) — do not guess column names from this brief. Identify: what daily/hourly grain the shape
   metrics are at, whether there's a season x daytype breakdown (T70's IMPL doc mentions Toronto/2022/
   shoulder/weekday as one cell — confirm the full set of season x daytype combinations present).
2. **Design the figure to match this project's established figure style** (see T71's four figures,
   `impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md` and its `run_meta.json`, for dpi=600, ~7 inch width,
   PNG output convention, and the "hatch/grey anything not backed by a real interval" rule). This figure has
   NO bootstrapped CI in its source data (T70 only produced point metrics) — if you plot any interval, it
   must come from a source you can name; otherwise plot points only, undecorated, and say so in the report.
3. Plot measured vs. simulated as two lines (or a small multi-panel if season x daytype has more than ~4
   combinations — read the data first, then decide layout) over the 24-hour cycle, Toronto, 2022, rebuilt
   runs. Y-axis units must match what the CSV actually stores (kW per premise, or whatever the real column
   is) — state the unit in the axis label, do not invent one.
4. **Controls required:**
   - **Seen-working control:** independently re-read one (season, daytype, hour) cell's measured AND
     simulated values directly from the CSV (grep/single-file read, not just trusting your own plotting
     code) and confirm it matches what lands in the plot.
   - **Row-count / completeness control:** confirm every season x daytype combination present in the CSV
     appears in the figure (no silently dropped rows), and state the count.
5. Save the PNG under `/speed-scratch/o_iseri/2J_revision/T73/out/figures/fig07_measured_vs_simulated_shape.png`.
6. Write `T73/logs/t73_run_meta.json` (JobID, elapsed, figure metadata — dpi, dimensions — and the
   seen-working control's hand-read vs plotted values) following T71's `run_meta.json` shape.
7. **Submit via `sbatch`, do not wait, do not poll.** Write the JobID into this file's Ledger section below,
   then end your turn. The manager collects when `sacct` shows COMPLETED, and will pull the PNG back locally
   via `scp` to view it directly before accepting.

## Ledger

- Read the CSV headers directly first (per instruction 1), before writing anything:
  - `sim_vs_measured_toronto_2022_shape_rebuilt.csv` on the cluster (`head`/`wc -l`, login-node
    allowed): 1,761 lines (1,760 data rows), columns `period,daytype,series,calendar,
    measured_scope,metric,sim,measured,sim_minus_measured,data_vintage`. Byte size 215,905 —
    matches the task brief exactly.
  - `sim_toronto_2022_shape_metrics_rebuilt.csv`: 881 lines (880 rows), columns `scope,year,
    period,daytype,n_days,mean_premises,mean_kwh_per_premise,max_kwh_per_premise,load_factor,
    peak_to_avg,midday_share,mean_peak_hour,series,archetype,calendar`. Byte size 150,762 —
    matches the task brief exactly.
  - **No `hour` column exists in either file** — confirmed by reading both headers directly,
    not assumed. See FINDING 1 below.
- scp'd both CSVs + `run_meta.json` down to `impl/T73_out/` locally for read-only inspection
  (permitted — reading, not recomputing). Confirmed file sizes match the on-cluster originals
  exactly (`ls -la` both sides).
- Read `T70_scripts/t70_sim_vs_measured_rebuilt.py` (already local at `impl/T70_scripts/`) in
  full to understand what the saved columns actually mean before designing the figure — see
  FINDINGs 1 and 2 below, both grounded in this read plus direct file checks, not guessed.
- Wrote `T73_scripts/t73_fig07_measured_vs_sim.py` (new file, does not touch T70/T71 code or
  output). Compile-checked locally (`py -3.13 -m py_compile`) and on the cluster with the
  project interpreter (`/speed-scratch/o_iseri/envs/step4/bin/python -m py_compile`) — both
  clean. Confirmed `matplotlib` 3.10.8, `pandas` 2.3.3, `PIL` importable on that interpreter
  (single-file `python -c` checks, login-node allowed, never executed as a script there).
- **Ran a full functional smoke test locally against the REAL downloaded CSV** (not synthetic
  data — the real file is small enough, 216 KB, to test directly; this is local reconnaissance,
  not a cluster execution) by monkeypatching the script's `JOIN_CSV`/`OUT_DIR` constants after
  module load. Ran to completion in 0.8s, produced a 60-row CSV and one PNG. **Visually
  inspected the PNG** — five clean panels (load factor, peak-to-average ratio, midday share,
  mean peak hour, max per-premise load), correct hatching on the max-per-premise sim bars, shared
  legend + scope note in the sixth cell, all 12 period x daytype x-axis labels present and
  readable. This confirms the design works on the real numbers before the cluster job ran.
- Uploaded the script to the cluster via `scp -r` of a local directory tree that already
  contained `T73_scripts/`, `logs/`, `out/figures/` (T70's own noted preference — avoids a
  login-node `mkdir`, which is not on the CLAUDE.md allow-list). Verified byte-for-byte match
  both sides (15,535 bytes local and remote).
- CPU/queue check: `squeue -u o_iseri --format='%i %j %t %C'` showed several other 2J jobs
  running/pending (`histnu` array, `wp9_*`, `t72_v3fix`) at 1 CPU each — this job requests only
  1 CPU / 8 GB, well within headroom.
- **JobID `1341255`** submitted from `speed-submit2`:
  `sbatch -p ps -c 1 --mem=8G -t 7-00:00:00 --job-name=T73_fig07
  --chdir=/speed-scratch/o_iseri/2J_revision/T73
  --output=/speed-scratch/o_iseri/2J_revision/T73/logs/t73_run.out
  --wrap='/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T73/T73_scripts/t73_fig07_measured_vs_sim.py'`
  Single `squeue -j 1341255` check immediately after submission: `R` (running), node `antenna1`,
  0:02 elapsed — not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T73/`):
  - `logs/t73_run.out` — stdout/stderr of the job (progress lines or a traceback if it fails)
  - `out/figures/fig07_measured_vs_simulated_shape.png` — the figure
  - `out/figures/fig07_measured_vs_simulated_shape.csv` — the 60 plotted data points plus a
    `status` column (`COMPARABLE` / `NOT_UNIT_COMPARABLE` / `NOT_EVALUABLE`)
  - `out/figures/run_meta.json` — dpi/pixel size read back via Pillow, seen-working control,
    row-count/completeness control, headline-scope record

  **The job's own real cluster output has not been read by this employee** — only the LOCAL
  functional-test copy (same code, real data, run on this Windows machine, not the cluster) was
  inspected above. The cluster job should behave identically (same interpreter family, same
  input file, same code), but that is an expectation, not yet a measurement of job `1341255`
  itself. A failed job stays in this ledger with the line that supersedes it — never dropped.

## Verified

- **FINDING 1 (load-bearing — changes what this figure can show): T70's accepted output has NO
  hourly (24-point) load curve.** The task brief's step 3 assumes "two lines ... over the 24-hour
  cycle." Reading `T70_scripts/t70_sim_vs_measured_rebuilt.py:180-230` (`compute_slice_outputs`)
  shows it DOES build an hourly `profile_rows` list internally (hour-ending 1-24,
  `kwh_per_premise`, `share`) — but `main()` calls it as `_profile_rows, metric_row = ...`
  (leading underscore = deliberately discarded) and never writes `_profile_rows` to any CSV.
  Confirmed by reading the call site directly, not inferred. The only saved outputs are SCALAR
  shape metrics per (period, daytype, series, calendar, scope): `max_kwh_per_premise,
  load_factor, peak_to_avg, midday_share, mean_peak_hour`. Recomputing the hourly profile from
  raw per-household run files was explicitly forbidden by this task's own brief ("do not
  recompute anything in them"), so Figure 7 plots these five SAVED scalar metrics across period
  x daytype cells instead of an hourly curve. This is a real gap in what T70 was ever asked to
  save, not an error in T73.
- **FINDING 2 (load-bearing): `max_kwh_per_premise`'s sim and measured columns are NOT on the
  same physical unit, despite sharing one column name.** Confirmed two ways: (a) reading
  `t70_sim_vs_measured_rebuilt.py:383-397`, the sim series is divided by each household run's OWN
  annual mean before aggregation ("scale-free normalization"), so sim values are dimensionless
  ratios (order ~1-3); (b) independently reading `T02/out/ieso_metrics.csv` directly (the
  measured source, read-only, unchanged) shows its `full_year` `mean_kwh_per_premise` is
  0.82/0.88/0.83 (weekday/weekend/holiday) — NOT ~1.0 — confirming the measured side is real,
  unnormalized kWh/premise, never scale-free-normalized. T15/T70 already made the accepted
  decision to keep `max_kwh_per_premise` in the join despite this (script comment: "KEPT — task
  text names only mean_kwh_per_premise for removal") — this employee does not re-litigate that
  decision, but never plots the two sides as if they were unit-comparable: the sim bar in that
  one panel is hatched, its axis label and the figure caption both say "NOT unit-comparable"
  explicitly. `load_factor`, `peak_to_avg`, `midday_share`, `mean_peak_hour` are scale-invariant
  (dividing by a constant does not change a mean/max ratio or which hour is the peak) so those
  four ARE genuinely comparable and are plotted as ordinary paired bars, no caveat needed.
- **Season x daytype reconnaissance (instruction 1):** the raw join CSV has 44 distinct
  `(period, daytype)` combinations — `period` ranges over `full_year, shoulder, summer, winter`
  plus `month_01`..`month_12`; `daytype` is `weekday, weekend, holiday`. Read directly with
  pandas locally on the downloaded copy (`.drop_duplicates()`), not assumed. `series` has 2
  values (`facility, nonhvac`), `calendar` has 2 (`eplus, real2022`), `measured_scope` has 2
  (`Toronto, Ontario`), `metric` has 5 (the five scalar shape metrics above).
- **Headline-scope reconnaissance:** filtering to `calendar=eplus` (confirmed primary — the
  script's own comment: "the day type the occupancy schedule actually ran against"),
  `series=facility` (whole-building electricity, the physically meaningful comparison to IESO's
  grid-metered load), `measured_scope=Toronto`, and `period` restricted to T70's own headline
  4-period set `[shoulder, winter, summer, full_year]` (literally the prefix of that script's own
  `period_order` list, before the 12 individual months) gives exactly 12 `(period, daytype)`
  combinations x 5 metrics = 60 rows, all present, zero NaN in `sim`/`measured` — read directly
  with pandas on the downloaded copy, not assumed.
- **Local functional-test seen-working control** (on the REAL data, run locally): independently
  re-read `(period=shoulder, daytype=weekday, calendar=eplus, series=facility,
  measured_scope=Toronto, metric=max_kwh_per_premise)` via a fresh boolean mask — got
  `sim=2.005789427462265, measured=1.6171703590483548`, matching the row seen in the raw file's
  first data line exactly. `n_rows_matched=1` (unique, not ambiguous).
- **Local functional-test row-count/completeness control**: `n_period_x_daytype_combos_in_full_
  raw_csv=44`, headline-scope combos present=12 (matches expected 12 exactly, `missing_from_
  figure=[]`), 12 individual months explicitly recorded as `periods_excluded_by_design_(not_a_
  silent_drop)`, `n_rows_used_in_figure=60` (12 combos x 5 metrics). All from the actual script
  run against the real downloaded CSV, not asserted.

**Everything in this section came from the LOCAL functional test against the real (downloaded,
read-only) CSV, or from direct file/script reads — none of it is from the cluster job's own
output, which is unread as of this write (see WHAT I DID NOT VERIFY).**

## Decisions

1. **Figure shows five scalar shape metrics across 12 period x daytype cells, not an hourly
   curve** (FINDING 1 above forces this — no hourly data exists in the accepted, non-recomputable
   input). This is the single biggest departure from the task brief's literal wording ("two lines
   ... over the 24-hour cycle") and is flagged prominently, in this doc, in the script's own
   header docstring, in `run_meta.json`'s notes, and in the figure's own caption — never silently
   substituted.
2. **Headline scope restricted to `calendar=eplus, series=facility, measured_scope=Toronto`,
   periods limited to T70's own 4-period headline set** (`shoulder, winter, summer, full_year`),
   dropping the 12 individual months from the plot. Not specified by the task brief, which left
   layout to this employee's judgment once the real grain was known. Chosen because: (a) `eplus`
   is T70's own documented primary calendar; (b) `facility` is the only series directly
   comparable to IESO's whole-grid measured load (`nonhvac` is a partial component); (c) `Toronto`
   is the direct local comparison (`Ontario` is a broader companion, already in the CSV, not
   re-plotted); (d) the 4-period set is literally the prefix T70's own script uses before
   appending 12 months — reusing an existing, already-meaningful grouping rather than inventing
   one. The row-count control states explicitly which combinations were excluded and why, so nothing
   is a silent drop.
3. **`max_kwh_per_premise` is shown, not hidden, but visually flagged** (hatched sim bar, "NOT
   unit-comparable" in its axis label, title, and the figure caption) rather than dropped from the
   figure — consistent with this project's "never silently drop or hide a value, mark it distinct
   instead" convention (same pattern T71 used for NOT_EVALUABLE cells).
4. **5-panel layout, 2 rows x 3 columns, sixth cell holds the shared legend + a scope note**
   (calendar/series/scope/period set spelled out on the figure itself) rather than repeating a
   legend five times or omitting the scope from the image. This follows the brief's own
   instruction ("small multi-panel if season x daytype has more than ~4 combinations") — with five
   metrics instead of four seasons, but the same principle (more items than fit one panel → grid).
5. **PNG at dpi=600, ~10.4 x 5.9 inch canvas** (wider than T71's 7-inch single/double-panel
   figures because this is a 3-wide grid) — dpi verified by reading the saved PNG back with
   Pillow, not just asserting the `dpi=` kwarg (same convention as T71). Local test showed
   599.9988 dpi (the same harmless PNG pixels-per-metre rounding artifact T71 already
   documented, not a real shortfall).
6. **No confidence interval plotted anywhere in this figure.** T70's saved output only ever
   carries point values for these five metrics (no bootstrap/CI columns exist in
   `sim_vs_measured_toronto_2022_shape_rebuilt.csv`) — confirmed by reading its header directly.
   All bars are plain point comparisons, undecorated, exactly as the task brief's own fallback
   instruction requires when no real interval exists.

## Next

- Manager collection (fresh agent, later): `sacct -j 1341255` first for state/exit code, then
  `run_meta.json` (seen_working_control, row_count_control, notes — confirm these read the same
  on the real cluster run as they did in this employee's local functional test against the same
  input file), then the CSV and PNG themselves.
- If the cluster job's `seen_working_control` or `row_count_control` numbers differ AT ALL from
  the local-test numbers recorded above (same input file, so they should match exactly), that is
  a new finding needing diagnosis before the figure is trusted — do not assume environment
  parity.
- scp the PNG + CSV + `run_meta.json` back to `impl/T73_out/` for manager/author viewing (not yet
  done as of this write for the CLUSTER job's own outputs — only the local-test copies exist
  there right now, and those must not be confused with the real cluster output).
- This is WP11's Figure 7 (measured-vs-simulated, rebuilt runs) — the second reviewer's headline
  ask. Once accepted, remaining WP11 work per T71's own "Next": Figure 6 (blocked on T30),
  Figures 1/8/9 (need path confirmation).

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341255`).** Everything numeric in `##
  Verified` above comes from a LOCAL functional test of the exact same script against the
  downloaded (real, unmodified) CSV, plus direct file/script reads — not from the cluster
  job's own execution. `logs/t73_run.out`, `out/figures/run_meta.json`, the CSV, and the PNG on
  the cluster are all unread as of writing this doc.
- Whether the cluster job completes within a reasonable time or hits any environment difference
  (different pandas/matplotlib version behavior, different filesystem read speed) — the local
  test ran in 0.8s on a 216 KB file with no chunking, so the cluster job (same tiny input, no
  per-household loop) is expected to be similarly fast, but this is an expectation, not a
  measurement of job `1341255`.
- Whether `T02/out/ieso_metrics.csv` (read as part of FINDING 2's independent check) has changed
  since T15/T70 last used it — read once here for the normalization check, not re-validated
  against any earlier accepted snapshot.
- Whether Applied Energy's own figure guidelines would prefer a different metric selection or
  layout than the 5-panel grid chosen here — not read for this task (same caveat T71 already
  logged for its own 7-inch width default).
- Whether the `real2022` calendar or `Ontario` measured_scope companion views (both present in
  the same join CSV, neither plotted here) would change the qualitative picture — deliberately
  out of scope for this headline figure, not evaluated.
