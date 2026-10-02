# 5J Step 9m: full code chain in the campaign skip key (task doc for a fresh employee)

Written 2026-10-01 19:30 EDT by the 5J manager. Parent: `Step9_docs/impl/2026-10-01_wp9l_campaign_madrid.md` (read the
"Manager read" at the end) and its task doc `Step9_docs/impl/2026-10-01_wp9l_campaign_madrid_TASK.md`. Rules
`Step9_docs/outputs_step9/step9_rules.md` R1 (d). State file you keep (new): `Step9_docs/impl/2026-10-01_wp9m_codekey.md`
(Ledger, Files, Verified, Next, WHAT I DID NOT VERIFY).

## Problem (manager trace, 19:29)
`hashes_static()` in `tools/speed/a9_campaign_task.py` (line ~96) hashes only 4 code files. The code that actually shapes a run
is wider:
* writer: `5thJ_modelA_idf.py` -> `5thJ_idf_mz.py` -> `5thJ_idf.py` and `4thJ_step8_idf.py` (campaign `root/` copies);
* households: `5thJ_modelA_households.py` -> `5thJ_design_tables.py`, `5thJ_step9_trigger_act2.py` (loaded from
  `/speed-scratch/o_iseri/5J/households/repo/5J_docs_occ/tools/`) -> `4thJ_step7_schedules.py` (households/repo
  `4J_docs_occ/tools/`) -> `4thJ_step7_indoor`, `decoder`, `encoder` (find where they load from), and maybe more.
A static list will drift again. A change in any of these files today would NOT make a finished run re-run (gate class 61).

## Build (local `tools/speed/a9_campaign_task.py`, staged on Speed; do NOT touch the live copy)
1. Replace the static list by the LOADED chain: in the task process, import the household chain (`load_hh()` +
   `setup_modules()`) and the writer module `5thJ_modelA_idf` in-process (first check its top-level code has no side effects:
   no file writes, no argv parsing at import; if it has, say so and stop). Collect every `sys.modules` entry whose `__file__`
   is under `/speed-scratch/o_iseri/` and not under `site-packages` / `lib/python`. writer_md5 = md5 of the sorted
   `(path, file md5)` list of files the writer import added; hh_md5 = same for the household chain. Store both lists in the
   result json as `code_files_writer` / `code_files_hh`. Print the lists once in the check job.
2. Add an env override `A9_CAMP` for `CAMP` (default unchanged) so a staged copy can be tested.
3. The household builder hardcodes `R = /speed-scratch/o_iseri/5J/households/repo`; leave it, but the hashed paths must be
   the files actually loaded (check `__file__`, do not assume).

## Seen failing (on a STAGED copy only: `/speed-scratch/o_iseri/5J/modelA/campaign_stage9m/`, new folder)
Copy `campaign/root/` and ONE finished smoke result (`results/ES-MAD-BERRUGUETE_05e17b2bf818153b_def_0.json`) into the stage.
One sbatch job (1 CPU, `-t 7-00:00:00`, `--exclude=antenna1`) that, with `A9_CAMP` = stage:
(a) prints both code lists (expect at least the 8+ files above);
(b) a result re-keyed with the NEW hashes -> SKIP;
(c) append one comment line to a staged copy of `4thJ_step8_idf.py` -> writer_md5 changes -> RERUN; restore;
(d) same with the staged `5thJ_design_tables.py` (or another hh file under the stage) -> hh_md5 changes -> RERUN; restore.
If the hh chain loads from households/repo (outside the stage), do NOT edit those; instead show (d) by computing the hash
on a temp copy of the list with one file md5 altered, and write that this is a weaker test.
Never run EnergyPlus in this test. Never write under `campaign/results/` or `campaign/root/`.

## Rules (binding)
* UK licence: never open, list, copy or pass any UK path, file or argument (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`, `_uk`).
  `4thJ_step7_schedules.py` is code; you may read code, never any diary, episode, manifest or data file it points to.
* No folder-wide or repo-wide search, no recursive listing, no wildcard; name files in full.
* Speed via sbatch only, never python on the login node (tcsh); 1 CPU; 5J total now 13 of 32. Never wait for the job:
  submit, write the id, end the turn.
* Write only: local `tools/speed/a9_campaign_task.py` (keep a copy of the old one as `a9_campaign_task_pre9m.py`), the stage
  folder, your state file. The live Speed copy is swapped by the MANAGER after smoke check 2 (job 1408136) ends.

## Done means
Code edited locally with md5s of old and new file written; staged job submitted with id; `Next` gives the manager the exact
`scp` line for the swap and the log line to read. End with "job N submitted, state written to <path>".
