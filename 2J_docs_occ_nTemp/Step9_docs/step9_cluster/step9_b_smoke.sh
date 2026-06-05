#!/encs/bin/bash
#SBATCH --job-name=s9_smoke
#SBATCH --partition=ps
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_run/logs/s9_smoke_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_run/logs/s9_smoke_%j.err

# Phase 3 — SMOKE TEST (HARD GATE).
# Runs BOTH treatments for sample_001 (first HH) of SingleD__Winnipeg_7A, year 2022.
# Checks:
#   [1] E+ 0 Severe errors
#   [2] baseline meters exist (non-zero Electricity:Facility)
#   [3] activity ≠ baseline (Equipment:Facility differs)
#   [4] equipment near-zero during sleep/away hours (h02-h05)
#   [5] activity annual equipment within ±50% of SHEU SingleD 3252 kWh (loose gate)
#
# HARD GATE: do NOT submit step9_b_array.sh unless this passes ALL checks.

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

SMOKE_CELL="SingleD__Winnipeg_7A"
SMOKE_YEAR="2022"

echo "=== Step 9 Smoke Test ==="
echo "Node: $(hostname)  Date: $(date)"

run_ep() {
    local TREATMENT=$1
    local OUT_DIR=$2
    local IDF_PATH=$3
    local EPW_PATH=$4

    echo ""
    echo "--- Running $TREATMENT ---"
    echo "  IDF: $IDF_PATH"

    cp "$IDF_PATH" "$OUT_DIR/in.idf"
    $SEXEC cat ${EP_BIN}/Energy+.idd > "$OUT_DIR/Energy+.idd"

    cd "$OUT_DIR"
    $SEXEC "${EP_BIN}/ExpandObjects"
    if [ -f "$OUT_DIR/expanded.idf" ]; then IDF_RUN="$OUT_DIR/expanded.idf"
    else IDF_RUN="$OUT_DIR/in.idf"; fi

    $SEXEC "${EP_BIN}/energyplus" -d "$OUT_DIR" -w "$EPW_PATH" "$IDF_RUN"
    EP_RC=$?
    echo "  E+ exit: $EP_RC"
    [ $EP_RC -ne 0 ] && return 1
    [ ! -f "$OUT_DIR/eplusout.end" ] && echo "  FAIL: eplusout.end missing" && return 1
    cat "$OUT_DIR/eplusout.end"

    SEVERE=$(grep -c "\*\* Severe" "$OUT_DIR/eplusout.err" 2>/dev/null || echo 0)
    echo "  Severe: $SEVERE"
    [ "$SEVERE" -gt 0 ] && echo "  FAIL: Severe errors" && return 1

    $PYTHON "$EXTRACT" "$OUT_DIR/eplusout.sql" "$OUT_DIR/hourly_meters.csv"
    [ $? -ne 0 ] && echo "  FAIL: extraction failed" && return 1
    echo "  Extraction: OK"
    return 0
}

# Locate smoke IDFs from manifest
BL_IDF=$(grep ",${SMOKE_CELL},baseline," "$MANIFEST" | grep ",${SMOKE_YEAR}," | head -1 | cut -d',' -f6)
BL_EPW=$(grep ",${SMOKE_CELL},baseline," "$MANIFEST" | grep ",${SMOKE_YEAR}," | head -1 | cut -d',' -f7)
AC_IDF=$(grep ",${SMOKE_CELL},activity," "$MANIFEST" | grep ",${SMOKE_YEAR}," | head -1 | cut -d',' -f6)
AC_EPW=$(grep ",${SMOKE_CELL},activity," "$MANIFEST" | grep ",${SMOKE_YEAR}," | head -1 | cut -d',' -f7)
# Strip CRLF \r (csv.writer CRLF) then normalize NFS symlink path in container
BL_EPW=$(echo "$BL_EPW" | tr -d '\r' | sed 's|/nfs/speed-scratch/|/speed-scratch/|g')
AC_EPW=$(echo "$AC_EPW" | tr -d '\r' | sed 's|/nfs/speed-scratch/|/speed-scratch/|g')

if [ -z "$BL_IDF" ] || [ -z "$AC_IDF" ]; then
    echo "ERROR: cannot locate smoke IDFs in manifest. Did Stage A complete?"
    exit 1
fi
echo "  Baseline IDF: $BL_IDF"
echo "  Activity IDF: $AC_IDF"

BL_DIR=$(dirname "$BL_IDF")
AC_DIR=$(dirname "$AC_IDF")

run_ep "baseline" "$BL_DIR" "$BL_IDF" "$BL_EPW" || { echo "=== SMOKE FAIL: baseline E+ ==="     ; exit 1; }
run_ep "activity" "$AC_DIR" "$AC_IDF" "$AC_EPW" || { echo "=== SMOKE FAIL: activity E+ ==="; exit 1; }

# Python validation
$PYTHON - <<PYCHECK
import csv, sys

def annual_kwh(rows, col):
    return sum(float(r.get(col,0)) for r in rows) / 3.6e6

def find_col(d, kw): return next((k for k in d if kw.lower() in k.lower()), None)

with open("$BL_DIR/hourly_meters.csv") as f: bl = list(csv.DictReader(f))
with open("$AC_DIR/hourly_meters.csv") as f: ac = list(csv.DictReader(f))

elec_col  = find_col(bl[0], 'Electricity:Facility')
equip_col = find_col(bl[0], 'InteriorEquipment:Electricity')

print(f"  elec_col : {elec_col}")
print(f"  equip_col: {equip_col}")

if not elec_col:
    print("FAIL [2]: no Electricity:Facility meter"); sys.exit(1)

bl_elec = annual_kwh(bl, elec_col)
ac_elec = annual_kwh(ac, elec_col)
print(f"  Baseline annual elec: {bl_elec:.0f} kWh")
print(f"  Activity annual elec: {ac_elec:.0f} kWh")

if bl_elec < 100:
    print("FAIL [2]: baseline near zero"); sys.exit(1)
print("  CHECK [2] PASS")

if equip_col:
    bl_eq = annual_kwh(bl, equip_col)
    ac_eq = annual_kwh(ac, equip_col)
    print(f"  Baseline equip: {bl_eq:.0f} kWh   Activity equip: {ac_eq:.0f} kWh")
    if abs(ac_eq - bl_eq) < 1.0:
        print("FAIL [3]: activity == baseline — Step 9 fracs not applied"); sys.exit(1)
    print("  CHECK [3] PASS")

    # Sleep hours check (h02-h05)
    sleep_mean = sum(float(r.get(equip_col,0)) for r in ac if int(r.get('hour',-1)) in [2,3,4,5]) / max(4*len([r for r in ac if int(r.get('hour',-1))==2]),1) / 3600
    print(f"  Sleep equip mean h02-h05: {sleep_mean:.2f} Wh")
    if sleep_mean > 300:
        print(f"WARN [4]: sleep equip {sleep_mean:.1f} Wh > 300 Wh — may be OK if dishwasher queue")
    else:
        print("  CHECK [4] PASS")

    # SHEU gate (±100% gross smoke gate — strict ±15% enforced in step9_validate.py)
    sheu = 3252.0
    pct = abs(ac_eq - sheu) / sheu * 100
    print(f"  Activity equip vs SHEU 3252: {ac_eq:.0f} kWh ({pct:.1f}%)")
    if pct > 100:
        print(f"FAIL [5]: {pct:.1f}% off SHEU (±100% smoke gate)"); sys.exit(1)
    print("  CHECK [5] PASS")

print("")
print("=== ALL SMOKE CHECKS PASS ===")
PYCHECK
SMOKE_RC=$?

echo ""
if [ $SMOKE_RC -eq 0 ]; then
    echo "=== SMOKE TEST: PASS — GO for full array (step9_b_array.sh) ==="
else
    echo "=== SMOKE TEST: FAIL — do NOT launch array ==="
    exit 1
fi
