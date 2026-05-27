#!/encs/bin/bash
#SBATCH --job-name=diag_HTime
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/diag_H_Time_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/diag_H_Time_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
TAG=H_Time
OUT="$BASE/outputs_step4_${TAG}"
DATA="$BASE/outputs_step4_G1"
S3="$BASE/outputs_step3"

mkdir -p "$BASE/logs" "$OUT"

echo "============================================================"
echo "Diagnostic pipeline: $TAG"
echo "  checkpoint: $OUT/checkpoints/best_model.pt"
echo "  data_dir:   $DATA"
echo "============================================================"

for f in step4_train.pt step4_val.pt step4_test.pt step4_all_meta.csv step4_feature_config.json training_pairs.pt; do
    if [ -f "$DATA/$f" ] && [ ! -e "$OUT/$f" ]; then
        ln -s "$DATA/$f" "$OUT/$f"
        echo "  symlinked $f"
    fi
done

if [ ! -f "$OUT/checkpoints/best_model.pt" ]; then
    echo "ERROR: checkpoint not found at $OUT/checkpoints/best_model.pt"
    exit 1
fi

echo ""
echo "--- 04E Inference ---"
$PYTHON -u 04E_inference.py --data_dir "$OUT" --checkpoint "$OUT/checkpoints/best_model.pt" --output "$OUT/augmented_diaries.csv" --temperature 0.8
echo "--- 04E DONE ---"

if [ ! -f "$OUT/augmented_diaries.csv" ]; then
    echo "ERROR: augmented_diaries.csv not generated"
    exit 1
fi

echo ""
echo "--- 04H AT_HOME diagnostics ---"
$PYTHON -u 04H_diagnostics_cpu.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_v4.json" --no_plot
echo "--- 04H DONE ---"

echo ""
echo "--- 04I Activity/Copresence diagnostics ---"
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_v4_actcop.json" --no_plot
echo "--- 04I DONE ---"

echo ""
echo "--- 04J Statistical diagnostics ---"
$PYTHON -u 04J_statistical_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_v4_statistical.json" --n_bootstrap 1000 --no_plot
echo "--- 04J DONE ---"

echo ""
echo "============================================================"
echo "DIAGNOSTIC PIPELINE COMPLETE: $TAG"
echo "Results:"
ls -lh "$OUT"/diagnostics_*.json 2>/dev/null
echo "============================================================"
