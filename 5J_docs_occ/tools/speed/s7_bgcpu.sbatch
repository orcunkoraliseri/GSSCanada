#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=24G
#SBATCH -J s7_bgcpu
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bgcpu_%j.out
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
$PY -u $C/s7_draws_gpu.py cpu
RC=$?
echo "s7_bgcpu EXIT $RC end=$(date -Iseconds)"
exit $RC
