#!/encs/bin/bash
#SBATCH --job-name=3J_s4_train
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_train_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_train_%j.err

# ── 3rdJ Step 4: Augmentation model — assembly -> pairs -> train -> inference ──
# Two-channel (Residential AT_HOME + Office AT_WORK) J3 Hybrid AR-Encoder.
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs
# Command:  sbatch 3rdJ_s4_2split_train.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
S3DIR="${SDIR}/../Step3_docs/outputs_step3"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4 Train (Leg-2 two-channel) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Python: $($PYTHON --version 2>&1)"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

# ── Module precheck (step4 venv) ──────────────────────────────────────────────
$PYTHON -c "import pandas, numpy, torch, scipy, sklearn" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet pandas numpy scipy scikit-learn 2>&1 | tail -5
}

# ── Input file check (Step-3 outputs) ─────────────────────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${S3DIR}/hetus_30min.csv"
chk "${S3DIR}/copresence_30min.csv"
chk "${S3DIR}/work_30min.csv"
echo "[OK] All 3 Step-3 input files present."

mkdir -p "${SDIR}/outputs_step4/checkpoints"
cd "$SDIR"

# ── 1. Data assembly ──────────────────────────────────────────────────────────
echo ""; echo "[04A] Dataset assembly..."
$PYTHON 3rdJ_04A_assembly_2split.py || { echo "[ERROR] 04A failed"; exit 11; }

# ── 2. Training pairs ─────────────────────────────────────────────────────────
echo ""; echo "[04C] Building day-type pairs..."
$PYTHON 3rdJ_04C_pairs_2split.py || { echo "[ERROR] 04C failed"; exit 12; }

# ── 3. Train ──────────────────────────────────────────────────────────────────
echo ""; echo "[04D] Training two-channel model..."
$PYTHON 3rdJ_04D_train_2split.py --fp16 || { echo "[ERROR] 04D failed"; exit 13; }

# ── 4. Inference ──────────────────────────────────────────────────────────────
echo ""; echo "[04E] Generating augmented diaries..."
$PYTHON 3rdJ_04E_inference_2split.py || { echo "[ERROR] 04E failed"; exit 14; }

# ── Check expected outputs ────────────────────────────────────────────────────
for F in checkpoints/best_model.pt step4_training_log.csv augmented_diaries.csv; do
    chk "${SDIR}/outputs_step4/${F}"
done
echo "[OK] All expected Step-4 outputs present."

echo ""; echo "===== Done ====="
date
