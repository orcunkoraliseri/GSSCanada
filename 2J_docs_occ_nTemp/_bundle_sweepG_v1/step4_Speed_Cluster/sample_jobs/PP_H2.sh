#!/encs/bin/bash
#SBATCH --job-name=PP_H2
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/PP_H2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/PP_H2_%j.err

# K=10 neighbors (default K=5) + F8 mask bounds.
# Creates symlink data dir and regenerates training pairs with K=10 before training.
set -e
. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

export MDLM_MASK_LO=0.01
export MDLM_MASK_HI=0.99
export KNN_K=10

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2_sample10_K10
TAG=PP_H2
OUT=outputs_step4_full/${TAG}

mkdir -p "$BASE/logs" "$BASE/${OUT}/checkpoints"

# Create K10 data dir with symlinks to original sample data + regenerate pairs
if [ ! -d "$DATA" ]; then
    mkdir -p "$DATA"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_train.pt" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_val.pt" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_test.pt" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_all_meta.csv" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_train_meta.csv" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_val_meta.csv" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_test_meta.csv" "$DATA/"
    ln -sf "$BASE/outputs_step4_G2_sample10/step4_feature_config.json" "$DATA/"
    echo "  Regenerating training pairs with KNN_K=10..."
    $PYTHON 04C_training_pairs.py --sample_dir "$DATA"
fi

echo "=== ${TAG} TRAIN START (K=10 + F8 mask) ==="
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
