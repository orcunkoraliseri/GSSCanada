#!/bin/bash
# Hotel-scoped dT for the K = 20 / K = 40 escalation, run as a dependency of headroom_k2040.sh.
#
# 🔴 THE REASON THIS SEPARATE JOB EXISTS, and it cost a wasted scoring attempt on 2026-08-04:
# `3rdJ_09H_plant_resize_probe.py` prints TOWER-WIDE DHW dT (all four channels, volume-weighted).
# H2/H6/H7/H8 are written on HOTEL-SCOPED dT, which only the campaign's channel resolution produces.
# The two differ by ~5 K on the same cell in the same run -- at K = 10 the `Tall__MTL` trio reads
# 60.24/60.36/60.68 K tower-wide and 65.50/65.51/65.51 K hotel-scoped. Scoring a hotel threshold
# against a tower-wide number manufactures a confident verdict out of a units mismatch. Read the
# per-cell lines BELOW, never the probe's own summary, for any gate in the H-series.
#
# THE ELASTICITY BLOCK IS N/A BY CONSTRUCTION AND MUST NOT BE QUOTED -- more so here than in
# `headroom_elast.sh`. The pairs below are not even distinct cells: two of them are the SAME cell at
# two different K. An E-vs-r fit across them regresses on a `r` axis with a repeated point. R0 is
# EXPECTED TO FAIL, exactly as it did in job 1171859 (got 1.8470 against 0.5617), and that failure is
# the script correctly refusing to let R3 be read. Written down in advance so that a PASS would be
# the thing demanding explanation.
#SBATCH --job-name=3J_L3_hd2elast
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/hd2elast_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/headroom/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_resize_elasticity.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }

# pair := <armH cell dir>:<resized dir>. Order matches tasks 0,1,2 of headroom_k2040.sh.
PAIRS="$CDIR/sens_hotel_opt__SuperTall__MTL:$CAMP/headroom/K20/sens_hotel_opt__SuperTall__MTL \
       $CDIR/sens_hotel_opt__SuperTall__MTL:$CAMP/headroom/K40/sens_hotel_opt__SuperTall__MTL \
       $CDIR/B_cons__Tall__CLG:$CAMP/headroom/K20/B_cons__Tall__CLG"

ARGS=""
for P in $PAIRS; do
  A=${P%%:*}; B=${P##*:}
  [ -d "$A" ] || { echo "FATAL: arm-H cell missing: $A"; exit 1; }
  [ -f "$B/run/eplusout.sql" ] || { echo "FATAL: resized sql missing: $B"; exit 1; }
  ARGS="$ARGS $P"
done

echo ""
echo "########## K ESCALATION -- read the per-cell dT lines ONLY, elasticity is N/A ##########"
echo "  ceiling reference: 65.50 K (grid-MIN cell at K=10, and the Tall__MTL trio at K=10)"
echo "  at K=10 the grid-MAX cell reached 63.56 K -- 1.94 K short -- so H2 FAILED."
echo ""
echo "  line 1 = grid MAX @ K=20   -> H6: >= 65.0 K and within 0.5 K of 65.50"
echo "  line 2 = grid MAX @ K=40   -> H7: dT(K40) - dT(K20) < 0.5 K  (a ceiling exists)"
echo "  line 3 = grid MIN @ K=20   -> H8: gain over its K=10 value (65.50 K) < 0.5 K  (control)"
echo "  all three  -> H5: volume identical to arm H"
echo ""
$PY -u $S9/3rdJ_09H_resize_elasticity.py $ARGS
RC=$?
echo "  exit=$RC  : $(date)"
# Never end on a bare `echo`: it would make the job exit 0 even when the reader refused.
exit $RC
