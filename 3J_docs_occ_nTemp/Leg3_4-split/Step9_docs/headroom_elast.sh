#!/bin/bash
# Hotel-scoped dT for the two grid-extreme cells at K = 10, run as a dependency of headroom_check.sh.
#
# WHAT IS BEING READ, AND WHAT IS NOT:
#
# Only the PER-CELL lines matter here -- `armH ... dT=` (gate H3) and `resized ... dT=` (gate H2),
# plus the volume equality (gate H1). Those come from the campaign's own channel resolution, which is
# why this script is reused rather than reading the probe's tower-wide totals.
#
# THE ELASTICITY BLOCK BELOW IS N/A BY CONSTRUCTION AND MUST NOT BE QUOTED. The two cells differ in
# height (SuperTall vs Tall), climate (MTL vs CLG) and scenario, so a 2-point E-vs-r fit across them
# confounds occupancy with geometry and weather. R0 is EXPECTED TO FAIL here -- it was calibrated on
# the `Tall__MTL` trio -- and that failure is the script correctly refusing to let R3 be read. An
# expected failure is written down in advance so it cannot later be mistaken for a surprise, and so
# that a PASS would be the thing demanding explanation.
#SBATCH --job-name=3J_L3_hdelast
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/hdelast_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
RDIR=$CAMP/headroom/K10
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/headroom/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_resize_elasticity.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }

ARGS=""
for C in sens_hotel_opt__SuperTall__MTL B_cons__Tall__CLG; do
  [ -d "$CDIR/$C" ] || { echo "FATAL: arm-H cell missing: $CDIR/$C"; exit 1; }
  [ -f "$RDIR/$C/run/eplusout.sql" ] || { echo "FATAL: resized sql missing for $C"; exit 1; }
  ARGS="$ARGS $CDIR/$C:$RDIR/$C"
done

echo ""
echo "########## HEADROOM: grid extremes at K = 10 -- read dT ONLY, elasticity is N/A ##########"
echo "  reference from the Tall__MTL trio at K = 10: dT = 65.50 / 65.51 / 65.51 K"
echo "  H2 needs both cells >= 65.0 K and within 0.5 K of each other"
echo "  H3 needs both arm-H (unresized) dT < 40 K, else H2 is vacuous"
$PY -u $S9/3rdJ_09H_resize_elasticity.py $ARGS
echo "  exit=$?  : $(date)"
