#!/bin/bash
#SBATCH -J frz_floor
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/floor_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -m py_compile $F/5thJ_04_scorer.py && echo "SYNTAX_OK scorer" || exit 3
$PY -u $F/frz_noisefloor.py
RC=$?
echo "EXIT $RC"
echo "end=$(date -Iseconds)"
exit $RC
