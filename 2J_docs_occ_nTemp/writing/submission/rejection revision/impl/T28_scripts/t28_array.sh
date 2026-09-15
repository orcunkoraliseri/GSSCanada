#!/bin/bash
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-3%1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --nice=100
#SBATCH --job-name=t28_array
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T28/logs/t28_%x_%A_%a.out

# t28_array.sh -- T28 Phase B array (NOT submitted by this employee; Phase A
# only writes and syntax-checks this script -- 2026-09-15_T28_wp4_n200_montreal.md
# Phase A brief). One array task per Montreal cell, N=200, both years in one run
# per cell -- same command shape as T21's "step8" campaign (t21_array.sh), just
# --n 200 instead of --n 50, and a 4-cell list instead of the full 24.
#
# Design (task doc, "Design" section): --n 200 --seed 42 --sim-mode standard
# --years 2022,2030, for SingleD__Montreal_6A, OtherDwelling__Montreal_6A,
# MidRise__Montreal_6A, HighRise__Montreal_6A (24-cell task ids 3,9,15,21 in the
# full ARCHS x CITIES grid, T27 Q2) -- 4 x 200 x 2 = 1,600 runs total, all 200
# households run every time (no skip option on the driver; the first 50 of each
# cell's draw reproduce T21's Step-8 50, T27 Q1a).
#
# Engine: the SAME run_paired_mc.py -> run_step8_paired_mc() as T21's step8
# campaign. T21's own Brief step 1 already resolved a design-vs-code mismatch:
# run_paired_mc.py has NO --code-root flag (Step8_docs/run_paired_mc.py:35-47);
# BASE_DIR is fixed by the script's own file location instead, so this script
# invokes the copy of run_paired_mc.py already staged at T22/code/repo directly
# (cd into its directory, then run it) -- read-only, T22's directory is never
# written to, matching the Phase A rule "never write into another task's
# directory (read-only use of T21/T22 staged files is fine)".
#
# Inputs: the SAME staged schedule files T21 Step 8 reads (T21/sched_activity/
# BEM_Schedules_2022.csv = Nb-f 2022, BEM_Schedules_2030.csv = T20 main), read
# only -- this script never writes into T21/'s directory either.
#
# --array=0-3%1: 4 tasks (one per Montreal cell), only 1 running at a time, so
# this campaign never exceeds 8 CPUs concurrently (design: "-c 8 ... 8 CPUs at a
# time"). --nice=100 so T21's own arrays (same account, same 32-CPU association
# ceiling) are scheduled ahead of this one whenever both are queued (Brief step
# 2: "so T21's arrays run first when both wait").
#
# Cell order (archetype order, task id -> cell): 0=SingleD, 1=OtherDwelling,
# 2=MidRise, 3=HighRise, all Montreal_6A -- matches the Brief's own "task 0-3 ->
# the four Montreal cells in archetype order".
#
# Warm-up retry (design: "a run that fails warm-up convergence is retried once
# with the 120-day warm-up, as in T21"): NOT implemented inline, same reason as
# t21_array.sh -- on every campaign so far this has been a SEPARATE post-hoc
# pass (Step9_docs/step9_cluster/step9_warmup120_recovery_v2.sh: sed-patches
# "Maximum Number of Warmup Days 25 -> 120" into the already-generated IDF, then
# re-runs only E+ on that one IDF) run AFTER the array finishes and undelivered
# runs are identified from this task's own exit code / log -- a Phase-B
# follow-up, not part of this script. Undelivered runs are never filled by hand
# (design line 26 / Acceptance B0).
#
# The "CELL=$CELL" header line below (not the %x/%A/%a log filename) is what
# t28_check.py uses to map a log file back to its cell -- decoupled from
# SLURM's own array-index-to-filename convention, which t21_check.py's own
# Phase-A note already flagged as unverified against a real run.

set -u
# NOTE: deliberately no `set -e` -- same reasoning as t21_array.sh: this script
# captures the driver's exit code explicitly ($?) and echoes it before exiting;
# `set -e` would abort the script at the failing command, before that echo ran.

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=8   # design: "-c 8", 8 E+ at a time inside a task

T28_ROOT=/speed-scratch/o_iseri/2J_revision/T28
T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
DRIVER=$CODE_ROOT/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
DRIVER_DIR=$(dirname "$DRIVER")

ARCHS=(SingleD OtherDwelling MidRise HighRise)
CITY=Montreal_6A

ARCH=${ARCHS[$SLURM_ARRAY_TASK_ID]}
CELL="${ARCH}__${CITY}"

SCHED_DIR=$T21_ROOT/sched_activity   # read-only: T21's own staged Nb-f 2022 / T20-main 2030 files
OUT_DIR=$T28_ROOT/out/$CELL

mkdir -p "$OUT_DIR" "$T28_ROOT/logs"

echo "=== T28 array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | CELL=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"
echo "SCHED_DIR=$SCHED_DIR  OUT_DIR=$OUT_DIR  DRIVER=$DRIVER"

if [ ! -f "$SCHED_DIR/BEM_Schedules_2022.csv" ] || [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
    echo "ERROR: missing staged schedule CSV(s) under $SCHED_DIR -- did T21's t21_extract_baseline.sh run first?"
    exit 1
fi

cd "$DRIVER_DIR"
"$PYTHON" "$DRIVER" \
    --archetype "$ARCH" --city "$CITY" \
    --n 200 --seed 42 --sim-mode standard --years 2022,2030 \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
RC=$?

echo "=== T28 array task $SLURM_ARRAY_TASK_ID ($CELL) exit=$RC ==="
exit $RC
