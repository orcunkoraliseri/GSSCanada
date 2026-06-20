#!/encs/bin/bash
#=============================================================================
# 3rdJ_s4_R10_twcoh.sh — Telework-Coherent Inference + Classic Rake + Validate
#
# Stage:    Infer (04E --telework_coherent) → Rake (04L classic) → Validate
# Build:    2026-06-19 (employee builder, Claude Sonnet 4.6)
# Purpose:  Re-run R10_fast inference with AT-WORK XOR TELEWORK posthoc fix
#           (--telework_coherent), then classic rake + validate.
#           Input checkpoint: outputs_step4/sweep/R10_fast/checkpoints/best_model.pt
#           Output (infer):   outputs_step4/sweep/R10_fast_twcoh/augmented_diaries.csv
#           Output (raked):   outputs_step4/sweep/R10_fast_twcoh_raked/augmented_diaries.csv
#
# SUBMIT (one line, from Step4_docs on the cluster login node):
#   sbatch /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_s4_R10_twcoh.sh
#=============================================================================
#SBATCH --job-name=s4_R10_twcoh
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s4_R10_twcoh_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/s4_R10_twcoh_%j.err

# ── Fail loudly: any step error aborts the job ────────────────────────────────
set -eo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
STEP4_DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
SHARED="${STEP4_DIR}/outputs_step4"
R10_CKPT="${SHARED}/sweep/R10_fast/checkpoints/best_model.pt"
TWCOH_OUT="${SHARED}/sweep/R10_fast_twcoh"
TWCOH_RAKED="${SHARED}/sweep/R10_fast_twcoh_raked"
LOG_DIR="/speed-scratch/o_iseri/logs"

mkdir -p "${TWCOH_OUT}" "${TWCOH_RAKED}" "${LOG_DIR}"

echo "======================================================================"
echo "Step 4 R10_twcoh (telework-coherent) — $(date)"
echo "  Node: $(hostname)  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "  data_dir:    ${SHARED}"
echo "  checkpoint:  ${R10_CKPT}"
echo "  infer_out:   ${TWCOH_OUT}"
echo "  raked_out:   ${TWCOH_RAKED}"
echo "======================================================================"

# ── [0/3] Environment precheck ───────────────────────────────────────────────
echo "[0/3] Checking Python environment ..."
${PYTHON} -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
${PYTHON} -c "import numpy, pandas, sklearn; print('numpy pandas sklearn OK')"

# ── Input file guard ─────────────────────────────────────────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing required file: $1"; exit 1; }; }
chk "${SHARED}/step4_train.pt"
chk "${SHARED}/step4_val.pt"
chk "${SHARED}/step4_test.pt"
chk "${SHARED}/step4_all_meta.csv"
chk "${SHARED}/step4_feature_config.json"
chk "${R10_CKPT}"
echo "[OK] All input files present."

cd "${STEP4_DIR}"

# ── [1/3] Inference with --telework_coherent ─────────────────────────────────
echo ""
echo "[1/3] Running 04E inference with --telework_coherent ..."
${PYTHON} 3rdJ_04E_inference_2split.py \
    --data_dir    "${SHARED}" \
    --checkpoint  "${R10_CKPT}" \
    --output      "${TWCOH_OUT}/augmented_diaries.csv" \
    --temperature 0.8 \
    --telework_coherent \
    > "${LOG_DIR}/s4_R10_twcoh_infer.log" 2>&1
echo "  Inference done. Log: ${LOG_DIR}/s4_R10_twcoh_infer.log"

chk "${TWCOH_OUT}/augmented_diaries.csv"

# ── [2/3] Classic rake (NO --telework_aware) ─────────────────────────────────
echo ""
echo "[2/3] Running 04L joint rake (classic, no --telework_aware) ..."
${PYTHON} 3rdJ_04L_joint_rake_2split.py \
    --data_dir   "${SHARED}" \
    --r5_dir     "${TWCOH_OUT}" \
    --output_dir "${TWCOH_RAKED}" \
    --temperature 0.8 \
    > "${LOG_DIR}/s4_R10_twcoh_rake.log" 2>&1
echo "  Rake done. Log: ${LOG_DIR}/s4_R10_twcoh_rake.log"

chk "${TWCOH_RAKED}/augmented_diaries.csv"

# ── [3/3] Validate ───────────────────────────────────────────────────────────
echo ""
echo "[3/3] Running validator on raked output ..."
${PYTHON} 3rdJ_04_augmentationGSS_2split_val.py \
    --step4_dir "${TWCOH_RAKED}" \
    > "${LOG_DIR}/s4_R10_twcoh_val.log" 2>&1
echo "  Validation done. Log: ${LOG_DIR}/s4_R10_twcoh_val.log"

echo ""
echo "======================================================================"
echo "R10_twcoh pipeline complete — $(date)"
echo "  Infer output: ${TWCOH_OUT}/augmented_diaries.csv"
echo "  Raked output: ${TWCOH_RAKED}/augmented_diaries.csv"
echo "  Logs:         ${LOG_DIR}/s4_R10_twcoh_*.log"
echo "======================================================================"
