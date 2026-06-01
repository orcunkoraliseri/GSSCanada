#!/encs/bin/bash
#SBATCH --job-name=PP_H1
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/PP_H1_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/PP_H1_%j.err

# Entity embedding (90-dim -> 32-dim bottleneck) + F8 mask bounds.
set -e
. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

export MDLM_MASK_LO=0.01
export MDLM_MASK_HI=0.99
export USE_ENTITY_EMBED=1
export ENTITY_EMBED_DIM=32

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2_sample10
TAG=PP_H1
OUT=outputs_step4_full/${TAG}

mkdir -p "$BASE/logs" "$BASE/${OUT}/checkpoints"

echo "=== ${TAG} TRAIN START (entity_embed=1 + F8 mask) ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/sample_configs/${TAG}.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir "$OUT" --checkpoint_dir "${OUT}/checkpoints" $PY_ARGS_CLEAN
echo "=== ${TAG} TRAIN DONE ==="

echo "=== ${TAG} INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint "${OUT}/checkpoints/best_model.pt" --output "${OUT}/augmented_diaries.csv"
echo "=== ${TAG} DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_H_${TAG}.json" --no_plot
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_I_${TAG}.json" --no_plot
$PYTHON -u 04J_statistical_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "${OUT}/diagnostics_${TAG}.json" --no_plot
echo "=== ${TAG} DONE ==="
