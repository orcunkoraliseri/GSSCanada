#!/encs/bin/bash
#SBATCH --job-name=s2_leg2_harmonize
#SBATCH --partition=ps
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/logs/s2_leg2_harmonize_%j.out

# Step 2 Leg-2 Harmonizer + Validator
# Partition: ps  |  Wall: 48h  |  Mem: 64G
# Run: sbatch 3rdJ_s2_2split_harmonize.sh

. /encs/pkg/modules-5.3.1/root/init/bash

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
S2DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step2_docs

echo "=== Step 2 Leg-2 Harmonize Job Start: $(date) ==="

# Precheck: install any missing packages
$PYTHON -m pip install --quiet pyreadstat seaborn matplotlib openpyxl

# Check required Step-1 input files
S1DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/outputs_step1
chk() { [ -f "$1" ] || { echo "MISSING INPUT: $1"; exit 1; }; }
chk $S1DIR/main_2005.csv
chk $S1DIR/main_2010.csv
chk $S1DIR/main_2015.csv
chk $S1DIR/main_2022.csv
chk $S1DIR/episode_2005.csv
chk $S1DIR/episode_2010.csv
chk $S1DIR/episode_2015.csv
chk $S1DIR/episode_2022.csv

# Check reference Excels
ACTXLS=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/references_activityCodes/Data\ Harmonization_activityCategories\ -\ execution.xlsx
PREXLS=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data\ Harmonization_presenceCategories\ -\ execution.xlsx
chk "$ACTXLS"
chk "$PREXLS"

mkdir -p $S2DIR/outputs_step2

echo "--- Running harmonizer ---"
cd $S2DIR
$PYTHON 3rdJ_02_harmonizeGSS_2split.py

echo "--- Running validator ---"
$PYTHON 3rdJ_02_harmonizeGSS_2split_val.py

echo "=== Step 2 Leg-2 Harmonize Job End: $(date) ==="
