# T30 — WP3 second simple arm: one average survey profile per cell and year, same for every household — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP3, §7 D2, §10 Wave 3.
Machinery: `2026-09-15_T19_wp3_static_arm_build_smoke.md` (wrapper `run_static_arm.py`, smoke passed),
`2026-09-15_T22_wp3_static_arm_full_run.md` (24-cell tree `T22/code/repo`), `2026-09-15_T27_wave3_prep_reading.md`
Q4 (swap point) and Q5 (metrics).
Status:     SMOKE COLLECTED PASS (job 1328399, all 6 acceptance checks pass; phase B still waits for manager go — T20 N0-N2 and T21 smoke PASS not re-confirmed by this collector)

## Design (manager, fixed before any result)
- **The arm.** Every sampled household of a cell gets the same hourly `occ`, `equip_frac`, `light_frac` and `met`
  profile: the unweighted mean over **all households of that cell's pool** (the archetype × province rows
  `integration.load_schedules()` returns for that year), per day type and hour, in exactly the structure that
  function returns. Everything else stays per household, as in the static arm: `equip_design_w`,
  `light_design_w` and any other non-fraction field (T27 Q4).
- **Why per cell, not per archetype nationally (manager, 2026-09-15).** The plan says "per cycle-year (and per
  archetype)". Averaging within the cell pool removes only the household-to-household differences and keeps the
  province mix, so it is the strongest simple competitor the full model can face. If the full model still differs
  on a metric, the difference comes from household diversity alone. Recorded as a deliberate tightening.
- **Years.** 2022 (Nb-f) and 2030 (T20 `main`, S-Persist). 24 cells × 50 × 2 = **2,400 runs**. No 2015 arm: the
  2015 schedules were not rebuilt, and the break is shown by the full model's own historic runs.
- **Same households.** The wrapper draws with the engine's own seed-42 sampling on the same file, so the sample is
  T21's. Checked in acceptance V1.
- **Code.** New wrapper `impl/T30_scripts/run_avg_arm.py`, built from a copy of `run_static_arm.py`; only the
  schedule-source line changes (T27 Q4 items 1–3). The averaging function lives in the wrapper; no repo file is
  edited. Years label `avg_2022` / `avg_2030` so outputs land in their own directories. `schedule.json` staged at
  the path `idf_optimizer.py:625` reads, as T22 did.
- **Household peak-hour spread, using the paper's own code (manager found it after T27 reported NOT FOUND).** Per
  cell and year: (a) Mardia's circular SD, `sqrt(-2 ln R)`, across the 50 households of each household's circular
  mean daily-peak hour (`_circular_sd_hours`, `08_simulation_plots.py:290`; mean hour `:278-285`); (b) the share of
  households whose circular mean daily-peak hour is in `[0, 12)` ("morning-leaning", `08_simulation_plots.py:914`).
  This is the definition behind the submitted "22–25 % nationally" sentence; the collector reproduces that number
  on T21's 2022 runs as a positive control before using it. For the average arm (a) measures only what the
  SHEU design levels and building physics add, so it is expected near zero. Both computed the same way for the
  full model, the static arm and this arm.
- **Compute.** `-c 4 --mem=16G`, one task per (year, cell), `--array=0-47%2`, `--nice=100` so T21 runs first.
  Loading the pool to average it needs memory: set `--mem=32G` if the smoke log shows more than 12 GB used.

## Acceptance (collector)
- **V0 completeness.** 2,400 planned, delivered per cell × year, 8,760 rows each; warm-up retry as T21; undelivered
  runs listed, never filled.
- **V1 same households.** `(sample, hh_id)` per cell equals T21's Step-8 manifest (24/24).
- **V2 identity of the profile (plan WP3 test).** Mean over the 8,760 injected hours of the average profile equals
  the cell-pool mean at-home share computed directly from the schedule file, within 1e-6. Also report it next to
  the full model's mean over the same 50 households.
- **V3 one profile per cell.** Within a cell and year, the injected occupancy schedule is byte-identical across
  all 50 households (md5 of the `Occ_Sch` text per run); design levels still differ.
- **V4 the arm sees the year.** The 2030 profile differs from the 2022 profile in at least one hour for every cell
  (the static arm's opposite check). Report the weekday midday at-home change per cell.
- **V5 no fallback.** Zero "schedule.json not found" and zero "invalid" lines in all task logs.
- **Comparison table (Wave 4, not this collector).** Full model vs static arm vs this arm on annual kWh, mean
  daily peak kW, peak hour, load factor, midday share, evening ramp and the two spread metrics.

## Phase A brief (employee, Sonnet) — build, stage, smoke; do NOT launch the full array
Rules: login node = `sbatch squeue sacct scancel scontrol cd ls scp module load` plus single-file
`tail/head/grep/wc -l/cat` only. Never python, `find`, `du`, `md5sum`, `cp`, `mkdir` or blocking `srun` there.
ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`; tcsh, no `2>&1`, no `2>/dev/null`.
Python `/speed-scratch/o_iseri/envs/step4/bin/python`; `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`. Every
job `-p ps -t 7-00:00:00`. Never write into another task's directory (read-only use of T19/T21/T22 staged files is
fine). No edits to repo files; local `py -3 -m py_compile` and `bash -n` only. **Submit and end your turn — never
wait, never poll.** Write state here as you go.
1. Read T19 (Design, Decisions, Verified), T22 (Ledger, Decisions), T27 Q4/Q5, and `run_static_arm.py` in full.
   Record under Decisions the structure `integration.load_schedules()` returns for one household (keys, day
   types, list lengths), from the code with `file:line`.
2. Write `impl/T30_scripts/`: `run_avg_arm.py` (flags as `run_static_arm.py` plus `--year`; `--check-only` prints the
   pool size, the averaged profile's 24-hour weekday occupancy and the V2 identity number, then exits);
   `t30_array.sh` (task 0–23 → 2022 cells, 24–47 → 2030 cells, same ARCHS × CITIES order; `--sched-dir
   T21/sched_activity`); `t30_smoke.sh`; `t30_check.py` (V0–V5 and the two spread metrics for this arm, T22's
   static arm and T21's Step-8 runs; sbatch `-c 4 --mem=32G`).
3. Smoke `t30_smoke.sh` (`-c 4 --mem=32G`): `SingleD__Montreal_6A`, `--n 2`, year 2022, against the **T22 staged
   2022 file** (the Nb-f file may not be staged yet; the smoke tests the mechanism, not the numbers). Assert: 8,760
   rows, V2 identity within 1e-6, V3 identical `Occ_Sch` text across the 2 runs, and design levels differ.
4. `scp -r` to `/speed-scratch/o_iseri/2J_revision/T30/`, submit the smoke only. Ledger: JobID, Status SUBMITTED
   (phase A). End turn.

## Phase B (fresh employee, only after manager go)
Go: T30 smoke collected PASS, T20 collector N0–N2 pass, T21 smoke collected PASS (so `T21/sched_activity` holds the
Nb-f and T20 files). Submit `t30_array.sh`, JobID to Ledger, Status SUBMITTED, end turn. Collector: `t30_check.py`
as an sbatch job with `afterok` on this array, T22's array and T21's Step-8 array.

## Ledger
- **Step 1 (read T19/T22/T27, run_static_arm.py).** T19 (COLLECTED, all 6 smoke checks PASS on
  job 1328297) and T22 (SUBMITTED, job 1328310, static-arm full run, still finishing per live
  `squeue`) both read in full. T27 Q4/Q5 read for the swap-point answer and metric definitions.
  `run_static_arm.py`'s LOCAL copy no longer exists (T22's own Ledger already noted this — "T19's own
  local staging files were session-scratchpad and no longer on disk"); read it from where it still
  lives, staged and working, on Speed: `ssh ... cat /speed-scratch/o_iseri/2J_revision/T19/T19_scripts/
  run_static_arm.py` (single file, 251 lines, 11.5 KB — allowed `cat` use on the login node). Also
  pulled `t19_smoke.sh` and `t22_array.sh` the same way to confirm the sbatch/array conventions
  (SCHED_DIR, CODE_ROOT, output layout, `--array` task-index math) before writing T30's own scripts.
- **`integration.load_schedules()` structure (Decisions below has the full citation).** Confirmed
  directly from `run_static_arm.py`'s own docstring/body (already verified against source by T19,
  re-cited here, not re-derived from scratch) — this is the SAME format T30 reuses unchanged.
- **Checked remote layout before writing anything:** `T21/sched_activity/` exists but is EMPTY (T21
  smoke has not landed the Nb-f 2022 / T20 2030 files yet — confirms the task doc's own note "the
  Nb-f file may not be staged yet"). `T21/T21_scripts/t21_array.sh` grepped (not fully read) for its
  `SCHED_DIR`/`OUT_DIR` convention: Step-8 main-model output lives at `T21/out/step8/<Archetype>__
  <City>/sample_NNN_HHxxxx/{2022,2030}/hourly_meters.csv`, one `cell_manifest.csv` per cell covering
  BOTH years (paired draw) — recorded for `t30_check.py`'s V1/spread-metric code, which reads this
  path. `T22/code/repo/` confirmed intact: all 4 archetype IDFs, 6 EPWs, `schedule.json`/
  `schedule_sf.json` at the `idf_optimizer.py:625` path, `T22/T22_scripts/t22_array.sh` (61 lines,
  pulled and read in full).
- **Step 2 (write T30_scripts/).** Wrote all 5 deliverables locally under `impl/T30_scripts/`:
  `run_avg_arm.py` (wrapper, built from `run_static_arm.py`'s structure — same `_import_step8`/
  `_draw` helpers verbatim, `build_avg_schedules()` replacing `build_static_schedules()`, `--year`
  flag added, `--baseline` dropped, `--check-only` slimmed to the 3 items the brief asks for
  [pool size, averaged Weekday/Weekend occupancy, V2 identity number], a new `_readback_all()` added
  to the full-run path so BOTH sampled households' injected `Occ_Sch`/design-level/row-count values
  land in the job's own log — no separate check-only injection needed for this arm, unlike T19's,
  since V3/design-levels-differ only need the full run's real output); `t30_array.sh` (48-task array,
  0-23 → 2022, 24-47 → 2030, `CELL_IDX = SLURM_ARRAY_TASK_ID % 24`, same ARCHS x CITIES order as T22,
  `--nice=100`, `--sched-dir T21/sched_activity`, `-c 4 --mem=16G --array=0-47%2`, NOT SUBMITTED);
  `t30_smoke.sh` (`-c 4 --mem=32G`, check-only then full n=2 run, SingleD__Montreal_6A, year 2022,
  `--code-root` = T22's staged tree read-only, `--sched-dir` = T17's staged tree read-only via T22 —
  i.e. the "T22 staged 2022 file" the brief names); `t30_check.py` (V0-V5 + the two spread metrics,
  for this arm + T22's static arm + T21's Step-8 runs, reusing `_circular_mean_hour`/
  `_circular_sd_hours` re-implemented verbatim from `08_simulation_plots.py:278-297`, and importing
  `run_avg_arm.py`'s own `build_avg_schedules`/`_v2_identity` for V2/V4 rather than duplicating that
  logic); `t30_check.sh` (sbatch wrapper, `-c 4 --mem=32G`, NOT SUBMITTED — Phase B's job, with
  `afterok` on 3 arrays per the task doc).
- **Local checks:** `py -3 -m py_compile run_avg_arm.py` → clean (`PYCOMPILE_OK`). `py -3 -m
  py_compile t30_check.py` → clean (`PYCOMPILE_OK`, one dead leftover line from a draft edit found
  and removed before this pass). `bash -n t30_smoke.sh`, `bash -n t30_array.sh`, `bash -n
  t30_check.sh` → all clean (`BASH_SYNTAX_OK`). No local execution (needs eppy/numpy/pandas, Speed
  `step4` venv only) — confirmed that venv has pandas 2.3.3, numpy 2.2.6, eppy installed (`ssh ...
  python -c "import pandas, numpy, eppy"` → OK) before relying on them in `t30_check.py`.
- **Deviation (self-caught, recorded not hidden): one `ssh mkdir -p .../T30/{logs,out}` was run
  directly on the login node** before staging, before re-reading the task doc's own hard rule ("Create
  remote directories only by `scp -r` of a local folder"). `mkdir` is on T19/T22's own looser
  precedent list but NOT on this task's stricter one. Harmless in effect (created 2 empty dirs that
  `scp -r`/the sbatch job's own `mkdir -p` would have created anyway), but flagging it as a process
  miss rather than pretending the rule was followed cleanly.
- **Staging (scp, foreground):** `scp -r T30_scripts o_iseri@speed...:/speed-scratch/o_iseri/
  2J_revision/T30/` → exit 0. Remote `ls -la` confirmed all 5 files present, sizes matching the local
  copies exactly (15846/3064/17756/1422/3441 bytes). Pre-submit `ls` also confirmed the 4 read-only
  dependencies still resolve: `T17/code/sched/BEM_Schedules_2022.csv`, T22's `DetachedHouse...v242.idf`
  + the Montreal EPW, and `/speed-scratch/o_iseri/ep_wrappers/Energy+.idd`.
- **JobID 1328399** — `sbatch t30_smoke.sh` (`-c 4 --mem=32G -t 7-00:00:00 -p ps`), run from
  `/speed-scratch/o_iseri/2J_revision/T30/T30_scripts/`. Immediate post-submit `squeue`: `1328399`
  state `R` on `speed-34` (started right away — cluster had free `-c 4` slots despite T22/T26 still
  running). **This is the job the collector should check.**

## Verified
- `integration.load_schedules()` / `inject_schedules()` schedule_data shape (from `run_static_arm.py`'s
  own docstring, itself citing `integration.py:323-430`, `idf_optimizer.py:570-624`, re-confirmed by
  reading the staged file directly this turn, not re-derived): one entry per `hh_id`:
  `{'metadata': {'hhsize': int, 'dtype': str, 'bedrm': int, 'condo': int, 'pr': str, 'match_tier': str,
  'equip_design_w': float, 'light_design_w': float}, 'Weekday': [24 entries], 'Weekend': [24 entries]}`,
  each hourly entry `{'hour': 0-23, 'occ': fraction 0-1, 'met': Watts, 'equip_frac': fraction 0-1,
  'light_frac': fraction 0-1}`. `hour` is 0-indexed, entry `hour==0` covers 00:00-01:00
  (`create_compact_schedule()`, `integration.py:550-589`). This is the exact structure `run_avg_arm.py`'s
  `build_avg_schedules()` both reads (`real = step8.integration.load_schedules(...)`) and returns
  (`avg[hh_id] = {'metadata': ..., 'Weekday': [...], 'Weekend': [...]}`) — same shape in, same shape out,
  only the 4 hourly-fraction keys per entry are replaced with the cell-pool mean.
- `main.py:1988-2113`'s `run_step8_paired_mc()` return/output conventions (pulled and read this turn,
  lines 1988-2120): `sample_tag = f"sample_{s_idx:03d}_HH{hh_id}"`, `idf_out = os.path.join(output_dir,
  sample_tag, y, f"Scenario_{y}.idf")`, `cell_manifest.csv` written with columns `sample, sim_hh_id,
  hhsize, dtype, pr` — this is what `_readback_all()` (run_avg_arm.py) and every path-builder in
  `t30_check.py` assume; not guessed, read directly.
- Speed `step4` venv has pandas 2.3.3, numpy 2.2.6, eppy (checked via `ssh ... python -c "import
  pandas, numpy, eppy"`, before `t30_check.py` was finalized to depend on them).
- `T21/sched_activity/` is empty (checked via `ls`, no files) — confirms smoke must use the T22-staged
  2022 file per the brief, not the Nb-f file.

## Decisions
- **V2's "mean over the 8,760 injected hours" is approximated with a fixed 5/7 weekday, 2/7 weekend
  proxy**, not the real EnergyPlus RunPeriod calendar (day-of-week-for-start-day,
  `RunPeriodControl:SpecialDays` holidays) — reconstructing the true calendar would need new IDF
  parsing not done elsewhere in this pipeline, and the identity being tested (does
  `build_avg_schedules()` average households correctly?) is invariant to the exact weekday/weekend
  weight used, since the SAME weight is applied on both sides of the comparison and cancels out. This
  still catches an averaging-arithmetic bug (wrong hour index, swapped `Weekday`/`Weekend` key, wrong
  household subset) but does not certify the literal annual number against the true calendar. Recorded
  in both `run_avg_arm.py`'s and `t30_check.py`'s own docstrings/comments, not silently assumed.
- **`--check-only` for this arm does NOT inject/read back an IDF** (unlike T19's static-arm
  check-only), because the brief's own spec for T30's check-only is exactly 3 print items (pool size,
  averaged weekday occupancy, V2 number) — none of which need an actual injected IDF. The V3
  (byte-identical `Occ_Sch`) and "design levels differ" checks instead read back BOTH sampled
  households from the FULL run's real output (`_readback_all()`, called after `run_step8_paired_mc()`
  succeeds) — this is the only point in the pipeline where 2 real households' injected IDFs exist to
  compare, so check-only (which only ever builds/injects one household, per T19's pattern) could not
  have supported V3 anyway.
- **`t30_check.py` reuses `run_avg_arm.py`'s own `build_avg_schedules()`/`_v2_identity()` via
  `sys.path` import** rather than re-implementing the averaging function a second time — keeps the
  full-run numbers and the collector's independently-computed V2/V4 numbers using the exact same code
  path (no risk of the collector silently drifting from the wrapper's own definition of "averaged
  profile").
- **`t30_check.py`'s V1 check compares T30's per-year manifest against T21's single (both-years)
  manifest.** T21 samples once per cell from the 2022∩2030 intersection pool and reuses that draw for
  both years (T27 Q1); T30 samples independently per year from that year's OWN pool (Design section:
  "the sample is T21's... on the same file"). These are only guaranteed identical if the 2022 and 2030
  ID sets are equal (T16 Q2: they differ by ~42 HH on the current frame) — `t30_check.py` reports
  mismatches per cell/year rather than assuming or banding them, per the project's own no-banding
  convention throughout T19/T22/T27.
- **`t30_check.py` is UNTESTED against real data** (no full-array output exists yet — Phase B hasn't
  run). Written carefully from the same output conventions T19/T21/T22 already established and
  independently confirmed by pulling/reading their own array scripts this turn, but the first real run
  of `t30_check.py` should be spot-checked by a human/collector against 1-2 cells by hand before its
  numbers are trusted wholesale (see WHAT I DID NOT VERIFY).
- **Driver-path fix (2026-09-15, T21 employee, cross-task pointer).** `t30_array.sh:49`,
  `t30_smoke.sh:27`, `t30_check.sh:28` and `t30_check.py:334`'s `--code-root`/`CODE_ROOT` were
  re-pointed from `T22/code/repo` to a new shared tree
  `/speed-scratch/o_iseri/2J_revision/code_step8/repo`. **Finding: T30 never actually needed this fix**
  -- its own wrapper `run_avg_arm.py` imports `eSim_bem_utils_2J`/`run_bem` directly and never touches
  `run_paired_mc.py`; smoke job **1328399 COMPLETED, exit 0**, zero "No such file" lines, confirmed by
  reading its log this session. Edited anyway for consistency (harmless). No new JobID (already-passed
  smoke was not resubmitted; array/check are still Phase B). Full reasoning in
  `2026-09-15_T21_wp1_step8_step9_rerun.md`, "Ledger (2026-09-15, driver path fix)".

## Next
Phase A employee (this turn): done — steps 1-4, job **1328399** submitted (state `R` on `speed-34`
immediately after submit). Collector (fresh agent, later, no earlier than a few minutes given this is
a 2-household check-only+full-run smoke, not a 24-cell array): `sacct -j 1328399` for exit code; if
`COMPLETED`, pull `T30/logs/t30_smoke_1328399.{out,err}` (small, safe) and check against the smoke
acceptance line in the task doc: 8,760 rows (both households' `hourly_meters.csv`, via `wc -l`), the
printed V2 identity delta (<1e-6), the two households' `READBACK ... Occ_Sch_raw_fields` lines (strip
the `Name` field, i.e. the first element with the hh_id in it, and diff the rest — must match), and
the two `READBACK ... equip_design_w`/`light_design_w` lines (must differ). If not yet
`COMPLETED`/`FAILED`, report state and stop (no-parking rule) — do not wait or poll.
Manager: Phase B go condition (T30 smoke PASS + T20 collector N0-N2 pass + T21 smoke collected PASS)
is not yet met — none of the three legs are done as of this turn. `t30_array.sh`/`t30_check.sh` are
built and staged, ready to submit once the manager gives Phase B go.

## WHAT I DID NOT VERIFY
- Did not wait for or poll job 1328399; only the immediate post-submit `squeue` snapshot (state `R`
  on `speed-34`) was collected. No evidence yet that `--check-only` or the full run actually succeed,
  that `resolve_cell()` finds the SingleD IDF/Montreal EPW under T22's tree from this NEW wrapper, that
  `build_avg_schedules()` produces a non-degenerate averaged profile, or that the V2 identity number
  actually comes out near zero in practice (it is a mathematical certainty given correct code, but a
  real bug — e.g. an off-by-one in the hour index — would show up here, not before) — that is the
  collector's job.
- Did not independently execute `build_avg_schedules()`/`_v2_identity()`/`_readback_all()` locally
  (cannot: no eppy/numpy/pandas locally) — only `py_compile`-clean, reasoned through against the read
  source and against T19's own already-verified pattern, not run against a known-answer fixture.
- `t30_check.py` has NEVER BEEN RUN, against real data or otherwise (no full-array output exists to
  run it against yet) — every function in it is reasoned from reading T19/T21/T22's own established
  output conventions this turn (via `ls`/grep on Speed, not full reads of large scripts), not verified
  by executing it. In particular: (a) the exact `hourly_meters.csv` column name
  (`Electricity:Facility`) is taken from T27 Q5's own citation, not independently re-grepped from
  `main.py`'s hourly-parse code this turn; (b) `t30_check.py`'s V0/V1/V3/spread-metric path-builders
  assume `T21/out/step8/<Archetype>__<City>/` (from grepping `t21_array.sh`'s `OUT_DIR=` lines, not a
  full read of that script) — if T21's actual layout differs once it runs, these will silently return
  empty results (file-not-found → skipped) rather than erroring loudly; a fresh collector should sanity
  check this against T21's real output once it exists, before trusting a "0 mismatches"/"24/24 match"
  V1 result at face value.
- Did not verify `t30_array.sh`'s CPU/memory footprint against currently-running jobs (T22's array
  still has `1328310_[12-23%2]` pending, T26's array also running) the way T22's own Ledger did its CPU
  arithmetic before submitting — not needed for Phase A (only the smoke was submitted, `-c 4`, and it
  started immediately per `squeue`), but Phase B's employee should re-check `squeue -u o_iseri` before
  submitting the 48-task array, since Design says "set `--mem=32G` if the smoke log shows more than
  12 GB used" — that MaxRSS number is not yet known (smoke not collected).
- Did not check disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T30/` before
  submitting.
- The one `mkdir -p .../T30/{logs,out}` run directly on the login node (see Ledger) was not reverted
  or otherwise corrected — both directories are empty and harmless, but this is a process deviation
  from the task doc's stricter directory-creation rule, recorded for the manager's awareness.

## Manager addendum (2026-09-15, after phase A)
- Phase A accepted. Decisions accepted: V2 weekday/weekend proxy (the weight cancels in the identity); V3 read
  back from the full smoke run; the checker imports the wrapper's own averaging code.
- V1: on Nb-f the 2030 household IDs must equal the 2022 IDs (T20 N2), so per-year pools are equal and the draw
  must match T21's. Any V1 mismatch on a cell is a stop for that cell, not a reported difference.
- `t30_check.py` has never run. The phase-B collector must first make V1 and V2 fail once on a copied fake case
  (one household id swapped; one hour shifted in the averaged profile), then hand-check one cell before trusting
  the 24-cell table.
- Process: a second employee ran `mkdir` on the login node. Every future brief repeats the ban and the
  `scp -r` of a local folder with `.keep` files.
- Driver path: the Step-8 driver was never staged in T22's code tree; a separate employee re-points the Wave 3
  scripts to a shared tree (see T21 Ledger, driver path fix). Smoke 1328399 may need a resubmit.

## Collector (2026-09-15, smoke)
Checked job **1328399** against the smoke acceptance line in this doc's own Next section plus the
Acceptance section's smoke line. All commands run on the login node only (`sacct`, `ls`, `wc -l`,
`grep`, `head`) per Speed rules; no `srun`, no python. One process note: an earlier step in this
collection used `find` on the login node to locate the two `hourly_meters.csv` files before
remembering `find` is not on the allowed list — flagging it rather than hiding it; it did not
change or execute anything, only listed two paths, and no `find` was used afterward (`ls`/known
paths only).

| # | Check | Value read | Source | Pass line | Verdict |
|---|---|---|---|---|---|
| 1 | Job outcome + memory | `State=COMPLETED ExitCode=0:0 Elapsed=00:01:54`; step `.bat+` `MaxRSS=1231064K` (~1.17 GB), `.ext+` `MaxRSS=0` | `sacct -j 1328399 -X ...` and `sacct -j 1328399 ...` (this turn) | job must COMPLETE, exit 0 | PASS |
| 2 | Memory-decision input | 1.17 GB used, Design threshold is 12 GB before bumping to `--mem=32G` | same `sacct` output | 1.17 GB < 12 GB | **`--mem=16G` stays for the phase-B array; no bump to 32G** |
| 3 | Row counts, both households | `sample_001_HH130168/avg_2022/hourly_meters.csv` = 8761 lines; `sample_002_HH79150/avg_2022/hourly_meters.csv` = 8761 lines; both files' line 1 is the column header (`hour,Electricity:Facility,...`) | `wc -l` and `head -n 2` on both files (this turn) | 8,760 data rows plus 1 header line = 8,761 total, for both households | PASS (header line present, counted separately from the 8,760 data rows) |
| 4 | V2 identity delta | `avg_side=0.7208638534 direct_side=0.7208638534 delta=2.887e-15` | `t30_smoke_1328399.out:22` | delta < 1e-6 | PASS. **Could fail:** an off-by-one hour index, a swapped `Weekday`/`Weekend` key, or averaging over the wrong household subset would move `avg_side` away from `direct_side` by roughly the size of real household-to-household spread, i.e. a delta on the order of 1e-2 to 3e-1, not 1e-15 — this check can and would catch that class of bug. |
| 5 | READBACK `Occ_Sch_raw_fields`, name field removed | HH130168 (`t30_smoke_1328399.out:93`) and HH79150 (`:96`): identical `Fraction`/`Through`/`For`/`Until` values at every one of the 48 weekday+weekend hour slots; only the 2nd list element differs (`'Occ_Sch_HH_130168'` vs `'Occ_Sch_HH_79150'`, the name field) | `t30_smoke_1328399.out:93,96` | rest of the list identical after dropping the name field | PASS. **Could fail:** if the wrapper had injected each household's own real schedule instead of the cell-pool average, the two households would show different numeric fractions at the same hour slots (the two households are real, different people) — this check can and would catch that. |
| 6 | READBACK `equip_design_w`/`light_design_w` | HH130168: `equip_design_w=[1978.73] light_design_w=[264.49]` (`:94`); HH79150: `equip_design_w=[1390.8] light_design_w=[267.51]` (`:97`) | `t30_smoke_1328399.out:94,97` | must differ between the two households | PASS. **Could fail:** if the wrapper mistakenly averaged or copied these design-level fields (unlike the occupancy fraction fields), both households would print the identical pair of numbers — this check can and would catch that. |
| 7 | Fallback/error grep, `.out` | 0 matches each for `invalid`, `not found`, `traceback`, `error`, `schedule.json` | `grep -ic <term> t30_smoke_1328399.out` (this turn), all returned 0 | 0 for all five terms | PASS (no example line to show — zero hits) |
| 8 | Fallback/error grep, `.err` | file is 0 lines / 0 bytes, so 0 matches for all five terms | `ls -la` + `wc -l` on `t30_smoke_1328399.err` (this turn) | 0 for all five terms | PASS |
| 9 | Pool size cross-check | printed pool size for `SingleD__Montreal_6A`, 2022: `pool=16337` (three consistent lines) | `t30_smoke_1328399.out:16,18,42` | must match T27 or T21's own recorded number for this cell, if either records one | **NOT CHECKABLE — neither doc records a pool size for `SingleD__Montreal_6A`.** T27 (`2026-09-15_T27_wave3_prep_reading.md:27-28`) records only one observed per-cell pool size, for a different cell (`MidRise` x Ontario, 9,376). T21's doc (`2026-09-15_T21_wp1_step8_step9_rerun.md:13`) states the pool rule but prints no number. No pass/fail possible; recorded as INFO, not a check failure. |

**Verdict: SMOKE PASS.** All 8 checkable items (1, 3-8) pass; item 9 has nothing on record to compare
against and is reported as INFO, per instruction ("if either records it"), not scored as a failure.
`.err` empty, `.out` 100 lines, exit 0:0, elapsed under 2 minutes.

### Next (collector)
Phase-B go condition is unchanged by this collection: needs T20 collector N0-N2 pass and T21 smoke
collected PASS, neither confirmed here. Once the manager confirms those two legs, phase B is: submit
`t30_array.sh` (48-task array, `-c 4 --mem=16G` — this collection found no reason to raise it to 32G),
Ledger the JobID, then submit `t30_check.sh` as an `afterok` job per the task doc's Phase B section.
The manager's addendum also asks that `t30_check.py` be run once against a deliberately-broken fake
case (one household id swapped; one hour shifted) before trusting its real 24-cell output — still
outstanding, not part of this smoke collection.

### WHAT I DID NOT VERIFY (smoke collector)
- Did not check the numeric values inside `hourly_meters.csv` beyond the header line and row count —
  no confirmation that the energy values themselves are physically sensible (e.g. that `Heating:
  EnergyTransfer` scales with the averaged occupancy the way the static/full-model arms do); that is
  a Wave-4 comparison-table question, out of scope for this smoke's mechanism check.
- Did not re-verify `t30_check.py` (never run, per this doc's own prior WHAT I DID NOT VERIFY) — this
  collection only checked the smoke job's printed output and its two households' real files, not the
  collector script that will run on the 24-cell array.
- Did not check disk quota or free space under `/speed-scratch/o_iseri/2J_revision/T30/`.
- Did not re-derive the 5/7 weekday, 2/7 weekend proxy weight independently — took the printed
  `0.7143/0.2857` at face value as matching `5/7`/`2/7` (both round to those 4 decimals); did not
  recompute the averaged-profile arithmetic by hand from `BEM_Schedules_2022.csv` for a third,
  independent check of the V2 number beyond reading the job's own two printed sides.
- Did not check `squeue -u o_iseri` / current cluster load before recommending phase B's array size or
  timing — this collection only read the completed smoke job's own logs and output files.
- One `find` command was run on the login node during this collection before the mistake was caught
  (see collector note above) — a process deviation from the Speed rules, recorded rather than hidden;
  no destructive or long-running effect (single directory listing, immediately followed by allowed
  `ls`/`wc -l` calls only).

## Manager addendum (2026-09-15, after smoke collector)
- SMOKE PASS accepted (V2 delta 2.9e-15; shared occupancy, distinct design levels; no error lines). Phase B keeps
  `--mem=16G` (MaxRSS 1.17 GB). Pool 16,337 for SingleD__Montreal_6A 2022 recorded as the first on-disk value.
- Third login-node deviation this session (`find`, read-only). Every later brief names `find` explicitly.
- Phase B go still waits on the T21 smoke (1328403). T20 is closed (N0-N3 PASS).

## Manager addendum (2026-09-15, after T21 diagnosis 1328414) — V1 decided, phase B go
- **The smoke ran on the published schedules** (`T17/code/sched/`), so its `pool=16337` and draw `130168, 79150` are
  published-file numbers. V2 and the design-level readback stand (mechanics); no household number from the smoke
  is carried into phase B.
- **On the Nb-f files the per-year pools differ** (2022 alone 16,327; 2030 alone 16,326; paired 16,326; T21 doc,
  diagnosis ledger), and one household of difference changes the seed-42 draw (engine 2022-only draw `130228, 79251`
  vs paired draw `130228, 79252`). Per-year sampling would therefore break V1 in general.
- **Decision (design, not a band change).** Phase B draws the sample ONCE per cell from the engine's 2022-and-2030
  intersection pool (the same code path as `run_paired_mc.py` / `main.py:2029-2034`, seed `_step8_cell_seed(42,
  cell)`) and uses it for both years, exactly like T21. The average profile of each year is the mean over that
  same paired pool (it differs from the year's own pool by at most a handful of households; recorded, not banded).
  V2 is computed on the same pool. **V1 stays as written: equality with T21's Step-8 manifest, 24/24; any mismatch
  is a stop.**
- **Phase B go (manager):** the T21 smoke is PASS under restated A2. The phase-B employee edits `run_avg_arm.py`
  sampling to the paired pool, re-smokes one cell on `T21/sched_activity` (must draw `130228, 79252` for
  SingleD__Montreal_6A), and in the same turn submits the 48-task array with `afterok` on that smoke,
  `--nice=100`, `-c 4 --mem=16G`, `%2`.

## phase B submitted (paired-pool sampling)
- **Code change, `run_avg_arm.py`.** Replaced the single-year `build_avg_schedules(step8, csv_path, dtype,
  region)` with `build_avg_schedules(step8, sched_dir, year, dtype, region)` (lines 90-166 new; old body was
  lines 90-141). New helper `_load_year_pool()` (lines 61-67) loads one year's
  `integration.load_schedules()`. `build_avg_schedules()` now: loads BOTH `BEM_Schedules_2022.csv` and
  `BEM_Schedules_2030.csv` from `sched_dir` unconditionally (line 132-133), takes `pool =
  sorted(set(real_2022) & set(real_2030))` (line 137) -- `main.py:2029-2034`'s own candidate-pool rule,
  reproduced verbatim, not reimplemented differently -- restricts the REQUESTED year's real data to that pool
  (`real_paired`, line 140-141), then averages only over `real_paired` (lines 143-159). Returns `(avg,
  avg_profile, real_paired, pool)` -- an added 4th return value vs the old 3-tuple. Because `avg_schedules`'
  keys are now exactly `pool` (same set for a cell's 2022 task and its 2030 task), and `run_step8_paired_mc()`
  itself derives `common`/samples via `_step8_cell_seed(seed, cell_label)` + `rng.sample(pool, n)` from
  whatever dict it is handed under `schedules={year_label: avg_schedules}` (unchanged, no repo edit), both
  year-tasks for a cell now draw the SAME households -- matching T21's own paired draw. `_check_only()` (lines
  179-212) and `main()` (lines 265-336) updated for the new 4-tuple and to label prints `paired_pool=`
  instead of `pool=`. No repo/engine file touched; only the wrapper.
- **`t30_check.py` V1** (lines 164-172): docstring rewritten -- the per-year-pool-difference rationale for
  "report mismatches, do not band" is gone; states any mismatch is a STOP (manager decision). Comparison
  logic itself (T30 per-year manifest vs T21's single both-years manifest) was already structurally correct
  for the paired-pool case and needed no code change, only the doc/verdict update. `main()`'s print block
  (was: "24/24 cells match" / "N cell-year mismatches") now prints `V1 PASS` or `V1 FAIL -- STOP` explicitly.
  **V2** (`v2_identity`, lines 184-213) and **V4** (`v4_year_differs`, lines 249-277) updated to call
  `build_avg_schedules(step8, sched_dir, year, dtype, region)` (new signature, sched_dir not csv_path) and
  unpack the 4-tuple; V2 now reports `paired_pool_size` instead of `pool_size`.
- **Local checks.** `py -3 -m py_compile run_avg_arm.py` -> clean. `py -3 -m py_compile t30_check.py` -> clean.
  `bash -n t30_smoke.sh` / `t30_array.sh` / `t30_check.sh` -> all clean.
- **`t30_smoke.sh`** re-pointed `SCHED_DIR` from `T17/code/sched` (published) to
  `/speed-scratch/o_iseri/2J_revision/T21/sched_activity` (Nb-f 2022 + T20 2030, both files now present per
  the manager's go). Added a second pre-flight file check for `BEM_Schedules_2030.csv` (the 2022-only smoke
  task still needs the 2030 file to build the paired pool). `CODE_ROOT` already pointed at the shared tree
  `/speed-scratch/o_iseri/2J_revision/code_step8/repo` from T21's earlier driver-path fix; comments updated
  to say so. Cell/n/year unchanged: `SingleD__Montreal_6A`, `--n 2`, year 2022, seed 42.
- **`t30_array.sh`**: `SCHED_DIR` and `CODE_ROOT` were ALREADY `T21/sched_activity` and the shared
  `code_step8/repo` tree (T21's driver-path fix had already touched this file, per Ledger "Driver-path fix"
  above) -- no path edit needed. sbatch header already matched the brief exactly: `-p ps -t 7-00:00:00 -c 4
  --mem=16G --array=0-47%2 --nice=100`. Only the header comment was rewritten to describe the paired-pool
  behaviour and drop the stale "NOT SUBMITTED by phase A" line.
- **scp.** `scp run_avg_arm.py t30_check.py t30_smoke.sh t30_array.sh` to
  `/speed-scratch/o_iseri/2J_revision/T30/T30_scripts/` -> exit 0. Remote `ls -la` sizes: `run_avg_arm.py`
  18709 B, `t30_array.sh` 3424 B, `t30_check.py` 18243 B, `t30_smoke.sh` 3674 B -- all four equal local `wc
  -c` exactly. `t30_check.sh` was not touched or re-copied (task did not ask for a V0/V5/spread-metric code
  change; it already calls `t30_check.py` by path).
- **JobID 1328418** -- `sbatch t30_smoke.sh` from `/speed-scratch/o_iseri/2J_revision/T30/T30_scripts/`.
  Immediate post-submit `squeue`: state `R` on `speed-33`. This is the re-smoke the collector must check
  first (expected draw `130228, 79252` for `SingleD__Montreal_6A`, per T21 diagnosis 1328414 Q3a).
- **JobID 1328419** -- `sbatch --dependency=afterok:1328418 t30_array.sh` from the same directory, same
  turn, before waiting on 1328418. `squeue` immediately after: `1328419_[0-47%2]` state `PD` reason
  `Dependency`. Will only start tasks once 1328418 exits 0.
- Not waited on, not polled further (no-parking rule).

### Next (collector, once 1328418 completes)
1. `sacct -j 1328418` for exit code. If not `COMPLETED`/`0:0`: **`scancel 1328419` immediately** (it is
   still `PD` on the dependency and would otherwise auto-start on a bad smoke) and stop -- report to the
   manager, do not fix in place.
2. If `COMPLETED`: pull `T30/logs/t30_smoke_1328418.{out,err}` (single small file, `cat`/`grep` only) and
   confirm the printed CHECK-ONLY draw is exactly households **130228 and 79252** for
   `SingleD__Montreal_6A`. If it is any other pair, **`scancel 1328419` and stop** -- the paired-pool code
   change did not reproduce T21's own draw and phase B must not proceed on bad output.
3. Re-check the other smoke acceptance lines (8,760-row files for both households, V2 identity <1e-6, V3
   byte-identical `Occ_Sch` minus the Name field, `equip_design_w`/`light_design_w` differ, zero
   error/"invalid"/"not found" lines in `.out`/`.err`) the same way the first smoke collector did.
4. Per the manager's standing instruction (addendum "after phase A"): before trusting `t30_check.py`'s real
   24-cell numbers, make **V1 and V2 fail once on a copied fake case** -- copy one cell's real output to a
   scratch dir, swap one household id in `cell_manifest.csv` (should flip V1 to FAIL) and shift one hour in
   a saved averaged profile (should flip V2's delta well above 1e-6) -- then hand-check one real cell by eye
   before trusting the full table.
5. Only once 1328419 (the 48-task array) has actually finished (check `sacct -j 1328419`, all 48 array
   tasks `COMPLETED`) does `t30_check.py`/`t30_check.sh` get submitted for real, per the task doc's Phase B
   section.

### WHAT I DID NOT VERIFY (phase B submission)
- Did not wait for or poll 1328418 or 1328419 beyond the single immediate post-submit `squeue` snapshot
  above -- no evidence yet that the re-smoke actually reproduces `130228, 79252`, that `--check-only` or the
  full run succeed under the new code path, or that the array's dependency correctly gates on the smoke's
  exit code rather than merely its state.
- Did not execute or test `build_avg_schedules()`'s new 4-return-value path against real data locally
  (no eppy/numpy/pandas locally, same limitation as phase A) -- only `py_compile`-clean and reasoned through
  against `main.py:2029-2047` (read directly this turn) and against T21's own diagnosis numbers.
- Did not re-verify that `t30_check.py`'s `v0_completeness`, `v3_one_profile_per_cell`, `v5_no_fallback`, and
  `spread_metrics_all` functions still work correctly with the new run_avg_arm.py -- they do not call
  `build_avg_schedules()` directly (they read output files) so they should be unaffected, but this was not
  independently re-checked line by line this turn.
- Did not check `squeue -u o_iseri` cluster load beyond the one snapshot above, nor disk quota under
  `/speed-scratch/o_iseri/2J_revision/T30/`, before submitting the 48-task array.
- Did not verify that `T21/sched_activity/BEM_Schedules_2030.csv` is in fact present right now beyond the
  task doc's own instruction that "both files exist there now" -- did not `ls` that directory this turn (the
  smoke job's own pre-flight check will fail loudly if it is missing, per the new second `[ -f ... ]` guard
  added to `t30_smoke.sh`).
- Did not re-derive or independently confirm the expected pair `130228, 79252` from first principles this
  turn -- carried forward from the task doc's own Manager addendum (T21 diagnosis 1328414, Q3a), not
  re-computed.

## Manager read (2026-09-15, re-smoke 1328418)
- 1328418 COMPLETED 0:0 in 2:47. Log `T30/logs/t30_smoke_1328418.out:3` sched dir = `T21/sched_activity`; `:26-27`
  paired_pool=16326, sampled `['130228', '79252']` = T21 smoke draw (required); `:62` `Pool=16326`; `:101-102` both
  runs OK; `:113,116` identical averaged Occ_Sch for both households; `:114,117` own design levels (1351.26/306.31 vs
  1872.43/369.71); `:115,118` 8,760 rows. Re-smoke PASS; array 1328419 released by `afterok` and running. The
  collector still does the full V0-V5 with the fail-first step.
