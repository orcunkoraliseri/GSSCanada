#!/bin/bash
#SBATCH --job-name=t06_enduse2022_v2
#SBATCH --partition=ps
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T06/out/t06v2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T06/out/t06v2_%j.err

INPUT_ROOT=/speed-scratch/o_iseri/2J_revision/T06/input
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SCRIPT=/speed-scratch/o_iseri/2J_revision/T06/T06_scripts/enduse_hour_2022_v2.py

echo "=== T06 enduse_hour_2022_v2 | job=${SLURM_JOB_ID} | node=$(hostname) | date=$(date) ==="

# v2 fix: job 1328259 failed because the tar has no "campaign_N50/" root -- its 24 cell
# dirs extract directly under $INPUT_ROOT. Guard on a real cell dir, not the phantom
# campaign_N50 path, and let the python script (v2) read $INPUT_ROOT directly.
if [ ! -d "$INPUT_ROOT/HighRise__Calgary_6B" ]; then
  echo "extracting t06_2022_input.tar.gz ..."
  cd "$INPUT_ROOT" && tar xzf t06_2022_input.tar.gz
  RC_TAR=$?
  echo "tar extract exit=${RC_TAR}"
fi

echo "input cell dir count: $(ls -d $INPUT_ROOT/*__* | wc -l)"

$PYTHON $SCRIPT
RC=$?
echo "=== exit=${RC} ==="
exit $RC
