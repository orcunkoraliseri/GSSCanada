#!/bin/bash
# HEADROOM CHECK: does K = 10 un-saturate the DHW plant at the GRID EXTREMES, not just at the low end?
#
# WHY THIS EXISTS: the K sweep (jobs 1171837/1171843) established R3 PASS at K = 10, but all three
# swept cells were `Tall__MTL`, and `Y2022__Tall__MTL` is the 3rd-LOWEST peak-draw cell of the 56
# (10.8173 m3/h). The grid maximum is `sens_hotel_opt__SuperTall__MTL` at 15.8878 m3/h -- 1.47x
# larger. K = 10 clearing the low end is NO evidence that it clears the high end. If it does not, the
# uniform plant is not a constant across the grid and the entire point of the user's
# "uniform hard-size to grid max" decision is lost. The 56-cell campaign is blocked on this.
#
# The two cells are the measured grid extremes, from job 1171806:
#   MAX  sens_hotel_opt__SuperTall__MTL   15.8878 m3/h   908.5 kW @ 49.2 K   1318.4 kW @ 71.4 K
#   MIN  B_cons__Tall__CLG                10.6444 m3/h   608.7 kW @ 49.2 K    883.3 kW @ 71.4 K
# Installed at K = 10 is 4,476.0 kW, so both are nominally covered -- but the sizing calc was already
# shown to understate the real requirement by ~3.4x because it used hourly means rather than the
# simulation timestep. Nominal coverage is exactly what is NOT trusted here.
#
# PRE-REGISTERED, before running (also in improvements/3rdJ_L3_improvements_step9.md):
#
#   H1  CONTROL     -- hotel volume unchanged from arm H (<= 0.1 %) in both cells, as K1/R1. If
#                      volume moves the edit is not surgical and nothing below is readable.
#   H2  DECISIVE    -- hotel-scoped delivered dT at K = 10 reaches the same unconstrained constant in
#                      BOTH extremes: >= 65.0 K, and the two cells agree with EACH OTHER within
#                      0.5 K. The trio sat at 65.50 / 65.51 / 65.51 K. If the grid-max cell lands
#                      below 65.0 K, K = 10 does NOT un-saturate the grid, the campaign stays
#                      blocked, and K must be raised and re-tested. Agreement between the extremes is
#                      the actual claim: a uniform plant is a valid control only if it delivers the
#                      same temperature everywhere.
#   H3  FALSIFIER   -- the UNRESIZED arm-H dT in these same two cells must be < 40 K. If arm H
#                      already delivered ~65.5 K at the grid max, H2 could not possibly fail there
#                      and would be measuring nothing. H3 is what establishes that H2 has something
#                      to detect. Expected ~22 K by analogy with the trio -- but MEASURED here, not
#                      assumed. H3 is read off the `armH` half of the elasticity script's per-cell
#                      line, and off the `[arm H]` line printed by the probe below.
#   H4  INFO        -- record each cell's measured peak requirement against the 4,476 kW installed.
#
# H3 is included because H2 is a "reaches the ceiling" gate, and a ceiling gate on a system that was
# already at the ceiling cannot fail. That is the vacuous-gate class this project keeps re-finding.
#
# 🔴 SECOND ATTEMPT. The first (job 1171855_0) refused on the grid-max cell with
# "expected 6 Heater Maximum Capacity fields, rewrote 11". The guard was right and the constant was
# wrong: `SuperTall` carries **11** `WaterHeater:Mixed`, `Tall` carries **6**. So the "installed =
# 447.6 kW" figure quoted throughout the K sweep is a Tall-geometry number and NEVER was a grid-wide
# constant. Two consequences, both recorded rather than smoothed over:
#
#   (a) `N_HEATERS = 6` is replaced by a per-IDF measured count. The guard now asserts "every heater
#       the IDF declares was rewritten", whose reference comes from the file under edit instead of
#       from a number I believed. A guard encoding an assumption about the stock cannot detect that
#       the assumption is wrong -- the same shape as vacuous-gate #9.
#   (b) K is a MULTIPLIER of each cell's own installed base, so cells of different geometry do not
#       end up at the same absolute kW. That is still faithful to the user's decision, because the
#       decision was about not letting the OCCUPANCY axis buy capacity: within any geometry group
#       every scenario gets an identical plant, and `B_opt` never gets a bigger boiler than
#       `B_cons`. Geometry is a design axis that already differs in floors and area. And once the
#       plant is non-binding the point is moot -- delivered dT goes constant and capacity drops out
#       of the answer entirely, which is exactly what H2 tests.
#
# The per-cell installed base is now PRINTED (`PLANT_BASE` line), so H4 reads a measured number.
#SBATCH --job-name=3J_L3_headroom
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-1
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/headroom_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
WX=/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile
export PYTHONPATH=$REPO

K=10
CELLS=(sens_hotel_opt__SuperTall__MTL B_cons__Tall__CLG)
EPWS=($WX/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw \
      $WX/CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw)
CELL=${CELLS[$SLURM_ARRAY_TASK_ID]}
EPW=${EPWS[$SLURM_ARRAY_TASK_ID]}

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_plant_resize_probe.py || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPW" ] || { echo "FATAL: EPW not found: $EPW"; exit 1; }
[ -d "$CDIR/$CELL" ] || { echo "FATAL: cell not found: $CDIR/$CELL"; exit 1; }

# The EPW is matched to the cell's climate token, not inherited from the sweep. Running the CLG cell
# against the Montreal EPW would change its draw and its plant duty, and H2 would then be comparing
# two different buildings in the same weather rather than two grid extremes each in its own.
echo "### 1. headroom probe  cell=$CELL  K=$K"
echo "    epw=$EPW"
$PY -u $S9/3rdJ_09H_plant_resize_probe.py "$CDIR/$CELL" "$CAMP/headroom/K$K/$CELL" "$EPW" "$K"
RC=$?
echo "  probe exit=$RC  : $(date)"
# `echo "exit=$?"` as the LAST line made the job exit with echo's status -- always 0. The first
# attempt (job 1171855_0) died on the 11-heater refusal and SLURM still reported COMPLETED in 2 s,
# and the `afterok` dependent was released. That is vacuous-gate #10 (reading the wrong process's
# exit code) in this project's own harness, for the second time. Propagate the real code.
exit $RC
