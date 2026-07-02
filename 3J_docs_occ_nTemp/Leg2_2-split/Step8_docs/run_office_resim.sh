#!/bin/bash
# run_office_resim.sh — Step 8C: RE-SIM office campaign with fixed schedule injection (3J Leg-2)
#
# Identical to run_office_array.sh EXCEPT it passes --no-skip so every one of the 252
# cells is overwritten (the prior outputs are the flat/buggy ones — pre zone-routing fix).
# 252 tasks: 3 arch × 2 envelope × 6 CZ × 7 scenarios. Writes over $SCRATCH/office.
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_resim.sh

#SBATCH --job-name=3J_8C_office_resim
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-251
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8C_office_resim_%A_%a.out

SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs

mkdir -p "$SCRATCH/logs"
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }

export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg

echo "=== 8C Office RE-SIM task $SLURM_ARRAY_TASK_ID of 251 ==="
echo "  Node: $(hostname)  Date: $(date)"

cd "$STEP8_DIR"
$PY office_runner.py \
    --cell-idx $SLURM_ARRAY_TASK_ID \
    --out-dir "$SCRATCH/office" \
    --no-skip

echo "  Task $SLURM_ARRAY_TASK_ID done: $(date)"
