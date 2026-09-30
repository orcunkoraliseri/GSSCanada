# TASK (employee, Sonnet): 5J corpus guard: the trigger reads only the Spain+Italy copy

Written 2026-09-29 ~21:30 by the 5J manager. Why: FINDING 5J-1 (checklist Progress Log, 2026-09-29 ~16:05): the
5J trigger reads the pooled 4J corpus `4J_docs_occ/Step3_docs/outputs_step3/4J_step3_corpus.jsonl`, which holds
UK rows (UKDS EUL v16 clause 5 forbids AI tools touching UK data). The author made a Spain+Italy copy at
`C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl`
(manager checked: 57,400 lines, es 19,140, it 38,260, uk 0; equal to 4J Step 3's own counts;
md5 1a5163445291b54114832e192b0d9a05).
Create and fill the state file `Step2_docs/impl/2026-09-29_wp1_corpus_guard.md` (Task doc / Status / Ledger /
Verified / Decisions / Next / WHAT I DID NOT VERIFY). Write to it as you go, not at the end.

## Hard rules
* 🔴 **Never open, read, grep, hash, `head`, `wc` or run anything on the pooled file
  `4J_step3_corpus.jsonl` or any other file that holds UK rows.** Never run fold `uk`. `ls -l` on names is fine.
  The guard test in step 3 must refuse BEFORE anything opens the file; test it with an argument check only
  (see step 3), never by letting a run start on it.
* Local only; python `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`. A weather download
  (python PID 19328) is running: do not touch it.
* Edit only `5J_docs_occ/tools/5thJ_step9_trigger_act2.py`. Additive: mark each change `# 5J change (FINDING 5J-1)`.
  Never edit anything under `4J_docs_occ\` or `OpenUBEM\`. New outputs under
  `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\wp1_guard\` (new folder); never write over `wp1_act2\`.
* You never wait or poll. If you pass about 150k tokens, stop, write state, say "handoff needed".

## Steps
1. **Audit first (read code only, no runs).** List every file path the trigger can open, directly or through
   the 4J modules it imports (`_import_step7` loads `4J_docs_occ/tools/4thJ_step7_schedules.py`; follow any
   further imports and module-level file reads). Grep the trigger and those modules for `outputs_step3`,
   `corpus`, `pool`, `jsonl`, `open(`, `outputs_step`, `uk`. For each path write in the state file: what it is,
   whether it is per-fold (named with the fold, e.g. `generated_leg5_es_constrained.jsonl`) or could pool
   countries, and how you know (file:line). Anything that could pool UK rows and is read on a Spain/Italy run:
   **stop, write it as a finding, do not run anything**, and end the turn.
2. **Implement.** Add `--corpus` (default = the copy path above) and pass it to `build_dwellings` (new optional
   parameter; the hard-coded pooled path at trigger line ~685 goes away). Add a guard that runs before any file
   is opened: exit with a non-zero code and a one-line message if the corpus path's basename is
   `4J_step3_corpus.jsonl` or the path lies under `4J_docs_occ`/`Step3_docs`. Print one line
   `GUARD corpus OK path=<path> md5=<md5>` for the accepted copy (hashing the COPY is fine) and write the path +
   md5 into the manifest only as NEW keys (additive).
3. **See the guard fail** (argument check only): call the guard function directly from a tiny python one-liner
   with the pooled path as a STRING, show it raises/exits non-zero, without opening the file. Record the output.
   Then show a made-up path with the same basename in `%TEMP%` (an empty file you create and delete) is also refused.
4. **Regression on Spain.** Re-run the exact command that made `_5J_data/surrogate/wp1_act2/step9_major/`
   (find it in `Step2_docs/impl/2026-09-29_wp1_act2.md`, the log head `wp1_act2/log_step9_major.txt`, or the
   wrapper state; write the command you used), now with the default `--corpus`, output to `wp1_guard/step9_major/`.
   md5 every output file on both sides. Expected: `enduse_by_dwelling_es.csv`, `cycles_es.csv`,
   `stock_series_es.csv`, `step9_objects_es.idf` and every file in `enduse_profiles/` EQUAL; the manifest may
   differ only by the new keys (show the diff). Any other difference: stop, record it, do not fix it.
5. **Italy smoke.** One Italy run as in `wp1_act2/it_major` (same command, new corpus default), output
   `wp1_guard/it_major/`; compare md5 with `wp1_act2/it_major` the same way.
6. State file: Status DONE, new trigger md5, the audit list, the md5 table as lines, Next = "manager verifies;
   then design tables".

## What the manager will re-derive
The trigger md5; the guard refusal (re-run your one-liner); one md5 from step 4 on both sides.
