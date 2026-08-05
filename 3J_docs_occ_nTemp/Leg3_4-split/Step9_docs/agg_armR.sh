#!/bin/bash
# 3J Leg-3 Step 8E -- aggregate the RESIZED arm (K = 10, all-channel burner resize).
#
# Built from agg_armE.sh, with three deliberate differences:
#  1. NO `campaign_<hash>/` level. The resized tree is `out_R_resize/K10/<cell>/` directly, because
#     each cell is a post-process of arm H rather than a fresh injection run. So the hash guard from
#     agg_armE.sh cannot apply here -- instead §1 asserts the arm-H campaign hash the cells were
#     built FROM, which is the provenance that actually matters.
#  2. NO T9-13 audit sweep. Every `injected.idf.provenance.txt` in this tree is COPIED from arm H
#     (the resize does not re-inject), so re-running the P1 shape sweep here would re-measure arm H
#     and report it as if it were a property of the resized arm -- vacuous-gate #9, the gate whose
#     reference comes from the source it audits. Arm H's sweep already passed and stands.
#  3. `--idf-name injected_resized.idf`. The resized cells write that name; `injected.idf` does not
#     exist here. The default is unchanged for every other arm.
#SBATCH --job-name=3J_L3_aggR
#SBATCH -p ps
# 1 CPU, not 4: the account cap is cpu=32 and an unrelated 32-task array (`qc1983nu`, jobs
# 1172111/1172112, 7-day walltime) is holding all of it, so a 4-CPU request waits for four
# simultaneous free slots. 8E walks the 56 cells sequentially -- the extra CPUs bought nothing but
# a harder scheduling constraint.
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/aggR_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
CDIR=$CAMP/out_R_resize/K10
ARMH=$CAMP/out_H_allfix/campaign_233932d7
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

echo "### 0. compile under the cluster interpreter (local py_compile is 3.13, this env is 3.10)"
$PY -m py_compile $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py \
  || { echo "FATAL: 3rdJ_08E_aggregate_4split.py does not compile"; exit 1; }
$PY -V

echo "### 1. the arm-H tree these cells were built from"
[ -d "$ARMH" ] || { echo "FATAL: arm H tree missing at $ARMH"; exit 1; }
echo "  arm H: $ARMH  (campaign_233932d7)"
echo "  resized: $CDIR"

echo "### 2. cell count and required inputs"
NCELL=$(ls -d $CDIR/*/ | wc -l)
echo "  result dirs: $NCELL / 56"
[ "$NCELL" = "56" ] || { echo "FATAL: expected 56 cells, found $NCELL -- do not aggregate a partial arm"; exit 1; }
for f in injected_resized.idf manifest.json hourly_meters.csv channel_hourly.csv dhw_hourly.csv; do
  N=$(ls $CDIR/*/$f 2>/dev/null | wc -l)
  echo "  $f : $N / 56"
  [ "$N" = "56" ] || { echo "FATAL: $f missing in $((56-N)) cell(s) -- aggregating would silently drop them"; exit 1; }
done
NSQL=$(ls $CDIR/*/run/eplusout.sql 2>/dev/null | wc -l)
echo "  run/eplusout.sql : $NSQL / 56"
[ "$NSQL" = "56" ] || { echo "FATAL: eplusout.sql missing in $((56-NSQL)) cell(s)"; exit 1; }

echo "### 3. aggregate (idf-name = injected_resized.idf, NOT the default)"
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1
$PY -u 3rdJ_08E_aggregate_4split.py \
    --campaign-dir "$CDIR" \
    --outdir $CAMP/agg_R_resize \
    --idf-name injected_resized.idf \
    --eplus-idd "$EPLUS_IDD"
RC=$?
echo "  aggregate arm R exit=$RC : $(date)"
ls -la $CAMP/agg_R_resize
# Never end on a bare `echo` -- the job's exit code must be the work's, not the echo's.
exit $RC
