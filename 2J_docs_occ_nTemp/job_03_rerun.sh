#!/encs/bin/bash
#SBATCH --job-name=step3_rerun
#SBATCH --mem=16G
#SBATCH -c 4
#SBATCH -p ps
#SBATCH -t 0-01:00:00
#SBATCH --output=logs/03_%j.out
#SBATCH --error=logs/03_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash

cd /speed-scratch/$USER/occModeling
mkdir -p logs

/speed-scratch/$USER/envs/step4/bin/python -u 03_mergingGSS.py
