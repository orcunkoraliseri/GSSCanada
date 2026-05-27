#!/encs/bin/bash
#SBATCH --job-name=J3_DEMO
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_DEMO_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_DEMO_%j.err

# J3_DEMO — Arm 1 of Phase 2: stock J3 + restored GSS demographics
# (POWST/ATTSCH/MODE). No architecture change vs J3 baseline (composite 0.6355);
# only the input tensor bundle changes. Tests whether demographics alone close
# the gates without any model edit. See 04_augmentationGSS_IMP.md §5.
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_DEMO/checkpoints"

echo "=== J3_DEMO TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_DEMO.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_DEMO --checkpoint_dir outputs_step4_J3_DEMO/checkpoints $PY_ARGS_CLEAN
echo "=== J3_DEMO TRAIN DONE ==="

echo "=== J3_DEMO INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_DEMO/checkpoints/best_model.pt --output outputs_step4_J3_DEMO/augmented_diaries.csv
echo "=== J3_DEMO INFERENCE DONE ==="

echo "=== J3_DEMO AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_DEMO --step3_dir "$S3" --output_json outputs_step4_J3_DEMO/diagnostics_H_J3_DEMO.json --no_plot
echo "=== J3_DEMO ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_DEMO --step3_dir "$S3" --output_json outputs_step4_J3_DEMO/diagnostics_I_J3_DEMO.json --no_plot
echo "=== J3_DEMO COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_DEMO --step3_dir "$S3" --output_json outputs_step4_J3_DEMO/diagnostics_J3_DEMO.json --no_plot
echo "=== J3_DEMO DONE: check outputs_step4_J3_DEMO/diagnostics_J3_DEMO.json ==="
