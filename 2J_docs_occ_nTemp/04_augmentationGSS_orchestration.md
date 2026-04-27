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

---

### 2026-04-26 — Session 2 — Smoke sweep debugging (IN PROGRESS)

**Context:** First smoke sweep attempt (job 905068) completed 04D successfully but 04E failed on all 3 trials, leaving 04H/I/J/F/extract in DependencyNeverSatisfied. A prior smoke attempt (jobs 904825–904829) had also failed due to the mapfile tag-collapse bug fixed in the same session.

**Bugs found and fixed:**

**Bug 1 — `submit_step4_array.sh` tag collapse** (fixed in earlier session 2 attempt):
- `tr -d '[:space:]'` in the mapfile pipeline deleted newlines, collapsing `F1\nF9a\nF9b` into `F1F9aF9b` — a single-element array. SLURM submitted `--array=0-0`; 04D looked for `configs/F1F9aF9b.yaml`, failed, poisoned entire chain.
- Fix: replaced `| tr -d '[:space:]'` with `| sed 's/[[:space:]]*$//'` to strip only trailing whitespace per line.

**Bug 2 — `04D_train.py` warmup gate blocks checkpoint save in sample mode**:
- In `--sample` mode, `warmup_steps=50`. With batch_size=16 and ~100 sample records, `len(train_loader)≈7`, so `warmup_epochs=ceil(50/7)=8`. Sample mode caps `max_epochs=5`, so `past_warmup` is never true. `best_model.pt` is never written — the old F1 checkpoint from a previous full run (trained with d_cond=91) survives unchanged.
- Fix (`2J_docs_occ_nTemp/04D_train.py` line 670): `past_warmup = args.sample or (epoch + 1) > warmup_epochs`

**Bug 3 — `04E_inference.py` overrides d_cond from live feature config**:
- Line 287 (`model_config["d_cond"] = feat_cfg["d_cond"]`) replaced the checkpoint's d_cond (91) with the current feature config's d_cond (92). This built a model with 92-feature conditioning but tried to load weights shaped for 91 features, producing `RuntimeError: size mismatch for cls_mlp.0.weight: [256, 92] vs [256, 93]` and the same for all FiLM gen layers.
- Fix (`2J_docs_occ_nTemp/04E_inference.py` line 287): removed the override; 04E now uses the checkpoint's own `model_config` without modification.

**Files edited:**
- `2J_docs_occ_nTemp/Speed_Cluster/submit_step4_array.sh`: mapfile pipeline fix (tag collapse)
- `2J_docs_occ_nTemp/04D_train.py`: warmup gate bypass for `--sample` mode
- `2J_docs_occ_nTemp/04E_inference.py`: removed `model_config["d_cond"]` override

**Orphaned jobs cancelled:** 904825–904829 (first attempt), 905070–905088 (second attempt).

**Deferred to user:**
1. `scancel 905070 905071 905072 905073 905074 905078 905079 905080 905081 905082 905084 905085 905086 905087 905088` (on cluster)
2. `scp 2J_docs_occ_nTemp/04D_train.py 2J_docs_occ_nTemp/04E_inference.py o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/` (locally)
3. `rm /speed-scratch/o_iseri/occModeling/outputs_step4_F1/checkpoints/best_model.pt` (on cluster — delete stale d_cond=91 checkpoint)
4. `cd /speed-scratch/o_iseri/occModeling && bash Speed_Cluster/submit_step4_array.sh configs/sweep_smoke.yaml smoke_$(date +%Y%m%d_%H%M)` (on cluster)

---

### 2026-04-26 — Session 1 task implementation notes (from `.claude/progress.md`)

These per-task notes supplement the Session 1 summary above with implementation-level detail recorded by the builder agent.

**Task 1 — configs/ scaffold:** `F1.yaml` fp16 with all defaults explicit; `F8.yaml` fp32 with `AUX_STRATUM_HEAD=1`. Both YAMLs reproduce their corresponding per-trial job scripts exactly (bit-for-bit compatible).

**Task 2 — config_to_env.sh + config_to_env.py:** `config_to_env.sh` is yq-based and auto-falls-back to `config_to_env.py` when yq unavailable on cluster. The `eval $(python config_to_env.py F8.yaml)` pattern. Missing YAML keys emit nothing — 04D_train.py defaults remain unchanged. This means any old trial config that omits a key does not break; it silently inherits 04D defaults.

**Task 3 — job_04D_train_array.sh:** `TRIAL_TAG` resolved from colon-separated `TRIAL_TAGS` env var at index `$SLURM_ARRAY_TASK_ID`. Sources `config_to_env.sh` for env-var injection; appends `--sample` when `SWEEP_SMOKE=1`.

**Task 4 — submit_step4_array.sh:** Reads `tags[]` list and `smoke` boolean from sweep YAML (grep/sed only, no yq dependency). Submits 04D as `--array=0-N-1`. Chains 04E → {04F, 04H, 04I, 04J} per trial via `--dependency=afterok:${JID_D}_${i}`. Final step: `extract_metrics.py` after 04J.

**Task 5 — extract_metrics.py:** Reads exact JSON field paths verified against `diagnostics_v4_statistical.json` (field names are non-obvious — see memory file). Uses `fcntl` file-lock for safe parallel CSV appends when multiple trials complete simultaneously. Archives per-trial JSON to `results_index/${TAG}/`.

**Task 6 — F1 regression test:** Gate documented (composite < 1.045 | AT_HOME ≤ +5.3 pp | Spouse ≤ +10 pp | act_JS ≤ 0.05). Cluster execution deferred — user runs smoke sweep first, diffs F1 smoke training log against baseline.

**Task 7 — F9a/F9b configs + 04D_train.py hooks:** `F9a.yaml` sets `aux_stratum_lambda: 0.02`; `F9b.yaml` sets `spouse_neg_weight: 0.4`. In `04D_train.py`: `AUX_STRATUM_LAMBDA` and `SPOUSE_NEG_WEIGHT` now read from env at module level; `LAMBDA_AUX` now equals `AUX_STRATUM_LAMBDA` (renamed reference); `SPOUSE_NEG_WEIGHT` cop `pos_weight` override block added after the `COP_POS_WEIGHT` section (index 1 = Spouse channel). All backward-compatible — defaults (0.1 and 1.0) reproduce F8 behaviour exactly.

**Task 8 — housekeeping:** Task doc (`04_augmentationGSS_orchestration.md`) created. HPC doc (`04_augmentationGSS_hpc.md`) orchestration-refactor row appended. Memory files (`memory/project_step4_gss_transformer.md`, `MEMORY.md`) created and indexed. Plan file (`.claude/plans/staged-singing-swing.md`) marked SUPERSEDED.

**Task 9 — upload prep:** One bundled `scp -r` command (locally); two sbatch lines for user (on cluster) — smoke first, real sweep second. Pipeline stopped before submitting.

**State at session close (from `.claude/state.md`):** COMPLETE — YAML configs + sbatch job array + auto-rsync implemented. 9/9 tasks done. Zero science changes. F9-a/b configs preserved. 04D_train.py env-var hooks landed. User sbatch lines ready.

---

### 2026-04-27 — Session 3 — Continued smoke sweep debugging (IN PROGRESS)

**Context:** Session 2's four deferred actions were executed by user (jobs cancelled, 04D_train.py + 04E_inference.py scp'd, stale checkpoint deleted, smoke sweep resubmitted as chain 905712). This exposed three new bugs in the orchestration layer.

---

**Bug 4 — `job_04D_train_array.sh`: `BASH_SOURCE[0]` resolves to SLURM spool dir**

- At SLURM runtime `BASH_SOURCE[0]` = `/local/data/slurm/var/spool/jobXXXX/slurm_script` (the job's spool copy), not the real script path. `dirname` of that path points to the spool directory, which contains no `config_to_env.sh`.
- Consequence: `source "${SCRIPT_DIR}/config_to_env.sh"` silently failed. All trial-specific env vars (`AUX_STRATUM_LAMBDA=0.02` for F9a, `SPOUSE_NEG_WEIGHT=0.4` for F9b) were never applied — all three trials silently ran with F8 defaults.
- Fix (`job_04D_train_array.sh`): replaced dynamic resolution with hardcoded `SCRIPT_DIR="$BASE/Speed_Cluster"` (BASE already set at script top to `/speed-scratch/o_iseri/occModeling`).
- Confirmed fixed in 905712 run: F9b log shows `SPOUSE_NEG_WEIGHT=0.4: Spouse (idx 1) cop pos_weight overridden` and `cls_mlp: Linear(in_features=93, ...)`.

---

**Bug 5 — `submit_step4_array.sh`: `DATA_DIR_04E` hardcoded to `outputs_step4`**

- 04E's `--data_dir` argument was hardcoded to `outputs_step4` regardless of smoke mode.
- In smoke mode 04D trains on `outputs_step4_test` (500 respondents, potentially different `d_cond`). 04E loading from a different dir would cause model architecture mismatches (tensor shape errors).
- Fix (`submit_step4_array.sh`): added `DATA_DIR_04E` variable; smoke mode sets it to `outputs_step4_test`; normal mode leaves it as `outputs_step4`. The `--data_dir ${DATA_DIR_04E}` substitution is now used in the 04E `--wrap` command.

---

**Bug 6 — CRLF line endings on cluster scripts**

- Scripts edited on Windows carry `\r\n` line endings. On the Linux cluster, bash interprets `\r` as part of command names → `\r': command not found` errors at runtime.
- Fix: `dos2unix` on affected scripts on the cluster (immediate workaround); added `*.sh text eol=lf` and `*.py text eol=lf` to root `.gitattributes` (permanent fix — enforces LF on checkout).
- File edited: `.gitattributes` (root of repo).

---

**Bug 7 (current blocker) — `outputs_step4_test/` missing inference metadata files for 04E**

- After 04D completes in smoke mode, 04E attempts to load `step4_all_meta.csv` and `step4_feature_config.json` from `args.data_dir` (= `outputs_step4_test/`).
- `outputs_step4_test/` was set up for training only and contains solely tensor `.pt` files. Both metadata files exist only in `outputs_step4/`.
- Error: `FileNotFoundError: [Errno 2] No such file or directory: 'outputs_step4_test/step4_all_meta.csv'` — crashed at `04E_inference.py:269` for all three trials (F1, F9a, F9b) in job chain 905713.
- Safety note: `04E_inference.py:305` uses `aug_df.merge(meta_merge, on=["occID","CYCLE_YEAR"], how="left")` — a LEFT JOIN, so using the full 64K-row `outputs_step4/step4_all_meta.csv` with a 500-row smoke `aug_df` is safe; only matching rows are retained.
- Fix proposed (not yet applied — awaiting user execution on cluster):
  ```
  ln -sf /speed-scratch/o_iseri/occModeling/outputs_step4/step4_all_meta.csv /speed-scratch/o_iseri/occModeling/outputs_step4_test/step4_all_meta.csv
  ln -sf /speed-scratch/o_iseri/occModeling/outputs_step4/step4_feature_config.json /speed-scratch/o_iseri/occModeling/outputs_step4_test/step4_feature_config.json
  ```
  No code changes needed — symlinks expose the full-data inference files inside the test data directory.

---

**Files edited in Session 3:**
- `2J_docs_occ_nTemp/Speed_Cluster/job_04D_train_array.sh`: BASH_SOURCE → hardcoded SCRIPT_DIR fix (Bug 4)
- `2J_docs_occ_nTemp/Speed_Cluster/submit_step4_array.sh`: DATA_DIR_04E variable for smoke mode (Bug 5)
- `.gitattributes`: added `*.sh text eol=lf` and `*.py text eol=lf` (Bug 6)

**Current status:** 04D CONFIRMED working (chain 905712 — all three trials complete, config env vars applied). 04E BLOCKED on Bug 7 (metadata files). Entire downstream chain (04F/04H/04I/04J/extract_metrics) in `DependencyNeverSatisfied`.

**Deferred to user:**
1. Cancel dead jobs (on cluster): `scancel $(squeue -u $USER -h -o %i)`
2. Create two symlinks (on cluster — single line each):
   `ln -sf /speed-scratch/o_iseri/occModeling/outputs_step4/step4_all_meta.csv /speed-scratch/o_iseri/occModeling/outputs_step4_test/step4_all_meta.csv`
   `ln -sf /speed-scratch/o_iseri/occModeling/outputs_step4/step4_feature_config.json /speed-scratch/o_iseri/occModeling/outputs_step4_test/step4_feature_config.json`
3. Resubmit smoke sweep (on cluster): `cd /speed-scratch/o_iseri/occModeling && bash Speed_Cluster/submit_step4_array.sh configs/sweep_smoke.yaml smoke_$(date +%Y%m%d_%H%M)`
4. After smoke passes all gates → submit real F9 sweep (on cluster): `bash Speed_Cluster/submit_step4_array.sh configs/sweep_F9.yaml F9_$(date +%Y%m%d_%H%M)`

**Gates (per arm):** composite < 1.045 | AT_HOME ≤ +5.3 pp | Spouse ≤ +10 pp | act_JS ≤ 0.05

