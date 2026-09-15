#!/bin/bash
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --array=0-23
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T21/logs/t21_%x_%A_%a.out

# t21_array.sh -- T21 Phase B array (NOT submitted by this employee; Phase A
# only writes and syntax-checks this script). One array task per cell for a
# given CAMPAIGN. CAMPAIGN is passed at submit time, e.g.:
#   sbatch --job-name=t21_step8          --export=ALL,CAMPAIGN=step8          t21_array.sh
#   sbatch --job-name=t21_step9_activity --export=ALL,CAMPAIGN=step9_activity t21_array.sh
#   sbatch --job-name=t21_step9_baseline --export=ALL,CAMPAIGN=step9_baseline t21_array.sh
# (Design: "One array task per (campaign, cell)" -- 3 separate submissions of
# this SAME script, one per CAMPAIGN value, each --array=0-23.)
#
# Engine: the SAME run_paired_mc.py -> run_step8_paired_mc() as the published
# campaign_N50 (T16 Q1/Q4). Code tree reused READ-ONLY from T22's already
# staged, all-24-cell tree (T22/code/repo -- never written to, per the task
# doc's "Never write into T17/T18/T19/T20/T22/T26 dirs").
#
# NOTE on the task doc's own wording (2026-09-15_T21_wp1_step8_step9_rerun.md
# Brief step 2: "reuse T22's staged T22/code/repo read-only via --code-root"):
# run_paired_mc.py has NO --code-root argument -- its only args are
# --archetype --city --n --seed --sim-mode --years --output-dir --sched-dir
# (Step8_docs/run_paired_mc.py:35-47, read in full this session). The code
# tree is instead selected by WHERE the script physically sits: BASE_DIR
# resolves as the 4th dirname() up from eSim_bem_utils_2J/main.py's own path
# (2026-09-15_T17_speed_reproduces_local_campaign.md Verified, "Path-resolution
# constraint for staging"; not CLI-overridable). This script therefore invokes
# the copy of run_paired_mc.py already staged at T22/code/repo directly (cd
# into its directory, then run it) instead of passing a --code-root flag that
# does not exist on this script -- recorded as a design-vs-code mismatch, not
# worked around silently.
#
# Cell order: same ARCHS x CITIES arrays, same task-index order, as
# Step9_docs/step9_cluster/step9_b_array_full.sh:31-38 (== step8_array_v2.sh
# order; cross-checked in 2026-09-15_T22_wp3_static_arm_full_run.md Decisions).
#
# Warm-up retry (design: "a run that fails warm-up convergence is retried once
# with the 120-day warm-up", T25 Q6 trap 4): NOT implemented inline in this
# script. On the published campaign this was a SEPARATE post-hoc pass
# (Step9_docs/step9_cluster/step9_warmup120_recovery_v2.sh: sed-patches
# "Maximum Number of Warmup Days 25 -> 120" into the already-generated
# Scenario_<year>.idf, then re-runs only E+ on that one IDF) run AFTER this
# array completes and undelivered runs are identified -- a Phase-B follow-up,
# not part of this script. This array records every undelivered run via its
# own per-task exit code and stdout log; do not fill gaps by hand (design
# line 26).

set -u
# NOTE: deliberately no `set -e` -- this script captures the driver's exit
# code explicitly ($?, see RC= below) and echoes it before exiting, matching
# T18's t18_chain.sh pattern; `set -e` would abort the script at the failing
# command, before the RC capture / summary echo ever ran.

: "${CAMPAIGN:?CAMPAIGN env var must be set to step8|step9_activity|step9_baseline}"

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=4   # design: "4 E+ at a time inside a task" (simulation.py:157-159)

T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
DRIVER=$CODE_ROOT/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
DRIVER_DIR=$(dirname "$DRIVER")

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

case "$CAMPAIGN" in
  step8)
    SCHED_DIR=$T21_ROOT/sched_activity
    OUT_DIR=$T21_ROOT/out/step8/$CELL
    ;;
  step9_activity)
    SCHED_DIR=$T21_ROOT/sched_activity
    OUT_DIR=$T21_ROOT/out/step9_activity/$CELL
    ;;
  step9_baseline)
    SCHED_DIR=$T21_ROOT/sched_baseline
    OUT_DIR=$T21_ROOT/out/step9_baseline/$CELL
    ;;
  *)
    echo "ERROR: unknown CAMPAIGN=$CAMPAIGN (want step8|step9_activity|step9_baseline)"
    exit 2
    ;;
esac

mkdir -p "$OUT_DIR" "$T21_ROOT/logs"

echo "=== T21 array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | CAMPAIGN=$CAMPAIGN CELL=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"
echo "SCHED_DIR=$SCHED_DIR  OUT_DIR=$OUT_DIR  DRIVER=$DRIVER"

if [ ! -f "$SCHED_DIR/BEM_Schedules_2022.csv" ] || [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
    echo "ERROR: missing staged schedule CSV(s) under $SCHED_DIR -- did t21_extract_baseline.sh run first?"
    exit 1
fi

cd "$DRIVER_DIR"
"$PYTHON" "$DRIVER" \
    --archetype "$ARCH" --city "$CITY" \
    --n 50 --seed 42 --sim-mode standard --years 2022,2030 \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
RC=$?

echo "=== T21 array task $SLURM_ARRAY_TASK_ID ($CAMPAIGN/$CELL) exit=$RC ==="
exit $RC
