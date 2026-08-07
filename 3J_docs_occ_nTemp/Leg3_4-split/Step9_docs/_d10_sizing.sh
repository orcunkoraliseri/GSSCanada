#!/bin/bash
# V2-D10: campaign-wide peak-draw sizing for the LAUNDRY heater, read off arm K1's existing ESOs.
# No simulation. Volume is a demand-side quantity, so K1's draw is the draw at every K.
set -u
# 2026-08-07: repertoires de sortie deplaces vers $BASE/_local_runs/ ; chemins rebases, contenu des runs inchange.
BASE="C:/Users/o_iseri/Desktop/GSSCanada"
SC="$BASE/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09H_peak_draw_sizing.py"
OUT="$BASE/_local_runs/_local_D10_K7laundry/_sizing_all56.log"
echo "=== campaign-wide LAUNDRY sizing from _local_K16/K1 ESOs  $(date) ===" > "$OUT"
for d in "$BASE"/_local_runs/_local_K16/K1/*/; do
  c=$(basename "$d")
  py "$SC" "$d" --equip "Laundry Service Water Use 30.6gpm 180F" --current-w 87921.3210516667 \
     >> "$OUT" 2>&1 || echo "  !! $c refused" >> "$OUT"
done
echo "=== done $(date) ===" >> "$OUT"
