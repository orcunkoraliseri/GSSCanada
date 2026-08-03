#!/bin/bash
# 3J Leg-3 Step 9 -- ARM H, 56 cells. The post-FINDING-6/7/8/9 campaign. sbatch only.
#
#   arm H (tasks 0-55)  --lighting-model calibrated_v2 --dhw-model volume_scaled
#
# Same two model flags as arm E, so H - E isolates the four fixes and nothing else. What differs
# from arm E is entirely upstream of the flags:
#
#   FINDING 6  office_presence_multiplier_2030.csv rebuilt on the matched stock frame  (575d17e5)
#   FINDING 7  retail 2030 product rewired to the calibrated _C_v2 pool                (3 CSVs)
#   FINDING 8  DHW schedule cache-key collision fixed  (injector 233932d7)
#   FINDING 9  per-day-type Saturday/Sunday loss fixed (injector 233932d7)
#
# Arms A-E all carry FINDING 9, so NO DHW number from them is comparable to this arm; that is the
# whole reason all 56 cells re-run rather than only the 36 stale 2030-family cells.
#
# User: sbatch /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08D_campaign_speed_armH.sh

#SBATCH --job-name=3J_L3_armH
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --array=0-55%20
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/campaign/logs/armH_%A_%a.out

CAMP=/speed-scratch/o_iseri/step8_4split/campaign
REPO=$CAMP/repo
PY=/speed-scratch/o_iseri/envs/step4/bin/python
S7=$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7

export ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export PYTHONPATH=$REPO

OUT=$CAMP/out_H_allfix
mkdir -p $CAMP/logs $OUT

CELL=$SLURM_ARRAY_TASK_ID
echo "=== arm H cell $CELL (lighting=calibrated_v2, dhw=volume_scaled) ==="
echo "  Node: $(hostname)  Date: $(date)"
echo "  outroot: $OUT"

$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
[ -x "$ENERGYPLUS_DIR/energyplus" ] || { echo "NO ENERGYPLUS at $ENERGYPLUS_DIR"; exit 1; }
[ -f "$EPLUS_IDD" ] || { echo "NO IDD at $EPLUS_IDD"; exit 1; }

# ---------------------------------------------------------------------------
# PROVENANCE GUARDS. Every one of them refuses rather than warns.
#
# INPUTS_HASH only protects a cell against a product that changed UNDER an existing outdir. A
# fresh outroot has no prior manifest, so it cannot tell a correct product from a stale one --
# it would happily run all 56 cells on the pre-FINDING-6/7 CSVs and record a self-consistent
# hash for them. These literals are the only thing standing between a stale cluster copy and a
# campaign that looks clean and is wrong. Checked on EVERY task, not just task 0: a partially
# completed scp would otherwise pass task 0 and corrupt the rest.
# ---------------------------------------------------------------------------
check_md5 () {  # $1 = path, $2 = expected md5, $3 = label
  if [ ! -f "$1" ]; then echo "FATAL: $3 missing at $1"; exit 1; fi
  GOT=$(md5sum "$1" | cut -d' ' -f1)
  if [ "$GOT" != "$2" ]; then
    echo "FATAL: $3 md5 mismatch"
    echo "       expected $2"
    echo "       got      $GOT"
    echo "       -> the cluster copy is STALE. Re-scp before launching; do NOT --allow-stale-inputs."
    exit 1
  fi
  echo "  [guard OK] $3 = ${GOT:0:8}"
}

check_md5 "$REPO/eSim_bem_utils/commercial_integration.py" \
          "233932d7b043dc54d3ad5a76cf2432bf" "injector (FINDING 8+9)"
check_md5 "$S7/office_presence_multiplier_2030.csv" \
          "575d17e55f32f8b5ec493ff590833d94" "office 2030 product (FINDING 6)"
check_md5 "$S7/retail_presence_multiplier_2030_cons.csv" \
          "82b425b51e077c6c45625a3ff0b0197c" "retail 2030 cons (FINDING 7)"
check_md5 "$S7/retail_presence_multiplier_2030_central.csv" \
          "11414644bf2c9fbb73664aab770c339e" "retail 2030 central (FINDING 7)"
check_md5 "$S7/retail_presence_multiplier_2030_opt.csv" \
          "700398d0980bd042015795f5ebb75c73" "retail 2030 opt (FINDING 7)"

# ---------------------------------------------------------------------------
# Compile under the CLUSTER interpreter. Local python is 3.13, this env is 3.10, and a
# multi-line f-string that compiled locally cost a full simulation round trip on 2026-08-02.
# ---------------------------------------------------------------------------
cd "$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs" || exit 1
for f in 3rdJ_08P_probe_driver.py 3rdJ_08D_campaign_driver.py 3rdJ_08D_campaign_cells.py; do
  $PY -m py_compile "$f" || { echo "FATAL: $f does not compile under $($PY -V 2>&1)"; exit 1; }
done
echo "  [guard OK] drivers compile under $($PY -V 2>&1)"

# T9-13 unit suite as a REAL gate, on every task.
#
# smoke_f9fix.sh ran this as `$PY ... | tail -3` and then reported `$?` -- which is TAIL's exit
# code, always 0. That line could not fail, whatever the suite did; it is vacuous-gate kind #2
# (the explanation that cannot fail) wearing a test's clothes. Fixed here by testing the suite's
# own status and refusing on it. Run on all 56 tasks rather than only task 0, because a gate that
# guards one cell out of 56 does not guard the campaign -- and the suite costs seconds.
$PY -u $REPO/eSim_tests/test_t9_13.py > /tmp/t9_13_unit_$$.log 2>&1
URC=$?
tail -3 /tmp/t9_13_unit_$$.log
rm -f /tmp/t9_13_unit_$$.log
if [ $URC -ne 0 ]; then
  echo "FATAL: T9-13 unit suite FAILED (exit $URC) -- refusing to simulate on a broken injector."
  exit 1
fi
echo "  [guard OK] T9-13 unit suite passed (exit 0)"

# Task 0 only: the things that are identical across all 56 cells and need saying once.
if [ "$CELL" = "0" ]; then
  echo "### task-0 one-time provenance"
  $PY -c "import sys; sys.path.insert(0,'$REPO'); import importlib.util as u; s=u.spec_from_file_location('p','3rdJ_08P_probe_driver.py'); m=u.module_from_spec(s); s.loader.exec_module(m); print('  OUTPUT_SCHEMA_HASH =', m.OUTPUT_SCHEMA_HASH, '(was db4e729f before the DHW volume variable)'); print('  DHW_VOLUME_VARIABLE =', m.DHW_VOLUME_VARIABLE)"
fi

$PY -u 3rdJ_08D_campaign_driver.py \
    --cell $CELL \
    --engine local \
    --repo-root "$REPO" \
    --outroot "$OUT" \
    --lighting-model calibrated_v2 \
    --dhw-model volume_scaled
RC=$?

echo "  arm H cell $CELL done, python exit=$RC: $(date)"
exit $RC
