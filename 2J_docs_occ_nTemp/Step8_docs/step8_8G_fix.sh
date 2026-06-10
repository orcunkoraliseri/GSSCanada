#!/encs/bin/bash
#SBATCH --job-name=s8_8G_fix
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/s8_8G_fix_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/s8_8G_fix_%j.err

# Sub-step 8G: single-run fix for OtherDwelling x Kelowna_5B / sample_050_HH145979 / 2010
# Fix applied: DX Cooling Coil_unit6 Gross Rated SHR autosize -> 0.75 (negative bypass factor)
# Runs the ISOLATED expanded.idf copy in step8_8G_fix/ (never touches campaign or Buildings_MTL_v242)

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers
IDD=/speed-scratch/o_iseri/ep_wrappers/Energy+.idd
EPW=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/WeatherFile/CAN_BC_Kelowna.Intl.AP.712030_TMYx_5B.epw
FIX_DIR=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/step8_8G_fix/OtherDwelling__Kelowna_5B__sample_050_HH145979__2010
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs

echo "=== step8_8G_fix.sh job=$SLURM_JOB_ID node=$SLURMD_NODENAME $(date) ==="
echo "FIX_DIR=$FIX_DIR"

# Pre-flight checks
[ -f "$FIX_DIR/expanded.idf" ] || { echo "FATAL: fixed expanded.idf not found"; exit 1; }
[ -f "$EPW" ]                   || { echo "FATAL: EPW not found: $EPW"; exit 1; }
[ -f "$IDD" ]                   || { echo "FATAL: IDD not found: $IDD"; exit 1; }
[ -x "$WRAPPER_DIR/energyplus" ] || { echo "FATAL: energyplus wrapper not executable"; exit 1; }
$PYTHON -c "import eppy" || { echo "FATAL: eppy missing"; exit 1; }

# Verify fix was applied (SHR = 0.75, not autosize)
python3 -c "
import re, sys
with open('$FIX_DIR/expanded.idf') as f:
    content = f.read()
m = re.search(r'DX Cooling Coil_unit6,\s*!\- Name.*?Gross Rated Sensible Heat Ratio', content, re.DOTALL)
if m and '0.75' in m.group():
    print('FIX VERIFIED: SHR=0.75 for unit6')
else:
    print('ERROR: fix not found or autosize still present')
    sys.exit(1)
"
[ $? -ne 0 ] && exit 1

export ENERGYPLUS_DIR="$WRAPPER_DIR"
export IDD_FILE="$IDD"

# Run E+ directly on the fixed expanded.idf (no ExpandObjects step needed -- already expanded)
cd "$FIX_DIR"
echo "Running E+ on fixed IDF: $(date)"
"$WRAPPER_DIR/energyplus" -w "$EPW" -i "$IDD" -d "$FIX_DIR" "$FIX_DIR/expanded.idf"
EP_EXIT=$?
echo "E+ exit=$EP_EXIT  $(date)"

tail -3 "$FIX_DIR/eplusout.end" || echo "No eplusout.end generated"

if [ $EP_EXIT -ne 0 ]; then
    echo "E+ FAILED (exit=$EP_EXIT) -- check eplusout.err"
    tail -20 "$FIX_DIR/eplusout.err"
    exit $EP_EXIT
fi

# Check success string
if ! grep -q "EnergyPlus Completed Successfully" "$FIX_DIR/eplusout.end"; then
    echo "E+ did not complete successfully -- see eplusout.end"
    cat "$FIX_DIR/eplusout.end"
    exit 1
fi

echo "E+ PASSED -- extracting hourly_meters.csv"

# Extract hourly_meters.csv from eplusout.sql using host Python
cd "$STEP8_DIR"
$PYTHON - << 'PYEOF'
import sqlite3, csv, sys, os
sys.path.insert(0, '/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs')
from eSim_bem_utils_2J import plotting

fix_dir = '/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/step8_8G_fix/OtherDwelling__Kelowna_5B__sample_050_HH145979__2010'
sql_path = os.path.join(fix_dir, 'eplusout.sql')
out_csv  = os.path.join(fix_dir, 'hourly_meters.csv')

if not os.path.exists(sql_path):
    print(f"FATAL: eplusout.sql not found at {sql_path}")
    sys.exit(1)

conn = sqlite3.connect(sql_path)
hourly = plotting.get_hourly_meter_data(conn)
conn.close()

if not hourly:
    print("FATAL: get_hourly_meter_data returned empty dict -- check SQL schema")
    sys.exit(1)

meters = list(hourly.keys())
nrows = max(len(v) for v in hourly.values())
print(f"Meters: {meters}")
print(f"Rows: {nrows} (expect 8760)")

with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['hour'] + meters)
    for h in range(nrows):
        w.writerow([h] + [hourly[m][h] if h < len(hourly[m]) else '' for m in meters])

print(f"Written: {out_csv}")
print("EXTRACTION OK")
PYEOF

EXTRACT_EXIT=$?
echo "Extraction exit=$EXTRACT_EXIT  $(date)"
if [ $EXTRACT_EXIT -ne 0 ]; then
    echo "EXTRACTION FAILED"
    exit $EXTRACT_EXIT
fi

# Verify output
NLINES=$(wc -l < "$FIX_DIR/hourly_meters.csv")
echo "hourly_meters.csv lines: $NLINES (expect 8761)"
if [ "$NLINES" -lt 8761 ]; then
    echo "WARN: hourly_meters.csv has fewer than 8760 data rows"
    exit 1
fi

echo "=== 8G FIX COMPLETE ==="
echo "Fixed run dir: $FIX_DIR"
echo "hourly_meters.csv: $NLINES lines"
