# T22 — WP3 static code-schedule arm: full run, 24 cells × 50 households (Speed) — implementation state

Task doc:   this file. Design + wrapper: `2026-09-15_T19_wp3_static_arm_build_smoke.md` (smoke passed all 6
checks, job 1328297). Cell list and staged assets: `2026-09-15_T17_speed_reproduces_local_campaign.md`.
Status:     SUBMITTED

## Design (manager, fixed before run)
- Same wrapper `T19/T19_scripts/run_static_arm.py`, unchanged, full-run mode, `--n 50 --seed 42`, for every
  archetype × city cell of the published campaign (24 cells; take the exact list from T17/T16, do not invent).
- Household sample and SHEU design levels from the **current** `BEM_Schedules_2022.csv` (T17 staged copy,
  read only). Manager decision: run now, do not wait for the 2022 rebuild. The rebuild keeps the same census
  households; T18's collector later confirms that the household ID set and `equip_design_w`/`light_design_w`
  of the 1,200 sampled households are identical in the rebuilt file. If not, only the differing cells rerun.
- Code tree: extend T19's own tree (`T19/code/repo`) into a new `T22/code/repo` with all archetype IDFs and
  city EPWs the 24 cells need, plus `schedule.json`/`schedule_sf.json` at the path `idf_optimizer.py:625`
  actually reads (T19 Decisions). Never write into T17/ or T19/.
- CPU: slurm array, one task per cell, `--array=0-23%N` with `-c` and `%N` chosen so that our running jobs
  together stay ≤ 32 CPUs, counting T17 (still running), T18 array 1328301 (2 × 8) and T20 (2 × 8, queued).
  Default if unsure: `-c 4`, `%2`. Memory 16G per task. Every job `-p ps -t 7-00:00:00`.

## Acceptance (collector)
- 24/24 tasks exit 0; each cell 50/50 successful runs, `hourly_meters.csv` 8760 rows each.
- Log of every cell has no "schedule.json not found" line (fallback bug did not trigger).
- Sampled household IDs per cell equal the seed-42 n=50 IDs of the published campaign for that cell
  (from the campaign's `cell_manifest.csv`, T17 tree or local). Report mismatches per cell, not banded.
- Output: one `cell_manifest.csv` per cell under `T22/out/<Archetype>__<City>/`.

## Brief (employee, Sonnet)
Rules as T19 (Speed login node = sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp plus single-file
tail/head/grep/wc -l/cat; never python/find/du/md5sum there; ssh `-o BatchMode=yes -o ConnectTimeout=60`;
tcsh, no `2>&1`; remote dirs by `scp -r`; python `/speed-scratch/o_iseri/envs/step4/bin/python`;
`ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`; no edits to existing repo files; local
`py -3 -m py_compile` / `bash -n` only). **Submit and end your turn — never wait.**
1. Read T19 and T17 docs; get the 24-cell list and where each IDF/EPW lives in T17's staged tree
   (`ls` only). Record under Decisions.
2. Build local staging `T22/code/repo` (T19 layout + all needed IDFs/EPWs + the two schedule JSONs at the
   `idf_optimizer.py` path) and `T22_scripts/t22_array.sh` (maps `SLURM_ARRAY_TASK_ID` → cell, output
   `T22/out/<Archetype>__<City>/`, log `T22/logs/`). Check `squeue -u o_iseri` for CPUs in use; set `-c`/`%N`.
3. `scp -r` to `/speed-scratch/o_iseri/2J_revision/T22/`, submit, write JobID + CPU arithmetic in the
   Ledger, Status SUBMITTED, end turn.

## Ledger
- **Step 1 (read T19/T17 docs, get the 24-cell list).** T19 (`2026-09-15_T19_wp3_static_arm_build_smoke.md`,
  COLLECTED, all 6 smoke checks PASS on job 1328297) confirms the wrapper `T19/T19_scripts/run_static_arm.py`
  is already staged and working on Speed at `/speed-scratch/o_iseri/2J_revision/T19/T19_scripts/
  run_static_arm.py` (args `--archetype --city --n --seed --sched-dir --output-dir --code-root`, full-run
  mode = no `--check-only`). T17 only ran/verified 4 Toronto cells, not the full 24. The exact 24-cell list
  (do-not-invent) is the published campaign's own array mapping: `Step8_docs/step8_array_v2.sh:18-29`
  (local read, `array=0-23`) = 4 archetypes (`SingleD, OtherDwelling, MidRise, HighRise`) x 6 cities
  (`Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B, Winnipeg_7A`), same task-index order,
  cross-checked against T16 Q1/Q3/Q8 (`--array=0-23`, same archetype/city names, same IDF/EPW filenames).
  IDF/EPW filenames and locations also from T16 Q3 (`2026-09-15_T16_step8_run_machinery.md`), confirmed
  present locally by Glob: 4 IDFs under `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`, 6 EPWs under
  `BEM_Setup/WeatherFile/`.
- **Step 2 (build local staging).** T19's own local staging files were session-scratchpad and no longer
  on disk; rebuilt `T22/code/repo` from the real local repo sources (not from T19's tree, which is gone
  locally but still live, unmodified, on Speed) with the SAME layout T19/T17 verified works:
  `T22/code/repo/2J_docs_occ_nTemp/Step8_docs/{run_bem.py, eSim_bem_utils_2J/*.py (16 files, unmodified)}`,
  `T22/code/repo/2J_docs_occ_nTemp/Step8_docs/0_BEM_Setup/Templates/{schedule.json,schedule_sf.json}`
  (copies placed at the buggy-but-unedited 2-up path `idf_optimizer.py:625` actually reads — same
  workaround T19 found, not a source edit), `T22/code/repo/2J_docs_occ_nTemp/BEM_setup/
  Buildings_MTL_v242/` (all 4 archetype IDFs, vs T19's 1), `T22/code/repo/BEM_Setup/WeatherFile/` (all
  6 city EPWs, vs T19's 1). Wrote `T22_scripts/t22_array.sh`: bash sbatch array script (24 tasks, same
  `ARCHETYPES`/`CITIES` bash arrays as `step8_array_v2.sh`, same task-index order), calling the EXISTING,
  unmodified `T19/T19_scripts/run_static_arm.py` directly from its Speed path (not re-copied) with
  `--code-root` pointed at the new `T22/code/repo`, `--sched-dir` pointed at T17's staged tree read-only
  (`/speed-scratch/o_iseri/2J_revision/T17/code/sched`), `--output-dir`
  `T22/out/<Archetype>__<City>`, `--n 50 --seed 42`, no `--check-only` (full-run mode). Local check:
  `bash -n t22_array.sh` -> clean (`BASH_SYNTAX_OK`). No local execution (needs eppy/E+, Speed-only venv).
  - **CPU check (`squeue -u o_iseri` before submit):** running = `1328286_2`/`_3` (T17 array, 2 tasks x
    `-c 8` = 16 CPU) + `1328301_0`/`_1` (T18 array, 2 tasks x `-c 8` = 16 CPU) = **32 CPU already running**,
    at the doc's own cap, before T22. `1328290` (T17 compare job, `-c 8`) was `PD` (Dependency), not yet
    consuming CPU — it starts only once T17's remaining 2 array tasks finish, at which point T17's
    footprint drops from 16 to 8 (the compare job alone). No T20 job visible in `squeue` (not currently
    running/queued, contrary to the Design section's stale note — read live, not assumed).
  - **Chosen: `--array=0-23%2 -c 4`** (the doc's own explicit default "if unsure"). Arithmetic: once T17's
    array finishes and hands off to its 8-CPU compare job, steady-state = T18 (16) + T17-compare (8) +
    T22 (%2 x 4 = 8) = **32 CPU, exactly at cap**. Before that handoff, if T22's throttled slots happened
    to start immediately, transient total could reach 40; recorded as a known, bounded risk rather than
    invented away — mitigated in practice by the cluster's own per-association CPU limit (see JobID entry
    below: T22 queued `PD (AssocGrpCpuLimit)` immediately after submit, i.e. the cluster itself is holding
    T22 at 0 running CPU until slots free, not letting the transient overshoot happen).
- **JobID 1328310** — `sbatch t22_array.sh` (`--array=0-23%2 -c 4 --mem=16G -t 7-00:00:00 -p ps`), run
  from `/speed-scratch/o_iseri/2J_revision/T22/T22_scripts/`. Immediate post-submit `squeue`: whole array
  `1328310_[0-23%2]` state `PD`, reason `AssocGrpCpuLimit` (association-level CPU cap already saturated
  by T17+T18 at 32 running CPU — confirms the arithmetic above, not a job-definition error). Will start
  tasks as T17/T18 free CPU.

## Verified
- Remote `ls` after `scp -r` (login node, allowed): all 16 `.py` files, `schedule.json`,
  `schedule_sf.json`, all 4 IDFs, all 6 EPWs, and `t22_array.sh` present under
  `/speed-scratch/o_iseri/2J_revision/T22/code/repo/` and `.../T22/T22_scripts/` exactly as staged
  locally — no partial copy.
- Confirmed via `ls` (not assumed) that `T19/T19_scripts/run_static_arm.py` and
  `T17/code/sched/BEM_Schedules_2022.csv`/`_2030.csv` still exist on Speed before pointing T22's array
  script at them.

## Decisions
- **Reuse T19's wrapper in place on Speed rather than re-copying it.** The Design section says "Same
  wrapper ... unchanged" — since T19's `run_static_arm.py` is already staged and smoke-verified at a
  fixed Speed path, `t22_array.sh` calls it there directly (`$WRAPPER=/speed-scratch/o_iseri/2J_revision/
  T19/T19_scripts/run_static_arm.py`) instead of scp'ing a second copy into T22; only `--code-root` (and
  `--output-dir`/`--sched-dir`) differ per T22's own new tree. Satisfies "never touch T17/ or T19/, only
  read/reuse" — T19 is read-only-invoked, nothing written there.
- **24-cell order/list taken from `step8_array_v2.sh`, not re-derived from `main.py`'s
  `STEP8_ARCHETYPES`/`STEP8_CITIES` dict ordering** — the array script is the actual historical
  task-index -> cell mapping used by the one full-campaign SLURM array on record (T16 Q1), and matches
  T16 Q3's independently-read filenames, so using it satisfies "do not invent" most directly.
- **`-c 4 %2`** chosen per the Design section's own explicit fallback, after checking live `squeue`
  (see Ledger) rather than trusting the Design section's now-stale T20 mention. Recorded, not silently
  overridden: the association CPU limit is what actually prevents any real overshoot past 32, confirmed
  by the job queuing `PD (AssocGrpCpuLimit)` rather than starting immediately.

## Next
Employee (done): steps 1-3, job **1328310** submitted (queued `PD`, `AssocGrpCpuLimit` — will start as
T17/T18 free CPU). Collector (fresh, >= 30 min later, likely many hours — 24 cells x 50 households):
`sacct -j 1328310` for per-task exit codes; if any/all tasks `COMPLETED`, `scp` back
`T22/logs/t22_<jobid>_<taskid>.{out,err}` and each cell's `cell_manifest.csv`
(`T22/out/<Archetype>__<City>/cell_manifest.csv`); grep every task log for "schedule.json not found"
(fallback-bug check, per T19's finding); compare sampled HH IDs per cell against the seed-42 n=50 draw
from the campaign's own `cell_manifest.csv` (T17 tree or local); check `hourly_meters.csv` row counts
(8760) per successful sample. Report mismatches per cell, not banded, per the Acceptance section above.
Manager: feeds WP3 comparison (static vs diary arm) once collected.

## WHAT I DID NOT VERIFY
- Did not wait for or poll job 1328310; only the immediate post-submit `squeue` snapshot (`PD`,
  `AssocGrpCpuLimit`) was collected. No evidence yet that any of the 24 tasks actually starts, that
  `run_static_arm.py` finds the 4 IDFs/6 EPWs under the new `T22/code/repo`, or that the fallback-path
  bug T19 found stays routed around at full-run scale — that is the collector's job.
- Did not re-verify T17's own current job state beyond the one `squeue` snapshot used for the CPU
  arithmetic; T17's remaining 2 array tasks and its pending compare job were not tracked further.
- Did not check disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T22/` before submitting
  (24 cells x 50 households worth of E+ output, larger than T19's 2-sample smoke).
- Did not independently re-verify T18's or T20's own job identity/purpose beyond what `squeue` showed;
  took the Design section's T18 CPU count at face value, and used live `squeue` (no T20 entry) rather
  than the doc's stale mention of a queued T20.
