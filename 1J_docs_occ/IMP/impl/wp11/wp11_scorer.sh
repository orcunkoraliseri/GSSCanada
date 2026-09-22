#!/bin/bash
#SBATCH --job-name=wp11_scorer
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp11_scorer_%j.out

# WP11 item 6: one stopping-rule scorer job for block $BLOCK (env var, set with
# --export at submission). Chained --dependency=afterany on the LIGHT/HEAVY array
# tasks that finish block $BLOCK (and, implicitly, all earlier blocks, since
# wp11_stoprule.py --mode real reads blocks 1..BLOCK). NOT submitted by this task's
# employee -- the manager submits after reading Gate 4 PASS, workers-check PASS and
# the swap probe PASS, and writes this job's own id into stage4/draws/job_ids.txt as
# "SCORER $BLOCK <id>" so a later STOP can scancel it if it is still queued.
#
# Submission (manager, not hardcoded here), one per block b=1..6:
#   sbatch --dependency=afterany:<light_task_ids_for_block_b>:<heavy_task_ids_for_block_b> \
#          --export=BLOCK=<b> wp11_scorer.sh
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 6.

WP11=/speed-scratch/o_iseri/1J_rerun/stage4/wp11
VENV=/speed-scratch/o_iseri/GSSCanada/venv

if [ -z "$BLOCK" ]; then
  echo "ERROR: BLOCK env var not set -- stopping."
  exit 2
fi

source "$VENV/bin/activate"

echo "=== Running wp11_stoprule.py --mode real --block $BLOCK ==="
python "$WP11/wp11_stoprule.py" --mode real --block "$BLOCK"
EXIT_CODE=$?
echo "Done: wp11_scorer block=$BLOCK (exit code: $EXIT_CODE)"
exit $EXIT_CODE
