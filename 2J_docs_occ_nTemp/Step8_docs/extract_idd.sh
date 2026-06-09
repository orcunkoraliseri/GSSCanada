#!/encs/bin/bash
#SBATCH --job-name=extract_idd
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/extract_idd_%j.out
singularity exec /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif cat /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/Energy+.idd > /speed-scratch/o_iseri/ep_wrappers/Energy+.idd && echo "IDD_OK" && wc -l /speed-scratch/o_iseri/ep_wrappers/Energy+.idd
