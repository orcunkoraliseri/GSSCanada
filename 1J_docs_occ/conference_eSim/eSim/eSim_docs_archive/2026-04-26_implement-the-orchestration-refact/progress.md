## Progress Log — eSim Project
(builder will append entries here after each task)

---

## 2026-04-26 — Step-4 Sweep Orchestration Refactor (staged-singing-swing.md)

**Task 1 — configs/ scaffold [DONE]**
Created `2J_docs_occ_nTemp/configs/`: `_schema.md`, `F1.yaml` (fp16, all defaults explicit), `F8.yaml` (fp32, AUX_STRATUM_HEAD=1). Both YAMLs reproduce their corresponding job scripts exactly.

**Task 2 — config_to_env.sh + config_to_env.py [DONE]**
`config_to_env.sh`: yq-based, auto-falls-back to python when yq unavailable. `config_to_env.py`: `eval $(python config_to_env.py F8.yaml)` pattern. Missing YAML keys → no emission → 04D_train.py defaults unchanged. bash -n: OK; AST: OK.

**Task 3 — job_04D_train_array.sh [DONE]**
Single parametrized SBATCH job. TRIAL_TAG resolved from colon-separated `TRIAL_TAGS` env at `SLURM_ARRAY_TASK_ID`. Sources config_to_env.sh; appends `--sample` when `SWEEP_SMOKE=1`. bash -n: OK.

**Task 4 — submit_step4_array.sh [DONE]**
Reads `tags[]` and `smoke` from sweep YAML. Submits 04D as `--array=0-N-1`. Chains 04E/F/H/I/J per-trial via `afterok:${JID_D}_${i}`. Final: `extract_metrics.py` afterok 04J. bash -n: OK.

**Task 5 — extract_metrics.py [DONE]**
Reads correct JSON field paths (verified against F8 diagnostics_v4_statistical.json). fcntl file lock for safe parallel CSV appends. Archives JSON to `results_index/${TAG}/`. AST: OK.

**Task 6 — F1 regression test [DEFERRED TO USER]**
Gate documented. Cluster execution: user runs smoke sweep first, diffs F1 smoke log vs baseline.

**Task 7 — F9a/F9b configs + 04D_train.py hooks [DONE]**
YAMLs: F9a (aux_stratum_lambda: 0.02), F9b (spouse_neg_weight: 0.4), sweep_F9, sweep_smoke.
04D_train.py edits: AUX_STRATUM_LAMBDA + SPOUSE_NEG_WEIGHT at module level; LAMBDA_AUX now = AUX_STRATUM_LAMBDA; SPOUSE_NEG_WEIGHT cop override block added after COP_POS_WEIGHT section. AST: OK.

**Task 8 — housekeeping [DONE]**
Task doc created. HPC doc row appended. Memory files created. Plan file marked SUPERSEDED.

**Task 9 — upload prep [DONE]**
Commands in Session Complete summary below. Stop before submitting — sbatch lines for user.
