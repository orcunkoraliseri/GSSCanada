#!/encs/bin/bash
#SBATCH --job-name=s9_rerun
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_rerun_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_rerun_%j.err

# Step 9 targeted re-run: scan manifest for missing hourly_meters.csv and run E+ serially.
# Expected: ~10 missing IDFs across 5 cell×arm buckets.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

GCMAIN=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main
ROOT=/speed-scratch/o_iseri/step9_run
SIF=/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif
EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
SEXEC="singularity exec --bind /speed-scratch $SIF"
PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
EXTRACT=$GCMAIN/2J_docs_occ_nTemp/Step9_docs/cluster_spike/extract_meters.py
MANIFEST=$ROOT/step9_manifest.csv

echo "=== Step 9 missing-run re-run | job=${SLURM_JOB_ID} ==="
echo "Node: $(hostname)  Date: $(date)"

run_one_ep() {
    local IDF_PATH=$1
    local EPW_PATH=$2
    local OUT_DIR
    OUT_DIR=$(dirname "$IDF_PATH")
    local LABEL
    LABEL=$(echo "$OUT_DIR" | awk -F/ '{print $(NF-3)"/"$(NF-2)"/"$(NF-1)"/"$NF}')

    if [ -f "$OUT_DIR/hourly_meters.csv" ]; then
        echo "  SKIP (already done): $LABEL"
        return 0
    fi

    echo "  RUNNING: $LABEL"
    cp "$IDF_PATH" "$OUT_DIR/in.idf"
    $SEXEC cat ${EP_BIN}/Energy+.idd > "$OUT_DIR/Energy+.idd"

    cd "$OUT_DIR"
    $SEXEC "${EP_BIN}/ExpandObjects"
    if [ -f "$OUT_DIR/expanded.idf" ]; then IDF_RUN="$OUT_DIR/expanded.idf"
    else IDF_RUN="$OUT_DIR/in.idf"; fi

    $SEXEC "${EP_BIN}/energyplus" -d "$OUT_DIR" -w "$EPW_PATH" "$IDF_RUN"
    EP_RC=$?
    if [ $EP_RC -ne 0 ]; then echo "  E+ FAIL ($EP_RC): $LABEL"; return 1; fi
    if [ ! -f "$OUT_DIR/eplusout.end" ]; then echo "  FAIL (no .end): $LABEL"; return 1; fi

    SEVERE=$(grep -c "\*\* Severe" "$OUT_DIR/eplusout.err" 2>/dev/null || echo 0)
    if [ "$SEVERE" -gt 0 ]; then echo "  FAIL ($SEVERE Severe): $LABEL"; return 1; fi

    $PYTHON "$EXTRACT" "$OUT_DIR/eplusout.sql" "$OUT_DIR/hourly_meters.csv"
    if [ $? -ne 0 ]; then echo "  FAIL (extract): $LABEL"; return 1; fi

    echo "  DONE: $LABEL"
    return 0
}

FOUND=0
DONE=0
FAIL=0

while IFS=',' read -r _IDX _CELL _TRT _HH _YEAR IDF_PATH EPW_RAW; do
    EPW=$(echo "$EPW_RAW" | tr -d '\r' | sed 's|/nfs/speed-scratch/|/speed-scratch/|g')
    OUT_DIR=$(dirname "$IDF_PATH")
    if [ ! -f "$OUT_DIR/hourly_meters.csv" ]; then
        FOUND=$((FOUND + 1))
        run_one_ep "$IDF_PATH" "$EPW"
        RC=$?
        if [ $RC -eq 0 ]; then DONE=$((DONE + 1)); else FAIL=$((FAIL + 1)); fi
    fi
done < <(tail -n +2 "$MANIFEST")

echo ""
echo "=== Re-run complete: found=$FOUND  succeeded=$DONE  failed=$FAIL ==="
echo "Date: $(date)"
