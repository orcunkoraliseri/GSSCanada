# EMPLOYEE PROMPT — Leg-3 · Step-4 · Stage 2a: 04E command discovery + DETERMINISM PROBE (cluster, sbatch-only)

**You are the employee. Execute the task below and append a Progress Log entry on completion.** Cluster work on Speed (`o_iseri@speed.encs.concordia.ca`). **🔴 ABSOLUTE RULES (account-suspension risk):** on the login node use ONLY `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, and single-file `cat`/`head`/`tail`/`grep`/`wc -l`. **NEVER run bare `python`/`python3` or a blocking `srun`/`tee` on the login node — ever.** Any Python runs via `sbatch` only. **Every `sbatch` MUST request `-t 7-00:00:00`** (7-day walltime floor) regardless of expected runtime. All cluster commands single-line (no line breaks). This stage does **NOT** modify any script, does **NOT** scp anything, does **NOT** run the full production inference — it is discovery + a cheap determinism probe. Decision-level questions → stop and flag the manager.

---

## Why you exist (context)

We patched `3rdJ_04E_inference_4split.py` locally (G3 co-presence binarization → per-(day-type×slot) with min-support fallback; predecessor archived; per-slot branch verified; constants at 200/20/50). To apply it we must **re-run 04E on the cluster** against the checkpoint that produced the Step-5 pool of record — `outputs_step4/seed_3/checkpoints/best_model.pt` — landing in a new non-clobbering dir. The whole "only the 9 co-presence channels change, act/hom/wrk/ret stay byte-identical to `seed_3`" premise depends on **04E inference being deterministic on this cluster** (sole RNG = `torch.multinomial`, downstream of `torch.manual_seed(42)`; no shuffle). On GPU that is *probably* true but not guaranteed. **Before spending a full ~400 MB inference, prove determinism cheaply.** If it fails, the manager switches to a copy-passthrough design — so STOP after the probe and report; do not proceed to the full run or the rakes.

Base dir on cluster: `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/`. The env pattern (from the existing wrappers): `. /encs/pkg/modules-5.3.1/root/init/bash` then the hardcoded venv interpreter `/speed-scratch/o_iseri/envs/step4/bin/python` (no conda). Reuse exactly that.

---

## Tasks (in order)

**T1 — Discover the exact 04E inference command that produced `outputs_step4/seed_3/augmented_diaries.csv`.**
- `ls -la outputs_step4/seed_3/` and locate the base (pre-rake) `augmented_diaries.csv` + any run log / sbatch `.out` / wrapper that invoked `3rdJ_04E_inference_4split.py` for seed_3. Check the sbatch wrappers (`3rdJ_s4_4split_*.sh`) and `/speed-scratch/o_iseri/logs/` for the 04E inference call (the one BEFORE rake jobs 1128036/1128047/1128070).
- Extract the **exact CLI args** used (`--data_dir`, `--checkpoint`, `--temperature`, `--top_p`, `--home_threshold`, `--work_threshold`, `--retail_threshold`, `--retail_pos_weight`, `--min_dwell`, `--output`). Record them verbatim. If no explicit invocation is found, record that and note the argparse defaults (temp 0.7, top_p 0.9, home 0.5, work 0.4, retail 0.15, min_dwell 2) as the presumed command — the determinism guard in Stage 2b will confirm.
- Confirm `outputs_step4/seed_3/checkpoints/best_model.pt` is present (`ls -la`, size).

**T2 — Determinism probe (cheap; the CURRENT cluster 04E script — do NOT scp the patch yet).**
Determinism of act/hom/wrk/ret is independent of our co-presence patch (the patch only touches cop columns), so probe with the **cluster's existing (unpatched) 04E**. Submit ONE `sbatch` job (`-t 7-00:00:00`) that, using the venv python, runs 04E inference **twice at small scale on the REAL seed_3 checkpoint** to two scratch outputs, e.g.:
- Run A: `... 3rdJ_04E_inference_4split.py --data_dir outputs_step4 --checkpoint outputs_step4/seed_3/checkpoints/best_model.pt --smoke --smoke_n 300 --output outputs_step4/g3fix_determinism_probe/runA.csv` (plus whatever seed_3 args T1 found).
- Run B: identical, `--output .../runB.csv`.
- Then compare **act30_*/hom30_*/wrk30_*/ret30_*** between runA and runB with `np.array_equal` per channel, and write a tiny `outputs_step4/g3fix_determinism_probe/DETERMINISM_RESULT.txt` containing, per channel, `EQUAL`/`DIFF` + (for DIFF) the count of differing cells; also line-count/row-shape of each. Keep the two CSVs (small, smoke-scale). **Everything (both runs + the compare) inside the ONE sbatch job** — no bare python on the login node.
  - IMPORTANT: confirm `--smoke` does NOT silently swap in a different (smoke) checkpoint — the probe MUST use the real `seed_3/checkpoints/best_model.pt`. If `--smoke` forces the smoke checkpoint, instead run a non-smoke inference on a small subset by whatever arg the script supports; if none exists, report that and STOP for manager guidance rather than probing the wrong checkpoint.
- After submitting, `squeue -u o_iseri` once to confirm it's queued/running. Do NOT poll in a tight loop — if it hasn't finished when you next check, wait ≥30 min between checks (or report the job id and let the manager pick up the result).

**T3 — Report the probe verdict.** Once the job completes, `cat outputs_step4/g3fix_determinism_probe/DETERMINISM_RESULT.txt` and report: are act/hom/wrk/ret **byte-identical run-to-run** (all EQUAL)? This is the go/no-go for Stage 2b's "only-cop-changes" premise.

---

## Deliverable / report back

Append a Progress Log entry to `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` headed `### 2026-07-21 — Stage 2a: 04E command discovery + determinism probe (cluster)`, containing: T1 (the exact seed_3 04E CLI args + checkpoint presence/size), T2 (the sbatch job id + the probe design), T3 (the DETERMINISM_RESULT.txt contents per channel).

Then report back to the manager with a 6–8 line summary ending in: **"Determinism = HOLDS (act/hom/wrk/ret EQUAL run-to-run) → Stage 2b full re-run is safe / BROKEN (channels DIFF) → manager must switch to copy-passthrough design; seed_3 04E command = ____; checkpoint present = yes/no."** Do NOT scp the patch, do NOT run the full inference, do NOT run any rake. STOP after reporting — the manager authorizes Stage 2b.

## Disciplines (enforce)
1. **Login-node-safe commands only**; **all Python via `sbatch`**, never bare python / blocking srun on the login node.
2. **Every `sbatch` `-t 7-00:00:00`**; single-line commands.
3. **No script edits, no scp, no full inference, no rakes** this stage.
4. **Probe must use the REAL seed_3 checkpoint** — verify `--smoke` doesn't swap it; if it does, STOP and flag.
5. **Verify from the artifact** (the RESULT.txt + `ls` sizes), not assumptions.
6. Don't tight-poll — ≥30 min between status checks, or hand the job id to the manager.
7. Decision-level questions → stop and flag the manager.
