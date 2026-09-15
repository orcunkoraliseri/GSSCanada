#!/bin/bash
#SBATCH --job-name=t18b
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --array=0-1
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T18b/logs/slurm_t18b_%A_%a.out

# t18b_job.sh -- T18b sbatch array: task 0 = N-f, task 1 = Nb-f.
# Task doc: 2026-09-15_T18b_wp1_linkage_lever_and_frozen_frame.md, Brief step 2.
# Shell/precedent matches T18's own t18_chain.sh (#!/bin/bash sbatch script;
# tcsh is only the login-node ssh session shell, not the batch script shell).
# No dependency: T18 outputs (Arm N excl stock, T18/reference, T18/input)
# already exist on disk before this array is submitted.

set -u

PYBIN=/speed-scratch/o_iseri/envs/step4/bin/python
T18B=/speed-scratch/o_iseri/2J_revision/T18b
SCRIPTS=$T18B/T18b_scripts

mkdir -p "$T18B/logs" "$T18B/out/nf" "$T18B/out/nbf"

if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
    BUILD=nf
else
    BUILD=nbf
fi

echo "=== T18b task $SLURM_ARRAY_TASK_ID = build $BUILD ==="
echo "host: $(hostname)  date: $(date)  job: $SLURM_JOB_ID"

"$PYBIN" "$SCRIPTS/t18b_pipeline.py" --build "$BUILD"
rc=$?
if [ $rc -ne 0 ]; then
    echo "T18B_STEP_FAILED: t18b_pipeline.py (build=$BUILD) exit=$rc"
    exit $rc
fi

echo "=== running t18b_metrics.py for build $BUILD ==="
"$PYBIN" "$SCRIPTS/t18b_metrics.py" --build "$BUILD"
rc2=$?
if [ $rc2 -ne 0 ]; then
    echo "T18B_STEP_FAILED: t18b_metrics.py (build=$BUILD) exit=$rc2"
    exit $rc2
fi

echo "=== TASK $SLURM_ARRAY_TASK_ID (build $BUILD) COMPLETE, exit 0 ==="
