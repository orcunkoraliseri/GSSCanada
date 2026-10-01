#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -J s7_bwb
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bwcheckb_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
$PY -u $C/s7_wcheck.py b
RC=$?
echo "s7_bwcheck EXIT $RC end=$(date -Iseconds)"
exit $RC
