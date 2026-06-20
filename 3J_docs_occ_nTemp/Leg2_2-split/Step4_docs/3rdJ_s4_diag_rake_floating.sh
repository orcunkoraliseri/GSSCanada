#!/encs/bin/bash
#SBATCH --job-name=3J_rake_float
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/diag_rake_floating_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/diag_rake_floating_%j.err

# 3rdJ Step 4S — rake-creates-floating diagnostic
# CPU-only: pure CSV before/after comparison, no GPU, no model.
# Partition: ps (CPU pool).
#
# Submit from Step4_docs on the cluster:
#   sbatch 3rdJ_s4_diag_rake_floating.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
SHARED="${SDIR}/outputs_step4"
R10_PRE="${SHARED}/sweep/R10_fast/augmented_diaries.csv"
R10_POST="${SHARED}/sweep/R10_fast_raked/augmented_diaries.csv"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
LOGDIR="/speed-scratch/o_iseri/logs"

echo "===== 3J Step 4S — rake-creates-floating diagnostic =====" ; date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "  SDIR:      $SDIR"
echo "  R10_PRE:   $R10_PRE"
echo "  R10_POST:  $R10_POST"
echo "  PYTHON:    $PYTHON"

# ── Import precheck ──────────────────────────────────────────────────────────
$PYTHON -c "import numpy, pandas; print('numpy', numpy.__version__, 'pandas', pandas.__version__)" || {
    echo "[PRECHECK] Installing missing packages..."
    $PYTHON -m pip install --quiet numpy pandas 2>&1 | tail -5
}

# ── Input file check ─────────────────────────────────────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "$R10_PRE"
chk "$R10_POST"
echo "[OK] Both input CSVs present."

mkdir -p "$LOGDIR"
cd "$SDIR"

# ── Run diagnostic ───────────────────────────────────────────────────────────
echo "" ; echo "[04S] Running rake-creates-floating diagnostic..."
$PYTHON 3rdJ_04S_diag_rake_creates_floating_2split.py \
    --pre_csv  "$R10_PRE" \
    --post_csv "$R10_POST" \
    --output   "${SHARED}/diag_rake_creates_floating_R10.txt" \
    --n_examples 5
EXIT_CODE=$?

echo "" ; echo "[04S] Exit code: $EXIT_CODE" ; date
exit $EXIT_CODE
