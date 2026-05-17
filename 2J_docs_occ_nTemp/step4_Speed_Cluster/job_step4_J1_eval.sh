#!/encs/bin/bash
#SBATCH --job-name=J1_eval
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=4:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J1_eval_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J1_eval_%j.err

# J1 archival gate evaluation: 04E -> 04H -> 04I -> 04J.
# Submit after full train completes. Gate: composite < 1.045, AT_HOME <=5.3 pp,
# Spouse <=5 pp, act_JS <=0.05. Compare vs H_Tanh baseline (1.319 / 5.19 / -3.07 / 0.029).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python
OUT=outputs_step4_J1
S3=outputs_step3

mkdir -p "$BASE/logs"

echo "=== 04E: generating synthetic diaries ==="
$PY 04E_inference.py \
    --data_dir outputs_step4_G1 \
    --checkpoint "$OUT/checkpoints/best_model.pt" \
    --output "$OUT/augmented_diaries.csv"

echo "=== 04H: AT_HOME diagnostics ==="
$PY 04H_diagnostics_cpu.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_H_J1.json" \
    --no_plot

echo "=== 04I: activity + co-presence diagnostics ==="
$PY 04I_activity_copresence_diagnostics.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_I_J1.json" \
    --no_plot

echo "=== 04J: composite score ==="
$PY 04J_statistical_diagnostics.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_J_J1.json" \
    --no_plot

echo "=== J1 EVAL COMPLETE — check $OUT/diagnostics_J_J1.json for composite ==="
