#!/encs/bin/bash
#SBATCH --job-name=3J_s4_val
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_4split_val_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_4split_val_%j.err

# ── 3rdJ Step 4: Validator only (Leg-3, 4-split) ──────────────────────────────
# Requires outputs_step4/augmented_diaries.csv (+ config + logs) from
# 3rdJ_s4_4split_joint.sh or 3rdJ_s4_4split_train.sh.
#
# ⚠️ NOTE (2026-07-19): 3rdJ_04_augmentationGSS_4split_val.py (the RW gates +
# ISR + regression-gate battery) is NOT YET BUILT — it is a separate,
# not-yet-started Progress Checklist item ("Validator: RW gates + ISR +
# regression gates"). This wrapper is provided now (per the requested sbatch
# family) so it is ready to use once that script lands; running it before
# then will fail with a clear "file not found" — that is expected, not a bug
# in this wrapper.
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs
# Command:  sbatch 3rdJ_s4_4split_valonly.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4 Validator (Leg-3, 4-split) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"

$PYTHON -c "import pandas, numpy, matplotlib, seaborn, scipy" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet matplotlib seaborn scipy 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${SDIR}/outputs_step4/augmented_diaries.csv"
chk "${SDIR}/outputs_step4/step4_feature_config.json"
chk "${SDIR}/3rdJ_04_augmentationGSS_4split_val.py"
echo "[OK] Step-4 outputs + validator script present. Starting validator..."

cd "$SDIR"
$PYTHON 3rdJ_04_augmentationGSS_4split_val.py
EXIT_VAL=$?
echo "[DONE] Validator exit code: $EXIT_VAL"

echo ""; echo "===== Done ====="
date
exit $EXIT_VAL
