#!/bin/bash
#SBATCH --job-name=t26_compare
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T26/logs/slurm_compare_%j.out

# T26 -- SC2 order check (Revert < Partial < Persist, strict) across the
# three scenario builds. Runs AFTER the t26_job.sh array (submitted with
# --dependency=afterok:<array JobID>), since SC2 needs all three outputs.
# Task doc: 2026-09-15_T26_wp2_scenario_builds.md.

set -e

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
T26_ROOT=/speed-scratch/o_iseri/2J_revision/T26
SCRIPTS=$T26_ROOT/T26_scripts

PERSIST_BEM=$T26_ROOT/out/lambda_1.0/BEM_Setup/BEM_Schedules_2030.csv
PARTIAL_BEM=$T26_ROOT/out/lambda_0.5/BEM_Setup/BEM_Schedules_2030.csv
REVERT_BEM=$T26_ROOT/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv

echo "=========== T26 compare (SC2) START ==========="

for f in "$PERSIST_BEM" "$PARTIAL_BEM" "$REVERT_BEM"; do
  echo "--- STEP START: input check ($f) ---"
  if [ ! -f "$f" ]; then
    echo "--- STEP FAILED: input check --- missing: $f"
    exit 1
  fi
  echo "--- STEP OK: input check ($f) ---"
done

echo "--- STEP START: t26_metrics.py --action compare ---"
"$PYTHON" "$SCRIPTS/t26_metrics.py" --action compare \
  --persist-bem "$PERSIST_BEM" --partial-bem "$PARTIAL_BEM" --revert-bem "$REVERT_BEM" \
  --out "$T26_ROOT/out/t26_compare_metrics.csv"
echo "--- STEP OK: t26_metrics.py --action compare ---"

echo "=========== T26 compare (SC2) COMPLETE ==========="
