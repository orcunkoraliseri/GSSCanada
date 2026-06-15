#!/encs/bin/bash
#SBATCH --job-name=3J_s4_val
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_val_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_val_%j.err

# ── 3rdJ Step 4: Validator only (Leg-2 two-channel) ───────────────────────────
# Requires Step-4 outputs in outputs_step4/ (augmented_diaries.csv + config + log).
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs
# Command:  sbatch 3rdJ_s4_2split_valonly.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4 Validator (Leg-2) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"

$PYTHON -c "import pandas, numpy, matplotlib, seaborn, scipy" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet matplotlib seaborn scipy 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${SDIR}/outputs_step4/augmented_diaries.csv"
chk "${SDIR}/outputs_step4/step4_feature_config.json"
echo "[OK] Step-4 outputs present. Starting validator..."

cd "$SDIR"
$PYTHON 3rdJ_04_augmentationGSS_2split_val.py
EXIT_VAL=$?
echo "[DONE] Validator exit code: $EXIT_VAL"

echo ""; echo "===== Done ====="
date
exit $EXIT_VAL
