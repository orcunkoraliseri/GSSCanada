#!/encs/bin/bash
#SBATCH --job-name=step8_w120_retry
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/w120_retry_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/w120_retry_%j.err

# Stage 1 follow-up: warmup-120 retry for persistent E+ failures.
# Run AFTER step8_array.sh finishes.
# Targets any cell/job where eplusout.end is missing or incomplete.
# HighRise/MidRise warmup oscillation is the primary expected failure mode.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
CAMPAIGN_ROOT=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/campaign_N50
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers

echo "=== Step 8 warmup-120 retry | campaign=$CAMPAIGN_ROOT ==="
echo "Start: $(date)"

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$WRAPPER_DIR/Energy+.idd"

cd "$STEP8_DIR"
$PYTHON step8_warmup_retry.py "$CAMPAIGN_ROOT"

echo "End: $(date)"
