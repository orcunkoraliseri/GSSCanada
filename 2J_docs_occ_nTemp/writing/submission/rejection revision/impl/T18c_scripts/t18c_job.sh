#!/bin/bash
#SBATCH --job-name=t18c
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --array=0-1
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T18c/logs/slurm_t18c_%A_%a.out

# t18c_job.sh -- T18c Frame v2 sbatch array: task 0 = nf, task 1 = nbf.
# Task doc: 2026-09-15_T18c_wp1_frame_v2.md, Rules (employee) section.
# Shell/precedent matches T18's t18_chain.sh and T18b's t18b_job.sh
# (#!/bin/bash sbatch script; tcsh is only the login-node ssh session shell,
# not the batch script shell -- T18b Decisions explains this explicitly).
# No dependency: T18 (arm_N) and T18b (nbf relink through run_exclusion())
# outputs already exist on disk before this array is submitted.
# Directory creation happens inside this job script, never on the login node
# (task doc Rules).

set -u

PYBIN=/speed-scratch/o_iseri/envs/step4/bin/python
T18C=/speed-scratch/o_iseri/2J_revision/T18c
SCRIPTS=$T18C/T18c_scripts

mkdir -p "$T18C/logs" "$T18C/out/nf" "$T18C/out/nbf" \
         "$T18C/nf/repo/outputs/aug_pipeline" "$T18C/nf/repo/outputs/BEM_Setup" \
         "$T18C/nbf/repo/outputs/aug_pipeline" "$T18C/nbf/repo/outputs/BEM_Setup"

if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
    BUILD=nf
else
    BUILD=nbf
fi

echo "=== T18c task $SLURM_ARRAY_TASK_ID = build $BUILD (Frame v2) ==="
echo "host: $(hostname)  date: $(date)  job: $SLURM_JOB_ID"

"$PYBIN" "$SCRIPTS/t18c_pipeline.py" --build "$BUILD"
rc=$?
if [ $rc -ne 0 ]; then
    echo "T18C_STEP_FAILED: t18c_pipeline.py (build=$BUILD) exit=$rc"
    exit $rc
fi

echo "=== running t18c_metrics.py for build $BUILD ==="
"$PYBIN" "$SCRIPTS/t18c_metrics.py" --build "$BUILD"
rc2=$?
if [ $rc2 -ne 0 ]; then
    echo "T18C_STEP_FAILED: t18c_metrics.py (build=$BUILD) exit=$rc2"
    exit $rc2
fi

echo "=== TASK $SLURM_ARRAY_TASK_ID (build $BUILD) COMPLETE, exit 0 ==="
