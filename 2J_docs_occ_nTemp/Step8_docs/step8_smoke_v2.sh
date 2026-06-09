#!/encs/bin/bash
#SBATCH --job-name=s8_smoke_v2
#SBATCH --partition=ps
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=06:00:00
#SBATCH --output=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/smoke_v2_%j.out
#SBATCH --error=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs/smoke_v2_%j.err

# Step 8 corrected-v2 smoke test: SingleD x Montreal_6A, N=3, ALL 5 years.
# DUAL GATE (must both pass before full array):
#   PHASE: weekday occupancy peaks overnight (h0-h5 > h11-h14) for all 5 years.
#   L&E:   per-year mean lights+equip kWh within 30% of original signed-off campaign.
#
# DOES NOT read from BEM_Setup. All schedules come from SCHED_DIR (private).

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
STEP8_DIR=/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/Step8_docs
SCHED_DIR=/speed-scratch/o_iseri/step8_run/sched
SMOKE_DIR=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/smoke
WRAPPER_DIR=/speed-scratch/o_iseri/ep_wrappers

mkdir -p "$SMOKE_DIR" /speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/logs

echo "=== Step 8 v2 SMOKE | arch=SingleD city=Montreal_6A N=3 all 5 years ==="
echo "SCHED_DIR=$SCHED_DIR"
echo "Start: $(date)"

# Pre-flight
singularity --version 2>/dev/null || { echo "ERROR: singularity not found"; exit 1; }
$PYTHON -c "import eppy" 2>/dev/null || { echo "ERROR: eppy missing; run: $PYTHON -m pip install eppy"; exit 1; }
[ -f "$WRAPPER_DIR/Energy+.idd" ] || { echo "ERROR: Energy+.idd missing from $WRAPPER_DIR"; exit 1; }
[ -x "$WRAPPER_DIR/energyplus"  ] || { echo "ERROR: energyplus wrapper not executable in $WRAPPER_DIR"; exit 1; }

# Verify private sched dir and log MD5s
echo "--- Schedule CSV checksums (from PRIVATE dir, NOT BEM_Setup) ---"
for yr in 2005 2010 2015 2022 2030; do
    f="$SCHED_DIR/BEM_Schedules_${yr}.csv"
    if [ ! -f "$f" ]; then
        echo "ERROR: missing $f — run build_s8_sched.sh first and wait for it to complete"
        exit 1
    fi
    echo "MD5 BEM_Schedules_${yr}.csv (private): $(md5sum $f | cut -d' ' -f1)"
done

# ===== GATE 1: PHASE gate on private schedule CSVs =====
echo ""
echo "=== GATE 1: PHASE check (occupancy clock) for all 5 years ==="
$PYTHON - <<'PYEOF'
import csv, sys
from pathlib import Path

SCHED_DIR = Path("/speed-scratch/o_iseri/step8_run/sched")
pass_all = True

for yr in ["2005", "2010", "2015", "2022", "2030"]:
    f = SCHED_DIR / f"BEM_Schedules_{yr}.csv"
    by_h = {}
    with open(f) as fh:
        for row in csv.DictReader(fh):
            if row.get("Day_Type") != "Weekday":
                continue
            h = int(row["Hour"])
            by_h.setdefault(h, []).append(float(row["Occupancy_Schedule"]))
    if not by_h:
        print(f"  {yr}: ERROR no Weekday rows"); pass_all = False; continue
    avg = {h: sum(v)/len(v) for h, v in by_h.items()}
    night_avg  = sum(avg.get(h, 0) for h in range(0, 6)) / 6
    midday_avg = sum(avg.get(h, 0) for h in range(11, 15)) / 4
    peak_h = max(avg, key=lambda k: avg[k])
    ok = (night_avg > midday_avg and peak_h < 8)
    status = "PASS" if ok else "FAIL"
    if not ok:
        pass_all = False
    print(f"  {yr}: night_h00-05={night_avg:.3f}  midday_h11-14={midday_avg:.3f}  peak=h{peak_h:02d}  -> {status}")

print()
if pass_all:
    print("PHASE GATE: PASS — clock correction confirmed for all 5 years")
    sys.exit(0)
else:
    print("PHASE GATE: FAIL — one or more years still show wrong clock. Check build_s8_sched.py output.")
    sys.exit(1)
PYEOF

PHASE_EXIT=$?
if [ $PHASE_EXIT -ne 0 ]; then
    echo "Aborting smoke: PHASE gate failed."
    exit 1
fi

# ===== Run N=3 E+ smoke =====
echo ""
echo "=== Running N=3 E+ smoke (SingleD x Montreal_6A, 5 years, --sched-dir $SCHED_DIR) ==="
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
    --sched-dir "$SCHED_DIR" \
    --output-dir "$SMOKE_DIR/SingleD__Montreal_6A"

EP_EXIT=$?
echo "E+ smoke exit=$EP_EXIT"

# ===== GATE 2: L&E gate from hourly_meters.csv =====
echo ""
echo "=== GATE 2: L&E check (per-year annual lights+equip kWh vs original campaign) ==="
$PYTHON - <<'PYEOF'
import csv, sys
from pathlib import Path

SMOKE = Path("/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/smoke/SingleD__Montreal_6A")

# Reference per-year means from original signed-off campaign (N=50, SingleD x Montreal_6A)
REF_LIGHTS = {"2005": 152, "2010": 151, "2015": 151, "2022": 156, "2030": 159}
REF_EQUIP  = {"2005": 6553, "2010": 6576, "2015": 6574, "2022": 6781, "2030": 6870}
TOL = 0.30  # 30% tolerance for N=3 smoke; full campaign target is 5%

by_year_lights = {}
by_year_equip  = {}

for hm_path in sorted(SMOKE.glob("**/hourly_meters.csv")):
    yr = hm_path.parent.name  # dir structure: .../sample_NNN_HHID/YEAR/hourly_meters.csv
    rows = list(csv.reader(open(hm_path)))
    if len(rows) < 2:
        continue
    header = rows[0]
    lights_cols = [i for i, h in enumerate(header)
                   if "InteriorLights" in h or h.lower() in ("interiorlights:electricity",)]
    equip_cols  = [i for i, h in enumerate(header)
                   if "InteriorEquipment" in h and "Gas" not in h]
    if not lights_cols or not equip_cols:
        print(f"  WARN {yr}: L&E columns not found; header={header[:6]}")
        continue
    tot_lights_j = sum(float(r[c]) for r in rows[1:] for c in lights_cols if r[c])
    tot_equip_j  = sum(float(r[c]) for r in rows[1:] for c in equip_cols  if r[c])
    by_year_lights.setdefault(yr, []).append(tot_lights_j / 3.6e6)
    by_year_equip.setdefault(yr,  []).append(tot_equip_j  / 3.6e6)

if not by_year_lights:
    print("FAIL: no hourly_meters.csv found — E+ produced no output")
    sys.exit(1)

pass_all = True
for yr in sorted(by_year_lights):
    n = len(by_year_lights[yr])
    ml = sum(by_year_lights[yr]) / n
    me = sum(by_year_equip.get(yr, [0])) / max(len(by_year_equip.get(yr, [1])), 1)
    ref_l = REF_LIGHTS.get(yr, 152)
    ref_e = REF_EQUIP.get(yr, 6600)
    ok_l = ref_l > 0 and abs(ml - ref_l) / ref_l <= TOL
    ok_e = ref_e > 0 and abs(me - ref_e) / ref_e <= TOL
    ok = ok_l and ok_e
    if not ok:
        pass_all = False
    tag_l = "ok" if ok_l else f"FAIL(ref={ref_l})"
    tag_e = "ok" if ok_e else f"FAIL(ref={ref_e})"
    status = "PASS" if ok else "FAIL"
    print(f"  {yr} (N={n}): lights={ml:.0f}kWh {tag_l}  equip={me:.0f}kWh {tag_e}  -> {status}")

print()
if pass_all:
    print("L&E GATE: PASS — schema correct (design-W dropped, standard L&E path active)")
    sys.exit(0)
else:
    print("L&E GATE: FAIL — check schema: near-zero L&E means design-W columns still present/active")
    sys.exit(1)
PYEOF

LE_EXIT=$?

echo ""
echo "=== SMOKE SUMMARY ==="
echo "E+ run exit    : $EP_EXIT"
echo "PHASE gate     : $([ $PHASE_EXIT -eq 0 ] && echo PASS || echo FAIL)"
echo "L&E gate       : $([ $LE_EXIT -eq 0 ] && echo PASS || echo FAIL)"
echo "End: $(date)"

if [ $EP_EXIT -ne 0 ] || [ $LE_EXIT -ne 0 ]; then
    echo "SMOKE RESULT: FAIL — do NOT submit full array until both gates pass"
    exit 1
fi
echo "SMOKE RESULT: PASS — ready to submit step8_array_v2.sh"
exit 0
