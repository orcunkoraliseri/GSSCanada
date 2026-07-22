#!/encs/bin/bash
#SBATCH --job-name=3J_s3_val_4split
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s3_val_4split_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s3_val_4split_%j.err

# ── 3rdJ Step 3: Validator only (Leg-3 Four-Channel Split) ────────────────────
# Requires Step-3 outputs to exist in outputs_step3/ (5 legacy CSVs + retail_30min.csv).
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step3_docs
# Command:  sbatch 3rdJ_s3_4split_valonly.sh

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step3_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 3 Validator (Leg-3 Four-Channel Split) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"

# ── Source modules and activate venv ─────────────────────────────────────────
. /encs/pkg/modules-5.3.1/root/init/bash
module load Python/3.9
$PYTHON -c "import pandas, numpy, matplotlib, seaborn" || {
    echo "[PRECHECK] Installing missing packages into venv..."
    /speed-scratch/o_iseri/envs/step4/bin/pip install matplotlib seaborn 2>&1 | tail -5
}

# ── Check Step-3 outputs exist ────────────────────────────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${SDIR}/outputs_step3/merged_episodes.csv"
chk "${SDIR}/outputs_step3/hetus_wide.csv"
chk "${SDIR}/outputs_step3/hetus_30min.csv"
chk "${SDIR}/outputs_step3/copresence_30min.csv"
chk "${SDIR}/outputs_step3/work_30min.csv"
chk "${SDIR}/outputs_step3/retail_30min.csv"
echo "[OK] All 6 Step-3 output CSVs present. Starting validator..."

# ── Run validator ─────────────────────────────────────────────────────────────
cd "$SDIR"
$PYTHON 3rdJ_03_mergingGSS_4split_val.py
EXIT_VAL=$?
echo "[DONE] Validator exit code: $EXIT_VAL"

echo ""; echo "===== Done ====="
date
exit $EXIT_VAL
