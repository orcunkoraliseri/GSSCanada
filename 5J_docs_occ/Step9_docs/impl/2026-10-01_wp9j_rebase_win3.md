# Step 9j: Model A on OpenUBEM's wall fix `_win_2026-10-03`: implementation state

Task doc:   `5J_docs_occ/Step9_docs/impl/2026-10-01_wp9j_rebase_win3_TASK.md`
Template:   `Step9_docs/impl/2026-10-01_wp9h_rebase_fixed.md`
Status:     items 1-4 DONE with numbers below; item 5 SUBMITTED, job 1407674 (no EnergyPlus result read yet). Employee, 2026-10-01 evening.
Files:      `Step9_docs/impl/wp9j_win3/` (logs, per-building csv, helpers/ = small scripts, run with `py`)

## Ledger (cluster jobs)
* 1407674 - 5J_9j_win3 (4 CPUs, 16 G, ps, -t 7-00:00:00, --exclude=antenna1; 4 EnergyPlus runs, each in its own run and cwd folder, then the reader, then the reader on a planted copy) - SUBMITTED - exit not yet known.
  Script `wp9j_win3/helpers/win3_task.sh` (copy on Speed: `/speed-scratch/o_iseri/5J/step9c/win3/win3_task.sh`). Logs `/speed-scratch/o_iseri/5J/step9c/win3/logs/task_1407674.out`,
  reader `.../logs/read_1407674.txt`, planted reader `.../logs/read_planted_1407674.txt`, run folders `.../win3/runs/<stem>/`, IDF copies `.../win3/idfs/<stem>.idf` (+ `<stem>.src.md5` = md5 of the delivered Speed file).
  Local md5 of the 4 delivered IDFs: `wp9j_win3/local_md5_4idfs.txt` (compare with the `.src.md5` files).
  Own folder `win3/`, not `win/` or `win2/`.

## Code changes (additive; old values keep working)
* `tools/5thJ_modelA_static.py`: vintage map win -> win, win_2026-10-02 -> win2, win_2026-10-03 -> win3 (wall table, zone map, output folder `static_win3/`); the "outward" check is used for 10-02 and 10-03.
* `tools/5thJ_modelA_buildsplit.py`: same switch, writes `buildsplit_win3/`.
* `tools/5thJ_modelA_win2_check.py`: new option `--new win_2026-10-03` (old = 10-02): counts the old base on every building too, writes `wp9j_win3/win3_check_*`; default run unchanged.
* `tools/5thJ_modelA_idf.py`: not edited (reads `MODELA_VINTAGE` already; lights meter off for any base after 10-01).

## Verified (numbers read; source = `wp9j_win3/win3_check_log.txt` unless named; every method side by side)
1. **Walls, own counters on `_win_2026-10-03` (every building: ES 1,172, IT 1,179).** Outdoor walls ES 36,183, IT 55,733 (equal to the peer's totals).
   * 5 cm probe (Newell normal, point against the zone floor polygon): ES inward 9, outward 35,973, undecidable 201. IT inward 4, outward 55,523, undecidable 206. Peer claim: inward 9 and 4. EQUAL.
   * Winding test (wall bottom edge vs the zone floor edge): ES inward 8, outward 32,633, no matching edge 3,542. IT inward 18, outward 51,282, none 4,433. **The winding test does NOT give the peer's 4 for Bologna (18).** Cross-tab probe x winding: ES in x in 1, in x none 8, out x in 4, unc x in 3; IT in x in 1, in x none 3, out x in 4, unc x in 13. The winding test is blind where the floor ring has split or partial edges; the 4 + 4 "out x in" are the same disagreement between my two tests as in 9h. Not resolved. The peer's own rule (5-point x 2-depth vote, floor edge, centroid) was not re-run by me.
   * Floors down ES 15,595 / IT 18,959, up 0 / 0; ceilings up 11,730 / 15,198, down 0; roofs up 3,257 / 2,802, down 0 (claim equal).
   * Windows ES 35,489, IT 55,075: normal differs from host wall 0 / 0, host not found 0 / 0 (claim of 100 % agreement reproduced).
   * Interzone pairs ES 25,897, IT 29,382, opposite 25,897 / 29,382 (strict dot < -0.999: all; unmatched 0). Claim reproduced. Homes without outdoor wall ES 11, IT 71 (equal to 9h).
   * `orientation.csv` (peer file) column sums: ES wall_inward 14, wall_outward 35,706, wall_unclear 463, wall_kept 28; IT wall_inward 2, wall_outward 55,240, wall_unclear 491, wall_kept 30. **Does not match the claim 9 / 4 and does not match my probe or winding counts (ES 14 vs 9 / 8, IT 2 vs 4 / 18); not reconciled.** Reported, not explained.
   * Per-building csv with the inward count (probe: `wall_out_in`, winding: `edge_in`) for the new base and the old base: `wp9j_win3/win3_check_per_building.csv` (extra columns `changed_walls_vs_old`, `changed_windows_vs_old`, `old_wall_out_in`, `old_edge_in`).
   * **Seen failing / reproduction on the old base `_win_2026-10-02` (every building, same counter, no sampling):** probe inward ES 162, IT 209; winding inward ES 237, IT 327 = 9h's numbers to the wall (verdict PASS). Planted: one outdoor wall of the old Madrid building flipped in memory -> probe total 162 -> 163, so the reproduction test would read FAIL (verdict "planted flip on the old base makes the reproduction test fail": PASS). Also a planted wall flip on the new base: inward 0 -> 1, outward 47 -> 46 (seen). Planted zone rename and 0.1 m vertex move caught by the comparison (2 and 3 problems); unplanted 0.
2. **Nothing else changed vs `_win_2026-10-02`, every building:** 0 buildings with any problem (1,172 + 1,179). Zone names and count, surface names and count, construction names, first 10 fields of every surface, surface area (1e-6), vertex sets, building area sum (ES 3,863,702.56 m2, IT 6,831,949.03 m2), window area (ES 159,170.02 m2 in 35,489 windows, IT 123,434.60 m2 in 55,075), text outside surface objects: all equal. Vertex sequence changed on: ES 334 wall-type surfaces + 212 windows = 546 (all reversed, 0 other order, 0 set differences); IT 489 + 257 = 746. (Not split by boundary type: the 334 / 489 are wall-type surfaces of any boundary, not only outdoor walls.)
   * md5 equal 10-02 vs 10-03: `prepared_buildings.csv` (ES 86c93a70..., IT 5c983ddd...), `windows.csv` (ES a3edc82e..., IT 232134d1...), `fleet.lst` (ES 0403eb36..., IT fa6d8cc7...). `orientation.csv` DIFFERENT (ES a76bd5ec... vs 78c76dae..., IT 48a2d166... vs bc9f92c6...): it describes the fix, a change is expected.
   * Files read by name: `weather/es_madrid_2009_2010_y2010.epw`, `weather/it_bologna_2013_2014_y2014.epw` byte-equal in both bases; `schedules/<stem>/<stem>_F<k>_dwelling_<n>_f000_gain.csv`: ES 1,172 folders / 12,525 files, IT 1,179 / 15,732, 0 listing or md5 differences (one folder at a time, no recursion).
3. **Rebuild (`MODELA_VINTAGE=win_2026-10-03`):** wall table `Step9_docs/impl/2026-10-01_wp9c_wall_table_win3.csv` (2,351 rows, md5 7fd2b692dcd132d2d16ee94f2b3f0df7 = BYTE-EQUAL to `_win2`; `helpers/cmp_walltable3.py`: no column differs in any row); zone map `..._zone_map_win3.csv` byte-equal to `_win2` (md5 1c48d2e5240962a88ca16279dd089d50); flats ES 1,165 buildings / 12,496 flats, IT 1,171 / 15,683 (as expected). Static tables in `static_win3/`: buildings tables byte-equal to `static_win2` (ES 8574a4a9..., IT 51326fdc...); flats ES 72cf56a1390a7d909d831e0c991f6b45, IT a492d460687c4ae8576a01beef4cbc28.
   * Flats vs `static_win2` (`helpers/cmp_flats3.py`, `cmp_flats3_stdout.txt`): same rows in the same order; flats with any non-orientation column different 0 / 0; **orientation columns changed: ES 270 of 12,496 flats (in 98 buildings), IT 330 of 15,683 (in 101 buildings).** Each changed flat sits in a building with at least one flipped wall: violations 0 / 0 (buildings with a flipped wall: ES 109, IT 134). Wall total and window total per flat equal in every flat. No changed flat is an exact N<->S / E<->W mirror (only some walls of a building flipped). Seen failing: one flat edited in memory in a building with no flipped wall -> the rule reports 1.
   * Static script checks (`static_win3_stdout.txt`): 21 PASS, 2 FAIL = the two strict "outward normals" checks (ES 9 of 35,969 outdoor walls inward, ambiguous 201; IT 4 of 54,700, ambiguous 206), kept as FAIL like 9h; the "uniformly outward" check (walls inward share 0.0003 / 0.0001, floors and roofs none inverted) PASS; same set of 23 check names as the 10-02 run. North-axis plant and planted wrong window U also seen.
4. **Split and hold-out:** `buildsplit_win3/` six lists + `strata.csv` BYTE-EQUAL to `buildsplit_win2/` (cmp, 7 of 7). md5 prefixes ES dev d6ada695, test c4b0e46c, val ddf1cc4b; IT dev 55410d35, test 71b57e8e, val b9d4f6d9. Script checks 6 PASS (incl. planted cross-split stem named). Hold-out `Step9_docs/impl/heldout_tinyflats_win3.csv` (112 rows, byte-equal to `heldout_tinyflats_win2.csv`, md5 1a0cd4ad0a4a906f57ec1e52ec0c5c37): ES 29 (dev 21, val 4, test 4), IT 83 (dev 56, val 9, test 18); same stems. Seen failing (`helpers/holdout3.py`): threshold 1.0 holds out 0 buildings, threshold 20 holds out 173 (rule at 15 gives 112).
5. **Tool switch check (import only; no old base re-run, nothing overwritten):** vintage "" and win_2026-10-01 -> old names; win_2026-10-02 -> `_win2` names and `static_win2` / `buildsplit_win2`; win_2026-10-03 -> `_win3`; an unknown value stops `static.py` (SystemExit, seen); `buildsplit.py` falls back to the old default for an unknown value, as before.

## Decisions (task doc did not decide; what I assumed)
* The 4 EnergyPlus buildings run as byte copies of the Speed-delivered files plus the same two output-only lines as 9h (EnvelopeSummary table, CommaAndHTML), same EPW copies, so results compare with 9h. Own folder `win3/`.
* Expected azimuth rule as in 9h (`helpers/mkexp3.py`: probe/winding classes; Newell azimuth for outward, +180 for inward). 105 outdoor walls, same as 9h, all with a defined geometric azimuth (91 out/out, 13 out/none, 1 unc/out). Exactly 2 rows differ from 9h's file (Wall 0006 of 0275c53572b2ff9f, Wall 0004 of 7307694dddf93fb6: classed inward then, outward now); their geometric outward azimuth is unchanged (215.7974 / 270.0000). So 105 of 105 should agree if EnergyPlus reads the new order.
* Planted check on the reader: a second reader pass on a copy of `expected_azimuth.csv` with the first wall's expected azimuth turned by 180 degrees (made with awk in the job); it must show exactly one more disagreement per source.
* `win2_check.py` default run unchanged (new = 10-02, old = 10-01 sample); `--new win_2026-10-03` selects the 9j mode.

## Next
Cold agent: (1) `ssh o_iseri@speed.encs.concordia.ca "sacct -j 1407674 -X"` (tcsh: no `$()`). (2) `cat /speed-scratch/o_iseri/5J/step9c/win3/logs/task_1407674.out` (rc per stem, reader rc) and `.../logs/read_1407674.txt` (per building: upside-down warnings, expected 0; Severe/Fatal; first outdoor wall azimuth sql vs eplustbl vs geometric; COMPARE lines: expected agree 105 of 105 for both sql and eplustbl; 9h had 103 of 105 on `_win_2026-10-02`). (3) `cat .../logs/read_planted_1407674.txt`: COMPARE lines must show one more disagreement than the real reader (seen failing). (4) Compare `.../win3/idfs/<stem>.src.md5` with `wp9j_win3/local_md5_4idfs.txt` (df86206c..., 6fc27aa8..., 2d0df7aa..., 25f44cd1...). (5) Copy these lines here under Verified 6 and set Status DONE.
Manager decisions: (a) flat counts are unchanged on this tag (1,165 + 1,171); if OpenUBEM's tiny-flat ruling changes them, add the new vintage value to the three suffix maps (one line each: `static.py`, `buildsplit.py`, `win2_check.py` claims) and rerun; (b) ask OpenUBEM what their `orientation.csv` column `wall_inward` counts (14 / 2 vs their stated 9 / 4); (c) my winding test says 18 inward in Bologna while the probe says 4: the probe is the better-posed test, but the difference is unexplained.

## WHAT I DID NOT VERIFY
* Any EnergyPlus result on the new base (job 1407674 pending).
* The peer's own wall classifier (5-point x 2-depth vote) was not re-run; only my two tests.
* Why the winding test gives 18 inward walls for Bologna (and `orientation.csv` 14 / 2) while the probe gives 9 / 4.
* Which of the 334 / 489 changed wall-type surfaces are outdoor walls, and why more surfaces changed than the old probe-inward counts (162 / 209; winding 237 / 327); not decomposed by boundary type.
* That the Speed copies of the 4 IDFs equal the local delivered files (md5 compare is step (4) above).
* Whether floor-ring slits (the 9h kept-wall case) explain the 4 remaining probe-inward walls per district.

## Manager read of E+ sample 1407674 (2026-10-01 18:37)
COMPLETED 29 min. Source md5 on Speed = desktop md5 (4/4); run copies only append EnvelopeSummary + table style. 0 Severe, 0 Fatal,
0 upside-down. sql azimuth = geometric outward azimuth 105/105; planted copy 1 disagreement (180 deg), as expected. Reader defect:
eplustbl branch matched surface names case-sensitively (EnergyPlus writes them upper-case) and found 0 rows; manager own code on the
copied tables: 105/105 agree. 9j CLOSED; `_win_2026-10-03` stands as the Model A base unless flat counts change (OpenUBEM FINDING 286).
