#!/encs/bin/bash
#SBATCH --job-name=06_LongForecast_C
#SBATCH --partition=pg
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/substage_c_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/substage_c_%j.out

# Step 6 — Longitudinal Forecasting Sub-stage C (Pooled Recency-Weighted + TrendEncoder)
# Empirical GPU time (v2 weekend-up-weight, job 928808 cancelled 2026-05-15 at epoch 12):
# 27.6 min/epoch joint training. ~36 epochs + pretext expected ≈ 18 hr; walltime 48 hr
# per persistent minimum (raised 2026-05-19 after two B TIMEOUTs + J5-X1b near-clip).
# Resumable: re-submit with RESUME=1 to skip pretext + W_2022_ft.pt warm start and
# continue from on-disk W_pooled_2030.pt + trend_encoder_2030.pt.
# Submit ONLY after Sub-stage B is confirmed complete and W_2022_ft.pt is saved.
#
# Expected outputs (all paths relative to BASE):
#   0_Occupancy/Models_Step6/W_pooled_2030.pt
#   0_Occupancy/Models_Step6/trend_encoder_2030.pt
#
# Gates (check log after job completes — do not submit Sub-stage D until all pass):
#   [GATE] W_pooled_2030.pt val_JS < 0.18
#   [GATE] No [FATAL] strict-load error (architecture drift between 04B_model.py and W_2022_ft.pt)
#   [GATE] AT_HOME_FINAL suppression < 5 pp (printed near end of substage C output)

. /encs/pkg/modules-5.3.1/root/init/bash
module load cuda/12.1

BASE=/speed-scratch/o_iseri/occModeling
cd "$BASE"

mkdir -p "$BASE/logs" "$BASE/0_Occupancy/Models_Step6" "$BASE/0_Occupancy/Outputs_21CEN22GSS/forecast_2030" "$BASE/0_Occupancy/Inputs_Step6"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

echo "============================================================"
echo "Step 6 Longitudinal Forecasting — stage=C"
echo "Start: $(date)"
echo "============================================================"

RESUME_FLAG=""
if [ -n "${RESUME:-}" ]; then
  RESUME_FLAG="--resume"
  echo "RESUME=1 detected — passing --resume to Sub-stage C"
fi

$PYTHON -u eSim_occ_utils/25CEN22GSS_classification/06_longitudinalForecasting.py --stage C $RESUME_FLAG

echo "============================================================"
echo "Step 6 Sub-stage C COMPLETE — $(date)"
echo "============================================================"
