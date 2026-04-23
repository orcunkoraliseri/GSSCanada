#!/encs/bin/bash
#SBATCH --job-name=04F_valid
#SBATCH --partition=ps
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/04F_valid_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/04F_valid_%j.err

cd /speed-scratch/o_iseri/occModeling
/speed-scratch/o_iseri/envs/step4/bin/python -u 04F_validation.py
