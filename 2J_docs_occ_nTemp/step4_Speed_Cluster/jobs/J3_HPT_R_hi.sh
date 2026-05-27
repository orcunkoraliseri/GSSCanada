#!/encs/bin/bash
#SBATCH --job-name=J3_HPT_R_hi
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_R_hi_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_R_hi_%j.err

# J3-HPT-R_hi — lr: 5e-5 -> 7e-5 (single axis on J3 baseline)
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_HPT_R_hi/checkpoints"

echo "=== J3_HPT_R_hi TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_HPT_R_hi.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_HPT_R_hi --checkpoint_dir outputs_step4_J3_HPT_R_hi/checkpoints $PY_ARGS_CLEAN
echo "=== J3_HPT_R_hi TRAIN DONE ==="

echo "=== J3_HPT_R_hi INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_HPT_R_hi/checkpoints/best_model.pt --output outputs_step4_J3_HPT_R_hi/augmented_diaries.csv
echo "=== J3_HPT_R_hi INFERENCE DONE ==="

echo "=== J3_HPT_R_hi AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_HPT_R_hi --step3_dir "$S3" --output_json outputs_step4_J3_HPT_R_hi/diagnostics_H_J3_HPT_R_hi.json --no_plot
echo "=== J3_HPT_R_hi ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_HPT_R_hi --step3_dir "$S3" --output_json outputs_step4_J3_HPT_R_hi/diagnostics_I_J3_HPT_R_hi.json --no_plot
echo "=== J3_HPT_R_hi COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_HPT_R_hi --step3_dir "$S3" --output_json outputs_step4_J3_HPT_R_hi/diagnostics_J3_HPT_R_hi.json --no_plot
echo "=== J3_HPT_R_hi DONE: check outputs_step4_J3_HPT_R_hi/diagnostics_J3_HPT_R_hi.json ==="
