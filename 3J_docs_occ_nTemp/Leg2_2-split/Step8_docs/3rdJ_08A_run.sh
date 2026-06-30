#!/bin/bash
# 3rdJ_08A_run.sh — Step 8A: Historical schedule generation wrapper (3J Leg-2)
# Wraps 3rdJ_08A_gen_historical_schedules.py for sbatch submission.
# Fix 5: dep precheck before running to fail fast if env is missing.

#SBATCH --job-name=3J_8A_hist
#SBATCH -p ps
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8A_%j.out

PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs
LOG=/speed-scratch/o_iseri/step8_2split/logs/8A_gen.out

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

cd "$STEP8_DIR"
$PY 3rdJ_08A_gen_historical_schedules.py --year all > "$LOG"
