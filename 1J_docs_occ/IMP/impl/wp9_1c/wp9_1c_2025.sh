#!/bin/tcsh
#SBATCH --job-name=wp9_1c_2025
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=48G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_stage1c_2025_%j.out

# WP9 Stage 1c (T8): rebuild the 2025 occupancy/BEM file with Ruling A (grid
# denominator), Ruling D-1J-A3 (start from the April Matched_Population_Keys.csv,
# do NOT re-run the matcher). Task doc:
#   1J_docs_occ/IMP/impl/2026-09-19_WP9_stage1c_2025.md ("Manager ruling after
#   BLOCKED", tasks T5-T8).
#
# Steps (task doc T8):
#   0. md5sum the three never-modify files + every uploaded input; TensorFlow
#      import check (exit 3, "TF MISSING", if it fails -- never pip-install).
#   1. driver --from-keys (expansion -> refinement -> aggregation); guard each
#      of the three expected outputs with exit 4 if missing.
#   2. --convert original -> BEM_Schedules_2025_original.csv (fixed name removed).
#   3. wp9_1c_repro_check.py: original vs reference/BEM_Schedules_2025_APRIL.csv.
#   4. --convert grid -> BEM_Schedules_2025_grid.csv (fixed name removed).
#   5. --convert hhsize -> BEM_Schedules_2025_hhsize.csv.
#   6. gate1_occ.py on grid and hhsize.
#   7. md5sum the three never-modify files again.
# Steps 4-6 run regardless of the Step-3 repro verdict (task doc: "Steps 4-6
# run whatever the repro verdict is").

setenv GSS_BASE_DIR /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy
# Ruling D-1J-A4: separate venv (GSSCanada venv's exact versions + tensorflow-cpu),
# built by wp9_1c_venv2025.sh; the GSSCanada venv has no TensorFlow (job 1339862, exit 3).
set PY = /speed-scratch/o_iseri/1J_rerun/venv2025/bin/python
echo "PYTHON USED: $PY (venv2025, ruling D-1J-A4)"
set CODE = /speed-scratch/o_iseri/1J_rerun/occ2025/code/eSim_occ_utils/25CEN22GSS_classification
set GATE = /speed-scratch/o_iseri/1J_rerun/occ/code/eSim_occ_utils/gate1_occ.py
set REPRO = $CODE/wp9_1c_repro_check.py
set OUT_DIR = $GSS_BASE_DIR/Outputs_CENSUS
set REF_FILE = $GSS_BASE_DIR/reference/BEM_Schedules_2025_APRIL.csv
set FIXED_FILE = $OUT_DIR/BEM_Schedules_2025.csv
set ORIGINAL_FILE = $OUT_DIR/BEM_Schedules_2025_original.csv
set GRID_FILE = $OUT_DIR/BEM_Schedules_2025_grid.csv
set HHSIZE_FILE = $OUT_DIR/BEM_Schedules_2025_hhsize.csv

cd $CODE

echo "=== Step 0a: md5sum never-modify files + uploaded inputs (START) ==="
md5sum eSim_datapreprocessing.py
md5sum eSim_dynamicML_mHead_alignment.py
md5sum previous/eSim_dynamicML_mHead.py
md5sum $GSS_BASE_DIR/Outputs_Aligned/Matched_Population_Keys.csv
md5sum $GSS_BASE_DIR/Outputs_Aligned/Aligned_GSS_2022.csv
md5sum $GSS_BASE_DIR/Outputs_CENSUS/cen06_filtered.csv
md5sum $GSS_BASE_DIR/Outputs_CENSUS/cen11_filtered.csv
md5sum $REF_FILE

echo "=== Step 0b: TensorFlow import check ==="
$PY -c "import tensorflow"
if ( $status != 0 ) then
    echo "TF MISSING"
    exit 3
endif
echo "TensorFlow import OK"

echo "=== Step 0c: import chain check (job 1339869 failed here, ModuleNotFoundError eSim_occ_utils) ==="
$PY -c "import wp9_1c_2025_rebuild as d; d._add_repo_dirs_to_path(); import run_step2, run_step3; print('IMPORT CHAIN: OK', run_step2.OUTPUT_DIR_ALIGNED)"
if ( $status != 0 ) then
    echo "IMPORT CHAIN: FAILED"
    exit 10
endif

echo "=== Step 1: --from-keys (expansion -> refinement -> aggregation) ==="
$PY wp9_1c_2025_rebuild.py --from-keys

if ( ! -e "$OUT_DIR/Full_Expanded_Schedules.csv" ) then
    echo "GUARD FAIL: Full_Expanded_Schedules.csv not produced"
    exit 4
endif
if ( ! -e "$OUT_DIR/Full_Expanded_Schedules_Refined.csv" ) then
    echo "GUARD FAIL: Full_Expanded_Schedules_Refined.csv not produced"
    exit 4
endif
if ( ! -e "$OUT_DIR/Full_data.csv" ) then
    echo "GUARD FAIL: Full_data.csv not produced"
    exit 4
endif
echo "Step 1 outputs present: Full_Expanded_Schedules.csv, Full_Expanded_Schedules_Refined.csv, Full_data.csv"

echo "=== Step 2: --convert original (P3 override NOT installed; repro check input) ==="
if ( -e "$FIXED_FILE" ) then
    echo "GUARD FAIL: fixed-name output already exists before the original-formula run: $FIXED_FILE"
    exit 5
endif
$PY wp9_1c_2025_rebuild.py --convert original
if ( ! -e "$FIXED_FILE" ) then
    echo "GUARD FAIL: expected original-formula output not found: $FIXED_FILE"
    exit 4
endif
cp -a $FIXED_FILE $ORIGINAL_FILE
echo "Saved original-formula version to $ORIGINAL_FILE"
rm $FIXED_FILE

echo "=== Step 3: reproduction check (original vs April reference) ==="
$PY $REPRO $ORIGINAL_FILE $REF_FILE

echo "=== Step 4: --convert grid (Ruling A) ==="
$PY wp9_1c_2025_rebuild.py --convert grid
if ( ! -e "$FIXED_FILE" ) then
    echo "GUARD FAIL: expected grid output not found: $FIXED_FILE"
    exit 4
endif
cp -a $FIXED_FILE $GRID_FILE
echo "Saved grid-denominator version to $GRID_FILE"
rm $FIXED_FILE

echo "=== Step 5: --convert hhsize (sensitivity check) ==="
$PY wp9_1c_2025_rebuild.py --convert hhsize
if ( ! -e "$FIXED_FILE" ) then
    echo "GUARD FAIL: expected hhsize output not found: $FIXED_FILE"
    exit 4
endif
cp -a $FIXED_FILE $HHSIZE_FILE
echo "Saved hhsize-denominator version to $HHSIZE_FILE"

echo "=== Step 6: Gate 1 on grid and hhsize ==="
$PY $GATE $GRID_FILE $HHSIZE_FILE

echo "=== Step 7: md5sum never-modify files (END) ==="
md5sum eSim_datapreprocessing.py
md5sum eSim_dynamicML_mHead_alignment.py
md5sum previous/eSim_dynamicML_mHead.py

echo "JOB DONE (WP9 Stage 1c, 2025 rebuild)"
