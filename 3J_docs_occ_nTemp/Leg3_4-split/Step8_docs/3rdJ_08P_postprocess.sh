#!/bin/bash
# 3J Leg-3 Step 8 -- §P PROBE post-processing-only recovery array (sbatch only; nothing
# runs on the login node). Recovers channel_hourly.csv (job 1169671 case-mismatch bug fix,
# 2026-07-28) for all 7 probe cells WITHOUT re-running EnergyPlus: re-derives
# hourly_meters.csv + channel_hourly.csv from each cell's already-existing
# <outdir>/run/eplusout.sql and rewrites manifest.json. Wrapper lives in the upload tree,
# NEVER in /tmp (noexec on Speed compute nodes).
#
# User: sbatch --dependency=afterany:1169664 /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_postprocess.sh
#       (afterany, not afterok -- cell 6 deliberately FAILED with exit 1 (fallback-retail
#       trip wire) but its eplusout.sql is still valid and must be recovered too)
#       (returns job ID instantly; NEVER run from login node interactively)

#SBATCH --job-name=3J_8P_post
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-6
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/logs/8P_post_%A_%a.out

export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=/speed-scratch/o_iseri/step8_4split/upload

PY=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs

mkdir -p /speed-scratch/o_iseri/step8_4split/probes /speed-scratch/o_iseri/step8_4split/logs

# Defensive dep precheck -- fail fast if the python env is missing a required
# package, so it surfaces in the job log immediately, not partway through the array.
# No EnergyPlus/singularity dependency here: --postprocess-only never launches EnergyPlus.
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

cd "$STEP8_DIR" || exit 1

echo "=== 8P postprocess-only recovery array task $SLURM_ARRAY_TASK_ID of 6 ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  PY: $PY"

$PY -u 3rdJ_08P_probe_driver.py --cell $SLURM_ARRAY_TASK_ID --postprocess-only
RC=$?

echo "  Task $SLURM_ARRAY_TASK_ID done (python exit=$RC): $(date)"
exit $RC
