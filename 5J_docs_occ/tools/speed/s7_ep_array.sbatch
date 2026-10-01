#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -J s7_eppilot
#SBATCH --array=1-4%4
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_eppilot_%A_%a.out
# one pilot block per task (4 CPUs in all); the campaign task code on the district run table
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
export CAMP_ROOT=$D/ep/ CAMP_PLAN=$D/ep/plan_pilot/ CAMP_HH=$D/hh/pool/
$PY -u $C/s7_ep_task.py es_madrid_2010 $SLURM_ARRAY_TASK_ID
RC=$?
echo "end=$(date -Iseconds) exit=$RC"
exit $RC
