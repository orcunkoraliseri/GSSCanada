#!/encs/bin/bash
#SBATCH --job-name=3J_s4_diaghw
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_diaghw_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_diaghw_%x_%j.err

# ── 3rdJ Step 4: G2/OW1 home/work operating-point diagnostic (Plan B) ──────────
# Re-runs model.generate with return_hw_probs=True to capture raw sigmoid
# probabilities for AT_HOME and AT_WORK heads before 0.5 threshold.
# Determines whether G2/OW1 gaps are OPERATING-POINT artifacts or LEARNED-DEFICIT.
# GPU required (model.generate). Does NOT write augmented_diaries.csv.
#
# Submit from Step4_docs on the cluster:
#   best variant:  sbatch --job-name=R5_diaghw --export=ALL,VARIANT=R5_lr1e4 3rdJ_s4_2split_diaghw.sh
#   baseline R0:   sbatch --job-name=R0_diaghw --export=ALL,VARIANT=__BASE__ 3rdJ_s4_2split_diaghw.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

: "${VARIANT:?ERROR: set VARIANT via sbatch --export (e.g. VARIANT=R5_lr1e4 or __BASE__ for baseline)}"
if [ "$VARIANT" = "__BASE__" ]; then
    VARDIR="${SDIR}/outputs_step4"
else
    VARDIR="${SDIR}/outputs_step4/sweep/${VARIANT}"
fi

echo "===== 3J Step 4H G2/OW1 home/work diagnostic — ${VARIANT} ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "VARDIR: $VARDIR"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

$PYTHON -c "import torch, pandas, numpy" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet pandas numpy 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${VARDIR}/checkpoints/best_model.pt"
chk "${VARDIR}/step4_train.pt"
chk "${SDIR}/3rdJ_04H_diag_homework_2split.py"
chk "${SDIR}/3rdJ_04B_model_2split.py"
echo "[OK] inputs present. Starting G2/OW1 diagnostic on ${VARIANT}..."

cd "$SDIR"
$PYTHON 3rdJ_04H_diag_homework_2split.py --step4_dir "$VARDIR" --data_dir "$VARDIR"
EXIT_VAL=$?
echo "[DONE] diagnostic exit code: $EXIT_VAL"

echo ""; echo "===== Done (${VARIANT}) ====="
date
exit $EXIT_VAL
