#!/encs/bin/bash
#SBATCH --job-name=workcal_test
#SBATCH --partition=pg
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/workcal_test_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/workcal_test_%j.err

# Step 4K: Work-calibration diagnostic (CPU-only, no GPU needed).
# Reads 4 model augmented_diaries.csv files one at a time; writes
# diag_workcal_compare.json and prints the comparison summary table.
# Must run AFTER job_step4_MDLM_G1_regen completes (use --dependency=afterok:<regen_jobid>).

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S3=outputs_step3

mkdir -p "$BASE/logs"

echo "=== workcal_test START ==="
$PY 04K_work_calibration_test.py --base_dir "$BASE" --step3_dir "$BASE/$S3" --output_json "$BASE/diag_workcal_compare.json"
echo "=== workcal_test DONE — check $BASE/diag_workcal_compare.json ==="
