#!/bin/bash
#SBATCH -J 5J_9k_store3
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/modelA/store_test3/logs/test_%j.out
# 5J Step 9k store re-test on the final base _win_2026-10-03. Submitted with --dependency=afterany:<aggregator of the writer array>. Never waited for.
# NO EnergyPlus run here: the writer's run folders (D, O, DF, OF; hourly csv kept by the KEEP_CSV switch of win_task.sh) are READ ONLY.
# Fix (1) of the 9g read (own working folder per EnergyPlus run) does not apply: no EnergyPlus is started by this job.
B=/speed-scratch/o_iseri/5J/modelA/store_test3
S=/speed-scratch/o_iseri/5J/step9c
W=$S/win3fix
export PYTHONDONTWRITEBYTECODE=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
mkdir -p $B/logs
echo "start $(date -Iseconds) host $(hostname)"
cd $B/code
$PY a9_store.py test $B $W $S/epw $W/runs D,O,DF,OF 0275c53572b2ff9f
echo "a9_store test exit code $?"
