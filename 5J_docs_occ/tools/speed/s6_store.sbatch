#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -J s6_store
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_store_%j.out
export OMP_NUM_THREADS=8
. /speed-scratch/o_iseri/5J/test/code/s6_prelude.sh
$PY -u $C/s6_store.py
RC=$?
echo "s6_store EXIT $RC end=$(date -Iseconds)"
exit $RC
