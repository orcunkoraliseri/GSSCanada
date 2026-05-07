#!/encs/bin/bash
#SBATCH --job-name=I1_smoke
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=02:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/I1_smoke_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/I1_smoke_%j.err

# I1 smoke run — 10 epochs, --sample (small model, fast).
# Pass criterion: act_loss strictly decreasing across first 5 epochs AND grad_norm finite.
# If flatline or grad_norm=inf at any epoch → STOP, diagnose before full train.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

SCRIPT_DIR="$BASE/Speed_Cluster"
CONFIG_PATH="$BASE/configs/sweep_smoke_I1.yaml"
TRIAL_TAG=I1_smoke

mkdir -p "$BASE/logs" "$BASE/outputs_step4_${TRIAL_TAG}/checkpoints"

source "${SCRIPT_DIR}/config_to_env.sh" "$CONFIG_PATH"

[[ -z "$PY_ARGS" ]] && { echo "ERROR: PY_ARGS empty — config_to_env failed for $CONFIG_PATH"; exit 1; }

DATA_DIR=$(grep '^data_dir:' "$CONFIG_PATH" 2>/dev/null | sed 's/^data_dir:[[:space:]]*//')
[ -z "$DATA_DIR" ] && DATA_DIR="outputs_step4_G1"
PY_ARGS=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')

echo "============================================================"
echo "I1 smoke run: MODEL_TYPE=${MODEL_TYPE}  DATA_DIR=$DATA_DIR"
echo "PY_ARGS: $PY_ARGS"
echo "============================================================"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON -u 04D_train.py \
    --data_dir "$DATA_DIR" \
    --output_dir "outputs_step4_${TRIAL_TAG}" \
    --checkpoint_dir "outputs_step4_${TRIAL_TAG}/checkpoints" \
    --sample \
    $PY_ARGS

echo "=== I1 SMOKE COMPLETE ==="
