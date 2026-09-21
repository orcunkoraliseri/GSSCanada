#!/bin/tcsh
#SBATCH --job-name=wp10_stage4_verify_probe
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp10_stage4_verify_probe_%j.out

# WP10 Stage 4: verify the newly re-staged BEM_Schedules_{year}.csv files (already
# re-staged by job 1341381, steps 1-2 of that job succeeded) then re-run the cheap
# no-EnergyPlus probe. Job 1341381's own step 3 crashed on a tcsh quoting bug
# ("$year:" is parsed as a history-modifier in tcsh even inside double quotes) before
# reaching the probe -- this job redoes ONLY the verify+probe part, with the colon
# moved into its own echo call so it is never adjacent to "$year".
# Task doc: 1J_docs_occ/IMP/impl/2026-09-21_WP10_stage4_manifest_patch.md

set BEM_DIR    = /speed-scratch/o_iseri/1J_rerun/code/BEM_Setup
set STAGE4_DIR = /speed-scratch/o_iseri/1J_rerun/stage4
set PY         = /speed-scratch/o_iseri/GSSCanada/venv/bin/python

echo "=== STEP 3 (retry): verify headers and row counts of the newly staged files ==="
foreach year (2005 2010 2015 2022 2025)
    echo -n "HEADER "
    echo -n "$year"
    echo -n ": "
    head -1 $BEM_DIR/BEM_Schedules_${year}.csv
    echo -n "ROWS "
    echo -n "$year"
    echo -n " (incl header): "
    wc -l < $BEM_DIR/BEM_Schedules_${year}.csv
end

echo "=== STEP 4: re-run the cheap no-EnergyPlus probe on the newly staged files ==="
$PY $STAGE4_DIR/wp10_stage4_probe.py
set PROBE_STATUS = $status
echo "PROBE EXIT: $PROBE_STATUS"

echo "JOB DONE"
