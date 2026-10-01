#!/bin/bash
#SBATCH -J cdtiming
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -o /speed-scratch/o_iseri/5J/campaign_prep/logs/timing_%j.out
# Part D: ONE job: build + run the two biggest buildings (TIMING ONLY, Spanish pilot households), extract, disk check, arithmetic.
R=/speed-scratch/o_iseri/5J/campaign_prep
T=$R/timing
PY=/speed-scratch/o_iseri/envs/step4/bin/python
EP=/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus
cd $R
echo "host=$(hostname) start=$(date -Iseconds)"
$PY -u cd_timing_build.py || { echo "BUILD FAILED"; exit 2; }
while read RID EPW; do
  RUN=$T/runs/$RID
  cd $RUN || exit 2
  [ -f model.idf ] && echo "PATCH model_idf_present OK $RID"
  rm -rf $RUN/eplus_out
  T0=$(date +%s)
  /usr/bin/time -v -o time.txt $EP -w $EPW -d $RUN/eplus_out -x -r $RUN/model.idf > eplus_stdout.txt 2>&1
  RC=$?
  T1=$(date +%s)
  ERR=$RUN/eplus_out/eplusout.err
  OK=no; SEV=NA
  if [ -f $ERR ]; then grep -q "EnergyPlus Completed Successfully" $ERR && OK=yes; SEV=$(grep -c "\*\* Severe" $ERR); fi
  RSS=$(grep "Maximum resident set size" time.txt | sed 's/.*: *//')
  DUK=$(du -sk $RUN | cut -f1)
  { echo "run_id=$RID"; echo "rc=$RC"; echo "seconds=$((T1-T0))"; echo "max_rss_kb=$RSS"; echo "completed_successfully=$OK"; echo "severe_count=$SEV"; echo "run_folder_du_sk=$DUK"; echo "epw=$EPW"; } > $RUN/status.txt
  cat $RUN/status.txt
  cd $R
done < $T/epw_map.txt
sed 's#^R = .*#R = "/speed-scratch/o_iseri/5J/campaign_prep/timing/"#' $R/mzp_extract.py > $R/cd_extract_timing.py
$PY -u cd_extract_timing.py
echo "extracted files:"; ls -l $T/extracted
D0=$(date +%s)
du -sb /speed-scratch/o_iseri/5J > $T/du5J.txt
D1=$(date +%s)
echo "DU_5J_SECONDS=$((D1-D0)) $(cat $T/du5J.txt)"
df -B1 /speed-scratch/o_iseri > $T/df_raw.txt
stat -f -c '%a %S' /speed-scratch/o_iseri > $T/statfs.txt
$PY -u cd_arith.py
echo "end=$(date -Iseconds)"
