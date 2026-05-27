#!/encs/bin/bash
#SBATCH --job-name=J5_B
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=24:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_B_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_B_%j.err

# J5-B single run — hierarchical chain-rule cop head.
# JSeriesHybrid build identical to J3 (arm2_act_proj path); chain rule applied via J5_B branches in
# compute_loss (04D_train.py) and infer (04B_model.py). Inference safety mask dropped.
# Predecessor archived to archive/04B_model_pre_J5_B.py before edit (per feedback_archive_predecessor).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_B/checkpoints"

echo "=== J5_B TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J5_B.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_B --checkpoint_dir outputs_step4_J5_B/checkpoints $PY_ARGS_CLEAN
echo "=== J5_B TRAIN DONE ==="

echo "=== J5_B INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_B/checkpoints/best_model.pt --output outputs_step4_J5_B/augmented_diaries.csv
echo "=== J5_B INFERENCE DONE ==="

echo "=== J5_B AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_B --step3_dir "$S3" --output_json outputs_step4_J5_B/diagnostics_H_J5_B.json --no_plot
echo "=== J5_B ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_B --step3_dir "$S3" --output_json outputs_step4_J5_B/diagnostics_I_J5_B.json --no_plot
echo "=== J5_B COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_B --step3_dir "$S3" --output_json outputs_step4_J5_B/diagnostics_J5_B.json --no_plot
echo "=== J5_B DONE: check outputs_step4_J5_B/diagnostics_J5_B.json ==="
