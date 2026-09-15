#!/bin/bash
#SBATCH --job-name=t29_smoke
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T29/logs/t29_smoke_%j.out

# t29_smoke.sh -- one-cell smoke of run_fixed_manifest.py (manager addendum 2,
# "Smoke first, same turn"). Cell SingleD__Montreal_6A, LAMBDA=0.0 (S-Revert),
# a hardcoded 2-row manifest (t29_smoke_manifest.csv: sample 1->130228,
# sample 2->79252 -- T21's own smoke draw, T21 doc diagnosis 1328414 Q3a).
# This smoke needs NO T21 Step-8 output (the manifest is hand-built, not read
# from T21/out/step8/) -- only the staged S-Revert scenario schedule file
# (t29_stage.sh's own output). Output goes to a DEDICATED smoke_out/ tree, not
# T29/out/lambda_0.0/SingleD__Montreal_6A/ (that path is the real 48-task
# array's own output dir for this same cell -- task-index 3 -- so the smoke
# must not write there).

set -u

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=2

T29_ROOT=/speed-scratch/o_iseri/2J_revision/T29
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
WRAPPER=$T29_ROOT/T29_scripts/run_fixed_manifest.py
MANIFEST=$T29_ROOT/T29_scripts/t29_smoke_manifest.csv

ARCH=SingleD
CITY=Montreal_6A
CELL="${ARCH}__${CITY}"
SCHED_DIR=$T29_ROOT/sched_lambda_0.0
OUT_DIR=$T29_ROOT/smoke_out/lambda_0.0/$CELL
EXP_HH1=130228
EXP_HH2=79252

mkdir -p "$OUT_DIR" "$T29_ROOT/logs"

echo "=== T29 smoke | job=${SLURM_JOB_ID} | CELL=$CELL LAMBDA=0.0 (S-Revert) ==="
echo "Node: $(hostname)  Date: $(date)"
echo "SCHED_DIR=$SCHED_DIR  OUT_DIR=$OUT_DIR  MANIFEST=$MANIFEST"

FAIL=0

if [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
    echo "--- STEP FAILED --- missing staged S-Revert schedule CSV under $SCHED_DIR -- did the staging job run first?"
    exit 1
fi
if [ ! -f "$MANIFEST" ]; then
    echo "--- STEP FAILED --- missing smoke manifest $MANIFEST"
    exit 1
fi

echo "  smoke manifest (input):"
cat "$MANIFEST"

"$PYTHON" "$WRAPPER" \
    --archetype "$ARCH" --city "$CITY" \
    --manifest "$MANIFEST" \
    --sim-mode standard \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR" \
    --code-root "$CODE_ROOT"
RC=$?
if [ "$RC" -ne 0 ]; then
    echo "--- STEP FAILED --- run_fixed_manifest.py exit=$RC"
    FAIL=1
fi

OUT_MANIFEST="$OUT_DIR/cell_manifest.csv"
if [ -f "$OUT_MANIFEST" ]; then
    echo "  cell_manifest.csv (this run's output):"
    cat "$OUT_MANIFEST"
    HH1=$(awk -F',' 'NR==2{print $2}' "$OUT_MANIFEST")
    HH2=$(awk -F',' 'NR==3{print $2}' "$OUT_MANIFEST")
    if [ "$HH1" = "$EXP_HH1" ] && [ "$HH2" = "$EXP_HH2" ]; then
        echo "  [pairing] PASS: sample1=$HH1 sample2=$HH2 match the fixed manifest, in order"
    else
        echo "  [pairing] FAIL: sample1=$HH1 sample2=$HH2 -- expected $EXP_HH1,$EXP_HH2"
        FAIL=1
    fi
else
    echo "  [pairing] FAIL: no cell_manifest.csv at $OUT_MANIFEST"
    FAIL=1
fi

UNDEL="$OUT_DIR/undelivered.csv"
if [ -f "$UNDEL" ]; then
    N_UNDEL=$(( $(wc -l < "$UNDEL") - 1 ))
    echo "  undelivered.csv rows (excl header): $N_UNDEL (want 0)"
    if [ "$N_UNDEL" -ne 0 ]; then
        echo "  [undelivered] FAIL: expected 0 undelivered households, got $N_UNDEL"
        cat "$UNDEL"
        FAIL=1
    else
        echo "  [undelivered] PASS: 0 undelivered"
    fi
else
    echo "  [undelivered] FAIL: no undelivered.csv written at $UNDEL"
    FAIL=1
fi

for HH in $EXP_HH1 $EXP_HH2; do
    HM=$(find "$OUT_DIR" -path "*/sample_*_HH${HH}/2030/hourly_meters.csv" 2>/dev/null | head -1)
    if [ -z "$HM" ]; then
        echo "  [shape] FAIL: no hourly_meters.csv found for HH$HH year=2030"
        FAIL=1
        continue
    fi
    NROWS=$(( $(wc -l < "$HM") - 1 ))
    if [ "$NROWS" -eq 8760 ]; then
        echo "  [shape] PASS: $HM has 8760 data rows"
    else
        echo "  [shape] FAIL: $HM has $NROWS data rows, expected 8760"
        FAIL=1
    fi
done

echo "=== T29 smoke COMPLETE | overall FAIL=$FAIL ==="
exit $FAIL
