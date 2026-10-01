#!/bin/bash
#SBATCH -J camp2B
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/integrity_%j.out
# Part 2, Part B: G5J.1 over all 9,269 planned runs (6 workers: reading every extracted file is slow on 1 CPU).
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -u $R/camp_integrity.py --workers 6
RC=$?
echo "INTEGRITY_EXIT $RC"
echo "EXTRACTED_DISK_BYTES $(du -sb $R/extracted | cut -f1)"
echo "end=$(date -Iseconds)"
exit $RC
