#!/encs/bin/bash
#SBATCH --job-name=MDLM_G1_regen
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/MDLM_G1_regen_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/MDLM_G1_regen_%j.err

# Step 4K PREP: Regenerate MDLM_G1 augmented_diaries.csv via 04E (no training).
# MDLM_G1 was trained on outputs_step4_G2 (confirmed from job 936694 log).
# model_type=MDLM → MDLMHybrid from 04B_model_MDLM.py; N_DENOISE_STEPS=16 (default).
# Expect 192,183 rows (64,061 respondents × 3 strata).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python

DATA=outputs_step4_G2
CKPT=outputs_step4_full/MDLM_G1/checkpoints/best_model.pt
OUT=outputs_step4_full/MDLM_G1/augmented_diaries.csv

mkdir -p "$BASE/logs"

echo "=== MDLM_G1 REGEN START ==="
echo "  data_dir  : $DATA"
echo "  checkpoint: $CKPT"
echo "  output    : $OUT"

$PY 04E_inference.py --data_dir "$DATA" --checkpoint "$CKPT" --output "$OUT"

echo "=== MDLM_G1 REGEN DONE — check $OUT ==="
