#!/bin/bash
#SBATCH --job-name=t21_a4_after
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T21/logs/t21_a4_after_%j.out

# t21_a4_md5_after.sh -- T21 Phase B, Acceptance A4 ("inputs unchanged during
# run"). Cheap, python-free, no-engine-import re-check of the 4 staged
# schedule CSVs' md5 against T21/sched_md5_before.txt (written by
# t21_extract_baseline.sh before any array task ran). Submitted with
# --dependency=afterany: on all three campaign arrays so it answers quickly
# without waiting on t21_check.py's much slower engine-based A2 re-draw
# across 24 cells (which also re-checks A4 internally as a second,
# independent confirmation -- see that script's own docstring).
#
# Task doc: 2026-09-15_T21_wp1_step8_step9_rerun.md, Acceptance A4.

set -u

T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
ACT_DIR=$T21_ROOT/sched_activity
BASE_DIR=$T21_ROOT/sched_baseline
BEFORE=$T21_ROOT/sched_md5_before.txt
AFTER=$T21_ROOT/logs/sched_md5_after_${SLURM_JOB_ID}.txt

echo "=== T21 A4 md5-after START | job=${SLURM_JOB_ID} host=$(hostname) date=$(date) ==="

if [ ! -f "$BEFORE" ]; then
  echo "--- STEP FAILED: no before-file at $BEFORE (did t21_extract_baseline.sh run?) ---"
  exit 1
fi

md5sum "$ACT_DIR/BEM_Schedules_2022.csv" "$ACT_DIR/BEM_Schedules_2030.csv" \
       "$BASE_DIR/BEM_Schedules_2022.csv" "$BASE_DIR/BEM_Schedules_2030.csv" \
       > "$AFTER"
RC=$?
if [ "$RC" -ne 0 ]; then
  echo "--- STEP FAILED: md5sum exit=$RC (one of the 4 files may be missing) ---"
  cat "$AFTER"
  exit 1
fi

echo "--- before ---"
cat "$BEFORE"
echo "--- after (this job) ---"
cat "$AFTER"

# Compare by path -> md5 (order-independent), same parsing rule as
# t21_check.py's a4_md5_check(): "<md5> <path>" per line.
DIFF_COUNT=0
while read -r md5_before path; do
  md5_now=$(grep -F " $path" "$AFTER" | awk '{print $1}')
  if [ -z "$md5_now" ]; then
    echo "MISSING_NOW: $path"
    DIFF_COUNT=$((DIFF_COUNT + 1))
  elif [ "$md5_now" != "$md5_before" ]; then
    echo "MISMATCH: $path before=$md5_before now=$md5_now"
    DIFF_COUNT=$((DIFF_COUNT + 1))
  fi
done < "$BEFORE"

if [ "$DIFF_COUNT" -eq 0 ]; then
  echo "=== A4 PASS: all 4 staged schedule files unchanged since before the arrays ran ==="
  exit 0
else
  echo "=== A4 FAIL: $DIFF_COUNT file(s) changed or missing ==="
  exit 1
fi
