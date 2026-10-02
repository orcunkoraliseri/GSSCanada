# 5J Step 9h: move Model A onto OpenUBEM's fixed base `_win_2026-10-02` (task doc for a fresh employee)

Written 2026-10-01 17:01 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md` (entries 16:10, 16:13, 16:39: FINDING 5J-5,
walls and windows faced inward; D9-6 ruled: OpenUBEM fixes at the source). State file you keep:
`Step9_docs/impl/2026-10-01_wp9h_rebase_fixed.md` (Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## What OpenUBEM delivered (17:00, peer session; peer numbers are claims until you re-measure them)
* Madrid: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-02/` (1,172 IDFs;
  Speed copy `/speed-scratch/o_iseri/fleets/EU11_ES-MAD-BERRUGUETE_win_2026-10-02/idfs`). Claimed: outdoor walls inward 0 /
  outward 35,720 / unclear 463; homes without an outdoor wall 11; interzone pairs opposite 25,897 of 25,897.
* Bologna: `.../EU-11/IT-BOL-GALVANI2_win_2026-10-02/` (1,179 IDFs; Speed `/speed-scratch/o_iseri/fleets/EU11_IT-BOL-GALVANI2_win_2026-10-02/idfs`).
  Claimed: inward 0 / outward 55,242 / unclear 491; no outdoor wall 71; interzone opposite 29,382 of 29,382.
* Claimed for both: floors point down, ceilings and roofs up, window normal = host wall normal 100 %; only the vertex order changed
  (no area, volume or geometry change); schedules and weather byte-identical to `_win_2026-10-01`; `orientation.csv` per home.
* Manager already measured: IDF counts 1,172 and 1,179; windows.csv md5 a3edc82e575be1cbd23e54bf1b3f5c61 (ES) and
  232134d1f406790bea33d16524facac1 (IT), equal to the old base; own point-in-floor test on 4 buildings (0275c53572b2ff9f,
  7307694dddf93fb6, 504fa19567bbc2b7, b3f8d90890ff6314): every decidable outdoor wall points out, first wall of 0275c53572b2ff9f
  now 124.4 degrees (was 304.4).

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). The `EU-11/` folder holds other countries: never list `EU-11/` itself; open only the two folders above by full name.
* **No folder-wide or repo-wide search, no recursive listing, and no wildcard of any kind** (FINDING 5J-2, 5J-4). Iterate IDFs by
  reading `fleet.lst` or listing the one `idfs/` folder, never a glob across districts.
* **Compute:** this is desktop work (one machine, at most 10 processes, the author's ruling). No Speed jobs in this task.
* Write only: new files named with `_win2` (never overwrite the old `_win` tables, the old static tables or the old split lists),
  additions to `tools/5thJ_modelA_idf.py`, `tools/5thJ_modelA_static.py`, `tools/5thJ_modelA_buildsplit.py` (old behaviour stays
  the default: a command-line or environment switch picks the new base and the new output names), your state file.

## What to do
1. **Re-measure the peer claims with your own code** (the Newell normal + point-in-floor test the manager used is in
   `tools/5thJ_modelA_idf.py` / the parent state; write your own counter if none fits): per district, outdoor walls pointing out /
   in / undecidable, floors down / up, roofs and ceilings up / down, windows whose normal differs from the host wall normal, and
   interzone pairs that are opposite. Compare with the claims above; any difference is reported, not explained away. **Seen
   failing:** run the same counter on 20 buildings of the OLD base `_win_2026-10-01` and show it reports walls inward there.
2. **Nothing else changed:** for every building in both bases compare, old vs new: zone names and count, surface names and count,
   surface areas (sum per building, within 1e-6 relative), window objects and total window area, construction names. Also md5
   of `prepared_buildings.csv`, and of the `schedules/` and `weather/` files OpenUBEM says are byte-identical (name each file read).
3. **Rebuild on the new base** (`MODELA_VINTAGE=win_2026-10-02`): wall table and zone map (`..._wall_table_win2.csv`,
   `..._zone_map_win2.csv`), then the static tables into `Step9_docs/impl/static_win2/`. Expect identical zone maps and flat counts
   (1,165 + 1,171 pass) and changed orientation columns only (wall and window shares by N/E/S/W swap to the opposite side). Show
   per district: rows equal; every non-orientation column equal; orientation columns changed for how many flats; one flat where
   north and south swapped, by name.
4. **Building split:** re-run `tools/5thJ_modelA_buildsplit.py` on the new wall table into `impl/buildsplit_win2/` and compare the
   six lists with the old ones (md5 in `Step9_docs/5thJ_09_modelA.md` entry 16:01). If the stems, classes and flat bands are equal
   the lists must be byte-equal; if not, list what moved and why.
5. **EnergyPlus sample (Speed, one small job is allowed for this item only, at most 4 CPUs, `sbatch`, `-t 7-00:00:00`,
   `--exclude=antenna1`, never wait):** the 4 buildings the manager checked, NEW base, as delivered, from the Speed copies of `_win_2026-10-02`; read from each
   `eplusout.err` the count of "upside down" warnings, and from `eplustbl` the azimuth EnergyPlus reports for the first outdoor wall
   vs your geometric outward azimuth (must now agree within 1 degree). Write the job id and the lines a cold agent reads.

## Done means
Items 1-4 done with numbers in the state file, item 5 submitted with its id, a `Next` a cold agent can start from, nothing UK
opened, listed or passed. End with "job N submitted, state written to <path>".
