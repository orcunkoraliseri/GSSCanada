#!/bin/bash
# 3J Leg-3 Step 8 armament -- AUDIT-W launcher (sbatch only; nothing runs on the login node).
# Wrapper lives in the upload tree, NEVER in /tmp (noexec on Speed compute nodes).
#SBATCH --job-name=3J_8W_audit
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/logs/8W_audit_%j.out

export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=/speed-scratch/o_iseri/step8_4split/upload

mkdir -p /speed-scratch/o_iseri/step8_4split/audit_w /speed-scratch/o_iseri/step8_4split/logs
cd /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs || exit 1

echo "=== AUDIT-W start ==="
date
/speed-scratch/o_iseri/envs/step4/bin/python 3rdJ_08W_audit_wiring.py
RC=$?
echo "=== AUDIT-W end (python exit=$RC) ==="
date
exit $RC
