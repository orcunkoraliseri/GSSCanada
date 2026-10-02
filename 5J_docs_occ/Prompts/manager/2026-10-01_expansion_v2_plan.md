# 5J expansion (v2): plan and open decisions

Written 2026-10-01 14:26 EDT by the 5J manager after the author's ruling. State file for the expansion; the Progress Log
points here. Nothing below is run yet.

## 1. The author's ruling (2026-10-01 ~14:25, answer to the manager's two questions)
* **Expand this paper** (not a second paper): reopen the design, the simulations, the training and the sealed tests.
* **Districts:** Madrid Berruguete with Spanish households, Bologna Galvani 2 with Italian households, London St Dunstan's with
  UK households. **Lyon is out.** "Use UK data."
* Countries: Spain, Italy, UK; France "if possible" (Progedo did not approve the diary file lil-1065); other HETUS countries
  "if we can reach their datasets" -> research prompt `Prompts/deepResearch/T49_hetus_country_data_access.md`.
* Context the author was given: nothing was excluded by accident. The pinned model was trained on all Spanish and Italian
  development data; the Spain-only and Italy-only trainings were a planned transfer test (Step 5 part E).

## 2. The three districts (OpenUBEM European locations, final 2026-09-09 restatement)
Source: `C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_ACTIVE/europeanLocations/STATE_european_locations_v5.md` (head block).
| District | Buildings prepared | Households |
|---|---|---|
| Madrid Berruguete (ES-MAD-BERRUGUETE) | 1,187 | Spain (INE) |
| Bologna Galvani 2 (IT-BOL-GALVANI2) | 1,215 | Italy (ISTAT) |
| London St Dunstan's (GB-LDN-STDUNSTANS) | 1,240 | UK (UKDS SN 8128) |
Multi-zone, no-core layouts, one zone per dwelling, EnergyPlus 23.1 (same engine as 5J). The 4J step-10 campaign already ran
these districts with 4J households; 5J Step 7 used 100 Berruguete twins (2,034 dwellings).

## 3. Hard constraints that do not move (binding rules)
1. **UK, licence clause 2:** the 5J purpose must be registered in the author's UKDS account (SN 8128 attached) before any UK
   use. Author action.
2. **UK, licence clause 5:** no online AI tool may be used "in connection with" the UK data without written UKDS permission.
   The manager and its employees therefore never open, and never launch scripts that read, UK diaries or anything built from
   them (schedules, IDFs, EnergyPlus outputs, model weights). Two routes: (a) UKDS gives written permission; (b) the author runs
   every UK step themselves, and every step that reads UK-derived files (pooled training, scoring of pooled models), and the
   manager writes code against the data dictionary only. Route (b) also covers the pooled model, which then becomes
   UK-derived as a whole.
3. **FINDING 5J-3 is still open:** the Spanish and Italian household days come from the 4J generator trained partly on UK
   diaries. T48 (written 14:03) researches the licence; the UKDS answer settles it.
4. Speed rules (sbatch only, 7-day walltime, at most 30 CPUs, antenna1 excluded); GPU access ends about late October 2026.
5. Gates stay frozen (Step 4 `gates_frozen.md5`); no threshold changes.

## 4. Recommended shape (for the author to confirm)
* **Keep the closed results as Study A.** The Spain + Italy archetype tests were sealed and scored once; they stay valid as
  they are. The expansion adds **Study B**: a model trained on all countries and the three real districts, scored once on new
  sealed tests (new households and new buildings drawn only from the districts). Discarding Study A would throw away the only
  clean test result the paper has.
* **Households from real diary days of the same country.** Replace the 4J generated-day pool with real days drawn from the
  same country's diaries (matched by household type and day type). This removes the UK dependency of the Spanish and Italian
  households (FINDING 5J-3) for Study B, at the cost of fewer distinct days.
* **Order:** (1) author: T48 run, UKDS project registration and written question on clause 5; (2) Study B design for Madrid
  and Bologna (Step 2 v2) while the UK answer is awaited; (3) Madrid + Bologna campaign on Speed; (4) London only after the
  UKDS answer, by route (a) or (b); (5) training and one scoring before the GPU window closes; (6) rewrite.

## 4b. Workflow RULED 2026-10-01 ~14:51 (author: "start with Italy and Spain as one model, and second model Italy & Spain & UK,
in case there is a rejection from the UK Data Service")
* **Model A (starts now, the paper's main model if the UK is refused):** Spain + Italy. Districts Madrid Berruguete (Spanish
  households) and Bologna Galvani 2 (Italian households). Households from each country's own diaries only. New design (Step 9a),
  campaign (9b), the frozen gates reused (Step 4, no threshold change), training (9c), one scoring on new sealed tests (9d),
  district spread and speed (9e).
* **Model B (only with written UKDS permission):** Spain + Italy + UK. Adds London St Dunstan's with UK households. Same steps
  (10a to 10e) with new sealed tests that include London. Model A is not changed by Model B; both are reported.
* **Decision gate (UKDS answer):** yes, with permission for AI-assisted processing -> Model B runs as above; yes, but no AI tools ->
  Model B only if the author runs every UK step and every step reading UK-derived files, else dropped; **no -> the paper ends
  with Model A**, London and the UK are named as a limitation, the email and the answer are kept on file.
* **Clock:** GPU access ends about late October 2026. Model A goes first so that the paper stands on it alone; Model B is fitted
  in only if the UKDS answer arrives in time (stated response time five working days).
* **Default-schedule comparison (author, 2026-10-01 ~14:52):** the occupancy-inserted district runs are compared with the
  OpenUBEM default-schedule runs of the same neighbourhoods, read from
  `C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_ACTIVE/europeanLocations/results/` and `.../outputs_3D/`. The default runs are being
  re-run now; the author expects them ready on 2026-10-02. Read them only after the author says they are done; name files in
  full (no folder-wide search). Default schedules contain no diary data, so London's default runs are not UK-derived.
* **Pilot:** the v1 Spain + Italy archetype results (Steps 1 to 8) are the pilot; how the pilot treats its UK-trained day pool is
  still the author's call (re-run with own-country days, or described as superseded method development).

## 5. Open decisions (asked 2026-10-01 14:26)
* D-V2-1 UK route: (a) ask UKDS for written permission first (recommended) or (b) author runs all UK and pooled steps.
* D-V2-2 Study A kept as is + Study B added (recommended), or Study A demoted to a pilot.
* D-V2-3 Household days for Study B: real days of the same country (recommended) or the 4J generated pool.

## 5b. Rulings 2026-10-01 ~14:40 (author's answers)
* **D-V2-2 RULED:** the Spain + Italy results become a **pilot**, possibly a chapter before the main study; the main study is
  one model trained on all countries and the three districts.
* **D-V2-3 RULED:** "every country needs to be based on their datasets; using UK as resource for it or ES is not correct."
  Every country's households come from that country's own diaries only. The 4J generated-day pools (Spain from the UK+Italy
  model, Italy from the Spain+UK model) are therefore out for the main study.
  Consequence flagged to the author: the pilot (Study A) itself used those pools, so the pilot carries the same problem; either
  the pilot is re-run with own-country days or it is described as method development that the main study replaces.
* **D-V2-1 still open:** the author ran T48 instead of choosing; RT48 vetted (`Prompts/deepResearch/VETTING_RT48.md`): only
  UKDS can settle model weights and cloud AI use. Recommendation unchanged: ask UKDS in writing (six questions in the vetting
  file); Madrid and Bologna proceed meanwhile.

## 6. Log
* 2026-10-01 14:26: plan written; T49 written; draft reference Kalkan B. -> S. (author: "probably Sinan Kalkan").
* 2026-10-01 14:42: rulings D-V2-2 and D-V2-3 recorded; RT48 vetted MIXED.
* 2026-10-01 14:51: workflow ruled: Model A (ES+IT, Madrid+Bologna) now; Model B (+UK, London) only with UKDS permission.
* 2026-10-01 14:52: default-schedule comparison source recorded (OpenUBEM results/ and outputs_3D/, ready ~2026-10-02).
* 2026-10-01 14:54: T50 (open diary files) and T51 (application routes) written next to T49.
* 2026-10-01 15:11: D9-3 RULED by the author ("yes go with pilot settings"): occupancy runs use the pilot settings (heating 20 C, cooling 26 C, people + appliances); each building gets one extra default-schedule run under the same settings for the comparison; the OpenUBEM heating-only re-run is a cross-check.
* 2026-10-01 15:20: D9-5 RULED by the author ("of course insert windows"): Model A IDF copies get windows (TABULA window share per archetype, as the pilot builder); comparison uses our own same-settings default run with windows.
* 2026-10-01 15:23: window data settled (OpenUBEM TABULA library per archetype, rectangular outdoor walls only); IDF-writer task launched.
* 2026-10-01 15:27: Model A base = OpenUBEM's own windowed IDFs (author-ruled method there); our own window code dropped.
* 2026-10-01 15:35: author ruled Model A uses the windowed OpenUBEM results; RT46/RT49/RT50/RT51 returned, vetting running.
* 2026-10-01 15:50: Model A design completed to a freeze-ready draft; only the compute size (D9-4) waits on measurements.
