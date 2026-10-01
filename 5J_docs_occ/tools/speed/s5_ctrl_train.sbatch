#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH --gres=gpu:nvidia_a100_2g.20gb:1
#SBATCH -c 3
#SBATCH --mem=48G
#SBATCH -J s5_ctrain
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_ctrain_%A_%a.out
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
case $SLURM_ARRAY_TASK_ID in
 0) NAME=S_seed2;    ARGS="--seed 2";;
 1) NAME=S_seed3;    ARGS="--seed 3";;
 2) NAME=C_seed1;    ARGS="--blind --seed 1";;
 3) NAME=C_seed2;    ARGS="--blind --seed 2";;
 4) NAME=C_seed3;    ARGS="--blind --seed 3";;
 5) NAME=S_loco_es;  ARGS="--country es --no-climate --seed 1";;
 6) NAME=S_loco_it;  ARGS="--country it --no-climate --seed 1";;
 *) echo "bad task id"; exit 2;;
esac
OUTD=$T/ckpt/$NAME
if [ -e $OUTD/best.pt ]; then echo "REFUSED: $OUTD/best.pt exists"; exit 4; fi
mkdir -p $OUTD
echo "TRAIN_CMD name=$NAME args=$ARGS out=$OUTD"
for f in s5_common.py s5_data.py s5_models.py s5_predict.py s5_train.py; do $PY -m py_compile $T/$f && echo "SYNTAX_OK $f $(md5sum $T/$f | cut -d' ' -f1)" || exit 3; done
$PY -u $T/s5_train.py --config 3 --out $OUTD $ARGS
RC=$?
echo "CTRL_TRAIN_EXIT $NAME $RC end=$(date -Iseconds)"
exit $RC
