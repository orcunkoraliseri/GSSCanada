#!/bin/bash
#SBATCH --job-name=t21_check
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T21/logs/t21_check_%j.out

# t21_check.sh -- T21 Phase B collector job: runs t21_check.py's --selftest
# FIRST (the A2-restated check must be SEEN failing on a swapped id before
# its PASS on real data is trusted, task doc Ledger "diagnosis 1328414 read
# + manager decision"), then, only if the selftest behaves as expected, the
# real A1-A4/A2(restated)/A2X/A2-info check across all 24 cells x 3
# campaigns. Submitted with --dependency=afterany: on all three campaign
# arrays (afterany, not afterok -- A1 must be able to report partial
# completeness / undelivered runs even if an array task failed; per the
# design's own "record every undelivered run by cell; do not fill it").
#
# Heavy: A2(restated) loads the staged 2022/2030 schedule CSVs per unique
# (sched_dir, dtype, region) via the engine's own load_schedules() --
# NEVER run this on the login node (see t21_check.py's own module
# docstring and this task's cluster rules).
#
# Task doc: 2026-09-15_T21_wp1_step8_step9_rerun.md, Acceptance A1-A6 (A5/A6
# are separate scripts per the design, not part of this collector run),
# Brief step 4 ("t21_check.py job (including the selftest first)").

set -u

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers

T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
SCRIPT_DIR=/speed-scratch/o_iseri/2J_revision/T21/T21_scripts
CHECK=$SCRIPT_DIR/t21_check.py

echo "=== T21 check job START | job=${SLURM_JOB_ID} host=$(hostname) date=$(date) ==="

echo "--- STEP START: A2-logic selftest (must report FAIL on the swapped-id copy) ---"
"$PYTHON" "$CHECK" --selftest --t21-root "$T21_ROOT" --code-root "$CODE_ROOT"
SELFTEST_RC=$?
if [ "$SELFTEST_RC" -ne 0 ]; then
  echo "--- STEP FAILED: selftest did not behave as expected (exit=$SELFTEST_RC) -- " \
       "the A2 check's own logic is suspect, NOT running the real check, its PASS could not be trusted ---"
  echo "=== T21 check job ABORTED (selftest failure) ==="
  exit 1
fi
echo "--- STEP OK: selftest behaved as expected (PASS on unmodified copy, FAIL on swapped copy) ---"

echo "--- STEP START: real A1-A4 / A2(restated) / A2X / A2-info check, 24 cells x 3 campaigns ---"
"$PYTHON" "$CHECK" \
    --t21-root "$T21_ROOT" \
    --code-root "$CODE_ROOT" \
    --pub-sched-dir "/speed-scratch/o_iseri/2J_revision/T17/code/sched" \
    --step8-ref-dir "$T21_ROOT/ref/step8" \
    --step9-ref-dir "$T21_ROOT/ref/step9" \
    --out "$T21_ROOT/out/t21_check_report.csv"
RC=$?
echo "=== T21 check job (real check) exit=$RC ==="
exit $RC
