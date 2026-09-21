# T70 -- WP5: redo the measured-vs-simulated 2022 profile comparison on the REBUILT runs

You are a Sonnet employee on the 2J Applied Energy resubmission. Cluster-only. Read `CLAUDE.md` at
the repo root first (top rule: `sbatch` only, never a blocking `srun` or bare python on the login
node). Submit your job, write state to the IMPL doc, **end your turn** -- do not wait or poll.
Collection is the manager's job.

## 0. Why this task exists

This is the second reviewer's MAIN point (checklist group D). T02/T09/T15 (mid-September) already
built and validated a measured-vs-simulated comparison method, but it ran on the OLD, since-retired
2022 simulation output. The 2022 rebuild (T21, using only 2022-year diaries) makes every one of
those numbers stale. Checklist item D3 ("Redo the comparison on the rebuilt runs") has been sitting
at "Later" since it was written and has never been dispatched -- do it now. This produces the data
for WP11 Figure 7 ("measured vs simulated 2022 profile").

## 1. Inputs -- read-only, never edit any of these

- `T02_out/ieso_metrics.csv` -- the measured IESO Ontario/Toronto 2022 (and 2019/2021/2023) hourly
  metrics. **Already trusted and validated (T02/T15's collection). Never re-derive it, never
  recompute a measured number -- read it as-is.**
- `T15_scripts/t15_sim_vs_measured.py` -- the exact validated comparison method: scale-free stock
  shape (each run normalized by its own annual mean before aggregation), the `eplus`-calendar day
  type fix (RunPeriod starts on a Sunday, weekday/weekend defined off that, not the real 2022
  calendar), and the four dwelling-unit counts derived from IDF zone geometry
  (`DWELLING_COUNT = {"SingleD": 1, "OtherDwelling": 7, "MidRise": 31, "HighRise": 79}`, Toronto
  only, evidence in `impl/2026-09-15_T15_wp5_sim_vs_measured_fix.md`'s Decisions section). Read that
  file's Ledger and Decisions in full before writing any code -- it explains every design choice you
  are reusing.
- `T21/out/step8/<archetype>__Toronto_5A/sample_NNN_HHxxxxx/2022/hourly_meters.csv` -- the REBUILT
  2022 Toronto runs (the new input tree). **This replaces T15's old input directory entirely.**
  Confirm by directory listing before writing code: how many runs exist per archetype in
  `SingleD__Toronto_5A`, `OtherDwelling__Toronto_5A`, `MidRise__Toronto_5A`, `HighRise__Toronto_5A`
  (T15 expected 50 per archetype, 200 total -- verify the rebuilt tree matches, do not assume).
- `T66/scripts/step9_validate_full_corrected.py` -- read-only, for column-name confirmation only if
  `hourly_meters.csv`'s header differs from what T15's script expects (it should not: T68/T69 already
  read this exact same tree format successfully).

**Do not use** any number already written into `impl/2026-09-15_T09_wp5_sim_vs_measured_toronto.md`
or `impl/2026-09-15_T15_wp5_sim_vs_measured_fix.md`'s **Verified** sections as a validation target --
those numbers came from the OLD retired runs and are exactly what this task supersedes. You MAY reuse
those files' **method** (script, dwelling counts, calendar logic) verbatim; you may NOT reuse their
**results**.

## 2. What changes vs. what stays identical to T15

**Copy (never edit) `T15_scripts/t15_sim_vs_measured.py` into a new `T70_scripts/` folder.** The
change is discovery only: `discover_toronto_2022_runs()` (or whatever T15 named its run-finder) must
be repointed from the old retired-output directory to `T21/out/step8/<archetype>__Toronto_5A/`. Every
other function -- `compute_slice_outputs`, `circular_mean_hour_idx`, `build_calendar_frame`,
`period_month_map`, `full_sub_table`, `STOCK_WEIGHTS`, `HOLIDAYS_2022`, `DWELLING_COUNT`, the
normalization step, the `eplus`/`real2022` two-calendar join loop -- stays byte-identical. If the
rebuilt tree's `hourly_meters.csv` has a different column layout than the old tree (check the header
before assuming), log the exact difference and adapt the read function minimally; do not change any
metric-computation logic to compensate.

**One new control, C5 (rebuild-vs-old sanity):** before trusting the real result, confirm the rebuilt
runs' raw (non-normalized) whole-building annual Facility kWh for each archetype is within a factor of
2 of T15's old per-archetype meter means (`run_meta.json`'s `annual_facility_kwh_meter_mean_per_archetype`
in the old T15 output) -- this is a sanity bound, not an exact-match test (the rebuild is expected to
shift these numbers, that is the whole point of the rebuild), just a guard against reading the wrong
tree or a badly broken meter column. Report both sides' numbers plainly; do not fail the job on this,
just flag if the ratio is outside 0.5-2.0 for any archetype.

## 3. Rulings

1. **Toronto only, as T15 was.** Do not extend to other cities -- WP5's whole scope, per the plan and
   the reviewer's own request, is a Toronto/Ontario comparison against IESO data.
2. **Dwelling counts are unchanged from T15.** The rebuild changes occupancy schedules (2022-diaries
   only), not building geometry/IDF zone structure -- so `DWELLING_COUNT` does not need re-deriving.
   State this reasoning explicitly in your IMPL doc rather than silently assuming it.
3. **Report both the `eplus` and `real2022` calendar joins**, exactly as T15's script already does --
   do not drop the `real2022` block, it is still useful as a sensitivity check.
4. **No manuscript language, no pass/fail verdict, no interpretation.** Numbers only, same discipline
   as T15's own task text ("Numbers only; no pass/fail, no interpretation"). The manager decides at
   collection what the comparison means for the paper.

## 4. Deliverables

Under `T70/out/`: `sim_toronto_2022_shape_metrics_rebuilt.csv` (per archetype and stock, both
calendars, both series), `sim_vs_measured_toronto_2022_shape_rebuilt.csv` (stock only, joined against
`T02_out/ieso_metrics.csv`, columns matching T15's file exactly plus a `data_vintage=rebuilt_2022`
column so it is never confused with T15's old file if both are ever read side by side),
`run_meta.json` (must include `n_runs_loaded_ok`/`skipped` per archetype, the dwelling-count
evidence/reasoning per Ruling 2, and the C5 sanity-bound numbers), slurm log at `T70/logs/t70_run.out`.

Job: reuse T15's resource shape (`-p ps -c 8 --mem=32G -t 7-00:00:00`) via `sbatch --wrap`. T15's real
run took 25 seconds; this should be similarly fast (200 households, same tree size).

## 5. Implementation doc

Create `impl/2026-09-21_T70_wp5_measured_vs_rebuilt_IMPL.md` before submitting, same skeleton as
T68/T69's (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), and write the JobID the
moment `sbatch` returns. End your turn immediately after. Do not read any output file after
submission -- that is the manager's job: `run_meta.json` first, then results, same fixed order as
every prior task.
