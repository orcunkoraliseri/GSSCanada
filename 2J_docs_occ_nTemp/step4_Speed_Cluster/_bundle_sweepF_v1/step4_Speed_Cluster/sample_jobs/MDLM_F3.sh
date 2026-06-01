#!/encs/bin/bash
#SBATCH --job-name=MDLM_F3
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/MDLM_F3_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/MDLM_F3_%j.err

# Stage F Trial 3: mask_schedule=cosine (default uniform).

set -e

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

export MDLM_MASK_SCHEDULE=cosine

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2_sample10
TAG=MDLM_F3
OUT=outputs_step4_full/${TAG}

mkdir -p "$BASE/logs" "$BASE/${OUT}/checkpoints"

echo "=== ${TAG} TRAIN START (MDLM_MASK_SCHEDULE=cosine) ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/sample_configs/${TAG}.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir "$OUT" --checkpoint_dir "${OUT}/checkpoints" $PY_ARGS_CLEAN
echo "=== ${TAG} TRAIN DONE ==="

echo "=== ${TAG} INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint "${OUT}/checkpoints/best_model.pt" --output "${OUT}/augmented_diaries.csv"
echo "=== ${TAG} INFERENCE DONE ==="

echo "=== ${TAG} DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_H_${TAG}.json" --no_plot
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_I_${TAG}.json" --no_plot
$PYTHON -u 04J_statistical_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_${TAG}.json" --no_plot
echo "=== ${TAG} DONE ==="
