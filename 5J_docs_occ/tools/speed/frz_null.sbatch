#!/bin/bash
#SBATCH -J frz_null
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/null_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
echo "host=$(hostname) start=$(date -Iseconds) NULL_REPS=${NULL_REPS:-200}"
export NULL_WORKERS=8
$PY -u $F/frz_null.py
echo "EXIT $?"
echo "end=$(date -Iseconds)"
