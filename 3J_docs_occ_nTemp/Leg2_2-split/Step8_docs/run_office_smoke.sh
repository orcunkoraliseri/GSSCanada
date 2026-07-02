#!/bin/bash
# run_office_smoke.sh — Step 8C: validate the office schedule-injection fix (3J Leg-2)
#
# Re-runs ONE cell for two contrasting scenarios (observed vs fullyhybrid) with the
# fixed office_integration.py, into a throwaway smoke dir, and prints the three
# acceptance checks:
#   (1) provenance n_office_zones > 0  (zone routing now works)
#   (2) hourly_meters.csv DIFFERS between the two bands (E+ now sees the modulation)
#   (3) the OpenOffice People object references OFC_People_* (field fix works)
#
# User: sbatch /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/run_office_smoke.sh

#SBATCH --job-name=3J_8C_smoke
#SBATCH -p ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/8C_smoke_%j.out

SCRATCH=/speed-scratch/o_iseri/step8_2split
PY=/speed-scratch/o_iseri/envs/step4/bin/python
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs
SMOKE=$SCRATCH/office_smoke
CELL=Office_Knowledge__SuperTall__6A

mkdir -p "$SCRATCH/logs"
$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }
export EPLUS_IDD=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd
export EPLUS_SIF="$SIF"
export MPLBACKEND=Agg

echo "=== 8C SMOKE (fixed office_integration) $(date) node=$(hostname) ==="
cd "$STEP8_DIR"
$PY -m py_compile office_integration.py office_runner.py || { echo "FATAL: py_compile failed"; exit 1; }
echo "  py_compile OK"

# fresh smoke dir so --no-skip definitely re-runs both cells
rm -rf "$SMOKE"

for SCEN in 2022 2030-fullyhybrid; do
  echo "--- smoke cell: Office_Knowledge SuperTall 6A $SCEN ---"
  $PY office_runner.py --archetype Office_Knowledge --envelope SuperTall --cz 6A \
      --scenario "$SCEN" --out-dir "$SMOKE" --no-skip
done

echo ""
echo "=== CHECK 1 — PROVENANCE (n_office_zones must be > 0) ==="
echo "[2022]";            cat "$SMOKE/$CELL/2022"/*.provenance.txt
echo "[2030-fullyhybrid]"; cat "$SMOKE/$CELL/2030-fullyhybrid"/*.provenance.txt

echo ""
echo "=== CHECK 2 — OUTPUT DIFF (must now DIFFER across bands) ==="
A="$SMOKE/$CELL/2022/hourly_meters.csv"
B="$SMOKE/$CELL/2030-fullyhybrid/hourly_meters.csv"
if [ -f "$A" ] && [ -f "$B" ]; then
  if cmp -s "$A" "$B"; then echo "HOURLY_IDENTICAL  <-- FIX FAILED"; else echo "HOURLY_DIFFER  <-- fix working"; fi
else
  echo "MISSING hourly_meters.csv (A=$([ -f "$A" ] && echo y || echo n) B=$([ -f "$B" ] && echo y || echo n))"
fi

echo ""
echo "=== CHECK 3 — PEOPLE WIRING (OpenOffice People should ref OFC_People_*) ==="
IDF="$SMOKE/$CELL/2030-fullyhybrid/Office_Office_Knowledge_SuperTall_6A_2030-fullyhybrid.idf"
grep -n -A4 "OpenOffice People" "$IDF" | head -20

echo ""
echo "  smoke done: $(date)"
