#!/bin/bash
#SBATCH -J cdfix2
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign_prep/logs/fix2_%j.out
# Step B: (1) flag OFF into scratch must reproduce the v1 tables byte for byte; (2) flag ON writes the new tables; (3) compare old/new; (4) all gates on the new tables.
cd /speed-scratch/o_iseri/5J/campaign_prep
PY=/speed-scratch/o_iseri/envs/step4/bin/python
echo "=== (1) --no-distinct-flats into scratch/design_off (must equal v1) ==="
$PY -u cd_design.py --no-distinct-flats --outdir /speed-scratch/o_iseri/5J/campaign_prep/scratch/design_off/ | grep -E "PATCH|REPAIR|SWAPS_TOTAL|RUNS_WRITTEN|DESIGN_DONE|Error|Traceback"
for cc in es it; do
  a=$(md5sum < scratch/design_off/campaign_runs_$cc.csv | cut -d' ' -f1); b=$(md5sum < out/campaign_runs_$cc.v1_2026-09-30.csv | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "FLAG_OFF_REPRODUCES_V1 $cc PASS $a" || echo "FLAG_OFF_REPRODUCES_V1 $cc FAIL off=$a v1=$b"
done
echo "=== (2) default (--distinct-flats) into out/ ==="
$PY -u cd_design.py
echo "exit_design=$?"
echo "=== (3) old vs new ==="
$PY -u cd_fix_compare.py
echo "=== (4) gates on the NEW tables ==="
$PY -u cd_gates.py
echo "exit_gates_new=$?"
md5sum out/campaign_runs_es.csv out/campaign_runs_it.csv out/campaign_runs_es.v1_2026-09-30.csv out/campaign_runs_it.v1_2026-09-30.csv out/splits_households.csv out/splits_buildings.csv out/k_table_es_it.csv
