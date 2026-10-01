#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -J s6_seenfail
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_seenfail_%j.out
# bash only; no scorer call; no truth file. Exit 0 only if every seen-failing case behaved as planned.
bash /speed-scratch/o_iseri/5J/test/code/s6_seenfail.sh
RC=$?
echo "s6_seenfail EXIT $RC end=$(date -Iseconds)"
exit $RC
