#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=32G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/score_%x_%j.out
# usage: sbatch -J <tag> frz_score.sbatch "<scorer args without --out/--tag/--workers>"
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
echo "host=$(hostname) start=$(date -Iseconds) tag=$SLURM_JOB_NAME args=$1"
$PY -u $F/5thJ_04_scorer.py --out $F/out/ --tag $SLURM_JOB_NAME --workers 6 $1 > $F/out/score_$SLURM_JOB_NAME.txt 2>&1
RC=$?
echo "SCORER_EXIT_CODE_SEEN_BY_JOB $RC"
tail -n 12 $F/out/score_$SLURM_JOB_NAME.txt
echo "end=$(date -Iseconds)"
exit $RC
