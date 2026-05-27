#!/encs/bin/bash
#SBATCH --job-name=J3_NEIGH
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_NEIGH_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_NEIGH_%j.err

# J3_NEIGH — Phase 3 (Lever B): tighter K=5 EXACT_COLS (+ATTSCH +POWST) and
# K-mean soft AT_HOME target across all K neighbors. Stock J3 architecture
# (composite 0.6355 baseline); changes are entirely in 04C + 04D pair-loader.
# Phase 2 (J3_DEMO + J3_DEMO_PSBLite) cancelled 2026-05-22 at ep 41 because
# home_BCE flatlined at ~0.385 — neither demographics (Lever A) nor regularized
# PSB-Lite (Lever C-i) moved binary heads; both arms appeared bounded by the
# K=5 neighbor-disagreement JS floor of 0.1888 that this run directly attacks.
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_NEIGH/checkpoints"

echo "=== J3_NEIGH TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_NEIGH.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_NEIGH --checkpoint_dir outputs_step4_J3_NEIGH/checkpoints $PY_ARGS_CLEAN
echo "=== J3_NEIGH TRAIN DONE ==="

echo "=== J3_NEIGH INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_NEIGH/checkpoints/best_model.pt --output outputs_step4_J3_NEIGH/augmented_diaries.csv
echo "=== J3_NEIGH INFERENCE DONE ==="

echo "=== J3_NEIGH AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_NEIGH --step3_dir "$S3" --output_json outputs_step4_J3_NEIGH/diagnostics_H_J3_NEIGH.json --no_plot
echo "=== J3_NEIGH ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_NEIGH --step3_dir "$S3" --output_json outputs_step4_J3_NEIGH/diagnostics_I_J3_NEIGH.json --no_plot
echo "=== J3_NEIGH COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_NEIGH --step3_dir "$S3" --output_json outputs_step4_J3_NEIGH/diagnostics_J3_NEIGH.json --no_plot
echo "=== J3_NEIGH DONE: check outputs_step4_J3_NEIGH/diagnostics_J3_NEIGH.json ==="
