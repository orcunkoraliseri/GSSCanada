#!/bin/bash
# R0/R3/R3v/R4 for the K = 3.0 uniform plant resize, hotel-scoped through the campaign's own
# channel mapping. Reads the three arm-H cells and their three resized twins from job 1171807.
#SBATCH --job-name=3J_L3_relast
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/relast_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
RDIR=$CAMP/resize_probe
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/resize_probe/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_resize_elasticity.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }

ARGS=""
for C in Y2022__Tall__MTL B_central__Tall__MTL B_opt__Tall__MTL; do
  [ -d "$CDIR/$C" ] || { echo "FATAL: arm-H cell missing: $CDIR/$C"; exit 1; }
  [ -f "$RDIR/$C/run/eplusout.sql" ] || { echo "FATAL: resized sql missing for $C"; exit 1; }
  ARGS="$ARGS $CDIR/$C:$RDIR/$C"
done

echo "### 1. hotel-scoped elasticity, arm H vs resized (K = 3.0)"
$PY -u $S9/3rdJ_09H_resize_elasticity.py $ARGS
echo "  exit=$?  : $(date)"
