#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -J hh_B
R=/speed-scratch/o_iseri/5J/households
PY=/speed-scratch/o_iseri/envs/step4/bin/python
$PY -u -c "import sys,numpy,pandas;print('python',sys.version.split()[0],'numpy',numpy.__version__,'pandas',pandas.__version__)"
$PY -u $R/tools/hh_B.py $LOG
echo "B exit=$?"
