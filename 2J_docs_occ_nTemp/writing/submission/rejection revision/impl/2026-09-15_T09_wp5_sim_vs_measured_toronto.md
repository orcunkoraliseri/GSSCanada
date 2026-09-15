# T09 — WP5 step 3: simulated Toronto 2022 vs measured IESO profiles — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP5 step 3–4, §10 Wave 2
Measured:   `2026-09-15_T02_wp5_ieso_measured_profiles.md`, outputs `T02_out/`
Status:     COLLECTED — job 1328279 COMPLETED exit 0:0, all checks pass, outputs at `impl/T09_out/`

## Task

**Why.** A reviewer asked for an independent check of the simulated hourly load shape against measured
Canadian residential electricity for 2022. T02 built measured Toronto (FSAs starting with `M`) and
Ontario residential profiles from IESO. Compute the **same metrics with the same code** on the
simulated Toronto 2022 runs and put them side by side. **Numbers only; no pass/fail bands, no
interpretation beyond stating mismatches.**

**All compute on Speed via `sbatch`** (`-p ps -c 8 --mem=32G -t 7-00:00:00`), python
`/speed-scratch/o_iseri/envs/step4/bin/python`, work dir `/speed-scratch/o_iseri/2J_revision/T09/`.
Login node: only `sbatch squeue sacct scancel scontrol cd ls scp` and single-file `tail head grep wc -l cat`.
**Never `find`, `du`, or python on the login node.** tcsh: no `2>&1` or `2>/dev/null` in ssh strings;
`ssh -o BatchMode=yes -o ConnectTimeout=60`, retry once.

**Simulated input — already on Speed, do not re-upload.** T06 extracted all 2022 `hourly_meters.csv`
plus manifests to `/speed-scratch/o_iseri/2J_revision/T06/input/<Arch>__<City>/` (see T06 doc Ledger;
confirm with `ls` on the four `*__Toronto_5A` dirs). Read only; write nothing under `T06/`.

**Steps.**
1. **Run selection.** Pick the canonical 2022 run per sample exactly as `Step8_docs/08_simulation_plots.py:154-234`
   does (merge both manifests, `new_2022_2030` wins). Copy that logic into your script with a line
   citation. Report n runs per Toronto archetype (expect 50).
2. **Units and clock.** Meters are joules per hour; convert to kWh. `hour` 0..8759. Establish, from
   the local `SingleD__Toronto_5A/sample_*/Scenario_2022.idf` `RunPeriod` object (grep, locally), the
   start day of week and whether holidays/DST are applied. Map row `hour` → calendar date 2022 and
   IESO `HOUR` (hour ending 1..24, EST, no DST). State the mapping in Decisions with evidence.
3. **Day types.** Use T02's calendar: weekday / weekend / holiday from T02's `HOLIDAY_SET`
   (`T02_scripts/ieso_wp5_build_v2.py:82-110`). If EnergyPlus's own day of week differs from the real
   2022 calendar, also report the metrics using EnergyPlus's day of week (that is the day the occupancy
   schedule used), and say so.
4. **Series.** (a) `Electricity:Facility` (all electricity, includes electric heating/cooling/water
   heating). (b) `InteriorLights:Electricity + InteriorEquipment:Electricity + Fan Electricity Energy`
   (non-HVAC subset). Per archetype, average kWh per run per (date, hour). Toronto stock profile =
   archetype mix weighted with the paper's archetype weights (`08_simulation_plots.py:74-77`) — Toronto
   only, no six-city split. Also report each archetype alone.
5. **Metrics.** Import or copy `compute_slice_outputs` and `circular_mean_hour_idx` from
   `T02_scripts/ieso_wp5_build_v2.py:271-338` **unchanged** (cite lines) so simulated and measured use
   one definition. Feed simulated data in T02's per-(DATE, HOUR) shape with `kwh_per_premise` = kWh
   per dwelling. Periods and day types exactly as in `T02_out/ieso_metrics.csv` (full_year, winter,
   summer, shoulder, month_01..12; weekday, weekend, holiday).
6. **Outputs** in `T09_out/`:
   - `sim_toronto_2022_metrics.csv` — same columns as `ieso_metrics.csv` plus `series`, `archetype`, `calendar`.
   - `sim_vs_measured_toronto_2022.csv` — join on period × daytype for the weighted stock, series (a)
     and (b), measured Toronto 2022 and Ontario 2022; columns metric, sim, measured, sim_minus_measured.
     Shoulder months first in row order.
   - `sim_toronto_2022_profiles_long.csv` — normalized 24-h shares, same shape as `ieso_profiles_long.csv`.
   - slurm log. scp all back to `impl/T09_out/`.
7. **Mismatches to state (Verified, one line each, no judgement):** EPW weather year vs actual 2022
   weather; measured includes all residential premises (all heating fuels, all dwelling types) vs
   four archetypes; per-premise vs per-dwelling; holiday treatment; clock/DST.

**Employee rules.** One job. Write the script, `py -3 -m py_compile` it locally (compile only), scp it,
submit, write the JobID in Ledger, **end the turn** ("job N submitted, state written to <this doc>").
No waiting, no polling, no sleep. Never read multi-MB files into context. Past ~150k tokens → write
state, stop, "handoff needed". Write NOT FOUND rather than guess.

**Collector (a later, fresh agent).** `sacct` state/exit, scp outputs, check row counts against
`ieso_metrics.csv` slices, check measured columns in the join equal `ieso_metrics.csv` values exactly,
fill Verified (weekday shoulder and full-year numbers for the weighted stock, both series).

## Ledger
- 2026-09-15 (employee) · Confirmed read-only, non-recursive `ls` on Speed: all four
  `*__Toronto_5A` dirs exist under `/speed-scratch/o_iseri/2J_revision/T06/input/`
  (`HighRise__Toronto_5A`, `MidRise__Toronto_5A`, `OtherDwelling__Toronto_5A`,
  `SingleD__Toronto_5A`), each with exactly 50 `sample_*` dirs (`ls -d .../sample_* | wc -l`),
  and `.../SingleD__Toronto_5A/sample_001_HH33188/2022/` holds `hourly_meters.csv` directly (no
  `campaign_N50/` root) — matches T06's own v2 fix, confirmed independently here, T06 not
  touched. Also confirmed `/speed-scratch/o_iseri/2J_revision/T02/out/ieso_metrics.csv` exists
  on Speed (read-only source for the join, T02 not touched).
- 2026-09-15 (employee) · One `ssh` command accidentally included `2>&1` inside the command
  string (against the tcsh hard rule) while probing a `2022/` subdir; tcsh printed `1: File
  exists` and aborted that one probe (no output). Checked immediately: `~/1` on Speed is a
  0-byte file already dated **Apr 16** (pre-existing, not created by this command — tcsh's
  `2>&1` parses as `> 1` and refused to clobber it). No side effect; the probe was re-run
  without `2>&1` and succeeded. Not repeated after this.
- Script written: `T09_scripts/sim_vs_measured_toronto_2022.py` (local, this repo's `impl/`).
  `py -3 -m py_compile` — OK. Smoke-tested locally against real (small) data: pointed
  `INPUT_ROOT` at the local `BEM_Setup/SimResults_Step8/campaign_N50` tree (monkeypatch, no
  cluster involved) — `discover_toronto_2022_runs` found exactly 50/50/50/50 runs per Toronto
  archetype; built the full 8-760-row calendar frame (216 holiday rows = 9 holidays × 24h, as
  expected); ran `compute_slice_outputs` on 2 real `SingleD` households' shoulder-weekday slice
  (`n_days=82`, matching T02's own Toronto/Ontario shoulder-weekday `n_days=82` for 2022 exactly
  — a real cross-check, not assumed) and on a 1-run-per-archetype stock-weighted slice (weights
  summed to exactly 1.0, `n_days=82` again); confirmed `share` sums to 1.0 per 24h profile; read
  the real `T02_out/ieso_metrics.csv` locally and confirmed `year` filters correctly as strings
  (`'2022'`) even though the column also holds the non-numeric `'2019_to_2022_delta'` label, and
  the Toronto/shoulder/weekday measured row is found by the same filter the job script uses.
- Uploaded via `scp -r` (local `T09_upload/T09/` → `/speed-scratch/o_iseri/2J_revision/`, chosen
  over a login-node `mkdir`, which is not on the allowed-command list): remote
  `T09/T09_scripts/sim_vs_measured_toronto_2022.py` is 22,503 bytes, matching the local file
  exactly (`ls -la` both sides).
- **Job 1328279** submitted: `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00
  --job-name=T09_sim_vs_measured --chdir=/speed-scratch/o_iseri/2J_revision/T09
  --output=/speed-scratch/o_iseri/2J_revision/T09/T09_%j.out
  --wrap="/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T09/T09_scripts/sim_vs_measured_toronto_2022.py"`. `sacct -j
  1328279 -X` confirmed the job exists, state **PENDING** at submission. The job's own
  `os.makedirs(OUT_DIR, exist_ok=True)` creates `/speed-scratch/o_iseri/2J_revision/T09/out/` on
  the compute node — no login-node `mkdir` used anywhere for this task. Outputs expected:
  `T09/out/sim_toronto_2022_metrics.csv`, `sim_toronto_2022_profiles_long.csv`,
  `sim_vs_measured_toronto_2022.csv`, `run_meta.json`, plus `T09/T09_1328279.out`. **Not yet
  collected — a fresh agent must read these** (`sacct -j 1328279` first for state/exit code).
- 2026-09-15 (collector) · **Job 1328279 → COMPLETED, exit 0:0, elapsed 00:00:50, 8 CPUs, MaxRSS
  580,352K** (`sacct -j 1328279 --format=JobID,State,Elapsed,ExitCode,MaxRSS,NCPUS`). `ls -la` on
  `T09/out/`: `run_meta.json` (487 B), `sim_toronto_2022_metrics.csv` (152,153 B),
  `sim_toronto_2022_profiles_long.csv` (2,255,680 B), `sim_vs_measured_toronto_2022.csv`
  (110,331 B) — all 4 expected outputs present. `T09_1328279.out` (747 B) grepped for
  error/warn/invalid/not found/skip: only match is the script's own log line `[T09] loaded 200
  runs ok, 0 skipped` (the string "skip" from normal status text, not an actual skip). Full log
  read (small, <1 KB): `n runs per archetype: {'SingleD': 50, 'OtherDwelling': 50, 'MidRise': 50,
  'HighRise': 50}` (total 200, matches "expect 50" exactly), `loaded 200 runs ok, 0 skipped`,
  entities `SingleD/OtherDwelling/MidRise/HighRise/StockWeighted` each logged done, ends `[T09]
  done in 38.5s`. `run_meta.json` confirms the same: `n_runs_loaded_ok: 200, n_runs_skipped: 0,
  skipped: []`. scp'd all 4 outputs + the slurm log to `impl/T09_out/`; local `ls -la` byte sizes
  match the Speed sizes exactly for every file.

## Verified
- **Run selection (task step 1):** `discover_toronto_2022_runs` in the submitted script is the
  `08_simulation_plots.py:154-234` (`load_cell_manifest` + `discover_runs`) "new_2022_2030 wins"
  gate, restricted to `Toronto_5A` and year fixed to `2022` — same pattern T06 already uses
  read-only (`T06_scripts/enduse_hour_2022_v2.py:175-210`, not edited here). Smoke-tested locally
  (see Ledger): 50/50/50/50 runs per archetype, matching the task's "expect 50".
- **Units/clock (task step 2), from `Scenario_2022.idf` `RunPeriod`** (grepped locally,
  `BEM_Setup/SimResults_Step8/campaign_N50/SingleD__Toronto_5A/sample_001_HH33188/2022/
  Scenario_2022.idf:115-129`): `Day of Week for Start Day = Sunday`, `Use Weather File Holidays
  and Special Days = Yes`, `Use Weather File Daylight Saving Period = Yes`. Real 2022-01-01 =
  **Saturday** (`python -c "datetime.date(2022,1,1).strftime('%A')"`, checked locally) — the
  simulated calendar's fixed Sunday start does NOT match the real 2022 weekday sequence.
  `hourly_meters.csv` confirmed joules-per-hour, `hour` 0..8759, by direct local header/row read
  on the same sample (matches T06's independently-verified header).
- **Day types (task step 3):** two calendars built and reported separately —
  `real2022` (T02's own weekday/weekend/holiday rule, same `HOLIDAY_SET`) and `eplus`
  (`08_simulation_plots.py:128-131` `is_weekend()`, ported verbatim as `is_weekend_eplus`).
  Local smoke test: `real2022` weekend rows = 2,472 (24h × 103 real-calendar weekend days,
  2022's 104 Sat/Sun days minus one that lands on a holiday), `eplus` weekend rows = 2,448 (24h ×
  102 days) — the two calendars genuinely disagree on ~1 day of week-type, as the IDF mismatch
  above implies.

- **2026-09-15 (collector) — row-count and exact-match checks, `py -3` locally, small outputs
  only, no multi-MB file printed:**
  - `sim_toronto_2022_metrics.csv`: 880 rows = 5 entities (4 archetypes + `StockWeighted`) × 2
    series × 2 calendars × 44 period×daytype combos — matches `ieso_metrics.csv`'s own 44
    period×daytype rows per scope for `year=2022` exactly (`Toronto` 44 rows, `Ontario` 44 rows in
    `ieso_metrics.csv`).
  - `sim_toronto_2022_profiles_long.csv`: 21,120 rows = 880 profile-groups × 24 hours, exact.
  - `sim_vs_measured_toronto_2022.csv`: 1,056 rows = 44 period×daytype × 2 series × 2
    measured_scope × 6 metrics, exact.
  - **Exact-match check (join's `measured` column vs `ieso_metrics.csv`, all 1,056 rows,
    `year=2022`):** merged on (measured_scope↔scope, period, daytype), 1,056/1,056 rows found a
    match, 0 NaN. **Max abs difference = 3.55e-15** (float round-trip through CSV write/read, not
    a real discrepancy) — the join's measured column equals `ieso_metrics.csv` exactly.
  - **Shoulder-months-first:** confirmed — `join.csv` row order is
    `shoulder, winter, summer, full_year, month_01..12` (shoulder literally first), matching the
    task's "shoulder months first in row order" instruction and the Decisions entry below.
  - **Normalized 24-h shares sum to 1 per profile:** 880 profile groups checked (grouped by
    scope/year/period/daytype/series/archetype/calendar); sums range 0.9999999999999984 –
    0.9999999999999993 (float rounding only); 0 groups differ from 1.0 by more than 1e-6; 0 NaN
    shares anywhere in the file.
  - **n_days cross-check:** `StockWeighted`/`real2022`/shoulder/weekday `n_days = 82` for both
    series in `sim_toronto_2022_metrics.csv`, matching `ieso_metrics.csv`'s own Toronto and
    Ontario shoulder-weekday `n_days = 82` for 2022 exactly (same calendar, same slice, real
    number not just the employee's earlier 1-2-household smoke test).
  - **`mean_premises = 24.0`** for the `StockWeighted` entity (both series, shoulder/weekday) —
    consistent with the Decisions-section explanation already on record (weights sum to ~1.0 per
    hour, summed over 24 h/day before the per-date mean), not a new problem.

- **2026-09-15 (collector) — Verified numbers for the weighted Toronto stock (`StockWeighted`,
  `calendar=real2022`), weekday, from `sim_vs_measured_toronto_2022.csv` (sim / measured /
  sim_minus_measured):**

  **Series (a) all electricity (`facility` = `Electricity:Facility`, includes electric
  heating/cooling/water heating):**
  | period | metric | vs | sim | measured | diff |
  |---|---|---|---|---|---|
  | shoulder | mean kWh/premise | Toronto | 12.909 | 0.696 | +12.213 |
  | shoulder | mean kWh/premise | Ontario | 12.909 | 0.838 | +12.071 |
  | shoulder | load factor | Toronto | 0.5018 | 0.4305 | +0.0714 |
  | shoulder | load factor | Ontario | 0.5018 | 0.4545 | +0.0473 |
  | shoulder | peak-to-avg | Toronto | 1.993 | 2.323 | -0.330 |
  | shoulder | peak-to-avg | Ontario | 1.993 | 2.200 | -0.207 |
  | shoulder | midday share | Toronto | 0.3509 | 0.3513 | -0.0004 |
  | shoulder | midday share | Ontario | 0.3509 | 0.3498 | +0.0011 |
  | shoulder | mean peak hour | Toronto | 17.546 | 18.690 | -1.144 |
  | shoulder | mean peak hour | Ontario | 17.546 | 18.424 | -0.878 |
  | full_year | mean kWh/premise | Toronto | 13.431 | 0.822 | +12.609 |
  | full_year | mean kWh/premise | Ontario | 13.431 | 0.992 | +12.439 |
  | full_year | load factor | Toronto | 0.4445 | 0.4399 | +0.0046 |
  | full_year | load factor | Ontario | 0.4445 | 0.4660 | -0.0216 |
  | full_year | peak-to-avg | Toronto | 2.250 | 2.273 | -0.024 |
  | full_year | peak-to-avg | Ontario | 2.250 | 2.146 | +0.104 |
  | full_year | midday share | Toronto | 0.3354 | 0.3524 | -0.0170 |
  | full_year | midday share | Ontario | 0.3354 | 0.3518 | -0.0164 |
  | full_year | mean peak hour | Toronto | 18.007 | 18.254 | -0.247 |
  | full_year | mean peak hour | Ontario | 18.007 | 17.910 | +0.097 |

  **Series (b) lights + equipment + fans (`nonhvac`, non-HVAC subset):**
  | period | metric | vs | sim | measured | diff |
  |---|---|---|---|---|---|
  | shoulder | mean kWh/premise | Toronto | 6.315 | 0.696 | +5.619 |
  | shoulder | mean kWh/premise | Ontario | 6.315 | 0.838 | +5.476 |
  | shoulder | load factor | Toronto | 0.5793 | 0.4305 | +0.1489 |
  | shoulder | load factor | Ontario | 0.5793 | 0.4545 | +0.1248 |
  | shoulder | peak-to-avg | Toronto | 1.726 | 2.323 | -0.597 |
  | shoulder | peak-to-avg | Ontario | 1.726 | 2.200 | -0.474 |
  | shoulder | midday share | Toronto | 0.3637 | 0.3513 | +0.0125 |
  | shoulder | midday share | Ontario | 0.3637 | 0.3498 | +0.0140 |
  | shoulder | mean peak hour | Toronto | 17.594 | 18.690 | -1.095 |
  | shoulder | mean peak hour | Ontario | 17.594 | 18.424 | -0.830 |
  | full_year | mean kWh/premise | Toronto | 6.312 | 0.822 | +5.491 |
  | full_year | mean kWh/premise | Ontario | 6.312 | 0.992 | +5.320 |
  | full_year | load factor | Toronto | 0.5791 | 0.4399 | +0.1393 |
  | full_year | load factor | Ontario | 0.5791 | 0.4660 | +0.1131 |
  | full_year | peak-to-avg | Toronto | 1.727 | 2.273 | -0.547 |
  | full_year | peak-to-avg | Ontario | 1.727 | 2.146 | -0.419 |
  | full_year | midday share | Toronto | 0.3565 | 0.3524 | +0.0041 |
  | full_year | midday share | Ontario | 0.3565 | 0.3518 | +0.0047 |
  | full_year | mean peak hour | Toronto | 17.394 | 18.254 | -0.860 |
  | full_year | mean peak hour | Ontario | 17.394 | 17.910 | -0.516 |

  (`max_kwh_per_premise` excluded from this table — it is per-instance across 200 sim runs vs a
  scope-summed measured value, not comparable at face value; full numbers are in
  `sim_vs_measured_toronto_2022.csv`. Note, not a check failure: sim `max_kwh_per_premise` is
  identical between `shoulder` and `full_year` for both series — 30.217 for series (a), 10.900 for
  series (b) — meaning the single largest hourly instance in the whole weekday full-year table
  falls inside a shoulder month; stated as observed, not interpreted.)

- **Clock/calendar mapping used (task step 2), one line each, no judgement:**
  - EnergyPlus `RunPeriod` (`Scenario_2022.idf:115-129`, grepped locally): `Day of Week for Start
    Day = Sunday`; real 2022-01-01 is a **Saturday** — E+'s simulated day-of-week sequence does
    **not** match the real 2022 civil calendar (confirmed by the employee, re-confirmed here from
    the same script/doc, not independently re-derived this turn).
  - Row `hour` (0..8759) → `day_idx = hour // 24`, `hour_of_day = hour % 24`; calendar date =
    2022-01-01 + `day_idx` days (real 2022 dates used as a pure day-of-year offset, independent of
    which weekday E+ itself assigns to day 1); IESO `HOUR` (hour-ending, 1-24) = `hour_of_day + 1`.
  - Two day-type calendars are both present in the outputs (`calendar` column: `real2022` vs
    `eplus`) — the `real2022`/weekday rows above are the ones joined against measured data
    (matches T02's own calendar); the `eplus` calendar (E+'s own Sunday-start weekday sequence,
    the calendar the occupancy schedule itself ran against) exists in `sim_toronto_2022_metrics.csv`
    and `..._profiles_long.csv` but was **not** pulled into the Verified table above — task step 3
    only requires reporting it "also", not joining it against measured data.

- **Mismatches (task step 7, one line each, no judgement):**
  - EPW weather year used for the simulation vs the actual 2022 weather that produced the measured
    IESO consumption — not verified which weather year the EPW file represents; NOT FOUND in this
    task (out of scope for the collector; would need the EPW file's own header).
  - Measured IESO data covers all residential premises in scope (all heating fuels, all dwelling
    types); simulated data covers exactly 4 Toronto archetypes (SingleD, OtherDwelling, MidRise,
    HighRise), 50 runs each.
  - Measured `kwh_per_premise` = total consumption / total premise count (scope-summed, all
    premises pooled); simulated `kwh_per_premise` = per-dwelling kWh from `compute_slice_outputs`
    fed a stock-weighted average across archetypes, i.e. a modelled per-dwelling value, not a
    census of real premises.
  - Holiday treatment: both sides use the same fixed `HOLIDAY_SET` (T02's 2022 statutory-holiday
    dates, ported verbatim); simulated data additionally has an `eplus`-calendar column where
    weekday/weekend (not holiday membership) follows E+'s own Sunday-start day sequence instead of
    the real calendar.
  - Clock/DST: IESO `HOUR` is fixed EST, no DST, all year; the simulated `RunPeriod` has `Use
    Weather File Daylight Saving Period = Yes`, so E+'s own hour labelling may follow the EPW's DST
    period — no DST shift was applied when building the simulated `HOUR` column (`hour_of_day + 1`
    used as-is for every day of the year).

## Decisions
- **Holiday membership is anchored to the real calendar date in BOTH the `real2022` and `eplus`
  day-type columns** — only the weekday/weekend split changes between the two calendars. Not
  specified explicitly by the task doc; reasoned because a statutory holiday is the same calendar
  date regardless of which weekday-numbering convention labels the surrounding days.
- **Stock-weighted series**: each archetype's per-run rows get weight
  `STOCK_WEIGHTS[arch] / n_runs_of_arch` applied to both `TOTAL_CONSUMPTION` and `PREMISE_COUNT`
  fed into the unmodified `compute_slice_outputs`, so weights sum to 1.0 and the result is a
  stock-weighted per-dwelling average without touching the shared metric function. Consequence:
  the `mean_premises` column for the `StockWeighted` archetype is a **weight sum (~1.0), not a
  real premise count** — left as-is, flagged here rather than renamed/dropped.
- **`sim_vs_measured_toronto_2022.csv` join**: built only from the `StockWeighted` archetype,
  `calendar="real2022"` (the calendar T02 also used, so period×daytype slices line up exactly);
  columns `period, daytype, series, measured_scope, metric, sim, measured, sim_minus_measured`,
  one row per (period, daytype, series, measured_scope∈{Toronto,Ontario}, metric). Only the 6
  substantive metrics are compared (`mean_kwh_per_premise, max_kwh_per_premise, load_factor,
  peak_to_avg, midday_share, mean_peak_hour`) — `n_days`/`mean_premises` excluded, since
  `mean_premises` means different things on each side (see decision above). Row order: period
  sorted `shoulder, winter, summer, full_year, month_01..12` (shoulder first, per task), then
  daytype `weekday, weekend, holiday`.
- **`sim_toronto_2022_profiles_long.csv` carries `series`, `archetype`, `calendar` columns too**,
  even though the task text only stated that add-on explicitly for the metrics CSV — needed
  because without them, rows for different series/archetype/calendar combinations would collide
  on the same `(scope,year,period,daytype,hour_ending)` key.
- **Directory creation on Speed used `scp -r` of a local folder, not a login-node `mkdir`**
  (`mkdir` is not on the allowed login-node command list). `T09/out/` itself is created by the
  job's own `os.makedirs(..., exist_ok=True)` on the compute node.

## Next
**Manager note, 2026-09-15 — the `StockWeighted` comparison is NOT usable as is; follow-up T15.**
1. **Scale mixing.** Sim "per-dwelling" mean is 13.4 kWh/h vs 0.8 measured. T06 shows annual Facility
   of 391,128 (HighRise), 268,723 (MidRise), 46,002 (OtherDwelling), 7,941 (SingleD) kWh: the multi-unit
   archetypes are whole buildings. Weighting building totals lets HighRise/MidRise set the stock shape,
   so stock load factor, peak-to-average and peak hour are not a stock shape. Per-archetype shape metrics
   are scale-free and remain valid.
2. **Wrong day-type calendar for the join.** E+ day 1 is Sunday, real 2022-01-01 is Saturday, so the
   schedules ran one weekday later than the real date. On the `real2022` calendar every real Friday is a
   simulated Saturday (weekend schedule) and every real Sunday a simulated Monday, so about one fifth of
   "weekday" days carry weekend occupancy. The join must use the `eplus` day type (weather by date stays).
3. **Clock.** `Use Weather File Daylight Saving Period = Yes` shifts schedules one hour during DST while
   IESO is EST all year; the −1.1 h shoulder peak-hour offset is the size of that shift. Not resolved.
The Verified tables above stay as the record of job 1328279; do not quote them.

Superseded: All Collector checks in the task doc are done and passed (row counts, exact-match, shoulder-first
order, share sums, Verified table, mismatches list). No manuscript or plan edits made, per the
Collector's own instructions. Next owner: manager decides whether/how these sim-vs-measured
Toronto numbers go into the WP5 write-up (same open question T02 left for the shoulder-weekday
Ontario/Toronto numbers).

## WHAT I DID NOT VERIFY
- Whether the job actually completes, how long it takes, exit code, or any real output numbers —
  nothing was collected; submit-and-end-turn rule (0 households/runs were processed end-to-end at
  the full 50×4 scale, only 1-2 per archetype locally).
- Task step 7's "Mismatches to state" list (EPW weather year, premise/dwelling-type coverage,
  per-premise vs per-dwelling, holiday treatment, clock/DST) is described in this doc's header
  comments and Verified/Decisions above but not yet written as the task's own explicit one-line-
  each Verified block — left for the collector.
- Whether `Use Weather File Holidays and Special Days = Yes` in the IDF actually changes anything
  E+ itself treats as a holiday internally (distinct from the HOLIDAY_SET this script applies) —
  not traced into any E+ output; this script does not read E+'s own holiday/DST markers at all,
  it only applies the fixed HOLIDAY_SET and the two weekday conventions described above.
- Whether every one of the 200 discovered runs actually has 8,760 well-formed rows and all 4
  required meter columns — the script checks and records `skipped` in `run_meta.json`; **now
  read: `n_runs_skipped: 0`, `skipped: []`**, so all 200 passed the script's own length/column
  checks, but this collector did not independently re-open any raw `hourly_meters.csv` to confirm.
- 2026-09-15 (collector) — not verified this turn:
  - Which EPW weather file / weather year underlies the Toronto_5A 2022 simulations, and whether it
    is TMY or an actual-2022 weather file — NOT FOUND, would need the IDF's `Site:Location`/EPW
    filename, not opened here.
  - Whether `Use Weather File Holidays and Special Days = Yes` in the IDF changes anything inside
    E+'s own internal holiday/DST handling, distinct from this script's own fixed `HOLIDAY_SET` —
    carried over unresolved from the employee's own note, not traced further here.
  - The `eplus`-calendar rows in `sim_toronto_2022_metrics.csv` / `..._profiles_long.csv` (weekday
    numbers under E+'s own Sunday-start day sequence) were not pulled into a Verified table or
    compared against measured data — only their presence and row counts were confirmed; the task's
    step 3 "also report" instruction is satisfied by the file existing, not by a written-out number
    here.
  - Only `weekday` shoulder/full_year rows were tabulated in Verified above; `weekend` and
    `holiday` daytype rows exist in both `sim_vs_measured_toronto_2022.csv` (all 1,056 rows
    present and exact-match-checked) and the metrics/profiles files, but were not individually
    read out.
  - Per-archetype (non-stock-weighted) numbers were not tabulated — only the `StockWeighted`
    entity was pulled into Verified, per the task's own instruction ("weighted Toronto stock").
  - Did not re-derive `STOCK_WEIGHTS` or `HOLIDAYS_2022` against `08_simulation_plots.py` /
    `ieso_wp5_build_v2.py` a second time this turn — relied on the employee's own verbatim-copy
    citations already in this doc's header comments and Verified section.
