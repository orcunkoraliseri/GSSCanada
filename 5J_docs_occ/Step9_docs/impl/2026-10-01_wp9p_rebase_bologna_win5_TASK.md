# 5J Step 9p: move Model A (Bologna) onto OpenUBEM's `_win_2026-10-05` (task doc for a fresh employee)

Written 2026-10-01 night by the 5J manager. Parent and template: `Step9_docs/impl/2026-10-01_wp9o_rebase_win5_TASK.md` and its state file
`2026-10-01_wp9o_rebase_win5.md` (the same job for Madrid: its tools, helpers in `impl/wp9o_win5/helpers/`, numbers and checks are your
template; read both first). Also `2026-10-01_wp9j_rebase_win3.md` (the 10-03 measurements for Bologna), `outputs_step9/step9_rules.md`
(R1 lists, R2 runs, R3 integrity, amendment A1), log `Step9_docs/5thJ_09_modelA.md`. State file you keep (new):
`Step9_docs/impl/2026-10-01_wp9p_rebase_bologna_win5.md` (Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## What OpenUBEM delivered (peer message, night of 10-01; claims until you re-measure them)
* Bologna ONLY: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05/` (`idfs/` 1,179 IDFs,
  `md5_2026-10-05.txt`, `changed_stems.txt` (tab: stem, reason), `degenerate_2026-10-05.csv`, `dwelling_counts_2026-10-05.csv`,
  `origin_offset.json`, `fleet.lst`, `prepared_buildings.csv`, `windows.csv`, `schedules/`, `weather/`). Replaces the 10-03 and 10-04 sets.
  No `orientation.csv` (as in Madrid 10-05).
* Claimed: 1,070 homes rebuilt with the area-based flat count (flats 15,767 -> 36,095; none under 15 m2; largest building 30090 with 1,247
  flats); the other 109 homes geometrically unchanged. EVERY IDF moved to a local origin: dx 685000, dy 4928000 (EPSG:32632), x/y only,
  z unchanged, a pure shift (areas, normals, partner pairs equal to 1e-6 m2). Degenerate surfaces: 0 in all 1,179 by their EnergyPlus-rule
  detector (nothing deleted). Orientation check: 91,386 of 91,386 interzone pairs opposite, 0 floors up, 0 windows off wall, 16 outdoor
  walls inward of about 71,000. `idf_sha256` in `prepared_buildings.csv` is stale: use `md5_2026-10-05.txt`. Weather file same as 10-03.
* **Manager measured (night, own md5sum of every IDF):** 1,179 of 1,179 equal `md5_2026-10-05.txt` (0 differences). sha256 of the five
  named files equals the peer's message (md5 file 541030a6..., changed_stems 80fabe76..., dwelling_counts ef594821..., degenerate 0c242d9c...,
  origin_offset a120aea3...). `changed_stems.txt` has 1,179 rows (1,070 flat_count+origin_shift, 109 origin_shift) as claimed (row count only).
  Nothing else measured by the manager.
* The peer says OpenUBEM runs its own Bologna runs from this tree now. No reply to the peer is needed unless you find a mismatch (tell the
  manager, do not message the peer).

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`, `_uk`).
  NEVER list `EU-11/` itself (the manager did once tonight by mistake, count only, no UK name read; do not repeat it); open only the ONE
  district folder above by full name, plus `IT-BOL-GALVANI2_win_2026-10-03` by full name for the comparison. No folder-wide or repo-wide
  search, no recursive listing, no wildcard over district folders (FINDING 5J-2, 5J-4); iterate IDFs by `fleet.lst` or the one `idfs/` folder.
* **The Madrid campaign array 1409235, check 1409266 and smoke 1409919 are LIVE on Speed.** Never edit, move, delete or overwrite anything
  under `/speed-scratch/o_iseri/5J/modelA/campaign/` or `campaign_win5/` (code, inputs, manifests, results, runs, logs), the Madrid fleet
  folders, nor the Madrid files under `impl/` (`_win5` Madrid names). Bologna Speed files only under new names:
  fleet `/speed-scratch/o_iseri/fleets/IT-BOL-GALVANI2_win_2026-10-05` (ls first: the OpenUBEM peer may have filled it, as it did for Madrid;
  add only what is missing, never overwrite) and manifests/inputs under `/speed-scratch/o_iseri/5J/modelA/campaign_win5/` ONLY in new files
  named `*_IT-BOL-GALVANI2*` (never the Madrid ones; if in doubt put the file in a new folder `campaign_bol5/` instead).
* **Compute:** desktop work, at most 10 processes. **NO Speed job of any kind** (the 5J cap of 32 CPUs is full while the Madrid array runs);
  only `ssh`/`scp` of small named files and `ls`. Never submit anything; the manager submits.
* Write only: new files named `_bol5` or `_win5` with IT in the name (never overwrite `_win`, `_win2`, `_win3` names or any Madrid `_win5`
  file), additive edits to `tools/5thJ_modelA_idf.py`, `tools/5thJ_modelA_static.py`, `tools/5thJ_modelA_buildsplit.py`,
  `tools/speed/a9_campaign_plan.py` ONLY if Bologna needs a change (the old vintages and the Madrid `win_2026-10-05` behaviour must not
  change: prove it by re-running the Madrid plan and static and comparing md5), output folder `Step9_docs/impl/wp9p_bol5/`,
  `Step9_docs/impl/static_bol5/`, `Step9_docs/impl/buildsplit_bol5/`, your state file.

## What to do
1. **Re-measure the delivery with our own code**, per stem, against `_win_2026-10-03` (read both `idfs/` folders): zone count and names,
   surface count, area sum (shift-invariant), window objects and area, construction names, and the x/y shift: every vertex of every IDF
   moved by exactly (-685000, -4928000), z unchanged (report any stem where it is not; also check origin objects/Building north axis if the
   IDF has one). The 109 origin-shift-only stems: expect everything equal after adding the offset back. The 1,070 flat_count stems: report
   what changed (zones, floors, flats per building, old -> new totals; claimed 15,767 -> 36,095) and list every difference not explained.
   **Seen failing:** the same counter on a copy of one 10-03 IDF with a surface deleted, and on one with a vertex moved 0.1 m, must flag it.
2. **Our own geometry check** (the code that produced `impl/wp9k/degenerate_win3.csv`): run it on all 1,179 10-05 IDFs. Claim: 0 degenerate.
   Report the number it finds and what the check cannot see (it is not EnergyPlus). Also run it on one 10-03 Bologna IDF known to be on the
   old list so you SEE it fire. Report whether our check works at the shifted origin (it may have a coordinate-size assumption).
3. **Copy to Speed** (scp only), per the rule above: `idfs/` + `windows.csv` + `fleet.lst` + `prepared_buildings.csv` + `schedules/` + `weather/`
   + the csv/txt/json files, to the NEW fleet folder. Compare names and byte sizes against the local folder (`ls -l`); the md5 itself is
   checked by the campaign task. Report free disk on `/speed-scratch` first (`df`), and the size copied.
4. **Rebuild** (`MODELA_VINTAGE=win_2026-10-05`, country IT): wall table, zone map and static tables (`flats_IT-BOL-GALVANI2.csv`,
   `buildings_...csv`) into `static_bol5/`; zone map and wall table with new `_win5` names that cannot collide with Madrid (if the tool
   writes one shared file for both countries, say so and write to the new folder instead). Compare to `static_win3` / `zone_map_win3.csv` for
   IT: byte-equal for the 109 origin-only stems (md5 per stem's rows); for the 1,070 give old -> new flat counts per stem (csv) and totals.
   Check that the static builder and the IDF writer do not depend on absolute coordinates (the origin shift): report.
5. **Split and hold-out, new base** (Bologna has no sealed lists yet; rule R1(c): derived on the new base, same seed 9102, same rule, by a
   dated amendment BEFORE any Bologna run): run `tools/5thJ_modelA_buildsplit.py` for IT into `impl/buildsplit_bol5/` (six lists + strata) and
   compare with `impl/buildsplit_win3/` (IT lists): stems that moved between lists, flat bands changed. Derive the tiny-flat hold-out list
   (any flat under 15 m2 in the new `flats_IT-BOL-GALVANI2.csv`; peer says none under 15 m2 now) into `impl/heldout_tinyflats_bol5.csv` (same
   columns as `..._win3.csv`) and report what the old list (IT 83) becomes. **Report, do not decide; give the md5 of each list so the manager
   can seal them by amendment A2.** Check the split is deterministic (run twice, byte-equal) and that no stem is in two lists (planted check).
6. **Plan**, new file, never overwriting a Madrid one: `a9_campaign_plan.py` for IT, `win_2026-10-05`, on the lists of item 5 (provisional until
   the manager seals them: say so in the file header or stdout), into `impl/wp9p_bol5/plan_IT-BOL-GALVANI2_win5.csv` (local; do NOT copy it to
   `campaign_win5/manifests/` until the manager says; put it in the new folder `campaign_bol5/manifests/` on Speed if you copy at all).
   Print: run counts per split and per mode (occupancy, B0, default), the B0 household it needs for IT (what exists, where; read the 9l / 9o
   state files for how Madrid's B0 copy was made and do not touch it), households per building, total CPU-hours estimate (Madrid per-run
   wall time from `impl/2026-10-01_wp9l_campaign_madrid.md` and the live results; say it is Madrid's), and the same check as 9o: **Seen
   failing:** a planted changed md5 on one row must show up. Compare against the OLD Bologna expectation (8,820 runs on the 10-03 lists).
7. Write for the manager: the exact `sbatch` line for a Bologna array (`--array=<ranges>%<cap>`, `-t 7-00:00:00`, `--exclude=antenna1`, a COPY of
   the campaign code for Bologna, MANIFEST path), plus its check job line, and the honest timing: the 5J cap is 32 CPUs and the Madrid array
   holds all of it until about 8 Oct; say what happens to the 1,458 Madrid resubmission rows and the Bologna rows in the queue (order, total
   days at 32 CPUs). Do not decide the order; give the numbers.

## Done means
Items 1-7 with numbers in the state file (what you re-measured, what you took from OpenUBEM), a `Next` a cold agent can start from, nothing
UK opened/listed/passed, nothing on Speed touched except the new names. End with "no job submitted, state written to <path>".
