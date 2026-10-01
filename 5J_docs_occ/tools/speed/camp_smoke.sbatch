#!/bin/bash
#SBATCH -J campsmoke
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/logs/smoke_%j.out
R=/speed-scratch/o_iseri/5J/campaign
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
/speed-scratch/o_iseri/envs/step4/bin/python -u $R/camp_smoke.py
RC=$?
echo "end=$(date -Iseconds) exit=$RC"
exit $RC
