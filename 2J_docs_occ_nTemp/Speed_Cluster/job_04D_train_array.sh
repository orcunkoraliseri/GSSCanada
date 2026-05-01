#!/encs/bin/bash
#SBATCH --job-name=04D_array
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40Gb
#SBATCH --time=2-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04D_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04D_%A_%a.err

# Parametrized array job — resolves TRIAL_TAG from TRIAL_TAGS (colon-separated)
# exported by submit_step4_array.sh via --export=ALL,TRIAL_TAGS=...
# SWEEP_SMOKE=1 adds --sample flag (smoke mode: 5 epochs, small model, CPU-friendly check)

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

# Resolve trial tag for this array slot
IFS=':' read -ra _TAGS <<< "$TRIAL_TAGS"
TRIAL_TAG="${_TAGS[$SLURM_ARRAY_TASK_ID]}"
echo "============================================================"
echo "Array slot $SLURM_ARRAY_TASK_ID → TRIAL_TAG=$TRIAL_TAG"
echo "============================================================"

mkdir -p "$BASE/logs" "$BASE/outputs_step4_${TRIAL_TAG}/checkpoints"

# Load env vars + PY_ARGS from YAML config (yq if available, else python fallback)
# BASH_SOURCE[0] resolves to SLURM spool dir at runtime — use BASE-relative path instead.
SCRIPT_DIR="$BASE/Speed_Cluster"
CONFIG_PATH="$BASE/configs/${TRIAL_TAG}.yaml"
source "${SCRIPT_DIR}/config_to_env.sh" "$CONFIG_PATH"

# Smoke mode: override to --sample (5 epochs, small model, ~5 min)
if [ "${SWEEP_SMOKE:-0}" = "1" ]; then
    PY_ARGS="$PY_ARGS --sample"
fi

# Extract data_dir directly from YAML via grep/sed — yq-independent, same approach as
# submit_step4_array.sh uses for TRIAL_DATA_DIR. Guarantees correct data_dir regardless
# of yq version or config_to_env PY_ARGS emission failures.
DATA_DIR=$(grep '^data_dir:' "$CONFIG_PATH" 2>/dev/null | sed 's/^data_dir:[[:space:]]*//')
[ -z "$DATA_DIR" ] && DATA_DIR="outputs_step4"

# Strip --data_dir from PY_ARGS to avoid duplicate flag (argparse takes last value, but
# cleaner to pass it exactly once via the explicit flag below).
PY_ARGS=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')

echo "  Env: AUX_STRATUM_HEAD=${AUX_STRATUM_HEAD:-0}  AUX_STRATUM_LAMBDA=${AUX_STRATUM_LAMBDA:-0.1}  SPOUSE_NEG_WEIGHT=${SPOUSE_NEG_WEIGHT:-1.0}"
echo "  DATA_DIR: $DATA_DIR"
echo "  PY_ARGS: $PY_ARGS"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON -u 04D_train.py \
    --data_dir    "$DATA_DIR" \
    --output_dir  "outputs_step4_${TRIAL_TAG}" \
    --checkpoint_dir "outputs_step4_${TRIAL_TAG}/checkpoints" \
    $PY_ARGS

echo "=== 04D COMPLETE: TRIAL_TAG=$TRIAL_TAG ==="
