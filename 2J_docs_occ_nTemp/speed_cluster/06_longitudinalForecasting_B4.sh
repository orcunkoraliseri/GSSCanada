#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast_B4
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=72:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_B4_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/06_LongForecast_B4_%j.err

# Step 6 — Sub-stage B4: Phase 4 resume from W_2015_ft.pt.
# Loads W_2015_ft.pt (saved by job 931841 before TIMEOUT) and runs only Phase 4
# on the 4-cycle pool to produce W_2022_ft.pt. AT_HOME hom_boost hardcoded to 1.0
# (Phase 3 AT_HOME_CHECK PASSED at 0.8pp suppression in the prior B run).
# Walltime 72h per persistent rule (24h minimum) + Phase 4 alone was ~15h for 38
# epochs in job 931841; full early-stop expected at ~epoch 42-43 → ~17-18h.

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
echo "Step 6 Longitudinal Forecasting — stage=B4 (Phase 4 resume)"
echo "Start: $(date)"
echo "============================================================"

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage B4

echo "============================================================"
echo "Step 6 Sub-stage B4 COMPLETE — $(date)"
echo "============================================================"
