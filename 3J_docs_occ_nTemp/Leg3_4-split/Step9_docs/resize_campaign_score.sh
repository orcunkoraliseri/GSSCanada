#!/bin/bash
# Score the 56-cell RESIZED campaign against the pre-registration in resize_campaign.sh.
# Submitted WITH the campaign, as an `afterany` dependent, so the gate code is frozen before any
# result exists. `afterany` rather than `afterok` on purpose: if a cell dies, this must still run
# and say WHICH cells are missing. A scorer that silently never runs is the quietest failure mode
# there is, and the 56 verdicts would simply be absent with nothing to explain them.
#SBATCH --job-name=3J_L3_resizescore
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/resizescore_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
K=10
OUT=$CAMP/out_R_resize/K$K
export PYTHONPATH=$REPO
export REPO=$REPO
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export TMPDIR=$CAMP/out_R_resize/_tmp
mkdir -p "$TMPDIR"

echo "### 0. compile under the cluster interpreter (local py_compile is 3.13, this env is 3.10)"
$PY -m py_compile $S9/3rdJ_09H_resize_campaign_score.py || { echo "FATAL: does not compile"; exit 1; }
$PY -m py_compile $S9/3rdJ_09H_resize_elasticity.py     || { echo "FATAL: does not compile"; exit 1; }
$PY -V

echo "### 1. scorecard  armH=$CDIR  resized=$OUT"
$PY -u $S9/3rdJ_09H_resize_campaign_score.py "$CDIR" "$OUT"
RC=$?
echo "  score exit=$RC  : $(date)"
# Never end on a bare `echo` -- the job's exit code must be the work's, not the echo's.
exit $RC
