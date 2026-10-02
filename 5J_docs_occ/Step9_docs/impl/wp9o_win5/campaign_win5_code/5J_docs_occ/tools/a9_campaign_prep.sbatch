#!/bin/bash
#SBATCH -J 5J_9l_prep
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -o /speed-scratch/o_iseri/5J/modelA/campaign_win5/logs/prep_%j.out
# 5J Step 9l prep: B0 average household (Madrid, dev only), light-vs-full placement, skip rule on a synthetic result. MANIFEST = plan or smoke csv.
C=/speed-scratch/o_iseri/5J/modelA/campaign_win5
: ${MANIFEST:?MANIFEST not set}
cd $C/root/5J_docs_occ/tools || exit 2
/speed-scratch/o_iseri/envs/step4/bin/python -u a9_campaign_task.py prep $MANIFEST
echo "prep exit=$?"
