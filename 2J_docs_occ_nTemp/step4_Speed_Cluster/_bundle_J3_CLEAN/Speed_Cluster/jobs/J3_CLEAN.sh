#!/encs/bin/bash
#SBATCH --job-name=J3_CLEAN
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_CLEAN_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_CLEAN_%j.err

# J3_CLEAN — Phase 4 (Lever C cheap-fixes stack): ACTIVITY_BOOSTS=0 + LAMBDA_TRANS=0.05
# + MARG_MODE=per_cs + per-channel cop pos_weight (rare positives) + Spouse down-weight.
# Stock J3 architecture (composite 0.6355 baseline). Lever B reverted (J3-NEIGH
# 935306 failed; K-mean soft AT_HOME decalibrated sigmoid head). Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_CLEAN/checkpoints"

echo "=== J3_CLEAN TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_CLEAN.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_CLEAN --checkpoint_dir outputs_step4_J3_CLEAN/checkpoints $PY_ARGS_CLEAN
echo "=== J3_CLEAN TRAIN DONE ==="

echo "=== J3_CLEAN INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_CLEAN/checkpoints/best_model.pt --output outputs_step4_J3_CLEAN/augmented_diaries.csv
echo "=== J3_CLEAN INFERENCE DONE ==="

echo "=== J3_CLEAN AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_CLEAN --step3_dir "$S3" --output_json outputs_step4_J3_CLEAN/diagnostics_H_J3_CLEAN.json --no_plot
echo "=== J3_CLEAN ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_CLEAN --step3_dir "$S3" --output_json outputs_step4_J3_CLEAN/diagnostics_I_J3_CLEAN.json --no_plot
echo "=== J3_CLEAN COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_CLEAN --step3_dir "$S3" --output_json outputs_step4_J3_CLEAN/diagnostics_J3_CLEAN.json --no_plot
echo "=== J3_CLEAN DONE: check outputs_step4_J3_CLEAN/diagnostics_J3_CLEAN.json ==="
