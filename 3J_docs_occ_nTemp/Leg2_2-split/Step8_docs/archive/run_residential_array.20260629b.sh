#!/bin/bash
# run_residential_array.sh — Step 8B: Residential paired-MC SLURM array (3J Leg-2)
#
# 168 tasks: 4 arch × 6 CZ × 7 scenarios, one task per cell.
# Each task runs N=50 EnergyPlus simulations for ONE scenario using a
# deterministic per-(arch×city) seed — same N=50 HH IDs across all scenario
# tasks for the same cell, enforcing the paired design.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/run_residential_array.sh
#       (returns job ID instantly; NEVER run from login node interactively)

#SBATCH --job-name=3J_8B_resid
#SBATCH -p ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-167
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8B_resid_%A_%a.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"

# Fix 5: dep precheck — fail fast if python env is missing a required package
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

# ---- E+ IDD extraction (once per node; shared /tmp) ----------------------
IDD_DIR="/tmp/eplus_idd_$$"
mkdir -p "$IDD_DIR"
singularity exec "$SIF" cp /EnergyPlus/Energy+.idd "$IDD_DIR/" 2>/dev/null || true
export EPLUS_IDD="$IDD_DIR/Energy+.idd"
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg
export ESIM_WORKERS=8

echo "=== 8B Residential array task $SLURM_ARRAY_TASK_ID of 167 ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  PY: $PY  SIF: $SIF"

# ---- run ------------------------------------------------------------------
cd "$STEP8_DIR"
$PY 3rdJ_08B_run_paired_mc.py \
    --cell-idx $SLURM_ARRAY_TASK_ID \
    --n 50 \
    --seed 42 \
    --mode standard \
    --out-dir "$SCRATCH/campaign"

echo "  Task $SLURM_ARRAY_TASK_ID done: $(date)"
rm -rf "$IDD_DIR"
