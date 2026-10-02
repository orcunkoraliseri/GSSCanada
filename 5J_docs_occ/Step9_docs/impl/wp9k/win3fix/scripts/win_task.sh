#!/bin/bash
#SBATCH -J 5J_9i_win2fix
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH --array=1-38%16
#SBATCH -o /speed-scratch/o_iseri/5J/step9c/win2fix/logs/task_%A_%a.out
# 5J Step 9i writer test on the fixed base _win_2026-10-02: one EnergyPlus run per task, row N of win2fix/manifest.csv. At most 16 at once (16 CPUs).
B=/speed-scratch/o_iseri/5J/step9c
W=$B/win2fix
EP=/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus
PY=/speed-scratch/o_iseri/envs/step4/bin/python
N=${SLURM_ARRAY_TASK_ID:?no task id}
LINE=$(sed -n "$((N+1))p" $W/manifest.csv)
D=$(echo "$LINE" | cut -d, -f2); STEM=$(echo "$LINE" | cut -d, -f3); RID=$(echo "$LINE" | cut -d, -f5)
IDF=$(echo "$LINE" | cut -d, -f6); EPWN=$(echo "$LINE" | cut -d, -f7)
[ -n "$STEM" ] && [ -n "$RID" ] || { echo "manifest row $N empty"; exit 2; }
RUN=$W/runs/${STEM}_$RID
rm -rf "$RUN"; mkdir -p "$RUN" $W/results
[ -s "$B/$IDF" ] || { echo "missing $B/$IDF"; exit 2; }
if [ "$RID" = "O" ]; then
  [ -s $B/test_series/test_presence.csv ] && [ -s $B/test_series/test_appliance.csv ] || { echo "missing test series"; exit 2; }
fi
# gain schedules: every ../../schedules path in the IDF must resolve from the idfs folder
cd "$W/$D/idfs" || exit 2
for f in $(grep -o '\.\./\.\./schedules/[^, ]*\.csv' "$B/$IDF"); do [ -s "$f" ] || { echo "unresolved schedule $f"; exit 2; }; done
# AMENDMENT 3: EnergyPlus (-x) creates an in.idf symlink in the working folder; tasks sharing the idfs folder collided on it
# ("cannot create symlink: File exists", rc 134 in 1 s). Each run gets its own working folder $W/cwd/<stem>_<run>/ whose ../../schedules is $W/schedules too.
CWD=$W/cwd/${STEM}_$RID
rm -rf "$CWD"; mkdir -p "$CWD" && cd "$CWD" || exit 2
for f in $(grep -o '\.\./\.\./schedules/[^, ]*\.csv' "$B/$IDF"); do [ -s "$f" ] || { echo "unresolved schedule from run folder $f"; exit 2; }; done
echo "task=$N stem=$STEM run=$RID host=$(hostname) start=$(date -Iseconds)"
T0=$(date +%s.%N)
"$EP" -w $B/epw/$EPWN -d "$RUN" -x -r "$B/$IDF" > "$RUN/eplus_stdout.txt" 2>&1
RC=$?
T1=$(date +%s.%N)
WALL=$(awk -v a=$T0 -v b=$T1 'BEGIN{printf "%.1f", b-a}')
$PY $W/win_summ.py "$N" "$STEM" "$RID" "$RC" "$WALL" "$B/$IDF" "$RUN" "$W/results/$N.json"
SRC=$?
rm -f "$RUN/eplusout.sql" "$RUN/eplusout.csv" "$RUN/eplusout.eso" "$RUN/eplusout.mtr" "$RUN/eplusmtr.csv"
[ "$RC" -eq 0 ] && [ "$SRC" -eq 0 ] && exit 0 || exit 1
