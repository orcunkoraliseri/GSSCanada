# EMPLOYEE PROMPT — Leg-3 · Step-4 · POOL PROVENANCE + FIX LANDING-POINT (read-only)

**You are the employee. Execute the task below and append a Progress Log entry on completion.** READ-ONLY reconnaissance: no script edits, no re-rake, no retrain, no job submission, no writes to any `outputs_step4/` dir. Your only write is a Progress Log entry. Windows-local reads use `py -3 -X utf8` only if you truly need Python (prefer `ls`/`head`/file-date peeks — do NOT scan the 400 MB pool into context). Cluster reads over ssh (`o_iseri@speed.encs.concordia.ca`) are **login-node-safe commands ONLY**: `ls`, single-file `cat`/`head`/`tail`/`grep`/`wc -l`, `squeue`, `sacct`, `scontrol`. **NEVER run bare `python`/`python3` or a blocking `srun` on the login node** (account-suspension rule). No `sbatch` either — this is pure inspection.

---

## Why you exist (context)

We are about to apply a small, targeted fix to `3rdJ_04E_inference_4split.py`'s G3 co-presence binarization (lines 526–561): replace the single **global** quantile threshold per co-presence channel with a **per-(day-type × slot)** threshold (with a min-support fallback). This fixes the W3 colleague-co-presence weekday-16:30 over-generation (diagnosed 2026-07-21 — see the W3 Progress Log entry in `3rdJ_04_augmentationGSS_4split.md`). The fix requires **re-running 04E inference** (the raw continuous co-presence scores are overwritten by binarization before the CSV is written — line 548 precedes the `to_csv` at line 576 — so there is no post-hoc shortcut).

**Before we spend a cluster re-cascade, we must know WHERE to land the fix.** The Step-5 pool of record is:
`3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv`.
Separately, a **warmup job `1127956`** was submitted to Speed on 2026-07-19 (`3rdJ_s4_4split_warmup.sh`), the first stage of a warmup→joint→5-seed-sweep→rake retrain. **The pivotal question: will that pending cluster run produce a NEW pool that supersedes `seed_3_raked3_mindwell_actv`, or is `seed_3` the final locked pool for Step-5?** The answer decides whether we bake the fix into the pending run's 04E (marginal cost ~0) or re-run 04E on the checkpoint that produced the current `seed_3` (separate re-cascade).

---

## Tasks (read-only, in order)

**T1 — Provenance of the current `seed_3` pool.**
- Local: report the file **modification date/size** of `.../sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv` and list the **sibling files** in that dir (any manifest/log/`g3_copresence_thresholds.json`/`isr_summary.json`/checkpoint pointer, `step4_validation_report.*`). From any manifest/log/thresholds JSON present, extract **which checkpoint and which 04E run** produced this pool (checkpoint path, date, `val_js`/seed label if recorded). Do NOT open the CSV itself — dates + sibling metadata only.
- Identify the **checkpoint** that generated `seed_3` (path + whether it still exists locally and/or on the cluster). This is the checkpoint a "re-run 04E on current pool" path would need.

**T2 — What will job 1127956 (and its downstream) produce?**
- Cluster: `squeue -u o_iseri` and `sacct -j 1127956 --format=JobID,JobName,State,Start,End,Elapsed,ExitCode` — report current state (running / completed / failed) and elapsed.
- Cluster: `cat` the wrapper `3rdJ_s4_4split_warmup.sh` (and, if present, `..._joint.sh`, `..._train.sh`) at `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/` — extract the **output directory** each stage writes its checkpoints/pool to, and whether the eventual 04E inference + rake chain writes to a **new** `sweep/…` dir or would **overwrite** `seed_3_raked3_mindwell_actv`. Report the exact output paths.
- Cluster: `tail` the warmup `.out`/`.err` at `/speed-scratch/o_iseri/logs/3J_s4_4split_warmup_1127956.*` — report progress/errors, whether 04A/04C/04D warmup have started/finished.
- State plainly: **does the pending run's pipeline target a new pool dir (supersedes seed_3), or seed_3's own dir (in-place), or neither yet (only warmup, pool generation not wired until a later manual step)?**

**T3 — Confirm the fix mechanics (cross-check, don't take my word).**
- In `3rdJ_04E_inference_4split.py`: confirm (a) the raw continuous co-presence scores are overwritten in-place by binarization (line ~548) **before** `to_csv` (line ~576) → not persisted; (b) inference RNG is seeded (`torch.manual_seed(42)`, line ~314) and note any OTHER RNG source in `run_inference` / the AR decode that could make a re-run non-deterministic for act/hom/wrk/ret (i.e. would re-running 04E on the same checkpoint reproduce act/hom/wrk/ret byte-identical, so ONLY co-presence changes?). Report yes/no with the evidence (which functions call `torch.multinomial`/`np.random`/`random` and whether they're seeded).

**T4 — Recommend the landing point (evidence-based, no action).**
Given T1–T3, state which is correct and why:
- **(A) Bake the per-slot G3 fix into 04E now**, so the pending cluster run's 04E inference carries it → fix is ~free, Step-5 re-runs on the new pool when it lands. (Correct IF the pending run will produce the pool Step-5 will use.)
- **(B) Re-run 04E on the checkpoint that made `seed_3`** to regenerate the current pool with the fix, then re-cascade 04L→04T→04M→Step-5. (Correct IF `seed_3` is the final pool and the pending run does NOT supersede it.)
Name the concrete output dir the fixed pool would land in under each, and flag any risk (e.g. re-running 04E on `seed_3`'s checkpoint would need that checkpoint present on the cluster — confirm it is).

---

## Deliverable / report back

Append a Progress Log entry to `3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` headed `### 2026-07-21 — Pool provenance + G3-fix landing-point recon (read-only)`, containing: T1 (seed_3 date + producing checkpoint + siblings), T2 (1127956 state + output-dir mapping + does-it-supersede-seed_3), T3 (persistence + determinism confirmation with evidence), T4 (recommended landing point A or B, with the exact target dir and any checkpoint-availability risk).

Then report back to the manager with a 6–8 line summary ending in the one-line verdict: **"Land the fix via (A) bake-into-pending-run / (B) re-run-04E-on-seed_3-checkpoint, because ____; target pool dir = ____; determinism = only-cop-changes CONFIRMED/AT-RISK because ____."** Do NOT propose or apply any edit. STOP after reporting — the manager authors the fix.

## Disciplines (enforce)
1. **Read-only.** No `.py` edits, no `sbatch`/`srun`/bare-python on the login node, no writes to `outputs_step4/`.
2. **Login-node-safe cluster commands only** (`ls`/`cat`/`head`/`tail`/`grep`/`wc -l`/`squeue`/`sacct`/`scontrol`); single-file peeks, no directory-wide python scans.
3. **Verify from the artifact/metadata, not assumptions** — dates, wrapper output paths, sacct state, code lines quoted verbatim.
4. **Do NOT open the 400 MB pool CSV** — provenance from dates + sibling manifests only.
5. Decision-level questions → stop and flag the manager.
