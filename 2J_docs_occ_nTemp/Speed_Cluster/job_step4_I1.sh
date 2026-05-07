#!/encs/bin/bash
#SBATCH --job-name=I1
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=24:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/I1_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/I1_%j.err

# I1 full training run — faithful encoder-only port (I-series).
# Submit only after smoke pass (10 epochs, act_loss decreasing, grad_norm finite).
# No --fp16: disabled at dispatch level for MODEL_TYPE=I1.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

SCRIPT_DIR="$BASE/Speed_Cluster"
CONFIG_PATH="$BASE/configs/I1.yaml"
TRIAL_TAG=I1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_${TRIAL_TAG}/checkpoints"

source "${SCRIPT_DIR}/config_to_env.sh" "$CONFIG_PATH"

[[ -z "$PY_ARGS" ]] && { echo "ERROR: PY_ARGS empty — config_to_env failed for $CONFIG_PATH"; exit 1; }

DATA_DIR=$(grep '^data_dir:' "$CONFIG_PATH" 2>/dev/null | sed 's/^data_dir:[[:space:]]*//')
[ -z "$DATA_DIR" ] && DATA_DIR="outputs_step4_G1"
PY_ARGS=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')

echo "============================================================"
echo "I1 full run: MODEL_TYPE=${MODEL_TYPE}  DATA_DIR=$DATA_DIR"
echo "PY_ARGS: $PY_ARGS"
echo "============================================================"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON -u 04D_train.py \
    --data_dir "$DATA_DIR" \
    --output_dir "outputs_step4_${TRIAL_TAG}" \
    --checkpoint_dir "outputs_step4_${TRIAL_TAG}/checkpoints" \
    $PY_ARGS

echo "=== I1 FULL RUN COMPLETE ==="
