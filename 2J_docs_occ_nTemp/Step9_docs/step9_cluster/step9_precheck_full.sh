#!/encs/bin/bash
#SBATCH --job-name=s9_precheck_full
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_precheck_full_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_precheck_full_%j.err

# Analytic pre-check (no EnergyPlus) for the FULL 24-cell grid.
# Runs precheck_calibration.py on one activity/2022 IDF per archetype (4 cells).
# MUST include OtherDwelling (new archetype, not validated in the 3-cell run).
# Run AFTER step9_a_generate_full.sh completes (manifest exists, all IDFs generated).
# Require RESULT: PASS (+-5%, zero leaks) on all 4 cells before step9_b_array_full.sh.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
PRECHECK=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/precheck_calibration.py

export ENERGYPLUS_DIR=$ROOT
export PYTHONPATH=$GCMAIN/2J_docs_occ_nTemp:$GCMAIN/2J_docs_occ_nTemp/Step8_docs

echo "=== Step 9 Full-Grid Analytic Pre-Check (4 cells, 1 per archetype) ==="
echo "Node: $(hostname)  Date: $(date)"

MANIFEST=$ROOT/step9_manifest.csv

CELLS=("SingleD__Winnipeg_7A SingleD" "OtherDwelling__Montreal_6A OtherDwelling" "MidRise__Toronto_5A MidRise" "HighRise__Montreal_6A HighRise")
FAIL=0

for ENTRY in "${CELLS[@]}"; do
    CELL=$(echo $ENTRY | cut -d' ' -f1)
    DTYPE=$(echo $ENTRY | cut -d' ' -f2)
    IDF=$(awk -F',' -v cell="$CELL" '$2==cell && $3=="activity" && $5=="2022" {print $6; exit}' "$MANIFEST")
    if [ -z "$IDF" ]; then
        echo "SKIP [$CELL]: no activity/2022 entry in manifest (run stage A first)"
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
    echo "=== ALL 4 PRECHECKS PASS — safe to run step9_b_array_full.sh ==="
else
    echo "=== PRECHECK FAIL — fix wiring BEFORE array ==="
    exit 1
fi
