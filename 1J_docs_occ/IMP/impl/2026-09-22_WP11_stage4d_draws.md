# WP11 — Stage 4d: draw-start patch, per-task extraction, stopping-rule scorer, draw arrays

State lives here. Do not park: write every result to this file's Ledger, then end your turn.
Never wait/sleep/poll for a running job; submit and stop.

Status: **IN PROGRESS** -- items 1-7 built and staged; only items 2 and 7 submitted (per spec). Waiting on 1342170/1342171 to land; manager builds/submits the draw arrays and scorers after Gate 4 (1342160), workers-check (1342163) and the probe (1342171) all read PASS.

Design source: plan log `1J_docs_occ/IMP/00_REVISION_PLAN.md` entry **(aw)** — read it first; it is binding.
Stopping rule: plan log (ar) / manager prompt §7.1 — never change a word or a number of it.

## Context you need (all measured by the manager, 2026-09-22)

- Staged code on Speed: `/speed-scratch/o_iseri/1J_rerun/code/eSim_bem_utils/` (`main.py` 2,700 lines,
  `run_batch_hpc.py`, `plotting.py`, `simulation.py`). Venv python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python`.
  EnergyPlus: `/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64`.
  Job template to copy (env, venv, md5 pre-flight): `/speed-scratch/o_iseri/1J_rerun/stage4/wp10_stage4_default_RC6.sh`.
- `main.py:2193-2199`: `for k in range(iter_count): draw_number = k + 1 ... iter_dir = os.path.join(neighbourhood_dir, f"iter_{k+1}")`.
  Also `batch_name=f"{batch_name}/iter_{k+1}"` at ~2232 and `f"{scenario}_Iter{k+1}"` at ~2245.
- Manifest: `/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv`, draws 1..30, 215 rows per draw
  (43 buildings x 5 years). Buildings per neighbourhood: RC1 2, RC2 2, RC3 14, RC4 8, RC5 8, RC6 9.
- Gate 4 code to reuse (G4.0 echo-vs-manifest logic): `/speed-scratch/o_iseri/1J_rerun/stage4/wp10_gate4.py`
  (`read_manifest_lookup`, `check_g4_0`). Local copy: `impl/wp10/wp10_gate4.py`.
- April Default references (Heating/Cooling, kWh/m2): RC1 35.1170/45.6120, RC2 38.1730/44.0140,
  RC3 24.9740/46.5260, RC4 156.4140/18.2310, RC5 158.5250/19.4240, RC6 150.7800/26.2210.
- Existing draw-1 results (block-1 reproducibility control): `/speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1/NUS_RC{1..6}/iter_1/<year>/eplusout.sql`.
- Every runner job exits 1 on a known, harmless plotting crash AFTER `aggregated_eui.csv` is written.
  Therefore chain only with `afterany`, never `afterok`, and never read success from the runner's exit code.
- Disk: `/speed-scratch` quota 8.7 T used of 10.0 T (`quota -s`). `eplusout.eso` is read by no code.
- Live jobs you must not disturb: 1341393, 1341394 (RC5/RC6 Default), 1342160 (Gate 4 real),
  1342161/1342162/1342163 (workers check). **Do not modify any file under `code/` directly.**

## What to build (all files under `/speed-scratch/o_iseri/1J_rerun/stage4/wp11/`, local copies under `impl/wp11/`)

1. **`main_wp11.py`** = copy of the staged `main.py` with the additive draw-start patch only:
   `draw_start = int(os.environ.get("WP11_DRAW_START", "1"))` read once at the start of the MC loop; print
   `WP11 DRAW START: {draw_start}` once (flush); then `draw_number = draw_start + k` and every `k+1`
   in that loop body (iter_dir, batch_name, the `_Iter` export label, the progress print) becomes
   `draw_number`. Nothing else changes. Save the diff as `wp11_main.diff` (must be small; show it in the Ledger).
2. **`wp11_swap_probe.sh`** (sbatch, 1 CPU, 32G): (a) `cp code/eSim_bem_utils/main.py code/eSim_bem_utils/main.py.pre_WP11`
   and check it is non-empty; (b) `cp main_wp11.py code/eSim_bem_utils/main.py`; (c) `grep -c "WP11 DRAW START"` on it must be 1,
   and `grep -c "WP10 GUARD"` must equal the count in `.pre_WP11`; (d) run `wp11_probe.py`.
   **`wp11_probe.py`** (no EnergyPlus): import the swapped `main` as the WP10 probe does, replace
   `m.simulation.run_simulations_parallel` with a no-op INSIDE THE PROBE ONLY, then call
   `m._run_mc_neighbourhood` for NUS_RC1 into `stage4/wp11/probe/<case>/` for three cases, and read back the echo files:
   - `unset`: env unset, iter_count 1 -> `iter_1/mc_manifest_echo.csv` draws all 1, hh_ids = manifest. Expect PASS.
   - `start6`: `WP11_DRAW_START=6`, iter_count 2 -> `iter_6` and `iter_7` exist, echo draws 6 and 7 = manifest; no `iter_1`. Expect PASS.
   - `start30` (**seen failing**): `WP11_DRAW_START=30`, iter_count 2 -> draw 31 must raise/record `MANIFEST MISS`. Expect FAIL-as-designed.
   Print `WP11 PROBE SUMMARY: unset=.. start6=.. start30=..` and `WP11 PROBE VERDICT: PASS` only if the three outcomes are exactly as expected.
   Submit with `--dependency=afterany:1342160:1342163` so nothing running sees the swap.
3. **`wp11_extract.py`** (runs inside each draw task, after the runner): args `--nu NUS_RCk --task-dir <block dir> --draw-start D --n-draws 5`.
   - For each draw d in D..D+4 and year in 2005/2010/2015/2022/2025: open `<task-dir>/NUS_RCk/iter_<d>/<year>/eplusout.sql`
     with sqlite3, call the pipeline's `plotting.calculate_eui(conn)`, take `end_uses_normalized` (fall back to
     `end_uses` exactly as `main.py:_flush_aggregated_csv` does). Write `<task-dir>/NUS_RCk/per_draw_eui.csv`:
     `neighbourhood,draw,year,end_use,value` for every end use (Heating and Cooling at minimum). Same for the task's `Default/eplusout.sql` with year=`Default`, draw=0.
   - Checks, each printing `WP11 EXTRACT <name>: PASS|FAIL -- detail`:
     E1 all 25 draw-year sqls present and non-empty; E2 for each year, mean over the 5 draws of Heating and of Cooling
     equals `aggregated_eui.csv` `<year>_mean` within 0.00051; E3 each `iter_<d>/mc_manifest_echo.csv` equals the manifest rows for (NUS_RCk, d) exactly
     (reuse `wp10_gate4.check_g4_0`); E4 the Default Heating/Cooling equal the April reference above within 0.00051;
     E5 `WP11 DRAW START: D` is PRESENT in the task log (path passed as `--log`).
   - `WP11 EXTRACT VERDICT: VERIFIED` only if E1-E5 all PASS; exit 0. Otherwise `NOT_VERIFIED`, exit 1.
4. **`wp11_draw_task.sh`** (sbatch array task, bash): maps `SLURM_ARRAY_TASK_ID` to (block, neighbourhood) from an
   `ARRAY_KIND` env (`LIGHT`: block = i//4+1, RC(i%4+1); `HEAVY`: block = i//2+1, RC5 if i even else RC6).
   `D = 5*(block-1)+1`. Pre-flight: parse `quota -s` for `/speed-scratch`; if free < 400 G print `WP11 PREFLIGHT DISK: FAIL` and exit 3
   before running; copy the md5 dedupe pre-flight from the RC6 template. Then `export WP11_DRAW_START=$D`, run
   `run_batch_hpc.py --idf .../NUS_RCk.idf --region Quebec --sim-mode standard --iter-count 5 --workers 5 --output-dir /speed-scratch/o_iseri/1J_rerun/stage4/draws/block_<b>`,
   log its exit code as `RUNNER EXIT: n (1 = known plotting crash)`, then run `wp11_extract.py`. **Only if VERIFIED:**
   delete every `eplusout.eso` under that task's `NUS_RCk/` (iter dirs and Default) and `gzip` every `eplusout.sql` there; print the
   count of files deleted/gzipped and the task dir size before/after (`du -sh` is fine INSIDE a job). If not VERIFIED, delete nothing.
   The task exits with the extraction's exit code. `#SBATCH -A chachemv -p ps -t 7-00:00:00 -c 5`, output
   `logs/wp11_draw_%A_%a.out`. Memory is given by the manager at submission (`--mem`), do not hard-code it.
5. **`wp11_stoprule.py`** (scorer): `--mode real --block b` or `--mode selftest`.
   - Real: for blocks 1..b read every `draws/block_<j>/NUS_RC*/per_draw_eui.csv`; require every contributing task log to
     show `WP11 EXTRACT VERDICT: VERIFIED`; require all 60 cells (6 neighbourhoods x 5 years x Heating/Cooling) to have exactly
     draws 1..5b, one value each. Otherwise `NOT_EVALUABLE` naming what is missing.
   - Per cell: n = 5b, mean, s = sample SD with ddof = 1, half = t(0.975, n-1) * s / sqrt(n), met iff half <= 0.01 * mean;
     mean <= 0 -> cell NOT_EVALUABLE. Use `scipy.stats.t.ppf` if the venv has scipy AND check it against this pinned table
     (df: value) 4: 2.776445, 9: 2.262157, 14: 2.144787, 19: 2.093024, 24: 2.063899, 29: 2.045230 to 1e-5; if scipy is absent use the table.
   - Block 1 only, control C1: draw 1 of every cell equals the value extracted the same way from `stage4/default/draw_1/NUS_RC*/iter_1/<year>/eplusout.sql`
     within 0.00051, else NOT_EVALUABLE (nondeterminism). If block 1 sqls are already gzipped, read the draw-1 value from block 1's `per_draw_eui.csv`.
   - Write `stage4/draws/stoprule_block_<b>.csv` (cell, n, mean, sd, half, half_pct, met) and print
     `STOPRULE SUMMARY: block=b n=5b cells_met=X/60 VERDICT=STOP|CONTINUE|CAP_REACHED_TARGET_UNMET|NOT_EVALUABLE` (CAP at b=6 unmet).
   - **On STOP only:** `scancel` the array tasks of blocks b+1..6 (both arrays) and the scorer jobs of blocks b+1..6, reading the IDs from
     `stage4/draws/job_ids.txt` (written by the manager at submission: lines `LIGHT <id>`, `HEAVY <id>`, `SCORER <b> <id>`); print every scancel it issues.
   - Selftest (synthetic numbers, no cluster files; must run locally with `py` too): seen failing first: (i) all cells at 0.5 % -> STOP;
     (ii) one cell at 1.2 % -> CONTINUE; (iii) one draw missing -> NOT_EVALUABLE; (iv) a cell with mean 0 -> NOT_EVALUABLE; (v) b=6 unmet -> CAP_REACHED_TARGET_UNMET;
     (vi) a hand-computed cell (values 10, 11, 9, 10.5, 9.5 -> mean 10, s = 0.790569, half = 0.981625, 9.82 %) matches to 1e-5 — this catches a ddof=0 slip;
     (vii) C1 mismatch -> NOT_EVALUABLE. Print `STOPRULE SELFTEST SUMMARY: 7 checks, 0 unexpected`.
6. **`wp11_scorer.sh`** (sbatch, 1 CPU, 8G): runs `wp11_stoprule.py --mode real --block $B`.
7. **Selftests on the cluster:** one sbatch job (1 CPU) runs `wp11_stoprule.py --mode selftest` and a `wp11_extract.py` selftest on
   ONE already-finished real task directory: `stage4/default/draw_1/NUS_RC1` with `--draw-start 1 --n-draws 1` (E2 against its own
   aggregated csv must PASS; then on a temp COPY of that csv with one mean changed by 0.01 it must FAIL — seen failing first). Never
   delete or gzip anything in `default/` — add a `--no-cleanup` guard and use it here.

## What you submit
Only: the selftest job (step 7) and `wp11_swap_probe.sh` (step 2, `afterany:1342160:1342163`). **Do NOT submit the draw arrays or scorers** —
the manager submits them after reading Gate 4, the workers check and the probe.

## Hard rules
- `sbatch` only; no python on the login node; login-node commands: sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp/module load and single-file tail/head/grep/wc -l/cat. No find/du/md5sum on the login node. tcsh login shell. Every job: `-A chachemv -p ps -t 7-00:00:00`.
- 1J CPU budget: at most 32 CPUs running at once (the rest belongs to `histnu`). Your jobs are 1 CPU each.
- Never edit `code/` directly; the swap job does it, after backing up.
- Write the Ledger as you go. Then end your turn with "jobs N, M submitted, state written to <this file>".

## Ledger
(append-only: JobID · what · state · exit · output path)

- **1342170** · `wp11_selftest.sh` (item 7: `wp11_stoprule.py --mode selftest` + `wp11_extract.py --mode selftest` on `default/draw_1/NUS_RC1`, `--no-cleanup`) · submitted 2026-09-22, no dependency · confirmed RUNNING via `squeue` at submission (0:10 elapsed on magic-node-04) · not polled further (no-parking rule) · output `/speed-scratch/o_iseri/1J_rerun/logs/wp11_selftest_1342170.out`.
- **1342171** · `wp11_swap_probe.sh` (item 2: backup+swap `main.py`↔`main_wp11.py`, two grep sanity checks, `wp11_probe.py`) · submitted 2026-09-22, `--dependency=afterany:1342160:1342163` · confirmed PENDING (Dependency) via `squeue` at submission · output `/speed-scratch/o_iseri/1J_rerun/logs/wp11_swap_probe_1342171.out`.
- Items 3, 4, 5, 6 (`wp11_extract.py`, `wp11_draw_task.sh` + `wp11_quota_check.py`, `wp11_stoprule.py`, `wp11_scorer.sh`) built and staged on the cluster, **not submitted** — per spec, the manager submits the draw arrays and scorers after reading Gate 4, the workers check and the probe.

## Verified

- `main_wp11.py`'s diff against the staged `main.py` (pulled fresh via `scp` before editing) is exactly the 4 named spots — no other line changed. Diff saved at `impl/wp11/wp11_main.diff` (also staged on the cluster) and reproduced in full below. `grep -c "WP11 DRAW START"` on `main_wp11.py` = 1; `grep -c "WP10 GUARD"` = 1, same as the pre-patch file (confirmed locally with `grep -c` on both copies).
- `py -m py_compile` clean on all 5 python files (`main_wp11.py`, `wp11_probe.py`, `wp11_extract.py`, `wp11_quota_check.py`, `wp11_stoprule.py`); `bash -n` clean on all 4 shell scripts (`wp11_swap_probe.sh`, `wp11_draw_task.sh`, `wp11_scorer.sh`, `wp11_selftest.sh`).
- `wp11_stoprule.py --mode selftest` run locally with `py`: **`STOPRULE SELFTEST SUMMARY: 7 checks, 0 unexpected`**, all 7 named checks (i)-(vii) PASS, including the ddof=1 hand-computed cell (mean=10.0, sd=0.7905694150420949, half=0.9816215807387786, half_pct=9.816215807387787 -- matches the doc's 0.790569/0.981625/9.82% to well under 1e-5). Local `py` has scipy 1.17.0 installed, so this run exercised the scipy path (`t.ppf(0.975, df)`), cross-checked against the pinned table to 1e-5 with no disagreement raised — the ImportError fallback path (pinned table only) was NOT exercised locally and is unverified on the cluster venv (see WHAT I DID NOT VERIFY).
- `wp11_quota_check.py` sanity-checked locally against three synthetic `quota -s`-shaped fixtures (duplicate soft/hard limit values, distinct values, a low-headroom case) — correctly returns `FREE_GB` using min(values)=used / max(values)=limit in each case, including the tie case that an earlier (largest, second-largest) design got wrong (used got reported as 0 free with tied 10.0T/10.0T tokens). Real `quota -s` output was never seen (see Decisions/WHAT I DID NOT VERIFY).
- `wp11_swap_probe.sh` and `wp11_selftest.sh` were confirmed queued via `squeue` immediately after submission (see Ledger); no job output was read (no-parking rule -- the manager reads results on wake).
- All 6 files scp'd to `/speed-scratch/o_iseri/1J_rerun/stage4/wp11/` and confirmed present via `ls -la` on the login node (allowed command).

### `wp11_main.diff` (the whole patch, item 1)
```diff
@@ -2190,12 +2190,21 @@
         # ranking or a pool any more; every household id below comes from
         # mc_draw_manifest, keyed by (neighbourhood, draw, year, building_index).

+        # WP11 (2026-09-22): draw-start patch, additive only -- behaviour is unchanged
+        # when WP11_DRAW_START is unset (defaults to "1", identical to the old k+1
+        # numbering). Lets one array task run draws D..D+iter_count-1 instead of always
+        # starting at draw 1, so several tasks for the same neighbourhood can cover
+        # different draw blocks without colliding on iter_1..iter_<iter_count>.
+        # Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 1.
+        wp11_draw_start = int(os.environ.get("WP11_DRAW_START", "1"))
+        print(f"WP11 DRAW START: {wp11_draw_start}", flush=True)
+
         for k in range(iter_count):
-            draw_number = k + 1
-            print(f"\n--- Iteration {k+1}/{iter_count} (manifest draw {draw_number}) ---")
+            draw_number = wp11_draw_start + k
+            print(f"\n--- Iteration {draw_number}/{iter_count} (manifest draw {draw_number}) ---")

             # Prepare jobs for this iteration
-            iter_dir = os.path.join(neighbourhood_dir, f"iter_{k+1}")
+            iter_dir = os.path.join(neighbourhood_dir, f"iter_{draw_number}")
             os.makedirs(iter_dir, exist_ok=True)

             jobs = []
@@ -2229,7 +2238,7 @@
                         prepared_idf, final_idf, schedules_list,
                         original_idf_path=selected_idf, epw_path=selected_epw,
                         sim_results_dir=SIM_RESULTS_DIR,
-                        batch_name=f"{batch_name}/iter_{k+1}"
+                        batch_name=f"{batch_name}/iter_{draw_number}"
                     )

                     # Export all used schedules for debugging (Iter 1 only to save space, or all?)
@@ -2242,7 +2251,7 @@
                         for sched in schedules_list:
                             hh_id = sched.get('hh_id', 'unknown')
                             integration.export_schedule_csv(
-                                sched, str(hh_id), f"{scenario}_Iter{k+1}",
+                                sched, str(hh_id), f"{scenario}_Iter{draw_number}",
                                 SIM_RESULTS_DIR, batch_name=batch_name
                             )
```
(45-line diff; two lines of context shrunk above for readability -- the file on disk is the literal `diff -u` output, unedited.)

## Decisions

1. **"the progress print" (item 1) read as the `Iteration {k+1}/{iter_count}` line, not the two later count-only prints.** Item 1 names four things whose `k+1` becomes `draw_number`: iter_dir, batch_name, the `_Iter` export label, "the progress print". Only one print sits among/near those three file-path spots and mentions the draw (`--- Iteration {k+1}/{iter_count} (manifest draw {draw_number}) ---`) -- that one was changed (both `{k+1}` occurrences now read `{draw_number}`, so the two numbers it prints stop disagreeing). Two other `k+1` prints exist further down (`"No jobs for iteration {k+1}, skipping"` and `"[checkpoint] ... ({k+1} iterations so far)"`) — left untouched, since both are genuinely counting *this job's own* iterations, not labelling a draw, and the doc's "Nothing else changes" line rules out touching them without a named reason. Cosmetic only either way — no file path, csv content or check reads these lines except E5, which only requires the `WP11 DRAW START: D` line, unaffected.
2. **Cleanup (delete `.eso`, gzip `.sql`) lives inside `wp11_extract.py --mode real`, not in `wp11_draw_task.sh`'s own bash logic**, gated by `--no-cleanup` (default: cleanup runs on VERIFIED). Item 4's prose describes the overall behaviour ("run wp11_extract.py... Only if VERIFIED: delete...") without saying which file does the deleting, and item 7 explicitly asks for "a `--no-cleanup` guard" on `wp11_extract.py` itself for the real-directory selftest — a flag that only makes sense if `wp11_extract.py` is the thing capable of deleting. Putting it there also means `wp11_draw_task.sh` doesn't have to re-derive which files belong to which task; it exits with `wp11_extract.py`'s own exit code either way, matching item 4's "the task exits with the extraction's exit code". `wp11_draw_task.sh` still prints `du -sh` on the task's `NUS_RCk/` dir before and after the extract call, satisfying "print... the task dir size before/after".
3. **A cell with mean ≤ 0 makes the WHOLE block NOT_EVALUABLE, not just that one cell.** The spec's per-cell line ("mean <= 0 -> cell NOT_EVALUABLE") could be read as "drop this cell from the count, keep scoring the rest" or "the block can't be scored at all". Item 7's own selftest case (iv), "a cell with mean 0 -> NOT_EVALUABLE", names a single top-level verdict with no qualifier, which only matches the second reading (a per-cell reading would produce CONTINUE or CAP_REACHED_TARGET_UNMET, since 59/60 met is still a real "not-all-met" outcome, never bare "NOT_EVALUABLE"). Implemented and selftest-confirmed as block-level.
4. **`wp11_quota_check.py`'s free-space arithmetic uses min(all size tokens)=used, max=limit, not "largest, second-largest".** `quota -s` conventionally prints (blocks-used, soft-quota, hard-limit) with soft and hard often equal — "second-largest" ties the limit in that common case and silently reports 0 free (caught locally, see Verified). Never having seen real `quota -s` output (not run — `quota` is not an allowed login-node command, and this parser only runs inside a submitted job), this is the most defensible generic heuristic, not a verified fact; flagged again below.
5. Task-log path for a (block, neighbourhood) task, needed by `wp11_stoprule.py`'s VERIFIED check and by the STOP-time `scancel`, is derived from `job_ids.txt`'s `LIGHT`/`HEAVY` parent array job id plus the same block-major task-id arithmetic as `wp11_draw_task.sh`'s own mapping (`(block-1)*4+(rc-1)` for LIGHT, `(block-1)*2+(0|1)` for HEAVY) — not separately recorded anywhere. If the manager submits the arrays with any different `--array=` layout or ordering than block-major, this mapping (and the log paths / scancel targets it produces) breaks silently. Flagged for the manager to confirm at submission time.

## Next
- Manager reads `/speed-scratch/o_iseri/1J_rerun/logs/wp11_selftest_1342170.out` for `STOPRULE SELFTEST SUMMARY` and `WP11 EXTRACT SELFTEST SUMMARY` (both expect 0 unexpected).
- Manager reads `/speed-scratch/o_iseri/1J_rerun/logs/wp11_swap_probe_1342171.out` for `SWAP CHECK: PASS` and `WP11 PROBE VERDICT: PASS` once 1342160 and 1342163 have both left the queue.
- Only if selftest PASS + probe PASS + Gate 4 PASS + workers-check PASS: manager submits the LIGHT/HEAVY `wp11_draw_task.sh` arrays (writing `job_ids.txt` `LIGHT`/`HEAVY` lines first) and, per completed block, `wp11_scorer.sh` (writing `job_ids.txt` `SCORER <b>` lines) with `--mem` set from the workers-check's measured MaxRSS.
- Before trusting the disk pre-flight for real, sanity-check `wp11_quota_check.py`'s parse against one real `quota -s` transcript captured from inside a job (Decision 4).

## WHAT I DID NOT VERIFY
- Did not run `wp11_probe.py`, `wp11_extract.py --mode real`, `wp11_draw_task.sh`, `wp11_stoprule.py --mode real`, or `wp11_scorer.sh` on the cluster — only the pure-python `wp11_stoprule.py --mode selftest` was actually executed (locally). Everything else is submitted-but-not-yet-read (items 2, 7) or built-but-not-submitted (items 3-6), per the task doc's own instruction not to wait/poll.
- Never saw real `quota -s` output (not an allowed login-node command, and no job has run it yet) — `wp11_quota_check.py`'s parser is a best-effort generic heuristic (Decision 4), untested against the real format.
- Never confirmed `eppy`/IDD parsing succeeds inside `wp11_probe.py` for `NUS_RC1` with EnergyPlus itself no-op'd — the WP10 probe deliberately avoided calling the full `_run_mc_neighbourhood` for this reason (heavier IDF-prep code path); WP11's probe calls it in full per the task doc's own spec, accepting that risk. If it errors, the probe's per-case `status`/`error` print will show it, but the specific failure mode was not pre-checked against `integration.py`/`neighbourhood.py` source (not read this session).
- Did not verify scipy is present/absent in the cluster venv, nor exercised the ImportError (table-only) fallback path in `t_critical()` — only the scipy-present path ran locally.
- `wp11_stoprule.py`'s C1 default-vs-block-1 comparison and its "read from per_draw_eui.csv if the sql is already gzipped" fallback were written from the spec and never exercised against a real gzipped `.sql.gz` (no block has run yet).
- Did not verify `read_aggregated_means()`'s column-parsing (`"<scenario>_mean"` suffix stripping) against a real `aggregated_eui.csv` beyond reading `_flush_aggregated_csv`'s source; no real file was opened this session (only source code was read).
