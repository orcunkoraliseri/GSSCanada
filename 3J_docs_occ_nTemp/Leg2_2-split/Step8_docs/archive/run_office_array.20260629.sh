#!/bin/bash
# run_office_array.sh — Step 8C: Office deterministic campaign SLURM array (3J Leg-2)
#
# 252 tasks: 3 arch × 2 envelope × 6 CZ × 7 scenarios.
# Each task = one deterministic EnergyPlus run.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/run_office_array.sh
#       (after run_residential_array.sh is launched — independent, can run in parallel)

#SBATCH --job-name=3J_8C_office
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-251
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8C_office_%A_%a.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"

# ---- E+ IDD extraction (once per node; shared /tmp) ----------------------
IDD_DIR="/tmp/eplus_idd_$$"
mkdir -p "$IDD_DIR"
singularity exec "$SIF" cp /EnergyPlus/Energy+.idd "$IDD_DIR/" 2>/dev/null || true
export EPLUS_IDD="$IDD_DIR/Energy+.idd"
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg

echo "=== 8C Office array task $SLURM_ARRAY_TASK_ID of 251 ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  PY: $PY  SIF: $SIF"

# ---- run ------------------------------------------------------------------
cd "$STEP8_DIR"
$PY office_runner.py \
    --cell-idx $SLURM_ARRAY_TASK_ID \
    --out-dir "$SCRATCH/office"

echo "  Task $SLURM_ARRAY_TASK_ID done: $(date)"
rm -rf "$IDD_DIR"
