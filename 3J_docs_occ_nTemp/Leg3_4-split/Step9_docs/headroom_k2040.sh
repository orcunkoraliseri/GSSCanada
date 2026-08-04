#!/bin/bash
# K ESCALATION after H2 FAILED at K = 10. Grid-max cell at K = 20 and K = 40, plus a positive control.
#
# WHY: at K = 10 the hotel-scoped delivered rise reached
#     grid MAX  sens_hotel_opt__SuperTall__MTL   25.34 -> 63.56 K
#     grid MIN  B_cons__Tall__CLG                24.19 -> 65.50 K
# The min-side cell landed exactly on the `Tall__MTL` trio's 65.50/65.51/65.51 K, i.e. on the ceiling.
# The grid-max cell fell 1.94 K short of it, so H2 failed on both its clauses (>= 65.0 K, and the two
# extremes within 0.5 K of each other). The pre-registration says: raise K, re-probe the grid-max
# cell, do not launch the campaign. That is what this is.
#
# The deficit is small -- 1.94 K on a +38.22 K move, so the cell is ~95 % of the way to the ceiling --
# and that is exactly why it must be tested rather than assumed away. "Nearly there" is the shape a
# still-binding plant has when the binding is intermittent: a handful of peak hours that never get
# served, invisible in an annual mean until you look for them.
#
# PRE-REGISTERED, written before submission (also in improvements/3rdJ_L3_improvements_step9.md).
# Three separately-numbered gates, NOT one conjunction -- vacuous-gate #13 was exactly the habit of
# bundling a trend clause and a threshold clause under a single verdict.
#
#   H5  CONTROL     -- hotel volume unchanged from arm H (<= 0.1 %) in every task. Same as H1. The
#                      burner cannot see the schedule; if volume moves, the edit is not surgical.
#
#   H6  DECISIVE    -- hotel-scoped delivered dT in `sens_hotel_opt__SuperTall__MTL` at K = 20 is
#                      >= 65.0 K AND within 0.5 K of 65.50 K (the value the grid-MIN cell and the
#                      whole Tall__MTL trio converge on). If it reaches it, burner capacity was the
#                      binding constraint in that cell too and the grid has a single ceiling.
#                      If K = 20 still falls short, this cell's constraint is NOT burner capacity and
#                      no K fixes it -- the search moves to `Tank Volume`, `Use Side Effectiveness`,
#                      or plant-loop flow, and the campaign stays blocked regardless of H7.
#
#   H7  SATURATION  -- dT(K = 40) - dT(K = 20) in that same cell is < 0.5 K. This is the claim that a
#                      ceiling EXISTS, separately from where it is. If dT is still climbing materially
#                      at 40x installed capacity, then `implied dT` is not measuring a delivered
#                      temperature approaching a setpoint -- it is tracking something unbounded, and
#                      the entire "un-saturate the plant" framing is wrong. H7 can fail while H6
#                      passes, and that combination would be the most informative outcome of all.
#
#   H8  POSITIVE CONTROL, and it is what stops H7 being vacuous -- `B_cons__Tall__CLG` is re-run at
#                      K = 20. It already sits ON the ceiling at K = 10 (65.50 K), so its gain from
#                      K = 10 to K = 20 must be < 0.5 K. If that cell ALSO keeps climbing, then a
#                      "< 0.5 K gain" is not a property of saturation and H7 cannot be read as one --
#                      the instrument, not the plant, would be what H7 measured.
#
# H8 is the arm that makes this design falsifiable. Without it, "dT stopped moving" and "dT moves
# slowly at large K for every cell" are the same observation.
#
# NOT AFFECTED BY THE OPEN ALL-CHANNEL-VS-HOTEL-ONLY QUESTION: these gates are read hotel-scoped, and
# the hotel's own `WaterHeater:Mixed` objects get the same multiplier under either resolution. So this
# probe is worth running while that decision is still with the user.
#SBATCH --job-name=3J_L3_hdroom2
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-2
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/hdroom2_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
WX=/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile
export PYTHONPATH=$REPO

MTL=$WX/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
CLG=$WX/CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw

# task 0 = H6 (grid max, K=20) | task 1 = H7 (grid max, K=40) | task 2 = H8 (control, K=20)
CELLS=(sens_hotel_opt__SuperTall__MTL sens_hotel_opt__SuperTall__MTL B_cons__Tall__CLG)
KS=(20 40 20)
EPWS=($MTL $MTL $CLG)
CELL=${CELLS[$SLURM_ARRAY_TASK_ID]}
K=${KS[$SLURM_ARRAY_TASK_ID]}
EPW=${EPWS[$SLURM_ARRAY_TASK_ID]}

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_plant_resize_probe.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPW" ] || { echo "FATAL: EPW not found: $EPW"; exit 1; }
[ -d "$CDIR/$CELL" ] || { echo "FATAL: cell not found: $CDIR/$CELL"; exit 1; }

echo "### 1. headroom probe  cell=$CELL  K=$K"
echo "    epw=$EPW"
$PY -u $S9/3rdJ_09H_plant_resize_probe.py "$CDIR/$CELL" "$CAMP/headroom/K$K/$CELL" "$EPW" "$K"
RC=$?
echo "  probe exit=$RC  : $(date)"
# The job's exit code must be the work's, not echo's -- see headroom_check.sh and §0.8 of the handoff.
exit $RC
