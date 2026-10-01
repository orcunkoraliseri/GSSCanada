# TASK (employee, Sonnet): 5J Step 5 part D: shortlist, scoring, winner, pinning (rules R7)

Written 2026-09-30 by the 5J manager (stamp = file time; `date` before every stamp you write). Launch only after the S grid
(part C) has finished and the manager has verified its smoke job. Read first, in full: `Step5_docs/outputs_step5/step5_rules.md`
(THE RULES incl. AMENDMENT 1; esp. R7, R11; never change them), `Step5_docs/impl/2026-09-30_wp3_store_TASK.md` (hard rules, they
bind you unchanged), the part B and part C state files `Step5_docs/impl/2026-09-30_wp3_b1.md`, `Step5_docs/impl/2026-09-30_wp3_s.md`,
`Step5_docs/outputs_step5/models.md`, `tools/speed/s5_train.py`, `tools/speed/s5_predict.py`, and `tools/speed/5thJ_04_scorer.py`
(how it writes its SUMMARY, G5J.2 and G5J.3 lines and its output file names; never change it, always run the FROZEN copy in
`/speed-scratch/o_iseri/5J/freeze/`). State file: create `Step5_docs/impl/2026-09-30_wp3_winner.md` (Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules (short; the full list is in the part A task)
Speed sbatch only, nothing on the local CPU. Only development / validation / b0_dev / b0_val lists; never test, unused or loco.
Spain + Italy only, no UK file, no folder-wide search or wildcard. Write only under `/speed-scratch/o_iseri/5J/train/`. GPU jobs:
`-p ps --gres=gpu:nvidia_a100_2g.20gb:1 -c 3 --mem=48G -t 7-00:00:00 --exclude=antenna1`; all 5J jobs together at most 30 CPUs
(check `squeue -u o_iseri` for other 5J jobs first; the `openubem_t07` array is another project, not counted, never touched).
Never wait: submit a dependency chain, write JobIDs, end. At most 6 sacct checks of 30 s per job. Past ~150k tokens: handoff.

## Parts (submit as ONE dependency chain, then end your turn)
A. `tools/speed/s5_shortlist.py` (CPU job, 1 CPU): read `train/ckpt/S/<i>/train_log.tsv` for i = 0..15; per config the best epoch
   validation sum (level + pair) and whether it finished, hit patience or hit the 4 GPU-hour cap; FAIL if any config has no log.
   Shortlist = the 3 lowest per family (TCN, Transformer) = 6, written to `train/winner/shortlist.json` and printed as a table.
B. Prediction array 0-5 (GPU, `%6`, afterok A): `s5_predict.py --ckpt train/ckpt/S/<cfg> --split validation --out
   train/pred/S<cfg>` for the 6 shortlisted configs (the task reads its config index from `shortlist.json`). Print rows written.
C. Scorer array 0-5 (6 CPUs each, at most 4 at once so CPUs stay <= 30 with nothing else running; afterok B): FROZEN scorer
   `--pred train/pred/S<cfg> --split validation --out train/score --tag S<cfg> --b1 train/pred/B1 --control train/pred/B0`.
D. `tools/speed/s5_winner.py` (CPU, afterok C): parse the 6 score files; per config: G5J.3 PASS cells (of 32), median G5J.3 R²
   over the 16 heating + cooling cells, G5J.2 PASS cells, validation loss. Apply R7.3 in that order; print every step of the
   tie-break and the winner; write `train/winner/winner.json` (config index, family, config, ckpt path, ckpt md5, md5 of every
   s5_*.py, seed, validation loss, the four numbers). Also print B1's G5J.3/G5J.2 line counts from `train/score` (tag B1) and say
   whether the winner's G5J.3 skill interval excludes 0 against B1 (R7.5; report either way, never tune).
   Seen failing (in the same job): feed the parser a copy of the score table with one PASS turned into FAIL and show the counts move.
E. Reload check (GPU, afterok D): load the winner's `best.pt` in a fresh process, recompute the validation loss on the fixed 20,000
   draws and print both values; PASS if equal to 4 decimals (R7.4, val 4.3). Copy the checkpoint to `train/winner/pinned/` with its
   md5 file, chmod 444.
F. Cleanup (CPU, afterok E): delete `train/pred/S<cfg>/` of the 5 non-winners ONLY (R7.6); score files stay. Print what was deleted.
G. Write the JobIDs and the chain into the state file, a "Winner" section into `Step5_docs/outputs_step5/models.md` ("running,
   manager reads" until done), and end.

## Report back (short, plain)
JobIDs of the chain; status; Next = "manager verifies winner; part E (control, seeds, one-country)".

## What the manager will re-derive
With own code: the shortlist from the 16 logs; the winner from the 6 score files by R7.3; one G5J.3 cell of the winner from its
prediction files and the truth; the reload loss.

## Manager note before launch (2026-09-30 23:21 EDT)
* Rules now include AMENDMENT 2 (static clip; `step5_rules.md` md5 65e54b5c3c69351fb7dd10fa4ac26345). The valid grid is array
  1404631 (all 16 GRID_EXIT 0, finished 23:19); `ckpt/S_void_1404570` is VOID: never read it, never shortlist from it.
* B1 (1404525) is still predicting validation runs (313/1980 at 23:16) and its scorer 1404526 waits on it. So: part A and the
  prediction array B run now; the scorer array C is `--dependency=afterok:<B>:1404526` (needs `train/pred/B1` complete and keeps
  CPUs <= 30); scorers `%4` once B1 has ended. If 1404525 or 1404526 fails, C never starts: write that in the state file and end.
* `s5_predict.py` loads `static_stats` from the checkpoint (with zmin/zmax): print the `STATIC_CLIP` line of each prediction task
  into the ledger (expect es_B40 clipped, 693 rows).
