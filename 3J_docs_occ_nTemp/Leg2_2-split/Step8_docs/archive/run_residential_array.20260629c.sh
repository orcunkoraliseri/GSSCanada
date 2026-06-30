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

# ---- E+ path: residential uses host-side ep_install directly (no SIF needed) ----
# simulation.py reads ENERGYPLUS_DIR to locate the energyplus binary and Energy+.idd.
# Default is /usr/local/EnergyPlus-24-2-0 which does NOT exist on this cluster.
export ENERGYPLUS_DIR=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg
export ESIM_WORKERS=8

# IDD extraction from SIF (dead code — simulation.py uses $ENERGYPLUS_DIR/Energy+.idd;
# kept here with corrected path in case it is wired in future).
IDD_DIR="/tmp/eplus_idd_$$"
mkdir -p "$IDD_DIR"
singularity exec "$SIF" cp /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/Energy+.idd "$IDD_DIR/" 2>/dev/null || true
export EPLUS_IDD="$IDD_DIR/Energy+.idd"

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
