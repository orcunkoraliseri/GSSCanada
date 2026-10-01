#!/bin/bash
#SBATCH -J frzcount
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/paircount_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
for s in validation development; do $PY -u /speed-scratch/o_iseri/5J/freeze/frz_paircount.py $s; done
