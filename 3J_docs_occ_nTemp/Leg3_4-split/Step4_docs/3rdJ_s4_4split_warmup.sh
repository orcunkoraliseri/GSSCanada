#!/encs/bin/bash
#SBATCH --job-name=3J_s4_warmup
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_4split_warmup_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_4split_warmup_%j.err

# ── 3rdJ Step 4 (Leg-3, 4-split): Phase 1 — retail_head warmup only ───────────
# Assembles data if missing (04A/04C), then runs 04D --phase warmup (5 epochs,
# ONLY retail_head trainable, AdamW lr=1e-3, no PCGrad, no exclusivity loss).
# Output: outputs_step4/checkpoints/warmup_checkpoint.pt — the required
# --warm_start input for 3rdJ_s4_4split_joint.sh.
#
# ⚠️ RESOLVED 2026-07-19 (was ESCALATE): the previous LEG2_CKPT path below
#   (Leg2_2-split/Step4_docs/outputs_step4/checkpoints/best_model.pt) was a
#   smoke-scale artifact, NOT the production model. The manager identified the
#   correct warm-start source = Leg-2's real production sweep run R5_lr1e4:
#   outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt
#   (d_model=256, d_cond=120, n_aux=11, val_js=0.0183). Verified present on
#   cluster 2026-07-19 (52,940,735 bytes, matches local copy exactly).
#   Warm-start compat PROVEN at state_dict level (local smoke, 2026-07-19):
#   256/261 tensors load clean by name+shape; only slot_linear.weight
#   mismatches (256,43)->(256,44) (expected: retail is a new n_aux column,
#   11->12) and retail_head.* (4 tensors) are missing-in-ckpt (new head) —
#   both fall back to random-init as intended. 0 unexpected/unused keys.
#   d_cond matches exactly (120=120) so proj_demo/cls_mlp load clean too.
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs
# Command:  sbatch 3rdJ_s4_4split_warmup.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs"
S3DIR="${SDIR}/../Step3_docs/outputs_step3"
LEG2_CKPT="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

echo "===== 3J Step 4 — Leg-3 4-split — Phase 1 (warmup) ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "Python: $($PYTHON --version 2>&1)"
$PYTHON -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1

$PYTHON -c "import pandas, numpy, torch, scipy, sklearn" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages into step4 env..."
    $PYTHON -m pip install --quiet pandas numpy scipy scikit-learn 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${LEG2_CKPT}"
echo "[OK] Leg-2 warm-start checkpoint present: ${LEG2_CKPT}"

mkdir -p "${SDIR}/outputs_step4/checkpoints"
cd "$SDIR"

# ── Assembly (idempotent — only needed the first time on this cluster copy) ──
if [ ! -f "${SDIR}/outputs_step4/step4_train.pt" ]; then
    echo ""; echo "[04A] Dataset assembly (retail channel)..."
    chk "${S3DIR}/hetus_30min.csv"; chk "${S3DIR}/copresence_30min.csv"
    chk "${S3DIR}/work_30min.csv";  chk "${S3DIR}/retail_30min.csv"
    $PYTHON 3rdJ_04A_assembly_4split.py || { echo "[ERROR] 04A failed"; exit 11; }
    echo ""; echo "[04C] Building day-type pairs..."
    $PYTHON 3rdJ_04C_pairs_4split.py || { echo "[ERROR] 04C failed"; exit 12; }
else
    echo "[SKIP] outputs_step4/step4_train.pt already present — assuming 04A/04C already run."
fi

# ── Phase 1: retail_head-only warmup ──────────────────────────────────────────
echo ""; echo "[04D --phase warmup] Training retail_head only (5ep, lr=1e-3)..."
$PYTHON 3rdJ_04D_train_4split.py --phase warmup --warm_start "${LEG2_CKPT}" --fp16 \
    || { echo "[ERROR] 04D (warmup) failed"; exit 13; }

chk "${SDIR}/outputs_step4/checkpoints/warmup_checkpoint.pt"
echo "[OK] Phase-1 output present: outputs_step4/checkpoints/warmup_checkpoint.pt"
echo "     Next: sbatch 3rdJ_s4_4split_joint.sh"

echo ""; echo "===== Done (warmup) ====="
date
