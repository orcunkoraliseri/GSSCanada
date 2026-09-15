#!/bin/bash
#SBATCH --job-name=t32_scenario
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T32/logs/slurm_%A_%a.out

# T32 -- S-Revert-std build (spec addendum Sec 5) plus a primary-basis
# regression guard (G0). Task doc: 2026-09-15_T32_wp2_srevert_std_build.md.
# Spec: 2026-09-15_WP2_scenario_spec.md Sec 2 and Sec 5.
# Array task 0 = --jump-basis primary (G0 regression guard: must reproduce
#                T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv exactly,
#                share of equal occupancy cells = 1.0, or task 1's output is
#                not used).
# Array task 1 = --jump-basis std (S-Revert-std).
# %2 throttles at most 2 (both) tasks running concurrently (16 of our
# 32-CPU cap at -c 8 each, T26 precedent).
#
# Inputs are the SAME Nb-f stock and diaries T26 used, plus T26's own
# lambda=0.0 (S-Revert) output as the G0 comparator:
#   stock          = T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
#   diaries (FULL) = T18/input/augmented_diaries.csv (unchanged)
#   arm_n_2022_bem = T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
#   t26_revert_bem = T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv (G0 reference, read-only)
# t32_scenario.py's own --scripts-dir points at T26/T26_scripts directly
# (read-only import of t26_scenario.py/t20_d1.py/06_forecast_rake.py/etc --
# never written to; T26 is a T17-T31 dir, off-limits to write).

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T32_ROOT=/speed-scratch/o_iseri/2J_revision/T32
T18_ROOT=/speed-scratch/o_iseri/2J_revision/T18
T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf
T26_ROOT=/speed-scratch/o_iseri/2J_revision/T26
SCRIPTS=$T32_ROOT/T32_scripts
T26_SCRIPTS=$T26_ROOT/T26_scripts

case "$SLURM_ARRAY_TASK_ID" in
  0) BASIS=primary; OUT_DIR=$T32_ROOT/out/guard_primary ;;
  1) BASIS=std; OUT_DIR=$T32_ROOT/out/std ;;
  *) echo "unexpected SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID"; exit 1 ;;
esac

LOGS=$T32_ROOT/logs
mkdir -p "$OUT_DIR" "$LOGS"

STOCK=$T18C_ROOT/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv
DIARIES=$T18_ROOT/input/augmented_diaries.csv
ARM_N_2022_BEM=$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
T26_REVERT_BEM=$T26_ROOT/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv

echo "=========== T32 task $SLURM_ARRAY_TASK_ID (jump-basis=$BASIS) START ==========="

for f in "$STOCK" "$DIARIES" "$ARM_N_2022_BEM" "$T26_REVERT_BEM"; do
  echo "--- STEP START: input check ($f) ---"
  if [ ! -f "$f" ]; then
    echo "--- STEP FAILED: input check --- missing: $f"
    exit 1
  fi
  echo "--- STEP OK: input check ($f) ---"
done

# Read-only leakage guard: md5 of T26's lambda=0.0 comparator before/after
# (T26 dir is off-limits to write; this only confirms it was not touched).
echo "--- STEP START: md5 before (T26 lambda=0.0 reference) ---"
md5sum "$T26_REVERT_BEM" > "$OUT_DIR/md5_t26_revert_before.txt"
cat "$OUT_DIR/md5_t26_revert_before.txt"
echo "--- STEP OK: md5 before (T26 lambda=0.0 reference) ---"

echo "--- STEP START: t32_scenario.py --jump-basis $BASIS ---"
"$PYTHON" "$SCRIPTS/t32_scenario.py" --jump-basis "$BASIS" \
  --stock "$STOCK" --diaries "$DIARIES" \
  --scripts-dir "$T26_SCRIPTS" --out-dir "$OUT_DIR" --validate
echo "--- STEP OK: t32_scenario.py --jump-basis $BASIS ---"

# md5 of this task's own output (task doc Design: "md5 of the output
# BEM_Schedules_2030.csv and of the T26 lambda=0 file").
echo "--- STEP START: md5 of this task's own output ---"
md5sum "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" > "$OUT_DIR/md5_own_output.txt"
cat "$OUT_DIR/md5_own_output.txt"
echo "--- STEP OK: md5 of this task's own output ---"

echo "--- STEP START: md5 after (T26 lambda=0.0 reference) ---"
md5sum "$T26_REVERT_BEM" > "$OUT_DIR/md5_t26_revert_after.txt"
cat "$OUT_DIR/md5_t26_revert_after.txt"
if diff -q "$OUT_DIR/md5_t26_revert_before.txt" "$OUT_DIR/md5_t26_revert_after.txt" > /dev/null; then
  echo "[LEAK-GUARD] PASS: T26 lambda=0.0 reference unchanged (task=$SLURM_ARRAY_TASK_ID)"
else
  echo "[LEAK-GUARD] FAIL: T26 lambda=0.0 reference changed -- leakage (task=$SLURM_ARRAY_TASK_ID)"
fi
echo "--- STEP OK: md5 after (T26 lambda=0.0 reference) ---"

echo "--- STEP START: t32_metrics.py --action report (jump-basis=$BASIS) ---"
if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then
  "$PYTHON" "$SCRIPTS/t32_metrics.py" --action report --scripts-dir "$T26_SCRIPTS" \
    --basis "$BASIS" \
    --arm-n-2022-bem "$ARM_N_2022_BEM" \
    --bem "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" \
    --targets "$OUT_DIR/t32_targets_$BASIS.csv" \
    --person-table "$OUT_DIR/t32_person_table_$BASIS.csv" \
    --t26-revert-bem "$T26_REVERT_BEM" \
    --out "$OUT_DIR/t32_metrics_$BASIS.csv"
else
  "$PYTHON" "$SCRIPTS/t32_metrics.py" --action report --scripts-dir "$T26_SCRIPTS" \
    --basis "$BASIS" \
    --arm-n-2022-bem "$ARM_N_2022_BEM" \
    --bem "$OUT_DIR/BEM_Setup/BEM_Schedules_2030.csv" \
    --targets "$OUT_DIR/t32_targets_$BASIS.csv" \
    --person-table "$OUT_DIR/t32_person_table_$BASIS.csv" \
    --out "$OUT_DIR/t32_metrics_$BASIS.csv"
fi
echo "--- STEP OK: t32_metrics.py --action report (jump-basis=$BASIS) ---"

echo "=========== T32 task $SLURM_ARRAY_TASK_ID (jump-basis=$BASIS) COMPLETE ==========="
