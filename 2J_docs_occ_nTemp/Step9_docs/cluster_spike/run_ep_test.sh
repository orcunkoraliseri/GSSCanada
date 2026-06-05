#!/encs/bin/bash
#SBATCH --job-name=ep_container_test
#SBATCH --partition=ps    # CPU partition; verify with `sinfo` on login node (may be `sp` or omit)
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/step9_spike/logs/ep_test_%j.out
#SBATCH --error=/speed-scratch/o_iseri/step9_spike/logs/ep_test_%j.err

# Container validation spike: E+ 24.2.0 in Singularity vs local Windows run.
# Reference: SingleD x Winnipeg_7A, HH77448, year 2022.
# Gate: hourly_meters_container.csv annual end-uses must match local within 0.5%.

. /encs/pkg/modules-5.3.1/root/init/bash
module load singularity/3.10.4

SPIKE=/speed-scratch/o_iseri/step9_spike
SIF="$SPIKE/energyplus_24.2.0.sif"
WORK="$SPIKE/output"
IDF="$SPIKE/Scenario_2022.idf"
EPW="$SPIKE/Winnipeg.epw"

echo "=== ep_container_test START ==="
echo "Node: $(hostname)  Date: $(date)"

if [ ! -f "$SIF" ]; then
    echo "ERROR: $SIF not found — run pull_sif.sh first"
    exit 1
fi
if [ ! -f "$IDF" ]; then
    echo "ERROR: $IDF not found — upload not complete"
    exit 1
fi
if [ ! -f "$EPW" ]; then
    echo "ERROR: $EPW not found — upload not complete"
    exit 1
fi

mkdir -p "$WORK"

EP_BIN=/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64
SEXEC="singularity exec --bind /speed-scratch $SIF"

echo "=== Copying IDF + Energy+.idd to work dir ==="
cp "$IDF" "$WORK/in.idf"
$SEXEC cat "${EP_BIN}/Energy+.idd" > "$WORK/Energy+.idd"
echo "Energy+.idd size: $(wc -c < $WORK/Energy+.idd) bytes"

echo "=== Running ExpandObjects in container (CWD: $WORK) ==="
cd "$WORK"
$SEXEC "${EP_BIN}/ExpandObjects"
if [ -f "$WORK/expanded.idf" ]; then
    IDF_RUN="$WORK/expanded.idf"
    echo "expanded.idf created ($(wc -c < $WORK/expanded.idf) bytes) — using it"
else
    IDF_RUN="$WORK/in.idf"
    echo "expanded.idf not found — using in.idf directly (HVACTemplate expansion may fail)"
fi

echo "=== Running EnergyPlus 24.2.0 in container ==="
$SEXEC "${EP_BIN}/energyplus" -d "$WORK" -w "$EPW" "$IDF_RUN"
EP_RC=$?
echo "energyplus exit code: $EP_RC"

if [ $EP_RC -ne 0 ]; then
    echo "ERROR: energyplus exited non-zero"
    exit 1
fi

if [ ! -f "$WORK/eplusout.end" ]; then
    echo "ERROR: eplusout.end missing — E+ did not complete"
    exit 1
fi

echo "=== eplusout.end ==="
cat "$WORK/eplusout.end"

echo "=== Extracting hourly meters from SQL (host step4 Python — no standalone python3 in NREL image) ==="
/speed-scratch/o_iseri/envs/step4/bin/python "$SPIKE/extract_meters.py" "$WORK/eplusout.sql" "$WORK/hourly_meters_container.csv"
EXT_RC=$?
echo "extract_meters exit code: $EXT_RC"

if [ $EXT_RC -ne 0 ]; then
    echo "ERROR: meter extraction failed"
    exit 1
fi

echo "=== Container test COMPLETE ==="
echo "Output: $WORK/hourly_meters_container.csv"
echo "Download it locally, then run: python compare_meters.py hourly_meters_local.csv hourly_meters_container.csv"
