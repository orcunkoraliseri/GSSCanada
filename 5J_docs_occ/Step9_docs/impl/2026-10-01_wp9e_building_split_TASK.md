# 5J Step 9e: Model A building split (task doc for a fresh employee)

Written 2026-10-01 15:59 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md`, block "9C FINAL DRAFT" (the rule; read
it first) and 9V item 7. Input verified by the manager at 15:54 / 15:58: `Step9_docs/impl/2026-10-01_wp9c_wall_table_win.csv`
(2,352 lines; usable = `zone_map_reason` empty: Madrid 1,165, Bologna 1,171).
State file you keep: `Step9_docs/impl/2026-10-01_wp9e_building_split.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
Model A tests the surrogate on buildings it never saw in training. The building split must be fixed before any run, from the
windowed buildings, and a building must never sit in two splits. Nothing is sealed by you; the manager seals after checking.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). You need no file outside the ones named here.
* **No folder-wide or repo-wide search, no recursive listing, and no wildcard of any kind** (a wildcard line count hit a London
  file earlier today, FINDING 5J-4). Open files by full name only.
* **Compute:** this is a small table job; run it on the desktop, one process (`py`). No Speed job is needed.
* Write only: `5J_docs_occ/tools/5thJ_modelA_buildsplit.py`, your state file, and the folder `Step9_docs/impl/buildsplit/`.

## Code to reuse (import, never copy-edit)
* `tools/5thJ_design_tables.py` `rng_for` (the seeded stream the household split uses; the households script
  `tools/5thJ_modelA_households.py` `split_hids` shows the exact pattern: sort, shuffle with `rng_for`, dev = round(0.70 n),
  val = round(0.15 n), test = rest). Use the same pattern so both splits follow one rule.

## What to write
1. **Usable buildings:** rows of the wall table with empty `zone_map_reason`. Class = `building_type` (AB, TH, MFH, SFH).
   Flat band from `n_flats`: `1`, `2-8`, `9-24`, `25+`. Flag `no_outdoor_wall` when outdoor_eligible_rectangle +
   outdoor_too_small + outdoor_triangle + outdoor_other_shape = 0 (these buildings stay in the split, flagged).
2. **Split:** per district, per stratum (class x flat band): stems sorted, shuffled with `rng_for(9102, "bsplit", district,
   class, band)`, then dev / val / test by the rule above. Write per district three lists `buildsplit/<district>_<split>.csv`
   (columns stem, building_id, class, band, n_flats, no_outdoor_wall) and print their md5; plus one table
   `buildsplit/strata.csv` (district, class, band, n, dev, val, test).
3. **Run plan count (feeds the compute decision):** per district, runs = dev buildings x 9 (3 dev + 2 val + 2 test + 1 average
   household + 1 default schedule) + val buildings x 6 (2 dev + 2 val + 1 + 1) + test buildings x 6 (2 dev + 2 test + 1 + 1).
   Print runs per district and per class, and flats summed over runs (household-years needed).
4. **Checks (each printed PASS / FAIL with what it counted):**
   * every usable building is in exactly one split; counts per district add up to 1,165 and 1,171;
   * the three lists have no stem in common;
   * planted fault: in a copy of the lists, move one test building into dev as well; the overlap check must FAIL and name
     exactly that building; then the unplanted lists pass again (show both verdicts);
   * same seed twice gives byte-identical lists (md5 equal); a different seed gives a different list (seen failing).
   * Report strata where val or test is empty (expected for small classes; this is the D9-2 "not evaluable" case, not an error).

## Done means
Script written and run; lists, strata table and md5 written; the state file has the md5 of each list, the strata table numbers,
the run plan counts, and every check verdict. Nothing UK opened. End your turn with "done, state written to <path>".
