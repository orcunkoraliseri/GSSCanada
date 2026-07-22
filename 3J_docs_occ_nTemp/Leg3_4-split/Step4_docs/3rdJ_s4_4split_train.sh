#!/encs/bin/bash
#SBATCH --job-name=3J_s4_train
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_4split_train_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_4split_train_%j.err

# ── 3rdJ Step 4 (Leg-3, 4-split): FULL orchestrator ───────────────────────────
# assembly -> pairs -> Phase 1 (warmup) -> Phase 2 (joint) -> inference.
# Three-GSS-head (AT_HOME + AT_WORK + AT_RETAIL) J3 Hybrid AR-Encoder.
# Does NOT auto-run the validator (Leg-2 gotcha) — submit
# 3rdJ_s4_4split_valonly.sh explicitly afterwards.
#
# ⚠️ RESOLVED 2026-07-19 (was ESCALATE): warm-start source = Leg-2's real
# production sweep run R5_lr1e4 (outputs_step4/sweep/R5_lr1e4/checkpoints/
# best_model.pt; d_model=256, d_cond=120, n_aux=11, val_js=0.0183) — the old
# Leg2_2-split/.../checkpoints/best_model.pt path was a smoke-scale artifact.
# See 3rdJ_s4_4split_warmup.sh header + Progress Log (2026-07-19) in
# 3rdJ_04_augmentationGSS_4split.md.
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs
# Command:  sbatch 3rdJ_s4_4split_train.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs"
S3DIR="${SDIR}/../Step3_docs/outputs_step3"
LEG2_CKPT="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4 Train (Leg-3, 4-split — full pipeline) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "Python: $($PYTHON --version 2>&1)"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

$PYTHON -c "import pandas, numpy, torch, scipy, sklearn" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet pandas numpy scipy scikit-learn 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${S3DIR}/hetus_30min.csv"
chk "${S3DIR}/copresence_30min.csv"
chk "${S3DIR}/work_30min.csv"
chk "${S3DIR}/retail_30min.csv"
chk "${LEG2_CKPT}"
echo "[OK] All 4 Step-3 input files + Leg-2 warm-start checkpoint present."

mkdir -p "${SDIR}/outputs_step4/checkpoints"
cd "$SDIR"

# ── 1. Data assembly ──────────────────────────────────────────────────────────
echo ""; echo "[04A] Dataset assembly (retail channel)..."
$PYTHON 3rdJ_04A_assembly_4split.py || { echo "[ERROR] 04A failed"; exit 11; }

# ── 2. Training pairs ─────────────────────────────────────────────────────────
echo ""; echo "[04C] Building day-type pairs..."
$PYTHON 3rdJ_04C_pairs_4split.py || { echo "[ERROR] 04C failed"; exit 12; }

# ── 3. Phase 1: retail_head-only warmup ───────────────────────────────────────
echo ""; echo "[04D --phase warmup] Training retail_head only (5ep, lr=1e-3)..."
$PYTHON 3rdJ_04D_train_4split.py --phase warmup --warm_start "${LEG2_CKPT}" --fp16 \
    || { echo "[ERROR] 04D (warmup) failed"; exit 13; }
chk "${SDIR}/outputs_step4/checkpoints/warmup_checkpoint.pt"

# ── 4. Phase 2: joint fine-tune (PCGrad + fixed alpha) ────────────────────────
echo ""; echo "[04D --phase joint] Training all params (15ep, lr=1e-4, PCGrad ON)..."
$PYTHON 3rdJ_04D_train_4split.py --phase joint --fp16 \
    || { echo "[ERROR] 04D (joint) failed"; exit 13; }
chk "${SDIR}/outputs_step4/checkpoints/best_model.pt"

# ── 5. Inference ───────────────────────────────────────────────────────────────
echo ""; echo "[04E] Generating augmented diaries (Deltas F/G)..."
$PYTHON 3rdJ_04E_inference_4split.py \
    || { echo "[ERROR] 04E failed"; exit 14; }

# ── Check expected outputs ────────────────────────────────────────────────────
for F in checkpoints/warmup_checkpoint.pt checkpoints/best_model.pt \
         step4_training_log_warmup.csv step4_training_log_joint.csv \
         augmented_diaries.csv isr_summary.json; do
    chk "${SDIR}/outputs_step4/${F}"
done
echo "[OK] All expected Step-4 (Leg-3) outputs present."
echo "     NOTE: validator NOT run here (Leg-2 gotcha) — submit 3rdJ_s4_4split_valonly.sh explicitly."

echo ""; echo "===== Done ====="
date
