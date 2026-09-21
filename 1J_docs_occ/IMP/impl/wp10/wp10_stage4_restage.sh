#!/bin/tcsh
#SBATCH --job-name=wp10_stage4_restage
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_restage_%j.out

# WP10 Stage 4: re-stage BEM_Schedules_{year}.csv from the Stage-1 REBUILT grid files
# (manager ruling (a), 2026-09-21, plan log (as)) -- archive the currently staged
# April BEM_Schedules_{year}.csv files first (never overwrite without archiving),
# then copy the rebuilt grid files into place, then re-run the cheap no-EnergyPlus
# probe (wp10_stage4_probe.py) to see whether all six neighbourhoods now succeed.
# Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md, "Next"
# section steps 2-3.

set BEM_DIR    = /speed-scratch/o_iseri/1J_rerun/code/BEM_Setup
set STAGE4_DIR = /speed-scratch/o_iseri/1J_rerun/stage4
set PY         = /speed-scratch/o_iseri/GSSCanada/venv/bin/python

set GRID_2005 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2010 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2015 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2022 = /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct_grid.csv
set GRID_2025 = /speed-scratch/o_iseri/1J_rerun/occ2025/0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025_grid.csv

echo "=== STEP 1: archive currently staged April BEM_Schedules_{year}.csv files (never overwrite without archiving) ==="
foreach year (2005 2010 2015 2022 2025)
    if (-e $BEM_DIR/BEM_Schedules_${year}.csv.pre_WP10_stage4_reload) then
        echo "ARCHIVE ABORT: $BEM_DIR/BEM_Schedules_${year}.csv.pre_WP10_stage4_reload already exists -- refusing to overwrite an existing archive"
        exit 20
    endif
    cp $BEM_DIR/BEM_Schedules_${year}.csv $BEM_DIR/BEM_Schedules_${year}.csv.pre_WP10_stage4_reload
    if ($status != 0) then
        echo "ARCHIVE FAILED: year $year"
        exit 21
    endif
    echo "ARCHIVED: BEM_Schedules_${year}.csv -> BEM_Schedules_${year}.csv.pre_WP10_stage4_reload"
end

echo "=== STEP 2: re-stage BEM_Schedules_{year}.csv from the Stage-1 REBUILT grid files ==="
cp $GRID_2005 $BEM_DIR/BEM_Schedules_2005.csv
if ($status != 0) then
    echo "RESTAGE FAILED: 2005"
    exit 22
endif
echo "RESTAGED: BEM_Schedules_2005.csv <- $GRID_2005"

cp $GRID_2010 $BEM_DIR/BEM_Schedules_2010.csv
if ($status != 0) then
    echo "RESTAGE FAILED: 2010"
    exit 22
endif
echo "RESTAGED: BEM_Schedules_2010.csv <- $GRID_2010"

cp $GRID_2015 $BEM_DIR/BEM_Schedules_2015.csv
if ($status != 0) then
    echo "RESTAGE FAILED: 2015"
    exit 22
endif
echo "RESTAGED: BEM_Schedules_2015.csv <- $GRID_2015"

cp $GRID_2022 $BEM_DIR/BEM_Schedules_2022.csv
if ($status != 0) then
    echo "RESTAGE FAILED: 2022"
    exit 22
endif
echo "RESTAGED: BEM_Schedules_2022.csv <- $GRID_2022"

cp $GRID_2025 $BEM_DIR/BEM_Schedules_2025.csv
if ($status != 0) then
    echo "RESTAGE FAILED: 2025"
    exit 22
endif
echo "RESTAGED: BEM_Schedules_2025.csv <- $GRID_2025"

echo "=== STEP 3: verify headers and row counts of the newly staged files ==="
foreach year (2005 2010 2015 2022 2025)
    echo -n "HEADER $year: "
    head -1 $BEM_DIR/BEM_Schedules_${year}.csv
    echo -n "ROWS $year (incl header): "
    wc -l < $BEM_DIR/BEM_Schedules_${year}.csv
end

echo "=== STEP 4: re-run the cheap no-EnergyPlus probe on the newly staged files ==="
$PY $STAGE4_DIR/wp10_stage4_probe.py
set PROBE_STATUS = $status
echo "PROBE EXIT: $PROBE_STATUS"

echo "JOB DONE"
