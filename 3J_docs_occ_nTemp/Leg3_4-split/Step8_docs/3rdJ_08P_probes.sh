#!/bin/bash
# 3J Leg-3 Step 8 armament -- §P PROBE array launcher (sbatch only; nothing runs on
# the login node). Wrapper lives in the upload tree, NEVER in /tmp (noexec on Speed
# compute nodes). 7 tasks, one per probe cell (3rdJ_08P_probe_driver.py --cell N).
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_probes.sh
#       (returns job ID instantly; NEVER run from login node interactively)

#SBATCH --job-name=3J_8P_probes
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-6
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/logs/8P_probe_%A_%a.out

export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=/speed-scratch/o_iseri/step8_4split/upload

PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs

mkdir -p /speed-scratch/o_iseri/step8_4split/probes /speed-scratch/o_iseri/step8_4split/logs

# Defensive dep precheck -- fail fast if the python env is missing a required
# package, so it surfaces in the job log immediately, not 40 minutes in.
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

cd "$STEP8_DIR" || exit 1

echo "=== 8P probe array task $SLURM_ARRAY_TASK_ID of 6 ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  PY: $PY"

$PY -u 3rdJ_08P_probe_driver.py --cell $SLURM_ARRAY_TASK_ID
RC=$?

echo "  Task $SLURM_ARRAY_TASK_ID done (python exit=$RC): $(date)"
exit $RC
