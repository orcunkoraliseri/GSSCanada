#!/bin/tcsh
#SBATCH --job-name=wp9_1c_venv2025
#SBATCH -A chachemv
#SBATCH -p ps
#SBATCH -t 7-00:00:00
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -o /speed-scratch/o_iseri/1J_rerun/logs/wp9_1c_venv2025_%j.out

# WP9 Stage 1c, ruling D-1J-A4 (manager, 2026-09-19): job 1339862 exited 3
# because the GSSCanada venv has no TensorFlow, which the protected 2025 module
# imports at its top (previous/eSim_dynamicML_mHead.py:15-16, 37-38, 277).
# Fix: build a SEPARATE venv under 1J_rerun with the GSSCanada venv's exact
# package versions plus tensorflow-cpu. The GSSCanada venv is only READ
# (pip list), never written; its list is snapshotted before and after and the
# two must be identical.
#
# Printed lines the manager checks (rule 58):
#   GSS VENV PYTHON: ...                  base interpreter version
#   PINNED PACKAGES: N                    lines taken from the GSSCanada venv
#   VENV PARITY: PASS|FAIL (...)          every pinned package same version in venv2025
#   GSS VENV UNCHANGED: YES|NO            before/after snapshot of the GSSCanada venv
#   TF VERSION: ...                       tensorflow + keras + numpy versions
#   MODULE IMPORT: OK|FAILED              the real protected module imports
# Exit codes: 6 = pip resolution/install failed, 7 = parity FAIL,
#             8 = GSSCanada venv changed, 9 = module import failed, 0 = all good.

set GSSPY = /speed-scratch/o_iseri/GSSCanada/venv/bin/python
set ROOT = /speed-scratch/o_iseri/1J_rerun
set NEW = $ROOT/venv2025
set WORK = $ROOT/venv2025_build
set CODE = $ROOT/occ2025/code/eSim_occ_utils/25CEN22GSS_classification
setenv PIP_CACHE_DIR $WORK/pipcache
setenv TMPDIR $WORK/tmp
mkdir -p $WORK/pipcache $WORK/tmp

echo "GSS VENV PYTHON: `$GSSPY -c 'import sys; print(sys.version.split()[0])'`"

echo "=== Step 1: snapshot the GSSCanada venv (read only) ==="
$GSSPY -m pip list --format=freeze --disable-pip-version-check > $WORK/gss_before.txt
grep -v -E '^(pip|setuptools|wheel)==' $WORK/gss_before.txt | grep '==' > $WORK/pins.txt
echo "Dropped (not pinnable or tooling):"
grep -v -E '==' $WORK/gss_before.txt
echo "PINNED PACKAGES: `wc -l < $WORK/pins.txt`"

echo "=== Step 2: create venv2025 ==="
if ( -e $NEW ) then
    echo "venv2025 already exists; removing the old copy (it lives only under 1J_rerun)"
    rm -rf $NEW
endif
$GSSPY -m venv $NEW
$NEW/bin/python -m pip install --disable-pip-version-check --upgrade pip
echo "=== Step 3: install pinned packages + tensorflow-cpu in ONE resolver call ==="
$NEW/bin/python -m pip install --disable-pip-version-check -r $WORK/pins.txt tensorflow-cpu
if ( $status != 0 ) then
    echo "PIP INSTALL: FAILED"
    exit 6
endif
echo "PIP INSTALL: OK"

echo "=== Step 4: parity check ==="
$NEW/bin/python -m pip list --format=freeze --disable-pip-version-check > $WORK/new_list.txt
grep -v -x -F -f $WORK/new_list.txt $WORK/pins.txt > $WORK/parity_missing.txt
set NMISS = `wc -l < $WORK/parity_missing.txt`
if ( $NMISS != 0 ) then
    echo "VENV PARITY: FAIL ($NMISS pinned packages not identical in venv2025)"
    cat $WORK/parity_missing.txt
    exit 7
endif
echo "VENV PARITY: PASS (all pinned packages identical)"
echo "Added by tensorflow-cpu:"
grep -v -x -F -f $WORK/pins.txt $WORK/new_list.txt

echo "=== Step 5: GSSCanada venv unchanged? ==="
$GSSPY -m pip list --format=freeze --disable-pip-version-check > $WORK/gss_after.txt
cmp -s $WORK/gss_before.txt $WORK/gss_after.txt
if ( $status != 0 ) then
    echo "GSS VENV UNCHANGED: NO"
    diff $WORK/gss_before.txt $WORK/gss_after.txt
    exit 8
endif
echo "GSS VENV UNCHANGED: YES"

echo "=== Step 6: import checks ==="
$NEW/bin/python -c "import tensorflow as tf, keras, numpy, pandas, sklearn; print('TF VERSION: tf', tf.__version__, 'keras', keras.__version__, 'numpy', numpy.__version__, 'pandas', pandas.__version__, 'sklearn', sklearn.__version__)"
cd $CODE
setenv GSS_BASE_DIR $ROOT/occ2025/0_Occupancy
$NEW/bin/python -c "from previous import eSim_dynamicML_mHead as m; ok = [hasattr(m, c) for c in ('ScheduleExpander', 'HouseholdAggregator', 'BEMConverter')]; print('module classes:', ok); assert all(ok)"
if ( $status != 0 ) then
    echo "MODULE IMPORT: FAILED"
    exit 9
endif
echo "MODULE IMPORT: OK"
echo "JOB DONE (venv2025 build)"
