#!/encs/bin/bash
#SBATCH --job-name=t30_smoke
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_smoke_%j.out
#SBATCH --error=/speed-scratch/o_iseri/2J_revision/T30/logs/t30_smoke_%j.err

# T30 smoke: WP3 average-profile arm (one average survey profile per cell/year).
# Tests the MECHANISM, not the numbers: cell=SingleD__Montreal_6A, year=2022,
# n=2, seed=42.
#
# Phase-B re-smoke (manager addendum, "V1 decided, phase B go", 2026-09-15):
# sched-dir re-pointed to T21/sched_activity, which now holds BOTH the Nb-f
# 2022 file and the T20 2030 file (both required -- run_avg_arm.py now loads
# both years to build the 2022-and-2030 intersection pool before sampling,
# even though this smoke only simulates year 2022). Expected draw on this
# paired pool for SingleD__Montreal_6A: households 130228 and 79252 (T21
# diagnosis 1328414, Q3a). CODE_ROOT is the shared driver tree (T21 Ledger,
# "driver path fix").
#
# Stage 1: --check-only (fast, no EnergyPlus) -- prints the paired pool size,
# the averaged Weekday/Weekend occupancy profile, and the V2 identity number.
# Stage 2: full run, n=2 -- produces 2 real E+ runs (8760-row hourly_meters.csv
# each) plus a READBACK of both households' injected Occ_Sch/design levels for
# a later collector to check V0/V2/V3/V4-style acceptance against.
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
CODE_ROOT=/speed-scratch/o_iseri/2J_revision/code_step8/repo
SCHED_DIR=/speed-scratch/o_iseri/2J_revision/T21/sched_activity
OUT_DIR=/speed-scratch/o_iseri/2J_revision/T30/out
SCRIPT_DIR=/speed-scratch/o_iseri/2J_revision/T30/T30_scripts
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers
IDD=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$IDD"

mkdir -p "$OUT_DIR" /speed-scratch/o_iseri/2J_revision/T30/logs

echo "=== T30 smoke | Start: $(date) ==="
echo "CODE_ROOT=$CODE_ROOT (shared driver tree, read-only reuse)"
echo "SCHED_DIR=$SCHED_DIR (T21/sched_activity: Nb-f 2022 + T20 2030, paired-pool draw)"

# Pre-flight (never on the login node -- this runs on the compute node).
$PYTHON -c "import eppy" 2>/dev/null || { echo "ERROR: eppy missing in $PYTHON"; exit 1; }
[ -f "$IDD" ]                    || { echo "ERROR: Energy+.idd not found at $IDD"; exit 1; }
[ -x "$WRAPPER_DIR/energyplus" ] || { echo "ERROR: energyplus wrapper not executable"; exit 1; }
[ -f "$SCHED_DIR/BEM_Schedules_2022.csv" ] || { echo "ERROR: missing $SCHED_DIR/BEM_Schedules_2022.csv"; exit 1; }
[ -f "$SCHED_DIR/BEM_Schedules_2030.csv" ] || { echo "ERROR: missing $SCHED_DIR/BEM_Schedules_2030.csv (needed for the paired pool even though this smoke only simulates 2022)"; exit 1; }

echo ""
echo "=== Stage 1: --check-only (SingleD x Montreal_6A, year=2022, n=2, seed=42) ==="
$PYTHON "$SCRIPT_DIR/run_avg_arm.py" --check-only \
    --archetype SingleD --city Montreal_6A --year 2022 --n 2 --seed 42 \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR" --code-root "$CODE_ROOT"
CHECK_STATUS=$?
echo "check-only exit: $CHECK_STATUS"
if [ "$CHECK_STATUS" -ne 0 ]; then
    echo "T30 SMOKE FAILED at check-only stage (exit $CHECK_STATUS)"
    exit "$CHECK_STATUS"
fi

echo ""
echo "=== Stage 2: full run (SingleD x Montreal_6A, year=2022, n=2, seed=42) ==="
$PYTHON "$SCRIPT_DIR/run_avg_arm.py" \
    --archetype SingleD --city Montreal_6A --year 2022 --n 2 --seed 42 \
    --sched-dir "$SCHED_DIR" --output-dir "$OUT_DIR" --code-root "$CODE_ROOT"
RUN_STATUS=$?
echo "full run exit: $RUN_STATUS"

echo "=== T30 smoke | End: $(date)  overall_exit=$RUN_STATUS ==="
exit "$RUN_STATUS"
