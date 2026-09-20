# WP9 Stage 2: choose the simulated households before simulating (draw manifest + Gate 2)

Task doc:   this file (written by the manager, 2026-09-19, plan log (ae))
Status:     SUBMITTED
Model:      Sonnet employee. One task, one turn. Write the scripts, test them locally on tiny synthetic
            files, upload, submit ONE sbatch job, write state here, stop. Never wait on a job.

## Why

Fable report `IMP/investigate/inv_1J-01_REPORT_fable.md:410-420` (Stage 2). The April simulation picked
households inside `_run_mc_neighbourhood` (`conference_eSim/eSim/eSim_bem_utils/main.py:2088-2209`):
a base household per building from the 2005 pool's better half by "working-day score" (unseeded
`random.choice`, :2133), then in EVERY year the single best-scoring household of the same size and
dwelling type (`integration.find_best_match_household`, :2202, deterministic SSE against
`TARGET_WORKING_PROFILE`). So years got the most "working-like" household, not a random one, and draws
repeated. **Ruling B (author, 2026-09-19): each draw picks a random household from the same (dwelling type,
household size) group, with a fixed seed.** This task writes that sample to a file BEFORE any EnergyPlus
run, so it can be reviewed, reproduced and extended.

Do NOT edit any file under `conference_eSim/` or the staged code tree. This task only reads them. Changing
`main.py` to read the manifest is a later stage.

## Inputs (all on Speed; read headers with `head -1` only, on the login node)

Rebuilt grid files (Ruling A; plan log (x), (y), (ab), (ac), (ad)):
- 2005 `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv`
- 2010 `.../Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv`
- 2015 `.../Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv`
- 2022 `.../Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv`
- 2025 `/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv`
  (`...` = `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy`). Confirm each exists with `ls -l` first; if a
  name differs, use the real one and write it here.
- Control file (G2.0 seen failing): `/speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/reference/BEM_Schedules_2025_APRIL.csv`
  (household 71748 carries two dwelling types, plan log (ad)).
- Neighbourhoods: `/speed-scratch/o_iseri/1J_rerun/code/BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf`.
- Code to IMPORT (never edit): the staged tree `/speed-scratch/o_iseri/1J_rerun/code/eSim_bem_utils/`
  (`integration.load_schedules`, `integration.find_best_match_household`,
  `neighbourhood.get_building_dtypes_from_idf`). Record its md5 of `integration.py` and `neighbourhood.py`
  at job start and end.
- Python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (read only; never pip-install into it).

## Design (fixed by the manager; do not change it, write any doubt under Decisions)

- **Pool of a year:** `integration.load_schedules(grid_file, region='Quebec')` (the exact loader the
  simulation uses), THEN drop households whose `pr` metadata is blank (the loader keeps blank-PR rows,
  `integration.py` region filter), THEN keep only households with exactly 24 Weekday AND 24 Weekend
  entries. Print per year: loader count, blank-PR dropped, incomplete dropped, final pool size.
- **Strata:** (dtype, hhsize) from the household's metadata. Write `pool_summary.csv`
  (year, dtype, hhsize, n_households, mean_weekday_hours, sd_weekday_hours). Weekday hours = sum of the
  24 hourly `occ` values of the Weekday day; weekend hours likewise.
- **Buildings:** `get_building_dtypes_from_idf(NUS_RCk.idf)` gives each building's dwelling type, in IDF
  order. B(nu, d) = number of buildings of dtype d in neighbourhood nu.
- **Eligible sizes:** size s is eligible for (nu, d) if in EVERY one of the five years the (d, s) pool
  holds at least B(nu, d) households. If a building's dtype has no eligible size: no fallback; write
  `NOT_EVALUABLE: no eligible size for <nu> <d>` and skip that neighbourhood (G2.1 then reports it).
- **Size of each building in a draw (the stratum):** drawn with
  `rng_s = random.Random(f"20260919|{nu}|draw{k}|stratum")`, buildings in IDF order, from the eligible sizes
  with probabilities = mean over the five years of that year's share of size s among eligible-size
  households of dtype d (each year weighs the same). Use `rng_s.choices(sizes, weights)`.
- **Household of each building in each year:** `rng_y = random.Random(f"20260919|{nu}|draw{k}|{year}")`;
  buildings in IDF order; candidates = the (d, s) pool of that year, **sorted by household ID as text**,
  minus households already used in this (nu, draw, year); pick `rng_y.choice(candidates)`. No ranking, no
  "working-day" filter, no fallback. Seeding by text keys means adding draws 31+ or dropping a year never
  changes any other row.
- **Draws:** k = 1..30 for all six neighbourhoods (30 = the stopping rule's ceiling; Stage 4 uses them in
  blocks of 5).
- **Manifest** `/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv`, one row per
  (neighbourhood, draw, year, building): `seed, draw, neighbourhood, building_index, building_dtype,
  stratum_hhsize, year, hh_id, hh_dtype, hh_hhsize, hh_pr, weekday_hours, weekend_hours`. Sorted by
  neighbourhood, draw, year, building_index. Plus `manifest_inputs.txt`: md5 of the five grid files, the two
  code files and the six IDFs.

## Gate 2 (a separate script that reads only the files; every check prints its own line)

Each check prints `G2.x: PASS | FAIL | NOT_EVALUABLE -- <numbers>`; a check that crashes prints
NOT_EVALUABLE, never FAIL. Last line: `GATE2 SUMMARY: G2.0=.. G2.1=.. ...` keeping all three states. The
script exits 0 whenever it ran to the end; the verdict is in the lines, not the exit code (write this in
the script header).

- **G2.0 one label per household:** in each of the five grid files, count households whose HHSIZE, DTYPE
  or PR differ between their rows. PASS if 0 in every file. (Also answers the open R6 item for the rebuilt
  files; print the per-file counts.)
- **G2.1 right stratum, no fallback:** every (nu, draw, year, building) row present (expected count
  printed), `hh_dtype == building_dtype` and `hh_hhsize == stratum_hhsize` on every row, and no
  NOT_EVALUABLE neighbourhood.
- **G2.2 no reuse:** no household twice within one (nu, draw, year).
- **G2.3 distinct samples:** per neighbourhood, the number of distinct household sets over the 30 draws
  (a set = all (year, hh_id) of a draw) and of distinct stratum profiles. PASS if distinct household sets
  = 30 in every neighbourhood.
- **G2.4 not an accident of ranking:** per year, M = mean weekday hours over manifest rows; E = mean over
  rows of the row's stratum pool mean; SE = sqrt(sum over rows of the stratum pool variance) / n_rows;
  z = (M - E) / SE. PASS if |z| <= 3 in every year. Print M, E, z per year.
- **G2.5 reproducible:** build the manifest a second time and with `--draws 10`; PASS if the second full
  build has the same md5 and the 10-draw build equals the first 10 draws row for row.

**Seen failing first (required, recorded before the real verdicts are read):**
- Locally, on tiny synthetic files you write (a few households, one fake IDF building list): identical
  good case PASS; a duplicated household -> G2.2 FAIL; one row's `hh_hhsize` changed -> G2.1 FAIL; a
  household with two DTYPEs -> G2.0 FAIL; a missing input file -> NOT_EVALUABLE. Write each result here.
- On Speed, in the same job: **G2.0 on the April 2025 reference file must FAIL** (>= 1 household, 71748).
  **G2.4 and G2.3 on an "April rule" control manifest**: same strata and rows, but each household replaced
  by `integration.find_best_match_household(year_pool, candidates_minus_used)` (the April per-year rule).
  Expected: G2.3 FAIL (few distinct sets) and G2.4 FAIL on at least one year (best match pulls weekday
  hours toward the working profile). If the control does NOT fail, write that plainly: G2.4 then lacks power
  and the manager decides.

## Job

One script `wp9_2.sh` (tcsh, `#SBATCH -A chachemv -p ps -c 1 --mem=32G -t 7-00:00:00`, log
`/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_%j.out`): md5 start, build manifest, build twice more
(G2.5), build control, run Gate 2 on real and control, md5 end, `JOB DONE`. Local files go in
`IMP/impl/wp9_2/` (`wp9_2_manifest.py`, `wp9_2_gate2.py`, `wp9_2.sh`, synthetic tests); upload to
`/speed-scratch/o_iseri/1J_rerun/stage2/` and check md5 local = cluster. Never write under
`/speed-scratch/o_iseri/GSSCanada/`.

## Rules (verbatim, binding)

- "NEVER run blocking `srun` or any python on the login node (`speed-submit2`). ALWAYS `sbatch`." Allowed
  there: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file
  `tail`/`head`/`grep`/`wc -l`/`cat`. No `find`, no `du`.
- ssh: `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`; the login shell is tcsh (no `2>/dev/null`,
  no awk `$` inside ssh strings).
- Locally use `py`, never `python`. Never open a multi-MB CSV locally (memory is short).
- Do not wait for the job. Submit, write the job ID and log path under Ledger, stop.

## Ledger

- **job 1339951** · `wp9_2.sh` · submitted 2026-09-19 · state at submission: RUNNING
  (`squeue -j 1339951` -> `R`, node `speed-32`) · log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_1339951.out` · runs, in order: real
  manifest (household-rule random, 30 draws) -> repeat build -> `--draws 10` build ->
  April-rule control manifest (30 draws) -> Gate 2 on real (all 6 checks) -> Gate 2 on
  control (G2.1-G2.4 only) -> Gate 2 on the April 2025 reference file alone (G2.0 only)
  -> md5 end. Never polled after submission (rule: employee never waits).

## Verified

- Cluster inputs confirmed with `ls -l` on the login node (all present, sizes/dates
  sane): the 5 grid files (91-119 MB each, `Sep 19` timestamps), the April 2025
  reference file (64 MB), the 6 `NUS_RC{1..6}.idf` files (2-10 MB), and
  `/speed-scratch/o_iseri/1J_rerun/code/eSim_bem_utils/{integration.py,neighbourhood.py,
  __init__.py}`. Names matched the doc exactly; nothing needed correcting.
  `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` exists (symlink -> `python3`).
- `/speed-scratch/o_iseri/1J_rerun/stage2/` did not exist before this task; created by
  the upload itself (`scp -r`), never by a bare `mkdir` on the login node.
- Upload integrity: `cat`'d each of the 3 uploaded files back from the cluster over
  ssh and diffed byte-for-byte against the local copies -- all 3 IDENTICAL. Local
  `md5sum` (git-bash, not the cluster) of the 3 files: `wp9_2_manifest.py`
  `84ca0cdabda72a5f7a59b34c49a236ee`, `wp9_2_gate2.py` `6f97c7c1f62ce363d3c9e2bbd445fe7d`,
  `wp9_2.sh` `7827eaab52b29e866e17a60fa193bb23`. No `md5sum` was run on the login node
  (not on its allowed list); the byte-for-byte `cat`+`diff` round trip is the substitute.
- **Local seen-failing-first tests** (tiny synthetic fixtures built by
  `wp9_2/tests/make_synth.py`: 7 households, 3 dtype/hhsize strata, one 3-building
  synthetic IDF `NUS_TINY1` with 2 SingleD + 1 MidRise; code imported, unmodified, from
  the real local `1J_docs_occ/conference_eSim/eSim/eSim_bem_utils/` -- eppy is installed
  locally so the real import chain runs, giving a higher-fidelity test than a stub):
  1. **Identical good case**: manifest + pool_summary built (`--draws 5`), Gate 2 run
     with all inputs incl. a repeat build and a `--draws 3` build -> **G2.0=PASS
     G2.1=PASS G2.2=PASS G2.3=PASS G2.4=PASS G2.5=PASS**.
  2. **Duplicated household** (one row's `hh_id` forced to collide with another row in
     the same neighbourhood/draw/year group) -> **G2.2=FAIL** (`duplicate_instances=1`),
     all other checks unaffected -- isolated the fault correctly.
  3. **One row's `hh_hhsize` changed** (+1) -> **G2.1=FAIL** (`hhsize_mismatches=1`).
  4. **A household with two DTYPEs** (one grid CSV, one household's Weekend rows given
     a different DTYPE than its Weekday rows) -> **G2.0=FAIL** (`total_multi_label_
     households=1`).
  5. **Missing input file** (`--manifest` pointed at a nonexistent path) -> **all six
     checks print NOT_EVALUABLE**, script still exits 0. Also checked the manifest
     builder itself on a missing grid file: it prints `FATAL:` and exits 2 (a hard
     arg/input error, not a gate, so it does not owe the NOT_EVALUABLE convention).
  6. Bonus smoke test (not on the required list): built the April-rule control manifest
     locally (`--household-rule april`, `--draws 3`) and gated it -- **G2.3=FAIL**
     (`distinct_household_sets=1` of 3), matching the doc's expectation for the April
     rule. G2.4 did NOT fail on this fixture because every synthetic household in a
     stratum has identical hours (zero within-stratum variance) -- a property of the
     tiny fixture, not evidence either way about the real 2025 data; the doc's own
     fallback applies ("G2.4 then lacks power and the manager decides").
  - One real bug found and fixed during (1): `wp9_2_gate2.py`'s independent G2.1
    recount crashed (`TypeError: '<' not supported between instances of 'str' and
    'int'`) because `pool_summary.csv`, read back from disk, has every field as a
    string, while `wp9_2_manifest.py`'s in-memory build path has real ints -- fixed by
    casting `n_households` to `int` in `pool_counts_by_key()` (`wp9_2_manifest.py`).
    Re-ran after the fix: all six checks PASS on the good case.

## Decisions

- **`seed` column**: not specified exactly by the design. Used the full seed string
  consumed by `rng_y` for that row's household draw
  (`f"{seed_date}|{nu}|draw{k}|{year}"`) rather than just the date prefix, so every row
  carries its own reproduction key.
- **`sd_weekday_hours`**: sample standard deviation (`statistics.stdev`, ddof=1), 0.0
  when a stratum has fewer than 2 households. Not specified by the design; smallest
  reasonable choice.
- **G2.1 independence**: rather than trusting the manifest's own row counts, Gate 2
  re-derives each neighbourhood's building dtypes/counts from the IDFs and re-derives
  eligibility from `pool_summary.csv`'s counts, importing the eligibility arithmetic
  from `wp9_2_manifest.py` (same directory) instead of writing it a second time, so the
  two copies of that formula cannot silently drift apart. This surfaced the str/int bug
  above.
- **Output layout**: `draw_manifest.csv`, `pool_summary.csv`, `manifest_inputs.txt`
  land flat directly under `/speed-scratch/o_iseri/1J_rerun/stage2/` (no subfolder),
  matching the exact path the Design section names. The repeat/`--draws 10`/control
  builds use descriptive suffixes (`_repeat`, `_draws10`, `_control`) in the same flat
  directory, since the doc does not name those files itself.
- **Control manifest draw count**: built at the same 30 draws as the real manifest
  (not some smaller number) to keep it a true apples-to-apples "same strata and rows"
  comparison per the doc's stated intent, even though the doc does not restate the
  draw count for the control build specifically.
- **`stage2/` directory creation**: no bare `mkdir` on the login node. Created it by
  `scp -r`-ing a local staging folder with only the 3 final files (no `tests/`) so the
  remote directory came into existence as a byproduct of the upload -- the same
  workaround already on record at `2026-09-19_WP9_stage1c_2025.md:565`.

## Next

- Job 1339951 is running/queued; nobody has read its output yet. Next agent: `tail` or
  `grep` (single-file, allowed on the login node)
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_1339951.out` for three `GATE2
  SUMMARY:` lines (real, control, April-reference-alone) plus the `JOB DONE` line and
  the start/end `md5sum` pairs for `integration.py`/`neighbourhood.py` (must match).
- If the REAL manifest's G2.0/G2.1/G2.2/G2.5 are anything but PASS, or if any
  neighbourhood printed `NOT_EVALUABLE: no eligible size for ...`, that is a real
  finding to record, not an expected control result.
- If the April-reference-alone run's G2.0 is NOT FAIL, that contradicts plan log (ad)
  (household 71748) and needs investigating before trusting G2.0 on anything else.
- This task doc does not authorize reading the manifest into main.py or running
  EnergyPlus -- that is explicitly the next stage, not this one.

## WHAT I DID NOT VERIFY

- The job was not watched to completion (rule: employee never waits) -- none of
  G2.0-G2.5's real verdicts on the true grid/IDF data are known yet, only the tiny
  synthetic verdicts above.
- Did not verify runtime/memory behaviour of the 4 real-data manifest builds (each
  reloads all 5 ~100 MB grid files via `integration.load_schedules`) against the
  6 real `NUS_RC{1..6}.idf` files' actual building counts -- only tested against a
  3-building synthetic IDF and 7-household synthetic pools.
- Did not check whether every real neighbourhood/dtype combination has an eligible
  size in all 5 years -- whether any of the 6 real neighbourhoods comes back
  NOT_EVALUABLE is unknown until the log is read.
- Did not confirm G2.4 has statistical power to catch the April rule's bias on the
  REAL data (only confirmed, on tiny synthetic data, that G2.3 catches it and that
  G2.4 has a documented no-power fallback path).
- Did not independently confirm that `/speed-scratch/o_iseri/GSSCanada/venv/bin/python`
  has every transitive import `integration.py` needs (`eppy`, `idf_optimizer`,
  `schedule_generator`, `schedule_visualizer`, `config`) -- relied on the task doc's
  designation of that venv plus an import-chain guard in `wp9_2.sh` Step 1 that exits
  10 with `IMPORT CHAIN: FAILED` if it does not import cleanly.
- Did not md5-compare the 6 real IDFs or 5 real grid files against any prior baseline
  (none exists -- `manifest_inputs.txt`, written by this job, IS the first recording).
