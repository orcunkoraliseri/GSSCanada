#!/bin/bash
# V3b: 4 building-city cells x {U, R, N, X, U2} = 20 tasks, 1 CPU each (tasks_v3b.csv).
# Throttle %2: 3J headroom at submission = 32 - 30 live 1J CPUs = 2 (see V3_design_and_runs.md).
#SBATCH --job-name=3J_V3b
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-19%2
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/v3b_%A_%a.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
cd $CODE || exit 1
echo "V3b task $SLURM_ARRAY_TASK_ID node $(hostname) $(date)"
$PY -u v3_task.py $ROOT/tasks_v3b.csv $SLURM_ARRAY_TASK_ID $ROOT/runs
RC=$?
echo "V3b task $SLURM_ARRAY_TASK_ID exit=$RC $(date)"
exit $RC
