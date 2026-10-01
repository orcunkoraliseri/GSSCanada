#!/bin/bash
#SBATCH -J mzpcheck
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/mz_pilot/logs/check_%j.out
/speed-scratch/o_iseri/envs/step4/bin/python -u /speed-scratch/o_iseri/5J/mz_pilot/5thJ_mz_pilot_check.py
RC=$?
echo "CHECKER_EXIT_CODE=$RC"
exit $RC
