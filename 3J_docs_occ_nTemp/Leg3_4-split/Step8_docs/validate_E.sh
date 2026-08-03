#!/bin/bash
# 3J Leg-3 -- pre-flight for arm E (T9-13 DHW volume scaling). sbatch only.
#
# Built on validate_v2.sh (job 1170770). Every assertion below has a stated expected value that
# arm D's own artefact contradicts, so this file can fail:
#   arm D (T9-11): n_dhw_applied=45  n_dhw_excluded=2  n_dhw_unresolved=0
#   arm E (T9-13): n_dhw_applied=47  n_dhw_excluded=0  n_dhw_unresolved=0
# The 2 LAUNDRY objects move from excluded to applied because T9-13 never touches intra-day shape.
# If this script prints PASS with 45/2, it did not test what it claims to test.
#SBATCH --job-name=3J_val_E
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/validate_E_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO
cd $REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs || exit 1

EXPECT_MD5=56d6e3241df20d45f3831770dbcba5a2
FAIL=0

echo "### 0. which injector does this job actually import? (shadowing guard, 2026-07-31 near-miss)"
$PY -c "
import hashlib, sys
import eSim_bem_utils.commercial_integration as m
h = hashlib.md5(open(m.__file__,'rb').read()).hexdigest()
print('  file:', m.__file__)
print('  md5 :', h)
print('  EXPECT:', '$EXPECT_MD5')
if h != '$EXPECT_MD5':
    print('  FATAL: injector md5 mismatch -- the upload did not land or a stale copy shadows it')
    sys.exit(1)
ref = m.DHW_MODEL_VOLUME_SCALED['reference_occ_mean']
ch  = m.DHW_MODEL_VOLUME_SCALED['channels']
print('  reference:', m.DHW_MODEL_VOLUME_SCALED['reference'])
print('  peak_policy:', m.DHW_MODEL_VOLUME_SCALED['peak_policy'], ' r_max:', m.DHW_MODEL_VOLUME_SCALED['r_max'])
if not ref:
    print('  FATAL: reference_occ_mean is EMPTY -- every object would report dhw_unresolved and the'); print('         whole arm would be a silent no-op with 56 plausible result dirs'); sys.exit(1)
miss = [c for c in ch if c not in ref]
if miss:
    print('  FATAL: no baseline reference for', miss); sys.exit(1)
flat = [c for c,v in ref.items() if not isinstance(v, dict)]
if flat:
    print('  FATAL: FLAT scalar reference for', flat, '-- FINDING 4, double-counts the day-type asymmetry'); sys.exit(1)
for c in sorted(ref):
    print('  ref %-12s wd=%.6f we=%.6f' % (c, ref[c]['wd'], ref[c]['we']))
"
[ $? -eq 0 ] || { echo "### VALIDATION FAILED at step 0 -- DO NOT SUBMIT"; exit 1; }

echo "### 0b. primitive test suite on the cluster copy"
$PY -u $REPO/eSim_tests/test_t9_13.py | tail -5
RC_T=${PIPESTATUS[0]}
[ $RC_T -eq 0 ] || { echo "  FAIL: primitive tests did not all pass on the cluster copy"; FAIL=1; }

echo "### EnergyPlus version through the wrapper"
$ENERGYPLUS_DIR/energyplus --version

echo "### 1. dry-run all 56 cells -- any MISSING line here is a stop"
NMISS=0
for c in $(seq 0 55); do
  OUT=$($PY -u 3rdJ_08D_campaign_driver.py --cell $c --dry-run --engine local --repo-root "$REPO" 2>&1)
  echo "$OUT" | grep -q "all inputs resolve" || { echo "CELL $c NOT RESOLVED:"; echo "$OUT"; NMISS=$((NMISS+1)); }
done
echo "### cells with unresolved inputs: $NMISS / 56"

echo "### 2. smoke cell 3, 2 days, arm E"
rm -rf $CAMP/smoke_E
$PY -u 3rdJ_08D_campaign_driver.py --cell 3 --engine local --repo-root "$REPO" \
    --outroot $CAMP/smoke_E --lighting-model calibrated_v2 --dhw-model volume_scaled --smoke-days 2
RC_E=$?
echo "    arm E exit=$RC_E"

echo "### 3. provenance"
PE=$(ls $CAMP/smoke_E/*/*/injected.idf.provenance.txt 2>/dev/null | head -1)
[ -n "$PE" ] || { echo "FATAL: no arm E provenance file found"; echo "### VALIDATION FAILED -- DO NOT SUBMIT"; exit 1; }
echo "--- $PE"
grep -E "^lighting_model|^dhw_model|^n_dhw_|^t9_13_audit|^t9_13_reference|^t9_13 |^dhw_EXCLUDED|^dhw_UNRESOLVED|^t9_13_VIOLATION" "$PE"

echo "### 4. assertions -- expected values stated, arm D's numbers would fail them"
[ $NMISS -eq 0 ] || { echo "  FAIL: $NMISS cells unresolved"; FAIL=1; }
[ $RC_E -eq 0 ] || { echo "  FAIL: arm E smoke exit $RC_E"; FAIL=1; }

# --- lighting must be IDENTICAL to arm C, or E-C is not a pure DHW delta ---
grep -q "open_hours_mix" "$PE" || { echo "  FAIL: no open_hours_mix -- T9-12 did not land, E-C would confound lighting"; FAIL=1; }
grep -q "retail_k_open': 0.6" "$PE" || { echo "  FAIL: k_open is not 0.6 -- not arm C's lighting"; FAIL=1; }

# --- T9-13 landed at all ---
grep -q "'reference': 'baseline_series'" "$PE" || { echo "  FAIL: dhw_model is not the baseline_series form"; FAIL=1; }

# --- the counts. arm D was 45/2/0; T9-13 must be 47/0/0 ---
NAPP=$(grep "^n_dhw_applied=" "$PE" | cut -d= -f2)
NEXC=$(grep "^n_dhw_excluded=" "$PE" | cut -d= -f2)
NUNR=$(grep "^n_dhw_unresolved=" "$PE" | cut -d= -f2)
echo "  counts: applied=$NAPP excluded=$NEXC unresolved=$NUNR   (expect 47 / 0 / 0; arm D was 45 / 2 / 0)"
[ "$NUNR" = "0" ] || { echo "  FAIL: $NUNR unresolved DHW objects"; FAIL=1; }
[ "$NEXC" = "0" ] || { echo "  FAIL: excluded=$NEXC, expected 0 -- laundry must NOT be excluded under T9-13"; FAIL=1; }
[ "$NAPP" = "47" ] || { echo "  FAIL: applied=$NAPP, expected 47 (= arm D's 45 + the 2 LAUNDRY objects)"; FAIL=1; }

# --- the audit must have RUN and PASSED, and must have seen every channel (D6) ---
grep -q "^t9_13_audit_pass=True" "$PE" || { echo "  FAIL: t9_13 audit did not pass"; FAIL=1; }
NAUD=$(grep "^t9_13_audit_pass=" "$PE" | sed 's/.*n_audited=\([0-9]*\).*/\1/')
echo "  audited: $NAUD"
[ "$NAUD" = "47" ] || { echo "  FAIL: audit saw $NAUD objects, expected 47 -- a channel ran a different model"; FAIL=1; }
for CH in office retail hotel residential; do
  grep -q "^t9_13_reference $CH:" "$PE" || { echo "  FAIL: no baseline reference recorded for $CH"; FAIL=1; }
  grep -q "^t9_13 $CH " "$PE" || { echo "  FAIL: channel $CH produced no T9-13 schedule (D6)"; FAIL=1; }
done

# --- it must actually DO something: cell 3 is B_central, nothing should be a no-op ---
grep -q "^t9_13 .*noop=False" "$PE" || { echo "  FAIL: every object is a no-op -- r==1 everywhere, the lever is dead"; FAIL=1; }
NCLIP=$(grep -c "clipped=True" "$PE")
[ "$NCLIP" = "0" ] || echo "  note: $NCLIP schedule(s) saturated at r_max -- check the audit D5 lines"

# --- shape preservation is an identity: it must hold on the real output, not just in the unit test ---
grep -q "^t9_13_VIOLATION" "$PE" && { echo "  FAIL: audit reported violations (see t9_13_VIOLATION lines above)"; FAIL=1; }

if [ $FAIL -eq 0 ]; then echo "### VALIDATION PASS -- safe to submit arm E"; else echo "### VALIDATION FAILED -- DO NOT SUBMIT"; fi
exit $FAIL
