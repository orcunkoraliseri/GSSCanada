#!/encs/bin/bash
#SBATCH --job-name=s8_w120_v2
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/w120_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/w120_%j.err

# Step 8 v2 warmup-120 retry for HighRise/MidRise warmup-convergence failures.
# Run AFTER step8_array_v2.sh finishes and any cells have < 250 hourly_meters.csv.
# The Python script dynamically walks the campaign root — no hardcoded failure list.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
CAMPAIGN_ROOT=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/campaign_N50
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers

echo "=== Step 8 v2 warmup-120 retry | campaign=$CAMPAIGN_ROOT ==="
echo "Start: $(date)"

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$WRAPPER_DIR/Energy+.idd"

cd "$STEP8_DIR"
$PYTHON step8_warmup_retry.py "$CAMPAIGN_ROOT"

EXIT=$?
echo "End: $(date)  exit=$EXIT"
exit $EXIT
