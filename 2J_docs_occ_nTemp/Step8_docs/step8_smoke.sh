#!/encs/bin/bash
#SBATCH --job-name=step8_smoke
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/smoke_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs/smoke_%j.err

# Stage 0 smoke test: SingleD x Montreal_6A, N=3, year=2022 only.
# Gate: E+ runs clean (0 Severe), EUI in 250-272 kWh/m2 band,
# magnitude consistent with pre-bug local run (annual EUI is phase-robust).

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers
SMOKE_DIR=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke

mkdir -p "$SMOKE_DIR" /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/logs

echo "=== Step 8 corrected SMOKE | arch=SingleD city=Montreal_6A N=3 year=2022 ==="
echo "Start: $(date)"

# Pre-flight checks
singularity --version || { echo "ERROR: singularity not found on this node"; exit 1; }
$PYTHON -c "import eppy" 2>/dev/null || { echo "ERROR: eppy missing; run: $PYTHON -m pip install eppy"; exit 1; }
[ -f "$WRAPPER_DIR/Energy+.idd" ] || { echo "ERROR: Energy+.idd missing from $WRAPPER_DIR"; exit 1; }
[ -x "$WRAPPER_DIR/energyplus" ]  || { echo "ERROR: energyplus wrapper not executable in $WRAPPER_DIR"; exit 1; }

# Log CSV checksum for provenance
echo "MD5 BEM_Schedules_2022.csv: $(md5sum /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/BEM_Schedules_2022.csv)"

# Quick container test
echo "--- Container E+ version check ---"
singularity exec --bind /speed-scratch "$WRAPPER_DIR/../step9_spike/energyplus_24.2.0.sif" \
    /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus --version

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$WRAPPER_DIR/Energy+.idd"
export ESIM_WORKERS=4

cd "$STEP8_DIR"
$PYTHON run_paired_mc.py \
    --archetype SingleD \
    --city Montreal_6A \
    --n 3 \
    --seed 42 \
    --sim-mode standard \
    --years 2022 \
    --output-dir "$SMOKE_DIR/SingleD__Montreal_6A"

EXIT_CODE=$?
echo "End: $(date)  exit=$EXIT_CODE"

# Post-run: report EUI from any completed hourly_meters.csv
echo "--- Smoke results ---"
$PYTHON - <<'PYEOF'
import os, csv, glob
smoke = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
csvs = glob.glob(os.path.join(smoke, "**", "hourly_meters.csv"), recursive=True)
print(f"hourly_meters.csv files found: {len(csvs)}")
for path in sorted(csvs)[:3]:
    try:
        with open(path) as f:
            rows = list(csv.reader(f))
        if len(rows) > 1:
            header = rows[0]
            vals = [sum(float(r[i]) for r in rows[1:] if r[i]) for i in range(1, len(header))]
            annual_j = sum(vals)
            print(f"  {os.path.relpath(path, smoke)}: annual_total={annual_j/3.6e9:.1f} kWh (check vs floor area for EUI)")
    except Exception as e:
        print(f"  {path}: {e}")
PYEOF

exit $EXIT_CODE
