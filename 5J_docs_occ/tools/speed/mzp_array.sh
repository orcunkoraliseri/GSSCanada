#!/bin/bash
#SBATCH -J mzprun
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH --array=1-36%30
#SBATCH -o /speed-scratch/o_iseri/5J/mz_pilot/logs/run_%A_%a.out
# 5J mz re-pilot, job 2: one EnergyPlus run per array task. Row N of run_manifest.csv (header excluded).
R=/speed-scratch/o_iseri/5J/mz_pilot
EP=/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus
N=${SLURM_ARRAY_TASK_ID:?no task id}
cd "$R" || exit 2
LINE=$(sed -n "$((N+1))p" run_manifest.csv)
RUN_ID=$(echo "$LINE" | cut -d, -f1)
[ -n "$RUN_ID" ] || { echo "manifest row $N empty"; exit 2; }
EPW=/speed-scratch/o_iseri/5J/pilot/epw/es_madrid_2009_2010_y2010.epw
RUN="$R/runs/$RUN_ID"
cd "$RUN" || exit 2
[ -f model.idf ] && echo "PATCH model_idf_present OK" || exit 2
rm -rf "$RUN/eplus_out"
echo "task=$N run_id=$RUN_ID epw=$EPW host=$(hostname) start=$(date -Iseconds)"
T0=$(date +%s)
if [ -x /usr/bin/time ] && /usr/bin/time -v true >/dev/null 2>&1; then
  /usr/bin/time -v -o time.txt "$EP" -w "$EPW" -d "$RUN/eplus_out" -x -r "$RUN/model.idf" > eplus_stdout.txt 2>&1
else
  "$EP" -w "$EPW" -d "$RUN/eplus_out" -x -r "$RUN/model.idf" > eplus_stdout.txt 2>&1
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
DUK=$(du -sk "$RUN" | cut -f1)
ESOB=NA; CSVB=NA
[ -f "$RUN/eplus_out/eplusout.eso" ] && ESOB=$(wc -c < "$RUN/eplus_out/eplusout.eso")
[ -f "$RUN/eplus_out/eplusout.csv" ] && CSVB=$(wc -c < "$RUN/eplus_out/eplusout.csv")
{
  echo "run_id=$RUN_ID"
  echo "rc=$RC"
  echo "seconds=$((T1-T0))"
  echo "max_rss_kb=$RSS"
  echo "completed_successfully=$OK"
  echo "severe_count=$SEV"
  echo "run_folder_du_sk=$DUK"
  echo "eso_bytes=$ESOB"
  echo "csv_bytes=$CSVB"
  echo "end=$(date -Iseconds)"
} > "$RUN/status.txt"
cat "$RUN/status.txt"
if [ "$RC" -ne 0 ] || [ "$OK" != "yes" ]; then exit 1; fi
exit 0
