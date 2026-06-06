#!/encs/bin/bash
#SBATCH --job-name=s9_full_ep
#SBATCH --partition=ps
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --time=48:00:00
#SBATCH --array=0-47
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_full_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_full_%A_%a.err

# Stage B FULL — 48-task array: 24 cells x 2 treatments.
# 9,600-task per-IDF array exceeds SLURM MaxArraySize; consolidated to 48 tasks.
# Each task handles one (cell, treatment) pair: 50 HH x 2 years = 100 E+ runs.
# Up to 4 E+ runs in parallel per task (cpus-per-task=4).
# ONLY submit after step9_precheck_full.sh + smoke on OtherDwelling cell PASS.

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
MAX_PAR=4

# Task 0-23 = baseline x 24 cells; Task 24-47 = activity x 24 cells.
ARCHS=(SingleD SingleD SingleD SingleD SingleD SingleD \
       OtherDwelling OtherDwelling OtherDwelling OtherDwelling OtherDwelling OtherDwelling \
       MidRise MidRise MidRise MidRise MidRise MidRise \
       HighRise HighRise HighRise HighRise HighRise HighRise)
CITIES=(Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A \
        Toronto_5A Kelowna_5B Vancouver_5C Montreal_6A Calgary_6B Winnipeg_7A)

CELL_IDX=$((SLURM_ARRAY_TASK_ID % 24))
if [ $SLURM_ARRAY_TASK_ID -lt 24 ]; then
    TREATMENT="baseline"
else
    TREATMENT="activity"
fi
ARCH=${ARCHS[$CELL_IDX]}
CITY=${CITIES[$CELL_IDX]}
CELL="${ARCH}__${CITY}"

echo "=== Step 9 full array | job=${SLURM_ARRAY_JOB_ID} task=${SLURM_ARRAY_TASK_ID} | ${CELL}/${TREATMENT} ==="
echo "Node: $(hostname)  Date: $(date)"

# Count total + already-done for this task
TOTAL_THIS=$(awk -F',' -v c="$CELL" -v t="$TREATMENT" \
    'NR>1 && $2==c && $3==t {count++} END {print count+0}' "$MANIFEST")
echo "  IDFs in manifest for this task: $TOTAL_THIS  (expect 100)"

if [ "$TOTAL_THIS" -eq 0 ]; then
    echo "ERROR: no manifest rows for ${CELL}/${TREATMENT} — did Stage A run?"
    exit 1
fi

run_one_ep() {
    local IDF_PATH=$1
    local EPW_PATH=$2
    local OUT_DIR
    OUT_DIR=$(dirname "$IDF_PATH")
    local LABEL="${CELL}/${TREATMENT}/$(basename "$(dirname "$OUT_DIR")")/$(basename "$OUT_DIR")"

    if [ -f "$OUT_DIR/hourly_meters.csv" ]; then
        echo "  SKIP (done): $LABEL"
        return 0
    fi

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

NRUN=0
while IFS=',' read -r _IDX _CELL _TRT _HH _YEAR IDF_PATH EPW_RAW; do
    EPW=$(echo "$EPW_RAW" | tr -d '\r' | sed 's|/nfs/speed-scratch/|/speed-scratch/|g')
    run_one_ep "$IDF_PATH" "$EPW" &
    NRUN=$((NRUN + 1))
    while [ "$(jobs -rp | wc -l)" -ge $MAX_PAR ]; do sleep 5; done
done < <(awk -F',' -v c="$CELL" -v t="$TREATMENT" 'NR>1 && $2==c && $3==t' "$MANIFEST")

wait

DONE_NOW=$(awk -F',' -v c="$CELL" -v t="$TREATMENT" \
    'NR>1 && $2==c && $3==t {print $6}' "$MANIFEST" | \
    while read -r IDF; do
        [ -f "$(dirname "$IDF")/hourly_meters.csv" ] && echo done
    done | wc -l)

echo ""
echo "=== Task $SLURM_ARRAY_TASK_ID COMPLETE: ${CELL}/${TREATMENT} ==="
echo "  Launched: $NRUN   Done hourly_meters: $DONE_NOW / $TOTAL_THIS"
echo "  Date: $(date)"
