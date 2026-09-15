#!/bin/bash
#SBATCH --job-name=t32_compare
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T32/logs/slurm_compare_%j.out

# T32 -- final compare: G0 regression guard (task 0 [guard_primary] vs
# T26's own lambda=0.0 S-Revert build), SC1/SC5 readout for S-Revert-std
# (task 1), and the weekday at-home change vs S-Revert (-3.2081 pp, T26
# collector). Runs AFTER the t32_job.sh array (submitted with
# --dependency=afterok:<array JobID>), since it needs both tasks' output.
# Task doc: 2026-09-15_T32_wp2_srevert_std_build.md.

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T32_ROOT=/speed-scratch/o_iseri/2J_revision/T32
T18C_ROOT=/speed-scratch/o_iseri/2J_revision/T18c/nbf
T26_ROOT=/speed-scratch/o_iseri/2J_revision/T26
SCRIPTS=$T32_ROOT/T32_scripts
T26_SCRIPTS=$T26_ROOT/T26_scripts

GUARD_BEM=$T32_ROOT/out/guard_primary/BEM_Setup/BEM_Schedules_2030.csv
STD_BEM=$T32_ROOT/out/std/BEM_Setup/BEM_Schedules_2030.csv
STD_TARGETS=$T32_ROOT/out/std/t32_targets_std.csv
STD_PERSON_TABLE=$T32_ROOT/out/std/t32_person_table_std.csv
ARM_N_2022_BEM=$T18C_ROOT/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv
T26_REVERT_BEM=$T26_ROOT/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv

echo "=========== T32 compare (G0 + SC1/SC5 readout) START ==========="

for f in "$GUARD_BEM" "$STD_BEM" "$STD_TARGETS" "$STD_PERSON_TABLE" "$ARM_N_2022_BEM" "$T26_REVERT_BEM"; do
  echo "--- STEP START: input check ($f) ---"
  if [ ! -f "$f" ]; then
    echo "--- STEP FAILED: input check --- missing: $f"
    exit 1
  fi
  echo "--- STEP OK: input check ($f) ---"
done

echo "--- STEP START: t32_metrics.py --action compare ---"
"$PYTHON" "$SCRIPTS/t32_metrics.py" --action compare --scripts-dir "$T26_SCRIPTS" \
  --bem "$GUARD_BEM" --t26-revert-bem "$T26_REVERT_BEM" \
  --std-bem "$STD_BEM" --arm-n-2022-bem "$ARM_N_2022_BEM" \
  --std-targets "$STD_TARGETS" --std-person-table "$STD_PERSON_TABLE" \
  --out "$T32_ROOT/out/t32_compare_metrics.csv"
echo "--- STEP OK: t32_metrics.py --action compare ---"

echo "=========== T32 compare (G0 + SC1/SC5 readout) COMPLETE ==========="
