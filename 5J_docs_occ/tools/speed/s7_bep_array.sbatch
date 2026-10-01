#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -J s7_bep
#SBATCH --array=1-15%15
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bep_%A_%a.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
export CAMP_ROOT=$D/ep/ CAMP_PLAN=$D/ep/plan_rest/ CAMP_HH=$D/hh/pool/
$PY -u $C/s7_ep_task.py es_madrid_2010 $SLURM_ARRAY_TASK_ID
RC=$?
echo "end=$(date -Iseconds) exit=$RC"
exit $RC
