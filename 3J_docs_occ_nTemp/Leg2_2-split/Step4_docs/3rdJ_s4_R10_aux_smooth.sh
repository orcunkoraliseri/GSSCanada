#!/encs/bin/bash
#=============================================================================
# 3rdJ_s4_R10_aux_smooth.sh — Aux-loss fine-tune from R10: L_smooth only
#
# Stage:    Warm-start Train (04D --warm_start R10 + --w_smooth 0.1) →
#           Infer (04E) → Rake (04L --floating_aware) → Validate
# Build:    2026-06-20 (employee builder, Claude Sonnet 4.6)
# Purpose:  Fine-tune the R10_fast best_model.pt with the AT_HOME smoothness
#           auxiliary loss (hinge on per-person hom30 transition count vs
#           smooth_target=2.0; mirrors GB which counts hom30 transitions/day;
#           hinge never pushes below observed ~2.0). Ablation variant
#           "smooth"; w_peak=0.0, w_order=0.0, w_smooth=0.1, epochs=25.
#           Output: sweep/R10_aux_smooth  (checkpoints + diaries)
#                   sweep/R10_aux_smooth_floataware_raked  (raked)
#
# SUBMIT (one line, from Step4_docs on the cluster login node):
#   sbatch /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_s4_R10_aux_smooth.sh
#=============================================================================
#SBATCH --job-name=s4_R10_aux_smooth
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s4_R10_aux_smooth_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/s4_R10_aux_smooth_%j.err

set -eo pipefail

STEP4_DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
SHARED="${STEP4_DIR}/outputs_step4"
R10_CKPT="${SHARED}/sweep/R10_fast/checkpoints/best_model.pt"
VARDIR="${SHARED}/sweep/R10_aux_smooth"
RAKED="${SHARED}/sweep/R10_aux_smooth_floataware_raked"
LOG_DIR="/speed-scratch/o_iseri/logs"

mkdir -p "${VARDIR}/checkpoints" "${RAKED}" "${LOG_DIR}"

echo "======================================================================"
echo "Step 4 R10_aux_smooth (aux L_smooth fine-tune) — $(date)"
echo "  Node: $(hostname)  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "  warm_start:  ${R10_CKPT}"
echo "  variant_dir: ${VARDIR}"
echo "  raked_out:   ${RAKED}"
echo "======================================================================"

echo "[0/4] Checking Python environment ..."
${PYTHON} -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
${PYTHON} -c "import numpy, pandas, sklearn; print('numpy pandas sklearn OK')"

chk() { [ -f "$1" ] || { echo "[ERROR] Missing required file: $1"; exit 1; }; }
chk "${SHARED}/step4_train.pt"
chk "${SHARED}/step4_val.pt"
chk "${SHARED}/step4_feature_config.json"
chk "${R10_CKPT}"
echo "[OK] All input files present."

cd "${STEP4_DIR}"

echo ""
echo "[1/4] Fine-tune 04D with --warm_start R10 + --w_smooth 0.1 (25 epochs) ..."
${PYTHON} 3rdJ_04D_train_2split.py --data_dir "${SHARED}" --output_dir "${VARDIR}" --checkpoint_dir "${VARDIR}/checkpoints" --fp16 --max_epochs 25 --warmup-epochs 5 --patience 15 --warm_start "${R10_CKPT}" --w_smooth 0.1 --smooth_target 2.0 --aux_loss_variant smooth > "${LOG_DIR}/s4_R10_aux_smooth_train.log" 2>&1
echo "  Train done. Log: ${LOG_DIR}/s4_R10_aux_smooth_train.log"

chk "${VARDIR}/checkpoints/best_model.pt"

echo ""
echo "[2/4] Inference (04E) ..."
${PYTHON} 3rdJ_04E_inference_2split.py --data_dir "${SHARED}" --checkpoint "${VARDIR}/checkpoints/best_model.pt" --output "${VARDIR}/augmented_diaries.csv" --temperature 0.8 > "${LOG_DIR}/s4_R10_aux_smooth_infer.log" 2>&1
echo "  Inference done. Log: ${LOG_DIR}/s4_R10_aux_smooth_infer.log"

chk "${VARDIR}/augmented_diaries.csv"

echo ""
echo "[3/4] Floating-AWARE rake (04L --floating_aware) ..."
${PYTHON} 3rdJ_04L_joint_rake_2split.py --data_dir "${SHARED}" --r5_dir "${VARDIR}" --checkpoint "${VARDIR}/checkpoints/best_model.pt" --output_dir "${RAKED}" --temperature 0.8 --floating_aware > "${LOG_DIR}/s4_R10_aux_smooth_rake.log" 2>&1
echo "  Rake done. Log: ${LOG_DIR}/s4_R10_aux_smooth_rake.log"

chk "${RAKED}/augmented_diaries.csv"

echo ""
echo "[4/4] Validate ..."
${PYTHON} 3rdJ_04_augmentationGSS_2split_val.py --step4_dir "${RAKED}" > "${LOG_DIR}/s4_R10_aux_smooth_val.log" 2>&1
echo "  Validation done. Log: ${LOG_DIR}/s4_R10_aux_smooth_val.log"

echo ""
echo "======================================================================"
echo "R10_aux_smooth pipeline complete — $(date)"
echo "  Variant output: ${VARDIR}/augmented_diaries.csv"
echo "  Raked output:   ${RAKED}/augmented_diaries.csv"
echo "  Logs:           ${LOG_DIR}/s4_R10_aux_smooth_*.log"
echo "======================================================================"
