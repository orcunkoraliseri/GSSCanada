#!/encs/bin/bash
#SBATCH --job-name=J6_HHC_eval
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J6_HHC_eval_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J6_HHC_eval_%j.err

# J6-HHC gate evaluation: 04E -> 04H -> 04I -> 04J.
# Gates: composite < 1.045, AT_HOME RMS <= 5.3 pp, COP max gap <= 5.0 pp, act_JS <= 0.05.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"
PY=/speed-scratch/o_iseri/envs/step4/bin/python
DATA=outputs_step4_G1
OUT=outputs_step4_J6_HHC
S3=outputs_step3

mkdir -p "$BASE/logs"

echo "=== 04E: generating synthetic diaries ==="
$PY 04E_inference.py --data_dir "$DATA" --checkpoint "$OUT/checkpoints/best_model.pt" --output "$OUT/augmented_diaries.csv"

echo "=== 04H: AT_HOME diagnostics ==="
$PY 04H_diagnostics_cpu.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_H_J6_HHC.json" --no_plot

echo "=== 04I: activity + co-presence diagnostics ==="
$PY 04I_activity_copresence_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_I_J6_HHC.json" --no_plot

echo "=== 04J: composite score ==="
$PY 04J_statistical_diagnostics.py --data_dir "$OUT" --step3_dir "$S3" --output_json "$OUT/diagnostics_J_J6_HHC.json" --no_plot

echo "=== J6_HHC EVAL COMPLETE — check $OUT/diagnostics_J_J6_HHC.json for composite ==="
