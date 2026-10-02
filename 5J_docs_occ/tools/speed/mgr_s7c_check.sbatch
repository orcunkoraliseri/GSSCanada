#!/bin/bash
#SBATCH -J mgr_s7c_check
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/mgr/mgr_s7c_check_%j.out
cd /speed-scratch/o_iseri/5J/mgr && md5sum mgr_s7c_check.py && /speed-scratch/o_iseri/envs/step4/bin/python -u mgr_s7c_check.py; echo EXIT $?
