#!/encs/bin/bash
#SBATCH --job-name=J3_DEMO_PSBLite
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/J3_DEMO_PSBLite_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/J3_DEMO_PSBLite_%j.err

# J3_DEMO_PSBLite — Arm 2 of Phase 2: J3 + restored demographics + regularized
# per-slot demographic broadcast (Linear(d_cond, 8) projection + per-slot
# cond-dropout p=0.5). Tests whether a regularized broadcast can survive paired
# with richer demographics, after raw J3-PSB (v2) crashed on Speed job 934720.
# See 04_augmentationGSS_IMP.md Progress Log "Phase 1 (J3-PSB) — SHELVED" and §5.
# Train -> infer -> 04H -> 04I -> 04J.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.8

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR="$BASE/Speed_Cluster"
S3=outputs_step3
DATA=outputs_step4_G2

mkdir -p "$BASE/logs" "$BASE/outputs_step4_J3_DEMO_PSBLite/checkpoints"

echo "=== J3_DEMO_PSBLite TRAIN START ==="
source "${SCRIPT_DIR}/config_to_env.sh" "$BASE/configs/J3_DEMO_PSBLite.yaml"
PY_ARGS_CLEAN=$(echo "$PY_ARGS" | sed 's/--data_dir[[:space:]]*[^[:space:]]*//')
$PYTHON -u 04D_train.py --data_dir "$DATA" --output_dir outputs_step4_J3_DEMO_PSBLite --checkpoint_dir outputs_step4_J3_DEMO_PSBLite/checkpoints $PY_ARGS_CLEAN
echo "=== J3_DEMO_PSBLite TRAIN DONE ==="

echo "=== J3_DEMO_PSBLite INFERENCE ==="
$PYTHON -u 04E_inference.py --data_dir "$DATA" --checkpoint outputs_step4_J3_DEMO_PSBLite/checkpoints/best_model.pt --output outputs_step4_J3_DEMO_PSBLite/augmented_diaries.csv
echo "=== J3_DEMO_PSBLite INFERENCE DONE ==="

echo "=== J3_DEMO_PSBLite AT_HOME DIAGNOSTICS ==="
$PYTHON -u 04H_diagnostics_cpu.py --data_dir outputs_step4_J3_DEMO_PSBLite --step3_dir "$S3" --output_json outputs_step4_J3_DEMO_PSBLite/diagnostics_H_J3_DEMO_PSBLite.json --no_plot
echo "=== J3_DEMO_PSBLite ACTIVITY+COP DIAGNOSTICS ==="
$PYTHON -u 04I_activity_copresence_diagnostics.py --data_dir outputs_step4_J3_DEMO_PSBLite --step3_dir "$S3" --output_json outputs_step4_J3_DEMO_PSBLite/diagnostics_I_J3_DEMO_PSBLite.json --no_plot
echo "=== J3_DEMO_PSBLite COMPOSITE SCORE ==="
$PYTHON -u 04J_statistical_diagnostics.py --data_dir outputs_step4_J3_DEMO_PSBLite --step3_dir "$S3" --output_json outputs_step4_J3_DEMO_PSBLite/diagnostics_J3_DEMO_PSBLite.json --no_plot
echo "=== J3_DEMO_PSBLite DONE: check outputs_step4_J3_DEMO_PSBLite/diagnostics_J3_DEMO_PSBLite.json ==="
