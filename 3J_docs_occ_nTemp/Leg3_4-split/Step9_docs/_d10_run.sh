#!/bin/bash
# V2-D10: 3-cell r-grid probe of the PER-OBJECT resize (LAUNDRY alone at K=7, all else K=1).
# Local win32 run. Not a campaign: the smallest set that can produce LAUNDRY's own slope.
set -u
# 2026-08-07: repertoires de sortie deplaces vers $BASE/_local_runs/ ; chemins rebases, contenu des runs inchange.
BASE="C:/Users/o_iseri/Desktop/GSSCanada"
export REPO="$BASE/GSSCanada-main"
export EPLUS_IDD="C:/EnergyPlusV24-2-0/Energy+.idd"
export EPLUS_EXE="C:/EnergyPlusV24-2-0/energyplus.exe"
EPW="$REPO/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
CELLSC="$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_resize_campaign_cell.py"
SPEC="Laundry Service Water Use 30.6gpm 180F=7"
OUT="$BASE/_local_runs/_local_D10_K7laundry"
mkdir -p "$OUT"
LOG="$OUT/_run.log"
echo "=== D10 per-object probe start $(date) ===" >> "$LOG"
echo "spec: $SPEC   default K=1" >> "$LOG"
for c in B_cons B_central B_opt; do
  cell="$BASE/_local_runs/_local_armH_cells/${c}__Tall__MTL"
  dst="$OUT/${c}__Tall__MTL"
  echo "--- $c $(date) ---" >> "$LOG"
  py "$CELLSC" "$cell" "$dst" "$EPW" 1.0 "$SPEC" > "$dst.log" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then echo "ok   $c" >> "$LOG"; else echo "FAIL $c rc=$rc" >> "$LOG"; tail -20 "$dst.log" >> "$LOG"; fi
done
echo "=== done $(date) ===" >> "$LOG"
