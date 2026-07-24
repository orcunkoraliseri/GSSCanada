# EMPLOYEE PROMPT — Leg-3 · Step-4 · Stage 2b: full 04E re-run (G3 per-slot fix) + rake re-cascade (cluster, sbatch-only)

**You are the employee. Execute the task below and append a Progress Log entry on completion.** Cluster work on Speed (`o_iseri@speed.encs.concordia.ca`). **🔴 ABSOLUTE RULES (account-suspension risk):** on the login node use ONLY `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, and single-file `cat`/`head`/`tail`/`grep`/`wc -l`. **NEVER run bare `python`/`python3` or a blocking `srun`/`tee` on the login node — ever.** Any Python runs via `sbatch` only. **Every `sbatch` MUST request `-t 7-00:00:00`** (7-day walltime floor) regardless of expected runtime. All cluster commands single-line (no line breaks). **The remote login shell is tcsh** — do NOT use `2>/dev/null` / `2>&1` / bash-isms in login-node commands (they error "Ambiguous output redirect" / "Unknown arguments"); the `#!/encs/bin/bash` sbatch scripts themselves are bash and may use bash syntax internally. Decision-level questions → STOP and flag the manager.

---

## Why you exist (context)

We patched `3rdJ_04E_inference_4split.py` locally (G3 co-presence binarization → per-(day-type×slot) with min-support fallback, constants 200/20/50; predecessor archived; local smoke + forced-per-slot branch both verified; only-cop-changed invariant held via `np.array_equal`). **Determinism probe (Stage 2a, job 1128526, COMPLETED exit 0) confirmed on the REAL `seed_3` checkpoint:** re-running the *unpatched* 04E twice gives act30/hom30/wrk30/ret30 **byte-identical run-to-run** (all EQUAL, `DETERMINISM_RESULT.txt`). So the premise holds: re-running 04E on `seed_3`'s checkpoint reproduces act/hom/wrk/ret exactly; **only the 9 co-presence channels change** (from our patch). Now apply the fix to the production pool by re-running the real 04E→04L→04M→04T chain into **new, non-clobbering `_g3fix` dirs**, verifying the only-cop-changed invariant on the FULL pool as a hard go/no-go before the rakes.

Base dir on cluster: `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/` (call it `SDIR`). Env pattern (from every wrapper): `. /encs/pkg/modules-5.3.1/root/init/bash` then `PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python` (no conda). Logs go to `/speed-scratch/o_iseri/logs/`.

**Production chain of record (do NOT overwrite any of these dirs — they are the pre-fix baseline for audit/diff):**
- 04E: `--data_dir outputs_step4 --checkpoint outputs_step4/seed_3/checkpoints/best_model.pt --output outputs_step4/seed_3/augmented_diaries.csv` (all other args = argparse defaults: temp 0.7, top_p 0.9, home 0.5, work 0.4, retail 0.15, min_dwell 2).
- 04L: `3rdJ_s4_4split_rake.sh` → `--data_dir outputs_step4 --r5_dir outputs_step4/seed_3 --output_dir outputs_step4/sweep/seed_3_raked3 --checkpoint outputs_step4/seed_3/checkpoints/best_model.pt`.
- 04M: `--in_csv outputs_step4/sweep/seed_3_raked3/augmented_diaries.csv --out_csv outputs_step4/sweep/seed_3_raked3_mindwell/augmented_diaries.csv --min_dwell 2`.
- 04T: `--in_csv outputs_step4/sweep/seed_3_raked3_mindwell/augmented_diaries.csv --out_dir outputs_step4/sweep/seed_3_raked3_mindwell_actv --seed 3`.

**Your `_g3fix` targets (all NEW):** `outputs_step4/seed_3_g3fix/augmented_diaries.csv` → `sweep/seed_3_g3fix_raked3/` → `sweep/seed_3_g3fix_raked3_mindwell/` → `sweep/seed_3_g3fix_raked3_mindwell_actv/`.

---

## Tasks (in order)

**T0 — Prep & verify the rake input mechanism (read-only first).** Before touching anything, `cat`/`grep` on the cluster to CONFIRM exactly how each rake stage reads its input pool, so your `_g3fix` wiring is correct (do NOT assume):
- `3rdJ_04L_joint_rake_4split.py`: confirm which arg/dir it reads the *input synthetic pool* from — is it `${r5_dir}/augmented_diaries.csv`, or a separate `--input`? Whatever it is, that is the field you must repoint at the g3fix pool. Also confirm `--checkpoint` is a separate arg (the model is only used for `model.generate()`; the checkpoint itself is unchanged by our fix, so it stays `outputs_step4/seed_3/checkpoints/best_model.pt`).
- Confirm 04M reads `--in_csv` and 04T reads `--in_csv` (per the production logs above).
- Report the confirmed input-arg for each of 04L/04M/04T in the Progress Log.

**T1 — Archive the cluster 04E predecessor, then scp the patched 04E up.**
- `cd $SDIR`, copy the current cluster `3rdJ_04E_inference_4split.py` to `archive/3rdJ_04E_inference_4split.py.20260721_cluster_preG3perslot` (`mkdir -p archive` first if needed). Confirm size via `ls -la`.
- From the Windows side, `scp` the LOCAL patched `3rdJ_04E_inference_4split.py` (the one at `.../Leg3_4-split/Step4_docs/3rdJ_04E_inference_4split.py`, constants 200/20/50) to `SDIR/3rdJ_04E_inference_4split.py`. After scp, `ls -la` on the cluster to confirm the new mtime/size, and `grep -n "G3_MIN_OBS_CELL\|G3_MIN_POS_CELL\|G3_MIN_SYN_CELL" 3rdJ_04E_inference_4split.py` on the cluster to confirm the three constants read **200 / 20 / 50** (proof the correct patched file landed, not the 5/1/2 branch-exercise version).

**T2 — Full 04E re-run on the seed_3 checkpoint + FULL-POOL determinism guard (ONE sbatch job).** Write a wrapper `3rdJ_s4_4split_04E_g3fix.sh` (`#!/encs/bin/bash`, SBATCH `-p pg --gres=gpu:1 --mem=32G -t 7-00:00:00`, output/error to `/speed-scratch/o_iseri/logs/3J_s4_04E_g3fix_%j.{out,err}`) that, in ONE job:
  1. `mkdir -p outputs_step4/seed_3_g3fix`.
  2. Runs the patched 04E: `$PYTHON 3rdJ_04E_inference_4split.py --data_dir outputs_step4 --checkpoint outputs_step4/seed_3/checkpoints/best_model.pt --output outputs_step4/seed_3_g3fix/augmented_diaries.csv` (NO other args — defaults match production).
  3. **Determinism guard (in the SAME job, a small inline `$PYTHON - <<'PY' ... PY` heredoc):** load `outputs_step4/seed_3/augmented_diaries.csv` (pre-fix baseline) and the new `outputs_step4/seed_3_g3fix/augmented_diaries.csv`, and for each channel group `act30_*/hom30_*/wrk30_*/ret30_*` assert `np.array_equal` (NaN-safe: compare with NaNs filled to a sentinel, or use `.fillna(-999)` on both consistently) → must be **EQUAL**. Also confirm row-count identical, and that at least SOME `colleagues30_*`/co-presence cells DIFFER (proving the fix actually changed cop). Write a tiny `outputs_step4/seed_3_g3fix/G3FIX_POOL_GUARD.txt` with per-group EQUAL/DIFF, row counts, and the cop-diff cell count. Use `usecols` to avoid loading all 644 cols twice if memory is tight; the two files are ~419 MB each.
  - Submit with `sbatch`, then `squeue -u o_iseri` once to confirm queued/running. **Do NOT tight-poll** — the harness will notify you when the job reaches a terminal state; if you must check manually, ≥30 min between checks.

**T3 — GO/NO-GO gate (hard).** When T2's job completes, `cat outputs_step4/seed_3_g3fix/G3FIX_POOL_GUARD.txt`:
  - **If act/hom/wrk/ret are ALL EQUAL and cop DIFFERS** → determinism held on the full pool; **proceed to T4**.
  - **If ANY of act/hom/wrk/ret shows DIFF** → the only-cop-changed premise BROKE at full scale (unexpected given Stage 2a). **STOP immediately, do NOT run any rake**, and flag the manager with the guard output — the manager switches to a copy-passthrough design (copy act/hom/wrk/ret from `seed_3`, splice in only the regenerated cop columns).

**T4 — Re-cascade the rakes into `_g3fix` dirs (only if T3 = GO).** Reproduce the production chain, each stage repointed at the g3fix pool, into NEW dirs (never overwrite `seed_3_raked3*`). Cleanest approach: copy each production wrapper to a `_g3fix` variant and swap only the dir vars (keep `--checkpoint outputs_step4/seed_3/checkpoints/best_model.pt` — the model is unchanged). Run them **in order, each as its own `sbatch -t 7-00:00:00`, waiting for each to COMPLETE before the next** (04M depends on 04L's output, 04T on 04M's):
  1. **04L** → copy `3rdJ_s4_4split_rake.sh` to `3rdJ_s4_4split_rake_g3fix.sh`; set the input pool dir/arg (per T0's confirmed mechanism) to the g3fix pool (`outputs_step4/seed_3_g3fix`), `--output_dir outputs_step4/sweep/seed_3_g3fix_raked3`, keep `--checkpoint outputs_step4/seed_3/checkpoints/best_model.pt`. If 04L's precheck `chk` requires `${R5DIR}/checkpoints/best_model.pt` and you point `--r5_dir` at `seed_3_g3fix` (which has no `checkpoints/`), either (a) keep `--r5_dir outputs_step4/seed_3` and add whatever separate arg feeds the *pool* from g3fix (if 04L supports it), or (b) `mkdir -p outputs_step4/seed_3_g3fix/checkpoints && cp outputs_step4/seed_3/checkpoints/best_model.pt outputs_step4/seed_3_g3fix/checkpoints/` so the g3fix dir is self-consistent — pick whichever matches 04L's actual input mechanism from T0 and note which you used and why.
  2. **04M** → `--in_csv outputs_step4/sweep/seed_3_g3fix_raked3/augmented_diaries.csv --out_csv outputs_step4/sweep/seed_3_g3fix_raked3_mindwell/augmented_diaries.csv --min_dwell 2` (own sbatch wrapper, or add to a g3fix cascade wrapper).
  3. **04T** → `--in_csv outputs_step4/sweep/seed_3_g3fix_raked3_mindwell/augmented_diaries.csv --out_dir outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv --seed 3`.
  - After each stage, `ls -la` the output dir + `wc -l` the output CSV to confirm **192,183 data rows** (same as production) and a non-truncated write. Capture each stage's job id + exit code from `sacct`.

**T5 — Validate the fixed pool (Step-4 validator) — this is the W3 efficacy check.** Point `3rdJ_s4_4split_valonly.sh` (copy → `_g3fix` variant) at `outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/`, `sbatch -t 7-00:00:00`. When done, `cat`/`grep` the validator report for the **W3 gate** result specifically (colleague co-presence, gate ≤3.0pp) plus the overall PASS/WARN/FAIL tally. Report W3's before (7.19pp) → after value. Do NOT relax any gate; just report the numbers. (If W3 still >3pp, STOP and flag — the fix underperformed and the manager re-adjudicates; do NOT proceed to scp/Step-5.)

**T6 — scp the fixed pool + report down to Windows.** Once T5 shows W3 passing (≤3pp) and no NEW FAIL vs the pre-fix baseline, `scp` the final `outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/augmented_diaries.csv` + its `step4_validation_report.{html,txt}` down to the LOCAL `.../Step4_docs/outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/` (create the local dir; do NOT overwrite the local `seed_3_raked3_mindwell_actv/` baseline). Confirm local sizes match cluster via `ls -la` both sides.

---

## Deliverable / report back

Append a Progress Log entry to `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` headed `### 2026-07-21 — Stage 2b: full 04E G3-fix re-run + rake re-cascade + validation (cluster)`, containing, in order: the Stage-2a determinism verdict transcribed from `DETERMINISM_RESULT.txt` (act/hom/wrk/ret all EQUAL), T0 (confirmed input-args), T1 (archive path + scp + constants-confirmed 200/20/50), T2/T3 (04E job id + FULL-POOL guard result: per-group EQUAL/DIFF + cop-diff count + GO/NO-GO), T4 (04L/04M/04T job ids + exit codes + row counts per stage), T5 (**W3 before→after + full PASS/WARN/FAIL tally, verified from the report's own text**), T6 (scp confirmation + local/cluster size match).

Then report back to the manager with an 8–10 line summary ending in: **"Fixed pool delivered at sweep/seed_3_g3fix_raked3_mindwell_actv/ (local+cluster); W3 = ___pp (was 7.19pp) → PASS/FAIL; overall Step-4 tally = __P/__W/__F; determinism guard = HELD/BROKE. Ready for Stage 3 (Step-5 re-run) / BLOCKED because ___."** Do NOT run Step-5, do NOT auto-advance — the manager authorizes Stage 3.

## Disciplines (enforce)
1. **Login-node-safe commands only**; **all Python via `sbatch`**, never bare python / blocking srun on the login node. **tcsh login shell** — no `2>/dev/null`/`2>&1` in login-node commands.
2. **Every `sbatch` `-t 7-00:00:00`**; single-line commands.
3. **Never overwrite** `seed_3/`, `seed_3_raked3*`, or any existing production/`sweep` dir — all new work lands in `_g3fix` dirs. Archive the cluster 04E predecessor before scp'ing the patch.
4. **FULL-POOL determinism guard is a hard gate** (`np.array_equal` on act/hom/wrk/ret) — if it BROKE, STOP before any rake and flag.
5. **Verify every load-bearing number from the artifact** (the guard txt, the validator report's own text, `wc -l` row counts), not from job logs or assumptions.
6. **Never relax a gate to clear a FAIL.** If W3 still >3pp, STOP and flag — do not scp/advance.
7. Don't tight-poll — rely on the completion notification, or ≥30 min between manual checks.
8. Decision-level questions → STOP and flag the manager.
