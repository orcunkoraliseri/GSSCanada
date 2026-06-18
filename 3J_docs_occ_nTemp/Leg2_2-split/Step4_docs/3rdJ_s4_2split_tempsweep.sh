#!/encs/bin/bash
#SBATCH --job-name=3J_s4_tsw
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_tsw_%x_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_tsw_%x_%j.err

# ── 3rdJ Step 4 — Inference-time TEMPERATURE sweep on the LOCKED R7_cap base ───
# Post-training tuning (no retrain): re-runs 04E generation at a chosen temperature
# off the EXISTING R7_cap checkpoint, then rakes (04L) at the SAME temperature, then
# validates. One T flows through both generation paths so it moves BOTH the
# rake-untouched activity channel (act30 -> G4 / S8 diversity) AND the raked binary
# channel (wrk30 -> OW5 per-person ordering). Mirrors Leg-1's 04E temperature knob.
#
# Knobs via sbatch --export:
#   TEMP  (required)  generation temperature, e.g. 0.6 / 0.7 / 0.9
#   TAG   (required)  short variant tag, e.g. t06  -> dirs R7_t06 + R7_t06_raked
#
# Submit (one line each, from Step4_docs on the cluster):
#   sbatch --job-name=R7_t06 --export=ALL,TEMP=0.6,TAG=t06 3rdJ_s4_2split_tempsweep.sh
#   sbatch --job-name=R7_t07 --export=ALL,TEMP=0.7,TAG=t07 3rdJ_s4_2split_tempsweep.sh
#   sbatch --job-name=R7_t09 --export=ALL,TEMP=0.9,TAG=t09 3rdJ_s4_2split_tempsweep.sh
# (R7_cap_raked at the default T=0.8 already exists and is the comparison anchor.)

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
SHARED="${SDIR}/outputs_step4"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

: "${TEMP:?ERROR: set TEMP via sbatch --export (e.g. TEMP=0.6)}"
: "${TAG:?ERROR: set TAG via sbatch --export (e.g. TAG=t06)}"

BASEDIR="${SHARED}/sweep/R7_cap"
CKPT="${BASEDIR}/checkpoints/best_model.pt"
VARIANT="R7_${TAG}"
VARDIR="${SHARED}/sweep/${VARIANT}"
RAKEDIR="${SHARED}/sweep/${VARIANT}_raked"

echo "===== 3J Step 4 TEMP SWEEP — ${VARIANT} (T=${TEMP}) =====" ; date
echo "SLURM_JOB_ID: $SLURM_JOB_ID  Node: $SLURMD_NODENAME"
echo "  base ckpt: $CKPT"
echo "  var dir  : $VARDIR"
echo "  rake dir : $RAKEDIR"

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 9; }; }
chk "$CKPT"
chk "${SHARED}/step4_train.pt"
echo "[OK] R7_cap checkpoint + shared tensors present."

# Variant dir reuses the R7_cap checkpoint (the rake reads <r5_dir>/checkpoints/best_model.pt).
mkdir -p "$VARDIR"
ln -sfn "${BASEDIR}/checkpoints" "${VARDIR}/checkpoints"

cd "$SDIR"

# ── 1) Re-infer at temperature T (no retrain) ─────────────────────────────────
echo ""; echo "[04E] Generating diaries for ${VARIANT} at T=${TEMP}..."
$PYTHON 3rdJ_04E_inference_2split.py --data_dir "$SHARED" --checkpoint "$CKPT" --temperature "$TEMP" --output "${VARDIR}/augmented_diaries.csv" || { echo "[ERROR] 04E failed for ${VARIANT}"; exit 13; }

# ── 2) Joint rake at the SAME temperature ─────────────────────────────────────
echo ""; echo "[04L] Raking ${VARIANT} at T=${TEMP}..."
$PYTHON 3rdJ_04L_joint_rake_2split.py --r5_dir "$VARDIR" --output_dir "$RAKEDIR" --temperature "$TEMP" || { echo "[ERROR] 04L rake failed for ${VARIANT}"; exit 14; }

# ── 3) Validate the raked output ──────────────────────────────────────────────
echo ""; echo "[04val] Validating ${VARIANT}_raked..."
$PYTHON 3rdJ_04_augmentationGSS_2split_val.py --step4_dir "$RAKEDIR" || { echo "[ERROR] validator failed for ${VARIANT}_raked"; exit 15; }

chk "${RAKEDIR}/augmented_diaries.csv"
chk "${RAKEDIR}/step4_validation_report.txt"
echo ""; echo "===== Done (${VARIANT}_raked at T=${TEMP}) =====" ; date
