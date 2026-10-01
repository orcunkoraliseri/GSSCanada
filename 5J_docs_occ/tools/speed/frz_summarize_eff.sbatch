#!/bin/bash
#SBATCH -J frz_summ_eff
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/freeze/logs/summ_eff_%j.out
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
cd $F || exit 2
$PY -u $F/frz_summarize.py --eff > $F/out/perturb_summary_eff.txt 2>&1
RC=$?
echo "SUMMARIZE_EXIT $RC"; wc -l $F/out/perturb_summary_eff.txt
exit $RC
