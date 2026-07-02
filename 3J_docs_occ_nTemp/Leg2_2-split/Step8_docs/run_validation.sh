#!/bin/bash
# run_validation.sh — Step 8E: two-channel validation scorecard (3J Leg-2)
#
# Runs 3rdJ_08_simulation_2split_val.py on a COMPUTE node. The validator imports
# pandas/numpy and rglobs the full campaign (8,400 cells) + office (252 cells)
# output trees, so it must NEVER run on the login node.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_validation.sh

#SBATCH --job-name=3J_8E_val
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8E_val_%j.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"

# dep precheck (runs on the compute node, not login)
$PY -c "import pandas, numpy" || { echo "MISSING DEP"; exit 1; }
# matplotlib is soft: the scorecard still generates without it (charts skipped)
$PY -c "import matplotlib" && echo "  matplotlib: OK (charts enabled)" || echo "  WARN: matplotlib missing — charts will be skipped"

# ---- point the validator at the REAL output trees -------------------------
# The SLURM arrays wrote to the scratch root, NOT into the upload tree. Without
# these, §1 would report 0/8400 + 0/252 "not yet run". Defaults are preserved
# in the script for local runs; these env vars override them.
export STEP8_CAMP_DIR=$SCRATCH/campaign
export STEP8_OFFICE_DIR=$SCRATCH/office
export MPLBACKEND=Agg

echo "=== 8E Validation task $(date) ==="
echo "  Node: $(hostname)"
echo "  CAMP=$STEP8_CAMP_DIR"
echo "  OFFICE=$STEP8_OFFICE_DIR"

# ---- run ------------------------------------------------------------------
cd "$STEP8_DIR"
# byte-compile first so a syntax slip fails in seconds, not after the campaign rglob
$PY -m py_compile 3rdJ_08_simulation_2split_val.py || { echo "FATAL: py_compile failed"; exit 1; }
echo "  py_compile: OK"
$PY 3rdJ_08_simulation_2split_val.py

echo "  8E validation done: $(date)"
