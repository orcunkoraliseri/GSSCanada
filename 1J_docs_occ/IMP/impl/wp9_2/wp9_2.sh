#!/bin/tcsh
#SBATCH --job-name=wp9_2_stage2
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_%j.out

# WP9 Stage 2: draw the manifest of simulated households BEFORE any EnergyPlus run
# (Ruling B). Task doc:
#   1J_docs_occ/IMP/impl/2026-09-19_WP9_stage2_draw_manifest.md
#
# Steps (task doc "Job" section):
#   0. md5sum the two never-edit code files (start).
#   1. Import-chain guard (eSim_bem_utils.integration / .neighbourhood importable).
#   2. Build the real manifest (household-rule random, 30 draws) -> draw_manifest.csv,
#      pool_summary.csv, manifest_inputs.txt.
#   3. Build it twice more for G2.5: a full repeat build, and a --draws 10 build.
#   4. Build the "April rule" control manifest (household-rule april, 30 draws).
#   5. Gate 2 on the real manifest (all six checks; G2.5 wired to the repeat/draws10
#      builds).
#   6. Gate 2 on the control manifest (only G2.1-G2.4 are evaluable from it; G2.0/G2.5
#      print NOT_EVALUABLE, which is expected -- see task doc "Seen failing first").
#   7. Gate 2 on the April 2025 reference file ALONE, for G2.0 (must FAIL: household
#      71748 carries two dwelling types, plan log (ad)).
#   8. md5sum the two never-edit code files (end) -- must match step 0.
#   9. JOB DONE.

set STAGE2_DIR = /speed-scratch/o_iseri/1J_rerun/stage2
set CODE_DIR   = /speed-scratch/o_iseri/1J_rerun/code
set IDF_DIR    = /speed-scratch/o_iseri/1J_rerun/code/BEM_Setup/Neighbourhoods
set PY         = /speed-scratch/o_iseri/GSSCanada/venv/bin/python

set GRID_2005 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2010 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2015 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2022 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2025 = /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv
set APRIL_REF = /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/reference/BEM_Schedules_2025_APRIL.csv

# Design section names the manifest path exactly as $STAGE2_DIR/draw_manifest.csv
# (no subfolder) -- outputs are written flat alongside the uploaded scripts.
set OUT_DIR = $STAGE2_DIR
mkdir -p $OUT_DIR

set MANIFEST_PY = $STAGE2_DIR/wp9_2_manifest.py
set GATE2_PY    = $STAGE2_DIR/wp9_2_gate2.py

set REAL_MANIFEST     = $OUT_DIR/draw_manifest.csv
set REAL_POOL_SUMMARY = $OUT_DIR/pool_summary.csv
set REAL_INPUTS       = $OUT_DIR/manifest_inputs.txt
set REPEAT_MANIFEST   = $OUT_DIR/draw_manifest_repeat.csv
set DRAWS10_MANIFEST  = $OUT_DIR/draw_manifest_draws10.csv
set CONTROL_MANIFEST  = $OUT_DIR/draw_manifest_control.csv
set CONTROL_POOL_SUMMARY = $OUT_DIR/pool_summary_control.csv

echo "=== Step 0: md5sum never-edit code files (START) ==="
md5sum $CODE_DIR/eSim_bem_utils/integration.py
md5sum $CODE_DIR/eSim_bem_utils/neighbourhood.py

echo "=== Step 1: import-chain guard ==="
$PY -c "import sys; sys.path.insert(0, '$CODE_DIR'); import eSim_bem_utils.integration, eSim_bem_utils.neighbourhood; print('IMPORT CHAIN: OK')"
if ( $status != 0 ) then
    echo "IMPORT CHAIN: FAILED"
    exit 10
endif

echo "=== Step 2: build real manifest (household-rule random, 30 draws) ==="
$PY $MANIFEST_PY \
    --code-dir $CODE_DIR \
    --grid-2005 $GRID_2005 --grid-2010 $GRID_2010 --grid-2015 $GRID_2015 \
    --grid-2022 $GRID_2022 --grid-2025 $GRID_2025 \
    --idf-dir $IDF_DIR \
    --draws 30 --household-rule random \
    --out-manifest $REAL_MANIFEST \
    --out-pool-summary $REAL_POOL_SUMMARY \
    --out-inputs $REAL_INPUTS
if ( $status != 0 ) then
    echo "GUARD FAIL: real manifest build did not exit 0"
    exit 4
endif
if ( ! -e "$REAL_MANIFEST" ) then
    echo "GUARD FAIL: $REAL_MANIFEST not produced"
    exit 4
endif

echo "=== Step 3a: rebuild real manifest a second time (G2.5 full-build reproducibility) ==="
$PY $MANIFEST_PY \
    --code-dir $CODE_DIR \
    --grid-2005 $GRID_2005 --grid-2010 $GRID_2010 --grid-2015 $GRID_2015 \
    --grid-2022 $GRID_2022 --grid-2025 $GRID_2025 \
    --idf-dir $IDF_DIR \
    --draws 30 --household-rule random \
    --out-manifest $REPEAT_MANIFEST
if ( $status != 0 ) then
    echo "GUARD FAIL: repeat manifest build did not exit 0"
    exit 4
endif

echo "=== Step 3b: build with --draws 10 (G2.5 subset reproducibility) ==="
$PY $MANIFEST_PY \
    --code-dir $CODE_DIR \
    --grid-2005 $GRID_2005 --grid-2010 $GRID_2010 --grid-2015 $GRID_2015 \
    --grid-2022 $GRID_2022 --grid-2025 $GRID_2025 \
    --idf-dir $IDF_DIR \
    --draws 10 --household-rule random \
    --out-manifest $DRAWS10_MANIFEST
if ( $status != 0 ) then
    echo "GUARD FAIL: draws10 manifest build did not exit 0"
    exit 4
endif

echo "=== Step 4: build April-rule CONTROL manifest (find_best_match_household, 30 draws) ==="
$PY $MANIFEST_PY \
    --code-dir $CODE_DIR \
    --grid-2005 $GRID_2005 --grid-2010 $GRID_2010 --grid-2015 $GRID_2015 \
    --grid-2022 $GRID_2022 --grid-2025 $GRID_2025 \
    --idf-dir $IDF_DIR \
    --draws 30 --household-rule april \
    --out-manifest $CONTROL_MANIFEST \
    --out-pool-summary $CONTROL_POOL_SUMMARY
if ( $status != 0 ) then
    echo "GUARD FAIL: control manifest build did not exit 0"
    exit 4
endif

echo "=== Step 5: Gate 2 on the REAL manifest (all six checks) ==="
$PY $GATE2_PY \
    --code-dir $CODE_DIR \
    --grid-file 2005=$GRID_2005 --grid-file 2010=$GRID_2010 --grid-file 2015=$GRID_2015 \
    --grid-file 2022=$GRID_2022 --grid-file 2025=$GRID_2025 \
    --manifest $REAL_MANIFEST \
    --pool-summary $REAL_POOL_SUMMARY \
    --idf-dir $IDF_DIR \
    --expected-draws 30 \
    --repeat-manifest $REPEAT_MANIFEST \
    --draws10-manifest $DRAWS10_MANIFEST \
    --draws10-count 10

echo "=== Step 6: Gate 2 on the CONTROL (April-rule) manifest -- G2.3/G2.4 only ==="
$PY $GATE2_PY \
    --code-dir $CODE_DIR \
    --manifest $CONTROL_MANIFEST \
    --pool-summary $CONTROL_POOL_SUMMARY \
    --idf-dir $IDF_DIR \
    --expected-draws 30

echo "=== Step 7: Gate 2 on the April 2025 REFERENCE file alone -- G2.0 must FAIL ==="
$PY $GATE2_PY \
    --grid-file 2025_april_reference=$APRIL_REF

echo "=== Step 8: md5sum never-edit code files (END) ==="
md5sum $CODE_DIR/eSim_bem_utils/integration.py
md5sum $CODE_DIR/eSim_bem_utils/neighbourhood.py

echo "JOB DONE (WP9 Stage 2, draw manifest + Gate 2)"
