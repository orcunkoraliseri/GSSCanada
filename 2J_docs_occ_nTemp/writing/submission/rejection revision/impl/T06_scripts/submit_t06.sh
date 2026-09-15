#!/bin/bash
#SBATCH --job-name=t06_enduse2022
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T06/out/t06_%j.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T06/out/t06_%j.err

INPUT_ROOT=/speed-scratch/o_iseri/2J_revision/T06/input
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT=/speed-scratch/o_iseri/2J_revision/T06/T06_scripts/enduse_hour_2022.py

echo "=== T06 enduse_hour_2022 | job=${SLURM_JOB_ID} | node=$(hostname) | date=$(date) ==="

if [ ! -d "$INPUT_ROOT/campaign_N50" ]; then
  echo "extracting t06_2022_input.tar.gz ..."
  cd "$INPUT_ROOT" && tar xzf t06_2022_input.tar.gz
  RC_TAR=$?
  echo "tar extract exit=${RC_TAR}"
fi

echo "campaign_N50 cell count: $(ls $INPUT_ROOT/campaign_N50 | wc -l)"

$PYTHON $SCRIPT
RC=$?
echo "=== exit=${RC} ==="
exit $RC
