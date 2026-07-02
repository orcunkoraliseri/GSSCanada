#!/bin/bash
# run_aggregation.sh — Step 8D: two-channel EUI / load-shape aggregation + validation refresh.
#
# Pass 1: 3rdJ_08_simulation_2split_agg.py streams every residential (8,400) + office (252)
#         hourly_meters.csv and eplusout.sql -> outputs_step8/agg/*.csv  (the heavy scan).
# Pass 2: 3rdJ_08_simulation_2split_val.py re-runs; §4/§5/§7 (+§6.1/6.4–6.7) now read the
#         agg tables and render their charts. One job, one refreshed HTML report.
#
# Imports pandas/numpy/matplotlib and walks the full campaign trees -> COMPUTE node only,
# NEVER the login node.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_aggregation.sh

#SBATCH --job-name=3J_8D_agg
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8D_agg_%j.out

# ---- paths ----------------------------------------------------------------
SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"
cd "$STEP8_DIR" || { echo "FATAL: cannot cd $STEP8_DIR"; exit 1; }

# ---- fast-fail prechecks (compute node) -----------------------------------
$PY -c "import pandas, numpy" || { echo "MISSING DEP (pandas/numpy)"; exit 1; }
$PY -c "import matplotlib" && echo "  matplotlib: OK (charts enabled)" || echo "  WARN: matplotlib missing — charts skipped"
# EUI needs the engine plotting helper; confirm it imports before the heavy scan
$PY -c "import sys; sys.path.insert(0,'.'); from eSim_bem_utils_3J import plotting; print('  eSim_bem_utils_3J.plotting: OK (calculate_eui available)')" \
    || { echo "FATAL: cannot import eSim_bem_utils_3J.plotting — EUI would be NaN"; exit 1; }
# byte-compile both scripts so a syntax slip fails in seconds, not after a 1-hr scan
$PY -m py_compile 3rdJ_08_simulation_2split_agg.py 3rdJ_08_simulation_2split_val.py \
    || { echo "FATAL: py_compile failed"; exit 1; }
echo "  py_compile: OK"

# ---- point both scripts at the REAL output trees --------------------------
export STEP8_CAMP_DIR=$SCRATCH/campaign
export STEP8_OFFICE_DIR=$SCRATCH/office
export MPLBACKEND=Agg

echo "=== 8D aggregation task $(date) ==="
echo "  Node:   $(hostname)"
echo "  CAMP=$STEP8_CAMP_DIR"
echo "  OFFICE=$STEP8_OFFICE_DIR"

# ---- Pass 1: aggregate ----------------------------------------------------
echo "--- Pass 1: aggregation (heavy scan) ---"
$PY 3rdJ_08_simulation_2split_agg.py \
    --camp "$STEP8_CAMP_DIR" --office "$STEP8_OFFICE_DIR" --rebuild \
    || { echo "FATAL: aggregation failed"; exit 1; }

echo "  agg tables:"
ls -l outputs_step8/agg/ 2>/dev/null

# ---- Pass 2: refresh validation report ------------------------------------
echo "--- Pass 2: validation refresh (fills §4/§5/§7) ---"
$PY 3rdJ_08_simulation_2split_val.py

echo "  8D aggregation + validation done: $(date)"
