#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast_D2
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/substage_d2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/substage_d2_%j.out

# Step 6 — Longitudinal Forecasting Sub-stage D Phase ii (2030 Forward Forecast)
# Inference only (no training). Loads scenario_2030_features.csv (37,008 rows)
# and generates 2030_synthetic_diaries.csv via W_pooled_2030 + TrendEncoder.
# Estimated GPU time: 5–15 min. Walltime 48 hr per persistent SLURM minimum (2026-05-19).
#
# Prerequisites (must exist on cluster before submitting):
#   0_Occupancy/Models_Step6/W_pooled_2030.pt
#   0_Occupancy/Models_Step6/trend_encoder_2030.pt
#   0_Occupancy/Inputs_Step6/scenario_2030_features.csv
#   0_Occupancy/Outputs_21CEN22GSS/forecast_2030/DRIFT_MATRIX_1015.csv
#   0_Occupancy/Outputs_21CEN22GSS/forecast_2030/DRIFT_MATRIX_1522.csv
#
# Expected outputs:
#   0_Occupancy/Outputs_21CEN22GSS/forecast_2030/2030_synthetic_diaries.csv
#
# Gates (check log after job completes):
#   [GATE] Row count ~37,008 (±100)
#   [GATE] WD AT_HOME in 65–90%
#   Log line on success: [SUBSTAGE_D_PHASE_II_COMPLETE]

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.1

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

mkdir -p "$BASE/logs" "$BASE/0_Occupancy/Inputs_Step6" "$BASE/0_Occupancy/Outputs_21CEN22GSS/forecast_2030"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "============================================================"
echo "Step 6 Longitudinal Forecasting — stage=D2 (Phase ii 2030 forecast)"
echo "Start: $(date)"
echo "============================================================"

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage D2

echo "============================================================"
echo "Step 6 Sub-stage D Phase ii COMPLETE — $(date)"
echo "============================================================"
