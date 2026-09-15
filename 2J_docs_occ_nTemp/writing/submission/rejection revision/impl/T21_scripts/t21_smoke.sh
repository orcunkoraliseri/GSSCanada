#!/bin/bash
#SBATCH --job-name=t21_smoke
#SBATCH --partition=ps
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T21/logs/t21_smoke_%j.out

# t21_smoke.sh -- T21 Phase A step 2/3: 1 cell (SingleD x Montreal_6A), --n 2,
# all three campaigns (step8, step9_activity, step9_baseline), verify the
# drawn household ids match the published manifests and that
# hourly_meters.csv has 8760 rows. Submitted with
# --dependency=afterok:<t21_extract_baseline.sh jobid>.
#
# Same-2-households-regardless-of-n assumption, verified this session
# (local py -3, not on Speed): random.Random(42).sample(list(range(144465)),50)[:2]
# == random.Random(42).sample(list(range(144465)),2) -> [29184, 6556] both ways
# -- CPython's random.sample is prefix-stable across k for this pool size, so
# --n 2 with seed 42 draws the SAME first-2 households as the published --n 50
# campaign for the same cell.
#
# Expected (sample,hh_id) for SingleD__Montreal_6A, seed 42 -- read directly,
# 2026-09-15, local repo (identical across all three published arms):
#   BEM_Setup/SimResults_Step8/campaign_N50/SingleD__Montreal_6A/cell_manifest.csv.new_2022_2030_20260711
#   BEM_Setup/SimResults_Step9/campaign_N50_2022_2030/idfs/SingleD__Montreal_6A/{baseline,activity}/cell_manifest.csv
#   -> sample=1 hh_id=130322 ; sample=2 hh_id=80058 (byte-identical pair in all three files)

set -u

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export ESIM_WORKERS=2

T21_ROOT=/speed-scratch/o_iseri/2J_revision/T21
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
DRIVER=$CODE_ROOT/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py
DRIVER_DIR=$(dirname "$DRIVER")
ARCH=SingleD
CITY=Montreal_6A
CELL="${ARCH}__${CITY}"
EXP_HH1=130322
EXP_HH2=80058

echo "=== T21 smoke | job=${SLURM_JOB_ID} | cell=$CELL ==="
echo "Node: $(hostname)  Date: $(date)"

FAIL=0
for CAMPAIGN in step8 step9_activity step9_baseline; do
    case "$CAMPAIGN" in
      step8)           SCHED_DIR=$T21_ROOT/sched_activity ;;
      step9_activity)  SCHED_DIR=$T21_ROOT/sched_activity ;;
      step9_baseline)  SCHED_DIR=$T21_ROOT/sched_baseline ;;
    esac
    OUT_DIR=$T21_ROOT/smoke_out/$CAMPAIGN/$CELL
    mkdir -p "$OUT_DIR"

    echo "--- STEP START: $CAMPAIGN ---"
    if [ ! -f "$SCHED_DIR/BEM_Schedules_2022.csv" ] || [ ! -f "$SCHED_DIR/BEM_Schedules_2030.csv" ]; then
        echo "--- STEP FAILED: $CAMPAIGN --- missing staged CSV(s) under $SCHED_DIR"
        FAIL=1
        continue
    fi

    cd "$DRIVER_DIR"
    "$PYTHON" "$DRIVER" \
        --archetype "$ARCH" --city "$CITY" \
        --n 2 --seed 42 --sim-mode standard --years 2022,2030 \
        --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR"
    RC=$?
    if [ "$RC" -ne 0 ]; then
        echo "--- STEP FAILED: $CAMPAIGN --- run_paired_mc.py exit=$RC"
        FAIL=1
        continue
    fi

    MANIFEST="$OUT_DIR/cell_manifest.csv"
    if [ ! -f "$MANIFEST" ]; then
        echo "--- STEP FAILED: $CAMPAIGN --- no cell_manifest.csv at $MANIFEST"
        FAIL=1
        continue
    fi
    echo "  cell_manifest.csv (this run):"
    cat "$MANIFEST"

    HH1=$(awk -F',' 'NR==2{print $2}' "$MANIFEST")
    HH2=$(awk -F',' 'NR==3{print $2}' "$MANIFEST")
    if [ "$HH1" = "$EXP_HH1" ] && [ "$HH2" = "$EXP_HH2" ]; then
        echo "  [A2 smoke] PASS: sample1=$HH1 sample2=$HH2 match published manifest"
    else
        echo "  [A2 smoke] FAIL: sample1=$HH1 sample2=$HH2 -- expected $EXP_HH1,$EXP_HH2"
        FAIL=1
    fi

    for YEAR in 2022 2030; do
        for HH in $HH1 $HH2; do
            HM=$(find "$OUT_DIR" -path "*/sample_*_HH${HH}/${YEAR}/hourly_meters.csv" 2>/dev/null | head -1)
            if [ -z "$HM" ]; then
                echo "  [shape] FAIL: no hourly_meters.csv found for HH$HH year=$YEAR"
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
    done
    echo "--- STEP DONE: $CAMPAIGN ---"
done

echo "=== T21 smoke COMPLETE | overall FAIL=$FAIL ==="
exit $FAIL
