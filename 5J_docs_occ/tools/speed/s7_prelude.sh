# sourced by every Step 7 job (Spain only; writes only under /speed-scratch/o_iseri/5J/district/)
PY=/speed-scratch/o_iseri/envs/step4/bin/python
D=/speed-scratch/o_iseri/5J/district
C=$D/code
export PYTHONDONTWRITEBYTECODE=1
cd $C || exit 2
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none}"
for f in $C/s7_*.py; do $PY -c "import sys; compile(open('$f').read(), '$f', 'exec')" && echo "SYNTAX_OK $(basename $f) $(md5sum < $f | cut -d' ' -f1)" || exit 3; done
