# 5J Step 9d: Model A households from own-country diary days (task doc for a fresh employee)

Written 2026-10-01 15:50 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md`, block "9B FINAL DRAFT" (the rules;
read it first), 9V items 3, 7, 8. Verified inputs: `Step9_docs/impl/2026-10-01_wp9a_inventory.md` section 5 (corpus path,
fields, counts, the back-off ladder lines).
State file you keep: `Step9_docs/impl/2026-10-01_wp9d_households.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
Model A households must use real diary days of their own country only, and a test household must never use a diary day that a
training household can use. This task writes the household split and the builder that turns a household into a year of
hourly presence and appliance series, and tests it on one building. Nothing is sealed by you; the manager seals after checking.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file, fold or argument for the UK (`GB`, `LDN`, `London`,
  `STDUNSTANS`, `uk`, `_uk`). The 4J schedule code accepts a fold `uk`: never pass it. Read only the Spain + Italy corpus copy
  `/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl` and the Spain / Italy episode parquets' columns hid, pid,
  weight_ind (as `tools/5thJ_design_tables.py` does). If any code you reuse reads a pooled or UK corpus by default, stop and
  write it in the state file.
* **No pilot generated-day pool and no pilot schedule file** may be read (they are probably built with UK-trained models).
* **No folder-wide or repo-wide search, no recursive listing, no wildcard that could match a UK file.** Open files by full name.
* **Compute:** Speed via `sbatch` only (`-t 7-00:00:00`, `--exclude=antenna1`, at most 6 CPUs; the cap is shared and busy).
  Never python on the login node. Never wait for a job: submit, write the id, end the turn.
* Write only: `5J_docs_occ/tools/5thJ_modelA_households.py`, your state file, and `/speed-scratch/o_iseri/5J/modelA/households/`.

## Code to reuse (import or call, never copy-edit; name each function you use in the state file)
* `tools/5thJ_design_tables.py`: `read_household_sizes`, `read_household_weights`, the weighted key of `draw_households`.
* 4J `4thJ_step7_schedules.py` (the copy the pilot used; find its path from the pilot's household builder
  `tools/speed/hh_build.py` and the Step 7 district builder `tools/speed/s7_hh_draw.py` / `s7_hh_build.py`): bucket fields, the
  back-off `draw` (lines about 245-257), and the episode-to-presence / appliance conversion with the act2 rule `prefix2_major`.
* The pilot's people and appliance levels per household (the same source the pilot builder used; name it).

## What to write
1. **Household split:** per country, positive-weight households stratified by size (1, 2, 3, 4, 5+), 70 / 15 / 15
   dev / val / test, seed 9101; three hid lists per country with md5, plus a respondent-to-split table.
2. **Split pools:** per country and split, the bucket index of real diary days (key = respondent; a day belongs to exactly one
   split). Print per split: respondents, days by day type, buckets, buckets with at least 5 days.
3. **Household-year builder:** given (country, split, hid, run seed, weather year), for each member and each day of the year,
   draw one day from the member's own split by day type with the 4J back-off; record (respondent of the drawn day, depth). Write
   8,760-value presence and appliance series per household in the format the Model A writer's placement CSV expects
   (`dwelling_zone, hid, presence_csv, appliance_csv, n_members, appliance_peak_w`; see `tools/5thJ_modelA_idf.py`).
4. **Flat assignment:** for one run, distinct households of the run's split into the flats of one building, by survey weight
   without replacement (the pilot key), from the windowed zone map
   (`Step9_docs/impl/2026-10-01_wp9c_zone_map_win.csv` if present, else the no-window `2026-10-01_wp9c_zone_map.csv`; say which).

## Test (one sbatch job)
One Madrid building with 5 to 25 flats and one Bologna building with 5 to 25 flats; for each, one run per split (dev, val,
test). Report:
* Purity: every drawn day's respondent belongs to the run's split (read back from the written draw records, not the plan).
* Planted fault P1: put one test respondent's day into the dev pool in a copy; the purity check must FAIL on exactly the runs
  that drew it (or report it NOT_EVALUABLE if no run drew it, and plant it so that one does).
* Back-off depth table per country and split; series length 8,760; presence within [0, members]; appliance not negative.
* Same inputs and seed twice gives byte-identical series (determinism).
* Wall time and disk per household-year.

## Done means
Script written; job submitted and id written; the state file lists the reused functions with their file:line, the split counts,
and a `Next` naming the output files a cold agent reads and the table to fill. Nothing UK opened or passed; no pilot pool read.
End your turn with "job N submitted, state written to <path>".
