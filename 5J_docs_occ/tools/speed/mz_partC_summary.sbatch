#!/bin/bash
#SBATCH -J mzsum
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/5J/multizone/logs/summary_%j.out
/speed-scratch/o_iseri/envs/step4/bin/python -u /speed-scratch/o_iseri/5J/multizone/mz_partC_summary.py
