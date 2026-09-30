#!/bin/bash
#SBATCH -J 5J_pilot
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH --array=1-50%8
#SBATCH -o /speed-scratch/o_iseri/5J/pilot/logs/task_%A_%a.out
# 5J pilot job 2: one EnergyPlus run per array task. Row N of run_manifest.csv (header excluded).
PILOT=${PILOT:-/speed-scratch/o_iseri/5J/pilot}
EP=${EP:-/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus}
N=${SLURM_ARRAY_TASK_ID:?no task id}
cd "$PILOT" || exit 2
LINE=$(sed -n "$((N+1))p" run_manifest.csv)
RUN_ID=$(echo "$LINE" | cut -d, -f1)
IID=$(echo "$LINE" | cut -d, -f7)
EPWMD5=$(echo "$LINE" | cut -d, -f10)
[ -n "$RUN_ID" ] && [ -n "$IID" ] || { echo "manifest row $N empty"; exit 2; }
EPW=$(ls "$PILOT"/epw/*.epw | head -1)
RUN="$PILOT/runs/$RUN_ID"
rm -rf "$RUN"; mkdir -p "$RUN" "$PILOT/extracted"
cp "$PILOT/inputs/$IID"/* "$RUN"/            # one working directory per run
cd "$RUN" || exit 2
echo "task=$N run_id=$RUN_ID input=$IID epw=$EPW host=$(hostname) start=$(date -Iseconds)"
T0=$(date +%s)
if [ -x /usr/bin/time ] && /usr/bin/time -v true >/dev/null 2>&1; then
  /usr/bin/time -v -o time.txt "$EP" -w "$EPW" -d "$RUN/eplus_out" -x -r "$RUN/in.idf" > eplus_stdout.txt 2>&1
else
  "$EP" -w "$EPW" -d "$RUN/eplus_out" -x -r "$RUN/in.idf" > eplus_stdout.txt 2>&1
fi
RC=$?
T1=$(date +%s)
ERR="$RUN/eplus_out/eplusout.err"
OK=no; SEV=NA
if [ -f "$ERR" ]; then
  grep -q "EnergyPlus Completed Successfully" "$ERR" && OK=yes
  SEV=$(grep -c "\*\* Severe" "$ERR")
fi
RSS=NA
[ -f time.txt ] && RSS=$(grep "Maximum resident set size" time.txt | sed 's/.*: *//')
# extract the 4 hourly columns
XRC=NA; XSIZE=NA
if [ -f "$RUN/eplus_out/eplusout.csv" ]; then
  awk -F, -f "$PILOT/5J_pilot_extract.awk" "$RUN/eplus_out/eplusout.csv" > "$PILOT/extracted/$RUN_ID.csv"
  XRC=$?
  XSIZE=$(wc -c < "$PILOT/extracted/$RUN_ID.csv")
fi
DU=$(du -sb "$RUN" | cut -f1)
{
  echo "run_id=$RUN_ID"
  echo "input_id=$IID"
  echo "rc=$RC"
  echo "seconds=$((T1-T0))"
  echo "max_rss_kb=$RSS"
  echo "run_dir_bytes=$DU"
  echo "completed_successfully=$OK"
  echo "severe_count=$SEV"
  echo "extract_rc=$XRC"
  echo "extracted_bytes=$XSIZE"
  echo "epw_md5_manifest=$EPWMD5"
  echo "end=$(date -Iseconds)"
} > "$RUN/status.txt"
cat "$RUN/status.txt"
if [ "$RC" -ne 0 ] || [ "$OK" != "yes" ] || [ "$XRC" != "0" ]; then exit 1; fi
exit 0
