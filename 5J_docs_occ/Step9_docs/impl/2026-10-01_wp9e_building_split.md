# 5J Step 9e building split: implementation state
Task doc:   Step9_docs/impl/2026-10-01_wp9e_building_split_TASK.md
Status:     DONE (employee part; manager seals)

## Ledger
* Desktop, one `py` process, no Speed job. Script `5J_docs_occ/tools/5thJ_modelA_buildsplit.py` (imports `rng_for` from `5thJ_design_tables.py`). Run exit 0, "ALL CHECKS PASS".
* Outputs in `Step9_docs/impl/buildsplit/`: six lists `<district>_<split>.csv` and `strata.csv`.

## Verified (all numbers read from the script's own output)
Wall table: 2,351 rows read, 0 in other districts; unusable (zone_map_reason set): Madrid 7, Bologna 8. Usable: Madrid 1,165, Bologna 1,171.
List md5 (seed 9102; lists: n):
* ES-MAD-BERRUGUETE dev 816 d6ada695904d16c81da1a13059dbfc9d; val 176 ddf1cc4b8f62717a4a0773d022210fdd; test 173 c4b0e46c3915dfa039eec08ef9da4c5c
* IT-BOL-GALVANI2 dev 820 55410d3538802ee66ef7ea636e008e47; val 176 b9d4f6d9318d5a0e57027ea8120cfd20; test 175 71b57e8ee5e3e76ba20288d8bf5eee78
* strata.csv 4dfec6eb5f9da455a5ae317ed6b05b6f

Strata (district class band n dev val test):
Madrid: AB 1 160 112/24/24; AB 2-8 417 292/63/62; AB 9-24 406 284/61/61; AB 25+ 111 78/17/16; TH 1 50 35/8/7; MFH 2-8 10 7/2/1; MFH 9-24 2 1/0/1; SFH 1 7 5/1/1; SFH 2-8 1 1/0/0; SFH 25+ 1 1/0/0.
Bologna: AB 9-24 702 491/105/106; AB 25+ 71 50/11/10; TH 1 36 25/5/6; MFH 2-8 311 218/47/46; MFH 9-24 31 22/5/4; SFH 1 20 14/3/3.
Strata with empty val or test (D9-2 not evaluable): 3, all Madrid: MFH 9-24 (n 2, val 0), SFH 2-8 (n 1, val 0, test 0), SFH 25+ (n 1, val 0, test 0).
no_outdoor_wall flagged: Madrid 11, Bologna 71 (kept in the split).

Run plan (9 / 6 / 6 runs for dev / val / test buildings), runs; flats summed over runs:
* Madrid 9,438 runs, 100,998 flats (1,165 buildings): AB 8,862 / 99,642; MFH 96 / 597; SFH 75 / 354; TH 405 / 405.
* Bologna 9,486 runs, 127,113 flats (1,171 buildings): AB 6,261 / 109,680; MFH 2,772 / 16,980; SFH 162 / 162; TH 291 / 291.
* Total 18,924 runs, 228,111 flats over runs.

Checks:
* 1 exactly one split, counts 1,165 and 1,171: PASS
* 2 no stem in common across the three lists: PASS (0 and 0)
* 3a planted fault (one Madrid test building, stem 00f87040080db31a, also put in dev): overlap check FAILED as intended and named exactly that stem (the printed label "3a ... PASS" means the planted-fault test passed, the check itself returned FAIL). 3b unplanted lists pass again: PASS
* 4a same seed twice: 6 of 6 md5 equal: PASS. 4b seed 9103: 6 of 6 lists differ: PASS

## Decisions
* Pattern as the households split: sort by stem, shuffle with `rng_for(9102, "bsplit", district, class, band)`, dev = int(round(0.70 n)), val = int(round(0.15 n)), test = rest. Python round is banker's rounding, same as the households script.
* Lists sorted by stem inside each file. Rows of any other district would have been skipped (none exist in the table).
* Planted fault and different-seed runs are done in memory only; nothing extra written.
* Run counts are the task doc's 9/6/6 (not the 9C draft's 8.1 average); D9-4 compute decision stays with the manager.

## Next
Manager checks and seals the lists (md5 above); decide D9-4 size with the run plan counts.

## WHAT I DID NOT VERIFY
* The wall table content (windows, n_flats values) was taken as given from the manager's verification, not re-derived.
* Did not check that every stem in the lists exists as a windowed IDF on disk.
* Did not re-read the written files from disk to recompute md5 (md5 computed from the same bytes written).
* Madrid has a one-building-or-two-building strata where val/test is empty; no rule was added to move buildings between splits.

## Manager check (2026-10-01 16:01)
* Own code re-derived the split from the wall table: same assignment (2,336 buildings), same six md5, flat counts equal the zone map, run plan equal (9,438 / 9,486). VERIFIED. Not sealed yet.
