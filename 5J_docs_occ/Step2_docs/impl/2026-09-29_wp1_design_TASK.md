# TASK (employee, Sonnet): 5J design tables: buildings, households, climates (+ pilot subset)

Written 2026-09-29 ~21:20 by the 5J manager. Spec: `Step2_docs/5thJ_02_campaignDesignPilot.md` §2A, §2B, §2D and
2F (read them). State file: create `Step2_docs/impl/2026-09-29_wp1_design.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY), write as you go.

## Hard rules
* 🔴 UK licence: never open any UK diary file, UK episode file, UK manifest, UK schedule, or any file pooling UK
  rows (including `4J_docs_occ/Step3_docs/outputs_step3/4J_step3_corpus.jsonl`: NEVER open, grep or hash it).
  The ONLY diary-derived file you may read is the Spain+Italy copy
  `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl`
  (md5 1a5163445291b54114832e192b0d9a05). UK TABULA rows and UK weather are fine (not diary data).
* For UK households you **write a script only** (`tools/5thJ_design_households_uk.py`); you never run it. The author
  runs it later. Test it only on the Spain+Italy copy with `--country es` to show it works.
* Do not edit `tools/5thJ_step9_trigger_act2.py` (another employee is changing it now) or anything under
  `4J_docs_occ\` / `OpenUBEM\`. Do not touch python PID 19328. Local only. Never wait or poll.
* Python `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`. One script
  `tools/5thJ_design_tables.py` with a fixed `--seed` (default 5) writes all tables; rerunning must give
  byte-identical files (show two runs md5-equal).

## Tables (write to `Step2_docs/outputs_step2/`)
1. **buildings.csv**: 40 variants per country (es, uk, it), the SAME 40 reused on all three climates of that
   country (manager decision, frozen frame; write it in Decisions). Base = the 4J TABULA archetypes in
   `4J_docs_occ/Step8_docs/outputs_step8/archetype_idf_manifest.csv` (es 24 = 6 per class, uk 32, it 32; classes
   SFH, TH, MFH, AB). 10 variants per class; within a class spread over the periods (each period at least once).
   Varied by a Latin hypercube within the class:
   * `infiltration_ach` and `north_axis_deg` (the two arguments of `tools/5thJ_idf.py` `build`); north axis over
     [0, 360); infiltration range = the TABULA range for that country and class if the TABULA source rows give an
     air-change field (find it, cite file:line or column), else [0.3, 1.0] ach flagged in Decisions for the manager.
   * any other parameter ONLY if `build` or the 4J `derive` already reads it from the row dict (e.g. a U-value
     field) so it changes by editing the row, not the code; list which you used and why, or say none.
   Columns: `building_id` (e.g. `es_B01`), country, class, archetype code, every varied value, `pilot` (0/1).
2. **households.csv** (Spain and Italy only here): 60 households per country from the copy, stratified by
   household size (members per `hid`), proportional to the size distribution in the copy. Survey weights: look for
   a household or person weight for es/it in the 4J Step 1/Step 2 outputs (not in the corpus text); if found, draw
   with it and cite where; if not, draw unweighted and flag it in Decisions. Check the 5J trigger's household
   loader (4J `load_households` in `4J_docs_occ/tools/4thJ_step7_schedules.py:440`, read only) and say whether the
   same `hid` values can be passed to it (or what is needed) so these 60 are the ones simulated. Columns:
   `household_id`, country, size, weight (or blank), draw order, `split_draft` (40 dev / 10 val / 10 test, by size),
   `pilot` (0/1). The 4J `split` field in the corpus is NOT used for 5J splits (say so).
3. **climates.csv**: nine rows (es Madrid 2010, Valencia 2010, Seville 2010; uk London 2014, Birmingham 2014,
   Manchester 2014; it Bologna 2014, Turin 2014, Milan 2014): path, md5, RMSE from
   `_5J_data/surrogate/weather/epw/weather_score_5J.json`. Manchester and Milan are still downloading: status
   `pending`, md5 blank.
4. **Pilot subset (§2D):** Spain, climate Madrid 2010 (the one used in the wrapper tests), 5 buildings (one per
   class + one extra), 10 households, 2 of the 50 inputs repeated 5 times. Write `pilot_runs.csv` (run_id,
   building_id, household_id, climate, replicate), exactly 50 rows; show the count.
5. **design_md5.txt**: md5 of every table and of the corpus copy, the archetype manifest and the script.

## Checks (seen failing, then passing)
One small checker `tools/5thJ_check_design.py`: 40 buildings per country, 10 per class, every archetype
period used; 60 households per country with no duplicate `hid`; split counts 40/10/10; pilot has 50 rows;
every pilot household and building exists. Show it FAIL on a planted copy in `%TEMP%` (drop one household row),
then PASS on the real tables. SUMMARY + exit code as in `tools/5thJ_check_epw.py`.

## Report back (short)
Table row counts; the infiltration range source; weights found or not; whether the hids feed the trigger; checker
fail + pass lines; md5s; every decision you took.
