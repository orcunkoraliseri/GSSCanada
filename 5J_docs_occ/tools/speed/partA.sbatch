#!/bin/bash
#SBATCH -J cdpartA
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign_prep/logs/partA_%j.out
R=/speed-scratch/o_iseri/5J/campaign_prep
PY=/speed-scratch/o_iseri/envs/step4/bin/python
cp /speed-scratch/o_iseri/5J/multizone/tabula/archetype_parameters_es.csv $R/tabula_in/
cd $R
echo "=== ITALY ==="; $PY -u cp_partA_tabula.py it; echo "exit_it=$?"
echo "=== SPAIN (control: must reproduce multizone/tabula/dwelling_count_es.csv) ==="; $PY -u cp_partA_tabula.py es; echo "exit_es=$?"
if cmp -s out/dwelling_count_es.csv /speed-scratch/o_iseri/5J/multizone/tabula/dwelling_count_es.csv; then echo "CONTROL_ES_REPRODUCES PASS (byte equal)"; else echo "CONTROL_ES_REPRODUCES FAIL"; fi
md5sum out/dwelling_count_it.csv out/dwelling_count_es.csv
wc -l out/dwelling_count_it.csv
