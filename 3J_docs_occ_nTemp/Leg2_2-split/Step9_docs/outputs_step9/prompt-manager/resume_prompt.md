# Resume prompt — 3J Leg-2 Step 9 report improvements

> Status as of 2026-07-06: **ALL TASKS (1–13) DONE.** Step-9 report improvements effort
> is closed out.

## Outcome

All detail lives in `Step9_docs/outputs_step9/step9_report_improvements_TASKS.md` — read it
first, it's the source of truth. Short version:

- **Tasks 1–12: DONE.** Verified clean and synced locally.
- **Task 13: DONE 2026-07-06.** §R3 residential `occ_mean`/`occ_pct_vs_2022` — Option 1
  shipped and verified: derive occupant-count post-hoc from `Occupancy_Schedule × HHSIZE`
  for 2022 + all 3 2030 bands (100% coverage), explicit documented NaN for historical
  2005/2010/2015 (only 11.7% coverage there — an unconditional gate in
  `_resid_occ_grid()` in `Step8_docs/3rdJ_08_simulation_2split_agg.py` prevents a biased
  partial-coverage mean from masquerading as a full-population value).

## What happened (for context, nothing left to do)

1. User + a second reviewer ("fable") both recommended Option 1 in
   `task13_occ_mean_gap_report.md`.
2. Implemented: unconditional historical gate in `_resid_occ_grid()` (predecessor archived
   to `Step8_docs/archive/3rdJ_08_simulation_2split_agg.20260706_preTask13gate.py`), plus a
   §R3 footnote in `Step9_docs/3rdJ_09_activityDrivenLoads_2split.py` explaining the
   historical NaN.
3. Uploaded the agg script to the cluster, submitted `run_aggregation.sh` via `sbatch` —
   **job 1068096** — `COMPLETED`, exit 0, 00:43:42 runtime, §8D scorecard 46P/1W/13I/0F
   (no regressions).
4. Downloaded the refreshed `outputs_step8/agg/*.csv`, re-ran
   `3rdJ_09_activityDrivenLoads_2split.py` locally. All 5 outputs regenerated. (Console
   scorecard print crashed on a `≥` unicode char under Windows cp1252 — cosmetic only, every
   output file was already written by that point; not fixed, noted in the Progress Log.)
5. Verified directly in `step9_scenario_response.csv`: resid `occ_mean` populated
   (1.471/1.523/1.56/1.593 for 2022/cons/hybrid/full) and blank for 2005/2010/2015 exactly as
   intended. HTML report footnote renders; embedded gate scorecard is PASS 10/WARN 1/INFO
   0/FAIL 0.
6. Marked Task 13 DONE in the TASKS doc with a closing Progress Log entry.

## Standing rules (for whatever comes next in this project)

- Tracking doc convention: append-only Progress Log entries in
  `step9_report_improvements_TASKS.md`, never edit/remove prior entries.
- Cluster hard rules still apply (`CLAUDE.md`): `sbatch` only (never blocking `srun`), no
  bare `python` on login node, ≥7-day walltime, archive predecessor scripts before overwrite,
  Haiku/Sonnet (never Opus) for monitoring/polling, ≥30 min between status checks.
- If a future task needs the console-encoding fix noted above:
  `sys.stdout.reconfigure(encoding="utf-8")` near the top of
  `3rdJ_09_activityDrivenLoads_2split.py`'s `main()` would resolve the Windows cp1252 crash
  in the final scorecard print loop — low priority, cosmetic only.
