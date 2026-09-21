#!/bin/bash
#SBATCH --job-name=wp10_stage4_gate4_real
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_gate4_real_%j.out

# WP10 Stage 4, step 4 of the "Next" ruling: score Gate 4 (G4.0-G4.3) on the six
# real Default (--iter-count 1) runs, chained after all six finish (afterok).
# Reference file for G4.3 is the April BatchAll_MC_N20_v2 aggregated_eui.csv
# (unaffected by the schedule re-stage -- Default reads neither all_schedules nor
# the manifest, confirmed in this task doc's 4a Ledger entry).
# Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

CODE_DIR=/speed-scratch/o_iseri/1J_rerun/code
STAGE4_DIR=/speed-scratch/o_iseri/1J_rerun/stage4
PY=/speed-scratch/o_iseri/GSSCanada/venv/bin/python
MANIFEST=/speed-scratch/o_iseri/1J_rerun/stage2/draw_manifest.csv
BATCH_DIR=/speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1

echo "=== Gate 4, --mode real, on the six Stage-4c Default runs ==="
$PY $STAGE4_DIR/wp10_gate4.py \
    --mode real \
    --manifest $MANIFEST \
    --batch-dir $BATCH_DIR \
    --code-dir $CODE_DIR \
    --log-glob "/speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_default_RC*.out"
STATUS=$?
echo "GATE4 REAL EXIT: $STATUS"
exit $STATUS
