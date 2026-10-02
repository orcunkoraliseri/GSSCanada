# 5J Step 9j: move Model A onto OpenUBEM's audited wall fix `_win_2026-10-03` (task doc for a fresh employee)

Written 2026-10-01 18:02 EDT by the 5J manager. Parents: `Step9_docs/impl/2026-10-01_wp9h_rebase_fixed.md` (the same job done
for `_win_2026-10-02`: its tools, numbers and checks are your template), `Step9_docs/impl/2026-10-01_wp9h_rebase_fixed_TASK.md`,
log `Step9_docs/5thJ_09_modelA.md` (entries 17:14, 17:41, 17:52). State file you keep (new):
`Step9_docs/impl/2026-10-01_wp9j_rebase_win3.md` (Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## What OpenUBEM delivered (18:00, peer session; peer numbers are claims until you re-measure them)
* Madrid `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-03/`, Bologna
  `.../EU-11/IT-BOL-GALVANI2_win_2026-10-03/` (each: `idfs/`, `windows.csv`, `orientation.csv`, `fleet.lst`,
  `prepared_buildings.csv`, `schedules/`, `weather/`). Speed copies `/speed-scratch/o_iseri/fleets/EU11_ES-MAD-BERRUGUETE_win_2026-10-03`
  and `/speed-scratch/o_iseri/fleets/EU11_IT-BOL-GALVANI2_win_2026-10-03`.
* Claimed: Madrid 9 of 36,183 outdoor walls inward, 25,897 of 25,897 shared-wall pairs opposite; Bologna 4 of 55,733 inward,
  29,382 pairs opposite; floors down, roofs up, window normal = wall normal 100 %; no geometry change (vertex order only).
  Their rule: 5-point x 2-depth vote, then floor edge, then centroid.
* Manager measured 18:01: 1,172 and 1,179 IDFs (= `fleet.lst` lines); `windows.csv` md5 a3edc82e575be1cbd23e54bf1b3f5c61 (ES)
  and 232134d1f406790bea33d16524facac1 (IT) = unchanged.
* Our counts on `_win_2026-10-02` (task 9h): 162 ES / 209 IT inward by the 5 cm probe, 237 / 327 by the winding test; OpenUBEM's
  own test said 261 + 8 / 351 + 6. The counts differ by method: report every method you run, side by side, per district.
* **Flat counts may still change** (OpenUBEM FINDING 286, tiny flats; their owner decides; Bologna most affected). This tag keeps
  the old counts. Your work must stay a one-line switch so a later tag reruns it unchanged.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Never list `EU-11/` itself; open only the two district folders above by full name.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard of any kind** (FINDING 5J-2, 5J-4). Iterate IDFs by
  reading `fleet.lst` or listing the one `idfs/` folder.
* **Compute:** desktop work, at most 10 processes. One Speed job allowed for item 5 only: `sbatch`, at most 4 CPUs,
  `-t 7-00:00:00`, `--exclude=antenna1`, never python or loops on the login node (tcsh), never wait for it.
* Write only: new files named `_win3` (never overwrite `_win`, `_win2`, `static/`, `static_win2/`, `buildsplit/`,
  `buildsplit_win2/`), additions to `tools/5thJ_modelA_idf.py`, `tools/5thJ_modelA_static.py`, `tools/5thJ_modelA_buildsplit.py`,
  `tools/5thJ_modelA_win2_check.py` (the old values `win_2026-10-01`, `win_2026-10-02` must keep working exactly as now; the
  new value `win_2026-10-03` picks `_win3` names), output folder `Step9_docs/impl/wp9j_win3/`, your state file.

## What to do
1. **Re-measure walls with our own code** on every building of both districts: outdoor walls out / in / undecidable by each
   method we have (5 cm probe, winding / floor-edge test), floors, roofs, window normal vs host wall, shared pairs opposite.
   Per district side by side with OpenUBEM's claim; any difference reported, not explained away. Per-building csv with the
   inward count. **Seen failing:** the same counter on `_win_2026-10-02` must reproduce 9h's 162 / 209 (probe) and 237 / 327
   (winding) to the wall.
2. **Nothing else changed** vs `_win_2026-10-02`, every building: zone names and count, surface names and count, surface area sum
   (1e-6 relative), window objects and window area, construction names; md5 of `prepared_buildings.csv`, `orientation.csv` and
   each file in `schedules/` and `weather/` (name each file read; list only those two folders, one level).
3. **Rebuild** (`MODELA_VINTAGE=win_2026-10-03`): wall table and zone map `_win3`, static tables into `Step9_docs/impl/static_win3/`.
   Expect zone maps byte-equal to `_win2` and flat counts 1,165 + 1,171; orientation columns change only for buildings whose
   walls flipped since 10-02: give the count of flats with changed orientation columns and check each such flat sits in a
   building with at least one flipped wall.
4. **Split and hold-out:** run `tools/5thJ_modelA_buildsplit.py` into `impl/buildsplit_win3/` and compare the six lists with
   `impl/buildsplit_win2/` (byte-equal expected if stems, classes, flat bands are equal; else list what moved and why). Re-derive
   the tiny-flat hold-out list (rule: any flat under 15 m2 in `static_win3/flats_<D>.csv`) into
   `impl/heldout_tinyflats_win3.csv`, same columns as `impl/heldout_tinyflats_win2.csv`; expect 29 ES / 83 IT and the same stems.
5. **EnergyPlus sample on Speed** (one job, at most 4 CPUs): the 4 buildings of 9h item 5 (0275c53572b2ff9f, 7307694dddf93fb6,
   504fa19567bbc2b7, b3f8d90890ff6314) as delivered from the Speed copies of `_win_2026-10-03`, each in its OWN working folder
   (`-d <run dir>` and `cd` into it; parallel runs sharing a folder abort on the `in.idf` symlink). Reuse 9h's reader: upside-down
   warnings, Severe, and EnergyPlus surface azimuth (sql) vs our geometric outward azimuth for every outdoor wall (9h found 103 of
   105 agree on `_win_2026-10-02`, the 2 others were walls our test calls inward). Write the job id and the lines a cold agent reads.

## Done means
Items 1-4 with numbers in the state file, item 5 submitted with its id, a `Next` a cold agent can start from, nothing UK opened,
listed or passed. End with "job N submitted, state written to <path>".
