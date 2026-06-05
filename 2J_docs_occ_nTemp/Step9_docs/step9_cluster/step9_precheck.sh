#!/encs/bin/bash
#SBATCH --job-name=s9_precheck
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_precheck_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_precheck_%j.err

# Analytic pre-check (no EnergyPlus): verify Step 9 consolidation wired correctly
# on the 3 cells before submitting the E+ array.
# Run AFTER step9_a2_regen.sh with the fixed integration.py.
# Require RESULT: PASS (+-5%, zero leaks) on all three cells.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
PRECHECK=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/precheck_calibration.py

export ENERGYPLUS_DIR=$ROOT
export PYTHONPATH=$GCMAIN/2J_docs_occ_nTemp:$GCMAIN/2J_docs_occ_nTemp/Step8_docs

echo "=== Step 9 Analytic Pre-Check ==="
echo "Node: $(hostname)  Date: $(date)"

CELLS=("SingleD__Winnipeg_7A SingleD" "HighRise__Montreal_6A HighRise" "MidRise__Toronto_5A MidRise")
FAIL=0

MANIFEST=$ROOT/step9_manifest.csv

for ENTRY in "${CELLS[@]}"; do
    CELL=$(echo $ENTRY | cut -d' ' -f1)
    DTYPE=$(echo $ENTRY | cut -d' ' -f2)
    # Use manifest (written by step9_idf_gen.py) to get a canonical IDF path,
    # avoiding stale IDFs from previous runs with different HH IDs.
    IDF=$(awk -F',' -v cell="$CELL" '$2==cell && $3=="activity" && $5=="2022" {print $6; exit}' "$MANIFEST")
    if [ -z "$IDF" ]; then
        echo "SKIP [$CELL]: no activity 2022 entry in manifest $MANIFEST (run A2 first)"
        FAIL=1
        continue
    fi
    echo ""
    echo "--- $CELL ($DTYPE) ---"
    echo "  IDF: $IDF"
    $PYTHON "$PRECHECK" "$IDF" --dtype "$DTYPE" --tol 0.05
    RC=$?
    if [ $RC -ne 0 ]; then
        echo "  PRECHECK FAIL for $CELL"
        FAIL=1
    fi
done

echo ""
if [ $FAIL -eq 0 ]; then
    echo "=== ALL 3 PRECHECKS PASS — safe to run E+ array ==="
else
    echo "=== PRECHECK FAIL — fix wiring BEFORE E+ array ==="
    exit 1
fi
