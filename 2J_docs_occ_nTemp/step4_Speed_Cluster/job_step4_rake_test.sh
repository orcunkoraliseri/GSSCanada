#!/encs/bin/bash
#SBATCH --job-name=rake_test
#SBATCH --partition=pg
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/rake_test_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/rake_test_%j.err

# Step 4L: Joint raking diagnostic (CPU-only, no GPU).
# Reads 4 model augmented_diaries.csv files, rakes AT_HOME + COP jointly,
# writes diag_rake_compare.json and augmented_diaries_raked.csv for J3.

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python

mkdir -p "$BASE/logs"

echo "=== rake_test START ==="
$PY 04L_joint_rake_test.py --base_dir "$BASE" --step3_dir "$BASE/outputs_step3" --output_json "$BASE/diag_rake_compare.json"
echo "=== rake_test DONE — check $BASE/diag_rake_compare.json ==="
