#!/bin/bash
#SBATCH -J camppre
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/logs/preflight_%j.out
# Part C: disk preflight (PASS if free > 10 x plan peak 27.5 GB) + the real plan on the two frozen tables.
R=/speed-scratch/o_iseri/5J/campaign
PY=/speed-scratch/o_iseri/envs/step4/bin/python
cd $R || exit 2
echo "host=$(hostname) start=$(date -Iseconds)"
echo "DESIGN_MD5 $(md5sum $R/in/campaign_design.md)"
echo "TABLE_MD5 $(md5sum $R/in/campaign_runs_es.csv) $(md5sum $R/in/campaign_runs_it.csv)"
df -B1 /speed-scratch/o_iseri > $R/logs/df_raw.txt
echo "DF_RAW_LINE:"; cat $R/logs/df_raw.txt
D0=$(date +%s)
du -sb /speed-scratch/o_iseri/5J > $R/logs/du5J.txt
D1=$(date +%s)
echo "DU_5J_SECONDS=$((D1-D0)) $(cat $R/logs/du5J.txt)"
FREE=$(tail -n 1 $R/logs/df_raw.txt | awk '{print $4}')
USED=$(cut -f1 $R/logs/du5J.txt)
PEAK=27500000000
echo "PREFLIGHT_DISK free_bytes=$FREE used_5J=$USED plan_peak_bytes=$PEAK"
if [ -n "$FREE" ] && [ "$FREE" -gt $((10*PEAK)) ]; then echo "PREFLIGHT_DISK_VERDICT PASS free > 10 x plan peak"; else echo "PREFLIGHT_DISK_VERDICT FAIL"; exit 3; fi
$PY -u $R/camp_plan.py
RC=$?
echo "PLAN_EXIT $RC"
echo "NBLOCKS_FILE:"; cat $R/plan/nblocks.txt
echo "end=$(date -Iseconds)"
exit $RC
