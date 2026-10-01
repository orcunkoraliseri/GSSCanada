#!/bin/bash
#SBATCH -J s6_reported
#SBATCH -p ps
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -o /speed-scratch/o_iseri/5J/train/reported/logs/s6_reported_%j.out
# 5J Step 6 part B0 (Spain + Italy only; VALIDATION only; no test file is opened).
# 1 compile, 2 planted refusal of --test on a scratch copy, 3 main run on validation S3, 4 lock the script if all is clean.
FIVE=/speed-scratch/o_iseri/5J
PY=/speed-scratch/o_iseri/envs/step4/bin/python
R=$FIVE/train/reported
S=$R/s6_reported.py
echo "JOB $SLURM_JOB_ID start $(date)"
echo "SCRIPT_MD5 $(md5sum $S)"
$PY -m py_compile $S && echo "COMPILE ok" || { echo "COMPILE FAILED"; exit 1; }
rm -rf $R/__pycache__

# ---- 2. planted --test call on a scratch copy whose ROOT is an empty folder: must refuse with exit 9
SC=$R/refusal
mkdir -p $SC/emptyroot $SC/out
sed 's#^ROOT = .*#ROOT = "/speed-scratch/o_iseri/5J/train/reported/refusal/emptyroot/"#' $S > $SC/s6_reported_scratch.py
if grep -q '^ROOT = "/speed-scratch/o_iseri/5J/train/reported/refusal/emptyroot/"$' $SC/s6_reported_scratch.py && [ ! -e $FIVE/gates_frozen_amend1.md5 ] && [ -z "$(ls -A $SC/emptyroot)" ]; then
  $PY -u $SC/s6_reported_scratch.py --pred $FIVE/train/pred/S3 --split test_both_new --out $SC/out --tag refuse --test
  RC_REF=$?
  echo "REFUSAL_EXIT $RC_REF"
  if [ "$RC_REF" = "9" ]; then echo "CHECK test_refuses_without_lock_file PASS exit=9"; else echo "CHECK test_refuses_without_lock_file FAIL exit=$RC_REF"; fi
else
  echo "CHECK test_refuses_without_lock_file FAIL scratch copy not set up as planned; the planted call was NOT run"
  RC_REF=99
fi
rm -rf $R/__pycache__

# ---- 3. main run on validation (the script itself prints its CHECK lines)
$PY -u $S --pred $FIVE/train/pred/S3 --split validation --out $R/ --tag S3_val --pairs-ref $FIVE/train/score/score_S3.txt --workers 4
RC_MAIN=$?
echo "MAIN_EXIT $RC_MAIN"

# ---- 4. lock only when everything is clean
NFAIL=$(grep -c '^CHECK .* FAIL' $R/reported_S3_val.txt)
echo "REAL_CHECKS_FAILED $NFAIL"
if [ "$RC_MAIN" = "0" ] && [ "$RC_REF" = "9" ] && [ "$NFAIL" = "0" ] && [ ! -e $FIVE/freeze/s6_reported.py ] && [ ! -e $FIVE/freeze/s6_reported.md5 ]; then
  cp $S $FIVE/freeze/s6_reported.py && chmod 444 $FIVE/freeze/s6_reported.py
  (cd $FIVE/freeze && md5sum s6_reported.py > s6_reported.md5 && chmod 444 s6_reported.md5)
  echo "LOCKED $(cat $FIVE/freeze/s6_reported.md5)"
else
  echo "NOT_LOCKED main=$RC_MAIN refusal=$RC_REF failed_checks=$NFAIL"
fi
echo "JOB_END $(date)"
