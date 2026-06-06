#!/encs/bin/bash
#SBATCH --job-name=s9_val_full
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_val_full_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_val_full_%j.err

# Stage C FULL — validate 24-cell/n=50 results (run after step9_b_array_full.sh completes).
# Calls step9_validate_full.py which applies the OtherDwelling fridge correction (D8).
# Expected: 4,800 hourly_meters.csv (200 per cell = 50 HH x 2 yr x 2 trt).
# Writes cluster_run_results.csv; exits 0 only if all 48 cell×year gates PASS.

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
VALIDATE=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_validate_full.py

echo "=== Step 9 Full-Grid Validation ==="
echo "Node: $(hostname)  Date: $(date)"

TOTAL=4800
DONE=$(find $ROOT/idfs -name "hourly_meters.csv" | wc -l)
echo "Completed runs: $DONE / $TOTAL"
if [ $DONE -lt $((TOTAL - 48)) ]; then
    echo "WARNING: more than 1% missing ($((TOTAL - DONE)) missing) — listing first 10:"
    find $ROOT/idfs -name "Scenario_*.idf" | while read IDF; do
        DIR=$(dirname "$IDF")
        if [ ! -f "$DIR/hourly_meters.csv" ]; then echo "  MISSING: $DIR"; fi
    done | head -10
fi

$PYTHON "$VALIDATE" --root "$ROOT" --out "$ROOT/cluster_run_results.csv"
VALIDATE_RC=$?

echo "Date: $(date)"
if [ $VALIDATE_RC -eq 0 ]; then
    echo "=== STAGE C: ALL 48 GATES PASS ==="
else
    echo "=== STAGE C: VALIDATION FAIL — report to manager ==="
    exit 1
fi
