# T69 -- WP6 Part B: end use x hour on the three scenario arms -- implementation state

Task doc: `impl/2026-09-21_T69_wp6_partB_scenarios.md`
Status:   **DONE -- ACCEPTED by manager 2026-09-21.** See "Manager collection" section at the end.

## Ledger

- **JobID `1341180`** -- `enduse_hour_scenarios.py` (all three scenario arms + the
  cross-scenario common-basis file, one job, sequential over arms). Submitted from
  `speed-submit2` via:
  `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00 --wrap '/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T69/T69_scripts/enduse_hour_scenarios.py > /speed-scratch/o_iseri/2J_revision/T69/logs/t69_run.out'`
  Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python` (same symlink T68 used, confirmed
  present via `ls -la` before submission, not executed on the login node).
  CPU budget check before submission: `squeue -u o_iseri --format='%i %j %t %C'` returned only
  `histnu` rows -- 0 of the 2J project's 32-CPU ceiling was in use before this job's 8 CPUs were
  requested.
  Single `squeue -j 1341180` check immediately after submission: `R` (running), node `speed-21`,
  0:01 elapsed -- not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T69/`):
  - `logs/t69_run.out` -- stdout/stderr of the whole job
  - `out/S-None/`, `out/S-Partial/`, `out/S-Revert-std/` -- each with `enduse_annual.csv`,
    `enduse_hourly_profile.csv`, `grid_metrics.csv`, `closure.csv`,
    `enduse_change_2022_2030.csv` (leading `scenario` column), `controls.json`, `run_meta.json`
  - `out/cross_scenario_common_basis.csv` -- the ruling-1 household-count table (4 singleton +
    6 pairwise + 1 four-way rows over {S-Full, S-None, S-Partial, S-Revert-std})

  **No number in these files has been read yet by this employee.** A failed job stays in this
  ledger with the line that supersedes it -- it is never dropped.

## Verified (numbers actually read, with source)

- **Directory-listing facts confirmed by `ssh` on 2026-09-21, before writing the script** (all
  single-file/`ls`/`cat` commands, allowed on the login node):
  - `find .../T29/out/lambda_0.0/ -name hourly_meters.csv | wc -l` = **1198**
  - `find .../T29/out/lambda_0.5/ -name hourly_meters.csv | wc -l` = **1200**
  - `find .../T32/step8_std/out/ -name hourly_meters.csv | wc -l` = **1199** (verified myself,
    per the task doc's instruction not to assume the number in its own text) -- one short, and
    `cat` on `OtherDwelling__Vancouver_5C/undelivered.csv` under `T32/step8_std/out/` confirms the
    missing household is sample 9 / HH129937, the SAME household item 33 already named for T29.
  - `find .../T21/out/step8/ -name hourly_meters.csv -path '*2022*' | wc -l` = **1200** (the
    common 2022 baseline, unchanged from T68).
  - `cell_manifest.csv` schema (`sample,sim_hh_id,hhsize,dtype,pr`) confirmed byte-identical
    across T21/T29-lambda0.0/T32-step8_std via `head -3` on all three.
  - `hourly_meters.csv` header confirmed identical across all four trees (same 10 columns,
    `hour` first, `Electricity:Facility` etc.) via `head -1`.
  - `undelivered.csv` for `SingleD__Toronto_5A` (the hand-check cell) is header-only (0 data
    rows) in all three scenario trees -- confirms `sample_001_HH32811` was not itself dropped
    anywhere before it was chosen as the hand-check household.
  - `sample_001_HH32811/2030/hourly_meters.csv` confirmed present in all three scenario trees,
    and its T21 `2022` counterpart confirmed present, via `ls` on each path individually.
- **Three independent hand-check references computed OFF-CLUSTER** (ruling 4): the real
  `sample_001_HH32811/SingleD__Toronto_5A/2030/hourly_meters.csv` file was `scp`'d down from each
  of the three scenario trees and read with a standalone `csv.DictReader` accumulation (never
  pandas, never this script's own vectorized code path -- see `hand_compute.py`, uploaded
  alongside the main script for provenance):
  - S-None: annual Electricity:Facility = **8174.604015 kWh**, peak = **5.638904 kW**
  - S-Partial: annual = **8166.934610 kWh**, peak = **5.501438 kW**
  - S-Revert-std: annual = **8101.741952 kWh**, peak = **5.404708 kW**
  These three numbers are hardcoded into `SCENARIOS` in the uploaded script and are what the
  real job's C2 control compares against (tolerance: relative diff < 5e-6, i.e. agreement
  through the 6th significant figure, per the task doc's "at least 6 significant figures").
- **`py_compile` clean** (`py -3.13 -m py_compile enduse_hour_scenarios.py`), twice (before and
  after the undelivered-sweep key-name fix found during the local test, see Decisions).
- **Local functional test against a synthetic tree**, run sequentially (not via `Pool`, same
  Windows-multiprocessing-avoidance reason T68 documented), engineered with:
  - 4 real paired households (2 SingleD__Toronto_5A, 2 HighRise__Kelowna_5B) present in T21's
    2022 tree AND all three scenario 2030 trees.
  - 1 orphan household (`HH99999`, 2030-only) planted in the S-None tree with NO T21 2022
    counterpart, to test ruling 2's "log every miss" requirement.
  - 1 household (`HH55555`) present in T21's 2022 tree only (no 2030 subfolder anywhere), to test
    that `discover_paired_household_set()` correctly EXCLUDES it from the S-Full reference set.
  - 1 engineered non-empty `undelivered.csv` row (HighRise cell, S-Partial arm only), to test that
    `sweep_undelivered()` actually parses row content, not just file presence.
  Results:
  - `discover_runs_scenario()`: S-None found 8 runs (4 pairs) + exactly 1 skip, logged by name
    (`HH99999`, reason = T21 2022 missing) -- **not silently dropped**. S-Partial and
    S-Revert-std: 8 runs, 0 skips.
  - `discover_paired_household_set()`: S-Full set = the 4 real households; `HH55555` correctly
    absent (asserted).
  - **All four controls (C1-C4) fired (`ran_and_fired`) on all three arms** -- `controls_all_fired
    = True` for S-None, S-Partial, and S-Revert-std, all asserted, not eyeballed.
  - `sweep_undelivered()`: S-Partial's HighRise cell shows `n_total_undelivered_rows=1`
    (the engineered row); S-None and S-Revert-std show `0` -- matches construction exactly.
  - `enduse_change_2022_2030.csv`'s leading column is `scenario`, uniformly set to the arm's own
    name, for all three arms (asserted).
  - `cross_scenario_common_basis.csv`: 11 rows (4 singleton + 6 pairwise + 1 four-way), the
    four-way intersection = 4 (all synthetic households, since none of the four sets differ in
    this small test), and S-None's own singleton count = 4, NOT 5 -- confirms the orphan
    household never leaks into the change table, the household-set, or the cross-scenario file.
  - A benign `scipy` `RuntimeWarning` ("invalid value encountered in multiply") fired ~120 times
    during the run, traced to `stats.t.interval` being called with `scale=0` -- an artifact of
    this synthetic test's Heating/Cooling/Water columns being set to IDENTICAL constants across
    every household and year (a shortcut in the synthetic-data generator, not a script bug); the
    two paired values are then exactly equal, giving zero variance. Confirmed this does not
    affect any assertion, output file, or control outcome. Not expected to recur on real data
    (real households will not have byte-identical thermal loads).

## Decisions (things the task doc did not decide, and what was assumed)

1. **C2 is a pure per-arm hand-check, with no aggregate-CSV reproduction step**, unlike T68's C2
   (which also reproduced T67's 2400-row `agg_annual.csv`). Ruling 4 states plainly that neither
   T67's `agg_annual.csv` nor T29's `p3_deltas.csv` cover these metrics on this basis, and the
   latter is explicitly not-to-be-trusted -- so there is no known-good aggregate file to
   reproduce for these three trees. Flagging this explicitly in case the manager wants a
   different "seen-working" check added at collection.
2. **midday_share/load_factor stock-weighted rows are NOT reused from any prior file** for these
   scenario arms (unlike T68, which read T67's `ci_reproduction_t67.csv` verbatim per ruling 6).
   That file only ever scored the T68/S-Full rebuild -- there is no equivalent already-scored
   file for S-None/S-Partial/S-Revert-std. Ruling 6 only forbids re-deriving what T67 ALREADY
   scored; it says nothing about metrics T67 never touched for these trees. So
   `build_change_table()` computes these two shape metrics' stock-weighted rows fresh, via the
   SAME `stock_weighted_cluster_bootstrap()` function (unchanged, T68's accepted one), applied to
   grid-metric DELTAS instead of percent changes. Every such row's `ci_method` field says in
   plain text that this is NEW, not a T67 reuse, so nobody downstream mistakes it for a T67
   number. **Flagging this as a decision the manager should rule on explicitly** -- it is the one
   place this script's behaviour diverges from "T67's numbers, never recomputed" without an
   explicit ruling covering it.
3. **The household set used for `S-Full` in `cross_scenario_common_basis.csv` is built by a
   directory-existence-only pass** (`discover_paired_household_set()`, a new, small function) --
   it does NOT read T68's own CSVs (particularly its 511 MB `enduse_hourly_profile.csv`) and does
   NOT recompute any of T68's statistics, per ruling 6's "for reference only, do not recompute
   it". This is a literal directory walk checking that both `2022/hourly_meters.csv` and
   `2030/hourly_meters.csv` exist for a given household name under T21's own tree -- the exact
   same check `discover_runs_scenario()` does for each scenario arm, just applied to T21 against
   itself.
4. **Only pairwise and four-way combinations are in `cross_scenario_common_basis.csv`** (7 rows),
   plus 4 singleton rows for convenience (11 rows total) -- no three-way combinations. Ruling 1's
   second sentence literally says "every pairwise and four-way combination", not three-way; three-
   way combinations were left out to match the literal ask. **Flagging this as a decision the
   manager should confirm** -- if a manuscript figure needs, say, "S-None vs S-Partial vs
   S-Revert-std, excluding S-Full", a three-way row would need to be added.
5. **The hand-check household is `sample_001_HH32811` / `SingleD__Toronto_5A` in ALL THREE
   arms** -- confirmed present and undropped in all three trees before being hardcoded (see
   Verified). Using the SAME household name across arms (rather than three different households)
   was chosen so that C1's clock-shift math and C2's hand-check both exercise the identical
   dwelling/divisor combination (SingleD, divisor 1.0 everywhere) across arms, for the cleanest
   possible cross-arm comparison of the control outputs at collection.
6. **Did not concatenate this task's three arms with T68's own `enduse_change_2022_2030.csv`**
   (which is implicitly `scenario = S-Full`) into one WP11-ready file -- ruling 6 explicitly
   reserves that decision for the manager at collection.
7. **A bug was found and fixed during the local functional test**: the first draft of
   `sweep_undelivered()`'s return dict used the key `n_total_rows`; my OWN test harness (not the
   main script) was written against the wrong key name and crashed with `KeyError`. On inspection
   the main script's actual key was always `n_total_undelivered_rows` (correct, matches the
   docstring) -- the bug was in the test harness, not the shipped script. Fixed the test harness
   and re-ran; all assertions passed. Flagging for transparency, since this looked like a script
   bug at first glance and it is worth a second look at collection to confirm `run_meta.json`'s
   real key really is `n_total_undelivered_rows`.

## Next

- Collection: read `run_meta.json`'s `controls_all_fired` FIRST for all three arms, then
  `controls.json` (especially C2's `hand_check_annual_rel_diff` / `hand_check_peak_rel_diff` --
  should be far below the 5e-6 threshold, per the local test's floating-point-noise-only
  experience with T68), then the results, in that fixed order.
- Read `discover_skipped_sample` in each arm's `run_meta.json` -- ruling 2 says this should be
  empty (all scenario households should trace back to a T21 2022 pair); if it is NOT empty on the
  real data, that is a real finding, not an engineering artifact.
- Read `n_paired_households_own_basis` per arm against the directory counts already confirmed
  above (S-None should land at 1198, S-Partial at 1200, S-Revert-std at 1199, MINUS any genuine
  T21-side misses ruling 2 says should not happen).
- Read `cross_scenario_common_basis.csv`'s four-way row -- this is the number WP11 most likely
  needs first for any figure comparing all three scenarios against the main rebuild.
- Decide on decisions 1, 2, and 4 above (C2's scope, the new non-T67-reuse bootstrap for
  midday_share/load_factor, and whether a three-way combination row is needed).
- Once accepted, WP11 (figures) can consume `T69/out/*/enduse_change_2022_2030.csv` and
  `T69/out/cross_scenario_common_basis.csv` directly; T68's own file remains ungrouped
  (`scenario=S-Full` only implicit, per decision 6) until the manager rules on concatenation.

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341180`) on the real T29/T32 data.**
  Everything in `## Verified` above about the script's correctness comes from directory listings,
  three off-cluster hand-check computations, and a synthetic local test -- not from the real
  run's output. `controls.json`, `run_meta.json`, and all CSVs under `T69/out/` for all three arms
  are unread as of writing this doc.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue.
  T68's equivalent single-arm job (2,400 household-years) finished in under 2 minutes; this job
  processes three arms of roughly the same size each (2,396 / 2,400 / 2,398 household-years) in
  one sequential job, so ~3x T68's real workload -- expected to still finish in well under 10
  minutes, but this is an expectation, not a measurement of THIS job.
- Whether `discover_skipped` is actually empty on the real data for all three arms (the task doc
  says it should be, "should not happen", but explicitly says "check, do not assume") -- this is
  precisely what the real run's `run_meta.json` will show and this employee has not read it.
- Whether any cell/meter combination in the real data hits the zero-variance
  `RuntimeWarning` seen in the synthetic test for a genuine (not engineering-shortcut) reason --
  unlikely given the real data's known variability, but not measured.
- Whether the two divisor dictionaries (`T66_CELL_EQUIP_DIVISOR`, `T66_CELL_LIGHT_DIVISOR`,
  copied verbatim from T68, itself copied verbatim from T66) still have full 24-key coverage
  against these THREE scenario trees' own cell directory names -- not re-checked here, since
  ruling 2/3 give no reason to expect the cell-naming convention differs from T21's, and T68's own
  collection already confirmed full coverage against T21's 24 cells. If any of the three scenario
  trees is missing a cell T21 has (or has an extra one), this would show up as a `NOT_EVALUABLE`
  divisor status in that arm's `enduse_annual.csv`, unread as of this writing.

## Manager collection (2026-09-21)

Job `1341180` COMPLETED (`sacct`: 00:03:23 elapsed, exit 0:0, all three steps). Collected in the
fixed order (`run_meta.json`'s `controls_all_fired` -> `controls.json` -> results) for all three
arms independently -- not just the employee's self-report.

- **`controls_all_fired = true`** for S-None, S-Partial, S-Revert-std, read directly from each
  arm's `run_meta.json`.
- **C2 hand-check, independently cross-checked against the employee's own hardcoded numbers**:
  matched to 6+ significant figures, actual relative diffs measured at 4.9e-11 (S-None annual),
  1.3e-11 (S-Partial annual), 1.4e-12 (S-Revert-std annual), all peak-kW diffs ~5e-8 -- floating-
  point noise only, nowhere near the 5e-6 tolerance.
- **C3 divisor invariance**: max abs pct diff ~1e-14 for all three arms (machine precision, as
  expected for a true identity).
- **Household counts match items 30/33 exactly**: S-None=1198, S-Partial=1200, S-Revert-std=1199,
  read from `n_paired_households_own_basis`, not assumed.
- **`n_discover_skipped = 0` and `discover_skipped_sample = []`** for all three arms -- every
  scenario household traced back to a T21 2022 pair, as ruling 2 required.
- **`cross_scenario_common_basis.csv`** (11 rows) matches the run log exactly: S-Full=1200,
  S-None=1198, S-Partial=1200, S-Revert-std=1199, four-way intersection=1198.
- **S-Revert-std's one undelivered household is `OtherDwelling__Vancouver_5C` sample 9 /
  `HH129937`** -- the SAME household item 33 already identified as shared between the two
  reversion-style arms. Confirms, does not contradict, prior findings.
- **Zero `NaN`/`inf` in any of the three `enduse_change_2022_2030.csv` files** (grepped directly).
- **The scipy `RuntimeWarning` seen in the real job's log (144 occurrences) is the same
  zero-variance artifact the employee already diagnosed in its synthetic test** (`stats.t.interval`
  called with `scale=0`), confirmed benign: no NaN/inf reached any output file.

**Decisions on the four flagged items:**
1. C2 pure per-arm hand-check (no aggregate-CSV reuse) -- **correct as specified**, matches
   ruling 4 (T67/T29 aggregates untrusted here).
2. `midday_share`/`load_factor` as a NEW bootstrap computation, not a T67 reuse -- **correct**,
   T67 never scored these three trees.
3. No three-way combinations in `cross_scenario_common_basis.csv` -- **matches ruling 1's literal
   text** ("every pairwise and four-way combination"); leave as built. Add a three-way row only if
   a specific WP11 figure needs one.
4. **T68 (S-Full) concatenation with T69's three arms: APPROVED.** Schema is confirmed identical
   (T68's `enduse_change_2022_2030.csv` columns plus `scenario`), verified by direct inspection of
   `T69/out/S-None/enduse_change_2022_2030.csv`'s header. WP11's figure-generation script may
   `pd.concat` the four files directly (T68's own file treated as `scenario=S-Full`, per its own
   implicit convention) -- no separate merge task needed.

**Verdict: T69 ACCEPTED, full controls-first verification complete. WP6 (Parts A + B) is now
CLOSED.** WP11 (figures) is unblocked and next on the critical path.
