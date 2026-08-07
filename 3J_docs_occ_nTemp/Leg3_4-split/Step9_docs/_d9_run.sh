#!/bin/bash
# V2-D9: retail -> NECB `Retail - sales` (density 24.97 -> 29.97 m2/person, NECB-A -> NECB-C).
# 3 injected Tall__MTL cells + the uninjected Default_NECB control, which is the cell where the
# A->C swap reaches all four retail ZoneLists instead of one. Local win32. K = 1 (no DHW resize).
set -u
# 2026-08-07: repertoires de sortie deplaces vers $BASE/_local_runs/ ; chemins rebases, contenu des runs inchange.
BASE="C:/Users/o_iseri/Desktop/GSSCanada"
export REPO="$BASE/GSSCanada-main"
export EPLUS_IDD="C:/EnergyPlusV24-2-0/Energy+.idd"
export EPLUS_EXE="C:/EnergyPlusV24-2-0/energyplus.exe"
EPW="$REPO/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw"
SD="$REPO/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs"
OUT="$BASE/_local_runs/_local_D9_necbC"
STAGE="$OUT/_staged"
mkdir -p "$STAGE"
LOG="$OUT/_run.log"
echo "=== D9 NECB-C retail probe start $(date) ===" >> "$LOG"
for c in B_cons B_central B_opt Default_NECB; do
  src="$BASE/_local_runs/_local_armH_cells/${c}__Tall__MTL"
  stg="$STAGE/${c}__Tall__MTL"
  dst="$OUT/${c}__Tall__MTL"
  rm -rf "$stg"; mkdir -p "$stg"
  cp "$src/manifest.json" "$stg/" 2>/dev/null
  cp "$src/injected.idf.provenance.txt" "$stg/" 2>/dev/null
  echo "--- $c $(date) ---" >> "$LOG"
  py "$SD/3rdJ_09J_retail_necb_c.py" "$src/injected.idf" "$stg/injected.idf" --verify >> "$LOG" 2>&1
  if [ $? -ne 0 ]; then echo "FAIL convert $c" >> "$LOG"; continue; fi
  py "$SD/3rdJ_09H_resize_campaign_cell.py" "$stg" "$dst" "$EPW" 1.0 > "$dst.log" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then echo "ok   $c" >> "$LOG"; else echo "FAIL run $c rc=$rc" >> "$LOG"; tail -20 "$dst.log" >> "$LOG"; fi
done
echo "=== done $(date) ===" >> "$LOG"
