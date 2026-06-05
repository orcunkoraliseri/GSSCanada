#!/encs/bin/bash
#SBATCH --job-name=s9_ep
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --array=0-239
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_ep_%A_%a.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_ep_%A_%a.err

# Phase 4 — Full SLURM array: 240 tasks (3 cells × 20 HH × 2 yr × 2 treatments).
# Each task: ExpandObjects + EnergyPlus + extract_meters.py for one IDF.
# ONLY submit after smoke test passes.

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
TASK_IDX=$SLURM_ARRAY_TASK_ID

echo "=== Step 9 array task $TASK_IDX ==="
echo "Node: $(hostname)  Date: $(date)"

MANIFEST_ROW=$(awk -F',' -v idx=$TASK_IDX 'NR > 1 && $1 == idx' "$MANIFEST")
if [ -z "$MANIFEST_ROW" ]; then
    echo "ERROR: no manifest row for idx=$TASK_IDX"
    exit 1
fi

IDF_PATH=$(echo "$MANIFEST_ROW" | cut -d',' -f6)
EPW_PATH=$(echo "$MANIFEST_ROW" | cut -d',' -f7 | tr -d '\r' | sed 's|/nfs/speed-scratch/|/speed-scratch/|g')
CELL=$(echo     "$MANIFEST_ROW" | cut -d',' -f2)
TREATMENT=$(echo "$MANIFEST_ROW" | cut -d',' -f3)
HH_ID=$(echo    "$MANIFEST_ROW" | cut -d',' -f4)
YEAR=$(echo     "$MANIFEST_ROW" | cut -d',' -f5)
OUT_DIR=$(dirname "$IDF_PATH")

echo "  $CELL / $TREATMENT / HH=$HH_ID / $YEAR"

# Idempotent: skip if already complete
if [ -f "$OUT_DIR/hourly_meters.csv" ]; then
    echo "  Already done — skipping."
    exit 0
fi

cp "$IDF_PATH" "$OUT_DIR/in.idf"
$SEXEC cat ${EP_BIN}/Energy+.idd > "$OUT_DIR/Energy+.idd"

cd "$OUT_DIR"
$SEXEC "${EP_BIN}/ExpandObjects"
if [ -f "$OUT_DIR/expanded.idf" ]; then IDF_RUN="$OUT_DIR/expanded.idf"
else IDF_RUN="$OUT_DIR/in.idf"; fi

$SEXEC "${EP_BIN}/energyplus" -d "$OUT_DIR" -w "$EPW_PATH" "$IDF_RUN"
EP_RC=$?
echo "  E+ exit: $EP_RC"
[ $EP_RC -ne 0 ] && echo "FAIL: E+ non-zero" && exit 1
[ ! -f "$OUT_DIR/eplusout.end" ] && echo "FAIL: no eplusout.end" && exit 1
cat "$OUT_DIR/eplusout.end"

SEVERE=$(grep -c "\*\* Severe" "$OUT_DIR/eplusout.err" 2>/dev/null || echo 0)
[ "$SEVERE" -gt 0 ] && echo "FAIL: $SEVERE Severe errors" && exit 1

$PYTHON "$EXTRACT" "$OUT_DIR/eplusout.sql" "$OUT_DIR/hourly_meters.csv"
[ $? -ne 0 ] && echo "FAIL: extraction failed" && exit 1

echo "=== Task $TASK_IDX COMPLETE ==="
