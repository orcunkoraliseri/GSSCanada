# 5J Step 9k: last checks on the final base `_win_2026-10-03` before the campaign (task doc for a fresh employee)

Written 2026-10-01 18:43 EDT by the 5J manager. Parents: `Step9_docs/impl/2026-10-01_wp9i_fixedbase_writer.md` (the same writer test
on `_win_2026-10-02`, all gates as expected, aggregator `/speed-scratch/o_iseri/5J/step9c/win2fix/logs/agg_1407560.out`),
`Step9_docs/impl/2026-10-01_wp9g_store.md` (store code ACCEPTED on real output; four harness fixes listed in "Manager read of test
1407350"), `Step9_docs/impl/2026-10-01_wp9j_rebase_win3.md` (final base checked), `Step9_docs/impl/2026-10-01_wp9c_idf_writer.md`
(line 132: the 12 degenerate surfaces of 1271cddbf6bd1e8a named), log `Step9_docs/5thJ_09_modelA.md` (entries 18:37, 18:42).
State file you keep (new): `Step9_docs/impl/2026-10-01_wp9k_final_base_check.md` (Ledger, Files, Verified, Decisions, Next, WHAT
I DID NOT VERIFY).

## Why
The rules (`Step9_docs/outputs_step9/step9_rules.md`, R3) say every writer gate must pass on the CAMPAIGN base before the campaign.
9i passed on `_win_2026-10-02`; the final base is `_win_2026-10-03` (only vertex order changed). Also: EnergyPlus calls a run not
clean when a building has degenerate surfaces (Severe), and the store refuses such runs, so we must know how many buildings
carry them before the campaign is sized.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Never list `EU-11/` itself; open only `EU-11/ES-MAD-BERRUGUETE_win_2026-10-03/` and `EU-11/IT-BOL-GALVANI2_win_2026-10-03/`
  by full name.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard of any kind** (FINDING 5J-2, 5J-4). Iterate IDFs by
  `fleet.lst` or by listing the one `idfs/` folder.
* **Compute:** desktop at most 10 processes. Speed via `sbatch` only, `-t 7-00:00:00`, `--exclude=antenna1`, at most 16 CPUs at
  once for this task; never python or loops on the login node (tcsh; write a script, scp it, `sbatch` it). Submit with
  dependencies, write the ids, end the turn. **Never wait for a job.**
* Write only: new Speed folders `/speed-scratch/o_iseri/5J/step9c/win3fix/` and `/speed-scratch/o_iseri/5J/modelA/store_test3/`
  (copy scripts from `win2fix/` and `store_test/`; never edit those), additions to `tools/5thJ_modelA_idf.py` and
  `tools/speed/a9_*.py` (old behaviour stays reachable), output folder `Step9_docs/impl/wp9k/`, your state file.
* G-c5 stays `severe == 0 and invalid/not found == 0`; no warning is whitelisted; no gate is relaxed.

## What to do
1. **Degenerate-surface count (desktop).** Write a counter that reads each IDF of both districts on `_win_2026-10-03` and flags a
   surface (wall, floor, roof, window) as degenerate when, after removing coincident vertices (distance under 0.01 m, EnergyPlus's
   tolerance as you find it stated in the EnergyPlus 23.1 documentation or source shipped on Speed; write which) and collinear
   vertices, fewer than 3 vertices remain. **Calibrate (seen failing / passing):** on `1271cddbf6bd1e8a` it must flag exactly the 12
   surfaces named in `2026-10-01_wp9c_idf_writer.md` line 132 (by name), and 0 on the other 7 buildings of 9i and 9j
   (919761afea1827b3, 0275c53572b2ff9f, 7307694dddf93fb6, 504fa19567bbc2b7, 1ef46361a8060ff9, 13c60875a803e164, b3f8d90890ff6314),
   and EnergyPlus's own count on those runs (eplusout.err "There are N degenerate surfaces" lines from the 9i run folders `step9c/win2fix/runs/` and the 9j run folders `step9c/win3/runs/`) must agree.
   If your rule cannot reproduce 12, say so and do not tune it to the answer on more than this one building without saying so.
   Then count over all 1,172 + 1,179 buildings: per district, buildings with at least one degenerate surface, how many of them are
   Model A buildings (one zone per flat), how many are already in `heldout_tinyflats_win3.csv`, and their split (dev / val / test
   from `buildsplit_win3/`). Per-building csv `wp9k/degenerate_win3.csv` (district, stem, n_degenerate, names, boundary types,
   split, heldout_tiny). Do not decide what happens to them: the manager does.
2. **Writer test on the final base (Speed).** Exactly 9i's set (6 buildings, R0 R1 D O DF OF + P1 on 504fa19567bbc2b7 + P2 on
   919761afea1827b3 = 38 runs) built with `MODELA_VINTAGE=win_2026-10-03`, `schedcheck` on every written IDF, scripts copied from
   `win2fix/` to `win3fix/` (paths changed only), array `%16`, aggregator `afterany`. Same gates and controls (G-c1..G-c5, G-c4s
   structural count, G-c7 fast setting with both controls, G-c8 with both controls, timing). Add to the aggregator: G-c4s
   (count of `EU_CoolingOff,` lines = zones + 1 in R0 and R1, = 1 in D, O, DF, OF; seen failing by reading a D file against the
   R1 expectation). Expected: as 9i, and G-c8's control walls may be missing now (walls fixed): then the control falls back to the
   "outward + 180" control and the inward-wall control prints NOT_RUN with the reason, never PASS.
3. **Store re-test on the final base (Speed),** after the writer array, on its D, O, DF, OF run folders (read only; copy them or
   point to them, never re-run EnergyPlus inside the store test if the writer runs exist): `a9_test.sbatch` copy with the four fixes
   of the 9g manager read: (1) own working folder per EnergyPlus run if any run is made; (2) `targets_<split>.npy` rows = flats rows,
   plus a check that fails on a planted extra row; (3) one heating column read by header position (and the check that the header
   at that position is the heating name); (4) extraction runs before anything deletes `eplusout.csv` (state where the writer's
   task script deletes it, and make sure the run folders you read still hold it: if the writer task deletes it, add a switch that
   keeps it for this test and for the campaign). Expected: every check PASS except the triangle runs refused by the clean rule
   (right behaviour), and the SIZE line again (MB per flat-year, with and without the fast runs).

## Done means
Item 1 with numbers and the per-building csv; items 2 and 3 submitted (array, aggregator, store test ids in the ledger) with a
`Next` naming each log and the lines a cold agent copies; nothing UK opened, listed or passed. End with "job N submitted, state
written to <path>".
