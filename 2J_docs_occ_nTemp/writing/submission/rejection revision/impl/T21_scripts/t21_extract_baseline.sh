#!/bin/bash
#SBATCH --job-name=t21_extract_baseline
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=64G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T21/logs/slurm_extract_%j.out

# t21_extract_baseline.sh -- T21 Phase A step 2: stage the two rebuilt 17-col
# "activity" schedule CSVs (T18 Arm N 2022 + T20 main 2030), derive the 13-col
# "baseline" CSVs from them with step9_a2_baseline_extract.py (same tool the
# published campaign used, T25 Q4), and expose the baseline CSVs under the
# PLAIN filename in a separate sched_baseline/ dir -- the layout
# run_paired_mc.py --sched-dir / run_step9_local.py's BASELINE_SCHED_DIR
# pattern expects (T25 Q7 item 2; run_step9_local.py:59,216-220).
#
# Task doc: 2026-09-15_T21_wp1_step8_step9_rerun.md, Design "Step-9 inputs
# regenerated together" + Brief step 2.
#
# Source files (rebuilt schedules; Nb-f stock per manager decision,
# 2026-09-15_T18c_wp1_frame_v2.md "Manager decision" -- supersedes the old
# T18 Arm N source, which this doc's Decisions section previously derived):
#   Nb-f 2022 (T18c): /speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
#     (confirmed present by remote ls -la before this edit; matches T20's own
#      t20_job.sh ARM_N_2022_BEM= the same path)
#   main   2030 (T20): /speed-scratch/o_iseri/2J_revision/T20/out/main/BEM_Setup/BEM_Schedules_2030.csv
#     (2026-09-15_T20_wp1_d1_2030_build.md Ledger: "Output: ... per-mode
#      artifacts under T20/out/{null,main}/ (... BEM_Setup/BEM_Schedules_2030.csv ...)")
#
# Old chain depended on job 1328311 (superseded, stuck behind FAILED
# 1328301) -- superseded here (manager, 2026-09-15) by the new T20 JobID on
# the Nb-f stock; both upstream sources are guaranteed to exist once this
# job starts -- the explicit existence checks below are defense-in-depth,
# matching T20's own t20_job.sh pattern, not a substitute for the Slurm
# dependency.

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf
T20_ROOT=/speed-scratch/o_iseri/2J_revision/T20
EXTRACT=$T21_ROOT/T21_scripts/step9_a2_baseline_extract.py

SRC_2022=$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
SRC_2030=$T20_ROOT/out/main/BEM_Setup/BEM_Schedules_2030.csv

ACT_DIR=$T21_ROOT/sched_activity
BASE_DIR=$T21_ROOT/sched_baseline
mkdir -p "$ACT_DIR" "$BASE_DIR" "$T21_ROOT/logs"

echo "=== T21 extract_baseline START | job=${SLURM_JOB_ID} host=$(hostname) date=$(date) ==="

echo "--- STEP START: input check ---"
if [ ! -f "$SRC_2022" ]; then
  echo "--- STEP FAILED: input check --- missing: $SRC_2022"
  exit 1
fi
if [ ! -f "$SRC_2030" ]; then
  echo "--- STEP FAILED: input check --- missing: $SRC_2030"
  exit 1
fi
echo "--- STEP OK: input check ---"

echo "--- STEP START: stage activity CSVs (copy, plain filename) ---"
cp "$SRC_2022" "$ACT_DIR/BEM_Schedules_2022.csv"
cp "$SRC_2030" "$ACT_DIR/BEM_Schedules_2030.csv"
echo "--- STEP OK: stage activity CSVs ---"

echo "--- STEP START: step9_a2_baseline_extract.py --bem_dir $ACT_DIR ---"
"$PYTHON" "$EXTRACT" --bem_dir "$ACT_DIR"
echo "--- STEP OK: step9_a2_baseline_extract.py ---"

echo "--- STEP START: expose baseline CSVs under plain filename ---"
if [ ! -f "$ACT_DIR/BEM_Schedules_2022_baseline.csv" ] || [ ! -f "$ACT_DIR/BEM_Schedules_2030_baseline.csv" ]; then
  echo "--- STEP FAILED: extractor did not write the expected _baseline.csv files ---"
  exit 1
fi
cp "$ACT_DIR/BEM_Schedules_2022_baseline.csv" "$BASE_DIR/BEM_Schedules_2022.csv"
cp "$ACT_DIR/BEM_Schedules_2030_baseline.csv" "$BASE_DIR/BEM_Schedules_2030.csv"
echo "--- STEP OK: expose baseline CSVs under plain filename ---"

echo "--- STEP START: md5 of all four staged files (A4 'before') ---"
md5sum "$ACT_DIR/BEM_Schedules_2022.csv" "$ACT_DIR/BEM_Schedules_2030.csv" \
       "$BASE_DIR/BEM_Schedules_2022.csv" "$BASE_DIR/BEM_Schedules_2030.csv" \
       > "$T21_ROOT/sched_md5_before.txt"
cat "$T21_ROOT/sched_md5_before.txt"
echo "--- STEP OK: md5 of all four staged files ---"

echo "=== T21 extract_baseline COMPLETE ==="
