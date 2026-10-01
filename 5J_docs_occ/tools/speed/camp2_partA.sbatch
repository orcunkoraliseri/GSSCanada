#!/bin/bash
#SBATCH -J camp2A
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/partA_%j.out
# Part 2, Part A: the 31 SUMMARY lines, counts of done/failed/runs folders. Spain + Italy logs only (six named arrays).
R=/speed-scratch/o_iseri/5J/campaign
echo "host=$(hostname) start=$(date -Iseconds)"
N=0
for pair in es_madrid_2010:1404153 es_valencia_2010:1404159 es_seville_2010:1404164 it_bologna_2014:1404165 it_turin_2014:1404174 it_milan_2014:1404179; do
  arr=${pair%%:*}; job=${pair##*:}
  for f in $R/logs/${arr}_${job}_*.out; do
    L=$(grep '^SUMMARY' "$f")
    if [ -z "$L" ]; then echo "NO_SUMMARY $f -> NOT_EVALUABLE"; else echo "$L   [$(basename $f)]"; N=$((N+1)); fi
  done
done
echo "SUMMARY_LINES_FOUND $N (expected 31)"
echo "DONE_FILES $(ls $R/done | wc -l) (json $(ls $R/done | grep -c '\.json$') err $(ls $R/done | grep -c '\.err$'))"
echo "FAILED_FILES $(ls $R/failed | wc -l)"
echo "RUNS_FOLDERS_LEFT $(ls $R/runs | wc -l)"
echo "DONE_JSON_STATUS_PASS $(grep -l '\"status\": \"pass\"' $R/done/*.json | wc -l)"
echo "DONE_JSON_NOT_PASS $(grep -L '\"status\": \"pass\"' $R/done/*.json | wc -l)"
for a in es_madrid_2010 es_valencia_2010 es_seville_2010 it_bologna_2014 it_turin_2014 it_milan_2014; do echo "EXTRACTED_FILES $a $(ls $R/extracted/$a | wc -l)"; done
echo "EXTRACTED_TMP_LEFT $(ls $R/extracted/*/ | grep -c '\.tmp$')"
echo "end=$(date -Iseconds)"
