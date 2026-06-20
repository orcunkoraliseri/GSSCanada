#!/encs/bin/bash
#SBATCH --job-name=3J_diag_float
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/diag_floating_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/diag_floating_%j.err

# 3rdJ Step 4R — FLOATING-state diagnostic (R10_fast, pre-rake)
# GPU needed for model.generate(return_hw_probs=True) in Sections B + C.
# Submit from Step4_docs on the cluster:
#   sbatch 3rdJ_s4_diag_floating.sh
#
# Optional: override n_sample via env var:
#   sbatch --export=ALL,N_SAMPLE=5000 3rdJ_s4_diag_floating.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
SHARED="${SDIR}/outputs_step4"
R10DIR="${SHARED}/sweep/R10_fast"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
LOGDIR="/speed-scratch/o_iseri/logs"
: "${N_SAMPLE:=2000}"

echo "===== 3J Step 4R — FLOATING diagnostic (R10_fast) =====" ; date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "  SDIR:    $SDIR"
echo "  R10DIR:  $R10DIR"
echo "  PYTHON:  $PYTHON"
echo "  N_SAMPLE: $N_SAMPLE"

# ── Import precheck ──────────────────────────────────────────────────────────
$PYTHON -c "import torch, numpy, pandas; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages..."
    $PYTHON -m pip install --quiet torch numpy pandas 2>&1 | tail -5
}

# ── Input file check ─────────────────────────────────────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${SHARED}/step4_train.pt"
chk "${SHARED}/step4_val.pt"
chk "${SHARED}/step4_test.pt"
chk "${R10DIR}/augmented_diaries.csv"
chk "${R10DIR}/checkpoints/best_model.pt"
echo "[OK] All input files present."

mkdir -p "$LOGDIR"
cd "$SDIR"

# ── Run diagnostic ───────────────────────────────────────────────────────────
echo "" ; echo "[04R] Running floating diagnostic..."
$PYTHON 3rdJ_04R_diag_floating_2split.py \
    --data_dir   "$SHARED" \
    --aug_csv    "${R10DIR}/augmented_diaries.csv" \
    --checkpoint "${R10DIR}/checkpoints/best_model.pt" \
    --n_sample   "$N_SAMPLE" \
    --output     "${SHARED}/diag_floating_R10.txt"
EXIT_CODE=$?

echo "" ; echo "[04R] Exit code: $EXIT_CODE" ; date
exit $EXIT_CODE
