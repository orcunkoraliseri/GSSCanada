# WP1 sampling frame and labelling sheets (Employee C) - implementation state
Task doc:   5J_docs_occ/impl/2026-09-26_wp1_task.md
Status:     DONE
Started/finished: 2026-09-26 (one session, local only, no cluster jobs)
Scripts:    C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\scripts_wp1\  (sample_wp1.py = sampler, checks_wp1.py = checks 1-5 and 7, breaks_wp1.py = deliberate breaks, look20.py = check 8)
Outputs:    C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\wp1\
**Seed: 20260926** (one integer, fixed in `sample_wp1.py`; `random.Random(seed)` used sequentially in a fixed order).

## Ledger
No cluster jobs. Local runs of `sample_wp1.py` (about 45 s each):
- run A (scratch) -> manifest sha256 f03364df...; first real run wrote sheets with 9 columns instead of 10 (bug in the blank-answer count, caught by check 7 "row width"); fixed (`blank = [""] * 8`) and re-run -> real outputs.
- run B (real output dir, final script) and run C (scratch `--out`, same seed): identical manifest, author sheet and sealed file (see check 6).
- run D (scratch, seed+1 copy of the script): different manifest (break for check 6).

## Outputs and sha256 (real run, `_5J_data\wp1\`)
| file | sha256 |
|---|---|
| sample_manifest.csv | f03364df235b84f63dbe37909bfe1538d240dc3bd93f7b6e8afa517554c0002d |
| universe_counts.csv | d6695887d920008bf02c866e4e3112e2ceb1d90fd2c9fc1af49c8d6988feed02 |
| labelling_sheet_author.csv | ed6e3ab1b9d4d0111b009c432bb64f0fe13b0d4042d2c19b7aa97c47a1960230 |
| labelling_sheet_colleague.csv | 67ff2cb5c707deb4d4b49cac085f12aa96d6dc2ea4a3a5ea11ce7cc5c5cc700a |
| labelling_sheet_author_readme.txt | 1106cbf8390d3cef3101062507fd33c27648819a11ccdc2d814438b5913540e0 |
| sealed/test_manifest_SEALED.csv (read-only attribute set) | d5f66eb32abde4258361018195ca8835995a336ef0bfb3df1ab3f5e2b62f26b9 |
| quota_report.csv (extra) | 50ddb5671e1b1f58b7c6c68ff8b421c1dba5f994a0f41d8c8c9cb58d1e9be2c3 |
| stratum_merges.csv (extra) | 7dbeec1817a93012d57df90dc5cd0ae30711842afcb7a315680e42c186e7e0d0 |
Also `run_log.txt` (counts printed by the sampler). **Nothing may read `sealed/test_manifest_SEALED.csv` until the manager freezes the gates.** (I did read the test rows of the ordinary `sample_manifest.csv` to check groups and run the checks; that file is the manager/modelling copy, per the task.)

## Verified
All numbers read from the script output (`run_log.txt`) or the check output below.
- Montreal universe: 560,309 permits; residential rule (WP0-A) 420,572 (equals WP0-A exactly); all 420,572 have non-empty `nature_travaux`. Universe = 420,572.
- Toronto: 1,083,669 unique (PERMIT_NUM, REVISION_NUM) keys (equals WP0-A); WP0-A residential rule 729,339 (equals WP0-A exactly); plus 2,386 extra rows (see Decisions 1); minus 2,001 with empty text after removing the "HVAC -" prefix and trimming. Universe = 729,724.
- Keyword-group counts in the universe (first-match regex, groups per task):
  - Montreal: HP 2,537 · AC 623 · F 504 · I 4,722 · W 65,541 · N 18,340 · D 13,731 · NONE 314,574.
  - Toronto: HP 267 · AC 515 · F 4,367 · I 2,556 · W 18,567 · N 33,559 · D 53,982 · NONE 615,911.
- Building-type classes: Montreal SF 164,947 · S24 (2 to 4 dwellings) 162,618 · MULTI 67,994 · OTHER 25,013; Toronto SFD 596,825 · SMALL 50,411 · LARGE 82,488.
- Decades: Montreal pre2000 50,112 · 2000s 92,227 · 2010s 153,936 · 2020s 124,297 · unknown 0. Toronto pre2000 10,983 · 2000s 198,027 · 2010s 301,288 · 2020s 180,716 · unknown 38,710 (no issue date).
- Strata: Montreal 114, Toronto 99 final strata; 30 merges (10 Montreal, 20 Toronto) in `stratum_merges.csv`, all within building type (no cross-type merge needed).
- Sample: 2,600 rows = Montreal test 800, cal 800, dev 400; Toronto test 300, cal 300. Double label 400 (Montreal 300: test 120, cal 120, dev 60; Toronto 100: test 50, cal 50). Per-group counts equal the quotas in all 40 (city, split, group) cells; no shortfall anywhere (40 of 40 rows have achieved = quota, none carry a note).
- Redraws (permits skipped because their normalised text was already in the sample): Montreal test 171, cal 229, dev 112; Toronto cal 5, Toronto test 0.
- Toronto rows in the sample with the "HVAC -" prefix: 80 of 600. Toronto rows with unknown issue date: 31 (own stratum "unk"). Minimum pi 8.07e-05, maximum weight 12,392, no pi equal to 1.
- Accents: read as UTF-8 (with BOM handling, as WP0-A did) there is **no** U+FFFD in any Montreal or Toronto text (0 of 420,572 and 0 of 729,724); accented letters such as e-acute, e-grave, c-cedilla are intact in the sample. The "broken accents" seen in a Windows console are a display artefact of that console, not of the file. `text_raw` is exactly as read.

### Checks (command; passing result; result of the deliberate break in temp copies under the scratchpad, never on the real outputs)
Pass run: `python checks_wp1.py ..\wp1` gave PASS on all of: 1 (rows 2600, duplicated source_id 0, duplicated row_id 0); 2 (439 stratum-split cells, 0 violations); 3 (2600 rows re-read from the source files: not residential 0, source row missing 0, text differs from source 0); 4 (0 cells outside 1 pp); 5 (0 repeated normalised texts); 7 author sheet (2600 rows, header ok, no problems) and colleague sheet (400 rows, no problems).
Break run: `python breaks_wp1.py <scratch>` (every line below is FAIL, as it must be):
1. Disjoint splits. Break: one test row copied into cal. Result: FAIL "rows 2601, duplicated source_id 1".
2. Weights add up. Check: for each stratum and split, sum(weight) = stratum universe count minus rows already drawn in earlier splits, plus pi*weight = 1 per row, plus the stored `pop_at_*` columns agree. Break A: one pi times 1.5: FAIL ("pi/weight" violation). Break B (pi and weight both changed so pi*weight = 1 still holds): FAIL "weights sum 18649.1667 != pop 19182". So the sum test itself discriminates.
3. Universe rule. Check re-reads every drawn permit from the source CSV (Montreal by `no_demande`, Toronto by key with the same file priority) and re-applies the rule with separate code, and compares the text. Break: one Montreal row replaced by a real "Commercial" permit: FAIL "not residential 1".
4. Quotas. Break: 20 W rows removed from Montreal test: FAIL (W share 15.9 % vs 18 %, not listed as a shortfall).
5. No duplicate normalised texts. Break: one text copied onto another row: FAIL "normalised texts repeated 1".
6. Reproducibility. Two runs, same seed: manifest sha256 f03364df235b84f63dbe37909bfe1538d240dc3bd93f7b6e8afa517554c0002d both times (real dir and scratch `--out`); author sheet and sealed file also identical (ed6e3ab1..., d5f66eb3...). Break: copy of the script with seed 20260927: manifest 3ab065e1..., sealed b1732cea..., i.e. different. 
7. Labeller-blind sheet. Check: header is exactly row_id, text, W, I, HP, AC, F, N, D, BAD; every answer cell empty; the text of each row equals `text_raw` of the same row_id in the manifest; no cell contains "stratum", "keyword_group", "keyword group" or any of the 213 stratum labels. Break A: " HP" appended to one text: FAIL (text differs from manifest raw text). Break B: an extra `keyword_group` column: FAIL (header, row width). Both sheets pass on the real outputs. Coverage: the sheet has 2,600 rows / 400 rows and the colleague ids are exactly the double_label = 1 rows (400).
8. Look at 20 random rows per city (`look20.py`, seed 8). Judged by eye:
   - Montreal: all 20 contain a real keyword hit of the group shown; **3 of 20 look wrong as a work event**: a fuel-oil tank fire separation labelled F ("mazout"), a contractor name "CHAUFFAGE SARCELLE" labelled F, and demolishing a low wall labelled D. (The label spec already treats these as traps; the regex is only a first pass.)
   - Toronto: all 20 contain a real hit; **2 of 20 look wrong**: two new-build texts sit in NONE because the N pattern misses "new single family dwelling" and "construct a new 2 storey SFD". So N is under-detected in Toronto (the N quota is met, but NONE holds unlabelled new builds). Regexes not changed.
   - Toronto texts often glue two sentences ("...HRV systemHVAC - Proposal ..."); raw text kept.

## Decisions
1. **Toronto extra rows.** The task says 2,394; I count 2,386. The 8 missing rows are "Window Replacements (except SFD)", which already match the WP0-A rule through the substring "sfd" (so WP0-A double-counted them in its 2,394). Extra values counted as residential (exact, case-insensitive): Residential 181, House 81, Residential Building 14, Residential Porches 267, Residential Decks 176, Residential Carports 120, Live/Work Unit 81, Group Home 571, Boarding/Lodging House 524, Student Residence 371 (total 2,386). All were then subject to the non-empty text rule.
2. **Toronto residential rule = the WP0-A script's rule** (`scripts_wp0\dedupe_full.py`, keyword "laneway", not "laneway suite"), because only that version gives 729,339. Duplicate keys: cleared_since2017 > cleared_2000_2016 > active, first row kept (as WP0-A).
3. **Toronto HVAC prefix.** Only a leading exact "HVAC -" is stripped (as WP0-A counted). `text_clean` = raw minus that prefix, trimmed; `text_raw` kept; column `hvac_prefix` = 1 if stripped. The empty-text rule uses `text_clean` (2,001 dropped; 1,772 of them have an empty raw description in the WP0-A rule set, the other 229 are extra-type rows or descriptions that are only "HVAC -"; I did not split the 229 further). Group regexes, duplicate check and the type use `text_clean`; the labeller sheet shows `text_raw`.
4. **Montreal `source_id` = `no_demande`** (unique in all 560,309 rows; `id_permis` is not: 560,281 unique). Toronto `source_id` = "PERMIT_NUM|REVISION_NUM".
5. **Montreal building type (4 classes, from `description_categorie_batiment`, accents removed, lower case)**: OTHER first (words dependance, garage, piscine, remise, accessoire, abri, stationnement, "permis ancien", "non categorise", "hp residentiel", commercial, mixte, autres, "comm"); then S24 (2, 3 or 4 logements; bi-, tri-, duplex, triplex, quadruplex, H2, H3); then MULTI (multi..., H4/H5/H6, "N a M logements", 12+ and 36+, "4 logements et plus", condominium, maison de chambre, collective, hebergement, personnes agees, batiments en hauteur; plain "multiplex" goes here); then SF (1 logement, unif..., H1, cottage, familiale, bungalow, jumelee, rangee, chalet, maison mobile, "residentiel"); anything else OTHER. Code: `mtl_type` in `sample_wp1.py`. 89 distinct residential values seen.
6. **Toronto building type (3 classes, from STRUCTURE_TYPE)**: LARGE = Apartment Building, Multiple Unit Building, Stacked Townhouses, plus group home, boarding/lodging house, student residence, "residential building"; SMALL = 2 Unit, 3+ Unit, Duplex, Triplex, Converted House; SFD = everything else (SFD..., townhouse, laneway, and the extra "Residential", "House", porches/decks/carports, live/work).
7. **Decade** from the year of `date_emission` (Montreal) / ISSUED_DATE (Toronto); no valid year -> decade "unk" (Toronto only, 38,710 permits, mostly active permits with no issue date). It is treated as a decade slot after "2020s" for the nearest-decade merge rule.
8. **Merges** (fewer than 5 permits): done once on the full universe, smallest first, into the nearest decade of the same city, group and type (ties: larger stratum, then later decade); a cross-type fallback exists in the code but was never used. Merged permits keep their true decade in the manifest (`decade`) while `stratum` shows the merged stratum.
9. **Draw order** test (Montreal, Toronto), cal (Montreal, Toronto), dev (Montreal). Each stratum has one seeded random order; a split takes from the front. Groups are processed HP, AC, F, I, W, N, D, NONE; a group that cannot fill its quota would hand the rest to NONE (never needed). Within a group, the quota is spread over strata proportionally to the universe count still in the stratum at draw time (largest remainder, capped by the permits still available). If a stratum ran out because of repeated texts, the deficit would be re-spread over the other strata of the group (never needed at the group level).
10. **Duplicate texts.** Normalised text = text_clean with text inside guillemets, straight double quotes and curly double quotes removed, accents removed, lower case, every non-letter/non-digit run turned into one space (digits kept). If that is empty the trimmed lower-case raw text is used. A repeated normalised text (across both cities and all splits) is skipped and the next permit in the stratum's random order is taken. **This slightly favours rare texts** (a common phrase can enter the sample only once, so common phrases are under-represented compared with their population share). The skipped permits stay in the stratum population when pi is computed (pi = drawn / population at draw time, population = stratum count minus permits already drawn in earlier splits), so weights add up to the population as the task requires; skipped permits are never used later.
11. **Double labelling**: within each city and split, the number is proportional to the split size (Montreal 60/120/120 for dev/cal/test, Toronto 50/50), spread over keyword groups by largest remainder, chosen at random within each group.
12. **Sheets**: row_id = random 6 characters from A-Z (no I, O) and 2-9, unrelated to source; author and colleague sheets are shuffled independently (utf-8 with BOM so Excel shows accents). The sheet text is `text_raw` exactly. The readme (3 lines) is in `labelling_sheet_author_readme.txt`.
13. **Extra manifest columns** (task lists the first 13): `hvac_prefix`, `issue_year`, `source_file` (which Toronto file the kept row came from; Montreal = montreal_permis_construction), `type_raw` (the raw type text). Extra output files: `quota_report.csv`, `stratum_merges.csv`. `universe_counts.csv` has extra columns (`n_cells_merged_in`, `pop_at_test/cal/dev`, `stratum`).
14. **Sealed copy**: `test_manifest_SEALED.csv` was written by the same script, set read-only (file attribute). A re-run of the script deletes and rewrites that file (same content); do not re-run against the real output folder after the manager freezes the gates.

## Next
Manager: review this doc; the author reads `5thJ_02_Label_Spec.md` and starts on `labelling_sheet_author.csv`; a colleague (not yet named) gets only `labelling_sheet_colleague.csv` (400 texts). Then freeze the gates (design doc section 7), record the sealed sha256 above, and only then open the sealed file. The manager may want to decide whether the N pattern (misses "new single family dwelling") needs a second pass; it only affects how strata were built, not the labels.

## WHAT I DID NOT VERIFY
- The keyword regexes are the task's, not tuned; I did not measure their recall or precision beyond the 40 rows looked at (5 of 40 group hits looked wrong as events, see check 8).
- Weight identity is checked against my own recomputation from `universe_counts.csv` and the manifest, not against a second independent universe count; the universe totals (420,572 and 729,339) equal WP0-A's, and the 2,386 extra rows and the empty-text drops are my own counts.
- Did not check that Montreal `no_demande` maps one-to-one to a single address/permit in the roll (WP0-A join is a later step; the roll was not joined here).
- The Toronto issue-date year for the two 23-character date formats was taken from the first 4 characters only; I did not open a sample of the odd-format dates.
- Not tested: opening the sheets in Excel (only BOM + comma CSV written); Windows read-only attribute is not real protection, only the sha256 is.
- Did not test the colleague sheet for being a different shuffle than the author sheet beyond the fact that they are separate `rng.shuffle` calls on different lists.

## Progress Log
- 2026-09-26 (Employee C): built `sample_wp1.py`, ran it (seed 20260926), wrote all outputs and the seven checks with deliberate breaks (all break as expected) plus the 40-row look. 2,600 rows drawn, no quota shortfall. One bug found by check 7 and fixed (sheet had 9 columns, needs 10). Status DONE.
