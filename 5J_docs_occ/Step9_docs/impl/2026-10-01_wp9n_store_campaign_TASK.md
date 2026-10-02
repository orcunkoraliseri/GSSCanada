# 5J Step 9n: build the Model A store from campaign results (task doc for a fresh employee)

Written 2026-10-01 20:30 EDT by the 5J manager. Rules (binding, read in full first): `Step9_docs/outputs_step9/step9_rules.md`
(SEALED 20:17; R1 test-id rule, R3 integrity, R9 store). Parents: `Step9_docs/impl/2026-10-01_wp9g_store.md` (store builder +
extractor, manager read 17:58), `Step9_docs/impl/2026-10-01_wp9k_final_base_check.md` (store re-test on the final base, manager
read 19:34), `Step9_docs/impl/2026-10-01_wp9l_campaign_madrid.md` (campaign runner: what each run keeps, manager read 20:18).
Log `Step9_docs/5thJ_09_modelA.md` (entries from 19:30). State file you keep (new): `Step9_docs/impl/2026-10-01_wp9n_store_campaign.md`
(Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
The Madrid campaign (Speed array 1409235, 8,616 runs, about 7 days) keeps per run only: err, eplustbl.csv, the summary json, the
arrays extracted by `a9_extract.py` (hourly per-zone targets + zone map), the IDF and the series (gzip). The big EnergyPlus csv is
deleted. The 9g store builder (`tools/speed/a9_store.py`) was tested on run folders that still had `eplusout.csv`. Training must be
able to start the day the campaign ends, so the store must build from what the campaign keeps.

## Build
1. Read `a9_store.py` and `a9_campaign_task.py` (local `tools/speed/`) and write down, in the state file, which inputs the store
   needs and where each comes from in a campaign result (file:line). If something the store needs is NOT kept by the campaign,
   STOP and write it under Decisions as a blocker with the exact missing item (the manager decides; do not change the runner).
2. Add (additive, old behaviour reachable) a campaign mode to the store builder: input = a plan manifest + `results/`; uses only
   runs whose status is CLEAN; **never opens a test-pool run (`pool == test`) or any run of a test building**, and logs every id it
   opens to the open log as the 9g guard does (R1: test runs are read only by the one scoring job); writes the store layout of R9
   under a given output folder; incremental (a re-run adds new clean runs, skips ones already stored with the same result md5).
3. Fix the store check `heating_column_unique_by_position` (9k read): the substring rule matched both `Supply Air Total Heating
   Energy` and `Zone Total Heating Energy`; match the exact supply-air label. Show it passing on the 9k case and failing on a
   planted header list with two exact supply-air columns.

## Test (desktop only; at most 8 worker processes; Speed CPUs are fully used by the campaign, do NOT submit Speed jobs)
Copy from Speed with `scp` (single named files or `scp -r` of named run folders only, no wildcard): the 36 smoke results of
`/speed-scratch/o_iseri/5J/modelA/campaign/manifests/smoke_ES-MAD-BERRUGUETE.csv` (result json + extracted arrays + whatever step 1
shows the store needs) into a NEW local folder `Step9_docs/impl/wp9n/smoke_copy/`. Build the store there. Checks printed
(PASS / FAIL / NOT_EVALUABLE, each seen failing once):
* stored runs = the clean, non-test smoke runs (count them from the manifest + result statuses first); not-clean runs refused by name;
* test guard: every test-pool run and every run of test building 4a1eb42e7c488fc0 refused and absent from the open log; a planted
  call that asks for a test id is refused;
* G-c3 in store (equipment = design x series) and one re-derivation of heating for one flat from the kept arrays;
* incremental: second build adds 0 runs; after deleting one stored run, the next build adds exactly 1;
* SIZE line (MB per flat-year) against R9's 0.229.

## Rules (binding)
* UK licence: never open, list, copy or pass any UK path, file or argument (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`, `_uk`).
* No folder-wide or repo-wide search, no recursive listing of folders you did not create, no wildcard; name files in full.
* Never python on the Speed login node; on Speed only `ls`/`cat`/`head`/`tail`/`scp` of named files in the campaign folders.
* Write only: `tools/speed/a9_store.py` (keep a copy as `a9_store_pre9n.py`), new local folder `Step9_docs/impl/wp9n/`, your state
  file. Never write on Speed.
* No gate relaxed; a not-clean run is refused and listed, never dropped silently.

## Done means
Inputs table written; campaign mode built; every check above printed with its seen-failing case; a `Next` telling the manager the
exact Speed command to build the store once the campaign check 1409266 is read. End with "state written to <path>".
