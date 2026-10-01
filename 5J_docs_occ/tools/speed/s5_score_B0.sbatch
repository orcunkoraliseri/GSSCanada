#!/bin/bash
#SBATCH -J s5_score_B0
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/5J/train/logs/s5_score_B0_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
cd $T || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID"
cp $F/split_loader.py $T/split_loader.py.tmp$$ && mv -f $T/split_loader.py.tmp$$ $T/split_loader.py
echo "split_loader md5 freeze=$(md5sum $F/split_loader.py | cut -d' ' -f1) copy=$(md5sum $T/split_loader.py | cut -d' ' -f1)"
mkdir -p $T/score
echo "scorer md5 $(md5sum $F/5thJ_04_scorer.py | cut -d' ' -f1) (expected 84d1dafa...)"
$PY -u $F/5thJ_04_scorer.py --pred $T/pred/B0 --split validation --out $T/score/ --tag B0 --b1 $F/out/standins/weakb1 --control $T/pred/B0 --workers 6 > $T/score/score_B0.txt 2>&1
RC=$?
echo "SCORER_EXIT_CODE_SEEN_BY_JOB $RC"
grep -E "^SUMMARY|^SCORER_EXIT|^PAIRS_TOTAL|^CHECK 2.3|^SUMMARY_GATE" $T/score/score_B0.txt
echo "--- G5J.2 lines"
grep -E "^GATE G5J.2" $T/score/score_B0.txt
echo "--- G5J.3 lines"
grep -E "^GATE G5J.3" $T/score/score_B0.txt
echo "end=$(date -Iseconds)"
exit $RC
