#!/bin/bash
#SBATCH -J 5J_9k_agg
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -o /speed-scratch/o_iseri/5J/step9c/win3fix/logs/agg_%j.out
/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/5J/step9c/win3fix/win_agg.py
