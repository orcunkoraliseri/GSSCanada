#!/encs/bin/bash
#SBATCH --job-name=J4_3_smoke
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=02:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J4_3_smoke_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J4_3_smoke_%j.err

# J4_3 smoke run — 10 epochs, --sample (small model, fast).
# Single axis: LAMBDA_LOGIC=0.1 (Alone*others penalty) only. Frozen J3 model build.
# Pass criterion: loss_logic finite and non-zero; cop channels not degenerate.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

SCRIPT_DIR="$BASE/Speed_Cluster"
CONFIG_PATH="$BASE/configs/sweep_smoke_J4_3.yaml"
TRIAL_TAG=J4_3_smoke

mkdir -p "$BASE/logs" "$BASE/outputs_step4_${TRIAL_TAG}/checkpoints"

source "${SCRIPT_DIR}/config_to_env.sh" "$CONFIG_PATH"

[[ -z "$PY_ARGS" ]] && { echo "ERROR: PY_ARGS empty — config_to_env failed for $CONFIG_PATH"; exit 1; }

DATA_DIR=$(grep '^data_dir:' "$CONFIG_PATH" 2>/dev/null | sed 's/^data_dir:[[:space:]]*//')
[ -z "$DATA_DIR" ] && DATA_DIR="outputs_step4_G1"
PY_ARGS=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')

echo "============================================================"
echo "J4_3 smoke run: MODEL_TYPE=${MODEL_TYPE}  LAMBDA_LOGIC=${LAMBDA_LOGIC}  DATA_DIR=$DATA_DIR"
echo "PY_ARGS: $PY_ARGS"
echo "============================================================"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON -u 04D_train.py \
    --data_dir "$DATA_DIR" \
    --output_dir "outputs_step4_${TRIAL_TAG}" \
    --checkpoint_dir "outputs_step4_${TRIAL_TAG}/checkpoints" \
    --sample \
    $PY_ARGS

echo "=== J4_3 SMOKE COMPLETE ==="
