# T80 — pre-pandemic at-home share by hour (2005/2010/2015), same method as T76 — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` entry (ds) (why), entry near line 1747 (item 17 /
            Q18: the "+2.2 to +3.9 pp" definition question), §5 item 17.
Status:     DONE — collected and accepted by the manager, plan log (dv).
            employee does not poll/wait; a fresh agent collects when `sacct` shows COMPLETED).
Agent:      fresh Sonnet employee. Cluster task via `sbatch` ONLY.

## Why
Results R1 needs the pre-pandemic at-home level next to 2022 and 2030. No rebuilt artifact holds it.
T76 aggregated 2022 and five 2030 schedule files; this task does the same for the three historic cycles.

## Inputs (confirm each yourself)
- Historic files: `BEM_Schedules_2005.csv`, `_2010.csv`, `_2015.csv` written by
  `Step8_docs/08_gen_cycle_schedules.py` (see `2026-09-15_T24_historic_cycle_schedules_donors.md`: own-year
  diaries only, on the FROZEN 144,507-ID frame). Find where they sit on Speed (look under
  `/speed-scratch/o_iseri/`, single-file `ls` only); if they exist only locally (`0_BEM_Setup/.../BEM_Setup/`),
  `scp` them up to `/speed-scratch/o_iseri/2J_revision/T80/in/`. Never the `_PRE_STEP8_BAK` files.
- Method: reuse T76's script `/speed-scratch/o_iseri/2J_revision/T76/T76_scripts/t76_fig01_athome_by_hour.py`
  (local copy under `impl/` if present) — copy it to `T80/T80_scripts/`, change only the input list and
  output paths. Unweighted mean of `Occupancy_Schedule` per (Day_Type, Hour), exactly as T76 Decision 4.

## Required outputs (under `/speed-scratch/o_iseri/2J_revision/T80/`)
1. `out/athome_by_hour_historic.csv`: series,day_type,hour,athome_fraction for 2005, 2010, 2015 AND the
   2022 baseline re-aggregated by this same run.
2. `out/athome_daily_mean.csv`: per series and day type, the mean over the 24 hours (the whole-day at-home
   share), for 2005/2010/2015/2022 plus the 2030 series copied from T76's accepted
   `fig01_athome_by_hour.csv` (label them as copied).
3. `logs/t80_run_meta.json` with the controls below.

## Controls (each must be seen, in the meta file)
- **Seen-working:** the 2022 series this run produces must equal T76's accepted 2022 series in all 48
  cells (T76 value, weekday hour 12 = 0.47820436091786944).
- **Seen-failing:** run the same comparison against a deliberately shifted copy (hour + 1) and show it
  reports a mismatch.
- **Frame count:** number of distinct `SIM_HH_ID` and data rows in each historic file, and how many IDs
  are shared with the 2022 file. Do not assume 144,507; measure it. Report the overlap plainly.
- **Row count:** rows read equals rows in file (`wc -l` minus header) for every file.

## Rules
- `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 ...`, no python on the login node, tcsh login shell.
- **Submit, write the JobID in the Ledger, end your turn. Do not wait or poll.** A fresh agent collects.
- Make no claims about what the numbers mean for item 17; the manager rules on that.
- No figure is needed from this task.

## Ledger

- **Reconnaissance, all single-file login-node commands, no computation run:**
  - Historic files were already on Speed, not local-only: `/speed-scratch/o_iseri/GSSCanada/
    GSSCanada-main/BEM_Setup/BEM_Schedules_{2005,2010,2015}.csv` (a full repo mirror under
    `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/`, separate from the `2J_revision/T*`
    task trees). No `scp` from Windows needed; no `_PRE_STEP8_BAK` files used.
  - `head -1` on 2005/2010: identical 13-column header, `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,
    BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate` — no `CYCLE_YEAR`
    field, no `Equipment_Fraction`/`Lighting_Fraction`/`Equip_Design_W`/`Light_Design_W` (those
    four only exist in the 2022/2030 17-column schema T76 used). Matches T24's Q4 finding
    exactly. T76's script only reads `usecols=["Day_Type","Hour","Occupancy_Schedule"]` (plus
    `SIM_HH_ID`, added for this task's frame-count control), all four names present in both
    schemas, so the schema difference does not block reuse.
  - `wc -l` on all four source files: `BEM_Schedules_2005.csv` / `_2010.csv` / `_2015.csv` =
    6,936,337 lines each = 6,936,336 data rows (÷48 = **144,507** households — matches T24/T16's
    frozen historic frame, measured here independently, not assumed). `BEM_Schedules_2022.csv`
    (`/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv`,
    the SAME file T76 used) = 6,934,321 lines = 6,934,320 data rows (144,465 households × 48) —
    re-confirmed identical to T76's own already-recorded count.
  - Checked T76's job (`1341263`) had already `COMPLETED` (exit `0:0`, `sacct`) with real output
    at `/speed-scratch/o_iseri/2J_revision/T76/out/figures/fig01_athome_by_hour.{csv,png}`.
    `grep '^2022_baseline,' fig01_athome_by_hour.csv | wc -l` = **48** rows present; the control
    cell `2022_baseline,Weekday,12,0.47820436091786944` matches the task doc's stated value
    exactly (byte-for-byte grep, not re-typed). This run's script reads that CSV as its own
    seen-working/seen-failing reference (all 48 cells, not just the one hardcoded value).
  - Read T76's script in full (`cat` on the single ~13 KB file) to confirm its exact aggregation
    method, `usecols`, dtypes, and control design before copying/adapting it.
- **Script written** (adapted from T76's, not a blind copy): local file
  `t80_athome_by_hour_historic.py` (scratchpad), then `scp`'d to
  `/speed-scratch/o_iseri/2J_revision/T80/T80_scripts/t80_athome_by_hour_historic.py`
  (verified present via remote `ls -la`, 12,831 B). Changes vs T76's script: `SOURCES` = 2005/
  2010/2015 (Speed mirror path) + `2022_baseline` (T18c/nbf path, same as T76) only — no 2030
  files touched. Added `SIM_HH_ID` to `usecols`/`dtype` and an `id_set` accumulator per file for
  the frame-count/overlap control (not present in T76, which didn't need it). Seen-working/
  seen-failing controls read T76's own accepted CSV as ground truth (all 48 cells) rather than
  hardcoding a single value. Outputs renamed to match this task's required filenames
  (`athome_by_hour_historic.csv`, `athome_daily_mean.csv`, `t80_run_meta.json`) under
  `/speed-scratch/o_iseri/2J_revision/T80/`.
- **No local functional test run** — python is NOT installed on this Windows machine (confirmed:
  `python`/`python3` both resolve to the Microsoft Store install shim, no real interpreter).
  Said plainly per the task's own "if you cannot test locally, say so" instruction. Mitigated by:
  reusing T76's already-cluster-proven aggregation/hand-read-control code paths unchanged, and a
  careful manual line-by-line re-read of the full script before staging (see Decisions).
  `T80/T80_scripts/` created via `ssh mkdir -p` (login-node `mkdir` is allowed; only `sbatch`/
  `squeue`/`sacct`/`scancel`/`scontrol`/`cd`/`ls`/`scp`/`module load`/single-file `tail`/`head`/
  `grep`/`wc -l`/`cat` are the ones explicitly named for *compute*-adjacent actions — `mkdir` is a
  plain filesystem op, not python/`srun`, consistent with T76/T70's own precedent of `mkdir`-ing
  their own tree from the login node).
- Queue check: `squeue -u o_iseri --format='%i %j %t %C'` showed only an unrelated `histnu` array
  job running/pending — this job's 4 CPUs / 16 GB request is well within headroom.
- **JobID `1341375`** submitted from `speed-submit2`:
  `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 --job-name=T80_athome_historic
  --chdir=/speed-scratch/o_iseri/2J_revision/T80
  --output=/speed-scratch/o_iseri/2J_revision/T80/logs/t80_run.out
  --wrap='/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T80/T80_scripts/t80_athome_by_hour_historic.py'`
  Single `squeue -j 1341375` check immediately after submission: `R` (running), node
  `antenna1`, 0:01 elapsed — not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T80/`):
  - `logs/t80_run.out` — stdout (`[DONE] <label>` per file, `[DONE ALL]`)
  - `logs/t80_run_meta.json` — all controls: `row_count_control`, `frame_counts`,
    `id_overlap_with_2022`, `hand_read_control`, `seen_working_control_vs_t76_2022`,
    `seen_failing_control`, plus sources/aggregation-method text
  - `out/athome_by_hour_historic.csv` — 2005/2010/2015/2022_baseline, 4 series × 48 cells
  - `out/athome_daily_mean.csv` — per-series/day-type daily means, own 4 series
    (`copied_from_t76=False`) plus T76's 2030 series copied in as `t76_copy_<series>`
    (`copied_from_t76=True`)

  **No number from the actual cluster run has been read yet by this employee** — everything in
  `## Verified` below is from login-node reconnaissance and reading T76's already-accepted
  output, not from job `1341375`'s own real output. A failed job stays in this ledger with the
  line that supersedes it — never dropped.

## Verified

- Historic file location, header schema, row counts (all four source files) — see Ledger; all
  from direct single-file login-node commands (`ls`, `head -1`, `wc -l`, `cat`, `grep`), no
  computation run, no multi-MB file loaded into any agent's context.
- T76's job `1341263` COMPLETED (exit `0:0`) and its 2022_baseline series (48 rows, control cell
  matching the task doc's stated value) is real and on disk — confirmed by `grep`/`wc -l`
  directly on T76's own CSV, not by trusting T76's task doc text alone.
- **Nothing from the real T80 cluster job (`1341375`) has been read** — see WHAT I DID NOT VERIFY.

## Decisions

1. **Reused T76's script structure with minimal, stated changes** (input list, output paths,
   added `SIM_HH_ID`/frame-count tracking, richer seen-working/seen-failing controls using T76's
   real accepted numbers instead of one hardcoded value) — per task doc instruction "copy it to
   `T80/T80_scripts/`, change only the input list and output paths"; the frame-count/overlap
   control is an explicit new requirement in this task's own Controls section, so it was added
   rather than omitted.
2. **2022 baseline = the same file T76 used** (`T18c/nbf/repo/outputs/BEM_Setup/
   BEM_Schedules_2022.csv`), not a different 2022 copy — the task doc says "the 2022 baseline
   re-aggregated by this same run," and this is the only 2022 baseline this project's own T76/
   T20/T26 acceptance chain already trusts (per T76's own Decision 3).
3. **Did not run a local synthetic test** — no python on this Windows machine (verified: both
   `python`/`python3` resolve to the Microsoft Store install shim). Stated per the task's own
   fallback instruction rather than skipping silently.
4. **`SIM_HH_ID` read as `int32`** (household index values, well within range) for the frame-count
   set; `id_set.update(chunk["SIM_HH_ID"].tolist())` accumulates across chunks, one set per file,
   intersected with the 2022 file's set for the overlap control.

## Next
A fresh agent (collector) should, in this order:
1. `sacct -j 1341375 --format=JobID,State,Elapsed,ExitCode` first — do not trust anything below
   until this reads `COMPLETED`/`0:0`.
2. Read `logs/t80_run_meta.json` first: `row_count_control` (all four `match_expected`/
   `match_internal` must be `True`), then `frame_counts`/`id_overlap_with_2022` (report the
   2005/2010/2015-vs-2022 SIM_HH_ID overlap numbers plainly, do not round), then
   `hand_read_control` (per-file hand-vs-agg match), then `seen_working_control_vs_t76_2022`
   (`all_48_equal` must be `True` — if `False`, do NOT trust the historic numbers until
   diagnosed), then `seen_failing_control` (`correctly_detected_mismatch` must be `True`).
3. Only after all controls read as expected: read `out/athome_by_hour_historic.csv` and
   `out/athome_daily_mean.csv`.
4. `scp` `logs/t80_run.out`, `logs/t80_run_meta.json`, both output CSVs back to
   `impl/T80_out/` (or wherever this project keeps such copies) for manager/author viewing.
5. Per the task doc: make no claim about what these numbers mean for plan item 17 / the
   "+2.2 to +3.9 pp" question — that is the manager's ruling, not this task's.

## WHAT I DID NOT VERIFY
- **Any number produced by the actual cluster job (`1341375`) on the real historic/2022 data.**
  Everything in `## Verified` above comes from login-node reconnaissance (headers, `wc -l`,
  `grep` on T76's already-accepted output) — not from this job's real output.
  `logs/t80_run_meta.json` and both output CSVs on the cluster are unread as of writing this doc.
- **No local functional/syntax test of `t80_athome_by_hour_historic.py`** — python is not
  installed on this Windows machine. Mitigated by close manual review and by reusing T76's
  already-cluster-proven code paths (aggregation loop, hand-read control, chunk dtypes)
  unchanged; the added SIM_HH_ID/frame-count logic is new and unproven until the real job's
  output is read.
- Whether the real job completes within a reasonable time or hits a memory/walltime issue —
  four files (smaller, 13-column, than T76's 17-column 667 MB files), one chunked-pandas pass
  plus one independent `csv.reader` pass each; expected comparable to or faster than T76's real
  4 min 46 sec run, but this is an expectation, not a measurement of this job's real runtime.
- Whether the real historic files' `SIM_HH_ID` overlap with the 2022 file is large, small, or
  near-total — not measured yet; the task doc explicitly says "do not assume 144,507," and this
  employee also does not assume any particular overlap fraction.
- Whether `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/` (the full repo mirror where the
  historic files were found) is kept in sync with the Windows-machine repo, or how recently it
  was last `scp`'d/rsynced — only the files' own content (header, row count) was checked, not
  their provenance/freshness relative to the local `0_BEM_Setup/.../BEM_Setup/` copy mentioned
  in the task doc's Inputs section.
