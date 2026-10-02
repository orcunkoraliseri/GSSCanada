# 5J 9l campaign runner Madrid - implementation state
Task doc:   Step9_docs/impl/2026-10-01_wp9l_campaign_madrid_TASK.md
Status:     SUBMITTED 19:09 EDT (smoke 1408110, check 1408112, re-submission 1408134, check 2 1408136); no smoke result read yet
## Ledger (append-only)
* 1408070 prep (first layout, code/) COMPLETED ALL PASS 19:06 (B0 es n_members 1.9333, peak 642.04 W, 2,339.0 kWh/y; light ctx = full ctx; skip rule synthetic seen failing 4/4); its b0 files were deleted with the folder rebuild below.
* 1408075 smoke array (first layout) CANCELLED 19:07: every task failed in the writer, `No module named 4thJ_step8_idf` (the writer imports 4J_docs_occ/tools relative to its own root). Dependents 1408088 (check), 1408089 (resubmission), 1408099 (check 2) CANCELLED with it. Fix: code moved to campaign/root/5J_docs_occ/tools + campaign/root/4J_docs_occ/tools/4thJ_step8_idf.py + 5thJ_idf.py; results/runs/b0 folders removed and re-made.
* 1408109 prep (root layout) SUBMITTED 19:07:50, 2 CPUs, log campaign/logs/prep_1408109.out
* 1408110 smoke array 1-36%10 (afterok:1408109), MANIFEST smoke csv, logs campaign/logs/t_1408110_<n>.out
* 1408109 prep COMPLETED exit 0, PREP_SUMMARY ALL PASS (19:08:50; same B0 gates as before, skip rule synthetic seen failing 4/4)
* 1408110 smoke array: tasks 1-10 RUNNING at 19:08:54 (writer + schedcheck PASS for task 1, EnergyPlus running); result not read
* 1408112 check (afterany:1408110), log campaign/logs/check_1408112.out
* 1408134 smoke RE-SUBMISSION, same array 1-36%10 (afterany:1408112); expected: every task prints `DECIDE ... SKIP`
* 1408136 check 2 with SKIPTEST=1 (afterany:1408134), log campaign/logs/check_1408136.out
* 5J CPUs at submit 19:09: 9k array 16 + smoke 10 = 26 (<= 32). Never more than 10 smoke tasks at once.
## Files
* Local code (tools/speed/): `a9_campaign_plan.py` (plan, runs LOCALLY with `py`), `a9_campaign_task.py` (sub-commands run / prep / check), `a9_campaign_task.sh` (array), `a9_campaign_prep.sbatch`, `a9_campaign_check.sbatch`.
* Additive edit `tools/5thJ_modelA_idf.py`: env `MODELA_FLEET_ROOT` (Speed base copy `<root>/EU11_<D>_<vintage>/idfs/<stem>.idf`); default behaviour unchanged. New md5 f7cd62b833752c85cb231599589d0694 (was 24ee239a... after nothing; before this task: 24ee239a194eb870c2dac2dc523b876e).
* households.py NOT edited (md5 bee14cda3ccc47f17fddbc3087613008); new logic lives in a9_campaign_task.py.
* Speed folder (new): /speed-scratch/o_iseri/5J/modelA/campaign/{code,inputs,manifests,logs,results,runs,schedules,b0}
* Plans (local scratchpad -> scp): plan_ES-MAD-BERRUGUETE.csv (9,201 rows, md5 f627f60d92243dc5019014cd30696a8b), smoke_ES-MAD-BERRUGUETE.csv (36 rows, md5 90d9ebb8ed7ea059dbd8f21ed6ab1b2c).
## Verified
* Plan checks (local, `py a9_campaign_plan.py ES-MAD-BERRUGUETE`): rows 9,201 PASS; buildings dev 795 / val 172 / test 169 PASS; no held-out stem; 1,136 stems once; run_id unique; 9/6/6 runs per building. Seen failing: planted held-out stem 1ccf53aa96c58223 left in the list -> rows 9,207 FAIL, val 173 FAIL, held-out left 6 FAIL; CONTROL FIRED (`--selftest`).
* Local md5 of base IDF 1271cddbf6bd1e8a equals the Speed fleet copy (d1d33a9c4d417d93f942308895d182b8).
* Smoke stems: 05e17b2bf818153b (2 flats, small dev), 394922138a6b5928 (77 flats, largest dev), 0b6eaecde1077a30 (6 flats, val), 4a1eb42e7c488fc0 (6 flats, test), 1271cddbf6bd1e8a (triangle, in plan, 18 flats) = 36 rows.
## Decisions
* B0 = 60 DEV households drawn by survey weight (key log(1-u)/w, seed 9106, new constant), unweighted mean with the pilot's `<cc>_avg` rule (hh_build.average_series), written at %.12f, one pair of series reused in every flat; built once by the prep job into campaign/b0/es/. Bologna B0 is built when Bologna is run.
* Placement recomputed from the plan (assign_flats with exclude of siblings r' < r of the same building and pool); light context (weights + sealed split lists) instead of the full pools for the skip decision.
* Skip key = src_idf_md5, writer_md5 (md5 of md5(idf.py)+md5(idf_mz.py)), hh_md5 (households.py + design_tables.py), placement_md5 (zone,hid lines; b0 adds the b0 file md5s); skipped only for status CLEAN or NOT_CLEAN.
* Extraction keeps the 4 core targets only (heating, cooling, equipment, total_elec; float32) + zones, not the 20 extra variables (disk). Big EnergyPlus files (csv, eso, sql, htm, audit, shd...) deleted after extraction; kept: err, end, eplustbl.csv, writer/eplus stdout, placement, draws.gz, series.tar.gz, IDF gz, summary.json.
* NOT_CLEAN (G-c5) runs are results (exit 0), reported by name by the check job; only TASK_ERROR gives exit 1.
* Memory 12 G per task (unmeasured; read MaxRSS of the smoke with sacct).
## Next
Cold agent / manager, in this order (login node = tcsh: no $(), no for; `ssh o_iseri@speed.encs.concordia.ca "<cmd>"`):
1. `sacct -j 1408110 -X -o JobID,State,ExitCode,Elapsed,MaxRSS` (smoke), then `cat /speed-scratch/o_iseri/5J/modelA/campaign/logs/check_1408112.out` (single file). Lines: `ROWS`, `NOT_CLEAN`, `EXTRACT_FAILED`, `TASK_ERROR`, `PURITY_VIOLATIONS`, `GC3_FAILURES`, `SRC_MD5_MISMATCH`, `CPU_SECONDS`, `CONTROL planted_faults`, `CHECK_SUMMARY`. Expected: the 6 runs of triangle building 1271cddbf6bd1e8a NOT_CLEAN by name (the stem has 9 runs if dev, 6 otherwise: all of them), every other row CLEAN.
2. Single task log: `tail -40 campaign/logs/t_1408110_<n>.out`; result `results/<run_id>.json`; run folder `runs/<run_id>/` (writer_stdout.txt, eplusout.err, summary.json).
3. Resubmission 1408089-style (same array, expected: every task prints `DECIDE ... SKIP`) and check 2 (`--skiptest`): see Ledger for ids; log `logs/check_<id>.out` lines `SKIPTEST ...` and `CONTROL skip_rule_on_real_copy`.
4. FULL MADRID (only after the manager reads the smoke and seals the rules), from the login node:
   `cd /speed-scratch/o_iseri/5J/modelA/campaign/root/5J_docs_occ/tools; sbatch --array=1-9201%32 --export=ALL,MANIFEST=/speed-scratch/o_iseri/5J/modelA/campaign/manifests/plan_ES-MAD-BERRUGUETE.csv a9_campaign_task.sh`
   (dependency-free form; MaxArraySize 10001 so one array; %32 only if the 5J total stays <= 32 CPUs: check `squeue -u o_iseri` first). Then the check: `sbatch --dependency=afterany:<arrayid> --export=ALL,MANIFEST=/speed-scratch/o_iseri/5J/modelA/campaign/manifests/plan_ES-MAD-BERRUGUETE.csv a9_campaign_check.sbatch`. Re-running the same command later skips every finished run (rule R1 d).
5. Bologna: `py tools/speed/a9_campaign_plan.py IT-BOL-GALVANI2` waits for the 10-04 lists (rules R1); prep must then also build b0 for `it` (the prep loop skips `it` on purpose).
## WHAT I DID NOT VERIFY
* Everything EnergyPlus-related of the smoke batch: whether the run folder works as EnergyPlus cwd for the relative schedule paths (default-mode runs need ../../schedules/<stem>/), extraction on real output, G-c3 per flat, bytes kept, wall times, MaxRSS (12 G is a guess).
* That the triangle building's runs come out NOT_CLEAN by name (expected from 9i/9k; not yet seen in this runner).
* Skip rule on a real copy (check 2) and the re-submission skipping (not yet run); the synthetic skip test passed in the prep job.
* Planted-fault control of the check job (CONTROL planted_faults line) is in check 1 and 2; not yet read.
* Bologna: untouched. B0 for `it` is not built (prep loop skips it).
* Check job and task tested only on Speed; nothing run locally except the plan (py) and syntax.
* The campaign writes `results/` and `runs/` into one folder each (9,201 x 2 files in results, 9,201 run folders): inode count not discussed with the cluster admins.
## Honest list of slips
* One `ls -d <folder>/*` (wildcard) on my own households code folder at the start; one `squeue ... | sort | uniq -c` and `| grep` on the login node (text filters on squeue output, no job data). Nothing UK opened, listed, copied or passed; no EU-11/ listing; the two district fleet folders were opened only by full file names (one IDF md5 + grep, one `ls | head -3` of the fleet schedules folder).
* First smoke array (1408075) failed on a missing import (module path of the writer); cancelled, fixed, resubmitted as 1408110. Old results/runs folders of that attempt were removed with `rm -rf` of my own campaign folders.
## Manager read of the employee return (2026-10-01 19:10 EDT, from `date`)
* Jobs re-measured with sacct/squeue at 19:09: prep 1408109 COMPLETED 0:0; smoke 1408110 tasks 1-10 RUNNING, 11-36 pending on the %10 limit; checks 1408112/1408136 and re-submission 1408134 pending on dependency. 5J CPUs 26 (9k 16 + smoke 10) <= 32.
* B0 rule ACCEPTED: 60 dev households by survey weight, unweighted mean = the pilot's rule (pilot es_avg / it_avg were the mean of 60, `Step2_docs/impl/2026-09-30_wp1_it_households.md` line 37), here drawn from DEV only (R2). Seed 9106 is new; recorded.
* Extraction of the 4 core targets + zone map only: ACCEPTED (R5 targets; R4 forbids any EnergyPlus output as input).
* To fix before the full Madrid array: the writer md5 in the skip key covers idf.py + idf_mz.py but not the modules it imports (`4thJ_step8_idf.py`, `5thJ_idf.py` copies in campaign/root). They are frozen copies; add their md5 to writer_md5 after the smoke + re-submission checks end and before the full array (the 36 smoke runs then re-run once; changing it mid-smoke would mix two keys).
* Open until the smoke is read: default-mode schedule paths, triangle NOT_CLEAN by name, MaxRSS, check controls, skip on a real copy.

## Manager read of the smoke batch (2026-10-01 20:18 EDT)
* sacct: smoke array 1408110 36/36 COMPLETED 0:0 (2-flat building about 3.5 min, 77-flat about 22 min, peak MaxRSS 7.3 GB on the 77-flat runs; largest Madrid building in the plan 79 flats -> `--mem=12G` kept); check 1408112, re-submission 1408134 (36/36), check 2 1408136 all COMPLETED 0:0.
* `check_1408112.out`: ROWS 36 done 36 clean 21; NOT_CLEAN 15 = the 6 runs of triangle 1271cddbf6bd1e8a (12 degenerate surfaces, expected) AND the 9 runs of the 77-flat dev building 394922138a6b5928 (EnergyPlus: 22 degenerate surfaces; it is in `wp9k/degenerate_win3.csv`, so known, not new); EXTRACT_FAILED 0, TASK_ERROR 0, PURITY 0, GC3 0, SRC_MD5_MISMATCH 0; 8.15 CPU-h, 0.043 GB kept.
* **CONTROL planted_faults printed DID_NOT_FIRE with every count right** (not_clean 1, purity 1, gc3 1, src 1, extract 1, missing 1, clean 4): the control's expectation `clean == 2` was wrong (f0, f2, f3, f4 keep status CLEAN; purity, G-c3 and src faults do not change the EnergyPlus status). Fixed to `clean == 4` (manager, 20:17, comment in code); check 1409234 on the swapped code prints FIRED.
* Re-submission: 36/36 task logs `DECIDE ... SKIP all four md5 equal`; check 2: same ROWS, `CONTROL skip_rule_on_real_copy FIRED` (each of the 4 md5s changed on a real copy -> RERUN).
* **Verdict: runner ACCEPTED** with the 9m key (staged test ALL PASS) and the control fix. Live script swapped 20:17 (old copy `a9_campaign_task_pre9m.py`, md5 8bcf9f15...; new 4bef1d8211785f7e79153e4526597d00). The 36 smoke results carry the old key, so they re-run inside the full array.
