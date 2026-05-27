#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast_B
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_B_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_B_%j.err

# Step 6 — Longitudinal Forecasting Sub-stage B (Progressive Fine-Tuning)
# Estimated GPU time: ~3–5 hrs; 10 hr walltime for headroom.
# Submit ONLY after Sub-stage A job completes and W_2005.pt is confirmed saved.
#
# BEFORE SUBMITTING: verify module versions on Speed with `module avail` and
# replace the placeholder versions below with the actual available versions.

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.1

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

mkdir -p "$BASE/logs" \
         "$BASE/0_Occupancy/Models_Step6" \
         "$BASE/0_Occupancy/Outputs_21CEN22GSS/forecast_2030" \
         "$BASE/0_Occupancy/Inputs_Step6"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "============================================================"
echo "Step 6 Longitudinal Forecasting — stage=B"
echo "Start: $(date)"
echo "============================================================"

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage B

echo "============================================================"
echo "Step 6 Sub-stage B COMPLETE — $(date)"
echo "============================================================"
