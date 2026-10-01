#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=32G
#SBATCH -J s7_hhfull
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_hhfull_%j.out
# full new-household set. Size rule (R7-2): 500 if the pilot's conservative estimate (pilot seconds / 10 x 500, fixed cost included) is <= 4 CPU-h
# = 14400 s, else 300, else 200. 500 -> pilot s <= 288 ; 300 -> <= 480 ; else 200 (written as not fitting if > 720).
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
R=/speed-scratch/o_iseri/5J/households
S=$(cat $D/hh/pilot10_seconds.txt)
if [ $S -le 288 ]; then N=500; elif [ $S -le 480 ]; then N=300; else N=200; fi
echo "HH_SIZE_RULE pilot_seconds=$S est_for_500=$((S*50)) est_for_300=$((S*30)) est_for_200=$((S*20)) CHOSEN N=$N (limit 14400 s)"
echo $N > $D/hh/n_new_chosen.txt
head -n $((N+1)) $D/hh/hids_es_new500.csv > $D/hh/hids_es_new${N}_used.csv
echo "HIDS_FILE rows=$(wc -l < $D/hh/hids_es_new${N}_used.csv) md5=$(md5sum < $D/hh/hids_es_new${N}_used.csv | cut -d' ' -f1)"
OUT=$D/hh/new_${N}
rm -rf $OUT
cd $R/repo
T0=$(date +%s)
/usr/bin/time -v -o $D/hh/full_time.txt $PY -u 5J_docs_occ/tools/5thJ_step9_trigger_act2.py --root $R/repo/4J_docs_occ --fold es --leg leg5 --year 2010 --seed 1 --households 100 --timestep 60 --shipped-suffix _cal2010 --corpus $R/repo/4J_step3_corpus_es_it.jsonl --hids $D/hh/hids_es_new${N}_used.csv --out $OUT
RC=$?
T1=$(date +%s)
echo "TRIGGER exit=$RC"
echo "FULL_TRIGGER_SECONDS $((T1-T0)) households $N"
grep -E "Maximum resident|Elapsed" $D/hh/full_time.txt
echo "TRIGGER_OUTPUT_MB $(du -sk $OUT | cut -f1) kB total for $N households"
[ $RC -eq 0 ] || exit $RC
cd $C
$PY -u $C/s7_hh_build.py $OUT $D/hh/hids_es_new${N}_used.csv $D/hh/new_${N}_pool --pool
RC2=$?
echo "BUILD exit=$RC2 end=$(date -Iseconds)"
echo "POOL_DISK_KB $(du -sk -L $D/hh/pool | cut -f1) (new folders)"
exit $RC2
