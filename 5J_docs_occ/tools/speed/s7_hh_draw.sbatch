#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J s7_hhdraw
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_hhdraw_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
$PY -u $C/s7_hh_draw.py
RC=$?
echo "s7_hh_draw EXIT $RC end=$(date -Iseconds)"
exit $RC
