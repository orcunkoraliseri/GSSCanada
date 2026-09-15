#!/bin/bash
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-5%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --nice=100
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T31/logs/t31_array_%A_%a.out

# t31_array.sh -- T31 Phase B array (NOT submitted by Phase A; written and
# bash -n checked only). Task doc: 2026-09-15_T31_wp7_existing_stock_envelope.md,
# Design section ("Runs") + Phase B section ("Go: ... Then build, stage,
# submit t31_array.sh").
#
# SingleD x the 6 cities x {2022,2030}, n=50, seed=42 -- 600 runs total (one
# array task per city; each task runs both years like T21/T22's own driver
# calls). Same engine as the published campaign (run_paired_mc.py ->
# run_step8_paired_mc()), same households as T21 (same seed/pool logic,
# T27 Q1).
#
# PREREQUISITE (Phase B employee's own job, done ONCE before this array is
# submitted, NOT inside this array script): build $VARIANT_CODE_ROOT as a
# copy of T22's staged, all-24-cell repo (T22/code/repo) with ONLY the
# SingleD IDF replaced by make_envelope_variant.py's output against the
# manager's envelope_existing_stock.json (written after dr_2J-09 is vetted
# -- see task doc "Phase B (later, fresh employee, only after manager go)").
# This array script does not build that tree itself, so that all 6 tasks
# read the SAME already-built, already-verified variant IDF rather than
# each task racing to rebuild it.
#
# Compute per Design section: "-c 4 --mem=16G, --array=0-5%2, --nice=100.
# About 12 CPU-hours" -- SBATCH headers above match this exactly.

set -u
# Deliberately no `set -e` (T21/T18 pattern): capture the driver's exit code
# explicitly and echo the summary line even on failure.

: "${VARIANT_CODE_ROOT:?VARIANT_CODE_ROOT env var must be set to the pre-built existing-stock variant tree, e.g. /speed-scratch/o_iseri/2J_revision/T31/code/repo_existing_stock}"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=4

T31_ROOT=/speed-scratch/o_iseri/2J_revision/T31
SCHED_DIR=$T31_ROOT/../T21/sched_activity   # design line 30: "--sched-dir T21/sched_activity"; same
                                             # activity-arm inputs step8/step9_activity used in T21 (T21
                                             # Verified: step8 and step9_activity share this dir).
DRIVER=$VARIANT_CODE_ROOT/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
DRIVER_DIR=$(dirname "$DRIVER")

ARCH=SingleD
CITIES=(Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A)
CITY=${CITIES[$SLURM_ARRAY_TASK_ID]}
CELL="${ARCH}__${CITY}"
OUT_DIR=$T31_ROOT/out/$CELL

mkdir -p "$OUT_DIR" "$T31_ROOT/logs"

echo "=== T31 array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | CELL=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"
echo "VARIANT_CODE_ROOT=$VARIANT_CODE_ROOT  SCHED_DIR=$SCHED_DIR  OUT_DIR=$OUT_DIR"

if [ ! -f "$DRIVER" ]; then
    echo "ERROR: driver not found at $DRIVER -- was VARIANT_CODE_ROOT built (prerequisite above)?"
    exit 1
fi
if [ ! -f "$SCHED_DIR/BEM_Schedules_2022.csv" ] || [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
    echo "ERROR: missing staged schedule CSV(s) under $SCHED_DIR"
    exit 1
fi

cd "$DRIVER_DIR"
"$PYTHON" "$DRIVER" \
    --archetype "$ARCH" --city "$CITY" \
    --n 50 --seed 42 --sim-mode standard --years 2022,2030 \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
RC=$?

echo "=== T31 array task $SLURM_ARRAY_TASK_ID ($CELL) exit=$RC ==="
exit $RC
