#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=14:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_%j.err

# Step 6 — Longitudinal Forecasting (2005–2030)
# Estimated GPU time: ~8–13 hrs (A100/V100); 14 hr walltime for headroom.
#
# BEFORE SUBMITTING: verify module versions on Speed with `module avail` and
# replace the placeholder versions below with the actual available versions.
# Run locally first: py 06_longitudinalForecasting.py --smoke --stage A

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
echo "Step 6 Longitudinal Forecasting — stage=A"
echo "Start: $(date)"
echo "============================================================"

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage A

echo "============================================================"
echo "Step 6 COMPLETE — $(date)"
echo "============================================================"
