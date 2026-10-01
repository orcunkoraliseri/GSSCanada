#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J hh_CD
PY=/speed-scratch/o_iseri/envs/step4/bin/python
$PY -u /speed-scratch/o_iseri/5J/households/tools/hh_build.py
echo "CD exit=$?"
