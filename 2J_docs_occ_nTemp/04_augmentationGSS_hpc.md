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
torch>=2.0
numpy>=1.24
pandas>=2.0
scikit-learn>=1.3
matplotlib>=3.7
scipy>=1.11
```

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
salloc --mem=20G --gpus=1 -p pg -c 4 -t 2:00:00
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

# Install remaining dependencies
pip install pandas>=2.0 scikit-learn>=1.3 matplotlib>=3.7 scipy>=1.11

# Verify GPU is visible
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"

conda deactivate
exit  # release the interactive node
```

### 3.2 Verify Environment (quick test)

```bash
salloc --mem=10G --gpus=1 -p pg -c 2 -t 0:30:00

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
#SBATCH --gpus=1
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
echo "=== Starting 04D Training ==="

python 04D_train.py \
    --data_dir outputs_step4 \
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

If training is interrupted by the 12-hour wall time:

```bash
# Edit job_04D_train.sh to add --resume flag:
python 04D_train.py \
    --data_dir outputs_step4 \
    --output_dir outputs_step4 \
    --checkpoint_dir outputs_step4/checkpoints \
    --resume outputs_step4/checkpoints/last_checkpoint.pt \
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
#SBATCH --gpus=1
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

---

## Reference Links

- Speed HPC docs: https://nag-devops.github.io/speed-hpc/
- Job script generator: https://nag-devops.github.io/speed-hpc/generator.html
- Example scripts: https://github.com/NAG-DevOps/speed-hpc/tree/master/src
- HPC support: `rt-ex-hpc@encs.concordia.ca`
