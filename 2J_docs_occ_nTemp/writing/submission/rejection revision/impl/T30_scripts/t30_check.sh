#!/encs/bin/bash
#SBATCH --job-name=t30_check
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_check_%j.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_check_%j.err

# T30 collector: V0-V5 + household peak-hour spread, for this arm, T22's
# static arm and T21's Step-8 runs. Read-only against all three staged trees.
#
# NOT SUBMITTED by phase A. Phase B submits this as its own job with `afterok`
# on t30_array.sh, T22's array (1328310) and T21's Step-8 array, per the T30
# task doc's Phase B section -- run it only after all three trees hold their
# full output (submit standalone, e.g. for a partial look, only if the
# manager explicitly asks for an early read).
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT_DIR=/speed-scratch/o_iseri/2J_revision/T30/T30_scripts

mkdir -p /speed-scratch/o_iseri/2J_revision/T30/logs

echo "=== T30 check | Start: $(date) ==="
$PYTHON "$SCRIPT_DIR/t30_check.py" \
    --t30-root /speed-scratch/o_iseri/2J_revision/T30 \
    --t22-root /speed-scratch/o_iseri/2J_revision/T22 \
    --t21-root /speed-scratch/o_iseri/2J_revision/T21 \
    --code-root /speed-scratch/o_iseri/2J_revision/code_step8/repo \
    --sched-dir /speed-scratch/o_iseri/2J_revision/T21/sched_activity
EXIT=$?
echo "=== T30 check | End: $(date)  exit=$EXIT ==="
exit $EXIT
