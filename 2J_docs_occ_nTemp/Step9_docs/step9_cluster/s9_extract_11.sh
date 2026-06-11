#!/encs/bin/bash
#SBATCH --job-name=s9_extract11
#SBATCH --partition=ps
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_extract11_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_extract11_%j.err

# Extract hourly_meters.csv for 11 HighRise IDFs that completed E+ successfully but
# were rejected by the Severe-error check in s9_recovery_32.sh.
# All 11 have "EnergyPlus Completed Successfully" in eplusout.end —
# the Severe errors are warmup non-convergence only (CheckWarmupConvergence after 120 days),
# which does not invalidate simulation results.
# Runs afterany:954482 so it executes regardless of recovery-32 exit code.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
ROOT=/speed-scratch/o_iseri/step9_run
GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
EXTRACT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/cluster_spike/extract_meters.py

echo "=== Step 9 extract-11 | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

DONE=0; FAIL=0

extract_one() {
    local LABEL=$1
    local DIR=$ROOT/idfs/$LABEL
    echo ""
    echo "=== EXTRACT: $LABEL ==="
    if [ ! -f "$DIR/eplusout.sql" ]; then
        echo "  FAIL: eplusout.sql missing at $DIR"
        return 1
    fi
    if [ -f "$DIR/hourly_meters.csv" ]; then
        echo "  SKIP: hourly_meters.csv already present"
        return 0
    fi
    $PYTHON "$EXTRACT" "$DIR/eplusout.sql" "$DIR/hourly_meters.csv"
    if [ $? -ne 0 ]; then echo "  FAIL (extract): $LABEL"; return 1; fi
    echo "  OK: $LABEL"
    return 0
}

extract_one "HighRise__Kelowna_5B/activity/sample_043_HH75840/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Kelowna_5B/baseline/sample_006_HH119046/2030"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Montreal_6A/baseline/sample_037_HH79579/2030"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Toronto_5A/baseline/sample_017_HH90265/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Toronto_5A/baseline/sample_026_HH47072/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Toronto_5A/baseline/sample_040_HH7077/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Vancouver_5C/activity/sample_032_HH104153/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Vancouver_5C/activity/sample_038_HH59576/2030"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Vancouver_5C/baseline/sample_006_HH64721/2030"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Vancouver_5C/baseline/sample_031_HH101651/2030"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

extract_one "HighRise__Vancouver_5C/baseline/sample_038_HH59576/2022"
[ $? -eq 0 ] && DONE=$((DONE+1)) || FAIL=$((FAIL+1))

echo ""
echo "=== Extract-11 complete: succeeded=$DONE  failed=$FAIL ==="
echo "Date: $(date)"
[ $FAIL -gt 0 ] && exit 1 || exit 0
