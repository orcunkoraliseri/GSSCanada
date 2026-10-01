#!/bin/bash
#SBATCH -J fig24_plot
#SBATCH -p ps
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/figures/logs/fig24_plot_%j.out
# 5J Step 8 part B: Figures 2 and 4 (scores.parquet and reported_S_<list>.txt only; no truth or prediction file).
FG=/speed-scratch/o_iseri/5J/figures
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SCORES=/speed-scratch/o_iseri/5J/test/score_collect/scores.parquet
export PYTHONDONTWRITEBYTECODE=1
echo "JOB $SLURM_JOB_ID start $(date) host=$(hostname)"
for f in fig_common.py fig02_load_accuracy.py fig04_peaks_timing.py; do
  echo "SCRIPT_MD5 $(md5sum $FG/scripts/$f)"
  $PY -c "import sys; compile(open('$FG/scripts/$f').read(), '$f', 'exec')" && echo "SYNTAX_OK $f" || { echo "SYNTAX FAILED $f"; exit 1; }
done
echo "SCORES_MD5 $(md5sum $SCORES)"
echo "REPORTED_MD5 $(cd $FG/inputs && md5sum reported_S_test_new_households.txt reported_S_test_new_buildings.txt reported_S_test_both_new.txt)"
cd $FG/scripts
$PY -u fig02_load_accuracy.py --scores $SCORES --out $FG/out
echo "FIG2_EXIT $?"
$PY -u fig04_peaks_timing.py --scores $SCORES --reported-dir $FG/inputs --out $FG/out
echo "FIG4_EXIT $?"
echo "JOB_END $(date)"
