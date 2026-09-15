#!/bin/bash
#SBATCH --job-name=t31_smoke
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T31/logs/t31_smoke_%j.out

# t31_smoke.sh -- T31 Phase A step 4: builder + identity smoke (E0/E1/E2).
# Task doc: 2026-09-15_T31_wp7_existing_stock_envelope.md, Phase A brief.
#
# Runs 2 households of SingleD__Montreal_6A, year 2022 only, in THREE trees,
# each a T31-local `cp -r` copy of T22's staged repo (T22/code/repo is only
# ever READ, never written to -- "never write into another task's
# directory"):
#   unmodified      -- untouched copy (only run_paired_mc.py added, see
#                       FINDING below), the reference for E0/E1 comparisons.
#   current         -- same copy, SingleD IDF replaced by
#                       make_envelope_variant.py's output using
#                       envelope_current.json (all targets null -> E0
#                       identity: this variant IDF must be byte-identical
#                       to the source).
#   mechanism_test  -- same, but envelope_mechanism_test.json (wall/ceiling
#                       RSI halved, window U 2.8, k=3 on ZoneLeak_* ELA --
#                       LABELLED MECHANISM TEST, NEVER a reported WP7 value;
#                       only checks that heating energy rises, i.e. E1).
#
# FINDING (T31 phase A, found live on Speed this session): T22's own staged
# repo (per 2026-09-15_T22_wp3_static_arm_full_run.md Ledger Step 2) only
# copied `run_bem.py` + `eSim_bem_utils_2J/*.py` into
# T22/code/repo/2J_docs_occ_nTemp/Step8_docs/ -- it never staged
# `run_paired_mc.py` itself, even though T21's own smoke script
# (T21_scripts/t21_smoke.sh) assumes that file is there and calls it at that
# exact path. Confirmed by `ls` on Speed: `run_paired_mc.py` is NOT present
# under T22/code/repo/2J_docs_occ_nTemp/Step8_docs/ (only `run_bem.py`,
# `0_BEM_Setup`, `eSim_bem_utils_2J`, `__pycache__`). `run_paired_mc.py`
# itself only imports `eSim_bem_utils_2J.main` and `run_bem`
# (`run_paired_mc.py:25-27`, both already staged) -- no other new
# dependency. This script therefore stages ONE extra file
# (T31_scripts/run_paired_mc.py, an unmodified copy of the local
# Step8_docs/run_paired_mc.py) and copies it into each of its own three
# T31-local tree copies below. Not fixed inside T22/ itself (out of scope,
# read-only) -- flagged for the T21 collector too, since T21's own
# 1328378/1328380 chain will hit the same missing file once it runs.
#
# --sched-dir points at T17's own staged schedule tree, read-only (proven
# working by T22's full 24-cell run, per 2026-09-15_T22_wp3_static_arm_full_run.md
# Decisions: "--sched-dir pointed at T17's staged tree read-only") -- this
# smoke does not depend on T21's currently-blocked T18/T20 chain at all.
#
# E2 (current model's implied ACH50) is NOT computed here -- it is a pure
# arithmetic readout from the IDF's own AirflowNetwork objects, already
# computed and written under this task doc's Verified section (no cluster
# job needed for E2).

set -u
# Deliberately no `set -e`: this script must keep going through all three
# trees and the summarizer even if one leg fails, so every result gets
# reported (same reasoning as T21's t21_array.sh / t21_smoke.sh).

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=2

T31_ROOT=/speed-scratch/o_iseri/2J_revision/T31
T22_CODE_ROOT=/speed-scratch/o_iseri/2J_revision/T22/code/repo
SCHED_DIR=/speed-scratch/o_iseri/2J_revision/T17/code/sched
BUILDER=$T31_ROOT/T31_scripts/make_envelope_variant.py
SUMMARIZER=$T31_ROOT/T31_scripts/t31_summarize_smoke.py
RUN_PAIRED_MC_SRC=$T31_ROOT/T31_scripts/run_paired_mc.py

DRIVER_REL=2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
SINGLED_IDF_REL=2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf
ARCH=SingleD
CITY=Montreal_6A

mkdir -p "$T31_ROOT/smoke/out" "$T31_ROOT/logs" "$T31_ROOT/code"

echo "=== T31 smoke | job=${SLURM_JOB_ID} | cell=${ARCH}__${CITY} | year=2022 only ==="
echo "Node: $(hostname)  Date: $(date)"

FAIL=0

if [ ! -f "$SCHED_DIR/BEM_Schedules_2022.csv" ]; then
    echo "FATAL: missing $SCHED_DIR/BEM_Schedules_2022.csv -- cannot run any leg"
    exit 1
fi
if [ ! -f "$RUN_PAIRED_MC_SRC" ]; then
    echo "FATAL: missing $RUN_PAIRED_MC_SRC -- see FINDING in this script's header (T22 never staged it)"
    exit 1
fi

# build_tree LABEL -> makes T31/code/repo_<label> as a fresh cp -r of T22's
# staged repo (read-only source) plus the one missing driver file, unless it
# already exists from a prior run of this script.
build_tree () {
    LABEL=$1
    TREE_ROOT=$T31_ROOT/code/repo_$LABEL
    if [ ! -d "$TREE_ROOT" ]; then
        cp -r "$T22_CODE_ROOT" "$TREE_ROOT"
    fi
    cp "$RUN_PAIRED_MC_SRC" "$TREE_ROOT/$DRIVER_REL"
    echo "$TREE_ROOT"
}

run_variant () {
    LABEL=$1
    TREE_ROOT=$2
    OUT_DIR=$T31_ROOT/smoke/out/$LABEL
    mkdir -p "$OUT_DIR"
    DRIVER=$TREE_ROOT/$DRIVER_REL
    DRIVER_DIR=$(dirname "$DRIVER")
    if [ ! -f "$DRIVER" ]; then
        echo "  [$LABEL] FAIL: driver not found at $DRIVER"
        FAIL=1
        return
    fi
    cd "$DRIVER_DIR"
    "$PYTHON" "$DRIVER" \
        --archetype "$ARCH" --city "$CITY" \
        --n 2 --seed 42 --sim-mode standard --years 2022 \
        --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
    RC=$?
    echo "  [$LABEL] driver exit=$RC (output under $OUT_DIR)"
    if [ "$RC" -ne 0 ]; then
        FAIL=1
    fi
}

echo "--- Tree 1: unmodified (T31-local copy of T22/code/repo, SingleD IDF untouched) ---"
UNMOD_ROOT=$(build_tree unmodified)
run_variant unmodified "$UNMOD_ROOT"

echo "--- Tree 2: current-values variant (envelope_current.json, E0) ---"
CUR_ROOT=$(build_tree current)
"$PYTHON" "$BUILDER" \
    --source "$T22_CODE_ROOT/$SINGLED_IDF_REL" \
    --targets "$T31_ROOT/T31_scripts/envelope_current.json" \
    --out-idf "$CUR_ROOT/$SINGLED_IDF_REL" \
    --out-log "$T31_ROOT/smoke/changelog_current.json"
BRC=$?
if [ "$BRC" -ne 0 ]; then
    echo "  [current] FAIL: make_envelope_variant.py exit=$BRC"
    FAIL=1
fi
run_variant current "$CUR_ROOT"

echo "--- E0 text-diff check (current-values variant vs source) ---"
if diff -q "$T22_CODE_ROOT/$SINGLED_IDF_REL" "$CUR_ROOT/$SINGLED_IDF_REL" > /dev/null; then
    echo "  [E0 text-diff] PASS: byte-identical (comments included) to the unmodified source IDF"
else
    echo "  [E0 text-diff] FAIL: current-values variant differs from source -- see diff below"
    diff "$T22_CODE_ROOT/$SINGLED_IDF_REL" "$CUR_ROOT/$SINGLED_IDF_REL"
    FAIL=1
fi

echo "--- Tree 3: mechanism-test variant (envelope_mechanism_test.json, E1 -- NEVER reported) ---"
MECH_ROOT=$(build_tree mechanism_test)
"$PYTHON" "$BUILDER" \
    --source "$T22_CODE_ROOT/$SINGLED_IDF_REL" \
    --targets "$T31_ROOT/T31_scripts/envelope_mechanism_test.json" \
    --out-idf "$MECH_ROOT/$SINGLED_IDF_REL" \
    --out-log "$T31_ROOT/smoke/changelog_mechanism_test.json"
BRC=$?
if [ "$BRC" -ne 0 ]; then
    echo "  [mechanism_test] FAIL: make_envelope_variant.py exit=$BRC"
    FAIL=1
fi
run_variant mechanism_test "$MECH_ROOT"

echo "--- Summarizing annual facility/heating kWh (E0/E1 verdicts) ---"
"$PYTHON" "$SUMMARIZER" --smoke-root "$T31_ROOT/smoke" --out "$T31_ROOT/smoke/e0_e1.csv"
SRC=$?
if [ "$SRC" -ne 0 ]; then
    FAIL=1
fi

echo "=== T31 smoke COMPLETE | overall FAIL=$FAIL ==="
exit $FAIL
