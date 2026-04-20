#!/bin/bash
#SBATCH --job-name=eSim_MC
#SBATCH --account=speed1
#SBATCH -p ps
#SBATCH --mem=8G
#SBATCH -c 4
#SBATCH -t 1-00:00:00
#SBATCH --array=1-6
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/logs/eSim_%A_%a.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=orcunkoral.oseri@concordia.ca

# ---------------------------------------------------------------------------
# eSim MC Neighbourhood Batch — SLURM Job Array
#
# One array task per neighbourhood (NUS_RC1 … NUS_RC6).
# Adjust ITER_COUNT below before submitting:
#   Smoke test  : ITER_COUNT=2
#   Production  : ITER_COUNT=20
# ---------------------------------------------------------------------------

ITER_COUNT=20

PROJECT=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64
VENV=/speed-scratch/o_iseri/GSSCanada/venv
OUTPUT_PARENT=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N${ITER_COUNT}
LOG_DIR=/speed-scratch/o_iseri/GSSCanada/logs

# --- Environment ---
source "$VENV/bin/activate"
export ENERGYPLUS_DIR="$EP_DIR"

# Sanity-check EnergyPlus binary
if ! "$EP_DIR/energyplus" --version > /dev/null 2>&1; then
    echo "ERROR: EnergyPlus not found at $EP_DIR" >&2
    exit 2
fi

# --- Neighbourhood mapping (array index 1-based → 0-based) ---
IDFS=(NUS_RC1 NUS_RC2 NUS_RC3 NUS_RC4 NUS_RC5 NUS_RC6)
REGIONS=(Quebec Quebec Quebec Quebec Quebec Quebec)

IDX=$((SLURM_ARRAY_TASK_ID - 1))
IDF_NAME="${IDFS[$IDX]}"
REGION="${REGIONS[$IDX]}"

IDF_PATH="$PROJECT/BEM_Setup/Neighbourhoods/${IDF_NAME}.idf"
OUTPUT_DIR="$OUTPUT_PARENT/${IDF_NAME}"

echo "========================================"
echo "Array task : $SLURM_ARRAY_TASK_ID / 6"
echo "IDF        : $IDF_PATH"
echo "Region     : $REGION"
echo "Iterations : $ITER_COUNT"
echo "Output dir : $OUTPUT_DIR"
echo "EnergyPlus : $EP_DIR"
echo "========================================"

# --- Validate IDF exists ---
if [ ! -f "$IDF_PATH" ]; then
    echo "ERROR: IDF not found: $IDF_PATH" >&2
    exit 2
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# --- Run ---
cd "$PROJECT"
python eSim_bem_utils/run_batch_hpc.py \
    --idf       "$IDF_PATH" \
    --region    "$REGION" \
    --sim-mode  weekly \
    --iter-count "$ITER_COUNT" \
    --output-dir "$OUTPUT_DIR"

EXIT_CODE=$?
echo "Done: $IDF_NAME (exit code: $EXIT_CODE)"
exit $EXIT_CODE
