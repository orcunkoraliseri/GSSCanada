#!/bin/bash
#SBATCH --job-name=t05_conv2022
#SBATCH --partition=ps
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T05/T05_out/t05_%j.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T05/T05_out/t05_%j.err

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT=/speed-scratch/o_iseri/2J_revision/T05/T05_scripts/convergence_2022.py

echo "=== T05 convergence_2022 | job=${SLURM_JOB_ID} | node=$(hostname) | date=$(date) ==="
$PYTHON $SCRIPT
RC=$?
echo "=== exit=${RC} ==="
exit $RC
