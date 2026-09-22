#!/bin/bash
#SBATCH --job-name=wp11_selftest
#SBATCH --account=chachemv
#SBATCH -p ps
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/1J_rerun/logs/wp11_selftest_%j.out

# WP11 item 7: cluster selftests. (a) wp11_stoprule.py --mode selftest (pure python,
# synthetic numbers, no cluster files -- also runnable locally with `py`, already run
# and PASSED locally before this job was written -- see task doc Verified). (b)
# wp11_extract.py --mode selftest against ONE already-finished real task directory
# (stage4/default/draw_1/NUS_RC1, --draw-start 1 --n-draws 1): E2 against its own
# real aggregated_eui.csv must PASS, then E2 against a temp COPY with one mean
# perturbed by 0.01 must FAIL (seen failing first). --no-cleanup is passed as a
# defensive guard so nothing under default/ can ever be touched by this job, even
# though --mode selftest never calls the cleanup routine itself.
#
# This is one of the two jobs the employee is authorised to submit directly (the
# other is wp11_swap_probe.sh); the manager submits the draw arrays and scorers
# later, after reading this selftest plus Gate 4, workers-check and probe all PASS.
#
# Task doc: 1J_docs_occ/IMP/impl/2026-09-22_WP11_stage4d_draws.md, item 7.

WP11=/speed-scratch/o_iseri/1J_rerun/stage4/wp11
VENV=/speed-scratch/o_iseri/GSSCanada/venv
DEFAULT_ROOT=/speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1

source "$VENV/bin/activate"

echo "=== (a) wp11_stoprule.py --mode selftest ==="
python "$WP11/wp11_stoprule.py" --mode selftest
STOPRULE_EXIT=$?
echo "wp11_stoprule.py --mode selftest exit code: $STOPRULE_EXIT"

echo ""
echo "=== (b) wp11_extract.py --mode selftest (real fixture: default/draw_1/NUS_RC1, --no-cleanup) ==="
python "$WP11/wp11_extract.py" --mode selftest \
    --nu NUS_RC1 --task-dir "$DEFAULT_ROOT" --draw-start 1 --n-draws 1 --no-cleanup
EXTRACT_EXIT=$?
echo "wp11_extract.py --mode selftest exit code: $EXTRACT_EXIT"

echo ""
if [ "$STOPRULE_EXIT" -eq 0 ] && [ "$EXTRACT_EXIT" -eq 0 ]; then
  echo "WP11 SELFTEST JOB: PASS -- both selftests exited 0"
  FINAL_EXIT=0
else
  echo "WP11 SELFTEST JOB: FAIL -- stoprule_exit=$STOPRULE_EXIT extract_exit=$EXTRACT_EXIT"
  FINAL_EXIT=1
fi
exit $FINAL_EXIT
