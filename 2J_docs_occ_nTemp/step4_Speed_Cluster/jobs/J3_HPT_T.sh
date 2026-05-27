#!/encs/bin/bash
#SBATCH --job-name=J3_HPT_T
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_T_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_HPT_T_%j.err

# J3-HPT-T — inference temperature: 0.8 -> 0.65 on existing J3 checkpoint.
# No training; reuses outputs_step4_J3/checkpoints/best_model.pt.
# Infer -> 04H -> 04I -> 04J. ~30 min total.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_HPT_T"

echo "=== J3_HPT_T INFERENCE (temperature=0.65 on J3 checkpoint) ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3/checkpoints/best_model.pt --output outputs_step4_J3_HPT_T/augmented_diaries.csv --temperature 0.65
echo "=== J3_HPT_T INFERENCE DONE ==="

echo "=== J3_HPT_T AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_HPT_T --step3_dir "$S3" --output_json outputs_step4_J3_HPT_T/diagnostics_H_J3_HPT_T.json --no_plot
echo "=== J3_HPT_T ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_HPT_T --step3_dir "$S3" --output_json outputs_step4_J3_HPT_T/diagnostics_I_J3_HPT_T.json --no_plot
echo "=== J3_HPT_T COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_HPT_T --step3_dir "$S3" --output_json outputs_step4_J3_HPT_T/diagnostics_J3_HPT_T.json --no_plot
echo "=== J3_HPT_T DONE: check outputs_step4_J3_HPT_T/diagnostics_J3_HPT_T.json ==="
