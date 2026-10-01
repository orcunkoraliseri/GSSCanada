#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -J s7_sample
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_sample_%j.out
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
$PY -u $C/s7_sample.py
RC=$?
echo "s7_sample EXIT $RC end=$(date -Iseconds)"
echo "md5 sample_buildings.csv $(md5sum < $D/in/sample_buildings.csv | cut -d' ' -f1)"
exit $RC
