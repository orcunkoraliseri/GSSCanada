#!/bin/bash
# FINDING 8 smoke test -- SCORING ONLY. No re-simulation: job 1171438 already produced both cells
# and the .sql files persist under out_F_f8fix/campaign_456301f5/. That job's E+ runs were clean
# (return code 0, all fuel- and channel-closure residuals 0.0000 %); only the scorer died, on a
# multi-line f-string that Python 3.10 (the cluster env) rejects and 3.13 (local) accepts.
#
# So this job compiles the scorer under the ACTUAL interpreter first and refuses to continue if it
# does not compile -- a scorer that cannot run is not a smoke test result.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/rescore_f8fix.sh

#SBATCH --job-name=3J_L3_rescoreF8
#SBATCH -p ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/rescoreF8_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
CDIR=$CAMP/out_F_f8fix/campaign_456301f5

export PYTHONPATH=$REPO
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1

echo "=== FINDING 8 smoke -- rescore ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  python: $($PY -V 2>&1)"
echo "  scorer md5: $(md5sum 3rdJ_09F_smoke_f8fix.py | cut -c1-8)"
echo "  campaign dir: $CDIR"

$PY -m py_compile 3rdJ_09F_smoke_f8fix.py || { echo "FATAL: scorer does not compile under the cluster interpreter"; exit 1; }
echo "  compile OK"

# the driver writes E+ output under <cell>/run/, not at the cell root
[ -f "$CDIR/Y2022__Tall__MTL/run/eplusout.sql" ] || { echo "FATAL: no sql for Y2022 cell"; exit 1; }
[ -f "$CDIR/Default_NECB__Tall__MTL/run/eplusout.sql" ] || { echo "FATAL: no sql for NECB cell"; exit 1; }

echo ""
echo "### SCORING (pre-registered predictions live in the scorer, not here)"
$PY -u 3rdJ_09F_smoke_f8fix.py "$CDIR/Y2022__Tall__MTL" "$CDIR/Default_NECB__Tall__MTL"
SRC=$?
echo "  scorer exit=$SRC"

echo ""
echo "### open item 5 check -- the Default_NECB control must report N/A, not FAIL"
grep -E "^t9_13_audit_(pass|verdict)=|^t9_13_d7_pass=" $CDIR/Default_NECB__Tall__MTL/injected.idf.provenance.txt

echo ""
echo "### full distinct MXU_*_DHWv2_* name list, injected cell"
grep -c "^t9_13_derived_name " $CDIR/Y2022__Tall__MTL/injected.idf.provenance.txt
grep "^t9_13_derived_name " $CDIR/Y2022__Tall__MTL/injected.idf.provenance.txt | grep -v "_HH"

echo ""
echo "### residential measurement (FINDING 8 1b)"
grep -E "^residential_dhw_" $CDIR/Y2022__Tall__MTL/injected.idf.provenance.txt

echo ""
echo "### cross-check: did the reference itself move? old arm-E NECB vs this one"
OLD=$CAMP/out_E_dhwvol/campaign_56d6e324/Default_NECB__Tall__MTL
if [ -f "$OLD/run/eplusout.sql" ]; then
  $PY -u 3rdJ_09F_smoke_f8fix.py "$CDIR/Default_NECB__Tall__MTL" "$OLD" 2>&1 | tail -30
else
  echo "  old arm-E NECB sql not on disk at $OLD -- cross-check SKIPPED (reported, not silently dropped)"
fi

echo ""
echo "rescore done: $(date)"
exit $SRC
