#!/encs/bin/bash
#SBATCH --job-name=3J_s4_valsw
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_valsw_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_valsw_%x_%j.err

# ── 3rdJ Step 4: Validator for a SWEEP variant (Leg-2 two-channel) ────────────
# Same validator as the baseline, but points --step4_dir at a per-variant subdir
# outputs_step4/sweep/$VARIANT/ (writes step4_validation_report.{html,txt} there).
# The variant only needs augmented_diaries.csv in that dir; config/training-log
# are optional (validator falls back gracefully).
#
# Submit from: .../Leg2_2-split/Step4_docs
#   sbatch --job-name=R5val --export=ALL,VARIANT=R5_lr1e4 3rdJ_s4_2split_valsweep.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

: "${VARIANT:?ERROR: set VARIANT via sbatch --export (e.g. VARIANT=R5_lr1e4)}"
VARDIR="${SDIR}/outputs_step4/sweep/${VARIANT}"

echo "===== 3J Step 4 Validator (Leg-2 SWEEP) — ${VARIANT} ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "VARDIR: $VARDIR"

$PYTHON -c "import pandas, numpy, matplotlib, seaborn, scipy" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet matplotlib seaborn scipy 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${VARDIR}/augmented_diaries.csv"
echo "[OK] Variant output present. Starting validator on ${VARIANT}..."

cd "$SDIR"
$PYTHON 3rdJ_04_augmentationGSS_2split_val.py --step4_dir "$VARDIR"
EXIT_VAL=$?
echo "[DONE] Validator exit code: $EXIT_VAL"

echo ""; echo "===== Done (${VARIANT}) ====="
date
exit $EXIT_VAL
