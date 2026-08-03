#!/bin/bash
# FINDING 8 smoke -- residual diagnosis. Reads IDFs only, simulates nothing.
# Source IDF = the Default_NECB cell's injected.idf: that cell injected nothing, and D7 verified
# all 47 WaterUse:Equipment objects there are unchanged, so it IS the source for this comparison.
#SBATCH --job-name=3J_L3_dtF8
#SBATCH -p ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/dtF8_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
CDIR=$CAMP/out_F_f8fix/campaign_456301f5
export PYTHONPATH=$REPO
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1

echo "node=$(hostname) date=$(date) python=$($PY -V 2>&1)"
$PY -m py_compile 3rdJ_09F_daytype_loss.py || { echo "FATAL: does not compile"; exit 1; }

$PY -u 3rdJ_09F_daytype_loss.py "$CDIR/Y2022__Tall__MTL/injected.idf" "$CDIR/Default_NECB__Tall__MTL/injected.idf"
echo "  exit=$?"
echo "daytype done: $(date)"
