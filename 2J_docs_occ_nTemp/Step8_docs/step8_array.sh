#!/encs/bin/bash
#SBATCH --job-name=step8_corrected
#SBATCH --partition=ps
#SBATCH --array=0-23
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/step8_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/step8_%A_%a.err

# Step 8 corrected full campaign — 24-cell SLURM array.
# One task = one (archetype x city) cell = 50 HH x 5 years = 250 annual E+ runs.
# E+ runs inside nrel/energyplus:24.2.0 Singularity container via wrapper scripts.
# Resume-safe: skips cells that already have 250 hourly_meters.csv files.

ARCHETYPES=(
    "SingleD"      "SingleD"      "SingleD"      "SingleD"      "SingleD"      "SingleD"
    "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling"
    "MidRise"      "MidRise"      "MidRise"      "MidRise"      "MidRise"      "MidRise"
    "HighRise"     "HighRise"     "HighRise"     "HighRise"     "HighRise"     "HighRise"
)
CITIES=(
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
)

ARCH="${ARCHETYPES[$SLURM_ARRAY_TASK_ID]}"
CITY="${CITIES[$SLURM_ARRAY_TASK_ID]}"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
CAMPAIGN_ROOT=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/campaign_N50
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers
IDD=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd

mkdir -p "$CAMPAIGN_ROOT" /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs

echo "=== Step 8 corrected | task=$SLURM_ARRAY_TASK_ID arch=$ARCH city=$CITY ==="
echo "Start: $(date)"

# Pre-flight
$PYTHON -c "import eppy" 2>/dev/null || { echo "ERROR: eppy missing; run: $PYTHON -m pip install eppy"; exit 1; }
[ -f "$IDD" ]                   || { echo "ERROR: Energy+.idd not found at $IDD"; exit 1; }
[ -x "$WRAPPER_DIR/energyplus" ] || { echo "ERROR: energyplus wrapper not executable"; exit 1; }

# Log schedule CSV checksums for run provenance
for yr in 2005 2010 2015 2022 2030; do
    CSV=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/BEM_Schedules_${yr}.csv
    echo "MD5 BEM_Schedules_${yr}.csv: $(md5sum $CSV 2>/dev/null || echo MISSING)"
done

# Resume: skip if cell already complete (250 = 50 HH * 5 years)
CELL_DIR="${CAMPAIGN_ROOT}/${ARCH}__${CITY}"
EXPECTED=250
FOUND=$(find "$CELL_DIR" -name "hourly_meters.csv" 2>/dev/null | wc -l)
if [ "$FOUND" -ge "$EXPECTED" ]; then
    echo "Cell already complete ($FOUND/$EXPECTED hourly_meters.csv). Skipping."
    exit 0
fi

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$IDD"
export ESIM_WORKERS="$SLURM_CPUS_PER_TASK"

cd "$STEP8_DIR"
$PYTHON run_paired_mc.py \
    --archetype "$ARCH" \
    --city "$CITY" \
    --n 50 \
    --seed 42 \
    --sim-mode standard \
    --output-dir "${CAMPAIGN_ROOT}/${ARCH}__${CITY}"

EXIT=$?
echo "End: $(date)  exit=$EXIT"
exit $EXIT
