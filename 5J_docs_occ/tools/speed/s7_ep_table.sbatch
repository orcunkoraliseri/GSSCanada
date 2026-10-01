#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -J s7_eptable
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_eptable_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
export CAMP_ROOT=$D/ep/ CAMP_PLAN=$D/ep/plan_pilot/ CAMP_HH=$D/hh/pool/
mkdir -p $D/ep
$PY -u $C/s7_ep_table.py
RC=$?
echo "s7_ep_table EXIT $RC end=$(date -Iseconds)"
exit $RC
