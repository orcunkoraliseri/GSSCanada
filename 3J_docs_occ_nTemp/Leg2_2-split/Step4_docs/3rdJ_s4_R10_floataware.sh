#!/encs/bin/bash
#=============================================================================
# 3rdJ_s4_R10_floataware.sh — Floating-AWARE rake (root-cause fix) + Validate
#
# Stage:    Rake (04L --floating_aware) → Validate   [NO inference — base R10_fast diaries]
# Build:    2026-06-20 (manager Opus)
# Purpose:  R10_twaware (job 980893) proved the ADDITIVE post-rake fixup
#           (--telework_aware) fixes FLOATING (0%) but inflates AT_HOME: it dumps
#           every floating work-slot into hom30=1 ON TOP of the already-satisfied
#           home quota -> G2 2015 wkdy/Sat FAIL (4.26/4.43 pp) + 10 G2 WARNs,
#           scorecard dropped 66->55 PASS.
#
#           Root cause: work-activity slots with no work-occupancy quota are
#           "floating"; the additive fixup adds home-mass beyond n_home. The fix
#           (--floating_aware): route work-act slots into the EXISTING per-slot
#           home/work quota by PRIORITY (TELEWORK==1 -> home, else -> work), then
#           non-work-act persons fill leftover quota. n_home/n_work stay EXACT ->
#           G2/OW1 preserved; floating collapses to only the irreducible
#           activity-vs-occupancy excess (the ~G4 over-production at peak), which
#           is REPORTED in provenance, never dumped to home.
#
#           Input: the ORIGINAL base R10_fast diaries (same as twaware) — isolates
#           the rake-side lever. Output dir is NEW so twaware/twcoh stay intact for
#           side-by-side comparison.
#
# SUBMIT (one line, from Step4_docs on the cluster login node):
#   sbatch /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_s4_R10_floataware.sh
#=============================================================================
#SBATCH --job-name=s4_R10_floataware
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s4_R10_floataware_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/s4_R10_floataware_%j.err

# ── Fail loudly: any step error aborts the job ────────────────────────────────
set -eo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
STEP4_DIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"
SHARED="${STEP4_DIR}/outputs_step4"
R10_DIR="${SHARED}/sweep/R10_fast"
R10_CKPT="${R10_DIR}/checkpoints/best_model.pt"
FLOAT_RAKED="${SHARED}/sweep/R10_fast_floataware_raked"
LOG_DIR="/speed-scratch/o_iseri/logs"

mkdir -p "${FLOAT_RAKED}" "${LOG_DIR}"

echo "======================================================================"
echo "Step 4 R10_floataware (floating-AWARE rake, root-cause fix) — $(date)"
echo "  Node: $(hostname)  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
echo "  data_dir:   ${SHARED}"
echo "  r5_dir:     ${R10_DIR}  (base R10_fast diaries)"
echo "  checkpoint: ${R10_CKPT}"
echo "  raked_out:  ${FLOAT_RAKED}"
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

# ── [1/2] Floating-AWARE rake (priority routing, no additive home-mass) ──────
echo ""
echo "[1/2] Running 04L joint rake with --floating_aware ..."
${PYTHON} 3rdJ_04L_joint_rake_2split.py \
    --data_dir   "${SHARED}" \
    --r5_dir     "${R10_DIR}" \
    --checkpoint "${R10_CKPT}" \
    --output_dir "${FLOAT_RAKED}" \
    --temperature 0.8 \
    --floating_aware \
    > "${LOG_DIR}/s4_R10_floataware_rake.log" 2>&1
echo "  Rake done. Log: ${LOG_DIR}/s4_R10_floataware_rake.log"

chk "${FLOAT_RAKED}/augmented_diaries.csv"

# ── [2/2] Validate ───────────────────────────────────────────────────────────
echo ""
echo "[2/2] Running validator on floating-aware raked output ..."
${PYTHON} 3rdJ_04_augmentationGSS_2split_val.py \
    --step4_dir "${FLOAT_RAKED}" \
    > "${LOG_DIR}/s4_R10_floataware_val.log" 2>&1
echo "  Validation done. Log: ${LOG_DIR}/s4_R10_floataware_val.log"

echo ""
echo "======================================================================"
echo "R10_floataware pipeline complete — $(date)"
echo "  Raked output: ${FLOAT_RAKED}/augmented_diaries.csv"
echo "  Logs:         ${LOG_DIR}/s4_R10_floataware_{rake,val}.log"
echo "======================================================================"
