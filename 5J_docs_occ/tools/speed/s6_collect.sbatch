#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -J s6_collect
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_collect_%j.out
# Collect job: reads only the printed score files of the one scoring job (arg 1 = its JobID). Runs after it whatever its exit (afterany).
export PYTHONDONTWRITEBYTECODE=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
JOB=$1
echo "COLLECT_JOB $SLURM_JOB_ID scoring_job=$JOB start $(date -Iseconds) script_md5 $(md5sum < /speed-scratch/o_iseri/5J/test/code/s6_collect.py | cut -d' ' -f1)"
$PY -u /speed-scratch/o_iseri/5J/test/code/s6_collect.py --score-dir /speed-scratch/o_iseri/5J/test/score --out /speed-scratch/o_iseri/5J/test/score_collect --job $JOB
RC=$?
echo "s6_collect EXIT $RC end=$(date -Iseconds)"
exit $RC
