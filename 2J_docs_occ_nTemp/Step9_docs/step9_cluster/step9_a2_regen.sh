#!/encs/bin/bash
#SBATCH --job-name=s9_a2
#SBATCH --partition=ps
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_a2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_a2_%j.err

# Stage A2: extract 13-col baseline CSVs + re-run IDF gen.
# Activity CSVs (17-col) already exist from Stage A (job 948062).
# This job only runs the baseline extract (~5 min) + IDF generation (~5 min).
# Do NOT re-run 07_aug_to_bem.py (activity CSVs are correct).

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
EXTRACT_SCRIPT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_a2_baseline_extract.py
IDF_GEN=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_idf_gen.py
BEM_DIR=$GCMAIN/BEM_Setup

echo "=== Step 9 Stage A2: baseline extract + IDF regen ==="
echo "Node: $(hostname)  Date: $(date)"

mkdir -p $ROOT/logs

# A2-1: extract 13-col baselines from existing activity CSVs
echo "--- A2-1: extract baseline CSVs ---"
$PYTHON "$EXTRACT_SCRIPT" --bem_dir "$BEM_DIR"
[ $? -ne 0 ] && echo "FAIL: baseline extract" && exit 1

# Verify baseline files exist
for yr in 2022 2030; do
    BL=$BEM_DIR/BEM_Schedules_${yr}_baseline.csv
    if [ ! -f "$BL" ]; then echo "FAIL: missing $BL"; exit 1; fi
    ROWS=$(wc -l < "$BL")
    echo "  BEM_Schedules_${yr}_baseline.csv: $ROWS lines"
done

# A2-2: re-run IDF generator (uses _baseline.csv now)
echo "--- A2-2: step9_idf_gen.py ---"
# eppy needs ENERGYPLUS_DIR to find Energy+.idd; was extracted by Stage A to $ROOT
if [ ! -f "$ROOT/Energy+.idd" ]; then
    echo "FAIL: $ROOT/Energy+.idd missing — re-extract from SIF first"
    exit 1
fi
export ENERGYPLUS_DIR=$ROOT
$PYTHON "$IDF_GEN" --root "$ROOT" --n 20 --seed 42
[ $? -ne 0 ] && echo "FAIL: IDF gen" && exit 1

MANIFEST=$ROOT/step9_manifest.csv
ROWS=$(wc -l < "$MANIFEST")
echo "  Manifest rows (incl. header): $ROWS  (expect 241)"
if [ "$ROWS" -ne 241 ]; then
    echo "FAIL: manifest has $ROWS rows, expected 241"
    exit 1
fi

echo "=== Stage A2 COMPLETE ==="
echo "Date: $(date)"
