#!/bin/bash
#SBATCH -J fig3_data
#SBATCH -p ps
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/figures/logs/fig3_data_%j.out
# 5J Step 8 part B: Figure 3 data job (Spain + Italy; reads sealed test truth + test predictions of S and C after scoring; logs every open).
FG=/speed-scratch/o_iseri/5J/figures
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export PYTHONDONTWRITEBYTECODE=1
echo "JOB $SLURM_JOB_ID start $(date) host=$(hostname)"
echo "SCRIPT_MD5 $(md5sum $FG/scripts/fig03_data.py)"
$PY -c "import sys; compile(open('$FG/scripts/fig03_data.py').read(), 'fig03_data.py', 'exec')" && echo "SYNTAX_OK" || { echo "SYNTAX FAILED"; exit 1; }
echo "SCORES_MD5 $(md5sum /speed-scratch/o_iseri/5J/test/score_collect/scores.parquet)"
$PY -u $FG/scripts/fig03_data.py --out $FG/data --scores /speed-scratch/o_iseri/5J/test/score_collect/scores.parquet --workers 4
echo "FIG3_DATA_EXIT $?"
echo "JOB_END $(date)"
