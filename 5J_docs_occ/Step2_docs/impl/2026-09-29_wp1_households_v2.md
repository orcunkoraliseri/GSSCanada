# 5J households v2 (weights + --hids + presence) - implementation state
Task doc:   5J_docs_occ/Step2_docs/impl/2026-09-29_wp1_households_v2_TASK.md (incl. amendments 6b and 9)
Status:     DONE (manager verifies)
Trigger md5 before: c642cda47c762fc11775e5ab7e808417
Trigger md5 NEW:    075fdd73188baedcb231241f8ddefb34 (syntax ok; all edits marked `# 5J change (households v2)`)
## Ledger (local, foreground, no cluster; python PID 19328 untouched; no UK/pooled file opened)
- v1 tables copied to outputs_step2/v1_unweighted/.
- wp1_hids/es_fail: --hids with hid 99999x -> exit 1, one line "HIDS refused: 1 hid(s) not in the es households of the corpus (first: 99999x; unknown)"; output dir NOT created (before any IDF object). Log log_fail.txt.
- wp1_hids/es_pilot10 (10 pilot hids, rc 0): SUPERSEDED by amendment 9 (kept). Its enduse hids = exactly the 10 (checked).
- wp1_hids/es_default_superseded_pre6b (default regression before presence/ was added, rc 0): SUPERSEDED by es_default (kept).
- wp1_hids/es_default (default command from wp1_corpus_guard.md, after 6b; rc 0), log_es_default.txt.
- wp1_hids/es_60 (--hids hids_es60.csv, rc 0), log_es_60.txt.
## Verified
Part A
- Household id: column `hid` in both parquets; corpus `hid` is the same string (es '00001','00002','00003'; it '000001','000002','000003'). es 9541/9541 corpus hids found; it 18435/18435 (parquet has 18439). Weight columns in parquet: weight_ind, weight_dia (no FACTOR_hogar).
- Weight used: es = weight_ind (FACTORF) of member with lowest pid; it = weight_ind (= coefin) of lowest pid (0 households with >1 value; strict check in code). Hids without weight: es 0, it 0.
- Draw: v1 counts kept (es 19/28/9/4; it 21/22/10/6/1), key log(u)/w (same order as u**(1/w)), seed 5, take largest. Weights in households.csv col `weight` (%.6f).
- buildings.csv md5 6162fec35def017644d476f4e2ef85fe = v1; climates.csv md5 bec7cfa924ec02c90a0ad1108cfa931f = v1. households.csv now e0a3a5e5c83fdca1552036e3f4aeaa2b (v1 13fe19c7...), pilot_runs.csv db37c61f35c18218cc9da31ea39bac6a (v1 e6eaae9e...; pilot households re-derived). Two runs byte-identical (4 md5s equal).
- UK script (new required `--episodes`, no default path): test with --country es + Spain parquet -> 60 rows equal to es rows of households.csv except pilot. Never run on UK.
- Checker: new check weight_es/it_nonblank_positive. Planted copy (%TEMP%, one es weight blanked): `FAIL weight_es_nonblank_positive bad=1 of 60`, `SUMMARY PASS=45 FAIL=1 NOT_EVALUABLE=0`, exit 1. Real tables: both PASS, `SUMMARY PASS=46 FAIL=0 NOT_EVALUABLE=0`, exit 0.
Part B
- Default run vs wp1_guard/step9_major: 204 non-manifest files md5-equal, 0 different (es enduse_by_dwelling ac89f6c8..., stock_series f5639bbf...); manifest: 0 keys removed, 0 added, 0 changed; new only `presence/` folder (100 files). Mean electricity 2322.8 kWh.
- Presence (6b): trigger writes `<out>/presence/presence_HH_<fold>_<hid>.csv` via s7.write_schedule_csv on rotate_to_midnight(presence, timestep) (shipped files are rotated, D-S9-3a). Default run: 100 of 100 md5-equal to the shipped file of the same hid. Planted: presence_HH_es_00035 vs shipped presence_HH_es_00094 -> different.
- es_60: 60 hids in enduse_by_dwelling_es.csv = exactly hids_es60.csv (set and order equal); the 10 pilot hids (pilot_hids_es.csv) all among them; log has GUARD, HIDS OK (md5 7bfae0a1...), NOTE lines; 60 presence files; manifest `households` = {hids_file, hids_md5, n=60}. Stock mean electricity 2307.2 kWh/dwelling.y vs default 2322.8 (different households, same calibration target, so a small difference is expected).
## Decisions
1. Spain has no FACTOR_hogar in the allowed files: fallback = weight_ind (FACTORF, a PERSON weight, varies within 6477 of 9541 households) of the lowest-pid member, same rule as Italy. FLAG for manager; true household weight is in DHOGAR (not opened, not on the allowed list).
2. Log-key form log(u)/w instead of u**(1/w): identical ranking, no precision loss for w up to ~1e5. u taken as 1-random() to avoid log(0).
3. Draw order within stratum is now by key (v1 was sample order); households differ from v1 by design.
4. Manifest keys for --hids are a top-level `households` block (hids_file, hids_md5, n), not inside `pool`.
5. --hids validation runs after the pool load and before any dwelling/IDF output; error exit code 1 via sys.exit(message).
6. Presence files are written in run_fold right after build_dwellings (default and --hids runs both).
## Next
Manager verifies; then pilot inputs to Speed. Later task: `5thJ_idf.py _household` (line ~317) must read `<out>/presence/` instead of the 4J shipped folder.
## WHAT I DID NOT VERIFY
- FACTOR_hogar for Spain (DHOGAR not read).
- The it/UK paths of the trigger with --hids (only es run); Italy hids not exercised.
- That es_60's mean kWh difference vs default is only household choice (not tested).

## Verified (manager, 2026-09-29 ~21:48 local)
- One Spain weight re-derived from `episodes_spain.parquet` (columns hid, pid, weight_ind only): hid 00388, members 00388_01 = 10982.835100, 00388_02 = 10779.906294; table weight 10982.835100 = lowest pid. OK.
- Checker re-run by the manager: `SUMMARY PASS=46 FAIL=0 NOT_EVALUABLE=0`, exit 0.
- Default run: `stock_series_es.csv` f5639bbf... = f5639bbf... (wp1_guard/step9_major vs wp1_hids/es_default). Presence written vs shipped: `presence_HH_es_04656.csv` md5-equal.
- es_60: enduse_by_dwelling_es.csv has 60 hids; hids_es60.csv = the 60 es hids of households.csv; the 10 pilot hids all among them; 60 presence files.
- Accepted.
## Manager rulings
- Decision 1 (Spain weight) ACCEPTED: household weight = person weight of the lowest-pid member in BOTH countries. Reason: Italy has no household weight at all, so one rule for both keeps the two countries' draws comparable; within-household spread is small (00388: 1.9%). The true Spanish household weight (`FACTOR_hogar`, raw DHOGAR file, codebook_facts_spain.md:23) is NOT used; it may be used later as a sensitivity check only. Method line for the paper: "households drawn with probability proportional to the diary weight of the reference member".
- Decisions 2-6 accepted. Later task (not now): `5thJ_idf._household` must read `<out>/presence/`; the pilot builder does this itself.
