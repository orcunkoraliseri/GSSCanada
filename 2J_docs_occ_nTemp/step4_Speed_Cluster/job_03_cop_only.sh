#!/encs/bin/bash
#SBATCH --job-name=03_cop_only
#SBATCH --mem=16G
#SBATCH -c 4
#SBATCH -p ps
#SBATCH -t 0-01:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/03_cop_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/03_cop_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash

cd /speed-scratch/o_iseri/occModeling
mkdir -p logs

/speed-scratch/o_iseri/envs/step4/bin/python -u 03_cop_only.py
