#!/bin/bash
# V3a: seed replicates, 2 scenarios x 4 cells x 5 residential-draw seeds = 40 tasks (tasks_v3a.csv).
# !!! TODO -- NOT SUBMITTABLE YET. Input products = the REBUILT Y2022/2030 products from
# !!! IMP/P10R_fix.md, not yet available. Before submitting: update v3_lib.PRODUCTS (file names +
# !!! md5s) to the rebuilt products, re-run v3_precheck_local.py (seed 42 rebuild must match the
# !!! rebuilt arm's frozen IDFs), re-upload, and set the throttle to the CPU headroom at that time.
#SBATCH --job-name=3J_V3a
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-39%2
#SBATCH --output=/speed-scratch/o_iseri/3J_V3/logs/v3a_%A_%a.out
source /speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/v3_env.sh
[ -f $ROOT/V3A_INPUTS_READY ] || { echo "FATAL: V3a inputs not marked ready (TODO P10R rebuilt products)"; exit 1; }
cd $CODE || exit 1
$PY -u v3_task.py $ROOT/tasks_v3a.csv $SLURM_ARRAY_TASK_ID $ROOT/runs
exit $?
