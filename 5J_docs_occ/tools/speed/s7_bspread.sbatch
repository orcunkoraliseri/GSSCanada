#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -J s7_bspread
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bspread_%j.out
export OMP_NUM_THREADS=1
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
export CAMP_ROOT=$D/ep/ CAMP_PLAN=$D/ep/plan_rest/ CAMP_HH=$D/hh/pool/
$PY -u $C/s7_spread.py
RC=$?
echo "s7_bspread EXIT $RC end=$(date -Iseconds)"
exit $RC
