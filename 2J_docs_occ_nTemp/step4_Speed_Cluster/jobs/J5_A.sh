#!/encs/bin/bash
#SBATCH --job-name=J5_A
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=24:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_A_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_A_%j.err

# J5-A single run — drop home_label_smooth (0.05 -> 0.0).
# JSeriesHybrid build byte-identical to J3; only home_label_smooth differs.
# Attacks home_head sigma=0.0 collapse / 0.198 BCE algebraic floor.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_A/checkpoints"

echo "=== J5_A TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J5_A.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_A --checkpoint_dir outputs_step4_J5_A/checkpoints $PY_ARGS_CLEAN
echo "=== J5_A TRAIN DONE ==="

echo "=== J5_A INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_A/checkpoints/best_model.pt --output outputs_step4_J5_A/augmented_diaries.csv
echo "=== J5_A INFERENCE DONE ==="

echo "=== J5_A AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_A --step3_dir "$S3" --output_json outputs_step4_J5_A/diagnostics_H_J5_A.json --no_plot
echo "=== J5_A ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_A --step3_dir "$S3" --output_json outputs_step4_J5_A/diagnostics_I_J5_A.json --no_plot
echo "=== J5_A COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_A --step3_dir "$S3" --output_json outputs_step4_J5_A/diagnostics_J5_A.json --no_plot
echo "=== J5_A DONE: check outputs_step4_J5_A/diagnostics_J5_A.json ==="
