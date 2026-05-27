#!/encs/bin/bash
#SBATCH --job-name=J5_X2
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=24:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_X2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_X2_%j.err

# J5-X2 single run — config fix for J5-X1's act_JS regression.
# Reuses J5_X1 MODEL_TYPE branch (dec_output.detach() route); only lambda_home=0.9 differs.
# Train -> infer -> 04H -> 04I -> 04J (same diagnostic chain as J5-X1 bundle leg).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_X2/checkpoints"

echo "=== J5_X2 TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J5_X2.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_X2 --checkpoint_dir outputs_step4_J5_X2/checkpoints $PY_ARGS_CLEAN
echo "=== J5_X2 TRAIN DONE ==="

echo "=== J5_X2 INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_X2/checkpoints/best_model.pt --output outputs_step4_J5_X2/augmented_diaries.csv
echo "=== J5_X2 INFERENCE DONE ==="

echo "=== J5_X2 AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_X2 --step3_dir "$S3" --output_json outputs_step4_J5_X2/diagnostics_H_J5_X2.json --no_plot
echo "=== J5_X2 ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_X2 --step3_dir "$S3" --output_json outputs_step4_J5_X2/diagnostics_I_J5_X2.json --no_plot
echo "=== J5_X2 COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_X2 --step3_dir "$S3" --output_json outputs_step4_J5_X2/diagnostics_J5_X2.json --no_plot
echo "=== J5_X2 DONE: check outputs_step4_J5_X2/diagnostics_J5_X2.json ==="
