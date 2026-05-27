#!/encs/bin/bash
#SBATCH --job-name=J5_F
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_F_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_F_%j.err

# J5-F single run — joint encoder supervision + AR decoder for activity only.
# Encoder shaped by all three losses (CE + 2x BCE); Arm-2 fusion + .detach() barrier dropped.
# Train -> infer -> 04H -> 04I -> 04J (standard J-series diagnostic chain).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_F/checkpoints"

echo "=== J5_F TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J5_F.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_F --checkpoint_dir outputs_step4_J5_F/checkpoints $PY_ARGS_CLEAN
echo "=== J5_F TRAIN DONE ==="

echo "=== J5_F INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_F/checkpoints/best_model.pt --output outputs_step4_J5_F/augmented_diaries.csv
echo "=== J5_F INFERENCE DONE ==="

echo "=== J5_F AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_F --step3_dir "$S3" --output_json outputs_step4_J5_F/diagnostics_H_J5_F.json --no_plot
echo "=== J5_F ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_F --step3_dir "$S3" --output_json outputs_step4_J5_F/diagnostics_I_J5_F.json --no_plot
echo "=== J5_F COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_F --step3_dir "$S3" --output_json outputs_step4_J5_F/diagnostics_J5_F.json --no_plot
echo "=== J5_F DONE: check outputs_step4_J5_F/diagnostics_J5_F.json ==="
