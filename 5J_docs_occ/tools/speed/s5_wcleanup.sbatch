#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -J s5_wcleanup
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_wcleanup_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=$SLURM_ARRAY_TASK_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d" " -f1) copy=$(md5sum $T/split_loader.py | cut -d" " -f1)"
$PY -m py_compile $T/s5_cleanup.py && echo "SYNTAX_OK s5_cleanup.py $(md5sum $T/s5_cleanup.py | cut -d" " -f1)" || exit 3
$PY -u $T/s5_cleanup.py
RC=$?
echo "CLEANUP_EXIT $RC"
exit $RC

