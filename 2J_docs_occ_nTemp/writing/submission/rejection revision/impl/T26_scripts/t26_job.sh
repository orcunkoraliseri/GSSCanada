#!/bin/bash
#SBATCH --job-name=t26_scenario
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-2%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T26/logs/slurm_%A_%a.out

# T26 -- WP2 2030 scenario schedule builds (S-Persist/S-Partial/S-Revert).
# Task doc: 2026-09-15_T26_wp2_scenario_builds.md. Spec:
# 2026-09-15_WP2_scenario_spec.md.
# Array task 0 = lambda 1.0 (S-Persist, SC0 nesting check vs T20 main, plus
#                the standardized-jump sensitivity -- lambda-independent, so
#                computed only here).
# Array task 1 = lambda 0.5 (S-Partial).
# Array task 2 = lambda 0.0 (S-Revert).
# %2 throttles at most 2 of the 3 tasks running concurrently (16 of our
# 32-CPU cap at -c 8 each).
#
# Inputs are the Nb-f stock (T18c manager decision, 2026-09-15: Nb-f is the
# frozen 2022 stock, 2026-09-15_T18c_wp1_frame_v2.md "Manager decision") plus
# the new T20 array's own output:
#   stock          = T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
#   diaries (FULL) = T18/input/augmented_diaries.csv (unchanged)
#   arm_n_2022_bem = T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
#   t20_main_bem   = T20/out/main/BEM_Setup/BEM_Schedules_2030.csv  (SC0 reference, task 0 only)
#
# Old chain read T18 Arm N outputs and depended on job 1328311 (superseded,
# stuck behind FAILED 1328301) -- superseded here (manager, 2026-09-15) by
# the Nb-f stock above. This array is submitted with
# --dependency=afterok:<new T20 JobID>, so every one of these exists by the
# time this job starts; each is also checked explicitly below as
# defense-in-depth.

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T26_ROOT=/speed-scratch/o_iseri/2J_revision/T26
T18_ROOT=/speed-scratch/o_iseri/2J_revision/T18
T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf
T20_ROOT=/speed-scratch/o_iseri/2J_revision/T20
SCRIPTS=$T26_ROOT/T26_scripts

case "$SLURM_ARRAY_TASK_ID" in
  0) LAM=1.0 ;;
  1) LAM=0.5 ;;
  2) LAM=0.0 ;;
  *) echo "unexpected SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID"; exit 1 ;;
esac

OUT_DIR=$T26_ROOT/out/lambda_$LAM
LOGS=$T26_ROOT/logs
mkdir -p "$OUT_DIR" "$LOGS"

STOCK=$T18C_ROOT/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
DIARIES=$T18_ROOT/input/augmented_diaries.csv
ARM_N_2022_BEM=$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
T20_MAIN_BEM=$T20_ROOT/out/main/BEM_Setup/BEM_Schedules_2030.csv

echo "=========== T26 task $SLURM_ARRAY_TASK_ID (lambda=$LAM) START ==========="

for f in "$STOCK" "$DIARIES" "$ARM_N_2022_BEM" "$T20_MAIN_BEM"; do
  echo "--- STEP START: input check ($f) ---"
  if [ ! -f "$f" ]; then
    echo "--- STEP FAILED: input check --- missing: $f"
    exit 1
  fi
  echo "--- STEP OK: input check ($f) ---"
done

# SC4 no-leakage: md5 of the Arm N + T20 outputs this task reads, before.
echo "--- STEP START: SC4 md5 before (lambda=$LAM) ---"
md5sum "$STOCK" > "$OUT_DIR/sc4_md5_stock_before.txt"
md5sum "$ARM_N_2022_BEM" > "$OUT_DIR/sc4_md5_bem2022_before.txt"
md5sum "$T20_MAIN_BEM" > "$OUT_DIR/sc4_md5_t20main_before.txt"
cat "$OUT_DIR/sc4_md5_stock_before.txt" "$OUT_DIR/sc4_md5_bem2022_before.txt" "$OUT_DIR/sc4_md5_t20main_before.txt"
echo "--- STEP OK: SC4 md5 before (lambda=$LAM) ---"

echo "--- STEP START: t26_scenario.py --lambda $LAM ---"
if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
  "$PYTHON" "$SCRIPTS/t26_scenario.py" --lambda "$LAM" \
    --stock "$STOCK" --diaries "$DIARIES" \
    --scripts-dir "$SCRIPTS" --out-dir "$OUT_DIR" --validate --std-jump
else
  "$PYTHON" "$SCRIPTS/t26_scenario.py" --lambda "$LAM" \
    --stock "$STOCK" --diaries "$DIARIES" \
    --scripts-dir "$SCRIPTS" --out-dir "$OUT_DIR" --validate
fi
echo "--- STEP OK: t26_scenario.py --lambda $LAM ---"

echo "--- STEP START: t26_metrics.py --action report (lambda=$LAM) ---"
if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
  "$PYTHON" "$SCRIPTS/t26_metrics.py" --action report --lam "$LAM" \
    --arm-n-2022-bem "$ARM_N_2022_BEM" \
    --bem "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" \
    --targets "$OUT_DIR/t26_targets_lambda_$LAM.csv" \
    --person-table "$OUT_DIR/t26_person_table_lambda_$LAM.csv" \
    --t20-main-bem "$T20_MAIN_BEM" \
    --out "$OUT_DIR/t26_metrics_lambda_$LAM.csv"
else
  "$PYTHON" "$SCRIPTS/t26_metrics.py" --action report --lam "$LAM" \
    --arm-n-2022-bem "$ARM_N_2022_BEM" \
    --bem "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" \
    --targets "$OUT_DIR/t26_targets_lambda_$LAM.csv" \
    --person-table "$OUT_DIR/t26_person_table_lambda_$LAM.csv" \
    --out "$OUT_DIR/t26_metrics_lambda_$LAM.csv"
fi
echo "--- STEP OK: t26_metrics.py --action report (lambda=$LAM) ---"

# SC4 no-leakage: md5 after. Same three files, still read-only originals.
echo "--- STEP START: SC4 md5 after (lambda=$LAM) ---"
md5sum "$STOCK" > "$OUT_DIR/sc4_md5_stock_after.txt"
md5sum "$ARM_N_2022_BEM" > "$OUT_DIR/sc4_md5_bem2022_after.txt"
md5sum "$T20_MAIN_BEM" > "$OUT_DIR/sc4_md5_t20main_after.txt"
cat "$OUT_DIR/sc4_md5_stock_after.txt" "$OUT_DIR/sc4_md5_bem2022_after.txt" "$OUT_DIR/sc4_md5_t20main_after.txt"
if diff -q "$OUT_DIR/sc4_md5_stock_before.txt" "$OUT_DIR/sc4_md5_stock_after.txt" > /dev/null \
   && diff -q "$OUT_DIR/sc4_md5_bem2022_before.txt" "$OUT_DIR/sc4_md5_bem2022_after.txt" > /dev/null \
   && diff -q "$OUT_DIR/sc4_md5_t20main_before.txt" "$OUT_DIR/sc4_md5_t20main_after.txt" > /dev/null; then
  echo "[SC4] PASS: Nb-f + T20 outputs unchanged (lambda=$LAM)"
else
  echo "[SC4] FAIL: an upstream output changed -- leakage (lambda=$LAM)"
fi
echo "--- STEP OK: SC4 md5 after (lambda=$LAM) ---"

echo "=========== T26 task $SLURM_ARRAY_TASK_ID (lambda=$LAM) COMPLETE ==========="
