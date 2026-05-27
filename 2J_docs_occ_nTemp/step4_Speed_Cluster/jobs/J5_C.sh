#!/encs/bin/bash
#SBATCH --job-name=J5_C
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_C_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_C_%j.err

# J5-C single run — linear-chain CRF + Viterbi on Arm-1 activity logits.
# J3 architecture preserved; psi_pair (14x14) added on Arm-1 unaries. CRF NLL at training,
# Viterbi at inference. Targets transition-rate-ratio residual (157.95x synthetic/observed).
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_C/checkpoints"

echo "=== J5_C TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J5_C.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_C --checkpoint_dir outputs_step4_J5_C/checkpoints $PY_ARGS_CLEAN
echo "=== J5_C TRAIN DONE ==="

echo "=== J5_C INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_C/checkpoints/best_model.pt --output outputs_step4_J5_C/augmented_diaries.csv
echo "=== J5_C INFERENCE DONE ==="

echo "=== J5_C AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_C --step3_dir "$S3" --output_json outputs_step4_J5_C/diagnostics_H_J5_C.json --no_plot
echo "=== J5_C ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_C --step3_dir "$S3" --output_json outputs_step4_J5_C/diagnostics_I_J5_C.json --no_plot
echo "=== J5_C COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_C --step3_dir "$S3" --output_json outputs_step4_J5_C/diagnostics_J5_C.json --no_plot
echo "=== J5_C DONE: check outputs_step4_J5_C/diagnostics_J5_C.json ==="
