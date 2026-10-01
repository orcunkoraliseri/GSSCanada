#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -J s7_bepcheck
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bepcheck_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
export CAMP_ROOT=$D/ep/ CAMP_PLAN=$D/ep/plan_rest/ CAMP_HH=$D/hh/pool/
export S7_TABLE=$D/in/district_runs_es.csv S7_IDS=$D/ep/all_ids.txt
$PY -u $C/s7_ep_check.py
RC=$?
echo "s7_bep_check EXIT $RC end=$(date -Iseconds)"
exit 0
