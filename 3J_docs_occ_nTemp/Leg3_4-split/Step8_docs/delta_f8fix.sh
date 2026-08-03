#!/bin/bash
# FINDING 8 smoke -- attribution pass. Reads existing .sql only, simulates nothing.
#SBATCH --job-name=3J_L3_deltaF8
#SBATCH -p ps
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/deltaF8_%j.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
export PYTHONPATH=$REPO
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs" || exit 1

echo "node=$(hostname) date=$(date) python=$($PY -V 2>&1)"
$PY -m py_compile 3rdJ_09F_smoke_delta.py || { echo "FATAL: does not compile"; exit 1; }

$PY -u 3rdJ_09F_smoke_delta.py "$CAMP/out_F_f8fix/campaign_456301f5" "$CAMP/out_E_dhwvol/campaign_56d6e324"
echo "  exit=$?"

echo ""
echo "### arm-E Y2022 provenance: how many DHWv2 schedules did the PRE-FIX injector make?"
EPROV=$CAMP/out_E_dhwvol/campaign_56d6e324/Y2022__Tall__MTL/injected.idf.provenance.txt
grep -c "^t9_13_derived_name " $EPROV
grep "^t9_13_derived_name " $EPROV | grep -v "_HH"
echo "--- and its modulated-schedule / audit lines ---"
grep -E "^t9_13_|^n_dhw_" $EPROV | grep -v "_HH" | head -20
echo "  (if that list is empty, the pre-fix provenance did not record derived names)"

echo "delta done: $(date)"
