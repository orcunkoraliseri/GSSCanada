#!/bin/bash
#SBATCH -J cdfix1
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign_prep/logs/fix1_%j.out
# Step A: preserve the OLD run tables, md5 everything, then run the NEW gates on the OLD tables (C1_distinct must FAIL).
cd /speed-scratch/o_iseri/5J/campaign_prep
PY=/speed-scratch/o_iseri/envs/step4/bin/python
for cc in es it; do
  [ -s out/campaign_runs_$cc.v1_2026-09-30.csv ] || cp -p out/campaign_runs_$cc.csv out/campaign_runs_$cc.v1_2026-09-30.csv
  [ -s out/campaign_runs_$cc.v1_2026-09-30.csv ] || { echo "BACKUP_MISSING $cc"; exit 3; }
done
md5sum out/campaign_runs_es.csv out/campaign_runs_it.csv out/campaign_runs_es.v1_2026-09-30.csv out/campaign_runs_it.v1_2026-09-30.csv out/splits_households.csv out/splits_buildings.csv out/k_table_es_it.csv
$PY -m py_compile cd_design.py cd_gates.py cd_fix_compare.py && echo "PYCOMPILE OK"
$PY -u cd_gates.py --runs-pattern /speed-scratch/o_iseri/5J/campaign_prep/out/campaign_runs_%s.v1_2026-09-30.csv --no-seenfail
echo "exit_gates_old=$?"
