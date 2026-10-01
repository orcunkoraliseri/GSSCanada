#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=96G
#SBATCH -J s6_b1
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_b1_%j.out
export OMP_NUM_THREADS=6
. /speed-scratch/o_iseri/5J/test/code/s6_prelude.sh
RC=0
for M in $1; do
  echo "== model $M"
  $PY -u $C/s6_b1_task.py $M || RC=1
done
echo "s6_b1 EXIT $RC end=$(date -Iseconds)"
exit $RC
