#!/bin/bash
#SBATCH -J camp2diag
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign/integrity/repdiag_%j.out
cd /speed-scratch/o_iseri/5J/campaign
/speed-scratch/o_iseri/envs/step4/bin/python -u camp2_repdiag.py
for f in es_madrid_B01_dev_1 es_madrid_B01_dev_1_rep1; do echo "DONE_JSON $f"; grep -E '"(seconds|host|idf_md5|cache_key|max_rss_kb)"' done/$f.json; done
