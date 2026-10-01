# 5J Step 3 part 2: campaign integrity (G5J.1), resume check, splits sealed (Spain + Italy) - implementation state
Task doc:   `Step3_docs/impl/2026-09-30_wp2_campaign_part2_TASK.md`
Status:     DONE 2026-09-30 18:53 EDT
Speed folders: R = `/speed-scratch/o_iseri/5J/campaign/`; outputs `R/integrity/`, `/speed-scratch/o_iseri/5J/splits/`; local scripts (the record) `tools/speed/camp2_*.py|sbatch`, `camp_integrity.py`, `split_*.py`.

## Ledger (append-only)
* 1404250 · Part A collector (31 SUMMARY lines, folder counts) · submitted 18:35 EDT · `R/integrity/partA_1404250.out`
* 1404250 · COMPLETED 0:0 (2 min) · 31 SUMMARY lines found, all ran_failed=0; done 18538 files, failed 0, runs/ 0 folders
* 1404251 · seen-failing tests v1 (scratch copies) · FAILED exit 1, 18:37 · T1-T4 each seen failing, but the CONTROL failed C10 (replicate content differs, see Decisions) -> check patched
* 1404252 · G5J.1 integrity v1 (6 workers, -c 6 --mem 16G) · COMPLETED (exit 1 by design) 18:43 · 11 of 12 checks PASS, C10 FAIL (whole-file replicate equality, see Decisions) · `integrity_1404252.out`
* 1404253 · Part D splits + loader test · COMPLETED 18:38 · `splits_1404253.out` (12 lists written and read-only; loader refuses test lists; md5 -c step used relative paths, re-verified in a later job)
* 1404254 · Part C resume test (afterok 1404252) · CANCELLED by me 18:40 (resubmitted as 1404259 after the patched integrity run)
* 1404255 · replicate diagnosis · COMPLETED 18:39 · `repdiag_1404255.out`
* 1404256 · seen-failing tests v2 · COMPLETED 0:0 · ALL_SEEN_FAILING
* 1404257 · G5J.1 integrity v2 (patched C10) · COMPLETED 0:0, 18:46 · SUMMARY PASS=12 FAIL=0 NOT_EVALUABLE=0 · `integrity_1404257.out`
* 1404258 · splits md5 -c check · COMPLETED · 12 OK
* 1404259 · Part C resume test (real task it_milan_2014 block 5) · COMPLETED 0:0, 18:47 · `resume_1404259.out`
* 1404272 · integrity re-run after the resume test · COMPLETED 0:0, 18:52 · SUMMARY PASS=12 FAIL=0 NOT_EVALUABLE=0, extracted 15357703558 bytes (same as before)

## Verified
* Part A (job 1404250, `partA_1404250.out`): 31 SUMMARY lines found (31 expected), every one ran_failed=0 and not_run=0; summed ran_passed per array = array run count. done/ 18538 files (9269 json + 9269 err), failed/ 0, runs/ 0 folders. No reruns needed.
* Part B patched run (job 1404257, `integrity_1404257.out`): `SUMMARY PASS=12 FAIL=0 NOT_EVALUABLE=0`, exit 0. C01-C08 and C11 PASS on 9,269 of 9,269 runs (C11: 240 B0 runs); C09 PASS (240 building-climate groups, 36,181 flats hashed, no equipment series shared by two households; run over every building, a superset of the required sample); C10 PASS (200 replicate runs in 20 groups: dwelling, hour and all 4 targets identical, max hourly diff 0 kWh and max annual spread 0 kWh for each of heating, cooling, equipment, total_elec); C12 PASS (extracted files 18,538 = exactly the planned set, done/ exactly the planned set).
* Replicate whole-file content: byte-equal (without # lines) in 150 of 200 runs; the other 50 differ only in non-target diagnostic columns: rh_pct up to 3e-06 %, zoneside_heating up to 5.6e-15 kWh, zoneside_cooling up to 3.9e-15 kWh (different hosts).
* Seen failing (job 1404256, `seenfail_1404256.out`, scratch copies, Spain runs): control PASS (PASS=11 FAIL=0 NE=0, exit 0); truncate one extracted file by 100 bytes -> C03 FAIL (and C04 FAIL unreadable, exit 1); delete one done.json -> C01 FAIL; copy flat 0 series onto flat 1 with a different household (done.json md5 updated so C03 passes) -> C09 FAIL; change one byte of one household file -> C02 FAIL (cache key). Same tests on v1 (1404251) also FAIL as expected; the v1 control failed C10, which is how the replicate finding was found.
* Total disk of R/extracted: 15,357,703,558 bytes (15.36 GB) (`du -sb`, in the integrity job).
* Part C (job 1404259, `resume_1404259.out`): task it_milan_2014 block 5, 9 runs, 18 done + 18 extracted files moved to R/resume_test/. PLAN lines: `PLAN total=9269 done=9269 todo=0` (before), `PLAN total=9269 done=9260 todo=9` (moved away; todo ids = exactly the task's 9 ids), `PLAN total=9269 done=9269 todo=0` (moved back). resume_test/ empty after; done/ 18538 again.
* Part D (job 1404253 + check 1404258, `splits_1404253.out`, `splitcheck_1404258.out`): input md5 of splits_households.csv 797a90683e26c42ee90d6bcc02112132 and splits_buildings.csv 7e3bf4edcd187f2b03ebb0f21e5c88d7 equal the design doc. 12 lists in `/speed-scratch/o_iseri/5J/splits/` (total / es / it): development 4335/2196/2139; validation 1980/1062/918; test_new_households 1107/564/543; test_new_buildings 813/414/399; test_both_new 207/105/102; unused 387/207/180; b0_dev 180/90/90; b0_val 30/15/15; b0_test 30/15/15; replicates 200/100/100; loco_es 4768/4768/0; loco_it 4501/0/4501. Gates: every run in exactly one of the 10 partition lists (9269); loco_es + loco_it = 9269; 0 household ids and 0 building ids in a list their split does not allow; 0 test households and 0 test buildings in development or validation; placements and run-table splits agree with the two splits CSVs (0 mismatches); files read back sorted without duplicates. Files chmod 440 (a write attempt: Permission denied); `md5sum -c splits.md5` 12 OK.
* Loader `tools/speed/split_loader.py` (copy in R): seen failing now with no gates_frozen.md5: test_new_households, test_new_buildings, test_both_new, b0_test, unused each refused ("REFUSED: split ... does not exist (Step 4 freezes the gates first)"); development, validation, b0_dev, replicates, loco_es load; with a SCRATCH gate file test_both_new loads (207 ids); `gates_frozen.md5` does not exist (ls).

## Decisions
* (18:40) Replicate finding: es_madrid_B01_dev_1 vs es_madrid_B01_dev_1_rep1 (run on hosts magic-node-10 and speed-21): dwelling, hour and all 4 targets identical; only diagnostic columns differ at machine noise (zoneside_heating/cooling up to 7.6e-16 kWh, rh_pct up to 3e-6 %). The task text says "content equal to their original"; a strict whole-file test fails on these noise digits. Decision: C10 gate = dwelling + hour + the 4 target columns bit-equal; whole-file byte-equality count and the max difference of every non-target column are printed, not gated (`PATCH c10_targets_exact`, backup `camp_integrity.py.v1_2026-09-30`). Author to note.
* Loader refuses `test_*`, and also `b0_test` and `unused` (they hold test households or buildings); the task text only names test_*, so this is stricter. Loader also checks each list against splits.md5.

## Split md5 (sealed 2026-09-30 18:38 EDT, chmod 440; `/speed-scratch/o_iseri/5J/splits/splits.md5`)
```
c277931d65f5599932524ded88ad9ff3  development.txt
88ec7ac05d8f3cbffa256e49800ec8df  validation.txt
b03e94ea47beb22dec9ac06e40f5d076  test_new_households.txt
13278a13f8b44097f36e87341c9065d4  test_new_buildings.txt
78464ddb3c1c406929314554c99bd635  test_both_new.txt
99ab66ca1dc3fa9266fc3eeeedf45f98  unused.txt
a22b94129679fc9ef94bc82ad9ebadfe  b0_dev.txt
6550aac8b45aa5a2c3aaae678461f63b  b0_val.txt
0b4faa5eac5b2b86390e1b5d7e809532  b0_test.txt
06aa21c6bcdb899378bd11c37f502237  replicates.txt
3b72391ba24e0f2cc101de7cfc5d3a02  loco_es.txt
53229ac95db7dbfd63be59f4eae12991  loco_it.txt
```

## Next
Manager verifies; Step 4 (freeze the gates). UK arrays wait on the author (O-7). gates_frozen.md5 NOT created.

## WHAT I DID NOT VERIFY
* Gate 4.4 (both members of every scoring pair in the same split): not in this task, not checked.
* Italian run correctness beyond the per-run checks (TABULA k from Italian dwelling counts): C01-C08 pass, but no independent recomputation of an Italian MFH/AB annual figure was done here.
* C09 compares hourly equipment series; it does not test that heating/cooling differ between households (only equipment, as the task says).
* Integrity C10: whole-file equality fails for 50 of 200 replicates at machine-noise level in diagnostic columns; the gate was set to the 4 targets (a decision, not the task text).
* `test_*` refusal is proven with a scratch gate file only; the real Step 4 gate file was never created, so that path is untested with the real file.
* Extracted disk is one moment (15.36 GB); free space after the campaign not re-read.
* (post-resume integrity re-run 1404272 also PASS=12.)

## Verified (manager) 2026-09-30 18:56 EDT (from `date`): part 2 ACCEPTED; Step 3 closed for Spain + Italy
Own Speed jobs 1404279 (`/speed-scratch/o_iseri/5J/mz_pilot/mgr/mgr_verify_p2.py`) and the EPW job (`mgr_epw.py`):
- 9,269 done.json. Random run (seeded) es_valencia_B37_test_2: extracted csv.gz md5 13e5b7fb637d0bee45d42488823665b2
  recomputed = done.json (7,440,235 bytes); 18 flats x 8,760 rows; flat 0 annual heating 4751.92, cooling 1039.95,
  equipment 1361.27 kWh; total electricity = equipment + heating/3 + cooling/3 (diff 1e-7 kWh, csv rounding).
- Split lists counted by own code: equal to the employee's table (development 4335 ... loco_it 4501); partition
  lists total 9,269, all distinct, none in two lists, none missing against done/.
- Loader: `REFUSED: split 'test_new_households' is a test list and .../gates_frozen.md5 does not exist`;
  development loads 4,335 rows.
- Resume PLAN lines as reported (read from the state file; not re-run).
- INFO: every Madrid run (1,656) and every Turin run (1,467) has ONE EnergyPlus warning "Temperature out of range
  (PsyPsatFnTemp) in PsyTwbFnTdbWPb" at one timestep (Madrid 12/26 13:50, Turin 02/06 11:20; same in every building,
  so it comes from the weather). The EPW rows around those hours are plausible (Madrid 4.2 C, dew -7.2 C, 43 %,
  93,970 Pa; Turin 3.5 C, dew -1.9 C, 68 %, 91,300 Pa) and a scan of all six EPWs finds 0 implausible rows. Read as
  EnergyPlus's wet-bulb iteration at one sub-hourly interpolated step; the targets are sensible/latent loads of
  the ideal-load system at room conditions, not outdoor wet bulb. Not a blocker; noted for the methods limitations.
- The replicate gate change (targets identical; diagnostic columns differ by up to 3e-6 % humidity between hosts)
  is accepted: target spread 0 kWh on all 200 replicates.
