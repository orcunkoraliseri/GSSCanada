# Step 4 — HPC Training Plan: Concordia Speed Cluster

## Goal

Prepare, transfer, train, and retrieve results for the Conditional Transformer (Step 4) on Concordia's Speed HPC cluster. This document covers the full workflow from local preparation through job submission to result extraction.

---

## Cluster Overview (Speed HPC)

| Property | Value |
|---|---|
| Login host | `speed.encs.concordia.ca` (alias for `speed-submit.encs.concordia.ca`) |
| SSH command | `ssh <ENCSuser>@speed.encs.concordia.ca` |
| Scheduler | SLURM |
| Default shell | tcsh (`#!/encs/bin/bash` for bash scripts) |
| Scratch storage | `/speed-scratch/$USER` (90-day inactivity auto-delete, NOT backed up) |
| Home directory | `~/` (small quota, backed up — scripts and configs only) |
| Node-local temp | `$TMPDIR` (fast I/O, deleted after job ends) |
| Off-campus access | Requires VPN |

### Target GPU Partitions

| Partition | GPU Type | VRAM | Nodes | Best For |
|---|---|---|---|---|
| `pg` | V100 | 32 GB | speed-25, speed-27 | Primary target — sufficient VRAM for d_model=256, batch=256 |
| `pt` | A100 | 80 GB | speed-37 to speed-43 | Larger batches / faster training (teaching partition — check availability) |
| `pg` | Tesla P6 | 16 GB | speed-01, speed-05, speed-17 | Fallback — may need smaller batch size |

---

## Cluster Access & Operating Model

1. **SSH hardening.** Use `ssh -o ServerAliveInterval=60 <ENCSuser>@speed.encs.concordia.ca` to avoid idle disconnects during long monitoring sessions. Off-campus: connect via Concordia GlobalProtect VPN first.
2. **Golden rule: login node vs. compute node.** The landing node is for editing, staging, `sbatch` submissions, and quick `squeue`/`sacct` checks only. All Python, `nvidia-smi`, `torch.cuda.is_available()`, and every package install **must** run inside an `salloc` shell or an `sbatch` job. Installing torch on the login node has bitten others.
3. **Interactive GPU shell for debugging.** For first-time env checks and one-off `torch.cuda.is_available()` sanity tests:
   ```bash
   salloc -p pg --gres=gpu:1 --cpus-per-task=4 --mem=32G -t 2:00:00
   ```
   Cheap and quick — burn this, not a 12-hour training slot, to confirm CUDA+torch see the GPU.
4. **Routine SLURM status commands.**
   - `squeue -u $USER` — is the job queued / running?
   - `sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ReqGRES` — post-mortem: was it host-RAM-bound? time-bound? did GPU allocation succeed? Use this before blaming the code.
   - `sinfo -p pg` — partition load / node availability.

### CPU pipeline → GPU pipeline parallels

The reader already runs a CPU-based EnergyPlus Monte Carlo pipeline on Speed (BEM). This table maps that mental model onto the Step-4 GPU workflow; reuse the patterns, switch the resource flags.

| Piece | CPU pipeline (existing BEM) | GPU pipeline (Step 4) |
|---|---|---|
| Scheduler | SLURM | SLURM |
| Job shape | Array `--array=1-6` (one task per neighbourhood) | Single job per training run today; array job reserved for future HP sweep |
| Submission script | `submit_array_tuned.sh` | `job_04D_train.sh` — same skeleton, different resource flags |
| Checkpointing | `iter_*/` dirs + `aggregated_eui.csv` | `ckpt_epoch_*.pt` (+ `best_model.pt`) + `step4_training_log.csv` |
| Progress monitor | `check_progress.sh` over SSH | `tail -f logs/04D_<jobid>.out` |
| Environment | `source $VENV/bin/activate` (CPU venv) | `conda activate /speed-scratch/$USER/envs/step4` — **separate CUDA-enabled env; do not share the CPU venv** |

---

## HPC Submission Checklist

One-page, tickable pre-flight and run-through for an end-to-end Step-4 submission on Speed. Each block abbreviates the corresponding phase — commands and context live in Phases 1–9 below; tick items here as you execute.

### Block 1 — Local Pre-flight (→ Phase 1)

- [ ] Phase-1 local gate green: seeds applied in 04D/04E, checkpoint guards in place, 04A–04F smoke-verified (see `Phase1_ready.md` Progress Log, 2026-04-20)
- [ ] `outputs_step4/step4_{train,val,test}.pt` present and non-empty
- [ ] `outputs_step4/step4_feature_config.json` present
- [ ] `outputs_step4/training_pairs.pt` and `val_pairs.pt` present (or 04A-produced equivalents)
- [ ] `requirements_step4.txt` written (§1.2)
- [ ] Transfer package created (§1.3)

### Block 2 — Transfer (→ Phase 2)

- [ ] `rsync -av` package to `/speed-scratch/$USER/occModeling/` (§2.1)
- [ ] SSH with keepalive verified: `ssh -o ServerAliveInterval=60 <ENCSuser>@speed.encs.concordia.ca` (see Cluster Access & Operating Model, §2.2)
- [ ] Package unpacked; repo and `outputs_step4/` visible on Speed

### Block 3 — Environment (one-time, on compute node) (→ Phase 3)

- [ ] Interactive GPU shell up: `salloc -p pg --gres=gpu:1 --cpus-per-task=4 --mem=32G -t 2:00:00` (see Cluster Access & Operating Model)
- [ ] Conda env built at `/speed-scratch/$USER/envs/step4` with `cuda/11.8` + torch cu118 (§3.1)
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` returns `True` inside the salloc shell (§3.2)
- [ ] (Optional) cu121 alternative evaluated and deferred — switch only after re-running local smoke tests (§3.1 note)

### Block 4 — Pre-Training CPU Jobs (→ Phase 4)

- [ ] `JOB_A=$(sbatch --parsable job_04A_dataset.sh)` — record job id (§4.1)
- [ ] `JOB_C=$(sbatch --parsable --dependency=afterok:$JOB_A job_04C_pairs.sh)` — record job id (§4.2)
- [ ] §4.3 output verification passes (file sizes sane, no empty tensors)
- [ ] If 04A fails → follow §4.2b recovery

### Block 5 — GPU Training (→ Phase 5)

- [ ] `JOB_D=$(sbatch --parsable --dependency=afterok:$JOB_A:$JOB_C job_04D_train.sh)` — record job id (§5.1)
- [ ] `tail -f logs/04D_<JOB_D>.out` — confirm GPU allocated, `$SLURM_TMPDIR` staging printed, first epoch starts (§5.1, §5.2)
- [ ] `squeue -u $USER` shows `R` (running), not stuck in `PD` (§5.2)
- [ ] Mid-run: `outputs_step4/checkpoints/ckpt_epoch_*.pt` land as expected
- [ ] If P6 OOM → resubmit with `--gres=gpu:v100:1` or `--batch_size=128` (§5.3, Troubleshooting)
- [ ] If wall-time hit → `--resume outputs_step4/checkpoints/<last_ckpt>.pt` (§5.4)

### Block 6 — Inference + Validation (→ Phases 6–7)

- [ ] `JOB_E=$(sbatch --parsable --dependency=afterok:$JOB_D job_04E_inference.sh)` — record job id (§6.1)
- [ ] 04E log shows checkpoint path + size printed (Phase1_ready item 4); predictions written under `outputs_step4/predictions/`
- [ ] `JOB_F=$(sbatch --parsable --dependency=afterok:$JOB_E job_04F_validation.sh)` — record job id (§7.1)
- [ ] Validation metrics written (`outputs_step4/validation/*.json` or equivalent per §7.1)

### Block 7 — Retrieve + Post-mortem + Cleanup (→ Phases 8–9)

- [ ] `rsync -av` outputs back to local — at minimum: checkpoints, predictions, validation, logs (§8.1)
- [ ] Local verification pass on downloaded files (§8.3)
- [ ] `sacct -j <JOB_A|C|D|E|F> --format=JobID,State,Elapsed,MaxRSS,ReqGRES` for each job — note any host-RAM pressure or GPU-starvation
- [ ] (Optional) Phase-9 cleanup on Speed — only after local validation sign-off

---

## Phase 1 — Local Preparation (Before Cluster)

### 1.1 Verify Local Files Are Ready

Before uploading, confirm all Step 4 scripts run locally on the sample dataset (see `04_augmentationGSS_testing.md`). Required files:

```
2J_docs_occ_nTemp/
├── 04A_dataset_assembly.py      # Merge + encode → tensor datasets
├── 04B_model.py                 # Transformer architecture definition
├── 04C_training_pairs.py        # Demographic-match pair construction
├── 04D_train.py                 # Training loop
├── 04E_inference.py             # Synthetic diary generation
├── 04F_validation.py            # Validation report
├── outputs_step3/
│   ├── hetus_30min.csv          # 64,061 rows × 120 cols
│   └── copresence_30min.csv     # 64,061 rows × 433 cols
└── requirements_step4.txt       # Python dependencies
```

### 1.2 Create `requirements_step4.txt`

```
torch>=2.0,<2.5
numpy>=1.24
pandas>=2.0
scikit-learn>=1.3
matplotlib>=3.7
scipy>=1.11
```

**Interpreter + CUDA pins for Speed:** Python 3.10, PyTorch 2.0–2.4, CUDA 11.8 (Speed module `cuda/11.8`). Do not upgrade torch to 3.x without re-smoke-testing locally first — `torch.load(weights_only=False)` semantics may change.

### 1.3 Package for Transfer

```bash
# On local machine — create a tarball of everything needed
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

---

## Phase 2 — Transfer to Speed

### 2.1 Upload Package

```bash
# From local machine
rsync -avP step4_hpc_package.tar.gz \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/
```

### 2.2 SSH and Unpack

```bash
ssh <ENCSuser>@speed.encs.concordia.ca

# Set up project directory on scratch
mkdir -p /speed-scratch/$USER/occModeling
cd /speed-scratch/$USER/occModeling

tar -xzf /speed-scratch/$USER/step4_hpc_package.tar.gz
ls -la  # verify all files present
```

---

## Phase 3 — Environment Setup on Speed

### 3.1 Create Conda Environment (one-time setup)

Request an interactive GPU node first — do NOT install packages on the login node:

```bash
salloc --mem=20G --gres=gpu:1 -p pg -c 4 -t 2:00:00
```

Once on the compute node:

```bash
# Set up scratch-based conda directories (avoid home quota)
mkdir -p /speed-scratch/$USER/envs/{tmp,pkgs}

# For bash users (must source modules manually):
# . /encs/pkg/modules-5.3.1/root/init/bash

# Load Anaconda
module load anaconda3/2023.03/default

# Set conda to use scratch for packages
export TMPDIR=/speed-scratch/$USER/envs/tmp
export CONDA_PKGS_DIRS=/speed-scratch/$USER/envs/pkgs

# Create environment with Python 3.10
conda create --prefix /speed-scratch/$USER/envs/step4 python=3.10 -y
conda activate /speed-scratch/$USER/envs/step4

# Check GPU driver version first — the CUDA toolkit must be compatible
nvidia-smi  # note the "CUDA Version" in top-right (driver's max supported CUDA)

# Install PyTorch with CUDA (adjust pytorch-cuda version if driver requires it)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

# Alternative (venv + pip): `module load cuda/12.1` then
#   pip install torch --index-url https://download.pytorch.org/whl/cu121
# Do NOT switch to cu121 without re-running the local smoke test first — torch 2.5+
# changes the default for torch.load(weights_only=...) and will break --resume
# unless the load calls are updated.

# Install remaining dependencies
pip install pandas>=2.0 scikit-learn>=1.3 matplotlib>=3.7 scipy>=1.11

# Verify GPU is visible
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"

conda deactivate
exit  # release the interactive node
```

**Keep the CPU BEM venv and this GPU env separate.** Reusing the BEM venv would pull in CPU-only `torch` wheels and mask GPU usage. Path convention: `/speed-scratch/$USER/envs/step4` for this pipeline; the BEM pipeline keeps its own path from the companion session.

### 3.2 Verify Environment (quick test)

```bash
salloc --mem=10G --gres=gpu:1 -p pg -c 2 -t 0:30:00

module load anaconda3/2023.03/default
conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling
python -c "
import torch, pandas as pd, numpy as np
print('PyTorch:', torch.__version__)
print('CUDA:', torch.cuda.is_available())
df = pd.read_csv('outputs_step3/hetus_30min.csv', nrows=5)
print('hetus_30min columns:', df.shape[1])
cop = pd.read_csv('outputs_step3/copresence_30min.csv', nrows=5)
print('copresence_30min columns:', cop.shape[1])
print('All imports OK')
"

conda deactivate
exit
```

---

## Phase 4 — Pre-Training Steps (CPU jobs)

Sub-steps 4A (dataset assembly) and 4C (training pairs) are CPU-bound and can run as regular jobs before the GPU training.

### 4.1 Dataset Assembly Job

Create `/speed-scratch/$USER/occModeling/job_04A_assembly.sh`:

```bash
#!/encs/bin/bash
#SBATCH --job-name=step4A_assembly
#SBATCH --mem=32G
#SBATCH -c 8
#SBATCH -p ps
#SBATCH -t 0-02:00:00
#SBATCH --output=logs/04A_%j.out
#SBATCH --error=logs/04A_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load anaconda3/2023.03/default
conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling
mkdir -p outputs_step4 logs

echo "=== Starting 04A Dataset Assembly ==="
python 04A_dataset_assembly.py
echo "=== 04A Complete ==="

conda deactivate
```

```bash
cd /speed-scratch/$USER/occModeling
mkdir -p logs
sbatch job_04A_assembly.sh
# Monitor: squeue -u $USER
# Check output: cat logs/04A_<jobid>.out
```

### 4.2 Training Pairs Job

Create `job_04C_pairs.sh`:

```bash
#!/encs/bin/bash
#SBATCH --job-name=step4C_pairs
#SBATCH --mem=32G
#SBATCH -c 8
#SBATCH -p ps
#SBATCH -t 0-02:00:00
#SBATCH --output=logs/04C_%j.out
#SBATCH --error=logs/04C_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load anaconda3/2023.03/default
conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling

echo "=== Starting 04C Training Pairs ==="
python 04C_training_pairs.py
echo "=== 04C Complete ==="

conda deactivate
```

```bash
sbatch job_04C_pairs.sh
```

### 4.2b What to do if 04A fails on Speed

Do **not** launch 04C/04D — both depend on the `step4_{train,val,test}.pt` files that 04A produces. Instead:

1. Pull the failing job's log (`logs/04A_<jobid>.err`) back to local.
2. Reproduce the failure locally on the 500-respondent sample (`python 04A_dataset_assembly.py --sample`) — it is almost always a data issue (column missing, unexpected dtype) rather than an HPC issue.
3. Fix and re-smoke-test locally, re-upload just the changed `.py` file (no need to re-tar the CSVs), and resubmit the chain starting from 04A. The `--dependency=afterok:$JOB_A` gating will keep 04C/04D pending until 04A succeeds.

### 4.3 Verify Pre-Training Outputs

After both jobs complete:

```bash
ls -lh outputs_step4/
# Expected:
#   step4_train.pt        (~XXX MB)
#   step4_val.pt          (~XXX MB)
#   step4_test.pt         (~XXX MB)
#   step4_feature_config.json
#   training_pairs.pt     (or similar)
```

---

## Phase 5 — GPU Training

### 5.1 Training Job Script

Create `job_04D_train.sh`:

```bash
#!/encs/bin/bash
#SBATCH --job-name=step4D_train
#SBATCH --mem=40G
#SBATCH -c 8
#SBATCH -p pg
#SBATCH --gres=gpu:1
# Pin family if needed:   #SBATCH --gres=gpu:v100:1   (or  gpu:a100:1  on -p pt)
#SBATCH -t 0-12:00:00
#SBATCH --output=logs/04D_%j.out
#SBATCH --error=logs/04D_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load anaconda3/2023.03/default
module load cuda/11.8

# Set scratch-based temp to avoid /tmp overflow
export TMPDIR=/speed-scratch/$USER/tmp
mkdir -p $TMPDIR

conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling
mkdir -p outputs_step4/checkpoints

echo "=== Job ID: $SLURM_JOBID ==="
echo "=== Node: $(hostname) ==="
echo "=== GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader) ==="

# Stage tensors to node-local fast scratch (GPU analogue of the BEM --use-tmpdir flag).
# $SLURM_TMPDIR is auto-cleaned when the job ends. Reads happen from local NVMe, not
# shared scratch — reduces per-epoch I/O wait on contended storage.
STAGE=$SLURM_TMPDIR/step4_data
mkdir -p $STAGE
cp outputs_step4/step4_{train,val,test}.pt  $STAGE/
cp outputs_step4/step4_feature_config.json  $STAGE/
cp outputs_step4/training_pairs.pt          $STAGE/ 2>/dev/null || true
cp outputs_step4/val_pairs.pt               $STAGE/ 2>/dev/null || true
echo "Staged $(du -sh $STAGE | cut -f1) to $STAGE"

echo "=== Starting 04D Training ==="

python 04D_train.py \
    --data_dir $STAGE \
    --output_dir outputs_step4 \
    --checkpoint_dir outputs_step4/checkpoints \
    --batch_size 256 \
    --max_epochs 100 \
    --patience 10 \
    --lr 1e-4 \
    --d_model 256 \
    --n_heads 8 \
    --n_enc_layers 6 \
    --n_dec_layers 6 \
    --fp16

echo "=== 04D Training Complete ==="
echo "=== Best checkpoint: $(ls -t outputs_step4/checkpoints/best_*.pt | head -1) ==="

conda deactivate
```

```bash
sbatch job_04D_train.sh
```

### 5.2 Monitor Training

```bash
# Check job status
squeue -u $USER

# Watch training output in real time
tail -f logs/04D_<jobid>.out

# Check GPU utilization (if you have an interactive session on same node)
# srun --jobid=<jobid> nvidia-smi

# Check job efficiency after completion
seff <jobid>

# Full post-mortem — tells you whether you were host-RAM-bound (bump --mem) or
# time-bound (resume with --resume), and whether the GPU was actually allocated.
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ReqGRES
```

### 5.3 Fallback: Smaller Batch for P6 (16 GB VRAM)

If the job lands on a Tesla P6 node and hits OOM:

```bash
# Resubmit with reduced batch size
sbatch --export=ALL job_04D_train.sh  # modify batch_size to 128 in script

# Or request V100 specifically:
sbatch --constraint=v100 job_04D_train.sh
# Note: --constraint may not work on Speed; instead check node availability
# and target specific nodes if needed
```

### 5.4 Resume from Checkpoint (if job times out)

GPU partition wall-time is tight; always design for resume. If training is interrupted by the 12-hour wall time:

1. Identify the latest checkpoint: `ls -t outputs_step4/checkpoints/*.pt | head -1`. `04D_train.py` writes `best_model.pt` (best val_JS so far) and periodic `ckpt_epoch_*.pt`; use the most recent of either.
2. Edit `job_04D_train.sh` to add the `--resume` flag pointing at the absolute path of that checkpoint. `04D_train.py` now raises `FileNotFoundError` with the absolute path if the resume target is missing (Phase1_ready item 3), so a typo fails loudly rather than silently restarting from scratch.

```bash
python 04D_train.py \
    --data_dir $STAGE \
    --output_dir outputs_step4 \
    --checkpoint_dir outputs_step4/checkpoints \
    --resume /speed-scratch/$USER/occModeling/outputs_step4/checkpoints/best_model.pt \
    --batch_size 256 \
    --max_epochs 100 \
    --patience 10 \
    --lr 1e-4 \
    --fp16

# Resubmit
sbatch job_04D_train.sh
```

---

## Phase 6 — Inference (GPU)

### 6.1 Inference Job Script

Create `job_04E_inference.sh`:

```bash
#!/encs/bin/bash
#SBATCH --job-name=step4E_infer
#SBATCH --mem=32G
#SBATCH -c 8
#SBATCH -p pg
#SBATCH --gres=gpu:1
# Pin family if needed:   #SBATCH --gres=gpu:v100:1
#SBATCH -t 0-02:00:00
#SBATCH --output=logs/04E_%j.out
#SBATCH --error=logs/04E_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load anaconda3/2023.03/default
module load cuda/11.8

export TMPDIR=/speed-scratch/$USER/tmp
mkdir -p $TMPDIR

conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling

echo "=== Starting 04E Inference ==="
# 04E asserts the checkpoint path exists and prints its absolute path + size
# before loading (Phase1_ready item 4). A missing --checkpoint here fails with
# a clear FileNotFoundError rather than a silent torch.load traceback.
python 04E_inference.py \
    --data_dir outputs_step4 \
    --checkpoint outputs_step4/checkpoints/best_model.pt \
    --output outputs_step4/augmented_diaries.csv \
    --temperature 0.8

echo "=== 04E Inference Complete ==="
echo "=== Output rows: $(wc -l < outputs_step4/augmented_diaries.csv) ==="

conda deactivate
```

```bash
sbatch job_04E_inference.sh
```

---

## Phase 7 — Validation (CPU)

### 7.1 Validation Job Script

Create `job_04F_validation.sh`:

```bash
#!/encs/bin/bash
#SBATCH --job-name=step4F_val
#SBATCH --mem=16G
#SBATCH -c 4
#SBATCH -p ps
#SBATCH -t 0-01:00:00
#SBATCH --output=logs/04F_%j.out
#SBATCH --error=logs/04F_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load anaconda3/2023.03/default
conda activate /speed-scratch/$USER/envs/step4

cd /speed-scratch/$USER/occModeling

echo "=== Starting 04F Validation ==="
python 04F_validation.py
echo "=== 04F Validation Complete ==="

conda deactivate
```

```bash
sbatch job_04F_validation.sh
```

---

## Phase 8 — Retrieve Results

### 8.1 Download Results to Local Machine

```bash
# From local machine
rsync -avP \
    <ENCSuser>@speed.encs.concordia.ca:/speed-scratch/<ENCSuser>/occModeling/outputs_step4/ \
    /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step4/
```

### 8.2 Key Files to Retrieve

| File | Size (est.) | Purpose |
|---|---|---|
| `augmented_diaries.csv` | ~2 GB | Primary output — 192K augmented diary-days |
| `best_model.pt` | ~50–100 MB | Trained checkpoint (reused in Step 6) |
| `step4_training_log.csv` | ~50 KB | Per-epoch metrics |
| `step4_validation_report.html` | ~5 MB | Validation report with charts |
| `step4_feature_config.json` | ~5 KB | Feature encoding spec |
| `logs/04D_*.out` | ~1 MB | Training stdout (for debugging) |

### 8.3 Verify Downloaded Files

```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step4

# Check augmented diaries
wc -l augmented_diaries.csv        # expect ~192,184 (header + 192,183 rows)
head -1 augmented_diaries.csv | tr ',' '\n' | wc -l   # expect ~552 columns

# Open validation report
open step4_validation_report.html
```

---

## Phase 9 — Cleanup on Speed

```bash
# After confirming local copies are complete:
# Keep the conda environment for Step 6 training
# Clean up large intermediate files
ssh <ENCSuser>@speed.encs.concordia.ca

cd /speed-scratch/$USER/occModeling
rm -f step4_hpc_package.tar.gz
rm -f outputs_step4/step4_train.pt outputs_step4/step4_val.pt outputs_step4/step4_test.pt

# Keep: best_model.pt (needed for Step 6), augmented_diaries.csv, feature_config.json
```

---

## Job Submission Quick Reference

| Step | Script | Partition | GPU | Mem | Time | Dependencies |
|---|---|---|---|---|---|---|
| 04A Assembly | `job_04A_assembly.sh` | `ps` (CPU) | 0 | 32G | 2h | None |
| 04C Pairs | `job_04C_pairs.sh` | `ps` (CPU) | 0 | 32G | 2h | 04A done |
| 04D Train | `job_04D_train.sh` | `pg` (GPU) | 1 | 40G | 12h | 04A + 04C done |
| 04E Inference | `job_04E_inference.sh` | `pg` (GPU) | 1 | 32G | 2h | 04D done |
| 04F Validation | `job_04F_validation.sh` | `ps` (CPU) | 0 | 16G | 1h | 04E done |

**Sequential submission with SLURM dependencies:**

```bash
JOB_A=$(sbatch --parsable job_04A_assembly.sh)
JOB_C=$(sbatch --parsable --dependency=afterok:$JOB_A job_04C_pairs.sh)
JOB_D=$(sbatch --parsable --dependency=afterok:$JOB_A:$JOB_C job_04D_train.sh)
JOB_E=$(sbatch --parsable --dependency=afterok:$JOB_D job_04E_inference.sh)
JOB_F=$(sbatch --parsable --dependency=afterok:$JOB_E job_04F_validation.sh)
echo "Submitted chain: $JOB_A → $JOB_C → $JOB_D → $JOB_E → $JOB_F"
```

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|---|---|---|
| `ModuleNotFoundError: torch` | Conda env not activated in job | Add `conda activate /speed-scratch/$USER/envs/step4` to job script |
| CUDA OOM | Batch too large for P6 (16 GB) | Reduce `--batch_size` to 128 or 64; or target V100/A100 partition |
| Job pending for hours | GPU partition busy | Check `sinfo -p pg --Node`; try `pt` partition (A100) |
| Job killed at 12h wall time | Training didn't converge | Add `--resume` with last checkpoint; increase `--patience` |
| `Disk quota exceeded` | Writing to home instead of scratch | Ensure all paths use `/speed-scratch/$USER/`; set `TMPDIR` |
| `bash: module: command not found` | Module system not sourced | Add `. /encs/pkg/modules-5.3.1/root/init/bash` to script |
| NaN in training loss | Learning rate too high or data issue | Check `logs/04D_*.out`; reduce `--lr` to 5e-5; verify data locally first |
| Idle SSH drops after ~10 min | Missing keepalive | Reconnect with `ssh -o ServerAliveInterval=60` |
| Training works on V100 but OOMs on P6 | P6 has only 16 GB VRAM | Resubmit with `--gres=gpu:v100:1` or reduce `--batch_size` to 128 |
| DataLoader I/O bottleneck (low GPU util) | Reading `.pt` over shared scratch each step | Stage to `$SLURM_TMPDIR` at job start (see §5.1) |
| Host-RAM OOM but GPU fine | `--mem` sets host RAM, not VRAM | Increase `--mem` (not `--gres`); lower DataLoader `num_workers` if spiking |

---

## Pitfalls (Speed-specific)

- **GPU queues are contended and wall-time-capped.** `pg` and `pt` fill up faster than `ps`, and the GPU partitions cap wall-time tighter than the CPU partition. Always design for checkpoint/resume — do not rely on "one clean 12-hour run."
- **`--mem` is host RAM, not VRAM.** VRAM is fixed by the card (32 GB V100, 80 GB A100, 16 GB P6). A job can succeed on host RAM and still CUDA-OOM on the GPU. The two are independent dials.
- **Don't over-request `--cpus-per-task`.** DataLoader workers rarely benefit beyond 4–8 for this dataset size; over-requesting just increases queue time without speeding training.
- **`--exclusive` almost never makes sense on GPU nodes.** Shared-node GPU jobs are the norm on Speed — each user's job gets its own GPU via `--gres` and the host node is shared.

---

## Future: hyperparameter sweep & multi-GPU

Neither is needed for the first HPC run. They are listed here so the pipeline's growth path is visible.

1. **HP sweep via array job.** Mirror the BEM CPU-pipeline pattern: `#SBATCH --array=1-N`, where `$SLURM_ARRAY_TASK_ID` selects a row from a CSV of `(lr, d_model, batch_size, n_enc_layers, …)` configs. Each array task writes to `outputs_step4/sweep_<task_id>/` with its own checkpoints; a small trailing CPU job aggregates `best_val_js` across runs to pick the winner.
2. **Multi-GPU training (DDP).** Change `--gres=gpu:1` to `--gres=gpu:2` and wrap the call with `torchrun --nproc_per_node=2 04D_train.py ...`. Requires a small refactor in `04D_train.py` (wrap the model in `DistributedDataParallel`, use `DistributedSampler` for the DataLoader, guard checkpoint-writes behind `rank==0`). Defer until single-GPU training is validated end-to-end on real data.

---

## Reference Links

- Speed HPC docs: https://nag-devops.github.io/speed-hpc/
- Job script generator: https://nag-devops.github.io/speed-hpc/generator.html
- Example scripts: https://github.com/NAG-DevOps/speed-hpc/tree/master/src
- HPC support: `rt-ex-hpc@encs.concordia.ca`

---

## Progress Log

| Date | Change | Status |
|---|---|---|
| 2026-04-20 | Reconciled doc with Speed GPU operating guidance from companion BEM session: added Cluster Access & Operating Model subsection (SSH keepalive, login-vs-compute rule, interactive GPU shell, `sacct` post-mortem), added CPU→GPU pipeline parallels table, switched `--gpus=1` → `--gres=gpu:1` in 04D/04E (with `gpu:v100:1` / `gpu:a100:1` pin examples), added `$SLURM_TMPDIR` data-staging block to `job_04D_train.sh`, tightened §5.4 resume guidance around the hardened `--resume` path (Phase1_ready item 3), cross-referenced checkpoint-path guard in §6.1 (Phase1_ready item 4), added Pitfalls (Speed-specific) and Future (HP sweep + DDP) subsections, expanded Troubleshooting with 4 Speed-specific rows. CUDA version unchanged (`cuda/11.8` + torch cu118); cu121 alternative noted with switch-discipline caveat. | COMPLETE |
| 2026-04-20 | Added "HPC Submission Checklist" section (7 blocks, GitHub `- [ ]` task list) mapping end-to-end submission to Phases 1–9. Placement: top matter, after CPU→GPU parallels table, before Phase 1. Cross-references existing §§ rather than duplicating commands. | COMPLETE |
