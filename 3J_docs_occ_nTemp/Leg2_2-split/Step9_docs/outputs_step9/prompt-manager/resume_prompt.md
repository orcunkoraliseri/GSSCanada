# Resume prompt — 3J Leg-2 Step 9 report improvements

> Status as of 2026-07-06: **Tasks 1–12 are DONE. Task 13 is OPEN — 2022/2030 portion is
> UNBLOCKED, historical (2005/2010/2015) portion is BLOCKED and awaiting a user decision.**
> Read this whole file before doing anything else, especially before touching the cluster.

## Outcome so far

All detail lives in `Step9_docs/outputs_step9/step9_report_improvements_TASKS.md` — read it
first, it's the source of truth. Short version:

- **Tasks 1–12: DONE.** Unchanged from before, all verified clean and synced locally.
- **Task 13: §R3 residential `occ_mean`/`occ_pct_vs_2022` NaN.** Option 2 (derive
  occupant-count from the input occupancy schedule, no re-simulation) chosen by the user
  over option 3 (re-simulate with a real E+ output variable).

## Where option 2 currently stands

1. **2026-07-05 session's "599 households / 14.9% / 1.0% coverage" numbers were wrong** —
   measured against a stale, unrelated local directory
   (`BEM_Setup/SimResults_Step8/campaign_N50/`), not the real 3J Leg-2 campaign. Re-pulled
   the real manifests fresh via `scp` from the actual cluster path
   (`/speed-scratch/o_iseri/step8_2split/campaign/`, now archived locally in
   `Step8_docs/outputs_step8/campaign_N50/`): **1,163** distinct real `sim_hh_id`s.
2. **2022 + all 3 2030 scenarios: 100% coverage confirmed (1,163/1,163).** The "same-day
   file revision" hypothesis from 2026-07-05 is refuted (all 3 timestamped variants of each
   file are byte-identical in household-ID membership). **Option 2 works cleanly for 5 of 7
   scenario-years — this is the real, shippable fix** for the large majority of NaN rows.
3. **Historical (2005/2010/2015): still blocked — only 11.7% overlap (136/1,163), and it's
   a harder problem than file-revision timing.** Confirmed the historical-schedule
   generator (`3rdJ_08A_gen_historical_schedules.py`) is fully deterministic (re-ran it,
   byte-identical output) and only ever matches ~2,883 of the 23,211-household stock by
   design (demographic-tier matching, most households have no valid historical diary
   match) — that part is expected, not a bug. But `main.py`'s campaign sampler
   (`run_step8_paired_mc`, L2045-2064) provably requires every *sampled* household to exist
   in the historical schedule dict too, and project memory confirms the historical CSVs did
   exist on the cluster when the real campaign completed (job 1029756, 2026-06-30) — so the
   population used at run-time was real but is **not reproducible from what's in the repo
   today**. Best current explanation: those exact files were deleted from cluster scratch
   sometime after 2026-06-30, before Task 13 started looking on 2026-07-05, and can't be
   regenerated to match. Likely **unrecoverable**, though not 100% certain without cluster
   job logs from that window.
4. **Still no cluster job submitted for Task 13 — everything above was local/read-only**
   (an `scp` pull of small manifest CSVs, local re-runs of a pandas-only script,
   `diff`/`comm` on local files). `3rdJ_08_simulation_2split_agg.py`'s fix
   (`_sched_path()`/`_resid_occ_lookup()`/`_resid_occ_grid()`) is still local-only, not
   uploaded.

## Decision needed from the user before resuming

Three options for the historical (2005/2010/2015) gap — pick one, or say if there's a 4th:

- **(A) Ship now, 2022/2030 only.** Submit the aggregation fix as-is; residential
  `occ_mean`/`occ_pct_vs_2022` populate correctly for 2022 + 2030×3, historical rows stay
  NaN with a documented caveat in the report/companion doc. Fastest path, no further
  cluster/local digging.
- **(B) Keep digging for the lost original historical population.** Would mean chasing
  cluster job logs/state from the 2026-06-30 window (job 1029756 and whatever preceded it)
  to see if the original historical CSVs (or a record of exactly what they contained) are
  recoverable anywhere. Uncertain payoff — may genuinely be gone.
- **(C) Fall back to option 3 for historical years only** (re-simulate 2005/2010/2015
  residential runs with a real `Zone People Occupant Count` output request), leaving
  2022/2030 on the already-working option-2 derivation. Re-opens the "recover 2J's
  Default-vs-Activity-driven figures" side-question too, if relevant.

## Standing rules for this effort

- Tracking doc is `Step9_docs/outputs_step9/step9_report_improvements_TASKS.md` — append
  new tasks/Progress Log entries there, not in the narrative doc
  (`3rdJ_09_activityDrivenLoads_2split.md`), per explicit user preference.
- Cluster hard rules still apply (`CLAUDE.md`): `sbatch` only (never blocking `srun`),
  ≥7-day walltime, archive predecessor scripts before overwrite, Haiku/Sonnet (never Opus)
  for monitoring/polling, ≥30 min between status checks.
- Do not upload/run anything on the cluster for Task 13 until the user picks A/B/C above —
  submitting now would ship the historical NaN gap silently rather than as a documented,
  chosen tradeoff.
