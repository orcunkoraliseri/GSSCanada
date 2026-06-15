#!/encs/bin/bash
#SBATCH --job-name=3J_s4_sw
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_sw_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_sw_%x_%j.err

# ── 3rdJ Step 4: HPT sweep — single-axis variants off the baseline ────────────
# REUSES the baseline assembly (step4_*.pt + config + training_pairs.pt in
# outputs_step4/) — does NOT re-run 04A/04C. Only re-trains (04D) + re-infers
# (04E) into a per-variant subdir outputs_step4/sweep/$VARIANT/.
#
# Knobs arrive as env vars via `sbatch --export`. Every knob defaults to the
# baseline value, so an unset knob == baseline behaviour.
#   VARIANT          (required) subdir + log tag, e.g. R1_workpw5
#   WORK_POS_WEIGHT  AT_WORK BCE pos_weight        (default: auto from config)
#   COP_POS_WEIGHT   co-presence pos_weight factor (default: 0 = off)
#   LAMBDA_DIV       diversity-loss weight         (default: 0.1)
#   WEIGHT_MODE      uw | slaw | equal             (default: uw)
#   LR               learning rate                 (default: 5e-5)
#   DMODEL           transformer width             (default: 256)
#
# Submit (one line each, from Step4_docs on the cluster):
#   sbatch --job-name=R1_workpw5 --export=ALL,VARIANT=R1_workpw5,WORK_POS_WEIGHT=5.0 3rdJ_s4_2split_sweep.sh
#   sbatch --job-name=R2_div02   --export=ALL,VARIANT=R2_div02,LAMBDA_DIV=0.2        3rdJ_s4_2split_sweep.sh
#   sbatch --job-name=R3_slaw    --export=ALL,VARIANT=R3_slaw,WEIGHT_MODE=slaw       3rdJ_s4_2split_sweep.sh
#   sbatch --job-name=R4_cop1    --export=ALL,VARIANT=R4_cop1,COP_POS_WEIGHT=1.0     3rdJ_s4_2split_sweep.sh
#   sbatch --job-name=R5_lr1e4   --export=ALL,VARIANT=R5_lr1e4,LR=1e-4               3rdJ_s4_2split_sweep.sh
#   sbatch --job-name=R6_d384    --export=ALL,VARIANT=R6_d384,DMODEL=384             3rdJ_s4_2split_sweep.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
SHARED="${SDIR}/outputs_step4"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

: "${VARIANT:?ERROR: set VARIANT via sbatch --export (e.g. VARIANT=R1_workpw5)}"
VARDIR="${SHARED}/sweep/${VARIANT}"

# Defaults = baseline
export WEIGHT_MODE="${WEIGHT_MODE:-uw}"
export LAMBDA_DIV="${LAMBDA_DIV:-0.1}"
export COP_POS_WEIGHT="${COP_POS_WEIGHT:-0}"
LR="${LR:-5e-5}"
DMODEL="${DMODEL:-256}"
# WORK_POS_WEIGHT left unset => 04D uses the config (auto) value
[ -n "${WORK_POS_WEIGHT:-}" ] && export WORK_POS_WEIGHT

echo "===== 3J Step 4 SWEEP — ${VARIANT} ====="
date
echo "SLURM_JOB_ID: $SLURM_JOB_ID   Node: $SLURMD_NODENAME"
echo "  WEIGHT_MODE=$WEIGHT_MODE  LAMBDA_DIV=$LAMBDA_DIV  COP_POS_WEIGHT=$COP_POS_WEIGHT"
echo "  WORK_POS_WEIGHT=${WORK_POS_WEIGHT:-auto}  LR=$LR  DMODEL=$DMODEL"
echo "  VARDIR=$VARDIR"

# ── Require the baseline assembly (do NOT re-run 04A/04C) ──────────────────────
chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1 — run the baseline train (3rdJ_s4_2split_train.sh) first"; exit 9; }; }
chk "${SHARED}/step4_train.pt"
chk "${SHARED}/step4_val.pt"
chk "${SHARED}/training_pairs.pt"
chk "${SHARED}/step4_feature_config.json"
echo "[OK] Shared baseline assembly present."

mkdir -p "${VARDIR}/checkpoints"
cd "$SDIR"

# ── Train (reads shared tensors, writes to per-variant dir) ────────────────────
echo ""; echo "[04D] Training variant ${VARIANT}..."
$PYTHON 3rdJ_04D_train_2split.py --data_dir "$SHARED" --output_dir "$VARDIR" \
        --checkpoint_dir "${VARDIR}/checkpoints" --lr "$LR" --d_model "$DMODEL" --fp16 \
    || { echo "[ERROR] 04D failed for ${VARIANT}"; exit 13; }

# ── Inference (shared data, variant checkpoint + output) ───────────────────────
echo ""; echo "[04E] Generating diaries for ${VARIANT}..."
$PYTHON 3rdJ_04E_inference_2split.py --data_dir "$SHARED" \
        --checkpoint "${VARDIR}/checkpoints/best_model.pt" \
        --output "${VARDIR}/augmented_diaries.csv" \
    || { echo "[ERROR] 04E failed for ${VARIANT}"; exit 14; }

chk "${VARDIR}/checkpoints/best_model.pt"
chk "${VARDIR}/augmented_diaries.csv"
echo "[OK] ${VARIANT} complete: ${VARDIR}"

echo ""; echo "===== Done (${VARIANT}) ====="
date
