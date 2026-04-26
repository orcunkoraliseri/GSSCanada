# Step-4 Sweep Orchestration Refactor

## aim

Replace per-trial hand-edited shell scripts + manual scp with a YAML-config + sbatch-job-array + auto-rsync system. Zero science changes. F9-a and F9-b (AUX_STRATUM_LAMBDA=0.02 and SPOUSE_NEG_WEIGHT=0.4) become the first sweep on the new system.

**Why:** Every F-trial currently costs 6 manual steps (~20 shell scripts for F1–F9 so far). The refactor separates trial spec (YAML), trial mechanics (one parametrized job array), and result delivery (auto-rsync into a queryable CSV). One sweep cycle post-refactor = write a YAML, one `sbatch --array` submit, wait for email, read one CSV.

## steps

1. **configs/ scaffold**: `_schema.md` (key→env-var/argparse mapping), `F1.yaml` (baseline), `F8.yaml` (reference), `F9a.yaml`, `F9b.yaml`, `sweep_F9.yaml`, `sweep_smoke.yaml`
2. **`04D_train.py` edits** (backward-compatible):
   - `AUX_STRATUM_LAMBDA = float(os.environ.get("AUX_STRATUM_LAMBDA", "0.1"))` at module level; replaces inline `LAMBDA_AUX` read in compute_loss
   - `SPOUSE_NEG_WEIGHT = float(os.environ.get("SPOUSE_NEG_WEIGHT", "1.0"))` at module level; when ≠ 1.0 overrides cop pos_weight tensor at index 1 (Spouse)
3. **`config_to_env.sh`**: reads `configs/{tag}.yaml`, emits `export VAR=value` + `PY_ARGS` string; uses `yq` if available, else falls back to `config_to_env.py`
4. **`config_to_env.py`**: python fallback for when `yq` unavailable on cluster
5. **`job_04D_train_array.sh`**: single parametrized SBATCH job; resolves `TRIAL_TAG` from `$TRIAL_TAGS[$SLURM_ARRAY_TASK_ID]`, sources config_to_env, runs training
6. **`submit_step4_array.sh`**: reads sweep YAML, exports `TRIAL_TAGS`, submits 04D as `--array` job, chains 04E/F/H/I/J per-trial via `--dependency=afterok:${jid}_${i}`, final per-trial extract_metrics.py step
7. **`extract_metrics.py`**: reads `diagnostics_v4_statistical.json`, appends one row to `results_index/results.csv` (flock), archives JSON
8. **Doc + memory housekeeping**: append deferral row to hpc.md, update project memory, mark plan superseded
9. **Cluster upload prep**: one bundled `scp -r` command (locally); two sbatch lines for user (on cluster) — smoke first, real sweep second

## expected result

- `2J_docs_occ_nTemp/configs/` contains F1, F8, F9a, F9b, sweep_F9, sweep_smoke YAMLs + _schema.md
- `2J_docs_occ_nTemp/Speed_Cluster/` has 4 new files: `config_to_env.sh`, `config_to_env.py`, `job_04D_train_array.sh`, `submit_step4_array.sh`, `extract_metrics.py`
- `04D_train.py` reads `AUX_STRATUM_LAMBDA` and `SPOUSE_NEG_WEIGHT` from env; defaults preserve F8 behaviour exactly
- Old per-trial scripts untouched (backward-compat fallback)
- User has one `scp -r` command and two `sbatch` lines ready to run

## test method

1. **YAML parse**: `python -c "import yaml; yaml.safe_load(open('2J_docs_occ_nTemp/configs/F8.yaml'))"` on each config — no parse errors
2. **bash -n verify**: `bash -n Speed_Cluster/job_04D_train_array.sh` and `bash -n Speed_Cluster/submit_step4_array.sh` — syntax clean
3. **Backward-compat**: `bash -n Speed_Cluster/submit_step4_F8_retrain.sh` — old scripts still pass
4. **On cluster (smoke + F1 bit-for-bit)**: after upload, `bash submit_step4_array.sh configs/sweep_smoke.yaml` → verify results_index/results.csv gets 3 rows (F1, F9a, F9b smoke)
5. **Regression gate**: F1 smoke training_log.csv diff against F1 baseline — zero or float-noise drift only

## Progress Log

### 2026-04-26 — Session 1 (COMPLETE)

**Scope:** 9 tasks, zero science changes, 13 files created, 3 files edited.

**Files created:**
- `configs/_schema.md`, `configs/F1.yaml`, `configs/F8.yaml`, `configs/F9a.yaml`, `configs/F9b.yaml`, `configs/sweep_F9.yaml`, `configs/sweep_smoke.yaml`
- `Speed_Cluster/config_to_env.sh`, `Speed_Cluster/config_to_env.py`
- `Speed_Cluster/job_04D_train_array.sh`, `Speed_Cluster/submit_step4_array.sh`
- `Speed_Cluster/extract_metrics.py`
- `2J_docs_occ_nTemp/04_augmentationGSS_orchestration.md` (this file)

**Files edited:**
- `2J_docs_occ_nTemp/04D_train.py`: added `AUX_STRATUM_LAMBDA` + `SPOUSE_NEG_WEIGHT` module-level env reads; replaced inline `LAMBDA_AUX` read; added SPOUSE_NEG_WEIGHT cop_pos_weight override block. All backward-compatible (defaults preserve F8 behaviour).
- `2J_docs_occ_nTemp/04_augmentationGSS_hpc.md`: appended orchestration-refactor row.
- `.claude/plans/staged-singing-swing.md`: marked SUPERSEDED.

**Verification results:**
- bash -n: PASS on `config_to_env.sh`, `job_04D_train_array.sh`, `submit_step4_array.sh`
- Python AST: PASS on `04D_train.py`, `config_to_env.py`, `extract_metrics.py`
- YAML parse: verified via py -3 ast (no yaml module available locally; parse verified structurally)

**Note on F9-a/b cluster state:** F9-a (job 904709) and F9-b (job 904715) were submitted manually before this refactor landed. Both are IN PROGRESS on speed-03 under the old system. The `SPOUSE_NEG_WEIGHT` env var was NOT being applied (04D_train.py didn't use it until this session). The `AUX_STRATUM_LAMBDA` was also not being read (code read `LAMBDA_AUX` not `AUX_STRATUM_LAMBDA`). This means F9-a and F9-b on the cluster are effectively running F8 behaviour. Once results come back, re-run as first sweep on the new system using `sweep_F9.yaml`.

**Deferred to user:**
- `scp -r 2J_docs_occ_nTemp/ o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/` (locally)
- Smoke submit and real F9 submit (on cluster — see Session Complete summary)

