#!/bin/bash
# V3c: 4 building-city cells x {F} = 4 tasks, 1 CPU each (tasks_v3c.csv). Standalone from v3b_array.sh
# (v3c_task.py, arm F only) so V3b's own pending array/checker (1342426/1342427) are never touched.
#SBATCH --job-name=3J_V3c
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-3
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/v3c_%A_%a.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
cd $CODE || exit 1
echo "V3c task $SLURM_ARRAY_TASK_ID node $(hostname) $(date)"
$PY -u v3c_task.py $ROOT/tasks_v3c.csv $SLURM_ARRAY_TASK_ID $ROOT/runs
RC=$?
echo "V3c task $SLURM_ARRAY_TASK_ID exit=$RC $(date)"
exit $RC
