#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -J s5_cs3c
#SBATCH -c 6
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_cs3c_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=$SLURM_ARRAY_TASK_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
echo "scorer md5 $(md5sum $F/5thJ_04_scorer.py | cut -d' ' -f1) (expected 84d1dafa...)"
if [ -e $T/score/score_S3_vsC.txt ]; then echo "REFUSED: score file exists"; exit 4; fi
$PY -u $F/5thJ_04_scorer.py --pred $T/pred/S3 --split validation --out $T/score/ --tag S3_vsC --b1 $T/pred/B1_clip0 --control $T/pred/C_seed1 --workers 6 > $T/score/score_S3_vsC.txt 2>&1
RC=$?
echo "SCORER_EXIT_CODE_SEEN_BY_JOB $RC"
grep -E "^SUMMARY|^SCORER_EXIT|^PAIRS_TOTAL|^SUMMARY_GATE" $T/score/score_S3_vsC.txt
echo "end=$(date -Iseconds)"
exit $RC
