# 5J Step 9o: move Model A (Madrid) onto OpenUBEM's `_win_2026-10-05` (task doc for a fresh employee)

Written 2026-10-01 21:10 EDT by the 5J manager. Parents: `Step9_docs/impl/2026-10-01_wp9j_rebase_win3_TASK.md` and its state file
`2026-10-01_wp9j_rebase_win3.md` (the same job for `_win_2026-10-03`: its tools, numbers and checks are your template),
`2026-10-01_wp9l_campaign_madrid.md` (plan and runner), `outputs_step9/step9_rules.md` (R1 lists, R2 runs, R3 integrity; SEALED 20:17),
log `Step9_docs/5thJ_09_modelA.md` (entries 20:48, 20:55). State file you keep (new): `Step9_docs/impl/2026-10-01_wp9o_rebase_win5.md`
(Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## What OpenUBEM delivered (21:00, peer session; peer numbers are claims until you re-measure them)
* Madrid ONLY: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05/` (`idfs/`,
  `md5_2026-10-05.txt`, `changed_stems.txt` (tab: stem, reason), `degenerate_2026-10-05.csv`, `dwelling_counts_2026-10-05.csv`,
  `fleet.lst`, `prepared_buildings.csv`, `windows.csv`, `schedules/`, `weather/`). **There is NO `orientation.csv`** in this folder
  (the 10-03 folder has one): find out whether our static builder needs it and what it reads instead; do not guess.
  Bologna is NOT delivered (comes later, with a local-origin shift): do not touch Bologna.
* Claimed: 171 changed stems = 113 `flat_count` (new floor-area flat rule) + 58 `degenerate`; the other 1,001 byte-identical to
  `_win_2026-10-03`; 647 surfaces deleted in 58 homes (4.92 m2 in total, largest 0.105 m2); `prepared_buildings.csv` keeps OLD
  `idf_sha256` for the 171 changed stems (use the md5 file); Madrid not moved to a local origin.
* **Manager measured 21:05 (own md5sum of every IDF in both folders):** 1,172 of 1,172 equal `md5_2026-10-05.txt`; the set of IDFs
  whose md5 differs from 10-03 is exactly the 171 stems of `changed_stems.txt`; 113 + 58. Against our deferred list
  `impl/wp9k/degenerate_win3.csv` (95 stems): all 58 of their degenerate stems are in ours; 37 of ours are NOT in their degenerate
  group (6 of them sit in the 113 flat_count group, 31 are unchanged and still byte-identical to 10-03, so they keep whatever made
  our G-c5 gate see a Severe). Both smoke buildings `394922138a6b5928` and `1271cddbf6bd1e8a` are in their degenerate group.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Never list `EU-11/` itself; open only the ONE district folder above by full name. No folder-wide or repo-wide search,
  no recursive listing, no wildcard (FINDING 5J-2, 5J-4); iterate IDFs by `fleet.lst` or the one `idfs/` folder.
* **The Madrid campaign array 1409235 and check 1409266 are LIVE on Speed.** Never edit, move, delete or overwrite anything under
  `/speed-scratch/o_iseri/5J/modelA/campaign/` (code, inputs, manifests, results, runs, logs) or the 10-03 fleet folder. New Speed
  files only under new names: fleet `/speed-scratch/o_iseri/fleets/EU11_ES-MAD-BERRUGUETE_win_2026-10-05` and code/manifests under
  `/speed-scratch/o_iseri/5J/modelA/campaign_win5/`.
* **Compute:** desktop work, at most 10 processes. **NO Speed job of any kind** (the 5J cap of 32 CPUs is full while the array runs):
  only `ssh`/`scp` of small named files and `ls`. The IDF md5 on Speed is checked by the campaign task itself (R1 d) when it runs.
  Never submit anything; the manager submits.
* Write only: new files named `_win5` (never overwrite `_win`, `_win2`, `_win3` names), additions to `tools/5thJ_modelA_idf.py`,
  `tools/5thJ_modelA_static.py`, `tools/5thJ_modelA_buildsplit.py`, `tools/speed/a9_campaign_plan.py` (the old values
  `win_2026-10-01/02/03` must keep working exactly as now; the new value `win_2026-10-05` picks `_win5` names), output folder
  `Step9_docs/impl/wp9o_win5/`, `Step9_docs/impl/static_win5/`, `Step9_docs/impl/buildsplit_win5/`, your state file.

## What to do
1. **Re-measure the delivery with our own code**, per stem, against `_win_2026-10-03` (read both `idfs/` folders): zone count and names,
   surface count, area sum, window objects and area, construction names. Expect: the 1,001 unchanged = identical; the 58 degenerate:
   only surfaces (and their windows) deleted, number and area equal to `degenerate_2026-10-05.csv` (647 surfaces, 4.92 m2); the 113
   flat_count: report what changed (zones, floors, flats). List every difference not explained. **Seen failing:** the same counter
   on a copy of one 10-03 IDF with a surface deleted must flag it.
2. **Our own geometry check on the 95-stem deferred list** (`wp9k/degenerate_win3.csv`, the code that produced it): re-run it on the
   10-05 IDFs. Report per stem: still degenerate (how many surfaces), fixed, or changed by the flat_count rebuild. These are the
   stems the campaign will submit first; the 31 unchanged ones are the ones that matter (they were NOT fixed by OpenUBEM).
3. **Copy to Speed** (scp only): `idfs/` + `windows.csv` + `fleet.lst` + `prepared_buildings.csv` + `schedules/` + `weather/` + the
   three csv/txt files, to the NEW fleet folder (never the old one). Compare names and byte sizes against the local folder
   (`ls -l`); the md5 itself is checked by the campaign task.
4. **Rebuild** (`MODELA_VINTAGE=win_2026-10-05`): wall table, zone map and static tables (`flats_ES-MAD-BERRUGUETE.csv`,
   `buildings_...csv`) into `static_win5/`, zone map `_win5`. Compare to `static_win3` / `zone_map_win3.csv`: byte-equal for the 1,001
   unchanged stems (md5 per stem's rows), and give the new flat counts of the 113 per stem old -> new, total flats old -> new.
   If the static builder needs `orientation.csv`, say where its content must come from; do not invent it.
5. **Split and hold-out** (the sealed lists NEVER move a building): run `tools/5thJ_modelA_buildsplit.py` into `impl/buildsplit_win5/`
   and compare the six lists with `impl/buildsplit_win3/`. **Report, do not decide**: every stem that is in one list and not the
   other, and every stem whose flat band or flat count changed. The manager decides what stands. Re-derive the tiny-flat hold-out
   list (rule: any flat under 15 m2 in `static_win5/flats_ES-MAD-BERRUGUETE.csv`) into `impl/heldout_tinyflats_win5.csv` (same
   columns as `..._win3.csv`) and list what moved in or out and why.
6. **New plan**, never overwriting the live one: `a9_campaign_plan.py` for `win_2026-10-05` into
   `/speed-scratch/o_iseri/5J/modelA/campaign_win5/manifests/plan_ES-MAD-BERRUGUETE_win5.csv` (and a local copy under
   `wp9o_win5/`), built on the sealed win3 building lists as the manager decides after item 5 (until then use the win3 lists and
   say so). Compare with the live plan `plan_ES-MAD-BERRUGUETE.csv` (read it by scp to a local copy; do not open it for writing):
   for every row, same `run_id`? same `seed`, `n_flats`, placement? same `src_idf_md5`? **Expected:** the 1,001 unchanged stems have
   identical rows (so the task SKIPS them, R1 d); the changed stems have a new `src_idf_md5` (and new flats for the 113); the 585
   deferred degenerate-building runs are now rows with their 10-05 md5 (those in the 58 fixed; the 31 unchanged ones too, as
   delivered). Print: rows new / identical / changed md5 / changed n_flats / dropped (a stem that left the plan) / added; and the
   run index ranges to submit (rows that are not identical to a done result), sorted so the two smoke buildings come first.
   **Seen failing:** a planted changed md5 on one unchanged row must show up as a re-run row.
7. Write for the manager: the exact `sbatch` line for the resubmission (`--array=<ranges>%32`, `-t 7-00:00:00`,
   `--exclude=antenna1`, using a COPY of the campaign code in `campaign_win5/`; the old code is untouched), and the list of old
   result files that become void (stems of the 171) to be moved by the manager into a `results_void_win3/` folder AFTER the live
   array ends (not by you).

## Done means
Items 1-6 with numbers in the state file (what you re-measured, what you took from OpenUBEM), item 7 written, a `Next` a cold
agent can start from, nothing UK opened/listed/passed, nothing on Speed touched except the new names. End with
"no job submitted, state written to <path>".
