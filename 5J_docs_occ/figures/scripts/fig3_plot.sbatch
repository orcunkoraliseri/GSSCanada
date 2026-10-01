#!/bin/bash
#SBATCH -J fig3_plot
#SBATCH -p ps
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/figures/logs/fig3_plot_%j.out
# 5J Step 8 part B: Figure 3 plot from figures/data/fig3_pairs.parquet only.
FG=/speed-scratch/o_iseri/5J/figures
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export PYTHONDONTWRITEBYTECODE=1
echo "JOB $SLURM_JOB_ID start $(date) host=$(hostname)"
for f in fig_common.py fig03_occupancy_effect.py; do
  echo "SCRIPT_MD5 $(md5sum $FG/scripts/$f)"
  $PY -c "import sys; compile(open('$FG/scripts/$f').read(), '$f', 'exec')" && echo "SYNTAX_OK $f" || { echo "SYNTAX FAILED $f"; exit 1; }
done
echo "TABLE_MD5 $(md5sum $FG/data/fig3_pairs.parquet) ; sidecar: $(cat $FG/data/fig3_pairs.parquet.md5.txt)"
cd $FG/scripts
$PY -u fig03_occupancy_effect.py --pairs $FG/data/fig3_pairs.parquet --out $FG/out
echo "FIG3_EXIT $?"
echo "JOB_END $(date)"
