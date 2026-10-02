# 5J Step 9m: full code chain in the campaign skip key - implementation state
Task doc:   Step9_docs/impl/2026-10-01_wp9m_codekey_TASK.md
Status:     IN PROGRESS (staged test job submitted 19:32 EDT, not read)

## Ledger
* 1408456 · staged codekey test (1 CPU, ps, 7-day, --exclude=antenna1) · SUBMITTED 2026-10-01 19:32 EDT · exit pending · log `/speed-scratch/o_iseri/5J/modelA/campaign_stage9m/logs/codekey_1408456.out`

## Files
* Local `5J_docs_occ/tools/speed/a9_campaign_task.py`: OLD md5 8bcf9f152e1fa7e99bb4df55c0044085 (kept as `a9_campaign_task_pre9m.py`), NEW md5 dd0c1bd2779d27bd08902f105ff4916f.
* Stage (new, Speed): `/speed-scratch/o_iseri/5J/modelA/campaign_stage9m/` holds `a9_campaign_task_new.py` (= the new file), `codekey_test.sbatch`, logs/. The job itself copies `campaign/root/`, the one smoke result `results/ES-MAD-BERRUGUETE_05e17b2bf818153b_def_0.json` and `inputs/zone_map_win3.csv` into the stage (copy done inside the job, not on the login node), puts the new file into the stage's `root/5J_docs_occ/tools/`, runs with `A9_CAMP`=stage. Live copy on Speed NOT touched; nothing written under live results/ or root/.
* Changes in the file: `CAMP` from env `A9_CAMP` (default unchanged, `LIVE_CAMP` kept); `hashes_static()` now = md5 of the sorted (path, file md5) lists of the LOADED chain: `code_chain()` imports the household chain (`load_hh()` + `setup_modules()` if not yet set up) and the writer module `5thJ_modelA_idf` in-process, then `_closure()` follows module globals and function/class home modules (the households chain is loaded with spec_from_file_location and is NOT in sys.modules, so sys.modules alone would miss it); only files under /speed-scratch/o_iseri/ and not site-packages / lib/python. File lists fixed once per process, md5s read fresh each call. Result json gains `code_files_writer` / `code_files_hh`. Check job prints both lists (`CODE_FILES_WRITER`, `CODE_FILES_HH`). New sub-command `codekeytest <manifest> <run_id>` (refuses to run unless A9_CAMP is a stage). `full_ctx` only calls `setup_modules()` if not yet done.
* Writer import side effects checked by reading (local copy): `5thJ_modelA_idf.py` top level = imports, sys.path insert, `importlib.import_module("5thJ_idf_mz")`, constants, os.environ reads; no file writes, no argv parsing (argparse only under `__main__`). `5thJ_idf_mz.py` top level: sys.path inserts and two imports. OK to import in-process.

## Verified
* Local only: syntax parse OK (py ast.parse). Nothing else yet.

## Decisions
* writer_md5 / hh_md5 formula: md5 of lines "path md5" sorted by path (path included, so moving the campaign changes the key; the manager swap puts the live file under the live paths, and all 36 smoke results re-run once, as planned).
* Stage test uses a DEF-pool result (no household placement needed), so the household context is never built in the test.
* Test (c) edits the stage copy of `4thJ_step8_idf.py` (writer chain); (d) edits the stage copy of `5thJ_design_tables.py` (loaded from the stage); (d2) WEAK test for every household-chain file outside the stage (`households/repo`: trigger_act2, step7 chain): md5 altered in the list only.

## Next
Manager: read `/speed-scratch/o_iseri/5J/modelA/campaign_stage9m/logs/codekey_1408456.out` (single file, `tail -80`). Expected lines: `CODE_FILES_WRITER n`, `CODE_FILES_HH n` (lists), `GATE (a)...`, `GATE (b0)... PASS`, `GATE (b)... PASS`, `GATE (c)... edit ... PASS` + `restored ... PASS`, `GATE (d)...` same, `GATE (d2) WEAK...`, `CODEKEYTEST_SUMMARY ALL PASS`. Exit 0 = all pass. Check with `sacct -j 1408456 -X -o JobID,State,ExitCode`.
Swap (only after smoke check 2, job 1408136, ends; the smoke 36 runs then re-run once):
`scp C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools/speed/a9_campaign_task.py speed:/speed-scratch/o_iseri/5J/modelA/campaign/root/5J_docs_occ/tools/a9_campaign_task.py` (md5 must be dd0c1bd2779d27bd08902f105ff4916f), then re-run the smoke to re-key it before the full array.

## WHAT I DID NOT VERIFY
* Nothing on Speed has run yet: the closure may list more or fewer files than expected; if the (a) gates fail the job log shows it.
* Lazy imports inside functions (loaded only after first use) are not in the file list because the list is fixed at first call; the closure also cannot see modules loaded by name through importlib inside functions.
* Data files read by the code (corpus, splits, tables, zone map) are keyed separately (split md5s, zone map md5), not by this change.
* Import time of the household chain on every skip decision (setup_modules loads the Step 7 chain): not measured; the job log has timestamps only for the test.
* Run on the Windows side not done (Speed paths only); numbers of files in the lists are not yet known.

## Manager read (2026-10-01 19:34 EDT)
Log `campaign_stage9m/logs/codekey_1408456.out` read (tail 60); sacct COMPLETED 0:0. CODE_FILES_WRITER 4 (step8_idf, 5thJ_idf, idf_mz, modelA_idf, all under the stage root), CODE_FILES_HH 7 (step7_indoor, step7_schedules, decoder, encoder, trigger_act2 from households/repo; design_tables, modelA_households from the stage). (b0) old-key result -> RERUN; (b) re-keyed -> SKIP; (c) edit of 4thJ_step8_idf.py -> RERUN, restored -> SKIP; (d) edit of design_tables -> RERUN, restored -> SKIP; (d2) WEAK list-alteration for the 5 households/repo files PASS; CODEKEYTEST_SUMMARY ALL PASS. **ACCEPTED.** Consequence: after the swap every smoke result's key differs (old 4-file key), so the 36 smoke runs re-run inside the full array (cost about 36 runs, accepted). Swap after 1408136 ends.
