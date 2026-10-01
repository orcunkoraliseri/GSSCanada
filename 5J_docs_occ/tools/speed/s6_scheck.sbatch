#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 6
#SBATCH --mem=32G
#SBATCH -J s6_scheck
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_scheck_%j.out
# Step 6 part A, check before the lock: the amended scorer without --test behaves like the frozen one (validation B0 scoring, same
# arguments as job 1404521); --test refusals; the comparison seen failing. NEVER scores or reads a test list (the only --test runs are
# refused before any list is read; the planted-lock copy is run only after its patch is verified by grep).
export PYTHONDONTWRITEBYTECODE=1
PY=/speed-scratch/o_iseri/envs/step4/bin/python
T=/speed-scratch/o_iseri/5J/train
F=/speed-scratch/o_iseri/5J/freeze
A=/speed-scratch/o_iseri/5J/test/amend1
C=/speed-scratch/o_iseri/5J/test/check/scheck
mkdir -p $C && cd $C || exit 2
FAILS=0
chk() { if [ "$2" = "0" ]; then echo "CHECK $1 PASS $3"; else echo "CHECK $1 FAIL $3"; FAILS=$((FAILS+1)); fi; }
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID"
md5sum $F/5thJ_04_scorer.py $A/5thJ_04_scorer_t.py
[ "$(md5sum < $F/5thJ_04_scorer.py | cut -d' ' -f1)" = "84d1dafaf6ca38bca3954e2b63720f5a" ]; chk frozen_scorer_md5_is_84d1dafa $?
[ "$(md5sum < $A/5thJ_04_scorer_t.py | cut -d' ' -f1)" = "4d15df70b60e20f561c8f81197aaf9a8" ]; chk staged_scorer_t_md5_is_4d15df70 $?
echo "== diff -u frozen amended (printed for the record)"; diff -u $F/5thJ_04_scorer.py $A/5thJ_04_scorer_t.py
echo "== flags-off equivalence: validation B0 scoring, arguments of job 1404521"
for NAME in frozen t; do
  if [ $NAME = frozen ]; then SC=$F/5thJ_04_scorer.py; else SC=$A/5thJ_04_scorer_t.py; fi
  mkdir -p $C/out_$NAME
  $PY -u $SC --pred $T/pred/B0 --split validation --out $C/out_$NAME/ --tag B0 --b1 $F/out/standins/weakb1 --control $T/pred/B0 --workers 6 > $C/out_$NAME/score_B0.txt 2>&1
  echo "RC_$NAME $?"
done
norm() { grep -v "^SCORER start" "$1" | grep -v "^  progress" | sed -E 's/ seconds=[0-9]+//' | sed -E "s#$C/out_frozen/#@OUT@/#g; s#$C/out_t/#@OUT@/#g; s#$T/score/#@OUT@/#g" ; }
norm $C/out_frozen/score_B0.txt > $C/n_frozen.txt
norm $C/out_t/score_B0.txt > $C/n_t.txt
norm $T/score/score_B0.txt > $C/n_orig1404521.txt
echo "== RAW diff frozen vs amended (expect: only the start line, progress lines, seconds=)"; diff $C/out_frozen/score_B0.txt $C/out_t/score_B0.txt | head -40
diff $C/n_frozen.txt $C/n_t.txt > $C/d_ft.txt; chk amended_without_test_score_file_equals_frozen_scorer_output $? "lines=$(wc -l < $C/n_t.txt) diff_lines=$(wc -l < $C/d_ft.txt)"
diff $C/n_frozen.txt $C/n_orig1404521.txt > $C/d_fo.txt; chk frozen_rerun_equals_original_job_1404521_output $? "diff_lines=$(wc -l < $C/d_fo.txt)"
for f in out_frozen out_t; do sort $C/$f/openlog_B0.tsv > $C/$f/openlog_sorted.tsv; done
cmp $C/out_frozen/openlog_sorted.tsv $C/out_t/openlog_sorted.tsv; chk open_logs_equal_after_sorting $? "lines=$(wc -l < $C/out_t/openlog_sorted.tsv)"
grep -E "^SUMMARY PASS|^SCORER_EXIT" $C/out_t/score_B0.txt
echo "== planted difference must be reported (seen failing)"
sed '0,/GATE G5J.3/s//GATE G5J.9/' $C/n_t.txt > $C/n_planted.txt
diff $C/n_frozen.txt $C/n_planted.txt > $C/d_pl.txt; [ -s $C/d_pl.txt ]; chk planted_difference_is_reported $? "diff_lines=$(wc -l < $C/d_pl.txt)"
echo "== refusals (each stops before any list is read)"
$PY -u $A/5thJ_04_scorer_t.py --test --split validation --pred /nonexistent --out $C/out_r1/ --tag r1 --workers 1 > $C/r1.txt 2>&1; RC=$?; tail -n 2 $C/r1.txt
[ $RC -ne 0 ] && grep -q "scores one of the three test lists only" $C/r1.txt; chk test_flag_with_validation_split_refused $?
$PY -u $F/5thJ_04_scorer.py --split test_both_new --pred /nonexistent --out $C/out_r2/ --tag r2 --workers 1 > $C/r2.txt 2>&1; RC=$?; tail -n 2 $C/r2.txt
[ $RC -ne 0 ] && grep -q "scorer runs on development or validation only" $C/r2.txt; chk frozen_scorer_still_refuses_test_split $?
$PY -u $A/5thJ_04_scorer_t.py --split test_both_new --pred /nonexistent --out $C/out_r3/ --tag r3 --workers 1 > $C/r3.txt 2>&1; RC=$?; tail -n 2 $C/r3.txt
[ $RC -ne 0 ] && grep -q "scorer runs on development or validation only" $C/r3.txt; chk amended_without_test_still_refuses_test_split $?
sed 's#/speed-scratch/o_iseri/5J/gates_frozen.md5#/speed-scratch/o_iseri/5J/NO_SUCH_LOCK_FILE.md5#' $A/5thJ_04_scorer_t.py > $C/scorer_t_nolock.py
[ "$(grep -c NO_SUCH_LOCK_FILE $C/scorer_t_nolock.py)" = "1" ] && [ "$(grep -c '5J/gates_frozen.md5' $C/scorer_t_nolock.py)" = "0" ]; PATCH=$?
chk planted_nolock_copy_patch_present_verified_before_run $PATCH
if [ $PATCH -eq 0 ]; then
  $PY -u $C/scorer_t_nolock.py --test --split test_both_new --pred /nonexistent --out $C/out_r4/ --tag r4 --workers 1 > $C/r4.txt 2>&1; RC=$?; tail -n 2 $C/r4.txt
  [ $RC -ne 0 ] && grep -q "REFUSED: --test needs" $C/r4.txt; chk test_flag_refuses_without_lock_file $?
else
  echo "planted copy not run (patch missing)"
fi
echo "CHECK_SCHECK_DONE fails=$FAILS end=$(date -Iseconds)"
[ $FAILS -eq 0 ]
