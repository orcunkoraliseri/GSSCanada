#!/encs/bin/bash
#SBATCH --job-name=s8_build_sched
#SBATCH --partition=ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_run/logs/build_sched_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step8_run/logs/build_sched_%j.err

# Build clock-correct, schema-consistent Step 8 private schedules.
# Reads from BEM_Setup (read-only), writes to /speed-scratch/o_iseri/step8_run/sched/.
# DOES NOT touch BEM_Setup (Step 9 owns it).

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs

mkdir -p /speed-scratch/o_iseri/step8_run/logs

echo "=== Step 8 schedule build ==="
echo "Start: $(date)"

$PYTHON -c "import pandas; print('pandas ok:', pandas.__version__)" || { echo "ERROR: pandas missing"; exit 1; }

$PYTHON "$STEP8_DIR/build_s8_sched.py"

EXIT=$?
echo "End: $(date)  exit=$EXIT"
exit $EXIT
