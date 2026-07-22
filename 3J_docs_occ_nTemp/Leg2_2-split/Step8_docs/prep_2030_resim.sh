#!/bin/bash
# prep_2030_resim.sh — archive (move) residential 2030 scenario subdirs out of
# campaign/ before the 2030-only re-sim. Doubles as (1) predecessor archive of the
# pre-mutex-fix 2030 results and (2) skip-done bypass (cell_is_done finds no
# 2030 hourly_meters.csv -> the array re-runs those cells). Office untouched
# (its 2030 input is md5-identical pre/post fix; office 2030 results unchanged).
#SBATCH --job-name=3J_prep_2030
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_2split/logs/prep_2030_%j.out

set -e
SCRATCH=/speed-scratch/o_iseri/step8_2split
ARCH=$SCRATCH/archive/campaign_2030_pre_mutexfix_20260717
mkdir -p "$ARCH"
mkdir -p "$SCRATCH/logs"

echo "=== BEFORE: resid 2030 leaf dirs in campaign/ ==="
find "$SCRATCH/campaign" -type d -path '*2030-*' -prune -print | wc -l

cd "$SCRATCH"
find campaign -type d -path '*2030-*' -prune -print0 | while IFS= read -r -d '' d; do
    mkdir -p "$ARCH/$(dirname "$d")"
    mv "$d" "$ARCH/$d"
done

echo "=== AFTER: resid 2030 leaf dirs remaining in campaign/ (want 0) ==="
find "$SCRATCH/campaign" -type d -path '*2030-*' -prune -print | wc -l
echo "=== archived resid 2030 leaf dirs (want 3600) ==="
find "$ARCH/campaign" -type d -path '*2030-*' -prune -print | wc -l
echo "PREP DONE"
