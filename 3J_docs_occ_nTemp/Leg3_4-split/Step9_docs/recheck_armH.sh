#!/bin/bash
# Arm H post-aggregation re-check, job 1171607 follow-up. Two questions, both report-only:
#
#  A. The 16 cells that FAILed the day-type gate (3d) did so because the predictor read only
#     Schedule:Compact and silently predicted 0.0 for any channel the injector had not rewritten.
#     The predictor now walks Schedule:Year -> Week:Daily -> Day:Interval and REFUSES (G4 FAIL,
#     itemised) rather than silently skipping. RE-PRE-REGISTERED before this run:
#        all 56 cells PASS at the SAME 1 % band, and n_unreadable == 0 on all 56.
#     A miss here is recorded, not repaired.
#
#  B. The 2 P1 shape VIOLATIONs. The pre-registered exception admits a violation ONLY if the object
#     is an MXU_Residential_DHWv2_* schedule with r_wd = 0.0 (a household with zero weekday
#     occupancy has no peak hour to preserve). This prints the offending object's actual schedule
#     name -- the r values are encoded in it as r<r_wd*1000>w<r_we*1000> -- so admissibility is
#     read off the artifact rather than assumed.
#SBATCH --job-name=3J_L3_recheckH
#SBATCH -p ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/recheckH_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S9=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs
CDIR=$CAMP/out_H_allfix/campaign_233932d7
export PYTHONPATH=$REPO

echo "### 0. syntax check UNDER THE CLUSTER INTERPRETER (local py_compile is 3.13, this is 3.10)"
$PY -m py_compile $S9/3rdJ_09H_daytype_volume_verify.py || { echo "FATAL: does not compile under $PY"; exit 1; }
echo "  compiles OK"
$PY -V

NCELL=$(ls -d $CDIR/*/ | wc -l)
echo "### 1. cells: $NCELL / 56"
[ "$NCELL" = "56" ] || { echo "FATAL: not 56 cells"; exit 1; }

echo "### 2. A -- day-type gate re-run with the Schedule:Year-aware predictor, all 56 cells"
$PY -u $S9/3rdJ_09H_daytype_volume_verify.py $CDIR/*/ > $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt
RC=$?
echo "  daytype exit=$RC   (0 = all 56 PASS, which is the pre-registered prediction)"
echo "  --- verdict table ---"
sed -n '/^  [A-Za-z].*\(PASS\|FAIL\)$/p' $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt | tail -60
echo "  --- G4 (unreadable schedules) across all cells ---"
grep -c "G4  every drawing" $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt
grep "G4  every drawing" $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt | sort | uniq -c
echo "  --- any itemised unreadable objects ---"
grep "unreadable:" $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt | sort | uniq -c | head -20
echo "  --- one previously-FAILing cell, in full ---"
grep -A 20 "CELL Y2010__Tall__CLG" $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt | head -22
echo "  --- the zero-injection control, in full ---"
grep -A 20 "CELL Default_NECB__Tall__CLG" $CAMP/logs/recheckH_daytype_$SLURM_JOB_ID.txt | head -22

echo "### 3. B -- P1 VIOLATION admissibility, read off the saved IDF"
for P in $CDIR/*/injected.idf.provenance.txt; do
  if grep -q "^t9_13_VIOLATION" "$P"; then
    D=$(dirname "$P")
    echo "  CELL $(basename $D)"
    grep -h "^t9_13_VIOLATION" "$P" | sed 's/^/    /'
    OBJ=$(grep -h -m1 "^t9_13_VIOLATION" "$P" | sed "s/.*'\(.*\)'.*/\1/")
    echo "    object: $OBJ"
    echo "    its WaterUse:Equipment block in the saved IDF:"
    grep -A 5 -F "    $OBJ," "$D/injected.idf" | head -7 | sed 's/^/      /'
  fi
done
echo "  (admissible ONLY if the schedule is MXU_Residential_DHWv2_* carrying r_wd = 0.000)"

echo "### 4. done: $(date)"
exit 0
