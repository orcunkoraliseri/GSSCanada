#!/bin/bash
#SBATCH -J s5_b1_smoke
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_b1_smoke_%j.out
export OMP_NUM_THREADS=2
export B1_SMOKE=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID cpus=2"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
for f in s5_common.py s5_b1.py; do $PY -m py_compile $T/$f && echo "SYNTAX_OK $f $(md5sum $T/$f | cut -d' ' -f1)" || exit 3; done
$PY -u $T/s5_b1.py
RC=$?
echo "B1_EXIT $RC end=$(date -Iseconds)"
exit $RC
