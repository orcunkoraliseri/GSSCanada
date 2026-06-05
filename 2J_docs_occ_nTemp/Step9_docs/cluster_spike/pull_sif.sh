#!/encs/bin/bash
#SBATCH --job-name=ep_pull_sif
#SBATCH --partition=ps    # CPU partition; verify with `sinfo` on login node (may be `sp` or omit)
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_spike/logs/pull_sif_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_spike/logs/pull_sif_%j.err

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

SPIKE=/speed-scratch/o_iseri/step9_spike
mkdir -p "$SPIKE/logs"

echo "=== Job: pull NREL EnergyPlus 24.2.0 SIF ==="
echo "Node: $(hostname)  Date: $(date)"

singularity pull --force "$SPIKE/energyplus_24.2.0.sif" docker://nrel/energyplus:24.2.0
PULL_RC=$?
echo "singularity pull exit code: $PULL_RC"
if [ $PULL_RC -ne 0 ]; then
    echo "ERROR: singularity pull failed (check network access from compute node)"
    exit 1
fi

echo "=== Verifying E+ version inside container ==="
singularity exec "$SPIKE/energyplus_24.2.0.sif" energyplus --version
echo "=== SIF ready: $SPIKE/energyplus_24.2.0.sif ==="
