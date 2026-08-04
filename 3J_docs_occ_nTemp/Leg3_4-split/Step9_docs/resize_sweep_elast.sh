#!/bin/bash
# Hotel-scoped elasticity at each swept K, run as a dependency of the K sweep array.
#
# Reuses `3rdJ_09H_resize_elasticity.py` unchanged, once per K. That script's R0 control re-derives
# the arm-H hotel elasticity every time and refuses to let R3 be quoted unless it reproduces 0.5617
# to within 0.02 -- so R0 is re-checked independently at every K rather than assumed from 1171835.
#
# K2 (elasticity >= 0.90, monotone in K) and K4 (|elasticity_dT| shrinking) are read off the printed
# elasticities across the two blocks. K3, the discriminator, is read off the `Y2022` delivered dT
# line: >= 47 K confirms the capacity hypothesis, < 42 K refutes it.
#SBATCH --job-name=3J_L3_kelast
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/kelast_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/resize_sweep/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_resize_elasticity.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }

for K in 6 10; do
  RDIR=$CAMP/resize_sweep/K$K
  ARGS=""
  OK=1
  for C in Y2022__Tall__MTL B_central__Tall__MTL B_opt__Tall__MTL; do
    if [ ! -f "$RDIR/$C/run/eplusout.sql" ]; then
      echo "SKIP K=$K: resized sql missing for $C"; OK=0; break
    fi
    ARGS="$ARGS $CDIR/$C:$RDIR/$C"
  done
  [ $OK -eq 1 ] || continue
  echo ""
  echo "########## K = $K : hotel-scoped elasticity vs arm H ##########"
  $PY -u $S9/3rdJ_09H_resize_elasticity.py $ARGS
  echo "  exit=$?"
done
echo "  done : $(date)"
