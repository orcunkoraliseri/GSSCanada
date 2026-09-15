# T19 — WP3 static code-schedule arm: wrapper script + Speed smoke — implementation state

Task doc:   this file (brief below). Plan: `../00_REVISION_PLAN.md` §3 WP3 arm 1. Machinery map: `2026-09-15_T16_step8_run_machinery.md` (Q4, Q5, Q7, Q8). Staging precedent: `2026-09-15_T17_speed_reproduces_local_campaign.md`.
Status:     COLLECTED

## Design (manager, fixed before build)
- **Same households, same SHEU levels, static schedules.** For each of the 50 seed-42 households per cell,
  run the base IDF with `integration.inject_schedules()` exactly as the campaign does, except the
  household diary is replaced by the DOE MidRise standard residential profile from
  `idf_optimizer.load_standard_residential_schedules(baseline='midrise')` (`idf_optimizer.py:570-624`,
  `0_BEM_Setup/Templates/schedule.json`). Same weekday/weekend profile every day of the year, every
  household, every archetype (the main model uses the MidRise baseline for all archetypes too).
  So only the occupancy timing differs from the main model; SHEU design levels stay per household.
- Year-independent: schedules come from no survey year. The household sample and SHEU levels are taken
  from the **2022** schedule file with `--years 2022` sampling. (The 2022 rebuild keeps the same census
  households, so the sample does not depend on WP1; if T18 shows the ID frame changed, rerun only the
  sampling, not this design.)
- **No edits to pipeline source.** New wrapper `T19_scripts/run_static_arm.py` imports the Step-8 modules
  and replicates the per-sample loop of `run_step8_paired_mc()` (`main.py:2029-2113`), passing a static
  `schedule_data` dict built in the same format `integration.load_schedules()` returns
  (`integration.py:323`). Outputs mirror the campaign: `Scenario_static.idf`, E+ outputs,
  `hourly_meters.csv`, `cell_manifest.csv`.

## Brief (employee, Sonnet)
Rules: Speed login node = `sbatch squeue sacct scancel scontrol cd ls scp` and single-file
`tail head grep wc -l cat` only; never python, `find`, `du`, `md5sum` there. Every job `-t 7-00:00:00`,
`-p ps`. ssh with `-o BatchMode=yes -o ConnectTimeout=60`; tcsh, so no `2>&1` in ssh strings. Create
remote dirs by `scp -r` of a local staging folder; run scp in the foreground. Do not touch
`/speed-scratch/o_iseri/2J_revision/T17/` except **read-only use of its staged code tree**
`T17/code/repo/` and `T17/code/sched/BEM_Schedules_2022.csv` (T17 jobs may still be running; never write
there). Do not edit any existing repo file. Write state into this doc as you go. **Submit and end your
turn — never wait for a job.**

1. Read `main.py:1952-2113`, `integration.py:300-420` (load_schedules format) and `:1269-1320`
   (inject_schedules signature), `idf_optimizer.py:570-624`. Record the `schedule_data` format and how you
   map the standard profile into it (which keys; fractions 0-1; hour indexing) under Decisions.
2. Write `impl/T19_scripts/run_static_arm.py` (args: --archetype --city --n --seed --sched-dir
   --output-dir --code-root) and `impl/T19_scripts/t19_smoke.sh` (sbatch, `-c 4 --mem=16G`,
   `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`, python `/speed-scratch/o_iseri/envs/step4/bin/python`).
   Local check: `py -3 -m py_compile` only (no local runs).
3. Also write in the wrapper a `--check-only` mode that, after building one injected IDF, prints: the
   sampled household IDs, the occupancy schedule values written into the IDF for one weekday, and the
   equipment/lighting design levels. The smoke job runs `--check-only` first, then MidRise × Toronto_5A
   with `--n 2`, output under `/speed-scratch/o_iseri/2J_revision/T19/out/`.
4. Stage `T19_scripts/` to `/speed-scratch/o_iseri/2J_revision/T19/` via `scp -r`, submit the smoke job,
   write the JobID in the Ledger, set Status SUBMITTED, end turn.

**Smoke acceptance (checked later by a fresh collector):** exit 0; 2 runs with `hourly_meters.csv`
8760 rows; the 2 sampled IDs equal the first 2 IDs the seed-42 campaign draw gives for that cell with
`--n 2` (print the `--n 50` list too and state whether the n=2 draw is its prefix — record, not banded);
injected occupancy values equal `schedule.json` values; design levels differ between the 2 households.

## Ledger
- **Local files written** (scratchpad staging dir, then scp'd): `T19_scripts/run_static_arm.py`
  (wrapper: `--check-only` + full-run modes) and `T19_scripts/t19_smoke.sh` (sbatch script).
- **`py -3 -m py_compile run_static_arm.py`** → clean, no output (`PYCOMPILE_OK`). **`bash -n
  t19_smoke.sh`** → clean (`BASH_SYNTAX_OK`). No local execution (needs eppy/numpy which are only
  installed in the Speed `step4` venv).
- **Staging (scp, foreground):** remote parent dir did not exist yet, so `ssh mkdir -p
  /speed-scratch/o_iseri/2J_revision/T19/{logs,out}` first (login-node `mkdir`, allowed), then `scp -r
  T19_scripts o_iseri@speed...:/speed-scratch/o_iseri/2J_revision/T19/` (exit 0, no error). Remote `ls`
  confirmed `run_static_arm.py` + `t19_smoke.sh` present. Pre-submit `ls` also confirmed T17's staged,
  read-only tree is still there: `T17/code/repo/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py`
  and `T17/code/sched/BEM_Schedules_2022.csv` both exist (T17 jobs 1328286/1328290 were still running at
  submit time per `squeue`; nothing was written into `T17/`, only read via `ls`).
- **JobID 1328296** — `sbatch t19_smoke.sh` (`-c 4 --mem=16G -t 7-00:00:00 -p ps`), first submission,
  `CODE_ROOT=T17/code/repo`. **CANCELLED by this employee turn before it could reach the full-run
  stage** (`scancel 1328296`, state went `R` → `CG`) after finding a real defect (see Decisions): reusing
  T17's staged tree for `--code-root` would have made every `load_standard_residential_schedules()` call
  silently fall back to a hardcoded approximation instead of the real DOE MidRise `schedule.json` profile
  — defeating the point of the design ("DOE MidRise standard residential profile from
  `idf_optimizer.load_standard_residential_schedules`"). Not a wasted run: `--check-only` would still
  have exited 0 (the fallback function also returns a well-formed dict), so this bug would NOT have
  shown up as a job failure — only as silently wrong data. Caught by inspection before any output was
  trusted, not by the job failing.
- **Fix (staging only, no wrapper code change, no pipeline source edit):** built a small, T19-owned
  code+asset tree (`T19/code/repo/`, 3.1 MB: the 16 `eSim_bem_utils_2J/*.py` files + `run_bem.py`
  unmodified, ONE MidRise IDF, ONE Toronto EPW, and `0_BEM_Setup/Templates/{schedule.json,
  schedule_sf.json}` placed at the exact path `idf_optimizer.py`'s own (unedited, buggy) `base_dir` calc
  looks for them — see Decisions) and pointed `CODE_ROOT` at it instead of T17's tree. `SCHED_DIR`
  unchanged, still `T17/code/sched` (the one large ~674 MB file the Brief named for read-only reuse).
  Staged via `ssh mkdir -p T19/code` then `scp -r T19_code/repo → T19/code/repo` (exit 0) + `scp
  t19_smoke.sh` (exit 0, overwriting only the `CODE_ROOT=` line inside T19's own tree — T17 untouched).
  Remote `ls` confirmed `schedule.json`, `schedule_sf.json`, the IDF, the EPW, and 16 `.py` files all
  landed. `bash -n t19_smoke.sh` re-run clean after the edit.
- **JobID 1328297** — `sbatch t19_smoke.sh` (`-c 4 --mem=16G -t 7-00:00:00 -p ps`), corrected
  `CODE_ROOT=/speed-scratch/o_iseri/2J_revision/T19/code/repo`, run from `T19/T19_scripts/`. Two stages
  inside one job: (1) `--check-only` on MidRise × Toronto_5A, n=2, seed=42, output under
  `T19/out/_check_only/`; (2) if stage 1 exits 0, full run MidRise × Toronto_5A, n=2, seed=42, output
  under `T19/out/MidRise__Toronto_5A/`. `squeue` immediately after submit: `1328297` state `R` on
  `magic-node-09`. **This is the job the collector should check — 1328296 is superseded, not a real
  result.**

## Verified

**Step 1 — `schedule_data` format + how the standard profile maps into it (read `main.py:1952-2113`,
`integration.py:300-430,1269-1330`, `idf_optimizer.py:570-624`).**
- `run_step8_paired_mc()`'s `schedules: dict = None` parameter (`main.py:1988`) is an EXISTING
  extensibility point, already used by `run_paired_mc.py --sched-dir`'s own preload
  (`Step8_docs/run_paired_mc.py:62-73`) to bypass the function's own CSV load (`main.py:2018-2027`) and
  hand it a pre-built dict instead. Shape required, one entry per `hh_id`:
  `{'metadata': {'hhsize': int, 'dtype': str, 'bedrm': int, 'condo': int, 'pr': str,
  'match_tier': str, 'equip_design_w': float, 'light_design_w': float}, 'Weekday': [24 entries],
  'Weekend': [24 entries]}`, each hourly entry `{'hour': 0-23, 'occ': fraction 0-1, 'met': Watts,
  'equip_frac': fraction 0-1, 'light_frac': fraction 0-1}` — read directly from `integration.py:323-430`
  (the `load_schedules()` docstring + its own CSV-row-to-entry parser body, not just the docstring).
- `hour` is 0-indexed and each entry covers `hour` to `hour+1`: `create_compact_schedule()`
  (`integration.py:550-589`) writes `Until: {hour+1:02d}:00` per entry, so index 0 of a 24-list is
  00:00-01:00. `load_standard_residential_schedules()` (`idf_optimizer.py:570-624`) returns
  `{'occupancy'|'equipment'|'lighting'|'dhw': {'Weekday':[24 vals],'Weekend':[24 vals]},
  'activity': <scalar Watts>}` in the SAME 0-indexed-hour, 0-1-fraction convention, so the mapping is a
  direct index-for-index substitution: `occupancy[h] -> occ`, `equipment[h] -> equip_frac`,
  `lighting[h] -> light_frac`, `activity` (one scalar, repeated 24x) `-> met`. `dhw` is not consumed
  anywhere in the single-building `inject_schedules()` path (confirmed by grep — no DHW hookup found,
  matches T16 Q4/Q5's own reading) — not used.
- Per-household `metadata` (incl. `equip_design_w`/`light_design_w`, the SHEU design levels) is kept
  UNCHANGED from the real `BEM_Schedules_2022.csv` row for that household — only the four hourly-value
  keys are swapped for the static profile. This is what the Design section's "SHEU design levels stay
  per household" requires, and it falls out for free from building the static dict on top of
  `integration.load_schedules()`'s own real-CSV output rather than constructing metadata from scratch.
- `inject_schedules(idf_path, output_path, hh_id, schedule_data, ...)` (`integration.py:1269-1305`) is
  called once per `(sample, year)` inside the loop at `main.py:2065-2070`; naming the synthetic year
  `'static'` makes that loop's own `f"Scenario_{y}.idf"` / `os.path.join(output_dir, sample_tag, y)`
  templating (`main.py:2061-2063`) produce exactly `Scenario_static.idf` under `.../sample_NNN_HHxxxx/
  static/`, matching the Design section's requested output name with no wrapper-side string formatting
  needed.
- Injected object names for check-only readback (grepped `integration.py`): occupancy schedule =
  `SCHEDULE:COMPACT` named `f"Occ_Sch_HH_{hh_id}"` (`integration.py:1411,1447-1448`); per-zone equipment
  = `ELECTRICEQUIPMENT` named `f"STEP9_Equip_{hh_id}_{zi}"`, `Design_Level` = `equip_design_w`
  (`integration.py:1616-1622`); per-zone lighting = `LIGHTS` named `f"STEP9_Lights_{hh_id}_{zi}"`,
  `Lighting_Level` = `light_design_w` (`integration.py:1707-1712`).

## Decisions
- **Delegate, don't hand-copy the loop.** Rather than reimplementing `run_step8_paired_mc()`'s ~80-line
  sample/inject/run/parse loop, `run_static_arm.py` calls that function directly with
  `years=['static']` and `schedules={'static': <static dict>}`. This reuses the tested
  sampling/injection/E+-run/hourly-parse/manifest-write code unedited (satisfies "No edits to pipeline
  source" more strongly than a hand-copy would) and gets `Scenario_static.idf` naming for free from the
  function's own year-templating. The Design section's phrase "replicates the per-sample loop... passing
  a static schedule_data dict" is satisfied by this call producing the same per-sample sequence of
  operations, not by a separate hand-written loop.
- **`--check-only` prints BOTH the n-sample and a separate seed-42 n=50 draw**, plus whether the
  n-sample is a prefix of the n=50 draw, using two independent `random.Random(same_seed)` instances (one
  `.sample()` call each) — this reproduces exactly what two separate `run_step8_paired_mc()` invocations
  with `--n 2` vs `--n 50` would each draw on their own, per the Smoke Acceptance section's requirement,
  without needing a second full run. Recorded as fact, not banded: Python's `random.Random.sample()` is
  not guaranteed to nest across different `n` (no `int` guaranteed prefix property), so the two draws may
  legitimately differ even though nothing is wrong.
- **Occupancy pool = 2022-only** (not the 2022∩2030 intersection the paired campaign's `years=` list
  would produce), per the Design section's explicit instruction; `build_static_schedules()` calls
  `integration.load_schedules()` on `BEM_Schedules_2022.csv` alone.
- **`--code-root` must be a T17-style staged tree** (`<root>/2J_docs_occ_nTemp/Step8_docs/
  eSim_bem_utils_2J/`, `<root>/BEM_Setup/WeatherFile/`, `<root>/2J_docs_occ_nTemp/BEM_setup/
  Buildings_MTL_v242/`) — `main.py`'s `BASE_DIR` is the 4th `dirname()` up from `main.py`'s own path and
  is NOT CLI-overridable (confirmed by T17's own reading, `main.py:38-39`).
- **FINDING (not fixed, routed around): `idf_optimizer.py:625`'s own `base_dir` inside
  `load_standard_residential_schedules()` is only the 2nd `dirname()` up from `idf_optimizer.py` itself
  (i.e. the `Step8_docs` level), NOT `main.py`'s 4-up `BASE_DIR` (the actual repo root).** It looks for
  `<Step8_docs>/0_BEM_Setup/Templates/schedule.json`, but the real file lives at `<repo root>/
  0_BEM_Setup/Templates/schedule.json` — confirmed missing at the 2-up path both on T17's staged tree
  (`ls` → No such file) and by `Glob` over the real local repo (no nested `2J_docs_occ_nTemp/**/
  0_BEM_Setup/` copy exists at all). **This means every call to this function anywhere in the pipeline
  — not just T19 — silently returns `_get_fallback_schedules()` (a hardcoded approximation), never the
  real DOE-MidRise/OpenStudio-Standards `schedule.json` profile the docstring and T16 Q5 both describe**,
  because `verbose` defaults to `False` so even the one warning line is suppressed by default. Did not
  edit `idf_optimizer.py` (forbidden). **Fix used: place a copy of `schedule.json`/`schedule_sf.json` at
  the exact (buggy) 2-up path inside a NEW, T19-owned code tree** (`T19/code/repo/2J_docs_occ_nTemp/
  Step8_docs/0_BEM_Setup/Templates/`) rather than T17's read-only one — this is staging a data file
  where existing, unedited code already looks for it, not a source edit. Flagging for the manager: this
  likely also silently affects the neighbourhood "Default"-arm path (T16 Q5) wherever it runs from the
  real repo layout — worth a fix ticket, out of scope for T19 itself. Practical consequence for this
  task: the smoke job's `--code-root` is `/speed-scratch/o_iseri/2J_revision/T19/code/repo` — a small
  (3.1 MB), T19-owned copy (code unmodified + 1 IDF + 1 EPW + the two schedule.json files placed at the
  buggy-but-unedited expected path), NOT T17's tree. `--sched-dir` still reuses T17's tree read-only for
  the one large file the Brief named.
- Smoke job runs BOTH stages (`--check-only` then the full n=2 run) inside ONE `sbatch` submission,
  stage 2 gated on stage 1's exit code, rather than two dependent jobs — simpler for a 2-run smoke where
  stage 1 takes seconds, matching "Submit and end your turn" (one JobID, not a dependency chain).

## Next
Employee (done): steps 1-4, job 1328296 submitted then cancelled (schedule.json fallback bug found),
corrected job **1328297** submitted (this is the live one). Collector (fresh agent, later): `sacct -j
1328297` for exit code/state (ignore `1328296` — cancelled, no output was ever trusted from it); if
`COMPLETED`, `scp` back the job's `.out`/`.err` from `T19/logs/` (small, safe to read directly) plus
`T19/out/_check_only/` and `T19/out/MidRise__Toronto_5A/cell_manifest.csv` +
`.../sample_*/static/hourly_meters.csv` (2 samples — small, safe). Check against the Smoke Acceptance
line at the top: exit 0; 2 runs with `hourly_meters.csv` 8760 rows; the printed n=2 vs n=50 draws and
the prefix statement (this employee turn only prints them, does not band the result); injected occupancy
values vs the REAL `schedule.json` (now confirm the check-only output does NOT contain a
"Warning: schedule.json not found" line -- that would mean the fallback bug still triggered somehow);
design levels differing between the 2 households. If `1328297` is not yet `COMPLETED`/`FAILED` in
`sacct`, do not wait — report state and stop (no-parking rule).

**Collector (2026-09-15, this turn) — COLLECTED.**
- `sacct -j 1328297` → `1328297` **COMPLETED**, ExitCode `0:0`, Elapsed `00:11:20`, MaxRSS
  ~1.17 GB (`.bat+` step). No `.ext+` anomaly.
- Actual remote layout differs from the Next-section guess: outputs land flat under
  `T19/out/` (`cell_manifest.csv`, `_check_only/`, `sample_001_HH125945/static/`,
  `sample_002_HH93952/static/`, plus a `SimResults_Plotting_Schedules/` plot dir) — there is
  no `T19/out/MidRise__Toronto_5A/` subfolder. Pulled the doc's own more specific list instead
  (logs `.out`/`.err`, `cell_manifest.csv`, both `hourly_meters.csv`, both `eplusout.err`, the
  check-only IDF) via individual `scp` (all exit 0, no >200 MB files encountered — largest per
  sample dir is `eplusout.sql` at ~41 MB, not pulled, listed only). Local copies under
  `impl/T19_out/logs/` and `impl/T19_out/out/`.
- **Smoke acceptance, checked against `t19_smoke_1328297.out` and the pulled files:**
  - exit 0: **PASS** — `sacct` ExitCode 0:0; log's own trailer `overall_exit=0`; `check-only
    exit: 0`; `full run exit: 0`.
  - 2 runs with `hourly_meters.csv` 8760 rows: **PASS** — `wc -l` on both pulled files = 8761
    (header + 8760), for `sample_001_HH125945` and `sample_002_HH93952`.
  - Both households produced outputs: **PASS** — log's own summary: `Successful: 2/2, Failed:
    0/2`; both `eplusout.err` tails end `EnergyPlus Completed Successfully -- ... 0 Severe
    Errors`; both sample dirs have a full E+ output set (audit/bnd/eio/eso/mtr/sql/eplustbl.*).
  - n=2 vs n=50 draw / prefix: **PASS (recorded, not banded)** — n=2 draw `['125945',
    '93952']`; n=50 draw's first two entries are the same two IDs in the same order; log
    states "n=2 draw is a prefix of the n=50 draw: True" with the correct caveat that
    `random.Random.sample()` nesting across `n` is not guaranteed in general.
  - Injected occupancy equals `schedule.json`: **PASS** — the log's own "Standard 'midrise'
    occupancy schedule, Weekday, hour 0-23" line (`1.000×7, 0.850, 0.390, 0.250×6, 0.300,
    0.520, 0.870×3, 1.000×3`) matches the `Occ_Sch_HH_125945` `Schedule:Compact` `Until:`
    values printed immediately after it, hour-for-hour, for both Weekdays and
    Weekends/Holidays/AllOtherDays blocks. `grep -i warning` on the full log found **no**
    "schedule.json not found" line — the T17-tree fallback bug the employee turn found and
    routed around did **not** trigger on this run.
  - Design levels differ between the 2 households: **PASS** — log: HH125945
    `equip_design_w=711.65` `light_design_w=133.78`; HH93952's injection block prints
    `carrier 996.8 W/zone` (equipment) and `135.0 W/zone` (lights) — both different from
    HH125945's values. Corroborated independently in the raw output data (not just the log):
    `hourly_meters.csv` hour-0 `InteriorEquipment:Electricity` is 44,120,241 J for HH125945 vs
    59,364,360 J for HH93952 — consistent with different equipment design levels. (Read via
    `head`/`wc -l` on the pulled CSVs; a pandas read was not needed since the difference is
    already visible in the first row and in the log's own printed values.)
- **Net: all 6 smoke-acceptance items PASS.** The one real defect this task surfaced was the
  `idf_optimizer.py` `base_dir` 2-up-vs-4-up mismatch (found and routed around by the employee
  turn, not by this collector) — flagged there as a fix ticket for the wider pipeline, out of
  scope for T19 itself.

## WHAT I DID NOT VERIFY
- Did not wait for or poll job 1328297; only the immediate post-submit `squeue` snapshot (state `R` on
  `magic-node-09`) was collected. No evidence yet that `--check-only` or the full run actually succeed,
  that `resolve_cell()` finds the staged MidRise IDF/Toronto EPW under `T19/code/repo`, that
  `eppy`/EnergyPlus import cleanly in the job's own environment, or that the injected occupancy/design-
  level values are numerically correct — that is the collector's job.
- Did not independently execute `build_static_schedules()`/`_check_only()` locally (cannot: no
  `eppy`/`numpy`/E+ locally per the task's own local-check constraint) — only `py_compile`-clean, and
  reasoned through against the read source, not run against a known-answer fixture.
- Did not re-verify that `resolve_cell()`'s `_find_one()` glob (`run_bem.py:34-50`) finds exactly the
  staged MidRise IDF and Toronto EPW under `T19/code/repo` at runtime -- only confirmed by `ls` that the
  files exist at the expected paths, not that eppy/glob actually resolves and opens them without error.
- Did not check disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T19/` before submitting.
- Found and routed around the `idf_optimizer.py` `base_dir` mismatch (see Decisions) by re-staging a
  small self-owned code tree with `schedule.json` at the path the unedited code actually looks for --
  did NOT verify this is the ONLY such path mismatch in the staged tree (e.g. did not check whether any
  other module under `eSim_bem_utils_2J/` has a similarly-idiosyncratic relative-path assumption beyond
  the ones T16/T17 already exercised: `config.py`'s `ENERGYPLUS_DIR`/`IDD_FILE`, `main.py`'s `BASE_DIR`,
  and now `idf_optimizer.py`'s `base_dir`).
- Did not re-run `--check-only` locally or on Speed myself before ending the turn (no-wait rule) -- the
  fix is reasoned from reading `idf_optimizer.py:624-726` plus confirming the file's presence/absence by
  `ls`, not from an actual successful run.

**Collector (2026-09-15) additions:**
- Did not pull or open any of the large E+ artefacts (`eplusout.sql` ~41 MB, `eplusout.eso`
  ~30 MB, `eplustbl.htm` ~7 MB, `eplusout.mtr`, `eplustbl.csv`, the `Scenario_static.idf` /
  `in.idf` copies, `Energy+.idd`) for either household — listed via remote `ls` only (sizes:
  see remote `ls -laR` output captured this turn), not opened. None individually exceeded the
  ~200 MB skip threshold, but they were not needed to check the six acceptance items and were
  left on Speed.
- Did not open the two `.png` schedule plots (`SimResults_Plotting_Schedules/`) or the
  check-only `Scenario_static_check_HH125945.idf` beyond confirming it was pulled — the log's
  own printed `Occ_Sch_HH_125945` `Schedule:Compact` field list was used for the occupancy
  check instead of re-parsing the IDF.
- Did not verify hourly-level numeric correctness of `hourly_meters.csv` beyond the header +
  first data row of each file (row count and one row spot-check) — did not scan all 8760 rows
  or run a full pandas read; no anomaly expected given the log's own clean-exit summary, but
  this was not exhaustively checked.
- Did not check `eplusout.err` warning counts for anything beyond the trailing summary line
  (42,561 / 83,591 Warnings, 0 Severe) — did not read the body of either `.err` file for
  specific warning content.
- Did not verify disk quota/free space on Speed, and did not check whether the `T17` staged
  tree (still referenced for `SCHED_DIR`) is still intact/unwritten — out of scope for this
  collection pass.
