#!/encs/bin/bash
#SBATCH --job-name=test_ep_wrapper
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/test_ep_%j.out
#SBATCH --error=/speed-scratch/o_iseri/ep_wrappers/test_ep_%j.err

RUN=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A/sample_001_HH130192/2022
EPW=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw
WRAPPER=/speed-scratch/o_iseri/ep_wrappers/energyplus

echo "=== PATH ==="
echo $PATH
echo "=== singularity location ==="
which singularity
singularity --version
echo "=== wrapper test: --version ==="
$WRAPPER --version
echo "=== running E+ on expanded.idf ==="
$WRAPPER -w "$EPW" -d "$RUN" "$RUN/expanded.idf"
echo "Exit: $?"
