#!/bin/bash
# 3J Leg-3 Step 8 -- 56-cell CAMPAIGN on Speed, TWO ARMS (112 tasks). sbatch only; nothing
# runs on the login node.
#
#   arm A (tasks   0- 55)  --lighting-model none        T9-9 standby-floor fix ONLY
#   arm B (tasks  56-111)  --lighting-model calibrated  T9-9 + T9-10 lighting diversity
#                                                        (office_n=3, hotel_n=1, retail open/closed)
#
# The pre-fix behaviour is NOT re-run: it is already the closed campaign_cf69d508 artefact set.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08D_campaign_speed.sh

#SBATCH --job-name=3J_L3_camp2arm
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-111%20
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/camp_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python

# EnergyPlus 24.2.0: ep_wrappers/energyplus is the Singularity shim the §P probes already used.
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

mkdir -p $CAMP/logs $CAMP/out_A_t99 $CAMP/out_B_lm3

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
[ -x "$ENERGYPLUS_DIR/energyplus" ] || { echo "NO ENERGYPLUS at $ENERGYPLUS_DIR"; exit 1; }
[ -f "$EPLUS_IDD" ] || { echo "NO IDD at $EPLUS_IDD"; exit 1; }

IDX=$SLURM_ARRAY_TASK_ID
CELL=$(( IDX % 56 ))
ARM=$(( IDX / 56 ))
if [ $ARM -eq 0 ]; then
  LM=none;       OUT=$CAMP/out_A_t99
else
  LM=calibrated; OUT=$CAMP/out_B_lm3
fi

echo "=== campaign task $IDX -> arm $ARM (lighting-model=$LM) cell $CELL ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  outroot: $OUT"

cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1

$PY -u 3rdJ_08D_campaign_driver.py \
    --cell $CELL \
    --engine local \
    --repo-root "$REPO" \
    --outroot "$OUT" \
    --lighting-model $LM
RC=$?

echo "  task $IDX (arm $ARM cell $CELL) done, python exit=$RC: $(date)"
exit $RC
