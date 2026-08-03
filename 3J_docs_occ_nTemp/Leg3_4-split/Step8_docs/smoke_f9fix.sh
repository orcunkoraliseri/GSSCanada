#!/bin/bash
# FINDING 9 fix -- SMOKE TEST. Two cells only, no campaign.
# Same pair as the FINDING 8 smoke, so arm G is directly comparable to arm F object by object.
# Requires injector md5 233932d7 (the per-day-type fix). Refuses to run on any other build.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/smoke_f9fix.sh

#SBATCH --job-name=3J_L3_smokeF9
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/smokeF9_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python

export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

OUT=$CAMP/out_G_f9fix
ARMF=$CAMP/out_F_f8fix/campaign_456301f5
mkdir -p $CAMP/logs $OUT

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
[ -x "$ENERGYPLUS_DIR/energyplus" ] || { echo "NO ENERGYPLUS at $ENERGYPLUS_DIR"; exit 1; }
[ -f "$EPLUS_IDD" ] || { echo "NO IDD at $EPLUS_IDD"; exit 1; }

MD5=$(md5sum $REPO/eSim_bem_utils/commercial_integration.py | cut -c1-8)
echo "=== FINDING 9 smoke test ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  injector md5: $MD5  (require 233932d7)"
if [ "$MD5" != "233932d7" ]; then
  echo "FATAL: not the FINDING 9 injector -- refusing to run a smoke test that cannot test"
  echo "       the thing it exists to test."
  exit 1
fi

# The scorer and the unit suite must both run under the CLUSTER interpreter, not the local one:
# the arm F scorer compiled on local Python 3.13 and was a SyntaxError on 3.10, and that cost a
# whole simulation round trip. Compile first, and run the primitive tests here too.
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1
$PY -m py_compile 3rdJ_09G_score_f9.py || { echo "FATAL: scorer does not compile"; exit 1; }
echo "  scorer compiles under $($PY -V 2>&1)"
# VACUOUS-GATE #10 (found 2026-08-03): this line used to be
#     $PY -u .../test_t9_13.py | tail -3
#     echo "  unit suite exit=$?"
# `$?` after a pipeline is the LAST command's status -- tail's -- which is always 0. The line
# printed "unit suite exit=0" no matter what the suite did. Capture the suite's own status, and
# refuse to continue on a failure, so the check can actually fail.
$PY -u $REPO/eSim_tests/test_t9_13.py > /tmp/t9_13_suite_$$.out
SUITE_RC=$?
tail -3 /tmp/t9_13_suite_$$.out
rm -f /tmp/t9_13_suite_$$.out
echo "  unit suite exit=$SUITE_RC"
[ "$SUITE_RC" = "0" ] || { echo "FATAL: T9-13 unit suite failed -- smoke aborted"; exit 1; }

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

CDIR=$(ls -d $OUT/campaign_*/ 2>/dev/null | head -1)
CDIR=${CDIR%/}
echo ""
echo "### campaign dir: $CDIR"

echo ""
echo "### SCORING against arm F (pre-registered predictions live in the scorer)"
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1
$PY -u 3rdJ_09G_score_f9.py "$CDIR" "$ARMF"
SRC=$?
echo "  scorer exit=$SRC"

echo ""
echo "### audit lines, injected cell"
grep -E "^t9_13_audit_(pass|verdict)=|^t9_13_d7_pass=|^t9_13_daytype_FALLBACK" $CDIR/Y2022__Tall__MTL/injected.idf.provenance.txt

echo ""
echo "### control cell must still be N/A"
grep -E "^t9_13_audit_(pass|verdict)=|^t9_13_d7_pass=" $CDIR/Default_NECB__Tall__MTL/injected.idf.provenance.txt

echo ""
echo "### independent check: schedule-only predictor must now say 1.0000 for every commercial object"
$PY -u 3rdJ_09F_daytype_loss.py "$CDIR/Y2022__Tall__MTL/injected.idf" "$CDIR/Default_NECB__Tall__MTL/injected.idf" | tail -12

echo ""
echo "smoke done: $(date)"
exit $SRC
