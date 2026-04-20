#!/bin/bash
#SBATCH --job-name=eSim_MC_tuned
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5           # 5 = one core per year-scenario (5 parallel E+ workers)
#SBATCH --mem=64G                   # RC6 peaked at 58 GB; 64G gives headroom
#SBATCH -t 7-00:00:00
#SBATCH --array=1-6                 # one array task per neighbourhood
# --exclusive: prevents node-sharing for clean wall-time benchmarks, but lengthens
# queue wait when the cluster is busy. Uncomment only for benchmarking (Task 6e).
##SBATCH --exclusive
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/logs/eSim_%A_%a.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=orcunkoral.oseri@concordia.ca

# ---------------------------------------------------------------------------
# eSim MC Neighbourhood Batch — Tuned SLURM Job Array (Task 6b)
#
# Differences from submit_array.sh:
#   --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=64G  (fat single-node task)
#   --workers $SLURM_CPUS_PER_TASK passed to run_batch_hpc.py (intra-node E+
#     parallelism: all 5 year-scenario jobs within each MC iteration run
#     simultaneously instead of serially).
#
# Adjust ITER_COUNT below before submitting:
#   Benchmark: ITER_COUNT=2
#   Production: ITER_COUNT=20
# ---------------------------------------------------------------------------

ITER_COUNT=20

PROJECT=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64
VENV=/speed-scratch/o_iseri/GSSCanada/venv
OUTPUT_PARENT=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N${ITER_COUNT}_v2
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
echo "Array task   : $SLURM_ARRAY_TASK_ID / 6"
echo "IDF          : $IDF_PATH"
echo "Region       : $REGION"
echo "Iterations   : $ITER_COUNT"
echo "Workers      : $SLURM_CPUS_PER_TASK"
echo "Output dir   : $OUTPUT_DIR"
echo "EnergyPlus   : $EP_DIR"
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
    --idf        "$IDF_PATH" \
    --region     "$REGION" \
    --sim-mode   weekly \
    --iter-count "$ITER_COUNT" \
    --output-dir "$OUTPUT_DIR" \
    --workers    "$SLURM_CPUS_PER_TASK" \
    --use-tmpdir

EXIT_CODE=$?
echo "Done: $IDF_NAME (exit code: $EXIT_CODE)"
exit $EXIT_CODE
