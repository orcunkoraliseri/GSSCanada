#!/bin/bash
#SBATCH -J frz_mkfloors
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/mkfloors_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
$PY -u $F/frz_mkfloors.py
RC=$?
md5sum $F/out/floors_PLANTED_HIGH.json
exit $RC
