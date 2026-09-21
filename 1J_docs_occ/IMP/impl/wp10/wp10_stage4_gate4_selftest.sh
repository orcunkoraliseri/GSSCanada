#!/bin/bash
#SBATCH --job-name=wp10_stage4_gate4_selftest
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_gate4_selftest_%j.out

# WP10 Stage 4, step 4 of the "Next" ruling: fresh Gate 4 selftest run, chained
# BEFORE the six Default jobs (repo rule: seen failing then passing, re-verified at
# every real submission, not just once). Same command as job 1341372's step 2.
# Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

CODE_DIR=/speed-scratch/o_iseri/1J_rerun/code
STAGE4_DIR=/speed-scratch/o_iseri/1J_rerun/stage4
PY=/speed-scratch/o_iseri/GSSCanada/venv/bin/python

echo "=== Gate 4 selftest (fresh run before the six Default jobs) ==="
$PY $STAGE4_DIR/wp10_gate4.py --mode selftest --code-dir $CODE_DIR
STATUS=$?
echo "GATE4 SELFTEST EXIT: $STATUS"
exit $STATUS
