#!/bin/bash
# 5J campaign, one array per country x climate. Two modes in one file:
#   submit (run from the login node, sbatch only):  bash camp_array.sh <climate_id>
#       reads R/plan/nblocks.txt and runs: sbatch --array=1-<nblocks>%5 camp_array.sh <climate_id>
#   task (inside the array, SLURM_ARRAY_TASK_ID set): one block -> camp_task.py <climate_id> <block>
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
ARR=${1:?climate id}
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
  N=$(grep "^$ARR " $R/plan/nblocks.txt | cut -d' ' -f2)
  [ -n "$N" ] || { echo "no block count for $ARR"; exit 2; }
  sbatch --array=1-${N}%5 -J camp_$ARR -o $R/logs/${ARR}_%A_%a.out $R/camp_array.sh $ARR
  exit $?
fi
cd $R || exit 2
echo "host=$(hostname) array=$ARR block=$SLURM_ARRAY_TASK_ID job=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID} start=$(date -Iseconds)"
$PY -u $R/camp_task.py $ARR $SLURM_ARRAY_TASK_ID
RC=$?
echo "end=$(date -Iseconds) exit=$RC"
exit $RC
