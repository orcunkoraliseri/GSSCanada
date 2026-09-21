# T76 — plot WP11 Figure 1 (at-home fraction by hour, across years/scenarios)

Task doc:   this file
Status:     IN PROGRESS — job `1341263` submitted, not yet collected (no-parking rule: this
            employee does not poll/wait; a fresh agent collects when `sacct` shows COMPLETED).

## Background

Plan entry (di) triaged the nine WP11 figures and left Figures 1, 8, 9 unscoped because their exact
source files had not been directory-confirmed. **Note: "Figure 1" in this task's name is WP11's own
figure numbering (an at-home-by-hour overview), NOT the manuscript's overall Figure 1, which is the
workflow diagram already generated and accepted (`Figure_01_workflow.png`, entry (bu)) — do not confuse
the two, and do not touch/overwrite the workflow diagram.**

The manager has confirmed on the cluster (login-node `find`/`head`/`ls -la` only, no computation run)
that these files exist and look like plausible sources, but has **not** fully worked out which years/
scenarios they cover or found the 2022 baseline — that is this task's first job:

- `/speed-scratch/o_iseri/2J_revision/T20/out/main/BEM_Setup/BEM_Schedules_2030.csv` and
  `/speed-scratch/o_iseri/2J_revision/T20/out/null/BEM_Setup/BEM_Schedules_2030.csv` — **each 667 MB**,
  per-household per-hour-per-daytype rows. Header confirmed by direct read:
  `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,
  Metabolic_Rate,Equipment_Fraction,Lighting_Fraction,Equip_Design_W,Light_Design_W`. `Occupancy_Schedule`
  is a per-hour at-home fraction — exactly the quantity this figure needs, IF this file is what it looks
  like. **What "main" vs "null" mean here is NOT yet confirmed by the manager** — read `T20/T20_scripts/`
  (or whatever script wrote this tree) and/or its own implementation doc under `impl/` to find out before
  assuming (a plausible guess is 2030-with-WFH-persisting vs. a null/no-change comparison arm, but this
  is a guess, not a finding — verify it).
- `/speed-scratch/o_iseri/2J_revision/T26/out/lambda_0.0/`, `lambda_0.5/`, `lambda_1.0/` — same
  `BEM_Setup/BEM_Schedules_2030.csv` structure, three WFH-persistence scenario arms (lambda is the
  persistence weight; 0.0/0.5/1.0 likely map to full-revert/half/full-persist — confirm against T26's own
  scripts or implementation doc rather than assuming from the number alone).
- **No 2022 baseline schedule file has been located yet.** T20/T26 both look 2030-only. The 2022
  at-home-by-hour baseline most likely lives under `T21/out/` (the main rebuild tree already used by
  T70/T71) or `T17/` (mentioned elsewhere in this project's history as a full-grid run) — but the manager
  looked in `T21/out/step8/`, `step9_activity/`, `step9_baseline/` and found only per-household PNG plots
  (`SimResults_Plotting_Schedules/`), not an aggregate per-hour CSV. **Finding (or building, if it
  genuinely does not exist as a saved aggregate) the 2022 at-home-by-hour baseline is this task's own
  responsibility — if after a real search none exists, report that plainly rather than guessing or
  silently dropping the 2022 line from the figure.**

## What to do

1. **Confirm what main/null (T20) and lambda_0.0/0.5/1.0 (T26) actually represent**, by reading their
   build scripts/implementation docs, not by guessing from names.
2. **Find the 2022 at-home-by-hour baseline.** Check `T21/`, `T17/`, and any other tree already used for
   the main 2022 rebuild (T70/T71's own inputs are a good starting point — they reused `T21/out/step8/...
   /2022/` per entry (dj)/(dk)). If no saved aggregate schedule exists for 2022, either compute the
   aggregate yourself from the same per-household run outputs T70/T71 already trust (state exactly which
   files, and get the aggregation logic reviewed against T70's own scale-free method for consistency), or
   report back to the manager that this figure cannot be built without a new task — do not silently
   substitute a different year or synthesize numbers.
3. **These CSVs are up to 667 MB — this is a real cluster compute task, not a login-node peek.** Do not
   load a full file in pandas without chunking/streaming consideration; aggregate `Occupancy_Schedule` by
   `Hour` and `Day_Type` (population mean, or stock-weighted mean if a weight column exists elsewhere —
   check whether these per-household rows already represent one real household each or need re-weighting,
   consistent with this project's "quotable core" divisor-invariance rule for what may carry a number).
4. **Design the figure to match this project's established style** (T71/T73 precedent: dpi=600, PNG, flag
   anything without a real interval or that mixes incompatible bases, state units — fraction 0-1 on the
   y-axis, hour 1-24 or 0-23 on the x-axis, one line per year/scenario: 2022, 2030-main, 2030-null (or
   whatever they turn out to represent), lambda 0.0/0.5/1.0).
5. **Controls required:**
   - **Seen-working control:** independently re-read a handful of raw rows directly from each source CSV
     (not through your aggregation code) for one (Hour, Day_Type) cell, hand-average them, and confirm the
     hand-average matches what the aggregation script produces for that same cell.
   - **Row-count/completeness control:** confirm the count of households/rows read from each input file
     matches that file's own expected row count (no silent truncation), and that every year/scenario line
     you intended to plot actually appears.
6. Save the PNG under `/speed-scratch/o_iseri/2J_revision/T76/out/figures/fig01_athome_by_hour.png`.
7. Write `T76/logs/t76_run_meta.json` (JobID, elapsed, figure metadata, controls, and what main/null/
   lambda were confirmed to mean, and where the 2022 baseline came from) following T71/T73's
   `run_meta.json` shape.
8. **Submit via `sbatch`, do not wait, do not poll.** Request enough memory for the 667 MB files (start at
   `--mem=16G`, project convention). Write the JobID into this file's Ledger section below, then end your
   turn. The manager collects when `sacct` shows COMPLETED and views the PNG via `scp` before accepting.

**If step 2 (finding the 2022 baseline) turns out to be a substantial new computation rather than a
quick file-location task, STOP after confirming that and report back — do not silently expand this task
into a large new simulation-adjacent job without the manager's sign-off. Write what you found in the
Ledger/Next sections and end your turn; a follow-up task will be scoped from there if needed.**

## Ledger

- **Reconnaissance (steps 1-2), all single-file login-node commands, no computation run:**
  - `head -1` on all six schedule CSVs — **identical 17-column header** on every one:
    `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,
    Occupancy_Schedule,Metabolic_Rate,Equipment_Fraction,Lighting_Fraction,Equip_Design_W,
    Light_Design_W` — T18c/nbf 2022, T20 main, T20 null, T26 lambda_0.0/0.5/1.0.
  - `wc -l` on all six — **every file is 6,934,321 lines (6,934,320 data rows)**, exactly
    matching the 144,465-household × 24-hour × 2-day-type shape already accepted by T20/T26's
    own collectors.
  - `head -5`/`tail -5` + targeted `grep -c` on the 2022 file: `Day_Type` has exactly two
    values, `Weekday` (3,467,160 rows) and `Weekend` (3,467,160 rows) — no `Saturday`/`Sunday`
    rows exist in the BEM schedule files (that 3-way split only exists earlier in the pipeline,
    at the person-level rake stage). `Hour` runs 0-23. `PR` is a province-name column
    (`Ontario` seen), **not a weight** — confirmed no weight/probability column exists anywhere
    in this schema.
  - Read `2026-09-15_T20_wp1_d1_2030_build.md` and `2026-09-15_T26_wp2_scenario_builds.md` in
    full (Design/Ledger/Decisions/Collector sections) — this answered "what main/null and
    lambda mean" directly from the manager's own written design, not by inspecting code fresh
    (see Decisions below for the exact quotes/citations).
  - Read `2026-09-15_T21_wp1_step8_step9_rerun.md` and `2026-09-21_T70_wp5_measured_vs_rebuilt_IMPL.md`
    in full — confirmed T21/out/step8 (and T70's read of it) holds per-household **EnergyPlus
    hourly ENERGY output** (`hourly_meters.csv`), never an occupancy-fraction schedule
    aggregate, and no `step9_activity`/`step9_baseline` tree or any other file in the project
    contains a saved 2022 at-home-by-hour aggregate. The only genuine 2022 at-home-by-hour
    source is the schedule-build CSV itself.
- **Local functional test, synthetic data (5 households × 2 day types × 24 hours, six files
  shaped exactly like the real schema)** — wrote `t76_make_synth.py`, ran the real script
  against the synthetic tree with paths/`EXPECTED_ROWS`/output dirs monkeypatched via a string
  substitution (not editing the real script), `CHUNKSIZE` shrunk to 50 to exercise the
  chunk-combining logic:
  - Clean run: all six `internal_count_match=True`, all six `match_expected=True` (240/240
    rows), `seen_working_match=True` on every file, `nesting_check_main_vs_lambda1.0`:
    48/48 cells exactly equal (by synthetic construction, mirroring the real SC0 property).
  - **Seen-failing-first control**: built a deliberately broken copy of the script (Hour
    shifted by 1 inside the aggregation's groupby key only, hand-read control left untouched)
    — every file's `seen_working_match` correctly flipped to `False`. Confirms the control is
    live, not a rubber stamp, before trusting its `True` on the real cluster run.
  - PNG inspected visually (two panels, Weekday/Weekend, 5 lines each, legend, correct axis
    range 0-1, dpi readback via Pillow `599.9988` — the same harmless PNG pixels-per-metre
    rounding artifact T71/T73 already documented, not a real shortfall). CSV has 288 data rows
    (6 series × 48 cells) exactly as expected.
- **Staged to Speed** via `scp -r` of a local tree already containing `T76/T76_scripts/`,
  `T76/logs/`, `T76/out/figures/` (avoids login-node `mkdir`, T70/T73's own documented
  preference). Remote `ls -la`: `t76_fig01_athome_by_hour.py` 13,641 B, byte-identical to the
  local file.
- CPU/queue check: `squeue -u o_iseri --format='%i %j %t %C'` (excluding the unrelated `histnu`
  array) showed only five 1-CPU 2J-project jobs running/pending — this job's 4 CPUs / 16 GB
  request is well within headroom.
- **JobID `1341263`** submitted from `speed-submit2`:
  `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 --job-name=T76_fig01_athome
  --chdir=/speed-scratch/o_iseri/2J_revision/T76
  --output=/speed-scratch/o_iseri/2J_revision/T76/logs/t76_run.out
  --wrap='/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T76/T76_scripts/t76_fig01_athome_by_hour.py'`
  Single `squeue -j 1341263` check immediately after submission: `R` (running), node
  `antenna1`, 0:01 elapsed — not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T76/`):
  - `logs/t76_run.out` — stdout of the whole job (`[DONE] <label>` per file,
    `[NESTING CHECK]`, `[DONE ALL]`)
  - `logs/t76_run_meta.json` — JobID, elapsed, per-file row-count/completeness control,
    seen-working control, nesting cross-check, main/null and lambda meaning text, 2022-baseline
    provenance text, dpi/pixel readback
  - `out/figures/fig01_athome_by_hour.png` — the figure
  - `out/figures/fig01_athome_by_hour.csv` — all six aggregated series (288 rows)

  **No number from the actual cluster run has been read yet by this employee** — everything in
  `## Verified` below is from local reconnaissance and the synthetic functional test, not from
  job `1341263`'s own real output. A failed job stays in this ledger with the line that
  supersedes it — never dropped.

## Verified

- Real-file header/row-count/Day_Type reconnaissance (see Ledger) — all six schedule CSVs
  confirmed identical schema, 6,934,320 data rows each, `Day_Type ∈ {Weekday, Weekend}` only,
  `Hour ∈ [0,23]`, no weight column.
- Synthetic functional test: clean run passes every control; deliberately-broken variant is
  seen failing on the same control first. See Ledger for exact numbers.
- **Nothing from the real cluster job (`1341263`) has been read** — see WHAT I DID NOT VERIFY.

## Decisions

1. **What "main" vs "null" (T20) mean — CONFIRMED, not guessed.** Read directly from
   `2026-09-15_T20_wp1_d1_2030_build.md`'s own Design section: `main` = 2030 built with the
   real OLS trend slope (`06_forecast_rake.py:138-165 project_to_2030`, fit on 2005/2010/2015
   real respondents) added to the 2022 stock rate, then raked to that target — the historical
   at-home trend is projected forward to 2030. `null` = the identical code path with
   `pre_slope` forced to an all-zero `(3,48)` array, i.e. `target == stock_rate (2022)` — a
   no-forecast-change control. T20's own N0 acceptance check already measured `null`'s
   weekday/weekend at-home means equal to 2022's to **0.0 pp**, with **100% of cells exactly
   equal** (`T20` Collector section, job `1328375`). This is the opposite of the task brief's
   own "plausible guess" (2030-with-WFH-persisting vs. a null/no-change arm) in one respect:
   there is no "WFH persisting" vs "not persisting" contrast in T20 at all — that contrast is
   what T26's `lambda` parameter provides. T20's `main`/`null` pair is really "trend continues"
   vs "trend flat," a different axis.
2. **What `lambda_0.0/0.5/1.0` (T26) mean — CONFIRMED, not guessed.** Read directly from
   `2026-09-15_T26_wp2_scenario_builds.md`: `lambda` is the persistence weight of the 2022
   pandemic-era at-home "jump" (the gap between the observed 2022 rate and where the pre-2022
   trend alone would have put it) relative to that pre-2022 trend. `lambda=1.0` = S-Persist
   (jump fully persists to 2030 — task 0 in the array), `lambda=0.5` = S-Partial (half
   persists — task 1), `lambda=0.0` = S-Revert (jump fully fades, only the pre-2022 trend
   continues — task 2). T26's own SC0 acceptance check already proved `lambda=1.0` is
   **100% cell-identical** to T20's `main` 2030 build (a nesting property, not a coincidence);
   SC2 proved the expected strict order `Revert < Partial < Persist` in national weekday
   at-home share, in all 5 archetypes too. This script's own `nesting_check_main_vs_lambda1.0`
   reproduces the SC0 equality independently on THIS aggregation's own code path, not by
   trusting the T26 doc's number alone.
3. **2022 baseline source — the Nb-f `BEM_Schedules_2022.csv` file itself, not a new
   computation.** `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/
   BEM_Schedules_2022.csv` is the SAME file T20's own N0/N1 acceptance checks already read to
   compute weekday/weekend at-home means, and the SAME file every 2030 build (T20 main/null,
   T26 lambda 0.0/0.5/1.0) was derived FROM (same 144,465 households, same stock, same schema).
   No separate 2022 at-home-by-hour aggregate exists anywhere else in the project — T21/T17
   hold per-household EnergyPlus hourly ENERGY output (what T70/T71/T73 read), not a
   household-level occupancy-FRACTION schedule aggregate. This satisfies the task brief's
   "quick aggregation reusing files T70/T71 already trust" bar (in spirit: this file is
   trusted by T20/T26's own acceptance machinery, which is the project's actual precedent for
   this exact aggregation method) — it is not the literal T70/T71 input files, but it needed no
   new simulation, no new modeling, and the identical grouped-mean method T20 N0/N1 already
   used on this same file. **This is why the hard-stop condition does NOT fire**: the 2022
   baseline was a same-shape file the project already has and already aggregates this way, not
   a substantial new computation.
4. **Aggregation method: unweighted mean of `Occupancy_Schedule` per `(Day_Type, Hour)` cell
   across all rows.** No weight column exists in any of the six files (`PR` is a province
   code). Each row is one real household (`SIM_HH_ID`), 144,465 total per file, matching
   T18c/T20/T26's own accepted household count — so the unweighted mean IS the population
   mean, literally the same method T20's own N0/N1 acceptance checks used on this same schema.
   No re-weighting was needed or invented.
5. **`lambda_1.0_persist` is aggregated (for the completeness/nesting cross-check) but NOT
   drawn as a separate line on the PNG**, since it is proven cell-identical to `main`
   (Decision 2) and would draw exactly on top of it with zero visible difference. Kept in the
   CSV deliverable for traceability; flagged explicitly in `run_meta.json` and the figure's own
   caption text — never a silent drop.
6. **Two-panel layout (Weekday / Weekend)**, 5 visible lines per panel, since `Day_Type` turned
   out to have exactly two real categories (not 3, per Decision-adjacent reconnaissance above)
   — a single panel with both day types overlaid was rejected as harder to read with 5 series
   already; a 2-panel small-multiple follows T73's own precedent for "more than ~4 series."
7. **No confidence interval plotted.** The source schedule CSVs carry point values only (no
   bootstrap/CI columns in this schema) — the figure's title states this explicitly ("point
   estimates, no CI in source data"), matching the project's "never invent a CI" rule.

## Next

- Manager/collector (fresh agent, later): `sacct -j 1341263` first for state/exit code. Fixed
  reading order per T71/T73 precedent: `logs/t76_run_meta.json` first —
  `row_count_control` (all six `match_expected`/`match_internal` must be `True`), then
  `seen_working_control` (all six `match` must be `True` — if any is `False`, do NOT trust the
  figure until diagnosed), then `nesting_check_main_vs_lambda1.0` (expect `all_equal: true`,
  reproducing T26's own SC0 on the real data) — then the PNG (visual inspection) and CSV.
- If any real-run `seen_working_control` entry reads `False`, or `nesting_check` does not read
  `all_equal: true` on the real files (unlike the synthetic test, which used engineered
  identical base values), that is a new finding needing diagnosis before the figure is
  trusted — do not round or silently accept.
- scp the PNG + CSV + `run_meta.json` + `logs/t76_run.out` back to `impl/T76_out/` for
  manager/author viewing (not yet done as of this write — job was still running when this doc
  was written).
- This is WP11's Figure 1. T74 (Figure 9) and T75 (Figure 8) are independent, running/dispatched
  in parallel by other employees — not touched by this task.

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341263`) on the real T18c/T20/T26 data.**
  Everything in `## Verified` above comes from direct file/header/row-count reconnaissance of
  the real (large) files (login-node-safe single-file commands only) and a synthetic local
  functional test — not from this job's real output. `logs/t76_run_meta.json`, the CSV, and the
  PNG on the cluster are all unread as of writing this doc.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue. The
  script does one chunked-pandas pass (small memory footprint, `usecols` limited to 3 columns)
  plus one independent full linear `csv.reader` pass (for the seen-working control) per file,
  six files total — expected to take longer than T71/T73's smaller/fewer-pass jobs (a rough
  guess of low tens of minutes given ~6.9M rows × 6 files × 2 passes), but this is an
  expectation from the synthetic test's timing profile scaled up, not a measurement of this
  job's real runtime.
- Whether the real six files' `nesting_check_main_vs_lambda1.0` actually reads `all_equal: true`
  the way T26's own SC0 already measured it — the synthetic test proved the CHECK fires
  correctly (both a true positive on engineered-identical data and a true negative via the
  broken-variant test), not that the real numbers will land exactly equal (they should, per
  T26's own already-accepted SC0 result, but this is unread on THIS script's own aggregation).
- Whether the real `Hour`/`Day_Type` combinations behave identically to the reconnaissance
  sample (only the 2022 file's head/tail/grep was directly inspected for `Day_Type` values;
  the other five files' headers were confirmed identical but their own `Day_Type` value sets
  were not separately `grep -c`'d — inferred from the identical schema and identical row count,
  not independently re-confirmed file-by-file).
- Whether Applied Energy's own figure guidelines would prefer a different layout than the
  2-panel/5-line design chosen here — not read for this task (same caveat T71/T73 already
  logged for their own layout choices).
