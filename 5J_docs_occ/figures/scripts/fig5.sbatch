#!/bin/bash
#SBATCH -J fig5
#SBATCH -p ps
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/figures/logs/fig5_%j.out
# 5J Step 8 part C: Figure 5 (district spread). Data first (stop if exit != 0), then the plot. District outputs only; no test-split file.
FG=/speed-scratch/o_iseri/5J/figures
DI=/speed-scratch/o_iseri/5J/district
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export PYTHONDONTWRITEBYTECODE=1
echo "JOB $SLURM_JOB_ID start $(date) host=$(hostname)"
for f in fig_common.py fig05_data.py fig05_district_spread.py; do
  echo "SCRIPT_MD5 $(md5sum $FG/scripts/$f)"
  $PY -c "import sys; compile(open('$FG/scripts/$f').read(), '$f', 'exec')" && echo "SYNTAX_OK $f" || { echo "SYNTAX FAILED $f"; exit 1; }
done
echo "INPUT_MD5 $(md5sum $DI/out_step7/district_spread.csv $DI/out_step7/district_check_draws.csv $DI/out/n_chosen_B.txt)"
cd $FG/scripts
$PY -u fig05_data.py --root $DI --out $FG/data
RC=$?
echo "FIG5_DATA_EXIT $RC"
if [ $RC -ne 0 ]; then echo "STOP: data exit $RC, plot not run"; exit $RC; fi
$PY -u fig05_district_spread.py --draws $FG/data/fig5_draws.parquet --spread $DI/out_step7/district_spread.csv --check $DI/out_step7/district_check_draws.csv --out $FG/out
echo "FIG5_PLOT_EXIT $?"
echo "JOB_END $(date)"
