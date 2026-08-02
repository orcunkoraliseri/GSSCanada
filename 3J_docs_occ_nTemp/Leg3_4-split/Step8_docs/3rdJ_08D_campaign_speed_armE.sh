#!/bin/bash
# 3J Leg-3 Step 9 -- arm E, 56 cells. sbatch only; nothing runs on the login node.
#
#   arm E (tasks 0-55)  --lighting-model calibrated_v2 --dhw-model volume_scaled
#
# arm E = arm C + T9-13. Lighting is held EXACTLY at arm C's calibrated_v2, so E - C isolates the
# DHW volume-scaling effect with no second variable moving. Same 56 cells, same %20 throttle.
#
# Requires injector md5 56d6e324... (T9-13 with the Y2022 per-day-type reference filled in) and
# driver md5 8164c10b... (--dhw-model volume_scaled wired). The driver FAILS LOUD if
# reference_occ_mean is empty rather than producing 56 silent no-op result dirs.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08D_campaign_speed_armE.sh

#SBATCH --job-name=3J_L3_armE
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-55%20
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/armE_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python

export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

mkdir -p $CAMP/logs $CAMP/out_E_dhwvol

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
[ -x "$ENERGYPLUS_DIR/energyplus" ] || { echo "NO ENERGYPLUS at $ENERGYPLUS_DIR"; exit 1; }
[ -f "$EPLUS_IDD" ] || { echo "NO IDD at $EPLUS_IDD"; exit 1; }

CELL=$SLURM_ARRAY_TASK_ID
OUT=$CAMP/out_E_dhwvol

echo "=== arm E cell $CELL (lighting=calibrated_v2, dhw=volume_scaled) ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  outroot: $OUT"
echo "  injector md5: $(md5sum $REPO/eSim_bem_utils/commercial_integration.py | cut -c1-8)"

cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1

$PY -u 3rdJ_08D_campaign_driver.py \
    --cell $CELL \
    --engine local \
    --repo-root "$REPO" \
    --outroot "$OUT" \
    --lighting-model calibrated_v2 \
    --dhw-model volume_scaled
RC=$?

echo "  arm E cell $CELL done, python exit=$RC: $(date)"
exit $RC
