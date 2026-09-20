#!/bin/tcsh
#SBATCH --job-name=wp9_f1j8_age88
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8_%j.out

# F-1J-8: measure how much the census age code 88 ("not available", mapped into the
# 75+ group by every alignment.py) changes the occupancy result. READ-ONLY -- this
# job writes only its own log and files under f1j8/.
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-19_WP9_f1j8_age88.md

set PY      = /speed-scratch/o_iseri/GSSCanada/venv/bin/python
set F1J8_DIR = /speed-scratch/o_iseri/1J_rerun/f1j8
set OUT_DIR  = $F1J8_DIR/results

echo "=== F-1J-8 age-88 sensitivity measurement ==="
echo "host: `hostname`"
echo "date: `date`"

$PY $F1J8_DIR/wp9_f1j8_age88.py --mode real --out-dir $OUT_DIR
set PYSTATUS = $status

if ( $PYSTATUS != 0 ) then
    echo "MEASUREMENT SCRIPT FAILED with exit code $PYSTATUS"
    exit $PYSTATUS
endif

echo "JOB DONE"
