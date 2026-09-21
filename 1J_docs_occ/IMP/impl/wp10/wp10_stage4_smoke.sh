#!/bin/tcsh
#SBATCH --job-name=wp10_stage4_smoke
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_smoke_%j.out

# WP10 Stage 4: staged-patch smoke test + Gate 4 seen-failing-first, BEFORE any
# EnergyPlus job is submitted. Task doc:
#   1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md
#
# Steps:
#   1. Import-chain guard: the staged, patched eSim_bem_utils.main must import cleanly.
#   2. Gate 4 selftest (wp10_gate4.py --mode selftest): synthetic seen-failing-first
#      checks for G4.0/G4.1/G4.2/G4.3, PLUS G4.1's static check against the REAL
#      deployed patched module.
#   3. Stage 4 probe (wp10_stage4_probe.py): cheap, no-EnergyPlus check of whether the
#      REAL draw_manifest.csv's households can actually be found (region='Quebec')
#      in the CURRENTLY STAGED BEM_Schedules_{year}.csv files, for all six
#      neighbourhoods' draw 1 -- this is the input this task found may not agree
#      with the manifest (see task doc Decisions).

set CODE_DIR  = /speed-scratch/o_iseri/1J_rerun/code
set STAGE4_DIR = /speed-scratch/o_iseri/1J_rerun/stage4
set PY        = /speed-scratch/o_iseri/GSSCanada/venv/bin/python

echo "=== STEP 1: import-chain guard ==="
$PY -c "import sys; sys.path.insert(0, '$CODE_DIR'); import eSim_bem_utils.main as m; print('IMPORT CHAIN: OK', m.__file__)"
if ($status != 0) then
    echo "IMPORT CHAIN: FAILED"
    exit 10
endif

echo "=== STEP 2: Gate 4 selftest ==="
$PY $STAGE4_DIR/wp10_gate4.py --mode selftest --code-dir $CODE_DIR
set GATE4_SELFTEST_STATUS = $status
echo "GATE4 SELFTEST EXIT: $GATE4_SELFTEST_STATUS"

echo "=== STEP 3: Stage 4 real-manifest / real-schedule-file probe (no EnergyPlus) ==="
$PY $STAGE4_DIR/wp10_stage4_probe.py
set PROBE_STATUS = $status
echo "PROBE EXIT: $PROBE_STATUS"

echo "JOB DONE"
