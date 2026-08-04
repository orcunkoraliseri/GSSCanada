#!/bin/bash
# K sweep, K in {6, 10}, on the same three Tall__MTL cells as the K = 3.0 probe (job 1171807).
#
# WHY A SWEEP AND NOT A SINGLE LARGER K: at K = 3.0 the hotel energy elasticity moved the WRONG WAY
# (0.5582 -> 0.4403) and the temperature sag with occupancy GREW (-0.443 -> -0.559), while installed
# capacity (1,342.8 kW) already exceeded the measured grid-max peak requirement (908.5 kW at the
# 49.2 K target). So "pick a bigger K" is a coin flip. The sweep is specified so that BOTH outcomes
# are informative -- see K3, the discriminator.
#
# PRE-REGISTERED, before running (also recorded in improvements/3rdJ_L3_improvements_step9.md):
#
#   K1  CONTROL     -- hotel volume unchanged (<= 0.1 %) at every K, as R1. If volume moves the edit
#                      is not surgical and nothing downstream is readable.
#   K2  DECISIVE    -- hotel energy elasticity rises MONOTONICALLY with K and reaches >= 0.90 at
#                      K = 10. Measured so far: K=1 -> 0.5582, K=3 -> 0.4403, already non-monotone,
#                      so K2 is PREDICTED TO FAIL. Written down anyway -- a prediction only counts
#                      if it was made before the run.
#   K3  DISCRIMINATOR -- delivered dT at r = 1.0 (Y2022) vs K. If capacity-limited, dT -> 49.2 K:
#                      pre-register dT(K=10) >= 47 K. If dT(K=10) < 42 K, burner capacity is REFUTED
#                      as the binding constraint and NO K fixes R3; the search moves to tank volume,
#                      `Use Side Effectiveness`, or plant-loop flow.
#   K4  -- the sag |elasticity_dT| shrinks with K. It GREW 0.443 -> 0.559 between K=1 and K=3;
#          continued growth or flatness is further positive evidence against the capacity story.
#
# K3 carries information whichever way it lands. That is why it is the discriminator, not K2.
#SBATCH --job-name=3J_L3_ksweep
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-5
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/ksweep_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
EPW=/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
export PYTHONPATH=$REPO

CELLS=(Y2022__Tall__MTL B_central__Tall__MTL B_opt__Tall__MTL)
KS=(6 10)
CELL=${CELLS[$(($SLURM_ARRAY_TASK_ID % 3))]}
K=${KS[$(($SLURM_ARRAY_TASK_ID / 3))]}

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_plant_resize_probe.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPW" ] || { echo "FATAL: EPW not found: $EPW"; exit 1; }
[ -d "$CDIR/$CELL" ] || { echo "FATAL: cell not found: $CDIR/$CELL"; exit 1; }

echo "### 1. resize probe  cell=$CELL  K=$K"
$PY -u $S9/3rdJ_09H_plant_resize_probe.py "$CDIR/$CELL" "$CAMP/resize_sweep/K$K/$CELL" "$EPW" "$K"
RC=$?
echo "  probe exit=$RC  : $(date)"
# See headroom_check.sh: `echo "exit=$?"` as the last line makes the job always exit 0, so a refusing
# probe still reports COMPLETED and releases its `afterok` dependent. Fixed here too. It did not
# mislead the K sweep -- all six tasks genuinely ran -- but the harness was unsound at the time.
exit $RC
