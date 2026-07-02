#!/bin/bash
# run_step9.sh — Step 9 (both channels) activity-driven end-use analysis (3J Leg-2)
#
# Reads the §8D agg tables (Step8_docs/outputs_step8/agg/) and emits the bi-channel Step-9
# deliverable (parallel resid/office tables + paired figures + step9_report.html). No
# re-simulation, but it imports pandas/numpy/matplotlib and streams agg_diurnal (~180 MB) in
# chunks, so it MUST run on a COMPUTE node — never the login node.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step9_docs/run_step9.sh

#SBATCH --job-name=3J_9_step9
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/9_step9_%j.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP9_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step9_docs
AGG_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/agg

mkdir -p "$SCRATCH/logs"

# ---- dep precheck (compute node, not login) -------------------------------
$PY -c "import pandas, numpy" || { echo "MISSING DEP: pandas/numpy"; exit 1; }
$PY -c "import matplotlib" && echo "  matplotlib: OK (figures enabled)" || echo "  WARN: matplotlib missing — figures will be skipped"

# ---- point the analysis at the real agg tables + output dir ----------------
export STEP9_AGG_DIR=$AGG_DIR
export STEP9_OUT_DIR=$STEP9_DIR/outputs_step9
export MPLBACKEND=Agg

echo "=== Step 9 (both channels) task $(date) ==="
echo "  Node: $(hostname)"
echo "  AGG=$STEP9_AGG_DIR"
echo "  OUT=$STEP9_OUT_DIR"

# quick visibility: confirm the agg tables are present before the heavy read
ls -la "$AGG_DIR" | head -8

# ---- run ------------------------------------------------------------------
cd "$STEP9_DIR"
$PY -m py_compile 3rdJ_09_activityDrivenLoads_2split.py || { echo "FATAL: py_compile failed"; exit 1; }
echo "  py_compile: OK"
$PY 3rdJ_09_activityDrivenLoads_2split.py

echo "  9 step9 done: $(date)"
