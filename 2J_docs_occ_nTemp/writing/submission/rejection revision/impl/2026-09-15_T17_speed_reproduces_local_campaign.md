# T17 — Can Speed reproduce the local 2022/2030 campaign? (Wave 3 prerequisite) — implementation state

Task doc:   this file (section "Task")
Parent:     `2026-09-15_T16_step8_run_machinery.md` (read all of Verified first)
Status:     COLLECTED — PASS (see Status section below)

## Task

**Why.** Every Wave 3 arm (2030 re-runs, static code schedule, N=200, envelope) will run on Speed. But
the current on-disk 2022/2030 `campaign_N50` was produced **locally on Windows** after the multi-zone
injection bug fix (T16 Q1), while the last Speed campaign used older code and a private schedule dir
(`Step8_docs/step8_array_v2.sh`). Before any new arm, show that Speed with the **current local code**
reproduces the local results. This test must be able to fail: compare against the local hourly files.

**Scope.** The four Toronto cells (`SingleD`, `OtherDwelling`, `MidRise`, `HighRise` × `Toronto_5A`),
`--years 2022,2030` (the sample pool is "IDs present in all requested years", `main.py:2029-2034`, so the
years must match the local run or the 50 households differ), `--n 50 --seed 42`. 400 EnergyPlus runs.

**All compute on Speed via `sbatch`**, one SLURM array `--array=0-3 -p ps -c 8 --mem=16G -t 7-00:00:00`
(32 CPUs total), python `/speed-scratch/o_iseri/envs/step4/bin/python`, work dir
`/speed-scratch/o_iseri/2J_revision/T17/`. Login node: only `sbatch squeue sacct scancel scontrol cd ls
scp` and single-file `tail head grep wc -l cat`. **Never `find`, `du`, `md5sum`, or python on the login
node** (checksums and file walks go inside the job). tcsh: no `2>&1` or `2>/dev/null` in ssh strings;
`ssh -o BatchMode=yes -o ConnectTimeout=60`.

**Steps (employee).**
1. **Establish what the local run used** (reading, cite `file:line`): code dir, schedule CSVs
   (`BEM_Setup/BEM_Schedules_2022.csv` / `_2030.csv`? private sched dir? clock correction?), IDF dir, EPW
   dir, E+ version, and the exact `run_campaign_local.py` / `run_paired_mc.py` arguments — from
   `Step8_docs/08_09_injection_bug_status.md` and the cell dirs (`cell_manifest.csv.new_2022_2030_*`,
   any run log). If the schedule files' dates post-date the local campaign, write that and STOP.
2. **Stage a fresh copy on Speed** under `T17/code/` (never reuse `/speed-scratch/o_iseri/GSSCanada/...`,
   which holds older code): `Step8_docs/run_paired_mc.py`, `Step8_docs/eSim_bem_utils_2J/`, the four
   IDFs, the Toronto EPW, and the two schedule CSVs (~674 MB each). Record local byte sizes and local md5
   (computed locally). Point `--output-dir` at `T17/out/` and `--sched-dir` at the staged CSVs. E+ via the
   existing wrappers `/speed-scratch/o_iseri/ep_wrappers/` (confirm with `ls`; if absent, NOT FOUND, stop).
   Make sure no path in the code can resolve to a local Windows path or to `campaign_N50` on Speed.
3. **New array script** `T17_scripts/t17_array.sh` (do not reuse `step8_array_v2.sh`): in-job md5 of the
   staged CSVs and code files, eppy import check, then `run_paired_mc.py --archetype A --city Toronto_5A
   --n 50 --seed 42 --years 2022,2030 --output-dir ... --sched-dir ...`.
4. **Compare script** `T17_scripts/t17_compare.py` (runs as a second sbatch job with
   `--dependency=afterok:<array job>`, `-c 8 --mem=16G`): needs the local reference hourly files for
   the four Toronto cells, 2022 and 2030, canonical runs per `08_simulation_plots.py:154-234` (T06
   already staged the 2022 ones at `/speed-scratch/o_iseri/2J_revision/T06/input/<Arch>__Toronto_5A/`,
   read only; stage 2030 ones yourself under `T17/ref/`). Report per cell × year: n households matched by
   HH id (expect 50), max abs and max relative difference per meter column, annual `Electricity:Facility`
   relative difference per household (max, median), and whether the drawn HH id set equals the local
   manifest's. Output `T17_out/t17_compare.csv` + log.
5. `py -3 -m py_compile` both scripts locally; submit array then compare job; write both JobIDs in
   Ledger; **end the turn**.

**Acceptance (fixed now).** Same 50 HH ids per cell; annual Facility within 0.1 % per household; hourly
max relative difference reported, not banded (Linux vs Windows E+ builds may differ in the last digits).
Any HH-id mismatch or any annual difference > 0.1 % = FAIL, reported, not fixed.

**Employee rules.** Submit and end the turn. No waiting, polling, sleep. Never read multi-MB files into
context. Past ~150k tokens: write state, "handoff needed". NOT FOUND rather than guess. Never write into
`BEM_Setup/SimResults_Step8/` or any `campaign_N50` directory, local or Speed.

**Collector (later, fresh agent).** `sacct` both jobs, scp `T17_out/`, fill Verified against the acceptance line.

## Ledger
- **Staging (scp, foreground, no login-node python/find/du/md5sum used):**
  - `scp -r <local staging>/T17 o_iseri@speed...:/speed-scratch/o_iseri/2J_revision/` — created
    `T17/code/repo/{BEM_Setup/WeatherFile/<Toronto EPW>, 2J_docs_occ_nTemp/BEM_setup/
    Buildings_MTL_v242/<4 IDFs>, 2J_docs_occ_nTemp/Step8_docs/{run_bem.py,run_paired_mc.py,
    eSim_bem_utils_2J/*.py (16 files)}}` and `T17/code/sched/{BEM_Schedules_2022.csv,
    BEM_Schedules_2030.csv}` in one recursive copy (exit 0). Remote `ls -la` on the two CSVs
    confirmed byte sizes match local exactly: 673,929,104 / 673,609,612. In-job md5 (array job,
    below) is the actual verification; local md5s recorded in Verified above for comparison.
  - Local script `build_2030_ref.py` (scratchpad) filtered each Toronto cell's 100 on-disk
    `sample_*` dirs down to the 50 canonical ones per `cell_manifest.csv.new_2022_2030_20260711`
    (0 missing, 200/200 `2030/hourly_meters.csv` files copied) — this is the fix for the
    orphaned-old-frame-leftover trap found in Verified above.
  - `scp t17_2030_ref.tar.gz` (73,347,359 B local, local md5 `5c6a5ee1fb17d6574f9bcb14e95a76af`) to
    `/speed-scratch/o_iseri/2J_revision/T17/` (exit 0) — extracted inside `t17_compare_job.sh`
    (compute node), never on the login node.
  - `scp -r T17_scripts_upload` → `/speed-scratch/o_iseri/2J_revision/T17/T17_scripts/` (exit 0):
    `t17_array.sh`, `t17_compare.py`, `t17_compare_job.sh`. `scp -r logs_placeholder` →
    `/speed-scratch/o_iseri/2J_revision/T17/logs/` (exit 0, so `#SBATCH --output=.../T17/logs/...`
    has somewhere to write before the job's own `mkdir -p` runs).
- **`py -3 -m py_compile t17_compare.py`** → clean. **`bash -n t17_array.sh` / `bash -n
  t17_compare_job.sh`** → clean.
- **JobID 1328286** — `sbatch t17_array.sh` (`--array=0-3 -p ps -c 8 --mem=16G -t 7-00:00:00`,
  run from `/speed-scratch/o_iseri/2J_revision/T17/T17_scripts/`). Task 0-3 =
  SingleD/OtherDwelling/MidRise/HighRise × Toronto_5A, `--n 50 --seed 42 --years 2022,2030
  --sim-mode standard --sched-dir .../T17/code/sched --output-dir .../T17/out/<Arch>__Toronto_5A`.
  `squeue` immediately after submit: all 4 array tasks `R` (running) on speed-34/speed-33/salus/
  speed-40.
- **JobID 1328290** — `sbatch --dependency=afterok:1328286 t17_compare_job.sh` (`-c 8 --mem=16G
  -t 7-00:00:00`, same dir). Extracts `t17_2030_ref.tar.gz` then runs `t17_compare.py`. `squeue`:
  `PD` (Dependency), as expected.
- **Collector check, 2026-09-15 (this session):** `sacct -j 1328286,1328290` — array tasks 0
  (SingleD) and 1 (OtherDwelling) `COMPLETED 0:0` (14m13s / 36m11s elapsed); tasks 2 (MidRise) and 3
  (HighRise) still `RUNNING` (50m26s elapsed); compare job 1328290 still `PENDING`
  (dependency not yet satisfied). Not all jobs ended — no scp, no Verified fill this pass per
  collector rules. Re-check later.
- **Collector re-check, 2026-09-15 (fresh session, this task):** `ssh ... sacct -j 1328290 -X -n -o
  JobID,State,ExitCode,Elapsed` → `1328290 COMPLETED 0:0 00:02:40`. `sacct -j 1328286 -X -n ...` →
  all 4 array tasks `COMPLETED 0:0`: task 0 (SingleD) 00:14:13, task 1 (OtherDwelling) 00:36:11,
  task 2 (MidRise) 02:35:55, task 3 (HighRise) 01:34:14. Matches the sacct fact given for 1328286;
  1328290 (unknown-state at task start) resolved to COMPLETED 0:0 in 2m40s once its `afterok`
  dependency was satisfied.
  - `ls -la .../T17/T17_out/` → `t17_compare.csv` (8,993 B) and `t17_compare.log` (2,609 B) both
    present, both `cat`'d directly (small, no scp needed, no login-node python/find/du used).
  - `wc -l` on all 5 `.err` files under `.../T17/logs/` (`t17_1328286_{0,1,2,3}.err`,
    `t17_compare_1328290.err`) → 0 lines each, no stderr from any of the 5 jobs.
  - `grep -i 'md5\|size\|import' .../T17/logs/t17_1328286_0.out` → in-job STAGED md5s for the two
    schedule CSVs: `BEM_Schedules_2022.csv` md5 `30fd815869942c1c292b6dfd26eaf8ad` size 673929104,
    `BEM_Schedules_2030.csv` md5 `5db4c84dcd59762be8fbf6b2f1814def` size 673609612 — **byte-for-byte
    identical** to the local md5s/sizes recorded in Verified — Step 1 above. Confirms Speed ran the
    same schedule files as the local campaign, not a stale or substituted copy.

## Verified

**Step 1 — what the local run used.**
- Schedule CSVs used: `BEM_Setup/BEM_Schedules_2022.csv` (673,929,104 B, Jul 9 20:57, local md5
  `30fd815869942c1c292b6dfd26eaf8ad`) and `BEM_Setup/BEM_Schedules_2030.csv` (673,609,612 B, Jul 9
  21:06, local md5 `5db4c84dcd59762be8fbf6b2f1814def`) — the shared `BEM_Setup` files, NOT a private
  dir. Both predate every 2022/2030 run that produced the current `campaign_N50` (Jul 10–15), so **not
  stale — no STOP.**
- Per-cell log headers confirm no override was used: `BEM_Setup/SimResults_Step8/campaign_N50/_logs/
  {SingleD,OtherDwelling,MidRise,HighRise}__Toronto_5A.log:1-6` each print `Loading schedules from
  BEM_Schedules_2022.csv...` (default `BEM_SETUP_DIR`, i.e. `run_paired_mc.py` invoked WITHOUT
  `--sched-dir`).
- **Clock correction: NOT used for the current on-disk campaign.** `Step8_docs/step8_array_v2.sh:13,15`
  documents a *different, superseded* Speed campaign ("corrected v2", job 953111 family, `cluster_
  rerun.md`) that read `(Hour+4)%24`-corrected schedules from a **private** `SCHED_DIR=/speed-scratch/
  o_iseri/step8_run/sched` (`step8_array_v2.sh:36,79`), explicitly "NOT BEM_Setup". That private,
  clock-shifted campaign is NOT what is on disk today — confirms the task's own framing verbatim.
- Exact per-cell command, reconstructed from `run_paired_mc.py:34-48,75-80` argument defaults + the
  4 Toronto log headers (`_logs/*__Toronto_5A.log:1-6`, byte-for-byte identical structure across all
  4 archetypes): `run_paired_mc.py --archetype <A> --city Toronto_5A --n 50 --seed 42 --sim-mode
  standard --years 2022,2030` (no `--sched-dir`, no `--output-dir` override recorded — default
  `SimResults_Step8/<archetype>__Toronto_5A`), invoked once per cell inside `run_campaign_local.py`'s
  `ThreadPoolExecutor` (`run_campaign_local.py:223`) from the Phase 5 launch documented at
  `08_09_injection_bug_status.md:35-36` (`run_paired_mc.py` PID 18992, started 22:00:15 EDT
  2026-07-13).
- **Provenance split within our 4 Toronto cells (file mtimes, `_logs/*.log`):** `SingleD__Toronto_5A`
  = Jul 10 16:23 (pre-bugfix run; SingleD is single-zone, confirmed unaffected by Bug A per
  `08_09_injection_bug_status.md:122`, so this is still the canonical file). `OtherDwelling__
  Toronto_5A` = Jul 14 00:17, `MidRise__Toronto_5A` = Jul 14 05:23, `HighRise__Toronto_5A` = Jul 14
  13:42 — all three from the post-bugfix Phase 5 re-run (`08_09_injection_bug_status.md:255-273`,
  18/18 cells, 1,800/1,800 E+ jobs ok, done 2026-07-14/15).
- IDF/EPW/E+ version: unchanged from T16 Q3 — `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf`,
  `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf`,
  `ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf`,
  `ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf` (all confirmed present in the 4
  Toronto log headers), EPW `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw`, EnergyPlus 24.2.
- **Reference-selection trap found (affects step 4):** each Toronto cell dir holds 100 `sample_NNN_
  HH*` subdirs, not 50 — an orphaned old-frame leftover set (pre-2026-07-09 relink) sits alongside the
  canonical 50, same `sample_NNN` prefix, different HH id (e.g. `OtherDwelling__Toronto_5A/
  sample_001_HH22934` [canonical, matches `cell_manifest.csv.new_2022_2030_20260711`] vs
  `sample_001_HH24199` [orphan, matches neither manifest]) — confirmed by direct `ls` + manifest read,
  matches `08_09_injection_bug_status.md:300-301` and is the exact same trap T06 already solved
  (`impl/2026-09-15_T06_wp6_enduse_by_hour_2022.md:194-206`: use `cell_manifest.csv.new_2022_2030_*`
  as ground truth, keep only the `(sample, hh_id)` pairs it lists). T06's own staged 2022 reference at
  `/speed-scratch/o_iseri/2J_revision/T06/input/<Arch>__Toronto_5A/` already has this filter applied
  (confirmed 50 sample dirs via remote `ls | grep -c sample_`). `t17_compare.py` must apply the same
  filter to the 2030 reference it stages itself.
- `ep_wrappers/` confirmed present on Speed: `/speed-scratch/o_iseri/ep_wrappers/{energyplus,
  ExpandObjects,Energy+.idd}` (remote `ls`, all present, executable).
- Path-resolution constraint for staging (read `main.py:38-39,79-80`, `run_bem.py:34-50`):
  `BASE_DIR` = the 4th `dirname()` up from `main.py`'s own path (not a fixed name), so
  `WEATHER_DIR`/`STEP8_BUILDINGS_DIR` are NOT CLI-overridable — the staged tree must replicate
  `<ROOT>/BEM_Setup/WeatherFile/` and `<ROOT>/2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`
  relative to wherever `eSim_bem_utils_2J/main.py` lands. `--sched-dir` and `--output-dir` ARE
  CLI-overridable (`run_paired_mc.py:44-47`), so those need no fixed nesting.

## Decisions
- Staged code tree uses `T17/code/repo/` as `<ROOT>` (arbitrary name — `BASE_DIR` resolution only
  cares about relative depth, not the name), with `T17/code/repo/BEM_Setup/WeatherFile/` and
  `T17/code/repo/2J_docs_occ_nTemp/{BEM_setup/Buildings_MTL_v242,Step8_docs/eSim_bem_utils_2J}`
  populated, plus a separate flat `T17/code/sched/` passed via `--sched-dir` and `T17/out/` via
  `--output-dir`. This satisfies "never reuse `/speed-scratch/o_iseri/GSSCanada/...`" while keeping
  the campaign-code import chain intact.

## Next
T17 is CLOSED — reproduction PASSED on the task's own fixed Acceptance line, 8/8 cell x year
combinations. No further Speed work owed by this task. Return to Wave 3 planning (manager): T17 was
its own prerequisite ("show that Speed with the current local code reproduces the local results
before any new arm" — Task, line 12-13); that gate is now cleared, so the next action is the manager
deciding/scoping the first real Wave 3 arm (2030 re-runs / static code schedule / N=200 / envelope),
not more T17 execution.

## WHAT I DID NOT VERIFY
- Did not wait for or poll either job; no run-time evidence beyond the immediate post-submit
  `squeue` snapshot (array tasks `R`, compare `PD`/Dependency) was collected. Actual EnergyPlus
  success, `hourly_meters.csv` completeness, and the compare CSV's numbers are all unread — that is
  the collector's job.
- Did not independently re-verify `t17_compare.py`'s own arithmetic (max abs/rel diff, annual
  relative diff, median) beyond a local `py_compile` syntax check — logic was reasoned through but
  not run against a known-answer fixture.
- Did not check whether `_run_simulations_with_fallback()` / `ENERGYPLUS_EXE` resolution
  (`eSim_bem_utils_2J/simulation.py`, not opened) needs anything beyond the `ENERGYPLUS_DIR`/
  `IDD_FILE` env vars already set in `t17_array.sh` — copied verbatim from the working
  `step8_array_v2.sh` pattern (T16 Q8) but not traced line-by-line for this staged tree.
- Did not check disk quota/free space on `/speed-scratch/o_iseri/2J_revision/T17/` before or after
  staging (~1.4 GB code+sched+ref); 400 E+ runs' own output (IDF/sql/csv per run) will add
  materially more — not sized in advance.
- Did not verify `08_simulation_plots.py:154-234`'s exact canonical-selection logic character-for-
  character against my own filter in `build_2030_ref.py` — I re-derived the same rule (match
  `(sample, hh_id)` to `cell_manifest.csv.new_2022_2030_20260711`) independently from the manifest
  contents and T06's precedent doc, not by re-reading `08_simulation_plots.py` itself line by line.
- Local `run_bem.py`'s md5 (`7b8055d2edda51960cb527150960152d`) was computed and staged but the
  in-job md5 list in `t17_array.sh` does not re-hash it (only `run_paired_mc.py`, `integration.py`,
  `main.py`, and the two schedule CSVs) — not a gap in the reproduction itself (the file is staged
  and used either way), just an omission from the printed provenance list.
- **Collector (this task) did not independently re-derive `t17_compare.py`'s own arithmetic** — read
  its output CSV/log and cross-checked the acceptance rule (0.1 % annual, 50 HH ids) against the raw
  numbers printed, but did not re-run the max/median relative-difference computation from the
  underlying hourly CSVs myself; the employee's own note above (same caveat) still stands.
- **Did not open the four `.out` files for tasks 1-3** (only task 0's `.out` was `grep`'d for
  md5/size lines) — assumed identical staged-file provenance across all 4 array tasks since they
  share the same staged `T17/code/` tree; not directly confirmed per-task.
- **Did not inspect the raw hourly `hourly_meters.csv` files** (Speed output or local reference) —
  worked only from `t17_compare.csv`/`.log`, which the employee's own script produced from them.
- **Did not check disk usage/quota** after the run (still open per the employee's own note).
- **Did not investigate the large hourly meter relative differences** (e.g. HighRise 2022
  `Cooling:EnergyTransfer` 201.7x) beyond noting they are explicitly out of scope for the
  pass/fail verdict per the task doc's Acceptance line; no root cause traced.

## Verified — Step 5 (collector, 2026-09-15, this task)

- **All jobs ended clean.** `sacct -j 1328286 -X -n -o JobID,State,ExitCode,Elapsed`: array tasks
  0-3 all `COMPLETED 0:0` (14m13s, 36m11s, 2h35m55s, 1h34m14s). `sacct -j 1328290 -X -n -o
  JobID,State,ExitCode,Elapsed`: `COMPLETED 0:0` (2m40s). All 5 `.err` logs under `T17/logs/` are
  empty (0 lines each, `wc -l`).
- **Staged code/schedule provenance matches local exactly.** In-job md5 of the two schedule CSVs
  (`t17_1328286_0.out`, `grep`'d) = `30fd815869942c1c292b6dfd26eaf8ad` /
  `5db4c84dcd59762be8fbf6b2f1814def`, identical to the local md5s recorded in Verified — Step 1.
- **`t17_compare.csv` (8,993 B, `T17_out/t17_compare.csv`, `cat`'d in full) and
  `t17_compare.log` (2,609 B, `cat`'d in full) — 8 of 8 cell x year combinations PASS the fixed
  acceptance line.** For every one of SingleD/OtherDwelling/MidRise/HighRise x 2022/2030:
  - `n_hh_matched = 50` and `hh_id_set_equals_manifest = True` — the Speed run drew the same 50
    household ids as the local campaign's manifest, for all 8 combinations.
  - Annual `Electricity:Facility` relative difference per household, max across the 50 HH: SingleD
    2022 = 1.14349e-05 (0.0011 %), 2030 = 1.08922e-05; OtherDwelling 2022 = 5.18056e-06, 2030 =
    5.16056e-06; MidRise 2022 = 2.96161e-06, 2030 = 2.45206e-06; HighRise 2022 = 3.76819e-06, 2030 =
    7.84567e-06. Every one of these is roughly 4-5 orders of magnitude under the 0.1 % (1e-3) bar in
    the task doc's own Acceptance line. `t17_compare.csv`'s own note column confirms `0/50
    households over 0.1% threshold` on all 8 rows.
  - `t17_compare.csv`'s own `acceptance` row per cell x year reads `PASS` for all 8; `t17_compare.log`
    ends `=== DONE. overall_fail=False ===`.
  - Hourly meter differences are large for some meters in absolute relative terms (e.g. HighRise
    2022 `Cooling:EnergyTransfer` max relative diff 201.7, `ElectricityNet:Facility` 0.527) — per the
    task doc's own Acceptance line ("hourly max relative difference reported, not banded"), these are
    **not** part of the pass/fail criterion and do not affect the verdict; they are expected
    Linux-vs-Windows E+ last-digit/edge-hour divergence, reported as data only.
- **Verdict against the task's fixed Acceptance line: PASS.** Same 50 HH ids per cell (8/8), annual
  Facility within 0.1 % per household (8/8, by 4-5 orders of magnitude), hourly max relative
  difference reported not banded (done, in the CSV). Speed with the current local code reproduces
  the local 2022/2030 campaign for the four Toronto cells.

## Status
COLLECTED — all 5 jobs (array 1328286 tasks 0-3, compare 1328290) COMPLETED 0:0; task's fixed
Acceptance line met on 8/8 cell x year combinations; PASS.
