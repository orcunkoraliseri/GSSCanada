#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH -c 3
#SBATCH --mem=48G
#SBATCH -J s7_bgrun
#SBATCH --array=1-20%3
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_bgrun_%A_%a.out
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=3
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
nvidia-smi -L
$PY -u $C/s7_draws_gpu.py run
RC=$?
echo "s7_bgrun EXIT $RC end=$(date -Iseconds)"
exit $RC
