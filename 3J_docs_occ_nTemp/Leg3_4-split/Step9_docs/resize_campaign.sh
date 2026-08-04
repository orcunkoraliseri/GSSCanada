#!/bin/bash
# 56-cell RESIZED campaign at K = 10: arm H re-simulated with the DHW burners scaled, nothing else.
#
# RELEASE CONDITION, and the honest version of it. The original hold read "do not submit until H2
# passes". H2 FAILED (job 1171859: grid-max 63.56 K, below the 65.0 K clause, and 1.94 K from the
# grid-min cell against a 0.5 K agreement clause) and it STANDS FAILED -- it is not re-scored here.
# What released the campaign is not H2 but the three gates that came after it and asked a better
# question:
#   H7 (job 1172031)  dT(K=40) - dT(K=20) = 0.00 K on the grid-max cell -- a ceiling EXISTS.
#   H8 (job 1172031)  grid-MIN gain K=10 -> 20 = 0.00 K -- flatness discriminates, H7 is not vacuous.
#   H9 + H10 + H11 (job 1172033)  every shared hotel use-type delivers the same rise in both grid
#                     extremes to 0.00 K, and the MIN cell's per-type rises re-weighted by the MAX
#                     cell's volume shares reconstruct the MAX cell's 63.55 K exactly.
# So the 1.94 K that failed H2 is USE-MIX, not throttling: the grid-max cell carries 64.57 % of its
# volume at the 180F target vs 73.34 % in the grid-min cell, and (0.7334-0.6457)*(71.40-49.19) =
# 1.95 K, the observed gap. The plant is non-binding at K = 10 everywhere. H2's second clause
# ("the extremes agree within 0.5 K") rested on a premise -- a uniform plant delivers one temperature
# everywhere -- that H7/H8/H9/H10 falsified. A gate whose reference was wrong has still failed.
#
# SCOPE, decided by the user 2026-08-04: ALL-CHANNEL. `resize_idf()` rewrites every
# `WaterHeater:Mixed` in the IDF, so this is NOT a hotel-side correction on top of an otherwise
# unchanged arm H -- it is a NEW ARM for residential, office, retail AND hotel. The tower-wide series
# on the `Tall__MTL` trio was still climbing 3-8 K from K=6 to K=10 while the hotel-scoped series was
# already pinned to three identical digits, so the non-hotel movement is expected to be LARGE, not
# cosmetic. Every comparison against arm H moves four channels at once and must say so.
#
# WHY A RESIZE CAMPAIGN AT ALL: arm H's hotel DHW energy elasticity w.r.t. occupancy is 0.5582, i.e.
# roughly half of any increase in hotel draw never becomes delivered energy because the burner cannot
# serve it. At K = 10 the elasticity is 1.0013 and delivered dT is constant across cells, so the
# plant contributes nothing to cross-cell variation and the occupancy lever is clean.
#
# WHAT MOVES AND WHAT DOES NOT: only `Heater Maximum Capacity`, on every `WaterHeater:Mixed` the cell
# declares (6 on Tall, 11 on SuperTall -- measured per IDF, see 3rdJ_09H_plant_resize_probe.py).
# Tank volume, parasitics and loss coefficients are untouched, so standby losses are identical and
# the flat 0.803984 efficiency (empty `Part Load Factor Curve Name`) makes oversizing cost nothing.
# The injection is NOT re-run: each cell starts from arm H's own `injected.idf`, so `INJ_HASH` and
# `INPUTS_HASH` are inherited unchanged and "resized minus arm H" moves exactly one variable.
#
# PRE-REGISTERED for the campaign, written before submission and SCORED BY
# `3rdJ_09H_resize_campaign_score.py`, which was written before any cell of this campaign existed.
# Three of these were re-specified on 2026-08-04, BEFORE submission and on measurement rather than
# on the convenience of passing; each re-specification is strictly stricter than what it replaces
# and each says below what would make it fail.
#
#   C1' CONTROL  -- DHW VOLUME per cell is unchanged from arm H (<= 0.1 %) in ALL FOUR CHANNELS
#                   (residential, office, retail, hotel), in all 56 cells. WIDENED from hotel-only:
#                   the resize touches every `WaterHeater:Mixed`, so residential/office/retail draw
#                   is equally exposed to an accidental change and a hotel-only control could not
#                   fail for three quarters of what the intervention touches. The draw is
#                   schedule-driven and cannot see the burner, so any movement means the edit was
#                   not surgical in that cell. A channel with zero draw in both arms is reported as
#                   `no-draw`, never silently counted as agreement.
#   C2' CONTROL  -- `injected_resized.idf` differs from arm H's `injected.idf` ONLY on
#                   `!- Heater Maximum Capacity` lines -- exactly `PLANT_N_HEATERS` of them, each
#                   scaled by exactly K -- plus the appended `Output:Variable` block. RE-SPECIFIED:
#                   the original clause ("`INJ_HASH` identical, area delta 0 m^2") is unscoreable as
#                   written. The resized manifest is a COPY of arm H's, so comparing its INJ_HASH to
#                   arm H's compares a value with itself -- vacuous-gate #9 exactly -- and no area
#                   key exists anywhere in the manifest (checked, 2026-08-04). The line diff tests
#                   the thing that can actually differ, and it subsumes the area claim: a geometry
#                   change would appear as a differing line.
#   C3a DECISIVE -- in all 56 cells, EVERY hotel `WaterUse:Equipment` type delivers its own design
#                   rise: 140F types within 0.5 K of 49.19 K, 180F types within 0.5 K of 71.40 K.
#                   RE-SPECIFIED: the original C3 ("hotel
#                   dT constant across all 56 cells within 0.5 K, ACROSS geometry groups") is false
#                   by construction -- the 180F volume share is a use-mix property that varies with
#                   geometry (64.57 % vs 73.34 % between the measured grid extremes), so C3 would
#                   have failed every run for a reason that has nothing to do with the plant.
#                   C3a is STRICTER, not looser: C3 checked one aggregate per cell and could not
#                   tell a throttle from a mix difference; C3a checks every object. ITS FAILURE
#                   MODE IS DEFINED -- any object short of its design rise is a throttle. The
#                   reference rises are the H9/H10 measurement (job 1172033: 140F types
#                   49.17-49.23 K, 180F 71.34-71.43 K, both grid extremes, both cities), not a
#                   constant chosen here.
#   C3b CONTROL, and it is what stops C3a resting on an unchecked table -- the per-type table C3a
#                   is scored on must reconcile with the driver's own hotel channel: volume to
#                   0.01 % of `dhwvol_hotel`, energy to 0.01 % of `dhw_hotel`. Each cell already
#                   refuses on the volume half at write time (the H11 pattern); C3b re-checks it
#                   across all 56 and adds the energy half.
#                   WHY THE PRE-REGISTRATION SPLIT IN TWO, stated rather than buried: the other
#                   clause originally written into C3' -- "the per-cell aggregate equals its own
#                   180F/140F volume-share reconstruction within 0.5 K" -- is ARITHMETICALLY
#                   IMPLIED by C3a. A weighted mean of values each within 0.5 K of their design
#                   rise is necessarily within 0.5 K of the weighted design mean, so that clause
#                   cannot fail once C3a passes. It is printed as a derived quantity and NOT
#                   SCORED; C3b is the independent check it was reaching for. Bundling a
#                   measurement clause and a reconciliation clause under one verdict is the defect
#                   catalogued as vacuous-gate #13.
#   C4  DECISIVE -- hotel DHW energy elasticity w.r.t. r, computed within each (geometry, city)
#                   group, is >= 0.90 in 4/4 groups. The K sweep showed 1.0013 on Tall__MTL only.
#                   Estimator IMPORTED from `3rdJ_09H_resize_elasticity.py` (`elasticity`, `hotel_r`)
#                   so the 0.90 threshold is read against the estimator it was written for.
#   C4c CONTROL, and it is what stops C4 being vacuous -- arm H's own per-group elasticity must be
#                   BELOW 0.90 in every group where C4 passes. A group already at >= 0.90 before
#                   the resize is a group where C4's pass discriminates nothing. Arm H measured
#                   0.5582 on Tall__MTL, so this is expected to pass -- expected is not measured.
#   C5  INFO     -- tower EUI shift vs arm H, and the hotel EUI band re-check. EXPECTED to be large
#                   and NOT a gate, because the hotel band question is still unresolved and open
#                   with the user. Recording it as INFO keeps it from being read as validation.
#   C6  INFO     -- per-channel resized-minus-arm-H DHW energy AND volume, for all four channels, in
#                   all 56 cells. Owed by the all-channel decision. It is INFO and stays INFO: there
#                   is no pre-registered expectation for how far residential/office/retail should
#                   move, and a number scored against an expectation invented after seeing it is not
#                   a test. DO NOT promote it to a gate on the strength of what it shows.
#
# C3a is the one to read first. C4 can only be meaningful if C3a holds: an elasticity of 1.0 in a
# group whose plant is still binding would be a coincidence, not a clean lever.
#
# EVIDENCE FOR C3a IS WRITTEN BY THE RUN, not reconstructed afterwards: each cell emits
# `hotel_dT_by_type.csv` from the same module H9/H10/H11 were scored with, and REFUSES if its
# per-type hotel volume does not reconcile with the driver's own `dhwvol_hotel` column.
#SBATCH --job-name=3J_L3_resizecamp
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-55%20
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/resizecamp_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
WX=/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile
K=10
OUT=$CAMP/out_R_resize/K$K
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/out_R_resize/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter"
$PY -m py_compile $S9/3rdJ_09H_resize_campaign_cell.py || { echo "FATAL: does not compile"; exit 1; }
$PY -m py_compile $S9/3rdJ_09H_plant_resize_probe.py   || { echo "FATAL: does not compile"; exit 1; }
$PY -m py_compile $S9/3rdJ_09H_hotel_dT_decompose.py   || { echo "FATAL: does not compile"; exit 1; }
$PY -V
[ -f "$EPLUS_IDD" ] || { echo "FATAL: IDD not found: $EPLUS_IDD"; exit 1; }

# The cell list is READ FROM THE ARM-H TREE, not typed out here. A hand-written list of 56 names is a
# second source of truth that silently drifts; `ls` cannot disagree with the directory it lists.
CELL=$(ls "$CDIR" | sort | sed -n "$((SLURM_ARRAY_TASK_ID + 1))p")
[ -n "$CELL" ] || { echo "FATAL: no cell at index $SLURM_ARRAY_TASK_ID"; exit 1; }
[ -d "$CDIR/$CELL" ] || { echo "FATAL: not a directory: $CDIR/$CELL"; exit 1; }

# EPW follows the cell's own city token. Running a CLG cell against the Montreal file would change
# its mains temperature and its draw, and the resize would be credited with a weather effect.
case "$CELL" in
  *__MTL) EPW=$WX/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw ;;
  *__CLG) EPW=$WX/CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw ;;
  *) echo "FATAL: cannot resolve a city token in cell name: $CELL"; exit 1 ;;
esac
[ -f "$EPW" ] || { echo "FATAL: EPW not found: $EPW"; exit 1; }

echo "### 1. resized cell  idx=$SLURM_ARRAY_TASK_ID  cell=$CELL  K=$K"
echo "    epw=$EPW"
echo "    out=$OUT/$CELL"
$PY -u $S9/3rdJ_09H_resize_campaign_cell.py "$CDIR/$CELL" "$OUT/$CELL" "$EPW" "$K"
RC=$?
echo "  cell exit=$RC  : $(date)"
# Never end on a bare `echo` -- see headroom_check.sh. The job's exit code must be the work's.
exit $RC
