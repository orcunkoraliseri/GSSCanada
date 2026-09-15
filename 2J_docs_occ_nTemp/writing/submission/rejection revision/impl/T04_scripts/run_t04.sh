#!/bin/bash
#SBATCH --job-name=T04_thresh
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T04/T04_thresh_%j.out

export T04_OUT_DIR=/speed-scratch/o_iseri/2J_revision/T04/T04_out
/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T04/T04_scripts/threshold_sensitivity.py
