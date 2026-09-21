# T87 — energy-use intensity (EUI) from the current simulations — task doc + implementation state

Task doc:   this file. Plan log (ed). Author approved the job 2026-09-21 ("yes run the job").
Status:     DONE (manager scored and applied, plan log (ef)); job 1341459 COMPLETED 0:0
Agent:      fresh Sonnet employee. Cluster via sbatch only. No new simulations. No web.

## Goal
Fill the manuscript's `[NUMBER NEEDED: EUI]` (Section 3.3) with EUI values computed from the simulations
already on Speed: total site energy per conditioned floor area, kWh per m2 per year, per archetype, 2022
and 2030 (main scenario), plus the end-use split on the same basis. This is READ AND DIVIDE only.

## Where the data is
- Main paired 2022/2030 tree (the one every Results number uses):
  `/speed-scratch/o_iseri/2J_revision/T21/out/step8/<Arch>__<City>/sample_NNN_HH<id>/<year>/`
  (known to hold `hourly_meters.csv`; T68 read it).
- Method precedent: `2026-09-15_T07_wp7_eui_gap_by_enduse.md` computed EUI from each run's `eplustbl.csv`
  ("End Uses" table, stopping before "End Uses By Subcategory"; floor area = conditioned floor area,
  summed across households, as in the old Table 5). Its script is under `T07_scripts/` or `T07_out/`
  locally if present; reuse its parsing logic, and read that doc's Verified section first.
- Cross-check source: `/speed-scratch/o_iseri/2J_revision/T67/out/agg_annual.csv` (annual kWh per
  household and year).

## Step 0 (STOP rule, do first)
From the login node, `ls` ONE run directory for each archetype (4 `ls` calls). If `eplustbl.csv` (or an
`eplusout.sql`) with the End Uses and Building Area tables is NOT kept in the T21 tree, STOP: write what
files exist into Verified, set Status BLOCKED, end the turn. Never re-run EnergyPlus.

## What the script computes (one sbatch job)
1. For every household run, year 2022 and 2030, in the T21 tree: total site energy (kWh), the End Uses
   table by category (heating, cooling, interior lighting, interior equipment, fans, water systems,
   other; all fuels), and Net Conditioned Building Area (m2), all read from that run's own table.
2. Output `out/eui_per_run.csv`: arch, city, sample, hh_id, year, area_m2, site_kWh, one column per end
   use, eui_kWh_m2.
3. Output `out/eui_by_archetype.csv`: arch, year, n_runs, EUI = sum(site_kWh)/sum(area_m2) over all
   cities and households (same basis as the old Table 5), plus each end use on the same basis, plus the
   per-city version in `out/eui_by_arch_city.csv`.
4. Internal check per file: sum of end-use categories equals the table's own Total End Uses row (within
   0.1 %). Report count passing.
5. Cross-check: each run's site_kWh against the matching household-year row in T67 `agg_annual.csv`
   (same meaning of total; if column meanings differ, say so, do not force a match). Report the
   largest relative difference.

## Controls (in the same job; each outcome one of ran_and_fired / ran_not_fired / not_evaluable_crashed)
- C1 seen failing: a copy of one `eplustbl.csv` with its area set to zero in a scratch dir must be
  flagged, never divided.
- C2 seen failing: a copy with one end-use value changed by 10 % must fail the internal check in step 4.
- C3 coverage: count of runs found vs expected (4 archetypes x 6 cities x 50 households x 2 years = 2,400);
  any missing run listed by name, and every `undelivered.csv` in the tree read and its rows listed.
Write `out/controls.json` and `out/run_meta.json` with a `controls_all_fired` boolean.

## Cluster rules
`sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 --wrap '/speed-scratch/o_iseri/envs/step4/bin/python
/speed-scratch/o_iseri/2J_revision/T87/T87_scripts/t87_eui.py > /speed-scratch/o_iseri/2J_revision/T87/logs/t87_run.out'`
Never run python on the login node. Login shell is tcsh. Syntax-check the script locally
(`py -m py_compile`) before upload. Submit, write the JobID in the Ledger, end the turn. Do not wait
or poll.

## Must not
- No number from this job goes into the manuscript until the manager has scored the controls.
- Never compare against or copy the old Table 5 values. Do not rescale anything toward the SHEU survey.

## Ledger

- **Step 0 (STOP rule) checked first, did not fire.** `ls` on `speed-submit2` of one 2022 run dir per
  archetype confirmed `eplustbl.csv` is present in the T21 tree for all four archetypes, both years
  (spot-checked SingleD/MidRise/OtherDwelling/HighRise at `Montreal_6A`, 2022 AND 2030 for the other
  three): `eplustbl.csv` exists next to `hourly_meters.csv` in every `<sample>/<year>/` dir checked.
  `grep -n` on one file (`SingleD__Montreal_6A/sample_001_HH130228/2022/eplustbl.csv`, single-file,
  allowed) confirmed it has a "End Uses" section (line 47) and a "Building Area" section (line 39,
  `Net Conditioned Building Area` present) — the two tables this task needs. **Status is NOT BLOCKED,
  proceeding.**
- **Local, no cluster.** Downloaded `T07_scripts/eui_enduse_by_run.py` (`scp`) and read it in full —
  reused its `_area()`/`_end_uses()` parsing logic verbatim (function bodies copied, renamed
  `parse_area_m2`/`parse_end_uses`) in the new script. Confirmed by direct inspection (`sed -n`) that
  T21's `eplustbl.csv` has the SAME two-"End Uses"-sections structure V4-B4 defect 1 warns about (a
  second "End Uses" section further down belongs to "Demand End Use Components Summary", peak kBtuh,
  not annual energy) — T07's stop-at-first-"End Uses By Subcategory"-and-break logic is the correct
  guard here too, reused unmodified.
- **Local, no cluster.** Wrote `T87_scripts/t87_eui.py` (7-category split per this task's own step 1:
  heating, cooling, interior_lighting, interior_equipment, fans, water_systems, other — NOT T07's
  5-category SHEU split, which folds fans into "appliances"; this task doc asks for fans separately).
- **Local functional test against two REAL downloaded `eplustbl.csv` files**
  (`SingleD__Montreal_6A/sample_001_HH130228/2022` and `HighRise__Montreal_6A/sample_001_HH106602/2022`,
  via `scp`, real Python 3.13 via the `py` launcher): `process_file()` on SingleD reproduced a
  hand-calculation done independently from the raw table rows (`site_kWh` 26885.1319 vs hand-calc
  26885.1319 from `(28030.11+63705.79)*0.293071`; `area_m2` 220.8397 vs hand-calc `2377.10*0.092903`)
  to full precision; internal check (sum of 7 buckets vs the table's own "Total End Uses" row) passed
  at 1.09e-05 % diff (SingleD) and 4.86e-04 % diff (HighRise), both far inside the 0.1 % tolerance.
  Control C1 (area zeroed in a scratch copy) fired: `area_ok=False`, `eui_kWh_m2=None`, never divided.
  Control C2 (Cooling value +10 % in a scratch copy) fired: internal check failed at 0.60 % diff (well
  past 0.1 %).
- **Local end-to-end pipeline test** on a synthetic tree shaped like T21's (2 archetypes x 2 cities x
  3 households x 2 years = 24 expected runs, all path constants monkey-patched off the cluster, one
  run's `eplustbl.csv` deliberately deleted, one `undelivered.csv` planted, a fake `T67/agg_annual.csv`
  with the REAL (no-total-column) schema): `discover_runs` found 23/24, correctly listed the 1 missing
  run by name; the `undelivered.csv` sweep found exactly the 1 planted row; `eui_by_archetype.csv` had
  4 rows with `n_runs` correctly reflecting the deletion (5, not 6, for `SingleD 2030`);
  `eui_by_arch_city.csv` had 8 rows; `eui_per_run.csv` had 23 rows (only discovered runs written); all
  three controls fired (`controls_all_fired: true`); the T67 cross-check correctly reported
  `NOT_POSSIBLE` (see Decisions). `py -m py_compile t87_eui.py` also run clean before and after these
  tests.
- **Staged and uploaded via `scp -r`** (never edited in place; a local `upload/` dir with
  `T87_scripts/t87_eui.py` and `logs/.keep` was built locally then `scp -r`'d in one call to
  `/speed-scratch/o_iseri/2J_revision/T87/`, which also creates the two remote directories — `mkdir`
  itself was never run on the login node). Remote `ls -la` confirmed `t87_eui.py` landed at exactly
  29398 bytes, matching the local file byte-for-byte.
- CPU budget check before submission: `squeue -u o_iseri --format='%i %j %t %C'` on `speed-submit2`
  showed only `histnu` array-job rows (a different project, per standing rule) and six 1-CPU
  `wp10_stage4_*` jobs (1J project, not 2J) running/pending — the 2J project's 32-CPU ceiling was
  unused before this job's 4 CPUs were requested.
- **JobID `1341459`** — `t87_eui.py`, submitted from `speed-submit2` via:
  `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 --wrap '/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T87/T87_scripts/t87_eui.py > /speed-scratch/o_iseri/2J_revision/T87/logs/t87_run.out'`
  Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python` (symlink to `python3.10`, confirmed via
  `ls -la` before submission, not executed on the login node).
  Single `squeue -j 1341459` check immediately after submission (not polled further, per the
  no-parking rule): `R` (running), node `antenna1`, 0:02 elapsed.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T87/`):
  - `logs/t87_run.out` — stdout of the whole job (progress lines + `DONE` if it completes, traceback
    if it fails)
  - `out/eui_per_run.csv` — one row per household x year: arch, city, sample, hh_id, year, path,
    status, error, area_m2, site_kWh, 7 end-use `*_kWh` columns, eui_kWh_m2, internal_check_pass,
    internal_check_diff_pct, unit
  - `out/eui_by_archetype.csv` — arch, year, n_runs, sum_area_m2, sum_site_kWh, EUI_kWh_m2, 7 end-use
    `*_kWh_m2` columns (pooled: sum(kWh)/sum(area) over all cities+households, same basis as old
    Table 5's method, never its values)
  - `out/eui_by_arch_city.csv` — same, per (arch, city, year)
  - `out/controls.json` — C1/C2/C3, each `outcome` in `{ran_and_fired, ran_not_fired,
    not_evaluable_crashed}`, plus `controls_all_fired`
  - `out/run_meta.json` — discovery/processing counts, the full missing-run list, the `undelivered.csv`
    sweep (files + rows), the internal-check pass count, and the T67 cross-check result/reason

  **No number from this job has been read yet by this employee.** A failed run stays in this ledger
  with the line that supersedes it — it is never dropped.

## Verified

- Step 0: `eplustbl.csv` present for all 4 archetypes, both years, in the T21 tree (see Ledger) — the
  STOP rule does not fire.
- `eplustbl.csv`'s "End Uses" table structure, units (`kBtu`, all fuels), and 14-column layout (13
  energy columns + Water last) confirmed identical to what T07's script expects, by direct read of a
  real T21-tree file (`sed -n` on the login node, single-file, allowed) and by two real-file
  functional-test reproductions matching independent hand-calculations to full precision (see Ledger).
- `T67`'s `out/agg_annual.csv` on the T21 tree has header `arch,city,sim_hh_id,year,midday_share,
  load_factor` (`head -3` on the login node) — **no annual total-kWh column exists**, matching T68's
  2026-09-20 finding. This is why step 5's cross-check could not be attempted as literally worded
  ("say so, do not force a match" — see Decisions).
- `cell_manifest.csv` row counts (`wc -l`, single-file) confirm 50 households per cell (51 lines incl.
  header) for the two cells checked — matches the 4 x 6 x 50 x 2 = 2,400 expected total.
- CPU budget and directory-creation-via-`scp -r` both confirmed by direct `ls -la`/`squeue` reads
  (see Ledger); no login-node rule violated (`mkdir`/`python`/`find` never invoked there).

## Decisions

1. **Step 5's T67 cross-check is reported as `NOT_POSSIBLE`, not attempted as a numeric comparison.**
   The task doc's own parenthetical description of `T67/out/agg_annual.csv` ("annual kWh per household
   and year") does not match that file's actual schema on the T21 tree, which carries only
   `midday_share`/`load_factor` — no annual total-kWh column of any kind, let alone one on the same
   physical basis as this task's `site_kWh` (all-fuel `eplustbl.csv` "End Uses" total). This is a
   stronger case than "column meanings differ" — there is no candidate column to compare at all — so
   the script reads the file, prints its real header, and writes `NOT_POSSIBLE` with the reason, rather
   than inventing a comparison. Not treated as a control failure; C1–C3 do not depend on this file.
2. **No per-dwelling-unit divisor is applied anywhere in this task**, unlike T68's end-use-by-hour
   work. EUI here divides a run's OWN whole-building energy (`site_kWh`, from that run's own
   `eplustbl.csv`) by that SAME run's OWN whole-building conditioned floor area (`area_m2`, from the
   same file) — both numerator and denominator carry an identical, if any, per-dwelling multiplier, so
   it cancels exactly. T65/T66's divisor concern is specific to *absolute per-dwelling* kWh, which this
   task never reports.
3. **`site_kWh` (the "total site energy" the task asks for) is read directly from the table's own
   "Total End Uses" row**, not recomputed as a sum of the 7 buckets — the 7-bucket sum is instead
   compared AGAINST that row as the task's own step-4 internal check. This keeps the check genuinely
   independent-in-arithmetic-path (two different reads of the same table, not one value compared with
   itself) rather than circular.
4. **7-category split, not T07's 5-category SHEU split** — this task's own step 1 lists heating,
   cooling, interior lighting, interior equipment, fans, water systems, other; T07's older split folded
   fans into "appliances". Followed this task doc literally; the "other" bucket here = exterior
   lighting + exterior equipment + pumps + heat rejection + humidification + heat recovery +
   refrigeration + generators.
5. **C3's "fired" outcome means the coverage-count and `undelivered.csv`-sweep code ran to completion
   without crashing and recorded both counts** — it does not itself assert 2,400/2,400 coverage; the
   actual found/missing counts are separate facts in `controls.json`/`run_meta.json` for the manager to
   read. C3 is a coverage/diagnostic control, not a seen-failing-first control like C1/C2, so there was
   no fake case to engineer it to fail on first.
6. **Never compared any number to the old Table 5 or V4-B4 values** (per Must-not) — the local
   functional test's real single-file EUI numbers (SingleD 2022 ≈ 121.74 kWh/m², HighRise 2022 ≈ 80.97
   kWh/m²) are reported here only as evidence the parser reproduces a hand-calculation from the same
   file, not as any form of plausibility check against prior campaign numbers.

## Next

- Job `1341459` is running on the cluster; nothing further for this employee to do. Manager collects:
  `sacct -j 1341459` for exit status, then `out/run_meta.json`'s `controls_all_fired` boolean first,
  then `out/controls.json` for each of C1/C2/C3's own outcome (not just the summary boolean), then the
  coverage numbers (found vs 2,400, missing-run list, undelivered.csv sweep) before trusting any
  `eui_by_archetype.csv` number. **No number from this job may enter the manuscript until that scoring
  is done (per Must-not).**

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341459`) on the real T21 data.** Everything in
  `## Verified` above comes from two real single-file downloads and a synthetic 24-run local pipeline
  test, not from the real 2,400-run job's output — `controls.json`, `run_meta.json`, and all five
  output files under `out/` are unread as of writing this doc.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue — 2,400
  files (roughly double T07's 1,200-file, 38-second job, same per-file parse cost) with 4 CPUs is
  expected to finish in well under a minute of real work, by direct analogy to T07's own timing, but
  this is an expectation, not a measurement of this job.
- Whether every one of the 2,400 expected runs is actually present on the real tree, or whether any
  `undelivered.csv` exists anywhere under the real T21 tree — Step 0 only spot-checked 4 sample
  directories (one per archetype); full coverage is exactly what `run_meta.json`'s `C3_coverage` and
  `undelivered_csv_sweep` fields exist to answer, and they are unread.
- Whether the internal check (sum of 7 buckets vs the table's own "Total End Uses" row) passes at
  ≤0.1 % on all 2,400 real files, or on some subset it does not — only 2 real files were checked by
  hand, both passed well inside tolerance, but this is not evidence about the other 2,398.
- Whether any archetype/city/year combination has an eplustbl.csv with a genuinely different unit
  (e.g. `GJ` instead of `kBtu`) than the 3 real files inspected (all `kBtu`/`ft2`) — the parser handles
  `GJ`, `kBtu`, `Btu`, `MJ`, `kWh`, and raises a clear `ValueError` (recorded as a per-file FAIL, not a
  crash of the whole job) on anything else, but this was not exercised against a real GJ/SI-unit file
  from this specific tree.
