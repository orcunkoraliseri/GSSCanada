#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH -c 3
#SBATCH --mem=48G
#SBATCH -J s6_pred
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_pred_%A_%a.out
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=3
. /speed-scratch/o_iseri/5J/test/code/s6_prelude.sh
nvidia-smi -L
$PY -u $C/s6_pred_task.py $SLURM_ARRAY_TASK_ID
RC=$?
echo "s6_pred EXIT $RC end=$(date -Iseconds)"
exit $RC
