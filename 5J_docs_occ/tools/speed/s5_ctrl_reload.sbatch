#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH -c 3
#SBATCH --mem=48G
#SBATCH -J s5_crel
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_crel_%j.out
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=3
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=$SLURM_ARRAY_TASK_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
nvidia-smi -L
$PY -m py_compile $T/s5_ctrl_reload.py && echo "SYNTAX_OK s5_ctrl_reload.py" || exit 3
$PY -u $T/s5_ctrl_reload.py
RC=$?
echo "CTRL_RELOAD_EXIT $RC end=$(date -Iseconds)"
exit $RC
