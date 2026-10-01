#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -J s6_snapshot
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_snapshot_%j.out
export OMP_NUM_THREADS=1
. /speed-scratch/o_iseri/5J/test/code/s6_prelude.sh
$PY -u $C/s6_checks.py snapshot
RC=$?
echo "s6_snapshot EXIT $RC end=$(date -Iseconds)"
exit $RC
