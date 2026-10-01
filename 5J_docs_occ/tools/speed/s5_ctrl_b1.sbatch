#!/bin/bash
#SBATCH -J s5_cb1
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=96G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_cb1_%j.out
export OMP_NUM_THREADS=6
CC=$1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=$SLURM_ARRAY_TASK_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
for f in s5_common.py s5_b1.py; do $PY -m py_compile $T/$f && echo "SYNTAX_OK $f $(md5sum $T/$f | cut -d' ' -f1)" || exit 3; done
if [ -e $T/ckpt/B1_loco_$CC/b1_config.json ]; then echo "REFUSED: ckpt/B1_loco_$CC exists"; exit 4; fi
$PY -u $T/s5_b1.py --country $CC --no-climate
RC=$?
echo "B1_LOCO_EXIT $CC $RC end=$(date -Iseconds)"
exit $RC
