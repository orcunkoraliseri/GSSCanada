#!/encs/bin/bash
#SBATCH --job-name=3J_s6_4split
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s6_4split_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s6_4split_%j.err

# ── 3rdJ Step 6 Track A (Leg-3, 4-split): GPU forecasting, full chain ─────────
# --stage all: audit -> A -> B -> C -> D1 -> D2 (3 WFH bands), on the raw
# (pre-rake) seed_3_g3fix pool (accepted-wholesale per Step-4's 2026-07-21
# Progress Log decision — supersedes seed_3; see the .py module docstring).
# Mirrors Leg-3 Step-4's own sbatch style (bash shebang + module init +
# PYTHON var), NOT Leg-2 Step-6's tcsh style — kept consistent with the rest
# of the Leg-3 tree, same venv.
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step6_docs
# Command:  sbatch slurm_06_4split.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step6_docs"
DATA="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs/outputs_step4/seed_3_g3fix/augmented_diaries.csv"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 6 Track A — Leg-3 4-split — full chain (audit->A->B->C->D1->D2) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "Python: $($PYTHON --version 2>&1)"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${DATA}"
echo "[OK] Raw pool present: ${DATA}"

mkdir -p "${SDIR}/outputs_step6/models"
cd "$SDIR"

$PYTHON -u 3rdJ_06_longitudinalForecasting_4split.py --stage all --data "${DATA}" \
    || { echo "[ERROR] Step 6 chain failed"; exit 21; }

echo ""; echo "===== Done ====="
date
