#!/encs/bin/bash
#SBATCH --job-name=J3_HPT_L
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_L_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_L_%j.err

# J3-HPT-L — lambda_home: 0.9 -> 1.1 (single axis on J3 baseline)
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_HPT_L/checkpoints"

echo "=== J3_HPT_L TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_HPT_L.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_HPT_L --checkpoint_dir outputs_step4_J3_HPT_L/checkpoints $PY_ARGS_CLEAN
echo "=== J3_HPT_L TRAIN DONE ==="

echo "=== J3_HPT_L INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_HPT_L/checkpoints/best_model.pt --output outputs_step4_J3_HPT_L/augmented_diaries.csv
echo "=== J3_HPT_L INFERENCE DONE ==="

echo "=== J3_HPT_L AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_HPT_L --step3_dir "$S3" --output_json outputs_step4_J3_HPT_L/diagnostics_H_J3_HPT_L.json --no_plot
echo "=== J3_HPT_L ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_HPT_L --step3_dir "$S3" --output_json outputs_step4_J3_HPT_L/diagnostics_I_J3_HPT_L.json --no_plot
echo "=== J3_HPT_L COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_HPT_L --step3_dir "$S3" --output_json outputs_step4_J3_HPT_L/diagnostics_J3_HPT_L.json --no_plot
echo "=== J3_HPT_L DONE: check outputs_step4_J3_HPT_L/diagnostics_J3_HPT_L.json ==="
