# Step 4 — Phase 1 Ready: Pre-HPC Checklist & Next Task

**Status as of 2026-04-10**
All local work for Step 4 is complete. The pipeline is ready to be packaged and submitted to the Concordia Speed HPC cluster.

---

## What Was Done (Local Machine)

### Scripts Built and Smoke-Tested

All 7 scripts were written and tested on a 500-respondent stratified sample (`--sample` flag). All tests passed.

| Script | Purpose | Smoke Test Result |
|--------|---------|-------------------|
| `sample_for_testing.py` | Stratified 500-respondent sample from Step 3 outputs | PASS |
| `04A_dataset_assembly.py` | Merge hetus + copresence, encode features, build train/val/test tensors | PASS — d_cond=76, 500 rows |
| `04B_model.py` | ConditionalTransformer architecture (import-only, not run directly) | PASS — imports clean |
| `04C_training_pairs.py` | K=5 demographic nearest-neighbor supervision pairs | PASS — 700 train, 150 val pairs |
| `04D_train.py` | Training loop: teacher forcing, AdamW, FP16, early stopping | PASS — 5 epochs, val_JS=0.136 |
| `04E_inference.py` | Autoregressive synthetic diary generation | PASS — 1500 rows (500×3) |
| `04F_validation.py` | 8-section validation + HTML report | PASS — report generated |

### Validation Report Reviewed

Sample run report (`outputs_step4_test/step4_validation_report.html`) was reviewed section by section. Result: **28 PASS / 1 WARN / 17 FAIL**.

The 17 FAILs were assessed:

| Section | Result | Interpretation |
|---------|--------|----------------|
| S1 — Training curves | FAIL (1.1, 1.2) | Only 5 epochs — pure epoch-count artifact, ignore |
| S2 — Activity JS divergence | ALL PASS (0.021–0.043) | Excellent — marginal distribution already correct |
| S3 — AT_HOME rate | 11 FAILs (8–28 pp off) | Undertrained — AT_HOME head not yet calibrated |
| S4 — Temporal structure | 4.2 FAIL (ratio=145×) | **Watch this** — model not yet generating smooth episodes |
| S5 — Co-presence | ALL PASS | Masking and binary encoding correct |
| S6 — Demographic conditioning | r=0.925 PASS | Demographics are being used correctly |
| S7 — Cross-stratum consistency | 2 FAILs | Consequence of S4 temporal incoherence |

**Decision:** No hyperparameter changes before HPC run. Architecture is sound. The transition rate (Section 4.2) is the one metric to check after full training — target ≤ 3× (currently 145× at 5 epochs).

### Supporting Files Created

- `requirements_step4.txt` — Python dependencies for HPC conda environment

### Reference Documents

- `04_augmentationGSS.md` — Full implementation spec + Progress Log
- `04_augmentationGSS_hpc.md` — Complete HPC submission guide (all 9 phases)
- `04_augmentationGSS_testing.md` — Testing spec
- `04_augmentationGSS_val.md` — Validation spec

---

## Next Task — HPC Submission (Phase 1: Local Packaging)

### Aim
Package all Step 4 scripts and the full 64,061-respondent input data into a tarball, then transfer to the Concordia Speed cluster and begin the full training run.

### What to Do
Create the tarball on the local machine and transfer it to `/speed-scratch/$USER/` on Speed. Then set up the conda environment and submit the SLURM job chain.

### Before Starting — Confirm These Are Ready

- [ ] VPN connected (required if off-campus)
- [ ] Concordia ENCS username available
- [ ] `outputs_step3/hetus_30min.csv` exists — **full 64,061-row file** (not the sample)
- [ ] `outputs_step3/copresence_30min.csv` exists — **full 64,061-row file** (not the sample)

To verify row counts:
```bash
wc -l outputs_step3/hetus_30min.csv        # expect 64,062 (header + 64,061 rows)
wc -l outputs_step3/copresence_30min.csv   # expect 64,062
```

### Steps

**Step 1 — Create tarball (local machine)**
```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp

tar -czf step4_hpc_package.tar.gz \
    04A_dataset_assembly.py \
    04B_model.py \
    04C_training_pairs.py \
    04D_train.py \
    04E_inference.py \
    04F_validation.py \
    requirements_step4.txt \
    outputs_step3/hetus_30min.csv \
    outputs_step3/copresence_30min.csv
```

Expected size: ~200–400 MB (dominated by the two CSV files).

**Step 2 — Transfer to Speed**
```bash
rsync -avP step4_hpc_package.tar.gz \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/
```

**Step 3 — SSH in and unpack**
```bash
ssh <ENCSuser>@speed.encs.concordia.ca

mkdir -p /speed-scratch/$USER/occModeling
cd /speed-scratch/$USER/occModeling
tar -xzf /speed-scratch/$USER/step4_hpc_package.tar.gz
ls -la   # confirm all files present
```

**Step 4 — Set up conda environment (one-time, on an interactive GPU node)**

Full instructions: `04_augmentationGSS_hpc.md` → Phase 3.

**Step 5 — Submit job chain**
```bash
cd /speed-scratch/$USER/occModeling
mkdir -p logs

JOB_A=$(sbatch --parsable job_04A_assembly.sh)
JOB_C=$(sbatch --parsable --dependency=afterok:$JOB_A job_04C_pairs.sh)
JOB_D=$(sbatch --parsable --dependency=afterok:$JOB_A:$JOB_C job_04D_train.sh)
JOB_E=$(sbatch --parsable --dependency=afterok:$JOB_D job_04E_inference.sh)
JOB_F=$(sbatch --parsable --dependency=afterok:$JOB_E job_04F_validation.sh)
echo "Submitted: $JOB_A → $JOB_C → $JOB_D → $JOB_E → $JOB_F"
```

Note: The SLURM job scripts (`job_04A_assembly.sh`, etc.) need to be created on the cluster before submission. Full script content is in `04_augmentationGSS_hpc.md` → Phases 4–7.

### What to Expect

| Job | Partition | Est. Time | Output |
|-----|-----------|-----------|--------|
| 04A Assembly | `ps` (CPU) | ~1–2 h | `outputs_step4/step4_*.pt`, `step4_feature_config.json` |
| 04C Pairs | `ps` (CPU) | ~1–2 h | `outputs_step4/training_pairs.pt`, `val_pairs.pt` |
| 04D Training | `pg` (GPU) | ~1.5–3 h | `outputs_step4/checkpoints/best_model.pt`, `step4_training_log.csv` |
| 04E Inference | `pg` (GPU) | ~15–30 min | `outputs_step4/augmented_diaries.csv` (~192K rows) |
| 04F Validation | `ps` (CPU) | ~30 min | `outputs_step4/step4_validation_report.html` |

### After the Run — What to Retrieve

```bash
# From local machine
rsync -avP \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/occModeling/outputs_step4/ \
    /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step4/
```

Key files to confirm after download:
- `augmented_diaries.csv` — expect ~192,184 rows and ~552 columns
- `step4_validation_report.html` — open and check Section 4.2 transition rate (target ≤ 3×)
- `step4_training_log.csv` — confirm val_JS converged and early stopping triggered

### Full HPC Guide
See `04_augmentationGSS_hpc.md` for complete SLURM job scripts, environment setup, troubleshooting, and cleanup instructions.
