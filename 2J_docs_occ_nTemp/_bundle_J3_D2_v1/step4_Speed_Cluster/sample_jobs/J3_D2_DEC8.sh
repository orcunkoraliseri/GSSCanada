#!/encs/bin/bash
#SBATCH --job-name=J3_D2_DEC8
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_D2_DEC8_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_D2_DEC8_%j.err

# J3_D2_DEC8 — Phase 7 T3: deeper decoder (n_dec=8, up from 6)

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_D2_DEC8/checkpoints"

echo "=== J3_D2_DEC8 TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_D2_DEC8.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_D2_DEC8 --checkpoint_dir outputs_step4_J3_D2_DEC8/checkpoints $PY_ARGS_CLEAN
echo "=== J3_D2_DEC8 TRAIN DONE ==="

echo "=== J3_D2_DEC8 INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_D2_DEC8/checkpoints/best_model.pt --output outputs_step4_J3_D2_DEC8/augmented_diaries.csv
echo "=== J3_D2_DEC8 DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_D2_DEC8 --step3_dir "$S3" --output_json outputs_step4_J3_D2_DEC8/diagnostics_H_J3_D2_DEC8.json --no_plot
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_D2_DEC8 --step3_dir "$S3" --output_json outputs_step4_J3_D2_DEC8/diagnostics_I_J3_D2_DEC8.json --no_plot
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_D2_DEC8 --step3_dir "$S3" --output_json outputs_step4_J3_D2_DEC8/diagnostics_J3_D2_DEC8.json --no_plot
echo "=== J3_D2_DEC8 DONE ==="
