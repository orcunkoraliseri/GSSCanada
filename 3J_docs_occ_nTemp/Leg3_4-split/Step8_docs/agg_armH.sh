#!/bin/bash
# 3J Leg-3 Step 8/9 -- aggregate ARM H (post-FINDING-6/7/8/9, T9-13 volume_scaled, 56 cells).
#
# Built from agg_armE.sh. Everything that arm E asserted is kept verbatim; three things change:
#  1. campaign dir  out_E_dhwvol -> out_H_allfix, expected hash 56d6e324 -> 233932d7 (the
#     FINDING 8+9 injector). The hash guard is the point of the directory layout -- do not relax it.
#  2. NEW step 3b: the pre-registered DHW-volume gates (G1-G7) over all 56 cells, in-job, plus the
#     pre-registered hotel-saturation test. Arm H is the first arm to carry dhw_volume_hourly.csv,
#     and it is written by a FAIL-SOFT try/except -- so its failure mode is silence. A campaign that
#     wrote 56 empty volume files would otherwise aggregate green.
#  3. outdir agg_E_dhwvol -> agg_H_allfix.
#SBATCH --job-name=3J_L3_aggH
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/aggH_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

echo "### 0. resolve the arm H campaign directory"
NDIR=$(ls -d $CAMP/out_H_allfix/campaign_*/ 2>/dev/null | wc -l)
if [ "$NDIR" != "1" ]; then
  echo "FATAL: expected exactly 1 campaign dir under out_H_allfix, found $NDIR"
  ls -d $CAMP/out_H_allfix/*/ 2>/dev/null
  exit 1
fi
CDIR=$(ls -d $CAMP/out_H_allfix/campaign_*/ | head -1)
CDIR=${CDIR%/}
echo "  campaign dir: $CDIR"
echo "  expected hash: campaign_233932d7 (FINDING 8+9 injector md5 prefix)"
case "$CDIR" in
  *campaign_233932d7) echo "  hash OK" ;;
  *) echo "FATAL: campaign hash is not 233932d7 -- a different injector produced these runs"; exit 1 ;;
esac

echo "### 1. cell count"
NCELL=$(ls -d $CDIR/*/ | wc -l)
echo "  result dirs: $NCELL / 56"
[ "$NCELL" = "56" ] || { echo "FATAL: expected 56 cells, found $NCELL -- do not aggregate a partial arm"; exit 1; }

echo "### 2. P1 sweep -- shape preservation across ALL 56 cells"
NPASS=$(grep -h "^t9_13_audit_pass=True" $CDIR/*/injected.idf.provenance.txt | wc -l)
NVIOL=$(grep -h "^t9_13_VIOLATION" $CDIR/*/injected.idf.provenance.txt | wc -l)
NEXC=$(grep -h "^n_dhw_excluded=0" $CDIR/*/injected.idf.provenance.txt | wc -l)
NUNR=$(grep -h "^n_dhw_unresolved=0" $CDIR/*/injected.idf.provenance.txt | wc -l)
NCLIP=$(grep -h "clipped=True" $CDIR/*/injected.idf.provenance.txt | wc -l)
echo "  audit pass          : $NPASS / 56"
echo "  cells excluded==0   : $NEXC / 56"
echo "  cells unresolved==0 : $NUNR / 56"
echo "  VIOLATION lines     : $NVIOL   (expect 0)"
echo "  r saturated at r_max: $NCLIP   (expect 0)"

echo "### 2b. n_audited -- PER GEOMETRY x REQUESTED CHANNELS, not a universal 47"
TBL=$CAMP/logs/aggH_naudited_$SLURM_JOB_ID.txt
: > $TBL
for D in $CDIR/*/; do
  CELL=$(basename "${D%/}")
  GEOM=$(echo "$CELL" | awk -F'__' '{print $2}')
  P="$D/injected.idf.provenance.txt"
  [ -f "$P" ] || { echo "MISSING PROVENANCE $CELL" >> $TBL; continue; }
  CH=$(grep -m1 "^channels_requested=" "$P" | cut -d= -f2-)
  NA=$(grep -m1 "^t9_13_audit_pass=" "$P" | sed 's/.*n_audited=\([0-9]*\).*/\1/')
  VD=$(grep -m1 "^t9_13_audit_verdict=" "$P" | cut -d= -f2)
  echo "$GEOM|$CH|$NA|$VD|$CELL" >> $TBL
done
echo "  (geometry, channels_requested) -> n_audited, cell count:"
cut -d'|' -f1,2,3 $TBL | sort | uniq -c | sort -k2
NBAD=$(cut -d'|' -f1,2,3 $TBL | sort -u | cut -d'|' -f1,2 | sort | uniq -d | wc -l)
echo "  (geometry, channels) groups with a NON-CONSTANT n_audited: $NBAD   (expect 0)"
if [ "$NBAD" != "0" ]; then
  echo "  FAIL: same geometry + same requested channels audited different object counts:"
  for K in $(cut -d'|' -f1,2,3 $TBL | sort -u | cut -d'|' -f1,2 | sort | uniq -d); do
    grep -F "$K|" $TBL | sort
  done
fi
echo "  verdict distribution (PASS / FAIL / N-A -- N/A is the no-DHW-channel control, not a FAIL):"
cut -d'|' -f4 $TBL | sort | uniq -c

echo "### 2c. D7 -- assignment check, read back from each saved IDF (FINDING 8 guard)"
ND7=$(grep -h "^t9_13_d7_pass=True" $CDIR/*/injected.idf.provenance.txt | wc -l)
ND7F=$(grep -h "^t9_13_d7_pass=False" $CDIR/*/injected.idf.provenance.txt | wc -l)
ND7M=$(grep -L "^t9_13_d7_pass=" $CDIR/*/injected.idf.provenance.txt | wc -l)
echo "  D7 pass  : $ND7 / 56"
echo "  D7 fail  : $ND7F        (expect 0)"
echo "  D7 absent: $ND7M        (expect 0 -- a cell run by the PRE-FIX injector has no D7 line)"

echo "### 2d. D9 -- per-day-type fidelity, read back from each saved IDF (FINDING 9 guard)"
ND9M=$(grep -L "n_d9=" $CDIR/*/injected.idf.provenance.txt | wc -l)
ND9F=$(grep -h "n_d9=" $CDIR/*/injected.idf.provenance.txt | grep -v "n_d9=0 " | wc -l)
NUNCH=$(grep -h "d9_unchecked=" $CDIR/*/injected.idf.provenance.txt | grep -v "d9_unchecked=0" | wc -l)
NFB=$(grep -h "^t9_13_daytype_FALLBACK" $CDIR/*/injected.idf.provenance.txt | wc -l)
echo "  D9 absent          : $ND9M        (expect 0 -- cell run by a PRE-FINDING-9 injector)"
echo "  cells with D9 > 0  : $ND9F        (expect 0)"
echo "  cells with unchecked day types: $NUNCH  (expect 0 -- unchecked is NOT a pass)"
echo "  2-day-type FALLBACK schedules  : $NFB     (expect 0 -- each one lost Sat!=Sun volume)"
if [ "$NFB" != "0" ]; then
  grep -h "^t9_13_daytype_FALLBACK" $CDIR/*/injected.idf.provenance.txt | sort -u | head -10
fi
if [ "$NVIOL" != "0" ]; then
  echo "  --- every violation, so the pre-registered residential zero-occupancy exception can be"
  echo "      told apart from a real shape bug (admissible only if MXU_Residential_DHWv2_* with r_wd=0.0):"
  grep -h "^t9_13_VIOLATION" $CDIR/*/injected.idf.provenance.txt | sort | uniq -c | sort -rn | head -20
fi

echo "### 3. the r values actually applied, per channel (deduped across all 56 cells)"
for CH in office retail hotel; do
  echo "  -- $CH"
  grep -h "^t9_13 $CH " $CDIR/*/injected.idf.provenance.txt \
    | sed 's/.*\(r_wd=[0-9.]*\) \(r_we=[0-9.]*\) \(R=[0-9.]*\).*/    \1 \2 \3/' | sort -u
done
echo "  -- residential (per-household; count of distinct r pairs)"
grep -h "^t9_13 residential " $CDIR/*/injected.idf.provenance.txt \
  | sed 's/.*\(r_wd=[0-9.]*\) \(r_we=[0-9.]*\).*/\1 \2/' | sort -u | wc -l

echo "### 3b. NEW -- pre-registered DHW-volume gates G1-G7 over all 56 cells, + hotel saturation"
# Arm H is the first arm to carry dhw_volume_hourly.csv, written by a FAIL-SOFT try/except whose
# failure mode is SILENCE. Thresholds were fixed on 2026-08-03 before any cell finished and are not
# re-tuned here. This step REPORTS; it does not gate the aggregation, because a volume-series
# problem does not invalidate the energy results the aggregate is built from.
$PY -u $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_dhwvol_sweep.py \
    "$CDIR" $CAMP/logs/aggH_dhwvol_$SLURM_JOB_ID.csv
echo "  dhwvol sweep exit=$?"

echo "### 4. aggregate"
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1
$PY -u 3rdJ_08E_aggregate_4split.py \
    --campaign-dir "$CDIR" \
    --outdir $CAMP/agg_H_allfix \
    --eplus-idd "$EPLUS_IDD"
RC=$?
echo "  aggregate arm H exit=$RC : $(date)"
ls -la $CAMP/agg_H_allfix
exit $RC
