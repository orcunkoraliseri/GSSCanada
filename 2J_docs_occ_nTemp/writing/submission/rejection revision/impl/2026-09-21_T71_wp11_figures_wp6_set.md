# T71 -- WP11: the four WP6-derived figures (end-use, load shape, peak/CI, end-use x hour)

You are a Sonnet employee on the 2J Applied Energy resubmission. Cluster-only for data reads (the
source CSVs live on Speed and some are hundreds of MB); plotting itself may run on the same cluster
job for simplicity. Read `CLAUDE.md` at the repo root first. Submit your job, write state to the IMPL
doc, **end your turn** -- do not wait or poll. Collection is the manager's job.

## 0. Why this task exists

Plan §4's WP11 lists nine figures. Four of them (2, 3, 4, 5 in the plan's own numbering) are built
entirely from WP6's already-ACCEPTED output (T68 = main 2022-to-2030 rebuild, T69 = the three
work-from-home/population-mix scenario arms) -- no new computation, no open data-provenance question,
fully controls-verified data. Build those four now. The other five figures (1, 6, 7, 8, 9) are
deliberately OUT OF SCOPE for this task: Figure 6 needs a manager rescoping decision first (the
WP3 static-schedule comparison was ruled "not home-for-home" and cannot be used; only the
average-profile comparison, T30, might still qualify, and T30's own scoring is not yet accepted),
Figure 7 needs T70 (WP5 redo) to land first, and Figures 1/8/9's exact source files have not yet been
confirmed by directory listing -- do not guess at them, they are a separate task.

## 1. Inputs -- read-only, never edit any of these

- `T68/out/enduse_annual.csv`, `T68/out/enduse_hourly_profile.csv`, `T68/out/grid_metrics.csv`,
  `T68/out/enduse_change_2022_2030.csv` -- the ACCEPTED main-rebuild (S-Full) WP6 output. Read
  `impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md`'s Manager collection section first for the
  divisor rules and the quotable/NOT_EVALUABLE convention before touching any number.
- `T69/out/S-None/`, `T69/out/S-Partial/`, `T69/out/S-Revert-std/` -- each with the same file set
  (`enduse_annual.csv`, `enduse_hourly_profile.csv`, `grid_metrics.csv`, `enduse_change_2022_2030.csv`).
  ACCEPTED, see `impl/2026-09-21_T69_wp6_partB_scenarios_IMPL.md`'s Manager collection section.
- `T69/out/cross_scenario_common_basis.csv` -- the household-count table for any cross-scenario
  figure; print the exact count used, per Ruling 1's household-basis discipline (do not renegotiate
  this rule, it is fixed).

**Concatenation is APPROVED** (T69 IMPL doc, Manager collection, item 4): treat T68's own file as
`scenario = S-Full` and `pd.concat` all four `enduse_change_2022_2030.csv` files directly when a
figure needs all four scenarios together. Confirm the column headers actually match before
concatenating (they were confirmed identical at collection, but confirm again yourself -- do not
take that on faith).

## 2. The four figures

1. **Annual energy by end use** (plan's figure 2). Bar or stacked-bar, 2022 vs 2030, per end use
   (Electricity:Facility, lights, equip, fan, heating_ET, cooling_ET, water_ET, hvac_dhw_elec),
   stock-weighted across all 24 cells, S-Full only (this is the main-rebuild headline figure, not a
   scenario comparison). Source: `T68/out/enduse_annual.csv`, stock-weighted using the same
   `STOCK_WEIGHTS`-style weighting T68's own script already used internally (read
   `T68_scripts/enduse_hour_corrected.py` for the exact weighting logic and reuse it -- do not
   invent a different weighting scheme). Respect the divisor rule: only equip/lights get a
   per-dwelling report; everything else reports whole-building or percent-change only, per T68's own
   `NOT_EVALUABLE` convention -- if a bar would require a per-dwelling number for fan/heating/cooling/
   water/hvac_dhw, use a relative (percent-change or share-of-total) framing instead, never a guessed
   divisor.
2. **Intraday load shape by scenario** (plan's figure 3). Hourly stock-weighted load curve
   (kWh or normalized share), one line per scenario (S-Full, S-None, S-Partial, S-Revert-std), for a
   representative day type (pick weekday, state which day type explicitly). Source:
   `enduse_hourly_profile.csv` per arm -- these files are large (T69's S-None alone is ~4M rows), so
   aggregate (groupby hour, stock-weighted mean) rather than loading all four in memory as raw frames
   at once if that risks the job's 32 GB budget; process one arm at a time and discard before loading
   the next. Restrict to the households common to all four arms (`cross_scenario_common_basis.csv`'s
   four-way row, n=1,198) per Ruling 1 -- print this count on the figure or in its caption data.
3. **Peak demand, load factor, ramp, with CIs** (plan's figure 4). One panel or small-multiple per
   metric, 2022 vs 2030 (S-Full) with the already-computed percent-change CI from
   `enduse_change_2022_2030.csv`'s `ci_low_pct`/`ci_high_pct` columns (method:
   `stock_weighted_cluster_bootstrap`, ACCEPTED and read line-by-line at T68). Use the `excludes_zero`/
   `change_quotable` columns as-is: a NOT_EVALUABLE row must be drawn distinctly (e.g. greyed out or
   flagged) from a QUOTABLE one, never presented the same way. Do not recompute any CI -- read it from
   the file.
4. **End use x hour difference (WP6)** (plan's figure 5) -- the figure the first reviewer asked for
   directly. Heatmap or small-multiple of (end use x hour-of-day) percent change 2022-to-2030, S-Full,
   stock-weighted. Source: same `enduse_hourly_profile.csv` T68 produced, aggregated by end use and
   hour. This is the figure most likely to be the paper's new headline result -- get the axis labels,
   units and the QUOTABLE/NOT_EVALUABLE distinction exactly right.

## 3. Rulings

1. **Only figures that carry a claim** (standing author preference, plan §4 WP11). Do not add panels,
   sub-figures or metrics beyond what's listed above.
2. **≥600 dpi at print width** (carried item, plan §4 WP11 -- 13 of 16 original figures were below
   this). Confirm the saved PNG/PDF's actual dpi and width in inches in your IMPL doc, do not just
   assert the matplotlib `dpi=` kwarg was set.
3. **No result number appears on a figure that isn't traceable to a specific CSV cell.** If you round
   or compute anything for display (e.g. a stock-weighted mean), say in the IMPL doc exactly which
   columns and weighting produced it.
4. **A NOT_EVALUABLE or non-quotable value is never silently dropped or silently plotted as if it were
   solid** -- grey it out, hatch it, or omit it with a stated reason, but do not let a reader mistake
   it for a normal data point.

## 4. Seen-working control (required before any figure is trusted)

For at least one end use, one hour, and one scenario, hand-verify the exact number your plotting code
reads out of `enduse_hourly_profile.csv`/`enduse_change_2022_2030.csv` against a fresh direct read of
that same cell from the CSV (e.g. `pandas.read_csv` + a direct row/column lookup, done separately from
your aggregation/plotting code path). Report the match (or mismatch) explicitly in the IMPL doc. This
is not optional -- it is the same discipline every prior WP6 task has applied to its own numbers.

## 5. Deliverables

Under `T71/out/figures/`: one PNG (or PDF, your choice, but state which and why) per figure, named
`fig02_annual_by_enduse`, `fig03_intraday_load_shape`, `fig04_peak_loadfactor_ramp_ci`,
`fig05_enduse_hour_diff`. Alongside each PNG, a same-named `.csv` with the exact numbers plotted (so
the manager and later WP10 rewrite can quote a number without re-reading the figure). `run_meta.json`
recording dpi/size per figure, the household count used for figure 2 (comparison basis), and the
seen-working control's result. `T71/logs/t71_run.out`.

Job: `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00` via `--wrap`, same interpreter as T68/T69
(`/speed-scratch/o_iseri/envs/step4/bin/python`, confirm `matplotlib` is importable there before
submitting -- a quick `python -c "import matplotlib"` check is a single-file-scale operation, allowed
on the login node). scp the PNGs and CSVs back to `impl/T71_out/` so the manager and author can view
them without another cluster round-trip.

## 6. Implementation doc

Create `impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md` before submitting, same skeleton as
T68/T69's (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), and write the JobID the
moment `sbatch` returns. End your turn immediately after.
