#!/encs/bin/bash
#SBATCH --job-name=s9_loadshape
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_loadshape_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_loadshape_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python3
GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
SCRIPT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_loadshape_aggregate.py

mkdir -p /speed-scratch/o_iseri/step9_run/loadshape

echo "=== Step 9 load-shape aggregate | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

$PYTHON $SCRIPT

echo "=== Done: $(date) ==="
