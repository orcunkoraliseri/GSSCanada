#!/encs/bin/bash
#SBATCH --job-name=3J_s4_joint
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --array=0-4
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_4split_joint_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_4split_joint_%A_%a.err

# ── 3rdJ Step 4 (Leg-3, 4-split): Phase 2 — joint fine-tune + inference ───────
# 5-SEED SWEEP (array 0-4, one SEED per array task). Requires
# outputs_step4/checkpoints/warmup_checkpoint.pt (run 3rdJ_s4_4split_warmup.sh
# first) — this SINGLE shared Phase-1 checkpoint is the --warm_start source
# for ALL 5 seeds. Runs 04D --phase joint (15 epochs, ALL params trainable,
# AdamW lr=1e-4, PCGrad ON, fixed alpha, exclusivity loss ON, early stopping
# on the gate-set proxy, patience 10), THEN 04E inference (Deltas F/G: nucleus
# decode, -ln49 retail calibration, min-dwell, exclusivity projection). Does
# NOT run the validator (separate job).
#
# Per-seed output isolation: each array task writes to its own subdir
# outputs_step4/seed_${SEED}/ (via 04D's --output_dir/--checkpoint_dir and
# 04E's --checkpoint/--output), so the 5 seeds never clobber one another.
# --data_dir stays pointed at the SHARED outputs_step4/ (step4_feature_config
# .json, step4_train.pt/step4_val.pt/step4_test.pt, training_pairs.pt, etc.
# are shared inputs, not per-seed).
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs
# Command:  sbatch 3rdJ_s4_4split_joint.sh      (submits all 5 seeds at once)

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

# SEED: from the array index; fall back to 42 if run outside an array context.
SEED="${SLURM_ARRAY_TASK_ID:-42}"

# Shared Phase-1 warm-start checkpoint (ORIGINAL location, same for all seeds).
WARM_START="${SDIR}/outputs_step4/checkpoints/warmup_checkpoint.pt"

# Per-seed output isolation.
SEED_OUT="${SDIR}/outputs_step4/seed_${SEED}"
SEED_CKPT="${SEED_OUT}/checkpoints"

echo "===== 3J Step 4 — Leg-3 4-split — Phase 2 (joint) + Inference — SEED=${SEED} ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID   Node: $SLURMD_NODENAME"
echo "SEED_OUT:  $SEED_OUT"
echo "SEED_CKPT: $SEED_CKPT"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${WARM_START}"
chk "${SDIR}/outputs_step4/step4_train.pt"
echo "[OK] Phase-1 checkpoint + baseline tensors present."

mkdir -p "$SEED_OUT" "$SEED_CKPT"

cd "$SDIR"

# ── Phase 2: joint fine-tune (explicit --warm_start; per-seed output/checkpoint dirs) ──
echo ""; echo "[04D --phase joint] Training all params (15ep, lr=1e-4, PCGrad ON)  seed=${SEED}..."
$PYTHON 3rdJ_04D_train_4split.py --phase joint --fp16 \
    --seed "$SEED" \
    --data_dir "${SDIR}/outputs_step4" \
    --output_dir "$SEED_OUT" \
    --checkpoint_dir "$SEED_CKPT" \
    --warm_start "$WARM_START" \
    || { echo "[ERROR] 04D (joint) failed"; exit 13; }

chk "${SEED_CKPT}/best_model.pt"

# ── Inference ──────────────────────────────────────────────────────────────────
echo ""; echo "[04E] Generating augmented diaries (Deltas F/G)  seed=${SEED}..."
$PYTHON 3rdJ_04E_inference_4split.py \
    --data_dir "${SDIR}/outputs_step4" \
    --checkpoint "${SEED_CKPT}/best_model.pt" \
    --output "${SEED_OUT}/augmented_diaries.csv" \
    || { echo "[ERROR] 04E failed"; exit 14; }

for F in checkpoints/best_model.pt step4_training_log_joint.csv augmented_diaries.csv isr_summary.json; do
    chk "${SEED_OUT}/${F}"
done
echo "[OK] All expected Step-4 (Leg-3) outputs present for seed=${SEED}."
echo "     NOTE: validator NOT run here — submit 3rdJ_s4_4split_valonly.sh explicitly."

echo ""; echo "===== Done (joint + inference) — SEED=${SEED} ====="
date
