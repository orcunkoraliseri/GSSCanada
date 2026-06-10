#!/encs/bin/bash
#SBATCH --job-name=s8_val_v2
#SBATCH --partition=ps
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/val_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/val_%j.err

set -e
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs/step8_val_v2.py

echo "=== step8_val_v2.sh  job=$SLURM_JOB_ID  node=$SLURMD_NODENAME  $(date) ==="
$PYTHON "$SCRIPT" --n-sample 2
echo "=== DONE $(date) ==="
