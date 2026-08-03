#!/bin/bash
# FINDING 8 fix -- SMOKE TEST. Two cells only, no campaign.
#   cell 0 = Default_NECB__Tall__MTL  (injects nothing -> the reference, and it exercises the new
#            N/A verdict from open item 5 plus D7 over untouched objects)
#   cell 1 = Y2022__Tall__MTL         (the T9-13 reference year: r = 1.000, so DHW must be a no-op)
#
# Requires injector md5 456301f5 (the cache-key fix). The job checks that and refuses to run on
# the pre-fix injector rather than producing a result that looks like a smoke test and is not.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/smoke_f8fix.sh

#SBATCH --job-name=3J_L3_smokeF8
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/smokeF8_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python

export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

OUT=$CAMP/out_F_f8fix
mkdir -p $CAMP/logs $OUT

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
[ -x "$ENERGYPLUS_DIR/energyplus" ] || { echo "NO ENERGYPLUS at $ENERGYPLUS_DIR"; exit 1; }
[ -f "$EPLUS_IDD" ] || { echo "NO IDD at $EPLUS_IDD"; exit 1; }

MD5=$(md5sum $REPO/eSim_bem_utils/commercial_integration.py | cut -c1-8)
echo "=== FINDING 8 smoke test ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  injector md5: $MD5  (require 456301f5)"
if [ "$MD5" != "456301f5" ]; then
  echo "FATAL: this is not the fixed injector -- refusing to run a smoke test that cannot"
  echo "       test the thing it exists to test."
  exit 1
fi
echo "  office product md5: $(md5sum $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/office_presence_multiplier_2030.csv | cut -c1-8)  (expect 575d17e5)"

cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1

for CELL in 0 1; do
  echo ""
  echo "### cell $CELL"
  $PY -u 3rdJ_08D_campaign_driver.py \
      --cell $CELL \
      --engine local \
      --repo-root "$REPO" \
      --outroot "$OUT" \
      --lighting-model calibrated_v2 \
      --dhw-model volume_scaled
  echo "  cell $CELL exit=$? : $(date)"
done

echo ""
echo "### result dirs"
ls -d $OUT/*/*/ 2>/dev/null

CDIR=$(ls -d $OUT/campaign_*/ 2>/dev/null | head -1)
CDIR=${CDIR%/}
echo "  campaign dir: $CDIR"

echo ""
echo "### SCORING (pre-registered predictions live in the scorer, not here)"
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1
$PY -u 3rdJ_09F_smoke_f8fix.py "$CDIR/Y2022__Tall__MTL" "$CDIR/Default_NECB__Tall__MTL"
SRC=$?
echo "  scorer exit=$SRC"

echo ""
echo "### open item 5 check -- the Default_NECB control must report N/A, not FAIL"
grep -E "^t9_13_audit_(pass|verdict)=|^t9_13_d7_pass=" $CDIR/Default_NECB__Tall__MTL/injected.idf.provenance.txt

echo ""
echo "### cross-check: did the reference itself move? old arm-E NECB vs this one"
OLD=$CAMP/out_E_dhwvol/campaign_56d6e324/Default_NECB__Tall__MTL
$PY -u 3rdJ_09F_smoke_f8fix.py "$CDIR/Default_NECB__Tall__MTL" "$OLD" 2>&1 | tail -25

echo ""
echo "smoke done: $(date)"
exit $SRC
