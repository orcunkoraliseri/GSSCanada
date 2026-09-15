#!/bin/bash
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-23%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T29/logs/t29_%x_%A_%a.out

# t29_array.sh -- T29 Phase B array. One array task per cell, for a given
# LAMBDA (0.5 = S-Partial, 0.0 = S-Revert). S-Persist (lambda=1.0) is NOT run
# here -- it is T21's own Step-8 2030 arm (task doc Design line 10-11).
#
# UPDATED (manager addendum 2, 2026-09-15): the phase-A premise ("--years 2030
# alone reproduces T21's households") is FALSE on the rebuilt scenario files.
# T21 diagnosis 1328414: the engine's pool is the set of households that pass
# validate_household_schedule() on the schedule file(s) LOADED, which depends
# on schedule CONTENT, not only on the stock/ID set (SingleD Montreal 2022
# alone 16,327, 2030 alone 16,326, paired 16,326 -- one household of
# difference already changes the seed-42 draw). Each scenario file changes
# schedule content, so a fresh rng.sample() draw on it would pick OTHER
# households than T21 did, and P1 (pairing) would fail by construction.
#
# This array therefore no longer calls run_paired_mc.py's own sampling path.
# It calls the new run_fixed_manifest.py wrapper (T29_scripts/, built from a
# COPY of run_paired_mc.py -- no repo edits), passing --manifest = T21's own
# Step-8 cell_manifest.csv for this cell, so this run simulates EXACTLY the
# same (sample, hh_id) pairs T21 used, on THIS scenario's schedule file, year
# 2030 only. A manifest household absent from -- or dropped by the sanity
# check in -- the scenario file lands in this cell's own undelivered.csv
# (never replaced), per addendum 2's own instruction. run_fixed_manifest.py
# takes --code-root (same mechanism as T30_scripts/run_avg_arm.py) instead of
# a chdir-into-DRIVER_DIR, so no `cd` is needed here.
#
# Two separate submissions of this SAME script, one per LAMBDA value, each
# --array=0-23 (task doc Design line 13: "one array per scenario"), e.g.:
#   sbatch --job-name=t29_partial --export=ALL,LAMBDA=0.5 --nice=100 t29_array.sh
#   sbatch --job-name=t29_revert  --export=ALL,LAMBDA=0.0 --nice=100 t29_array.sh
# --nice=100 is passed at submit time (Phase B), not embedded here, "so T21's
# arrays run first" (task doc Design line 21) -- same reason --dependency is
# passed at submit time rather than hardcoded (T21/T26 precedent: t21_array.sh
# and t26_job.sh headers carry no --dependency either). Addendum 2: this array
# must also wait on T21's own Step-8 array (JobID 1328422), since it reads
# that array's own per-cell cell_manifest.csv as --manifest.
#
# Cell order: same ARCHS x CITIES arrays, same task-index order, as
# impl/T21_scripts/t21_array.sh (itself matching step8_array_v2.sh /
# step9_b_array_full.sh, T27 Q2) -- copied verbatim so cell N here and cell N
# in T21's Step-8 array are the SAME cell (needed so $MANIFEST below points at
# the matching T21 cell).
#
# Warm-up retry (task doc Design line 25/Brief step 2: "same warm-up retry as
# t21_array.sh"): NOT implemented inline, same as t21_array.sh itself -- on
# the published campaign and on T21 this was always a SEPARATE post-hoc pass
# (step9_warmup120_recovery_v2.sh) run AFTER the array completes and specific
# undelivered runs are identified. This array records every undelivered run
# via its own per-task exit code and stdout log, PLUS run_fixed_manifest.py's
# own undelivered.csv per cell; do not fill gaps by hand (task doc Design line
# 25-26 / P0 "undelivered runs listed, never filled").

set -u
# NOTE: deliberately no `set -e`, same reason as t21_array.sh -- this script
# captures the driver's exit code explicitly ($?, see RC= below) and echoes
# it before exiting; `set -e` would abort before that capture/echo ran.

: "${LAMBDA:?LAMBDA env var must be set to 0.5|0.0}"
case "$LAMBDA" in
  0.5|0.0) ;;
  *) echo "ERROR: unknown LAMBDA=$LAMBDA (want 0.5|0.0 -- lambda=1.0/S-Persist is T21's arm, not rerun here)"; exit 2 ;;
esac

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=4   # design: "4 E+ at a time inside a task" (T21 precedent, simulation.py:157-159)

T29_ROOT=/speed-scratch/o_iseri/2J_revision/T29
T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
WRAPPER=$T29_ROOT/T29_scripts/run_fixed_manifest.py

ARCHS=(SingleD SingleD SingleD SingleD SingleD SingleD \
       OtherDwelling OtherDwelling OtherDwelling OtherDwelling OtherDwelling OtherDwelling \
       MidRise MidRise MidRise MidRise MidRise MidRise \
       HighRise HighRise HighRise HighRise HighRise HighRise)
CITIES=(Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A)

ARCH=${ARCHS[$SLURM_ARRAY_TASK_ID]}
CITY=${CITIES[$SLURM_ARRAY_TASK_ID]}
CELL="${ARCH}__${CITY}"

SCHED_DIR=$T29_ROOT/sched_lambda_${LAMBDA}
OUT_DIR=$T29_ROOT/out/lambda_${LAMBDA}/$CELL
MANIFEST=$T21_ROOT/out/step8/$CELL/cell_manifest.csv

mkdir -p "$OUT_DIR" "$T29_ROOT/logs"

echo "=== T29 array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | LAMBDA=$LAMBDA CELL=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"
echo "SCHED_DIR=$SCHED_DIR  OUT_DIR=$OUT_DIR  MANIFEST=$MANIFEST  WRAPPER=$WRAPPER"

if [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
    echo "ERROR: missing staged schedule CSV under $SCHED_DIR -- did t29_stage.sh run first?"
    exit 1
fi
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: missing T21 Step-8 manifest $MANIFEST -- did T21's Step-8 array (1328422) finish?"
    exit 1
fi

"$PYTHON" "$WRAPPER" \
    --archetype "$ARCH" --city "$CITY" \
    --manifest "$MANIFEST" \
    --sim-mode standard \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR" \
    --code-root "$CODE_ROOT"
RC=$?

echo "=== T29 array task $SLURM_ARRAY_TASK_ID (LAMBDA=$LAMBDA/$CELL) exit=$RC ==="
exit $RC
