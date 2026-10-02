#!/bin/bash
#SBATCH -J 5J_9j_win3
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o /speed-scratch/o_iseri/5J/step9c/win3/logs/task_%j.out
# 5J Step 9j item 5: 4 buildings, base _win_2026-10-03, one EnergyPlus run each (4 at once = 4 CPUs), each in its OWN run and cwd folder.
# IDF = byte copy of the delivered file + two output-only lines appended (EnvelopeSummary table, CommaAndHTML style); nothing else changed.
W=/speed-scratch/o_iseri/5J/step9c/win3
EP=/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/fleets
mkdir -p $W/logs $W/runs $W/cwd $W/schedules $W/idfs
echo "job=$SLURM_JOB_ID host=$(hostname) start=$(date -Iseconds)"
run_one() {
  D=$1; STEM=$2; EPWF=$3
  FL=$F/EU11_${D}_win_2026-10-03
  SRC=$FL/idfs/$STEM.idf
  [ -s "$SRC" ] || { echo "missing $SRC"; return 2; }
  md5sum "$SRC" > $W/idfs/$STEM.src.md5
  cp "$SRC" $W/idfs/$STEM.idf
  printf '\nOutput:Table:SummaryReports,\n  EnvelopeSummary;\n\nOutputControl:Table:Style,\n  CommaAndHTML;\n' >> $W/idfs/$STEM.idf
  rm -f $W/schedules/$STEM; ln -s $FL/schedules/$STEM $W/schedules/$STEM
  CWD=$W/cwd/$STEM; RUN=$W/runs/$STEM
  rm -rf "$CWD" "$RUN"; mkdir -p "$CWD" "$RUN"; cd "$CWD" || return 2
  for f in $(grep -o '\.\./\.\./schedules/[^, ]*\.csv' $W/idfs/$STEM.idf); do [ -s "$f" ] || { echo "unresolved schedule $f"; return 2; }; done
  T0=$(date +%s)
  "$EP" -w /speed-scratch/o_iseri/5J/step9c/epw/$EPWF -d "$RUN" -x -r $W/idfs/$STEM.idf > "$RUN/eplus_stdout.txt" 2>&1
  echo "stem=$STEM rc=$? wall_s=$(( $(date +%s) - T0 ))"
}
run_one ES-MAD-BERRUGUETE 0275c53572b2ff9f es_madrid_2009_2010_y2010.epw &
run_one ES-MAD-BERRUGUETE 7307694dddf93fb6 es_madrid_2009_2010_y2010.epw &
run_one IT-BOL-GALVANI2 504fa19567bbc2b7 it_bologna_2013_2014_y2014.epw &
run_one IT-BOL-GALVANI2 b3f8d90890ff6314 it_bologna_2013_2014_y2014.epw &
wait
$PY $W/win3_read.py $W > $W/logs/read_$SLURM_JOB_ID.txt 2>&1
echo "reader rc=$? "
# seen failing: reader on the same runs but with ONE expected azimuth turned by 180 degrees (planted); must show exactly one more disagreement per source
P=$W/plant; rm -rf $P; mkdir -p $P; ln -s $W/runs $P/runs
awk -F, -v OFS=, 'NR==2{$7=sprintf("%.4f",($7+180)%360)}1' $W/expected_azimuth.csv > $P/expected_azimuth.csv
$PY $W/win3_read.py $P > $W/logs/read_planted_$SLURM_JOB_ID.txt 2>&1
echo "planted reader rc=$? end=$(date -Iseconds)"
