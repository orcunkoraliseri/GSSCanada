# 5J Step 9l: Model A campaign runner, Madrid first (task doc for a fresh employee)

Written 2026-10-01 18:57 EDT by the 5J manager. Rules (binding, read in full first): `Step9_docs/outputs_step9/step9_rules.md`
(R1 lists, R2 runs and settings, R3 integrity, R9 store, R10 size). Parents: `Step9_docs/impl/2026-10-01_wp9i_fixedbase_writer.md`
(writer test scripts `/speed-scratch/o_iseri/5J/step9c/win2fix/`: `win_task.sh`, `win_summ.py`), `Step9_docs/impl/2026-10-01_wp9k_final_base_check.md`
(same on the final base, `/speed-scratch/o_iseri/5J/step9c/win3fix/`), `Step9_docs/impl/2026-10-01_wp9d_households.md` (household
builder `tools/5thJ_modelA_households.py`, Speed `/speed-scratch/o_iseri/5J/modelA/households/`), `Step9_docs/impl/2026-10-01_wp9g_store.md`
(extractor `tools/speed/a9_extract.py`; four harness fixes), pilot average household `Step2_docs/impl/2026-09-30_wp1_it_households.md`
and `Step2_docs/impl/2026-09-29_wp1_households_v2.md` (the `<cc>_avg` rule). Log `Step9_docs/5thJ_09_modelA.md` (entries from 18:37).
State file you keep (new): `Step9_docs/impl/2026-10-01_wp9l_campaign_madrid.md` (Ledger, Files, Verified, Decisions, Next, WHAT I
DID NOT VERIFY).

## Scope
Build the code that runs the whole Model A plan, district by district, and prove it on a SMOKE batch of Madrid buildings. The
manager reads the smoke batch and the 9k checks, seals the rules, and then submits the full Madrid array with your script.
Bologna is NOT run (it waits for OpenUBEM's `_win_2026-10-04` tag); the code takes the district as an argument so Bologna is a
one-line switch later.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Never list `EU-11/` itself; open only the two district folders of `_win_2026-10-03` by full name. The household builder's
  corpus guard and `assert_not_uk` stay on.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard of any kind** (FINDING 5J-2, 5J-4).
* **Compute:** Speed via `sbatch` only, `-t 7-00:00:00`, `--exclude=antenna1`; the smoke batch uses at most 12 CPUs at once (9k
  jobs may still hold 16; the 5J cap is 32 in total; check `squeue -u o_iseri` before submitting and stay under 32). Never python
  or loops on the login node (tcsh). Desktop at most 10 processes. **Never wait for a job:** submit, write the ids, end the turn.
* Write only: new Speed folder `/speed-scratch/o_iseri/5J/modelA/campaign/` (code, manifests, runs, results, logs), new local files
  `tools/speed/a9_campaign_plan.py`, `tools/speed/a9_campaign_task.sh`, `tools/speed/a9_campaign_task.py` (names may differ; list
  them), additions to `tools/5thJ_modelA_households.py` and `tools/5thJ_modelA_idf.py` (old behaviour stays reachable), your
  state file. Never edit `win/`, `win2fix/`, `win3fix/`, `store_test*/`.
* G-c5 stays `severe == 0 and invalid/not found == 0`; nothing whitelisted; no gate relaxed; a not-clean run is kept and reported
  by name, never dropped silently.

## What to build
1. **Plan (manifest)** `a9_campaign_plan.py <district>`: from the sealed building lists (`Step9_docs/impl/buildsplit_win3/<D>_<split>.csv`,
   read by full name) minus `Step9_docs/impl/heldout_tinyflats_win3.csv`, one row per run, columns at least: run_id, district, stem,
   building_split, pool (dev / val / test / b0 / def), r, mode (occupancy / default), n_flats, seed, src_idf, src_idf_md5. Runs per
   building exactly as R2 (dev building: dev 1-3, val 1-2, test 1-2, b0, def = 9; val building: dev 1-2, val 1-2, b0, def = 6; test
   building: dev 1-2, test 1-2, b0, def = 6). `run_id = <D>_<stem>_<pool>_<r>` (b0 and def: r = 0). Seeds from the household
   builder's `run_seed_of(run_id)`. **Check printed:** Madrid 9,201 rows; buildings 795 / 172 / 169; plan md5 written. Seen failing:
   a planted held-out stem left in the list must make the count check fail.
2. **Task** (one array task = one run, 1 CPU): (a) skip only if `results/<run_id>.json` exists AND its stored src_idf_md5,
   writer md5, household-code md5 and placement md5 equal the current ones (otherwise re-run; rule R1 (d); seen failing: change one
   md5 in a copy of a result and show the task re-runs); (b) households: `assign_flats` for the run's split with the
   no-repeat rule (no flat gets the same household twice within one pool of one building: keep a per-building, per-pool record of
   earlier runs' placements; the dev 1-3 runs of one building therefore need the placements of their siblings; make placement
   deterministic from the plan so every task can recompute its siblings' placements without reading their outputs), then
   `household_year` per household with the run seed, series written under the run folder; b0 = the pilot's average-household rule
   computed from DEV households only (write how; one series reused in every flat); def = no household (writer mode default);
   (c) write the IDF with `tools/5thJ_modelA_idf.py write` (`MODELA_VINTAGE=win_2026-10-03`, **no `--fast`**: OpenUBEM settings,
   author ruling 18:55), then `schedcheck`; (d) EnergyPlus 23.1 in the run's OWN working folder; (e) summarize (G-c5 clean status,
   Severe lines, annual heating / cooling / equipment, wall seconds) and **extract before anything is deleted** with `a9_extract.py`
   (hourly per-zone targets + the zone map) into `results/<run_id>.*`; (f) purity read back from the written draw files (`purity`),
   G-c3 equipment = design x series on occupancy runs; (g) then delete the large EnergyPlus files (eso, sql, csv, audit, shd) and
   keep err, eplustbl.csv, the summary json, the extracted arrays, the IDF (gzip) and the series (gzip). Write per-run bytes kept.
3. **Array script**: `sbatch --array=<from>-<to>%<k>` over manifest rows (MaxArraySize 10001, so Madrid fits one array; write the
   exact command the manager will use with `%32` and the dependency-free form). Per-task log `logs/t_<jobid>_<task>.out`.
4. **Check job** (`a9_campaign_check`): reads the manifest and `results/`: rows done / missing / not clean (by name) / purity
   violations / G-c3 failures / src md5 mismatches, CPU seconds per district, bytes kept; exit code meaning written down (0 = all
   sections ran; nonzero = crashed = NOT_EVALUABLE).

## Smoke batch (submit, do not wait)
Madrid, 4 buildings, every run of each: one small dev building, one large dev building (most flats in the dev list), one val, one
test building; plus the triangle building `1271cddbf6bd1e8a` if it is in the plan (its runs must come out NOT CLEAN by name).
Run the check job with `afterany`. Also submit, after the smoke array, a re-submission of the SAME array (expected: every task
skips) and a check job after it (expected: same result, zero re-runs). Write every id in the ledger.

## Done means
Plan count checks printed (9,201) and seen failing; skip rule seen failing on a copied result; smoke array + check + re-submission
+ second check submitted with ids; a `Next` naming the logs and lines a cold agent copies, and the exact full-Madrid submit
command for the manager. Nothing UK opened, listed or passed. End with "job N submitted, state written to <path>".
