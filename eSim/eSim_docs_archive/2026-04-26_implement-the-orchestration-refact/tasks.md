# tasks.md — Step-4 Sweep Orchestration Refactor
## Session: 2026-04-26
## Goal: YAML configs + sbatch job arrays + auto-rsync (staged-singing-swing.md)
## Skills: ext_python-pro (builder persona), ext_ml-engineer (thematic)

## Session scope
- Read: 2J_docs_occ_nTemp/Speed_Cluster/ (existing scripts), 2J_docs_occ_nTemp/04D_train.py, 2J_docs_occ_nTemp/04_augmentationGSS_hpc.md, diagnostics_v4_statistical.json, .claude/plans/staged-singing-swing.md
- Write: 2J_docs_occ_nTemp/configs/ (new dir), 2J_docs_occ_nTemp/Speed_Cluster/ (new files only), 2J_docs_occ_nTemp/04D_train.py, 2J_docs_occ_nTemp/04_augmentationGSS_hpc.md, 2J_docs_occ_nTemp/04_augmentationGSS_orchestration.md (new), .claude/tasks.md, .claude/progress.md, .claude/state.md, memory/project_step4_gss_transformer.md
- Off-limits: eSim_occ_utils/, eSim_bem_utils/, 0_Occupancy/, 0_BEM_Setup/, all existing job_04D_train_F[X].sh and submit_step4_F[X]_retrain.sh

## Tasks

- [x] Task 1 — Scaffold `configs/` and create the F1 baseline YAML
- [x] Task 2 — `config_to_env.sh` (or `.py`): YAML → env-export translator
- [x] Task 3 — `Speed_Cluster/job_04D_train_array.sh` (single parametrized job)
- [x] Task 4 — `Speed_Cluster/submit_step4_array.sh` (sweep driver)
- [x] Task 5 — `extract_metrics.py` (final post-job step)
- [x] Task 6 — Bit-for-bit regression test on F1 (doc + gates defined; cluster execution deferred to user)
- [x] Task 7 — F9-a / F9-b configs (the carry-forward science)
- [x] Task 8 — Doc + memory + stale-plan housekeeping
- [x] Task 9 — Cluster upload + first sweep submit
