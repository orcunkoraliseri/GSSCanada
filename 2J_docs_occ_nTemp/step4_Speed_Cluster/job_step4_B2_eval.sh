#!/encs/bin/bash
#SBATCH --job-name=B2_eval
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/B2_eval_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/B2_eval_%j.err

# Phase 8B-2 (G4_NAT_COP) archival gate evaluation: 04E -> 04H -> 04I -> 04J.
# Gates: composite < 1.045, AT_HOME RMS <= 5.3 pp, COP max gap <= 5.0 pp, act_JS <= 0.05.
# The whole bet: NAT COP branch eliminates AR cascading -> COP gap should drop vs G4 (19-23 pp).

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python
DATA=outputs_step4_G1
OUT=outputs_step4_B2
S3=outputs_step3

mkdir -p "$BASE/logs"

echo "=== 04E: generating synthetic diaries ==="
$PY 04E_inference.py \
    --data_dir "$DATA" \
    --checkpoint "$OUT/checkpoints/best_model.pt" \
    --output "$OUT/augmented_diaries.csv"

echo "=== 04H: AT_HOME diagnostics ==="
$PY 04H_diagnostics_cpu.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_H_B2.json" \
    --no_plot

echo "=== 04I: activity + co-presence diagnostics ==="
$PY 04I_activity_copresence_diagnostics.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_I_B2.json" \
    --no_plot

echo "=== 04J: composite score ==="
$PY 04J_statistical_diagnostics.py \
    --data_dir "$OUT" \
    --step3_dir "$S3" \
    --output_json "$OUT/diagnostics_J_B2.json" \
    --no_plot

echo "=== B2 EVAL COMPLETE — check $OUT/diagnostics_J_B2.json for composite ==="
