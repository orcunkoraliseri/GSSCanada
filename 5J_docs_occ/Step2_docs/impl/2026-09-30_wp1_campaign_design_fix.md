# WP1 campaign design FIX (3 distinct flats per household) - implementation state
Task doc:   Step2_docs/impl/2026-09-30_wp1_campaign_design_fix_TASK.md
Status:     DONE (Wed Sep 30 16:35:59 EDT 2026)
Speed root: R=/speed-scratch/o_iseri/5J/campaign_prep/
Local copies of the Speed scripts (the record): tools/speed/{cp_partA_tabula,cd_design,cd_gates,cd_timing_build,cd_arith,cd_extract_timing,cd_fix_compare}.py, *.sbatch (design, gates, partA, timing, fix_step1)
Backups on Speed: cd_design.py.v1_2026-09-30, cd_gates.py.v1_2026-09-30 (made before any edit)

## Ledger
(append-only)
- 1404140 . fix step A: backup old tables (md5 es 84218a41..., it 7c517ba1...), py_compile, NEW gates on OLD tables . COMPLETED 0:0 3 s . R/logs/fix1_1404140.out . C1_distinct FAIL both countries (es 217 pairs, it 172 pairs), C1_slots PASS

- 1404141 . fix step B: flag OFF into scratch (reproduces v1 md5 byte for byte, es+it PASS), flag ON writes new tables, old/new compare, all 8 gates + 8 seen-failing on new tables . COMPLETED 0:0 6 s . R/logs/fix2_1404141.out . SUMMARY PASS=16 FAIL=0, SEENFAIL 8/8, REPAIR_STUCK_COUNT 0

## Verified (read from the Speed logs fix1_1404140.out, fix2_1404141.out; copies in outputs_step2/)
- C1_distinct on the OLD tables FAILS (seen failing on real data): Spain 217 (building, household) pairs below the bar in every climate (651 building x climate x household), Italy 172 (516), in es_B21..B39 and it_B21..B40 (it_B37 is clean). es_B21: 10 households (as the manager found). C1_slots (old C1) PASSES on the same tables.
- Old tables preserved: campaign_runs_{es,it}.v1_2026-09-30.csv (md5 es 84218a416b241db55617c9533c85d4a8, it 7c517ba1f1f50cb82be4e33978f9b7bc). The script with the flag OFF reproduces them byte for byte.
- Repair swaps: 380 (Spain 219, Italy 161), REPAIR_STUCK 0. Old slot-clash swaps unchanged: 136 (49 backward).
- Old vs new: run counts identical in every country, class, pool cell (Spain 4,768, Italy 4,501, incl. 100 replicates and 120 B0); run_id order, all columns except placement, and slots per household per building identical; placement differs in 484 (es) and 328 (it) rows, all MFH/AB.
- Gates on NEW tables: C1_slots, C1_distinct, C2..C7 all PASS both countries (16 of 16); seen-failing 8 of 8 fired (C1_distinct planted: a household repeating flat 0 in two runs of es_B21 -> 1 pair below the bar).
- New md5: campaign_runs_es.csv b4d5b42eb6220b25daef7f2a7cff18d1, campaign_runs_it.csv e9ddcf105c2aca2958439e70cd8e3dfb. splits_households 797a9068..., splits_buildings 7e3bf4ed..., k_table e07bd579... unchanged (equal to the values in campaign_design.md).
- Position variety (new tables, first climate; INFO in fix2 log): e.g. es AB distinct floors per household 2:77, 3:421, 4:81, 5:5, 6:13, 7:3; es AB households with at least one end and one middle flat: 36 of 600 (most Spanish AB buildings have k 1-2, so no middle flat exists); it MFH 370 of 600, it AB 419 of 600.
- outputs_step2/campaign_design.md updated (md5 list, placement rule with the repair, gate line). Splits, counts, timing and disk sections untouched.

## Decisions (not in the task doc)
- cd_design.py: flag --distinct-flats (default on) / --no-distinct-flats (old v1), --outdir (write dir; inputs still read from R/out/). cd_gates.py: old C1 = C1_slots; new C1_distinct; --runs-pattern, --no-seenfail.
- Repair condition for h2: its distinct flats after the swap >= min(3, n) (strict reading); h scan order = pool order; a swap inside the same run (b = a) is allowed. Never triggered REPAIR_STUCK.
- Replicate rows (run 1 of the dev pool) follow the repaired placement (same inputs, new who-sits-where); the replicate input choice is unchanged.

## Next
Manager verifies (distinct flats on es_B21 and one more building, own job; run counts; md5); manager freezes the design.

## WHAT I DID NOT VERIFY
- Nothing was re-derived independently of cd_gates.py's own distinct-flat count (same code counts in the gate and in the INFO); the manager's own job is the independent check.
- The timing, disk and arrays sections of campaign_design.md were not re-checked (only confirmed not edited); the changed placements do not change run counts or zone counts, so they should be unchanged.
- tools/speed/ copies of the Speed scripts are the current Speed copies (scp), not byte-compared after copy; cd_arith.py, cd_timing_build.py, cd_extract_timing.py, cp_partA_tabula.py were copied unchanged.
- Whether B0 slot `<cc>_avg` and the households.csv input are still the same as staged (households task not checked).
- Script syntax was checked only by py_compile on Speed (PYCOMPILE OK), not by a local interpreter.

## Verified (manager) 2026-09-30 16:37 EDT (from `date`): fix ACCEPTED, design FROZEN
Own Speed job 1404143 (`/speed-scratch/o_iseri/5J/mz_pilot/mgr/mgr_verify_cd2.py`, own code) over EVERY MFH/AB
building, pool and climate: new tables 0 (building, household) pairs below min(3, n) distinct flats, 0 mixed-pool
runs, 0 runs with a repeated household, every pool household present; v1 tables 651 (es) and 516 (it) = 217 and 172
x 3 climates, as reported. Rows 4,768 / 4,501 unchanged. md5 inside a Speed job equal to the reported ones; the
splits and households.csv unchanged. Design frozen (Progress Log 16:38).
