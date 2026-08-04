#!/bin/bash
# Decompose the 1.95 K hotel-ceiling gap between the grid extremes. No EnergyPlus -- SQL + IDF reads
# on runs that already exist (K = 40 grid-max, K = 20 grid-min), so this is minutes, not an hour.
#
# H7/H8 ruled out burner capacity: 4x capacity moves the grid-max ceiling by 0.00 K. What is left is
# either MIX (the grid-max hotel channel carries more volume in low-target uses, so 63.55 K is its
# legitimate ceiling and `C3` is the thing that is wrong) or THROTTLE (something non-capacity is
# holding an object short of its own target, and the campaign stays blocked until it is found).
#
# Gates H9 / H10 / H11 are pre-registered in the head of 3rdJ_09H_hotel_dT_decompose.py and are not
# restated here, so there is one copy of them and it sits next to the code that evaluates them.
# The short form: H9 = the parts agree, H10 = the mix arithmetic reproduces the whole, H11 = this
# script's duplicated channel map agrees with the driver's to 0.01 % or it refuses. H9 AND H10 are
# both required for MIX; H9 alone is satisfiable by the wrong mechanism, which is why H10 exists.
#SBATCH --job-name=3J_L3_dtdecomp
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/dtdecomp_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/headroom/_tmp
mkdir -p "$TMPDIR"

MAXD=$CAMP/headroom/K40/sens_hotel_opt__SuperTall__MTL
MIND=$CAMP/headroom/K20/B_cons__Tall__CLG

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_hotel_dT_decompose.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }
[ -f "$MAXD/run/eplusout.sql" ] || { echo "FATAL: no sql at $MAXD"; exit 1; }
[ -f "$MIND/run/eplusout.sql" ] || { echo "FATAL: no sql at $MIND"; exit 1; }

# Both sides are read at a K where the plant is provably non-binding (H7: 4x capacity, 0.00 K move;
# H8: the min cell is flat from K=10 to K=20). Comparing a saturated arm-H run against a resized one
# would confound the mix question with the capacity question all over again.
echo "### 1. decompose  MAX=$MAXD  (K=40)   MIN=$MIND  (K=20)"
$PY -u $S9/3rdJ_09H_hotel_dT_decompose.py "MAX=$MAXD" "MIN=$MIND"
RC=$?
echo "  decompose exit=$RC  : $(date)"
exit $RC
