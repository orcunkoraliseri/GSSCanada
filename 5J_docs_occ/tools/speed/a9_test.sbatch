#!/bin/bash
#SBATCH -J 5J_9g_test
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/modelA/store_test/logs/test_%j.out
# 5J Step 9g test job. Submitted with --dependency=afterany:1407093 (the writer aggregator). Never waited for.
# Step 1: the writer's test runs deleted their hourly csv after summarising, so the D and O runs are RE-RUN here from the writer's IDFs
#         (read only) into our own folder, 4 at a time, keeping eplusout.csv. Step 2: python a9_store.py test (extract, store, checks).
B=/speed-scratch/o_iseri/5J/modelA/store_test
S=/speed-scratch/o_iseri/5J/step9c
W=$S/win
export EP=/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export B S W
export PYTHONDONTWRITEBYTECODE=1
mkdir -p $B/runs $B/logs
awk -F, 'NR>1 && ($5=="D" || $5=="O") {print $2, $3, $5, $7}' $W/manifest.csv > $B/runs/list.txt
echo "runs to do: $(wc -l < $B/runs/list.txt)  start $(date -Iseconds) host $(hostname)"
runone() {
  D=$1; STEM=$2; R=$3; EPWN=$4
  RUN=$B/runs/${STEM}_$R
  rm -rf "$RUN"; mkdir -p "$RUN"
  cd "$W/$D/idfs" || { echo "no idfs folder $D"; return 1; }
  T0=$(date +%s)
  "$EP" -w "$S/epw/$EPWN" -d "$RUN" -x -r "$W/$D/idfs/${STEM}_$R.idf" > "$RUN/eplus_stdout.txt" 2>&1
  RC=$?
  echo "run ${STEM}_$R rc=$RC wall_s=$(( $(date +%s) - T0 )) end=$(tail -c 120 $RUN/eplusout.end 2>/dev/null | tr '\n' ' ')"
}
export -f runone
xargs -P 4 -L 1 bash -c 'runone $0 $1 $2 $3' < $B/runs/list.txt
echo "energyplus part done $(date -Iseconds)"
cd $B/code
$PY a9_store.py test $B $W $S/epw
echo "a9_store test exit code $?"
