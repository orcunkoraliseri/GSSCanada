#!/bin/bash
#SBATCH --job-name=t20_d1_2030
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T20/logs/slurm_%A_%a.out

# T20 -- WP1 stage B, part 3: build 2030 by D1 on the Nb-f rebuilt-2022
# stock (T18c manager decision, 2026-09-15: Nb-f is the frozen 2022 stock).
# Task doc: 2026-09-15_T20_wp1_d1_2030_build.md; stock choice:
# 2026-09-15_T18c_wp1_frame_v2.md "Manager decision".
# Array task 0 = null run (pre_slope == 0, N0 acceptance test).
# Array task 1 = main run (real slopes, N1/R-rake/N2 acceptance tests) --
# this task also runs the Step-7 validator (task doc: "validator on task 1").
#
# Every input path below is the exact Speed path recorded for the Nb-f stock
# (2026-09-15_T18c_wp1_frame_v2.md, Manager decision):
#   stock  = T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
#   bem22  = T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
#   diaries (FULL all-cycle, read-only) = T18/input/augmented_diaries.csv (unchanged)
#
# Old chain read T18 Arm N outputs and depended on job 1328301 (FAILED);
# that dependency and the Arm N paths are superseded here (manager,
# 2026-09-15) by the Nb-f stock above -- this job has no --dependency
# (Nb-f files already exist), and every input is also checked explicitly
# below (fail loudly, with the step name, if missing) as defense-in-depth.

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T20_ROOT=/speed-scratch/o_iseri/2J_revision/T20
T18_ROOT=/speed-scratch/o_iseri/2J_revision/T18
T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf
SCRIPTS=$T20_ROOT/T20_scripts

if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
  MODE=null
else
  MODE=main
fi

OUT_DIR=$T20_ROOT/out/$MODE
LOGS=$T20_ROOT/logs
mkdir -p "$OUT_DIR" "$LOGS"

STOCK=$T18C_ROOT/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
DIARIES=$T18_ROOT/input/augmented_diaries.csv
ARM_N_2022_BEM=$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv

echo "=========== T20 task $SLURM_ARRAY_TASK_ID (mode=$MODE) START ==========="

echo "--- STEP START: input check (Nb-f stock) ---"
if [ ! -f "$STOCK" ]; then
  echo "--- STEP FAILED: input check (Nb-f stock) --- missing: $STOCK"
  exit 1
fi
echo "--- STEP OK: input check (Nb-f stock) ---"

echo "--- STEP START: input check (full augmented_diaries.csv) ---"
if [ ! -f "$DIARIES" ]; then
  echo "--- STEP FAILED: input check (full augmented_diaries.csv) --- missing: $DIARIES"
  exit 1
fi
echo "--- STEP OK: input check (full augmented_diaries.csv) ---"

echo "--- STEP START: input check (Nb-f 2022 BEM_Schedules) ---"
if [ ! -f "$ARM_N_2022_BEM" ]; then
  echo "--- STEP FAILED: input check (Nb-f 2022 BEM_Schedules) --- missing: $ARM_N_2022_BEM"
  exit 1
fi
echo "--- STEP OK: input check (Nb-f 2022 BEM_Schedules) ---"

# N3 no-leakage: md5 of the Nb-f 2022 outputs, computed inside the job
# (never on the login node), before this task touches anything.
echo "--- STEP START: N3 md5 before ($MODE) ---"
md5sum "$STOCK" > "$OUT_DIR/n3_md5_stock_before.txt"
md5sum "$ARM_N_2022_BEM" > "$OUT_DIR/n3_md5_bem2022_before.txt"
cat "$OUT_DIR/n3_md5_stock_before.txt" "$OUT_DIR/n3_md5_bem2022_before.txt"
echo "--- STEP OK: N3 md5 before ($MODE) ---"

echo "--- STEP START: t20_d1.py --mode $MODE ---"
if [ "$MODE" = "main" ]; then
  "$PYTHON" "$SCRIPTS/t20_d1.py" --mode "$MODE" \
    --stock "$STOCK" --diaries "$DIARIES" \
    --scripts-dir "$SCRIPTS" --out-dir "$OUT_DIR" --validate
else
  "$PYTHON" "$SCRIPTS/t20_d1.py" --mode "$MODE" \
    --stock "$STOCK" --diaries "$DIARIES" \
    --scripts-dir "$SCRIPTS" --out-dir "$OUT_DIR"
fi
echo "--- STEP OK: t20_d1.py --mode $MODE ---"

echo "--- STEP START: t20_metrics.py --action report ($MODE) ---"
"$PYTHON" "$SCRIPTS/t20_metrics.py" --action report --mode "$MODE" \
  --arm-n-2022-bem "$ARM_N_2022_BEM" \
  --bem "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" \
  --targets "$OUT_DIR/t20_targets_$MODE.csv" \
  --person-table "$OUT_DIR/t20_person_table_$MODE.csv" \
  --out "$OUT_DIR/t20_metrics_$MODE.csv"
echo "--- STEP OK: t20_metrics.py --action report ($MODE) ---"

# N3 no-leakage: md5 after. Same two files, still read-only originals.
echo "--- STEP START: N3 md5 after ($MODE) ---"
md5sum "$STOCK" > "$OUT_DIR/n3_md5_stock_after.txt"
md5sum "$ARM_N_2022_BEM" > "$OUT_DIR/n3_md5_bem2022_after.txt"
cat "$OUT_DIR/n3_md5_stock_after.txt" "$OUT_DIR/n3_md5_bem2022_after.txt"
if diff -q "$OUT_DIR/n3_md5_stock_before.txt" "$OUT_DIR/n3_md5_stock_after.txt" > /dev/null \
   && diff -q "$OUT_DIR/n3_md5_bem2022_before.txt" "$OUT_DIR/n3_md5_bem2022_after.txt" > /dev/null; then
  echo "[N3] PASS: Nb-f 2022 outputs unchanged ($MODE)"
else
  echo "[N3] FAIL: Nb-f 2022 outputs changed -- leakage ($MODE)"
fi
echo "--- STEP OK: N3 md5 after ($MODE) ---"

echo "=========== T20 task $SLURM_ARRAY_TASK_ID (mode=$MODE) COMPLETE ==========="
