#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=16G
#SBATCH -J s7_hhpilot
#SBATCH -o /speed-scratch/o_iseri/5J/district/logs/s7_hhpilot_%j.out
# pilot: 10 new Spanish households through the same trigger as the 60 (same options as hh_run_fold.sbatch), timed; then folders + checks
. /speed-scratch/o_iseri/5J/district/code/s7_prelude.sh
R=/speed-scratch/o_iseri/5J/households
OUT=$D/hh/pilot10
rm -rf $OUT
cd $R/repo
T0=$(date +%s)
/usr/bin/time -v -o $D/hh/pilot10_time.txt $PY -u 5J_docs_occ/tools/5thJ_step9_trigger_act2.py --root $R/repo/4J_docs_occ --fold es --leg leg5 --year 2010 --seed 1 --households 100 --timestep 60 --shipped-suffix _cal2010 --corpus $R/repo/4J_step3_corpus_es_it.jsonl --hids $D/hh/hids_es_pilot10.csv --out $OUT
RC=$?
T1=$(date +%s)
echo "TRIGGER exit=$RC"
echo "PILOT_TRIGGER_SECONDS $((T1-T0)) households 10"
echo $((T1-T0)) > $D/hh/pilot10_seconds.txt
grep -E "Maximum resident|Elapsed" $D/hh/pilot10_time.txt
echo "TRIGGER_OUTPUT_MB $(du -sk $OUT | cut -f1) kB total for 10 households"
[ $RC -eq 0 ] || exit $RC
cd $C
$PY -u $C/s7_hh_build.py $OUT $D/hh/hids_es_pilot10.csv $D/hh/pilot_pool
RC2=$?
echo "BUILD exit=$RC2 end=$(date -Iseconds)"
exit $RC2
