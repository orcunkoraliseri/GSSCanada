#!/bin/bash
# 3J Leg-3 Step 8 -- disk guard + archive of the 4 stale probe-cell output dirs
# ahead of the post-retail-fix re-simulation (sbatch only; nothing runs on the login node).
#SBATCH --job-name=3J_8P_archive
#SBATCH -p ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 7-00:00:00
#SBATCH --output=/speed-scratch/o_iseri/step8_4split/logs/8P_archive_%j.out

CAMPAIGN=/speed-scratch/o_iseri/step8_4split/probes/campaign_5670f602
MIN_FREE_GB=5

echo "=== 8P archive+disk-guard start ==="
date
echo "  Node: $(hostname)"

echo "--- disk free on /speed-scratch/o_iseri ---"
df -h /speed-scratch/o_iseri
FREE_GB=$(df -BG --output=avail /speed-scratch/o_iseri | tail -1 | tr -dc '0-9')
echo "  Free space (GB, integer floor): $FREE_GB"

if [ -z "$FREE_GB" ] || [ "$FREE_GB" -lt "$MIN_FREE_GB" ]; then
    echo "[FAIL] free space ${FREE_GB}GB is below the ${MIN_FREE_GB}GB floor -- refusing to proceed (re-sim adds ~1.15GB on top of retained old outputs)"
    exit 1
fi
echo "[ok] free space ${FREE_GB}GB >= ${MIN_FREE_GB}GB floor -- proceeding"

echo "--- archiving (rename, not copy) ---"
for tag in B_central var_office var_retail var_hotel; do
    SRC="$CAMPAIGN/$tag"
    DST="$CAMPAIGN/${tag}_PRE_RETAILFIX_20260728"
    if [ -d "$SRC" ]; then
        mv "$SRC" "$DST"
        echo "  renamed $SRC -> $DST"
    else
        echo "  [WARN] source dir missing, nothing to rename: $SRC"
    fi
done

echo "--- listing for proof ---"
ls -la "$CAMPAIGN"

echo "=== 8P archive+disk-guard end ==="
date
