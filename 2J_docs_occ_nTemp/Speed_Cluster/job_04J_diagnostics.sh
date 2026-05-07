#!/encs/bin/bash
#SBATCH --job-name=step4J_diag
#SBATCH --mem=8G
#SBATCH -c 4
#SBATCH -p ps
#SBATCH -t 0-00:30:00
#SBATCH --output=logs/04J_%j.out
#SBATCH --error=logs/04J_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash

cd /speed-scratch/$USER/occModeling
mkdir -p logs

/speed-scratch/$USER/envs/step4/bin/python -u 04J_statistical_diagnostics.py --data_dir outputs_step4 --step3_dir outputs_step3 --output_json outputs_step4/diagnostics_v4_statistical.json --n_bootstrap 1000
