#!/encs/bin/bash
#SBATCH --job-name=s9_validate
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_validate_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_validate_%j.err

# Phase 5 — validation + report (run after array is complete).

. /encs/pkg/modules-5.3.1/root/init/bash

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
VALIDATE=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/step9_cluster/step9_validate.py

echo "=== Step 9 Validation ==="
echo "Node: $(hostname)  Date: $(date)"

TOTAL=240
DONE=$(find $ROOT/idfs -name "hourly_meters.csv" | wc -l)
echo "Completed runs: $DONE / $TOTAL"
if [ $DONE -lt $TOTAL ]; then
    echo "WARNING: $((TOTAL - DONE)) runs missing — listing first 10:"
    find $ROOT/idfs -name "Scenario_*.idf" | while read IDF; do
        DIR=$(dirname "$IDF")
        if [ ! -f "$DIR/hourly_meters.csv" ]; then echo "  MISSING: $DIR"; fi
    done | head -10
fi

$PYTHON "$VALIDATE" --root "$ROOT" --out "$ROOT/cluster_run_results.csv"
VALIDATE_RC=$?

echo "Date: $(date)"
if [ $VALIDATE_RC -eq 0 ]; then
    echo "=== PHASE 5: ALL GATES PASS ==="
else
    echo "=== PHASE 5: VALIDATION FAIL — report to manager ==="
    exit 1
fi
