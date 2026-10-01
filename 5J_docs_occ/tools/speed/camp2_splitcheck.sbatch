#!/bin/bash
#SBATCH -J camp2Dv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/splitcheck_%j.out
cd /speed-scratch/o_iseri/5J/splits || exit 2
md5sum -c splits.md5
echo "MD5_CHECK_NOT_OK_COUNT $(md5sum -c splits.md5 | grep -vc ': OK')"
for f in *.txt; do echo "LINES $f $(wc -l < $f)"; done
ls -l
