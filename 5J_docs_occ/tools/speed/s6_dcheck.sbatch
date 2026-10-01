#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -J s6_dcheck
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_dcheck_%j.out
export OMP_NUM_THREADS=4
. /speed-scratch/o_iseri/5J/test/code/s6_prelude.sh
$PY -u $C/s6_checks.py dcheck
RC=$?
echo "s6_dcheck EXIT $RC end=$(date -Iseconds)"
exit $RC
