#!/encs/bin/bash
#SBATCH --job-name=3J_s4_diagcop
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_diagcop_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_diagcop_%x_%j.err

# ── 3rdJ Step 4: G3 co-presence diagnostic (analysis-only, no retraining) ─────
# Reads the stored co-presence PROBABILITIES in a variant's augmented_diaries.csv
# and reports, per channel, whether the residual G3 gap is operating-point
# (fixable by a per-channel threshold) or a learned deficit.
#
# Submit from Step4_docs on the cluster:
#   baseline R0:  sbatch --job-name=R0_diagcop --export=ALL,VARIANT=__BASE__ 3rdJ_s4_2split_diagcop.sh
#   a sweep var:  sbatch --job-name=R5_diagcop --export=ALL,VARIANT=R5_lr1e4 3rdJ_s4_2split_diagcop.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

: "${VARIANT:?ERROR: set VARIANT via sbatch --export (e.g. VARIANT=R5_lr1e4, or __BASE__ for baseline)}"
if [ "$VARIANT" = "__BASE__" ]; then
    VARDIR="${SDIR}/outputs_step4"
else
    VARDIR="${SDIR}/outputs_step4/sweep/${VARIANT}"
fi

echo "===== 3J Step 4 G3 co-presence diagnostic — ${VARIANT} ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "VARDIR: $VARDIR"

$PYTHON -c "import pandas, numpy" 2>/dev/null || {
    echo "[PRECHECK] Installing pandas/numpy into step4 env..."
    $PYTHON -m pip install --quiet pandas numpy 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${VARDIR}/augmented_diaries.csv"
chk "${SDIR}/3rdJ_04G_diag_copresence_2split.py"
echo "[OK] inputs present. Starting diagnostic on ${VARIANT}..."

cd "$SDIR"
$PYTHON 3rdJ_04G_diag_copresence_2split.py --step4_dir "$VARDIR"
EXIT_VAL=$?
echo "[DONE] diagnostic exit code: $EXIT_VAL"

echo ""; echo "===== Done (${VARIANT}) ====="
date
exit $EXIT_VAL
