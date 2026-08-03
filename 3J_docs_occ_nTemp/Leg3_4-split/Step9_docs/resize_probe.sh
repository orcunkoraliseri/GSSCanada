#!/bin/bash
# 3-cell UNIFORM PLANT RESIZE probe (K = 3.0, burners only). Same geometry and city (Tall, MTL),
# three hotel `r` values, so the r-elasticity of delivered energy is re-measured against arm H's
# 0.5617 -- R3, the gate that decides whether a 56-cell campaign is worth launching.
#
#   Y2022__Tall__MTL     r = 1.0000
#   B_central__Tall__MTL r = 1.1244
#   B_opt__Tall__MTL     r = 1.2031
#
# Deliberately NOT 56 cells: whether a 3x burner removes the plant from the occupancy signal is a
# property of the building, not of the scenario grid, and every cell answers it the same way.
# the sizing objects, not of the scenario grid, and it is answered identically by every cell.
#SBATCH --job-name=3J_L3_resizeH
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-2
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/resizeH_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
EPW=/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
export PYTHONPATH=$REPO

CELLS=(Y2022__Tall__MTL B_central__Tall__MTL B_opt__Tall__MTL)
CELL=${CELLS[$SLURM_ARRAY_TASK_ID]}

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_plant_resize_probe.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPW" ] || { echo "FATAL: EPW not found: $EPW"; exit 1; }
[ -d "$CDIR/$CELL" ] || { echo "FATAL: cell not found: $CDIR/$CELL"; exit 1; }

echo "### 1. probe $CELL"
$PY -u $S9/3rdJ_09H_plant_resize_probe.py "$CDIR/$CELL" "$CAMP/resize_probe/$CELL" "$EPW" 3.0
echo "  probe exit=$?  : $(date)"
