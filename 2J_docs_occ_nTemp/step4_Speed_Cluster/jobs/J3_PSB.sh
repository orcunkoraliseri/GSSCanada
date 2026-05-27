#!/encs/bin/bash
#SBATCH --job-name=J3_PSB
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_PSB_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_PSB_%j.err

# J3-PSB — J3 + per-slot demographic broadcast on encoder slot tokens.
# Phase 1 of 04_augmentationGSS_IMP.md. Architecture-only single-axis change vs J3.
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_PSB/checkpoints"

echo "=== J3_PSB TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_PSB.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_PSB --checkpoint_dir outputs_step4_J3_PSB/checkpoints $PY_ARGS_CLEAN
echo "=== J3_PSB TRAIN DONE ==="

echo "=== J3_PSB INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_PSB/checkpoints/best_model.pt --output outputs_step4_J3_PSB/augmented_diaries.csv
echo "=== J3_PSB INFERENCE DONE ==="

echo "=== J3_PSB AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_PSB --step3_dir "$S3" --output_json outputs_step4_J3_PSB/diagnostics_H_J3_PSB.json --no_plot
echo "=== J3_PSB ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_PSB --step3_dir "$S3" --output_json outputs_step4_J3_PSB/diagnostics_I_J3_PSB.json --no_plot
echo "=== J3_PSB COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_PSB --step3_dir "$S3" --output_json outputs_step4_J3_PSB/diagnostics_J3_PSB.json --no_plot
echo "=== J3_PSB DONE: check outputs_step4_J3_PSB/diagnostics_J3_PSB.json ==="
