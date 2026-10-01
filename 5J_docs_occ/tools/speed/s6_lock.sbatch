#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -J s6_lock
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_lock_%j.out
# Step 6 part A: lock the amendment (runs only after the scorer check). Additive only: the original lock file and everything in freeze/
# stay as they are; two new files are added (the scorer copy and the amend1 md5 record).
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=/speed-scratch/o_iseri/5J/freeze
A=/speed-scratch/o_iseri/5J/test/amend1
L0=/speed-scratch/o_iseri/5J/gates_frozen.md5
L1=/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5
FAILS=0
chk() { if [ "$2" = "0" ]; then echo "CHECK $1 PASS $3"; else echo "CHECK $1 FAIL $3"; FAILS=$((FAILS+1)); fi; }
echo "host=$(hostname) start=$(date -Iseconds) job=$SLURM_JOB_ID"
[ ! -e $F/5thJ_04_scorer_t.py ] && [ ! -e $L1 ]; chk no_existing_amend_files_to_overwrite $?
[ "$FAILS" = "0" ] || { echo "LOCK STOPPED"; exit 3; }
L0MD5=$(md5sum < $L0 | cut -d' ' -f1); echo "original lock file md5 before: $L0MD5"
[ "$(md5sum < $F/gates_frozen.md | cut -d' ' -f1)" = "5a0dae85994acb2aefdb08fb01aab950" ]; chk frozen_gates_md_md5_is_5a0dae85 $?
[ "$(md5sum < $A/5thJ_04_scorer_t.py | cut -d' ' -f1)" = "4d15df70b60e20f561c8f81197aaf9a8" ]; chk staged_scorer_t_md5_is_4d15df70 $?
N=$(wc -c < $F/gates_frozen.md); NN=$(wc -c < $A/gates_frozen.md)
cmp -n $N $F/gates_frozen.md $A/gates_frozen.md; chk old_gates_frozen_bytes_are_an_unchanged_prefix_of_the_new_one $? "old_bytes=$N new_bytes=$NN"
[ $NN -gt $N ]; chk new_file_is_longer $?
# seen failing: a one-byte change inside the old part must be caught by the same cmp
sed '1s/^#/@/' $F/gates_frozen.md > $A/prefix_planted.md
cmp -n $N $A/prefix_planted.md $A/gates_frozen.md > /dev/null 2>&1; [ $? -ne 0 ]; chk prefix_check_planted_change_CAUGHT_seen_failing $?
rm -f $A/prefix_planted.md
grep -q "no test prediction, test score or test truth read existed\|No test prediction, test score or test truth read existed" $A/gates_frozen.md; chk amendment_text_has_the_no_test_result_sentence $?
[ "$FAILS" = "0" ] || { echo "LOCK STOPPED (checks failed, nothing written)"; exit 3; }
cp $A/5thJ_04_scorer_t.py $F/5thJ_04_scorer_t.py && chmod 444 $F/5thJ_04_scorer_t.py
cmp $A/5thJ_04_scorer_t.py $F/5thJ_04_scorer_t.py; chk scorer_t_copied_byte_equal $?
md5sum $A/gates_frozen.md $F/5thJ_04_scorer_t.py $F/split_loader.py > $L1 && chmod 444 $L1
echo "== $L1"; cat $L1; ls -la $L1 $F/5thJ_04_scorer_t.py
md5sum -c $L1; chk md5_record_verifies $?
[ "$(md5sum < $L0 | cut -d' ' -f1)" = "$L0MD5" ]; chk original_lock_file_untouched $? "md5 after: $(md5sum < $L0 | cut -d' ' -f1)"
[ "$(md5sum < $F/gates_frozen.md | cut -d' ' -f1)" = "5a0dae85994acb2aefdb08fb01aab950" ]; chk freeze_gates_frozen_md_untouched $?
echo "LOCK_DONE fails=$FAILS end=$(date -Iseconds)"
[ $FAILS -eq 0 ]
