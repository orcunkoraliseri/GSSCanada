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
| 2026-04-21 | **Inference bottleneck diagnosed and fixed (04E_inference.py).** Job 901028 stalled at 64/64061 respondents after 12+ minutes. Root cause: `run_inference()` was calling `model.generate()` once per respondent (B=1), totalling ~128K serial GPU calls. Fix: rewrote `run_inference()` to collect all synthetic (respondent, target_stratum) pairs per batch chunk and call `model.generate()` once per batch (~512 pairs at once, batch_size=256). Job 901031 confirmed fix — inference completed successfully. | COMPLETE |
| 2026-04-21 | **Activity distribution quality failure diagnosed (check_04E_output.py created).** Ran diagnostic on augmented_diaries.csv from job 901031. Found severe distribution mismatch in synthetic diaries: Work 13.3%→0.9% (suppressed 15×), Recreation 15.2%→32.1% (inflated 2×). Root causes identified: (1) unweighted cross-entropy loss treats all 14 activity classes equally, causing the model to ignore rare classes like Work; (2) validation used only n=200 random samples → noisy val_JS metric that masked the problem. Created `check_04E_output.py` (diagnostic: activity marginal distributions, sleep/work temporal patterns, AT_HOME consistency, sample respondent diary) and `job_check_04E.sh` (sbatch wrapper, ps partition, 32G). **HPC policy warning received from Speed managers:** running `check_04E_output.py` directly on speed-submit (login node) violated HPC compute policy. All diagnostics must be submitted via `sbatch`. Corrective action: all future diagnostics use `job_check_04E.sh`. | COMPLETE |
| 2026-04-21 | **Class-weighted training run submitted (job 901038, 04D_train.py).** Applied two fixes to 04D_train.py: (1) class-weighted CE loss — inverse-sqrt-frequency weights computed from training data (`weight ∝ 1/√count`, normalised to unit mean) passed to `F.cross_entropy()` via new `act_weights` parameter in `compute_loss()`; upweights Work (~2.74×) and other rare classes; (2) validation upgraded from n_sample=200 to n_sample=2000 with batched generation (batch_sz=256) to reduce noise in val_JS. `job_04D_train.sh` updated: removed `--resume` flag for a clean run. Job 901038 ran on speed-17 (pg partition, 40G RAM, Tesla P6 GPU). **Training outcome:** early stopped at epoch 11 (patience=10). Best val_JS=0.1253 saved at epoch 1; val_JS degraded thereafter as weighted training progressed. **Key finding:** val_JS in `validate()` already computes stratum-specific JS (ref_dists keyed by (cy, s_tgt)) — the metric was not miscalibrated. The issue is that inverse-sqrt-freq weights normalized by mean give Work (13% freq) a weight ≈ 0.43 — *below average* — meaning the normalization accidentally provides insufficient gradient boost for Work. | COMPLETE |
| 2026-04-21 | **Inference job 901044 completed; diagnostic jobs 901050 and 901054 confirmed Work suppression.** Inference with best_model.pt from job 901038: 192183 rows saved (64061 observed + 128122 synthetic), correct shape (192183, 545), colleagues=0 OK. Diagnostic job 901050 (check_04E_output.py) ran on speed-07. Extended diagnostic (job 901054) added per-stratum breakdown (Section 2b). **Findings:** Work suppressed across all strata — weekday obs 16.5% → syn 3.9% (4.2×), Saturday obs 5.9% → syn 0.7% (8.4×), Sunday obs 5.0% → syn 0.6% (8.3×). Recreation over-generated +10pp in every stratum. Transit suppressed ~3× across all strata. AT_HOME consistency: clean (0 violations). Root cause confirmed: inv-sqrt-freq weights normalized by mean leave Work with weight 0.43 (below average) — effectively under-boosted despite the intent. | COMPLETE |
| 2026-04-21 | **Targeted class-weight boosts applied; training job 901055 submitted.** Fixed `04D_train.py` lines 342–347: after inv-sqrt-freq mean-normalization, apply explicit multipliers — Work (idx 0) ×5, Transit (idx 12) ×3, Social (idx 8) ×2 — based on observed suppression factors from diagnostic job 901054. Training from scratch (no `--resume`). Job 901055 running on speed-01 (pg partition, Tesla P6, 40G RAM). Wall-time limit: 2 days. | COMPLETE |
| 2026-04-21 | **04F validation job 901071 completed. PASS: 29 / WARN: 0 / FAIL: 17.** All 8 sections ran without error. HTML report saved to `outputs_step4/step4_validation_report.html` and retrieved locally. Section 2 (JS divergence): all 12 cycle × stratum checks PASS — JS values 0.007–0.016, well below the 0.05 threshold. Activity distribution fidelity is good. Section 5 (co-presence): all 10 checks PASS. Section 4.1 (night sleep rate): PASS. The 17 FAILs break into four groups: **(1) AT_HOME bias (§3, 12 FAILs)** — synthetic AT_HOME rate is 12–25 pp higher than observed across every cycle × stratum combination; the threshold is 2 pp. This is the most significant finding and is directly relevant to BEM because AT_HOME drives occupancy schedules. **(2) Transition rate (§4.2, 1 FAIL)** — synthetic diaries switch activity ~2.5× more often than observed (`|ratio−1|×100 = 153`; threshold 20). The transformer generates "chatty" sequences with many single-slot bouts. Slot-level marginals are still correct (§2 PASS), so impact on aggregate occupancy schedules is limited. **(3) Work peak and per-respondent ordering (§4.3 + §7.1, 2 FAILs)** — work rate during peak hours (slots 9–20) is 18.9 pp below the `hetus_30min.csv` reference (threshold 3 pp); only 42.8% of respondents show the expected Weekday ≥ Sat ≥ Sun work ordering (threshold 90%). **(4) Employment conditioning (§6.2, 1 FAIL) + training convergence (§1.2, 1 FAIL)** — synthetic employed respondents do not have more work slots than NILF; val JS did not improve for ≥20 epochs before early stopping. **BEM impact assessment:** AT_HOME bias (§3) is the blocking issue — a 12–25 pp systematic offset in at-home rate will propagate directly into EnergyPlus occupancy schedules. Next step: investigate root cause of AT_HOME bias (generated directly by model vs. derived post-hoc from activity). <br><br> **04F result summary** <br> \| Section \| Checks \| PASS \| FAIL \| Key finding \| \|---------|--------|------|------|-------------\| \| §1 Training curves \| 4 \| 3 \| 1 \| Val JS plateau before 20-epoch improvement \| \| §2 JS divergence \| 13 \| 13 \| 0 \| All cycle × stratum JS < 0.016 ✓ \| \| §3 AT_HOME rate \| 12 \| 0 \| 12 \| Synthetic 12–25 pp higher than observed (blocker) \| \| §4 Temporal structure \| 3 \| 1 \| 2 \| Transition rate 2.5× obs; work peak 18.9 pp gap \| \| §5 Co-presence \| 10 \| 10 \| 0 \| All binary range checks pass ✓ \| \| §6 Demographic conditioning \| 2 \| 1 \| 1 \| Age correlation r=0.92 ✓; LFTAG work separation fails \| \| §7 Cross-stratum consistency \| 2 \| 1 \| 1 \| Weekend AT_HOME ≥ weekday 84% ✓; work ordering 43% ✗ \| \| §8 Summary \| — \| — \| — \| Auto-generated from above \| | COMPLETE |
| 2026-04-21 | **Inference job 901068 + diagnostic job 901069 confirmed Work suppression largely resolved.** Inference (job 901068) regenerated augmented_diaries.csv (192183 rows, 545 cols). Diagnostic (job 901069, check_04E_output.py Section 2b) per-stratum results: Weekday Work obs 16.5% → syn 12.3% (gap 4.2pp, was 12.6pp — below 5pp LARGE DIFF threshold); Saturday Work obs 5.9% → syn 2.8% (gap 3.1pp); Sunday Work obs 5.0% → syn 3.0% (gap 2.0pp). Recreation remains inflated ~6–7pp across all strata (no Recreation penalty applied). AT_HOME consistency: 0 violations (perfect). Work temporal pattern: correct peak 08:00–14:00. Section 2 overall Work flag (13.3% obs → 4.2% syn) is a strata-imbalance artifact — per-stratum is the valid comparison. **Decision: proceed to 04F validation.** All per-stratum Work gaps < 5pp, hard constraints satisfied, temporal patterns correct. <br><br> **Result: Work suppression resolved — proceed to 04F** <br> \| Stratum \| Gap before \| Gap after \| Status \| \|----------\|------------\|-----------\|-------------------\| \| Weekday \| 12.6pp \| 4.2pp \| < 5pp threshold ✓ \| \| Saturday \| 5.2pp \| 3.1pp \| < 5pp threshold ✓ \| \| Sunday \| 4.4pp \| 2.0pp \| < 5pp threshold ✓ \| | COMPLETE |

| 2026-04-21 | **Option A planned: inference-side calibration sweep (04G).** Root-cause audit of §3 AT_HOME bias (12–25 pp): confirmed AT_HOME is generated directly by `home_head` in `04B_model.py` (line 162, `nn.Linear(d_model, 1)`), thresholded at a hard 0.5 in `generate()` (line 348), and fed back autoregressively into the decoder aux input at the next slot (line 360) — so threshold choice cascades through the diary. The only post-hoc corrections in `04E_inference.py:83-102` are narrow (Sleep@night→1, Work→0). The bias is therefore a decision-boundary calibration issue, not a derivation-rule issue. §4.2 transition-rate bloat (ratio 2.5×) is governed by the activity-head sampling temperature (default 0.8). **Plan:** before committing to a retrain (Option B: stronger `cond_vec` injection, BCE `pos_weight` on home_head, possible FiLM conditioning), first sweep `(temperature × home_threshold)` on a stratified subsample. Changes made: (1) `04B_model.py::generate()` — added `home_threshold: float = 0.5` param (default preserves current behavior); (2) `04E_inference.py` — added `--home_threshold` CLI flag, forwarded through `run_inference()`; (3) new `04G_calibrate.py` — stratified subsample (150 resp × 12 buckets = 1800 resp), sweep grid T ∈ {0.5,0.6,0.7,0.8} × θ ∈ {0.50,0.55,0.60,0.65,0.70} = 20 combos, metrics match 04F definitions exactly, writes `sweep_results.csv` + `sweep_summary.txt`; (4) new `job_04G_calibrate.sh` — `pg` partition, 1 GPU, 32G, 2h wall. **Decision rule:** if calibration hits PASS thresholds (AT_HOME ≤ 2pp, transition dev ≤ 20%), re-run full 04E with winning `(T, θ)` then 04F; otherwise fall back to Option B retrain targeting the §4.3/§7.1/§6.2 conditioning failures (calibration cannot fix those). | PLANNED |
| 2026-04-21 | **Option A calibration sweep complete (job 901177) — FAILED, pivoting to Option B.** Job 901174 first attempt failed (`conda activate` silently no-op'd → fell back to system Python without CUDA → crashed at `tgt_is_causal` kwarg unsupported in old torch). Fixed `job_04G_calibrate.sh` to match the working 04D/04E pattern: drop `module load anaconda3` + `conda activate`, call `/speed-scratch/o_iseri/envs/step4/bin/python` directly, use `cuda/12.8`. Job 901177 ran clean on speed-01 (37.6s/combo × 20 = ~12.5min wall). **Result: calibration cannot fix §3.** Best combo T=0.5 θ=0.7: AT_HOME max 26.27 pp (gate 2 pp), transition dev 88% (gate 20%). Critical observation: at T=0.5, varying θ from 0.50→0.70 only moves AT_HOME mean from 18.99→18.64 pp (Δ −0.35 pp); at T=0.6, θ ∈ {0.50, 0.55, 0.60, 0.65} produce *identical* metrics (26.08 pp). This means `home_head` sigmoid outputs are saturated above 0.70 for ~75–80% of slots — no inference-time threshold can reclassify them. Per-bucket bias is uniform across all strata (every cycle × stratum +7 to +26 pp), so it's both class imbalance *and* weak conditioning. **Decision: pivot to Option B retrain.** | COMPLETE |
| 2026-04-22 | **Option B training complete (job 901180) — early-stopped with best checkpoint at epoch 1.** Ran clean on speed-01 (pg, Tesla P6, FP16). Architecture confirmed from startup log: `FiLMTransformerDecoder` with 6 × `TransformerDecoderLayer` + 6 × `FiLMLayer(Linear(112, 512))`; `d_cond_dec = 112` matches `d_cond (96) + d_cycle (13) + 3` (strata one-hot). Per-epoch trajectory: **val_JS = 0.0741 (ep1) → 0.1049 → 0.0873 → 0.1979 → 0.2111 → 0.2759 → 0.2092 → 0.2495 → 0.2106 → 0.2405 → 0.2279 (ep11, early stop, patience=10).** Auxiliary losses fell cleanly through all 11 epochs: home 0.4046 → 0.1025, marg 0.0249 → 0.0060, cop 0.3995 → 0.0971, act 2.2194 → 0.8365. `grad_norm = nan` at epoch 6 (recovered next epoch, no crash). **Best checkpoint `best_model.pt` saved after epoch 1 only** (val_JS=0.0741, 46.3 MB); `last_checkpoint.pt` holds epoch-11 state. Previous baseline preserved as `best_model_run1.pt` (44.9 MB). Wall time ~90 min (11 epochs × ~492 s). **Read:** FiLM + pos_weight + marg_loss drove aux-loss convergence, but val_JS (activity distribution metric) regressed sharply after ep1 — the conditioning push moved activity marginals off-distribution faster than home/marg improvements could compensate. Since val_JS is the checkpoint-selection metric and §3 AT_HOME is the actual BEM blocker, the epoch-1 checkpoint may still be viable if home calibration improved there. Also: the `-u` unbuffered-python flag has been added locally to `job_04D_train.sh` so future runs stream stdout to the `.out` log in real time (this run's `.out` stayed 0 bytes until the buffer flushed at job end). **Decision: run 04E + 04F on the current `best_model.pt` before planning any retrain.** If §3 AT_HOME ≤ 2 pp → ship it regardless of val_JS regression. If §3 in (2, 5] pp → run small θ sweep on new checkpoint. If §3 > 5 pp → retrain with reduced `LAMBDA_MARG` (0.5 → 0.1), peak lr halved (1e-4 → 5e-5), and a checkpoint-selection metric that combines val_JS with a home-marginal-gap term. | COMPLETE |
| 2026-04-22 | **Option B validation — 04E+04F on `best_model.pt` (epoch 1) FAILED §3 gate.** Ran 04E inference (job 901253, pg partition, Tesla P6, FP16, temperature=0.8, ~37 min) and 04F validation (job 901255, ps partition, ~7 min). **Result: PASS 29 / WARN 0 / FAIL 17** — essentially same shape as the pre-Option-B baseline (PASS 29 / FAIL 17). §3 |ΔAT_HOME| per cycle (aggregated): **2005 = 15.71, 2010 = 15.59, 2015 = 14.54, 2022 = 10.92 pp** — all well above the 5 pp retrain threshold (and 7× above the 2 pp ship threshold). FiLM + pos_weight + marg_loss did not move §3 meaningfully vs Option A baseline. Per the pre-recorded decision rule (>5 pp → retrain), this triggers a retrain. | COMPLETE |
| 2026-04-22 | **Option B validation — 04E+04F on `last_checkpoint.pt` (epoch 11) is WORSE than epoch-1.** Sanity-check: although val_JS-based selection picked epoch 1, epoch-11 had 4× lower home-BCE loss (0.1025 vs 0.4046), so ran inference+validation on it to confirm checkpoint selection wasn't the bottleneck. Created variant job `job_04E_inference_last.sh` (via sed on cluster: `best_model.pt`→`last_checkpoint.pt`, `augmented_diaries.csv`→`augmented_diaries_lastckpt.csv`, `name=04E_infer`→`name=04E_infer_last`) after one failed attempt (over-broad sed also rewrote `04E_inference.py`→`04E_infer_lastence.py`; fixed with `name=` anchor). Job 901259 ran clean (30:41). For 04F, swapped CSVs in place (backed up best as `aug_best.csv`) and re-ran `job_04F_validation.sh`; restored via rename afterward. **Result: PASS 15 / WARN 1 / FAIL 30** — overall regression vs epoch-1. §3 |ΔAT_HOME| per (cycle × stratum): 2005 Wkday 16.65 / Sat 7.97 / Sun 5.19; 2010 Wkday 15.22 / Sat 7.69 / Sun 6.08; 2015 Wkday 14.50 / Sat 3.41 / Sun 0.66 (only §3 PASS); 2022 Wkday 10.45 / Sat 5.86 / Sun 4.90 pp. Section 2 JS degraded (overall 0.0684 FAIL vs. previously ~0.015 PASS). Weekday AT_HOME gap is essentially unchanged between the two checkpoints — the problem is NOT checkpoint selection, it is systematic in the Option B training run. **Conclusion:** val_JS-based checkpoint selection was correct; over-training past epoch 1 degrades activity distribution without fixing AT_HOME. Cleaned up: renamed cluster outputs → `augmented_diaries_lastckpt.csv`, `report_lastckpt.html`; restored `augmented_diaries.csv` and `step4_validation_report.html` to point at the epoch-1 baseline. | COMPLETE |
| 2026-04-22 | **Option B retrain planned — reduced marginal-bias weight + halved LR + combined checkpoint metric.** Two validations (best + last) confirm Option B training geometry is fundamentally mis-tuned for §3: val_JS regressed immediately while home/marg auxiliary losses continued to drop — the two objectives trade off too steeply. Proposed retrain tweaks to `04D_train.py`: **(1) `LAMBDA_MARG = 0.5 → 0.1`** — weaken marginal-bias loss so it doesn't over-pull the home distribution at the cost of activity head. **(2) peak lr `1e-4 → 5e-5`** (halved) — slow the training so the balance between heads stabilizes rather than overshooting after epoch 1. **(3) Checkpoint-selection metric changed from pure val_JS → combined metric** `val_score = val_JS + 0.5 · mean_|ΔAT_HOME|` (both quantities on comparable scale after normalization); pick minimum. Rationale: val_JS alone picked epoch 1 with a huge §3 failure; pure home-gap would pick late epochs with degraded activity. Combined metric lets the two trade off. **(4) Early-stopping patience 10 → 15** — give the combined metric room to find a better local minimum. **Retain:** FiLM conditioning, BCE `pos_weight` on home_head (these did not harm), FP16, `-u` stdout flag, `temperature=0.8` in 04E. **Pre-retrain cleanup on cluster:** delete old `checkpoints/best_model.pt`, `last_checkpoint.pt`, `best_model_run1.pt`; old `augmented_diaries.csv`, `augmented_diaries_lastckpt.csv`; old validation reports; old `calibration/` dir (Option A abandoned); old `step4_training_log.csv`. **Keep:** `step4_{train,val,test}.pt`, all `*_meta.csv`, `step4_feature_config.json`, `training_pairs.pt`, `val_pairs.pt` (inputs reusable). After retrain: 04E → 04F → apply same decision rule (≤2 pp ship / 2–5 pp θ sweep / >5 pp escalate further). | PLANNED |

| 2026-04-22 | **Option B retrain executed (job 901267) — val_score-selected checkpoint regressed further on §3. STUCK.** Cleaned cluster per 2026-04-22 plan (deleted old checkpoints / augmented CSVs / reports / calibration dir), applied `LAMBDA_MARG = 0.5 → 0.1`, peak lr `1e-4 → 5e-5`, patience `10 → 15`, and combined checkpoint metric `val_score = val_JS + 0.5·mean_|ΔAT_HOME|`. Train job 901267: COMPLETED 00:41:35, early-stopped (§1.2 "Val JS improves for ≥20 epochs before plateau" = 4 epochs → FAIL — combined-metric triggered stop much earlier than pure val_JS). Inference job 901321: COMPLETED 00:29:55, `augmented_diaries.csv` 222 MB. Validation job 901370: **PASS 25 / WARN 2 / FAIL 19** — *worse* than the epoch-1 Option-B baseline (29/17). §3 |ΔAT_HOME| per (cycle × stratum): 2005 Wkday 21.07 / Sat 16.62 / Sun 14.21; 2010 Wkday 20.49 / Sat 16.35 / Sun 14.99; 2015 Wkday 17.46 / Sat 13.70 / Sun 10.91; 2022 Wkday 22.86 / Sat 12.71 / Sun 11.07 pp — uniformly worse than the epoch-1 Option-B baseline (10.92–15.71 pp). §4.2 transition-rate ratio 159.77 (gate 20). §4.3 work-peak delta 5.91 pp (FAIL). §7.1 work ordering 43.21%, §7.4 weekend AT_HOME ≥ weekday 45.09% (FAIL). **Pre-retrain best checkpoint was overwritten** (no `archive/` backup); `best_model.pt` timestamp Apr 22 11:38 is the retrained model. Revert-in-place unavailable. **Status: STUCK — neither Option A (calibration) nor two Option-B tunings have closed §3. Need a structured investigation before any further GPU time.** HTML reports retained locally as `step4_validation_report_v2.html` (pre-retrain, 29/17) and `step4_validation_report_v3.html` (this run, 25/19); next download → `_v4`. | COMPLETE |
| 2026-04-23 | **Sign-flip fix CONFIRMED — disabled BCE `pos_weight` on `home_head`; retrain + inference + validation + diagnostics complete.** Root cause of the monotonic §3 worsening across Option A → two Option B runs: the `pos_weight = (1 − obs_home_rate) / obs_home_rate` computed in job 901180 evaluates to ~0.38 (since `obs_home_rate ≈ 0.725`), which *down-weights* the positive class — the opposite of what we wanted. Combined with the already-saturated `home_head` sigmoid (Option A finding), this pushed the distribution further from observed on each retrain. **Fix applied to `04D_train.py`:** pos_weight disabled (pass `pos_weight=None` to `F.binary_cross_entropy_with_logits`); `LAMBDA_MARG` retained at 0.1 as a direction-agnostic marginal-gap guard; FiLM conditioning retained. Jobs: retrain **901399** (`pg`, Tesla P6, FP16) → inference **901476** → validation **901563** (`ps`) → diagnostics **901564** (`ps`, new CPU-only 04H script `04H_diagnostics_cpu.py` + `job_04H_diagnostics.sh`). **04H result: all four hypotheses resolved.** H1 `H1_rejected` (pair-target AT_HOME vs population gap 2.43 pp — clean). **H2 flipped from `H2_dominant` → `H2_rejected`.** H3 `H3_not_dominant` (afternoon_evening-to-morning gap ratio 0.66). H5 `H5_rejected` (T6 all `implausible=false`, night AT_HOME 0.88–0.94 across every cycle × stratum, all under 0.95 threshold). Recommendation: **`SKIP_GPU`** — no further retrain indicated. **T3 overall:** midday mean gap **−27.8 pp (pre-fix) → +4.08 pp (v4)**, max_gap **−40.9 → +11.41 pp** at slot 34 (evening), slot-of-max moved from morning saturation-low to evening mild overshoot. **04F result: PASS 28 / WARN 1 / FAIL 17** (vs pre-fix 29/17 — total FAIL count unchanged but §3 composition now dominated by the new stratum-split pattern, not uniform inflation). **Artefacts:** `outputs_step4/diagnostics_v4.json` + `diagnostics_v4_trajectories.png` downloaded locally OK. **HTML report broken on cluster:** `outputs_step4/step4_validation_report.html` (33950 B, Apr 23 05:28) is byte-identical in size to `diagnostics_v4.json` (33950 B, 05:22) and contains JSON content, not HTML — some post-04F step clobbered the file. Needs re-run of 04F to regenerate; root cause of clobber not yet diagnosed. **Residual issue (new, out of scope for sign-flip fix): stratum-conditional AT_HOME bias.** T2/T3 per-cycle gaps split cleanly along stratum axis — **stratum 1 (weekday):** synthetic **under-predicts** at_home by 5–14 pp (midday gap −7 to −14); **strata 2/3 (weekend):** synthetic **over-predicts** by 3–8 pp (midday gap up to +23 at slot 34). Overall means near zero because directions cancel. Trajectory PNG confirms visually. Points to `cond_vec`/FiLM path — matches pre-existing §4.3/§7.1/§6.2 failure modes Option A could not repair. **Next steps:** (1) regenerate + re-pull the real HTML report (resubmit 04F); (2) audit remaining un-validated output channels — **co-presence** (9-way BCE head) and **activity distribution** (14-way CE head) per cycle × stratum; (3) address stratum-conditional bias via stronger `cond_vec`/FiLM injection (separate workstream). | COMPLETE |
| 2026-04-23 | **04I activity + co-presence diagnostic run — both heads FAIL; co-presence mode collapse confirmed.** Created `04I_activity_copresence_diagnostics.py` + `job_04I_diagnostics.sh` (`ps` partition, 8G, 4c, 30min) to audit the 14-way activity head (JS divergence, per-cycle × stratum) and 7-way co-presence head (prevalence gap in pp, per channel and per cycle × stratum). **Two bugs found and fixed during run cycle:** (1) `COP_NAMES` was 9 entries (included `otherInFAMs`, `otherHHs` which do not exist in any frame) — corrected to 7: `[Alone, Spouse, Children, parents, friends, others, colleagues]`; (2) `run_copresence()` was reading co-presence prevalences from `copresence_30min.csv` or `hetus_30min.csv`, neither of which carries `*30_001..048` COP columns — only `augmented_diaries.csv` does. Fix: `run_copresence()` now accepts `aug=` parameter and uses `aug[IS_SYNTHETIC==0]` as the observed source; the earlier frames are fallback only. PNG-write gated on non-empty `per_channel` dict to prevent a silent skip being logged as a write. Job 901568 ran on cluster; artefacts downloaded: `outputs_step4/diagnostics_v4_actcop.json` (31 KB), `diagnostics_v4_activity.png` (80 KB), `diagnostics_v4_copresence.png` (42 KB). Downloaded `.out` log (`04I_901568.out`) is the pre-patch run (shows stale `copresence_ok max_gap_pp=0.0`); JSON + PNGs reflect the patched post-fix run. **Activity result: `activity_fail`** — overall JS mean 0.0559 (gate 0.05), 10 / 12 cycle × stratum cells FAIL, 2 WARN. Code 1 (home/personal care) nearly doubles obs on all weekdays (~+15 pp); code 10 (recreation) under-predicted on weekdays. 2022 weekend cells are the best (JS 0.034–0.038). **Co-presence result: `copresence_fail`** — 6 / 7 channels FAIL. `Alone` +17.4 pp (syn over-predicts), `Spouse` −19.0 pp (under-predicts); `Children`, `parents`, `friends`, `others`, `colleagues` all syn ≈ 0 (max_gap_pp across these five > 3 pp gate). Visual inspection of `diagnostics_v4_copresence.png` confirms mode collapse: only Alone and Spouse have visible bars; all other channels are flat zero. Root cause candidates: inference-time hard threshold (`σ > 0.5`) collapsing rare-positive BCE outputs, or BCE training without sufficient positive-class weighting on minority co-presence channels. **Next step: inspect augmenter/inference scripts for hard threshold or column-zero writes on COP channels to determine whether collapse is at inference time (fixable without retrain) or in the trained weights (requires retrain with `pos_weight` per COP channel).** | COMPLETE |
| 2026-04-21 | **Option B implemented: FiLM decoder conditioning + AT_HOME pos_weight + marginal-bias loss.** Three architecture/loss changes targeting both §3 (AT_HOME saturation, confirmed by job 901177) and the §4.3/§7.1/§6.2 weak-conditioning failures. Changes: **(1) `04B_model.py` — FiLM conditioning per decoder layer.** New `FiLMLayer` (zero-init → identity at start, `x → (1+γ)·x + β`) and `FiLMTransformerDecoder` (drop-in for `nn.TransformerDecoder`, plus per-layer FiLM, drops `tgt_is_causal` kwarg for cross-PyTorch-version safety). FiLM input vector: `[cond_vec ∥ cycle_emb ∥ strata_oh]` of size `d_cond + d_cycle + 3`. `decode()` and `generate()` updated to build this `dec_cond` once and pass to the decoder; `forward()` plumbs `cond_vec, cycle_idx` from batch. The original additive `strata_emb` injection (line 241/242 path) is preserved alongside FiLM. **(2) `04D_train.py` — BCE `pos_weight` on `home_head`.** Compute `obs_home_rate = train_data["aux_seq"][:, :, 0].float().mean()` once at startup, derive `pos_weight = (1 − obs_home_rate) / obs_home_rate`, pass into `F.binary_cross_entropy_with_logits` via `compute_loss(home_pos_weight=...)`. Down-weights the positive class to counter the saturation. **(3) `04D_train.py` — marginal-bias loss term.** New `LAMBDA_MARG = 0.5`; `marg_loss = |sigmoid(home_logits).mean() − home_tgt.mean()|` per batch, added to total loss. Direct counter to §3 over-prediction; logged to console + `step4_training_log.csv` as `marg_loss` column. **Important: do not use `--resume` for this retrain** — the FiLM modules don't exist in any prior checkpoint, so train from scratch. Same `job_04D_train.sh` as job 901055; expected wall-time similar (~6–8h on Tesla P6). After the retrain finishes: re-run 04E (no `--home_threshold` needed, leave default 0.5) → 04F. **Decision rule:** if 04F §3 still fails by >5 pp, the conditioning is the real issue (FiLM didn't help enough) — escalate to investigating training-pair sampling; if §3 lands in (2, 5] pp, run a small θ sweep on the new checkpoint. | PLANNED |
| 2026-04-23 | **F3 sweep plan + §9/§10 doc appended to `step4_training.md`. Activity code-1 identity resolved.** Task 0a confirmed activity code 1 (raw) = "Work & Related" (paid work) from `04E_inference.py:55` comment (`WORK_CAT = 0  # raw category 1 = Work & Related`) and `04D_train.py:381` comment (`# Work (idx 0): weekday obs 16.5% → syn 3.9% → 5x`). `step4_feature_config.json` carries no label map — labels live in code comments only. **F1 manual Work ×5 boost is confirmed prime suspect for the 14–15 pp weekday over-production.** F3-A removing the boost is well-motivated. Plan file `staged-singing-swing.md` patched to remove the code-1 ambiguity note. Three additions appended to `step4_training.md` (nothing above §8.10 modified): (1) new §8.10 Progress Log entry capturing `diagnostics_v4_actcop.json` F-COP-1a verdict (Alone +16.1 pp dominant, 5/7 channels fail, activity 10/12 cells fail) and the F3 decision; (2) new §9 — F3 hyper-parameter sweep (5 configs: F3-A baseline_balanced_bce, F3-B +stratum_marg, F3-C +aux_stratum_head, F3-D +data_side_sampling, F3-E inference-only sweep; exact file:line change specs; sweep infrastructure spec; go/no-go gates; risks); (3) new §10 — 04J statistical diagnostics spec (5 tests: bootstrap CIs, calibration curves, joint distributions, χ²/KS, composite score; composite score formula with pinned weights w1=0.20, w2=0.35, w3=0.35, w4=0.10; CLI contract; dry-run gate). | COMPLETE |
| 2026-04-23 | **Task 1 dry-run gate PASSED (job 901974, COMPLETED 00:01:23). F1 baseline composite score = 1.045.** Fixed memory error in T1 bootstrap (3M-row flatten OOM) by switching to per-respondent row-means before resampling. Gate check: Alone calibration σ̄=0.553 bin → empirical prevalence 0.321 (plan expected 0.51/0.35 approx; spread across all 10 bins confirms F-COP-1a soft σ are being read correctly, not hard 0/1). Key findings: Alone +16.1 pp CI [+15.8, +16.3], Spouse +6.5 pp, colleagues −4.8 pp, AT_HOME +5.3 pp (all statistically real); activity JS mean 0.056; alone KS 0.55–0.79 across all strata; AT_HOME calibration degenerate (all values in σ=0.0 bin — AT_HOME was not updated to soft output in F-COP-1a, calibration is meaningless for that head). **GATE: PASS. Task 2 authorized.** | COMPLETE |
| 2026-04-23 | **Task 2: `04A`, `04B`, `04C`, `04D` edited for F3-A/B/C/D env-flag-gated configs.** `04A`: added COP pos_weight computation (7 usable channels, `assert pw>1` sign-flip guard) and 14-way activity class freqs; both saved to `step4_feature_config.json`. `04C`: added `np.save` for `strata_inv_freq.npy` in main(). `04D`: (1) LAMBDA_* and MARG_MODE now read from env vars (defaults = F1 values, zero behavior change under default env); (2) `compute_loss` accepts `cop_pos_weight` and optional `aux_logits`; (3) per-CS marg_loss gated by `MARG_MODE=per_cs`; (4) COP BCE pos_weight gated by `COP_POS_WEIGHT=1`; (5) activity boosts gated by `ACTIVITY_BOOSTS=0`; (6) `DATA_SIDE_SAMPLING=1` multiplies sampler weights by WGHT_PER; (7) `AUX_STRATUM_HEAD=1` wired into model_config. `04B`: `FiLMTransformerDecoder.forward()` now returns `(final_output, layer0_hidden)` tuple; optional `aux_strata_head` MLP on decoder layer-0 mean-pool, gated by `config["aux_stratum_head"]`; `decode()` and `generate()` updated. All default env = F1 config. | COMPLETE |
| 2026-04-23 | **Task 3: F3 sweep infrastructure created — 6 new scripts, `bash -n` PASS on all.** New files: `Speed_Cluster/job_04D_train_F3{A,B,C,D}.sh` (4 training job scripts, each sets env vars for its config and calls `04D_train.py --data_dir outputs_step4 --output_dir outputs_step4_F3X --checkpoint_dir outputs_step4_F3X/checkpoints --fp16`); `Speed_Cluster/job_04Z_F3_compare.sh` (CPU `ps` job, 4G, 15min, calls `04Z_F3_compare.py` with 5 JSON paths + `--out_dir deliveries/F3_sweep/${CHAIN_TAG}`); `Speed_Cluster/submit_step4_F3_sweep.sh` (orchestrator: submits 4 parallel retrain chains, each `04D → 04E → {04F, 04H, 04I, 04J}` with `afterok` dependencies, then 04Z with `afterok` on all 4 terminal 04J JIDs); `04Z_F3_compare.py` (reads F1 + F3-A/B/C/D statistical JSON, extracts composite_score + key gaps, ranks by composite ascending, writes `F3_sweep_ranking.md` + `F3_sweep_comparison.html` + `F3_sweep_results.json`). Env-var mapping: F3-A `COP_POS_WEIGHT=1 ACTIVITY_BOOSTS=0`; F3-B adds `MARG_MODE=per_cs`; F3-C adds `AUX_STRATUM_HEAD=1`; F3-D adds `DATA_SIDE_SAMPLING=1`. All configs isolate checkpoints/outputs under per-config dirs to avoid Option-B-v2 clobber. `bash -n` passed on all 6 scripts. **PRE-FLIGHT before Task 4 submit: copy F1 `best_model.pt` to `deliveries/F1_baseline/checkpoints/best_model.pt` on cluster.** | COMPLETE |
| 2026-04-23 | **Task 1: `04J_statistical_diagnostics.py` + `job_04J_diagnostics.sh` created.** New CPU-only diagnostic script implementing T1 (bootstrap CIs, 1000 resamples, per COP channel + AT_HOME), T2 (matched calibration curves — synthetic σ joined to observed binary via occID × CYCLE_YEAR, 10-bin reliability diagram, MAE per channel), T3 (joint distributions: activity × AT_HOME, activity × Alone, Alone × AT_HOME; χ² + Cramér V for obs and syn), T4 (χ² on activity counts + KS on AT_HOME/Alone sigma per cycle × stratum, Bonferroni-corrected α), T5 (composite score S = w1·AT_HOME_gap_rms/10 + w2·cop_max_gap_pp/10 + w3·act_JS·10 + w4·cop_cal_MAE·10, weights 0.20/0.35/0.35/0.10). Job script: `ps` partition, 8G, 4 cores, 30min, mirrors `job_04I_diagnostics.sh`. Output: `diagnostics_v4_statistical.json` + `_bootstrap.png`, `_calibration.png`, `_joints.png`. **DRY-RUN GATE: upload files to cluster and submit to validate on F1 `augmented_diaries.csv` before any F3 retrain.** | COMPLETE |
| 2026-04-24 | **F3 sweep first submission failed (04D arity bug) — fixed and resubmitted; sweep now running (tag `F3_sweep_20260424_1635`).** Initial 4 × 04D jobs (902739/902745/902751/902757) all FAILED 1:0 within 1–7 minutes with `ValueError: too many values to unpack (expected 3)` at `04D_train.py:297` (`validate()`) and also latent in `04G_calibrate.py:193` (`generate_syn_for_subsample()`). Root cause: `model.generate()` returns 4 values `(gen_act, gen_home, gen_cops, gen_cop_probs)` after the co-presence head was added, but both call sites only unpacked 3. `04E_inference.py:158` was already correct (4-value unpack). **Fix:** `04D_train.py:297` — `gen_act, gen_home, _ = model.generate(...)` → `gen_act, gen_home, _, __ = model.generate(...)`; `04G_calibrate.py:193` — `gen_act, gen_home, _gen_cop = model.generate(...)` → `gen_act, gen_home, _gen_cop, _gen_cop_probs = model.generate(...)`. All 21 pending 04E/04F/04H/04I/04J/04Z jobs had `DependencyNeverSatisfied` status (permanent once parent fails) and were cancelled. Fixed files uploaded and sweep resubmitted via `submit_step4_F3_sweep.sh`. **New job IDs:** `04D_F3A` 902821 (cisr-1), `04D_F3B` 902827 (cisr-2), `04D_F3C` 902833 (speed-01), `04D_F3D` 902839 (speed-01) — all `R` on GPU compute nodes, full downstream chain pending `afterok` dependency (no `DependencyNeverSatisfied`). All compute runs on dedicated GPU worker nodes in `/speed-scratch`; login node (`speed-submit2`) used for `sbatch` only — no policy violation. **Next:** wait for 04D jobs to complete (~6–18 h), full chain fires automatically (04D → 04E → {04F, 04H, 04I, 04J} → 04Z). When queue empties, pull `deliveries/F3_sweep/F3_sweep_20260424_1635/` and review `F3_sweep_ranking.md` — any config with composite score < 1.045 beats the F1 baseline. | IN PROGRESS |
| 2026-04-24 | **F3 sweep COMPLETE — F1 remains best (composite 1.045); F3-C closest challenger; `04Z_F3_compare.py` key-mismatch bug fixed.** All 20 jobs (902892–902912) completed cleanly. `04Z` (902912) ran but produced all-NaN scores due to 5 key-name mismatches in `04Z_F3_compare.py:extract_metrics()`: (1) `d.get("composite_score")` → `d["composite"]["composite_score"]`; (2) `bootstrap_cis.get("AT_HOME")` → `bootstrap_cis["at_home"]`; (3) `at_home.get("mean_gap_pp")` → `at_home["gap_pp"]`; (4) `at_home.get("ci_lo/ci_hi")` → `at_home["gap_ci_lo/hi_pp"]`; (5) `bootstrap_cis.get("activity")` → `d["composite"]["components"]["act_js_mean"]`; (6) `cal.get("MAE")` → `cal["mae"]`. Fix applied locally, script re-uploaded, 04Z re-run interactively on cluster. **Final ranking (composite lower=better, gate 1.045):** (1) F1 1.045 AT_HOME +5.3 pp Alone +16.1 pp JS 0.056 — 0/7 pass; (2) F3-C 2.366 AT_HOME +5.8 pp Alone +13.3 pp JS 0.041 — 1/7 pass (JS now passes ≤0.05 threshold); (3) F3-D 2.425 AT_HOME +16.7 pp Alone +14.3 pp JS 0.028 — 1/7 pass; (4) F3-A 2.460 AT_HOME +18.6 pp Alone +23.6 pp JS 0.024 — 1/7 pass; (5) F3-B 2.478 AT_HOME +21.6 pp Alone +26.3 pp JS 0.025 — 1/7 pass. **F1 is still WINNER.** F3-C (aux_stratum_head) is the best F3: JS improved 0.056→0.041 and Alone gap reduced 16.1→13.3 pp, but composite still 2.3× F1 due to Alone gap dominating w2=0.35 term. F3-A/B (balanced BCE) caused large AT_HOME regressions (18–22 pp) — removing the manual activity boosts without the aux stratum head over-corrects. F3-D improved JS most (0.028) but AT_HOME blew out to 16.7 pp. **No F3 config beats F1.** F3-C partial gains (JS + Alone) suggest the `aux_stratum_head` direction is worth continuing, but a full co-presence re-architecture is needed to close the Alone +13 pp gap. | COMPLETE |
| 2026-04-24 | **F4 retrain planned — F3-C base + disable Alone pos_weight (sign-flip fix).** Root cause of Alone +13.3 pp residual in F3-C: `cop_pos_weights["Alone"]` ≈ 1.86 (freq ≈ 0.35, formula `(1-freq)/freq`) upweights Alone=1 training examples, worsening an already over-predicted channel — same sign-flip mechanism as the AT_HOME pos_weight fix. F3-C's `COP_POS_WEIGHT=1` was applying this weight throughout the F3 sweep, but Alone remained the composite's dominant penalty term (w2=0.35 × cop_max_gap_pp/10 accounts for most of the 2.366 composite). **Fix:** new `COP_ALONE_PW` env var in `04D_train.py` (default `1` = use feature-config weight; `0` = override Alone to 1.0). Sign-flip guard assert relaxed to exclude Alone when `COP_ALONE_PW=0`. All other channels (Spouse, Children, parents, friends, others, colleagues) retain computed pos_weights. **New files:** `Speed_Cluster/job_04D_train_F4.sh` (F3-C env vars + `COP_ALONE_PW=0`), `Speed_Cluster/submit_step4_F4_retrain.sh` (single-chain `04D→04E→{04F,04H,04I,04J}`, outputs to `outputs_step4_F4/`). **Submit gate:** upload `04D_train.py`, `job_04D_train_F4.sh`, `submit_step4_F4_retrain.sh` to cluster, then `bash submit_step4_F4_retrain.sh F4_retrain_YYYYMMDD_HHMM`. **Comparison gate:** pull `outputs_step4_F4/diagnostics_v4_statistical.json`; composite < 2.366 and Alone gap < 13.3 pp = improvement over F3-C. **Job IDs (tag F4_retrain_20260424_2004):** 04D 902983 → 04E 902984 → {04F 902985, 04H 902986, 04I 902987, 04J 902988}. | IN PROGRESS |
| 2026-04-24 | **F4 first attempt (jobs 902983–902988) FAILED — same 3-value unpack bug as F3 sweep first submission.** 04D job 902983 failed within seconds with `ValueError: too many values to unpack (expected 3)` at `04D_train.py:266` (`validate()`). Root cause: the cluster copy of `04D_train.py` still had the old 3-value unpack `gen_act, gen_home, _ = model.generate(...)` at `validate()`, not the corrected 4-value unpack added for the F3 sweep fix. The local file (line 297) already had the correct `gen_act, gen_home, _, __ = model.generate(...)`. All 5 downstream jobs (902984–902988) went to `DependencyNeverSatisfied`. **Fix:** re-uploaded the correct local `04D_train.py` to the cluster, cancelled jobs 902984–902988, resubmitted chain as new tag `F4_retrain_20260425` — 04D job 903458, 04E 903459, {04F 903460, 04H 903461, 04I 903462, 04J 903463}. | COMPLETE |
| 2026-04-25 | **F4 second attempt (jobs 903458–903463) COMPLETE but INVALID — best checkpoint is epoch 1 (untrained model); pivoting to F5.** All 6 jobs completed (04D exit 0:0, 00:12:11; 04E 0:0, 00:09:34; 04F FAILED 2:0 as expected; 04H/04I/04J all 0:0). `diagnostics_v4_statistical.json` (18 KB) pulled locally. **Gate check:** composite 2.3564 < 2.366 (PASS, margin 0.010); Alone gap 9.9 pp < 13.3 pp (PASS). **However, training log reveals the run is invalid.** 04D log shows: epoch 1 produced `NaN gradient + grad_norm=inf` → PyTorch AMP GradScaler skipped the optimizer update; best model saved at epoch 1 val_score=0.1129; every subsequent epoch (2–16) had higher val_score; early stopping fired at epoch 16 (patience=15). **The saved `best_model.pt` is therefore from an epoch where the model weights were never updated — essentially random initialization.** The "passing" gate scores are artefacts of a random-weight model, not a learned one. **Root cause of NaN:** FP16 overflow from the large cop pos_weights on rare channels — parents 40.77×, friends 15.17×, children 10.99×, colleagues 12.26× — these cause BCE loss overflow in the first backward pass. Same sign-flip over-weighting pattern as AT_HOME and Alone, but more extreme for rare channels. **Symptom in diagnostics:** non-Alone cop channels all predict ~50% (Spouse +34.7 pp, Children +41.4 pp, parents +47.7 pp, friends +48.0 pp) — consistent with a random-weight model outputting uniform predictions. Alone improved (9.9 pp) only because Alone's pos_weight was disabled (COP_ALONE_PW=0), while all other channels retained their inflated weights. AT_HOME calibration fully degenerate (all 1.17M predictions in σ≈0 bin, MAE 0.441). **Decision: F4 INVALID. Pivoting to F5.** F5 = F3-C base + `COP_POS_WEIGHT=0` (disable ALL cop pos_weights). Rationale: F1 (the current best, composite 1.045) used `COP_POS_WEIGHT=0`; the large rare-channel weights cause FP16 NaN in any config that enables them; disabling all weights removes the overflow risk and aligns with the proven F1 direction while keeping F3-C's structural improvements (AUX_STRATUM_HEAD=1, MARG_MODE=per_cs, ACTIVITY_BOOSTS=0). | COMPLETE |
| 2026-04-24 | **F3 sweep second failure (04E wrong `--data_dir`) — root cause diagnosed, submit script fixed, recovery script created, 17 jobs cancelled, chains re-submitted.** `04D_F3A` (902821, cisr-1) and `04D_F3B` (902827, cisr-2) both COMPLETED successfully (exit 0:0, ~40 min). Their downstream `04E_F3A` (902822) and `04E_F3B` (902828) then failed in 5 seconds with `FileNotFoundError: outputs_step4_F3A/step4_train.pt`. **Root cause:** `submit_step4_F3_sweep.sh:70` passed `--data_dir ${OUT_DIR}` (e.g. `outputs_step4_F3A`) to `04E_inference.py`. But `04E` uses `data_dir` to load the preprocessed tensor files (`step4_train.pt`, `step4_val.pt`, `step4_test.pt`) which live in the shared `outputs_step4/` directory — the per-config output dirs only contain `checkpoints/` and `step4_training_log.csv`. The same failure would have hit F3C and F3D when their 04D jobs finished. **Fix:** changed `submit_step4_F3_sweep.sh:70` from `--data_dir ${OUT_DIR}` → `--data_dir outputs_step4`. **Recovery:** created `Speed_Cluster/resume_04E_F3_sweep.sh` — submits corrected 04E→{04F,04H,04I,04J}→04Z chains for all 4 configs (F3A/B immediately since 04D is done; F3C/D with `afterok:902833`/`afterok:902839` since 04D is still running). Cancelled all 17 bad pending jobs (F3A/B downstream `DependencyNeverSatisfied`: 902823–902826, 902829–902832; F3C/D wrong-data_dir pending: 902834–902838, 902840–902844; 04Z: 902845). **Next:** upload fixed `submit_step4_F3_sweep.sh` + new `resume_04E_F3_sweep.sh` to cluster, cancel the 17 jobs, run `bash resume_04E_F3_sweep.sh F3_sweep_20260424_1635`. F3C/D 04D still running — recovery script chains 04E off those job IDs automatically. | COMPLETE |
| 2026-04-25 | **F5 retrain (job 903501) COMPLETE but INVALID — same early-stopping trap as F4, one residual NaN gradient with fp16.** Config: F3-C base + `COP_POS_WEIGHT=0` (all cop pos_weights disabled), same as F1 direction but keeping AUX_STRATUM_HEAD=1, MARG_MODE=per_cs, ACTIVITY_BOOSTS=0. Chain submitted via `submit_step4_F5_retrain.sh`; outputs to `outputs_step4_F5/`. **Training log (04D job 903501) shows:** `WARN: 215 params have zero gradient` and `FAIL: 1 params have NaN gradient`, `grad_norm=inf` at epoch 1. AMP GradScaler skipped the optimizer step; epoch 1 val_score=0.1831 saved as best. Epochs 2–16 ranged 0.2041–0.3921 (all worse). Early stopping fired at epoch 16 (patience=15). `best_model.pt` = random-initialization weights (never updated). **The one residual NaN param survives with `COP_POS_WEIGHT=0`** — the cop pos_weight overflow was the dominant FP16 failure mode in F4, but a secondary NaN source persists. Candidates: FP16 overflow in the forward pass with random-init weights, or `log(0)` in per_cs marginal loss computation. **F5 is INVALID: same trap as F4.** 04F/04H/04I/04J chain completed and diagnostics were pulled, but results are artefacts of a random-weight model — not representative. AT_HOME calibration anomaly in 04J output: σ≈0 for all 469,239 predictions (home_head not outputting meaningful probabilities). | COMPLETE |
| 2026-04-25 | **F6 retrain submitted (jobs 903599–903604) — fp32 only, eliminates FP16 as NaN source.** Config: F3-C + `COP_POS_WEIGHT=0` + fp32 (no `--fp16` flag). New job script `job_04D_train_F6.sh` and chain script `submit_step4_F6_retrain.sh` created. Chain: `04D_F6` (903599) → `04E_F6` (903600) → parallel `{04F_F6` (903601), `04H_F6` (903602), `04I_F6` (903603), `04J_F6` (903604)}. Outputs to `outputs_step4_F6/`. **Rationale:** fp32 eliminates FP16 overflow as a failure mode. If epoch 1 still shows NaN at fp32, the source is logic-level (`log(0)` in per_cs marg loss) and requires a code fix in `04D_train.py`. If clean, F6 is a valid training run. fp32 is ~2× slower than fp16 but fits within the 2-day SBATCH wall limit. **Epoch 1 check:** confirm no `FAIL: NaN gradient` and finite `grad_norm` in `logs/04D_F6_903599.out`. Gates: composite < 2.366 AND Alone gap < 13.3 pp (beat F3-C baseline). Stretch: composite < 1.045 (beat F1). | IN PROGRESS |
| 2026-04-25 | **F6 COMPLETE but INVALID — fp32 eliminated NaN but warmup-induced early-stopping trap fired.** 04D job 903599 completed. fp32 cleared the gradient NaN (no `FAIL: NaN gradient` in the log). However a new trap emerged: at epoch 1 the LR is 8.77e-06 (17.5% of peak 5e-05, deep into the linear warmup schedule) → model makes near-uniform predictions → val_JS=0.0866, combined val_score=0.1844 saved as best. Epochs 2–16 val_score ranged 0.2082–0.3915 — never beat 0.1844. Early stopping fired at epoch 16 (patience=15). `best_model.pt` = epoch 1 near-uniform weights. **Root cause:** `04D_train.py` only gated the patience counter (early-stop) on `past_warmup`, but the best-model save block had no such gate — so epoch 1's artificially low val_score was written as best and blocked all real training. Same structural trap as F4/F5, different mechanism. **F6 is INVALID. Decision: apply warmup-gate fix in F7.** Fix: gate both best-model saving AND patience counter on `past_warmup = (epoch+1) > warmup_epochs` (warmup_epochs ≈ 6 for ~350 batches/epoch). | COMPLETE |
| 2026-04-26 | **F8 COMPLETE — hard gates FAIL; key isolation finding: AUX_STRATUM_HEAD=1 dramatically fixes AT_HOME but causes Spouse explosion.** Chain jobs 904149–904154 completed. `diagnostics_v4_statistical.json` pulled from `outputs_step4_F8/`. **Gate evaluation:** composite 1.376 > 1.045 ✗ FAIL; AT_HOME mean gap +1.41 pp ≤ +5.3 pp ✅ PASS; Spouse gap +19.36 pp > +5 pp ✗ FAIL. **Key metrics (bootstrap CIs):** AT_HOME gap +1.41 pp [+1.14, +1.68] (obs 72.5%, syn 73.9%) — best AT_HOME result in the entire sweep, better even than F1 (+5.3 pp); Alone gap +13.52 pp [+13.12, +13.89]; Spouse gap +19.36 pp [+18.93, +19.76] (obs 22.4%, syn 41.7%); act_JS 0.0657; cop_cal_MAE 0.330; AT_HOME_rms 6.90 pp. **Composite components:** AT_HOME_rms 6.90 pp → 0.138, cop_max_gap 19.36 pp → 0.677, act_JS 0.0657 → 0.230, cop_cal_MAE 0.330 → 0.330. **Diagnostic interpretation (per gate logic):** AT_HOME ≤ 6 pp ✅ → AUX_STRATUM_HEAD is safe for AT_HOME. Spouse NOT small ✗ → F9 cannot simply stack MARG_MODE=per_cs. **Isolation finding (F8 = F1 + AUX_STRATUM_HEAD=1 only):** AUX_STRATUM_HEAD=1 singularly causes AT_HOME improvement (+5.3→+1.41 pp mean) and simultaneously causes/worsens Spouse over-prediction (~12 pp in F1 back-calculated → +19.4 pp; same pattern seen in F7 at +20.3 pp). Since F7 also had Spouse +20.3 pp with the same aux head plus three other config changes, and F8 confirms Spouse is +19.4 pp with ONLY the aux head, the Spouse explosion is definitively AUX_STRATUM_HEAD-induced — not MARG_MODE or ACTIVITY_BOOSTS. activity JS regressed slightly vs F1 (0.066 vs 0.056), suggesting the aux task diverts some capacity from activity modeling. **Spouse calibration pattern:** model bimodal — 3.29M predictions σ < 0.1, 2.31M σ > 0.85; in high-confidence σ ≈ 0.90 bin, actual Spouse=1 prevalence only 43–53% (systematic over-confidence for Spouse=True). Model over-predicts Spouse, so pos_weight < 1.0 (NOT > 1.0) is the correction direction. **Next step (F9):** keep AUX_STRATUM_HEAD=1 (AT_HOME benefit essential), add Spouse-specific down-weight — set `pos_weight[Spouse] = 0.4` in the cop BCE head to penalize false positives more. New env var `SPOUSE_NEG_WEIGHT` in `04D_train.py`. F9 gates: composite < 1.045 AND AT_HOME ≤ +5.3 pp AND Spouse ≤ +10 pp (relaxed intermediate). | COMPLETE |
| 2026-04-25 | **F8 retrain submitted — single-axis ablation: F1 + AUX_STRATUM_HEAD=1 only.** Config: MARG_MODE=global (F1 default), ACTIVITY_BOOSTS=1 (F1 default — Work ×5, Transit ×3, Social ×2 retained), COP_POS_WEIGHT=0 (F1 default), DATA_SIDE_SAMPLING=0 (F1 default), AUX_STRATUM_HEAD=1 (only delta from F1), fp32, warmup-gate fix. **Rationale:** F7 conflated four config changes vs F1 (AUX_STRATUM_HEAD=1, MARG_MODE=per_cs, ACTIVITY_BOOSTS=0, fp32); we cannot attribute AT_HOME regression (5.3→11.1 pp) or Spouse explosion (→20.3 pp) to any single axis. F8 isolates AUX_STRATUM_HEAD alone. If AT_HOME stays ≤ 6 pp and Spouse stays small, the aux head is safe → F9 can stack MARG_MODE=per_cs. If AT_HOME blows out, the aux head leaks into home_head and F3-C's direction is suspect. **`04D_train.py` warmup-gate fix applied (permanent):** lines ~654–672 restructured so both best-model saving and patience counter are gated on `past_warmup = (epoch+1) > warmup_epochs`; prior code only gated patience. New files: `Speed_Cluster/job_04D_train_F8.sh`, `Speed_Cluster/submit_step4_F8_retrain.sh`. Chain: `04D_F8` (904149) → `04E_F8` (904150) → parallel `{04F_F8` (904151), `04H_F8` (904152), `04I_F8` (904153), `04J_F8` (904154)}. Tag: `F8_retrain_20260425_2147`. Node: cisr-1. Outputs to `outputs_step4_F8/`. (First attempt 904143–904148 failed: printf terminal-wrapping mangled the job script; fixed by deriving F8 from F7 via sed.) **Hard gates:** composite < 1.045 (beat F1) AND AT_HOME ≤ +5.3 pp AND Spouse ≤ +5 pp. | COMPLETE |
| 2026-04-26 | **ML engineer review of F8 result + Sonnet's F9 plan — flags act_JS regression overlooked, recommends F9-a (mechanism-level) over F9-b (symptom-level).** Sonnet's isolation logic on AUX_STRATUM_HEAD as the single cause of F8's behaviour is sound. Two valid F8 findings: (1) AT_HOME mean +5.3 → +1.41 pp is the best AT_HOME result of any run including F1 — a genuine win worth keeping; (2) Spouse +19.4 pp regression. **Caveat on the Spouse magnitude:** Sonnet's "F1 baseline ~12 pp" is a back-calc, not an observed value; F1's `cop_max_gap` was Alone (+16.1 pp) so F1 Spouse < 16.1 pp, but the precise number is not in the diagnostics or memory. **Overlooked regression in Sonnet's table:** `act_JS = 0.066` vs F1 0.056 is also a fail of an `act_JS ≤ 0.05` gate. F8 quietly degraded the activity head as well. Sonnet's F9-b (`SPOUSE_NEG_WEIGHT=0.4`, cop-head only) targets only Spouse — even if it works, the act_JS regression remains. This widens suspicion: AUX_STRATUM_HEAD is distorting the **whole decoder representation**, not just the cop head. **Concerns with F9-b design:** (1) magnitude of 0.4 is arbitrary, no calibration; principled starting point would be obs/syn ratio (22.4/42.6 ≈ 0.53), but `pos_weight` doesn't map linearly to predicted prevalence; (2) symptom-level — bimodal Spouse logit (σ<0.1 or σ>0.85, 43–53% empirical at σ≈0.90) is overconfidence + miscalibration; `pos_weight` shifts mean but does not fix bimodality (focal loss or temperature scaling at inference would target that); (3) cop-head-only fix is irrelevant to activity CE. **Proposed F9-a alternative (mechanism-level):** reduce aux-head λ from 0.1 → 0.02, OR detach the aux head gradient from the shared trunk. Hypothesis: AUX_STRATUM_HEAD makes the decoder hidden state encode stratum too aggressively → stratum is correlated with household composition → bleeds into Spouse and activity predictions. Reducing λ keeps the AT_HOME +1.41 pp benefit (which is the real signal of better stratum conditioning) while damping the representation distortion that drives both Spouse and act_JS regressions. **Recommended F9 sequencing:** F9-a first (single-knob mechanism test); if F9-a closes Spouse to ≤ +10 pp without losing AT_HOME, that's the signal — F10 can fine-tune. If F9-a leaves Spouse blown out but recovers act_JS, then Sonnet's symptom-level cop weight becomes F10. Reverse order is worse — F9-b first leaves act_JS unexplained and consumes a sweep slot without disambiguating mechanism vs symptom. If 4-GPU budget allows, run F9-a and F9-b in parallel — they're independent axes. | COMPLETE |
| 2026-04-26 | **F9-a retrain submitted — mechanism-level test: F8 + AUX_STRATUM_LAMBDA=0.02.** Config: AUX_STRATUM_HEAD=1, AUX_STRATUM_LAMBDA=0.02 (down from F8 default 0.1), MARG_MODE=global, ACTIVITY_BOOSTS=1, COP_POS_WEIGHT=0, DATA_SIDE_SAMPLING=0, fp32, warmup-gate fix. **Rationale (per ML engineer review):** F8 showed act_JS regression (0.066 vs F1 0.056) in addition to Spouse explosion (+19.4 pp). Both regressions co-occur with AUX_STRATUM_HEAD=1, suggesting the aux task makes the decoder encode stratum too aggressively, causing representation distortion that bleeds into both cop and activity heads. Reducing λ from 0.1 → 0.02 damps this distortion while preserving the AT_HOME benefit (+1.41 pp). **New env var `AUX_STRATUM_LAMBDA` in `04D_train.py`** (module-level, default 0.1 preserves F8 behaviour exactly — backward-compatible). Tag: `F9a_retrain_20260426_0953`. Node: speed-03. **Job IDs:** 04D 904709 → 04E 904710 → {04F 904711, 04H 904712, 04I 904713, 04J 904714}. **Hard gates:** composite < 1.045 AND AT_HOME ≤ +5.3 pp AND Spouse ≤ +10 pp AND act_JS ≤ 0.05. **CANCELLED** — all 6 jobs (904709–904714) cancelled before results arrived; will re-submit after orchestration refactor upload. | CANCELLED |
| 2026-04-26 | **F9-b retrain submitted — symptom-level test: F8 + SPOUSE_NEG_WEIGHT=0.4.** Config: AUX_STRATUM_HEAD=1, SPOUSE_NEG_WEIGHT=0.4 (sets pos_weight[Spouse]=0.4 in cop BCE, index 1 of 9 cop channels), MARG_MODE=global, ACTIVITY_BOOSTS=1, COP_POS_WEIGHT=0, DATA_SIDE_SAMPLING=0, fp32, warmup-gate fix. **Rationale:** Spouse over-prediction (obs 22.4%, syn 41.7%) — model bimodal, 43–53% actual Spouse=1 in high-confidence σ≈0.90 bins. Down-weighting Spouse=True training examples penalizes false positives more, reducing over-prediction. Cop-head-only fix; independent of F9-a. **Expected behaviour:** Spouse gap reduces; act_JS regression (0.066 vs F1 0.056) likely persists since this does not address decoder representation distortion. **New env var `SPOUSE_NEG_WEIGHT` in `04D_train.py`** (module-level, default 1.0 preserves F8 behaviour exactly — backward-compatible). Tag: `F9b_retrain_20260426_0953`. Node: speed-03. **Job IDs:** 04D 904715 → 04E 904716 → {04F 904717, 04H 904718, 04I 904719, 04J 904720}. **Hard gates:** composite < 1.045 AND AT_HOME ≤ +5.3 pp AND Spouse ≤ +10 pp AND act_JS ≤ 0.05. **CANCELLED** — all 6 jobs (904715–904720) cancelled before results arrived; will re-submit after orchestration refactor upload. | CANCELLED |
| 2026-04-26 | **Orchestration refactor COMPLETE — per-trial shell scripts superseded by YAML configs + sbatch job arrays + auto-rsync.** Manual F9-a (job 904709) and F9-b (job 904715) were submitted before the refactor landed and then cancelled (all 12 jobs 904709–904720 cancelled). Their configs are preserved as `configs/F9a.yaml` and `configs/F9b.yaml` and will be the first sweep targets when re-submitted on the new system. New files: `configs/_schema.md`, `configs/F1.yaml`, `configs/F8.yaml`, `configs/F9a.yaml`, `configs/F9b.yaml`, `configs/sweep_F9.yaml`, `configs/sweep_smoke.yaml`; `Speed_Cluster/job_04D_train_array.sh`, `submit_step4_array.sh`, `config_to_env.sh`, `config_to_env.py`, `extract_metrics.py`. `04D_train.py` edited: `AUX_STRATUM_LAMBDA` and `SPOUSE_NEG_WEIGHT` now read from env at module level (defaults preserve F8 behaviour). See `04_augmentationGSS_orchestration.md` for full design. Old per-trial scripts untouched (backward-compat fallback). | COMPLETE |
| 2026-04-25 | **F7 retrain COMPLETE — both hard gates PASS; stretch goal not met. First valid run since F1.** Config: F3-C + `COP_POS_WEIGHT=0` + fp32 + warmup-gate fix. `04D_train.py` lines ~654–672 modified: both best-model save and patience counter now gated on `past_warmup = (epoch+1) > warmup_epochs`; epochs 1–6 print `[warmup epoch N/6 — skipping best-model tracking]`. Chain: `04D_F7` (903690) → `04E_F7` (903691) → parallel `{04F_F7` (903692), `04H_F7` (903693), `04I_F7` (903694), `04J_F7` (903695)}`. Outputs to `outputs_step4_F7/`. **Training log:** best checkpoint at epoch 72, val_score=0.1743 (val_JS=0.0810, home_gap=0.1866); patience counter 3/15 at time of context compaction; warmup-gate confirmed working (epoch 72 save was the first real checkpoint). **Gate evaluation from `outputs_step4_F7/diagnostics_v4_statistical.json`:** composite 1.3645 < 2.366 ✅ PASS; Alone gap 12.95 pp < 13.3 pp ✅ PASS (margin 0.35 pp); stretch composite < 1.045 ✗ FAIL (1.3645). **Key metrics (bootstrap CIs):** AT_HOME gap +11.14 pp [+10.88, +11.38] (obs 72.5%, syn 83.6%); Alone gap +12.95 pp [+12.56, +13.33]; Spouse gap +20.27 pp [+19.86, +20.67] (obs 22.4%, syn 42.6%). Activity JS mean 0.0406; cop cal MAE 0.340. **Composite components:** AT_HOME_rms 8.63 pp (w1=0.20 → 0.173), cop_max_gap 20.27 pp (w2=0.35 → 0.709), act_JS 0.0406 (w3=0.35 → 0.142), cop_cal_MAE 0.340 (w4=0.10 → 0.340). **Dominant failure mode:** Spouse +20.27 pp (syn 42.6% vs obs 22.4%) is the single largest composite term (52%). AT_HOME regressed vs F1 (+11.1 pp vs +5.3 pp) and vs F3-C (+5.8 pp). Alone gap improved vs F1 (12.95 pp vs 16.1 pp). Activity JS improved vs F1 (0.041 vs 0.056). **AT_HOME calibration anomaly in 04J:** all predictions land in σ≈0 bin (mae=0.511) — this is a 04J bug where the binary AT_HOME column in augmented_diaries.csv is read instead of the raw sigmoid; the bootstrap CI gap (+11.14 pp) is the reliable AT_HOME metric. **Decision pending:** F7 passes gates and is the first valid model since F1. Primary question for F8: address Spouse +20.3 pp gap (model predicts Spouse co-presence 2× more than observed) while recovering AT_HOME gap (+11.1 pp, regressed from +5.3 pp in F1). | COMPLETE |
