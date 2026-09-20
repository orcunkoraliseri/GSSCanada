#!/bin/tcsh
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_section41_%j.out

/speed-scratch/o_iseri/GSSCanada/venv/bin/python /speed-scratch/o_iseri/1J_rerun/section41/compute_section41.py
