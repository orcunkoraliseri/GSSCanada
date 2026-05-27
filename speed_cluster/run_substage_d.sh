#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast_D
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/substage_d_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/substage_d_%j.out

# Step 6 — Longitudinal Forecasting Sub-stage D (Phase i only: 2022 Backcasting)
# Inference only (no training). ~37,008 rows × self-reconstruction forward pass on GPU.
# Estimated GPU time: 5–15 min. Walltime 48 hr per persistent SLURM minimum (2026-05-19).
# Submit ONLY after Sub-stage C confirmed complete (W_pooled_2030.pt saved).
#
# Phase ii (2030 forecast) is NOT IMPLEMENTED yet — blocked on scenario_2030_features.csv.
#
# Expected outputs (paths relative to BASE):
#   0_Occupancy/Outputs_21CEN22GSS/forecast_2030/reconstructed_2022_diaries.csv
#
# Gates (check log after job completes):
#   [GATE] No [FATAL] strict-load error
#   [GATE] JS < 0.10 per stratum (WD, Sat, Sun)
#   [GATE] WD AT_HOME |obs - pred| <= 2.0 pp
#   Log line on success: [SUBSTAGE_D_PHASE_I_COMPLETE]

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.1

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

mkdir -p "$BASE/logs" "$BASE/0_Occupancy/Models_Step6" "$BASE/0_Occupancy/Outputs_21CEN22GSS/forecast_2030"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "============================================================"
echo "Step 6 Longitudinal Forecasting — stage=D (Phase i backcasting)"
echo "Start: $(date)"
echo "============================================================"

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage D

echo "============================================================"
echo "Step 6 Sub-stage D Phase i COMPLETE — $(date)"
echo "============================================================"
