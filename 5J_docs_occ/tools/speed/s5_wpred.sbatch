#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -J s5_wpred
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH -c 3
#SBATCH --mem=48G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_wpred_%A_%a.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=$SLURM_ARRAY_TASK_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d" " -f1) copy=$(md5sum $T/split_loader.py | cut -d" " -f1)"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=3
nvidia-smi -L
for f in s5_common.py s5_data.py s5_models.py s5_predict.py s5_pred_task.py; do $PY -m py_compile $T/$f && echo "SYNTAX_OK $f $(md5sum $T/$f | cut -d" " -f1)" || exit 3; done
$PY -u $T/s5_pred_task.py $SLURM_ARRAY_TASK_ID
RC=$?
echo "PRED_EXIT $RC end=$(date -Iseconds)"
exit $RC

