#!/encs/bin/bash
#SBATCH --job-name=check_04E
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/occModeling/logs/check_04E_%j.out
#SBATCH --error=/speed-scratch/o_iseri/occModeling/logs/check_04E_%j.err

cd /speed-scratch/o_iseri/occModeling
/speed-scratch/o_iseri/envs/step4/bin/python -u check_04E_output.py
