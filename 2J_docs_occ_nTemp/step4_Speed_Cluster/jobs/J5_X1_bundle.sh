#!/encs/bin/bash
#SBATCH --job-name=J5_X1_bundle
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=38:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J5_X1_bundle_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J5_X1_bundle_%j.err

# J5-X1 + J5-X1b sequential bundle — binary-head re-route experiment.
# Trains J5_X1 to completion (~17h), then J5_X1b (~17h). No mid-run gates.
# Both checkpoints, 04H/04I/04J diagnostics, and composite scores come back together.
#
# WALL-TIME NOTE: All prior J-series scripts show --time=24:00:00; pg likely caps at 24h.
# If sbatch rejects --time=38:00:00 with "Invalid time specification", split into:
#   job1: jobs/J5_X1_bundle_A.sh (J5_X1 train+eval, --time=24:00:00)
#   job2: jobs/J5_X1_bundle_B.sh (J5_X1b train+eval, --time=24:00:00)
#   submit B with: sbatch --dependency=afterok:<job1_id> jobs/J5_X1_bundle_B.sh

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G1

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J5_X1/checkpoints" "$BASE/outputs_step4_J5_X1b/checkpoints"

# ─── Leg 1: J5-X1 (dec_output.detach() route) ────────────────────────────────

echo "=== J5_X1 TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "${SCRIPT_DIR}/configs/J5_X1.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_X1 --checkpoint_dir outputs_step4_J5_X1/checkpoints $PY_ARGS_CLEAN
echo "=== J5_X1 TRAIN DONE ==="

echo "=== J5_X1 INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_X1/checkpoints/best_model.pt --output outputs_step4_J5_X1/augmented_diaries.csv
echo "=== J5_X1 INFERENCE DONE ==="

echo "=== J5_X1 AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_X1 --step3_dir "$S3" --output_json outputs_step4_J5_X1/diagnostics_H_J5_X1.json --no_plot
echo "=== J5_X1 ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_X1 --step3_dir "$S3" --output_json outputs_step4_J5_X1/diagnostics_I_J5_X1.json --no_plot
echo "=== J5_X1 COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_X1 --step3_dir "$S3" --output_json outputs_step4_J5_X1/diagnostics_J5_X1.json --no_plot
echo "=== J5_X1 VALIDATION DONE ==="

# ─── Leg 2: J5-X1b (dec_output, no detach barrier) ───────────────────────────

echo "=== J5_X1b TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "${SCRIPT_DIR}/configs/J5_X1b.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J5_X1b --checkpoint_dir outputs_step4_J5_X1b/checkpoints $PY_ARGS_CLEAN
echo "=== J5_X1b TRAIN DONE ==="

echo "=== J5_X1b INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J5_X1b/checkpoints/best_model.pt --output outputs_step4_J5_X1b/augmented_diaries.csv
echo "=== J5_X1b INFERENCE DONE ==="

echo "=== J5_X1b AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J5_X1b --step3_dir "$S3" --output_json outputs_step4_J5_X1b/diagnostics_H_J5_X1b.json --no_plot
echo "=== J5_X1b ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J5_X1b --step3_dir "$S3" --output_json outputs_step4_J5_X1b/diagnostics_I_J5_X1b.json --no_plot
echo "=== J5_X1b COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J5_X1b --step3_dir "$S3" --output_json outputs_step4_J5_X1b/diagnostics_J5_X1b.json --no_plot
echo "=== J5_X1b VALIDATION DONE ==="

echo "=== BUNDLE COMPLETE: check outputs_step4_J5_X1/diagnostics_J5_X1.json and outputs_step4_J5_X1b/diagnostics_J5_X1b.json ==="
