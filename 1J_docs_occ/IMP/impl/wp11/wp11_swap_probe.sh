#!/bin/bash
#SBATCH --job-name=wp11_swap_probe
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp11_swap_probe_%j.out

# WP11 item 2: back up the staged main.py, swap in main_wp11.py (additive draw-start
# patch only), sanity-check the swap with two grep counts, then run the no-EnergyPlus
# probe (wp11_probe.py). Chained --dependency=afterany on Gate 4 real (1342160) and
# the workers check (1342163) so no job that is currently reading main.py sees it
# change underneath it.
# Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 2.

CODE=/speed-scratch/o_iseri/1J_rerun/code
WP11=/speed-scratch/o_iseri/1J_rerun/stage4/wp11
VENV=/speed-scratch/o_iseri/GSSCanada/venv
EP_DIR=/speed-scratch/o_iseri/EnergyPlus/EnergyPlus-24.2.0-94a887817b-Linux-CentOS7.9.2009-x86_64

echo "=== (a) Backing up staged main.py ==="
cp "$CODE/eSim_bem_utils/main.py" "$CODE/eSim_bem_utils/main.py.pre_WP11"
if [ ! -s "$CODE/eSim_bem_utils/main.py.pre_WP11" ]; then
  echo "ERROR: main.py.pre_WP11 is missing or empty after backup -- stopping before swap."
  exit 3
fi
echo "Backup OK: main.py.pre_WP11 non-empty."

PRE_GUARD_COUNT=$(grep -c "WP10 GUARD" "$CODE/eSim_bem_utils/main.py.pre_WP11")
echo "Pre-swap WP10 GUARD count: $PRE_GUARD_COUNT"

echo "=== (b) Swapping in main_wp11.py ==="
cp "$WP11/main_wp11.py" "$CODE/eSim_bem_utils/main.py"

echo "=== (c) Post-swap sanity checks ==="
DRAW_START_COUNT=$(grep -c "WP11 DRAW START" "$CODE/eSim_bem_utils/main.py")
POST_GUARD_COUNT=$(grep -c "WP10 GUARD" "$CODE/eSim_bem_utils/main.py")
echo "Post-swap WP11 DRAW START count: $DRAW_START_COUNT (must be 1)"
echo "Post-swap WP10 GUARD count: $POST_GUARD_COUNT (must equal pre-swap count $PRE_GUARD_COUNT)"

if [ "$DRAW_START_COUNT" -ne 1 ]; then
  echo "SWAP CHECK: FAIL -- WP11 DRAW START count is $DRAW_START_COUNT, expected 1"
  exit 3
fi
if [ "$POST_GUARD_COUNT" -ne "$PRE_GUARD_COUNT" ]; then
  echo "SWAP CHECK: FAIL -- WP10 GUARD count changed ($PRE_GUARD_COUNT -> $POST_GUARD_COUNT)"
  exit 3
fi
echo "SWAP CHECK: PASS"

echo "=== (d) Running wp11_probe.py (no EnergyPlus) ==="
source "$VENV/bin/activate"
export ENERGYPLUS_DIR="$EP_DIR"

python "$WP11/wp11_probe.py"
EXIT_CODE=$?
echo "Done: wp11_swap_probe (exit code: $EXIT_CODE)"
exit $EXIT_CODE
