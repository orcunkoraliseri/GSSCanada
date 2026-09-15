#!/bin/bash
#SBATCH --job-name=t18_chain
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --array=0-1
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T18/logs/slurm_%A_%a.out

# t18_chain.sh -- T18 sbatch array: task 0 = Arm C (control), task 1 = Arm N (new).
# Task doc: 2026-09-15_T18_wp1_rebuild_2022_build.md, Brief step 2.
# Runs t18_pipeline.py (the full staged chain, no pipeline source edits) then
# t18_metrics.py (N4 a-f + R0 for task 0) for its arm. Any failure inside
# either script prints the failing step name (t18_pipeline.py's _step()
# wrapper) before the non-zero exit propagates here.

set -u

PYBIN=/speed-scratch/o_iseri/envs/step4/bin/python
WORKDIR=/speed-scratch/o_iseri/2J_revision/T18
SCRIPTS=$WORKDIR/T18_scripts

mkdir -p "$WORKDIR/logs" "$WORKDIR/out"

if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
    ARM=C
else
    ARM=N
fi

echo "=== T18 chain task $SLURM_ARRAY_TASK_ID = Arm $ARM ==="
echo "host: $(hostname)  date: $(date)  job: $SLURM_JOB_ID"

"$PYBIN" "$SCRIPTS/t18_pipeline.py" --arm "$ARM"
rc=$?
if [ $rc -ne 0 ]; then
    echo "T18_CHAIN_STEP_FAILED: t18_pipeline.py (arm=$ARM) exit=$rc"
    exit $rc
fi

echo "=== running t18_metrics.py for arm $ARM ==="
"$PYBIN" "$SCRIPTS/t18_metrics.py" --arm "$ARM"
rc2=$?
if [ $rc2 -ne 0 ]; then
    echo "T18_CHAIN_STEP_FAILED: t18_metrics.py (arm=$ARM) exit=$rc2"
    exit $rc2
fi

echo "=== TASK $SLURM_ARRAY_TASK_ID (arm $ARM) COMPLETE, exit 0 ==="
