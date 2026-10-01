#!/bin/bash
#SBATCH -J camp2SF
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/seenfail_%j.out
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -u $R/camp2_seenfail.py
RC=$?
echo "SEENFAIL_EXIT $RC"
echo "end=$(date -Iseconds)"
exit $RC
