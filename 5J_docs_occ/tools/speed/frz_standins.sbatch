#!/bin/bash
#SBATCH -J frz_standins
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/standins_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -m py_compile $F/5thJ_04_scorer.py && echo "SYNTAX_OK scorer" || exit 3
$PY -u $F/frz_standins.py
RC=$?
echo "EXIT $RC"
echo "end=$(date -Iseconds)"
exit $RC
