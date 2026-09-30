# 5J corpus guard - implementation state
Task doc:   5J_docs_occ/Step2_docs/impl/2026-09-29_wp1_corpus_guard_TASK.md
Status:     DONE (manager verifies)
Trigger md5 before: f02f52d15709765d135cf643623ba23c
Trigger md5 NEW:    c642cda47c762fc11775e5ab7e808417 (syntax ok; 9 lines marked `# 5J change (FINDING 5J-1)`)
## Ledger (local, foreground, no cluster)
- es run: rc 0, 2m37s, log `_5J_data/surrogate/wp1_guard/log_step9_major.txt`, out `wp1_guard/step9_major/`
- it run: rc 0, 2m45s, log `wp1_guard/log_it_major.txt`, out `wp1_guard/it_major/`
- (a git-bash md5 loop timed out to background id bbcawkc0p; read-only, superseded by the python compare below)
## Verified - audit of every path the trigger can open (code read only, nothing run, no UK/pooled file touched)
Trigger `tools/5thJ_step9_trigger_act2.py` (root = 4J_docs_occ, fold es|it):
- Step9_docs/outputs_step9/activity_appliance_map.csv: appliance map, no country rows; per-run, not per-fold (trigger:1115-1118).
- Step2_docs/outputs_step2/crosswalk_copresence.csv: bit positions (trigger:666; encoder.py:125 load_bit_positions); no country rows.
- Step2_docs/outputs_step2/outdoor_at_home.csv: code list (step7_indoor.py:96-111, called from step7 load_pool:194 and trigger act2 pool loader); no diary rows.
- Step7_docs/outputs_step7/generated_leg5_<fold>_constrained.jsonl: PER-FOLD generated diary pool, name carries the fold (trigger:668-669, 5J loader :600-634). Cannot pool countries by name; contents not opened by me (they are generated, not survey rows).
- Step7_docs/outputs_step7/schedules/leg5_<fold>_independent_seed1[_calYYYY]/ presence csv: PER-FOLD shipped schedules for the dwelling identity check (trigger:706-712, 740-750).
- **Step3_docs/outputs_step3/4J_step3_corpus.jsonl: POOLED es/uk/it corpus, hard-coded at trigger:685-686, read by step7 `load_households` (step7:440-482, filters `r["country"] != country` only AFTER json.loads of every line, so UK lines are parsed in-process).** This is FINDING 5J-1. It is fixed by this task (step 2), and it is the only pooling path: it is a task fix, not a new stop.
Imported 4J modules: `4thJ_step7_schedules.py` (imports decoder, encoder, `4thJ_step7_indoor`; its own `build()`/CLI with `--corpus` are NOT called by the trigger, only load_pool/load_households/assemble/_stratum_key are), `decoder.py` (no file reads), `encoder.py` (opens only crosswalk csv files, :125,:140), `4thJ_step7_indoor.py` (opens outdoor_at_home.csv only). No other module-level file reads found (grep for open(/read_csv/jsonl/outputs_step).
Conclusion: no other path can pool UK rows on a Spain/Italy run. Proceeding.
## Verified - guard and regression
- Guard refusal (`wp1_guard/guard_refusal_test.txt`, function called with a STRING, nothing opened): pooled path -> REFUSED exit code 3; empty `4J_step3_corpus.jsonl` in %TEMP% (created, deleted) -> REFUSED exit code 3; the es+it copy -> passes (test label says "ACCEPTED (bad)" by my wording slip; it is the expected pass).
- Guard also runs in main() right after parse_args (before run_fold) and again in build_dwellings; both log lines `GUARD corpus OK path=... md5=1a5163445291b54114832e192b0d9a05` (matches manager's md5 of the copy).
- Command (both runs, root = 4J_docs_occ, python313): `trigger --root <4J_docs_occ> --fold es --leg leg5 --year 2010 --seed 1 --households 100 --timestep 60 --shipped-suffix _cal2010 --out wp1_guard/step9_major` and `--fold it --year 2014 --shipped-suffix _cal2014 --out wp1_guard/it_major`. Default --corpus.
- md5 vs wp1_act2 (full table `wp1_guard/md5_compare.txt`): both folds 205 files on each side, same names, 204 non-manifest files EQUAL, 0 different.
  - EQUAL cycles_es.csv 95207cf6788b75011a6b6cc1abba4636; enduse_by_dwelling_es.csv ac89f6c89c3b164bbd968af37610fe67; step9_objects_es.idf 0ce45c98420e548710ed6e7b06537fde; stock_series_es.csv f5639bbf6907567c952d23d9bb13d41f
  - EQUAL cycles_it.csv 11d97d2140ab5b1dbf0cd405bc3ce9e2; enduse_by_dwelling_it.csv e44afdd0e092a99d51455603bfdd6f13; step9_objects_it.idf 2d91607aabaaf259e4071a3a2061ad20; stock_series_it.csv bce0bedae33302119195f9e824cba74d
  - all enduse_profiles/ files EQUAL (both folds)
- Manifest diff (both folds): only two NEW keys `pool/corpus_path`, `pool/corpus_md5`; 0 removed, 0 changed.
- Log line changes: one new line `GUARD corpus OK ...`; the PATCH and result lines are identical to wp1_act2 (es 2322.8 kWh, it 2111.5).
## Decisions
- Command of the regression runs was not recorded in the act2 state; reconstructed from manifests: es: `--root 4J_docs_occ --fold es --leg leg5 --year 2010 --seed 1 --households 100 --timestep 60 --shipped-suffix _cal2010` (act2 default prefix2_major); it: same with `--fold it --year 2014 --shipped-suffix _cal2014`.
## Next
Manager verifies; then design tables.
## WHAT I DID NOT VERIFY
- Contents of generated pool files (not needed; per-fold name).
- Did not run fold uk or open any UK or pooled file. Python PID 19328 untouched.
- The guard matches by basename and by path parts (`4j_docs_occ`, `step3_docs`); a renamed copy of the pooled file placed elsewhere would NOT be caught (the task specified name/location only).
- Corpus keys landed inside the manifest's `pool` block rather than top level (still new keys only).

## Verified (manager, 2026-09-29 ~21:37 local)
- Trigger md5 re-read: c642cda47c762fc11775e5ab7e808417 (= employee). Hard-coded pooled path gone (grep `outputs_step3` = 0 hits); `load_households` now gets the guarded path (trigger:705-708).
- Guard re-run by the manager (string argument, nothing opened): the real pooled path -> `GUARD corpus REFUSED`, exit 3; a made-up `D:\elsewhere\4J_step3_corpus.jsonl` -> REFUSED, exit 3.
- Regression md5 re-derived on both sides: `enduse_by_dwelling_es.csv` ac89f6c8... = ac89f6c8... (wp1_act2 vs wp1_guard); `stock_series_it.csv` bce0bedae... = bce0bedae....
- Accepted. Known limit (employee's own note, kept): the guard matches name and location only; a renamed copy of the pooled file elsewhere would pass. Rule stays: only the author ever handles the pooled file; 5J code only ever points at `_5J_data/surrogate/inputs/4J_step3_corpus_es_it.jsonl`.
