#!/encs/bin/bash
#SBATCH --job-name=04C_pairs
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04C_pairs_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04C_pairs_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash

cd /speed-scratch/o_iseri/occModeling
/speed-scratch/o_iseri/envs/step4/bin/python 04C_training_pairs.py
