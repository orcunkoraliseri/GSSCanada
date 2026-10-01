#!/bin/bash
#SBATCH -J s5_store
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_store_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
for f in s5_common.py s5_store.py; do $PY -m py_compile $T/$f && echo "SYNTAX_OK $f $(md5sum $T/$f | cut -d' ' -f1)" || exit 3; done
$PY -u $T/s5_store.py
RC=$?
echo "STORE_EXIT $RC"
ls -l $T/store/
echo "end=$(date -Iseconds)"
exit $RC
