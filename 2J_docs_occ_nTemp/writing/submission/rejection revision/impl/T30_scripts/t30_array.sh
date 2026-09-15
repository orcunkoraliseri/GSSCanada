#!/encs/bin/bash
#SBATCH --job-name=t30_avg
#SBATCH --partition=ps
#SBATCH --array=0-47%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --nice=100
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_%A_%a.err

# T30 -- WP3 average-profile arm, full run, 24 cells x 2 years = 48 tasks.
# Task 0-23 -> year 2022 (Nb-f rebuild), task 24-47 -> year 2030 (T20 main,
# S-Persist), same ARCHETYPES x CITIES cross join and task-index order as
# T22's static arm / the published campaign (step8_array_v2.sh:18-29, T27 Q2).
# CODE_ROOT is the shared driver tree (T21 Ledger, "driver path fix"), read-only.
# SCHED_DIR is T21/sched_activity -- holds the Nb-f 2022 file and the T20
# 2030 file (Phase B go condition: T21 smoke collected PASS, i.e. that dir
# is populated).
# --nice=100 so T21's own remaining jobs get scheduling priority over this array.
#
# Phase-B paired-pool change (manager addendum, "V1 decided, phase B go",
# 2026-09-15): run_avg_arm.py now loads BOTH years from SCHED_DIR for every
# task (even a 2030 task also reads the 2022 file) to build the 2022-and-2030
# intersection pool before sampling, so the household draw is identical for
# a cell's 2022 task and its 2030 task -- matching T21's own paired draw.
#
# Submitted by phase B with --dependency=afterok:<re-smoke JobID>; see the
# T30 task doc's Phase B section and this doc's own Ledger for the JobID.

ARCHETYPES=(
    "SingleD"       "SingleD"       "SingleD"       "SingleD"       "SingleD"       "SingleD"
    "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling" "OtherDwelling"
    "MidRise"       "MidRise"       "MidRise"       "MidRise"       "MidRise"       "MidRise"
    "HighRise"      "HighRise"      "HighRise"      "HighRise"      "HighRise"      "HighRise"
)
CITIES=(
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
    "Toronto_5A" "Kelowna_5B" "Vancouver_5C" "Montreal_6A" "Calgary_6B" "Winnipeg_7A"
)

CELL_IDX=$(( SLURM_ARRAY_TASK_ID % 24 ))
if [ "$SLURM_ARRAY_TASK_ID" -lt 24 ]; then
    YEAR=2022
else
    YEAR=2030
fi
ARCH="${ARCHETYPES[$CELL_IDX]}"
CITY="${CITIES[$CELL_IDX]}"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
WRAPPER=/speed-scratch/o_iseri/2J_revision/T30/T30_scripts/run_avg_arm.py
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
SCHED_DIR=/speed-scratch/o_iseri/2J_revision/T21/sched_activity
OUT_ROOT=/speed-scratch/o_iseri/2J_revision/T30/out

mkdir -p "${OUT_ROOT}/${ARCH}__${CITY}__${YEAR}" /speed-scratch/o_iseri/2J_revision/T30/logs

export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export IDD_FILE=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd

echo "=== T30 avg arm | task=$SLURM_ARRAY_TASK_ID cell_idx=$CELL_IDX arch=$ARCH city=$CITY year=$YEAR ==="
echo "CODE_ROOT=$CODE_ROOT"
echo "SCHED_DIR=$SCHED_DIR"
echo "Start: $(date)"

$PYTHON "$WRAPPER" \
    --archetype "$ARCH" \
    --city "$CITY" \
    --year "$YEAR" \
    --n 50 \
    --seed 42 \
    --sched-dir "$SCHED_DIR" \
    --output-dir "${OUT_ROOT}/${ARCH}__${CITY}__${YEAR}" \
    --code-root "$CODE_ROOT"

EXIT=$?
echo "End: $(date)  exit=$EXIT"
exit $EXIT
