#!/bin/bash
# 3J Leg-3 Step 8 -- P1-P4 PROBE GATES launcher (sbatch only; nothing runs on the login node).
# Wrapper lives in the upload tree, NEVER in /tmp (noexec on Speed compute nodes).
#SBATCH --job-name=3J_8P_gates
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/logs/8P_gates_%j.out

export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=/speed-scratch/o_iseri/step8_4split/upload

cd /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs || exit 1

echo "=== P GATES start ==="
date
/speed-scratch/o_iseri/envs/step4/bin/python -u 3rdJ_08P_probe_gates.py
RC=$?
echo "=== P GATES end (python exit=$RC) ==="
date
exit $RC
