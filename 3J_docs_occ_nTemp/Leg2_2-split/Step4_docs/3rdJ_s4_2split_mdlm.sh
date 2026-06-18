#!/encs/bin/bash
#=============================================================================
# 3rdJ_s4_2split_mdlm.sh — MDLM Ablation: Train → Infer → Rake → Validate
#
# Stage:    LOCAL BUILD ONLY — DO NOT SUBMIT UNTIL MANAGER CONFIRMS
# Build:    2026-06-18 (local, CPU smoke-tested)
# Author:   Claude Sonnet 4.6 (employee builder)
#
# SUBMIT COMMANDS (paste on cluster login node when ready):
# ─────────────────────────────────────────────────────────────────────────────
#   ARM A — MDLM ablation (this script):
#       sbatch /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_s4_2split_mdlm.sh
#
#   ARM B — AR baseline on 10% (for apples-to-apples comparison; uses existing 04D):
#       sbatch --job-name=s4_AR_s10 -p pg --gres=gpu:1 --mem=64G --time=48:00:00 \
#         --output=/speed-scratch/o_iseri/logs/s4_AR_s10_%j.out \
#         --wrap="cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs && \
#           /speed-scratch/o_iseri/venv/bin/python 3rdJ_04D_train_2split.py \
#             --data_dir /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4_s10 \
#             --output_dir /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/AR_s10 \
#             --checkpoint_dir /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/AR_s10/checkpoints \
#             --max_epochs 100 --patience 15 --warmup-epochs 20 --lr 5e-5 --fp16 \
#             > /speed-scratch/o_iseri/logs/s4_AR_s10_train.log 2>&1 && \
#           /speed-scratch/o_iseri/venv/bin/python 3rdJ_04E_inference_2split.py \
#             --data_dir /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4_s10 \
#             --checkpoint /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/AR_s10/checkpoints/best_model.pt \
#             --output /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/AR_s10/augmented_diaries_AR.csv \
#             > /speed-scratch/o_iseri/logs/s4_AR_s10_infer.log 2>&1"
#
# NOTE: Submit BOTH arms at the same time so they run in parallel.
#       MDLM inference is ~32x slower per respondent than AR on the same GPU.
#       Expected wall time at 10%: MDLM ~8-12h, AR ~2-4h.  Both well within 48h.
#=============================================================================
#SBATCH --job-name=s4_MDLM_s10
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s4_MDLM_s10_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/s4_MDLM_s10_%j.err

# ── Paths ────────────────────────────────────────────────────────────────────
STEP4_DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/venv/bin/python"
DATA_S10="${STEP4_DIR}/outputs_step4_s10"
SWEEP_OUT="${STEP4_DIR}/outputs_step4/sweep/MDLM_s10"
SWEEP_RAKED="${STEP4_DIR}/outputs_step4/sweep/MDLM_s10_raked"
CKPT_DIR="${SWEEP_OUT}/checkpoints_mdlm"
LOG_DIR="/speed-scratch/o_iseri/logs"

mkdir -p "${SWEEP_OUT}" "${SWEEP_RAKED}" "${CKPT_DIR}" "${LOG_DIR}"

echo "======================================================================"
echo "Step 4 MDLM Ablation — $(date)"
echo "  Node: $(hostname)  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "  data_s10:  ${DATA_S10}"
echo "  sweep_out: ${SWEEP_OUT}"
echo "======================================================================"

# ── Module / environment checks ──────────────────────────────────────────────
echo "[0/4] Checking Python environment ..."
${PYTHON} -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
${PYTHON} -c "import numpy, pandas, sklearn; print('numpy pandas sklearn OK')"

# ── Step 1: Make 10% subsample (idempotent — skips if dst already exists) ────
echo ""
echo "[1/4] Building 10% subsample (outputs_step4_s10) ..."
if [ -f "${DATA_S10}/step4_train.pt" ]; then
    echo "  outputs_step4_s10 already exists — skipping 04Q."
else
    cd "${STEP4_DIR}"
    ${PYTHON} 3rdJ_04Q_make_s10_sample.py \
        --frac 0.10 --seed 42 \
        > "${LOG_DIR}/s4_MDLM_04Q.log" 2>&1
    echo "  04Q done. Log: ${LOG_DIR}/s4_MDLM_04Q.log"
fi

# ── Step 2: Train MDLM ────────────────────────────────────────────────────────
echo ""
echo "[2/4] Training MDLM on 10% subsample ..."
cd "${STEP4_DIR}"
${PYTHON} 3rdJ_04D_mdlm_train_2split.py \
    --data_dir       "${DATA_S10}" \
    --output_dir     "${SWEEP_OUT}" \
    --checkpoint_dir "${CKPT_DIR}" \
    --max_epochs 100 \
    --patience 15 \
    --warmup-epochs 20 \
    --lr 5e-5 \
    --d_model 256 \
    --n_enc_layers 6 \
    --mdlm_mask_schedule cosine \
    --mdlm_denoise_steps 16 \
    --fp16 \
    > "${LOG_DIR}/s4_MDLM_train.log" 2>&1
echo "  Training done. Log: ${LOG_DIR}/s4_MDLM_train.log"

# ── Step 3: MDLM Inference ────────────────────────────────────────────────────
echo ""
echo "[3/4] Running MDLM inference ..."
${PYTHON} 3rdJ_04E_mdlm_infer_2split.py \
    --data_dir    "${DATA_S10}" \
    --checkpoint  "${CKPT_DIR}/best_model.pt" \
    --output      "${SWEEP_OUT}/augmented_diaries_MDLM.csv" \
    --mdlm_denoise_steps 16 \
    --mdlm_mask_schedule cosine \
    --temperature 0.8 \
    > "${LOG_DIR}/s4_MDLM_infer.log" 2>&1
echo "  Inference done. Log: ${LOG_DIR}/s4_MDLM_infer.log"

# ── Step 4: Rake ─────────────────────────────────────────────────────────────
echo ""
echo "[4a/4] Running joint rake (04L) ..."
${PYTHON} 3rdJ_04L_joint_rake_2split.py \
    --input  "${SWEEP_OUT}/augmented_diaries_MDLM.csv" \
    --output "${SWEEP_RAKED}/augmented_diaries_MDLM_raked.csv" \
    > "${LOG_DIR}/s4_MDLM_rake.log" 2>&1
echo "  Rake done. Log: ${LOG_DIR}/s4_MDLM_rake.log"

# ── Step 5: Validate ─────────────────────────────────────────────────────────
echo ""
echo "[4b/4] Running validator (04_augmentationGSS_2split_val) ..."
${PYTHON} 3rdJ_04_augmentationGSS_2split_val.py \
    --input "${SWEEP_RAKED}/augmented_diaries_MDLM_raked.csv" \
    > "${LOG_DIR}/s4_MDLM_val.log" 2>&1
echo "  Validation done. Log: ${LOG_DIR}/s4_MDLM_val.log"

echo ""
echo "======================================================================"
echo "MDLM ablation pipeline complete — $(date)"
echo "  Results: ${SWEEP_RAKED}"
echo "  Logs:    ${LOG_DIR}/s4_MDLM_*.log"
echo "======================================================================"
