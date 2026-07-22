#!/encs/bin/bash
#SBATCH --job-name=3J_s4_rake
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/3J_s4_4split_rake_%j.out
#SBATCH --error=/speed-scratch/o_iseri/logs/3J_s4_4split_rake_%j.err

# ── 3rdJ Step 4L (Leg-3, 4-split): Joint AT_HOME + AT_WORK + AT_RETAIL ────────
# post-hoc raking (Delta H of 3rdJ_04_augmentationGSS_4split.md). GPU needed
# for model.generate() (activity AR arm + the three occupancy heads).
#
# Points at seed 3's winning checkpoint (outputs_step4/seed_3/), the shared
# data_dir (outputs_step4/), and writes the raked pool to a NEW dir
# (outputs_step4/sweep/seed_3_raked3/) — never overwrites the seed_3 source.
#
# Submit from: /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs
# Command:  sbatch 3rdJ_s4_4split_rake.sh

. /encs/pkg/modules-5.3.1/root/init/bash

SDIR="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step4_docs"
PYTHON="/speed-scratch/o_iseri/envs/step4/bin/python"

DATADIR="${SDIR}/outputs_step4"
R5DIR="${SDIR}/outputs_step4/seed_3"
OUTDIR="${SDIR}/outputs_step4/sweep/seed_3_raked3"

echo "===== 3J Step 4L (Leg-3, 4-split) — Joint 3-Channel Rake =====" ; date
echo "SLURM_JOB_ID: $SLURM_JOB_ID  Node: $SLURMD_NODENAME"
echo "  data dir:    $DATADIR"
echo "  seed_3 dir:  $R5DIR"
echo "  output  dir: $OUTDIR"

$PYTHON -c "import pandas, numpy, torch" 2>/dev/null || {
    echo "[PRECHECK] Installing missing packages..."
    $PYTHON -m pip install --quiet pandas numpy torch 2>&1 | tail -5
}

chk() { [ -f "$1" ] || { echo "[ERROR] Missing: $1"; exit 1; }; }
chk "${R5DIR}/checkpoints/best_model.pt"
chk "${R5DIR}/augmented_diaries.csv"
chk "${DATADIR}/step4_train.pt"
echo "[OK] seed_3 checkpoint + augmented_diaries.csv + shared tensors present."

mkdir -p "$OUTDIR"

cd "$SDIR"
$PYTHON 3rdJ_04L_joint_rake_4split.py \
    --data_dir "$DATADIR" \
    --r5_dir "$R5DIR" \
    --output_dir "$OUTDIR" \
    --checkpoint "${R5DIR}/checkpoints/best_model.pt"
EXIT_RAKE=$?
echo "[DONE] Rake exit code: $EXIT_RAKE" ; date
exit $EXIT_RAKE
