#!/bin/bash
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH --exclude=antenna1
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -J s6_score
#SBATCH -o /speed-scratch/o_iseri/5J/test/logs/s6_score_%j.out
# 5J Step 6 part B: THE ONE scoring job on the sealed test lists (Spain + Italy only). Submitted ONCE, afterok the seen-failing job.
# The only reader of test truth is the locked test-mode scorer (and the locked s6_reported_v2.py) called below.
FIVE=/speed-scratch/o_iseri/5J
PY=/speed-scratch/o_iseri/envs/step4/bin/python
F=$FIVE/freeze
T=$FIVE/test
C=$T/code
O=$T/score
FLOORS=$F/out/floors.json
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
echo "JOB $SLURM_JOB_ID start $(date -Iseconds) host=$(hostname) cpus=${SLURM_CPUS_PER_TASK:-?}"
echo "JOB_SCRIPT_MD5 $(md5sum < $C/s6_score.sbatch | cut -d' ' -f1) STARTUP_SCRIPT_MD5 $(md5sum < $C/s6_startup.sh | cut -d' ' -f1)"
# once only: an existing score folder means a score job already started; a rerun needs the manager to move it away first
if [ -e $O ]; then echo "REFUSED: $O exists (the scoring job is submitted once; a rerun needs the crash line in the ledger and the folder moved by the manager)"; exit 4; fi
bash $C/s6_startup.sh
RCS=$?
if [ "$RCS" != "0" ]; then echo "STARTUP FAILED exit $RCS: no scorer call is made"; exit 9; fi
SM=$(md5sum < $F/5thJ_04_scorer_t.py | cut -d' ' -f1)
SR=$(grep '/5thJ_04_scorer_t.py$' $FIVE/gates_frozen_amend1.md5 | cut -d' ' -f1)
if [ -n "$SM" ] && [ "$SM" = "$SR" ]; then echo "SCORER_MD5 $SM PRESENT (equals the record in gates_frozen_amend1.md5)"; else echo "SCORER_MD5 $SM ABSENT (record $SR)"; exit 9; fi
RM=$(md5sum < $F/s6_reported_v2.py | cut -d' ' -f1)
RR=$(cut -d' ' -f1 $F/s6_reported_v2.md5)
if [ -n "$RM" ] && [ "$RM" = "$RR" ]; then echo "REPORTED_V2_MD5 $RM PRESENT (equals freeze/s6_reported_v2.md5)"; else echo "REPORTED_V2_MD5 $RM ABSENT (record $RR)"; exit 9; fi
echo "FLOORS $FLOORS md5 $(md5sum < $FLOORS | cut -d' ' -f1) (the file the default of the validation scoring used)"
mkdir -p $O || exit 2

call() {  # $1 tag, then the scorer arguments (before the common ones)
  local tag=$1; shift
  echo "CALL $tag START $(date -Iseconds)"
  $PY -u $F/5thJ_04_scorer_t.py "$@" --test --floors $FLOORS --nboot 2000 --workers 16 --out $O/ --tag $tag > $O/score_$tag.txt 2>&1
  local rc=$?
  echo $rc > $O/exit_$tag.txt; echo $SLURM_JOB_ID > $O/jobid_$tag.txt
  echo "CALL $tag EXIT $rc"
}
P=$T/pred
for L in test_new_households test_new_buildings test_both_new; do
  call S_$L      --split $L --pred $P/S --b1 $P/B1 --control $P/C --secondary
  call C_$L      --split $L --pred $P/C --b1 $P/B1 --control $P/C
  call B1_$L     --split $L --pred $P/B1 --b1 $P/B1 --control $P/C
  call B0_$L     --split $L --pred $P/B0 --b1 $P/B1 --control $P/C
  call SloES_$L  --split $L --pred $P/S_loco_es --b1 $P/B1_loco_es --control $P/B0
  call SloIT_$L  --split $L --pred $P/S_loco_it --b1 $P/B1_loco_it --control $P/B0
  call Sseed2_$L --split $L --pred $P/S_seed2 --b1 $P/B1 --control $P/C
  call Sseed3_$L --split $L --pred $P/S_seed3 --b1 $P/B1 --control $P/C
  tag=reported_S_$L
  echo "CALL $tag START $(date -Iseconds)"
  $PY -u $F/s6_reported_v2.py --test --pred $P/S --split $L --out $O/ --tag $tag --pairs-ref $O/score_S_$L.txt --workers 16 > $O/stdout_$tag.txt 2>&1
  rc=$?
  echo $rc > $O/exit_$tag.txt; echo $SLURM_JOB_ID > $O/jobid_$tag.txt
  echo "CALL $tag EXIT $rc"
done
echo "SCORE_FILES $(ls $O | wc -l) files in $O"
echo "S6_DONE end=$(date -Iseconds)"
exit 0
