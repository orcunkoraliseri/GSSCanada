#!/encs/bin/bash
#SBATCH --job-name=s2_leg2_valonly
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s2_leg2_valonly_%j.out

# Step 2 Leg-2 Validator Only (assumes harmonized CSVs already exist)
# Partition: ps  |  Wall: 48h  |  Mem: 16G
# Run: sbatch 3rdJ_s2_2split_valonly.sh

. /encs/pkg/modules-5.3.1/root/init/bash

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
S2DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step2_docs

echo "=== Step 2 Leg-2 ValOnly Job Start: $(date) ==="

$PYTHON -m pip install --quiet seaborn matplotlib

# Check harmonized output files exist
OUT=$S2DIR/outputs_step2
chk() { [ -f "$1" ] || { echo "MISSING: $1"; exit 1; }; }
chk $OUT/main_2005.csv
chk $OUT/main_2010.csv
chk $OUT/main_2015.csv
chk $OUT/main_2022.csv
chk $OUT/episode_2005.csv
chk $OUT/episode_2010.csv
chk $OUT/episode_2015.csv
chk $OUT/episode_2022.csv

echo "--- Running validator ---"
cd $S2DIR
$PYTHON 3rdJ_02_harmonizeGSS_2split_val.py

echo "=== Step 2 Leg-2 ValOnly Job End: $(date) ==="
