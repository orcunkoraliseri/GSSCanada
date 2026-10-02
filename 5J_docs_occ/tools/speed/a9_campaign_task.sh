#!/bin/bash
#SBATCH -J 5J_9l_run
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=12G
#SBATCH -o /speed-scratch/o_iseri/5J/modelA/campaign/logs/t_%A_%a.out
# 5J Step 9l: one array task = one Model A run = one row of the manifest (MANIFEST, passed with --export=ALL,MANIFEST=<csv>).
# Submit: sbatch --array=<from>-<to>%<k> --export=ALL,MANIFEST=<csv> a9_campaign_task.sh      (k = at most 32 CPUs for 5J in total)
C=/speed-scratch/o_iseri/5J/modelA/campaign
: ${MANIFEST:?MANIFEST not set}
: ${SLURM_ARRAY_TASK_ID:?no task id}
cd $C/root/5J_docs_occ/tools || exit 2
/speed-scratch/o_iseri/envs/step4/bin/python -u a9_campaign_task.py run $MANIFEST $SLURM_ARRAY_TASK_ID
exit $?
