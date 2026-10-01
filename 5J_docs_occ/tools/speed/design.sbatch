#!/bin/bash
#SBATCH -J cddesign
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign_prep/logs/design_%j.out
cd /speed-scratch/o_iseri/5J/campaign_prep
/speed-scratch/o_iseri/envs/step4/bin/python -u cd_design.py
echo "exit_design=$?"
