# TASK (employee, Sonnet): 5J households v2: survey weights + run exactly the chosen households

Written 2026-09-29 ~21:40 by the 5J manager. Read first: `2026-09-29_wp1_design.md` (same folder; the "Manager
rulings" section at the end) and `2026-09-29_wp1_corpus_guard.md`. Spec: `Step2_docs/5thJ_02_campaignDesignPilot.md`
§2A Households ("drawn with the survey weights, stratified by household size").
State file: create `Step2_docs/impl/2026-09-29_wp1_households_v2.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY); write as you go.

## Hard rules
* 🔴 UK licence. Never open, read, grep, hash or list the CONTENT of any UK file: `episodes_uk.parquet`, the pooled
  corpus `4J_docs_occ/Step3_docs/outputs_step3/4J_step3_corpus.jsonl`, or any file with UK rows. Never use a
  wildcard that could match them (no `episodes_*.parquet`, no `*.parquet` over a folder): name each file in full.
* 🔴 **No repo-wide or folder-wide search** (FINDING 5J-2). Grep only the files named below. If you need another
  file, find it by reading a doc, not by searching.
* Files you may read: the Spain+Italy copy `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl`;
  `4J_docs_occ/Step1_docs/outputs_step1/episodes_spain.parquet` and `.../episodes_italy.parquet` (weight and id
  columns only; not UK data); `.../codebook_facts_spain.md`, `.../codebook_facts_italy.md`; the 5J tools; 
  `4J_docs_occ/tools/4thJ_step7_schedules.py` and `decoder.py` (read only).
* Edit only: `5J_docs_occ/tools/5thJ_design_tables.py`, `5thJ_check_design.py`, `5thJ_design_households_uk.py`,
  `5thJ_step9_trigger_act2.py` (additive, mark `# 5J change (households v2)`). Never edit `4J_docs_occ\` or
  `OpenUBEM\`. Local only, python `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`. Do not touch
  python PID 19328 (weather download). Never wait or poll. Past ~150k tokens: stop, write state, "handoff needed".

## Part A: weights
1. From the codebooks, find the household id column in each episode parquet and how it maps to the corpus `hid`
   (show 3 matching ids per country). Spain: household weight `FACTOR_hogar` if present, else say so. Italy: no
   household weight exists; **manager ruling: household weight = `coefin` of the member with the lowest `pid`**.
   If a household has two different values of its weight in the file, stop and record.
2. `5thJ_design_tables.py`: within each size stratum keep the v1 counts (es 19/28/9/4; it 21/22/10/6/1), draw
   without replacement with probability proportional to the weight, seeded (seed 5; e.g. keys `u**(1/w)`, take the
   largest), fill the `weight` column. Splits and pilot re-derived by the same code as v1. Every corpus hid must
   have a weight; count and report any without (drop them from the draw, record the count).
3. `buildings.csv` and `climates.csv` must stay md5-equal to v1 (show). Two runs byte-identical (show).
   Keep v1 tables as `outputs_step2/v1_unweighted/` (copy, do not delete).
4. `5thJ_design_households_uk.py`: same weighted logic, with the UK episode file as an ARGUMENT only (no default
   path pointing at it). Test it only with `--country es` and the Spain parquet: its es rows must equal the es rows
   of the new `households.csv` (except `pilot`). Never run it on UK.
5. Checker: add "es/it weight non-blank and > 0". See it FAIL on a planted copy in `%TEMP%` (blank one weight), then
   PASS on the real tables. SUMMARY + exit code as before.

## Part B: `--hids FILE` in the trigger (md5 before: c642cda47c762fc11775e5ab7e808417)
6. New optional `--hids` (a csv with a `hid` column; default None). When given: a NEW function in the trigger
   (not in 4J) loads the corpus (through `check_corpus_guard`, as now) and returns exactly those households, in
   file order, with the same member/prefix parsing as `s7.load_households` (4thJ_step7_schedules.py:440-482: decode
   the prefix, first diary day per pid). An unknown hid, or a hid of another country: exit non-zero with one line.
   `--households` is ignored (print a line saying so). The Step 8 dwelling-identity check is skipped with a printed
   line (as `pool_path` does). New manifest keys only: `households/hids_file`, `households/hids_md5`, `households/n`.
6b. **(Added by the manager ~21:45.)** `tools/5thJ_idf.py` takes each household's presence from the 4J SHIPPED
   folder `4J_docs_occ/Step7_docs/outputs_step7/schedules/leg5_es_independent_seed1_cal2010/presence_HH_es_<hid>.csv`
   (`_household`, 5thJ_idf.py:317), which exists only for 4J's own 100 households. So the trigger must also WRITE
   the presence series of every dwelling it builds, to `<out>/presence/presence_HH_<fold>_<hid>.csv`, in exactly
   the shipped format: call 4J `s7.write_schedule_csv(path, series, "HH_<fold>_<hid>_Presence")`
   (4thJ_step7_schedules.py:359, read-only import) with the same series the Step 8 identity check compares
   (trigger ~:796; apply `rotate_to_midnight` only if the shipped files are rotated: find out from 4thJ_step7:520-536).
   Gate: in the default run every written presence file must be md5-equal to the shipped file of the same hid
   (show the count, e.g. 100 of 100 equal); seen failing: compare one written file against a DIFFERENT hid's
   shipped file (must differ). Do not edit `5thJ_idf.py`; write in Next that `_household` must read
   `<out>/presence/` instead of the shipped folder (a later task).
7. Default (no `--hids`) must stay byte-identical (the new `presence/` folder is the only allowed addition): re-run the Spain command in `2026-09-29_wp1_corpus_guard.md`
   (Verified, "Command") to `wp1_hids/es_default/`; all non-manifest files md5-equal to `wp1_guard/step9_major/`;
   manifest differs by no key (the new keys appear only with `--hids`) or by new keys only (say which).
8. See it fail: `--hids` with one made-up hid -> non-zero exit, before any EnergyPlus object is written.
9. **(Amended by the manager ~21:40: the appliance hazards are calibrated over the whole stock of the run,
   `calibrate_to_published`, trigger:1214, so a 10-household run would calibrate on 10.)** Households run: Spain,
   ALL 60 Spanish households of the new `households.csv` (write their hids to `outputs_step2/hids_es60.csv`; also
   write the 10 pilot ones to `outputs_step2/pilot_hids_es.csv` for later use), output `wp1_hids/es_60/`. Show
   the hids in `enduse_by_dwelling_es.csv` are exactly the 60, the 10 pilot hids are among them, the log has the
   GUARD line, and write the stock mean appliance kWh next to the default run's (2322.8) with one line on why they
   may differ (different households, calibration target the same).
10. State file: Status DONE, new trigger md5, the md5 lines, Next = "manager verifies; then pilot inputs to Speed".

## What the manager will re-derive
One Spain weight straight from the parquet for one drawn hid; the checker; one default-run md5 on both sides; the
10 hids in the pilot output.
