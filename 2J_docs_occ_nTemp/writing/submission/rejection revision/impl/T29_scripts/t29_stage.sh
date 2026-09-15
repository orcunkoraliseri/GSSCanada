#!/bin/bash
#SBATCH --job-name=t29_stage
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T29/logs/t29_stage_%j.out

# t29_stage.sh -- T29 Phase B step 1 (NOT submitted by Phase A -- Phase A only
# writes + syntax-checks this script). Copies the two T26 scenario-build
# outputs (S-Partial lambda=0.5, S-Revert lambda=0.0) into T29's own
# sched_lambda_<v>/ dirs under the plain filename run_paired_mc.py's
# --sched-dir expects, and writes md5s of the SOURCE files before either
# array starts (task doc design line 18-19: "writes md5s before the arrays
# start"). S-Persist (lambda=1.0) is NOT staged here -- it is T21's own
# Step-8 2030 arm and is not rerun (task doc Design, WP2 spec Sec 4).
#
# Source: T26/out/lambda_<v>/BEM_Setup/BEM_Schedules_2030.csv (T26 task doc
# Ledger, "Output: ... per-lambda artifacts under T26/out/lambda_<v>/
# (... BEM_Setup/BEM_Schedules_2030.csv ...)").
# Dest:   T29/sched_lambda_<v>/BEM_Schedules_2030.csv (plain filename;
# run_paired_mc.py's --sched-dir pre-loads BEM_Schedules_{y}.csv per
# requested year from this dir, main.py:2025-2027, T21 Verified).
#
# NOTE: this job only stages the 2030 file per lambda. The command
# (task doc Design line 12) is "--years 2030" alone (not "2022,2030"): T27
# Q1b confirms that when the 2030 file's household-ID set equals the 2022
# file's (true here -- T26's builds keep the 2022 IDs, task doc Design line
# 15-16), the per-cell pool for --years 2030 alone is just
# sorted(keys(schedules['2030'])), so no 2022 file is needed in T29's own
# sched_lambda_<v>/ dirs. This is checked by the collector's P1 (pairing
# against T21's own manifest), not assumed here.

set -u

T29_ROOT=/speed-scratch/o_iseri/2J_revision/T29
T26_ROOT=/speed-scratch/o_iseri/2J_revision/T26

FAIL=0
MD5_BEFORE=$T29_ROOT/sched_md5_before.txt
: > "$MD5_BEFORE"

echo "=== T29 stage | job=${SLURM_JOB_ID} | $(date) ==="

for V in 0.5 0.0; do
    SRC=$T26_ROOT/out/lambda_${V}/BEM_Setup/BEM_Schedules_2030.csv
    DST_DIR=$T29_ROOT/sched_lambda_${V}
    DST=$DST_DIR/BEM_Schedules_2030.csv

    echo "--- STEP START: lambda=${V} ---"
    if [ ! -f "$SRC" ]; then
        echo "--- STEP FAILED: lambda=${V} --- missing source $SRC (has T26's array/job completed?)"
        FAIL=1
        continue
    fi

    mkdir -p "$DST_DIR"

    SRC_MD5=$(md5sum "$SRC" | awk '{print $1}')
    echo "$SRC_MD5  $SRC" >> "$MD5_BEFORE"

    cp "$SRC" "$DST"
    RC=$?
    if [ "$RC" -ne 0 ]; then
        echo "--- STEP FAILED: lambda=${V} --- cp exit=$RC"
        FAIL=1
        continue
    fi

    DST_MD5=$(md5sum "$DST" | awk '{print $1}')
    if [ "$SRC_MD5" != "$DST_MD5" ]; then
        echo "--- STEP FAILED: lambda=${V} --- md5 mismatch after copy (src=$SRC_MD5 dst=$DST_MD5)"
        FAIL=1
        continue
    fi
    echo "  copied OK: $SRC -> $DST (md5 $SRC_MD5)"
    echo "--- STEP DONE: lambda=${V} ---"
done

echo "=== T29 stage COMPLETE | overall FAIL=$FAIL | md5-before -> $MD5_BEFORE ==="
exit $FAIL
