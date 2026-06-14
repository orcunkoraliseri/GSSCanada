#!/bin/bash
#SBATCH --job-name=interim_plots
#SBATCH --partition=ps
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/logs/interim_plots_%j.out

set -e
source /speed-scratch/o_iseri/GSSCanada/venv/bin/activate
export ESIM_BATCH_DIR=/speed-scratch/o_iseri/GSSCanada/results/BatchAll_MC_N20_flat
cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main
python interim_report_gen.py
