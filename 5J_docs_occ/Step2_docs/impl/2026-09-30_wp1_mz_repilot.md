# WP1 multi-zone re-pilot (every flat tested) - implementation state
Task doc:   Step2_docs/impl/2026-09-30_wp1_mz_repilot_TASK.md
Status:     DONE (2026-09-30 16:10 EDT)
Speed root: R=/speed-scratch/o_iseri/5J/mz_pilot/   (read-only: 5J/pilot/, 5J/multizone/)

## Ledger
(append-only)
- 1404082 . syntax check (ast.parse) of builder + 3 new scripts . COMPLETED 0:0 . SYNTAX_OK x4 (R/logs/compile_1404082.out)
- 1404083 . build job (design, household md5, 36 IDFs, gates, seen-failing, collapse cmp) . submitted 2026-09-30 16:05 EDT . R/logs/build_1404083.out
- 1404084 . EnergyPlus array 1-36%30, afterok 1404083 . submitted . R/logs/run_1404084_<n>.out
- 1404085 . extraction job, afterany 1404084 . submitted . R/logs/extract_1404085.out
- 1404086 . checker job (tools/5thJ_mz_pilot_check.py), afterok 1404085 . submitted . R/logs/check_1404086.out ; results R/report/

Ledger outcomes (sacct): 1404083 build COMPLETED 0:0; 1404084 array 36/36 COMPLETED 0:0 (4-25 s each); 1404085 extract COMPLETED 0:0 2:07; 1404086 checker COMPLETED 0:0 (EXIT_CODE 0).

## Verified (read from Speed logs, 2026-09-30 16:06-16:10 EDT)
- Build log R/logs/build_1404083.out: PATCH_TOTAL 324 over 36 IDFs (36 PATCHCHECK PASS); 36 AREAGATES 7/7 PASS; capacity all-sides rel <= 5.9e-06; collapse_byte_identical PASS x5 (md5 equal); SEENFAIL_MASS_pairs_once FAIL (rel 0.31) CONFIRMED; staging md5 of one file equal local/Speed (31baa0032d57e3f1b6821740773b8fe4); buildings.csv on Speed 40 rows, 0 non-Spanish; DESIGN runs=36; household_md5.txt 122 lines.
- Array: 36/36 COMPLETED; status.txt MZ021: rc 0, 14 s, rss 233516 kB, du 58048 kB; MZ025: 23 s, du 84504 kB. 72 files in R/extracted (36 csv.gz + 36 dwellings.csv).
- Checker R/logs/check_1404086.out (copy: outputs_step2/mz_pilot_check_1404086.out): SUMMARY PASS=10 FAIL=0 WARN=0 NOT_EVALUABLE=0, EXIT_CODE 0; four SEENFAIL lines all FAIL.
- Copies here: outputs_step2/mz_pilot_runs.csv, run_table.csv, dwelling_table.csv, household_md5.txt, mz_pilot_build_1404083.out, mz_pilot_report.md.

## Decisions
- Part A1 mass: default `mass_rule="all_sides"`; old behaviour kept as `mass_rule="pairs_once"` (additive). Collapse IDF header text kept unchanged so collapse IDFs are byte-identical.
- Part A2: `k_from_tabula()` added to tools/5thJ_idf_mz.py (prints `PATCH mz_k`); the 9th PATCH line per IDF (36 x 9 = 324).
- Replicates: 5 extra copies of MZ001 (es_B07, hid 02822) and of MZ025 (es_B37 run 1), in addition to the original runs (20 + 6 + 10 = 36); replicate column 0 for originals, 1-5 for copies.
- Seeds: SFH/TH have no permutation (seed NA). Permutation = random.Random(seed).shuffle of hids_es60.csv order; a second shuffle continues if n > 60 (never needed).
- Extraction format: long csv.gz (8,760 rows per dwelling), COP 3.0 assumed in the header; side table per run. No Lights object exists, so no lighting column.
- Gate 2.4: eplustbl End Uses is in GJ with 2 decimals, so tolerance = 0.1 % OR 0.005 GJ (table rounding). Added 2.4b (dwelling annual vs the dwelling's own zone columns in eplusout.csv, 1e-6) because a 1 % error in one flat of a 12-flat run is only ~0.08 % at facility level.
- 4.3: "absent" = presence == 0; 8 dwellings skipped (presence always 1 or always 0).
- 5.3: Italy and UK building rows not opened; Spain's 40-building mix used as proxy; 9 climates = 3 per country; class median seconds and MB; in flight = 30.
- buildings.csv: used the builder task's Spanish-only copy on Speed (multizone/repo/buildings.csv, read-only); job asserts 0 non-Spanish rows.
- Local work: only edits/scp/ssh/ls and cp of 60 Spanish appliance files into the scratchpad for scp. No local python or EnergyPlus.

## Next
Manager verifies (one flat's annual heating from its extracted file vs zone sums; B21 flat count 12 and area; one run's seconds; checker SUMMARY and exit code); manager rules O-3.

## WHAT I DID NOT VERIFY
- Whether TABULA n_Apartment is a published or default value (carried from the builder task).
- Class-median run time for AB buildings with more than 18 zones (AB max 77 zones; not run).
- Italy and UK climates or buildings (proxy only).
- That COP 3.0 is what the author meant; no lighting outputs exist (no Lights object).
- Raw folders were not deleted; total raw about 1.1 GB, extracted about 85 MB (estimated from the run table medians, not du of R).

## Verified (manager) 2026-09-30 16:14 EDT (from `date`): re-pilot ACCEPTED
Own job on Speed (1404122, `R/mgr/mgr_verify_mz.py`, COMPLETED 0:0), independent of `mzp_extract.py` and the
checker: zone -> dwelling from the zone NAME suffix `D<jj>`, areas from `eplusout.eio`, energy from `eplusout.csv`.
- MZ021 (es_B21, MFH): IDF has 12 zones = 12 dwellings; eio floor area sum 555.48 m2 vs A_C_Ref 555.50 (eio rounds
  each zone to 2 decimals; 12 x 46.2917 = 555.50 in the side table).
- Dwelling 5 (Z_F02_D05, hid 09010): annual heating 4176.3907 kWh extracted = 4176.3907 from its zone column
  (rel 2e-10); cooling 4017.1935 = 4017.1935; equipment 3207.6649 = 3207.6649; total electricity 5938.8597 =
  equipment + heating/3 + cooling/3 recomputed. 90.2 kWh/m2 heating (middle floor).
- Seconds: sacct 1404084_21 Elapsed 00:00:14 = status.txt seconds=14 (MaxRSS 233516 kB, du 58048 kB).
- Checker copy: `SUMMARY PASS=10 FAIL=0 WARN=0 NOT_EVALUABLE=0`, `EXIT_CODE 0`; four SEENFAIL lines FAIL.
- The 2.4b gate shares the zone map with the extractor (failure class 62); the manager's check above maps zones
  by name, a route the extractor's defect could not reach, and agrees.
Notes (not blocking, for Step 2 sanity/Step 8): Madrid cooling per m2 is high (SFH 85 kWh/m2 > heating 69; top
floors 88-149): ideal loads to 26 C with no shading, no night ventilation and 2-38 people; record as a model
limitation candidate, re-check against a TABULA/literature band before the paper. The 5.3 arithmetic under-counts
AB above 18 zones (77-zone AB.06 not timed): the campaign prep check job times it.
