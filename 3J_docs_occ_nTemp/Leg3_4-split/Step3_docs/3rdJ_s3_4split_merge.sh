#!/encs/bin/bash
#SBATCH --job-name=3J_s3_merge_4split
#SBATCH --partition=ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s3_merge_4split_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s3_merge_4split_%j.err

# ── 3rdJ Step 3: Merge & Tiling (Leg-3 Four-Channel Split) ────────────────────
# Runs main script then validator in one job.
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step3_docs
# Command:  sbatch 3rdJ_s3_4split_merge.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step3_docs"
S2DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step2_docs/outputs_step2"
LEG2_S3DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step3_docs/outputs_step3"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 3 Merge + Tiling (Leg-3 Four-Channel Split) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Python: $($PYTHON --version 2>&1)"

# ── Module precheck (step4 venv) ────────────────────────────────────────────────
$PYTHON -c "import pandas, numpy, pyarrow, matplotlib, seaborn" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet pyarrow matplotlib seaborn 2>&1 | tail -5
}

# ── Input file check (read-only Leg-2 Step-2 outputs) ─────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
for C in 2005 2010 2015 2022; do
    chk "${S2DIR}/main_${C}.csv"
    chk "${S2DIR}/episode_${C}.csv"
done
echo "[OK] All 8 Step-2 input files present."

# ── Leg-2 bit-identity reference check (Delta D) ──────────────────────────────
for F in merged_episodes.csv merged_episodes.parquet hetus_wide.csv hetus_30min.csv copresence_30min.csv work_30min.csv; do
    chk "${LEG2_S3DIR}/${F}"
done
echo "[OK] All 6 Leg-2 legacy reference outputs present (Delta D hash gate reference)."

# ── Ensure output directory exists ────────────────────────────────────────────
mkdir -p "${SDIR}/outputs_step3"

# ── Run main merger ───────────────────────────────────────────────────────────
cd "$SDIR"
echo ""; echo "[STEP 3 MAIN] Starting merge + tiling..."
$PYTHON 3rdJ_03_mergingGSS_4split.py
EXIT_MAIN=$?
echo "[STEP 3 MAIN] Exit code: $EXIT_MAIN"
if [ $EXIT_MAIN -ne 0 ]; then
    echo "[ERROR] Main script failed — stopping before validator."; exit $EXIT_MAIN
fi

# ── Check expected outputs (6 legacy + retail_30min) ──────────────────────────
for F in merged_episodes.csv hetus_wide.csv hetus_30min.csv copresence_30min.csv work_30min.csv retail_30min.csv; do
    chk "${SDIR}/outputs_step3/${F}"
done
echo "[OK] All 6 expected Step-3 output CSVs present (5 legacy + retail_30min)."

# ── Run validator ─────────────────────────────────────────────────────────────
echo ""; echo "[STEP 3 VAL] Starting validator..."
$PYTHON 3rdJ_03_mergingGSS_4split_val.py
EXIT_VAL=$?
echo "[STEP 3 VAL] Exit code: $EXIT_VAL"

echo ""; echo "===== Done ====="
date
exit $EXIT_VAL
