#!/encs/bin/bash
#=============================================================================
# 3rdJ_s4_R10_twaware.sh — Telework-AWARE rake (post-rake FLOATING fixup) + Validate
#
# Stage:    Rake (04L --telework_aware) → Validate   [NO inference — reuses base R10_fast diaries]
# Build:    2026-06-19 (manager Opus)
# Purpose:  R10_twcoh (job 980832) proved the INFERENCE-level fix (04E --telework_coherent)
#           is overwritten by the classic rake — post-rake FLOATING stayed at 30.87%.
#           The correct lever is 04L's existing --telework_aware flag, which runs the
#           rake uniformly (no work-slot locking) then applies a post-rake FLOATING
#           fixup: any work-activity slot left wrk30=0 & hom30=0 -> hom30=1.
#           This drives FLOATING -> 0% AFTER the rake. The validator adjudicates
#           whether G2 (AT_HOME) / OW1 (AT_WORK) survive the added home-mass.
#
#           Input: the ORIGINAL base R10_fast diaries (NOT the twcoh re-inference) —
#           isolates the rake-side fix as the sole lever and keeps the simplest
#           base->Step5 pipeline (R10_fast inference -> tw-aware rake -> validate).
#
# SUBMIT (one line, from Step4_docs on the cluster login node):
#   sbatch /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_s4_R10_twaware.sh
#=============================================================================
#SBATCH --job-name=s4_R10_twaware
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s4_R10_twaware_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/s4_R10_twaware_%j.err

# ── Fail loudly: any step error aborts the job ────────────────────────────────
set -eo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
STEP4_DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
SHARED="${STEP4_DIR}/outputs_step4"
R10_DIR="${SHARED}/sweep/R10_fast"
R10_CKPT="${R10_DIR}/checkpoints/best_model.pt"
TWAWARE_RAKED="${SHARED}/sweep/R10_fast_twaware_raked"
LOG_DIR="/speed-scratch/o_iseri/logs"

mkdir -p "${TWAWARE_RAKED}" "${LOG_DIR}"

echo "======================================================================"
echo "Step 4 R10_twaware (telework-AWARE rake) — $(date)"
echo "  Node: $(hostname)  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "  data_dir:   ${SHARED}"
echo "  r5_dir:     ${R10_DIR}  (base R10_fast diaries)"
echo "  checkpoint: ${R10_CKPT}"
echo "  raked_out:  ${TWAWARE_RAKED}"
echo "======================================================================"

# ── [0/2] Environment + input guards ─────────────────────────────────────────
echo "[0/2] Checking Python environment ..."
${PYTHON} -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
${PYTHON} -c "import numpy, pandas, sklearn; print('numpy pandas sklearn OK')"

chk() { [ -f "$1" ] || { echo "[ERROR] Missing required file: $1"; exit 1; }; }
chk "${SHARED}/step4_train.pt"
chk "${SHARED}/step4_all_meta.csv"
chk "${R10_DIR}/augmented_diaries.csv"
chk "${R10_DIR}/g3_copresence_thresholds.json"
chk "${R10_CKPT}"
echo "[OK] All input files present."

cd "${STEP4_DIR}"

# ── [1/2] Telework-AWARE rake (post-rake FLOATING fixup) ─────────────────────
echo ""
echo "[1/2] Running 04L joint rake with --telework_aware ..."
${PYTHON} 3rdJ_04L_joint_rake_2split.py \
    --data_dir   "${SHARED}" \
    --r5_dir     "${R10_DIR}" \
    --checkpoint "${R10_CKPT}" \
    --output_dir "${TWAWARE_RAKED}" \
    --temperature 0.8 \
    --telework_aware \
    > "${LOG_DIR}/s4_R10_twaware_rake.log" 2>&1
echo "  Rake done. Log: ${LOG_DIR}/s4_R10_twaware_rake.log"

chk "${TWAWARE_RAKED}/augmented_diaries.csv"

# ── [2/2] Validate ───────────────────────────────────────────────────────────
echo ""
echo "[2/2] Running validator on telework-aware raked output ..."
${PYTHON} 3rdJ_04_augmentationGSS_2split_val.py \
    --step4_dir "${TWAWARE_RAKED}" \
    > "${LOG_DIR}/s4_R10_twaware_val.log" 2>&1
echo "  Validation done. Log: ${LOG_DIR}/s4_R10_twaware_val.log"

echo ""
echo "======================================================================"
echo "R10_twaware pipeline complete — $(date)"
echo "  Raked output: ${TWAWARE_RAKED}/augmented_diaries.csv"
echo "  Logs:         ${LOG_DIR}/s4_R10_twaware_{rake,val}.log"
echo "======================================================================"
